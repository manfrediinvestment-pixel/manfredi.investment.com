# Agrega la entrada del informe inicial de PFE al principio de informes/manifest.json (cifras desde model.json).
import json, sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4].as_posix()
MINUS = '−'
M = json.load(open(HERE / 'model.json', encoding='utf-8'))
p = ROOT + '/informes/manifest.json'
raw = open(p, encoding='utf-8', newline='').read()   # conserva CRLF
NL = chr(13) + chr(10) if chr(13) + chr(10) in raw else chr(10)
NUM = 'pfe-2026-11-23'
lst = [e for e in json.loads(raw) if e.get('num') != NUM]
def usd(v): return '$' + f'{v:,.2f}'
def pct(v): return (MINUS if v < 0 else '+') + f'{abs(v):.1f}%'
entry = {
    "num": NUM,
    "ticker": "PFE",
    "title": "Informe inicial: Pfizer Inc. (PFE) — 3T 2026",
    "abstract": (f"Informe inicial con el tercer trimestre (comunicado y 10-Q del 3-nov-2026): ingresos de ${M['rev3']:,.0f} millones ({pct(M['rev3_g'])}), "
                 f"con el resto de la cartera +{M['rev3_xcov_g_op']:.0f}% sin COVID y guía 2026 subida a ${M['g_rev_lo']:.0f}-{M['g_rev_hi']:.0f} mil millones. "
                 f"El precipicio de patentes: ${M['gap30']:.1f} mil millones de ventas ({M['gap30_pct']:.1f}%) pierden la exclusividad antes de fin de 2030 "
                 f"(Eliquis en abril de 2028, Ibrance y Xtandi en 2027, Vyndaqel fuera de EE.UU.). La suma de partes producto por producto con el pipeline "
                 f"ponderado (Metsera, Seagen, PD-1 x VEGF) da {usd(M['m1'])}; comparables con la mediana de 13 pares {usd(M['m2'])}; reversión en la ventana "
                 f"posterior a la COVID {usd(M['m3'])}; consenso {usd(M['m4'])}. Blend {usd(M['blend'])} vs. {usd(M['price'])} ({pct(M['blend_gap'])}). "
                 f"Dividendo de {M['div_yield']:.2f}% cubierto {M['div_cover_fcf']:.2f} veces por el flujo de caja libre. Postura: {M['postura']}."),
    "date": "23 de noviembre de 2026",
    "href": "informes/pfe.html",
    "publishedAt": "2026-11-23",
}
lst.insert(0, entry)
out = json.dumps(lst, ensure_ascii=False, indent=2) + (chr(10) if raw.endswith(NL) else '')
open(p, 'w', encoding='utf-8', newline='').write(out.replace(chr(10), NL))
chk = json.load(open(p, encoding='utf-8'))
assert chk[0]['num'] == NUM
print(chk[0]['abstract'])
