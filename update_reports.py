#!/usr/bin/env python3
"""
Manfredi Investment - Generador automático de reportes diarios
Corre via GitHub Actions todos los días a las 13:00 UTC (10:00 AM Argentina)
Sin IA - APIs gratuitas + scraping de noticias + análisis por reglas
"""

import json
import urllib.request
import urllib.error
import re
from datetime import datetime, timezone, timedelta
from html.parser import HTMLParser

# ── ZONA HORARIA ──────────────────────────────────────────────────────────────
ARG_TZ = timezone(timedelta(hours=-3))
now    = datetime.now(ARG_TZ)
fecha  = now.strftime("%d/%m/%Y")
hora   = now.strftime("%H:%M")

# ── HTTP HELPERS ──────────────────────────────────────────────────────────────
def fetch(url, headers=None):
    try:
        req = urllib.request.Request(url, headers=headers or {'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=12) as r:
            return json.loads(r.read())
    except Exception as e:
        print(f"  [WARN] fetch {url}: {e}")
        return None

def fetch_html(url):
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml',
            'Accept-Language': 'es-AR,es;q=0.9'
        })
        with urllib.request.urlopen(req, timeout=12) as r:
            return r.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"  [WARN] fetch_html {url}: {e}")
        return ""

def clean_title(t):
    t = re.sub(r'\s+', ' ', t).strip()
    t = re.sub(r'<[^>]+>', '', t)
    return t if len(t) > 20 else None

# ── SCRAPING: NOTICIAS ARGENTINA ──────────────────────────────────────────────
def get_noticias_argentina():
    noticias = []

    # Ámbito Financiero
    html = fetch_html("https://www.ambito.com/economia")
    if html:
        matches = re.findall(r'<h[23][^>]*>(.*?)</h[23]>', html, re.DOTALL)
        for m in matches:
            c = clean_title(m)
            if c:
                noticias.append({"titulo": c, "fuente": "Ámbito"})
            if len(noticias) >= 4:
                break

    # El Cronista
    if len(noticias) < 5:
        html2 = fetch_html("https://www.cronista.com/economia-politica/")
        if html2:
            matches = re.findall(r'<h[23][^>]*>(.*?)</h[23]>', html2, re.DOTALL)
            for m in matches[:4]:
                c = clean_title(m)
                if c:
                    noticias.append({"titulo": c, "fuente": "El Cronista"})

    # Infobae Economía
    if len(noticias) < 5:
        html3 = fetch_html("https://www.infobae.com/economia/")
        if html3:
            matches = re.findall(r'<h[23][^>]*>(.*?)</h[23]>', html3, re.DOTALL)
            for m in matches[:3]:
                c = clean_title(m)
                if c:
                    noticias.append({"titulo": c, "fuente": "Infobae"})

    seen, result = set(), []
    for n in noticias:
        if n["titulo"] not in seen:
            seen.add(n["titulo"])
            result.append(n)
        if len(result) >= 6:
            break
    return result

# ── SCRAPING: NOTICIAS WALL STREET ───────────────────────────────────────────
def get_noticias_wallstreet():
    noticias = []

    # Yahoo Finance Markets
    html = fetch_html("https://finance.yahoo.com/topic/stock-market-news/")
    if html:
        matches = re.findall(r'<h[23][^>]*>(.*?)</h[23]>', html, re.DOTALL)
        for m in matches[:5]:
            c = clean_title(m)
            if c and not any(x in c.lower() for x in ['cookie', 'privacy', 'javascript', 'yahoo']):
                noticias.append({"titulo": c, "fuente": "Yahoo Finance"})

    # Reuters Markets
    if len(noticias) < 4:
        html2 = fetch_html("https://www.reuters.com/markets/")
        if html2:
            matches = re.findall(r'<h[23][^>]*>(.*?)</h[23]>', html2, re.DOTALL)
            for m in matches[:4]:
                c = clean_title(m)
                if c and not any(x in c.lower() for x in ['cookie', 'reuters', 'login']):
                    noticias.append({"titulo": c, "fuente": "Reuters"})

    seen, result = set(), []
    for n in noticias:
        if n["titulo"] not in seen:
            seen.add(n["titulo"])
            result.append(n)
        if len(result) >= 6:
            break
    return result

# ── DATOS FINANCIEROS: ARGENTINA ─────────────────────────────────────────────
def get_dolar():
    data = fetch("https://dolarapi.com/v1/dolares")
    if not data:
        return {}
    result = {}
    for d in data:
        casa = d.get("casa", "").lower()
        result[casa] = {
            "compra": d.get("compra"),
            "venta":  d.get("venta"),
            "nombre": d.get("nombre")
        }
    return result

def get_merval():
    url  = "https://query1.finance.yahoo.com/v8/finance/chart/%5EMERV?interval=1d&range=5d"
    data = fetch(url)
    if not data:
        return None
    try:
        meta     = data["chart"]["result"][0]["meta"]
        precio   = meta.get("regularMarketPrice", 0)
        anterior = meta.get("previousClose", 0)
        return {
            "precio":          round(precio, 2),
            "cierre_anterior": round(anterior, 2),
            "variacion":       round(((precio - anterior) / anterior) * 100, 2) if anterior else 0
        }
    except:
        return None

def get_bcra():
    data = fetch("https://api.bcra.gob.ar/estadisticas/v3.0/monetarias/reservasinternacionales?limit=5")
    if not data:
        return None
    try:
        ultimo = data["results"][0]
        return {"reservas": ultimo.get("value"), "fecha": ultimo.get("date")}
    except:
        return None

# ── DATOS FINANCIEROS: WALL STREET ───────────────────────────────────────────
def get_yahoo(ticker, nombre):
    url  = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=2d"
    data = fetch(url)
    base = {"nombre": nombre, "ticker": ticker, "precio": None, "variacion": None}
    if not data:
        return base
    try:
        meta     = data["chart"]["result"][0]["meta"]
        precio   = meta.get("regularMarketPrice", 0)
        anterior = meta.get("previousClose", 0)
        variacion = round(((precio - anterior) / anterior) * 100, 2) if anterior else 0
        return {"nombre": nombre, "ticker": ticker, "precio": round(precio, 2), "variacion": variacion}
    except:
        return base

# ── ANÁLISIS POR REGLAS: ARGENTINA ───────────────────────────────────────────
def analisis_argentina(dolar, merval, bcra):
    partes = []

    blue = dolar.get("blue", {})
    mep  = dolar.get("bolsa", {})
    ccl  = dolar.get("contadoconliqui", {})

    if blue.get("venta"):
        partes.append(f"El dólar blue cotiza a ${blue['venta']} (compra ${blue.get('compra', 'N/D')}).")

    if mep.get("venta") and blue.get("venta"):
        brecha = round((blue["venta"] - mep["venta"]) / mep["venta"] * 100, 1)
        if brecha > 5:
            partes.append(f"La brecha entre el blue y el MEP se amplía al {brecha}%, señal de presión cambiaria.")
        else:
            partes.append(f"La brecha entre el blue y el MEP es del {brecha}%, relativamente estable.")

    if ccl.get("venta"):
        partes.append(f"El dólar CCL opera a ${ccl['venta']}.")

    if merval:
        v = merval.get("variacion", 0)
        p = merval.get("precio", 0)
        if v is not None:
            if abs(v) >= 3:
                mov = "fuerte suba" if v > 0 else "fuerte caída"
                partes.append(f"El Merval registra una {mov} del {v:+.1f}%, en torno a {p:,.0f} puntos.")
            elif abs(v) >= 1:
                mov = "sube" if v > 0 else "baja"
                partes.append(f"El Merval {mov} un {v:+.1f}%, operando cerca de {p:,.0f} puntos.")
            else:
                partes.append(f"El Merval opera sin grandes cambios, rondando los {p:,.0f} puntos.")

    if bcra and bcra.get("reservas"):
        partes.append(f"Las reservas internacionales del BCRA se ubican en USD {bcra['reservas']:,} millones al {bcra.get('fecha', 'N/D')}.")

    return " ".join(partes) if partes else f"Mercado argentino al {fecha}."

# ── ANÁLISIS POR REGLAS: WALL STREET ─────────────────────────────────────────
def analisis_wallstreet(indices, commodities):
    partes = []
    idx = {i["nombre"]: i for i in indices}

    sp = idx.get("S&P 500", {})
    nq = idx.get("Nasdaq", {})
    dj = idx.get("Dow Jones", {})
    vx = idx.get("VIX", {})
    ru = idx.get("Russell 2000", {})

    if sp.get("variacion") is not None:
        v = sp["variacion"]
        p = sp.get("precio", "N/D")
        if abs(v) >= 2:
            mov = "fuerte avance" if v > 0 else "fuerte retroceso"
            partes.append(f"El S&P 500 registra un {mov} del {v:+.2f}%, en {p:,.0f} puntos.")
        else:
            mov = "avanza" if v >= 0 else "retrocede"
            partes.append(f"El S&P 500 {mov} un {v:+.2f}%, cotizando en {p:,.0f} puntos.")

    if nq.get("variacion") is not None:
        v = nq["variacion"]
        mov = "sube" if v >= 0 else "baja"
        partes.append(f"El Nasdaq {mov} un {v:+.2f}%.")

    if dj.get("variacion") is not None:
        v = dj["variacion"]
        mov = "avanza" if v >= 0 else "cede"
        partes.append(f"El Dow Jones {mov} un {v:+.2f}%.")

    if ru.get("variacion") is not None:
        v = ru["variacion"]
        mov = "sube" if v >= 0 else "baja"
        partes.append(f"El Russell 2000 (small caps) {mov} un {v:+.2f}%.")

    if vx.get("precio") is not None:
        p = vx["precio"]
        if p >= 30:
            partes.append(f"El VIX en {p:.1f} indica alta volatilidad y nerviosismo en el mercado.")
        elif p >= 20:
            partes.append(f"El VIX en {p:.1f} refleja cierta cautela entre los inversores.")
        else:
            partes.append(f"El VIX en {p:.1f} sugiere calma en los mercados.")

    com = {c["nombre"]: c for c in commodities}
    oro = com.get("Oro", {})
    btc = com.get("Bitcoin", {})
    wti = com.get("Petróleo WTI", {})
    plata = com.get("Plata", {})

    if oro.get("precio"):
        partes.append(f"El oro cotiza a USD {oro['precio']:,.0f} por onza.")
    if plata.get("precio"):
        partes.append(f"La plata opera en USD {plata['precio']:.2f}.")
    if wti.get("precio"):
        partes.append(f"El petróleo WTI se ubica en USD {wti['precio']:.1f} el barril.")
    if btc.get("precio"):
        v = btc.get("variacion", 0) or 0
        mov = "sube" if v >= 0 else "baja"
        partes.append(f"Bitcoin {mov} un {v:+.1f}%, operando cerca de USD {btc['precio']:,.0f}.")

    return " ".join(partes) if partes else f"Mercados globales al {fecha}."

# ── GENERAR REPORTE ARGENTINA ─────────────────────────────────────────────────
print("Generando reporte Argentina...")
dolar        = get_dolar()
merval       = get_merval()
bcra         = get_bcra()
noticias_ar  = get_noticias_argentina()

argentina = {
    "fecha": fecha,
    "hora":  hora,
    "dolar": {
        "oficial":   dolar.get("oficial"),
        "blue":      dolar.get("blue"),
        "mep":       dolar.get("bolsa"),
        "ccl":       dolar.get("contadoconliqui"),
        "cripto":    dolar.get("cripto"),
        "mayorista": dolar.get("mayorista"),
        "tarjeta":   dolar.get("tarjeta")
    },
    "merval":   merval,
    "bcra":     bcra,
    "analisis": analisis_argentina(dolar, merval, bcra),
    "noticias": noticias_ar
}

with open("argentina.json", "w", encoding="utf-8") as f:
    json.dump(argentina, f, ensure_ascii=False, indent=2)
print("  argentina.json OK")

# ── GENERAR REPORTE WALL STREET ───────────────────────────────────────────────
print("Generando reporte Wall Street...")
indices = [
    get_yahoo("%5EGSPC", "S&P 500"),
    get_yahoo("%5EDJI",  "Dow Jones"),
    get_yahoo("%5EIXIC", "Nasdaq"),
    get_yahoo("%5EVIX",  "VIX"),
    get_yahoo("%5ERUT",  "Russell 2000"),
]

commodities = [
    get_yahoo("GC%3DF",  "Oro"),
    get_yahoo("CL%3DF",  "Petróleo WTI"),
    get_yahoo("SI%3DF",  "Plata"),
    get_yahoo("BTC-USD", "Bitcoin"),
    get_yahoo("ETH-USD", "Ethereum"),
]

noticias_ws = get_noticias_wallstreet()

wallstreet = {
    "fecha":       fecha,
    "hora":        hora,
    "indices":     indices,
    "commodities": commodities,
    "analisis":    analisis_wallstreet(indices, commodities),
    "noticias":    noticias_ws
}

with open("wallstreet.json", "w", encoding="utf-8") as f:
    json.dump(wallstreet, f, ensure_ascii=False, indent=2)
print("  wallstreet.json OK")

print(f"\nReportes generados a las {hora} del {fecha}")
