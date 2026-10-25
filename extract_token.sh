#!/bin/bash
# 切客纪 Token 提取辅助脚本

echo "==================================="
echo "  切客纪 Token 提取工具"
echo "==================================="
echo ""

# 检查 ADB 是否可用
if ! command -v adb &> /dev/null; then
    echo "❌ 未找到 adb 命令"
    echo "请先安装 Android SDK Platform Tools:"
    echo "  sudo apt install adb  # Ubuntu/Debian"
    echo "  brew install android-platform-tools  # macOS"
    exit 1
fi

echo "📱 检查设备连接..."
adb devices

# 检查是否有设备连接
if ! adb devices | grep -q "device$"; then
    echo ""
    echo "❌ 未检测到设备连接"
    echo "请确保："
    echo "  1. 手机已通过 USB 连接到电脑"
    echo "  2. 手机已开启 USB 调试模式"
    echo "  3. 已在手机上授权此电脑的调试请求"
    exit 1
fi

echo ""
echo "✅ 设备已连接"
echo ""

# 检查是否有 root 权限
echo "🔐 检查 root 权限..."
if adb shell "su -c 'echo test'" 2>/dev/null | grep -q "test"; then
    echo "✅ 已获取 root 权限"
    HAS_ROOT=true
else
    echo "⚠️  无 root 权限，将使用备用方案"
    HAS_ROOT=false
fi

echo ""
echo "==================================="
echo "  开始提取 Token"
echo "==================================="
echo ""

if [ "$HAS_ROOT" = true ]; then
    # 方案1: 使用 root 直接读取 SharedPreferences
    echo "📂 尝试从 SharedPreferences 提取..."
    
    # 列出所有 XML 文件
    PREFS_FILES=$(adb shell "su -c 'ls /data/data/com.qiekj.user/shared_prefs/*.xml'" 2>/dev/null)
    
    if [ -n "$PREFS_FILES" ]; then
        echo "找到以下配置文件："
        echo "$PREFS_FILES" | while read -r file; do
            echo "  - $(basename $file)"
        done
        echo ""
        
        # 搜索包含 token 的文件
        for file in $PREFS_FILES; do
            TOKEN=$(adb shell "su -c 'cat $file'" 2>/dev/null | grep -i "token" | head -1)
            if [ -n "$TOKEN" ]; then
                echo "✅ 在 $(basename $file) 中找到 Token:"
                echo ""
                echo "$TOKEN"
                echo ""
                
                # 尝试提取纯 token 值
                TOKEN_VALUE=$(echo "$TOKEN" | sed -n 's/.*value="\([^"]*\)".*/\1/p')
                if [ -n "$TOKEN_VALUE" ]; then
                    echo "📋 提取的 Token 值:"
                    echo "$TOKEN_VALUE"
                    echo ""
                    
                    # 复制到剪贴板（如果可用）
                    if command -v xclip &> /dev/null; then
                        echo "$TOKEN_VALUE" | xclip -selection clipboard
                        echo "✅ Token 已复制到剪贴板"
                    elif command -v xsel &> /dev/null; then
                        echo "$TOKEN_VALUE" | xsel --clipboard
                        echo "✅ Token 已复制到剪贴板"
                    fi
                fi
            fi
        done
    else
        echo "❌ 未找到 SharedPreferences 文件"
    fi
else
    echo "⚠️  无 root 权限，无法直接读取应用数据"
    echo ""
    echo "📝 备用方案："
    echo ""
    echo "请使用以下方法之一获取 Token："
    echo ""
    echo "方法1: 使用抓包工具（推荐）"
    echo "  1. 在手机上安装 HttpCanary 或类似抓包工具"
    echo "  2. 打开抓包，然后使用切客纪 APP"
    echo "  3. 在抓包记录中找到请求头 Authorization 的值"
    echo ""
    echo "方法2: 使用 Root Explorer 等文件管理器"
    echo "  1. 使用有 root 权限的文件管理器"
    echo "  2. 导航到 /data/data/com.qiekj.user/shared_prefs/"
    echo "  3. 打开 XML 文件，搜索 token 关键词"
    echo ""
    echo "方法3: 使用模拟器"
    echo "  1. 在 Android 模拟器中安装切客纪"
    echo "  2. 使用 adb root 获取权限"
    echo "  3. 重新运行此脚本"
fi

echo ""
echo "==================================="
echo "  提取完成"
echo "==================================="
echo ""

# 附加功能：提取设备 ID
echo "🔍 是否还需要提取设备 ID (deviceId)? (y/n)"
read -r response

if [[ "$response" =~ ^[Yy]$ ]]; then
    echo ""
    echo "📱 正在获取设备信息..."
    
    if [ "$HAS_ROOT" = true ]; then
        DEVICE_ID=$(adb shell "su -c 'cat /data/data/com.qiekj.user/shared_prefs/*.xml'" 2>/dev/null | grep -i "oaid\|deviceId" | head -1)
        if [ -n "$DEVICE_ID" ]; then
            echo "✅ 找到设备 ID 相关信息:"
            echo "$DEVICE_ID"
        else
            echo "⚠️  未在配置文件中找到设备 ID"
        fi
    fi
    
    # 获取手机型号
    BRAND=$(adb shell getprop ro.product.brand | tr -d '\r')
    MODEL=$(adb shell getprop ro.product.model | tr -d '\r')
    echo ""
    echo "📱 设备品牌: $BRAND"
    echo "📱 设备型号: $MODEL"
fi

echo ""
echo "✨ 完成！请将提取的信息填入 qiekj_auto_sign.py 的配置中"
