# -*- coding: utf-8 -*-
"""采集 TradingView RSS 候选文章并写入 pending-articles.json。

说明:
  - 本地沙箱直连 tradingview.com 会因代理 TLS 握手失败, 因此 RSS 采集在服务器端执行,
    再把 XML 下载回本地解析。
  - 解析后按资产关键词过滤, 与服务器端已发布文章去重, 生成本地与服务器两份 pending-articles.json。
"""
import json
import os
import re

import ssh_tunnel

RSS_URL = "https://www.tradingview.com/feed/"
LOCAL_PENDING = "/workspace/pending-articles.json"
REMOTE_PENDING = "/www/wwwroot/gubut/pending-articles.json"
REMOTE_RSS_TMP = "/tmp/rss_gubut.xml"

# 明确的资产标的, 至少命中其一才保留
ASSET_KEYWORDS = [
    "BTC", "BITCOIN", "ETH", "ETHEREUM", "XAUUSD", "GOLD", "NEAR", "SOL",
    "XRP", "BNB", "DOGE", "ADA", "AVAX", "LINK", "USDT", "EURUSD", "GBPUSD",
    "USDJPY", "CRYPTO", "ZEC", "LSK", "RUNE", "THORCHAIN", "TOTAL3", "SPY",
    "NVDA", "NVIDIA", "SOXX", "GBP-USD",
]


def fetch_rss_xml():
    """在服务器端抓取 RSS, 下载到本地临时文件。"""
    out, err = ssh_tunnel.run_remote(
        'curl -sS -m 40 -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64)" '
        '"{}" -o {} -w "code=%{{http_code}} size=%{{size_download}}\\n"'.format(
            RSS_URL, REMOTE_RSS_TMP
        )
    )
    print("[collect] 服务器端 RSS 抓取结果:", out.strip())
    if err.strip():
        print("[collect] 服务器端 stderr:", err.strip()[:500])
    if "code=200" not in out:
        raise RuntimeError("RSS 抓取失败, 输出: " + out.strip())

    local_tmp = "/tmp/rss_gubut.xml"
    ssh_tunnel.download(REMOTE_RSS_TMP, local_tmp)
    with open(local_tmp, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def parse_items(xml):
    items = []
    for m in re.finditer(r"<item>([\s\S]*?)</item>", xml):
        block = m.group(1)

        def grab(pat, group=1):
            mm = re.search(pat, block, re.S)
            return mm.group(group) if mm else ""

        title = grab(r"<title>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>")
        link = grab(r"<link>(.*?)</link>")
        desc = grab(r"<description>(?:<!\[CDATA\[)?([\s\S]*?)(?:\]\]>)?</description>")
        pub_date = grab(r"<pubDate>(.*?)</pubDate>")

        items.append({
            "title": _strip_html(title).strip(),
            "link": link.strip(),
            "description": _strip_html(desc).strip()[:1200],
            "pubDate": pub_date.strip(),
        })
    return items


def _strip_html(text):
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    text = text.replace("&quot;", '"').replace("&#39;", "'")
    return re.sub(r"\s+", " ", text).strip()


def filter_relevant(items):
    def hit(text):
        up = text.upper()
        return any(re.search(r"\b" + re.escape(k) + r"\b", up) for k in ASSET_KEYWORDS)

    out = [it for it in items if hit(it["title"] + " " + it["description"])]
    return out


def load_published_keys():
    """读取服务器端已发布记录, 返回用于去重的链接集合与标题键集合。"""
    keys = set()
    try:
        out, _ = ssh_tunnel.run_remote(
            "cat /www/wwwroot/gubut/.published-articles.json 2>/dev/null"
        )
        data = json.loads(out) if out.strip() else []
        for rec in data:
            if isinstance(rec, dict):
                if rec.get("link") or rec.get("source"):
                    keys.add((rec.get("link") or rec.get("source")).strip())
                if rec.get("titleKey"):
                    keys.add(rec["titleKey"].strip().lower())
    except Exception as e:
        print("[collect] 读取已发布记录失败(忽略):", e)
    return keys


def dedup(items, published_keys):
    result = []
    for it in items:
        link = it["link"].strip()
        title = it["title"].strip().lower()
        if link in published_keys or title in published_keys:
            continue
        result.append(it)
    return result


def main():
    print("[collect] 开始采集 TradingView RSS ...")
    xml = fetch_rss_xml()
    items = parse_items(xml)
    print("[collect] 解析到 {} 篇文章".format(len(items)))

    relevant = filter_relevant(items)
    print("[collect] 过滤出 {} 篇资产/策略相关文章".format(len(relevant)))

    published_keys = load_published_keys()
    pending = dedup(relevant, published_keys)
    print("[collect] 去重后剩余 {} 篇候选".format(len(pending)))

    os.makedirs(os.path.dirname(LOCAL_PENDING), exist_ok=True)
    with open(LOCAL_PENDING, "w", encoding="utf-8") as f:
        json.dump(pending, f, ensure_ascii=False, indent=2)

    ssh_tunnel.upload(LOCAL_PENDING, REMOTE_PENDING)
    print("[collect] 已写入本地:", LOCAL_PENDING)
    print("[collect] 已上传服务器:", REMOTE_PENDING)

    for i, it in enumerate(pending):
        print("  [{}] {} | {}".format(i, it["pubDate"][:22], it["title"][:70]))


if __name__ == "__main__":
    main()
