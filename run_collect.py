# -*- coding: utf-8 -*-
"""
采集 TradingView RSS 候选文章，写入服务器 pending-articles.json。

默认使用 TradingView Ideas 的 RSS 源。若网络不可达则保留服务器上已有的
pending-articles.json，并输出采集结果说明。
"""
import json
import sys
import urllib.request
import xml.etree.ElementTree as ET

import ssh_tunnel

RSS_FEEDS = [
    "https://www.tradingview.com/feed/",
]

REMOTE_PATH = "/www/wwwroot/gubut/pending-articles.json"


def fetch_feed(url, timeout=25):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Accept": "application/rss+xml, application/xml, text/xml, */*",
        },
    )
    return urllib.request.urlopen(req, timeout=timeout).read()


def parse_rss(xml_bytes):
    root = ET.fromstring(xml_bytes)
    items = []
    for item in root.iter("item"):
        def text(tag):
            node = item.find(tag)
            return (node.text or "").strip() if node is not None and node.text else ""

        items.append(
            {
                "title": text("title"),
                "link": text("link"),
                "description": text("description"),
                "pubDate": text("pubDate"),
            }
        )
    return items


def main():
    collected = []
    errors = []
    for url in RSS_FEEDS:
        try:
            xml_bytes = fetch_feed(url)
            items = parse_rss(xml_bytes)
            if items:
                collected.extend(items)
                break
            errors.append("{} 无有效条目".format(url))
        except Exception as e:  # noqa: BLE001
            errors.append("{}: {}".format(url, e))

    if collected:
        payload = json.dumps(collected, ensure_ascii=False, indent=2)
        # 通过临时文件上传，避免 shell 转义问题
        import tempfile
        import os

        fd, tmp = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w") as f:
            f.write(payload)
        try:
            ssh_tunnel.put_file(tmp, REMOTE_PATH)
        finally:
            os.remove(tmp)
        print("采集成功: {} 篇，已写入 {}".format(len(collected), REMOTE_PATH))
        return 0

    print("采集失败，保留服务器已有 pending-articles.json")
    for e in errors:
        print("  -", e)
    return 1


if __name__ == "__main__":
    sys.exit(main())
