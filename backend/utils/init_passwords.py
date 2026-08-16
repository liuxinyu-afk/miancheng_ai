"""
种子数据密码初始化脚本
用途: 为 init.sql 中的种子账号生成正确的 bcrypt 密码哈希
使用方法: python utils/init_passwords.py
然后将输出的哈希值替换到 init.sql 中，或在数据库中直接执行 UPDATE 语句
"""
from utils.security import hash_password


def main():
    password = "123456"
    hashed = hash_password(password)

    print("=" * 60)
    print("绵城AI学习集市 - 种子账号密码哈希生成")
    print("=" * 60)
    print(f"\n明文密码: {password}")
    print(f"bcrypt哈希: {hashed}\n")

    print("方式一: 修改 init.sql 中的密码哈希值后重新执行建表")
    print("-" * 60)

    print("\n方式二: 数据库已建表后，直接执行以下 SQL 更新密码:")
    print("-" * 60)
    users = [
        ("admin", "管理员"),
        ("auditor01", "审核员"),
        ("teacher01", "教师"),
        ("student01", "学生"),
        ("student02", "学生"),
    ]
    for username, role_name in users:
        h = hash_password(password)
        print(f"-- {role_name} {username}")
        print(f"UPDATE `user` SET `password` = '{h}' WHERE `username` = '{username}';")

    print("\n" + "=" * 60)
    print("完成！默认账号密码均为: 123456")
    print("=" * 60)


if __name__ == "__main__":
    main()
