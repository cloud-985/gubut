"""将 /workspace/ai_article.json 发布到 gubut.com：
  1) 追加到服务器 articles.json
  2) 生成文章 HTML 页面（套用 generate-article.js 模板）
  3) 更新 sitemap.xml
"""
import sys
import os
import json
import time
import re
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ssh_tunnel import run_remote, write_remote_file, upload_local_to_remote, REMOTE_BASE

SERVER_NEW = f"{REMOTE_BASE}/new"
TEMPLATE_META_KEYWORDS = "区块链策略开发, 量化交易策略, 数据采集, 行情数据接口, K线数据, 交易所API, 策略回测, Web3数据, 区块链数据分析, 自动化交易"


def beijing_now():
    """返回北京时间字符串 YYYY/MM/DD HH:MM:SS"""
    bj = timezone(timedelta(hours=8))
    return datetime.now(bj).strftime("%Y/%m/%d %H:%M:%S")


def load_server_articles():
    path = f"{REMOTE_BASE}/articles.json"
    raw = run_remote(f"test -f {path} && cat {path} || echo '[]'")
    try:
        return json.loads(raw.strip() or "[]")
    except json.JSONDecodeError:
        return []


def build_article_html(article):
    """基于 generate-article.js 的模板生成完整 SEO 文章页"""
    title = article["title"]
    aid = article["id"]
    date = article["date"]
    keywords = ", ".join(article.get("keywords", [])) if isinstance(article.get("keywords"), list) else str(article.get("keywords", ""))
    desc = article.get("description") or (title + " - 谷比算力聚焦区块链与MT5量化交易策略")
    content = article["content"]

    # 用文章自身 keywords + 默认行业关键词组合 meta keywords
    meta_kws = (keywords + ", " + TEMPLATE_META_KEYWORDS).strip(", ")

    html = f"""<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="shortcut icon" href="../favicon.ico" type="image/x-icon">
    <title>{title} - 谷比算力</title>
    <meta name="keywords" content="{meta_kws}">
    <meta name="description" content="{desc}">
    <meta name="robots" content="index,follow">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{desc}">
    <meta property="og:type" content="article">
    <meta property="og:url" content="https://www.gubut.com/new/article-{aid}.html">
    <meta property="og:site_name" content="谷比算力">
    <link rel="canonical" href="https://www.gubut.com/new/article-{aid}.html">
    <!-- 引入Font Awesome -->
    <link href="https://cdn.jsdelivr.net/npm/font-awesome@4.7.0/css/font-awesome.min.css" rel="stylesheet">
    <!-- 引入Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- 引入Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <!-- 引入样式文件 -->
    <link rel="stylesheet" href="../styles.css">
    <!-- 引入语言切换组件 -->
    <script src="../lang.js"></script>
    <!-- 自定义配置 -->
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    colors: {{
                        primary: '#4F46E5',
                        secondary: '#10B981',
                        dark: '#111827',
                        light: '#F9FAFB'
                    }},
                    fontFamily: {{
                        inter: ['Inter', 'system-ui', 'sans-serif'],
                    }},
                }}
            }}
        }}
    </script>
</head>
<body>
    <!-- 导航栏占位符 -->
    <div id="navbar-placeholder"></div>

    <div class="article-container">
        <article class="article-content">
            <h1>{title}</h1>
            <div class="article-meta">
                <span data-lang="zh">发布于: </span><span data-lang="en" class="hidden-lang">Published: </span>{date}
                <span style="margin-left:10px;color:#888;">来源: {article.get('source','谷比算力原创')}</span>
            </div>
            <div class="article-body">
                {content}
            </div>

            <div class="related-articles">
                <h3>更多文章</h3>
                <div id="related-articles-list">
                    <p>加载中...</p>
                </div>
                <div class="all-articles-link">
                    <a href="../articles.html">查看所有文章 →</a>
                </div>
            </div>
        </article>
    </div>

    <!-- 数据信号服务板块 -->
    <section class="py-8 min-h-[20vh] flex items-center justify-center bg-gradient-to-br from-blue-900 via-blue-800 to-purple-700 text-white">
        <div class="container mx-auto px-2 sm:px-6 lg:px-8 w-full">
            <div class="text-center max-w-3xl mx-auto mb-16">
                <h2 class="text-[clamp(1.5rem,3vw,2.5rem)] font-bold mb-4" data-lang-key="signals.title">数据信号服务</h2>
                <p class="text-blue-100 text-lg" data-lang-key="signals.subtitle">快人一步的行情数据，让你在别人还没反应时，就已经进场</p>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-8 justify-items-center">
                <div class="bg-white/10 backdrop-blur-md rounded-xl p-8 border border-white/20 hover:border-blue-300/50 transition-all duration-300 hover:shadow-lg hover:shadow-blue-400/20 transform hover:-translate-y-1 max-w-sm w-full">
                    <div class="w-16 h-16 mb-6 mx-auto flex items-center justify-center text-3xl">🔔</div>
                    <h3 class="text-xl font-bold mb-3 text-center">新币上线提醒</h3>
                    <p class="text-blue-100 text-center">第一时间获取新币上线信息，抢占先机</p>
                </div>
                <div class="bg-white/10 backdrop-blur-md rounded-xl p-8 border border-white/20 hover:border-blue-300/50 transition-all duration-300 hover:shadow-lg hover:shadow-blue-400/20 transform hover:-translate-y-1 max-w-sm w-full">
                    <div class="w-16 h-16 mb-6 mx-auto flex items-center justify-center text-3xl">🚀</div>
                    <h3 class="text-xl font-bold mb-3 text-center">市场异动推送</h3>
                    <p class="text-blue-100 text-center">实时推送资金流异常、盘口深度变化等关键信号</p>
                </div>
                <div class="bg-white/10 backdrop-blur-md rounded-xl p-8 border border-white/20 hover:border-blue-300/50 transition-all duration-300 hover:shadow-lg hover:shadow-blue-400/20 transform hover:-translate-y-1 max-w-sm w-full">
                    <div class="w-16 h-16 mb-6 mx-auto flex items-center justify-center text-3xl">💎</div>
                    <h3 class="text-xl font-bold mb-3 text-center">VIP社群服务</h3>
                    <p class="text-blue-100 text-center">高质量策略交流、实盘跟单、EA 共享与回测数据</p>
                </div>
            </div>
        </div>
    </section>

    <!-- 导航栏 & 社交组件注入 -->
    <script>
        // 注入导航
        const navHtml = `
        <header class="fixed top-0 left-0 right-0 bg-white/80 backdrop-blur-md border-b border-gray-100 z-50 transition-all duration-300 shadow-sm">
          <div class="container mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex items-center justify-between h-16 sm:h-20">
              <a href="../index.html" class="flex items-center space-x-2 hover:opacity-90 transition-opacity duration-300">
                <img src="../img/logo.png" alt="谷比算力 Logo" class="h-8 sm:h-10 w-auto">
                <span class="text-lg sm:text-xl font-bold text-primary">谷比算力</span>
              </a>
              <div class="flex items-center space-x-4">
                <a href="https://t.me/mevjk_bot" target="_blank" class="hidden md:block px-4 py-2 rounded-full bg-primary text-white hover:bg-primary/90 font-medium transition-all-300 shadow-md hover:shadow-lg">立即开始</a>
              </div>
            </div>
          </div>
        </header>`;
        document.getElementById('navbar-placeholder').innerHTML = navHtml;
    </script>
</body>
</html>
"""
    return html


def update_sitemap(articles):
    """基于 articles.json 重新生成 sitemap.xml"""
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        '  <url><loc>https://www.gubut.com/</loc><changefreq>daily</changefreq><priority>1.0</priority></url>',
        '  <url><loc>https://www.gubut.com/articles.html</loc><changefreq>daily</changefreq><priority>0.8</priority></url>',
        '  <url><loc>https://www.gubut.com/admin.html</loc><changefreq>weekly</changefreq><priority>0.5</priority></url>',
        '  <url><loc>https://www.gubut.com/privacy.html</loc><changefreq>monthly</changefreq><priority>0.3</priority></url>',
        '  <url><loc>https://www.gubut.com/terms.html</loc><changefreq>monthly</changefreq><priority>0.3</priority></url>',
    ]
    for a in sorted(articles, key=lambda x: x.get("id", 0), reverse=True):
        aid = a.get("id")
        if not aid:
            continue
        lines.append(
            f'  <url><loc>https://www.gubut.com/new/article-{aid}.html</loc>'
            f'<lastmod>{a.get("date","").replace("/","-")}</lastmod>'
            f'<changefreq>weekly</changefreq><priority>0.7</priority></url>'
        )
    lines.append("</urlset>")
    return "\n".join(lines)


def main():
    local_json = "/workspace/ai_article.json"
    if not os.path.exists(local_json):
        print("[ERR] /workspace/ai_article.json 不存在，请先生成")
        sys.exit(1)

    article = json.load(open(local_json, encoding="utf-8"))
    if not article.get("date"):
        article["date"] = beijing_now()
    print(f"发布文章：{article['title']}")
    print(f"  id   = {article['id']}")
    print(f"  date = {article['date']}")

    # 1) 合并 articles.json（本地写好 → SFTP 上传，避免 echo+base64 对大文件 EOF）
    articles = load_server_articles()
    exists = any(str(a.get("id")) == str(article["id"]) for a in articles)
    if exists:
        print("[WARN] id 已存在，跳过 JSON 合并")
    else:
        articles.append(article)
    merged_json_path = "/workspace/_tmp_articles_merged.json"
    with open(merged_json_path, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    upload_local_to_remote(merged_json_path, f"{REMOTE_BASE}/articles.json")
    run_remote(f"chmod 644 {REMOTE_BASE}/articles.json")
    print(f"  articles.json 更新完成，共 {len(articles)} 篇")

    # 2) 生成并上传文章页 HTML
    html = build_article_html(article)
    local_html = f"/workspace/article-{article['id']}.html"
    with open(local_html, "w", encoding="utf-8") as f:
        f.write(html)
    remote_html = f"{SERVER_NEW}/article-{article['id']}.html"
    upload_local_to_remote(local_html, remote_html)
    run_remote(f"chmod 644 {remote_html}")
    print(f"  上传 {remote_html} 完成")

    # 3) 更新 sitemap.xml（同样本地写好再 SFTP）
    sitemap = update_sitemap(articles)
    local_sitemap = "/workspace/_tmp_sitemap.xml"
    with open(local_sitemap, "w", encoding="utf-8") as f:
        f.write(sitemap)
    upload_local_to_remote(local_sitemap, f"{REMOTE_BASE}/sitemap.xml")
    run_remote(f"chmod 644 {REMOTE_BASE}/sitemap.xml")
    print("  sitemap.xml 更新完成")

    # 清理临时文件
    for tmp in [merged_json_path, local_sitemap]:
        if os.path.exists(tmp):
            os.remove(tmp)

    url = f"https://www.gubut.com/new/article-{article['id']}.html"
    print(f"\n✅ 发布成功！URL: {url}")


if __name__ == "__main__":
    main()
