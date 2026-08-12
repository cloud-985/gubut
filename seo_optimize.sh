#!/bin/bash
###############################################################################
# SEO 优化一键脚本
# 功能:
#   1. 备份网站文件
#   2. 添加 Google Search Console 验证 meta 标签
#   3. 添加 Google Analytics 4 (GA4) 跟踪代码
#   4. SEO 优化:meta description/keywords、Open Graph、Twitter Card、
#      canonical、JSON-LD 结构化数据、robots.txt、sitemap.xml
#
# 用法:
#   chmod +x seo_optimize.sh
#   ./seo_optimize.sh [网站根目录] [网站域名]
#
# 示例:
#   ./seo_optimize.sh /www/wwwroot/sedgo https://sedgo.com
###############################################################################

set -euo pipefail

# ===== 配置项(可按需修改) =====
SITE_DIR="${1:-/www/wwwroot/sedgo}"
SITE_DOMAIN="${2:-}"  # 例如 https://sedgo.com (不带末尾斜杠)

# Google Analytics 4 跟踪 ID
GA4_ID="G-0HHCWGLR3N"

# Google Search Console 验证 content 值
GSC_VERIFICATION="FVQ6oEo6VtJ2YyT-BSgoX5-s43MPeuA3uPlVu5kJKw4"

# 网站默认描述/关键词(如 HTML 中无则填入)
DEFAULT_DESCRIPTION="Sedgo - 专业的高端服务平台,提供卓越的产品与服务体验。"
DEFAULT_KEYWORDS="sedgo,专业服务,高端平台"
DEFAULT_AUTHOR="Sedgo"
DEFAULT_OG_TYPE="website"
DEFAULT_OG_IMAGE=""  # 可填入默认社交分享图绝对路径,如 https://sedgo.com/og-image.jpg

# ===== 颜色输出 =====
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info()  { echo -e "${BLUE}[INFO]${NC} $*"; }
ok()    { echo -e "${GREEN}[OK]${NC} $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
err()   { echo -e "${RED}[ERROR]${NC} $*"; }

# ===== 前置检查 =====
if [[ ! -d "$SITE_DIR" ]]; then
    err "网站目录不存在: $SITE_DIR"
    exit 1
fi

# 自动探测域名(若未提供)
if [[ -z "$SITE_DOMAIN" ]]; then
    info "未提供域名,尝试自动探测..."
    # 从 nginx 配置中提取 server_name
    if command -v nginx &>/dev/null; then
        NGINX_CONF=$(nginx -T 2>/dev/null | grep -E "server_name|root" | head -40)
        DETECTED_DOMAIN=$(echo "$NGINX_CONF" | grep -A1 "root.*${SITE_DIR##*/}" | grep server_name | head -1 | awk '{print $2}' | sed 's/;//' | head -1)
        [[ -z "$DETECTED_DOMAIN" ]] && DETECTED_DOMAIN=$(nginx -T 2>/dev/null | grep -B5 "root ${SITE_DIR}" | grep server_name | head -1 | awk '{print $2}' | sed 's/;//' | head -1)
        if [[ -n "$DETECTED_DOMAIN" && "$DETECTED_DOMAIN" != "_" ]]; then
            SITE_DOMAIN="https://${DETECTED_DOMAIN}"
            ok "探测到域名: $SITE_DOMAIN"
        fi
    fi
    # 从 apache 配置中提取
    if [[ -z "$SITE_DOMAIN" ]] && command -v httpd &>/dev/null; then
        DETECTED_DOMAIN=$(grep -rh "ServerName" /etc/httpd/conf/ /etc/apache2/ 2>/dev/null | head -1 | awk '{print $2}')
        if [[ -n "$DETECTED_DOMAIN" ]]; then
            SITE_DOMAIN="https://${DETECTED_DOMAIN}"
            ok "探测到域名: $SITE_DOMAIN"
        fi
    fi
    # 从 .htaccess 或已有 HTML 中探测
    if [[ -z "$SITE_DOMAIN" ]]; then
        DETECTED_DOMAIN=$(grep -rohE 'https?://[a-zA-Z0-9._-]+\.[a-zA-Z]{2,}' "$SITE_DIR" 2>/dev/null | head -1)
        if [[ -n "$DETECTED_DOMAIN" ]]; then
            SITE_DOMAIN="$DETECTED_DOMAIN"
            ok "从文件中探测到域名: $SITE_DOMAIN"
        fi
    fi
    if [[ -z "$SITE_DOMAIN" ]]; then
        warn "未能自动探测域名,将使用 http://localhost 作为占位符"
        warn "建议手动运行: ./$0 $SITE_DIR https://你的域名.com"
        SITE_DOMAIN="http://localhost"
    fi
fi

# 去掉末尾斜杠
SITE_DOMAIN="${SITE_DOMAIN%/}"

info "网站目录: $SITE_DIR"
info "网站域名: $SITE_DOMAIN"
info "GA4 ID: $GA4_ID"
info "GSC 验证码: $GSC_VERIFICATION"
echo ""

# ===== 1. 备份 =====
BACKUP_DIR="${SITE_DIR}/.seo_backup_$(date +%Y%m%d_%H%M%S)"
info "正在备份网站文件到: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"

# 只备份 HTML/PHP 文件和 robots.txt/sitemap.xml
find "$SITE_DIR" -maxdepth 5 \( -name "*.html" -o -name "*.htm" -o -name "*.php" \) -not -path "*/.seo_backup_*" -print0 2>/dev/null | while IFS= read -r -d '' f; do
    rel="${f#$SITE_DIR/}"
    mkdir -p "$BACKUP_DIR/$(dirname "$rel")"
    cp -p "$f" "$BACKUP_DIR/$rel"
done
[[ -f "$SITE_DIR/robots.txt" ]] && cp -p "$SITE_DIR/robots.txt" "$BACKUP_DIR/"
[[ -f "$SITE_DIR/sitemap.xml" ]] && cp -p "$SITE_DIR/sitemap.xml" "$BACKUP_DIR/"
ok "备份完成: $BACKUP_DIR"
echo ""

# ===== 2. 收集所有 HTML/PHP 文件 =====
HTML_FILES=()
while IFS= read -r -d '' f; do
    HTML_FILES+=("$f")
done < <(find "$SITE_DIR" -maxdepth 5 \( -name "*.html" -o -name "*.htm" -o -name "*.php" \) -not -path "*/.seo_backup_*" -print0 2>/dev/null)

if [[ ${#HTML_FILES[@]} -eq 0 ]]; then
    warn "未找到 HTML/PHP 文件,请检查目录: $SITE_DIR"
    ls -la "$SITE_DIR" | head -20
    exit 1
fi
info "找到 ${#HTML_FILES[@]} 个 HTML/PHP 文件待处理"
echo ""

# ===== 3. 定义要注入的代码片段 =====
# GSC 验证 meta 标签
GSC_META="<meta name=\"google-site-verification\" content=\"${GSC_VERIFICATION}\" />"

# GA4 跟踪代码(官方 gtag.js)
GA4_CODE="<!-- Google tag (gtag.js) - GA4 -->
<script async src=\"https://www.googletagmanager.com/gtag/js?id=${GA4_ID}\"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', '${GA4_ID}', { 'anonymize_ip': true });
</script>"

# SEO 基础 meta 标签
SEO_META="<meta name=\"description\" content=\"${DEFAULT_DESCRIPTION}\" />
<meta name=\"keywords\" content=\"${DEFAULT_KEYWORDS}\" />
<meta name=\"author\" content=\"${DEFAULT_AUTHOR}\" />
<meta name=\"robots\" content=\"index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1\" />
<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />"

# Open Graph 标签
OG_TAGS="<meta property=\"og:type\" content=\"${DEFAULT_OG_TYPE}\" />
<meta property=\"og:site_name\" content=\"${DEFAULT_AUTHOR}\" />
<meta property=\"og:title\" content=\"${DEFAULT_AUTHOR}\" />
<meta property=\"og:description\" content=\"${DEFAULT_DESCRIPTION}\" />
<meta property=\"og:url\" content=\"${SITE_DOMAIN}\" />"

if [[ -n "$DEFAULT_OG_IMAGE" ]]; then
    OG_TAGS="${OG_TAGS}
<meta property=\"og:image\" content=\"${DEFAULT_OG_IMAGE}\" />"
fi

# Twitter Card 标签
TWITTER_TAGS="<meta name=\"twitter:card\" content=\"summary_large_image\" />
<meta name=\"twitter:title\" content=\"${DEFAULT_AUTHOR}\" />
<meta name=\"twitter:description\" content=\"${DEFAULT_DESCRIPTION}\" />"

# canonical 链接
CANONICAL_TAG="<link rel=\"canonical\" href=\"${SITE_DOMAIN}\" />"

# JSON-LD 结构化数据(Organization)
JSONLD="<script type=\"application/ld+json\">
{
  \"@context\": \"https://schema.org\",
  \"@type\": \"Organization\",
  \"name\": \"${DEFAULT_AUTHOR}\",
  \"url\": \"${SITE_DOMAIN}\",
  \"description\": \"${DEFAULT_DESCRIPTION}\"
}
</script>"

# ===== 4. 处理每个文件 =====
info "开始处理文件..."
PROCESSED=0
SKIPPED=0

for f in "${HTML_FILES[@]}"; do
    rel="${f#$SITE_DIR/}"
    # 跳过已处理(避免重复)
    if grep -q "google-site-verification.*${GSC_VERIFICATION:0:20}" "$f" 2>/dev/null && \
       grep -q "gtag/js?id=${GA4_ID}" "$f" 2>/dev/null; then
        SKIPPED=$((SKIPPED+1))
        continue
    fi

    # 生成文件对应的 canonical URL(基于相对路径)
    if [[ "$rel" == "index.html" || "$rel" == "index.php" || "$rel" == "index.htm" ]]; then
        CANON_URL="$SITE_DOMAIN"
    else
        # 去掉文件名中的 index.html 等
        CANON_PATH=$(echo "$rel" | sed -E 's#/(index\.(html?|php))$##; s#^(index\.(html?|php))$##')
        [[ -z "$CANON_PATH" ]] && CANON_URL="$SITE_DOMAIN" || CANON_URL="${SITE_DOMAIN}/${CANON_PATH}"
    fi

    FILE_CANONICAL="<link rel=\"canonical\" href=\"${CANON_URL}\" />"

    # 使用 Python 进行精确的、幂等的注入(比 sed 更可靠)
    python3 - "$f" "$GSC_META" "$GA4_CODE" "$SEO_META" "$OG_TAGS" "$TWITTER_TAGS" "$FILE_CANONICAL" "$JSONLD" <<'PYEOF'
import sys, re

fpath = sys.argv[1]
gsc_meta, ga4_code, seo_meta, og_tags, twitter_tags, canonical_tag, jsonld = sys.argv[2:9]

with open(fpath, 'r', encoding='utf-8', errors='replace') as fh:
    content = fh.read()

original = content
inserted = []

def has(content, snippet):
    # 用 snippet 的关键片段判断是否已存在
    key = re.sub(r'\s+', ' ', snippet).strip()
    # 取一个特征子串
    if 'google-site-verification' in key:
        return 'google-site-verification' in content
    if 'gtag/js' in key:
        return 'gtag/js' in content
    if 'name="description"' in key:
        return re.search(r'name\s*=\s*["\']description["\']', content) is not None
    if 'name="keywords"' in key:
        return re.search(r'name\s*=\s*["\']keywords["\']', content) is not None
    if 'name="author"' in key:
        return re.search(r'name\s*=\s*["\']author["\']', content) is not None
    if 'name="robots"' in key:
        return re.search(r'name\s*=\s*["\']robots["\']', content) is not None
    if 'name="viewport"' in key:
        return re.search(r'name\s*=\s*["\']viewport["\']', content) is not None
    if 'property="og:type"' in key:
        return 'property="og:type"' in content or "property='og:type'" in content
    if 'name="twitter:card"' in key:
        return 'name="twitter:card"' in content or "name='twitter:card'" in content
    if 'rel="canonical"' in key:
        return 'rel="canonical"' in content or "rel='canonical'" in content
    if 'application/ld+json' in key:
        return 'application/ld+json' in content
    return key[:30] in content

# 收集需要插入的标签
to_insert_after_head = []
to_insert_before_head_close = []

if not has(content, gsc_meta):
    to_insert_after_head.append(gsc_meta)
if not has(content, seo_meta):
    # 拆开检查,只插入缺失的
    for line in seo_meta.split('\n'):
        if line.strip() and not has(content, line):
            to_insert_after_head.append(line.strip())
if not has(content, og_tags):
    for line in og_tags.split('\n'):
        if line.strip() and not has(content, line):
            to_insert_after_head.append(line.strip())
if not has(content, twitter_tags):
    for line in twitter_tags.split('\n'):
        if line.strip() and not has(content, line):
            to_insert_after_head.append(line.strip())
if not has(content, canonical_tag):
    to_insert_after_head.append(canonical_tag)

if not has(content, ga4_code):
    to_insert_before_head_close.append(ga4_code)
if not has(content, jsonld):
    to_insert_before_head_close.append(jsonld)

if not to_insert_after_head and not to_insert_before_head_close:
    sys.exit(0)

# 插入到 <head> 之后
if to_insert_after_head:
    block = '\n' + '\n'.join(to_insert_after_head)
    # 匹配 <head ...> 标签
    m = re.search(r'<head[^>]*>', content, re.IGNORECASE)
    if m:
        pos = m.end()
        content = content[:pos] + block + content[pos:]
    else:
        # 没有 <head>,尝试在 <html> 后或 <!DOCTYPE> 后插入 <head>
        m2 = re.search(r'<html[^>]*>', content, re.IGNORECASE)
        if m2:
            pos = m2.end()
            content = content[:pos] + '\n<head>' + block + content[pos:]
        else:
            content = '<head>' + block + '\n' + content

# 插入到 </head> 之前
if to_insert_before_head_close:
    block = '\n' + '\n'.join(to_insert_before_head_close) + '\n'
    if re.search(r'</head>', content, re.IGNORECASE):
        content = re.sub(r'</head>', block + '</head>', content, count=1, flags=re.IGNORECASE)
    else:
        # 没有 </head>,在 </body> 或文件末尾前加 </head>
        if re.search(r'</body>', content, re.IGNORECASE):
            content = re.sub(r'</body>', block + '</head>\n</body>', content, count=1, flags=re.IGNORECASE)
        else:
            content = content + '\n' + block + '</head>\n'

if content != original:
    with open(fpath, 'w', encoding='utf-8') as fh:
        fh.write(content)
    print(f"  [UPDATED] {fpath}")
else:
    print(f"  [SKIP]    {fpath}")
PYEOF
    PROCESSED=$((PROCESSED+1))
done

ok "处理完成: 更新 $PROCESSED 个文件, 跳过 $SKIPPED 个已处理文件"
echo ""

# ===== 5. 生成 robots.txt =====
info "生成/更新 robots.txt"
ROBOTS_FILE="$SITE_DIR/robots.txt"

# 检测域名(去掉协议)
ROBOTS_DOMAIN=$(echo "$SITE_DOMAIN" | sed -E 's#^[a-zA-Z]+://##')

# 如果已有 robots.txt 且包含 Sitemap,则只补充缺失项
if [[ -f "$ROBOTS_FILE" ]]; then
    if ! grep -qi "googlebot" "$ROBOTS_FILE"; then
        cat >> "$ROBOTS_FILE" <<EOF

# Added by SEO optimizer
User-agent: Googlebot
Allow: /
Disallow: /*.json$
Disallow: /*.log$
EOF
    fi
    if ! grep -qi "User-agent: \*" "$ROBOTS_FILE"; then
        cat >> "$ROBOTS_FILE" <<EOF
User-agent: *
Allow: /
Disallow: /admin/
Disallow: /*.json$
Disallow: /*.log$
EOF
    fi
    if ! grep -qi "Sitemap:" "$ROBOTS_FILE"; then
        echo "Sitemap: ${SITE_DOMAIN}/sitemap.xml" >> "$ROBOTS_FILE"
    fi
else
    cat > "$ROBOTS_FILE" <<EOF
# robots.txt for ${ROBOTS_DOMAIN}
User-agent: *
Allow: /
Disallow: /admin/
Disallow: /*.json$
Disallow: /*.log$
Disallow: /.seo_backup_*

User-agent: Googlebot
Allow: /

Sitemap: ${SITE_DOMAIN}/sitemap.xml
EOF
fi
ok "robots.txt 已就绪"
echo ""

# ===== 6. 生成 sitemap.xml =====
info "生成/更新 sitemap.xml"
SITEMAP_FILE="$SITE_DIR/sitemap.xml"
TODAY=$(date +%Y-%m-%d)

{
echo '<?xml version="1.0" encoding="UTF-8"?>'
echo '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
} > "$SITEMAP_FILE"

# 添加首页
cat >> "$SITEMAP_FILE" <<EOF
  <url>
    <loc>${SITE_DOMAIN}/</loc>
    <lastmod>${TODAY}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
EOF

# 遍历 HTML 文件添加到 sitemap(排除备份、404 等)
find "$SITE_DIR" -maxdepth 4 \( -name "*.html" -o -name "*.htm" \) -not -path "*/.seo_backup_*" -not -name "404*" -not -name "503*" 2>/dev/null | sort | while IFS= read -r f; do
    rel="${f#$SITE_DIR/}"
    # 跳过 index(已作为首页添加)
    [[ "$rel" == "index.html" || "$rel" == "index.htm" ]] && continue
    # 转换为 URL 路径
    url_path=$(echo "$rel" | sed -E 's#/(index\.(html?|php))$##; s#^(index\.(html?|php))$##')
    if [[ -z "$url_path" ]]; then
        url="${SITE_DOMAIN}/"
    else
        url="${SITE_DOMAIN}/${url_path}"
    fi
    # URL 编码空格等(基础)
    url=$(echo "$url" | sed 's/ /%20/g')
    cat >> "$SITEMAP_FILE" <<EOF
  <url>
    <loc>${url}</loc>
    <lastmod>${TODAY}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
EOF
done

echo '</urlset>' >> "$SITEMAP_FILE"
ok "sitemap.xml 已生成 ($(grep -c '<url>' "$SITEMAP_FILE") 个 URL)"
echo ""

# ===== 7. 设置文件权限 =====
info "设置文件权限..."
# 尝试识别 web 服务器用户
WEB_USER="www-data"
if id -u "www" &>/dev/null; then
    WEB_USER="www"
elif id -u "nginx" &>/dev/null; then
    WEB_USER="nginx"
elif id -u "apache" &>/dev/null; then
    WEB_USER="apache"
fi
chown "${WEB_USER}:${WEB_USER}" "$ROBOTS_FILE" "$SITEMAP_FILE" 2>/dev/null || true
chmod 644 "$ROBOTS_FILE" "$SITEMAP_FILE"
ok "权限设置完成"
echo ""

# ===== 8. 输出汇总 =====
echo "========================================================"
ok "SEO 优化全部完成!"
echo "========================================================"
echo ""
echo "完成项目:"
echo "  ✓ 网站文件已备份至: $BACKUP_DIR"
echo "  ✓ Google Search Console 验证 meta 标签已注入"
echo "  ✓ Google Analytics 4 跟踪代码已注入 (ID: $GA4_ID)"
echo "  ✓ SEO meta 标签(description/keywords/robots/viewport)"
echo "  ✓ Open Graph 社交分享标签"
echo "  ✓ Twitter Card 标签"
echo "  ✓ canonical 规范链接"
echo "  ✓ JSON-LD 结构化数据(Organization)"
echo "  ✓ robots.txt 已生成/更新"
echo "  ✓ sitemap.xml 已生成"
echo ""
echo "后续建议:"
echo "  1. 访问 https://search.google.com/search-console 验证站点所有权"
echo "  2. 访问 https://analytics.google.com 确认 GA4 数据接收正常(需 24-48h)"
echo "  3. 在 Search Console 提交 sitemap: ${SITE_DOMAIN}/sitemap.xml"
echo "  4. 如需回滚,执行: rm -rf $SITE_DIR && mv $BACKUP_DIR/* $SITE_DIR/"
echo ""
warn "提示: 如网站使用 PHP/模板引擎动态渲染,建议同时检查模板文件(如 header.php / layout 模板)以确保所有页面都包含代码。"
