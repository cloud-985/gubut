import sys

import ssh_tunnel

LOCAL_ARTICLE = "/workspace/ai_article.json"
REMOTE_ARTICLE = "/www/wwwroot/gubut/ai_article.json"


def main():
    ssh_tunnel.upload_file(LOCAL_ARTICLE, REMOTE_ARTICLE)
    print("[上传] ai_article.json 已上传至服务器")

    result = ssh_tunnel.run_remote(
        "cd /www/wwwroot/gubut && node _publish_ai.js", timeout=180
    )
    print(result["stdout"])
    if result["stderr"]:
        print("[STDERR]", result["stderr"], file=sys.stderr)
    if result["code"] != 0:
        print("[发布] _publish_ai.js 退出码非0: {}".format(result["code"]), file=sys.stderr)
        sys.exit(1)
    print("[发布] 发布流程执行完成")


if __name__ == "__main__":
    main()
