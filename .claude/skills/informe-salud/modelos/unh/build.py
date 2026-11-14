# Arma informes/unh.html: CSS y motor de gráficos de informes/pg.html (ya probados en celular) + plantilla + modelo.
import subprocess, sys, os
from pathlib import Path
ROOT = Path(__file__).resolve().parents[5].as_posix()   # raíz del repo
pg = open(f'{ROOT}/.claude/skills/informe-consumo-masivo/modelos/_motor/pg_motor_sep2026.html', encoding='utf-8').read()   # motor congelado: pg.html cambia en cada edición de PG
css = pg[pg.index('<style>'): pg.index('</style>')+len('</style>')]
css = css.replace('content:"PG";', 'content:"UNH";')
assert 'content:"UNH"' in css
css = css.replace('.verdict-note{color:#5d646f !important;}', '.verdict-note{color:var(--muted) !important;}')   # CERO texto gris
assert '#5d646f' not in css and '.verdict-note{color:var(--muted) !important;}' in css
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
