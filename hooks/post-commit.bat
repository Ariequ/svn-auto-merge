@echo off
REM SVN Post-Commit 钩子脚本 (Windows版本)
REM 当A分支有提交时，自动检查是否需要合并到B分支

REM 配置参数
set REPOS=%1
set REV=%2
set TOOL_PATH=C:\path\to\svn-auto-merge
set PYTHON_PATH=C:\Python39\python.exe

REM 日志文件
set LOG_FILE=%TOOL_PATH%\logs\hook.log

REM 创建日志目录
if not exist "%TOOL_PATH%\logs" mkdir "%TOOL_PATH%\logs"

REM 记录钩子执行
echo %date% %time%: Post-commit hook triggered for revision %REV% >> "%LOG_FILE%"

REM 检查工具路径是否存在
if not exist "%TOOL_PATH%" (
    echo %date% %time%: Error: Tool path %TOOL_PATH% does not exist >> "%LOG_FILE%"
    exit /b 1
)

REM 检查Python是否存在
if not exist "%PYTHON_PATH%" (
    echo %date% %time%: Error: Python not found at %PYTHON_PATH% >> "%LOG_FILE%"
    exit /b 1
)

REM 切换到工具目录
cd /d "%TOOL_PATH%" || (
    echo %date% %time%: Error: Cannot change to directory %TOOL_PATH% >> "%LOG_FILE%"
    exit /b 1
)

REM 执行自动合并工具
"%PYTHON_PATH%" svn_auto_merge.py --mode hook --revision %REV% --repo-path "%REPOS%" >> "%LOG_FILE%" 2>&1

REM 记录执行结果
if %errorlevel% equ 0 (
    echo %date% %time%: Hook execution completed successfully >> "%LOG_FILE%"
) else (
    echo %date% %time%: Hook execution failed with exit code %errorlevel% >> "%LOG_FILE%"
)

exit /b 0
