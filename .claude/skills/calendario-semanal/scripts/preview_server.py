# -*- coding: utf-8 -*-
"""Vista previa local del calendario con los datos de una semana nueva.

Sirve el sitio (una carpeta con index.html) y, en /preview.html, entrega index.html con
la respuesta del worker /calendario reemplazada por el JSON de la semana. No modifica
ningun archivo del repo; el resto del sitio (y los demas endpoints) siguen reales.

Uso:
    python preview_server.py <raiz-del-repo> <semana.json> [puerto]
Luego abrir  http://localhost:8899/preview.html#calendario
Se apaga con Ctrl+C (o deteniendo la tarea si se lanzo en segundo plano).
"""
import http.server
import io
import json
import os
import socketserver
import sys

if len(sys.argv) < 3:
    sys.exit(__doc__)

ROOT = os.path.abspath(sys.argv[1])
DATA = os.path.abspath(sys.argv[2])
PORT = int(sys.argv[3]) if len(sys.argv) > 3 else 8899

if not os.path.isfile(os.path.join(ROOT, "index.html")):
    sys.exit("No hay index.html en " + ROOT)

data = json.dumps(json.load(io.open(DATA, encoding="utf-8")), ensure_ascii=False)

# Intercepta fetch() hacia .../manfredi-calendario.../calendario y responde con la semana nueva.
INJECT = (
    "<script>(function(){var D=" + data + ";var F=window.fetch;"
    "window.fetch=function(u){var s=String(u&&u.url||u);"
    "if(s.indexOf('manfredi-calendario')>-1&&/\\/calendario(\\?|$)/.test(s)){"
    "return Promise.resolve(new Response(JSON.stringify(D),"
    "{status:200,headers:{'Content-Type':'application/json'}}));}"
    "return F.apply(this,arguments);};})();</script>"
).encode("utf-8")


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=ROOT, **k)

    def do_GET(self):
        if self.path.split("?")[0] in ("/preview.html", "/preview"):
            raw = io.open(os.path.join(ROOT, "index.html"), "rb").read()
            i = raw.lower().find(b"<head")
            j = raw.find(b">", i) + 1
            body = raw[:j] + INJECT + raw[j:]
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        return super().do_GET()

    def log_message(self, *a):
        pass


socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
    print("Vista previa en http://localhost:%d/preview.html#calendario" % PORT, flush=True)
    httpd.serve_forever()
