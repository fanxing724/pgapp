#!/usr/bin/env python3
"""
GitHub Actions 专用签到脚本
优化了无头运行、日志输出、错误处理
"""

import os
import sys
import json
import time
import hashlib
import base64
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime

try:
    import requests
except ImportError:
    print("❌ 缺少 requests 库，正在安装...")
    os.system("pip install requests")
    import requests


@dataclass
class Account:
    """账号配置"""
    name: str
    token: str
    device_id: str = ""
    app_secret: str = "bkZVOXBiRzhZUW9BZTFrRmgrRTdleXJkbFNMZ2x3RUplQTB3d0hCMWo1bz0="
    version: str = "1.144.0"
    phone_brand: str = "Xiaomi"
    enabled: bool = True


class GitHubAutoSign:
    """GitHub Actions 自动签到"""
    
    def __init__(self, account: Account):
        self.account = account
        self.base_url = "https://userapi.qiekj.com/"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "okhttp/4.12.0",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        })
        self.results = []
    
    def log(self, message: str, level: str = "INFO"):
        """输出日志（GitHub Actions 格式）"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # GitHub Actions 特殊格式
        if level == "ERROR":
            print(f"::error::{message}")
        elif level == "WARNING":
            print(f"::warning::{message}")
        elif level == "NOTICE":
            print(f"::notice::{message}")
        else:
            print(f"[{timestamp}] {message}")
        
        self.results.append({
            "time": timestamp,
            "level": level,
            "message": message
        })
    
    def _generate_sign(self, path: str, timestamp: str) -> str:
        """生成请求签名"""
        try:
            decoded_secret = base64.b64decode(self.account.app_secret).decode('utf-8', errors='ignore')
        except:
            decoded_secret = self.account.app_secret
        
        sign_str = (
            f"appSecret={decoded_secret}"
            f"&channel=android_app"
            f"&timestamp={timestamp}"
            f"&token={self.account.token}"
            f"&version={self.account.version}"
            f"&{path}"
        )
        return hashlib.sha256(sign_str.encode('utf-8')).hexdigest()
    
    def _build_headers(self, path: str) -> Dict[str, str]:
        """构建请求头"""
        timestamp = str(int(time.time() * 1000))
        sign = self._generate_sign(path, timestamp)
        
        return {
            "Authorization": self.account.token,
            "version": self.account.version,
            "channel": "android_app",
            "phoneBrand": self.account.phone_brand,
            "deviceId": self.account.device_id,
            "timestamp": timestamp,
            "sign": sign,
        }
    
    def _post(self, path: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """发送POST请求"""
        url = f"{self.base_url}{path}"
        headers = self._build_headers(path)
        
        form_data = data or {}
        if self.account.token:
            form_data["token"] = self.account.token
        
        try:
            response = self.session.post(url, headers=headers, data=form_data, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            self.log(f"请求超时: {path}", "ERROR")
            return {"code": -1, "msg": "请求超时"}
        except requests.exceptions.RequestException as e:
            self.log(f"请求失败 [{path}]: {e}", "ERROR")
            return {"code": -1, "msg": str(e)}
        except json.JSONDecodeError:
            self.log(f"响应解析失败: {path}", "ERROR")
            return {"code": -1, "msg": "响应格式错误"}
    
    def check_sign_status(self) -> bool:
        """检查今日是否已签到"""
        self.log("🔍 检查签到状态...")
        result = self._post("signIn/isSign")
        
        if result.get("code") == 200:
            is_signed = result.get("data", False)
            if is_signed:
                self.log("✅ 今日已签到", "NOTICE")
            else:
                self.log("⏳ 今日未签到")
            return is_signed
        else:
            self.log(f"❌ 查询失败: {result.get('msg', '未知错误')}", "ERROR")
            return False
    
    def do_sign_in(self) -> bool:
        """执行签到"""
        self.log("📝 执行签到...")
        result = self._post("signIn/today")
        
        if result.get("code") == 200:
            data = result.get("data", {})
            integral = data.get('integral', 'N/A')
            con_day = data.get('conDay', 'N/A')
            self.log(f"✅ 签到成功! 获得积分: {integral}, 连续签到: {con_day} 天", "NOTICE")
            return True
        else:
            msg = result.get('msg', '未知错误')
            self.log(f"❌ 签到失败: {msg}", "ERROR")
            return False
    
    def check_ad_status(self) -> bool:
        """检查广告状态"""
        self.log("📺 检查广告状态...")
        result = self._post("ad/status")
        
        if result.get("code") == 200:
            can_watch = result.get("data", False)
            if can_watch:
                self.log("✅ 有可观看广告")
            else:
                self.log("⏸️ 暂无可观看广告")
            return can_watch
        else:
            self.log(f"❌ 查询广告状态失败: {result.get('msg', '未知错误')}", "WARNING")
            return False
    
    def report_ad_finish(self) -> bool:
        """上报广告完成"""
        self.log("✅ 上报广告完成...")
        result = self._post("ad/media/finish")
        
        if result.get("code") == 200:
            self.log("✅ 广告完成上报成功")
            return True
        else:
            self.log(f"❌ 广告上报失败: {result.get('msg', '未知错误')}", "WARNING")
            return False
    
    def get_task_reward(self) -> bool:
        """领取任务奖励"""
        self.log("🎁 领取任务奖励...")
        result = self._post("task/getReward")
        
        if result.get("code") == 200:
            rewards = result.get("data", [])
            self.log(f"✅ 领取成功! 获得 {len(rewards)} 个奖励", "NOTICE")
            for reward in rewards:
                name = reward.get('name', 'N/A')
                value = reward.get('value', 'N/A')
                self.log(f"   - {name}: {value}")
            return True
        else:
            self.log(f"❌ 领取奖励失败: {result.get('msg', '未知错误')}", "WARNING")
            return False
    
    def get_user_info(self) -> bool:
        """获取用户信息"""
        self.log("👤 获取用户信息...")
        result = self._post("user/info")
        
        if result.get("code") == 200:
            data = result.get("data", {})
            nickname = data.get('nickname', 'N/A')
            integral = data.get('integral', 'N/A')
            balance = data.get('balance', 'N/A')
            self.log(f"   昵称: {nickname}")
            self.log(f"   积分: {integral}")
            self.log(f"   余额: {balance}")
            return True
        else:
            self.log(f"❌ 获取用户信息失败: {result.get('msg', '未知错误')}", "WARNING")
            return False
    
    def run(self) -> bool:
        """执行完整签到流程"""
        self.log(f"\n{'='*60}")
        self.log(f"🚀 开始处理账号: {self.account.name}")
        self.log(f"{'='*60}\n")
        
        # 1. 检查签到状态
        if self.check_sign_status():
            self.log("⚠️ 今日已签到，跳过", "NOTICE")
            return True
        
        # 2. 执行签到
        if not self.do_sign_in():
            self.log("❌ 签到失败，终止流程", "ERROR")
            return False
        
        # 3. 检查并观看广告
        self.log(f"\n{'-'*60}")
        if self.check_ad_status():
            self.log("⏳ 模拟观看广告 (5秒)...")
            time.sleep(5)
            
            if self.report_ad_finish():
                time.sleep(1)
                self.get_task_reward()
        
        # 4. 获取用户信息
        self.log(f"\n{'-'*60}")
        self.get_user_info()
        
        self.log(f"\n{'='*60}")
        self.log("✅ 签到流程完成", "NOTICE")
        self.log(f"{'='*60}\n")
        
        return True


def load_accounts_from_env() -> List[Account]:
    """从环境变量加载账号配置"""
    accounts = []
    
    # 方法1: 从 ACCOUNTS_CONFIG 环境变量（JSON格式）
    accounts_json = os.environ.get('ACCOUNTS_CONFIG', '')
    if accounts_json:
        try:
            data = json.loads(accounts_json)
            if isinstance(data, dict) and 'accounts' in data:
                for acc in data['accounts']:
                    if acc.get('enabled', True):
                        accounts.append(Account(
                            name=acc.get('name', f"账号{len(accounts)+1}"),
                            token=acc['token'],
                            device_id=acc.get('device_id', ''),
                            app_secret=acc.get('app_secret', Account.app_secret),
                            version=acc.get('version', '1.144.0'),
                            phone_brand=acc.get('phone_brand', 'Xiaomi'),
                            enabled=True
                        ))
        except json.JSONDecodeError as e:
            print(f"::error::解析 ACCOUNTS_CONFIG 失败: {e}")
    
    # 方法2: 从单独的环境变量（单账号）
    if not accounts:
        token = os.environ.get('QIEKJ_TOKEN', '')
        if token:
            accounts.append(Account(
                name=os.environ.get('QIEKJ_NAME', '默认账号'),
                token=token,
                device_id=os.environ.get('QIEKJ_DEVICE_ID', ''),
                version=os.environ.get('QIEKJ_VERSION', '1.144.0'),
                phone_brand=os.environ.get('QIEKJ_PHONE_BRAND', 'Xiaomi'),
            ))
    
    return accounts


def send_notification(results: List[Dict], success_count: int, total_count: int):
    """发送通知"""
    webhook_url = os.environ.get('WEBHOOK_URL', '')
    if not webhook_url:
        return
    
    title = f"切客纪签到报告 ({success_count}/{total_count})"
    
    content_lines = ["## 签到结果\n"]
    for r in results:
        status = "✅" if "成功" in r.get('message', '') or r.get('level') == 'NOTICE' else "❌"
        content_lines.append(f"{status} {r.get('message', '')}")
    
    content = "\n".join(content_lines)
    
    # 支持多种 Webhook 格式
    payload = {
        "title": title,
        "content": content,
        "text": content,
        "message": content,
    }
    
    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        if response.status_code == 200:
            print("::notice::通知发送成功")
        else:
            print(f"::warning::通知发送失败: HTTP {response.status_code}")
    except Exception as e:
        print(f"::warning::通知发送异常: {e}")


def main():
    """主函数"""
    print("="*60)
    print("🚀 切客纪 GitHub Actions 自动签到")
    print(f"⏰ 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # 加载账号
    accounts = load_accounts_from_env()
    
    if not accounts:
        print("::error::未配置任何账号")
        print("\n请设置以下环境变量之一：")
        print("  - ACCOUNTS_CONFIG: JSON格式的多账号配置")
        print("  - QIEKJ_TOKEN: 单个账号的Token")
        sys.exit(1)
    
    print(f"::notice::共加载 {len(accounts)} 个账号")
    
    # 执行签到
    all_results = []
    success_count = 0
    
    for idx, account in enumerate(accounts, 1):
        print(f"\n::group::账号 {idx}/{len(accounts)}: {account.name}")
        
        try:
            signer = GitHubAutoSign(account)
            if signer.run():
                success_count += 1
            all_results.extend(signer.results)
        except Exception as e:
            print(f"::error::账号 {account.name} 处理异常: {e}")
            all_results.append({
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "level": "ERROR",
                "message": f"账号 {account.name} 异常: {e}"
            })
        
        print("::endgroup::")
        
        # 账号间延迟
        if idx < len(accounts):
            delay = 10
            print(f"⏳ 等待 {delay} 秒后处理下一个账号...")
            time.sleep(delay)
    
    # 发送通知
    send_notification(all_results, success_count, len(accounts))
    
    # 输出统计
    print("\n" + "="*60)
    print("📊 签到统计")
    print("="*60)
    print(f"总账号数: {len(accounts)}")
    print(f"成功: {success_count}")
    print(f"失败: {len(accounts) - success_count}")
    print(f"成功率: {success_count/len(accounts)*100:.1f}%")
    print("="*60)
    
    # 设置退出码
    sys.exit(0 if success_count == len(accounts) else 1)


if __name__ == "__main__":
    main()
