@echo off
REM TransLearn 启动脚本

echo ========================================
echo   TransLearn - 翻译学习工具
echo ========================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.10+
    pause
    exit /b 1
)

REM 检查配置文件
if not exist "data\config.toml" (
    echo [警告] 配置文件不存在，请先运行 scripts\setup_dev.py
    pause
    exit /b 1
)

REM 启动应用
echo [启动] 正在启动 TransLearn...
python -m src

pause

