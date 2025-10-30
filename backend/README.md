# 食堂餐点预定系统 - 后端 API

基于 FastAPI + SQLModel 实现的食堂餐点预定系统后端接口。

## 快速开始

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置数据库

修改 `backend/database.py` 中的数据库连接配置：

```python
DB_USER = "root"
DB_PASS = "your_password"
DB_HOST = "localhost"
DB_PORT = 3306
DB_NAME = "ordersystem"
```

### 3. 初始化数据库

```bash
mysql -u root -p < ../init.sql
```

### 4. 创建管理员账户

```bash
python init_admin.py
```

### 5. 启动服务

```bash
python main.py
```

或使用 uvicorn：

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. 访问 API 文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- 健康检查: http://localhost:8000/health

## API 端点

### 认证模块 `/auth`
- `POST /auth/register` - 用户注册
- `POST /auth/login` - 用户登录
- `POST /auth/refresh` - 刷新令牌
- `GET /auth/me` - 获取当前用户信息

### 用户管理 `/user`
- `GET /user/me` - 获取当前用户信息
- `PUT /user/me` - 更新当前用户信息
- `PUT /user/me/password` - 修改密码
- `DELETE /user/me` - 注销账户
- `GET /user/` - 管理员查询用户列表
- `GET /user/{user_id}` - 管理员查询指定用户
- `PUT /user/{user_id}` - 管理员更新用户
- `DELETE /user/{user_id}` - 管理员删除用户

### 商家管理 `/store`
- `POST /store/` - 发布商家信息
- `GET /store/` - 查询商家列表
- `GET /store/my` - 查询自己的商家信息
- `GET /store/{store_id}` - 查询指定商家
- `PUT /store/{store_id}` - 更新商家信息
- `DELETE /store/{store_id}` - 删除商家信息
- `GET /store/admin/pending` - 管理员查询待审核商家
- `POST /store/{store_id}/review` - 管理员审核商家

### 餐点管理 `/item`
- `POST /item/` - 添加餐点
- `GET /item/` - 查询餐点列表
- `GET /item/store/{store_id}` - 查询指定商家的餐点
- `GET /item/{item_id}` - 查询指定餐点
- `PUT /item/{item_id}` - 更新餐点
- `DELETE /item/{item_id}` - 删除餐点

### 订单管理 `/order`
- `POST /order/` - 创建订单
- `GET /order/` - 查询订单列表
- `GET /order/my` - 查询自己的订单
- `GET /order/store/my` - 商家查询店铺订单
- `GET /order/{order_id}` - 查询指定订单
- `PUT /order/{order_id}` - 更新订单状态
- `DELETE /order/{order_id}` - 删除订单

### 评论管理 `/comment`
- `POST /comment/` - 发表评论
- `GET /comment/` - 查询评论列表
- `GET /comment/store/{store_id}` - 查询指定商家的评论
- `GET /comment/my` - 查询自己的评论
- `GET /comment/{comment_id}` - 查询指定评论
- `PUT /comment/{comment_id}` - 更新评论
- `DELETE /comment/{comment_id}` - 删除评论
- `GET /comment/admin/pending` - 管理员查询待审核评论
- `POST /comment/{comment_id}/review` - 管理员审核评论

## 用户角色

- **admin**: 管理员，可以管理所有用户和数据，审核商家和评论
- **vendor**: 商家，可以发布商家信息和餐点，处理订单
- **customer**: 普通用户，可以浏览商家、下单、发表评论

## 技术栈

- **FastAPI** - Web 框架
- **SQLModel** - ORM 框架
- **MySQL** - 数据库
- **JWT** - 身份认证
- **Pydantic** - 数据验证

## 项目结构

```
backend/
├── __init__.py
├── main.py              # 主应用入口
├── database.py          # 数据库配置
├── models.py            # 数据模型
├── schemas.py           # Pydantic Schema
├── security.py          # 安全相关
├── dependencies.py      # 依赖注入
├── init_admin.py        # 管理员初始化脚本
├── requirements.txt     # Python 依赖
└── routers/             # API 路由
    ├── auth.py          # 认证
    ├── user.py          # 用户管理
    ├── store.py         # 商家管理
    ├── item.py          # 餐点管理
    ├── order.py         # 订单管理
    └── comment.py       # 评论管理
```

## 数据库设计

系统使用 MySQL 数据库，包含以下表：

- `user` - 用户表（支持管理员、商家、普通用户）
- `store` - 商家信息表
- `item` - 餐点信息表
- `order` - 订单表
- `orderitem` - 订单商品表
- `comment` - 评论表

详见 `../init.sql`

## 开发说明

### 数据库表名映射

SQLModel 使用小写单数形式的表名：
- User → `user`
- Store → `store`
- Item → `item`
- Order → `order`
- OrderItem → `orderitem`
- Comment → `comment`

### API 路径规范

所有 API 路径使用单数形式：
- `/api/user` - 用户相关
- `/api/store` - 商家相关
- `/api/item` - 餐点相关
- `/api/order` - 订单相关
- `/api/comment` - 评论相关

## 注意事项

1. 首次启动前需要执行数据库初始化脚本
2. 需要创建管理员账户才能进行管理操作
3. 商家发布信息需要管理员审核
4. 用户发表评论需要管理员审核
5. 订单创建会自动扣减库存，取消会恢复库存

## 默认账户

运行 `init_admin.py` 后会创建默认管理员账户：
- 用户名: `admin`
- 密码: `admin123456`

⚠️ **请务必在生产环境中修改默认密码！**

## 许可证

本项目仅供学习交流使用。
