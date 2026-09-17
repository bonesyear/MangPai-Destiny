#!/usr/bin/env python3
"""check_typing_imports - 静态扫描"注解里用了但模块未导入"的符号（AST 级）。

背景：H8 P0 发现 guanming.py 用了 Any 未导入、engine.py 用了 Optional 未导入，
3.14（PEP 649 惰性注解）掩盖、3.11 及更早版本 import 即 NameError。
本脚本对每个 .py 文件：
  1. 收集模块级已绑定名字（import/from import/def/class/赋值目标/类型别名）+ builtins；
  2. 遍历所有注解上下文（函数参数/返回值/AnnAssign/类型别名），收集其中的 Name 节点；
  3. 注解名不在已绑定集合内 → 报告 文件:行号 符号。
字符串注解（"Dict[str, ...]"）同样解析检查；`import typing` 后以 typing.X 限定使用的不算问题。

用法：python3 scripts/check_typing_imports.py [路径...]（默认 mangpai foundation scripts）
退出码：0=零残留，1=有发现。
"""
import ast
import builtins
import os
import sys

BUILTIN_NAMES = set(dir(builtins))


class _BindingCollector(ast.NodeVisitor):
    """收集模块级（含类体级）绑定名。不深入函数体收集局部名——
    注解在定义处求值，模块级注解只能看到模块级名字。"""

    def __init__(self):
        self.bound = set()

    def visit_Import(self, node):
        for a in node.names:
            self.bound.add((a.asname or a.name).split('.')[0])

    def visit_ImportFrom(self, node):
        for a in node.names:
            if a.name != '*':
                self.bound.add(a.asname or a.name)

    def visit_FunctionDef(self, node):
        self.bound.add(node.name)  # 函数名本身模块可见；不进入函数体

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node):
        self.bound.add(node.name)
        for stmt in node.body:  # 类体级绑定（类属性等）对方法注解可见
            self.visit(stmt)

    def visit_Assign(self, node):
        for t in node.targets:
            self._bind_target(t)
        self.visit(node.value)

    def visit_AnnAssign(self, node):
        self._bind_target(node.target)
        if node.value is not None:
            self.visit(node.value)

    def visit_AugAssign(self, node):
        self._bind_target(node.target)

    def visit_For(self, node):
        self._bind_target(node.target)
        self.generic_visit(node)

    visit_AsyncFor = visit_For

    def visit_With(self, node):
        for item in node.items:
            if item.optional_vars is not None:
                self._bind_target(item.optional_vars)
        self.generic_visit(node)

    visit_AsyncWith = visit_With

    def visit_ExceptHandler(self, node):
        if node.name:
            self.bound.add(node.name)
        self.generic_visit(node)

    def visit_TypeAlias(self, node):  # py3.12+
        self._bind_target(node.name)

    def _bind_target(self, t):
        if isinstance(t, ast.Name):
            self.bound.add(t.id)
        elif isinstance(t, (ast.Tuple, ast.List)):
            for e in t.elts:
                self._bind_target(e)
        elif isinstance(t, ast.Starred):
            self._bind_target(t.value)


class _AnnotationNameCollector(ast.NodeVisitor):
    """收集注解上下文里的 Name（含字符串注解解析后的 Name）。"""

    def __init__(self):
        self.uses = []  # [(name, lineno)]

    def _from_annotation(self, ann):
        if ann is None:
            return
        if isinstance(ann, ast.Constant) and isinstance(ann.value, str):
            try:
                sub = ast.parse(ann.value, mode='eval')
            except SyntaxError:
                return
            for n in ast.walk(sub):
                if isinstance(n, ast.Name):
                    self.uses.append((n.id, ann.lineno))
            return
        for n in ast.walk(ann):
            if isinstance(n, ast.Name):
                self.uses.append((n.id, ann.lineno))

    def visit_arg(self, node):
        self._from_annotation(node.annotation)

    def visit_FunctionDef(self, node):
        self._from_annotation(node.returns)
        self.generic_visit(node)  # 嵌套函数/默认值的注解也要查

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_AnnAssign(self, node):
        self._from_annotation(node.annotation)
        self.generic_visit(node)


def check_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=path)
    except (SyntaxError, UnicodeDecodeError) as e:
        return [(path, 0, f'<parse-error: {e}>')]
    bc = _BindingCollector()
    for stmt in tree.body:
        bc.visit(stmt)
    bound = bc.bound | BUILTIN_NAMES
    ac = _AnnotationNameCollector()
    ac.visit(tree)
    findings = []
    seen = set()
    for name, lineno in ac.uses:
        if name not in bound and (name, lineno) not in seen:
            seen.add((name, lineno))
            findings.append((path, lineno, name))
    return findings


def main(argv):
    roots = argv or ['mangpai', 'foundation', 'scripts']
    files = []
    for root in roots:
        if os.path.isfile(root):
            files.append(root)
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in ('__pycache__', '.pytest_cache', '.git')]
            for fn in filenames:
                if fn.endswith('.py'):
                    files.append(os.path.join(dirpath, fn))
    all_findings = []
    for path in sorted(files):
        all_findings.extend(check_file(path))
    for path, lineno, name in all_findings:
        print(f'{path}:{lineno}: 注解使用但未导入/未绑定: {name}')
    print(f'---\n扫描 {len(files)} 个文件，发现 {len(all_findings)} 处')
    return 1 if all_findings else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
