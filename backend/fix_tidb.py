"""
TiDB 兼容性修复脚本 - 修复 TEXT 列默认值 + 补充导入失败的数据
使用方法: python fix_tidb.py
"""
import pymysql
import ssl
import os

DB_HOST = "gateway01.ap-southeast-1.prod.aws.tidbcloud.com"
DB_PORT = 4000
DB_USER = "2UEE2A4qBecptw8.root"
DB_PASSWORD = "bbPIae9DoK2eHt8G"
DB_NAME = "personal_growth_platform"

# 需要执行的修复语句
FIX_SQL = [
    # 1. 修复 study_room 表：把 TEXT 类型的 announcement 改为 VARCHAR
    "ALTER TABLE study_room MODIFY COLUMN announcement VARCHAR(2000) NOT NULL DEFAULT ''",

    # 2. 修复 study_room_checkin 表：把 TEXT 类型的 completed 改为 VARCHAR
    "ALTER TABLE study_room_checkin MODIFY COLUMN completed TEXT NULL",

    # 3. 修复 study_room 表的 tags 和 description（如果上次失败的话）
    "ALTER TABLE study_room ADD COLUMN IF NOT EXISTS tags VARCHAR(255) NOT NULL DEFAULT ''",
    "ALTER TABLE study_room ADD COLUMN IF NOT EXISTS description VARCHAR(500) NOT NULL DEFAULT ''",

    # 4. 补充 seed_data.sql 中可能失败的数据
    """INSERT IGNORE INTO note (user_id, package_id, title, content, is_public) VALUES
    (4, 1, 'Python数据分析学习笔记', '# Python数据分析笔记\n\n## NumPy核心\n- ndarray创建\n- 数组索引\n- 广播机制\n\n## Pandas核心\n- DataFrame创建与索引\n- 数据清洗\n- 分组聚合', 1),
    (4, 1, 'Pandas速查表', '# Pandas常用操作\n\n```python\ndf = pd.read_csv("data.csv")\ndf.head()\ndf.info()\ndf.describe()\ndf[df["age"] > 18]\ndf.groupby("city")["salary"].mean()\n```', 1),
    (5, 2, '考研政治马原笔记', '# 马原核心考点\n\n## 唯物论\n1. 物质决定意识\n2. 物质的唯一特性是客观实在性\n\n## 辩证法\n1. 对立统一规律\n2. 量变和质变\n3. 否定之否定规律', 1),
    (6, 3, '英语四级备考心得', '# 四级备考笔记\n\n## 听力技巧\n- 预读选项\n- 听关键词\n\n## 阅读技巧\n- 先看题目\n- 定位关键词', 0),
    (5, 4, '微积分公式整理', '# 微积分公式大全\n\n## 求导公式\n- (x^n)\' = nx^(n-1)\n- (sinx)\' = cosx\n- (e^x)\' = e^x\n- (lnx)\' = 1/x\n\n## 积分公式\n- ∫x^n dx = x^(n+1)/(n+1) + C\n- ∫e^x dx = e^x + C', 1),
    (6, 5, 'Java集合框架笔记', '# Java集合框架\n\n## List\n- ArrayList：底层数组\n- LinkedList：底层链表\n\n## Map\n- HashMap：key-value存储\n- TreeMap：按key排序', 1)""",
]


def main():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    print(f"正在连接 TiDB Cloud...")
    conn = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        ssl=ctx,
    )
    print("连接成功！")
    cursor = conn.cursor()

    success = 0
    errors = 0

    for sql in FIX_SQL:
        try:
            cursor.execute(sql)
            conn.commit()
            success += 1
            print(f"  OK: {sql[:70]}...")
        except Exception as e:
            err_msg = str(e).lower()
            if "already exists" in err_msg or "duplicate" in err_msg:
                success += 1
                print(f"  跳过(已存在): {sql[:70]}...")
            else:
                errors += 1
                print(f"  失败: {str(e)[:100]}")
                print(f"  SQL: {sql[:80]}...")

    print(f"\n修复完成: {success} 成功, {errors} 失败")

    # 验证各表数据量
    print(f"\n{'='*50}")
    print("数据验证:")
    tables = [
        "user", "task_package", "task_item", "market_resource",
        "achievement_post", "achievement_comment", "achievement_like",
        "check_record", "note", "user_favorite", "message",
        "study_room", "study_room_member", "audit_log",
    ]
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  {table}: {count} 条")
        except Exception as e:
            print(f"  {table}: 表不存在或查询失败 ({str(e)[:50]})")

    cursor.close()
    conn.close()
    print("\n修复脚本执行完毕")


if __name__ == "__main__":
    main()
