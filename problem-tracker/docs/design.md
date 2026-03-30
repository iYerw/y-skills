# Problem Tracker 技能设计文档

## 概述

Problem Tracker 是一个轻量级的问题跟踪管理工具，用于记录、追踪和管理问题。

## 技术栈

- Python 3 (标准库)
- SQLite3 (数据存储)

## 目录结构

```
problem-tracker/
├── SKILL.md                    # 技能定义
├── scripts/
│   └── problem_tracker.py      # 主脚本
├── data/
│   ├── .gitignore              # 忽略 db 文件
│   └── problems.db             # SQLite 数据库（自动生成）
├── references/
│   └── schema.md               # 数据结构说明
└── docs/
    └── design.md               # 本文档
```

## 功能设计

### 命令列表

| 命令 | 功能 | 示例 |
|------|------|------|
| add | 添加问题 | `add "标题" --severity high` |
| list | 查询列表 | `list --status open` |
| show | 查看详情 | `show 1` |
| update | 更新问题 | `update 1 --status resolved` |
| delete | 删除问题 | `delete 1 --force` |
| stats | 统计分析 | `stats` |

### 数据模型

详见 [references/schema.md](../references/schema.md)

### 严重程度

| 级别 | Emoji | 说明 |
|------|-------|------|
| critical | 🔴 | 严重，需立即处理 |
| high | 🟠 | 高优先级 |
| medium | 🟡 | 中等优先级（默认） |
| low | 🟢 | 低优先级 |

### 状态流转

| 状态 | Emoji | 说明 |
|------|-------|------|
| open | 📭 | 开放（默认） |
| in_progress | 🔧 | 处理中 |
| resolved | ✅ | 已解决 |
| closed | 📁 | 已关闭 |

## 实现细节

### 数据库

- 首次运行时自动创建
- 使用 CHECK 约束确保枚举值有效
- 建立索引加速查询

### 分页

- 默认每页 20 条
- 最大每页 100 条
- 支持多种排序方式

### 特殊功能

- 状态变为 resolved 时自动记录 resolved_at
- 严重程度排序按优先级（critical > high > medium > low）
- 删除操作默认需要确认

## 使用场景

1. **个人项目管理** - 跟踪待办事项和问题
2. **Bug 追踪** - 记录软件缺陷
3. **运维问题管理** - 记录服务器、网络问题
4. **知识库索引** - 标记需要关注的领域