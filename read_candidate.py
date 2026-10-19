import sys
import json

sys.path.insert(0, "/workspace")
import ssh_tunnel


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    out, err = ssh_tunnel.read_remote("/www/wwwroot/gubut/pending-articles.json")
    if err.strip():
        print("读取失败:", err)
        return
    try:
        data = json.loads(out)
    except Exception as e:
        print("JSON 解析失败:", e)
        print(out[:2000])
        return
    if not data:
        print("0 篇候选文章，跳过当日。")
        return
    print(f"候选总数: {len(data)}，显示前 {min(n, len(data))} 篇完整内容：")
    for i, a in enumerate(data[:n]):
        print("=" * 70)
        print(f"[{i}] 标题: {a.get('title', '')}")
        print(f"链接: {a.get('link', '')}")
        print(f"发布时间: {a.get('pubDate', '')}")
        print(f"描述: {a.get('description', '')}")
        print()


if __name__ == "__main__":
    main()
