import json
import sys
import ssh_tunnel


PENDING_PATH = "/www/wwwroot/gubut/pending-articles.json"


def load_candidates():
    raw = ssh_tunnel.read_remote_file(PENDING_PATH)
    return json.loads(raw)


def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    candidates = load_candidates()
    for i, item in enumerate(candidates[:limit]):
        print(f"===== 候选 {i + 1} =====")
        print(f"标题: {item.get('title', '')}")
        print(f"链接: {item.get('link', '')}")
        print(f"日期: {item.get('pubDate', '')}")
        print(f"描述: {item.get('description', '')}")
        print()


if __name__ == "__main__":
    main()
