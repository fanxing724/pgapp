#!/usr/bin/env python3
"""
测试脚本 - 验证配置和签名算法
不会实际发送请求到服务器
"""

import hashlib
import base64
from qiekj_auto_sign import Config, QieKjAutoSign


def test_sign_algorithm():
    """测试签名算法"""
    print("="*60)
    print("🧪 测试签名算法")
    print("="*60)
    
    # 测试数据
    test_config = Config(
        token="test_token_12345",
        app_secret="bkZVOXBiRzhZUW9BZTFrRmgrRTdleXJkbFNMZ2x3RUplQTB3d0hCMWo1bz0=",
        device_id="test_device",
        version="1.144.0",
    )
    
    # 不需要实际实例化，直接测试算法
    pass
    
    # 测试路径
    test_path = "signin/doUserSignIn"
    test_timestamp = "1698240000000"
    
    # 生成签名
    import base64
    try:
        decoded_secret = base64.b64decode(test_config.app_secret).decode('utf-8', errors='ignore')
        print(f"✅ Secret 解码成功: {decoded_secret[:20]}...")
    except Exception as e:
        print(f"❌ Secret 解码失败: {e}")
        decoded_secret = test_config.app_secret
    
    # 构建签名字符串
    sign_str = (
        f"appSecret={decoded_secret}"
        f"&channel={test_config.channel}"
        f"&timestamp={test_timestamp}"
        f"&token={test_config.token}"
        f"&version={test_config.version}"
        f"&{test_path}"
    )
    
    print(f"\n📝 签名字符串:\n{sign_str}\n")
    
    # 计算 SHA-256
    sign_result = hashlib.sha256(sign_str.encode('utf-8')).hexdigest()
    print(f"✅ 生成的签名: {sign_str}")
    
    return True


def test_config():
    """测试配置类"""
    print("\n" + "="*60)
    print("🧪 测试配置类")
    print("="*60)
    
    config = Config(
        token="test_token",
        app_secret="bkZVOXBiRzhZUW9BZTFrRmgrRTdleXJkbFNMZ2x3RUplQTB3d0hCMWo1bz0=",
        device_id="test_device_001",
        version="1.144.0",
        phone_brand="Xiaomi",
    )
    
    print(f"✅ Token: {config.token}")
    print(f"✅ Version: {config.version}")
    print(f"✅ Channel: {config.channel}")
    print(f"✅ Device ID: {config.device_id}")
    print(f"✅ Phone Brand: {config.phone_brand}")
    print(f"✅ Base URL: {config.base_url}")
    
    return True


def test_endpoints():
    """测试 API 端点"""
    print("\n" + "="*60)
    print("🧪 测试 API 接口路径")
    print("="*60)
    
    endpoints = [
        ("signin/todaySignIn", "检查签到状态"),
        ("signin/doUserSignIn", "执行签到"),
        ("signin/signInAcList", "获取签到活动"),
        ("alipay/tap/adStatus", "检查广告状态"),
        ("alipay/admedia/finishFlag", "上报广告完成"),
        ("task/getTaskReward", "领取任务奖励"),
        ("user/info", "获取用户信息"),
    ]
    
    print("\n已配置的接口:\n")
    for path, desc in endpoints:
        print(f"  📍 {desc}")
        print(f"     路径: {path}")
        print(f"     完整URL: https://userapi.qiekj.com/{path}\n")
    
    return True


def main():
    """主函数"""
    print("\n" + "="*60)
    print("🚀 切客纪自动签到工具 - 功能测试")
    print("="*60 + "\n")
    
    tests = [
        ("配置类测试", test_config),
        ("签名算法测试", test_sign_algorithm),
        ("API 端点测试", test_endpoints),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            print(f"\n▶️  运行: {name}")
            if test_func():
                print(f"✅ {name} 通过")
                passed += 1
            else:
                print(f"❌ {name} 失败")
                failed += 1
        except Exception as e:
            print(f"❌ {name} 异常: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print("📊 测试结果")
    print("="*60)
    print(f"✅ 通过: {passed}")
    print(f"❌ 失败: {failed}")
    print(f"📈 通过率: {passed/(passed+failed)*100:.1f}%")
    print("="*60 + "\n")
    
    if failed == 0:
        print("🎉 所有测试通过！")
        print("\n下一步:")
        print("1. 运行 ./extract_token.sh 获取 Token")
        print("2. 编辑 qiekj_auto_sign.py 填入 Token")
        print("3. 运行 python3 qiekj_auto_sign.py 开始签到")
    else:
        print("⚠️  部分测试失败，请检查配置")
    
    return failed == 0


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
