# problem-tracker 技能设计文档

## 一、背景与目的

收集和追踪使用 OpenClaw 过程中遇到的问题，特别是 AI 输出不符合预期导致的返工情况。便于后期回顾、分析和改进。

## 二、问题分类

| 分类 | 标识 | 说明 | 示例 |
|------|------|------|------|
| AI产出不符预期 | `ai-mismatch` | AI输出不符合预期，需要返工 | "写的代码结构不对"、"理解错了需求" |
| AI事实/逻辑错误 | `ai-error` | AI的事实或逻辑错误 | "API参数搞错了"、"用了过期的库" |
| 工具执行失败 | `tool-fail` | 工具/命令执行失败 | "pip安装失败"、"git push超时" |
| 环境配置问题 | `env-issue` | 环境/配置问题 | "Python版本不对"、"权限不足" |
| 流程协作问题 | `workflow` | 流程/协作问题 | "分支命名不规范"、"忘记走review" |
| 其他 | `other` | 其他未分类问题 | - |

**分类目的**：便于统计分析，发现高频问题类型，针对性改进。

## 三、数据结构

### 表结构

```sql
CREATE TABLE problems (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- 基本信息
    title TEXT NOT NULL,           -- 问题简介（一句话）
    description TEXT,              -- 详细描述
    solution TEXT,                 -- 解决办法
    
    -- 分类与标记
    category TEXT DEFAULT 'ai-mismatch',  -- 问题分类
    severity TEXT DEFAULT 'medium',       -- 严重程度: low/medium/high
    tags TEXT,                            -- 自由标签（逗号分隔）
    
    -- 状态（两阶段）
    status TEXT DEFAULT 'open',           -- 当前状态: open/resolved/followup
    review_status TEXT DEFAULT 'pending', -- 回顾状态: pending/reviewed/confirmed/closed
    
    -- 时间与来源
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    source TEXT                           -- 来源场景（可选）
);
```

### 字段说明

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| id | INTEGER | 是 | 自增 | 主键 |
| title | TEXT | 是 | - | 问题简介，一句话描述 |
| description | TEXT | 否 | - | 详细描述 |
| solution | TEXT | 否 | - | 解决办法 |
| category | TEXT | 否 | 'ai-mismatch' | 问题分类 |
| severity | TEXT | 否 | 'medium' | 严重程度: low/medium/high |
| tags | TEXT | 否 | - | 自由标签，逗号分隔 |
| status | TEXT | 否 | 'open' | 当前状态: open/resolved/followup |
| review_status | TEXT | 否 | 'pending' | 回顾状态: pending/reviewed/confirmed/closed |
| created_at | TEXT | 否 | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | TEXT | 否 | CURRENT_TIMESTAMP | 更新时间 |
| source | TEXT | 否 | - | 来源场景 |

### 状态说明

**status（当前状态）**：
- `open` - 问题待解决
- `resolved` - 问题已解决
- `followup` - 需要后续跟进

**review_status（回顾状态）**：
- `pending` - 未回顾
- `reviewed` - 已回顾，等待确认
- `confirmed` - 确认已解决
- `closed` - 彻底解决，关闭

**状态流转**：
```
status: open → resolved → followup
review_status: pending → reviewed → confirmed → closed
```

## 四、功能需求

### 4.1 添加问题

命令：`problem_tracker.py add`

参数：
- `--title` 必填，问题简介
- `--description` 可选，详细描述
- `--category` 可选，默认 ai-mismatch
- `--severity` 可选，默认 medium
- `--tags` 可选，逗号分隔
- `--solution` 可选，解决办法
- `--source` 可选，来源场景

### 4.2 查询问题列表

命令：`problem_tracker.py list`

参数：
- `--category` 按分类筛选
- `--status` 按状态筛选
- `--review-status` 按回顾状态筛选
- `--severity` 按严重程度筛选
- `--tags` 按标签筛选（支持多个，逗号分隔）
- `--keyword` 关键词搜索（搜索 title、description、tags）
- `--start-date` 开始日期
- `--end-date` 结束日期
- `--page` 页码，默认 1
- `--page-size` 每页条数，默认 20
- `--sort` 排序字段，默认 created_at
- `--order` 排序方向，默认 desc

输出格式：表格展示，包含 id、title、category、status、review_status、created_at

### 4.3 查看问题详情

命令：`problem_tracker.py show <id>`

输出：完整问题信息

### 4.4 更新问题

命令：`problem_tracker.py update <id>`

参数：
- `--title` 更新标题
- `--description` 更新描述
- `--solution` 更新解决办法
- `--category` 更新分类
- `--severity` 更新严重程度
- `--tags` 更新标签
- `--status` 更新状态
- `--review-status` 更新回顾状态
- `--source` 更新来源

### 4.5 删除问题

命令：`problem_tracker.py delete <id>`

确认后删除。

### 4.6 统计分析

命令：`problem_tracker.py stats`

输出：
- 各分类问题数量
- 各状态问题数量
- 各严重程度问题数量
- 最近 7 天新增数量
- 未解决问题数量

## 五、目录结构

```
problem-tracker/
├── SKILL.md              # 技能定义
├── docs/
│   └── design.md         # 设计文档（本文档）
├── scripts/
│   └── problem_tracker.py  # 主脚本
├── data/
│   ├── .gitignore        # 忽略 db 文件
│   └── problems.db       # SQLite数据库（自动创建）
└── references/
    └── schema.md         # 数据结构说明（可选）
```

## 六、技术实现

### 6.1 语言

Python 3，使用 sqlite3 标准库。

### 6.2 数据库初始化

首次执行时自动创建数据库和表结构：
- 检查 `data/problems.db` 是否存在
- 不存在则创建并执行建表语句
- 表结构保持一致，后续可添加索引优化

### 6.3 data/.gitignore 内容

```
*.db
*.db-journal
```

### 6.4 命令行参数解析

使用 argparse 库。

## 七、使用场景示例

### 添加问题

用户说：**"记录一下这个问题"**

AI 执行：
```
problem_tracker.py add \
  --title "AI写的代码结构不对" \
  --description "要求按照project-layout规范，AI把业务逻辑放到了cmd目录" \
  --category "ai-mismatch" \
  --severity "medium" \
  --tags "go,code-structure" \
  --solution "重新派发coder，明确目录规范"
```

### 查询问题

用户说：**"看看最近的问题"**

AI 执行：
```
problem_tracker.py list --page 1 --page-size 10
```

用户说：**"看看所有 ai-mismatch 的问题"**

AI 执行：
```
problem_tracker.py list --category ai-mismatch
```

### 回顾问题

用户说：**"回顾问题 #5"**

AI 执行：
```
problem_tracker.py show 5
```

展示详情，用户确认后：

```
problem_tracker.py update 5 --review-status confirmed
```

### 统计分析

用户说：**"问题统计"**

AI 执行：
```
problem_tracker.py stats
```

---

## 八、开发任务清单

1. 创建目录结构
2. 编写 SKILL.md
3. 编写 problem_tracker.py 脚本
4. 创建 data/.gitignore
5. 测试所有命令
6. 编写 references/schema.md（可选）

---

*文档版本: 1.0*
*创建时间: 2026-03-30*