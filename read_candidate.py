import json

import ssh_tunnel


def main():
    cmd = f'cat {ssh_tunnel.SITE_DIR}/pending-articles.json'
    out = ssh_tunnel.run_remote(cmd, timeout=120)
    articles = json.loads(out)
    print(f'共 {len(articles)} 篇候选文章，展示前 8 篇完整内容：\n')
    for i, a in enumerate(articles[:8]):
        print('=' * 80)
        print(f"[{i + 1}] {a.get('title')}")
        print(f"链接: {a.get('link')}")
        print(f"发布时间: {a.get('pubDate')}")
        print(f"描述:\n{a.get('description')}")
        print()


if __name__ == '__main__':
    main()
