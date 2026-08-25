import json
import sys
sys.path.insert(0, '/workspace')
from ssh_tunnel import run_remote, REMOTE_BASE


def get_pending_articles():
    """读取服务器pending-articles.json"""
    result = run_remote(f'cat {REMOTE_BASE}/pending-articles.json')
    if result['exit_code'] != 0 or not result['stdout'].strip():
        print('无pending-articles.json，直接从RSS获取')
        return []
    try:
        articles = json.loads(result['stdout'])
        print(f'从服务器获取 {len(articles)} 篇待处理文章')
        return articles
    except json.JSONDecodeError:
        print('pending-articles.json格式错误')
        return []


def main():
    articles = get_pending_articles()
    if not articles:
        print('服务器无待处理文章')
        return

    for i, a in enumerate(articles[:10]):
        title = a.get('title', '无标题')
        url = a.get('url', '')
        summary = a.get('summary', '')[:100]
        print(f'[{i+1}] {title}')
        print(f'     URL: {url}')
        print(f'     摘要: {summary}')
        print()


if __name__ == '__main__':
    main()
