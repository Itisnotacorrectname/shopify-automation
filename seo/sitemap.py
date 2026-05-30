"""
Sitemap 生成模块
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import List

sys.path.insert(0, str(Path(__file__).parent.parent))

from src import ShopifyClient
from src.api_client import ShopifyAPIError


def generate_sitemap(
    base_url: str = None,
    output_file: str = None,
    include_products: bool = True,
    include_pages: bool = True,
    include_collections: bool = True
) -> str:
    """
    生成 sitemap.xml
    
    Args:
        base_url: 网站基础 URL，如 https://hyl-test.myshopify.com
        output_file: 输出文件路径，默认输出到控制台
        include_products: 是否包含产品
        include_pages: 是否包含页面
        include_collections: 是否包含分类
    
    Returns:
        sitemap XML 内容
    """
    print("=" * 60)
    print("Generate Sitemap")
    print("=" * 60)
    
    client = ShopifyClient()
    
    if base_url is None:
        base_url = f"https://{client.store}"
    
    print(f"\nBase URL: {base_url}")
    
    url_count = 0
    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    ]
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 主页
    xml_lines.append(f"  <url>")
    xml_lines.append(f"    <loc>{base_url}/</loc>")
    xml_lines.append(f"    <lastmod>{today}</lastmod>")
    xml_lines.append(f"    <changefreq>daily</changefreq>")
    xml_lines.append(f"    <priority>1.0</priority>")
    xml_lines.append(f"  </url>")
    url_count += 1
    
    # 产品
    if include_products:
        print("\n📦 Fetching products...")
        try:
            products = client.get_products(limit=250)
            for product in products:
                handle = product.get("handle", "")
                updated_at = product.get("updated_at", today)[:10]
                
                xml_lines.append(f"  <url>")
                xml_lines.append(f"    <loc>{base_url}/products/{handle}</loc>")
                xml_lines.append(f"    <lastmod>{updated_at}</lastmod>")
                xml_lines.append(f"    <changefreq>weekly</changefreq>")
                xml_lines.append(f"    <priority>0.8</priority>")
                xml_lines.append(f"  </url>")
                url_count += 1
            print(f"   Added {len(products)} products")
        except ShopifyAPIError as e:
            print(f"   Error: {e}")
    
    # 页面
    if include_pages:
        print("\n📄 Fetching pages...")
        try:
            pages = client.get_pages()
            for page in pages:
                handle = page.get("handle", "")
                updated_at = page.get("updated_at", today)[:10]
                
                xml_lines.append(f"  <url>")
                xml_lines.append(f"    <loc>{base_url}/pages/{handle}</loc>")
                xml_lines.append(f"    <lastmod>{updated_at}</lastmod>")
                xml_lines.append(f"    <changefreq>monthly</changefreq>")
                xml_lines.append(f"    <priority>0.6</priority>")
                xml_lines.append(f"  </url>")
                url_count += 1
            print(f"   Added {len(pages)} pages")
        except ShopifyAPIError as e:
            print(f"   Error: {e}")
    
    # 分类
    if include_collections:
        print("\n📁 Fetching collections...")
        try:
            data = client._request("GET", "custom_collections.json")
            collections = data.get("custom_collections", [])
            for collection in collections:
                handle = collection.get("handle", "")
                updated_at = collection.get("updated_at", today)[:10]
                
                xml_lines.append(f"  <url>")
                xml_lines.append(f"    <loc>{base_url}/collections/{handle}</loc>")
                xml_lines.append(f"    <lastmod>{updated_at}</lastmod>")
                xml_lines.append(f"    <changefreq>daily</changefreq>")
                xml_lines.append(f"    <priority>0.7</priority>")
                xml_lines.append(f"  </url>")
                url_count += 1
            print(f"   Added {len(collections)} collections")
        except ShopifyAPIError as e:
            print(f"   Error: {e}")
    
    xml_lines.append("</urlset>")
    
    sitemap_xml = "\n".join(xml_lines)
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(sitemap_xml)
        print(f"\n✓ Sitemap saved to: {output_file}")
    else:
        print(f"\n--- Sitemap XML ({url_count} URLs) ---")
        print(sitemap_xml)
    
    return sitemap_xml


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate sitemap.xml")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--base-url", help="Base URL for the store")
    parser.add_argument("--no-products", action="store_true", help="Exclude products")
    parser.add_argument("--no-pages", action="store_true", help="Exclude pages")
    parser.add_argument("--no-collections", action="store_true", help="Exclude collections")
    
    args = parser.parse_args()
    
    generate_sitemap(
        base_url=args.base_url,
        output_file=args.output,
        include_products=not args.no_products,
        include_pages=not args.no_pages,
        include_collections=not args.no_collections
    )