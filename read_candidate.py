"""
读取远程服务器 pending-articles.json 中前5-8篇完整内容
"""
import json
import sys
import os

# 添加当前目录到路径，便于导入ssh_tunnel
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ssh_tunnel import run_remote, download_file, SERVER_WEB_DIR


def read_remote_pending_articles(top_n: int = 8) -> list:
    """
    从远程服务器读取 pending-articles.json
    
    策略:
    1. 先尝试用scp下载文件
    2. 失败则用cat命令读取
    3. 都失败则读取本地 run_collect.py 生成的 pending-articles-local.json
    """
    remote_file = f"{SERVER_WEB_DIR}/pending-articles.json"
    local_file = "/workspace/pending-articles-remote.json"
    local_fallback = "/workspace/pending-articles-local.json"

    articles = []

    # 方法1: SFTP下载
    try:
        print(f"[读取] 尝试下载远程文件: {remote_file}")
        ok = download_file(remote_file, local_file)
        if ok and os.path.exists(local_file):
            with open(local_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict) and "articles" in data:
                articles = data["articles"]
            elif isinstance(data, list):
                articles = data
            print(f"[读取] SFTP下载成功，共 {len(articles)} 篇")
    except Exception as e:
        print(f"[读取] SFTP下载失败: {e}")

    # 方法2: SSH cat读取
    if not articles:
        print(f"[读取] 尝试SSH cat读取...")
        code, out, err = run_remote(f"cat {remote_file} 2>/dev/null || echo '__EMPTY__'")
        if code == 0 and out.strip() and not out.strip().endswith("__EMPTY__"):
            try:
                data = json.loads(out)
                if isinstance(data, dict) and "articles" in data:
                    articles = data["articles"]
                elif isinstance(data, list):
                    articles = data
                print(f"[读取] SSH读取成功，共 {len(articles)} 篇")
            except Exception as e:
                print(f"[读取] SSH内容解析失败: {e}")

    # 方法3: 本地回退
    if not articles:
        print(f"[读取] 远程读取失败，尝试本地回退文件: {local_fallback}")
        if os.path.exists(local_fallback):
            try:
                with open(local_fallback, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict) and "articles" in data:
                    articles = data["articles"]
                elif isinstance(data, list):
                    articles = data
                print(f"[读取] 本地回退文件读取成功，共 {len(articles)} 篇")
            except Exception as e:
                print(f"[读取] 本地回退文件解析失败: {e}")

    # 取前N篇
    result = articles[:top_n]
    print(f"\n[读取] 最终选取前 {len(result)} 篇候选:")
    for i, a in enumerate(result):
        title = a.get("title", "N/A")[:70]
        asset = a.get("asset", "?")
        print(f"  [{i+1}] [{asset}] {title}")

    # 保存到标准文件供后续步骤使用
    output = {
        "loadedAt": __import__("time").time() * 1000,
        "count": len(result),
        "articles": result,
    }
    with open("/workspace/loaded-candidates.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"[读取] 已保存候选到 /workspace/loaded-candidates.json")

    return result


if __name__ == "__main__":
    n = 8
    if len(sys.argv) > 1:
        try:
            n = int(sys.argv[1])
        except:
            pass
    arts = read_remote_pending_articles(n)
    if not arts:
        print("\n[警告] 0篇候选，后续流程将跳过")
        sys.exit(0)
