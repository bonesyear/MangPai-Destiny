#!/usr/bin/env python3
"""分层铁律检查（H-fix-4c）：AST 静态分析 import 关系，断言单向依赖。

层次（只允许低层←高层，禁止反向）：
    foundation/（学派中性）← mangpai/objective/（纯检测）
    ← mangpai/subjective/（解释判断）← mangpai/engine.py（编排）

检查项：
  1. foundation/**   不得 import mangpai.objective / mangpai.subjective / mangpai.engine
  2. mangpai/objective/** 不得 import mangpai.subjective / mangpai.engine
  3. mangpai/subjective/** 不得 import mangpai.engine
  4. mangpai/subjective 内部**顶层** import 图必须无环（函数内局部导入为
     显式备案的循环规避回边，不计入顶层图，但会列出）。

用法：python3 scripts/check_layering.py [--graph]
退出码：0=无违规；1=存在反向依赖或顶层环。
"""
import ast
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LAYER_FOUNDATION = 'foundation'
LAYER_OBJECTIVE = 'mangpai.objective'
LAYER_SUBJECTIVE = 'mangpai.subjective'
LAYER_ENGINE = 'mangpai.engine'


def _layer_of_module(mod: str):
    """被导入模块 → 层名（仅关心仓内层次，仓外/标准库返回 None）。"""
    if mod == 'mangpai.engine' or mod.startswith('mangpai.engine.'):
        return LAYER_ENGINE
    if mod.startswith('mangpai.subjective'):
        return LAYER_SUBJECTIVE
    if mod.startswith('mangpai.objective'):
        return LAYER_OBJECTIVE
    if mod == 'mangpai':
        return None  # 包级 __init__（re-export 枢纽），不按层约束
    if mod.startswith('foundation'):
        return LAYER_FOUNDATION
    return None


def _file_layer(path: str):
    rel = os.path.relpath(path, ROOT).replace(os.sep, '/')
    if rel.startswith('foundation/'):
        return LAYER_FOUNDATION
    if rel.startswith('mangpai/objective/'):
        return LAYER_OBJECTIVE
    if rel.startswith('mangpai/subjective/'):
        return LAYER_SUBJECTIVE
    if rel == 'mangpai/engine.py':
        return LAYER_ENGINE
    return None


# 每层禁止 import 的目标层
FORBIDDEN = {
    LAYER_FOUNDATION: {LAYER_OBJECTIVE, LAYER_SUBJECTIVE, LAYER_ENGINE},
    LAYER_OBJECTIVE: {LAYER_SUBJECTIVE, LAYER_ENGINE},
    LAYER_SUBJECTIVE: {LAYER_ENGINE},
    LAYER_ENGINE: set(),
}

# 显式备案的例外（文件, 被导入模块）：函数内局部导入，非顶层耦合。
# - llm_channel.demo()/main 为 CLI 调试入口，延迟加载 engine 避免库调用方
#   承担编排层导入（H-fix-4c 备案，代码处有注释）。
WHITELIST = {
    ('mangpai/subjective/llm_channel.py', 'mangpai.engine'),
}


def _imports_of(path: str):
    """返回 (顶层导入模块列表, 局部导入模块列表)。相对导入已解析为绝对名。"""
    with open(path, encoding='utf-8') as f:
        tree = ast.parse(f.read(), filename=path)
    rel = os.path.relpath(path, ROOT).replace(os.sep, '/')
    pkg = os.path.dirname(rel).replace('/', '.')

    def _resolve(node):
        if node.level:
            base = pkg
            for _ in range(node.level - 1):
                base = base.rsplit('.', 1)[0] if '.' in base else ''
            return f'{base}.{node.module}' if node.module else base
        return node.module or ''

    top, local = [], []

    def _visit(body, is_top):
        for node in body:
            if isinstance(node, ast.Import):
                for a in node.names:
                    (top if is_top else local).append(a.name)
            elif isinstance(node, ast.ImportFrom):
                mod = _resolve(node)
                if mod:
                    (top if is_top else local).append(mod)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                _visit(node.body, False)
            elif isinstance(node, ast.ClassDef):
                _visit(node.body, is_top)
            elif isinstance(node, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                # try/except、if 等模块级块内的导入仍视为顶层（如软依赖 guard）
                for stmt_list in _child_bodies(node):
                    _visit(stmt_list, is_top)
    _visit(tree.body, True)
    return top, local


def _child_bodies(node):
    for field in ('body', 'orelse', 'finalbody'):
        yield getattr(node, field, [])
    if isinstance(node, ast.Try):
        for h in node.handlers:
            yield h.body


def _module_name_of(path: str):
    rel = os.path.relpath(path, ROOT).replace(os.sep, '/')
    return rel[:-3].replace('/', '.') if rel.endswith('.py') else rel


def main():
    scan_dirs = ['foundation', 'mangpai/objective', 'mangpai/subjective']
    files = []
    for d in scan_dirs:
        for dirpath, _dirnames, filenames in os.walk(os.path.join(ROOT, d)):
            for fn in filenames:
                if fn.endswith('.py'):
                    files.append(os.path.join(dirpath, fn))
    files.append(os.path.join(ROOT, 'mangpai', 'engine.py'))

    violations = []
    subj_top_edges = {}   # subjective 模块 -> 顶层导入的 subjective 模块集
    subj_local_edges = {} # subjective 模块 -> 局部导入的 subjective 模块集

    for path in sorted(files):
        layer = _file_layer(path)
        if layer is None:
            continue
        mod_self = _module_name_of(path)
        top, local = _imports_of(path)
        for mod in top + local:
            tgt = _layer_of_module(mod)
            rel_path = os.path.relpath(path, ROOT)
            if tgt and tgt in FORBIDDEN[layer] \
                    and (rel_path, mod) not in WHITELIST:
                violations.append(
                    f'{rel_path} ({layer}) 反向导入 {mod} ({tgt})')
        if layer == LAYER_SUBJECTIVE:
            s_top = {m for m in top if m.startswith('mangpai.subjective')}
            s_local = {m for m in local if m.startswith('mangpai.subjective')}
            subj_top_edges[mod_self] = s_top
            if s_local:
                subj_local_edges[mod_self] = s_local

    # subjective 顶层图无环断言（DFS 三色标记）
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {m: WHITE for m in subj_top_edges}
    cycles = []

    def _dfs(node, stack):
        color[node] = GRAY
        for nxt in subj_top_edges.get(node, ()):
            if nxt not in color:
                continue
            if color[nxt] == GRAY:
                cycles.append(' -> '.join(stack + [nxt]))
            elif color[nxt] == WHITE:
                _dfs(nxt, stack + [nxt])
        color[node] = BLACK

    for m in sorted(subj_top_edges):
        if color[m] == WHITE:
            _dfs(m, [m])

    if '--graph' in sys.argv:
        print('=== subjective 顶层依赖图（模块 -> 顶层导入的 subjective 模块）===')
        for m in sorted(subj_top_edges):
            deps = sorted(subj_top_edges[m])
            if deps:
                print(f'{m}')
                for d in deps:
                    print(f'  -> {d}')
        if subj_local_edges:
            print('=== 函数内局部导入（循环规避回边/延迟加载，不计入顶层图）===')
            for m in sorted(subj_local_edges):
                for d in sorted(subj_local_edges[m]):
                    print(f'{m}  ~~> {d}')

    ok = True
    if violations:
        ok = False
        print('!! 分层违规（反向依赖）：')
        for v in violations:
            print(f'  {v}')
    if cycles:
        ok = False
        print('!! subjective 顶层依赖环：')
        for c in cycles:
            print(f'  {c}')
    if ok:
        print(f'分层检查通过：{len(files)} 文件，无反向依赖，subjective 顶层图无环。')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
