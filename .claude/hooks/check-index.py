#!/usr/bin/env python3
"""PostToolUse：index.html 被修改後，檢查內嵌 JavaScript 有沒有語法錯誤。

整個程式都在 index.html 一個檔案裡，一個語法錯誤就會讓整個網站壞掉。
有錯時以 exit code 2 結束，錯誤訊息會回給 Claude。
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    path = (data.get("tool_input") or {}).get("file_path", "")
    if os.path.basename(path) != "index.html":
        sys.exit(0)
    node = shutil.which("node")
    if not node or not os.path.isfile(path):
        sys.exit(0)
    html = open(path, encoding="utf-8").read()
    blocks = re.findall(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", html, re.S)
    errors = []
    for i, code in enumerate(blocks, 1):
        with tempfile.TemporaryDirectory() as d:
            f = os.path.join(d, "block.js")
            with open(f, "w", encoding="utf-8") as fh:
                fh.write(code)
            r = subprocess.run([node, "--check", f], capture_output=True, text=True, timeout=30)
            if r.returncode != 0:
                errors.append("<script> #%d:\n%s" % (i, r.stderr.strip()))
    if errors:
        sys.stderr.write("[check-index] index.html 內嵌 JS 有語法錯誤，請立刻修正：\n" + "\n".join(errors) + "\n")
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
