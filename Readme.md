# 食堂餐点预约系统

简要说明: 本仓库包含食堂餐点预约系统的后端（FastAPI）与前端（Web + UniApp）代码。本 README 给出开发模式与部署模式下的安装与运行步骤，便于在本地或服务器上启动完整系统。

## 目录

- [开发（本地）](#开发本地)
- [数据库初始化](#数据库初始化)
- [前端（开发/构建）](#前端开发构建)
- [部署（生产）](#部署生产)
- [环境变量与配置](#环境变量与配置)
- [常见问题](#常见问题)
- [许可证](#许可证)

## 开发（本地）

以下步骤假定你在 Windows PowerShell 中工作；Linux/macOS 下命令类似（路径分隔符不同）。

### 后端（FastAPI）

先决条件:

- Python >= 3.13（pyproject.toml 中要求）
- MySQL（或使用容器方式启动 MySQL）

推荐的开发步骤（PowerShell）:

```powershell
# 1. 进入后台目录
cd backend

# 2. 创建并激活虚拟环境（PowerShell）
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. 升级 pip（可选）
python -m pip install --upgrade pip build

# 4. 安装依赖（推荐：使用 pyproject）
# 可选方式 A（可编辑安装，适合开发）
python -m pip install -e .

# 可选方式 B（如果仓库中提供 requirements.txt）
# python -m pip install -r requirements.txt

# 5. 初始化数据库（在仓库根目录执行）
# 如果在项目根目录运行：
mysql -u root -p < init.sql

# 6. 初始化管理员
python init_admin.py

# 7. 启动开发服务器（带热重载）
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# 或使用仓内的快速启动脚本（注意：脚本可能会尝试安装 requirements.txt）
python start.py
```

提示：

- 当前示例代码中，数据库连接默认写在 `backend/database.py`（包含 DB_USER/DB_PASS/DB_HOST/DB_PORT/DB_NAME），请根据你的环境修改该文件或改为从环境变量读取。
- `backend/security.py` 中有 `SECRET_KEY` 常量，生产环境请替换为安全的随机字符串并从环境变量读取。

### 前端 - Web（`frontend-web`）

先决条件:

- Node.js >= 20.19.0（参考 package.json）
- pnpm >= 8.x（推荐使用 pnpm）

开发与构建：

```bash
cd frontend-web
pnpm install
pnpm dev        # 启动开发服务器（Vite）
# 构建生产包
pnpm build
pnpm preview    # 本地预览构建结果
```

默认 Vite dev 服务器端口通常为 5173（控制台会显示实际访问地址）。

### 前端 - App / UniApp（`frontend-app`）

该子项目基于 uni-app 模板，常见命令：

```bash
cd frontend-app
pnpm install
pnpm dev:h5      # 开发 H5（浏览器）
pnpm build:h5    # 构建 H5
# 也支持 dev:app / dev:mp 等其它运行目标，见 package.json scripts
```

## 数据库初始化

项目提供了 `init.sql`（位于仓库根目录）用于创建 schema 和测试数据。示例（本地安装 mysql 的情况下）：

```bash
mysql -u root -p < init.sql
```

如果你希望用容器快速启动 MySQL（示例 docker-compose）：

```yaml
version: "3.8"
services:
	 db:
		 image: mysql:8.0
		 environment:
			 MYSQL_ROOT_PASSWORD: changeme
			 MYSQL_DATABASE: ordersystem
		 ports:
			 - "3306:3306"
		 volumes:
			 - ./init.sql:/docker-entrypoint-initdb.d/init.sql:ro
```

保存为 `docker-compose.yml` 后运行：

```bash
docker compose up -d
```

然后根据容器网络调整 `backend/database.py` 中的 DB_HOST（例如指向 `db` 服务名）。

## 部署（生产）

以下给出常见的生产部署思路（非强制）。

### 前端（已有 Dockerfile）

项目在 `frontend-app/codes/docker/Dockerfile` 中提供了一个用于构建 H5 并用 nginx 进行发布的 Dockerfile，构建并运行示例：

```bash
# 从项目根构建 frontend-app 的镜像
docker build -f frontend-app/codes/docker/Dockerfile -t ordersystem-frontend:latest frontend-app

# 运行
docker run -d -p 80:80 --name ordersystem-frontend ordersystem-frontend:latest
```

### 后端（示例 Dockerfile）

本仓库未包含后端 Dockerfile。下面提供一个最小示例供参考（把它保存为 `backend/Dockerfile`）：

```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY backend/pyproject.toml backend/ .
RUN python -m pip install --upgrade pip build
RUN pip install .
COPY backend/ .
EXPOSE 8000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

构建并运行：

```bash
docker build -t ordersystem-backend:latest -f backend/Dockerfile .
docker run -d -p 8000:8000 --env-file backend/.env --name ordersystem-backend ordersystem-backend:latest
```

注意：

- 生产环境建议使用更成熟的进程管理（如 Gunicorn + UvicornWorker）或在容器编排平台（Kubernetes）中运行，并使用反向代理（Nginx/Traefik）做 TLS、负载均衡与静态文件服务。
- 将敏感配置（如数据库密码、SECRET_KEY）通过环境变量或秘密管理系统传入容器，而不要写死在代码里。

## 环境变量示例（建议）

在 `backend/` 下创建 `.env`（或在容器中通过 env 注入），示例：

```
DB_USER=root
DB_PASS=changeme
DB_HOST=localhost
DB_PORT=3306
DB_NAME=ordersystem
SECRET_KEY=please-change-this-secret
```

提示：当前代码中数据库配置与 SECRET_KEY 写在 `backend/database.py` / `backend/security.py` 文件内；建议根据需要改为读取环境变量（使用 `os.getenv` 或 `python-dotenv`）。

## 本地一键启动建议（简要）

1.  启动 MySQL（本机或 docker-compose）
2.  从仓库根执行 `mysql -u root -p < init.sql`
3.  后端：在 `backend` 中创建并激活 venv，安装依赖并运行 `uvicorn` 或 `python start.py`
4.  前端：分别在 `frontend-web`（或 `frontend-app`）中运行 `pnpm dev`

## 常见问题

- PowerShell 无法执行激活脚本：
  ```powershell
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
  .\.venv\Scripts\Activate.ps1
  ```
- 如果 `start.py` 提示找不到 `requirements.txt`，请改用 `pip install -e .`（见上文）。
