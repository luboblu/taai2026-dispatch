#!/usr/bin/env python3
"""PreToolUse 護欄：擋下違反 AGENTS.md 的操作。

規則（出處：AGENTS.md「協作規則」）：
1. 不可修改 data.json（只能由統籌在網頁按「發布」寫入）。
2. 不可 git add / commit data.json 與 .test/。
3. 不可把 GitHub token 寫進檔案（repo 是公開的）。

被擋下時以 exit code 2 結束，stderr 的訊息會回給 Claude。
"""
import json
import os
import re
import subprocess
import sys

TOKEN_RE = re.compile(r"(ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|gh[ousr]_[A-Za-z0-9]{20,})")
WRITE_VERBS = re.compile(r"(>|\btee\b|\bsed\s+-i|\bmv\b|\bcp\b|\brm\b|\btruncate\b|\bdd\b|\bperl\s+-i|json\.dump|write_text|open\()")


def block(msg):
    sys.stderr.write("[guard] " + msg + "\n")
    sys.exit(2)


def project_dir():
    return os.path.realpath(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())


def is_repo_data_json(path):
    if not path:
        return False
    real = os.path.realpath(os.path.join(project_dir(), path))
    return real == os.path.join(project_dir(), "data.json")


def data_json_dirty():
    try:
        out = subprocess.run(
            ["git", "status", "--porcelain", "--", "data.json"],
            cwd=project_dir(), capture_output=True, text=True, timeout=10,
        ).stdout
        return bool(out.strip())
    except Exception:
        return False


def check_file_tool(inp):
    path = inp.get("file_path") or inp.get("notebook_path") or ""
    if is_repo_data_json(path):
        block("data.json 只能由統籌在網頁按「發布」寫入，任何助理都不可直接修改（AGENTS.md）。"
              "需要修正資料請改寫成一次性套用函式（參考 applyAgendaFix）。")
    text = "\n".join(str(inp.get(k, "")) for k in ("content", "new_string", "new_source"))
    if TOKEN_RE.search(text):
        block("內容看起來含有 GitHub token。這個 repo 是公開的，不可把 token 寫進檔案（AGENTS.md）。")


def check_bash(cmd):
    # 1. 以指令改寫 repo 根目錄的 data.json
    for part in re.split(r"&&|;|\|\||\n", cmd):
        p = part.strip()
        if not WRITE_VERBS.search(p):
            continue
        toks = re.findall(r"[\w./~-]*data\.json", p)
        if re.match(r"cp\s", p) and ">" not in p:
            # cp 只會讀來源，只有最後一個參數（目的地）會被寫入
            last = p.split()[-1]
            toks = [last] if last.endswith("data.json") else []
        for tok in toks:
            if is_repo_data_json(os.path.expanduser(tok)):
                block("data.json 只能由統籌在網頁按「發布」寫入，不可用指令修改（AGENTS.md）。")
    # 2. git add / commit 的限制
    for seg in re.split(r"&&|;|\|\||\n", cmd):
        s = seg.strip()
        if re.match(r"git\s+(-C\s+\S+\s+)?add\b", s):
            if re.search(r"(^|\s)(\./)?data\.json(\s|$)", s) or re.search(r"\.test\b", s):
                block("不要 commit data.json 或 .test/（AGENTS.md 協作規則第 4 點）。")
            if re.search(r"(\s-A\b|\s--all\b|\s-u\b|\s\.(\s|$)|\s\*(\s|$))", s) and data_json_dirty():
                block("data.json 目前有未提交的變動，用 git add -A / . 會把它一起加入。請改成逐一指定檔案。")
        if re.match(r"git\s+(-C\s+\S+\s+)?commit\b", s) and re.search(r"\s-\w*a\w*\b|\s--all\b", s) and data_json_dirty():
            block("data.json 目前有未提交的變動，git commit -a 會把它一起提交。請先 git add 指定檔案。")
    # 3. 指令裡直接出現 token
    if TOKEN_RE.search(cmd) and re.search(r"(>|tee|sed -i|git\s+commit)", cmd):
        block("指令裡含有 GitHub token，且可能寫入檔案或 commit。請不要把 token 放進 repo。")


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    tool = data.get("tool_name", "")
    inp = data.get("tool_input") or {}
    if tool in ("Edit", "Write", "NotebookEdit", "MultiEdit"):
        check_file_tool(inp)
    elif tool == "Bash":
        check_bash(inp.get("command", ""))
    sys.exit(0)


if __name__ == "__main__":
    main()
