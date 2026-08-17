"""采集 TradingView RSS 候选文章，写入服务器 /www/wwwroot/gubut/pending-articles.json。

策略:
- 抓取 https://www.tradingview.com/feed/ (走 HTTP 代理)
- 只保留标题或描述中包含资产关键词 (BTC/ETH/XAUUSD/GOLD/EURUSD/GBPUSD/USDJPY 等)
  且包含策略关键词 (support/resistance/breakout/long/short 等) 的条目
- 去重: 过滤掉已经出现在服务器 pending-articles.json 或 .published-articles.json 里的链接
- 写回服务器 pending-articles.json
"""
import json
import re
import sys
import feedparser
import requests

from ssh_tunnel import ssh_tunnel, REMOTE_ROOT

RSS_URL = "https://www.tradingview.com/feed/"
PENDING_REMOTE = f"{REMOTE_ROOT}/pending-articles.json"
PUBLISHED_LOG_REMOTE = f"{REMOTE_ROOT}/.published-articles.json"

ASSET_KEYWORDS = [
    "BTC", "BITCOIN", "ETH", "ETHEREUM", "XAUUSD", "GOLD",
    "NEAR", "SOL", "XRP", "BNB", "DOGE", "ADA", "AVAX", "LINK",
    "USDT", "EURUSD", "GBPUSD", "USDJPY", "CRYPTO",
]
STRATEGY_KEYWORDS = [
    "SCALPING", "GRID", "BREAKOUT", "SUPPORT", "RESISTANCE",
    "FIBONACCI", "RSI", "MACD", "MT5", "EA", "FOREX", "ALTCOIN",
    "LONG", "SHORT", "BUY", "SELL", "TREND", "PIPS", "ANALYSIS",
]


def fetch_rss():
    """通过 HTTP 代理抓取 RSS feed。"""
    proxies = {
        "http": "http://127.0.0.1:18080",
        "https": "http://127.0.0.1:18080",
    }
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    resp = requests.get(RSS_URL, headers=headers, proxies=proxies, timeout=30)
    resp.raise_for_status()
    return resp.text


def parse_items(xml_text):
    """从 RSS XML 中解析条目。"""
    feed = feedparser.parse(xml_text)
    items = []
    for e in feed.entries:
        title = (e.get("title") or "").strip()
        link = (e.get("link") or "").strip()
        description = (e.get("summary") or e.get("description") or "").strip()
        pub_date = (e.get("published") or e.get("updated") or "").strip()
        if not title or not link:
            continue
        items.append({
            "title": title,
            "link": link,
            "description": description,
            "pubDate": pub_date,
        })
    return items


def is_relevant(item):
    text = (item["title"] + " " + item["description"]).upper()
    has_asset = any(k in text for k in ASSET_KEYWORDS)
    has_strategy = any(k in text for k in STRATEGY_KEYWORDS)
    return has_asset and has_strategy


def strip_html(s):
    return re.sub(r"<[^>]+>", " ", s or "").replace("&nbsp;", " ")


def dedup(new_items, known_links):
    out = []
    seen = set()
    for it in new_items:
        if it["link"] in known_links or it["link"] in seen:
            continue
        seen.add(it["link"])
        out.append(it)
    return out


def main():
    print("[1/5] 抓取 TradingView RSS...")
    try:
        xml = fetch_rss()
        print(f"  RSS 长度: {len(xml)} 字节")
    except Exception as e:
        print(f"  RSS 抓取失败: {e}")
        print("  → 将仅使用服务器现有 pending-articles.json")
        xml = None

    print("[2/5] 读取服务器现有 pending & published 列表...")
    try:
        pending_raw = ssh_tunnel.read_remote(PENDING_REMOTE)
        existing_pending = json.loads(pending_raw) if pending_raw.strip() else []
    except Exception as e:
        print(f"  读取 pending 失败: {e}")
        existing_pending = []
    try:
        published_raw = ssh_tunnel.read_remote(PUBLISHED_LOG_REMOTE)
        published_list = json.loads(published_raw) if published_raw.strip() else []
    except Exception:
        published_list = []

    known_links = set()
    for it in existing_pending:
        known_links.add(it.get("link", ""))
    for it in published_list:
        # published-articles.json 中可能是字符串或对象
        if isinstance(it, dict):
            known_links.add(it.get("link", "") or it.get("source", ""))
        elif isinstance(it, str):
            known_links.add(it)
    print(f"  已知链接数: {len(known_links)} (pending={len(existing_pending)}, published={len(published_list)})")

    if xml:
        print("[3/5] 解析 & 过滤 RSS 条目...")
        all_items = parse_items(xml)
        print(f"  RSS 总条目: {len(all_items)}")
        relevant = [it for it in all_items if is_relevant(it)]
        print(f"  与交易策略相关条目: {len(relevant)}")
        # 清洗 description
        for it in relevant:
            it["description"] = strip_html(it["description"])[:1500]
        fresh = dedup(relevant, known_links)
        print(f"  去重后新条目: {len(fresh)}")
        merged = fresh + existing_pending
        # 限制总数到 30 条
        merged = merged[:30]
    else:
        print("[3/5] 跳过 RSS 解析 (RSS 抓取失败)")
        merged = existing_pending

    print(f"[4/5] 写回服务器 pending-articles.json (共 {len(merged)} 条)...")
    ssh_tunnel.write_remote(PENDING_REMOTE, json.dumps(merged, ensure_ascii=False, indent=2))
    print("  写入完成")

    print("[5/5] 输出前 8 条:")
    for i, it in enumerate(merged[:8]):
        title = it.get("title", "")[:80]
        pub = it.get("pubDate", "")[:16]
        print(f"  {i:2d}. [{pub}] {title}")
    print(f"\n候选总数: {len(merged)}")
    if len(merged) == 0:
        print("0 篇候选，跳过当日发布。")
        sys.exit(2)


if __name__ == "__main__":
    main()
