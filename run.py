"""
Shopify Automation Framework
一键部署入口
"""

import sys
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from deploy import deploy_all


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Shopify Theme Automation")
    parser.add_argument("--theme-dir", help="Theme directory path")
    parser.add_argument("--full", action="store_true", help="Force full deployment")
    parser.add_argument("--dry-run", action="store_true", help="Preview mode")
    
    args = parser.parse_args()
    
    success = deploy_all(
        theme_dir=args.theme_dir,
        incremental=not args.full,
        dry_run=args.dry_run
    )
    
    sys.exit(0 if success else 1)