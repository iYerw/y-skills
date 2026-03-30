# Problem Tracker 数据结构

## 表结构

### problems 表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 问题唯一标识 |
| title | TEXT | NOT NULL | 问题标题 |
| description | TEXT | | 问题描述（详细说明） |
| severity | TEXT | DEFAULT 'medium' | 严重程度: critical, high, medium, low |
| status | TEXT | DEFAULT 'open' | 状态: open, resolved, followup |
| review_status | TEXT | DEFAULT 'pending' | 回顾状态: pending, reviewed, confirmed, closed |
| category | TEXT | | 分类标签 |
| assignee | TEXT | | 负责人 |
| tags | TEXT | | 标签（逗号分隔） |
| created_at | TEXT | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | TEXT | DEFAULT CURRENT_TIMESTAMP | 更新时间 |
| resolved_at | TEXT | | 解决时间 |

## SQL 创建语句

```sql
CREATE TABLE IF NOT EXISTS problems (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    severity TEXT DEFAULT 'medium' CHECK(severity IN ('critical', 'high', 'medium', 'low')),
    status TEXT DEFAULT 'open' CHECK(status IN ('open', 'resolved', 'followup')),
    review_status TEXT DEFAULT 'pending' CHECK(review_status IN ('pending', 'reviewed', 'confirmed', 'closed')),
    category TEXT,
    assignee TEXT,
    tags TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    resolved_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_status ON problems(status);
CREATE INDEX IF NOT EXISTS idx_severity ON problems(severity);
CREATE INDEX IF NOT EXISTS idx_category ON problems(category);
CREATE INDEX IF NOT EXISTS idx_created_at ON problems(created_at);
CREATE INDEX IF NOT EXISTS idx_review_status ON problems(review_status);
```

## 枚举值

### severity (严重程度)
- `critical` - 严重，需要立即处理
- `high` - 高优先级
- `medium` - 中等优先级（默认）
- `low` - 低优先级

### status (状态)
- `open` - 开放（默认）
- `resolved` - 已解决
- `followup` - 需跟进

### review_status (回顾状态)
- `pending` - 待回顾（默认）
- `reviewed` - 已回顾
- `confirmed` - 已确认
- `closed` - 已关闭

## 状态说明

### status 与 review_status 的区别

| 字段 | 用途 | 说明 |
|------|------|------|
| status | 问题状态 | 描述问题本身的处理状态 |
| review_status | 回顾状态 | 描述问题回顾/复盘的状态 |

**典型工作流：**

1. 问题创建：`status=open`, `review_status=pending`
2. 问题解决：`status=resolved`, `review_status=pending`
3. 问题回顾：`review_status=reviewed`
4. 确认完成：`review_status=confirmed`
5. 归档关闭：`review_status=closed`

**特殊状态：**
- `status=followup`：需要后续跟进的问题（如需要其他团队配合、等待外部反馈等）

## 数据库路径

`{skill_dir}/data/problems.db`

首次运行时自动创建。

## 数据迁移

如果从旧版本（status 包含 in_progress/closed）升级，脚本会自动迁移：

- `in_progress` → `followup`
- `closed` → `resolved` 并设置 `review_status=closed`