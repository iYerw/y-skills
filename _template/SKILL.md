---
name: template-skill
description: 技能模板 - 复制此目录开始创建新技能
version: 1.0.0
tags:
  - template
---

# 技能模板

这是技能模板，复制此目录并修改内容创建新技能。

## 目录结构

```
skill-name/
├── SKILL.md          # 技能定义（必需）
├── scripts/          # 脚本文件（可选）
│   └── example.sh
└── references/       # 参考文档（可选）
    └── guide.md
```

## SKILL.md 格式

```yaml
---
name: skill-name                    # 技能唯一标识（必需）
description: 技能简短描述            # 用于技能列表展示
version: 1.0.0                      # 版本号（可选）
tags:                               # 标签（可选）
  - category
---

# 技能名称

详细描述技能的功能和使用方法...

## 触发条件

描述何时应该使用这个技能...

## 可用命令

- `command1` - 功能描述
- `command2` - 功能描述

## 注意事项

- 注意点1
- 注意点2
```

## 使用说明

1. 复制 `_template/` 目录为新技能目录
2. 修改 `SKILL.md` 的内容和元数据
3. 添加需要的脚本和参考文档
4. 提交并推送到仓库