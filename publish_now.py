"""上传 ai_article.json 并调用服务器 publish_ai.js 发布。"""
import sys
import ssh_tunnel

LOCAL = "/workspace/ai_article.json"
REMOTE = "/www/wwwroot/gubut/ai_article.json"
SITE_DIR = "/www/wwwroot/gubut"


def main():
    print("[发布] 上传 ai_article.json ...")
    out, err, rc = ssh_tunnel.upload(LOCAL, REMOTE)
    if rc != 0:
        print("[ERR] 上传失败:", err.strip()[:500])
        sys.exit(1)
    print("[OK] 已上传到", REMOTE)

    print("[发布] 执行 node publish_ai.js ...")
    stdout, stderr, rc = ssh_tunnel.run_remote(
        f"cd {SITE_DIR} && node publish_ai.js", timeout=180
    )
    print(stdout)
    if stderr.strip():
        print("--- stderr ---")
        print(stderr.strip()[:2000])
    sys.exit(rc)


if __name__ == "__main__":
    main()
