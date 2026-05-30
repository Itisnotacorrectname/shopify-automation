"""
API Client 测试
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src import ShopifyClient


def test_connection():
    """测试 API 连接"""
    client = ShopifyClient()
    print(f"Store: {client.store}")
    print(f"Theme ID: {client.theme_id}")
    print(f"Base URL: {client.base_url}")
    assert client.store == "hyl-test.myshopify.com"
    print("✓ Connection test passed")


def test_get_products():
    """测试获取产品列表"""
    client = ShopifyClient()
    products = client.get_products(limit=5)
    print(f"Found {len(products)} products")
    for p in products[:3]:
        print(f"  - {p.get('title')}")
    assert len(products) > 0
    print("✓ Get products test passed")


def test_get_pages():
    """测试获取页面列表"""
    client = ShopifyClient()
    pages = client.get_pages()
    print(f"Found {len(pages)} pages")
    for page in pages[:3]:
        print(f"  - {page.get('title')}")
    assert len(pages) > 0
    print("✓ Get pages test passed")


def test_get_asset():
    """测试获取资源"""
    client = ShopifyClient()
    asset = client.get_asset("layout/theme.liquid")
    assert asset is not None
    print(f"✓ Get asset test passed")


if __name__ == "__main__":
    print("=" * 60)
    print("Running API Tests")
    print("=" * 60)
    
    try:
        test_connection()
        test_get_products()
        test_get_pages()
        test_get_asset()
        print("\n✓ All tests passed!")
    except Exception as e:
        print(f"\n✗ Test failed: {e}")