# Agrega la entrada de la edición 3T 2026 de JNJ al principio de informes/manifest.json (cifras desde model.json).
import json, sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
ROOT = Path(__file__).resolve().parents[5].as_posix()
MINUS = '−'
M = json.load(open('model.json', encoding='utf-8'))
p = ROOT + '/informes/manifest.json'
raw = open(p, encoding='utf-8').read()
lst = [e for e in json.loads(raw) if e.get('num') != 'jnj-2026-11-13']
def usd(v): return '$' + f'{v:,.2f}'
def pct(v): return (MINUS if v < 0 else '+') + f'{abs(v):.1f}%'
def susd(v): return (MINUS if v < 0 else '+') + '$' + f'{abs(v):,.2f}'
entry = {
    "num": "jnj-2026-11-13",
    "ticker": "JNJ",
    "title": "Informe actualizado: Johnson & Johnson (JNJ) — 3T 2026",
    "abstract": (f"Actualización con el tercer trimestre (cerrado el 27-sep-2026, reportado el 13-oct y 10-Q del 21-oct): ventas de ${M['rev3']:,.0f} millones ({pct(M['rev3_g'])}). "
                 f"Innovative Medicine creció {M['g3_im']:.1f}% con Stelara en {pct(M['g3_stelara'])}; sin Stelara, {M['g3_im_x_ste']:.1f}%. Los seis motores de reemplazo "
                 f"(Darzalex, Tremfya, Carvykti, Rybrevant, Spravato y Caplyta) crecieron {M['mot6_g3']:.0f}%, pero MedTech solo {M['g3_mt']:.1f}%, segundo trimestre por debajo de lo esperado. "
                 f"El cargo de $5,500 millones por el acuerdo de talco de ovario dejó el EPS GAAP en {usd(M['eps3'])}; guía de EPS ajustado subida a {usd(M['g_eps_mid'])}. "
                 f"La suma de partes baja de $97.56 a {usd(M['m1'])} (margen de caja anclado en un flujo operativo de {M['ttm_ocfm']:.1f}% y reserva total de talco de $9,000 millones), "
                 f"pero comparables, reversión y consenso suben: el blend pasa de $199.64 a {usd(M['blend'])} ({susd(M['bridge_model'])} del modelo). La acción subió "
                 f"{M['price_chg']:.1f}%, a {usd(M['price'])}, y la brecha pasa de {MINUS}25.8% a {pct(M['blend_gap'])}. La separación de DePuy Synthes (escisión, mediados de 2027) "
                 f"queda como escenario. El modelo de septiembre se reconstruyó (Base {usd(M['sep_rebuilt_m1'])} contra $97.56). Postura: neutral, con sesgo bajista."),
    "date": "13 de noviembre de 2026",
    "href": "informes/jnj.html",
    "publishedAt": "2026-11-13",
}
lst.insert(0, entry)
open(p, 'w', encoding='utf-8', newline='\n').write(json.dumps(lst, ensure_ascii=False, indent=2) + ('\n' if raw.endswith('\n') else ''))
chk = json.load(open(p, encoding='utf-8'))
assert chk[0]['num'] == 'jnj-2026-11-13'
print(chk[0]['abstract'])
