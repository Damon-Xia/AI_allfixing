@echo off
chcp 65001 >nul
echo ========================================
echo   批量重命名工具 - 打包为 .exe
echo ========================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

REM 安装 PyInstaller（如果没有）
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo 正在安装 PyInstaller ...
    pip install pyinstaller
)

echo.
echo 正在打包，请稍候 ...
echo.

pyinstaller --onefile --name 批量重命名工具 --windowed rename_tool.py

echo.
if exist "dist\批量重命名工具.exe" (
    echo ✓ 打包成功！
    echo.
    echo   文件位置：dist\批量重命名工具.exe
    echo   大小：
    for %%A in ("dist\批量重命名工具.exe") do echo   %%~zA 字节
    echo.
    echo 双击 dist\批量重命名工具.exe 即可使用（无需安装 Python）
) else (
    echo ✗ 打包失败，请检查上方错误信息
)

echo.
pause
