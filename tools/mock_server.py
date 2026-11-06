#!/usr/bin/env python3
"""本機測試伺服器：模擬 GitHub Pages 與 GitHub Contents API，不會碰到線上資料。

用法（在 repo 根目錄）：
    python3 tools/mock_server.py          # 預設 port 8791
    python3 tools/mock_server.py 8800

做的事：
- 把 index.html、data.json 複製到 .test/（已列在 .gitignore），
  並把 API 改成本機的 /api、repo 改成 o/r。repo 裡的檔案不會被改到。
- 開 http://127.0.0.1:8791/index.html ，按「編輯登入」輸入假 token：
    good-token  可以發布
    ro-token    唯讀，發布會失敗（用來測錯誤訊息）
- 發布只會寫進 .test/data.json。
- 測試用網址：
    /__flag?slow=1   讓 data.json 載入變慢
    /__flag?fail=1   讓 data.json 載入失敗（=0 恢復）
    /__quit          關閉伺服器
"""
import base64
import hashlib
import http.server
import json
import os
import sys
import time

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.join(REPO_ROOT, ".test")
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8791
DATA = os.path.join(ROOT, "data.json")
FLAGS = {"slow": False, "fail": False}


def build():
    os.makedirs(ROOT, exist_ok=True)
    html = open(os.path.join(REPO_ROOT, "index.html"), encoding="utf-8").read()
    for old, new in (('const API="https://api.github.com";', 'const API="/api";'),
                     ("const REPO=detectRepo();", 'const REPO={owner:"o",repo:"r"};')):
        if html.count(old) != 1:
            sys.exit("index.html 裡找不到「%s」，請更新 tools/mock_server.py" % old)
        html = html.replace(old, new)
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(html)
    src = os.path.join(REPO_ROOT, "data.json")
    if os.path.exists(src):
        open(DATA, "wb").write(open(src, "rb").read())


def sha():
    return hashlib.sha1(open(DATA, "rb").read()).hexdigest() if os.path.exists(DATA) else None


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=ROOT, **k)

    def log_message(self, *a):
        pass

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def reply(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def authorized(self):
        return self.headers.get("Authorization") in ("Bearer good-token", "Bearer ro-token")

    def do_GET(self):
        if self.path == "/__quit":
            self.reply(200, {})
            os._exit(0)
        if self.path.startswith("/__flag"):
            query = self.path.split("?", 1)[1] if "?" in self.path else ""
            for part in query.split("&"):
                if "=" in part:
                    k, v = part.split("=", 1)
                    FLAGS[k] = v == "1"
            return self.reply(200, FLAGS)
        if self.path.startswith("/api/repos/o/r/contents/data.json"):
            if not self.authorized():
                return self.reply(401, {})
            if not os.path.exists(DATA):
                return self.reply(404, {})
            raw = base64.encodebytes(open(DATA, "rb").read()).decode()
            return self.reply(200, {"sha": sha(), "encoding": "base64", "content": raw})
        if self.path.startswith("/api/repos/o/r"):
            return self.reply(200, {"permissions": {"push": True}}) if self.authorized() else self.reply(401, {})
        if self.path.startswith("/data.json"):
            if FLAGS["slow"]:
                time.sleep(2.5)
            if FLAGS["fail"]:
                return self.reply(500, {})
        return super().do_GET()

    def do_PUT(self):
        if not self.authorized():
            return self.reply(401, {})
        if self.headers.get("Authorization") == "Bearer ro-token":
            return self.reply(403, {})
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        if body["content"] == "!":  # 登入時的寫入權限檢查
            return self.reply(422, {})
        cur = sha()
        if cur and body.get("sha") is None:
            return self.reply(422, {"message": "sha missing"})
        if cur and body.get("sha") != cur:
            return self.reply(409, {"message": "sha mismatch"})
        open(DATA, "wb").write(base64.b64decode(body["content"]))
        self.reply(200, {"content": {}})


if __name__ == "__main__":
    build()
    print("測試網址：http://127.0.0.1:%d/index.html （假 token：good-token / ro-token）" % PORT, flush=True)
    http.server.ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
