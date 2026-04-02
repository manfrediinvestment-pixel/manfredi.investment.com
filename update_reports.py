#!/usr/bin/env python3
"""
Manfredi Investment - Generador automático de reportes diarios
Corre via GitHub Actions todos los días a las 13:00 UTC (10:00 AM Argentina)
Sin IA - APIs gratuitas + scraping de titulares + análisis por reglas
"""

import json
import urllib.request
import urllib.error
import html
import re
from datetime import datetime, timezone, timedelta

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
        with urllib.request.urlopen(req, timeout=12) as r:
            return json.loads(r.read())
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def fetch_text(url, headers=None):
    try:
        req = urllib.request.Request(url, headers=headers or {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        with urllib.request.urlopen(req, timeout=12) as r:
            return r.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Error fetching text {url}: {e}")
        return None

# ─────────────────────────────────────────────────────────────────────────────
# SCRAPING DE NOTICIAS
# ─────────────────────────────────────────────────────────────────────────────

def scrape_ambito():
    """Scrapea titulares del RSS de Ámbito Financiero"""
    noticias = []
    try:
        content = fetch_text("https://www.ambito.com/rss/pages/economia.xml")
        if not content:
            content = fetch_text("https://www.ambito.com/rss/pages/home.xml")
        if content:
            items = re.findall(r'<item>(.*?)</item>', content, re.DOTALL)
            for item in items[:8]:
                title = re.search(r'<title><!\[CDATA\[(.*?)\]\]></title>', item)
                if not title:
                    title = re.search(r'<title>(.*?)</title>', item)
                link = re.search(r'<link>(.*?)</link>', item)
                if title:
                    noticias.append({
                        "titulo": html.unescape(title.group(1).strip()),
                        "fuente": "Ámbito",
                        "url": link.group(1).strip() if link else ""
                    })
    except Exception as e:
        print(f"Error scraping Ámbito: {e}")
    return noticias

def scrape_cronista():
    """Scrapea titulares del RSS de El Cronista"""
    noticias = []
    try:
        content = fetch_text("https://www.cronista.com/files/feed_articles.xml")
        if content:
            items = re.findall(r'<item>(.*?)</item>', content, re.DOTALL)
            for item in items[:6]:
                title = re.search(r'<title><!\[CDATA\[(.*?)\]\]></title>', item)
                if not title:
                    title = re.search(r'<title>(.*?)</title>', item)
                link = re.search(r'<link>(.*?)</link>', item)
                if title:
                    noticias.append({
                        "titulo": html.unescape(title.group(1).strip()),
                        "fuente": "El Cronista",
                        "url": link.group(1).strip() if link else ""
                    })
    except Exception as e:
        print(f"Error scraping El Cronista: {e}")
    return noticias

def scrape_noticias_internacionales():
    """Scrapea noticias financieras globales via RSS de Reuters y MarketWatch"""
    noticias = []
    fuentes = [
        ("https://feeds.reuters.com/reuters/businessNews", "Reuters"),
        ("https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best", "Reuters Finance"),
    ]
    for url, fuente in fuentes:
        try:
            content = fetch_text(url)
            if content:
                items = re.findall(r'<item>(.*?)</item>', content, re.DOTALL)
                for item in items[:5]:
                    title = re.search(r'<title><!\[CDATA\[(.*?)\]\]></title>', item)
                    if not title:
                        title = re.search(r'<title>(.*?)</title>', item)
                    link = re.search(r'<link>(.*?)</link>', item)
                    if title:
                        noticias.append({
                            "titulo": html.unescape(title.group(1).strip()),
                            "fuente": fuente,
                            "url": link.group(1).strip() if link else ""
                        })
                if noticias:
                    break
        except Exception as e:
            print(f"Error scraping {fuente}: {e}")
    return noticias[:6]

# ─────────────────────────────────────────────────────────────────────────────
# DATOS ARGENTINA
# ─────────────────────────────────────────────────────────────────────────────

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

# ─────────────────────────────────────────────────────────────────────────────
# DATOS WALL STREET
# ─────────────────────────────────────────────────────────────────────────────

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

# ─────────────────────────────────────────────────────────────────────────────
# ANÁLISIS POR REGLAS
# ─────────────────────────────────────────────────────────────────────────────

def analizar_argentina(dolar, merval, bcra):
    """Genera análisis textual automático del mercado argentino"""
    puntos = []

    # Análisis dólar blue
    blue = dolar.get("blue", {})
    oficial = dolar.get("oficial", {})
    if blue.get("venta") and oficial.get("venta"):
        brecha = round(((blue["venta"] - oficial["venta"]) / oficial["venta"]) * 100, 1)
        puntos.append(f"La brecha cambiaria entre el dólar blue (${blue['venta']}) y el oficial (${oficial['venta']}) se ubica en {brecha}%.")

    # Análisis Merval
    if merval:
        v = merval.get("variacion", 0)
        p = merval.get("precio", 0)
        if v > 2:
            puntos.append(f"El Merval muestra una suba destacada de {v}%, cerrando en {p:,.0f} puntos, reflejando optimismo en el mercado local.")
        elif v < -2:
            puntos.append(f"El Merval registra una caída de {abs(v)}%, cerrando en {p:,.0f} puntos, en una rueda de presión vendedora.")
        elif v > 0:
            puntos.append(f"El Merval avanza moderadamente {v}%, cerrando en {p:,.0f} puntos.")
        else:
            puntos.append(f"El Merval cede {abs(v)}%, cerrando en {p:,.0f} puntos.")

    # Análisis MEP vs CCL
    mep = dolar.get("bolsa", {})
    ccl = dolar.get("contadoconliqui", {})
    if mep.get("venta") and ccl.get("venta"):
        diff = round(ccl["venta"] - mep["venta"], 2)
        puntos.append(f"El dólar MEP cotiza a ${mep['venta']} y el CCL a ${ccl['venta']}, con una diferencia de ${diff} entre ambos.")

    # Reservas BCRA
    if bcra and bcra.get("reservas"):
        puntos.append(f"Las reservas internacionales del BCRA se ubican en USD {bcra['reservas']:,} millones (dato al {bcra['fecha']}).")

    if not puntos:
        return f"Mercado argentino al {fecha}. Dólar blue: ${blue.get('venta', 'N/D')}."

    return " ".join(puntos)

def analizar_wallstreet(indices, commodities):
    """Genera análisis textual automático del mercado global"""
    puntos = []

    sp = next((i for i in indices if "S&P" in i["nombre"]), None)
    nasdaq = next((i for i in indices if "Nasdaq" in i["nombre"]), None)
    dow = next((i for i in indices if "Dow" in i["nombre"]), None)
    vix = next((i for i in indices if "VIX" in i["nombre"]), None)

    # Tono general del mercado
    variaciones = [i["variacion"] for i in indices if i.get("variacion") is not None and "VIX" not in i["nombre"]]
    if variaciones:
        promedio = sum(variaciones) / len(variaciones)
        if promedio > 1:
            puntos.append(f"Wall Street cierra una rueda alcista con ganancias generalizadas.")
        elif promedio < -1:
            puntos.append(f"Wall Street termina en rojo con caídas en los principales índices.")
        else:
            puntos.append(f"Wall Street opera con movimientos mixtos y sin tendencia definida.")

    if sp and sp.get("precio"):
        signo = "+" if (sp["variacion"] or 0) >= 0 else ""
        puntos.append(f"El S&P 500 cierra en {sp['precio']:,} puntos ({signo}{sp['variacion']}%).")

    if nasdaq and nasdaq.get("precio"):
        signo = "+" if (nasdaq["variacion"] or 0) >= 0 else ""
        puntos.append(f"El Nasdaq finaliza en {nasdaq['precio']:,} puntos ({signo}{nasdaq['variacion']}%).")

    if dow and dow.get("precio"):
        signo = "+" if (dow["variacion"] or 0) >= 0 else ""
        puntos.append(f"El Dow Jones registra {dow['precio']:,} puntos ({signo}{dow['variacion']}%).")

    # VIX
    if vix and vix.get("precio"):
        if vix["precio"] > 25:
            puntos.append(f"El VIX en {vix['precio']} señala alta volatilidad e incertidumbre en el mercado.")
        elif vix["precio"] < 15:
            puntos.append(f"El VIX en {vix['precio']} indica baja volatilidad y calma en los mercados.")
        else:
            puntos.append(f"El VIX se ubica en {vix['precio']}, reflejando volatilidad moderada.")

    # Commodities
    oro = next((c for c in commodities if "Oro" in c["nombre"]), None)
    petroleo = next((c for c in commodities if "Petróleo" in c["nombre"]), None)
    btc = next((c for c in commodities if "Bitcoin" in c["nombre"]), None)

    if oro and oro.get("precio"):
        signo = "+" if (oro["variacion"] or 0) >= 0 else ""
        puntos.append(f"El oro cotiza a USD {oro['precio']:,} ({signo}{oro['variacion']}%).")

    if petroleo and petroleo.get("precio"):
        signo = "+" if (petroleo["variacion"] or 0) >= 0 else ""
        puntos.append(f"El petróleo WTI opera a USD {petroleo['precio']} ({signo}{petroleo['variacion']}%).")

    if btc and btc.get("precio"):
        signo = "+" if (btc["variacion"] or 0) >= 0 else ""
        puntos.append(f"Bitcoin cotiza en USD {btc['precio']:,} ({signo}{btc['variacion']}%).")

    return " ".join(puntos)

# ─────────────────────────────────────────────────────────────────────────────
# GENERAR REPORTES
# ─────────────────────────────────────────────────────────────────────────────

print("Scrapeando noticias Argentina...")
noticias_arg = scrape_ambito() + scrape_cronista()
noticias_arg = noticias_arg[:8]  # máximo 8 titulares

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
    "analisis": analizar_argentina(dolar, merval, bcra),
    "noticias": noticias_arg
}

with open("argentina.json", "w", encoding="utf-8") as f:
    json.dump(argentina, f, ensure_ascii=False, indent=2)
print("argentina.json generado OK")

print("Scrapeando noticias internacionales...")
noticias_int = scrape_noticias_internacionales()

print("Generando reporte Wall Street...")
indices = [
    get_indice("%5EGSPC", "S&P 500"),
    get_indice("%5EDJI", "Dow Jones"),
    get_indice("%5EIXIC", "Nasdaq"),
    get_indice("%5EVIX", "VIX"),
]

commodities = [
    get_indice("GC%3DF", "Oro"),
    get_indice("CL%3DF", "Petróleo WTI"),
    get_indice("BTC-USD", "Bitcoin"),
]

wallstreet = {
    "fecha": fecha,
    "hora": hora,
    "indices": indices,
    "commodities": commodities,
    "analisis": analizar_wallstreet(indices, commodities),
    "noticias": noticias_int
}

with open("wallstreet.json", "w", encoding="utf-8") as f:
    json.dump(wallstreet, f, ensure_ascii=False, indent=2)
print("wallstreet.json generado OK")

print(f"✅ Reportes generados exitosamente a las {hora} del {fecha}")
