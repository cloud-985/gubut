"""
读取服务器上的pending-articles.json候选文章完整内容
参考：使用ssh_tunnel.run_remote执行远程命令
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ssh_tunnel import run_remote, REMOTE_DIR
import json


def read_pending_articles(limit=8):
    """读取服务器pending-articles.json前N篇完整内容"""
    remote_file = f"{REMOTE_DIR}/pending-articles.json"
    
    # 检查文件是否存在
    check_cmd = f"test -f {remote_file} && echo 'EXISTS' || echo 'NOT_FOUND'"
    check_result = run_remote(check_cmd).strip()
    
    if "NOT_FOUND" in check_result:
        print(f"服务器上未找到文件: {remote_file}")
        return []
    
    # 读取文件内容
    content = run_remote(f"cat {remote_file}")
    
    try:
        articles = json.loads(content)
        print(f"成功读取 {len(articles)} 篇候选文章")
        
        # 取前limit篇
        selected = articles[:limit]
        print(f"\n=== 前{len(selected)}篇候选文章摘要 ===")
        for i, art in enumerate(selected, 1):
            title = art.get("title", "无标题")
            source = art.get("source", "")
            # 粗略统计字数
            content_text = art.get("content", "")
            word_count = len(content_text)
            print(f"  [{i}] {title}")
            print(f"      来源: {source} | 字数: {word_count}")
            if art.get("link"):
                print(f"      链接: {art.get('link')}")
        
        return selected
        
    except json.JSONDecodeError as e:
        print(f"解析JSON失败: {e}")
        print(f"原始内容前500字符: {content[:500]}")
        return []


if __name__ == "__main__":
    limit = 8
    if len(sys.argv) > 1:
        try:
            limit = int(sys.argv[1])
        except ValueError:
            pass
    
    articles = read_pending_articles(limit)
    
    # 保存到本地供参考
    if articles:
        local_file = "/workspace/pending_candidates_local.json"
        with open(local_file, "w", encoding="utf-8") as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
        print(f"\n本地副本已保存到: {local_file}")
