#!/usr/bin/env python3
"""读取服务器 pending-articles.json 前 N 篇候选完整内容。"""
import json
import sys
import ssh_tunnel as s

PENDING = "/www/wwwroot/gubut/pending-articles.json"
DEFAULT_N = 8


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_N
    out, err, code = s.run_remote(f"cat {PENDING}", timeout=60)
    if code != 0 or not out.strip():
        print("读取失败:", err)
        return
    try:
        items = json.loads(out)
    except json.JSONDecodeError as e:
        print("JSON 解析失败:", e)
        print(out[:2000])
        return
    print(f"候选总数: {len(items)}，展示前 {n} 篇\n")
    for i, it in enumerate(items[:n], 1):
        print("=" * 70)
        print(f"[{i}] 标题: {it.get('title')}")
        print(f"链接: {it.get('link')}")
        print(f"发布时间: {it.get('pubDate')}")
        print("描述:")
        print(it.get("description"))
        print()


if __name__ == "__main__":
    main()
