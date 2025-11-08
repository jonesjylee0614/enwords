"""
开发环境设置脚本
"""
import sys
import subprocess
from pathlib import Path

project_root = Path(__file__).parent.parent


def setup_dev_environment():
    """设置开发环境"""
    print("=" * 60)
    print("TransLearn 开发环境设置")
    print("=" * 60)
    
    # 1. 安装依赖
    print("\n[1/4] 安装 Python 依赖...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements-dev.txt"],
            cwd=project_root,
            check=True
        )
        print("✓ 依赖安装完成")
    except subprocess.CalledProcessError:
        print("✗ 依赖安装失败")
        return
    
    # 2. 创建数据目录
    print("\n[2/4] 创建数据目录...")
    data_dir = project_root / "data"
    data_dir.mkdir(exist_ok=True)
    (data_dir / "logs").mkdir(exist_ok=True)
    (data_dir / "backups").mkdir(exist_ok=True)
    print("✓ 数据目录创建完成")
    
    # 3. 复制配置文件
    print("\n[3/4] 设置配置文件...")
    config_file = data_dir / "config.toml"
    example_file = data_dir / "config.example.toml"
    
    if not config_file.exists() and example_file.exists():
        import shutil
        shutil.copy(example_file, config_file)
        print("✓ 配置文件已创建，请编辑 data/config.toml")
        print("  注意：请配置数据库连接信息!")
    elif config_file.exists():
        print("✓ 配置文件已存在")
    else:
        print("⚠ 请手动创建配置文件")
    
    # 4. 提示数据库设置
    print("\n[4/4] 数据库设置")
    print("请确保:")
    print("  1. MySQL 5.7+ 已安装并运行")
    print("  2. 创建数据库:")
    print("     CREATE DATABASE translearn CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    print("  3. 配置 data/config.toml 中的数据库连接信息")
    print("  4. 运行: python scripts/init_database.py")
    
    print("\n" + "=" * 60)
    print("开发环境设置完成!")
    print("=" * 60)
    print("\n运行应用: python -m src")


if __name__ == "__main__":
    setup_dev_environment()

