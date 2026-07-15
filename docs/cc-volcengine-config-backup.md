# Claude Code 火山引擎 API 配置备份
# 备份时间: 2026-07-09
# 用途: CC (Claude Code) 通过火山引擎 ark API 调用 glm-5.2 模型

## 1. CLI 版本
claude --version  →  2.1.202 (Claude Code)

## 2. 环境变量（来源: /root/.hermes/.env）
export ANTHROPIC_API_KEY=ark-1ad8616c-a339-4af6-aece-e258e433b945-6780f
export ANTHROPIC_BASE_URL=https://ark.cn-beijing.volces.com/api/plan
export ANTHROPIC_DEFAULT_SONNET_MODEL=ark-code-latest

说明：
- ark-code-latest 即 glm-5.2，模型名不同但同一个东西
- 端点 /api/plan（不是 /api/v3）
- 每个 terminal() 调用是新 shell，必须重新 export 这三个变量
- API Key 每次从 /root/.hermes/.env 中 grep + export

## 3. CC 配置文件
- 主配置: /root/.claude.json
- 权限设置: /root/.claude/settings.json
  {
    "permissions": {
      "allow": ["Bash", "Read", "Edit", "Write", "WebSearch", "WebFetch"],
      "deny": []
    },
    "theme": "dark"
  }
- 项目记忆: /root/.claude/projects/-root-metaphysics/memory/
- 任务记录: /root/.claude/tasks/

## 4. 调用方式

### 基本调用
```bash
export ANTHROPIC_API_KEY=ark-xxx
export ANTHROPIC_BASE_URL=https://ark.cn-beijing.volces.com/api/plan
export ANTHROPIC_DEFAULT_SONNET_MODEL=ark-code-latest
claude --print "简短 prompt" 2>&1
```

### 长 prompt（避免 shell 截断）
```bash
cat /tmp/task.md | claude --print 2>&1
```

### 长时间任务（超时设置）
```bash
export CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0
# terminal() 中用: background=true, notify_on_complete=true, pty=true, timeout=600
```

## 5. 常见问题 & 避坑

### Shell 截断 Markdown
claude --print "包含反引号或管道符的 prompt" → shell 会把 ``` 和 | 当成命令执行
解决: 把 prompt 写入文件，用 cat file | claude --print

### Prompt 太长
claude --print "$(cat file)" → "Prompt is too long"
解决: 用 cat file | claude --print（stdin 方式）

### API 只支持 text
"Model only support text input" → CC 不能直接读 PDF
解决: 先用 pdftotext 转成 .txt

### 周配额耗尽
"429 exceeded weekly usage quota" → 等重置或换 API Key

### CC foreground 超时
foreground 最长 600s，超时会被杀
解决: 用 background=true + notify_on_complete=true

### 模型名
ark-code-latest 就是 glm-5.2，同一个东西两个名字

## 6. 当前使用范围
- 项目: /root/metaphysics（玄学命理系统）
- 主要用途: 命理古籍审计、代码修复、模块开发
- 工作流: 写 prompt → CC 通读原文 → 对照引擎审计 → 修复代码
