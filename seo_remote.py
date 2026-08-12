#!/usr/bin/env python3
"""
SedGo SEO 优化远程处理脚本
在服务器上执行:备份、替换GA4、追加GSC、补全页面SEO、创建robots.txt和sitemap.xml
"""
import os
import re
import sys
import shutil
from datetime import date

# ===== 配置 =====
BASE_DIR = "/www/wwwroot/sedgo"
PAGES_DIR = os.path.join(BASE_DIR, "pages")
STATIC_DIR = os.path.join(BASE_DIR, "static")
SITE_DOMAIN = "https://sedgo.ai"

# GA4
OLD_GA4_ID = "G-EY1DRQWZC3"
NEW_GA4_ID = "G-0HHCWGLR3N"

# GSC
OLD_GSC = "9CV4LREFzX5L3a-2e1ZVUq1cXRM0RHxlgkwuwHFN0cY"
NEW_GSC = "FVQ6oEo6VtJ2YyT-BSgoX5-s43MPeuA3uPlVu5kJKw4"

# 页面分类
PUBLIC_PAGES = ["index.html", "terms.html", "privacy.html", "refund.html", "support.html", "api.html"]
NOINDEX_PAGES = ["admin.html", "admin_login.html", "profile.html"]  # 后台/用户页面,不索引

# GA4 代码模板
GA4_BLOCK = """<!-- Google tag (gtag.js) - GA4 -->
  <script async src="https://www.googletagmanager.com/gtag/js?id={GA4_ID}"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', '{GA4_ID}', {{ 'anonymize_ip': true }});
  </script>"""

# 新 GSC meta 标签
NEW_GSC_META = '  <meta name="google-site-verification" content="{}" />'.format(NEW_GSC)

# 页面元信息(用于补全缺失的 SEO)
PAGE_META = {
    "index.html": {
        "title": "SedGo AI - AI Video Generator | AI视频生成",
        "desc": "SedGo AI - AI Video Generator | Create stunning AI videos from text, images, and audio. Text-to-Video, Image-to-Video, Video Composition with AI. Free trial available.",
        "url": SITE_DOMAIN + "/",
    },
    "terms.html": {
        "title": "Terms of Service | SedGo AI",
        "desc": "SedGo AI Terms of Service | Read our terms and conditions for using AI video generation services. User agreement, service level commitments, and acceptable use policy.",
        "url": SITE_DOMAIN + "/pages/terms",
    },
    "privacy.html": {
        "title": "Privacy Policy | SedGo AI",
        "desc": "SedGo AI Privacy Policy | Learn how we collect, use, and protect your data when using our AI video generation platform.",
        "url": SITE_DOMAIN + "/pages/privacy",
    },
    "refund.html": {
        "title": "Refund Policy | SedGo AI",
        "desc": "SedGo AI Refund Policy | Read our refund and cancellation policy for AI video generation subscriptions and point packages.",
        "url": SITE_DOMAIN + "/pages/refund",
    },
    "support.html": {
        "title": "Support & FAQ | SedGo AI",
        "desc": "SedGo AI Support Center | Find answers to common questions about AI video generation, account management, billing, and technical support.",
        "url": SITE_DOMAIN + "/pages/support",
    },
    "api.html": {
        "title": "API Documentation | SedGo AI",
        "desc": "SedGo AI API Documentation | Integrate AI video generation into your applications. REST API for text-to-video, image-to-video, and video composition.",
        "url": SITE_DOMAIN + "/pages/api",
    },
    "admin.html": {"title": "Admin Panel | SedGo AI", "desc": "SedGo AI Admin Panel", "url": SITE_DOMAIN + "/pages/admin"},
    "admin_login.html": {"title": "Admin Login | SedGo AI", "desc": "SedGo AI Admin Login", "url": SITE_DOMAIN + "/pages/admin_login"},
    "profile.html": {"title": "My Profile | SedGo AI", "desc": "SedGo AI user profile and account settings.", "url": SITE_DOMAIN + "/pages/profile"},
}


def log(msg, level="INFO"):
    colors = {"INFO": "\033[34m", "OK": "\033[32m", "WARN": "\033[33m", "ERR": "\033[31m"}
    print("{}[{}]{}\033[0m {}".format(colors.get(level, ""), level, "", msg))


# ===== 1. 备份 =====
def backup():
    backup_dir = os.path.join(BASE_DIR, ".seo_backup_{}".format(os.popen("date +%Y%m%d_%H%M%S").read().strip()))
    os.makedirs(backup_dir, exist_ok=True)
    # 备份 pages
    if os.path.isdir(PAGES_DIR):
        shutil.copytree(PAGES_DIR, os.path.join(backup_dir, "pages"), dirs_exist_ok=True)
    # 备份 static 中的 sitemap/robots(如果存在)
    for f in ["robots.txt", "sitemap.xml"]:
        src = os.path.join(STATIC_DIR, f)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(backup_dir, f))
    log("备份完成: {}".format(backup_dir), "OK")
    return backup_dir


# ===== 2. 处理 HTML 文件 =====
def process_file(filepath, filename):
    """处理单个 HTML 文件:替换GA4、追加GSC、补全SEO。"""
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
    original = content
    meta = PAGE_META.get(filename, {})
    is_noindex = filename in NOINDEX_PAGES
    changed = False

    # --- GA4 处理 ---
    if OLD_GA4_ID in content:
        # 替换旧的 GA4 ID 为新的
        new_content = content.replace(OLD_GA4_ID, NEW_GA4_ID)
        # 同时确保有 anonymize_ip(如果旧的没有)
        # 检查是否已有 anonymize_ip
        if "anonymize_ip" not in new_content:
            new_content = new_content.replace(
                "gtag('config', '{}');".format(NEW_GA4_ID),
                "gtag('config', '{}', {{ 'anonymize_ip': true }});".format(NEW_GA4_ID),
            )
        content = new_content
        changed = True
        log("  [GA4] 替换 {} -> {}".format(OLD_GA4_ID, NEW_GA4_ID), "OK")
    elif NEW_GA4_ID not in content and not is_noindex:
        # 没有 GA4 代码,添加(仅公开页面)
        ga4_code = GA4_BLOCK.format(GA4_ID=NEW_GA4_ID)
        if re.search(r"</head>", content, re.IGNORECASE):
            content = re.sub(r"(\s*)(</head>)", r"\1" + ga4_code + r"\1\2", content, count=1, flags=re.IGNORECASE)
            changed = True
            log("  [GA4] 添加 GA4 代码 ({})".format(NEW_GA4_ID), "OK")
        else:
            log("  [GA4] 未找到 </head>,跳过", "WARN")

    # --- GSC 处理(追加新的验证码,保留旧的) ---
    if NEW_GSC not in content:
        gsc_tag = '  <meta name="google-site-verification" content="{}" />\n'.format(NEW_GSC)
        if re.search(r"<head[^>]*>", content, re.IGNORECASE):
            content = re.sub(r"(<head[^>]*>)", r"\1\n" + gsc_tag, content, count=1, flags=re.IGNORECASE)
            changed = True
            log("  [GSC] 追加新验证码: {}...".format(NEW_GSC[:16]), "OK")
        else:
            log("  [GSC] 未找到 <head>,跳过", "WARN")

    # --- noindex 处理(后台页面) ---
    if is_noindex:
        if not re.search(r'name=["\']robots["\']', content):
            noindex_tag = '  <meta name="robots" content="noindex, nofollow" />\n'
            if re.search(r"<head[^>]*>", content, re.IGNORECASE):
                content = re.sub(r"(<head[^>]*>)", r"\1\n" + noindex_tag, content, count=1, flags=re.IGNORECASE)
                changed = True
                log("  [SEO] 添加 noindex(后台页面)", "OK")

    # --- canonical 补全 ---
    if not is_noindex and meta.get("url"):
        if not re.search(r'rel=["\']canonical["\']', content):
            canonical = '  <link rel="canonical" href="{}" />\n'.format(meta["url"])
            if re.search(r"</head>", content, re.IGNORECASE):
                content = re.sub(r"(\s*)(</head>)", r"\1" + canonical + r"\1\2", content, count=1, flags=re.IGNORECASE)
                changed = True
                log("  [SEO] 添加 canonical: {}".format(meta["url"]), "OK")

    # --- Open Graph 补全(仅公开页面,基础版) ---
    if not is_noindex and meta.get("desc"):
        if not re.search(r'property=["\']og:title["\']', content):
            og_block = (
                '  <meta property="og:type" content="website" />\n'
                '  <meta property="og:url" content="{}" />\n'
                '  <meta property="og:title" content="{}" />\n'
                '  <meta property="og:description" content="{}" />\n'
                '  <meta property="og:image" content="{}/static/og-image.png" />\n'
            ).format(meta["url"], meta.get("title", "SedGo AI"), meta["desc"], SITE_DOMAIN)
            if re.search(r"</head>", content, re.IGNORECASE):
                content = re.sub(r"(\s*)(</head>)", r"\1" + og_block + r"\1\2", content, count=1, flags=re.IGNORECASE)
                changed = True
                log("  [SEO] 添加 Open Graph 标签", "OK")

    if changed:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    else:
        log("  [SKIP] 无需修改", "WARN")
        return False


# ===== 3. 创建 robots.txt =====
def create_robots():
    robots_path = os.path.join(STATIC_DIR, "robots.txt")
    content = (
        "# robots.txt for sedgo.ai\n"
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /pages/admin\n"
        "Disallow: /pages/admin_login\n"
        "Disallow: /pages/profile\n"
        "Disallow: /gradio\n"
        "Disallow: /api/\n"
        "Disallow: /*.json$\n"
        "Disallow: /*.log$\n"
        "Disallow: /.seo_backup_*\n"
        "\n"
        "User-agent: Googlebot\n"
        "Allow: /\n"
        "Disallow: /pages/admin\n"
        "Disallow: /pages/admin_login\n"
        "Disallow: /pages/profile\n"
        "\n"
        "Sitemap: {}/sitemap.xml\n"
    ).format(SITE_DOMAIN)
    with open(robots_path, "w", encoding="utf-8") as f:
        f.write(content)
    log("robots.txt 已创建: {}".format(robots_path), "OK")


# ===== 4. 创建 sitemap.xml =====
def create_sitemap():
    sitemap_path = os.path.join(STATIC_DIR, "sitemap.xml")
    today = date.today().isoformat()
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    # 首页
    lines.append("  <url>")
    lines.append("    <loc>{}/</loc>".format(SITE_DOMAIN))
    lines.append("    <lastmod>{}</lastmod>".format(today))
    lines.append("    <changefreq>weekly</changefreq>")
    lines.append("    <priority>1.0</priority>")
    lines.append("  </url>")
    # 公开页面
    for page in PUBLIC_PAGES:
        if page == "index.html":
            continue
        slug = page.replace(".html", "")
        lines.append("  <url>")
        lines.append("    <loc>{}/pages/{}</loc>".format(SITE_DOMAIN, slug))
        lines.append("    <lastmod>{}</lastmod>".format(today))
        lines.append("    <changefreq>monthly</changefreq>")
        lines.append("    <priority>0.8</priority>")
        lines.append("  </url>")
    lines.append("</urlset>")
    with open(sitemap_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    log("sitemap.xml 已创建: {} ({} 个URL)".format(sitemap_path, len(PUBLIC_PAGES)), "OK")


# ===== 主流程 =====
def main():
    log("=" * 60)
    log("SedGo SEO 优化开始")
    log("域名: {} | 新GA4: {} | 新GSC: {}...".format(SITE_DOMAIN, NEW_GA4_ID, NEW_GSC[:16]))
    log("=" * 60)

    # 1. 备份
    log("\n[步骤1] 备份文件")
    backup_dir = backup()

    # 2. 处理 HTML 文件
    log("\n[步骤2] 处理 HTML 文件")
    processed = 0
    skipped = 0
    for filename in sorted(os.listdir(PAGES_DIR)):
        if not filename.endswith((".html", ".htm")):
            continue
        if filename.startswith("google"):  # 跳过 GSC 验证文件
            continue
        filepath = os.path.join(PAGES_DIR, filename)
        log("\n处理: {}".format(filename))
        if process_file(filepath, filename):
            processed += 1
        else:
            skipped += 1
    log("\n处理完成: 更新 {} 个文件, 跳过 {} 个".format(processed, skipped), "OK")

    # 3. 创建 robots.txt
    log("\n[步骤3] 创建 robots.txt")
    create_robots()

    # 4. 创建 sitemap.xml
    log("\n[步骤4] 创建 sitemap.xml")
    create_sitemap()

    # 5. 设置权限
    log("\n[步骤5] 设置文件权限")
    for f in ["robots.txt", "sitemap.xml"]:
        path = os.path.join(STATIC_DIR, f)
        os.chmod(path, 0o644)
        try:
            os.system("chown www:www {} 2>/dev/null || true".format(path))
        except Exception:
            pass
    log("权限设置完成 (www:www, 644)", "OK")

    # 汇总
    log("\n" + "=" * 60)
    log("SEO 优化全部完成!", "OK")
    log("=" * 60)
    log("备份目录: {}".format(backup_dir))
    log("GA4: {} -> {}".format(OLD_GA4_ID, NEW_GA4_ID))
    log("GSC: 保留旧的 + 追加新的")
    log("robots.txt + sitemap.xml 已创建到 static/")
    log("\n后续验证:")
    log("  1. curl https://sedgo.ai/robots.txt")
    log("  2. curl https://sedgo.ai/sitemap.xml")
    log("  3. 查看网页源码确认 GA4/GSC 标签")
    log("  4. 重启服务(如有缓存): supervisorctl restart 或 systemctl restart")


if __name__ == "__main__":
    main()
