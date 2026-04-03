import json, urllib.request, urllib.error, os
from datetime import datetime, timezone, timedelta

ARG_TZ = timezone(timedelta(hours=-3))
now = datetime.now(ARG_TZ)
fecha = now.strftime("%d/%m/%Y")
hora = now.strftime("%H:%M")

def fetch(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read())
    except Exception as e:
        print(f"Error: {url} -> {e}")
        return None

def yahoo(ticker, nombre):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=2d"
    data = fetch(url)
    if not data:
        return {"valor": None, "variacion": None}
    try:
        meta = data["chart"]["result"][0]["meta"]
        precio = meta.get("regularMarketPrice", 0)
        anterior = meta.get("previousClose", 0)
        var = round(((precio - anterior) / anterior) * 100, 2) if anterior else 0
        var_str = f"{'+' if var >= 0 else ''}{var}%"
        return {"valor": round(precio, 2), "variacion": var_str}
    except:
        return {"valor": None, "variacion": None}

# ── ARGENTINA ─────────────────────────────────────────────────────
print("Generando argentina.json...")
dolar_raw = fetch("https://dolarapi.com/v1/dolares") or []
dolar = {}
for d in dolar_raw:
    casa = d.get("casa", "").lower()
    dolar[casa] = d.get("venta")

merval_raw = yahoo("%5EMERV", "Merval")
merval_precio = merval_raw.get("valor")
merval_var = merval_raw.get("variacion", "")
try:
    var_num = float(merval_var.replace('%','').replace('+',''))
    tendencia = "alcista" if var_num > 0 else "bajista"
except:
    tendencia = "neutral"

blue_v = dolar.get("blue")
mep_v = dolar.get("bolsa")
oficial_v = dolar.get("oficial")

argentina = {
    "fecha": fecha,
    "hora": hora,
    "resumen": f"Mercado argentino al {fecha}. Dólar blue: ${blue_v}. MEP: ${mep_v}. Merval: {merval_precio} pts ({merval_var}).",
    "dolar": {
        "blue": f"${blue_v}" if blue_v else "—",
        "oficial": f"${oficial_v}" if oficial_v else "—",
        "mep": f"${mep_v}" if mep_v else "—",
        "ccl": f"${dolar.get('contadoconliqui')}" if dolar.get("contadoconliqui") else "—",
        "brecha": None
    },
    "merval": {
        "valor": merval_precio,
        "variacion": merval_var,
        "tendencia": tendencia
    },
    "bcra": {
        "reservas": "Ver BCRA.gob.ar",
        "tasa": "—",
        "nota": None
    },
    "noticias": [],
    "conclusion": f"Datos actualizados automáticamente a las {hora} hs del {fecha}."
}

os.makedirs("reports", exist_ok=True)
with open("reports/argentina.json", "w", encoding="utf-8") as f:
    json.dump(argentina, f, ensure_ascii=False, indent=2)
print("reports/argentina.json OK")

# ── WALL STREET ───────────────────────────────────────────────────
print("Generando wallstreet.json...")
sp = yahoo("%5EGSPC", "S&P 500")
dj = yahoo("%5EDJI", "Dow Jones")
nq = yahoo("%5EIXIC", "Nasdaq")
oro = yahoo("GC%3DF", "Oro")
wti = yahoo("CL%3DF", "WTI")
soja = yahoo("ZS%3DF", "Soja")

wallstreet = {
    "fecha": fecha,
    "hora": hora,
    "horario_datos": f"Datos al cierre · {fecha}",
    "resumen": f"Wall Street al {fecha}. S&P 500: {sp.get('valor','N/D')} ({sp.get('variacion','N/D')}). Oro: ${oro.get('valor','N/D')}.",
    "indices": {
        "sp500": sp,
        "dow": dj,
        "nasdaq": nq
    },
    "bonos_usa": {
        "t10_yield": "—",
        "lectura": "neutral",
        "nota": None
    },
    "commodities": {
        "oro": {"precio": f"${oro.get('valor','—')}", "variacion": oro.get("variacion","")},
        "wti": {"precio": f"${wti.get('valor','—')}", "variacion": wti.get("variacion","")},
        "soja": {"precio": f"${soja.get('valor','—')}", "variacion": soja.get("variacion","")}
    },
    "macro_fed": {
        "postura_fed": "neutral",
        "nota": "Seguí la Fed en Investing.com para datos en tiempo real."
    },
    "impacto_argentina": f"Mercados globales actualizados al {fecha}.",
    "noticias": [],
    "conclusion": f"Datos actualizados automáticamente a las {hora} hs del {fecha}."
}

with open("reports/wallstreet.json", "w", encoding="utf-8") as f:
    json.dump(wallstreet, f, ensure_ascii=False, indent=2)
print("reports/wallstreet.json OK")
print(f"Listo: {fecha} {hora}")
