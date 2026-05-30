"""
产品导入模块
支持从 CSV 文件导入产品到 Shopify
"""

import sys
import csv
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from src import ShopifyClient
from src.api_client import ShopifyAPIError


def read_csv(file_path: str) -> List[Dict]:
    """读取 CSV 文件"""
    products = []
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            products.append(row)
    return products


def parse_product(row: Dict) -> Dict:
    """
    解析 CSV 行数据为 Shopify 产品格式
    
    必需的 CSV 列：
    - title: 产品标题
    - body_html: 产品描述（可选）
    - vendor: 供应商（可选）
    - product_type: 产品类型（可选）
    - tags: 标签，逗号分隔（可选）
    - variants_price: 变体价格（可选）
    - variants_sku: SKU（可选）
    - variants_inventory_quantity: 库存数量（可选）
    - images_src: 图片 URL（可选）
    """
    product = {
        "title": row.get("title", ""),
        "body_html": row.get("body_html", ""),
        "vendor": row.get("vendor", ""),
        "product_type": row.get("product_type", ""),
        "tags": row.get("tags", ""),
    }
    
    # 处理变体
    variants = []
    price = row.get("variants_price", "").strip()
    sku = row.get("variants_sku", "").strip()
    inventory = row.get("variants_inventory_quantity", "").strip()
    
    if price or sku:
        variant = {
            "price": price,
            "sku": sku,
        }
        if inventory:
            variant["inventory_quantity"] = int(inventory)
            variant["inventory_management"] = "shopify"
        variants.append(variant)
    
    if variants:
        product["variants"] = variants
    
    # 处理图片
    images_src = row.get("images_src", "").strip()
    if images_src:
        product["images"] = [{"src": src.strip()} for src in images_src.split(",") if src.strip()]
    
    return product


def import_products_from_csv(
    csv_file: str,
    update_existing: bool = False,
    max_products: int = None
) -> Dict:
    """
    从 CSV 文件导入产品
    
    Args:
        csv_file: CSV 文件路径
        update_existing: 是否更新已存在的产品
        max_products: 最大导入数量，None 表示不限制
    
    Returns:
        导入统计
    """
    print("=" * 60)
    print("Product Import from CSV")
    print("=" * 60)
    print(f"\nFile: {csv_file}")
    
    # 读取 CSV
    try:
        rows = read_csv(csv_file)
        print(f"Found {len(rows)} products in CSV")
    except Exception as e:
        print(f"Failed to read CSV: {e}")
        return {"error": str(e)}
    
    # 限制数量
    if max_products:
        rows = rows[:max_products]
        print(f"Limiting to {max_products} products")
    
    # 初始化客户端
    client = ShopifyClient()
    
    stats = {
        "created": 0,
        "updated": 0,
        "skipped": 0,
        "errors": 0
    }
    
    # 获取现有产品用于比较
    existing_products = {}
    if update_existing:
        print("\n📊 Fetching existing products...")
        try:
            products = client.get_products(limit=250)
            existing_products = {p["title"]: p for p in products}
            print(f"   Found {len(existing_products)} existing products")
        except ShopifyAPIError as e:
            print(f"   Warning: Could not fetch existing products: {e}")
    
    # 导入每个产品
    print("\n" + "=" * 60)
    print("Importing Products...")
    print("=" * 60)
    
    for i, row in enumerate(rows, 1):
        title = row.get("title", "").strip()
        if not title:
            print(f"[{i}] ⚠ Skipped: No title")
            stats["skipped"] += 1
            continue
        
        # 检查是否已存在
        if title in existing_products and not update_existing:
            print(f"[{i}] ⏭ {title} - already exists (skip)")
            stats["skipped"] += 1
            continue
        
        # 解析产品数据
        product_data = parse_product(row)
        
        try:
            if title in existing_products:
                # 更新现有产品
                product_id = existing_products[title]["id"]
                client.update_product(product_id, product_data)
                print(f"[{i}] 🔄 {title} - updated")
                stats["updated"] += 1
            else:
                # 创建新产品
                client.create_product(product_data)
                print(f"[{i}] ✓ {title} - created")
                stats["created"] += 1
        except ShopifyAPIError as e:
            print(f"[{i}] ✗ {title} - {e}")
            stats["errors"] += 1
    
    # 总结
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"  Created: {stats['created']}")
    print(f"  Updated: {stats['updated']}")
    print(f"  Skipped: {stats['skipped']}")
    print(f"  Errors:  {stats['errors']}")
    print("\n✓ Import complete!")
    
    return stats


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Import products from CSV")
    parser.add_argument("csv_file", help="CSV file path")
    parser.add_argument("--update", action="store_true", help="Update existing products")
    parser.add_argument("--max", type=int, help="Maximum products to import")
    
    args = parser.parse_args()
    
    stats = import_products_from_csv(
        args.csv_file,
        update_existing=args.update,
        max_products=args.max
    )