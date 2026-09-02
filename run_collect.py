#!/usr/bin/env python3
"""Collect TradingView RSS candidate articles and save to remote pending-articles.json.

Fetches public TradingView RSS feeds (multiple popular symbols / markets),
deduplicates by link, sorts by pubDate (newest first), and uploads
to /www/wwwroot/gubut/pending-articles.json on the remote server.
"""
import json
import re
import sys
from datetime import datetime
from email.utils import parsedate_to_datetime

import feedparser
import requests

import ssh_tunnel

REMOTE_PATH = f"{ssh_tunnel.REMOTE_ROOT}/pending-articles.json"

# A mix of TradingView RSS feeds covering the three target asset classes:
# BTC / 黄金(XAUUSD) / 外汇 (GBPUSD, EURUSD etc.)
FEEDS = [
    # Crypto (BTC-centric)
    "https://www.tradingview.com/feed/?symbol=BITSTAMP%3ABTCUSD",
    "https://www.tradingview.com/feed/?symbol=BINANCE%3ABTCUSDT",
    "https://www.tradingview.com/feed/?symbol=COINBASE%3ABTCUSD",
    # Gold / XAUUSD
    "https://www.tradingview.com/feed/?symbol=OANDA%3AXAUUSD",
    "https://www.tradingview.com/feed/?symbol=TVC%3AGOLD",
    # Forex majors
    "https://www.tradingview.com/feed/?symbol=OANDA%3AGBPUSD",
    "https://www.tradingview.com/feed/?symbol=FX%3AEURUSD",
    "https://www.tradingview.com/feed/?symbol=OANDA%3AUSDJPY",
    # General ideas RSS
    "https://www.tradingview.com/feed/rss/",
]


def fetch_one(url, timeout=20):
    """Parse one RSS feed and return list of normalized entries."""
    try:
        # TradingView sometimes requires a reasonable user-agent
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (compatible; GubutCollector/1.0; "
                "+https://www.gubut.com)"
            ),
            "Accept": "application/rss+xml, application/xml, text/xml",
        }
        r = requests.get(url, headers=headers, timeout=timeout)
        r.raise_for_status()
        feed = feedparser.parse(r.content)
    except Exception as e:
        print(f"   ⚠️  抓取失败 {url[:80]}...: {e}")
        return []

    entries = []
    for e in feed.entries:
        title = (e.get("title") or "").strip()
        link = (e.get("link") or "").strip()
        desc = (e.get("description") or "").strip()
        pub = e.get("published") or e.get("updated") or ""

        if not link:
            continue

        # Try to parse date for sorting
        ts = 0
        try:
            dt = parsedate_to_datetime(pub) if pub else None
            if dt:
                ts = int(dt.timestamp())
        except Exception:
            pass

        entries.append(
            {
                "title": title,
                "link": link,
                "description": desc,
                "pubDate": pub,
                "_ts": ts,
            }
        )
    return entries


def dedupe(entries):
    seen = set()
    out = []
    for e in entries:
        key = e["link"]
        if key in seen:
            continue
        seen.add(key)
        out.append(e)
    return out


def main():
    print("📡 开始采集 TradingView RSS 候选文章...")
    all_entries = []
    for f in FEEDS:
        print(f"   → {f[:90]}")
        got = fetch_one(f)
        print(f"     ✓ 获取 {len(got)} 条")
        all_entries.extend(got)

    # Dedupe + sort
    all_entries = dedupe(all_entries)
    all_entries.sort(key=lambda e: e["_ts"], reverse=True)

    # Drop internal sort key from final output
    for e in all_entries:
        e.pop("_ts", None)

    print(f"📦 去重后共 {len(all_entries)} 条候选")

    if not all_entries:
        print("❌ 0条候选，中止上传")
        sys.exit(1)

    # Save locally + upload to remote
    local_path = "/workspace/pending-articles.json"
    with open(local_path, "w", encoding="utf-8") as f:
        json.dump(all_entries, f, ensure_ascii=False, indent=2)

    print("🚀 上传到远程服务器 pending-articles.json ...")
    ssh_tunnel.upload_file(local_path, REMOTE_PATH)
    ssh_tunnel.run_remote(
        f"chown www:www {REMOTE_PATH} && chmod 644 {REMOTE_PATH}"
    )
    print(f"✅ 完成，已上传 {len(all_entries)} 条候选到 {REMOTE_PATH}")


if __name__ == "__main__":
    main()
