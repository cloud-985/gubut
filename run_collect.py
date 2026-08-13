#!/usr/bin/env python3
"""采集TradingView RSS候选文章并同步到远程服务器"""

import feedparser
import json
import time
import os
import sys
from datetime import datetime, timezone, timedelta
from ssh_tunnel import run_remote, upload_file, REMOTE_DIR

# TradingView RSS源 - 区块链/加密货币/外汇/黄金相关
RSS_FEEDS = [
    # 加密货币相关
    "https://www.tradingview.com/feed/?_symbol=BITSTAMP%3ABTCUSD",
    "https://www.tradingview.com/feed/?_symbol=COINBASE%3ABTCUSD",
    "https://www.tradingview.com/feed/?_symbol=BINANCE%3ABTCUSDT",
    "https://www.tradingview.com/feed/?_symbol=OANDA%3AXAUUSD",
    "https://www.tradingview.com/feed/?_symbol=OANDA%3AEURUSD",
    "https://www.tradingview.com/feed/?_symbol=FX%3AGBPUSD",
    # 社区热门观点
    "https://www.tradingview.com/feed/rss/ideas/ta/crypto/",
    "https://www.tradingview.com/feed/rss/ideas/ta/forex/",
    "https://www.tradingview.com/feed/rss/ideas/ta/commodities/",
]

# 备份RSS源（通用RSS）
BACKUP_RSS = [
    "https://cointelegraph.com/rss",
    "https://cryptonews.com/news/feed/",
    "https://www.dailyfx.com/forex/rss",
]

CANDIDATE_FILE = "/workspace/pending-articles.json"
REMOTE_CANDIDATE_FILE = f"{REMOTE_DIR}/pending-articles.json"

BEIJING_TZ = timezone(timedelta(hours=8))


def parse_rss_feed(url, max_retries=2):
    """解析RSS源，返回文章列表"""
    for attempt in range(max_retries):
        try:
            print(f"  解析: {url[:80]}...")
            feed = feedparser.parse(url)
            if feed.entries:
                print(f"    找到 {len(feed.entries)} 篇文章")
                return feed.entries
            else:
                print(f"    无内容")
        except Exception as e:
            print(f"    解析失败 (尝试{attempt+1}/{max_retries}): {e}")
            time.sleep(2)
    return []


def extract_article_data(entry, source_name):
    """从RSS条目提取标准化数据"""
    article = {
        "id": str(int(time.time() * 1000)) + str(hash(entry.get('link', '') % 10000)).zfill(4),
        "title": entry.get('title', '无标题'),
        "link": entry.get('link', ''),
        "source": source_name,
        "published": entry.get('published', entry.get('updated', datetime.now(BEIJING_TZ).isoformat())),
        "summary": entry.get('summary', entry.get('description', '')),
        "content": "",
        "tags": [],
        "collected_at": datetime.now(BEIJING_TZ).strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # 提取标签
    if 'tags' in entry:
        article['tags'] = [tag.get('term', '') for tag in entry.tags if tag.get('term')]
    
    # 提取内容（如果有）
    if 'content' in entry:
        for c in entry.content:
            article['content'] += c.get('value', '')
    
    return article


def deduplicate_articles(articles):
    """根据标题去重"""
    seen_titles = set()
    unique = []
    for art in articles:
        title_key = art['title'].strip().lower()
        if title_key not in seen_titles and len(title_key) > 5:
            seen_titles.add(title_key)
            unique.append(art)
    return unique


def filter_relevant(articles):
    """筛选与交易相关的文章"""
    keywords = [
        'btc', 'bitcoin', 'eth', 'ethereum', 'crypto', '加密', '比特币',
        'xau', 'gold', '黄金', 'forex', '外汇', 'eur', 'usd', 'gbp', 'jpy',
        'trade', 'trading', '交易', 'strategy', '策略', 'technical', '技术分析',
        'price', '价格', 'market', '市场', 'analysis', '分析', 'signal', '信号',
        'mt5', 'mt4', 'indicator', '指标', 'support', '支撑', 'resistance', '阻力',
        'trend', '趋势', 'breakout', '突破', 'rally', '反弹', 'pullback', '回调'
    ]
    
    relevant = []
    for art in articles:
        text = (art['title'] + ' ' + art['summary'] + ' ' + art.get('content', '')).lower()
        score = sum(1 for kw in keywords if kw in text)
        if score >= 1:
            art['relevance_score'] = score
            relevant.append(art)
    
    # 按相关度排序
    relevant.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
    return relevant


def main():
    print("=" * 60)
    print("TradingView RSS 文章采集启动")
    print(f"启动时间: {datetime.now(BEIJING_TZ).strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    all_articles = []
    
    # 主RSS源采集
    print("\n[1/2] 采集 TradingView RSS 源...")
    for i, url in enumerate(RSS_FEEDS):
        print(f"\n源 {i+1}/{len(RSS_FEEDS)}:")
        entries = parse_rss_feed(url)
        for entry in entries:
            art = extract_article_data(entry, "TradingView")
            all_articles.append(art)
        time.sleep(1)
    
    # 备份RSS源采集
    print(f"\n[2/2] 采集备份 RSS 源...")
    for i, url in enumerate(BACKUP_RSS):
        print(f"\n备份源 {i+1}/{len(BACKUP_RSS)}:")
        entries = parse_rss_feed(url)
        source_name = url.split('/')[2] if '//' in url else url
        for entry in entries:
            art = extract_article_data(entry, source_name)
            all_articles.append(art)
        time.sleep(1)
    
    print(f"\n采集完成，共 {len(all_articles)} 篇原始文章")
    
    # 去重
    all_articles = deduplicate_articles(all_articles)
    print(f"去重后剩余 {len(all_articles)} 篇")
    
    # 筛选相关内容
    all_articles = filter_relevant(all_articles)
    print(f"筛选后相关文章 {len(all_articles)} 篇")
    
    # 只保留前20篇
    all_articles = all_articles[:20]
    
    # 读取现有候选文章
    existing = []
    if os.path.exists(CANDIDATE_FILE):
        try:
            with open(CANDIDATE_FILE, 'r', encoding='utf-8') as f:
                existing = json.load(f)
            print(f"读取现有候选 {len(existing)} 篇")
        except:
            existing = []
    
    # 合并去重（按标题）
    existing_titles = {a['title'].strip().lower() for a in existing}
    for art in all_articles:
        if art['title'].strip().lower() not in existing_titles:
            existing.insert(0, art)  # 新文章放前面
    
    # 最多保留50篇
    existing = existing[:50]
    
    # 保存到本地
    with open(CANDIDATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)
    print(f"\n本地保存 {len(existing)} 篇候选文章到 {CANDIDATE_FILE}")
    
    # 上传到远程服务器
    print("\n上传到远程服务器...")
    if upload_file(CANDIDATE_FILE, REMOTE_CANDIDATE_FILE):
        print("上传成功!")
    else:
        print("上传失败!")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("采集完成!")
    print(f"候选文章总数: {len(existing)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
