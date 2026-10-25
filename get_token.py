#!/usr/bin/env python3
"""
切客纪 Token 自动获取工具
通过手机号+验证码登录获取 Token
"""

import hashlib
import time
import base64
import requests
from typing import Optional, Dict, Any


class QieKjLogin:
    """切客纪登录类"""

    def __init__(self):
        self.base_url = "https://userapi.qiekj.com/"
        self.app_secret = "bkZVOXBiRzhZUW9BZTFrRmgrRTdleXJkbFNMZ2x3RUplQTB3d0hCMWo1bz0="
        self.channel = "android_app"
        self.version = "1.144.0"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "okhttp/4.12.0",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        })

    def _generate_sign(self, path: str, timestamp: str, token: str = "") -> str:
        """生成请求签名"""
        try:
            decoded_secret = base64.b64decode(self.app_secret).decode('utf-8', errors='ignore')
        except:
            decoded_secret = self.app_secret

        sign_str = (
            f"appSecret={decoded_secret}"
            f"&channel={self.channel}"
            f"&timestamp={timestamp}"
            f"&token={token}"
            f"&version={self.version}"
            f"&{path}"
        )
        return hashlib.sha256(sign_str.encode('utf-8')).hexdigest()

    def _build_headers(self, path: str, token: str = "") -> Dict[str, str]:
        """构建请求头"""
        timestamp = str(int(time.time() * 1000))
        sign = self._generate_sign(path, timestamp, token)

        return {
            "Authorization": token,
            "version": self.version,
            "channel": self.channel,
            "phoneBrand": "Xiaomi",
            "deviceId": "",
            "timestamp": timestamp,
            "sign": sign,
        }

    def _post(self, path: str, data: Dict[str, Any], token: str = "") -> Dict[str, Any]:
        """发送POST请求"""
        url = f"{self.base_url}{path}"
        headers = self._build_headers(path, token)

        try:
            response = self.session.post(url, headers=headers, data=data, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"code": -1, "msg": str(e)}

    def send_sms_code(self, phone: str) -> bool:
        """
        发送短信验证码

        参数:
            phone: 手机号

        返回:
            成功返回 True，失败返回 False
        """
        print(f"\n📱 正在向 {phone} 发送验证码...")

        result = self._post("common/sms/sendCode", {
            "phone": phone,
            "template": "reg"
        })

        if result.get("code") in [0, 200]:
            print("✅ 验证码发送成功！")
            print("📩 请查看手机短信，验证码有效期通常为 5 分钟")
            return True
        else:
            print(f"❌ 验证码发送失败: {result.get('msg', '未知错误')}")
            return False

    def login_and_get_token(self, phone: str, verify_code: str) -> Optional[str]:
        """
        使用手机号+验证码登录，获取 Token

        参数:
            phone: 手机号
            verify_code: 短信验证码

        返回:
            成功返回 Token 字符串，失败返回 None
        """
        print(f"\n🔐 正在登录...")

        result = self._post("user/reg", {
            "channel": "android_app",
            "phone": phone,
            "verify": verify_code
        })

        if result.get("code") in [0, 200]:
            data = result.get("data", {})
            token = data.get("token")

            if token:
                print("✅ 登录成功！")
                return token
            else:
                print("❌ 登录成功但未返回 Token")
                return None
        else:
            print(f"❌ 登录失败: {result.get('msg', '未知错误')}")
            return None


def main():
    """主函数"""
    print("="*60)
    print("🔑 切客纪 Token 自动获取工具")
    print("="*60)
    print("\n💡 此工具通过手机号+验证码登录获取 Token")
    print("⚠️  请确保使用的是你自己的手机号\n")

    # 创建登录实例
    login = QieKjLogin()

    # 获取手机号
    phone = input("📱 请输入手机号: ").strip()
    if not phone or len(phone) != 11:
        print("❌ 手机号格式不正确")
        return

    # 发送验证码
    if not login.send_sms_code(phone):
        print("\n❌ 验证码发送失败，请检查：")
        print("   1. 手机号是否正确")
        print("   2. 网络连接是否正常")
        print("   3. 是否频繁请求（请稍后再试）")
        return

    # 获取验证码
    print("\n" + "-"*60)
    verify_code = input("🔢 请输入收到的验证码: ").strip()
    if not verify_code:
        print("❌ 验证码不能为空")
        return

    # 登录获取 Token
    token = login.login_and_get_token(phone, verify_code)

    if token:
        print("\n" + "="*60)
        print("🎉 Token 获取成功！")
        print("="*60)
        print(f"\n📋 你的 Token:\n")
        print(f"{token}\n")
        print("="*60)

        # 保存到文件
        save = input("\n💾 是否保存 Token 到文件? (y/n): ").strip().lower()
        if save == 'y':
            filename = f"token_{phone}.txt"
            with open(filename, 'w') as f:
                f.write(f"手机号: {phone}\n")
                f.write(f"获取时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Token: {token}\n")
            print(f"✅ Token 已保存到: {filename}")

        # 复制到剪贴板提示
        print("\n💡 提示:")
        print("   1. 请妥善保管 Token，不要分享给他人")
        print("   2. Token 有效期通常为 7-30 天")
        print("   3. 过期后需要重新获取")
        print("\n📝 下一步:")
        print("   将 Token 添加到 GitHub Secrets 或本地配置文件")

        # 询问是否直接配置到 GitHub
        print("\n" + "-"*60)
        config_now = input("🔧 是否现在配置到 GitHub Secrets? (y/n): ").strip().lower()
        if config_now == 'y':
            print("\n📋 请复制以下内容到 GitHub Secrets:")
            print("\n方式一：单账号配置")
            print(f"   Name: QIEKJ_TOKEN")
            print(f"   Value: {token}")
            print("\n方式二：多账号配置（推荐）")
            print(f"   Name: ACCOUNTS_CONFIG")
            print(f"   Value:")
            print(f"""   {{
     "accounts": [
       {{
         "name": "账号_{phone[-4:]}",
         "token": "{token}",
         "device_id": "",
         "enabled": true
       }}
     ]
   }}""")
            print("\n🔗 配置地址: https://github.com/fanxing724/pgapp/settings/secrets/actions")
    else:
        print("\n❌ Token 获取失败")
        print("\n可能的原因:")
        print("   1. 验证码错误或已过期")
        print("   2. 网络连接问题")
        print("   3. 服务器异常")
        print("\n💡 建议:")
        print("   重新运行脚本，使用新的验证码")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户取消操作")
    except Exception as e:
        print(f"\n\n❌ 发生错误: {e}")
