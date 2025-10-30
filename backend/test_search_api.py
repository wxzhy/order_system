"""
测试搜索API功能

使用方法:
1. 启动后端服务: python -m uvicorn backend.main:app --reload
2. 运行测试脚本: python backend/test_search_api.py

测试覆盖:
- 用户搜索 (username, email, phone)
- 商家搜索 (name, description, address)
- 餐点搜索 (name, description, 价格范围, 库存状态)
- 订单搜索 (商家名称, 用户名)
- 评论搜索 (content, 商家名称, 用户名)
"""

import requests
import json

BASE_URL = "http://localhost:8000"


def login_admin():
    """登录管理员账户"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": "admin", "password": "admin123456"},
    )
    if response.status_code == 200:
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    else:
        print(f"登录失败: {response.status_code} - {response.text}")
        return None


def test_user_search(headers):
    """测试用户搜索"""
    print("\n=== 测试用户搜索 ===")

    # 搜索用户名包含 "vendor" 的用户
    response = requests.get(
        f"{BASE_URL}/api/user/", params={"search": "vendor"}, headers=headers
    )
    print(f"1. 搜索 'vendor': 找到 {len(response.json())} 个用户")
    for user in response.json():
        print(f"   - {user['username']} ({user['email']})")

    # 搜索邮箱包含 "example" 的用户
    response = requests.get(
        f"{BASE_URL}/api/user/", params={"search": "example"}, headers=headers
    )
    print(f"2. 搜索 'example': 找到 {len(response.json())} 个用户")

    # 按用户类型筛选
    response = requests.get(
        f"{BASE_URL}/api/user/", params={"user_type": "vendor"}, headers=headers
    )
    print(f"3. 筛选商家用户: 找到 {len(response.json())} 个用户")


def test_store_search(headers):
    """测试商家搜索"""
    print("\n=== 测试商家搜索 ===")

    # 搜索商家名称
    response = requests.get(
        f"{BASE_URL}/api/store/", params={"search": "美食", "state": "approved"}
    )
    print(f"1. 搜索 '美食': 找到 {len(response.json())} 个商家")
    for store in response.json():
        print(f"   - {store['name']} ({store['address']})")

    # 按状态筛选
    response = requests.get(
        f"{BASE_URL}/api/store/", params={"state": "pending"}, headers=headers
    )
    print(f"2. 待审核的商家: 找到 {len(response.json())} 个")

    # 按店主ID筛选
    response = requests.get(
        f"{BASE_URL}/api/store/", params={"owner_id": 2, "state": "approved"}
    )
    print(f"3. 指定店主的商家: 找到 {len(response.json())} 个")


def test_item_search(headers):
    """测试餐点搜索"""
    print("\n=== 测试餐点搜索 ===")

    # 搜索餐点名称
    response = requests.get(f"{BASE_URL}/api/item/", params={"search": "饭"})
    print(f"1. 搜索 '饭': 找到 {len(response.json())} 个餐点")
    for item in response.json():
        print(f"   - {item['name']}: ¥{item['price']} (库存: {item['quantity']})")

    # 按价格范围筛选
    response = requests.get(
        f"{BASE_URL}/api/item/", params={"min_price": 10, "max_price": 30}
    )
    print(f"2. 价格 ¥10-30: 找到 {len(response.json())} 个餐点")

    # 筛选有库存的餐点
    response = requests.get(f"{BASE_URL}/api/item/", params={"in_stock": True})
    print(f"3. 有库存的餐点: 找到 {len(response.json())} 个")

    # 筛选无库存的餐点
    response = requests.get(f"{BASE_URL}/api/item/", params={"in_stock": False})
    print(f"4. 无库存的餐点: 找到 {len(response.json())} 个")

    # 按商家筛选
    response = requests.get(f"{BASE_URL}/api/item/", params={"store_id": 1})
    print(f"5. 商家ID=1的餐点: 找到 {len(response.json())} 个")


def test_order_search(headers):
    """测试订单搜索"""
    print("\n=== 测试订单搜索 ===")

    # 搜索订单（通过商家名称或用户名）
    response = requests.get(
        f"{BASE_URL}/api/order/", params={"search": "vendor"}, headers=headers
    )
    print(f"1. 搜索 'vendor': 找到 {len(response.json())} 个订单")

    # 按状态筛选
    response = requests.get(
        f"{BASE_URL}/api/order/", params={"state": "pending"}, headers=headers
    )
    print(f"2. 待审核的订单: 找到 {len(response.json())} 个")

    # 按商家ID筛选
    response = requests.get(
        f"{BASE_URL}/api/order/", params={"store_id": 1}, headers=headers
    )
    print(f"3. 商家ID=1的订单: 找到 {len(response.json())} 个")

    # 按用户ID筛选
    response = requests.get(
        f"{BASE_URL}/api/order/", params={"user_id": 4}, headers=headers
    )
    print(f"4. 用户ID=4的订单: 找到 {len(response.json())} 个")


def test_comment_search(headers):
    """测试评论搜索"""
    print("\n=== 测试评论搜索 ===")

    # 搜索评论内容
    response = requests.get(
        f"{BASE_URL}/api/comment/", params={"search": "好", "state": "approved"}
    )
    print(f"1. 搜索 '好': 找到 {len(response.json())} 条评论")
    for comment in response.json()[:3]:  # 只显示前3条
        print(f"   - {comment['content'][:30]}...")

    # 按商家筛选
    response = requests.get(f"{BASE_URL}/api/comment/", params={"store_id": 1})
    print(f"2. 商家ID=1的评论: 找到 {len(response.json())} 条")

    # 按状态筛选
    response = requests.get(
        f"{BASE_URL}/api/comment/", params={"state": "pending"}, headers=headers
    )
    print(f"3. 待审核的评论: 找到 {len(response.json())} 条")


def main():
    print("开始测试搜索API功能...")

    # 登录获取token
    headers = login_admin()
    if not headers:
        print("无法登录，请确保后端服务正在运行且管理员账户已创建")
        return

    print(f"✓ 管理员登录成功")

    # 运行所有测试
    try:
        test_user_search(headers)
        test_store_search(headers)
        test_item_search(headers)
        test_order_search(headers)
        test_comment_search(headers)

        print("\n" + "=" * 50)
        print("✓ 所有搜索API测试完成！")
        print("=" * 50)

    except Exception as e:
        print(f"\n✗ 测试出错: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
