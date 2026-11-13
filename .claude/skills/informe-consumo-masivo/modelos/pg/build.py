# Arma informes/pg.html: CSS y motor de gráficos congelados (modelos/_motor/pg_motor_sep2026.html, copia del pg.html de
# septiembre que también usan KO, PEP, WMT y UNH) + parches + plantilla pg.tpl.html + model.json.
import subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[5].as_posix()   # raíz del repo
base = open(f'{ROOT}/.claude/skills/informe-consumo-masivo/modelos/_motor/pg_motor_sep2026.html', encoding='utf-8').read()
css = base[base.index('<style>'): base.index('</style>')+len('</style>')]
# CERO texto gris: la nota de la portada tenía #5d646f (KO y PEP lo heredaron de acá); pasa al azul oscuro del sitio
assert css.count('.verdict-note{color:#5d646f !important;}') == 1
css = css.replace('.verdict-note{color:#5d646f !important;}', '.verdict-note{color:var(--muted) !important;}')
assert '#5d646f' not in css
# tablas anchas: el texto de las celdas largas se parte (celular)
css = css.replace('</style>', '  td.label.wrap{white-space:normal; min-width:180px;}\n</style>')
s0 = base.index('<script>', base.index('</style>'))
s1 = base.index('  function renderAll(){', s0)
eng = base[s0:s1]
# ---- parches de KO (leyenda de drawLines en varias filas, grilla de drawGroupedBars, rombos chicos en celular)
a = "    var minV = Math.min.apply(null, allVals) * 0.92;\n"
assert eng.count(a) == 1; eng = eng.replace(a, a + "    if(opts.minV != null) minV = opts.minV; if(opts.maxV != null) maxV = opts.maxV;\n", 1)
a = "    var padL = 40, padR = 28, padT = 16, padB = 54;\n"
assert eng.count(a) == 1
eng = eng.replace(a, a + "    ctx.font = '11px \"Inter\", sans-serif'; var lw = 0; series.forEach(function(s){ lw += 14 + ctx.measureText(s.name).width + 20; }); padB += Math.max(0, Math.ceil(lw / (W - padL)) - 1) * 15;\n", 1)
a = "    for(var gv = Math.ceil(minV); gv <= Math.floor(maxV); gv++){\n"
assert eng.count(a) == 1
eng = eng.replace(a, "    var gstep = (maxV - minV) > 24 ? 5 : ((maxV - minV) > 12 ? 2 : 1);\n    for(var gv = Math.ceil(minV/gstep)*gstep; gv <= Math.floor(maxV); gv += gstep){\n", 1)
a = """        ctx.font = '600 10.5px "IBM Plex Mono", monospace'; ctx.textAlign = 'center';
        var mv = markers.values[i];
        ctx.fillText((mv>0?'+':'')+mv+'%', cx, padT - 6);"""
assert eng.count(a) == 1
eng = eng.replace(a, """        var narrow = slot < 44;
        ctx.font = (narrow ? '600 9px' : '600 10.5px') + ' "IBM Plex Mono", monospace'; ctx.textAlign = 'center';
        var mv = markers.values[i];
        ctx.fillText((mv>0?'+':'')+mv+(narrow?'':'%'), cx, padT - 6);""", 1)
# ---- drawLines: etiquetas de valor con pointLabels:true (formato opcional labelFmt) y, si son muchas, solo la primera y
# la última de cada serie
a = """        if(opts.valueFmt){"""
assert eng.count(a) == 1
eng = eng.replace(a, """        if(opts.pointLabels && !opts.valueFmt){
          var lf = opts.labelFmt || function(x){ return x.toFixed(1); };
          if(s.values.length <= 8 || i === 0 || i === s.values.length-1){
            ctx.font = '600 10px "IBM Plex Mono", monospace'; ctx.textAlign = 'center'; ctx.fillText(lf(v), x, y - 8);
          }
        }
        if(opts.valueFmt){""", 1)
tpl = open('pg.tpl.html', encoding='utf-8').read().replace('@@CSS@@', css).replace('@@ENGINE@@', eng.rstrip())
assert '@@' not in tpl
open('pg.full.tpl.html', 'w', encoding='utf-8', newline='\n').write(tpl)
subprocess.run([sys.executable, 'render.py', 'pg.full.tpl.html', f'{ROOT}/informes/pg.html'], check=True)
