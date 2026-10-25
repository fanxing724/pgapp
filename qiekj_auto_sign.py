#!/usr/bin/env python3
"""
切客纪自动签到脚本
功能：自动签到 + 过广告领取奖励
"""

import hashlib
import time
import base64
import requests
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class Config:
    """配置类"""
    # 用户Token（从APP中获取）
    token: str = ""
    
    # API基础URL
    base_url: str = "https://userapi.qiekj.com/"
    
    # 应用版本（需要与官方版本一致或接近）
    version: str = "1.144.0"
    
    # 应用构建号（versionCode）
    build_code: str = "294"
    
    # 渠道
    channel: str = "android_app"
    
    # 设备信息
    device_id: str = ""  # OAID
    phone_brand: str = "Xiaomi"
    
    # appSecret（需要从APK中提取或抓包获取）
    app_secret: str = ""
    
    # User-Agent
    user_agent: str = "okhttp/4.12.0"


class QieKjAutoSign:
    """切客纪自动签到类"""
    
    def __init__(self, config: Config):
        self.config = config
        self.session = requests.Session()
        # User-Agent 必须与官方 APP 格式一致，服务器从中解析版本号
        # 格式: QEUser/{versionName} ({package}; build:{versionCode}; Android {osVer}; userChannel:android_app; version:{versionName}) OkHttp/4.12.0
        ua = (
            f"QEUser/{config.version} (com.qiekj.user; build:{config.build_code}; "
            f"Android 13; userChannel:android_app; version:{config.version}) OkHttp/4.12.0"
        )
        self.session.headers.update({
            "User-Agent": ua,
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        })
    
    def _generate_sign(self, path: str, timestamp: str) -> str:
        """
        生成请求签名（与官方 APP HeadInterceptor 一致）
        sign = SHA-256("appSecret={secret}&channel=android_app&timestamp={ts}&token={token}&version={version}&/{path}")
        
        注意：
        - appSecret 需要先进行 Base64 解码
        - 路径带前导斜杠（OkHttp encodedPath() 格式）
        """
        # 解码 Base64 编码的 secret
        try:
            decoded_secret = base64.b64decode(self.config.app_secret).decode('utf-8', errors='ignore')
        except:
            decoded_secret = self.config.app_secret
        
        sign_str = (
            f"appSecret={decoded_secret}"
            f"&channel={self.config.channel}"
            f"&timestamp={timestamp}"
            f"&token={self.config.token}"
            f"&version={self.config.version}"
            f"&/{path}"
        )
        return hashlib.sha256(sign_str.encode('utf-8')).hexdigest()
    
    def _build_headers(self, path: str) -> Dict[str, str]:
        """构建请求头（与官方 APP HeadInterceptor 一致）"""
        timestamp = str(int(time.time() * 1000))
        sign = self._generate_sign(path, timestamp)
        
        headers = {
            "Authorization": self.config.token,
            "token": self.config.token,
            "Version": self.config.version,
            "channel": self.config.channel,
            "phoneBrand": self.config.phone_brand,
            "deviceId": self.config.device_id,
            "timestamp": timestamp,
            "sign": sign,
        }
        return headers
    
    def _post(self, path: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """发送POST请求"""
        url = f"{self.config.base_url}{path}"
        headers = self._build_headers(path)
        
        # 构建表单数据，自动添加token
        form_data = data or {}
        if self.config.token:
            form_data["token"] = self.config.token
        
        try:
            response = self.session.post(url, headers=headers, data=form_data, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ 请求失败 [{path}]: {e}")
            return {"code": -1, "msg": str(e)}
    
    def check_sign_status(self) -> bool:
        """
        检查今日是否已签到
        接口: signin/todaySignIn
        """
        print("🔍 检查签到状态...")
        result = self._post("signin/todaySignIn")
        
        if result.get("code") == 0:  # 成功码是0，不是200
            data = result.get("data") or {}
            # 真实响应格式: {"isSignIn": false}
            if isinstance(data, bool):
                is_signed = data
            else:
                is_signed = data.get('isSignIn', False) if isinstance(data, dict) else False
            status = "✅ 已签到" if is_signed else "⏳ 未签到"
            print(f"   状态: {status}")
            return is_signed
        else:
            print(f"   ❌ 查询失败: {result.get('msg', '未知错误')}")
            return False
    
    def do_sign_in(self) -> Dict[str, Any]:
        """
        执行签到
        接口: signin/doUserSignIn
        """
        print("📝 执行签到...")
        result = self._post("signin/doUserSignIn")
        
        if result.get("code") == 0:  # 成功码是0，不是200
            data = result.get("data") or {}
            # 真实响应: {"totalDays":2,"totalIntegral":3,"nextIntegral":4,"signInResult":true,"failReason":null}
            if data.get('signInResult', False):
                print(f"   ✅ 签到成功!")
                print(f"   📊 本次积分: +{data.get('totalIntegral', 'N/A')}, 明日可得: {data.get('nextIntegral', 'N/A')}")
                print(f"   📅 累计签到: {data.get('totalDays', 'N/A')} 天")
            else:
                print(f"   ⚠️ 签到未生效: {data.get('failReason') or '未知原因'}")
            return result
        else:
            print(f"   ❌ 签到失败: {result.get('msg', '未知错误')}")
            return result
    
    def get_sign_activity(self) -> Dict[str, Any]:
        """
        获取签到活动信息
        接口: signin/signInAcList
        """
        print("🎯 获取签到活动信息...")
        result = self._post("signin/signInAcList")
        
        if result.get("code") == 0:  # 成功码是0，不是200
            data = result.get("data") or {}
            # 真实格式: 单个活动对象，含 ruleSignInDTO.cycleCumulatives 积分规则
            rule = data.get('ruleSignInDTO') or {}
            cycle = rule.get('cycleCumulatives') or []
            if cycle:
                print(f"   📋 签到周期: {rule.get('cycle', len(cycle))} 天一轮")
                for item in cycle:
                    print(f"      - 第{item.get('day', '?')}天: +{item.get('amount', '?')} 积分")
            else:
                print(f"   📋 {data.get('info', '暂无活动详情')}")
            return result
        else:
            print(f"   ❌ 获取失败: {result.get('msg', '未知错误')}")
            return result
    
    def _get(self, path: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """发送GET请求（与官方 APP 一致：token 放 query 参数）"""
        url = f"{self.config.base_url}{path}"
        headers = self._build_headers(path)
        query = dict(params or {})
        query["token"] = self.config.token

        try:
            response = self.session.get(url, headers=headers, params=query, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ 请求失败 [{path}]: {e}")
            return {"code": -1, "msg": str(e)}

    def claim_timed_benefit(self) -> bool:
        """
        定时福利（积分页"点击领积分"）
        真实流程（逆向 IntegralFragment / SignInViewModel）:
          1. GET timedBenefit/queryTimedBenefit
             applyStatus: 1=倒计时中(surplusTime秒后可领) 2=可领取 3/4=明日再领
          2. applyStatus==2 → POST integralCaptcha/isCaptcha 风控检查
          3. 无验证码 → GET timedBenefit/applyRewardForTimeBenefit 领取
        注意: 该接口有服务器侧风控/时段限制，纯 API 领取可能被拒
             （"福利奖励领取失败"），失败仅记录日志不影响主流程。
        """
        print("🎁 检查定时福利...")
        result = self._get("timedBenefit/queryTimedBenefit")

        if result.get("code") != 0:  # 成功码是0，不是200
            print(f"   ⚠️ 查询失败: {result.get('msg', '未知错误')}")
            return False

        data = result.get("data") or {}
        status = data.get("applyStatus")
        next_reward = data.get("nextRewardNum", 0)
        surplus = data.get("surplusTime")
        freq = data.get("applyFreq", 0)

        if status == 1:
            print(f"   ⏳ 倒计时中，{surplus}秒后可领 +{next_reward} 积分")
            return False
        elif status in (3, 4):
            print(f"   ℹ️ 今日已领完（{freq}次），明日再领")
            return False
        elif status != 2:
            print(f"   ℹ️ 状态未知(applyStatus={status})")
            return False

        print(f"   🎯 可领取 +{next_reward} 积分，尝试领取...")
        time.sleep(1)

        captcha = self._post("integralCaptcha/isCaptcha")
        if captcha.get("code") == 0 and captcha.get("data") is True:
            print("   ⚠️ 触发风控验证码，无法自动领取")
            return False

        claim = self._get("timedBenefit/applyRewardForTimeBenefit")
        if claim.get("code") == 0:  # 成功码是0，不是200
            print(f"   ✅ 定时福利领取成功! +{next_reward} 积分")
            return True
        else:
            print(f"   ⚠️ 领取被拒: {claim.get('msg', '未知')}（服务器风控，需真实APP环境）")
            return False

    def query_video_task(self) -> None:
        """
        查询"看视频赚积分"任务状态（仅报告）
        实测: task/getTaskReward 纯API调用虽返回成功，但服务器有 TopOn 广告SDK
        服务端校验，未真实观看不发奖励（completedFreq 不变、积分不到账）。
        """
        print("📺 查询视频任务状态...")
        result = self._post("task/queryPushTask")

        if result.get("code") == 0:  # 成功码是0，不是200
            data = result.get("data") or {}
            title = data.get("title", "看视频赚积分")
            done = data.get("completedFreq", 0)
            limit = data.get("dailyTaskLimit", 0)
            points = (data.get("extendMap") or {}).get("awardPoint") or []
            per = points[0] if points else data.get("awardNumber", "?")
            if done < limit:
                print(f"   ℹ️ 「{title}」今日 {done}/{limit} 次，每次 +{per} 积分（需APP内看激励视频）")
            else:
                print(f"   ✅ 「{title}」今日已完成 {done}/{limit} 次")
        else:
            print(f"   ⚠️ 查询失败: {result.get('msg', '未知错误')}")

    def report_integral_stats(self) -> None:
        """报告今日积分统计"""
        print("📊 今日积分统计...")
        result = self._post("integralRecord/integralDailStatistics")

        if result.get("code") == 0:  # 成功码是0，不是200
            data = result.get("data") or {}
            print(f"   今日已赚: +{data.get('dailyEarnIntegral', 0)} 积分（击败 {data.get('ratio', 'N/A')} 用户）")
        else:
            print(f"   ⚠️ 查询失败: {result.get('msg', '未知错误')}")

    def auto_sign_with_ad(self):
        """
        自动签到完整流程（签到 + 定时福利 + 任务状态报告）
        """
        print("=" * 60)
        print("🚀 切客纪自动签到开始")
        print("=" * 60)

        # 1. 检查是否已签到：已签到只跳过签到步骤，其余流程照常执行
        if self.check_sign_status():
            print("\n⚠️  今日已签到，跳过签到步骤")
        else:
            # 2. 执行签到
            sign_result = self.do_sign_in()
            if sign_result.get("code") != 0:
                print("\n❌ 签到失败（继续尝试福利/任务流程）")

        # 3. 定时福利（可领时自动尝试）
        print("\n" + "-" * 60)
        self.claim_timed_benefit()

        # 4. 视频任务状态（仅报告，需真实观看）
        print("\n" + "-" * 60)
        self.query_video_task()

        # 5. 今日积分统计
        print("\n" + "-" * 60)
        self.report_integral_stats()

        print("\n" + "=" * 60)
        print("✅ 自动签到流程完成")
        print("=" * 60)
    
    def get_user_info(self) -> Dict[str, Any]:
        """获取用户信息"""
        print("👤 获取用户信息...")
        result = self._post("user/info")
        
        if result.get("code") == 0:  # 成功码是0，不是200
            data = result.get("data", {})
            # 真实响应字段: userName / balance / phone（无 integral 字段）
            print(f"   昵称: {data.get('userName', 'N/A')}")
            print(f"   手机号: {data.get('phone', 'N/A')}")
            print(f"   余额: {data.get('balance', 'N/A')}")
            return result
        else:
            print(f"   ❌ 获取失败: {result.get('msg', '未知错误')}")
            return result


def main():
    """主函数"""
    # ===== 配置区域 =====
    # Token 优先从环境变量 QIEKJ_TOKEN 读取，其次从 ~/.qiekj_tokens/ 目录读取
    import os, glob
    token = os.environ.get("QIEKJ_TOKEN", "").strip()
    if not token:
        token_files = sorted(glob.glob(os.path.expanduser("~/.qiekj_tokens/token_*.txt")),
                             key=os.path.getmtime, reverse=True)
        if token_files:
            with open(token_files[0]) as f:
                for line in f:
                    if line.startswith("Token:"):
                        token = line.split(":", 1)[1].strip()
                        break
    if not token:
        token = "YOUR_TOKEN_HERE"

    config = Config(
        token=token,
        
        # ✅ appSecret 已从APK中提取（Base64编码）
        # 原始值在 HeadInterceptor.<clinit> 中定义
        app_secret="bkZVOXBiRzhZUW9BZTFrRmgrRTdleXJkbFNMZ2x3RUplQTB3d0hCMWo1bz0=",
        
        # 设备ID（OAID），可以从APP中获取或使用随机值
        # 获取方法：抓包查看请求头中的 deviceId 字段
        device_id="your-device-id-here",
        
        # 其他配置保持默认即可
        version="1.144.0",
        phone_brand="Xiaomi",
    )
    # ====================
    
    # 创建签到实例
    signer = QieKjAutoSign(config)
    
    # 方式1: 仅签到
    # signer.do_sign_in()
    
    # 方式2: 签到 + 过广告
    signer.auto_sign_with_ad()
    
    # 方式3: 查看用户信息
    # signer.get_user_info()


if __name__ == "__main__":
    main()
