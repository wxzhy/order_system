"""
测试分页API返回格式
验证所有列表API是否返回正确的分页格式
"""

import requests
import json

BASE_URL = "http://localhost:8000"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123456"


def login():
    """管理员登录"""
    print("\n" + "=" * 60)
    print("登录管理员账户")
    print("=" * 60)

    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
    )

    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        print(f"✅ 登录成功")
        return token
    else:
        print(f"❌ 登录失败: {response.status_code}")
        return None


def test_pagination_format(api_name, url, headers, params=None):
    """测试分页格式"""
    print(f"\n{'=' * 60}")
    print(f"测试 {api_name}")
    print(f"{'=' * 60}")
    print(f"URL: {url}")
    print(f"参数: {params}")

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        print(f"❌ 请求失败: {response.status_code}")
        print(response.text)
        return False

    try:
        data = response.json()

        # 验证返回格式
        required_fields = ["records", "total", "current", "size"]
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            print(f"❌ 缺少必需字段: {missing_fields}")
            print(f"返回数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
            return False

        # 验证字段类型
        if not isinstance(data["records"], list):
            print(f"❌ records 应该是列表类型")
            return False

        if not isinstance(data["total"], int):
            print(f"❌ total 应该是整数类型")
            return False

        if not isinstance(data["current"], int):
            print(f"❌ current 应该是整数类型")
            return False

        if not isinstance(data["size"], int):
            print(f"❌ size 应该是整数类型")
            return False

        # 验证页码计算
        expected_current = (params.get("skip", 0) // params.get("limit", 100)) + 1
        if data["current"] != expected_current:
            print(
                f"⚠️  页码计算可能有误: 期望 {expected_current}, 实际 {data['current']}"
            )

        print(f"✅ 分页格式正确")
        print(f"   - 记录数: {len(data['records'])}")
        print(f"   - 总数: {data['total']}")
        print(f"   - 当前页: {data['current']}")
        print(f"   - 每页大小: {data['size']}")

        return True

    except json.JSONDecodeError:
        print(f"❌ 响应不是有效的JSON")
        return False
    except Exception as e:
        print(f"❌ 验证出错: {e}")
        return False


def main():
    """主测试流程"""
    print("\n" + "=" * 60)
    print("  分页API格式测试")
    print("=" * 60)

    # 登录
    token = login()
    if not token:
        print("\n❌ 无法继续测试,登录失败")
        return

    headers = {"Authorization": f"Bearer {token}"}

    # 测试结果统计
    tests = []

    # 1. 测试用户列表
    tests.append(
        test_pagination_format(
            "用户列表 GET /api/user/",
            f"{BASE_URL}/api/user/",
            headers,
            {"skip": 0, "limit": 10},
        )
    )

    # 2. 测试用户列表 - 第2页
    tests.append(
        test_pagination_format(
            "用户列表第2页 GET /api/user/ (skip=10)",
            f"{BASE_URL}/api/user/",
            headers,
            {"skip": 10, "limit": 10},
        )
    )

    # 3. 测试商店列表
    tests.append(
        test_pagination_format(
            "商店列表 GET /api/store/",
            f"{BASE_URL}/api/store/",
            headers,
            {"skip": 0, "limit": 10, "state": "approved"},
        )
    )

    # 4. 测试待审核商店列表
    tests.append(
        test_pagination_format(
            "待审核商店列表 GET /api/store/admin/pending",
            f"{BASE_URL}/api/store/admin/pending",
            headers,
            {"skip": 0, "limit": 10},
        )
    )

    # 5. 测试商品列表
    tests.append(
        test_pagination_format(
            "商品列表 GET /api/item/",
            f"{BASE_URL}/api/item/",
            headers,
            {"skip": 0, "limit": 10},
        )
    )

    # 6. 测试订单列表
    tests.append(
        test_pagination_format(
            "订单列表 GET /api/order/",
            f"{BASE_URL}/api/order/",
            headers,
            {"skip": 0, "limit": 10},
        )
    )

    # 7. 测试评论列表
    tests.append(
        test_pagination_format(
            "评论列表 GET /api/comment/",
            f"{BASE_URL}/api/comment/",
            headers,
            {"skip": 0, "limit": 10},
        )
    )

    # 8. 测试待审核评论列表
    tests.append(
        test_pagination_format(
            "待审核评论列表 GET /api/comment/admin/pending",
            f"{BASE_URL}/api/comment/admin/pending",
            headers,
            {"skip": 0, "limit": 10},
        )
    )

    # 统计结果
    print("\n" + "=" * 60)
    print("  测试结果汇总")
    print("=" * 60)
    passed = sum(tests)
    total = len(tests)
    print(f"通过: {passed}/{total}")

    if passed == total:
        print("✅ 所有测试通过!")
    else:
        print(f"❌ {total - passed} 个测试失败")

    print("=" * 60)


if __name__ == "__main__":
    main()
