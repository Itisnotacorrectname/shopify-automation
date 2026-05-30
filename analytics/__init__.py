"""
Analytics Module - 数据分析模块
"""

import sys
from pathlib import Path
from typing import Dict, List
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from src import ShopifyClient
from src.api_client import ShopifyAPIError


def get_store_summary() -> Dict:
    """获取商店概览"""
    print("=" * 60)
    print("Store Summary")
    print("=" * 60)
    
    client = ShopifyClient()
    
    summary = {
        "store": client.store,
        "products_count": 0,
        "collections_count": 0,
        "pages_count": 0,
        "total_inventory": 0
    }
    
    # 获取产品
    try:
        products = client.get_products(limit=250)
        summary["products_count"] = len(products)
        
        # 计算总库存
        total_inv = 0
        for p in products:
            for v in p.get("variants", []):
                total_inv += v.get("inventory_quantity", 0) or 0
        summary["total_inventory"] = total_inv
        print(f"📦 Products: {len(products)}")
        print(f"   Total Inventory: {total_inv}")
    except ShopifyAPIError as e:
        print(f"⚠ Failed to fetch products: {e}")
    
    # 获取分类
    try:
        data = client._request("GET", "custom_collections.json")
        collections = data.get("custom_collections", [])
        summary["collections_count"] = len(collections)
        print(f"📁 Collections: {len(collections)}")
    except ShopifyAPIError as e:
        print(f"⚠ Failed to fetch collections: {e}")
    
    # 获取页面
    try:
        pages = client.get_pages()
        summary["pages_count"] = len(pages)
        print(f"📄 Pages: {len(pages)}")
    except ShopifyAPIError as e:
        print(f"⚠ Failed to fetch pages: {e}")
    
    return summary


def get_inventory_report() -> Dict:
    """生成库存报告"""
    print("=" * 60)
    print("Inventory Report")
    print("=" * 60)
    
    client = ShopifyClient()
    
    try:
        products = client.get_products(limit=250)
    except ShopifyAPIError as e:
        print(f"Failed to fetch products: {e}")
        return {}
    
    low_stock = []
    out_of_stock = []
    healthy_stock = []
    
    for product in products:
        for variant in product.get("variants", []):
            qty = variant.get("inventory_quantity", 0) or 0
            title = f"{product['title']} - {variant.get('title', 'Default')}"
            sku = variant.get("sku", "N/A")
            
            if qty == 0:
                out_of_stock.append({"title": title, "sku": sku, "qty": qty})
            elif qty < 10:
                low_stock.append({"title": title, "sku": sku, "qty": qty})
            else:
                healthy_stock.append({"title": title, "sku": sku, "qty": qty})
    
    report = {
        "total_variants": len(out_of_stock) + len(low_stock) + len(healthy_stock),
        "out_of_stock": out_of_stock,
        "low_stock": low_stock,
        "healthy_stock": healthy_stock
    }
    
    print(f"\n📊 Summary:")
    print(f"   Total Variants: {report['total_variants']}")
    print(f"   Out of Stock: {len(out_of_stock)}")
    print(f"   Low Stock: {len(low_stock)}")
    print(f"   Healthy: {len(healthy_stock)}")
    
    if out_of_stock:
        print(f"\n⚠️ Out of Stock ({len(out_of_stock)}):")
        for item in out_of_stock[:5]:
            print(f"   - {item['title']} (SKU: {item['sku']})")
        if len(out_of_stock) > 5:
            print(f"   ... and {len(out_of_stock) - 5} more")
    
    return report


def generate_products_csv(output_file: str = "products_export.csv"):
    """导出产品到 CSV"""
    import csv
    
    print("=" * 60)
    print("Export Products to CSV")
    print("=" * 60)
    
    client = ShopifyClient()
    
    try:
        products = client.get_products(limit=250)
    except ShopifyAPIError as e:
        print(f"Failed to fetch products: {e}")
        return False
    
    with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow([
            'ID', 'Title', 'Handle', 'Vendor', 'Type', 'Tags',
            'Variant Price', 'Variant SKU', 'Variant Inventory',
            'Status', 'Created At', 'Updated At'
        ])
        
        for p in products:
            for v in p.get("variants", [{}]):
                writer.writerow([
                    p.get('id'),
                    p.get('title'),
                    p.get('handle'),
                    p.get('vendor'),
                    p.get('product_type'),
                    p.get('tags'),
                    v.get('price'),
                    v.get('sku'),
                    v.get('inventory_quantity', 0) or 0,
                    p.get('status'),
                    p.get('created_at'),
                    p.get('updated_at')
                ])
    
    print(f"\n✓ Exported {len(products)} products to {output_file}")
    return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Analytics")
    parser.add_argument("--summary", action="store_true", help="Show store summary")
    parser.add_argument("--inventory", action="store_true", help="Inventory report")
    parser.add_argument("--export", metavar="FILE", help="Export products to CSV")
    
    args = parser.parse_args()
    
    if args.summary:
        get_store_summary()
    elif args.inventory:
        get_inventory_report()
    elif args.export:
        generate_products_csv(args.export)
    else:
        get_store_summary()