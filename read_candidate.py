import json

import ssh_tunnel


def read_candidates():
    result = ssh_tunnel.run_remote(
        "cat /www/wwwroot/gubut/pending-articles.json", timeout=60
    )
    return json.loads(result["stdout"])


def main():
    items = read_candidates()
    print("候选总数:", len(items))
    for i, a in enumerate(items[:8]):
        desc = (a.get("description") or "").replace("\n", " ")
        print("\n===== 候选 [{i}] =====".format(i=i))
        print("标题:", a.get("title"))
        print("链接:", a.get("link"))
        print("日期:", a.get("pubDate"))
        print("描述:", desc)


if __name__ == "__main__":
    main()
