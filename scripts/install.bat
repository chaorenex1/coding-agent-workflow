@echo off
REM Orchestrator Windows 安装脚本
REM
REM 使用方法:
REM     install.bat [options]
REM
REM 选项:
REM     --skip-deps          跳过依赖检查
REM     --skip-memex         跳过 memex-cli 安装
REM     --skip-workflow      跳过 workflow 安装
REM     --skip-requirements  跳过 requirements 安装
REM     --verbose            详细输出

setlocal enabledelayedexpansion

REM 设置编码为UTF-8
chcp 65001 >nul

echo.
echo ======================================================================
echo   Orchestrator V3 - Windows 安装程序
echo ======================================================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    exit /b 1
)

echo [信息] 找到 Python:
python --version

REM 运行Python安装脚本
echo.
echo 启动 Python 安装脚本...
echo.

python "%~dp0install_orchestrator.py" %*

if errorlevel 1 (
    echo.
    echo [错误] 安装失败，请查看上述错误信息
    exit /b 1
) else (
    echo.
    echo [成功] 安装完成！
    echo.
    echo 下一步:
    echo   1. 运行验证: python scripts\verify_installation.py
    echo   2. 运行测试: python orchestrator\tests\test_phase5_simple.py
    echo   3. 查看文档: docs\ARCHITECTURE.md
    echo.
)

endlocal
