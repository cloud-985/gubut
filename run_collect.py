"""
run_collect.py - 从 TradingView 等 RSS 源采集候选文章
将采集到的文章保存到服务器 /www/wwwroot/gubut/pending-articles.json
"""
import feedparser
import json
import time
import hashlib
import sys
sys.path.insert(0, '/workspace')
from ssh_tunnel import run_remote, remote_read, remote_write, REMOTE_BASE

# 多个 RSS 源，覆盖区块链、加密货币、外汇、黄金
# 注意：部分源可能在本代理环境不可达
RSS_SOURCES = [
    # 加密货币新闻
    "https://cointelegraph.com/rss",
    "https://news.bitcoin.com/feed/",
    "https://cryptonews.com/feed/",
    "https://www.coindesk.com/arc/outboundfeeds/rss/",
    # 外汇/黄金
    "https://www.fxstreet.com/rss",
    "https://www.forexlive.com/feed/",
    "https://www. Investing.com/rss/news",
    # TradingView (可能不可达)
    "https://www.tradingview.com/rss/ideas/",
    "https://www.tradingview.com/rss/ideas/?category=crypto",
    "https://www.tradingview.com/rss/ideas/?category=forex",
    # Medium 加密货币话题
    "https://medium.com/feed/cryptocurrency",
    "https://medium.com/feed/bitcoin",
]

# 关键词过滤：保留金融交易相关
KEEP_KEYWORDS = [
    "bitcoin", "btc", "ethereum", "eth", "crypto", "cryptocurrency",
    "blockchain", "xrp", "solana", "doge", "memecoin", "nft", "defi",
    "gold", "xau", "forex", "fx", "eurusd", "gbpusd", "usdjpy",
    "技术分析", "技术形态", "交易策略", "突破", "支撑", "阻力",
    "量化", "趋势", "k线", "蜡烛图", "均线", "macd", "rsi",
    "trading", "strategy", "chart", "analysis", "market",
    "feed", "breakout", "support", "resistance", "indicator",
]


def fetch_feed(url, timeout=20):
    """获取并解析单个 RSS feed（通过代理）"""
    import requests
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    proxies = {
        'http': 'http://127.0.0.1:18080',
        'https': 'http://127.0.0.1:18080',
    }
    try:
        resp = requests.get(url, proxies=proxies, timeout=timeout, verify=False, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/rss+xml, application/xml, text/xml, */*',
        })
        resp.raise_for_status()
        feed = feedparser.parse(resp.content)
        print(f"  ✓ {url[:60]}... → {len(feed.entries)} 条")
        return feed.entries
    except Exception as e:
        print(f"  ✗ {url[:60]}... → 失败: {e}")
        return []


def entry_to_candidate(entry, source_url):
    """将 feed entry 转为候选文章 dict"""
    title = entry.get('title', '').strip()
    link = entry.get('link', '')
    summary = entry.get('summary', entry.get('description', ''))
    # 清理 summary 中的 HTML 标签
    import re
    summary_clean = re.sub(r'<[^>]+>', '', summary).strip()
    published = entry.get('published', entry.get('updated', ''))
    
    # 生成唯一 ID
    raw = (title + link).encode('utf-8')
    fid = hashlib.md5(raw).hexdigest()[:12]
    
    return {
        'fid': fid,
        'title': title,
        'link': link,
        'summary': summary_clean[:1500],
        'published': published,
        'source_url': source_url,
        'collected_at': int(time.time() * 1000),
    }


def is_relevant(candidate):
    """检查文章是否与金融交易相关"""
    text = (candidate['title'] + ' ' + candidate['summary']).lower()
    return any(kw in text for kw in KEEP_KEYWORDS)


def load_existing_pending():
    """加载服务器上已有的 pending-articles.json"""
    path = f"{REMOTE_BASE}/pending-articles.json"
    try:
        content = remote_read(path)
        data = json.loads(content)
        return [a['fid'] for a in data], data
    except Exception as e:
        print(f"  读取已有 pending-articles.json 失败(可能不存在): {e}")
        return [], []


def save_pending(candidates):
    """保存候选文章到服务器"""
    path = f"{REMOTE_BASE}/pending-articles.json"
    content = json.dumps(candidates, ensure_ascii=False, indent=2)
    remote_write(path, content)
    print(f"✓ 已保存 {len(candidates)} 篇候选到服务器 {path}")


def main():
    print("=" * 60)
    print("📰 TradingView / 加密货币 RSS 采集")
    print("=" * 60)
    
    # 读取已有 FID，去重
    existing_fids, existing_list = load_existing_pending()
    print(f"已有候选文章: {len(existing_list)} 篇")
    
    # 采集所有源
    all_entries = []
    for url in RSS_SOURCES:
        entries = fetch_feed(url)
        all_entries.extend(entries)
        time.sleep(0.5)  # 礼貌间隔
    
    print(f"\n总共采集到 {len(all_entries)} 条条目")
    
    # 转换并过滤
    new_candidates = []
    seen_fids = set(existing_fids)
    for entry in all_entries:
        candidate = entry_to_candidate(entry, entry.get('link', ''))
        if candidate['fid'] in seen_fids:
            continue
        if not is_relevant(candidate):
            continue
        seen_fids.add(candidate['fid'])
        new_candidates.append(candidate)
    
    print(f"新增有效候选: {len(new_candidates)} 篇")
    
    # 合并并保存（保留所有，按采集时间倒序）
    merged = new_candidates + existing_list
    merged.sort(key=lambda x: x.get('collected_at', 0), reverse=True)
    
    # 保留最多 100 篇
    merged = merged[:100]
    
    save_pending(merged)
    
    print("\n✅ 采集完成")
    return len(new_candidates)


if __name__ == '__main__':
    count = main()
    print(f"\n新增候选文章数: {count}")
