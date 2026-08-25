import feedparser
import requests
import json
import re
import os
import sys
from datetime import datetime

PROXY = {'http': 'http://127.0.0.1:18080', 'https': 'http://127.0.0.1:18080'}

RSS_SOURCES = [
    'https://www.tradingview.com/rss/news/',
    'https://www.investing.com/rss/news_301.rss',
    'https://cointelegraph.com/rss',
    'https://www.coindesk.com/arc/outboundfeeds/rss/',
    'https://cryptonews.com/news/feed/',
]

OUTPUT_FILE = '/workspace/pending_articles.json'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}

KEYWORDS_FILTER = [
    'bitcoin', 'btc', 'ethereum', 'eth', 'crypto', 'blockchain',
    'gold', 'xauusd', 'forex', 'trading', 'strategy',
    'technical analysis', 'mt5', 'metatrader', 'grid', 'futures',
    'swing', 'scalping', 'risk', 'solana', 'sol', 'bnb',
    'binance', 'altcoin', 'market', 'crash', 'surge',
    '合约', '网格', '策略', '交易', '技术分析', '风险', '行情'
]


def clean_html(html_content):
    if not html_content:
        return ''
    text = re.sub(r'<[^>]+>', ' ', html_content)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def fetch_rss_articles():
    all_articles = []
    for rss_url in RSS_SOURCES:
        try:
            print(f'尝试: {rss_url}')
            resp = requests.get(rss_url, headers=HEADERS, timeout=20, proxies=PROXY)
            resp.raise_for_status()
            feed = feedparser.parse(resp.content)

            for entry in feed.entries[:10]:
                title = entry.get('title', '').strip()
                link = entry.get('link', '')
                summary = entry.get('summary', '')
                published = entry.get('published', '')

                content_text = clean_html(summary)
                if len(content_text) > 50:
                    all_articles.append({
                        'title': title,
                        'url': link,
                        'summary': content_text[:600],
                        'published': published,
                        'source': rss_url.split('/')[2] if '/' in rss_url else 'RSS'
                    })

            print(f'  成功: 获取 {len(feed.entries)} 条')
        except Exception as e:
            print(f'  失败: {e}')
    return all_articles


def fetch_article_content(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20, proxies=PROXY)
        resp.raise_for_status()
        html = resp.text
        text = clean_html(html)
        return text[:8000]
    except Exception:
        return ''


def filter_relevant(articles):
    relevant = []
    for a in articles:
        title_lower = a['title'].lower()
        summary_lower = a['summary'].lower()
        combined = title_lower + ' ' + summary_lower
        score = sum(1 for kw in KEYWORDS_FILTER if kw.lower() in combined)
        if score >= 2:
            a['relevance_score'] = score
            relevant.append(a)
    relevant.sort(key=lambda x: x['relevance_score'], reverse=True)
    return relevant


def fetch_from_server():
    """从服务器获取待处理文章列表"""
    try:
        sys.path.insert(0, '/workspace')
        from ssh_tunnel import run_remote, REMOTE_BASE
        result = run_remote(f'cat {REMOTE_BASE}/pending-articles.json')
        if result['exit_code'] == 0 and result['stdout'].strip():
            articles = json.loads(result['stdout'])
            print(f'从服务器获取 {len(articles)} 篇待处理文章')
            return articles
    except Exception as e:
        print(f'从服务器获取失败: {e}')
    return []


def main():
    print('=== 开始采集候选文章 ===')

    server_articles = fetch_from_server()
    if server_articles:
        print(f'\n服务器已有 {len(server_articles)} 篇待处理文章，直接使用')
        for i, a in enumerate(server_articles[:10]):
            title = a.get('title', '无标题')
            print(f'  [{i+1}] {title}')

        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(server_articles, f, ensure_ascii=False, indent=2)
        print(f'\n已保存到 {OUTPUT_FILE}')
        return server_articles

    print('\n服务器无待处理文章，开始RSS采集...')
    raw_articles = fetch_rss_articles()
    print(f'\n共采集到 {len(raw_articles)} 篇原始文章')

    relevant = filter_relevant(raw_articles)
    print(f'筛选出 {len(relevant)} 篇相关文章')

    for i, a in enumerate(relevant[:15]):
        print(f'  [{i+1}] (score={a.get("relevance_score",0)}) {a["title"]}')
        print(f'      摘要: {a["summary"][:120]}...')

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(relevant, f, ensure_ascii=False, indent=2)
    print(f'\n已保存到 {OUTPUT_FILE}')
    return relevant


if __name__ == '__main__':
    main()
