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
        self.session.headers.update({
            "User-Agent": config.user_agent,
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        })
    
    def _generate_sign(self, path: str, timestamp: str) -> str:
        """
        生成请求签名
        sign = SHA-256("appSecret={secret}&channel=android_app&timestamp={ts}&token={token}&version={version}&{path}")
        
        注意：appSecret 需要先进行 Base64 解码
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
            f"&{path}"
        )
        return hashlib.sha256(sign_str.encode('utf-8')).hexdigest()
    
    def _build_headers(self, path: str) -> Dict[str, str]:
        """构建请求头"""
        timestamp = str(int(time.time() * 1000))
        sign = self._generate_sign(path, timestamp)
        
        headers = {
            "Authorization": self.config.token,
            "version": self.config.version,
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
        
        if result.get("code") == 200:
            data = result.get("data", False)
            # data 可能是布尔值或包含签到信息的对象
            if isinstance(data, bool):
                is_signed = data
            else:
                is_signed = data.get('signed', False) if isinstance(data, dict) else False
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
        
        if result.get("code") == 200:
            data = result.get("data", {})
            print(f"   ✅ 签到成功!")
            print(f"   📊 获得积分: {data.get('integral', 'N/A')}")
            print(f"   📅 连续签到: {data.get('conDay', 'N/A')} 天")
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
        
        if result.get("code") == 200:
            data = result.get("data", [])
            print(f"   📋 可用活动数: {len(data)}")
            for act in data:
                print(f"      - {act.get('name', 'N/A')}: {act.get('desc', '')}")
            return result
        else:
            print(f"   ❌ 获取失败: {result.get('msg', '未知错误')}")
            return result
    
    def check_ad_status(self) -> bool:
        """
        检查广告状态
        接口: alipay/tap/adStatus
        """
        print("📺 检查广告状态...")
        result = self._post("alipay/tap/adStatus")
        
        if result.get("code") == 200:
            can_watch = result.get("data", False)
            status = "✅ 可观看" if can_watch else "⏸️ 暂无广告"
            print(f"   状态: {status}")
            return can_watch
        else:
            print(f"   ❌ 查询失败: {result.get('msg', '未知错误')}")
            return False
    
    def report_ad_finish(self) -> bool:
        """
        上报广告完成
        接口: alipay/admedia/finishFlag
        """
        print("✅ 上报广告完成...")
        result = self._post("alipay/admedia/finishFlag")
        
        if result.get("code") == 200:
            print("   ✅ 广告完成上报成功")
            return True
        else:
            print(f"   ❌ 上报失败: {result.get('msg', '未知错误')}")
            return False
    
    def get_task_reward(self, task_id: str = "") -> Dict[str, Any]:
        """
        领取任务奖励
        接口: task/getTaskReward
        """
        print("🎁 领取任务奖励...")
        data = {}
        if task_id:
            data["taskId"] = task_id
        
        result = self._post("task/getTaskReward", data)
        
        if result.get("code") == 200:
            rewards = result.get("data", [])
            print(f"   ✅ 领取成功! 获得 {len(rewards)} 个奖励")
            for reward in rewards:
                print(f"      - {reward.get('name', 'N/A')}: {reward.get('value', 'N/A')}")
            return result
        else:
            print(f"   ❌ 领取失败: {result.get('msg', '未知错误')}")
            return result
    
    def apply_task(self, task_id: str) -> bool:
        """
        申请完成任务
        接口: markActivity/doApplyTask
        """
        print(f"📋 申请任务 {task_id}...")
        result = self._post("markActivity/doApplyTask", {"taskId": task_id})
        
        if result.get("code") == 200:
            print("   ✅ 任务申请成功")
            return True
        else:
            print(f"   ❌ 申请失败: {result.get('msg', '未知错误')}")
            return False
    
    def mark_task_done(self, task_id: str) -> bool:
        """
        标记任务完成
        接口: markActivity/doMarkTask
        """
        print(f"✅ 标记任务 {task_id} 完成...")
        result = self._post("markActivity/doMarkTask", {"taskId": task_id})
        
        if result.get("code") == 200:
            print("   ✅ 任务标记成功")
            return True
        else:
            print(f"   ❌ 标记失败: {result.get('msg', '未知错误')}")
            return False
    
    def auto_sign_with_ad(self):
        """
        自动签到完整流程（含广告）
        """
        print("=" * 60)
        print("🚀 切客纪自动签到开始")
        print("=" * 60)
        
        # 1. 检查是否已签到
        if self.check_sign_status():
            print("\n⚠️  今日已签到，无需重复签到")
            return
        
        # 2. 执行签到
        sign_result = self.do_sign_in()
        if sign_result.get("code") != 200:
            print("\n❌ 签到失败，流程结束")
            return
        
        # 3. 检查是否有广告可看
        print("\n" + "-" * 60)
        if self.check_ad_status():
            # 4. 模拟观看广告（实际使用时需要真实观看或模拟）
            print("\n⏳ 模拟观看广告 (3秒)...")
            time.sleep(3)
            
            # 5. 上报广告完成
            if self.report_ad_finish():
                # 6. 领取广告奖励
                time.sleep(1)
                self.get_task_reward()
        else:
            print("\nℹ️  暂无可观看的广告")
        
        print("\n" + "=" * 60)
        print("✅ 自动签到流程完成")
        print("=" * 60)
    
    def get_user_info(self) -> Dict[str, Any]:
        """获取用户信息"""
        print("👤 获取用户信息...")
        result = self._post("user/info")
        
        if result.get("code") == 200:
            data = result.get("data", {})
            print(f"   昵称: {data.get('nickname', 'N/A')}")
            print(f"   积分: {data.get('integral', 'N/A')}")
            print(f"   余额: {data.get('balance', 'N/A')}")
            return result
        else:
            print(f"   ❌ 获取失败: {result.get('msg', '未知错误')}")
            return result


def main():
    """主函数"""
    # ===== 配置区域 =====
    config = Config(
        # ⚠️ 请填入你的Token（从APP抓包或SharedPreferences中获取）
        # 获取方法：
        # 1. 使用抓包工具（如HttpCanary、Charles）抓取任意API请求
        # 2. 查看请求头中的 Authorization 字段值
        # 3. 或者从手机 /data/data/com.qiekj.user/shared_prefs/ 中查找
        token="YOUR_TOKEN_HERE",
        
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
