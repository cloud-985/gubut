"""
采集TradingView RSS候选文章并保存到远程服务器 pending-articles.json
"""
import feedparser
import requests
import json
import time
import re
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ssh_tunnel import REMOTE_DIR, read_remote_json, write_remote_json

# TradingView RSS源 - 覆盖加密货币、黄金、外汇
RSS_FEEDS = [
    # 加密货币
    "https://www.tradingview.com/feed/?binance",
    "https://www.tradingview.com/feed/?bitcoin",
    "https://www.tradingview.com/feed/?ethereum",
    "https://www.tradingview.com/feed/?crypto",
    "https://www.tradingview.com/rss/ideas/symbol/BINANCE:BTCUSDT/",
    "https://www.tradingview.com/rss/ideas/symbol/BINANCE:ETHUSDT/",
    "https://www.tradingview.com/rss/ideas/symbol/COINBASE:BTCUSD/",
    # 黄金/大宗商品
    "https://www.tradingview.com/feed/?gold",
    "https://www.tradingview.com/feed/?xauusd",
    "https://www.tradingview.com/rss/ideas/symbol/OANDA:XAUUSD/",
    "https://www.tradingview.com/rss/ideas/symbol/TVC:GOLD/",
    # 外汇
    "https://www.tradingview.com/feed/?forex",
    "https://www.tradingview.com/feed/?eurusd",
    "https://www.tradingview.com/feed/?gbpusd",
    "https://www.tradingview.com/rss/ideas/symbol/OANDA:EURUSD/",
    "https://www.tradingview.com/rss/ideas/symbol/OANDA:GBPUSD/",
    "https://www.tradingview.com/rss/ideas/symbol/OANDA:USDJPY/",
]

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


def detect_asset(title, summary, link):
    """根据标题/摘要判断资产类型"""
    text = f"{title} {summary} {link}".lower()
    if any(k in text for k in ["btc", "bitcoin", "比特币", "xbt", "binance:btc", "coinbase:btc"]):
        return "BTC"
    if any(k in text for k in ["eth", "ethereum", "以太坊"]):
        return "ETH"
    if any(k in text for k in ["xau", "gold", "黄金", "tvc:gold", "xauusd"]):
        return "XAUUSD"
    if any(k in text for k in ["eurusd", "eur/usd", "欧元"]):
        return "EURUSD"
    if any(k in text for k in ["gbpusd", "gbp/usd", "英镑"]):
        return "GBPUSD"
    if any(k in text for k in ["usdjpy", "usd/jpy", "日元"]):
        return "USDJPY"
    if any(k in text for k in ["crypto", "加密", "币", "sol", "solana", "altcoin", "山寨"]):
        return "CRYPTO"
    if any(k in text for k in ["forex", "外汇", "fx "]):
        return "FOREX"
    return "OTHER"


def fetch_rss_entries(feed_url):
    """抓取单个RSS源"""
    print(f"  抓取: {feed_url[:80]}...")
    entries = []
    try:
        headers = {"User-Agent": USER_AGENT}
        # 使用requests获取内容，feedparser解析
        resp = requests.get(feed_url, headers=headers, timeout=30)
        resp.raise_for_status()
        d = feedparser.parse(resp.content)
        for e in d.entries[:15]:
            title = getattr(e, "title", "").strip()
            link = getattr(e, "link", "").strip()
            summary = getattr(e, "summary", getattr(e, "description", "")).strip()
            published = getattr(e, "published", "")
            # 提取纯文本摘要
            if summary:
                soup = BeautifulSoup(summary, "html.parser")
                summary_text = soup.get_text(separator=" ", strip=True)
            else:
                summary_text = ""
            if not title or not link:
                continue
            entries.append({
                "title": title,
                "link": link,
                "summary": summary_text[:1500],
                "published": published,
                "asset": detect_asset(title, summary_text, link),
                "source_feed": feed_url,
                "collected_at": datetime.now(timezone.utc).isoformat()
            })
    except Exception as ex:
        print(f"  [ERR] {feed_url[:60]} -> {type(ex).__name__}: {str(ex)[:120]}")
    return entries


def fetch_full_content(url):
    """尝试获取文章完整内容"""
    try:
        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
        }
        resp = requests.get(url, headers=headers, timeout=45)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # 移除脚本和样式
        for tag in soup(["script", "style", "noscript", "iframe", "nav", "header", "footer", "aside"]):
            tag.decompose()

        # TradingView文章内容
        candidates = []
        for sel in [
            "article",
            ".js-idea-content",
            ".tv-chart-view-count",
            "[data-role='idea-content']",
            ".tv-feed-post",
            ".content",
            ".article-content",
            "main"
        ]:
            el = soup.select_one(sel)
            if el:
                candidates.append(el)

        if candidates:
            # 取文本最长的
            candidates.sort(key=lambda c: len(c.get_text(strip=True)), reverse=True)
            text = candidates[0].get_text(separator="\n", strip=True)
            if len(text) > 300:
                return text[:8000]

        # 回退：取body中的长文本段落
        paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
        long_p = [p for p in paragraphs if len(p) > 100]
        if long_p:
            return "\n".join(long_p)[:8000]

        return ""
    except Exception as ex:
        print(f"  [WARN] 获取正文失败 {url[:60]}: {str(ex)[:100]}")
        return ""


def main():
    print(f"[{datetime.now()}] 开始采集 TradingView RSS...")
    all_entries = []
    seen_links = set()

    # 读取现有pending，避免重复
    remote_path = f"{REMOTE_DIR}/pending-articles.json"
    try:
        existing = read_remote_json(remote_path)
    except Exception:
        existing = []
    existing_links = {a.get("link") for a in existing if a.get("link")}
    print(f"现有 pending 文章数: {len(existing)}")

    for feed in RSS_FEEDS:
        entries = fetch_rss_entries(feed)
        for e in entries:
            if e["link"] in seen_links or e["link"] in existing_links:
                continue
            seen_links.add(e["link"])
            all_entries.append(e)
        time.sleep(0.5)

    print(f"从RSS获取到 {len(all_entries)} 篇新候选")

    # 获取前12篇全文
    enriched = []
    for i, e in enumerate(all_entries[:12]):
        print(f"  抓取正文 ({i+1}/{min(len(all_entries),12)}): {e['title'][:60]}")
        content = fetch_full_content(e["link"])
        e["full_content"] = content
        # 信息密度评分：摘要+全文长度
        score = len(e.get("summary", "")) + len(content)
        e["_score"] = score
        enriched.append(e)
        time.sleep(1)

    # 与现有pending合并（新的在前面）
    merged = enriched + existing
    # 去重（按link）
    seen = set()
    dedup = []
    for a in merged:
        lk = a.get("link", "")
        if not lk or lk in seen:
            continue
        seen.add(lk)
        dedup.append(a)

    # 最多保留40篇
    dedup = dedup[:40]
    print(f"写入 pending-articles.json: 共 {len(dedup)} 篇 (新增 {len(enriched)})")
    write_remote_json(remote_path, dedup)
    print(f"[{datetime.now()}] 采集完成")


if __name__ == "__main__":
    main()
