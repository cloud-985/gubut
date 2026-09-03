#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一键发布脚本：上传 ai_article.json 到服务器并执行 node publish_ai.js
步骤：
    1. 本地 /workspace/ai_article.json -> 服务器 /www/wwwroot/gubut/ai_article.json
    2. 服务器 cd /www/wwwroot/gubut && node publish_ai.js
    3. 读取服务器返回的发布结果与文章URL
"""

import sys
import os
import json
import ssh_tunnel

LOCAL_AI = '/workspace/ai_article.json'
REMOTE_AI = '/www/wwwroot/gubut/ai_article.json'
REMOTE_DIR = '/www/wwwroot/gubut'
PUBLISH_SCRIPT = 'publish_ai.js'  # 服务器上已存在


def main():
    if not os.path.exists(LOCAL_AI):
        print(f'[ERROR] 本地 ai_article.json 不存在: {LOCAL_AI}')
        sys.exit(1)

    # 1. 校验本地 JSON 合法性
    try:
        with open(LOCAL_AI, 'r', encoding='utf-8') as f:
            article = json.load(f)
        print(f'[1/3] 本地 JSON 校验通过: id={article.get("id")}, title={article.get("title","")[:50]}')
    except Exception as e:
        print(f'[ERROR] 本地 JSON 非法: {e}')
        sys.exit(1)

    # 2. 上传到服务器
    try:
        ssh_tunnel.upload_file(LOCAL_AI, REMOTE_AI, mode=0o644)
        print(f'[2/3] 已上传到服务器: {REMOTE_AI}')
    except Exception as e:
        print(f'[ERROR] 上传失败: {e}')
        sys.exit(1)

    # 3. 赋予 www 权限并执行发布脚本
    cmds = [
        f'chown www:www {REMOTE_AI} && chmod 644 {REMOTE_AI}',
        f'cd {REMOTE_DIR} && node {PUBLISH_SCRIPT} 2>&1',
    ]
    for i, cmd in enumerate(cmds, start=1):
        out, err, code = ssh_tunnel.run_remote(cmd, timeout=120)
        if i == 1:
            if code != 0:
                print(f'[WARN] chown 退出码 {code}: {err}')
            else:
                print(f'[2.5/3] 权限修正完成')
        else:
            print(f'[3/3] 执行 node {PUBLISH_SCRIPT}:')
            print(out)
            if err and 'WARN' not in err.upper():
                print('[STDERR]', err)
            if code != 0:
                print(f'[ERROR] 发布脚本退出码 {code}')
                sys.exit(1)

    # 4. 解析输出中的 URL 与结果
    lines = [l.strip() for l in out.split('\n') if l.strip()]
    result_url = None
    for line in lines:
        if 'article-' in line and '.html' in line:
            import re
            m = re.search(r'article-\d+\.html', line)
            if m:
                result_url = 'https://www.gubut.com/new/' + m.group(0)
                break
    if result_url:
        print()
        print(f'[SUCCESS] 发布成功! 文章URL: {result_url}')
    else:
        print('[INFO] 请从上方输出中查看文章URL')


if __name__ == '__main__':
    main()
