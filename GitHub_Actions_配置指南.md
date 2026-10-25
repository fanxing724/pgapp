# GitHub Actions 自动签到配置指南

## 🚀 快速开始

### 1. Fork 或创建仓库

1. 将这些文件上传到你的 GitHub 仓库
2. 确保 `.github/workflows/auto-sign.yml` 文件存在

### 2. 配置 GitHub Secrets

进入仓库 → Settings → Secrets and variables → Actions → New repository secret

#### 方式一：单账号配置（简单）

| Secret 名称 | 值 | 必填 |
|------------|---|------|
| `QIEKJ_TOKEN` | 你的用户Token | ✅ |
| `QIEKJ_DEVICE_ID` | 设备ID | 推荐 |
| `QIEKJ_NAME` | 账号备注名 | 可选 |
| `QIEKJ_PHONE_BRAND` | 手机品牌 | 可选 |
| `WEBHOOK_URL` | 通知Webhook地址 | 可选 |

#### 方式二：多账号配置（推荐）

创建一个名为 `ACCOUNTS_CONFIG` 的 Secret，值为 JSON 格式：

```json
{
  "accounts": [
    {
      "name": "主账号",
      "token": "token_1_here",
      "device_id": "device_1",
      "phone_brand": "Xiaomi",
      "enabled": true
    },
    {
      "name": "备用账号",
      "token": "token_2_here",
      "device_id": "device_2",
      "phone_brand": "Huawei",
      "enabled": true
    }
  ]
}
```

### 3. 启用工作流

1. 进入仓库的 Actions 标签
2. 选择 "切客纪自动签到" 工作流
3. 点击 "Enable workflow"

### 4. 手动测试

点击 "Run workflow" 按钮手动触发一次测试

## ⏰ 定时执行时间

**默认配置：每天随机执行一次**

工作流在北京时间 **8:00 / 12:00 / 18:00** 三个时间点触发，根据当天日期的 MD5 哈希值确定性地选择一个时间点真正执行，其他时间点自动跳过。执行前还有 0-10 分钟的随机延迟。

这样的好处：
- ✅ 每天恰好执行一次
- ✅ 时间随机分布，避免风控检测
- ✅ 模拟真人不规律的操作习惯

```yaml
schedule:
  - cron: '0 0 * * *'   # UTC 0:00 = 北京时间 8:00
  - cron: '0 4 * * *'   # UTC 4:00 = 北京时间 12:00
  - cron: '0 10 * * *'  # UTC 10:00 = 北京时间 18:00
```

**Cron 格式说明**：
```
┌───────── 分钟 (0 - 59)
│ ┌───────── 小时 (0 - 23)
│ │ ┌───────── 日期 (1 - 31)
│ │ │ ┌───────── 月份 (1 - 12)
│ │ │ │ ┌───────── 星期 (0 - 6，0=周日)
│ │ │ │ │
* * * * *
```

常用示例：
- `0 0 * * *` - 每天 UTC 0:00
- `0 0,12 * * *` - 每天 UTC 0点和12点
- `0 0 * * 1` - 每周一 UTC 0点
- `*/30 * * * *` - 每30分钟

## 📤 通知配置（可选）

### Server 酱（微信通知）

1. 访问 https://sct.ftqq.com/
2. 微信扫码登录，获取 SendKey
3. 在 `config.json` 中配置：

```json
{
  "notification": {
    "enabled": true,
    "type": "serverchan",
    "key": "你的SendKey"
  }
}
```

### Bark（iOS 通知）

1. 在 App Store 下载 Bark
2. 获取推送 Key
3. 配置：

```json
{
  "notification": {
    "enabled": true,
    "type": "bark",
    "key": "你的BarkKey"
  }
}
```

### 自定义 Webhook

设置 `WEBHOOK_URL` Secret：

```
https://your-webhook.com/notify
```

支持的 Webhook 格式：
- 钉钉机器人
- 企业微信机器人
- 飞书机器人
- 自定义 HTTP 接口

## 🔒 安全建议

### 1. 保护敏感信息

- ✅ 使用 GitHub Secrets 存储 Token
- ✅ 不要在代码中硬编码 Token
- ✅ 定期更换 Token
- ✅ 不要将 Token 提交到代码仓库

### 2. 私有仓库

建议将仓库设为 **Private**，防止 Token 泄露：

Settings → General → Danger Zone → Change repository visibility → Make private

### 3. 限制工作流权限

在 `.github/workflows/auto-sign.yml` 中添加：

```yaml
permissions:
  contents: read
```

## 📊 查看执行日志

1. 进入 Actions 标签
2. 点击最近的工作流运行
3. 展开 "执行签到" 步骤查看详细日志

日志特性：
- ✅ 彩色输出（INFO/WARNING/ERROR）
- ✅ 分组显示每个账号
- ✅ 自动上传日志文件
- ✅ 支持 GitHub Actions 注释格式

## 🐛 故障排查

### Q1: 工作流没有自动执行

**原因**：GitHub Actions 定时任务有延迟

**解决**：
- 定时任务可能延迟 5-30 分钟
- 如果仓库 60 天无活动，定时任务会自动禁用
- 点击 "Enable workflow" 重新启用

### Q2: 提示 "未配置任何账号"

**原因**：Secrets 未正确配置

**解决**：
1. 检查 Secret 名称是否正确
2. 检查 JSON 格式是否正确（多账号配置）
3. 重新创建 Secret

### Q3: 签到失败 "Token 无效"

**原因**：Token 过期或错误

**解决**：
- 重新获取 Token
- 更新 Secret 中的 Token 值

### Q4: 如何停止自动签到

**方法1**：禁用工作流
- Actions → 选择工作流 → ⋯ → Disable workflow

**方法2**：删除 Secret
- Settings → Secrets → 删除相关 Secret

## 📝 高级配置

### 自定义执行时间

编辑 `.github/workflows/auto-sign.yml`，修改 cron 表达式和对应的时间检查逻辑：

```yaml
schedule:
  # 例如改为北京时间 7:00 / 13:00 / 20:00
  - cron: '0 23 * * *'  # UTC 23:00 = 北京时间 7:00（次日）
  - cron: '0 5 * * *'   # UTC 5:00 = 北京时间 13:00
  - cron: '0 12 * * *'  # UTC 12:00 = 北京时间 20:00
```

同时更新"检查今日执行时间"步骤中的 `SLOT_HOURS` 数组为 `(23 5 12)`。

### 指定账号执行

手动触发时，在 `account_index` 输入框中输入账号索引（从 0 开始）：
- `0` - 只执行第一个账号
- `0,1` - 执行前两个账号
- 留空 - 执行所有账号

### 调整账号间延迟

编辑 `github_sign.py`，找到：

```python
if idx < len(accounts):
    delay = 10  # 修改这个值（秒）
    time.sleep(delay)
```

## 🔗 相关链接

- [GitHub Actions 文档](https://docs.github.com/actions)
- [Cron 表达式生成器](https://crontab.guru/)
- [Server 酱](https://sct.ftqq.com/)
- [Bark](https://bark.day.app/)

---

**提示**：首次使用建议先手动触发一次测试，确认配置正确后再启用定时任务。
