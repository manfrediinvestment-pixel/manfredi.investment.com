# Arma informes/unh.html: CSS y motor de gráficos de informes/pg.html (ya probados en celular) + plantilla + modelo.
import subprocess, sys, os
from pathlib import Path
ROOT = Path(__file__).resolve().parents[5].as_posix()   # raíz del repo
pg = open(f'{ROOT}/informes/pg.html', encoding='utf-8').read()
css = pg[pg.index('<style>'): pg.index('</style>')+len('</style>')]
css = css.replace('content:"PG";', 'content:"UNH";')
assert 'content:"UNH"' in css
s0 = pg.index('<script>', pg.index('</style>'))
s1 = pg.index('  function renderAll(){', s0)
eng = pg[s0:s1]
for fn in ('function drawVBars','function drawHBars','function drawLines','function drawRangeBars','function drawGroupedBars','function drawLegend','function wrapLabel','var padL = Math.min(opts.padL || 128'):
    assert fn in eng, fn
# drawLines: rango del eje Y opcional (opts.minV / opts.maxV) para escalas limpias
a = "    var minV = Math.min.apply(null, allVals) * 0.92;\n"
assert a in eng, 'drawLines minV'
eng = eng.replace(a, a + "    if(opts.minV != null) minV = opts.minV; if(opts.maxV != null) maxV = opts.maxV;\n", 1)
ch = open('charts_unh.js', encoding='utf-8').read()
tpl = open('unh.tpl.html', encoding='utf-8').read().replace('@@CSS@@', css).replace('@@SCRIPT@@', eng.rstrip() + '\n' + ch.lstrip('\n').rstrip('\n'))
assert '@@' not in tpl
open('unh.full.tpl.html', 'w', encoding='utf-8', newline='\n').write(tpl)
subprocess.run([sys.executable, 'render.py', 'unh.full.tpl.html', f'{ROOT}/informes/unh.html'], check=True)
