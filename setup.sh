#!/bin/bash
# Shopify Automation - GitHub Setup Script
# 运行此脚本初始化 Git 仓库并推送到 GitHub

echo "============================================"
echo "Shopify Automation - GitHub Setup"
echo "============================================"

# 检查 Git 是否安装
if ! command -v git &> /dev/null; then
    echo "❌ Git 未安装，请先安装 Git"
    exit 1
fi

# 检查是否已有远程仓库
if git remote -v | grep -q origin; then
    echo "⚠️ 远程仓库已存在，跳过添加"
else
    echo "📝 请输入 GitHub 仓库 URL (例如: https://github.com/username/shopify-automation.git)"
    read -p "> " repo_url
    
    if [ -z "$repo_url" ]; then
        echo "❌ 未提供仓库 URL"
        exit 1
    fi
    
    git remote add origin "$repo_url"
    echo "✅ 已添加远程仓库"
fi

# 初始化 Git（如果需要）
if [ ! -d ".git" ]; then
    echo "📦 初始化 Git 仓库..."
    git init
    git branch -M main
    
    # 添加所有文件
    echo "📁 添加文件..."
    git add .
    
    # 创建初始提交
    echo "💾 创建初始提交..."
    git commit -m "Initial commit - Shopify Automation Framework"
    
    echo ""
    echo "============================================"
    echo "✅ Git 仓库初始化完成！"
    echo "============================================"
    echo ""
    echo "下一步："
    echo "1. 在 GitHub 上创建仓库（如果还没有）"
    echo "2. 添加 Secrets 到 GitHub:"
    echo "   - SHOPIFY_STORE"
    echo "   - SHOPIFY_TOKEN"
    echo "   - SHOPIFY_THEME_ID"
    echo "3. 推送代码:"
    echo "   git push -u origin main"
    echo ""
fi

echo "📋 GitHub Secrets 配置指南:"
echo ""
echo "1. 进入 GitHub 仓库 → Settings → Secrets and variables → Actions"
echo "2. 添加以下 Secrets:"
echo ""
echo "   Name: SHOPIFY_STORE"
echo "   Value: hyl-test.myshopify.com"
echo ""
echo "   Name: SHOPIFY_TOKEN"
echo "   Value: shpat_xxxxxxxxxxxxxxxxxxxx"
echo ""
echo "   Name: SHOPIFY_THEME_ID"
echo "   Value: 151845732535"
echo ""
echo "============================================"
echo "🎉 设置完成！"
echo "============================================"