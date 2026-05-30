"""
部署 Assets (CSS, JS, Images)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src import ShopifyClient, FileLoader
from src.api_client import ShopifyAPIError


def deploy_assets(
    theme_dir: str = None,
    incremental: bool = True
):
    """
    部署资源文件
    
    Args:
        theme_dir: 主题目录路径
        incremental: 是否启用增量部署
    """
    print("=" * 60)
    print("Deploying Assets")
    print("=" * 60)
    
    client = ShopifyClient()
    loader = FileLoader(theme_dir)
    
    assets = loader.get_assets()
    print(f"\nFound {len(assets)} assets")
    
    # 增量部署
    if incremental:
        try:
            remote_hashes = client.get_all_assets()
            to_upload, _, _ = loader.compare_remote(remote_hashes)
            to_upload = [a for a in to_upload if a.startswith("assets/")]
            print(f"Incremental: {len(to_upload)} files to upload")
        except ShopifyAPIError:
            to_upload = assets
    else:
        to_upload = assets
    
    success = 0
    errors = 0
    
    for asset in assets:
        if incremental and asset not in to_upload:
            continue
        
        content = loader.load_file(asset)
        if content is None:
            print(f"⚠ {asset} - not found")
            errors += 1
            continue
        
        try:
            client.upload_asset(asset, content)
            print(f"✓ {asset}")
            success += 1
        except ShopifyAPIError as e:
            print(f"✗ {asset} - {e}")
            errors += 1
    
    print(f"\nDone: {success} uploaded, {errors} errors")
    return errors == 0