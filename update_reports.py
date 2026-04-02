#!/usr/bin/env python3
"""
Manfredi Investment - Generador automático de reportes diarios
Corre via GitHub Actions todos los días a las 13:00 UTC (10:00 AM Argentina)
Sin IA - usa APIs gratuitas + scraping RSS + análisis por reglas
"""

import json
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
import re

# Zona horaria Argentina
ARG_TZ = timezone(timedelta(hours=-3))
now = datetime.now(ARG_TZ)
fecha = now.strftime("%d/%m/%Y")
hora = now.strftime("%H:%M")

def fetch(url, headers=None):
    try:
        req = urllib.request.Request(url, headers=headers or {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read())
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def fetch_rss(url):
    """Obtiene titulares de un feed RSS"""
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        with urllib.request.urlopen(req, timeout=10) as r:
            content = r.read()
        root = ET.fromstring(content)
        items = []
        for item in root.findall('.//item')[:5]:
            titulo = item.findtext('title', '').strip()
            link = item.findtext('link', '').strip()
            if titulo:
                items.append({"titulo": titulo, "link": link})
        return items
    except Exception as e:
        print(f"Error fetching RSS {url}: {e}")
        return []

# ── NOTICIAS ──────────────────────────────────────────────────────────────────

def get_noticias_argentina():
    """Scraping de titulares financieros argentinos via RSS"""
    noticias = []

    # Ámbito Financiero - Economía
    ambito = fetch_rss("https://www.ambito.com/rss/pages/economia.xml")
    for n in ambito[:3]:
        n["fuente"] = "Ámbito"
        noticias.append(n)

    # El Cronista
    cronista = fetch_rss("https://www.cronista.com/rss/finanzas-y-mercados/")
    for n in cronista[:3]:
        n["fuente"] = "El Cronista"
        noticias.append(n)

    # Infobae Economía
    infobae = fetch_rss("https://www.infobae.com/economia/rss/")
    for n in infobae[:2]:
        n["fuente"] = "Infobae"
        noticias.append(n)

    return noticias[:7]  # máximo 7 noticias

def get_noticias_wallstreet():
    """Scraping de titulares financieros globales via RSS"""
    noticias = []

    # Reuters Business
    reuters = fetch_rss("https://feeds.reuters.com/reuters/businessNews")
    for n in reuters[:3]:
        n["fuente"] = "Reuters"
        noticias.append(n)

    # MarketWatch
    marketwatch = fetch_rss("https://feeds.content.dowjones.io/public/rss/mw_topstories")
    for n in marketwatch[:3]:
        n["fuente"] = "MarketWatch"
        noticias.append(n)

    # Yahoo Finance
    yahoo = fetch_rss("https://finance.yahoo.com/news/rssindex")
    for n in yahoo[:2]:
        n["fuente"] = "Yahoo Finance"
        noticias.append(n)

    return noticias[:7]

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
    url = "https://query1.finance.yahoo.com/v8/finance/chart/%5EMERV?interval=1d&range=5d"
    data = fetch(url)
    if not data:
        return None
    try:
        meta = data["chart"]["result"][0]["meta"]
        precio = meta.get("regularMarketPrice", 0)
        anterior = meta.get("previousClose", 0)
        variacion = round(((precio - anterior) / anterior) * 100, 2) if anterior else 0
        return {
            "precio": round(precio, 2),
            "cierre_anterior": round(anterior, 2),
            "variacion": variacion
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

# ── ANÁLISIS POR REGLAS ───────────────────────────────────────────────────────

def analizar_argentina(dolar, merval, bcra):
    """Genera un párrafo de análisis basado en los datos del día"""
    partes = []

    # Análisis dólar blue
    blue_venta = (dolar.get("blue") or {}).get("venta")
    oficial_venta = (dolar.get("oficial") or {}).get("venta")
    mep_venta = (dolar.get("bolsa") or {}).get("venta")

    if blue_venta and oficial_venta:
        brecha = round(((blue_venta - oficial_venta) / oficial_venta) * 100, 1)
        if brecha > 30:
            partes.append(f"La brecha cambiaria se mantiene elevada en {brecha}%, con el dólar blue a ${blue_venta} frente al oficial de ${oficial_venta}.")
        elif brecha > 15:
            partes.append(f"La brecha cambiaria se ubica en {brecha}%, con el blue a ${blue_venta} y el oficial a ${oficial_venta}.")
        else:
            partes.append(f"La brecha cambiaria se comprimió a {brecha}%, con el blue en ${blue_venta} muy cerca del oficial de ${oficial_venta}.")

    if mep_venta:
        partes.append(f"El dólar MEP cotiza a ${mep_venta}.")

    # Análisis Merval
    if merval:
        var = merval.get("variacion", 0)
        precio = merval.get("precio")
        if var > 3:
            partes.append(f"El Merval tuvo una jornada muy positiva, subiendo {var}% hasta los {precio:,.0f} puntos.")
        elif var > 1:
            partes.append(f"El Merval avanzó {var}% cerrando en {precio:,.0f} puntos.")
        elif var < -3:
            partes.append(f"El Merval sufrió una fuerte caída de {var}%, cerrando en {precio:,.0f} puntos.")
        elif var < -1:
            partes.append(f"El Merval retrocedió {var}%, cerrando en {precio:,.0f} puntos.")
        else:
            partes.append(f"El Merval operó sin grandes cambios, cerrando en {precio:,.0f} puntos ({var:+.2f}%).")

    # Reservas BCRA
    if bcra and bcra.get("reservas"):
        reservas = bcra["reservas"]
        partes.append(f"Las reservas internacionales del BCRA se ubican en USD {reservas:,} millones.")

    return " ".join(partes) if partes else f"Mercado argentino operando con normalidad al {fecha}."

def analizar_wallstreet(indices, commodities):
    """Genera un párrafo de análisis del mercado americano"""
    partes = []

    sp = next((i for i in indices if "S&P" in i["nombre"]), None)
    nasdaq = next((i for i in indices if "Nasdaq" in i["nombre"]), None)
    vix = next((i for i in indices if "VIX" in i["nombre"]), None)
    oro = next((c for c in commodities if "Oro" in c["nombre"]), None)
    petroleo = next((c for c in commodities if "Petróleo" in c["nombre"]), None)
    btc = next((c for c in commodities if "Bitcoin" in c["nombre"]), None)

    # Análisis S&P 500
    if sp and sp.get("variacion") is not None:
        var = sp["variacion"]
        precio = sp["precio"]
        if var > 1.5:
            partes.append(f"Wall Street tuvo una jornada alcista con el S&P 500 ganando {var}% hasta los {precio:,.0f} puntos.")
        elif var > 0.3:
            partes.append(f"El S&P 500 cerró en alza de {var}% en {precio:,.0f} puntos.")
        elif var < -1.5:
            partes.append(f"Wall Street cayó con fuerza, el S&P 500 perdió {abs(var)}% hasta los {precio:,.0f} puntos.")
        elif var < -0.3:
            partes.append(f"El S&P 500 cerró en baja de {abs(var)}% en {precio:,.0f} puntos.")
        else:
            partes.append(f"El S&P 500 operó sin grandes cambios en {precio:,.0f} puntos ({var:+.2f}%).")

    # Nasdaq
    if nasdaq and nasdaq.get("variacion") is not None:
        var = nasdaq["variacion"]
        if abs(var) > 1:
            tendencia = "avanzó" if var > 0 else "retrocedió"
            partes.append(f"El Nasdaq {tendencia} {abs(var)}%.")

    # VIX - índice del miedo
    if vix and vix.get("precio") is not None:
        v = vix["precio"]
        if v > 30:
            partes.append(f"El VIX se ubica en {v}, reflejando alta volatilidad e incertidumbre en el mercado.")
        elif v > 20:
            partes.append(f"El VIX en {v} indica una volatilidad moderada.")
        else:
            partes.append(f"El VIX en {v} sugiere calma en los mercados.")

    # Oro
    if oro and oro.get("precio"):
        var = oro.get("variacion", 0)
        partes.append(f"El oro cotiza a USD {oro['precio']:,.0f} la onza ({var:+.2f}%).")

    # Petróleo
    if petroleo and petroleo.get("precio"):
        var = petroleo.get("variacion", 0)
        partes.append(f"El petróleo WTI se ubica en USD {petroleo['precio']:.1f} ({var:+.2f}%).")

    # Bitcoin
    if btc and btc.get("precio"):
        var = btc.get("variacion", 0)
        partes.append(f"Bitcoin cotiza a USD {btc['precio']:,.0f} ({var:+.2f}%).")

    return " ".join(partes) if partes else f"Mercados globales operando con normalidad al {fecha}."

# ── GENERAR REPORTES ──────────────────────────────────────────────────────────

print("Obteniendo noticias Argentina...")
noticias_arg = get_noticias_argentina()
print(f"  → {len(noticias_arg)} titulares obtenidos")

print("Generando reporte Argentina...")
dolar = get_dolar()
merval = get_merval()
bcra = get_bcra()

analisis_arg = analizar_argentina(dolar, merval, bcra)

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
    "noticias": noticias_arg,
    "analisis": analisis_arg,
    # Compatibilidad con versión anterior
    "resumen": analisis_arg
}

with open("argentina.json", "w", encoding="utf-8") as f:
    json.dump(argentina, f, ensure_ascii=False, indent=2)
print("argentina.json generado OK")

print("Obteniendo noticias Wall Street...")
noticias_ws = get_noticias_wallstreet()
print(f"  → {len(noticias_ws)} titulares obtenidos")

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

analisis_ws = analizar_wallstreet(indices, commodities)

wallstreet = {
    "fecha": fecha,
    "hora": hora,
    "indices": indices,
    "commodities": commodities,
    "noticias": noticias_ws,
    "analisis": analisis_ws,
    # Compatibilidad con versión anterior
    "resumen": analisis_ws
}

with open("wallstreet.json", "w", encoding="utf-8") as f:
    json.dump(wallstreet, f, ensure_ascii=False, indent=2)
print("wallstreet.json generado OK")

print(f"\n✅ Reportes generados exitosamente a las {hora} del {fecha}")
print(f"   Argentina: {len(noticias_arg)} noticias | Análisis: {len(analisis_arg)} chars")
print(f"   Wall Street: {len(noticias_ws)} noticias | Análisis: {len(analisis_ws)} chars")
