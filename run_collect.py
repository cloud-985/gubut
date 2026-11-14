#!/usr/bin/env python3
"""采集 TradingView RSS 候选文章，写入 pending-articles.json（本地 + 服务器）。

说明：本地沙箱无法直连 TradingView，但生产服务器可以。因此先在服务器上
用 curl 拉取 RSS，再下载到本地解析、过滤，最后写回本地并上传到服务器。
"""

import html as htmlmod
import json
import re

import ssh_tunnel

RSS_URL = "https://www.tradingview.com/feed/"
REMOTE_RSS_PATH = "/www/wwwroot/gubut/.tradingview-rss.xml"
LOCAL_RSS_PATH = "/workspace/.tradingview-rss.xml"
PENDING_LOCAL = "/workspace/pending-articles.json"
PENDING_REMOTE = "/www/wwwroot/gubut/pending-articles.json"

# 明确的资产标的（必须匹配其一才会被选中），覆盖区块链与外汇/贵金属
ASSET_KEYWORDS = [
    "BTC", "BITCOIN", "ETH", "ETHEREUM", "XAUUSD", "GOLD", "NEAR",
    "SOL", "XRP", "BNB", "DOGE", "ADA", "AVAX", "LINK", "USDT",
    "EURUSD", "GBPUSD", "USDJPY", "CRYPTO", "FOREX",
]


def strip_html(text):
    text = re.sub(r"<[^>]+>", " ", text)
    text = htmlmod.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def fetch_rss_on_server():
    cmd = (
        "curl -sS -A 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' --max-time 40 "
        "'{url}' -o {out} && wc -c < {out}"
    ).format(url=RSS_URL, out=REMOTE_RSS_PATH)
    out, err = ssh_tunnel.run_remote(cmd)
    if err.strip():
        raise RuntimeError("服务器 curl 出错: " + err.strip())

    ssh_tunnel.download(REMOTE_RSS_PATH, LOCAL_RSS_PATH)
    with open(LOCAL_RSS_PATH, encoding="utf-8") as f:
        return f.read()


def _grab(block, tag):
    m = re.search(
        r"<%s>(?:<!\[CDATA\[)?([\s\S]*?)(?:\]\]>)?</%s>" % (tag, tag), block
    )
    return m.group(1) if m else ""


def parse_items(xml):
    items = []
    for m in re.finditer(r"<item>([\s\S]*?)</item>", xml):
        block = m.group(1)
        items.append(
            {
                "title": strip_html(_grab(block, "title")),
                "link": _grab(block, "link").strip(),
                "description": strip_html(_grab(block, "description")),
                "pubDate": _grab(block, "pubDate").strip(),
            }
        )
    return items


def filter_relevant(items):
    def word_match(kw, text):
        return re.search(r"\b" + re.escape(kw) + r"\b", text, re.IGNORECASE) is not None

    relevant = []
    for it in items:
        text = it["title"] + " " + it["description"]
        if any(word_match(kw, text) for kw in ASSET_KEYWORDS):
            relevant.append(it)
    return relevant


def main():
    xml = fetch_rss_on_server()
    items = parse_items(xml)
    relevant = filter_relevant(items)
    print("RSS 共解析 %d 篇，过滤后相关 %d 篇" % (len(items), len(relevant)))

    data = json.dumps(relevant, ensure_ascii=False, indent=2)
    with open(PENDING_LOCAL, "w", encoding="utf-8") as f:
        f.write(data)

    ssh_tunnel.upload(PENDING_LOCAL, PENDING_REMOTE)
    print("已写入 %s 并上传到 %s" % (PENDING_LOCAL, PENDING_REMOTE))


if __name__ == "__main__":
    main()
