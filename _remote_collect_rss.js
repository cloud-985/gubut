
const https = require('https');
const fs = require('fs');
const path = require('path');

const SITE_DIR = '/www/wwwroot/gubut';
const RSS_URL = 'https://www.tradingview.com/feed/';
const PENDING_FILE = path.join(SITE_DIR, 'pending-articles.json');

const ASSET_KEYWORDS = ['BTC', 'BITCOIN', 'ETH', 'ETHEREUM', 'XAUUSD', 'GOLD', 'NEAR', 'SOL', 'XRP', 'BNB', 'DOGE', 'ADA', 'AVAX', 'LINK', 'USDT', 'EURUSD', 'GBPUSD', 'USDJPY', 'CRYPTO'];

function httpsGet(url) {
  return new Promise((resolve, reject) => {
    https.get(url, { headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' } }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve(data));
    }).on('error', reject);
  });
}

function stripHtml(html) {
  return html.replace(/<[^>]+>/g, ' ').replace(/&[a-z]+;/g, ' ').replace(/\s+/g, ' ').trim();
}

async function main() {
  console.log('[采集] 开始采集 TradingView RSS...');
  const xml = await httpsGet(RSS_URL);
  console.log('[采集] RSS 长度:', xml.length);

  const items = [];
  const itemRegex = /<item>([\s\S]*?)<\/item>/g;
  let match;
  while ((match = itemRegex.exec(xml)) !== null) {
    const itemXml = match[1];
    const title = (itemXml.match(/<title>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?<\/title>/) || [])[1] || '';
    const link = (itemXml.match(/<link>(.*?)<\/link>/) || [])[1] || '';
    const desc = (itemXml.match(/<description>(?:<!\[CDATA\[)?([\s\S]*?)(?:\]\]>)?<\/description>/) || [])[1] || '';
    const pubDate = (itemXml.match(/<pubDate>(.*?)<\/pubDate>/) || [])[1] || '';

    items.push({
      title: stripHtml(title).trim(),
      link: link.trim(),
      description: stripHtml(desc).trim(),
      pubDate: pubDate.trim(),
    });
  }
  console.log('[采集] 解析到', items.length, '篇文章');

  // 过滤:必须包含明确的资产标的
  const wordMatch = (kws, text) => kws.some(k => new RegExp('\\b' + k + '\\b', 'i').test(text));
  const relevant = items.filter(item => {
    const text = item.title + ' ' + item.description;
    return wordMatch(ASSET_KEYWORDS, text);
  });
  console.log('[采集] 过滤后', relevant.length, '篇区块链/交易相关文章');

  // 读取已发布文章(用于去重)
  let publishedTitles = [];
  try {
    const pub = JSON.parse(fs.readFileSync(path.join(SITE_DIR, '.published-articles.json'), 'utf8'));
    publishedTitles = pub.map(p => p.titleKey);
  } catch (e) {}
  let existingZhTitles = [];
  try {
    const arts = JSON.parse(fs.readFileSync(path.join(SITE_DIR, 'articles.json'), 'utf8'));
    existingZhTitles = arts.map(a => (a.title || '').substring(0, 20));
  } catch (e) {}

  // 去重
  const unpublished = relevant.filter(item => {
    const titleKey = item.title.substring(0, 30).toLowerCase();
    if (publishedTitles.includes(titleKey)) return false;
    return true;
  });
  console.log('[采集] 去重后', unpublished.length, '篇未发布候选文章');

  // 保存候选文章到 pending-articles.json(覆盖式,只保留最新的候选)
  fs.writeFileSync(PENDING_FILE, JSON.stringify(unpublished, null, 2));
  console.log('[采集] 已保存候选文章到 pending-articles.json');
  console.log('');
  console.log('===== 候选文章列表 =====');
  unpublished.slice(0, 10).forEach((item, i) => {
    console.log((i + 1) + '. ' + item.title);
    console.log('   描述: ' + item.description.substring(0, 120) + '...');
    console.log('   链接: ' + item.link);
    console.log('');
  });
}

main().catch(e => { console.error('[错误]', e.message); process.exit(1); });
