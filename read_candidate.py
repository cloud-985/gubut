"""从服务器 pending-articles.json 读取候选文章（前 N 条）"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ssh_tunnel import run_remote, REMOTE_BASE


def read_candidates(limit=8, min_plain_len=400):
    path = f"{REMOTE_BASE}/pending-articles.json"
    raw = run_remote(f"test -f {path} && cat {path} || echo '[]'")
    try:
        arr = json.loads(raw.strip() or "[]")
    except json.JSONDecodeError as e:
        print(f"[ERR] 解析 pending-articles.json 失败: {e}")
        return []

    # 过滤掉内容太短的，保留前 limit 条完整内容
    arr = [a for a in arr if (a.get("plain_text_length") or 0) >= min_plain_len or a.get("content_html")]
    picks = arr[:limit]
    print(f"共 {len(arr)} 条，返回前 {len(picks)} 条候选")
    return picks


if __name__ == "__main__":
    picks = read_candidates()
    out_path = "/workspace/candidates.json"
    json.dump(picks, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"已写入 {out_path}")
    for i, a in enumerate(picks):
        print(f"\n--- #{i+1} ---")
        print(f"title: {a.get('title')}")
        print(f"url:   {a.get('url')}")
        print(f"len:   {a.get('plain_text_length')}")
        print(f"summary: {(a.get('summary') or '')[:200]}")
