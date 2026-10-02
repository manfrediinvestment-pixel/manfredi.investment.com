# Agrega la entrada de PEP al principio de informes/manifest.json (json.dumps, sin heredoc de bash).
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4].as_posix()
MINUS = '−'
M = json.load(open(HERE/'model.json'))
p = ROOT + '/informes/manifest.json'
raw = open(p, encoding='utf-8').read()
lst = [e for e in json.loads(raw) if e.get('ticker') != 'PEP']
def usd(v): return '$' + f'{v:,.2f}'
def pct(v): return (MINUS if v < 0 else '+') + f'{abs(v):.1f}%'
entry = {
    "num": "pep-2026-10-02",
    "ticker": "PEP",
    "title": "Nuevo informe: PepsiCo (PEP) — snacks y bebidas, Elliott, suma de partes y comparación con Coca-Cola bajo la misma vara",
    "abstract": (f"El crecimiento de PepsiCo viene del precio: el volumen orgánico fue negativo en {M['neg_vol_q']:.0f} de los últimos doce trimestres "
                 f"y las bebidas de Norteamérica pierden volumen hace ocho. A {M['pe_ntm_now']:.1f}x las ganancias de los próximos doce meses, "
                 f"el blend de cinco métodos da {usd(M['blend'])}, {pct(M['blend_gap'])} contra {usd(M['price'])}, pero el flujo de caja "
                 f"descontado da {usd(M['dcf_base'])}: está barata contra sus pares y su historia, no en términos absolutos. Bajo la misma "
                 f"vara, Coca-Cola cotiza {M['gap_pe']:.1f} puntos de P/E más cara y el modelo de negocio explica menos de la mitad."),
    "date": "2 de octubre de 2026",
    "href": "informes/pep.html",
    "publishedAt": "2026-10-02",
}
lst.insert(0, entry)
open(p, 'w', encoding='utf-8', newline='\n').write(json.dumps(lst, ensure_ascii=False, indent=2) + ('\n' if raw.endswith('\n') else ''))
chk = json.load(open(p, encoding='utf-8'))
assert chk[0]['ticker'] == 'PEP'
print(chk[0]['abstract']); print(len(chk))
