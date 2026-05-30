#!/usr/bin/env python3
"""
Shopify Automation CLI
统一的命令行入口
"""

import sys
import argparse
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))


def cmd_deploy(args):
    """部署命令"""
    from deploy import deploy_all
    return deploy_all(
        theme_dir=args.theme_dir,
        incremental=not args.full,
        dry_run=args.dry_run
    )


def cmd_backup(args):
    """备份命令"""
    from maintenance import backup_theme, list_backups
    
    if args.list:
        return list_backups(args.dir) is not None
    
    result = backup_theme(args.dir, include_assets=not args.no_assets)
    return "error" not in result


def cmd_rollback(args):
    """回滚命令"""
    from maintenance import rollback_to_version
    
    result = rollback_to_version(
        args.backup_path,
        file_pattern=args.pattern,
        dry_run=args.dry_run
    )
    return result.get("errors", 0) == 0


def cmd_import(args):
    """导入产品命令"""
    from products import import_products_from_csv
    
    result = import_products_from_csv(
        args.csv_file,
        update_existing=args.update,
        max_products=args.max
    )
    return result.get("errors", 0) == 0


def cmd_inventory(args):
    """库存命令"""
    from products import update_inventory
    
    result = update_inventory(csv_file=args.csv)
    return result.get("errors", 0) == 0


def cmd_sitemap(args):
    """Sitemap 命令"""
    from seo import generate_sitemap
    
    generate_sitemap(
        base_url=args.base_url,
        output_file=args.output,
        include_products=not args.no_products,
        include_pages=not args.no_pages,
        include_collections=not args.no_collections
    )
    return True


def cmd_seo(args):
    """SEO 报告命令"""
    from seo import generate_meta_report
    
    generate_meta_report(args.output)
    return True


def cmd_summary(args):
    """商店概览命令"""
    from analytics import get_store_summary
    
    get_store_summary()
    return True


def cmd_inventory_report(args):
    """库存报告命令"""
    from analytics import get_inventory_report
    
    get_inventory_report()
    return True


def cmd_export(args):
    """导出产品命令"""
    from analytics import generate_products_csv
    
    generate_products_csv(args.output or "products_export.csv")
    return True


def cmd_update_prices(args):
    """更新价格命令"""
    from pricing import update_prices
    
    result = update_prices(
        csv_file=args.csv,
        percentage_change=args.percent
    )
    return result.get("errors", 0) == 0


def cmd_compare_prices(args):
    """比较价格命令"""
    from pricing import compare_prices
    
    compare_prices(args.csv)
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Shopify Automation CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # 部署
  %(prog)s deploy                    # 增量部署
  %(prog)s deploy --full             # 全量部署
  %(prog)s deploy --dry-run         # 预览

  # 备份与回滚
  %(prog)s backup                    # 备份主题
  %(prog)s backup --list            # 列出备份
  %(prog)s rollback <path> --dry-run # 预览回滚

  # 产品管理
  %(prog)s import products.csv       # 导入产品
  %(prog)s inventory --csv file.csv  # 更新库存

  # SEO
  %(prog)s sitemap -o sitemap.xml   # 生成 sitemap
  %(prog)s seo --report             # SEO 报告

  # 数据分析
  %(prog)s summary                  # 商店概览
  %(prog)s inventory-report         # 库存报告
  %(prog)s export -o products.csv   # 导出产品

  # 价格管理
  %(prog)s update-prices prices.csv # 更新价格
  %(prog)s compare-prices prices.csv # 比较价格
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Deploy
    deploy_parser = subparsers.add_parser("deploy", help="Deploy theme")
    deploy_parser.add_argument("--theme-dir", help="Theme directory")
    deploy_parser.add_argument("--full", action="store_true", help="Full deployment")
    deploy_parser.add_argument("--dry-run", action="store_true", help="Preview mode")
    deploy_parser.set_defaults(func=cmd_deploy)
    
    # Backup
    backup_parser = subparsers.add_parser("backup", help="Backup theme")
    backup_parser.add_argument("--dir", help="Backup directory")
    backup_parser.add_argument("--list", action="store_true", help="List backups")
    backup_parser.add_argument("--no-assets", action="store_true", help="Skip assets")
    backup_parser.set_defaults(func=cmd_backup)
    
    # Rollback
    rollback_parser = subparsers.add_parser("rollback", help="Rollback theme")
    rollback_parser.add_argument("backup_path", help="Backup directory path")
    rollback_parser.add_argument("--pattern", help="File pattern")
    rollback_parser.add_argument("--dry-run", action="store_true", help="Preview mode")
    rollback_parser.set_defaults(func=cmd_rollback)
    
    # Import
    import_parser = subparsers.add_parser("import", help="Import products")
    import_parser.add_argument("csv_file", help="CSV file path")
    import_parser.add_argument("--update", action="store_true", help="Update existing")
    import_parser.add_argument("--max", type=int, help="Max products")
    import_parser.set_defaults(func=cmd_import)
    
    # Inventory
    inv_parser = subparsers.add_parser("inventory", help="Update inventory")
    inv_parser.add_argument("--csv", help="CSV file path")
    inv_parser.set_defaults(func=cmd_inventory)
    
    # Sitemap
    sitemap_parser = subparsers.add_parser("sitemap", help="Generate sitemap")
    sitemap_parser.add_argument("--output", "-o", help="Output file")
    sitemap_parser.add_argument("--base-url", help="Base URL")
    sitemap_parser.add_argument("--no-products", action="store_true")
    sitemap_parser.add_argument("--no-pages", action="store_true")
    sitemap_parser.add_argument("--no-collections", action="store_true")
    sitemap_parser.set_defaults(func=cmd_sitemap)
    
    # SEO
    seo_parser = subparsers.add_parser("seo", help="SEO report")
    seo_parser.add_argument("--output", "-o", help="Output file")
    seo_parser.add_argument("--report", action="store_true", help="Generate report")
    seo_parser.set_defaults(func=cmd_seo)
    
    # Summary
    summary_parser = subparsers.add_parser("summary", help="Store summary")
    summary_parser.set_defaults(func=cmd_summary)
    
    # Inventory Report
    inv_report_parser = subparsers.add_parser("inventory-report", help="Inventory report")
    inv_report_parser.set_defaults(func=cmd_inventory_report)
    
    # Export
    export_parser = subparsers.add_parser("export", help="Export products")
    export_parser.add_argument("-o", "--output", help="Output file")
    export_parser.set_defaults(func=cmd_export)
    
    # Update Prices
    price_parser = subparsers.add_parser("update-prices", help="Update prices")
    price_parser.add_argument("csv", help="CSV file with prices")
    price_parser.add_argument("--percent", type=float, help="Percentage change")
    price_parser.set_defaults(func=cmd_update_prices)
    
    # Compare Prices
    compare_parser = subparsers.add_parser("compare-prices", help="Compare prices")
    compare_parser.add_argument("csv", help="CSV file to compare")
    compare_parser.set_defaults(func=cmd_compare_prices)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        success = args.func(args)
        return 0 if success else 1
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())