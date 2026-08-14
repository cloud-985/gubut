"""
TradingView RSS采集脚本 - 采集TradingView RSS候选文章
"""
import json
import time
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta

RSS_FEEDS = [
    "https://www.tradingview.com/feed/rss/?stream=all_ideas",
    "https://www.tradingview.com/feed/rss/?stream=forex_ideas",
    "https://www.tradingview.com/feed/rss/?stream=crypto_ideas",
    "https://www.tradingview.com/feed/rss/?stream=commodities_ideas",
]

PROXY = "127.0.0.1:18080"
OUTPUT_FILE = "/workspace/rss_candidates.json"


def fetch_rss(url, use_proxy=False):
    """获取RSS内容"""
    try:
        if use_proxy:
            proxy_handler = urllib.request.ProxyHandler({
                "http": f"socks5h://{PROXY}",
                "https": f"socks5h://{PROXY}"
            })
            opener = urllib.request.build_opener(proxy_handler)
        else:
            opener = urllib.request.build_opener()
        
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (compatible; GubutBot/1.0)"
        })
        
        with opener.open(req, timeout=30) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  获取RSS失败 {url}: {e}")
        return None


def parse_rss(xml_content):
    """解析RSS XML内容，返回文章列表"""
    articles = []
    try:
        root = ET.fromstring(xml_content)
        channel = root.find("channel")
        if channel is None:
            return articles
        
        for item in channel.findall("item"):
            title = item.findtext("title", "").strip()
            link = item.findtext("link", "").strip()
            description = item.findtext("description", "").strip()
            pub_date = item.findtext("pubDate", "").strip()
            category = item.findtext("category", "").strip()
            
            # 提取内容（可能是HTML）
            content_encoded = ""
            for child in item:
                if "encoded" in child.tag:
                    content_encoded = (child.text or "").strip()
            
            if title:
                articles.append({
                    "title": title,
                    "link": link,
                    "description": description,
                    "content": content_encoded or description,
                    "pub_date": pub_date,
                    "category": category,
                    "collected_at": datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")
                })
    except Exception as e:
        print(f"  解析RSS失败: {e}")
    
    return articles


def main():
    print("开始采集TradingView RSS候选文章...")
    all_articles = []
    
    for feed_url in RSS_FEEDS:
        print(f"正在采集: {feed_url}")
        xml_content = fetch_rss(feed_url, use_proxy=False)
        if not xml_content:
            # 尝试使用代理
            xml_content = fetch_rss(feed_url, use_proxy=True)
        
        if xml_content:
            articles = parse_rss(xml_content)
            print(f"  获取到 {len(articles)} 篇文章")
            all_articles.extend(articles)
        time.sleep(1)
    
    # 去重（按link）
    seen = set()
    unique_articles = []
    for art in all_articles:
        if art["link"] and art["link"] not in seen:
            seen.add(art["link"])
            unique_articles.append(art)
        elif not art["link"]:
            unique_articles.append(art)
    
    print(f"\n总共采集到 {len(unique_articles)} 篇候选文章（去重后）")
    
    # 保存到本地
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(unique_articles, f, ensure_ascii=False, indent=2)
    print(f"已保存到: {OUTPUT_FILE}")
    
    # 打印样例
    if unique_articles:
        print("\n=== 前5篇候选标题 ===")
        for i, art in enumerate(unique_articles[:5], 1):
            print(f"  {i}. {art['title']}")
    
    return unique_articles


if __name__ == "__main__":
    main()
