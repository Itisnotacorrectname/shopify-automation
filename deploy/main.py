"""
一键部署脚本
部署所有主题文件到 Shopify
"""

import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src import ShopifyClient, FileLoader
from src.api_client import ShopifyAPIError


def deploy_all(
    theme_dir: str = None,
    incremental: bool = True,
    dry_run: bool = False
):
    """
    一键部署所有主题文件
    
    Args:
        theme_dir: 主题目录路径
        incremental: 是否启用增量部署（只上传修改的文件）
        dry_run: 是否为预览模式（不实际上传）
    """
    print("=" * 60)
    print("Shopify Theme Deploy")
    print("=" * 60)
    
    # 初始化客户端
    try:
        client = ShopifyClient()
        print(f"\n✓ Connected to: {client.store}")
        print(f"  Theme ID: {client.theme_id}")
    except Exception as e:
        print(f"\n✗ Connection failed: {e}")
        return False
    
    # 初始化文件加载器
    loader = FileLoader(theme_dir)
    print(f"\n✓ Theme directory: {loader.theme_dir}")
    
    # 检查主题目录是否存在
    if not loader.theme_dir.exists():
        print(f"\n✗ Theme directory not found: {loader.theme_dir}")
        return False
    
    # 统计
    stats = {
        "uploaded": 0,
        "skipped": 0,
        "errors": 0
    }
    
    # 如果启用增量部署，先获取远程文件列表
    if incremental and not dry_run:
        print("\n📊 Fetching remote file list...")
        try:
            remote_hashes = client.get_all_assets()
            to_upload, to_delete, unchanged = loader.compare_remote(remote_hashes)
            print(f"   {len(to_upload)} files to upload")
            print(f"   {len(unchanged)} files unchanged")
            print(f"   {len(to_delete)} files to delete")
        except ShopifyAPIError as e:
            print(f"\n⚠ Failed to fetch remote files: {e}")
            print("   Falling back to full deployment...")
            to_upload = loader.list_files()
            incremental = False
    else:
        to_upload = loader.list_files()
    
    # 部署各个类型的文件
    print("\n" + "=" * 60)
    print("Deploying...")
    print("=" * 60)
    
    # 1. Sections
    print("\n📦 Sections:")
    sections = loader.get_sections()
    for section in sections:
        if incremental and section not in to_upload:
            stats["skipped"] += 1
            continue
        
        content = loader.load_file(section)
        if content is None:
            print(f"   ⚠ {section} - file not found")
            stats["errors"] += 1
            continue
        
        if dry_run:
            print(f"   🔄 {section} (dry run)")
            stats["uploaded"] += 1
        else:
            try:
                client.upload_asset(section, content)
                print(f"   ✓ {section}")
                stats["uploaded"] += 1
            except ShopifyAPIError as e:
                print(f"   ✗ {section} - {e}")
                stats["errors"] += 1
    
    # 2. Templates
    print("\n📄 Templates:")
    templates = loader.get_templates()
    for template in templates:
        if incremental and template not in to_upload:
            stats["skipped"] += 1
            continue
        
        content = loader.load_file(template)
        if content is None:
            print(f"   ⚠ {template} - file not found")
            stats["errors"] += 1
            continue
        
        if dry_run:
            print(f"   🔄 {template} (dry run)")
            stats["uploaded"] += 1
        else:
            try:
                client.upload_asset(template, content)
                print(f"   ✓ {template}")
                stats["uploaded"] += 1
            except ShopifyAPIError as e:
                print(f"   ✗ {template} - {e}")
                stats["errors"] += 1
    
    # 3. Assets
    print("\n🎨 Assets:")
    assets = loader.get_assets()
    for asset in assets:
        if incremental and asset not in to_upload:
            stats["skipped"] += 1
            continue
        
        content = loader.load_file(asset)
        if content is None:
            print(f"   ⚠ {asset} - file not found")
            stats["errors"] += 1
            continue
        
        if dry_run:
            print(f"   🔄 {asset} (dry run)")
            stats["uploaded"] += 1
        else:
            try:
                client.upload_asset(asset, content)
                print(f"   ✓ {asset}")
                stats["uploaded"] += 1
            except ShopifyAPIError as e:
                print(f"   ✗ {asset} - {e}")
                stats["errors"] += 1
    
    # 总结
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"  Uploaded: {stats['uploaded']}")
    print(f"  Skipped:  {stats['skipped']}")
    print(f"  Errors:   {stats['errors']}")
    
    if dry_run:
        print("\n🔍 This was a dry run. No files were actually uploaded.")
    
    print("\n✓ Deployment complete!")
    return stats["errors"] == 0


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Deploy Shopify theme")
    parser.add_argument("--theme-dir", help="Theme directory path")
    parser.add_argument("--full", action="store_true", help="Force full deployment (disable incremental)")
    parser.add_argument("--dry-run", action="store_true", help="Preview mode (no actual upload)")
    
    args = parser.parse_args()
    
    success = deploy_all(
        theme_dir=args.theme_dir,
        incremental=not args.full,
        dry_run=args.dry_run
    )
    
    sys.exit(0 if success else 1)