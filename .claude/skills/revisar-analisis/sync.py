"""Conecta la skill revisar-analisis con el worker manfredi-analistas.

    python .claude/skills/revisar-analisis/sync.py bajar          # pendientes sin revisión → revision/pendientes/
    python .claude/skills/revisar-analisis/sync.py bajar --todos  # también los ya revisados (para revisar de nuevo)
    python .claude/skills/revisar-analisis/sync.py subir <id>     # sube revision/pendientes/<id>/revision.json
    python .claude/skills/revisar-analisis/sync.py subir --todos  # sube todas las revisiones que falten

Variables de entorno:
    ANALISTAS_API        URL del worker (por defecto la de producción;
                         para probar en local: http://127.0.0.1:8791)
    ANALISTAS_ADMIN_KEY  la clave ADMIN_KEY del worker (wrangler secret). Nunca va al repo.
"""
import json, os, pathlib, sys, urllib.request, urllib.error

API = os.environ.get('ANALISTAS_API', 'https://manfredi-analistas.nachito2502.workers.dev').rstrip('/')
KEY = os.environ.get('ANALISTAS_ADMIN_KEY', '')
RAIZ = pathlib.Path(__file__).resolve().parents[3]
DESTINO = RAIZ / 'revision' / 'pendientes'


def pedir(metodo, ruta, cuerpo=None, crudo=False):
    data = json.dumps(cuerpo).encode() if cuerpo is not None else None
    r = urllib.request.Request(API + ruta, data=data, method=metodo, headers={'X-Admin-Key': KEY, 'Content-Type': 'application/json', 'User-Agent': 'revisar-analisis'})
    try:
        with urllib.request.urlopen(r, timeout=60) as resp:
            b = resp.read()
            return b if crudo else json.loads(b or b'{}')
    except urllib.error.HTTPError as e:
        sys.exit('Error %s en %s: %s' % (e.code, ruta, e.read()[:300].decode('utf-8', 'replace')))


def bajar(todos):
    envios = pedir('GET', '/creador/envios?estado=recibido')['envios']
    if not todos:
        envios = [e for e in envios if not e.get('revision')]
    DESTINO.mkdir(parents=True, exist_ok=True)
    ids = []
    for e in envios:
        d = DESTINO / e['id']
        d.mkdir(exist_ok=True)
        completo = pedir('GET', '/creador/envio/%s/envio.json' % e['id'])
        a = e.get('autorPerfil') or {}
        completo['autor'] = {'slug': a.get('slug', e.get('autor')), 'nombre': a.get('nombre', ''), 'email': e['email'], 'rol': a.get('rol', ''),
                             'pais': a.get('pais', 'AR'), 'asesor': bool(a.get('asesor')), 'links': a.get('links', {})}
        if e['formato'] == 'pdf':
            (d / 'analisis.pdf').write_bytes(pedir('GET', '/creador/envio/%s/analisis.pdf' % e['id'], crudo=True))
            try:
                (d / 'tapa.jpg').write_bytes(pedir('GET', '/creador/envio/%s/tapa.jpg' % e['id'], crudo=True))
            except SystemExit:
                pass
            completo['archivo'] = 'analisis.pdf'
        (d / 'envio.json').write_text(json.dumps(completo, ensure_ascii=False, indent=2), encoding='utf-8')
        ids.append(e['id'])
        print('bajado', e['id'], '·', e['titulo'])
    todos_ids = sorted(x.name for x in DESTINO.iterdir() if (x / 'envio.json').exists())
    (DESTINO / 'index.json').write_text(json.dumps({'origen': 'pendientes', 'envios': todos_ids}, indent=2), encoding='utf-8')
    print('%d envíos para revisar' % len(ids) if ids else 'No hay envíos nuevos para revisar.')


def subir(ids):
    for i in ids:
        f = DESTINO / i / 'revision.json'
        if not f.exists():
            print('sin revision.json:', i)
            continue
        pedir('POST', '/creador/revision', {'id': i, 'revision': json.loads(f.read_text(encoding='utf-8'))})
        (DESTINO / i / '.subida').write_text('ok')
        print('subida', i)


if __name__ == '__main__':
    if not KEY:
        sys.exit('Falta ANALISTAS_ADMIN_KEY (la clave ADMIN_KEY del worker).')
    if len(sys.argv) < 2 or sys.argv[1] not in ('bajar', 'subir'):
        sys.exit(__doc__)
    if sys.argv[1] == 'bajar':
        bajar('--todos' in sys.argv)
    else:
        if '--todos' in sys.argv:
            ids = [x.name for x in DESTINO.iterdir() if (x / 'revision.json').exists() and not (x / '.subida').exists()] if DESTINO.exists() else []
        else:
            ids = sys.argv[2:]
        subir(ids)
