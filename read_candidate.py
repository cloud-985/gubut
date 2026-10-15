import json
import sys

import ssh_tunnel


def read_pending():
    raw = ssh_tunnel.run_remote("cat /www/wwwroot/gubut/pending-articles.json")
    return json.loads(raw)


def read_published_titles():
    raw = ssh_tunnel.run_remote("cat /www/wwwroot/gubut/.published-articles.json")
    return json.loads(raw)


if __name__ == "__main__":
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    items = read_pending()
    print("候选文章总数: %d" % len(items))
    print("=" * 70)
    for i, item in enumerate(items[:limit]):
        print("[%d] %s" % (i + 1, item.get("title", "")))
        print("    链接: %s" % item.get("link", ""))
        print("    日期: %s" % item.get("pubDate", ""))
        print("    描述: %s" % item.get("description", ""))
        print("-" * 70)
