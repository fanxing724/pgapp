# GitHub Actions 部署清单

## ✅ 部署前检查

### 1. 文件准备

确保以下文件已创建：

- [x] `.github/workflows/auto-sign.yml` - GitHub Actions 工作流
- [x] `github_sign.py` - GitHub Actions 专用脚本
- [x] `qiekj_auto_sign.py` - 核心签到逻辑
- [x] `config_template.json` - 配置模板
- [x] `.gitignore` - Git 忽略文件
- [x] `README.md` - 项目说明
- [x] `GitHub_Actions_配置指南.md` - 配置指南

### 2. 获取必要信息

- [ ] 切客纪 Token（通过抓包或 Root 获取）
- [ ] 设备 ID（可选但推荐）
- [ ] GitHub 账号

## 🚀 部署步骤

### 方式一：使用部署脚本（推荐）

```bash
./deploy_to_github.sh
```

按提示操作即可。

### 方式二：手动部署

#### 1. 初始化 Git

```bash
git init
git add .
git commit -m "初始化项目"
```

#### 2. 创建 GitHub 仓库

访问 https://github.com/new 创建新仓库：
- 仓库名称：`qiekj-auto-sign`（或自定义）
- 可见性：**Private**（推荐）
- 不要初始化 README、.gitignore 或 License

#### 3. 推送代码

```bash
git remote add origin https://github.com/你的用户名/qiekj-auto-sign.git
git branch -M main
git push -u origin main
```

#### 4. 配置 Secrets

访问 `https://github.com/你的用户名/qiekj-auto-sign/settings/secrets/actions`

**单账号配置**（简单）：

| Name | Value |
|------|-------|
| `QIEKJ_TOKEN` | 你的Token |
| `QIEKJ_DEVICE_ID` | 设备ID（可选） |
| `QIEKJ_NAME` | 账号备注（可选） |

**多账号配置**（推荐）：

创建 Secret `ACCOUNTS_CONFIG`，值为：

```json
{
  "accounts": [
    {
      "name": "主账号",
      "token": "你的Token1",
      "device_id": "设备ID1",
      "phone_brand": "Xiaomi",
      "enabled": true
    },
    {
      "name": "备用账号",
      "token": "你的Token2",
      "device_id": "设备ID2",
      "phone_brand": "Huawei",
      "enabled": true
    }
  ]
}
```

#### 5. 启用工作流

1. 访问 `https://github.com/你的用户名/qiekj-auto-sign/actions`
2. 点击 "I understand my workflows, go ahead and enable them"
3. 选择 "切客纪自动签到" 工作流
4. 点击 "Enable workflow"

#### 6. 测试运行

1. 在 Actions 页面，选择 "切客纪自动签到"
2. 点击 "Run workflow" 按钮
3. 选择 "Run workflow" 确认
4. 等待执行完成，查看日志

## 🔍 验证部署

### 检查清单

- [ ] 仓库已创建且为 Private
- [ ] 代码已推送成功
- [ ] Secrets 已正确配置
- [ ] 工作流已启用
- [ ] 手动触发测试成功
- [ ] 日志显示签到成功

### 查看日志

1. 进入 Actions 标签
2. 点击最近的运行记录
3. 展开各个步骤查看详细日志

成功的日志应该包含：
```
✅ 签到成功! 获得积分: X, 连续签到: Y 天
```

## ⚙️ 配置优化

### 调整执行时间

编辑 `.github/workflows/auto-sign.yml`：

```yaml
schedule:
  # 北京时间 6:00 (UTC 22:00 前一天)
  - cron: '0 22 * * *'
  # 北京时间 18:00 (UTC 10:00)
  - cron: '0 10 * * *'
```

### 添加通知

在 Secrets 中添加：

| Name | Value |
|------|-------|
| `WEBHOOK_URL` | 你的Webhook地址 |

支持的 Webhook：
- Server酱: `https://sctapi.ftqq.com/YOUR_KEY.send`
- Bark: `https://api.day.app/YOUR_KEY/`
- 自定义: 任何接受 POST JSON 的 URL

## 🐛 常见问题

### 问题1: 工作流未自动执行

**原因**：
- GitHub Actions 定时任务可能有 5-30 分钟延迟
- 仓库 60 天无活动会自动禁用定时任务

**解决**：
- 等待或手动触发
- 定期访问仓库保持活跃
- 或在设置中重新启用工作流

### 问题2: Secrets 配置后仍提示未配置

**检查**：
- Secret 名称是否完全匹配（区分大小写）
- JSON 格式是否正确（多账号配置）
- 是否点击了 "Add secret" 保存

### 问题3: 签到失败 "Token 无效"

**原因**：
- Token 已过期（通常 7-30 天有效期）
- Token 复制不完整

**解决**：
- 重新获取 Token
- 更新对应的 Secret

### 问题4: 部分账号签到失败

**检查**：
- 查看日志中的具体错误信息
- 确认每个账号的 Token 都有效
- 检查账号间延迟是否足够

## 📊 监控和维护

### 定期检查

- 每周检查一次 Actions 运行记录
- 确认签到成功率
- 及时更新过期的 Token

### 日志保存

GitHub Actions 会保存 90 天的运行日志：
- 可以在 Actions 页面下载
- 也可以配置 artifact 自动保存

### Token 更新提醒

建议在 Token 过期前更新：
1. 在手机上重新登录切客纪 APP
2. 抓包获取新 Token
3. 更新 GitHub Secrets
4. 测试运行确认

## 🔗 相关链接

- 📖 [完整配置指南](./GitHub_Actions_配置指南.md)
- 📊 [API 分析文档](./qiekj_api_analysis_report.md)
- 🔧 [Token 提取工具](./extract_token.sh)
- 💬 [GitHub Actions 文档](https://docs.github.com/actions)

## ✨ 完成标志

当你看到以下内容时，说明部署成功：

1. ✅ GitHub 仓库中有完整的代码
2. ✅ Actions 页面显示绿色的成功标记
3. ✅ 日志中显示 "签到成功"
4. ✅ 每天自动执行（北京时间 8:00 和 20:00）

---

**恭喜！你的自动签到系统已经搭建完成！** 🎉
