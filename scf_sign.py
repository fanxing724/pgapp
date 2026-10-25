# -*- coding: utf-8 -*-
"""
切客纪自动签到 - 腾讯云函数 SCF 版
SCF Python3 运行时内置 requests，无需打包依赖

部署入口: scf_sign.main_handler
"""
import hashlib
import base64
import json
import time
import random
from datetime import datetime, timezone, timedelta

import requests

# ==================== 配置（部署时直接改这里，或用环境变量）====================
import os

TOKEN = os.environ.get("QIEKJ_TOKEN", "").strip()  # 推荐用环境变量配置
VERSION = "1.144.0"
BASE_URL = "https://userapi.qiekj.com/"
APP_SECRET_B64 = "bkZVOXBiRzhZUW9BZTFrRmgrRTdleXJkbFNMZ2x3RUplQTB3d0hCMWo1bz0="


def log(msg, level="INFO"):
    print(f"[{level}] {msg}", flush=True)


class QieKjSigner:
    def __init__(self, token):
        self.token = token
        self.app_secret = base64.b64decode(APP_SECRET_B64).decode()
        self.session = requests.Session()

    def _build_headers(self, path):
        timestamp = str(int(time.time() * 1000))
        sign_str = (f"appSecret={self.app_secret}&channel=android_app&timestamp={timestamp}"
                    f"&token={self.token}&version={VERSION}&/{path}")
        sign = hashlib.sha256(sign_str.encode()).hexdigest()
        return {
            "User-Agent": f"QEUser/{VERSION} (com.qiekj.user; build:294; Android 13; "
                          f"userChannel:android_app; version:{VERSION}) OkHttp/4.12.0",
            "Authorization": self.token,
            "token": self.token,
            "Version": VERSION,
            "channel": "android_app",
            "phoneBrand": "Xiaomi",
            "deviceId": "",
            "timestamp": timestamp,
            "sign": sign,
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        }

    def _post(self, path, data=None):
        try:
            resp = self.session.post(
                f"{BASE_URL}{path}", headers=self._build_headers(path),
                data={**(data or {}), "token": self.token}, timeout=30)
            return resp.json()
        except Exception as e:
            log(f"❌ 请求失败 [{path}]: {e}", "ERROR")
            return {"code": -999, "msg": str(e)}

    def _get(self, path, params=None):
        try:
            resp = self.session.get(
                f"{BASE_URL}{path}", headers=self._build_headers(path),
                params={**(params or {}), "token": self.token}, timeout=30)
            return resp.json()
        except Exception as e:
            log(f"❌ 请求失败 [{path}]: {e}", "ERROR")
            return {"code": -999, "msg": str(e)}

    def check_sign_status(self):
        """检查今日是否已签到"""
        log("🔍 检查签到状态...")
        result = self._post("signin/todaySignIn")
        if result.get("code") == 0:
            data = result.get("data")
            is_signed = data if isinstance(data, bool) else (data or {}).get("isSignIn", False)
            log("✅ 今日已签到" if is_signed else "⏳ 今日未签到")
            return bool(is_signed)
        log(f"❌ 查询失败: {result.get('msg', '未知错误')}", "ERROR")
        return False

    def do_sign_in(self):
        """执行签到"""
        log("📝 执行签到...")
        result = self._post("signin/doUserSignIn")
        if result.get("code") == 0:
            data = result.get("data") or {}
            if data.get("signInResult"):
                log(f"✅ 签到成功! +{data.get('totalIntegral', '?')} 积分, "
                    f"累计 {data.get('totalDays', '?')} 天, 明日可得 {data.get('nextIntegral', '?')}")
                return True
            log(f"⚠️ {data.get('failReason') or '签到失败'}", "WARNING")
            return False
        log(f"❌ 签到失败: {result.get('msg', '未知错误')}", "ERROR")
        return False

    def claim_timed_benefit(self):
        """
        定时福利（积分页"点击领积分"）
        applyStatus: 1=倒计时中 2=可领取 3/4=明日再领
        注意: 服务器风控可能拒绝纯API领取，失败不影响主流程
        """
        log("🎁 检查定时福利...")
        result = self._get("timedBenefit/queryTimedBenefit")
        if result.get("code") != 0:
            log(f"⚠️ 查询定时福利失败: {result.get('msg', '未知错误')}", "WARNING")
            return False

        data = result.get("data") or {}
        status, nxt, surplus, freq = (data.get("applyStatus"), data.get("nextRewardNum", 0),
                                      data.get("surplusTime"), data.get("applyFreq", 0))
        if status == 1:
            log(f"⏳ 定时福利倒计时中，{surplus}秒后可领 +{nxt} 积分")
            return False
        if status in (3, 4):
            log(f"ℹ️ 今日定时福利已领完（{freq}次），明日再领")
            return False
        if status != 2:
            log(f"ℹ️ 定时福利状态未知(applyStatus={status})")
            return False

        log(f"🎯 定时福利可领取 +{nxt} 积分，尝试领取...")
        time.sleep(1)
        captcha = self._post("integralCaptcha/isCaptcha")
        if captcha.get("code") == 0 and captcha.get("data") is True:
            log("⚠️ 触发风控验证码，无法自动领取", "WARNING")
            return False

        claim = self._get("timedBenefit/applyRewardForTimeBenefit")
        if claim.get("code") == 0:
            log(f"✅ 定时福利领取成功! +{nxt} 积分")
            return True
        log(f"⚠️ 定时福利领取被拒: {claim.get('msg', '未知')}（服务器风控，需真实APP环境）", "WARNING")
        return False

    def query_video_task(self):
        """查询"看视频赚积分"任务状态（仅报告，需APP内真实观看广告）"""
        log("📺 查询视频任务状态...")
        result = self._post("task/queryPushTask")
        if result.get("code") == 0:
            data = result.get("data") or {}
            done, limit = data.get("completedFreq", 0), data.get("dailyTaskLimit", 0)
            points = (data.get("extendMap") or {}).get("awardPoint") or []
            per = points[0] if points else data.get("awardNumber", "?")
            if done < limit:
                log(f"ℹ️ 「{data.get('title', '看视频')}」今日 {done}/{limit} 次，"
                    f"每次 +{per} 积分（需APP内看激励视频）")
            else:
                log(f"✅ 「{data.get('title', '看视频')}」今日已完成 {done}/{limit} 次")
        else:
            log(f"⚠️ 查询视频任务失败: {result.get('msg', '未知错误')}", "WARNING")

    def report_integral_stats(self):
        """报告今日积分统计"""
        log("📊 查询今日积分统计...")
        result = self._post("integralRecord/integralDailStatistics")
        if result.get("code") == 0:
            data = result.get("data") or {}
            log(f"📊 今日已赚: +{data.get('dailyEarnIntegral', 0)} 积分"
                f"（击败 {data.get('ratio', 'N/A')} 用户）")
        else:
            log(f"⚠️ 查询积分统计失败: {result.get('msg', '未知错误')}", "WARNING")

    def run(self):
        log("=" * 50)
        log("🚀 切客纪自动签到开始")
        if not self.check_sign_status():
            if not self.do_sign_in():
                log("❌ 签到失败（继续尝试福利/任务流程）", "ERROR")
        else:
            log("⚠️ 今日已签到，跳过签到步骤")
        log("-" * 50)
        self.claim_timed_benefit()
        log("-" * 50)
        self.query_video_task()
        log("-" * 50)
        self.report_integral_stats()
        log("✅ 签到流程完成")
        return True


def main_handler(event, context):
    """SCF 入口函数：每天 12:00 定时触发（随机延迟 0-10 分钟模拟真人）"""
    beijing = datetime.now(timezone(timedelta(hours=8)))
    log(f"📅 触发时间: {beijing.strftime('%Y-%m-%d %H:%M:%S')} (北京时间)")

    # 随机延迟 0-600 秒，模拟真人操作（SCF 超时时间需 ≥ 900 秒）
    # 手动测试（控制台"测试"按钮）不延迟，直接执行
    is_timer = "Time" in json.dumps(event) or event.get("Type") == "Timer"
    if is_timer:
        delay = random.randint(0, 600)
        log(f"⏳ 随机延迟 {delay} 秒...")
        time.sleep(delay)
    else:
        log("🔧 手动测试触发，跳过延迟直接执行")

    token = TOKEN
    if not token:
        msg = "❌ 未配置 QIEKJ_TOKEN 环境变量"
        log(msg, "ERROR")
        return msg

    try:
        QieKjSigner(token).run()
        return "✅ 签到流程完成"
    except Exception as e:
        log(f"❌ 执行异常: {e}", "ERROR")
        return f"❌ 执行异常: {e}"
