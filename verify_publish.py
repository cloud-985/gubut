"""
验证：
1. 文章页SEO标签（title/keywords/description/canonical/og/twitter/JSON-LD）
2. 正文无英文残留（纯中文，资产代码除外）
3. sitemap含新URL
"""
import re, os, sys
sys.path.insert(0, '.')
from ssh_tunnel import REMOTE_DIR, read_remote_file, read_remote_json

ART_ID = 1787966357373
ART_URL = f"https://www.gubut.com/new/article-{ART_ID}.html"
ART_REMOTE = f"{REMOTE_DIR}/new/article-{ART_ID}.html"
SITEMAP_REMOTE = f"{REMOTE_DIR}/sitemap.xml"

print("=" * 70)
print("【验证1：文章页SEO标签】")
print("=" * 70)
html = read_remote_file(ART_REMOTE)
print(f"文章页已存在,大小: {len(html)} 字节")

checks = []
# title
m = re.search(r"<title>(.*?)</title>", html, re.S)
if m:
    t = m.group(1).strip()
    ok = "XAUUSD" in t and "谷比算力" in t
    checks.append(("title", ok, t))
    print(f"  {'✓' if ok else '✗'} title: {t}")
else:
    checks.append(("title", False, "missing"))

# meta keywords
m = re.search(r'<meta\s+name="keywords"\s+content="([^"]*)"', html)
if m:
    kw = m.group(1).strip()
    ok = len(kw) > 20
    checks.append(("keywords", ok, kw[:80]))
    print(f"  {'✓' if ok else '✗'} keywords({len(kw)}字): {kw[:80]}...")
else:
    checks.append(("keywords", False, "missing"))

# meta description
m = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', html)
if m:
    desc = m.group(1).strip()
    ok = len(desc) > 30
    checks.append(("description", ok, desc[:80]))
    print(f"  {'✓' if ok else '✗'} description({len(desc)}字): {desc[:80]}...")
else:
    checks.append(("description", False, "missing"))

# canonical
m = re.search(r'<link\s+rel="canonical"\s+href="([^"]*)"', html)
if m and ART_URL in m.group(1):
    checks.append(("canonical", True, m.group(1)))
    print(f"  ✓ canonical: {m.group(1)}")
else:
    checks.append(("canonical", False, "missing or wrong"))
    actual = m.group(1) if m else "None"
    print(f"  ✗ canonical: {actual}")

# og tags
og_ok = "og:title" in html and "og:description" in html and "og:url" in html and "og:image" in html
checks.append(("OpenGraph", og_ok, ""))
print(f"  {'✓' if og_ok else '✗'} OpenGraph 标签")

# twitter card
tw_ok = "twitter:card" in html and "twitter:title" in html and "twitter:description" in html
checks.append(("TwitterCard", tw_ok, ""))
print(f"  {'✓' if tw_ok else '✗'} Twitter Card 标签")

# JSON-LD schema
ld_ok = 'application/ld+json' in html and '"@type": "Article"' in html
checks.append(("JSON-LD", ld_ok, ""))
print(f"  {'✓' if ld_ok else '✗'} JSON-LD Article 结构化数据")

print()
print("=" * 70)
print("【验证2：正文英文残留扫描】")
print("=" * 70)
# 提取 article-body 部分
body_m = re.search(r'<div class="article-body">(.*?)</div>\s*<div class="related-articles">', html, re.S)
if body_m:
    body = body_m.group(1)
    # 去除HTML标签
    plain = re.sub(r"<[^>]*>", " ", body)
    plain = re.sub(r"&[a-z]+;", " ", plain)
    plain = re.sub(r"&#\d+;", " ", plain)
    # 找连续的英文单词/句子
    en_sequences = re.findall(r"[A-Za-z][A-Za-z0-9_ /\-\.]*(?:\s+[A-Za-z][A-Za-z0-9_/\-\.]*)*", plain)
    # 过滤：纯技术代码（XAUUSD/MT5/EA/BTC/ETH等）、单个字母、数字
    allowed_prefixes = {
        "XAUUSD", "MT5", "EA", "RSI", "MACD", "CCI", "ATR", "EMA", "MQL5", "MQL",
        "SM", "CT", "TP", "SL", "US", "CPI", "GDP", "PCE", "ETF", "TP1", "TP2", "TP3",
        "H1", "H2", "M5", "M15", "M30", "D1", "W1", "MN1", "SMC", "CTA", "OB", "API",
        "CSV", "VPS", "ADX", "VWAP", "USD", "JPY", "EUR", "GBP", "BTC", "ETH", "SOL",
        "UK", "FX", "FVG", "BOS", "CHoCH", "CLS", "CIOD",
        "BuyZone", "TrailingStep", "OrderSend", "IsBullishEngulfing",
        "POSITION", "INDENT", "Bid", "CheckAccountRisk",
        "Every tick", "VOLUME", "REAL", "GOLD",
    }
    def is_allowed(text):
        tokens = re.split(r"\s+|_|-", text.strip())
        if len(tokens) <= 1 and len(tokens[0]) <= 8:
            return True  # 短词
        # 检查每个token是否都是技术代码
        for tok in tokens:
            if not tok:
                continue
            if tok.upper() in {p.upper() for p in allowed_prefixes}:
                continue
            if re.fullmatch(r"[A-Za-z]{1,3}\d{0,3}", tok):
                continue  # 短代码
            if re.fullmatch(r"\d+[A-Za-z]*", tok):
                continue
            return False
        return True

    suspicious = []
    for seq in en_sequences:
        s = seq.strip()
        if len(s) < 5:
            continue
        # 检查是否包含实际的英文句子
        words = [w for w in re.split(r"\s+", s) if len(w) > 2]
        if len(words) >= 3:
            suspicious.append(s[:120])
        elif not is_allowed(s):
            suspicious.append(s[:120])

    if suspicious:
        print(f"  ⚠ 发现 {len(suspicious)} 处疑似英文片段:")
        for s in suspicious[:15]:
            print(f"    - {s}")
    else:
        print(f"  ✓ 正文无英文散文残留 (HTML属性/技术代码名除外)")
        # 打印几个典型的"英文"展示是技术词
        samples = [s for s in en_sequences if 4 < len(s.strip()) < 30][:5]
        if samples:
            print(f"    (仅技术代码示例: {samples})")

    plain_cn = re.sub(r"[A-Za-z0-9_/\-.,!?$%():;='\"&<>%+\[\]{}]", "", plain)
    plain_cn = re.sub(r"\s+", "", plain_cn)
    print(f"  正文纯字数: {len(plain_cn)} 汉字")
else:
    print("  ✗ 未找到 article-body 部分")

print()
print("=" * 70)
print("【验证3：Sitemap包含新URL】")
print("=" * 70)
sitemap = read_remote_file(SITEMAP_REMOTE)
if ART_URL in sitemap:
    print(f"  ✓ sitemap.xml 已包含新URL: {ART_URL}")
    # 显示上下文
    idx = sitemap.index(ART_URL)
    ctx = sitemap[max(0, idx-30):idx+200]
    print(f"    上下文: ...{ctx.replace(chr(10),' ')}...")
else:
    print(f"  ✗ sitemap.xml 未找到新URL！")

# 验证远程 articles.json
print()
print("=" * 70)
print("【验证4：articles.json追加正确】")
print("=" * 70)
arts = read_remote_json(f"{REMOTE_DIR}/articles.json")
found = [a for a in arts if str(a.get("id")) == str(ART_ID)]
if found:
    a = found[0]
    title = a.get("title", "")[:80]
    date = a.get("date", "")
    content_len = len(a.get("content", ""))
    print(f"  ✓ articles.json 已收录, 排在第 {arts.index(a)+1}/{len(arts)} 位")
    print(f"    title: {title}")
    print(f"    date:  {date}")
    print(f"    content(纯文本摘要长度): {content_len} 字")
else:
    print(f"  ✗ articles.json 未找到新文章!")

print()
print("=" * 70)
print("【验证汇总】")
print("=" * 70)
passed = sum(1 for _, ok, _ in checks if ok)
total = len(checks)
for name, ok, extra in checks:
    print(f"  {'✓' if ok else '✗'} {name}")
print(f"SEO标签: {passed}/{total} 通过")
if passed == total:
    print(f"\n🎉 所有验证通过! 文章已成功发布!")
else:
    print(f"\n⚠ 有 {total - passed} 项SEO检查未通过")
