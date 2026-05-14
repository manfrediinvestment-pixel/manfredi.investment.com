import json, urllib.request, urllib.error, os, xml.etree.ElementTree as ET
import re
from datetime import datetime, timezone, timedelta

ARG_TZ = timezone(timedelta(hours=-3))
now = datetime.now(ARG_TZ)
fecha = now.strftime("%d/%m/%Y")
hora = now.strftime("%H:%M")

def fetch(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=12) as r:
            return json.loads(r.read())
    except Exception as e:
        print(f"Error fetch JSON: {e}")
        return None

def fetch_text(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=12) as r:
            return r.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"Error fetch text: {e}")
        return None

def fetch_rss(url, max_items=4):
    try:
        text = fetch_text(url)
        if not text:
            return []
        root = ET.fromstring(text)
        items = root.findall(".//item")
        results = []
        for item in items[:max_items]:
            title_el = item.find("title")
            link_el = item.find("link")
            desc_el = item.find("description")
            title = title_el.text.strip() if title_el is not None and title_el.text else ""
            link = link_el.text.strip() if link_el is not None and link_el.text else ""
            desc = desc_el.text.strip() if desc_el is not None and desc_el.text else ""
            desc = re.sub(r"<[^>]+>", "", desc)[:250]
            if title:
                results.append({"titulo": title, "link": link, "resumen": desc})
        return results
    except Exception as e:
        print(f"Error RSS {url}: {e}")
        return []

def yahoo(ticker, nombre):
    for host in ["query1", "query2"]:
        url = f"https://{host}.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=5d"
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "Accept": "application/json",
            })
            with urllib.request.urlopen(req, timeout=12) as r:
                data = json.loads(r.read())
            meta = data["chart"]["result"][0]["meta"]
            precio = meta.get("regularMarketPrice") or meta.get("regularMarketPreviousClose", 0)
            pct = meta.get("regularMarketChangePercent")
            if pct is not None and abs(pct) > 0.001:
                sign = "+" if pct >= 0 else ""
                var_str = f"{sign}{round(pct, 2)}%"
            else:
                try:
                    closes = data["chart"]["result"][0]["indicators"]["quote"][0]["close"]
                    closes = [c for c in closes if c is not None]
                    if len(closes) >= 2:
                        var = round(((closes[-1] - closes[-2]) / closes[-2]) * 100, 2)
                        sign = "+" if var >= 0 else ""
                        var_str = f"{sign}{var}%"
                    else:
                        anterior = meta.get("chartPreviousClose") or meta.get("previousClose", 0)
                        if anterior and anterior != precio:
                            var = round(((precio - anterior) / anterior) * 100, 2)
                            sign = "+" if var >= 0 else ""
                            var_str = f"{sign}{var}%"
                        else:
                            var_str = "N/D"
                except Exception:
                    var_str = "N/D"
            return {"valor": round(precio, 2), "variacion": var_str}
        except Exception as e:
            print(f"Error parseando {ticker}: {e}")
            continue
    return {"valor": None, "variacion": "N/D"}

# NOTICIAS ARGENTINA
print("Obteniendo noticias Argentina...")
noticias_arg = []
noticias_arg.extend(fetch_rss("https://www.ambito.com/rss/economia.xml", 3))
noticias_arg.extend(fetch_rss("https://www.infobae.com/feeds/rss/economia.xml", 3))
noticias_arg.extend(fetch_rss("https://cronista.com/files/rss/economia.xml", 2))
if not noticias_arg:
    noticias_arg = [{"titulo": "Mercado argentino en operacion", "link": "", "resumen": "Consulte Ambito.com e Infobae.com para noticias del dia."}]
noticias_arg = noticias_arg[:5]

# NOTICIAS WALL STREET
print("Obteniendo noticias Wall Street...")
noticias_ws = []
noticias_ws.extend(fetch_rss("https://feeds.reuters.com/reuters/businessNews", 3))
noticias_ws.extend(fetch_rss("https://feeds.finance.yahoo.com/rss/2.0/headline?s=%5EGSPC&region=US&lang=en-US", 3))
if not noticias_ws:
    noticias_ws = [{"titulo": "Wall Street en operacion", "link": "", "resumen": "Consulte Reuters.com para noticias globales."}]
noticias_ws = noticias_ws[:5]

# ARGENTINA
print("Generando argentina.json...")
dolar_raw = fetch("https://dolarapi.com/v1/dolares") or []
dolar = {}
for d in dolar_raw:
    casa = d.get("casa", "").lower()
    dolar[casa] = d.get("venta")

merval_raw = yahoo("%5EMERV", "Merval")
merval_precio = merval_raw.get("valor")
merval_var = merval_raw.get("variacion", "N/D")
try:
    var_num = float(merval_var.replace("%", "").replace("+", ""))
    tendencia = "alcista" if var_num > 0 else "bajista"
except Exception:
    tendencia = "neutral"

blue_val = dolar.get("blue")
mep_val = dolar.get("bolsa")
oficial_val = dolar.get("oficial")
ccl_val = dolar.get("contadoconliqui")
dash = chr(8212)

argentina = {
    "fecha": fecha,
    "hora": hora,
    "resumen": "Mercado argentino al " + fecha + ". Dolar blue: $" + str(blue_val) + ". MEP: $" + str(mep_val) + ". Merval: " + str(merval_precio) + " pts (" + merval_var + ").",
    "dolar": {
        "blue": ("$" + str(blue_val)) if blue_val else dash,
        "oficial": ("$" + str(oficial_val)) if oficial_val else dash,
        "mep": ("$" + str(mep_val)) if mep_val else dash,
        "ccl": ("$" + str(ccl_val)) if ccl_val else dash,
        "brecha": None
    },
    "merval": {
        "valor": merval_precio,
        "variacion": merval_var,
        "tendencia": tendencia
    },
    "bcra": {
        "reservas": "Ver BCRA.gob.ar",
        "tasa": dash,
        "nota": None
    },
    "noticias": noticias_arg,
    "conclusion": "Datos actualizados automaticamente a las " + hora + " hs del " + fecha + "."
}

with open("reports/argentina.json", "w", encoding="utf-8") as f:
    json.dump(argentina, f, ensure_ascii=False, indent=2)
print("reports/argentina.json OK")

# WALL STREET
print("Generando wallstreet.json...")
sp   = yahoo("%5EGSPC", "SP500")
dj   = yahoo("%5EDJI",  "DowJones")
nq   = yahoo("%5EIXIC", "Nasdaq")
oro  = yahoo("GC%3DF",  "Oro")
wti  = yahoo("CL%3DF",  "WTI")
soja = yahoo("ZS%3DF",  "Soja")

sp_v  = sp.get("valor",  "N/D"); sp_var  = sp.get("variacion",  "N/D")
dj_v  = dj.get("valor",  "N/D"); dj_var  = dj.get("variacion",  "N/D")
nq_v  = nq.get("valor",  "N/D"); nq_var  = nq.get("variacion",  "N/D")
oro_v = oro.get("valor", "N/D"); oro_var = oro.get("variacion", "N/D")
wti_v = wti.get("valor", "N/D"); wti_var = wti.get("variacion", "N/D")
soj_v = soja.get("valor","N/D"); soj_var = soja.get("variacion","N/D")

wallstreet = {
    "fecha": fecha,
    "hora": hora,
    "horario_datos": "Datos al cierre - " + fecha,
    "resumen": "Wall Street al " + fecha + ". S&P 500: " + str(sp_v) + " (" + str(sp_var) + "). Oro: $" + str(oro_v) + ".",
    "indices": {
        "sp500":  {"valor": sp_v,  "variacion": sp_var},
        "dow":    {"valor": dj_v,  "variacion": dj_var},
        "nasdaq": {"valor": nq_v,  "variacion": nq_var}
    },
    "bonos_usa": {
        "t10_yield": dash,
        "lectura": "neutral",
        "nota": None
    },
    "commodities": {
        "oro":  {"precio": "$" + str(oro_v), "variacion": oro_var},
        "wti":  {"precio": "$" + str(wti_v), "variacion": wti_var},
        "soja": {"precio": "$" + str(soj_v), "variacion": soj_var}
    },
    "macro_fed": {
        "postura_fed": "neutral",
        "nota": "Segui la Fed en Investing.com para datos en tiempo real."
    },
    "impacto_argentina": "Mercados globales actualizados al " + fecha + ".",
    "noticias": noticias_ws,
    "conclusion": "Datos actualizados automaticamente a las " + hora + " hs del " + fecha + "."
}

with open("reports/wallstreet.json", "w", encoding="utf-8") as f:
    json.dump(wallstreet, f, ensure_ascii=False, indent=2)
print("reports/wallstreet.json OK")
# -- FUNDAMENTALS (SEC EDGAR) ------------------------------------------------
TICKERS_CIK = {
    "NVDA": "0001045810",
    "META": "0001326801",
    "AMZN": "0001018724",
    "YPF":  "0000904851",
}

def fetch_fundamentals(ticker, cik):
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    headers = {
        "User-Agent": "manfrediinvestment-pixel contact@manfredi.com",
        "Accept-Encoding": "gzip, deflate",
        "Host": "data.sec.gov",
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read())
    except Exception as e:
        print(f"[fundamentals] Error fetching {ticker}: {e}")
        return None

    us_gaap = data.get("facts", {}).get("us-gaap", {})

    def quarter_label(end_date, fy, fp):
        try:
            quarter_map = {"Q1": "Q1", "Q2": "Q2", "Q3": "Q3", "Q4": "Q4", "FY": "Q4"}
            q = quarter_map.get(fp, fp)
            return f"{q} {fy}"
        except Exception:
            return end_date[:7]

    def get_quarterly_series(concept_names, scale=1e9, max_q=8):
        for concept in concept_names:
            node = us_gaap.get(concept, {})
            units = node.get("units", {})
            usd_list = units.get("USD", [])
            quarterly = [
                e for e in usd_list
                if e.get("form") in ("10-Q", "10-K")
                and e.get("fp") in ("Q1", "Q2", "Q3", "Q4", "FY")
                and e.get("filed") is not None
            ]
            seen = set()
            unique = []
            for e in sorted(quarterly, key=lambda x: x.get("end", ""), reverse=True):
                key = (e.get("end"), e.get("fp"), e.get("fy"))
                if key not in seen:
                    seen.add(key)
                    unique.append(e)
                if len(unique) >= max_q:
                    break
            if not unique:
                continue
            unique.reverse()
            return [
                {
                    "label": quarter_label(e.get("end", ""), e.get("fy", ""), e.get("fp", "")),
                    "val": round(e.get("val", 0) / scale, 2)
                }
                for e in unique
            ]
        return []

    revenue   = get_quarterly_series(["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues"])
    gross     = get_quarterly_series(["GrossProfit"])
    op_income = get_quarterly_series(["OperatingIncomeLoss"])
    cfo       = get_quarterly_series(["NetCashProvidedByUsedInOperatingActivities"])
    capex_raw = get_quarterly_series(["PaymentsToAcquirePropertyPlantAndEquipment"])
    debt      = get_quarterly_series(["LongTermDebt"])
    cash      = get_quarterly_series(["CashAndCashEquivalentsAtCarryingValue"])

    def series_map(series):
        return {e["label"]: e["val"] for e in series}

    rev_map   = series_map(revenue)
    gross_map = series_map(gross)
    op_map    = series_map(op_income)
    cfo_map   = series_map(cfo)
    capex_map = series_map(capex_raw)

    all_labels = [e["label"] for e in cfo]
    fcf = [
        {"label": lbl, "val": round(cfo_map.get(lbl, 0) - capex_map.get(lbl, 0), 2)}
        for lbl in all_labels
    ]

    gross_margin = [
        {"label": lbl, "val": round(gross_map[lbl] / rev_map[lbl] * 100, 2)}
        for lbl in [e["label"] for e in gross]
        if rev_map.get(lbl) and rev_map[lbl] != 0 and gross_map.get(lbl) is not None
    ]

    op_margin = [
        {"label": lbl, "val": round(op_map[lbl] / rev_map[lbl] * 100, 2)}
        for lbl in [e["label"] for e in op_income]
        if rev_map.get(lbl) and rev_map[lbl] != 0 and op_map.get(lbl) is not None
    ]

    return {
        "revenue":     revenue,
        "grossMargin": gross_margin,
        "opMargin":    op_margin,
        "fcf":         fcf,
        "debt":        debt,
        "cash":        cash,
    }


print("Generando reports/fundamentals.json...")
fundamentals = {}
for ticker, cik in TICKERS_CIK.items():
    print(f"  Fetching fundamentals: {ticker}...")
    result = fetch_fundamentals(ticker, cik)
    if result:
        fundamentals[ticker] = result
        print(f"  {ticker} OK -- {len(result.get('revenue', []))} quarters")
    else:
        print(f"  {ticker} FAILED -- se omite")

with open("reports/fundamentals.json", "w", encoding="utf-8") as f:
    json.dump(fundamentals, f, ensure_ascii=False, indent=2)
print("reports/fundamentals.json OK")

print("Listo: " + fecha + " " + hora)
