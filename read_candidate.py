#!/usr/bin/env python3
"""读取服务器 pending-articles.json 候选文章（默认前 8 篇完整内容）。"""
import json
import ssh_tunnel

REMOTE = '/www/wwwroot/gubut/pending-articles.json'


def main(n=8):
    r = ssh_tunnel.run_remote(f'python3 -c "import json,sys; p=json.load(open(\'{REMOTE}\')); print(json.dumps(p[:{n}], ensure_ascii=False, indent=2))"', timeout=60)
    data = json.loads(r['stdout'])
    print(f'候选文章总数: {len(data[:{n}])} 篇（展示前 {n} 篇）')
    for i, x in enumerate(data):
        print(f'\n=== [{i}] {x.get("title")}')
        print(f'链接: {x.get("link")}')
        print(f'发布时间: {x.get("pubDate")}')
        print(f'描述: {(x.get("description") or "").strip()}')


if __name__ == '__main__':
    import sys
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    main(n)
