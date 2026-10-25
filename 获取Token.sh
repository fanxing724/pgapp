#!/bin/bash
# 切客纪 Token 获取工具 - 一键运行脚本

cd "$(dirname "$0")"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 首次运行，正在创建虚拟环境..."
    python3 -m venv venv
    echo "✅ 虚拟环境创建完成"
    echo ""
    echo "📥 正在安装依赖..."
    ./venv/bin/pip install pynacl requests -q
    echo "✅ 依赖安装完成"
    echo ""
fi

# 运行 Token 获取工具
./venv/bin/python get_token.py
