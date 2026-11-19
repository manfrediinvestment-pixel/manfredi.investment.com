"""Completa gancho y seccion-3 con el cierre real de la primera rueda (Yahoo 5m) y el múltiplo del informe.
Uso: python rellenar.py <ruta a resultados.json del informe>"""
import json, sys, urllib.request
r = json.load(open(sys.argv[1], encoding='utf-8'))
req = urllib.request.Request('https://query1.finance.yahoo.com/v8/finance/chart/ANT?interval=5m&range=1d', headers={'User-Agent': 'Mozilla/5.0'})
c = json.load(urllib.request.urlopen(req))['chart']['result'][0]
px = [round(x, 2) for x in c['indicators']['quote'][0]['close'] if x is not None]
close = round(r['price'], 2)
px = [83.0, 111.5] + [p for p in px if p != 83.0][1:-1] + [close]   # salida, apertura, intradía, cierre
fmt = lambda v: f"{v:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
g = open('gancho/index.tpl.html', encoding='utf-8').read()
g = g.replace('__PX__', json.dumps(px)).replace('__CLOSE_LBL__', 'US$ ' + fmt(close))
open('gancho/index.html', 'w', encoding='utf-8').write(g)
rows = [('Palantir', 'CRECE 53%', r['peers']['PLTR']['mult']), ('Promedio', 'MSFT · NVDA · PLTR', r['peer_avg']),
        ('Anthropic', '+140% ESTIMADO 2027', r['ant_ev_rev27']), ('Microsoft', 'CRECE 19%', r['peers']['MSFT']['mult']),
        ('NVIDIA', 'CRECE 70%', r['peers']['NVDA']['mult'])]
rows.sort(key=lambda x: -x[2])
ant = lambda a, b: [a if n == 'Anthropic' else b for n, _, _ in rows]
s = open('seccion-3/index.tpl.html', encoding='utf-8').read()
s = (s.replace('__CP_LABELS__', json.dumps([x[0] for x in rows], ensure_ascii=False))
      .replace('__CP_SUBS__', json.dumps([x[1] for x in rows], ensure_ascii=False))
      .replace('__CP_VALUES__', json.dumps([round(x[2], 2) for x in rows]))
      .replace('__CP_COLORS__', json.dumps(ant('linear-gradient(90deg,#b8603f,#d97757)', '#3a4a6b')))
      .replace('__CP_VALCOLORS__', json.dumps(ant('#f0dcaa', '#e6cf96')))
      .replace('__CP_LABCOLORS__', json.dumps(ant('#f0dcaa', None))))
open('seccion-3/index.html', 'w', encoding='utf-8').write(s)
print('cierre', close, 'puntos', len(px), 'apertura->cierre', round((close/83-1)*100, 1), '% sobre 83', [x[:3:2] for x in rows])

# guion y vista previa
pct = (close / 83 - 1) * 100
rep = {'{CIERRE}': fmt(close), '{PCT_CIERRE}': ('+' if pct >= 0 else '−') + f"{abs(pct):.1f}%".replace('.', ','),
       '{MULT}': f"{r['ant_ev_rev27']:.1f}".replace('.', ','), '{PROM}': f"{r['peer_avg']:.0f}"}
for src, dst in (('GUION.tpl.md', 'GUION.md'), ('preview.tpl.html', 'salida/index.html')):
    t = open(src, encoding='utf-8').read()
    for k, v in rep.items(): t = t.replace(k, v)
    open(dst, 'w', encoding='utf-8').write(t)
print('guion y preview OK', rep)
