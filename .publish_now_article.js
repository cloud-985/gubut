
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
