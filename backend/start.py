"""
快速启动脚本
用于一键初始化和启动后端服务
"""

import subprocess
import sys
import os


def print_section(title):
    """打印分隔符"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


def check_python_version():
    """检查 Python 版本"""
    print_section("检查 Python 版本")
    if sys.version_info < (3, 10):
        print("❌ Python 版本过低，需要 Python 3.10 或更高版本")
        print(f"   当前版本: {sys.version}")
        return False
    print(f"✅ Python 版本: {sys.version}")
    return True


def check_mysql():
    """检查 MySQL 是否运行"""
    print_section("检查 MySQL 服务")
    try:
        import importlib.util

        spec = importlib.util.find_spec("mysqlclient")
        if spec is not None:
            print("✅ mysqlclient 已安装")
            return True
        else:
            print("⚠️  mysqlclient 未安装，将尝试安装...")
            return False
    except ImportError:
        print("⚠️  mysqlclient 未安装，将尝试安装...")
        return False


def install_dependencies():
    """安装依赖"""
    print_section("安装依赖包")
    try:
        print("正在安装依赖...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            check=True,
        )
        print("✅ 依赖安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败: {e}")
        return False


def check_database_config():
    """检查数据库配置"""
    print_section("检查数据库配置")

    # 检查是否有 .env 文件
    if os.path.exists(".env"):
        print("✅ 找到 .env 配置文件")
        return True
    elif os.path.exists(".env.example"):
        print("⚠️  未找到 .env 文件，但找到了 .env.example")
        print("   请复制 .env.example 为 .env 并修改数据库配置")
        return False
    else:
        print("⚠️  未找到配置文件")
        print("   请在 backend/database.py 中配置数据库连接")
        return True  # 继续执行，使用默认配置


def init_admin():
    """初始化管理员账户"""
    print_section("初始化管理员账户")
    try:
        result = subprocess.run(
            [sys.executable, "init_admin.py"], capture_output=True, text=True
        )
        if "已存在" in result.stdout:
            print("ℹ️  管理员账户已存在")
        else:
            print(result.stdout)
        return True
    except Exception as e:
        print(f"⚠️  管理员初始化失败: {e}")
        print("   可以稍后手动运行: python init_admin.py")
        return True  # 不阻止启动


def start_server():
    """启动服务器"""
    print_section("启动服务器")
    print("正在启动 FastAPI 服务器...")
    print("访问地址:")
    print("  - API 文档 (Swagger): http://localhost:8000/docs")
    print("  - API 文档 (ReDoc):   http://localhost:8000/redoc")
    print("  - 健康检查:           http://localhost:8000/health")
    print("\n按 Ctrl+C 停止服务器\n")
    print("-" * 60)

    try:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "backend.main:app",
                "--reload",
                "--host",
                "0.0.0.0",
                "--port",
                "8000",
            ]
        )
    except KeyboardInterrupt:
        print("\n\n服务器已停止")


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("  食堂餐点预定系统 - 后端快速启动")
    print("=" * 60)

    # 1. 检查 Python 版本
    if not check_python_version():
        sys.exit(1)

    # 2. 安装依赖
    if not install_dependencies():
        print("\n❌ 依赖安装失败，请手动安装")
        print("   运行: pip install -r requirements.txt")
        sys.exit(1)

    # 3. 检查数据库配置
    check_database_config()

    # 4. 初始化管理员
    init_admin()

    # 5. 启动服务器
    start_server()


if __name__ == "__main__":
    main()
