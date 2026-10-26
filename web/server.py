#!/usr/bin/env python3
# server.py - ErrorBuddy web playground.
#
# Serves index.html and one API endpoint. POST /api/compile with {"source": "..."}
# runs the real ./errorbuddy binary on the code and returns its output as JSON.
#
#   python3 web/server.py [port]      (default 8795), then open http://localhost:8795
import json, os, re, subprocess, sys, tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
EXE = os.path.join(ROOT, "errorbuddy")
MAX_SOURCE = 64 * 1024


def compile_source(source):
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        f.write(source)
    try:
        r = subprocess.run([EXE, f.name, "--tokens"], capture_output=True, text=True, timeout=5)
    finally:
        os.unlink(f.name)
    out = r.stdout.replace(f.name, "program.txt")
    result = {"ok": r.returncode == 0, "exit": r.returncode, "raw": out}

    tokens = re.search(r"Tokens \(output of the lexer\):\n.*?\n((?:  .*\n)*)", out)
    result["tokens"] = [dict(zip(("line", "type", "text"), ln.split(None, 2)))
                        for ln in (tokens[1].splitlines() if tokens else [])]

    err = re.search(r"Error on line (\d+):\n(.*)\nSuggestion: (.*)\n\n\(Found during: (.*)\)", out)
    if err:
        result["error"] = dict(line=int(err[1]), message=err[2], suggestion=err[3], phase=err[4])
    section = lambda title: re.search(title + r":\n((?:    .*\n?)*)", out)
    tac, sym, phases = section(r"Intermediate Code \(Three-Address Code\)"), section("Symbol Table"), section("Phases completed")
    result["tac"] = [l.strip() for l in tac[1].splitlines()] if tac else []
    result["symbols"] = [dict(name=m[1], line=int(m[2])) for m in
                         re.finditer(r"^\s+(\S+)\s+int\s+\(declared on line (\d+)\)", sym[1], re.M)] if sym else []
    result["phases"] = [l.strip() for l in phases[1].splitlines()] if phases else []
    return result


def examples():
    d = os.path.join(ROOT, "examples")
    return [{"name": n[:-4], "source": open(os.path.join(d, n)).read()}
            for n in sorted(os.listdir(d)) if n.endswith(".txt") and n != "empty.txt"]


class Handler(BaseHTTPRequestHandler):
    def send(self, code, body, ctype):
        data = body if isinstance(body, bytes) else body.encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self.send(200, open(os.path.join(HERE, "index.html"), "rb").read(), "text/html; charset=utf-8")
        elif self.path == "/api/examples":
            self.send(200, json.dumps(examples()), "application/json")
        else:
            self.send(404, "not found", "text/plain")

    def do_POST(self):
        if self.path != "/api/compile":
            return self.send(404, "not found", "text/plain")
        n = int(self.headers.get("Content-Length", 0))
        if n > MAX_SOURCE:
            return self.send(413, json.dumps({"detail": "Program is too large (64 KB max)."}), "application/json")
        try:
            source = json.loads(self.rfile.read(n) or b"{}").get("source", "")
            self.send(200, json.dumps(compile_source(source)), "application/json")
        except subprocess.TimeoutExpired:
            self.send(500, json.dumps({"detail": "The compiler took too long."}), "application/json")
        except (ValueError, AttributeError):
            self.send(400, json.dumps({"detail": "Bad request."}), "application/json")

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    if not os.path.exists(EXE):
        subprocess.run(["make", "-s", "-C", ROOT], check=True)
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8795
    print(f"ErrorBuddy playground on http://localhost:{port}")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
