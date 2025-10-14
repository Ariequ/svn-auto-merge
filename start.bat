@echo off
echo SVN自动合并智能体工具启动中...
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.7+
    pause
    exit /b 1
)

REM 检查虚拟环境
if not exist "venv" (
    echo 创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 安装依赖
echo 安装依赖包...
pip install -r requirements.txt

REM 检查配置文件
if not exist "config.json" (
    echo 错误: 未找到config.json配置文件
    echo 请先配置分支路径和匹配规则
    pause
    exit /b 1
)

REM 启动程序
echo 启动SVN自动合并智能体...
python svn_auto_merge.py

pause
