#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Mongolian Coal Auction Data Fetcher (comex.mse.mn)
蒙古矿产交易所拍卖实时看板数据接口
"""

import os
import sys
import json
import ssl
import argparse
import urllib.request
from datetime import datetime

API_URL = "https://comex.mse.mn/getdashboardtable"
REFERER_URL = "https://comex.mse.mn/home"

def fetch_raw_data():
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Referer": REFERER_URL,
        "X-Requested-With": "XMLHttpRequest"
    }

    req = urllib.request.Request(API_URL, headers=headers)
    ctx = ssl.create_default_context()

    try:
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            raw_content = resp.read().decode("utf-8")
            return json.loads(raw_content)
    except Exception as e:
        print(f"[错误] 请求 comex.mse.mn 失败: {e}", file=sys.stderr)
        return None

def format_status(status_code, order_price=None):
    if status_code == 3 and (order_price is None or order_price == "" or order_price == 0):
        return "流拍"
    status_map = {
        1: "尚未开始",
        2: "正在竞价",
        3: "已结束",
        4: "流拍"
    }
    return status_map.get(status_code, f"状态 {status_code}")

def get_today_auctions(target_date=None):
    """
    获取指定日期（默认当天）的拍卖看板数据列表
    """
    if not target_date:
        target_date = datetime.now().strftime("%Y-%m-%d")

    data = fetch_raw_data()
    if not data:
        return []

    all_items = data.get("tableData", [])
    filtered = [
        item for item in all_items
        if item.get("auctionStartTime", "").startswith(target_date)
    ]
    return filtered

def print_table(target_date, items):
    print("\n" + "=" * 125)
    print(f"  蒙古煤炭及矿产在线拍卖实时看板 (comex.mse.mn)  |  筛选日期: {target_date}")
    print("=" * 125)
    
    if not items:
        print(f"  当前日期 ({target_date}) 暂无进行中或待开始的拍卖项目。")
        print("=" * 125)
        return

    header = f"{'时间':<10} | {'产品':<8} | {'状态':<10} | {'卖方':<24} | {'底价':<14} | {'成交价':<12} | {'规格 (包/吨)':<18} | {'详情链接'}"
    print(header)
    print("-" * 125)

    for row in items:
        start_time = row.get("auctionStartTime", "").split(" ")[-1][:5] if " " in row.get("auctionStartTime", "") else row.get("auctionStartTime", "")
        product = row.get("productTypeNameCN") or row.get("productTypeNameEN") or "煤炭"
        order_price = row.get("orderPrice")
        status_code = row.get("auctionStatus")
        status = format_status(status_code, order_price)
        seller = row.get("sellerNameCN") or row.get("sellerNameMN") or "-"
        price = f"{row.get('productPrice', '')} {row.get('currency', '')}"
        if order_price:
            deal_price = f"{order_price} {row.get('currency', '')}"
        elif status == "流拍":
            deal_price = "流拍"
        else:
            deal_price = "-"
        lots = f"{row.get('size', 0)}包 ({float(row.get('lot_price', 0)):,.0f}吨/包)"
        detail_url = f"https://comex.mse.mn/multi/auctions/single/{row.get('auctionId')}"
        
        print(f"{start_time:<10} | {product:<8} | {status:<10} | {seller:<24} | {price:<14} | {deal_price:<12} | {lots:<18} | {detail_url}")

    print("=" * 125 + "\n")

def main():
    today_str = datetime.now().strftime("%Y-%m-%d")
    parser = argparse.ArgumentParser(description="获取 comex.mse.mn 实时拍卖数据")
    parser.add_argument("--date", type=str, default=today_str, help=f"目标日期 (默认今天: {today_str})")
    args = parser.parse_args()

    items = get_today_auctions(args.date)
    print_table(args.date, items)

if __name__ == "__main__":
    main()
