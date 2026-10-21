import json

import ssh_tunnel as s

PENDING_FILE = "/www/wwwroot/gubut/pending-articles.json"


def read_candidates(limit=8):
    raw = s.get_file(PENDING_FILE)
    data = json.loads(raw.decode("utf-8"))
    return data[:limit]


def main():
    data = read_candidates(8)
    print("共 %d 篇候选文章，展示前 %d 篇" % (len(data), len(data)))
    for i, p in enumerate(data):
        print("-" * 50)
        print("[%d] %s" % (i + 1, p.get("title")))
        print("链接: %s" % p.get("link"))
        print("发布时间: %s" % (p.get("pubDate") or ""))
        print("描述:\n%s" % (p.get("description") or ""))


if __name__ == "__main__":
    main()
