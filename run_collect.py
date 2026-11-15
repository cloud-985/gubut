"""采集 TradingView RSS 候选文章并写入服务器 pending-articles.json。"""
import json
import re
import sys
import ssh_tunnel

RSS_URL = "https://www.tradingview.com/feed/"
REMOTE_PENDING = "/www/wwwroot/gubut/pending-articles.json"
LOCAL_TMP = "/tmp/pending-articles.json"

# 资产关键词：用于粗筛(与服务器 auto-publish.js 保持一致)
ASSET_KEYWORDS = [
    "BTC", "BITCOIN", "ETH", "ETHEREUM", "XAUUSD", "GOLD", "NEAR", "SOL",
    "XRP", "BNB", "DOGE", "ADA", "AVAX", "LINK", "USDT", "EURUSD", "GBPUSD",
    "USDJPY", "CRYPTO",
]


def strip_html(html):
    return re.sub(r"<[^>]+>", " ", html).replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")


def parse_rss(xml):
    items = []
    for m in re.finditer(r"<item>([\s\S]*?)</item>", xml):
        block = m.group(1)
        title = re.search(r"<title>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>", block)
        link = re.search(r"<link>(.*?)</link>", block)
        desc = re.search(r"<description>(?:<!\[CDATA\[)?([\s\S]*?)(?:\]\]>)?</description>", block)
        pub = re.search(r"<pubDate>(.*?)</pubDate>", block)
        items.append({
            "title": strip_html(title.group(1)).strip() if title else "",
            "link": (link.group(1) or "").strip() if link else "",
            "description": strip_html(desc.group(1)).strip() if desc else "",
            "pubDate": (pub.group(1) or "").strip() if pub else "",
        })
    return items


def filter_relevant(items):
    out = []
    for it in items:
        text = (it["title"] + " " + it["description"]).upper()
        if any(re.search(r"\b" + re.escape(k) + r"\b", text) for k in ASSET_KEYWORDS):
            out.append(it)
    return out


def main():
    print("[采集] 通过服务器抓取 TradingView RSS ...")
    # 服务器有直连外网能力，用 curl 抓取，避免沙箱代理对 tradingview.com 的限制
    out, err, rc = ssh_tunnel.run_remote(f'curl -sS --max-time 60 "{RSS_URL}"', timeout=120)
    if rc != 0 or not out.strip():
        print("[ERR] RSS 抓取失败:", (err or "空响应").strip()[:500])
        sys.exit(1)
    items = parse_rss(out)
    print(f"[OK] 解析到 {len(items)} 条原始条目")
    relevant = filter_relevant(items)
    print(f"[OK] 过滤后 {len(relevant)} 条候选")
    if not relevant:
        print("[WARN] 无候选文章")
        sys.exit(0)

    with open(LOCAL_TMP, "w", encoding="utf-8") as f:
        json.dump(relevant, f, ensure_ascii=False, indent=2)

    _, err, rc = ssh_tunnel.upload(LOCAL_TMP, REMOTE_PENDING)
    if rc != 0:
        print("[ERR] 上传 pending-articles.json 失败:", err.strip()[:500])
        sys.exit(2)
    print(f"[OK] 已写入 {REMOTE_PENDING} ({len(relevant)} 篇)")


if __name__ == "__main__":
    main()
