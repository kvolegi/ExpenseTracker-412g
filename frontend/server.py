"""
Static file server + API proxy for frontend
"""
import os
import urllib.request
import urllib.error
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(Path(__file__).parent), **kwargs)

    def log_message(self, format, *args):
        print(f"[{self.address_string()}] {format % args}")

    def do_proxy(self):
        backend_host = os.environ.get("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")
        backend_url = f"{backend_host}{self.path}"
        headers = {k: v for k, v in self.headers.items() if k.lower() != 'host'}
        body = None
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > 0:
            body = self.rfile.read(content_length)

        req = urllib.request.Request(backend_url, data=body, headers=headers, method=self.command)
        try:
            with urllib.request.urlopen(req) as resp:
                self.send_response(resp.status)
                for k, v in resp.getheaders():
                    if k.lower() not in ('transfer-encoding', 'content-length', 'access-control-allow-origin'):
                        self.send_header(k, v)
                self.send_header('Access-Control-Allow-Origin', '*')
                resp_body = resp.read()
                self.send_header('Content-Length', str(len(resp_body)))
                self.end_headers()
                self.wfile.write(resp_body)
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            for k, v in e.headers.items():
                if k.lower() not in ('transfer-encoding', 'content-length', 'access-control-allow-origin'):
                    self.send_header(k, v)
            self.send_header('Access-Control-Allow-Origin', '*')
            err_body = e.read()
            self.send_header('Content-Length', str(len(err_body)))
            self.end_headers()
            self.wfile.write(err_body)
        except Exception as e:
            self.send_error(502, f"Bad Gateway: {e}")

    def do_GET(self):
        if self.path.startswith('/api/'):
            return self.do_proxy()
        return super().do_GET()

    def do_POST(self):
        if self.path.startswith('/api/'):
            return self.do_proxy()
        return super().do_POST()

    def do_PUT(self):
        if self.path.startswith('/api/'):
            return self.do_proxy()
        return super().do_PUT()

    def do_DELETE(self):
        if self.path.startswith('/api/'):
            return self.do_proxy()
        return super().do_DELETE()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache')
        super().end_headers()


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    print(f"Frontend server starting on port {port}")
    server = HTTPServer(('0.0.0.0', port), Handler)
    server.serve_forever()
