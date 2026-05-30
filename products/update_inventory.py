"""
库存同步模块
"""

import sys
import csv
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).parent.parent))

from src import ShopifyClient
from src.api_client import ShopifyAPIError


def update_inventory(
    csv_file: str = None,
    sku_quantities: Dict[str, int] = None
) -> Dict:
    """
    更新库存数量
    
    Args:
        csv_file: CSV 文件路径（需包含 sku 和 quantity 列）
        sku_quantities: SKU 到数量的字典（直接指定）
    
    Returns:
        更新统计
    """
    print("=" * 60)
    print("Update Inventory")
    print("=" * 60)
    
    client = ShopifyClient()
    
    # 收集 SKU 和数量
    updates = {}
    
    if csv_file:
        print(f"\n📄 Reading from: {csv_file}")
        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                sku = row.get('sku', '').strip()
                qty = row.get('quantity', '').strip()
                if sku and qty:
                    updates[sku] = int(qty)
        print(f"   Found {len(updates)} inventory updates")
    
    if sku_quantities:
        updates.update(sku_quantities)
        print(f"   Added {len(sku_quantities)} manual updates")
    
    if not updates:
        print("No inventory updates to process")
        return {"updated": 0}
    
    # 获取所有产品
    print("\n📊 Fetching products...")
    products = client.get_products(limit=250)
    print(f"   Found {len(products)} products")
    
    stats = {"updated": 0, "errors": 0}
    
    print("\n" + "=" * 60)
    print("Updating Inventory...")
    print("=" * 60)
    
    for product in products:
        for variant in product.get("variants", []):
            sku = variant.get("sku", "").strip()
            if sku in updates:
                inventory_item_id = variant.get("inventory_item_id")
                if not inventory_item_id:
                    continue
                
                new_qty = updates[sku]
                try:
                    # 更新库存
                    endpoint = f"inventory_levels/set.json"
                    data = {
                        "location_id": "current",  # 需要先获取正确的 location_id
                        "inventory_item_id": inventory_item_id,
                        "available": new_qty
                    }
                    client._request("POST", endpoint, data)
                    print(f"  ✓ {sku}: {new_qty}")
                    stats["updated"] += 1
                except ShopifyAPIError as e:
                    print(f"  ✗ {sku}: {e}")
                    stats["errors"] += 1
    
    print(f"\nDone: {stats['updated']} updated, {stats['errors']} errors")
    return stats


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Update inventory")
    parser.add_argument("--csv", help="CSV file with SKU and quantity columns")
    
    args = parser.parse_args()
    
    update_inventory(csv_file=args.csv)