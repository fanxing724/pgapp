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
    build_code: str = "294"
    phone_brand: str = "Xiaomi"
    enabled: bool = True


class GitHubAutoSign:
    """GitHub Actions 自动签到"""
    
    def __init__(self, account: Account):
        self.account = account
        self.base_url = "https://userapi.qiekj.com/"
        self.session = requests.Session()
        # User-Agent 必须与官方 APP 格式一致，服务器从中解析版本号
        ua = (
            f"QEUser/{account.version} (com.qiekj.user; build:{account.build_code}; "
            f"Android 13; userChannel:android_app; version:{account.version}) OkHttp/4.12.0"
        )
        self.session.headers.update({
            "User-Agent": ua,
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
            f"&/{path}"
        )
        return hashlib.sha256(sign_str.encode('utf-8')).hexdigest()
    
    def _build_headers(self, path: str) -> Dict[str, str]:
        """构建请求头（与官方 APP HeadInterceptor 一致）"""
        timestamp = str(int(time.time() * 1000))
        sign = self._generate_sign(path, timestamp)
        
        return {
            "Authorization": self.account.token,
            "token": self.account.token,
            "Version": self.account.version,
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
        result = self._post("signin/todaySignIn")
        
        if result.get("code") == 0:  # 成功码是0，不是200
            data = result.get("data") or {}
            # 真实响应格式: {"isSignIn": false}
            if isinstance(data, bool):
                is_signed = data
            else:
                is_signed = data.get('isSignIn', False) if isinstance(data, dict) else False
            
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
        result = self._post("signin/doUserSignIn")
        
        if result.get("code") == 0:  # 成功码是0，不是200
            data = result.get("data") or {}
            # 真实响应: {"totalDays":2,"totalIntegral":3,"nextIntegral":4,"signInResult":true,"failReason":null}
            if data.get('signInResult', False):
                integral = data.get('totalIntegral', 'N/A')
                total_days = data.get('totalDays', 'N/A')
                next_integral = data.get('nextIntegral', 'N/A')
                self.log(f"✅ 签到成功! 本次积分: +{integral}, 累计: {total_days} 天, 明日可得: {next_integral}", "NOTICE")
                return True
            else:
                fail_reason = data.get('failReason') or '未知原因'
                self.log(f"⚠️ 签到未生效: {fail_reason}", "WARNING")
                return False
        else:
            msg = result.get('msg', '未知错误')
            self.log(f"❌ 签到失败: {msg}", "ERROR")
            return False
    
    def _get(self, path: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """发送 GET 请求（与官方 APP 一致：token 放 query 参数）"""
        headers = self._build_headers(path)
        url = f"{self.base_url}{path}"
        query = dict(params or {})
        query["token"] = self.account.token
        try:
            resp = self.session.get(url, headers=headers, params=query, timeout=30)
            return resp.json()
        except Exception as e:
            self.log(f"❌ 请求异常: {e}", "ERROR")
            return {"code": -999, "msg": str(e)}

    def claim_timed_benefit(self) -> bool:
        """
        定时福利（积分页"点击领积分"）
        真实流程（来自 IntegralFragment / SignInViewModel 逆向）:
          1. GET timedBenefit/queryTimedBenefit 查询状态
             applyStatus: 1=倒计时中(surplusTime秒后可领) 2=可领取 3/4=明日再领
          2. applyStatus==2 时 POST integralCaptcha/isCaptcha 检查风控
          3. 无需验证码则 GET timedBenefit/applyRewardForTimeBenefit 领取
        注意: 该接口有服务器侧风控/时段限制，纯 API 领取可能被拒（"福利奖励领取失败"），
              失败不影响签到主流程，仅记录日志。
        """
        self.log("🎁 检查定时福利...")
        result = self._get("timedBenefit/queryTimedBenefit")

        if result.get("code") != 0:  # 成功码是0，不是200
            self.log(f"⚠️ 查询定时福利失败: {result.get('msg', '未知错误')}", "WARNING")
            return False

        data = result.get("data") or {}
        status = data.get("applyStatus")
        next_reward = data.get("nextRewardNum", 0)
        surplus = data.get("surplusTime")
        freq = data.get("applyFreq", 0)

        if status == 1:
            self.log(f"⏳ 定时福利倒计时中，{surplus}秒后可领 +{next_reward} 积分")
            return False
        elif status in (3, 4):
            self.log(f"ℹ️ 今日定时福利已领完（已领{freq}次），明日再领")
            return False
        elif status != 2:
            self.log(f"ℹ️ 定时福利状态未知(applyStatus={status})")
            return False

        # applyStatus == 2: 可领取
        self.log(f"🎯 定时福利可领取 +{next_reward} 积分，尝试领取...")
        time.sleep(1)  # 模拟真实操作间隔

        # 风控检查（与 APP 一致）
        captcha = self._post("integralCaptcha/isCaptcha")
        if captcha.get("code") == 0 and captcha.get("data") is True:
            self.log("⚠️ 触发风控验证码，无法自动领取", "WARNING")
            return False

        claim = self._get("timedBenefit/applyRewardForTimeBenefit")
        if claim.get("code") == 0:  # 成功码是0，不是200
            self.log(f"✅ 定时福利领取成功! +{next_reward} 积分", "NOTICE")
            return True
        else:
            # 服务器风控拒绝（纯 API 常见），仅记录不报错
            self.log(f"⚠️ 定时福利领取被拒: {claim.get('msg', '未知')}（服务器风控，需真实APP环境）", "WARNING")
            return False

    def query_video_task(self) -> None:
        """
        查询"看视频赚积分"任务状态（仅报告，无法纯API完成）
        实测验证: task/getTaskReward 虽返回成功但服务器有 TopOn 广告 SDK
        服务端校验，未真实观看不发奖励（completedFreq 不变、积分不到账）。
        """
        self.log("📺 查询视频任务状态...")
        result = self._post("task/queryPushTask")

        if result.get("code") == 0:  # 成功码是0，不是200
            data = result.get("data") or {}
            title = data.get("title", "看视频赚积分")
            done = data.get("completedFreq", 0)
            limit = data.get("dailyTaskLimit", 0)
            points = (data.get("extendMap") or {}).get("awardPoint") or []
            per = points[0] if points else data.get("awardNumber", "?")
            if done < limit:
                self.log(f"ℹ️ 「{title}」今日 {done}/{limit} 次，每次 +{per} 积分（需在APP内观看激励视频，纯API无法完成）")
            else:
                self.log(f"✅ 「{title}」今日已完成 {done}/{limit} 次")
        else:
            self.log(f"⚠️ 查询视频任务失败: {result.get('msg', '未知错误')}", "WARNING")

    def report_integral_stats(self) -> None:
        """报告今日积分统计"""
        self.log("📊 查询今日积分统计...")
        result = self._post("integralRecord/integralDailStatistics")

        if result.get("code") == 0:  # 成功码是0，不是200
            data = result.get("data") or {}
            earned = data.get("dailyEarnIntegral", 0)
            ratio = data.get("ratio", "N/A")
            self.log(f"   今日已赚积分: +{earned}（击败 {ratio} 用户）", "NOTICE")
        else:
            self.log(f"⚠️ 查询积分统计失败: {result.get('msg', '未知错误')}", "WARNING")

    def get_user_info(self) -> bool:
        """获取用户信息"""
        self.log("👤 获取用户信息...")
        result = self._post("user/info")

        if result.get("code") == 0:  # 成功码是0，不是200
            data = result.get("data") or {}
            # 真实响应字段: userName / balance / phone（无 integral 字段）
            nickname = data.get('userName', 'N/A')
            balance = data.get('balance', 'N/A')
            phone = data.get('phone', 'N/A')
            self.log(f"   昵称: {nickname}")
            self.log(f"   手机号: {phone}")
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
        
        # 1. 检查签到状态：已签到只跳过签到步骤，其余流程照常执行
        if self.check_sign_status():
            self.log("⚠️ 今日已签到，跳过签到步骤", "NOTICE")
        else:
            # 2. 执行签到
            if not self.do_sign_in():
                self.log("❌ 签到失败（继续尝试福利/任务流程）", "ERROR")

        # 3. 定时福利（可领时自动尝试领取；被风控则记录日志）
        self.log(f"\n{'-'*60}")
        self.claim_timed_benefit()

        # 4. 视频任务状态（仅报告，需真实观看广告）
        self.log(f"\n{'-'*60}")
        self.query_video_task()

        # 5. 今日积分统计 + 用户信息
        self.log(f"\n{'-'*60}")
        self.report_integral_stats()
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
