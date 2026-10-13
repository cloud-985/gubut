import json
import sys
from ssh_tunnel import run_remote


def main():
    code, out, err = run_remote(
        "cat /www/wwwroot/gubut/pending-articles.json", timeout=60
    )
    if code != 0:
        print(f"[ERROR] 读取失败 退出码 {code}", file=sys.stderr)
        print(err, file=sys.stderr)
        sys.exit(1)
    data = json.loads(out)
    articles = data if isinstance(data, list) else data.get("articles", data)
    print(f"候选文章总数: {len(articles)}\n")
    for i, a in enumerate(articles[:8], 1):
        print(f"===== 候选 {i} =====")
        print(f"标题: {a.get('title', '')}")
        print(f"链接: {a.get('link', '')}")
        print(f"日期: {a.get('pubDate', a.get('date', ''))}")
        desc = a.get('description', a.get('content', ''))
        print(f"描述/内容: {desc[:2000]}")
        print()


if __name__ == "__main__":
    main()
