#!/bin/bash
# 打包为 Linux/Mac 可执行文件
echo "========================================"
echo "  批量重命名工具 - 打包为可执行文件"
echo "========================================"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "错误：未找到 python3"
    exit 1
fi

# 安装 PyInstaller
pip3 show pyinstaller &> /dev/null || pip3 install pyinstaller

echo "正在打包 ..."
echo ""

pyinstaller --onefile --name 批量重命名工具 --console rename_tool.py

echo ""
if [ -f "dist/批量重命名工具" ]; then
    echo "✓ 打包成功！"
    echo "  文件位置：dist/批量重命名工具"
    echo "  大小：$(du -h dist/批量重命名工具 | cut -f1)"
    echo ""
    echo "  运行方式：./dist/批量重命名工具 --cli ..."
    echo "  或直接：./dist/批量重命名工具 （打开GUI）"
else
    echo "✗ 打包失败"
fi
