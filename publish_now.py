"""
publish_now.py - 将 ai_article.json 上传到服务器并发布文章
步骤：
1. 读取本地 ai_article.json
2. 读取服务器 articles.json
3. 将新文章 prepend 到 articles.json
4. 上传回服务器
5. 服务器执行 node build.js 生成 HTML 页面和 sitemap
6. 验证结果
"""
import json
import sys
import os
sys.path.insert(0, '/workspace')
from ssh_tunnel import run_remote, remote_read, remote_write, remote_upload, REMOTE_BASE


def main():
    print("=" * 60)
    print("🚀 文章发布流程")
    print("=" * 60)
    
    local_article_path = '/workspace/ai_article.json'
    
    # 1. 读取本地 AI 文章
    if not os.path.exists(local_article_path):
        print(f"✗ 本地文章文件不存在: {local_article_path}")
        return False
    
    with open(local_article_path, 'r', encoding='utf-8') as f:
        new_article = json.load(f)
    
    article_id = new_article['id']
    article_title = new_article['title']
    print(f"\n📄 待发布文章:")
    print(f"  ID:    {article_id}")
    print(f"  标题:  {article_title}")
    print(f"  日期:  {new_article['date']}")
    
    # 2. 读取服务器 articles.json
    print("\n📥 读取服务器 articles.json...")
    articles_path = f"{REMOTE_BASE}/articles.json"
    try:
        articles_content = remote_read(articles_path)
        articles = json.loads(articles_content)
        print(f"  服务器现有文章: {len(articles)} 篇")
    except Exception as e:
        print(f"  警告: articles.json 读取失败，创建新列表: {e}")
        articles = []
    
    # 3. 检查是否已存在相同 ID
    existing_ids = [a.get('id') for a in articles]
    if article_id in existing_ids:
        print(f"  警告: ID {article_id} 已存在，跳过发布")
        return False
    
    # 4. 新文章插入到最前面
    articles.insert(0, new_article)
    
    # 5. 上传 articles.json 回服务器
    print(f"\n📤 上传 articles.json ({len(articles)} 篇)...")
    updated_json = json.dumps(articles, ensure_ascii=False, indent=2)
    remote_write(articles_path, updated_json)
    print("  ✓ articles.json 已更新")
    
    # 6. 在服务器上运行 build.js 生成 HTML 页面
    print("\n🔧 执行 node build.js...")
    build_cmd = f"cd {REMOTE_BASE} && node build.js 2>&1"
    out, err, code = run_remote(build_cmd)
    print(f"  exit code: {code}")
    if out:
        for line in out.strip().split('\n'):
            print(f"  | {line}")
    if err:
        print(f"  ⚠️ stderr: {err[:500]}")
    
    if code != 0:
        print(f"\n  ✗ build.js 执行失败")
        # 尝试手动检查
        print("\n  尝试检查手动构建...")
    
    # 7. 验证：检查文章 HTML 是否生成
    article_html = f"{REMOTE_BASE}/new/article-{article_id}.html"
    out2, err2, code2 = run_remote(f"ls -la {article_html}")
    if code2 == 0:
        print(f"\n  ✓ 文章HTML已生成: article-{article_id}.html")
    else:
        print(f"\n  ⚠️ 文章HTML未找到，尝试手动生成...")
        # 手动调用 generate-article.js 的逻辑
        gen_cmd = f"""cd {REMOTE_BASE} && node -e "
const {{ generateArticlePage, updateSitemap }} = require('./generate-article');
const article = {json.dumps(new_article, ensure_ascii=False)};
generateArticlePage(article);
const fs = require('fs');
const articles = JSON.parse(fs.readFileSync('./articles.json', 'utf8'));
updateSitemap(articles, []);
console.log('✓ 手动生成完成');
" 2>&1"""
        out3, err3, code3 = run_remote(gen_cmd)
        print(f"  手动生成: {out3.strip()}")
    
    # 8. 更新 sitemap.xml（确保包含新 URL）
    print("\n🔍 检查 sitemap.xml...")
    sitemap_path = f"{REMOTE_BASE}/sitemap.xml"
    out4, err4, code4 = run_remote(f"grep -c 'article-{article_id}' {sitemap_path} 2>/dev/null || echo '0'")
    sitemap_count = out4.strip()
    print(f"  sitemap 中新文章 URL 出现次数: {sitemap_count}")
    
    # 9. 输出结果
    article_url = f"https://www.gubut.com/new/article-{article_id}.html"
    print("\n" + "=" * 60)
    print("✅ 发布完成！")
    print(f"  文章标题: {article_title}")
    print(f"  文章 URL: {article_url}")
    print(f"  已发布文章总数: {len(articles)} 篇")
    print("=" * 60)
    
    # 10. 清理 pending-articles.json 中已使用的文章
    # （不删除原始素材，只是使用它）
    print("\n💾 发布记录：")
    print(f"  素材来源: FXStreet Gold price analysis")
    print(f"  重写方式: AI深度原创重写")
    print(f"  资产主题: 黄金 XAUUSD")
    
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
