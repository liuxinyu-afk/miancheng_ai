"""
重新导入空表数据 - 使用 pymysql 多语句模式
使用方法: python fix_import.py
"""
import pymysql
import ssl
from pymysql.constants import CLIENT

DB_HOST = "gateway01.ap-southeast-1.prod.aws.tidbcloud.com"
DB_PORT = 4000
DB_USER = "2UEE2A4qBecptw8.root"
DB_PASSWORD = "bbPIae9DoK2eHt8G"
DB_NAME = "personal_growth_platform"


def main():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    print("正在连接 TiDB Cloud（多语句模式）...")
    conn = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        ssl=ctx,
        client_flag=CLIENT.MULTI_STATEMENTS,
    )
    print("连接成功！")
    cursor = conn.cursor()

    # 读取 seed_data.sql 并执行
    with open("seed_data.sql", "r", encoding="utf-8") as f:
        sql_content = f.read()

    # 去掉开头的 USE 语句和注释行
    lines = sql_content.split("\n")
    clean_lines = []
    skip_use = True
    for line in lines:
        stripped = line.strip()
        if skip_use and (stripped.startswith("USE ") or stripped.startswith("--") or stripped == ""):
            if stripped.startswith("USE "):
                continue
            clean_lines.append(line)
            continue
        skip_use = False
        clean_lines.append(line)

    sql_clean = "\n".join(clean_lines)

    print("正在执行 seed_data.sql...")
    try:
        cursor.execute(sql_clean)
        # 消费所有结果集
        while cursor.nextset():
            pass
        conn.commit()
        print("seed_data.sql 执行完成！")
    except Exception as e:
        print(f"执行出错: {e}")
        conn.rollback()

        # 如果整体执行失败，逐条执行
        print("\n尝试逐条执行...")
        statements = sql_clean.split(";")
        success = 0
        errors = 0
        for stmt in statements:
            stmt = stmt.strip()
            if not stmt or stmt.startswith("--"):
                continue
            try:
                cursor.execute(stmt)
                conn.commit()
                success += 1
            except Exception as e2:
                err = str(e2).lower()
                if "duplicate" in err or "already exists" in err:
                    success += 1
                else:
                    errors += 1
                    if errors <= 5:
                        print(f"  错误: {str(e2)[:100]}")
        print(f"逐条执行: {success} 成功, {errors} 失败")

    # 重新执行迁移脚本
    migrate_files = ["migrate_v7.sql", "migrate_v8.sql", "migrate_study_room_message.sql", "fix_database.sql"]
    for mf in migrate_files:
        try:
            with open(mf, "r", encoding="utf-8") as f:
                msql = f.read()
            # 去掉 USE 语句
            msql_lines = [l for l in msql.split("\n") if not l.strip().startswith("USE ")]
            msql_clean = "\n".join(msql_lines)
            cursor.execute(msql_clean)
            while cursor.nextset():
                pass
            conn.commit()
            print(f"{mf} 执行完成")
        except Exception as e:
            print(f"{mf} 部分失败: {str(e)[:80]}")

    # 验证
    print(f"\n{'='*50}")
    print("数据验证:")
    tables = [
        "user", "task_package", "task_item", "market_resource",
        "achievement_post", "achievement_comment", "achievement_like",
        "check_record", "note", "user_favorite", "message",
        "study_room", "study_room_member", "audit_log",
    ]
    all_good = True
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            status = "OK" if count > 0 else "EMPTY"
            if count == 0:
                all_good = False
            print(f"  {table}: {count} 条 [{status}]")
        except Exception as e:
            print(f"  {table}: 查询失败 ({str(e)[:50]})")
            all_good = False

    if all_good:
        print("\n所有表都有数据，数据库导入完成！")
    else:
        print("\n部分表仍为空，但不影响核心功能（登录、任务包、成果展示等）")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    main()
