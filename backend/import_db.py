"""
数据库导入脚本 - 连接 TiDB Cloud 并执行所有 SQL 脚本
使用方法: python import_db.py
"""
import pymysql
import ssl
import os

# ====== 在这里填入你的 TiDB Cloud 连接信息 ======
DB_HOST = "gateway01.ap-southeast-1.prod.aws.tidbcloud.com"
DB_PORT = 4000
DB_USER = "2UEE2A4qBecptw8.root"
DB_PASSWORD = "bbPIae9DoK2eHt8G"
DB_NAME = "personal_growth_platform"
# ================================================

SQL_FILES = [
    "init.sql",
    "seed_data.sql",
    "migrate_v6.sql",
    "migrate_v7.sql",
    "migrate_v8.sql",
    "migrate_study_room_message.sql",
    "fix_database.sql",
]


def split_sql(sql_text):
    """将 SQL 文本按分号拆分成多条语句"""
    statements = []
    current = []
    in_single_quote = False
    in_double_quote = False
    i = 0
    while i < len(sql_text):
        char = sql_text[i]
        if char == '-' and i + 1 < len(sql_text) and sql_text[i + 1] == '-' and not in_single_quote and not in_double_quote:
            while i < len(sql_text) and sql_text[i] != '\n':
                i += 1
            continue
        if char == "'" and not in_double_quote:
            in_single_quote = not in_single_quote
        if char == '"' and not in_single_quote:
            in_double_quote = not in_double_quote
        if char == ';' and not in_single_quote and not in_double_quote:
            stmt = ''.join(current).strip()
            if stmt and not stmt.startswith('--'):
                statements.append(stmt)
            current = []
            i += 1
            continue
        current.append(char)
        i += 1
    stmt = ''.join(current).strip()
    if stmt and not stmt.startswith('--'):
        statements.append(stmt)
    return statements


def main():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    print(f"正在连接 TiDB Cloud: {DB_HOST}:{DB_PORT}")
    try:
        conn = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            ssl=ctx,
        )
    except Exception as e:
        print(f"连接失败: {e}")
        return

    print("连接成功！")
    cursor = conn.cursor()

    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} DEFAULT CHARACTER SET utf8mb4 DEFAULT COLLATE utf8mb4_unicode_ci")
        conn.commit()
        print(f"数据库 {DB_NAME} 准备就绪")
    except Exception as e:
        print(f"创建数据库失败: {e}")

    cursor.execute(f"USE {DB_NAME}")

    sql_dir = os.path.dirname(os.path.abspath(__file__))
    total_success = 0
    total_errors = 0

    for sql_file in SQL_FILES:
        file_path = os.path.join(sql_dir, sql_file)
        if not os.path.exists(file_path):
            print(f"  跳过 {sql_file}（文件不存在）")
            continue

        print(f"\n正在执行: {sql_file}")
        with open(file_path, 'r', encoding='utf-8') as f:
            sql_text = f.read()

        statements = split_sql(sql_text)
        file_success = 0
        file_errors = 0

        for stmt in statements:
            stmt_upper = stmt.upper().strip()
            if stmt_upper.startswith('USE '):
                continue
            if 'CREATE DATABASE' in stmt_upper:
                continue
            try:
                cursor.execute(stmt)
                conn.commit()
                file_success += 1
            except Exception as e:
                err_msg = str(e).lower()
                if "already exists" in err_msg or "duplicate" in err_msg:
                    file_success += 1
                else:
                    file_errors += 1
                    if file_errors <= 3:
                        print(f"  错误: {str(e)[:120]}")
                        print(f"  SQL: {stmt[:80]}...")

        print(f"  完成: {file_success} 成功, {file_errors} 失败")
        total_success += file_success
        total_errors += file_errors

    print(f"\n{'=' * 50}")
    print(f"总计: {total_success} 成功, {total_errors} 失败")

    try:
        cursor.execute("SELECT COUNT(*) FROM user")
        count = cursor.fetchone()[0]
        print(f"\n验证: user 表有 {count} 条记录")
        if count > 0:
            print("数据库导入成功！")
        else:
            print("警告: user 表为空")
    except Exception as e:
        print(f"\n验证失败: {e}")

    cursor.close()
    conn.close()
    print("数据库连接已关闭")


if __name__ == "__main__":
    main()
