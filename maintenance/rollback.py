"""
回滚模块
从备份恢复主题文件到 Shopify
"""

import sys
import json
from pathlib import Path
from typing import Dict, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from src import ShopifyClient, FileLoader
from src.api_client import ShopifyAPIError


def rollback_to_version(
    backup_path: str,
    file_pattern: str = None,
    dry_run: bool = False
) -> Dict:
    """
    从备份恢复主题文件
    
    Args:
        backup_path: 备份目录路径
        file_pattern: 文件过滤模式（如 "sections/*.liquid"），None 表示全部
        dry_run: 预览模式，不实际上传
    
    Returns:
        恢复统计
    """
    print("=" * 60)
    print("Theme Rollback")
    print("=" * 60)
    print(f"\n📁 Backup: {backup_path}")
    
    backup_dir = Path(backup_path)
    
    if not backup_dir.exists():
        print("✗ Backup directory not found")
        return {"error": "Backup not found"}
    
    # 读取元数据
    metadata_file = backup_dir / "metadata.json"
    if metadata_file.exists():
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        print(f"   Store: {metadata.get('store')}")
        print(f"   Date:  {metadata.get('timestamp')}")
    
    client = ShopifyClient()
    loader = FileLoader(str(backup_dir))
    
    # 获取要恢复的文件
    if file_pattern:
        files = [str(p.relative_to(backup_dir)) for p in backup_dir.glob(file_pattern) if p.is_file()]
        print(f"\n🔍 Pattern: {file_pattern}")
    else:
        files = loader.list_files()
    
    print(f"   Files: {len(files)}")
    
    if dry_run:
        print("\n🔍 DRY RUN - No files will be uploaded\n")
    
    stats = {"uploaded": 0, "errors": 0}
    
    print("\n" + "=" * 60)
    print("Restoring Files...")
    print("=" * 60)
    
    for file_path in sorted(files):
        # 跳过元数据文件
        if file_path == "metadata.json" or file_path.startswith("."):
            continue
        
        content = loader.load_file(file_path)
        if content is None:
            print(f"⚠ {file_path} - not found")
            stats["errors"] += 1
            continue
        
        if dry_run:
            print(f"🔄 {file_path} (dry run)")
            stats["uploaded"] += 1
        else:
            try:
                client.upload_asset(file_path, content)
                print(f"✓ {file_path}")
                stats["uploaded"] += 1
            except ShopifyAPIError as e:
                print(f"✗ {file_path} - {e}")
                stats["errors"] += 1
    
    # 总结
    print("\n" + "=" * 60)
    print("Rollback Complete")
    print("=" * 60)
    print(f"  Uploaded: {stats['uploaded']}")
    print(f"  Errors:   {stats['errors']}")
    
    if dry_run:
        print("\n🔍 This was a dry run.")
    
    return stats


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Rollback Shopify theme")
    parser.add_argument("backup_path", help="Backup directory path")
    parser.add_argument("--pattern", help="File pattern to restore (e.g., 'sections/*.liquid')")
    parser.add_argument("--dry-run", action="store_true", help="Preview mode")
    
    args = parser.parse_args()
    
    rollback_to_version(
        args.backup_path,
        file_pattern=args.pattern,
        dry_run=args.dry_run
    )