import sys
import os

sys.path.insert(0, "/workspace")
import ssh_tunnel

LOCAL = "/workspace/ai_article.json"
REMOTE = "/www/wwwroot/gubut/ai_article.json"


def main():
    if not os.path.exists(LOCAL):
        print("未找到", LOCAL)
        sys.exit(1)

    print("[上传]", LOCAL, "->", REMOTE)
    ssh_tunnel.sftp_put(LOCAL, REMOTE)

    print("[发布] 执行 node _publish_ai.js ...")
    out, err = ssh_tunnel.run_remote("cd /www/wwwroot/gubut && node _publish_ai.js")
    print(out)
    if err.strip():
        print("--- STDERR ---")
        print(err)


if __name__ == "__main__":
    main()
