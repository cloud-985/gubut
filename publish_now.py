# publish_now.py - 上传 ai_article.json 并调用远端 publish_ai.js 发布

import json
import sys
from ssh_tunnel import upload_file, run_remote

LOCAL_FILE = "/workspace/ai_article.json"
REMOTE_FILE = "/www/wwwroot/gubut/ai_article.json"


def main():
    with open(LOCAL_FILE, "r", encoding="utf-8") as f:
        article = json.load(f)
    print(f"[上传] {LOCAL_FILE} -> {REMOTE_FILE}")
    upload_file(LOCAL_FILE, REMOTE_FILE, timeout=120)
    print("[上传] 完成")

    print("[发布] 运行远端 node publish_ai.js ...")
    code, out, err = run_remote(
        "cd /www/wwwroot/gubut && node publish_ai.js", timeout=180
    )
    print(out)
    if err.strip():
        print("[STDERR]", err, file=sys.stderr)
    if code != 0:
        print(f"[ERROR] publish_ai.js 退出码 {code}", file=sys.stderr)
        sys.exit(1)

    print("\n===== 发布结果 =====")
    print("标题:", article.get("title"))
    print("ID:", article.get("id"))
    print("URL: https://www.gubut.com/new/article-" + str(article.get("id")) + ".html")


if __name__ == "__main__":
    main()
