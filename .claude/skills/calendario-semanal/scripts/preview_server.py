# -*- coding: utf-8 -*-
"""Vista previa local del calendario con los datos de una semana nueva.

Sirve el sitio (una carpeta con index.html) y, en /preview.html, entrega index.html con
las respuestas del worker reemplazadas por los JSON de la semana: /calendario siempre, y
/earnings y /dividends si se pasan. No modifica ningun archivo del repo; el resto del
sitio (y los demas endpoints) siguen reales.

Uso:
    python preview_server.py <raiz-del-repo> <semana.json> [puerto]
                             [--earnings earnings.json] [--dividends dividendos.json]
Luego abrir  http://localhost:8899/preview.html#calendario  y usar las pestanas
Economico / Earnings / Dividendos de la grilla.
Se apaga con Ctrl+C (o deteniendo la tarea si se lanzo en segundo plano).
"""
import http.server
import io
import json
import os
import socketserver
import sys

args = sys.argv[1:]
opts = {}
for flag in ("--earnings", "--dividends"):
    if flag in args:
        i = args.index(flag)
        if i + 1 >= len(args):
            sys.exit("Falta el archivo despues de " + flag)
        opts[flag[2:]] = args[i + 1]
        del args[i:i + 2]

if len(args) < 2:
    sys.exit(__doc__)

ROOT = os.path.abspath(args[0])
PORT = int(args[2]) if len(args) > 2 else 8899

if not os.path.isfile(os.path.join(ROOT, "index.html")):
    sys.exit("No hay index.html en " + ROOT)


def cargar(path):
    return json.load(io.open(os.path.abspath(path), encoding="utf-8"))


# endpoint del worker -> JSON a devolver
DATOS = {"calendario": cargar(args[1])}
for nombre, path in opts.items():
    DATOS[nombre] = cargar(path)

# Intercepta fetch() hacia .../manfredi-calendario.../<endpoint> y responde con la semana nueva.
INJECT = (
    "<script>(function(){var D=" + json.dumps(DATOS, ensure_ascii=False) + ";var F=window.fetch;"
    "window.fetch=function(u){var s=String(u&&u.url||u);"
    "if(s.indexOf('manfredi-calendario')>-1){"
    "var m=s.match(/\\/(calendario|earnings|dividends)(\\?|$)/);"
    "if(m&&D[m[1]]){return Promise.resolve(new Response(JSON.stringify(D[m[1]]),"
    "{status:200,headers:{'Content-Type':'application/json'}}));}}"
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
    print("Vista previa en http://localhost:%d/preview.html#calendario (%s)"
          % (PORT, ", ".join(sorted(DATOS))), flush=True)
    httpd.serve_forever()
