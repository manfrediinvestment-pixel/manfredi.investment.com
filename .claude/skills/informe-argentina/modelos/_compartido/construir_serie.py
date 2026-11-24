"""Serie histórica trimestral compartida por los bancos argentinos (GGAL, BMA, BBAR, SUPV).

Construye, a cada cierre de trimestre (dic-2016 → sep-2026):
  - riesgo país EMBI (pb)              — api.argentinadatos.com /v1/finanzas/indices/riesgo-pais
  - CCL (venta)                        — api.argentinadatos.com /v1/cotizaciones/dolares/contadoconliqui
  - IPC (índice encadenado, base dic-2016 = 100) — api.argentinadatos.com /v1/finanzas/indices/inflacion (INDEC)
  - precio ADR GGAL / BMA (USD) y acción local (ARS) — Yahoo chart API
  - P/BV en pesos de GGAL y BMA = precio local × acciones / patrimonio nominal de esa fecha
    (patrimonio: 20-F XBRL de SEC a cada 31-dic 2018-2024 + trimestres 2025-2026 de los 6-K;
     entre dos datos se interpola geométricamente; antes de 2020 el patrimonio NO está ajustado
     por inflación — NIC 29 para bancos rige desde ene-2020 — así que el P/BV 2018-19 está inflado).

Uso:  python construir_serie.py <dir_con_json_crudos>
      (si falta un archivo lo baja; escribe serie-trimestral.json al lado de este script)
"""
import json, os, sys, datetime, urllib.request
from math import log, exp

AQUI = os.path.dirname(os.path.abspath(__file__))
RAW = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, "_crudos")
os.makedirs(RAW, exist_ok=True)

FUENTES = {
    "rp.json": "https://api.argentinadatos.com/v1/finanzas/indices/riesgo-pais",
    "ccl.json": "https://api.argentinadatos.com/v1/cotizaciones/dolares/contadoconliqui",
    "ipc.json": "https://api.argentinadatos.com/v1/finanzas/indices/inflacion",
    "h_GGAL.json": "https://query1.finance.yahoo.com/v8/finance/chart/GGAL?period1=1451606400&period2=1795000000&interval=1d",
    "h_BMA.json": "https://query1.finance.yahoo.com/v8/finance/chart/BMA?period1=1451606400&period2=1795000000&interval=1d",
    "h_GGAL.BA.json": "https://query1.finance.yahoo.com/v8/finance/chart/GGAL.BA?period1=1451606400&period2=1795000000&interval=1d",
    "h_BMA.BA.json": "https://query1.finance.yahoo.com/v8/finance/chart/BMA.BA?period1=1451606400&period2=1795000000&interval=1d",
}
for f, u in FUENTES.items():
    p = os.path.join(RAW, f)
    if not os.path.exists(p):
        req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
        open(p, "wb").write(urllib.request.urlopen(req, timeout=60).read())

def cargar(f):
    return json.load(open(os.path.join(RAW, f), encoding="utf-8"))

def serie_fecha(lista, campo="valor"):
    return sorted((x["fecha"][:10], x[campo]) for x in lista)

def ultimo_hasta(serie, fecha):
    v = None
    for d, x in serie:
        if d <= fecha:
            v = x
        else:
            break
    return v

def yahoo(f):
    d = cargar(f)["chart"]["result"][0]
    out = []
    for ts, c in zip(d["timestamp"], d["indicators"]["quote"][0]["close"]):
        if c:
            out.append((datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).strftime("%Y-%m-%d"), c))
    return out

rp = serie_fecha(cargar("rp.json"))
ccl = serie_fecha(cargar("ccl.json"), "venta")
# IPC mensual (%) → índice encadenado
ipc_m = serie_fecha(cargar("ipc.json"))
idx, nivel = [], 100.0
for d, v in ipc_m:
    if d > "2016-12-31":
        nivel *= 1 + v / 100
        idx.append((d, nivel))
    elif d[:7] == "2016-12":
        idx.append((d, 100.0))

px = {t: yahoo(f"h_{t}.json") for t in ["GGAL", "BMA", "GGAL.BA", "BMA.BA"]}

# Patrimonio nominal (ARS) a cada fecha — fuente en el docstring
PATRIMONIO = {
    "GGAL": {"2018-12-31": 60125152e3, "2019-12-31": 113941959e3, "2020-12-31": 182333732e3,
             "2021-12-31": 304469220e3, "2022-12-31": 608877539e3, "2023-12-31": 2017155269e3,
             "2024-12-31": 6063585599e3, "2025-06-30": 6927260013e3, "2025-09-30": 7092570000e3,
             "2025-12-31": 7759335807e3, "2026-03-31": 8589046000e3, "2026-06-30": 9197727443e3},
    "BMA": {"2018-12-31": 60908329e3, "2019-12-31": 106054978e3, "2020-12-31": 151543943e3,
            "2021-12-31": 239599563e3, "2022-12-31": 512144187e3, "2023-12-31": 2043559163e3,
            "2024-12-31": 4049083078e3, "2025-03-31": 4439133000e3, "2025-06-30": 4515765900e3,
            "2025-09-30": 4756885134e3, "2026-03-31": 5855969445e3, "2026-06-30": 6291414498e3},
}
# Acciones en circulación (20-F: weighted average / issued; HSBC Argentina dic-2024 → 1.606,3 M en GGAL)
def acciones(t, fecha):
    if t == "GGAL":
        if fecha < "2020-09-30":
            return 1426.765e6
        if fecha < "2024-12-06":
            return 1474.692e6
        return 1606.3e6
    return 669.663e6 if fecha < "2019-06-30" else 639.413e6

def patrimonio_interp(t, fecha):
    pts = sorted(PATRIMONIO[t].items())
    if fecha < pts[0][0]:
        return None
    if fecha > pts[-1][0]:  # estimado: último patrimonio reexpresado por IPC (sin sumar resultados)
        return pts[-1][1] * ultimo_hasta(idx, fecha) / ultimo_hasta(idx, pts[-1][0])
    for (d0, v0), (d1, v1) in zip(pts, pts[1:]):
        if d0 <= fecha <= d1:
            f0 = datetime.date.fromisoformat(d0); f1 = datetime.date.fromisoformat(d1)
            w = (datetime.date.fromisoformat(fecha) - f0).days / (f1 - f0).days
            return exp(log(v0) + w * (log(v1) - log(v0)))
    return pts[-1][1]

cierres = []
for y in range(2016, 2027):
    for m, dd in ((3, 31), (6, 30), (9, 30), (12, 31)):
        f = f"{y}-{m:02d}-{dd}"
        if "2016-12-31" <= f <= "2026-09-30":
            cierres.append(f)

filas = []
for f in cierres:
    fila = {"fecha": f, "riesgo_pais": ultimo_hasta(rp, f), "ccl": ultimo_hasta(ccl, f),
            "ipc_idx": round(ultimo_hasta(idx, f), 2)}
    for t in ("GGAL", "BMA"):
        adr = ultimo_hasta(px[t], f); loc = ultimo_hasta(px[t + ".BA"], f)
        fila[f"{t.lower()}_adr"] = round(adr, 2)
        eq = patrimonio_interp(t, f)
        fila[f"{t.lower()}_pbv"] = round(loc * acciones(t, f) / eq, 3) if eq and loc else None
    filas.append(fila)

out = {"generado": "2026-11-23", "nota": __doc__.strip().split("\n")[0], "filas": filas}
json.dump(out, open(os.path.join(AQUI, "serie-trimestral.json"), "w", encoding="utf-8"), indent=1,
          ensure_ascii=False)

if __name__ == "__main__":
    print(f"{'fecha':10} {'RP':>5} {'CCL':>7} {'GGAL$':>6} {'GGAL P/BV':>9} {'BMA$':>6} {'BMA P/BV':>8}")
    for r in filas:
        print(f"{r['fecha']:10} {r['riesgo_pais']:>5} {r['ccl']:>7.1f} {r['ggal_adr']:>6} "
              f"{str(r['ggal_pbv']):>9} {r['bma_adr']:>6} {str(r['bma_pbv']):>8}")
