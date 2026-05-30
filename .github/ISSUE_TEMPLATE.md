# GitHub Integration Guide

## 快速开始

### 1. 初始化 Git 仓库

```bash
# 进入项目目录
cd shopify-automation

# 运行设置脚本（Windows 使用 Git Bash 或 WSL）
bash setup.sh

# 或者手动初始化
git init
git branch -M main
```

### 2. 创建 GitHub 仓库

1. 登录 GitHub
2. 点击右上角 `+` → `New repository`
3. 填写仓库名称：`shopify-automation`
4. 不要勾选 "Initialize with README"
5. 点击 "Create repository"

### 3. 推送代码

```bash
git remote add origin https://github.com/YOUR_USERNAME/shopify-automation.git
git push -u origin main
```

### 4. 配置 GitHub Secrets

1. 进入仓库 `Settings` → `Secrets and variables` → `Actions`
2. 点击 `New repository secret`

添加以下 Secrets：

| Name | Value | 说明 |
|------|-------|------|
| `SHOPIFY_STORE` | `hyl-test.myshopify.com` | 商店域名 |
| `SHOPIFY_TOKEN` | `shpat_xxx` | Admin API Token |
| `SHOPIFY_THEME_ID` | `151845732535` | 主题 ID |

### 5. 启用 GitHub Actions

推送代码后，Actions 会自动运行：

- **Deploy**: 推送到 `main` 分支时自动部署
- **Test**: 每次 PR 和推送时运行测试
- **Backup**: 每天凌晨 2:00 自动备份

## 工作流程

### 自动部署流程

```
Push to main → Deploy Action → Deploy to Shopify → Backup
```

### 手动触发

1. 进入 `Actions` 标签页
2. 选择 `Deploy Shopify Theme` 或 `Daily Backup`
3. 点击 `Run workflow`

## 分支策略

| 分支 | 用途 |
|------|------|
| `main` | 生产环境，稳定版本 |
| `develop` | 开发分支，测试新功能 |

```bash
# 开发新功能
git checkout -b feature/new-feature
# ... 开发完成后
git push origin feature/new-feature
# 创建 Pull Request
```

## 本地开发

```bash
# 克隆仓库
git clone https://github.com/YOUR_USERNAME/shopify-automation.git

# 安装依赖
pip install -r requirements.txt

# 配置本地 config.yaml（不要提交）
# 编辑 config.yaml 设置你的商店信息

# 测试部署（预览模式）
python cli.py deploy --dry-run

# 提交更改
git add .
git commit -m "描述你的更改"
git push
```

## 故障排除

### Secrets 未配置
- 检查 `Settings` → `Secrets and variables` → `Actions`
- 确保 Secrets 名称完全匹配

### 部署失败
- 查看 Actions 日志
- 检查 API Token 权限
- 确认主题 ID 正确

### 测试失败
- 本地运行 `python -m pytest tests/`
- 确保 config.yaml 配置正确