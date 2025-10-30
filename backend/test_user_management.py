"""
用户管理API测试脚本
测试搜索、删除、重置密码功能
"""

import requests
import json

# 配置
BASE_URL = "http://localhost:8000"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123456"


# 登录获取token
def login():
    """管理员登录"""
    print("\n" + "=" * 60)
    print("步骤 1: 管理员登录")
    print("=" * 60)

    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
    )

    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        print(f"✅ 登录成功! Token: {token[:50]}...")
        return token
    else:
        print(f"❌ 登录失败: {response.status_code}")
        print(response.text)
        return None


def test_user_list(token):
    """测试用户列表获取"""
    print("\n" + "=" * 60)
    print("步骤 2: 获取用户列表 (不带搜索)")
    print("=" * 60)

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/api/user/", headers=headers, params={"skip": 0, "limit": 10}
    )

    if response.status_code == 200:
        users = response.json()
        print(f"✅ 成功获取 {len(users)} 个用户:")
        for user in users:
            print(
                f"   - ID: {user['id']}, 用户名: {user['username']}, "
                f"类型: {user['user_type']}, 邮箱: {user['email']}"
            )
        return users
    else:
        print(f"❌ 获取失败: {response.status_code}")
        print(response.text)
        return []


def test_user_search_keyword(token):
    """测试关键词搜索"""
    print("\n" + "=" * 60)
    print("步骤 3: 测试关键词搜索 (search='admin')")
    print("=" * 60)

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/api/user/",
        headers=headers,
        params={"search": "admin", "limit": 10},
    )

    if response.status_code == 200:
        users = response.json()
        print(f"✅ 搜索结果: {len(users)} 个用户")
        for user in users:
            print(
                f"   - ID: {user['id']}, 用户名: {user['username']}, "
                f"邮箱: {user['email']}"
            )
    else:
        print(f"❌ 搜索失败: {response.status_code}")
        print(response.text)


def test_user_filter_type(token):
    """测试用户类型过滤"""
    print("\n" + "=" * 60)
    print("步骤 4: 测试用户类型过滤 (user_type='customer')")
    print("=" * 60)

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/api/user/",
        headers=headers,
        params={"user_type": "customer", "limit": 10},
    )

    if response.status_code == 200:
        users = response.json()
        print(f"✅ 筛选结果: {len(users)} 个普通用户")
        for user in users:
            print(
                f"   - ID: {user['id']}, 用户名: {user['username']}, "
                f"类型: {user['user_type']}"
            )
    else:
        print(f"❌ 筛选失败: {response.status_code}")
        print(response.text)


def test_combined_search(token):
    """测试组合搜索"""
    print("\n" + "=" * 60)
    print("步骤 5: 测试组合搜索 (search='test' + user_type='vendor')")
    print("=" * 60)

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/api/user/",
        headers=headers,
        params={"search": "test", "user_type": "vendor", "limit": 10},
    )

    if response.status_code == 200:
        users = response.json()
        print(f"✅ 组合搜索结果: {len(users)} 个商家用户")
        for user in users:
            print(
                f"   - ID: {user['id']}, 用户名: {user['username']}, "
                f"类型: {user['user_type']}"
            )
    else:
        print(f"❌ 搜索失败: {response.status_code}")
        print(response.text)


def test_reset_password(token, user_id):
    """测试重置密码"""
    print("\n" + "=" * 60)
    print(f"步骤 6: 测试重置密码 (用户ID: {user_id})")
    print("=" * 60)

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.put(
        f"{BASE_URL}/api/user/{user_id}/reset-password",
        headers=headers,
        params={"new_password": "test123456"},
    )

    if response.status_code == 200:
        result = response.json()
        print(f"✅ 密码重置成功: {result.get('message')}")
    else:
        print(f"❌ 重置失败: {response.status_code}")
        print(response.text)


def test_pagination(token):
    """测试分页功能"""
    print("\n" + "=" * 60)
    print("步骤 7: 测试分页功能")
    print("=" * 60)

    headers = {"Authorization": f"Bearer {token}"}

    # 第一页
    response1 = requests.get(
        f"{BASE_URL}/api/user/", headers=headers, params={"skip": 0, "limit": 5}
    )

    if response1.status_code == 200:
        page1 = response1.json()
        print(f"✅ 第一页: {len(page1)} 个用户")
        print(f"   用户ID: {[u['id'] for u in page1]}")

    # 第二页
    response2 = requests.get(
        f"{BASE_URL}/api/user/", headers=headers, params={"skip": 5, "limit": 5}
    )

    if response2.status_code == 200:
        page2 = response2.json()
        print(f"✅ 第二页: {len(page2)} 个用户")
        print(f"   用户ID: {[u['id'] for u in page2]}")

        # 检查是否有重复
        ids1 = {u["id"] for u in page1}
        ids2 = {u["id"] for u in page2}
        overlap = ids1 & ids2
        if overlap:
            print(f"⚠️  发现重复ID: {overlap}")
        else:
            print("✅ 无重复数据")


def main():
    """主测试流程"""
    print("\n" + "=" * 60)
    print("  用户管理功能测试")
    print("=" * 60)
    print(f"\n后端地址: {BASE_URL}")
    print(f"管理员账户: {ADMIN_USERNAME}")

    # 1. 登录
    token = login()
    if not token:
        print("\n❌ 无法继续测试,登录失败")
        return

    # 2. 获取用户列表
    users = test_user_list(token)

    # 3. 关键词搜索
    test_user_search_keyword(token)

    # 4. 用户类型过滤
    test_user_filter_type(token)

    # 5. 组合搜索
    test_combined_search(token)

    # 6. 重置密码 (使用第一个非管理员用户)
    non_admin_user = next((u for u in users if u["user_type"] != "admin"), None)
    if non_admin_user:
        test_reset_password(token, non_admin_user["id"])
    else:
        print("\n⚠️  没有找到非管理员用户,跳过密码重置测试")

    # 7. 分页测试
    test_pagination(token)

    print("\n" + "=" * 60)
    print("  测试完成!")
    print("=" * 60)
    print("\n接下来请在浏览器中手动测试:")
    print("1. 访问 http://localhost:9527")
    print("2. 使用管理员账户登录")
    print("3. 导航到用户管理页面")
    print("4. 测试搜索、过滤、重置密码、删除等功能")


if __name__ == "__main__":
    main()
