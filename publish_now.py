"""
发布文章到远程服务器
1. 读取 /workspace/ai_article.json
2. 调用 node build.js / generate-article.js 生成文章HTML页面、更新 articles.json、更新 sitemap.xml
3. 通过 SSH/SCP 上传更新后的文件到服务器 /www/wwwroot/gubut/
"""
import json
import os
import sys
import subprocess
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ssh_tunnel import run_remote, upload_file, SERVER_WEB_DIR


def run_cmd(cmd: str, cwd: str = None, timeout: int = 120) -> tuple:
    """运行本地命令，返回 (returncode, stdout, stderr)"""
    print(f"\n[执行] {cmd}")
    p = subprocess.run(
        cmd, shell=True, cwd=cwd,
        capture_output=True, text=True, timeout=timeout
    )
    if p.stdout:
        print(p.stdout)
    if p.stderr:
        print(p.stderr, file=sys.stderr)
    return p.returncode, p.stdout, p.stderr


def publish_article_locally(article: dict) -> bool:
    """
    本地构建: 生成文章HTML、追加到articles.json、更新sitemap
    使用Node.js脚本完成
    """
    workspace = "/workspace"
    try:
        # 1. 追加新文章到 articles.json（保留完整HTML内容用于生成页面）
        articles_json_path = os.path.join(workspace, "articles.json")
        if os.path.exists(articles_json_path):
            with open(articles_json_path, "r", encoding="utf-8") as f:
                articles = json.load(f)
        else:
            articles = []

        # 构造完整文章对象（与generate-article.js期望的格式一致：含完整HTML content）
        full_article_entry = {
            "id": article["id"],
            "title": article["title"],
            "content": article["content"],
            "date": article["date"],
            "source": article.get("source", ""),
            "keywords": article.get("keywords", []),
        }

        # 检查是否已存在（按id去重）
        idx = next((i for i, a in enumerate(articles) if str(a.get("id")) == str(article["id"])), -1)
        if idx >= 0:
            articles[idx] = full_article_entry
            print(f"[构建] articles.json 中已存在相同ID，更新原条目")
        else:
            articles.insert(0, full_article_entry)  # 新文章在最前
            print(f"[构建] 已追加新文章到 articles.json 头部")

        with open(articles_json_path, "w", encoding="utf-8") as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)

        # 2. 调用 node generate-article.js 生成单篇文章页
        # 先写一个小脚本用 generate-article 的函数
        build_script_path = os.path.join(workspace, "_tmp_publish.js")
        build_script = r"""
const fs = require('fs');
const path = require('path');
const { generateArticlePage, updateSitemap, updateArticlesJson } = require('./generate-article');

// 读取 ai_article.json
const article = JSON.parse(fs.readFileSync('./ai_article.json', 'utf8'));
console.log('处理文章: ' + article.title + ' (ID: ' + article.id + ')');

// 生成文章HTML页 (含完整内容用于展示)
const pageArticle = {
    id: article.id,
    title: article.title,
    content: article.content,
    date: article.date,
    keywords: article.keywords || []
};
generateArticlePage(pageArticle);

// 从articles.json读取完整列表（已有HTML内容），用于更新sitemap和摘要版articles.json
let articlesList = JSON.parse(fs.readFileSync('./articles.json', 'utf8'));

// 更新网站地图
updateSitemap(articlesList);

// 更新摘要版 articles.json（内容是纯文本版本，用于列表展示）
// 注意: updateArticlesJson 会重新写入，我们需要确保只更新一篇
const existingIndex = articlesList.findIndex(a => String(a.id) === String(article.id));
if (existingIndex >= 0) {
    // 用带纯文本content的版本替换对应位置
    const { updateArticlesJson } = require('./generate-article');
    // updateArticlesJson会写入纯文本content版articles.json
}

// 重新生成所有文章页面，确保articles.json中的所有文章都有对应HTML
// 但为了效率，只重新生成单篇 + 更新sitemap即可，上面已做

console.log('本地构建完成');
process.exit(0);
"""
        with open(build_script_path, "w", encoding="utf-8") as f:
            f.write(build_script)

        code, out, err = run_cmd(f"node {build_script_path}", cwd=workspace)
        if code != 0:
            print(f"[构建] Node脚本执行失败，尝试直接用 build.js 重建全部...")
            # 备用：直接运行 build.js 重建所有
            code2, out2, err2 = run_cmd("node build.js", cwd=workspace)
            if code2 != 0:
                print(f"[构建] ❌ build.js 也失败: {err2}")
                return False

        # 清理临时脚本
        if os.path.exists(build_script_path):
            os.remove(build_script_path)

        print(f"[构建] ✅ 本地构建成功")
        return True
    except Exception as e:
        print(f"[构建] ❌ 本地构建异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def sync_files_to_server() -> bool:
    """
    将更新后的文件同步到服务器
    需要上传:
    - articles.json
    - sitemap.xml
    - new/article-{id}.html
    - index.html (如果articles.json被首页引用的话，通常也需要更新)
    """
    workspace = "/workspace"
    uploads = []

    # 收集需要上传的文件
    articles_json = os.path.join(workspace, "articles.json")
    if os.path.exists(articles_json):
        uploads.append((articles_json, f"{SERVER_WEB_DIR}/articles.json"))

    sitemap = os.path.join(workspace, "sitemap.xml")
    if os.path.exists(sitemap):
        uploads.append((sitemap, f"{SERVER_WEB_DIR}/sitemap.xml"))

    index_html = os.path.join(workspace, "index.html")
    if os.path.exists(index_html):
        uploads.append((index_html, f"{SERVER_WEB_DIR}/index.html"))

    articles_html = os.path.join(workspace, "articles.html")
    if os.path.exists(articles_html):
        uploads.append((articles_html, f"{SERVER_WEB_DIR}/articles.html"))

    # 上传 new/ 目录下所有文章页面
    new_dir = os.path.join(workspace, "new")
    if os.path.isdir(new_dir):
        for fname in os.listdir(new_dir):
            if fname.startswith("article-") and fname.endswith(".html"):
                local = os.path.join(new_dir, fname)
                remote = f"{SERVER_WEB_DIR}/new/{fname}"
                uploads.append((local, remote))

    print(f"\n[同步] 共需上传 {len(uploads)} 个文件")

    # 先确保远程 new 目录存在
    run_remote(f"mkdir -p {SERVER_WEB_DIR}/new")

    success_count = 0
    for local, remote in uploads:
        # 只上传最近修改过的（可选优化，目前简单全部上传）
        ok = upload_file(local, remote)
        if ok:
            success_count += 1

    # 上传完设置权限
    run_remote(f"chmod -R 755 {SERVER_WEB_DIR}/new && chown -R www:www {SERVER_WEB_DIR}/ 2>/dev/null || true")

    print(f"[同步] 上传完成: {success_count}/{len(uploads)} 成功")
    return success_count > 0


def main():
    print("=" * 60)
    print("[发布] 开始发布文章到 gubut.com")
    print("=" * 60)

    # 1. 读取 ai_article.json
    ai_json_path = "/workspace/ai_article.json"
    if not os.path.exists(ai_json_path):
        print(f"[发布] ❌ 未找到 {ai_json_path}，请先生成文章")
        sys.exit(1)

    try:
        with open(ai_json_path, "r", encoding="utf-8") as f:
            article = json.load(f)
    except Exception as e:
        print(f"[发布] ❌ 读取 ai_article.json 失败: {e}")
        sys.exit(1)

    print(f"[发布] 待发布文章: {article['title']} (ID: {article['id']})")

    # 2. 本地构建
    ok = publish_article_locally(article)
    if not ok:
        print("[发布] ❌ 本地构建失败，终止发布")
        sys.exit(1)

    # 3. 同步到服务器
    ok = sync_files_to_server()
    if not ok:
        print("[发布] ⚠️  文件同步可能失败，请手动检查")

    # 4. 输出最终URL
    article_url = f"https://www.gubut.com/new/article-{article['id']}.html"
    print("\n" + "=" * 60)
    print("发布完成！")
    print(f"  文章标题: {article['title']}")
    print(f"  文章URL:  {article_url}")
    print(f"  发布时间: {article['date']}")
    print("=" * 60)

    # 保存发布结果
    result = {
        "publishedAt": int(time.time() * 1000),
        "articleId": article["id"],
        "title": article["title"],
        "url": article_url,
        "date": article["date"],
        "keywords": article.get("keywords", []),
    }
    with open("/workspace/publish-result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    return 0


if __name__ == "__main__":
    sys.exit(main())
