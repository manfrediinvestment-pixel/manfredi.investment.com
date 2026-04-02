#!/usr/bin/env python3
"""
Manfredi Investment - Generador automático de reportes diarios
Corre via GitHub Actions todos los días a las 13:00 UTC (10:00 AM Argentina)
No usa IA - solo APIs gratuitas de datos financieros
"""

import json
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta

# Zona horaria Argentina
ARG_TZ = timezone(timedelta(hours=-3))
now = datetime.now(ARG_TZ)
fecha = now.strftime("%d/%m/%Y")
hora = now.strftime("%H:%M")

def fetch(url, headers=None):
    try:
        req = urllib.request.Request(url, headers=headers or {
            'User-Agent': 'Mozilla/5.0'
        })
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read())
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

# ── ARGENTINA ─────────────────────────────────────────────────────────────────

def get_dolar():
    data = fetch("https://dolarapi.com/v1/dolares")
    if not data:
        return {}
    result = {}
    for d in data:
        casa = d.get("casa", "").lower()
        result[casa] = {
            "compra": d.get("compra"),
            "venta": d.get("venta"),
            "nombre": d.get("nombre")
        }
    return result

def get_merval():
    # Yahoo Finance para el Merval (^MERV)
    url = "https://query1.finance.yahoo.com/v8/finance/chart/%5EMERV?interval=1d&range=5d"
    data = fetch(url)
    if not data:
        return None
    try:
        meta = data["chart"]["result"][0]["meta"]
        return {
            "precio": round(meta.get("regularMarketPrice", 0), 2),
            "cierre_anterior": round(meta.get("previousClose", 0), 2),
            "variacion": round(
                ((meta.get("regularMarketPrice", 0) - meta.get("previousClose", 0)) /
                 meta.get("previousClose", 1)) * 100, 2
            )
        }
    except:
        return None

def get_bcra():
    data = fetch("https://api.bcra.gob.ar/estadisticas/v3.0/monetarias/reservasinternacionales?limit=5")
    if not data:
        return None
    try:
        ultimo = data["results"][0]
        return {
            "reservas": ultimo.get("value"),
            "fecha": ultimo.get("date")
        }
    except:
        return None

# ── WALL STREET ───────────────────────────────────────────────────────────────

def get_indice(ticker, nombre):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=2d"
    data = fetch(url)
    if not data:
        return {"nombre": nombre, "ticker": ticker, "precio": None, "variacion": None}
    try:
        meta = data["chart"]["result"][0]["meta"]
        precio = meta.get("regularMarketPrice", 0)
        anterior = meta.get("previousClose", 0)
        variacion = round(((precio - anterior) / anterior) * 100, 2) if anterior else 0
        return {
            "nombre": nombre,
            "ticker": ticker,
            "precio": round(precio, 2),
            "variacion": variacion
        }
    except:
        return {"nombre": nombre, "ticker": ticker, "precio": None, "variacion": None}

def get_commodity(ticker, nombre):
    return get_indice(ticker, nombre)

# ── GENERAR REPORTES ──────────────────────────────────────────────────────────

print("Generando reporte Argentina...")
dolar = get_dolar()
merval = get_merval()
bcra = get_bcra()

argentina = {
    "fecha": fecha,
    "hora": hora,
    "dolar": {
        "oficial": dolar.get("oficial"),
        "blue": dolar.get("blue"),
        "mep": dolar.get("bolsa"),
        "ccl": dolar.get("contadoconliqui"),
        "cripto": dolar.get("cripto"),
        "mayorista": dolar.get("mayorista")
    },
    "merval": merval,
    "bcra": bcra,
    "resumen": f"Tipo de cambio actualizado al {fecha}. Dólar blue: ${dolar.get('blue', {}).get('venta', 'N/D')}. Dólar MEP: ${dolar.get('bolsa', {}).get('venta', 'N/D')}."
}

with open("argentina.json", "w", encoding="utf-8") as f:
    json.dump(argentina, f, ensure_ascii=False, indent=2)
print("argentina.json generado OK")

print("Generando reporte Wall Street...")
indices = [
    get_indice("%5EGSPC", "S&P 500"),
    get_indice("%5EDJI", "Dow Jones"),
    get_indice("%5EIXIC", "Nasdaq"),
    get_indice("%5EVIX", "VIX"),
]

commodities = [
    get_commodity("GC%3DF", "Oro"),
    get_commodity("CL%3DF", "Petróleo WTI"),
    get_commodity("BTC-USD", "Bitcoin"),
]

wallstreet = {
    "fecha": fecha,
    "hora": hora,
    "indices": indices,
    "commodities": commodities,
    "resumen": f"Mercados al {fecha}. S&P 500: {indices[0].get('precio', 'N/D')} ({'+' if (indices[0].get('variacion') or 0) >= 0 else ''}{indices[0].get('variacion', 'N/D')}%)."
}

with open("wallstreet.json", "w", encoding="utf-8") as f:
    json.dump(wallstreet, f, ensure_ascii=False, indent=2)
print("wallstreet.json generado OK")

print(f"Reportes generados exitosamente a las {hora} del {fecha}")
