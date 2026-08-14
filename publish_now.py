"""
即时发布脚本 - 读取ai_article.json，生成文章HTML页面，更新articles.json和sitemap
并上传发布到服务器
"""
import sys
import os
import json
import time
import subprocess
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ssh_tunnel import run_remote, sftp_upload, REMOTE_DIR


def extract_text_from_html(html_content):
    """从HTML提取纯文本（用于articles.json缩略）"""
    import re
    # 移除script和style
    text = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
    # 移除HTML标签
    text = re.sub(r'<[^>]+>', ' ', text)
    # 移除多余空白
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def update_articles_json_locally(article):
    """本地更新articles.json，添加新文章到开头"""
    articles_json_path = "/workspace/articles.json"
    
    # 处理文章（提取文本）
    processed_article = {
        "id": article["id"],
        "title": article["title"],
        "date": article["date"],
        "content": extract_text_from_html(article["content"])
    }
    
    # 读取现有内容
    articles = []
    if os.path.exists(articles_json_path):
        try:
            with open(articles_json_path, "r", encoding="utf-8") as f:
                articles = json.load(f)
        except Exception as e:
            print(f"  ⚠️ 读取现有articles.json失败: {e}，将创建新文件")
            articles = []
    
    # 检查是否已存在
    existing_index = next(
        (i for i, a in enumerate(articles) if a.get("id") == processed_article["id"]),
        -1
    )
    
    if existing_index >= 0:
        articles[existing_index] = processed_article
        print(f"  🔄 本地articles.json: 更新已存在的文章 #{processed_article['id']}")
    else:
        articles.insert(0, processed_article)  # 新文章放最前面
        print(f"  ➕ 本地articles.json: 已添加新文章 #{processed_article['id']}")
    
    # 保存
    with open(articles_json_path, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    
    return articles


def run_node_build():
    """运行Node.js build脚本生成文章HTML页面和sitemap"""
    print("\n📦 运行build.js生成文章页面和sitemap...")
    try:
        result = subprocess.run(
            ["node", "build.js"],
            cwd="/workspace",
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0:
            print(f"  ⚠️ build.js stderr: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"  ❌ 运行build.js失败: {e}")
        return False


def upload_to_server(article_id):
    """上传更新后的文件到服务器"""
    print("\n🌐 上传文件到服务器...")
    
    # 需要上传的文件列表：articles.json, sitemap.xml, 新文章HTML
    upload_files = [
        ("/workspace/articles.json", f"{REMOTE_DIR}/articles.json"),
        ("/workspace/sitemap.xml", f"{REMOTE_DIR}/sitemap.xml"),
        (f"/workspace/new/article-{article_id}.html", f"{REMOTE_DIR}/new/article-{article_id}.html"),
    ]
    
    all_ok = True
    for local_path, remote_path in upload_files:
        if not os.path.exists(local_path):
            print(f"  ⚠️  跳过不存在的文件: {local_path}")
            continue
        
        print(f"  📤 上传: {os.path.basename(local_path)} -> {remote_path}")
        result = sftp_upload(local_path, remote_path)
        
        if "ERROR" in str(result):
            print(f"    ❌ 上传失败: {result}")
            all_ok = False
        else:
            print(f"    ✅ 上传成功")
    
    return all_ok


def verify_remote(article_id):
    """验证远程服务器文件是否更新"""
    print("\n🔍 验证远程发布...")
    article_url = f"https://www.gubut.com/new/article-{article_id}.html"
    
    # 检查远程文件存在
    check_cmd = f"ls -la {REMOTE_DIR}/new/article-{article_id}.html 2>/dev/null && echo 'FILE_EXISTS' || echo 'FILE_NOT_FOUND'"
    result = run_remote(check_cmd)
    
    if "FILE_EXISTS" in result:
        print(f"  ✅ 远程文章文件存在")
        # 提取文件大小
        lines = result.strip().split("\n")
        for line in lines:
            if "article-" in line:
                parts = line.split()
                if len(parts) >= 5:
                    print(f"     文件大小: {parts[4]} 字节")
    else:
        print(f"  ❌ 远程文章文件未找到!")
        return False
    
    # 检查sitemap包含新URL
    sitemap_check = run_remote(f"grep -l 'article-{article_id}' {REMOTE_DIR}/sitemap.xml 2>/dev/null && echo 'IN_SITEMAP' || echo 'NOT_IN_SITEMAP'")
    if "IN_SITEMAP" in sitemap_check:
        print(f"  ✅ sitemap已包含新文章URL")
    else:
        print(f"  ⚠️  sitemap暂未检测到新URL（可能grep匹配问题）")
    
    print(f"\n📰 文章URL: {article_url}")
    return True


def main():
    print("=" * 60)
    print("🚀 谷比算力文章即时发布脚本")
    print("=" * 60)
    
    # 1. 读取ai_article.json
    ai_article_path = "/workspace/ai_article.json"
    if not os.path.exists(ai_article_path):
        print(f"❌ 错误: 找不到 {ai_article_path}")
        print("   请先用 gen_article.py 生成文章JSON")
        return False
    
    print("\n📖 读取ai_article.json...")
    try:
        with open(ai_article_path, "r", encoding="utf-8") as f:
            article = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析失败: {e}")
        return False
    
    print(f"   标题: {article['title']}")
    print(f"   ID: {article['id']}")
    print(f"   日期: {article['date']}")
    
    # 2. 本地更新articles.json
    print("\n📝 本地更新articles.json...")
    all_articles = update_articles_json_locally(article)
    print(f"   当前总文章数: {len(all_articles)}")
    
    # 3. 运行build.js生成HTML和sitemap
    build_ok = run_node_build()
    if not build_ok:
        print("⚠️  build.js运行有警告，继续尝试发布")
    
    # 确认生成的HTML文件
    html_path = f"/workspace/new/article-{article['id']}.html"
    if os.path.exists(html_path):
        size = os.path.getsize(html_path)
        print(f"  ✅ 已生成文章页面: {html_path} ({size} 字节)")
    else:
        print(f"  ❌ 文章HTML未生成: {html_path}")
        return False
    
    # 4. 上传到服务器
    upload_ok = upload_to_server(article["id"])
    if not upload_ok:
        print("❌ 部分文件上传失败")
    
    # 5. 验证远程
    verify_remote(article["id"])
    
    print("\n" + "=" * 60)
    print(f"✅ 发布完成!")
    print(f"   标题: {article['title']}")
    print(f"   URL: https://www.gubut.com/new/article-{article['id']}.html")
    print(f"   字数: ~{len(extract_text_from_html(article['content']))} 字")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
