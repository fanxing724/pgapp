#!/usr/bin/env python3
"""
切客纪 Token 自动获取工具（电脑端运行）
功能：手机号登录获取 Token → 可选自动更新到 GitHub Secrets
"""

import hashlib
import time
import base64
import json
import os
import sys
import requests
from pathlib import Path
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
        """发送短信验证码"""
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
        """登录获取 Token"""
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


class GitHubSecretsManager:
    """GitHub Secrets 自动更新管理器"""

    def __init__(self, repo: str, github_token: str):
        """
        参数:
            repo: 仓库地址，格式 "username/repo"
            github_token: GitHub Personal Access Token (需要 repo 权限)
        """
        self.repo = repo
        self.github_token = github_token
        self.api_base = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def _get_public_key(self) -> Optional[Dict[str, str]]:
        """获取仓库公钥"""
        url = f"{self.api_base}/repos/{self.repo}/actions/secrets/public-key"
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ 获取公钥失败: {e}")
            return None

    def _encrypt_secret(self, public_key: str, secret_value: str) -> Optional[str]:
        """使用仓库公钥加密 secret"""
        try:
            from nacl import encoding, public

            public_key_obj = public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder())
            sealed_box = public.SealedBox(public_key_obj)
            encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
            return base64.b64encode(encrypted).decode("utf-8")
        except ImportError:
            return None

    def update_secret(self, secret_name: str, secret_value: str) -> bool:
        """更新 GitHub Secret"""
        # 检查 pynacl
        try:
            from nacl import encoding, public
        except ImportError:
            print("❌ 缺少 pynacl 库，无法加密 Secret")
            print("   请运行: pip install pynacl")
            return False

        print(f"\n🔄 正在更新 GitHub Secret: {secret_name}")

        # 获取公钥
        key_data = self._get_public_key()
        if not key_data:
            return False

        # 加密
        encrypted_value = self._encrypt_secret(key_data["key"], secret_value)
        if not encrypted_value:
            return False

        # 更新 Secret
        url = f"{self.api_base}/repos/{self.repo}/actions/secrets/{secret_name}"
        data = {
            "encrypted_value": encrypted_value,
            "key_id": key_data["key_id"]
        }

        try:
            response = requests.put(url, headers=self.headers, json=data, timeout=30)
            if response.status_code in [201, 204]:
                print(f"✅ Secret '{secret_name}' 更新成功！")
                return True
            else:
                print(f"❌ 更新失败: HTTP {response.status_code}")
                print(f"   响应: {response.text}")
                return False
        except Exception as e:
            print(f"❌ 更新失败: {e}")
            return False


def load_github_config() -> Dict[str, str]:
    """加载保存的 GitHub 配置"""
    config_file = Path.home() / ".qiekj_github_config.json"
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except:
            pass
    return {}


def save_github_config(repo: str, token: str):
    """保存 GitHub 配置"""
    config_file = Path.home() / ".qiekj_github_config.json"
    try:
        with open(config_file, 'w') as f:
            json.dump({"repo": repo, "github_token": token}, f)
        os.chmod(config_file, 0o600)  # 仅所有者可读写
        print(f"✅ GitHub 配置已保存到: {config_file}")
    except Exception as e:
        print(f"⚠️  配置保存失败: {e}")


def update_github_secrets(token: str):
    """引导用户更新 GitHub Secrets"""
    print("\n" + "="*60)
    print("🔧 GitHub Secrets 自动更新")
    print("="*60)

    # 加载已保存的配置
    saved_config = load_github_config()

    # 获取仓库信息
    default_repo = saved_config.get("repo", "fanxing724/pgapp")
    repo = input(f"\n📦 GitHub 仓库 (默认: {default_repo}): ").strip() or default_repo

    # 获取 GitHub Token
    saved_gh_token = saved_config.get("github_token", "")
    if saved_gh_token:
        use_saved = input("🔑 检测到已保存的 GitHub Token，是否使用? (y/n, 默认 y): ").strip().lower()
        if use_saved in ['', 'y']:
            github_token = saved_gh_token
        else:
            github_token = input("🔑 请输入 GitHub Personal Access Token: ").strip()
    else:
        print("\n💡 需要 GitHub Personal Access Token 才能自动更新 Secrets")
        print("   获取地址: https://github.com/settings/tokens")
        print("   权限要求: 勾选 'repo' 完整权限")
        github_token = input("\n🔑 请输入 GitHub Personal Access Token: ").strip()

    if not github_token:
        print("⚠️  未提供 Token，跳过自动更新")
        return False

    # 保存配置
    save_github_config(repo, github_token)

    # 更新 Secrets
    manager = GitHubSecretsManager(repo, github_token)

    # 询问更新方式
    print("\n📝 选择更新方式:")
    print("   1. 单账号 (QIEKJ_TOKEN)")
    print("   2. 多账号 (ACCOUNTS_CONFIG)")
    choice = input("请选择 (1/2, 默认 1): ").strip() or "1"

    if choice == "1":
        return manager.update_secret("QIEKJ_TOKEN", token)
    else:
        # 读取现有的 ACCOUNTS_CONFIG 或创建新的
        print("\n💡 多账号配置")
        name = input("账号备注名 (默认: 我的账号): ").strip() or "我的账号"

        config = {
            "accounts": [
                {
                    "name": name,
                    "token": token,
                    "device_id": "",
                    "enabled": True
                }
            ]
        }
        return manager.update_secret("ACCOUNTS_CONFIG", json.dumps(config, ensure_ascii=False))


def main():
    """主函数"""
    print("="*60)
    print("🔑 切客纪 Token 自动获取工具（电脑端）")
    print("="*60)
    print("\n💡 工作流程:")
    print("   1. 本工具在电脑上运行，获取 Token")
    print("   2. 自动更新到 GitHub Secrets（可选）")
    print("   3. GitHub Actions 每天自动签到+看广告")
    print("\n⚠️  请确保使用的是你自己的手机号\n")

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

    if not token:
        print("\n❌ Token 获取失败")
        return

    # 显示 Token
    print("\n" + "="*60)
    print("🎉 Token 获取成功！")
    print("="*60)
    print(f"\n📋 你的 Token:\n")
    print(f"{token}\n")
    print("="*60)

    # 保存到本地文件
    token_dir = Path.home() / ".qiekj_tokens"
    token_dir.mkdir(exist_ok=True)
    token_file = token_dir / f"token_{phone}.txt"
    with open(token_file, 'w') as f:
        f.write(f"手机号: {phone}\n")
        f.write(f"获取时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Token: {token}\n")
    os.chmod(token_file, 0o600)
    print(f"\n💾 Token 已保存到: {token_file}")

    # 询问是否自动更新 GitHub Secrets
    print("\n" + "-"*60)
    auto_update = input("🚀 是否自动更新到 GitHub Secrets? (y/n, 默认 y): ").strip().lower()

    if auto_update in ['', 'y']:
        if update_github_secrets(token):
            print("\n" + "="*60)
            print("🎊 全部完成！")
            print("="*60)
            print("\n✅ Token 已获取并更新到 GitHub Secrets")
            print("☁️  GitHub Actions 将使用新 Token 自动签到")
            print("\n🔗 查看运行状态:")
            print(f"   https://github.com/{load_github_config().get('repo', 'fanxing724/pgapp')}/actions")
        else:
            print("\n⚠️  自动更新失败，请手动配置")
            print_manual_config(token)
    else:
        print_manual_config(token)


def print_manual_config(token: str):
    """打印手动配置说明"""
    print("\n📝 手动配置 GitHub Secrets:")
    print("   1. 访问: https://github.com/fanxing724/pgapp/settings/secrets/actions")
    print("   2. 点击 'New repository secret'")
    print("   3. 添加以下 Secret:")
    print(f"\n      Name: QIEKJ_TOKEN")
    print(f"      Value: {token}")
    print("\n   或使用多账号配置 (ACCOUNTS_CONFIG):")
    print(f'''   {{
     "accounts": [
       {{
         "name": "我的账号",
         "token": "{token}",
         "device_id": "",
         "enabled": true
       }}
     ]
   }}''')


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户取消操作")
    except Exception as e:
        print(f"\n\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
