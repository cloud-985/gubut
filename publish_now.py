import json
import sys
import ssh_tunnel


LOCAL_FILE = "/workspace/ai_article.json"
REMOTE_FILE = "/www/wwwroot/gubut/ai_article.json"


def main():
    with open(LOCAL_FILE, encoding="utf-8") as f:
        content = f.read()
    article = json.loads(content)

    ssh_tunnel.write_remote_file(REMOTE_FILE, content)
    print(f"已上传 {LOCAL_FILE} -> {REMOTE_FILE}")

    res = ssh_tunnel.run_remote(
        "cd /www/wwwroot/gubut && /usr/bin/node _publish_ai.js 2>&1",
        timeout=180,
    )
    sys.stdout.write(res["stdout"])
    if res["stderr"]:
        sys.stderr.write(res["stderr"])
    sys.exit(res["code"])


if __name__ == "__main__":
    main()
