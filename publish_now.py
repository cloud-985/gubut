import json

import ssh_tunnel

LOCAL_ARTICLE = "/workspace/ai_article.json"
REMOTE_ARTICLE = "/www/wwwroot/gubut/ai_article.json"


def main():
    with open(LOCAL_ARTICLE, "r", encoding="utf-8") as f:
        article = json.load(f)

    print("上传 ai_article.json -> 服务器 ...")
    out = ssh_tunnel.upload_text(
        json.dumps(article, ensure_ascii=False, indent=2),
        REMOTE_ARTICLE,
    )
    if out.strip():
        print(out)

    print("执行服务器端发布脚本 _publish_ai.js ...")
    out = ssh_tunnel.run_remote(
        "cd /www/wwwroot/gubut && node _publish_ai.js"
    )
    print(out)


if __name__ == "__main__":
    main()
