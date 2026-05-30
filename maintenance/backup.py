"""
备份模块
下载并保存主题文件到本地
"""

import sys
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from src import ShopifyClient, FileLoader
from src.api_client import ShopifyAPIError


def backup_theme(backup_dir: str = None, include_assets: bool = True) -> Dict:
    """
    备份当前主题到本地目录
    
    Args:
        backup_dir: 备份目录，默认使用 config 中的设置
        include_assets: 是否包含资源文件（图片等）
    
    Returns:
        备份统计
    """
    print("=" * 60)
    print("Theme Backup")
    print("=" * 60)
    
    client = ShopifyClient()
    
    # 确定备份目录
    if backup_dir is None:
        backup_dir = Path(__file__).parent.parent / "backups"
    else:
        backup_dir = Path(backup_dir)
    
    # 创建带时间戳的备份目录
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / timestamp
    backup_path.mkdir(parents=True, exist_ok=True)
    
    print(f"\n📁 Backup location: {backup_path}")
    
    stats = {
        "sections": 0,
        "templates": 0,
        "layouts": 0,
        "snippets": 0,
        "assets": 0,
        "other": 0,
        "errors": 0
    }
    
    # 获取所有资源
    print("\n📥 Downloading assets...")
    try:
        # 获取主题所有文件
        all_keys = _get_all_asset_keys(client)
        print(f"   Found {len(all_keys)} files to backup")
        
        for key in all_keys:
            try:
                asset = client.get_asset(key)
                if not asset:
                    continue
                
                value = asset.get("value", "")
                if not value:
                    continue
                
                # 保存文件
                file_path = backup_path / key
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(value)
                
                # 统计
                if key.startswith("sections/"):
                    stats["sections"] += 1
                elif key.startswith("templates/"):
                    stats["templates"] += 1
                elif key.startswith("layout/"):
                    stats["layouts"] += 1
                elif key.startswith("snippets/"):
                    stats["snippets"] += 1
                elif key.startswith("assets/") and include_assets:
                    stats["assets"] += 1
                else:
                    stats["other"] += 1
                    
            except Exception as e:
                print(f"   ⚠ {key}: {e}")
                stats["errors"] += 1
                
    except ShopifyAPIError as e:
        print(f"Failed to fetch assets: {e}")
        return {"error": str(e)}
    
    # 保存备份元数据
    metadata = {
        "timestamp": timestamp,
        "store": client.store,
        "theme_id": client.theme_id,
        "stats": stats
    }
    
    with open(backup_path / "metadata.json", 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)
    
    # 总结
    print("\n" + "=" * 60)
    print("Backup Complete")
    print("=" * 60)
    print(f"  Sections:    {stats['sections']}")
    print(f"  Templates:  {stats['templates']}")
    print(f"  Layouts:     {stats['layouts']}")
    print(f"  Snippets:    {stats['snippets']}")
    print(f"  Assets:      {stats['assets']}")
    print(f"  Other:       {stats['other']}")
    print(f"  Errors:      {stats['errors']}")
    
    return {"path": str(backup_path), "stats": stats}


def _get_all_asset_keys(client: ShopifyClient) -> List[str]:
    """获取所有资源键"""
    keys = []
    page_info = None
    
    while True:
        if page_info:
            url = f"themes/{client.theme_id}/assets.json?limit=250&page_info={page_info}"
        else:
            url = f"themes/{client.theme_id}/assets.json?limit=250"
        
        data = client._request("GET", url)
        
        for asset in data.get("assets", []):
            keys.append(asset["key"])
        
        # 检查分页
        link = data.get("pagination", {}).get("next_url", "")
        if not link:
            break
        
        # 提取 page_info
        import re
        match = re.search(r'page_info=([^&]+)', link)
        if match:
            page_info = match.group(1)
        else:
            break
    
    return keys


def list_backups(backup_dir: str = None) -> List[Dict]:
    """
    列出所有备份
    
    Returns:
        备份列表
    """
    if backup_dir is None:
        backup_dir = Path(__file__).parent.parent / "backups"
    else:
        backup_dir = Path(backup_dir)
    
    if not backup_dir.exists():
        print("No backups found")
        return []
    
    backups = []
    
    for item in sorted(backup_dir.iterdir(), reverse=True):
        if item.is_dir():
            metadata_file = item / "metadata.json"
            if metadata_file.exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    backups.append({
                        "path": str(item),
                        "timestamp": metadata.get("timestamp"),
                        "store": metadata.get("store"),
                        "stats": metadata.get("stats", {})
                    })
    
    print("=" * 60)
    print(f"Backups ({len(backups)} found)")
    print("=" * 60)
    
    for i, backup in enumerate(backups, 1):
        print(f"\n[{i}] {backup['timestamp']}")
        print(f"    Store: {backup['store']}")
        print(f"    Files: {sum(backup['stats'].values()) - backup['stats'].get('errors', 0)}")
    
    return backups


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Backup Shopify theme")
    parser.add_argument("--list", action="store_true", help="List all backups")
    parser.add_argument("--dir", help="Backup directory")
    
    args = parser.parse_args()
    
    if args.list:
        list_backups(args.dir)
    else:
        backup_theme(args.dir)