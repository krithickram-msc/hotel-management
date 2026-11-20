"""Local-only dashboard server. Uses Python standard library only."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse
import csv, json, webbrowser, threading
ROOT = Path(__file__).resolve().parent
HOST, PORT = "127.0.0.1", 8765

def read_rows(name):
    path = ROOT / name
    if not path.exists(): return [], {"exists": False, "modified": None, "error": None, "count": 0}
    try:
        with path.open(newline="", encoding="utf-8-sig") as f: rows = list(csv.DictReader(f))
        return rows, {"exists": True, "modified": datetime.fromtimestamp(path.stat().st_mtime).astimezone().isoformat(timespec="seconds"), "error": None, "count": len(rows)}
    except (OSError, csv.Error, UnicodeError) as exc:
        return [], {"exists": True, "modified": None, "error": str(exc), "count": 0}

class Handler(BaseHTTPRequestHandler):
    def send_bytes(self, status, body, content_type):
        self.send_response(status); self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self' 'unsafe-inline' data:; img-src 'self' data:; connect-src 'self'; font-src 'self' data:")
        self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)
    def do_GET(self):
        route = urlparse(self.path).path
        if route == "/api/data":
            data, files = {}, {}
            for name in ("work_orders.csv", "results.csv", "needs_info.csv", "complaints.csv", "open_tickets.csv"):
                rows, meta = read_rows(name); key = name.removesuffix(".csv"); data[key] = rows; files[key] = meta
            p = ROOT / "summary.txt"
            try:
                summary = p.read_text(encoding="utf-8-sig") if p.exists() else ""
                summary_file = {"exists": p.exists(), "modified": datetime.fromtimestamp(p.stat().st_mtime).astimezone().isoformat(timespec="seconds") if p.exists() else None}
            except OSError as exc: summary, summary_file = "", {"exists": False, "error": str(exc)}
            payload = {**data, "summary": summary, "files": files, "summary_file": summary_file, "generated_at": datetime.now().astimezone().isoformat(timespec="seconds")}
            self.send_bytes(200, json.dumps(payload, ensure_ascii=False).encode(), "application/json; charset=utf-8"); return
        if route in ("/", "/index.html"):
            try: self.send_bytes(200, (ROOT / "dashboard.html").read_bytes(), "text/html; charset=utf-8")
            except OSError: self.send_error(500, "Dashboard file is missing")
            return
        if route == "/favicon.ico": self.send_response(204); self.end_headers(); return
        self.send_error(404)
    def log_message(self, *_): pass

if __name__ == "__main__":
    url = f"http://{HOST}:{PORT}"
    try: server = ThreadingHTTPServer((HOST, PORT), Handler)
    except OSError as exc:
        print(f"Could not start dashboard on {url}: {exc}\nClose another dashboard window and retry."); input("Press Enter to close..."); raise SystemExit(1)
    print("="*62 + "\n HOSTELOPS | ADVANCED MAINTENANCE COMMAND CENTER\n Local-only dashboard: " + url + "\n Data stays on this computer. Press Ctrl+C to stop.\n" + "="*62)
    threading.Timer(.8, lambda: webbrowser.open(url)).start()
    try: server.serve_forever()
    except KeyboardInterrupt: print("\nDashboard stopped.")
    finally: server.server_close()
