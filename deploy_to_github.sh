#!/bin/bash
# GitHub 自动签到一键部署脚本

echo "==================================="
echo "  GitHub 自动签到部署工具"
echo "==================================="
echo ""

# 检查 git 是否安装
if ! command -v git &> /dev/null; then
    echo "❌ 未安装 git"
    echo "请先安装 git: sudo apt install git"
    exit 1
fi

# 获取仓库信息
echo "📝 请输入 GitHub 仓库信息"
echo ""
read -p "GitHub 用户名: " github_user
read -p "仓库名称 (默认: qiekj-auto-sign): " repo_name
repo_name=${repo_name:-qiekj-auto-sign}

echo ""
read -p "是否创建新仓库? (y/n): " create_repo

if [[ "$create_repo" =~ ^[Yy]$ ]]; then
    echo ""
    echo "💡 请先在 GitHub 上创建仓库: https://github.com/new"
    echo "   仓库名称: $repo_name"
    echo "   可见性: Private (推荐)"
    echo ""
    read -p "创建完成后按回车继续..."
fi

# 初始化 git 仓库
echo ""
echo "🔧 初始化 Git 仓库..."
git init
git branch -M main

# 创建 .gitignore
cat > .gitignore << EOF
# 配置文件（包含敏感信息）
config.json
*.log

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
*.egg-info/

# IDE
.vscode/
.idea/
*.swp
*.swo

# 系统文件
.DS_Store
Thumbs.db
EOF

# 添加必要文件
echo "📦 添加文件到 Git..."
git add .github/workflows/auto-sign.yml
git add github_sign.py
git add qiekj_auto_sign.py
git add config_template.json
git add .gitignore
git add README.md
git add GitHub_Actions_配置指南.md

# 创建初始提交
echo "💾 创建提交..."
git commit -m "🎉 初始化自动签到项目

- 支持多账号批量签到
- 支持定时任务
- 支持消息推送
- 支持 GitHub Actions 自动化"

# 添加远程仓库
echo ""
echo "🔗 关联远程仓库..."
repo_url="https://github.com/${github_user}/${repo_name}.git"
git remote add origin "$repo_name" 2>/dev/null || git remote set-url origin "$repo_name"

echo ""
echo "==================================="
echo "  部署准备完成！"
echo "==================================="
echo ""
echo "📋 下一步操作："
echo ""
echo "1. 推送到 GitHub:"
echo "   git push -u origin main"
echo ""
echo "2. 配置 Secrets:"
echo "   访问: https://github.com/${github_user}/${repo_name}/settings/secrets/actions"
echo "   添加 Secret: ACCOUNTS_CONFIG (多账号) 或 QIEKJ_TOKEN (单账号)"
echo ""
echo "3. 启用工作流:"
echo "   访问: https://github.com/${github_user}/${repo_name}/actions"
echo "   点击 'Enable workflow'"
echo ""
echo "4. 手动测试:"
echo "   在 Actions 页面点击 'Run workflow'"
echo ""
echo "📖 详细文档: GitHub_Actions_配置指南.md"
echo ""

# 询问是否立即推送
read -p "是否立即推送到 GitHub? (y/n): " push_now

if [[ "$push" =~ ^[Yy]$ ]]; then
    echo ""
    echo "📤 推送到 GitHub..."
    git push -u origin main
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ 推送成功！"
        echo "🌐 仓库地址: https://github.com/${github_user}/${repo_name}"
        echo "⚙️  Actions: https://github.com/${github_user}/${repo_name}/actions"
    else
        echo ""
        echo "❌ 推送失败，请检查："
        echo "   1. 是否已在 GitHub 创建仓库"
        echo "   2. 是否有推送权限"
        echo "   3. 网络连接是否正常"
    fi
else
    echo ""
    echo "✅ 本地准备完成，稍后手动执行:"
    echo "   git push -u origin main"
fi

echo ""
echo "🎉 部署完成！"
