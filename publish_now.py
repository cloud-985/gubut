#!/usr/bin/env python3
"""读取 /workspace/ai_article.json，上传并发布到 gubut.com。

发布动作复用服务器上现有的 lib/ 能力，与 auto-publish.js 保持一致：
1. 追加文章到 articles.json（按 id 去重）
2. 记录到 .published-articles.json
3. 生成文章页（含完整 SEO 标签）到 new/article-{id}.html
4. 更新 sitemap.xml
5. 修复文件属主
"""

import json

import ssh_tunnel

AI_ARTICLE_LOCAL = "/workspace/ai_article.json"
AI_ARTICLE_REMOTE = "/www/wwwroot/gubut/ai_article.json"
NODE_SCRIPT_REMOTE = "/www/wwwroot/gubut/.publish_now_article.js"
NODE_SCRIPT_LOCAL = "/workspace/.publish_now_article.js"

NODE_SCRIPT = r"""
const fs = require('fs');
const path = require('path');
const { mutateArticles, writeFileAtomic } = require('/www/wwwroot/gubut/lib/articles-store');
const { renderArticleHtml } = require('/www/wwwroot/gubut/lib/article-renderer');
const { writeSitemap } = require('/www/wwwroot/gubut/lib/sitemap');
const { articleFileName } = require('/www/wwwroot/gubut/lib/article-id');
const { chown, chownRecursive } = require('/www/wwwroot/gubut/lib/chown');

const SITE_DIR = '/www/wwwroot/gubut';
const ARTICLES_JSON = path.join(SITE_DIR, 'articles.json');
const PUBLISHED_LOG = path.join(SITE_DIR, '.published-articles.json');
const AI_ARTICLE_JSON = path.join(SITE_DIR, 'ai_article.json');

const article = JSON.parse(fs.readFileSync(AI_ARTICLE_JSON, 'utf8'));

// 与现有 articles.json 结构保持一致（不含 keywords）
const listArticle = {
  id: article.id,
  title: article.title,
  content: article.content,
  date: article.date,
  source: article.source,
};

const result = mutateArticles((list) => {
  if (list.some((a) => String(a.id) === String(listArticle.id))) {
    return null; // 已存在，放弃写入
  }
  list.unshift(listArticle);
  return list;
}, { filePath: ARTICLES_JSON });

if (!result.written) {
  console.log(JSON.stringify({ ok: false, error: '文章 id 已存在，跳过发布', id: article.id }));
  process.exit(0);
}
const articles = result.articles;

let published = [];
try { published = JSON.parse(fs.readFileSync(PUBLISHED_LOG, 'utf8')); } catch (e) {}
published.push({
  titleKey: (article.title || '').substring(0, 30).toLowerCase(),
  publishedAt: new Date().toISOString(),
  articleId: article.id,
});
writeFileAtomic(PUBLISHED_LOG, JSON.stringify(published, null, 2));

const newDir = path.join(SITE_DIR, 'new');
if (!fs.existsSync(newDir)) fs.mkdirSync(newDir);
const pagePath = path.join(newDir, articleFileName(article.id));
writeFileAtomic(pagePath, renderArticleHtml(article));

const sitemapResult = writeSitemap(articles, { filePath: path.join(SITE_DIR, 'sitemap.xml') });

chown([pagePath, ARTICLES_JSON, PUBLISHED_LOG]);
chownRecursive(newDir);

console.log(JSON.stringify({
  ok: true,
  id: article.id,
  title: article.title,
  url: 'https://www.gubut.com/new/' + articleFileName(article.id),
  pagePath: pagePath,
  articlesCount: articles.length,
  sitemapUrls: sitemapResult.count,
}));
"""


def main():
    with open(AI_ARTICLE_LOCAL, encoding="utf-8") as f:
        article = json.load(f)

    for key in ("id", "title", "date", "source", "keywords", "content"):
        if key not in article:
            raise SystemExit("ai_article.json 缺少字段: " + key)
    if not (8 <= len(article["keywords"]) <= 15):
        raise SystemExit("keywords 数量应为 8-15，当前 %d" % len(article["keywords"]))

    print("上传 ai_article.json ...")
    ssh_tunnel.upload(AI_ARTICLE_LOCAL, AI_ARTICLE_REMOTE)

    with open(NODE_SCRIPT_LOCAL, "w", encoding="utf-8") as f:
        f.write(NODE_SCRIPT)
    ssh_tunnel.upload(NODE_SCRIPT_LOCAL, NODE_SCRIPT_REMOTE)

    print("执行发布 ...")
    out, err = ssh_tunnel.run_remote(
        "cd /www/wwwroot/gubut && node " + NODE_SCRIPT_REMOTE
    )

    ssh_tunnel.run_remote("rm -f " + NODE_SCRIPT_REMOTE)

    print(out.strip())
    if err.strip():
        print("[stderr]", err.strip())


if __name__ == "__main__":
    main()
