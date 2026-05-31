#!/bin/bash
# 本地部署脚本
# 使用方法: ./deploy-local.sh [zip文件路径]

set -e

ZIP_FILE="${1:-theme.zip}"

# 下载最新的主题包
gh run download latest --repo Itisnotacorrectname/shopify-automation --name shopify-theme-zip --dir . || {
    echo "请先在 GitHub Actions 中运行 deploy workflow 生成主题包"
    echo "或者手动提供 zip 文件路径: ./deploy-local.sh /path/to/theme.zip"
    exit 1
}

# 解压
unzip -o "$ZIP_FILE" -d deploy-temp

# 使用 cli.py 部署
cd deploy-temp
python ../cli.py deploy --full --theme-dir .
cd ..

# 清理
rm -rf deploy-temp

echo "部署完成！"