"""读取服务器 pending-articles.json 候选文章(默认前 N 篇完整内容)。"""
import json
import sys
import ssh_tunnel

REMOTE_PENDING = "/www/wwwroot/gubut/pending-articles.json"


def read_pending(limit=None):
    out, err, rc = ssh_tunnel.run_remote(f"cat {REMOTE_PENDING}", timeout=60)
    if rc != 0:
        raise RuntimeError(f"读取失败: {err.strip()[:300]}")
    data = json.loads(out)
    if limit:
        data = data[:limit]
    return data


def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    items = read_pending(limit)
    print(json.dumps(items, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
