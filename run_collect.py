#!/usr/bin/env python3
"""采集 TradingView RSS 候选文章并写入服务器 pending-articles.json。

由于本沙箱无法直连 tradingview.com（代理 SSL 失败），RSS 抓取委托给
服务器端 node 执行（服务器可直连 TradingView，auto-publish.js 已使用该方式）。
"""
import json
import ssh_tunnel

RSS_URL = "https://www.tradingview.com/feed/"
REMOTE_OUT = "/www/wwwroot/gubut/pending-articles.json"

# 资产标的过滤关键词（与服务器 auto-publish.js 保持一致）
ASSET_KEYWORDS = [
    "BTC", "BITCOIN", "ETH", "ETHEREUM", "XAUUSD", "GOLD", "NEAR",
    "SOL", "XRP", "BNB", "DOGE", "ADA", "AVAX", "LINK", "USDT",
    "EURUSD", "GBPUSD", "USDJPY", "CRYPTO",
]

NODE_SCRIPT = r"""
const https = require('https');
const fs = require('fs');
const RSS_URL = 'https://www.tradingview.com/feed/';
const OUT = '/www/wwwroot/gubut/pending-articles.json';
const ASSET_KEYWORDS = ['BTC','BITCOIN','ETH','ETHEREUM','XAUUSD','GOLD','NEAR','SOL','XRP','BNB','DOGE','ADA','AVAX','LINK','USDT','EURUSD','GBPUSD','USDJPY','CRYPTO'];

function httpsGet(url) {
  return new Promise((resolve, reject) => {
    https.get(url, { headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' } }, (res) => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => resolve(data));
    }).on('error', reject);
  });
}
function stripHtml(h) {
  return h.replace(/<[^>]+>/g, ' ').replace(/&[a-z]+;/g, ' ').replace(/\s+/g, ' ').trim();
}

(async () => {
  const xml = await httpsGet(RSS_URL);
  const items = [];
  const re = /<item>([\s\S]*?)<\/item>/g;
  let m;
  while ((m = re.exec(xml)) !== null) {
    const x = m[1];
    const title = (x.match(/<title>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?<\/title>/) || [])[1] || '';
    const link = (x.match(/<link>(.*?)<\/link>/) || [])[1] || '';
    const desc = (x.match(/<description>(?:<!\[CDATA\[)?([\s\S]*?)(?:\]\]>)?<\/description>/) || [])[1] || '';
    const pubDate = (x.match(/<pubDate>(.*?)<\/pubDate>/) || [])[1] || '';
    items.push({
      title: stripHtml(title).trim(),
      link: link.trim(),
      description: stripHtml(desc).trim().substring(0, 2000),
      pubDate: pubDate.trim(),
    });
  }
  const wordMatch = (kws, t) => kws.some(k => new RegExp('\\b' + k + '\\b', 'i').test(t));
  const relevant = items.filter(i => wordMatch(ASSET_KEYWORDS, i.title + ' ' + i.description));
  fs.writeFileSync(OUT, JSON.stringify(relevant, null, 2));
  console.log('TOTAL=' + items.length + ' RELEVANT=' + relevant.length);
  relevant.forEach((i, idx) => console.log(idx + ' | ' + i.pubDate + ' | ' + i.title));
})().catch(e => { console.log('ERR=' + e.message); process.exit(1); });
"""


def main():
    remote_script = "/tmp/collect_rss.js"
    ssh_tunnel.put_file_bytes(remote_script, NODE_SCRIPT.encode("utf-8"))
    out, err, code = ssh_tunnel.run_remote("node " + remote_script)
    print(out, end="")
    if err:
        print("STDERR:", err)
    if code != 0:
        print("[采集失败] exit code", code)
        raise SystemExit(code)

    # 回读统计
    raw = ssh_tunnel.get_file_bytes(REMOTE_OUT)
    candidates = json.loads(raw.decode("utf-8"))
    print(f"\n已写入 {REMOTE_OUT}，候选 {len(candidates)} 篇")


if __name__ == "__main__":
    main()
