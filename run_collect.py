import sys

import ssh_tunnel


def main():
    result = ssh_tunnel.run_remote(
        "cd /www/wwwroot/gubut && node collect-rss.js", timeout=180
    )
    print(result["stdout"])
    if result["stderr"]:
        print("[STDERR]", result["stderr"], file=sys.stderr)
    if result["code"] != 0:
        print("[采集] collect-rss.js 退出码非0: {}".format(result["code"]), file=sys.stderr)
        sys.exit(1)

    check = ssh_tunnel.run_remote(
        "python3 -c \"import json;d=json.load(open('/www/wwwroot/gubut/pending-articles.json'));print(len(d))\"",
        timeout=60,
    )
    print("[采集] pending-articles.json 候选数:", check["stdout"].strip())


if __name__ == "__main__":
    main()
