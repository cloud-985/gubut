#!/usr/bin/env python3
"""上传 ai_article.json 到服务器并执行发布流程。"""
import json
import ssh_tunnel as s

LOCAL_FILE = "/workspace/ai_article.json"
REMOTE_FILE = "/www/wwwroot/gubut/ai_article.json"
CMD = "cd /www/wwwroot/gubut && node publish_ai.js"


def main():
    with open(LOCAL_FILE, "r", encoding="utf-8") as f:
        article = json.load(f)

    # 1) 上传
    s.write_remote_file(REMOTE_FILE, json.dumps(article, ensure_ascii=False, indent=2))
    print("已上传 ai_article.json ->", REMOTE_FILE)

    # 2) 发布
    out, err, code = s.run_remote(CMD, timeout=180)
    print(out)
    if err:
        print("STDERR:", err)
    print("EXIT:", code)


if __name__ == "__main__":
    main()
