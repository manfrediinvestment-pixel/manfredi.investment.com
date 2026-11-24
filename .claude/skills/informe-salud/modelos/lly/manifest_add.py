# Agrega la entrada de la edición 3T 2026 de LLY al principio de informes/manifest.json (json.dumps, sin heredoc de bash)
# y repara la entrada de septiembre, a la que el shell le había comido los "$3", "$7", "$9" y "$1" del texto.
import json, sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
ROOT = Path(__file__).resolve().parents[5].as_posix()
MINUS = '−'
M = json.load(open('model.json', encoding='utf-8'))
p = ROOT + '/informes/manifest.json'
raw = open(p, encoding='utf-8').read()
lst = json.loads(raw)
for e in lst:
    if e.get('num') == 'lly-2026-09-24':
        a = e['abstract']
        for x, y in [('(86.44)', '($386.44)'), ('(50.91)', '($750.91)'), ('Blend 86.03 vs. ,150.99', 'Blend $986.03 vs. $1,150.99')]:
            if x in a: a = a.replace(x, y)
        e['abstract'] = a
lst = [e for e in lst if e.get('num') != 'lly-2026-11-13']
def usd(v): return '$' + f'{v:,.2f}'
def pct(v): return (MINUS if v < 0 else '+') + f'{abs(v):.1f}%'
entry = {
    "num": "lly-2026-11-13",
    "ticker": "LLY",
    "title": "Informe actualizado: Eli Lilly and Company (LLY) — 3T 2026",
    "abstract": (f"Actualización con el tercer trimestre (reportado y 10-Q del 29-oct-2026): ingresos de ${M['rev3']:,.0f} millones (+{M['rev3_g']:.0f}%), "
                 f"con volumen +{M['vp']['tot']['vol']}% y precio realizado {MINUS}{abs(M['vp']['tot']['price'])}% ({MINUS}{abs(M['us_price_ex_adj'])}% en EE.UU. sin ajustes de descuentos). "
                 f"Mounjaro y Zepbound sumaron ${M['tirz3']:,.0f} millones (+{M['tirz3_g']:.0f}%) y Foundayo ${M['found3']:.0f} millones, todavía por detrás de la pastilla de Novo. "
                 f"Guía 2026 subida por tercera vez: ingresos de ${M['g_rev_lo']:.0f}-{M['g_rev_hi']:.0f} mil millones y margen de desempeño de {M['g_pm_lo']:.1f}%-{M['g_pm_hi']:.1f}%. "
                 f"El blend sube de $986.03 a {usd(M['blend'])}: la suma de partes por producto pasa de $386.44 a {usd(M['m1'])} (tirzepatida anclada en el consenso 2027, "
                 f"margen por la guía y dos activos de fase 3 más), y prácticamente todo el cambio es del modelo ({'+' if M['bridge_model'] > 0 else MINUS}${abs(M['bridge_model']):.2f}). "
                 f"Pero la acción subió {M['price_move']:.1f}%, a {usd(M['price'])}: la brecha pasa de {MINUS}14.3% a {pct(M['blend_gap'])}, y ahora también la reversión a su propio "
                 f"múltiplo ({usd(M['m3'])}) queda debajo del precio; solo el consenso ({usd(M['m4'])}) lo supera. El modelo de septiembre se reconstruyó "
                 f"(Base {usd(M['sep_rebuilt_m1'])} contra $386.44 publicado). Postura: neutral, con sesgo bajista."),
    "date": "13 de noviembre de 2026",
    "href": "informes/lly.html",
    "publishedAt": "2026-11-13",
}
lst.insert(0, entry)
open(p, 'w', encoding='utf-8', newline='\n').write(json.dumps(lst, ensure_ascii=False, indent=2) + ('\n' if raw.endswith('\n') else ''))
chk = json.load(open(p, encoding='utf-8'))
assert chk[0]['num'] == 'lly-2026-11-13'
print(chk[0]['abstract']); print([e['abstract'][:200] for e in chk if e.get('num') == 'lly-2026-09-24'])
