# Shopify Automation Framework

Shopify 主题自动化部署与管理系统

[English](README_EN.md) | 中文

## 功能特性

- ✅ **主题部署** - 增量部署、全量部署、预览模式
- ✅ **产品管理** - CSV 导入、库存同步
- ✅ **备份回滚** - 完整主题备份与恢复
- ✅ **SEO 工具** - Sitemap 生成、Meta Tags 报告
- ✅ **数据分析** - 商店概览、库存报告、产品导出
- ✅ **价格管理** - 批量更新、价格比较
- ✅ **CI/CD 集成** - GitHub Actions 自动部署
- ✅ **Slack 通知** - 部署/备份完成通知

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置

编辑 `config.yaml` 文件：

```yaml
environments:
  dev:
    store: "hyl-test.myshopify.com"
    token: "shpat_xxx"
    theme_id: 123456789
```

### 3. 使用 CLI

```bash
# 部署
python cli.py deploy                    # 增量部署
python cli.py deploy --full             # 全量部署
python cli.py deploy --dry-run          # 预览模式

# 备份与回滚
python cli.py backup                    # 备份主题
python cli.py rollback <path> --dry-run # 预览回滚

# 产品管理
python cli.py import products.csv       # 导入产品
python cli.py inventory --csv file.csv  # 更新库存

# SEO
python cli.py sitemap -o sitemap.xml   # 生成 sitemap

# 数据分析
python cli.py summary                  # 商店概览
python cli.py inventory-report         # 库存报告
python cli.py export -o products.csv  # 导出产品

# 价格管理
python cli.py update-prices prices.csv # 更新价格
python cli.py compare-prices prices.csv # 比较价格
```

## 目录结构

```
shopify-automation/
├── cli.py                  # 统一 CLI 入口
├── config.yaml            # 配置文件
├── requirements.txt       # 依赖
├── src/                   # 核心模块
│   ├── api_client.py     # API 客户端
│   ├── file_loader.py    # 文件加载器
│   └── config.py         # 配置管理
├── deploy/                # 部署模块
├── products/              # 产品管理
├── maintenance/           # 备份回滚
├── seo/                   # SEO 工具
├── analytics/             # 数据分析
├── pricing/              # 价格管理
├── web/                  # 通知模块
└── .github/workflows/     # CI/CD
```

## GitHub 集成

### 自动部署

1. 将项目推送到 GitHub
2. 在 GitHub Settings → Secrets 添加：
   - `SHOPIFY_STORE`
   - `SHOPIFY_TOKEN`
   - `SHOPIFY_THEME_ID`

3. 推送到 `main` 分支将自动部署

详细说明请查看 [.github/ISSUE_TEMPLATE.md](.github/ISSUE_TEMPLATE.md)

### GitHub Actions 工作流

| Workflow | 触发条件 |
|----------|----------|
| Deploy | push 到 main 分支 |
| Test | push/PR 到 main 分支 |
| Backup | 每天凌晨 2:00 |

## 示例 CSV 格式

### 产品导入

```csv
title,body_html,vendor,product_type,tags,variants_price,variants_sku,variants_inventory_quantity
Memory Foam Mattress,<p>Premium mattress</p>,HYL,Mattresses,mattress,299.99,MF-001,50
```

### 库存更新

```csv
sku,quantity
MF-001,45
MF-002,30
```

### 价格更新

```csv
sku,price
MF-001,279.99
MF-002,199.99
```

## 开发

### 运行测试

```bash
python -m pytest tests/ -v
```

### 添加新模块

```python
# 新建模块
mkdir new_module
touch new_module/__init__.py

# 添加到 CLI
def cmd_new(args):
    from new_module import some_function
    return some_function()

# 在 main() 中注册
new_parser = subparsers.add_parser("new-command", help="Description")
new_parser.set_defaults(func=cmd_new)
```

## 注意事项

1. **API Token** - 请妥善保管您的 Shopify Admin API Token
2. **备份** - 重要操作前建议先备份
3. **测试** - 首次使用建议先在预览模式测试

## License

MIT