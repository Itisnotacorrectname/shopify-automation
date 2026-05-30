"""
部署功能测试
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src import FileLoader, ShopifyClient


def test_file_loader():
    """测试文件加载器"""
    loader = FileLoader()
    
    # 测试获取 sections
    sections = loader.get_sections()
    print(f"Found {len(sections)} sections")
    assert len(sections) > 0
    
    # 测试获取 templates
    templates = loader.get_templates()
    print(f"Found {len(templates)} templates")
    
    # 测试获取 assets
    assets = loader.get_assets()
    print(f"Found {len(assets)} assets")
    
    # 测试加载文件
    content = loader.load_file("sections/hyl-hero.liquid")
    assert content is not None
    assert "{% comment %}" in content
    print("✓ File loader test passed")


def test_hash_comparison():
    """测试哈希比较"""
    loader = FileLoader()
    
    # 获取文件哈希
    hash1 = loader.get_file_hash("sections/hyl-hero.liquid")
    hash2 = loader.get_file_hash("sections/hyl-hero.liquid")
    
    assert hash1 == hash2
    print(f"Hash: {hash1[:16]}...")
    print("✓ Hash comparison test passed")


def test_dry_run_deploy():
    """测试预览模式部署"""
    from deploy import deploy_all
    
    result = deploy_all(dry_run=True)
    assert result == True
    print("✓ Dry run deploy test passed")


if __name__ == "__main__":
    print("=" * 60)
    print("Running Deploy Tests")
    print("=" * 60)
    
    try:
        test_file_loader()
        test_hash_comparison()
        test_dry_run_deploy()
        print("\n✓ All tests passed!")
    except Exception as e:
        print(f"\n✗ Test failed: {e}")