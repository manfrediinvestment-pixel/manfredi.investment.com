import json
import urllib.request
import urllib.error
import os
import sys
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
        print(f"Error fetching {url}: {e}")
        return None

def get_yahoo(ticker, nombre):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=2d"
    data = fetch(url)
    if not data:
        return {"nombre": nombre, "ticker": ticker, "precio": None, "variacion": None}
    try:
        meta = data["chart"]["result"][0]["meta"]
        precio = meta.get("regularMarketPrice", 0)
        anterior = meta.get("previousClose", 0)
        variacion = round(((precio - anterior) / anterior) * 100, 2) if anterior else 0
        return {"nombre": nombre, "ticker": ticker,
                "precio": round(precio, 2), "variacion": variacion}
    except:
        return {"nombre": nombre, "ticker": ticker, "precio": None, "variacion": None}

# ── ARGENTINA ──────────────────────────────────────────────────────
print("Generando argentina.json...")
dolar_data = fetch("https://dolarapi.com/v1/dolares") or []
dolar = {}
for d in dolar_data:
    casa = d.get("casa", "").lower()
    dolar[casa] = {"compra": d.get("compra"), "venta": d.get("venta"), "nombre": d.get("nombre")}

merval = get_yahoo("%5EMERV", "Merval")

argentina = {
    "fecha": fecha, "hora": hora,
    "dolar": {
        "oficial": dolar.get("oficial"),
        "blue": dolar.get("blue"),
        "mep": dolar.get("bolsa"),
        "ccl": dolar.get("contadoconliqui"),
        "mayorista": dolar.get("mayorista")
    },
    "merval": merval,
    "resumen": f"Mercado argentino al {fecha}. Dólar blue: ${dolar.get('blue', {}).get('venta', 'N/D')}. MEP: ${dolar.get('bolsa', {}).get('venta', 'N/D')}. Merval: {merval.get('precio', 'N/D')} pts."
}

with open("argentina.json", "w", encoding="utf-8") as f:
    json.dump(argentina, f, ensure_ascii=False, indent=2)
print("argentina.json OK")

# ── WALL STREET ────────────────────────────────────────────────────
print("Generando wallstreet.json...")
indices = [
    get_yahoo("%5EGSPC", "S&P 500"),
    get_yahoo("%5EDJI", "Dow Jones"),
    get_yahoo("%5EIXIC", "Nasdaq"),
    get_yahoo("%5EVIX", "VIX"),
]
commodities = [
    get_yahoo("GC%3DF", "Oro"),
    get_yahoo("CL%3DF", "Petróleo WTI"),
    get_yahoo("BTC-USD", "Bitcoin"),
]

sp = indices[0]
wallstreet = {
    "fecha": fecha, "hora": hora,
    "indices": indices,
    "commodities": commodities,
    "resumen": f"Wall Street al {fecha}. S&P 500: {sp.get('precio','N/D')} ({'+' if (sp.get('variacion') or 0)>=0 else ''}{sp.get('variacion','N/D')}%). Oro: {commodities[0].get('precio','N/D')} USD."
}

with open("wallstreet.json", "w", encoding="utf-8") as f:
    json.dump(wallstreet, f, ensure_ascii=False, indent=2)
print("wallstreet.json OK")
print(f"Reportes generados: {fecha} {hora}")
