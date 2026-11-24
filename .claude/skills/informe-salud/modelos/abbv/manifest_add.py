# Agrega la entrada del informe inicial de ABBV al principio de informes/manifest.json (cifras desde model.json).
# NO se corre en la rama del informe: se corre en la integración (feat/defensivos-10-de-10).
# Catálogo de la estantería: después de este script, `node scripts/catalogo-informes.mjs` regenera informes/catalogo.json
# leyendo informes/*.html y la fecha de publicación de este manifest (no hace falta editarlo a mano).
import json, sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4].as_posix()
MINUS = '−'
M = json.load(open(HERE / 'model.json', encoding='utf-8'))
p = ROOT + '/informes/manifest.json'
raw = open(p, encoding='utf-8').read()
NUM = 'abbv-2026-11-22'
lst = [e for e in json.loads(raw) if e.get('num') != NUM]
def usd(v): return '$' + f'{v:,.2f}'
def pct(v): return (MINUS if v < 0 else '+') + f'{abs(v):.1f}%'
entry = {
    "num": NUM,
    "ticker": "ABBV",
    "title": "Informe inicial: AbbVie Inc. (ABBV) — 3T 2026",
    "abstract": (f"Informe inicial con datos al tercer trimestre (comunicado del 30-oct-2026 y 10-Q del 3-nov-2026): ingresos de ${M['rev3']:,.0f} millones ({pct(M['rev3_g'])}), "
                 f"con Skyrizi y Rinvoq en ${M['sky_rin3']:,.0f} millones ({pct(M['sky_rin3_g'])}), {M['sky_rin3_share']:.0f}% de las ventas. Humira, que facturó $21,237 millones en 2022, "
                 f"perdió {M['hum_us_y3']:.0f}% de sus ventas en EE.UU. en tres años de biosimilares: el informe usa esa curva real como análogo para Skyrizi (patente de 2033) "
                 f"y Rinvoq (genéricos desde abril de 2037). La suma de partes producto por producto + pipeline ponderado da {usd(M['m1'])}; comparables contra 13 pharmas (mediana) "
                 f"{usd(M['m2'])}; reversión al múltiplo posterior a Humira {usd(M['m3'])}; consenso {usd(M['m4'])}. Blend {usd(M['blend'])} vs. {usd(M['price'])} "
                 f"(cierre del 20-nov), {pct(M['blend_gap'])}. Puente GAAP → ajustado (amortización y regalías contingentes de Skyrizi), deuda de Apogee "
                 f"({M['nd_ebitda']:.2f}x EBITDA) y dividendo con {M['payout_fcf']:.0f}% del FCF. Postura: {M['postura'].lower()}."),
    "date": "22 de noviembre de 2026",
    "href": "informes/abbv.html",
    "publishedAt": "2026-11-22",
}
lst.insert(0, entry)
open(p, 'w', encoding='utf-8', newline='\n').write(json.dumps(lst, ensure_ascii=False, indent=2) + ('\n' if raw.endswith('\n') else ''))
chk = json.load(open(p, encoding='utf-8'))
assert chk[0]['num'] == NUM
print(chk[0]['abstract'])
