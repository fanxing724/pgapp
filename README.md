# 切客纪自动签到工具集

> 基于官方 APK v1.144.0 逆向分析的完整自动签到解决方案

[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-支持-2088FF?logo=github-actions)](https://github.com/features/actions)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 🏗️ 系统架构

```
电脑端 (获取 Token) → GitHub (存储配置) → GitHub Actions (自动签到+广告)
```

- 💻 **电脑端**：运行 `get_token.py` 获取 Token，自动更新到 GitHub Secrets
- ☁️ **GitHub Actions**：每天自动执行签到和观看广告
- 📦 **GitHub 仓库**：存放所有工具和分析结果

## ✨ 特性

- 🔑 **Token 自动获取** - 手机号+验证码一键获取，自动更新 GitHub Secrets
- ☁️ **云端自动化** - GitHub Actions 免费运行，无需服务器
- 🎲 **随机执行时间** - 每天在北京时间 8:00/12:00/18:00 中随机执行一次
- 🔐 **完整签名算法** - 基于官方 APK 提取的 appSecret
- 👥 **多账号支持** - 批量签到、独立配置
- 📺 **广告任务** - 自动观看广告领取奖励
- 📤 **消息推送** - Server酱、Bark、Webhook
- 🛡️ **防风控** - 随机时间 + 随机延迟，模拟真人操作
- 📊 **详细日志** - GitHub Actions 格式、本地彩色输出

## 🚀 快速开始（3 步）

```bash
# 1. 克隆仓库
git clone git@github.com:fanxing724/pgapp.git
cd pgapp

# 2. 获取 Token（电脑端运行）
./获取Token.sh

# 3. 启用 GitHub Actions（网页操作）
# 访问 https://github.com/fanxing724/pgapp/actions
# 点击 "Enable workflow"
```

**完成！** GitHub Actions 将每天自动执行签到和观看广告。

📖 **详细教程**：[完整方案.md](./完整方案.md)

## 📦 文件说明

| 文件名 | 功能描述 |
|--------|---------|
| **get_token.py** | 🔑 **Token 自动获取工具**（推荐） |
| **qiekj_auto_sign.py** | 🌟 核心签到脚本（单账号，功能完整） |
| **github_sign.py** | ☁️ **GitHub Actions 专用版**（推荐） |
| **quick_sign.py** | ⚡ 快速签到脚本（适合定时任务） |
| **auto_sign_advanced.py** | 🚀 高级版（支持多账号、消息推送） |
| **config_template.json** | 📋 多账号配置模板 |
| **extract_token.sh** | 🔧 Token 提取辅助工具 |
| **deploy_to_github.sh** | 🚀 **GitHub 一键部署脚本** |
| **自动签到_使用说明.md** | 📖 详细使用文档 |
| **GitHub_Actions_配置指南.md** | ☁️ **GitHub 部署指南** |
| **qiekj_api_analysis_report.md** | 📊 完整 API 分析报告 |

## 🚀 快速开始

### 方式1: GitHub Actions 自动化（推荐）⭐

**无需服务器，免费自动运行！**

1. 一键部署到 GitHub：
   ```bash
   ./deploy_to_github.sh
   ```

2. 配置 GitHub Secrets（Token）

3. 完成！每天自动执行签到

详见：[GitHub Actions 配置指南](./GitHub_Actions_配置指南.md)

### 方式2: 本地单账号使用

1. 编辑 `qiekj_auto_sign.py` 底部的配置：

```python
config = Config(
    token="粘贴你的Token",
    app_secret="bkZVOXBiRzhZUW9BZTFrRmgrRTdleXJkbFNMZ2x3RUplQTB3d0hCMWo1bz0=",
    device_id="你的设备ID",
)
```

2. 运行：

```bash
python3 qiekj_auto_sign.py
```

### 方式3: 本地多账号使用

1. 复制配置模板：

```bash
cp config_template.json config.json
```

2. 编辑 `config.json`，填入多个账号信息

3. 运行：

```bash
python3 auto_sign_advanced.py
```

## 🔧 Token 获取

### 方法 1️⃣：手机号登录获取（最简单，推荐）⭐

无需 Root，无需抓包，直接通过手机号+验证码获取 Token：

```bash
python3 get_token.py
```

按提示输入手机号和验证码即可自动获取 Token。

### 方法 2️⃣：自动提取（需要 Root）

```bash
./extract_token.sh
```

### 方法 3️⃣：抓包获取

查看 [自动签到_使用说明.md](./自动签到_使用说明.md) 中的详细说明。

## ⏰ 定时任务

### ☁️ GitHub Actions（推荐）

- ✅ 无需服务器
- ✅ 免费使用
- ✅ 自动执行
- ✅ 日志记录

详见：[GitHub Actions 配置指南](./GitHub_Actions_配置指南.md)

### 🖥️ 本地定时任务

#### Linux/macOS

```bash
# 编辑 crontab
crontab -e

# 每天早上 8 点执行签到
0 8 * * * cd /home/fanxing/文档/Default\ Project && python3 quick_sign.py >> /tmp/qiekj.log 2>&1
```

#### Windows

使用"任务计划程序"创建定时任务。

## 📊 功能特性

- ☁️ **GitHub Actions 自动化**（免费、无需服务器）
- ✅ 自动检测签到状态
- ✅ 执行每日签到
- ✅ 模拟观看广告领取奖励
- ✅ 多账号批量签到
- ✅ 签到结果通知（Server酱/Bark/Webhook）
- ✅ 防风控延迟
- ✅ 详细的日志输出
- ✅ GitHub Secrets 安全存储

## 🔐 安全说明

1. **appSecret 已从官方 APK 提取**，确保签名正确
2. **Token 有效期**：通常 7-30 天，过期后需重新获取
3. **风控策略**：
   - 每个账号间延迟 5 秒
   - 建议每天执行 1-2 次
   - 避免频繁请求

## 📖 相关文档

- 📋 [完整方案](./完整方案.md) - **完整架构和使用流程（推荐阅读）**
- ⚡ [快速参考](./快速参考.md) - 常用命令和配置速查表
- ☁️ [GitHub Actions 配置指南](./GitHub_Actions_配置指南.md) - 云端自动化详细教程
- 🚀 [GitHub 部署清单](./GitHub_部署清单.md) - 部署步骤检查表
- 📖 [使用说明](./自动签到_使用说明.md) - 详细的配置和故障排查指南
- 📊 [API 完整分析](./qiekj_api_analysis_report.md) - 393 个接口的详细文档

## ⚠️ 免责声明

本工具仅供学习交流使用，请勿用于商业目的。使用自动化脚本可能违反应用用户协议，存在账号封禁风险。使用本工具产生的一切后果由使用者自行承担。

## 📝 技术栈

- Python 3.8+
- requests - HTTP 客户端
- hashlib - SHA-256 签名
- base64 - 密钥解码

## 🛠️ 开发者

- 逆向分析：REA (Reverse Engineering Anything) + JADX
- API 分析：基于官方 APK v1.144.0
- 参考实现：[qiekj-android](https://github.com/wzs0512/qiekj-android)

---

**最后更新**: 2026-10-25
