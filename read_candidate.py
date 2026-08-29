"""
读取远程服务器 pending-articles.json 前5-8篇完整内容
参考：使用 ssh_tunnel.run_remote 或 read_remote_json 执行
"""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ssh_tunnel import REMOTE_DIR, read_remote_json


def load_candidates(n=8):
    """从远程加载前N篇候选文章"""
    remote_path = f"{REMOTE_DIR}/pending-articles.json"
    print(f"读取远程文件: {remote_path}")
    try:
        data = read_remote_json(remote_path)
    except FileNotFoundError:
        print("ERROR: pending-articles.json 不存在")
        return []
    except json.JSONDecodeError as e:
        print(f"ERROR: JSON解析失败 {e}")
        return []

    print(f"共读取 {len(data)} 篇候选")
    # 优先选择有full_content的
    with_content = [x for x in data if x.get("full_content") and len(x.get("full_content", "")) > 300]
    print(f"其中包含完整正文的: {len(with_content)} 篇")

    result = with_content[:n] if with_content else data[:n]

    # 打印概览
    for i, a in enumerate(result):
        title = a.get("title", "(无标题)")[:80]
        asset = a.get("asset", "?")
        has_full = "有全文" if a.get("full_content") and len(a.get("full_content", "")) > 300 else "仅摘要"
        summary_len = len(a.get("summary", ""))
        full_len = len(a.get("full_content", ""))
        print(f"  [{i+1}] [{asset}] {title} | {has_full} | 摘要{summary_len}字 / 全文{full_len}字")
    return result


def print_full(idx, candidates):
    """详细打印某一篇的完整内容"""
    if idx < 0 or idx >= len(candidates):
        print("索引超出范围")
        return
    a = candidates[idx]
    print("\n" + "=" * 80)
    print(f"标题: {a.get('title')}")
    print(f"资产: {a.get('asset')}  |  来源: {a.get('link')}")
    print(f"发布: {a.get('published')}")
    print("=" * 80)
    print("【摘要】")
    print(a.get("summary", "")[:1000])
    print("\n【完整正文】")
    print(a.get("full_content", "")[:5000])
    if len(a.get("full_content", "")) > 5000:
        print(f"... (截断，共 {len(a['full_content'])} 字)")
    print("=" * 80)


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    candidates = load_candidates(n)
    # 如果传入第二个参数（索引），打印该篇详细内容
    if len(sys.argv) > 2:
        idx = int(sys.argv[2]) - 1
        print_full(idx, candidates)
