"""
只导入空表数据 - 用 INSERT IGNORE 跳过重复
使用方法: python fix_empty.py
"""
import pymysql
import ssl
import re

DB_HOST = "gateway01.ap-southeast-1.prod.aws.tidbcloud.com"
DB_PORT = 4000
DB_USER = "2UEE2A4qBecptw8.root"
DB_PASSWORD = "bbPIae9DoK2eHt8G"
DB_NAME = "personal_growth_platform"

# 需要补充数据的空表
EMPTY_TABLES = [
    "market_resource", "note", "user_favorite", "message",
    "study_room", "study_room_member", "audit_log",
]


def extract_insert_statements(sql_content):
    """从 SQL 文件中提取每条 INSERT 语句"""
    statements = []
    current = []
    in_insert = False

    for line in sql_content.split("\n"):
        if "INSERT INTO" in line and not line.strip().startswith("--"):
            in_insert = True
            current = [line]
        elif in_insert:
            current.append(line)
            if line.rstrip().endswith(";"):
                statements.append("\n".join(current))
                current = []
                in_insert = False

    return statements


def main():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    print("正在连接 TiDB Cloud...")
    conn = pymysql.connect(
        host=DB_HOST, port=DB_PORT, user=DB_USER,
        password=DB_PASSWORD, database=DB_NAME, ssl=ctx,
    )
    print("连接成功！\n")
    cursor = conn.cursor()

    # 读取 seed_data.sql
    with open("seed_data.sql", "r", encoding="utf-8") as f:
        content = f.read()

    # 提取所有 INSERT 语句
    all_inserts = extract_insert_statements(content)
    print(f"从 seed_data.sql 中提取到 {len(all_inserts)} 条 INSERT 语句\n")

    # 只执行空表对应的 INSERT
    success = 0
    errors = 0

    for stmt in all_inserts:
        # 获取表名
        match = re.match(r"INSERT INTO [`\"]?(\w+)[`\"]?", stmt)
        if not match:
            continue
        table_name = match.group(1)

        # 检查是否是空表
        if table_name not in EMPTY_TABLES:
            continue

        # 把 INSERT INTO 改成 INSERT IGNORE INTO
        stmt_ignored = stmt.replace("INSERT INTO", "INSERT IGNORE INTO", 1)

        try:
            cursor.execute(stmt_ignored)
            conn.commit()
            affected = cursor.rowcount
            success += 1
            print(f"  OK: {table_name} 导入 {affected} 条")
        except Exception as e:
            errors += 1
            print(f"  失败: {table_name} - {str(e)[:80]}")

    print(f"\n导入完成: {success} 成功, {errors} 失败")

    # 验证
    print(f"\n{'='*50}")
    print("数据验证:")
    for table in EMPTY_TABLES:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            status = "OK" if count > 0 else "EMPTY"
            print(f"  {table}: {count} 条 [{status}]")
        except Exception as e:
            print(f"  {table}: 查询失败 ({str(e)[:50]})")

    cursor.close()
    conn.close()
    print("\n完成")


if __name__ == "__main__":
    main()
