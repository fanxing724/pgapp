#!/usr/bin/env python3
"""
切客纪快速签到脚本（简化版）
适合定时任务使用
"""

import sys
sys.path.insert(0, '/home/fanxing/文档/Default Project')

from qiekj_auto_sign import QieKjAutoSign, Config

def main():
    # 从环境变量或硬编码读取配置
    config = Config(
        token="YOUR_TOKEN_HERE",  # 填入你的Token
        app_secret="bkZVOXBiRzhZUW9BZTFrRmgrRTdleXJkbFNMZ2x3RUplQTB3d0hCMWo1bz0=",
        device_id="",
        version="1.144.0",
        phone_brand="Xiaomi",
    )
    
    try:
        signer = QieKjAutoSign(config)
        
        # 静默执行签到
        result = signer.do_sign_in()
        
        if result.get("code") == 200:
            print("✅ 签到成功")
            sys.exit(0)
        else:
            print(f"❌ 签到失败: {result.get('msg')}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ 异常: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
