"""
Pricing Module - 价格管理模块
批量更新产品价格
"""

import sys
import csv
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).parent.parent))

from src import ShopifyClient
from src.api_client import ShopifyAPIError


def update_prices(
    csv_file: str = None,
    price_changes: Dict[str, float] = None,
    percentage_change: float = None
) -> Dict:
    """
    更新产品价格
    
    Args:
        csv_file: CSV 文件（需包含 sku 和 price 列）
        price_changes: SKU 到新价格的字典
        percentage_change: 百分比调整（如 1.1 表示涨价 10%）
    
    Returns:
        更新统计
    """
    print("=" * 60)
    print("Update Prices")
    print("=" * 60)
    
    client = ShopifyClient()
    
    # 收集价格更新
    updates = {}
    
    if csv_file:
        print(f"\n📄 Reading from: {csv_file}")
        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                sku = row.get('sku', '').strip()
                price = row.get('price', '').strip()
                if sku and price:
                    updates[sku] = float(price)
        print(f"   Found {len(updates)} price updates")
    
    if price_changes:
        updates.update(price_changes)
        print(f"   Added {len(price_changes)} manual updates")
    
    if not updates:
        print("No price updates to process")
        return {"updated": 0}
    
    # 获取所有产品
    print("\n📊 Fetching products...")
    products = client.get_products(limit=250)
    print(f"   Found {len(products)} products")
    
    stats = {"updated": 0, "errors": 0}
    
    print("\n" + "=" * 60)
    print("Updating Prices...")
    print("=" * 60)
    
    for product in products:
        product_updated = False
        product_data = {"id": product["id"], "variants": []}
        
        for variant in product.get("variants", []):
            sku = variant.get("sku", "").strip()
            
            if sku in updates:
                old_price = variant.get("price")
                new_price = updates[sku]
                
                # 如果设置了百分比调整
                if percentage_change and old_price:
                    new_price = round(float(old_price) * percentage_change, 2)
                
                product_data["variants"].append({
                    "id": variant["id"],
                    "price": str(new_price)
                })
                
                if not product_updated:
                    print(f"  🔄 {product['title']}")
                    product_updated = True
                
                print(f"     {sku}: {old_price} → {new_price}")
        
        if product_data.get("variants"):
            try:
                client._request("PUT", f"products/{product['id']}.json", {"product": product_data})
                stats["updated"] += len(product_data["variants"])
            except ShopifyAPIError as e:
                print(f"  ✗ {product['title']}: {e}")
                stats["errors"] += 1
    
    print(f"\nDone: {stats['updated']} prices updated, {stats['errors']} errors")
    return stats


def compare_prices(
    csv_file: str,
    show_differences: bool = True
) -> Dict:
    """
    比较 CSV 中的价格与 Shopify 当前价格
    
    Returns:
        差异报告
    """
    print("=" * 60)
    print("Compare Prices")
    print("=" * 60)
    
    client = ShopifyClient()
    
    # 读取 CSV
    csv_prices = {}
    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            sku = row.get('sku', '').strip()
            price = row.get('price', '').strip()
            if sku and price:
                csv_prices[sku] = float(price)
    
    print(f"\n📄 Loaded {len(csv_prices)} prices from CSV")
    
    # 获取产品
    products = client.get_products(limit=250)
    
    differences = {
        "higher": [],   # Shopify 价格更高
        "lower": [],    # Shopify 价格更低
        "same": [],     # 价格相同
        "not_found": [] # CSV 中有但 Shopify 没有
    }
    
    print("\n" + "=" * 60)
    print("Price Comparison...")
    print("=" * 60)
    
    shopify_prices = {}
    for product in products:
        for variant in product.get("variants", []):
            sku = variant.get("sku", "").strip()
            if sku:
                shopify_prices[sku] = {
                    "price": float(variant.get("price", 0)),
                    "title": f"{product['title']} - {variant.get('title', 'Default')}"
                }
    
    for sku, csv_price in csv_prices.items():
        if sku not in shopify_prices:
            differences["not_found"].append({"sku": sku, "csv_price": csv_price})
            continue
        
        shopify_price = shopify_prices[sku]["price"]
        title = shopify_prices[sku]["title"]
        
        if csv_price > shopify_price:
            diff = csv_price - shopify_price
            differences["higher"].append({
                "sku": sku,
                "title": title,
                "csv_price": csv_price,
                "shopify_price": shopify_price,
                "diff": diff
            })
        elif csv_price < shopify_price:
            diff = shopify_price - csv_price
            differences["lower"].append({
                "sku": sku,
                "title": title,
                "csv_price": csv_price,
                "shopify_price": shopify_price,
                "diff": diff
            })
        else:
            differences["same"].append({"sku": sku, "price": csv_price})
    
    # 输出报告
    print(f"\n📊 Results:")
    print(f"   Higher in Shopify: {len(differences['higher'])}")
    print(f"   Lower in Shopify:  {len(differences['lower'])}")
    print(f"   Same:              {len(differences['same'])}")
    print(f"   Not Found:         {len(differences['not_found'])}")
    
    if show_differences and differences["higher"]:
        print(f"\n⚠️ Higher in Shopify ({len(differences['higher'])}):")
        for item in differences["higher"][:5]:
            print(f"   {item['sku']}: CSV ${item['csv_price']:.2f} vs Shopify ${item['shopify_price']:.2f} (+${item['diff']:.2f})")
    
    if show_differences and differences["lower"]:
        print(f"\n✅ Lower in Shopify ({len(differences['lower'])}):")
        for item in differences["lower"][:5]:
            print(f"   {item['sku']}: CSV ${item['csv_price']:.2f} vs Shopify ${item['shopify_price']:.2f} (-${item['diff']:.2f})")
    
    return differences


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Price Management")
    parser.add_argument("--update", metavar="CSV", help="Update prices from CSV")
    parser.add_argument("--compare", metavar="CSV", help="Compare CSV prices with Shopify")
    parser.add_argument("--increase", type=float, help="Increase all prices by percentage (e.g., 1.1 for 10%)")
    parser.add_argument("--decrease", type=float, help="Decrease all prices by percentage (e.g., 0.9 for 10%)")
    
    args = parser.parse_args()
    
    if args.update:
        pct = None
        if args.increase:
            pct = args.increase
        elif args.decrease:
            pct = args.decrease
        update_prices(args.update, percentage_change=pct)
    elif args.compare:
        compare_prices(args.compare)
    else:
        parser.print_help()