"""
部署 Sections
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src import ShopifyClient, FileLoader
from src.api_client import ShopifyAPIError


def deploy_sections(
    theme_dir: str = None,
    specific_sections: list = None,
    incremental: bool = True
):
    """
    部署 Section 文件
    
    Args:
        theme_dir: 主题目录路径
        specific_sections: 指定要部署的 section 列表，为空则部署全部
        incremental: 是否启用增量部署
    """
    print("=" * 60)
    print("Deploying Sections")
    print("=" * 60)
    
    client = ShopifyClient()
    loader = FileLoader(theme_dir)
    
    sections = loader.get_sections()
    
    if specific_sections:
        sections = [s for s in sections if any(name in s for name in specific_sections)]
        print(f"\nFiltering to: {specific_sections}")
    
    print(f"\nFound {len(sections)} sections")
    
    # 增量部署准备
    if incremental:
        try:
            remote_hashes = client.get_all_assets()
            to_upload, _, _ = loader.compare_remote(remote_hashes)
            to_upload = [s for s in to_upload if s.startswith("sections/")]
            print(f"Incremental: {len(to_upload)} files to upload")
        except ShopifyAPIError:
            print("Failed to get remote files, deploying all...")
            to_upload = sections
    else:
        to_upload = sections
    
    success = 0
    errors = 0
    
    for section in sections:
        if incremental and section not in to_upload:
            continue
        
        content = loader.load_file(section)
        if content is None:
            print(f"⚠ {section} - not found")
            errors += 1
            continue
        
        try:
            client.upload_asset(section, content)
            print(f"✓ {section}")
            success += 1
        except ShopifyAPIError as e:
            print(f"✗ {section} - {e}")
            errors += 1
    
    print(f"\nDone: {success} uploaded, {errors} errors")
    return errors == 0