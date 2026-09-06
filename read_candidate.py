"""
read_candidate.py - 从服务器读取 pending-articles.json 候选文章
输出前 N 篇完整内容到本地 ai_article.json 前的参考文件
"""
import json
import sys
import os
import re

sys.path.insert(0, '/workspace')
from ssh_tunnel import remote_read, run_remote, REMOTE_BASE

PENDING_PATH = f"{REMOTE_BASE}/pending-articles.json"


def fetch_full_article(url, timeout=20):
    """尝试抓取文章全文"""
    try:
        import urllib.request
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })
        proxy_handler = urllib.request.ProxyHandler({
            'http': 'http://127.0.0.1:18080',
            'https': 'http://127.0.0.1:18080',
        })
        opener = urllib.request.build_opener(proxy_handler)
        with opener.open(req, timeout=timeout) as resp:
            html = resp.read().decode('utf-8', errors='replace')
        
        # 简单提取正文
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'lxml')
        
        # 移除脚本和样式
        for tag in soup(['script', 'style', 'nav', 'header', 'footer']):
            tag.decompose()
        
        # 尝试找主要内容
        content_selectors = [
            'article', '.article-content', '.post-content', 
            '.entry-content', 'main', '[role="main"]',
            '.content-wrapper', '#content', '.post',
        ]
        
        text = ''
        for sel in content_selectors:
            el = soup.select_one(sel)
            if el and len(el.get_text()) > 200:
                text = el.get_text('\n', strip=True)
                break
        
        if not text:
            text = soup.get_text('\n', strip=True)
        
        # 清理多余空行
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text[:5000]
    except Exception as e:
        return f"[抓取失败: {e}]"


def main(count=8, fetch_content=True):
    """读取并展示前 N 篇候选文章"""
    print("=" * 60)
    print(f"📖 读取候选文章 (前 {count} 篇)")
    print("=" * 60)
    
    # 读取 pending-articles.json
    try:
        content = remote_read(PENDING_PATH)
        candidates = json.loads(content)
    except Exception as e:
        print(f"✗ 读取 pending-articles.json 失败: {e}")
        return []
    
    print(f"服务器共有候选文章: {len(candidates)} 篇\n")
    
    if not candidates:
        print("⚠️ 无候选文章，先运行 run_collect.py")
        return []
    
    selected = candidates[:count]
    
    # 同时读取已发布文章列表用于去重
    articles_json_path = f"{REMOTE_BASE}/articles.json"
    published_titles = set()
    try:
        published_content = remote_read(articles_json_path)
        published_articles = json.loads(published_content)
        for a in published_articles:
            t = a.get('title', '').lower()
            # 提取主要关键词
            words = re.findall(r'[\u4e00-\u9fff]+|[a-z]+', t)
            published_titles.update(words)
        print(f"已发布文章: {len(published_articles)} 篇（用于去重）\n")
    except Exception as e:
        print(f"⚠️ 读取已发布文章失败: {e}\n")
    
    results = []
    for i, c in enumerate(selected, 1):
        print(f"--- 候选 #{i} ---")
        print(f"标题: {c['title']}")
        print(f"链接: {c.get('link', 'N/A')}")
        print(f"发布: {c.get('published', 'N/A')}")
        print(f"摘要: {c.get('summary', '')[:200]}")
        
        # 尝试获取正文
        full_text = ''
        if fetch_content and c.get('link'):
            print(f"→ 抓取正文中...")
            full_text = fetch_full_article(c['link'])
            print(f"  正文长度: {len(full_text)} 字")
        
        item = {
            'index': i,
            'fid': c['fid'],
            'title': c['title'],
            'link': c.get('link', ''),
            'summary': c.get('summary', ''),
            'published': c.get('published', ''),
            'source_url': c.get('source_url', ''),
            'full_text': full_text,
        }
        results.append(item)
    
    # 保存到本地参考文件
    local_path = '/workspace/_candidates_ref.json'
    with open(local_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n✓ 已保存参考文件: {local_path}")
    
    return results


if __name__ == '__main__':
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    main(count=count)
