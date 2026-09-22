#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Mongolian Mineral/Coal Auction Notices Fetcher (comex.mse.mn/show-notices)
蒙古矿产品/煤炭拍卖通告详细清单采集接口
"""

import os
import sys
import json
import argparse
from datetime import datetime
import requests
from bs4 import BeautifulSoup

NOTICES_URL = "https://comex.mse.mn/show-notices"
LANG_SWITCH_URL = "https://comex.mse.mn/home_/ch"

def get_session():
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": NOTICES_URL
    })
    try:
        session.get(LANG_SWITCH_URL, timeout=10)
    except Exception as e:
        print(f"[提示] 切换中文语言失败: {e}", file=sys.stderr)
    return session

def get_today_notices(target_date=None, product="", seller="", is_changed="", page=1):
    """
    获取指定日期（默认当天）的拍卖通告详细清单列表
    """
    session = get_session()
    
    if not target_date:
        target_date = datetime.now().strftime("%Y-%m-%d")
        
    params = {
        "start_date": target_date,
        "end_date": target_date,
        "product": product,
        "seller": seller,
        "isChangedPrice": is_changed,
        "page": page
    }

    try:
        resp = session.get(NOTICES_URL, params=params, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print(f"[错误] 请求通告失败: {e}", file=sys.stderr)
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    table = soup.find("table", class_="table")
    if not table:
        return []

    tbody = table.find("tbody")
    if not tbody:
        return []

    rows = []
    for tr in tbody.find_all("tr"):
        tds = tr.find_all(["td", "th"])
        if len(tds) < 11:
            continue
        
        row_num = tds[0].get_text(strip=True)
        product_name = tds[1].get_text(strip=True)
        product_type = tds[2].get_text(strip=True)
        seller_name = tds[3].get_text(strip=True)
        date_time = tds[4].get_text(strip=True)
        quantity = tds[5].get_text(strip=True)
        floor_price = tds[6].get_text(strip=True)
        price_type = tds[7].get_text(strip=True)
        order_number = tds[8].get_text(strip=True)

        lab_report_link = None
        lab_a = tds[9].find("a")
        if lab_a and lab_a.get("href"):
            lab_report_link = lab_a.get("href")

        detail_info_link = None
        detail_a = tds[10].find("a")
        if detail_a and detail_a.get("href"):
            detail_info_link = detail_a.get("href")

        rows.append({
            "no": row_num,
            "product": product_name,
            "productType": product_type,
            "seller": seller_name,
            "datetime": date_time,
            "quantity": quantity,
            "floorPrice": floor_price,
            "priceType": price_type,
            "orderNumber": order_number,
            "labReportUrl": lab_report_link,
            "detailInfoUrl": detail_info_link
        })

    return rows

def print_notices_table(target_date, records):
    print("\n" + "=" * 135)
    print(f"  蒙古矿产/煤炭拍卖通告参与清单 (comex.mse.mn/show-notices)  |  筛选日期: {target_date}  |  共 {len(records)} 条记录")
    print("=" * 135)

    if not records:
        print(f"  当前日期 ({target_date}) 暂无拍卖通告记录。")
        print("=" * 135)
        return

    header = f"{'序号':<4} | {'产品':<6} | {'产品类型':<16} | {'卖方':<22} | {'拍卖时间':<19} | {'数量':<18} | {'最低价':<8} | {'订单号':<14} | {'化验报告'}"
    print(header)
    print("-" * 135)

    for r in records:
        print(f"{r['no']:<4} | {r['product']:<6} | {r['productType']:<16} | {r['seller']:<22} | {r['datetime']:<19} | {r['quantity']:<18} | {r['floorPrice']:<8} | {r['orderNumber']:<14} | {r['labReportUrl'] or '-'}")

    print("=" * 135 + "\n")

def main():
    today_str = datetime.now().strftime("%Y-%m-%d")
    parser = argparse.ArgumentParser(description="获取 comex.mse.mn 拍卖通告详细清单")
    parser.add_argument("--date", type=str, default=today_str, help=f"查询日期 (默认今天: {today_str})")
    args = parser.parse_args()

    records = get_today_notices(target_date=args.date)
    print_notices_table(args.date, records)

if __name__ == "__main__":
    main()
