"""采集 TradingView 加密货币 & 外汇 RSS 文章，补充到服务器 pending-articles.json"""
import sys
import os
import json
import time
import hashlib
import feedparser
import requests
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ssh_tunnel import run_remote, read_remote_file, write_remote_file, REMOTE_BASE

# TradingView Idea 频道 RSS（BTC、ETH、黄金、外汇、MT5 相关）
RSS_FEEDS = [
    # 加密货币
    "https://www.tradingview.com/rss/ideas/?symbol=BINANCE:BTCUSDT",
    "https://www.tradingview.com/rss/ideas/?symbol=BINANCE:ETHUSDT",
    "https://www.tradingview.com/rss/ideas/?symbol=COINBASE:SOLUSD",
    # 黄金 / 商品
    "https://www.tradingview.com/rss/ideas/?symbol=TVC:GOLD",
    "https://www.tradingview.com/rss/ideas/?symbol=COMEX:GC1!",
    # 外汇
    "https://www.tradingview.com/rss/ideas/?symbol=FX:EURUSD",
    "https://www.tradingview.com/rss/ideas/?symbol=FX:GBPUSD",
    "https://www.tradingview.com/rss/ideas/?symbol=FX:USDJPY",
    "https://www.tradingview.com/rss/ideas/?symbol=FX:XAUUSD",
    # 指数
    "https://www.tradingview.com/rss/ideas/?symbol=TVC:US100",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/125.0 Safari/537.36"
}

KEYWORD_BLOCKLIST = [
    "advertisement", "promotion", "giveaway", "airdrop", "scam",
    "注册送", "免费领", "零撸",
]


def extract_full_content(entry):
    """从 entry 中提取尽可能完整的正文"""
    # TradingView RSS 的 content 可能在 summary / content / description 里
    text = ""
    if hasattr(entry, "content") and entry.content:
        text = entry.content[0].get("value", "") if isinstance(entry.content, list) else str(entry.content)
    if not text:
        text = entry.get("summary", "") or entry.get("description", "") or ""
    # 去除 HTML 标签，保留纯文本粗估长度（用于判断信息密度）
    import re
    plain = re.sub(r"<[^>]+>", " ", text)
    plain = re.sub(r"\s+", " ", plain).strip()
    return text, plain


def is_relevant(title, plain):
    """粗略过滤：只保留加密/黄金/外汇交易策略相关"""
    blob = (title + " " + plain[:300]).lower()
    keywords = [
        "btc", "bitcoin", "eth", "ethereum", "crypto", "加密", "币",
        "gold", "黄金", "xauusd", "gc", "metal",
        "eurusd", "gbpusd", "usdjpy", "forex", "外汇", "dollar",
        "strategy", "策略", "signal", "指标", "ea", "expert advisor",
        "grid", "martingale", "scalp", "swing", "position", "交易",
        "support", "resistance", "关键位",
    ]
    score = sum(1 for k in keywords if k in blob)
    blocked = any(b in blob for b in KEYWORD_BLOCKLIST)
    return score >= 1 and not blocked


def fetch_rss(url, timeout=15):
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        if r.status_code != 200:
            print(f"  [WARN] HTTP {r.status_code} from {url}")
            return []
        feed = feedparser.parse(r.content)
        return feed.entries
    except Exception as e:
        print(f"  [ERR] {url}: {e}")
        return []


def load_pending():
    path = f"{REMOTE_BASE}/pending-articles.json"
    raw = run_remote(f"test -f {path} && cat {path} || echo '[]'")
    try:
        return json.loads(raw.strip() or "[]")
    except json.JSONDecodeError:
        print("[WARN] pending-articles.json corrupt, resetting")
        return []


def load_published_ids():
    """从服务器 articles.json 加载已发布 id 集合"""
    path = f"{REMOTE_BASE}/articles.json"
    raw = run_remote(f"test -f {path} && cat {path} || echo '[]'")
    try:
        arr = json.loads(raw.strip() or "[]")
        return {a.get("source_id") or str(a.get("title", "")) for a in arr}
    except Exception:
        return set()


def main():
    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] 开始采集 TradingView RSS ...")
    pending = load_pending()
    published_keys = load_published_ids()
    existing_ids = {a.get("id") for a in pending}

    new_count = 0
    for feed_url in RSS_FEEDS:
        print(f"\n→ {feed_url}")
        entries = fetch_rss(feed_url)
        print(f"   获取到 {len(entries)} 条")
        for entry in entries[:20]:  # 每个 feed 取最新 20 条
            title = entry.get("title", "").strip()
            link = entry.get("link", "")
            if not title or not link:
                continue
            text_html, plain = extract_full_content(entry)
            if not is_relevant(title, plain):
                continue

            fid = hashlib.md5(link.encode()).hexdigest()
            if fid in existing_ids or fid in published_keys:
                continue

            item = {
                "id": fid,
                "source": "tradingview",
                "title": title,
                "url": link,
                "published": entry.get("published", ""),
                "summary": entry.get("summary", ""),
                "content_html": text_html,
                "plain_text_length": len(plain),
                "collected_at": int(time.time() * 1000),
            }
            pending.append(item)
            existing_ids.add(fid)
            new_count += 1
            print(f"   + {title[:70]}")

    # 保留最新 200 条，按 collected_at 降序
    pending.sort(key=lambda x: x.get("collected_at", 0), reverse=True)
    pending = pending[:200]

    # 写回服务器
    remote_path = f"{REMOTE_BASE}/pending-articles.json"
    write_remote_file(remote_path, json.dumps(pending, ensure_ascii=False, indent=2))
    print(f"\n[{datetime.now():%H:%M:%S}] 采集完成：新增 {new_count} 条，待处理总数 {len(pending)}")


if __name__ == "__main__":
    main()
