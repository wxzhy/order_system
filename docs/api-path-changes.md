# API路径变更说明

## 变更概述

已将所有API路径从 `/api/*` 改为直接路径 `/*`，去除了 `/api/` 前缀。

## 变更日期

2025年10月30日

## 后端变更

### 路由器配置更新

所有后端路由器的前缀已更新：

| 模块 | 旧路径 | 新路径 |
|------|--------|--------|
| 认证 | `/api/auth` | `/auth` |
| 用户管理 | `/api/user` | `/user` |
| 商家管理 | `/api/store` | `/store` |
| 餐点管理 | `/api/item` | `/item` |
| 订单管理 | `/api/order` | `/order` |
| 评论管理 | `/api/comment` | `/comment` |

### 修改的文件

#### 路由器文件
- `backend/routers/auth.py` - 认证路由
- `backend/routers/user.py` - 用户管理路由
- `backend/routers/store.py` - 商家管理路由
- `backend/routers/item.py` - 餐点管理路由
- `backend/routers/order.py` - 订单管理路由
- `backend/routers/comment.py` - 评论管理路由

#### 依赖配置
- `backend/dependencies.py` - OAuth2 token URL 更新为 `/auth/login/token`

#### 测试文件
- `backend/test_pagination_api.py` - 分页API测试
- `backend/test_user_management.py` - 用户管理测试
- `backend/test_search_api.py` - 搜索API测试

## 新API端点示例

### 认证相关
```
POST   /auth/register          # 用户注册
POST   /auth/login             # 用户登录
POST   /auth/login/token       # Token登录(OAuth2)
POST   /auth/refresh           # 刷新token
GET    /auth/logout            # 登出
```

### 用户管理
```
GET    /user/me                # 获取当前用户信息
PUT    /user/me                # 更新当前用户信息
PUT    /user/me/password       # 修改密码
GET    /user/                  # 获取用户列表(管理员)
PUT    /user/{user_id}         # 更新用户(管理员)
DELETE /user/{user_id}         # 删除用户(管理员)
PUT    /user/{user_id}/reset-password  # 重置密码(管理员)
```

### 商家管理
```
POST   /store/                 # 创建商家
GET    /store/                 # 获取商家列表
GET    /store/{store_id}       # 获取商家详情
PUT    /store/{store_id}       # 更新商家信息
DELETE /store/{store_id}       # 删除商家
GET    /store/admin/pending    # 获取待审核商家(管理员)
PUT    /store/{store_id}/review # 审核商家(管理员)
```

### 餐点管理
```
POST   /item/                  # 添加餐点
GET    /item/                  # 获取餐点列表
GET    /item/{item_id}         # 获取餐点详情
PUT    /item/{item_id}         # 更新餐点
DELETE /item/{item_id}         # 删除餐点
GET    /item/store/{store_id}  # 获取商家餐点列表
```

### 订单管理
```
POST   /order/                 # 创建订单
GET    /order/                 # 获取订单列表
GET    /order/{order_id}       # 获取订单详情
PUT    /order/{order_id}       # 更新订单状态
DELETE /order/{order_id}       # 删除订单
GET    /order/my               # 获取我的订单
GET    /order/store/my         # 获取商家订单
```

### 评论管理
```
POST   /comment/               # 发表评论
GET    /comment/               # 获取评论列表
GET    /comment/{comment_id}   # 获取评论详情
PUT    /comment/{comment_id}   # 更新评论
DELETE /comment/{comment_id}   # 删除评论
GET    /comment/store/{store_id} # 获取商家评论
GET    /comment/my             # 获取我的评论
GET    /comment/admin/pending  # 获取待审核评论(管理员)
PUT    /comment/{comment_id}/review # 审核评论(管理员)
```

## 前端适配

前端代码已经使用无 `/api/` 前缀的路径，无需修改。

### 确认的前端文件
- `frontend-web/src/service-alova/api/auth.ts` - 已使用 `/auth/*` 路径
- `frontend-web/src/service/api/auth.ts` - 已使用 `/auth/*` 路径

## 测试验证

所有测试文件已更新以使用新路径：

```bash
# 测试分页API
python backend/test_pagination_api.py

# 测试用户管理
python backend/test_user_management.py

# 测试搜索功能
python backend/test_search_api.py
```

## 注意事项

⚠️ **破坏性变更**: 此更改会影响所有API调用

✅ **向后不兼容**: 旧的 `/api/*` 路径将不再工作

✅ **Swagger文档**: API文档会自动更新，访问 `http://localhost:8000/docs`

## 迁移指南

如果有外部服务或客户端调用API，需要更新：

### 旧调用方式
```javascript
fetch('http://localhost:8000/api/auth/login', {
  method: 'POST',
  body: JSON.stringify({ username, password })
})
```

### 新调用方式
```javascript
fetch('http://localhost:8000/auth/login', {
  method: 'POST',
  body: JSON.stringify({ username, password })
})
```

## 回滚方案

如需回滚，修改以下文件中的 `prefix` 参数：

```python
# 将 prefix="/auth" 改回 prefix="/api/auth"
router = APIRouter(prefix="/auth", tags=["认证"])
```

对所有6个路由器文件执行相同操作。
