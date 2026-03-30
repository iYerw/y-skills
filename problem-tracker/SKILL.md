---
name: problem-tracker
description: 问题跟踪管理工具。用于记录、追踪和管理问题。支持添加、查询、更新、删除和统计问题。当用户提到"问题跟踪"、"bug 追踪"、"问题管理"、"记录问题"、"查看问题列表"时触发。
---

# Problem Tracker

问题跟踪管理工具，使用 SQLite 存储数据。

## 快速开始

```bash
# 添加问题
python scripts/problem_tracker.py add "登录失败" --severity high --category auth

# 查看问题列表
python scripts/problem_tracker.py list

# 查看问题详情
python scripts/problem_tracker.py show 1

# 更新问题
python scripts/problem_tracker.py update 1 --status resolved

# 删除问题
python scripts/problem_tracker.py delete 1 --force

# 统计分析
python scripts/problem_tracker.py stats
```

## 命令详解

### add - 添加问题

```bash
python scripts/problem_tracker.py add <title> [options]

参数:
  title                   问题标题（必需）

选项:
  -d, --description       问题描述
  -s, --severity          严重程度: critical, high, medium, low (default: medium)
  -S, --status            状态: open, resolved, followup (default: open)
  -r, --review-status     回顾状态: pending, reviewed, confirmed, closed (default: pending)
  -c, --category          分类
  -a, --assignee          负责人
  -t, --tags              标签（逗号分隔）
```

示例:
```bash
python scripts/problem_tracker.py add "API 超时" \
  --description "生产环境 API 响应超过 30 秒" \
  --severity critical \
  --category api \
  --assignee "张三"
```

### list - 查询问题列表

```bash
python scripts/problem_tracker.py list [options]

筛选选项:
  -s, --status            按状态筛选
  -r, --review-status     按回顾状态筛选
  -S, --severity          按严重程度筛选
  -c, --category          按分类筛选
  -a, --assignee          按负责人筛选
  --search                搜索标题或描述

分页选项:
  --page                  页码 (default: 1)
  --per-page              每页数量 (default: 20)

排序选项:
  --sort-by               排序字段: id, created_at, updated_at, severity, status
  --sort-desc             降序排列
```

示例:
```bash
# 查看所有开放的高优先级问题
python scripts/problem_tracker.py list --status open --severity high

# 查看待回顾的问题
python scripts/problem_tracker.py list --review-status pending

# 搜索包含"登录"的问题
python scripts/problem_tracker.py list --search 登录

# 按严重程度降序排列
python scripts/problem_tracker.py list --sort-by severity --sort-desc
```

### show - 查看问题详情

```bash
python scripts/problem_tracker.py show <id>
```

### update - 更新问题

```bash
python scripts/problem_tracker.py update <id> [options]

选项:
  -t, --title             更新标题
  -d, --description       更新描述
  -s, --severity          更新严重程度
  -S, --status            更新状态
  -r, --review-status     更新回顾状态
  -c, --category          更新分类
  -a, --assignee          更新负责人
  --tags                  更新标签
```

示例:
```bash
# 更新状态为已解决
python scripts/problem_tracker.py update 1 --status resolved

# 标记为需要跟进
python scripts/problem_tracker.py update 1 --status followup

# 更新回顾状态
python scripts/problem_tracker.py update 1 --review-status reviewed
```

### delete - 删除问题

```bash
python scripts/problem_tracker.py delete <id> [-f, --force]
```

默认需要确认，使用 `--force` 跳过确认。

### stats - 统计分析

```bash
python scripts/problem_tracker.py stats
```

显示:
- 问题总数
- 各状态分布
- 各回顾状态分布
- 各严重程度分布
- 分类分布 (Top 10)
- 负责人分布 (Top 10)

## 状态说明

### status (问题状态)

| 状态 | Emoji | 说明 |
|------|-------|------|
| open | 📭 | 开放，新创建的问题 |
| resolved | ✅ | 已解决 |
| followup | 🔔 | 需跟进，需要后续处理 |

### review_status (回顾状态)

| 状态 | Emoji | 说明 |
|------|-------|------|
| pending | ⏳ | 待回顾 |
| reviewed | 👁️ | 已回顾 |
| confirmed | ✔️ | 已确认 |
| closed | 📁 | 已关闭 |

### 典型工作流

```
创建问题 → open + pending
    ↓
解决问题 → resolved + pending
    ↓
回顾复盘 → resolved + reviewed
    ↓
确认完成 → resolved + confirmed
    ↓
归档关闭 → resolved + closed
```

## 数据结构

详见 [references/schema.md](references/schema.md)

## 数据库

- 路径: `data/problems.db`
- 首次运行时自动创建