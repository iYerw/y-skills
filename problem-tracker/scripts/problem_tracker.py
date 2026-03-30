#!/usr/bin/env python3
"""
Problem Tracker - 问题跟踪管理工具

功能:
- add: 添加问题
- list: 查询问题列表（支持分页、筛选）
- show: 查看问题详情
- update: 更新问题
- delete: 删除问题
- stats: 统计分析
"""

import argparse
import sqlite3
import sys
import os
from datetime import datetime
from typing import Optional, List, Dict, Any

# 数据库路径（相对于脚本所在目录）
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), 'data')
DB_PATH = os.path.join(DATA_DIR, 'problems.db')

# 严重程度和状态的有效值
VALID_SEVERITIES = ['critical', 'high', 'medium', 'low']
VALID_STATUSES = ['open', 'resolved', 'followup']
VALID_REVIEW_STATUSES = ['pending', 'reviewed', 'confirmed', 'closed']


def ensure_db():
    """确保数据库存在并创建表结构"""
    os.makedirs(DATA_DIR, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
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
            solution TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            resolved_at TEXT
        )
    ''')
    
    # 创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON problems(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_severity ON problems(severity)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON problems(category)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON problems(created_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_review_status ON problems(review_status)')
    
    # 迁移旧数据：如果表中存在 review_status 列不存在的情况，添加该列
    cursor.execute("PRAGMA table_info(problems)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'review_status' not in columns:
        cursor.execute("ALTER TABLE problems ADD COLUMN review_status TEXT DEFAULT 'pending'")
    if 'solution' not in columns:
        cursor.execute("ALTER TABLE problems ADD COLUMN solution TEXT")
    
    # 迁移旧数据：如果 status 列使用旧值，进行转换
    # in_progress -> followup, closed -> resolved (并设置 review_status = 'closed')
    cursor.execute("UPDATE problems SET status = 'followup' WHERE status = 'in_progress'")
    cursor.execute("UPDATE problems SET review_status = 'closed', status = 'resolved' WHERE status = 'closed'")
    
    conn.commit()
    conn.close()


def get_connection() -> sqlite3.Connection:
    """获取数据库连接"""
    ensure_db()
    return sqlite3.connect(DB_PATH)


def dict_factory(cursor, row):
    """将查询结果转为字典"""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def format_datetime(dt_str: Optional[str]) -> str:
    """格式化时间显示"""
    if not dt_str:
        return '-'
    try:
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M')
    except:
        return dt_str


def severity_emoji(severity: str) -> str:
    """严重程度对应的 emoji"""
    return {
        'critical': '🔴',
        'high': '🟠',
        'medium': '🟡',
        'low': '🟢'
    }.get(severity, '⚪')


def status_emoji(status: str) -> str:
    """状态对应的 emoji"""
    return {
        'open': '📭',
        'followup': '🔔',
        'resolved': '✅'
    }.get(status, '❓')


def review_status_emoji(review_status: str) -> str:
    """回顾状态对应的 emoji"""
    return {
        'pending': '⏳',
        'reviewed': '👁️',
        'confirmed': '✔️',
        'closed': '📁'
    }.get(review_status, '❓')


# ==================== 命令实现 ====================

def cmd_add(args):
    """添加问题"""
    conn = get_connection()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    now = datetime.now().isoformat()
    
    cursor.execute('''
        INSERT INTO problems (title, description, severity, status, review_status, category, assignee, tags, solution, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        args.title,
        args.description,
        args.severity,
        args.status,
        args.review_status,
        args.category,
        args.assignee,
        args.tags,
        args.solution,
        now,
        now
    ))
    
    problem_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    print(f"✅ 问题已创建: #{problem_id}")
    print(f"   标题: {args.title}")
    print(f"   严重程度: {severity_emoji(args.severity)} {args.severity}")
    print(f"   状态: {status_emoji(args.status)} {args.status}")
    print(f"   回顾状态: {review_status_emoji(args.review_status)} {args.review_status}")
    if args.category:
        print(f"   分类: {args.category}")
    if args.assignee:
        print(f"   负责人: {args.assignee}")
    if args.tags:
        print(f"   标签: {args.tags}")
    if args.solution:
        print(f"   解决办法: {args.solution}")
    
    return 0


def cmd_list(args):
    """查询问题列表"""
    conn = get_connection()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    # 构建查询
    conditions = []
    params = []
    
    if args.status:
        conditions.append('status = ?')
        params.append(args.status)
    if args.review_status:
        conditions.append('review_status = ?')
        params.append(args.review_status)
    if args.severity:
        conditions.append('severity = ?')
        params.append(args.severity)
    if args.category:
        conditions.append('category = ?')
        params.append(args.category)
    if args.assignee:
        conditions.append('assignee = ?')
        params.append(args.assignee)
    if args.search:
        conditions.append('(title LIKE ? OR description LIKE ?)')
        search_pattern = f'%{args.search}%'
        params.extend([search_pattern, search_pattern])
    
    where_clause = ' AND '.join(conditions) if conditions else '1=1'
    
    # 计算总数
    count_sql = f'SELECT COUNT(*) as total FROM problems WHERE {where_clause}'
    cursor.execute(count_sql, params)
    total = cursor.fetchone()['total']
    
    # 分页
    page = max(1, args.page)
    per_page = max(1, min(100, args.per_page))
    offset = (page - 1) * per_page
    
    # 排序
    order_field = args.sort_by if args.sort_by in ['id', 'created_at', 'updated_at', 'severity', 'status'] else 'created_at'
    order_dir = 'DESC' if args.sort_desc else 'ASC'
    
    # 特殊排序：severity 需要映射
    if order_field == 'severity':
        order_clause = f"CASE severity WHEN 'critical' THEN 1 WHEN 'high' THEN 2 WHEN 'medium' THEN 3 WHEN 'low' THEN 4 END {order_dir}"
    else:
        order_clause = f'{order_field} {order_dir}'
    
    sql = f'SELECT * FROM problems WHERE {where_clause} ORDER BY {order_clause} LIMIT ? OFFSET ?'
    cursor.execute(sql, params + [per_page, offset])
    rows = cursor.fetchall()
    conn.close()
    
    # 输出
    total_pages = (total + per_page - 1) // per_page
    
    print(f"\n📋 问题列表 (第 {page}/{total_pages} 页，共 {total} 条)\n")
    print(f"{'ID':<6} {'严重程度':<12} {'状态':<12} {'回顾':<10} {'标题':<36} {'创建时间':<16}")
    print("-" * 95)
    
    for row in rows:
        severity = f"{severity_emoji(row['severity'])} {row['severity']}"
        status = f"{status_emoji(row['status'])} {row['status']}"
        review = f"{review_status_emoji(row['review_status'])} {row['review_status'][:4]}"
        title = row['title'][:34] + '..' if len(row['title']) > 36 else row['title']
        created = format_datetime(row['created_at'])
        
        print(f"#{row['id']:<5} {severity:<12} {status:<12} {review:<10} {title:<36} {created:<16}")
    
    print()
    if total > per_page:
        print(f"💡 使用 --page {page + 1} 查看下一页，或调整 --per-page")


def cmd_show(args):
    """查看问题详情"""
    conn = get_connection()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM problems WHERE id = ?', (args.id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        print(f"❌ 问题 #{args.id} 不存在")
        return 1
    
    print(f"\n{'='*60}")
    print(f"问题 #{row['id']}: {row['title']}")
    print(f"{'='*60}\n")
    
    print(f"严重程度: {severity_emoji(row['severity'])} {row['severity']}")
    print(f"状态:     {status_emoji(row['status'])} {row['status']}")
    print(f"回顾状态: {review_status_emoji(row['review_status'])} {row['review_status']}")
    print(f"分类:     {row['category'] or '-'}")
    print(f"负责人:   {row['assignee'] or '-'}")
    print(f"标签:     {row['tags'] or '-'}")
    print(f"\n创建时间: {format_datetime(row['created_at'])}")
    print(f"更新时间: {format_datetime(row['updated_at'])}")
    if row['resolved_at']:
        print(f"解决时间: {format_datetime(row['resolved_at'])}")
    
    if row['description']:
        print(f"\n📝 描述:\n{row['description']}")
    
    if row['solution']:
        print(f"\n💡 解决办法:\n{row['solution']}")
    
    print()


def cmd_update(args):
    """更新问题"""
    conn = get_connection()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    # 检查问题是否存在
    cursor.execute('SELECT * FROM problems WHERE id = ?', (args.id,))
    row = cursor.fetchone()
    if not row:
        print(f"❌ 问题 #{args.id} 不存在")
        conn.close()
        return 1
    
    # 构建更新
    updates = []
    params = []
    
    if args.title:
        updates.append('title = ?')
        params.append(args.title)
    if args.description is not None:
        updates.append('description = ?')
        params.append(args.description)
    if args.severity:
        updates.append('severity = ?')
        params.append(args.severity)
    if args.status:
        updates.append('status = ?')
        params.append(args.status)
        # 如果状态变为 resolved，设置 resolved_at
        if args.status == 'resolved' and row['status'] != 'resolved':
            updates.append('resolved_at = ?')
            params.append(datetime.now().isoformat())
    if args.review_status:
        updates.append('review_status = ?')
        params.append(args.review_status)
    if args.category is not None:
        updates.append('category = ?')
        params.append(args.category)
    if args.assignee is not None:
        updates.append('assignee = ?')
        params.append(args.assignee)
    if args.tags is not None:
        updates.append('tags = ?')
        params.append(args.tags)
    if args.solution is not None:
        updates.append('solution = ?')
        params.append(args.solution)
    
    if not updates:
        print("⚠️ 没有要更新的字段")
        conn.close()
        return 0
    
    updates.append('updated_at = ?')
    params.append(datetime.now().isoformat())
    params.append(args.id)
    
    sql = f"UPDATE problems SET {', '.join(updates)} WHERE id = ?"
    cursor.execute(sql, params)
    conn.commit()
    conn.close()
    
    print(f"✅ 问题 #{args.id} 已更新")


def cmd_delete(args):
    """删除问题"""
    conn = get_connection()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    # 检查问题是否存在
    cursor.execute('SELECT title FROM problems WHERE id = ?', (args.id,))
    row = cursor.fetchone()
    if not row:
        print(f"❌ 问题 #{args.id} 不存在")
        conn.close()
        return 1
    
    if args.force or input(f"确认删除问题 #{args.id}: {row['title']}? [y/N] ").lower() == 'y':
        cursor.execute('DELETE FROM problems WHERE id = ?', (args.id,))
        conn.commit()
        print(f"🗑️ 问题 #{args.id} 已删除")
    else:
        print("取消删除")
    
    conn.close()


def cmd_stats(args):
    """统计分析"""
    conn = get_connection()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    # 总数
    cursor.execute('SELECT COUNT(*) as total FROM problems')
    total = cursor.fetchone()['total']
    
    # 按状态统计
    cursor.execute('''
        SELECT status, COUNT(*) as count
        FROM problems
        GROUP BY status
        ORDER BY 
            CASE status 
                WHEN 'open' THEN 1 
                WHEN 'resolved' THEN 2 
                WHEN 'followup' THEN 3 
            END
    ''')
    status_stats = cursor.fetchall()
    
    # 按回顾状态统计
    cursor.execute('''
        SELECT review_status, COUNT(*) as count
        FROM problems
        GROUP BY review_status
        ORDER BY 
            CASE review_status 
                WHEN 'pending' THEN 1 
                WHEN 'reviewed' THEN 2 
                WHEN 'confirmed' THEN 3 
                WHEN 'closed' THEN 4 
            END
    ''')
    review_status_stats = cursor.fetchall()
    
    # 按严重程度统计
    cursor.execute('''
        SELECT severity, COUNT(*) as count
        FROM problems
        GROUP BY severity
        ORDER BY 
            CASE severity 
                WHEN 'critical' THEN 1 
                WHEN 'high' THEN 2 
                WHEN 'medium' THEN 3 
                WHEN 'low' THEN 4 
            END
    ''')
    severity_stats = cursor.fetchall()
    
    # 按分类统计
    cursor.execute('''
        SELECT category, COUNT(*) as count
        FROM problems
        WHERE category IS NOT NULL AND category != ''
        GROUP BY category
        ORDER BY count DESC
        LIMIT 10
    ''')
    category_stats = cursor.fetchall()
    
    # 按负责人统计
    cursor.execute('''
        SELECT assignee, COUNT(*) as count
        FROM problems
        WHERE assignee IS NOT NULL AND assignee != ''
        GROUP BY assignee
        ORDER BY count DESC
        LIMIT 10
    ''')
    assignee_stats = cursor.fetchall()
    
    conn.close()
    
    # 输出
    print(f"\n📊 问题统计 (共 {total} 条)\n")
    
    print("📈 状态分布:")
    for row in status_stats:
        status = f"{status_emoji(row['status'])} {row['status']}"
        bar = '█' * min(20, int(row['count'] / max(1, total) * 20))
        print(f"   {status:<18} {row['count']:>4} {bar}")
    
    print("\n🔍 回顾状态分布:")
    for row in review_status_stats:
        review = f"{review_status_emoji(row['review_status'])} {row['review_status']}"
        bar = '█' * min(20, int(row['count'] / max(1, total) * 20))
        print(f"   {review:<18} {row['count']:>4} {bar}")
    
    print("\n🎯 严重程度分布:")
    for row in severity_stats:
        severity = f"{severity_emoji(row['severity'])} {row['severity']}"
        bar = '█' * min(20, int(row['count'] / max(1, total) * 20))
        print(f"   {severity:<18} {row['count']:>4} {bar}")
    
    if category_stats:
        print("\n📁 分类分布 (Top 10):")
        for row in category_stats:
            bar = '█' * min(15, int(row['count'] / max(1, total) * 15))
            print(f"   {row['category']:<20} {row['count']:>4} {bar}")
    
    if assignee_stats:
        print("\n👤 负责人分布 (Top 10):")
        for row in assignee_stats:
            bar = '█' * min(15, int(row['count'] / max(1, total) * 15))
            print(f"   {row['assignee']:<20} {row['count']:>4} {bar}")
    
    print()


# ==================== 参数解析 ====================

def main():
    parser = argparse.ArgumentParser(
        description='Problem Tracker - 问题跟踪管理工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  %(prog)s add "登录失败" --severity high --category auth
  %(prog)s list --status open --severity critical
  %(prog)s show 1
  %(prog)s update 1 --status resolved --assignee "张三"
  %(prog)s delete 1 --force
  %(prog)s stats
'''
    )
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # add 命令
    add_parser = subparsers.add_parser('add', help='添加新问题')
    add_parser.add_argument('title', help='问题标题')
    add_parser.add_argument('-d', '--description', help='问题描述')
    add_parser.add_argument('-s', '--severity', choices=VALID_SEVERITIES, default='medium', help='严重程度 (default: medium)')
    add_parser.add_argument('-S', '--status', choices=VALID_STATUSES, default='open', help='状态 (default: open)')
    add_parser.add_argument('-r', '--review-status', choices=VALID_REVIEW_STATUSES, default='pending', dest='review_status', help='回顾状态 (default: pending)')
    add_parser.add_argument('-c', '--category', help='分类')
    add_parser.add_argument('-a', '--assignee', help='负责人')
    add_parser.add_argument('-t', '--tags', help='标签（逗号分隔）')
    add_parser.add_argument('--solution', help='解决办法')
    
    # list 命令
    list_parser = subparsers.add_parser('list', help='查询问题列表')
    list_parser.add_argument('-s', '--status', choices=VALID_STATUSES, help='按状态筛选')
    list_parser.add_argument('-r', '--review-status', choices=VALID_REVIEW_STATUSES, dest='review_status', help='按回顾状态筛选')
    list_parser.add_argument('-S', '--severity', choices=VALID_SEVERITIES, help='按严重程度筛选')
    list_parser.add_argument('-c', '--category', help='按分类筛选')
    list_parser.add_argument('-a', '--assignee', help='按负责人筛选')
    list_parser.add_argument('--search', help='搜索标题或描述')
    list_parser.add_argument('--page', type=int, default=1, help='页码 (default: 1)')
    list_parser.add_argument('--per-page', type=int, default=20, help='每页数量 (default: 20)')
    list_parser.add_argument('--sort-by', choices=['id', 'created_at', 'updated_at', 'severity', 'status'], default='created_at', help='排序字段')
    list_parser.add_argument('--sort-desc', action='store_true', help='降序排列')
    
    # show 命令
    show_parser = subparsers.add_parser('show', help='查看问题详情')
    show_parser.add_argument('id', type=int, help='问题 ID')
    
    # update 命令
    update_parser = subparsers.add_parser('update', help='更新问题')
    update_parser.add_argument('id', type=int, help='问题 ID')
    update_parser.add_argument('-t', '--title', help='更新标题')
    update_parser.add_argument('-d', '--description', help='更新描述')
    update_parser.add_argument('-s', '--severity', choices=VALID_SEVERITIES, help='更新严重程度')
    update_parser.add_argument('-S', '--status', choices=VALID_STATUSES, help='更新状态')
    update_parser.add_argument('-r', '--review-status', choices=VALID_REVIEW_STATUSES, dest='review_status', help='更新回顾状态')
    update_parser.add_argument('-c', '--category', help='更新分类')
    update_parser.add_argument('-a', '--assignee', help='更新负责人')
    update_parser.add_argument('--tags', help='更新标签')
    update_parser.add_argument('--solution', help='更新解决办法')
    
    # delete 命令
    delete_parser = subparsers.add_parser('delete', help='删除问题')
    delete_parser.add_argument('id', type=int, help='问题 ID')
    delete_parser.add_argument('-f', '--force', action='store_true', help='强制删除，不确认')
    
    # stats 命令
    subparsers.add_parser('stats', help='统计分析')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    # 执行命令
    commands = {
        'add': cmd_add,
        'list': cmd_list,
        'show': cmd_show,
        'update': cmd_update,
        'delete': cmd_delete,
        'stats': cmd_stats,
    }
    
    return commands[args.command](args) or 0


if __name__ == '__main__':
    sys.exit(main())