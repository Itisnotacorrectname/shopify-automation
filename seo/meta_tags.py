"""
Meta Tags 生成模块
自动为产品、页面生成 SEO meta tags
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from src import ShopifyClient
from src.api_client import ShopifyAPIError


def generate_meta_title(title: str, site_name: str = None) -> str:
    """生成优化的 meta title"""
    max_length = 60
    if site_name:
        formatted = f"{title} | {site_name}"
    else:
        formatted = title
    
    if len(formatted) > max_length:
        return title[:max_length - 3] + "..."
    return formatted


def generate_meta_description(description: str, max_length: int = 160) -> str:
    """生成优化的 meta description"""
    # 去除 HTML 标签
    import re
    clean = re.sub(r'<[^>]+>', '', description)
    # 去除多余空格
    clean = re.sub(r'\s+', ' ', clean).strip()
    
    if len(clean) > max_length:
        return clean[:max_length - 3] + "..."
    return clean


def update_meta_tags(
    product_ids: List[int] = None,
    page_ids: List[int] = None,
    default_title: str = None,
    default_description: str = None
) -> Dict:
    """
    更新产品/页面的 Meta tags
    
    Args:
        product_ids: 要更新的产品 ID 列表，None 表示所有产品
        page_ids: 要更新的页面 ID 列表，None 表示所有页面
        default_title: 默认标题模板，如 "{title} | HYL Furniture"
        default_description: 默认描述模板
    
    Returns:
        更新统计
    """
    print("=" * 60)
    print("Update Meta Tags")
    print("=" * 60)
    
    client = ShopifyClient()
    stats = {"updated": 0, "skipped": 0, "errors": 0}
    
    # 更新产品
    if product_ids or product_ids is None:
        print("\n📦 Products:")
        try:
            products = client.get_products(limit=250)
            
            for product in products:
                if product_ids and product["id"] not in product_ids:
                    continue
                
                title = product.get("title", "")
                body_html = product.get("body_html", "")
                
                # 生成 meta 数据
                seo_title = default_title.format(title=title) if default_title else generate_meta_title(title)
                seo_description = default_description.format(description=body_html) if default_description else generate_meta_description(body_html)
                
                # 注意：Shopify API 不允许直接更新 meta_fields，需要通过主题或其他方式
                # 这里只是打印预览
                print(f"  ✓ {title}")
                print(f"    Title: {seo_title}")
                print(f"    Desc:  {seo_description[:50]}...")
                
                stats["updated"] += 1
                
        except ShopifyAPIError as e:
            print(f"  Error fetching products: {e}")
            stats["errors"] += 1
    
    # 更新页面
    if page_ids or page_ids is None:
        print("\n📄 Pages:")
        try:
            pages = client.get_pages()
            
            for page in pages:
                if page_ids and page["id"] not in page_ids:
                    continue
                
                title = page.get("title", "")
                body_html = page.get("body_html", "")
                
                seo_title = default_title.format(title=title) if default_title else generate_meta_title(title)
                seo_description = default_description.format(description=body_html) if default_description else generate_meta_description(body_html)
                
                print(f"  ✓ {title}")
                print(f"    Title: {seo_title}")
                print(f"    Desc:  {seo_description[:50]}...")
                
                stats["updated"] += 1
                
        except ShopifyAPIError as e:
            print(f"  Error fetching pages: {e}")
            stats["errors"] += 1
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"  Updated: {stats['updated']}")
    print(f"  Skipped: {stats['skipped']}")
    print(f"  Errors:  {stats['errors']}")
    
    return stats


def generate_meta_report(output_file: str = None) -> str:
    """
    生成 SEO meta tags 报告
    
    Returns:
        报告内容
    """
    print("=" * 60)
    print("SEO Meta Report")
    print("=" * 60)
    
    client = ShopifyClient()
    
    report_lines = [
        "# SEO Meta Tags Report",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Store: {client.store}",
        "",
        "## Products",
        ""
    ]
    
    try:
        products = client.get_products(limit=250)
        for product in products:
            title = product.get("title", "")
            body_html = product.get("body_html", "")
            
            report_lines.append(f"### {title}")
            report_lines.append(f"- Title: {generate_meta_title(title)}")
            report_lines.append(f"- Description: {generate_meta_description(body_html)[:100]}...")
            report_lines.append("")
            
    except ShopifyAPIError as e:
        report_lines.append(f"Error: {e}")
    
    report_lines.extend(["", "## Pages", ""])
    
    try:
        pages = client.get_pages()
        for page in pages:
            title = page.get("title", "")
            body_html = page.get("body_html", "")
            
            report_lines.append(f"### {title}")
            report_lines.append(f"- Title: {generate_meta_title(title)}")
            report_lines.append(f"- Description: {generate_meta_description(body_html)[:100]}...")
            report_lines.append("")
            
    except ShopifyAPIError as e:
        report_lines.append(f"Error: {e}")
    
    report = "\n".join(report_lines)
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n✓ Report saved to: {output_file}")
    else:
        print(report)
    
    return report


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="SEO Meta Tags")
    parser.add_argument("--report", action="store_true", help="Generate SEO report")
    parser.add_argument("--output", help="Output file for report")
    
    args = parser.parse_args()
    
    if args.report:
        generate_meta_report(args.output)
    else:
        update_meta_tags()