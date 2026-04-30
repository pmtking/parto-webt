# api/index.py
from http.server import BaseHTTPRequestHandler
import urllib.request, urllib.error, json, os, re


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self._handle_request()

    def do_POST(self):
        self._handle_request()

    def _handle_request(self):
        # استخراج URL هدف از پارامتر 'url'
        query = self.path.split('?', 1)[-1] if '?' in self.path else ''
        params = dict(pair.split('=') for pair in query.split('&') if '=' in pair)
        target_url = params.get('url')

        if not target_url:
            self._send_json(400, {"error": "Missing 'url' parameter"})
            return

        # اعتبارسنجی URL
        if not re.match(r'^https?://', target_url):
            target_url = 'https://' + target_url

        # هدرهای شبیه مرورگر عادی
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }

        try:
            req = urllib.request.Request(target_url, headers=headers, method=self.command)
            with urllib.request.urlopen(req, timeout=15) as resp:
                content = resp.read()
                self.send_response(200)
                self.send_header('Content-Type', resp.headers.get('Content-Type', 'text/plain'))
                self.send_header('Cache-Control', 'public, max-age=300')
                self.end_headers()
                self.wfile.write(content)
        except urllib.error.URLError as e:
            self._send_json(502, {"error": f"Upstream error: {str(e)}"})
        except Exception as e:
            self._send_json(500, {"error": str(e)})

    def _send_json(self, code, data):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())