"""读取服务器 pending-articles.json 前 N 篇候选文章完整内容。"""
import json
import sys
import ssh_tunnel

PENDING = "/www/wwwroot/gubut/pending-articles.json"

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    out, err, code = ssh_tunnel.run_remote(f"cat {PENDING}", timeout=60)
    if code != 0:
        print("读取失败:", err or out)
        raise SystemExit(code)
    data = json.loads(out)
    print(f"共 {len(data)} 篇候选文章, 显示前 {n} 篇:\n")
    for i, item in enumerate(data[:n]):
        print("=" * 70)
        print(f"[{i}] {item.get('title', '')}")
        print(f"链接: {item.get('link', '')}")
        print(f"日期: {item.get('pubDate', '')}")
        print(f"描述: {item.get('description', '')}")
    print("\n" + "=" * 70)
