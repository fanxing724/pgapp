#!/usr/bin/env python3
"""
切客纪自动签到脚本（高级版）
支持多账号、配置文件、定时任务、消息推送
"""

import json
import sys
import time
import requests
from pathlib import Path
from typing import List, Dict

from qiekj_auto_sign import QieKjAutoSign, Config


class MultiAccountSign:
    """多账号签到管理器"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self.accounts = []
        self.global_config = {}
        self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        if not self.config_file.exists():
            print(f"❌ 配置文件不存在: {self.config_file}")
            print("请参考 config_template.json 创建配置文件")
            sys.exit(1)
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # 加载账号
            for acc in config_data.get('accounts', []):
                if acc.get('enabled', True):
                    self.accounts.append(acc)
            
            self.global_config = config_data.get('schedule', {})
            self.notification_config = config_data.get('notification', {})
            
            print(f"✅ 已加载 {len(self.accounts)} 个账号")
            
        except Exception as e:
            print(f"❌ 加载配置文件失败: {e}")
            sys.exit(1)
    
    def sign_all_accounts(self):
        """为所有账号执行签到"""
        results = []
        
        for idx, account in enumerate(self.accounts, 1):
            print(f"\n{'='*60}")
            print(f"📱 处理账号 {idx}/{len(self.accounts)}: {account['name']}")
            print(f"{'='*60}\n")
            
            try:
                # 创建配置
                config = Config(
                    token=account['token'],
                    app_secret=account['app_secret'],
                    device_id=account.get('device_id', ''),
                    version=account.get('version', '1.144.0'),
                    phone_brand=account.get('phone_brand', 'Xiaomi'),
                )
                
                # 创建签到实例
                signer = QieKjAutoSign(config)
                
                # 执行签到
                if self.global_config.get('watch_ad', True):
                    signer.auto_sign_with_ad()
                else:
                    signer.do_sign_in()
                
                results.append({
                    'account': account['name'],
                    'status': 'success',
                    'message': '签到成功'
                })
                
                # 账号间延迟，避免触发风控
                if idx < len(self.accounts):
                    delay = 5
                    print(f"\n⏳ 等待 {delay} 秒后处理下一个账号...")
                    time.sleep(delay)
                
            except Exception as e:
                print(f"\n❌ 账号 {account['name']} 签到失败: {e}")
                results.append({
                    'account': account['name'],
                    'status': 'failed',
                    'message': str(e)
                })
        
        return results
    
    def send_notification(self, results: List[Dict]):
        """发送签到结果通知"""
        if not self.notification_config.get('enabled', False):
            return
        
        print("\n📤 发送通知...")
        
        # 构建通知内容
        success_count = sum(1 for r in results if r['status'] == 'success')
        total_count = len(results)
        
        title = f"切客纪签到报告 ({success_count}/{total_count})"
        
        content_lines = ["签到结果详情：\n"]
        for r in results:
            emoji = "✅" if r['status'] == 'success' else "❌"
            content_lines.append(f"{emoji} {r['account']}: {r['message']}")
        
        content = "\n".join(content_lines)
        
        # 根据配置的类型发送通知
        notify_type = self.notification_config.get('type')
        
        if notify_type == 'serverchan':
            self._send_serverchan(title, content)
        elif notify_type == 'bark':
            self._send_bark(title, content)
        elif notify_type == 'webhook':
            self._send_webhook(title, content)
    
    def _send_serverchan(self, title: str, content: str):
        """发送 Server 酱通知"""
        key = self.notification_config.get('key')
        if not key:
            print("❌ 未配置 Server 酱 Key")
            return
        
        url = f"https://sctapi.ftqq.com/{key}.send"
        data = {
            "title": title,
            "desp": content
        }
        
        try:
            response = requests.post(url, data=data, timeout=10)
            if response.json().get('code') == 0:
                print("✅ Server 酱通知发送成功")
            else:
                print(f"❌ Server 酱通知发送失败: {response.json()}")
        except Exception as e:
            print(f"❌ 发送通知失败: {e}")
    
    def _send_bark(self, title: str, content: str):
        """发送 Bark 通知（iOS）"""
        key = self.notification_config.get('key')
        if not key:
            print("❌ 未配置 Bark Key")
            return
        
        url = f"https://api.day.app/{key}/{title}/{content}"
        
        try:
            response = requests.get(url, timeout=10)
            if response.json().get('code') == 200:
                print("✅ Bark 通知发送成功")
            else:
                print(f"❌ Bark 通知发送失败: {response.json()}")
        except Exception as e:
            print(f"❌ 发送通知失败: {e}")
    
    def _send_webhook(self, title: str, content: str):
        """发送自定义 Webhook"""
        url = self.notification_config.get('url')
        if not url:
            print("❌ 未配置 Webhook URL")
            return
        
        data = {
            "title": title,
            "content": content,
            "timestamp": int(time.time())
        }
        
        try:
            response = requests.post(url, json=data, timeout=10)
            if response.status_code == 200:
                print("✅ Webhook 通知发送成功")
            else:
                print(f"❌ Webhook 通知发送失败: {response.status_code}")
        except Exception as e:
            print(f"❌ 发送通知失败: {e}")


def main():
    """主函数"""
    print("="*60)
    print("🚀 切客纪自动签到工具（高级版）")
    print("="*60)
    print()
    
    # 检查配置文件
    config_file = Path(__file__).parent / "config.json"
    if not config_file.exists():
        # 尝试使用模板文件
        template_file = Path(__file__).parent / "config_template.json"
        if template_file.exists():
            print(f"⚠️  未找到 config.json，请复制 {template_file.name} 并重命名为 config.json")
            print(f"   然后编辑填入你的账号信息")
        else:
            print("❌ 未找到配置文件")
        sys.exit(1)
    
    # 创建多账号管理器
    manager = MultiAccountSign(str(config_file))
    
    # 执行签到
    results = manager.sign_all_accounts()
    
    # 发送通知
    manager.send_notification(results)
    
    # 打印总结
    print("\n" + "="*60)
    print("📊 签到完成统计")
    print("="*60)
    success_count = sum(1 for r in results if r['status'] == 'success')
    total_count = len(results)
    print(f"总账号数: {total_count}")
    print(f"成功: {success_count}")
    print(f"失败: {total_count - success_count}")
    print("="*60)


if __name__ == "__main__":
    main()
