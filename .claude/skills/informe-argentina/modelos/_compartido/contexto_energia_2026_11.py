"""Espejo de máquina de contexto-energia-2026-11.md (fechas y fuentes en el .md). Corte: 24-nov-2026.

Búsqueda compartida de petróleo para YPF y VIST (y la que viene: PAM upstream, TGS líquidos).
Los valuacion.py de energía importan de acá: deck de crudo, escenarios macro actualizados al 24-nov,
comparables, consenso, serie trimestral de múltiplos y funciones del modelo E&P (NAV y flujo).
"""
import statistics

FECHA_CORTE = "2026-11-24"

# ------------------------- Macro actualizada (ver "Actualización 24-nov-2026" en contexto-2026-11.md)
RP_SPOT = 1035            # pb, EMBI 23-nov-2026 (último publicado al corte; argentinadatos)
RP_PROM_90D = 663         # pb, 26-ago → 23-nov-2026 (64 ruedas)
RP_NORMALIZACION = 550
CCL = 1806.2              # venta 24-nov-2026 (argentinadatos)
MEP = 1743.1
OFICIAL_MAYORISTA = 1580.0
RF = 0.0490               # UST 10Y 24-nov-2026 (Yahoo ^TNX)
ERP = 0.0423              # Damodaran ctryprem ene-2026
CRP_DAMODARAN_AR = 0.0971
TASA_IMP = 0.35

# Beta: Damodaran ene-2026, Oil/Gas (Production and Exploration) EE.UU., 142 empresas: beta desapalancada 0,56
# (Integrated EE.UU. da 0,27 con solo 4 empresas: muestra chica, no se usa).
BETA_U_EYP = 0.56

# Escenarios macro: mismas reglas que contexto_2026_11 (Base: spot → punto medio entre spot y 550),
# recalculadas con el riesgo país del corte nuevo. Probabilidades: año preelectoral → más peso a la cola.
ESCENARIOS = {
    "bear": {"rp1": 1500, "rp_lp": 1000, "p": 0.30},
    "base": {"rp1": RP_SPOT, "rp_lp": (RP_SPOT + RP_NORMALIZACION) / 2, "p": 0.45},
    "bull": {"rp1": RP_SPOT, "rp_lp": 500, "p": 0.25},
}

# ------------------------- Deck de crudo (regla de informe-energia: nunca el spot)
BRENT_SPOT = 88.41        # USD/bbl, 24-nov-2026 (BZ=F)
WTI_SPOT = 81.64
CURVA_BRENT = {"dic-27": 75.74, "dic-28": 71.82, "dic-29": 70.00, "dic-30": 68.87}   # NYMEX BZ, 24-nov
CURVA_WTI = {"dic-27": 71.80, "dic-28": 67.70, "dic-29": 65.43, "dic-30": 63.25, "dic-31": 60.65}
BRENT_PROM = {"2024": 73.1, "2025": 68.1, "2026 (al 24-nov)": 91.4, "4T25": 63.1, "3T26": 91.5}
EIA_STEO_2027 = 86.0      # STEO 10-nov-2026 (4T27: 77)
# Bear = un precio vivido: promedio del 4T25 (63). Base = mitad de ciclo 70 (backend de la curva 69-72,
# bancos: GS 70 en 2028, BofA 70 desde 2027, Bradesco LP 65, Vista 75 real desde 2028).
# Bull = EIA 2027 (~85). Año 1 (2027) arranca en la curva dic-27 y converge al nivel del deck.
DECK = {"bear": 63.0, "base": 70.0, "bull": 85.0}
P_CRUDO = {"bear": 0.25, "base": 0.45, "bull": 0.30}     # ponderación 25/45/30 de informe-energia
BRENT_AÑO1 = 75.74

# ------------------------- Comparables en USD (24-nov-2026). EV/EBITDA TTM; P/E forward (Yahoo);
# EV/boe sobre reservas probadas 1P dic-2025; DN/EBITDA; dividend yield. País para el CRP.
COMPS = {
    #  nombre:           (EV/EBITDA, P/E fwd, EV/boe 1P, DN/EBITDA, div. yield, país, grupo)
    "Diamondback":       (5.32, 8.1, 18.8, 0.99, 0.027, "US", "shale EE.UU."),
    "EOG":               (4.85, 8.6, 14.1, 0.16, 0.030, "US", "shale EE.UU."),
    "Permian Resources": (4.71, 7.5, 18.6, 0.71, 0.031, "US", "shale EE.UU."),
    "Devon":             (5.64, 8.0, None, 1.06, 0.031, "US", "shale EE.UU."),
    "Petrobras":         (3.81, 3.8, 13.3, 1.42, 0.090, "BR", "Latam estatal"),
    "Ecopetrol":         (3.63, 7.0, 28.5, 1.89, 0.049, "CO", "Latam estatal"),
    "Pampa (PAM)":       (5.23, 5.1, None, 1.81, 0.000, "AR", "local"),
    "TGS":               (3.60, 7.6, None, -0.22, 0.000, "AR", "local"),
}
REFINADORAS = {"Valero": 4.63, "Marathon Petroleum": 5.26, "Phillips 66": 6.92}   # EV/EBITDA TTM, Yahoo 24-nov
PEMEX = "bono 6,625% 2035: G-spread ~331 pb (Cbonds, fecha no publicada) — sin acción cotizante"
CRP_PAIS = {"US": 0.0, "BR": 0.0324, "CO": 0.0285, "MX": 0.0246, "AR": None}

# ------------------------- Consenso: precios objetivo del ADR, ventana 90 días (26-ago → 24-nov-2026)
# Fecha = fecha del reporte si se publicó; si no, la de la nota que lo informa (ver .md).
CONSENSO = {
    "YPF": [("Goldman Sachs", "10-nov-2026", 48.70), ("JPMorgan", "31-ago-2026", 66.0),
            ("Citi", "11-sep-2026", 60.0), ("BofA", "11-sep-2026", 65.0), ("BTG Pactual", "11-sep-2026", 58.0),
            ("UBS", "28-oct-2026", 55.0), ("Bradesco BBI", "28-oct-2026", 55.0),
            ("Santander", "28-oct-2026", 84.0), ("TPH Research", "28-oct-2026", 85.0),
            ("Allaria", "28-oct-2026", 80.0), ("Latin Securities", "28-oct-2026", 65.0),
            ("Adcap", "30-oct-2026", 63.0)],
    "VIST": [("Goldman Sachs", "10-nov-2026", 69.70), ("BofA", "10-sep-2026", 107.0), ("UBS", "10-sep-2026", 80.0),
             ("Itaú BBA", "11-sep-2026", 100.0), ("JPMorgan", "11-sep-2026", 94.0), ("BTG Pactual", "11-sep-2026", 92.0),
             ("Citi", "11-sep-2026", 91.0), ("HSBC", "11-sep-2026", 90.0), ("Adcap", "30-oct-2026", 87.0)],
}

# ------------------------- Serie trimestral (4T21 → 3T26): riesgo país a cierre (serie-trimestral.json),
# ADR (Yahoo) y EV/EBITDA TTM reportado (stockanalysis.com, ratios trimestrales, bajado el 24-nov-2026).
TRIM = ["2021-12-31", "2022-03-31", "2022-06-30", "2022-09-30", "2022-12-31", "2023-03-31", "2023-06-30",
        "2023-09-30", "2023-12-31", "2024-03-31", "2024-06-30", "2024-09-30", "2024-12-31", "2025-03-31",
        "2025-06-30", "2025-09-30", "2025-12-31", "2026-03-31", "2026-06-30", "2026-09-30"]
RP_TRIM = [1688, 1718, 2428, 2754, 2213, 2276, 2037, 2543, 1906, 1439, 1456, 1290, 635, 816, 701, 1222, 571,
           617, 426, 607]
EV_EBITDA = {
    "YPF": [2.70, 2.63, 2.19, 2.77, 3.45, 4.08, 5.79, 7.10, 8.47, 7.71, 6.51, 4.78, 6.71, 6.04, 5.30, 5.09,
            5.93, 5.91, 4.33, 3.83],
    "VIST": [2.24, 2.63, 1.98, 1.91, 2.40, 2.81, 3.50, 4.61, 4.16, 5.28, 5.07, 4.23, 5.71, 4.77, 5.06, 4.48,
             4.99, 6.06, 4.81, 4.12],
}
# ADR a cierre de trimestre, dic-2016 → sep-2026 (Yahoo, USD): para el gráfico precio vs. riesgo país
ADR_HIST = {
    "fechas": ["2016-12", "2017-06", "2017-12", "2018-06", "2018-12", "2019-06", "2019-09", "2019-12",
               "2020-03", "2020-12", "2021-06", "2021-12", "2022-06", "2022-12", "2023-06", "2023-12",
               "2024-06", "2024-12", "2025-06", "2025-09", "2025-12", "2026-03", "2026-06", "2026-09", "2026-11"],
    "rp": [455, 432, 351, 610, 817, 835, 2143, 1744, 3803, 1368, 1596, 1688, 2428, 2213, 2037, 1906, 1456, 635,
           701, 1222, 571, 617, 426, 607, 1035],
    "YPF": [16.5, 21.9, 22.91, 13.58, 13.39, 18.21, 9.25, 11.58, 4.17, 4.7, 4.68, 3.82, 3.26, 9.19, 14.89, 17.19,
            20.12, 42.51, 31.45, 24.29, 36.16, 46.22, 45.47, 50.13, 31.71],
    "VIST": [None, None, None, None, None, None, 5.17, 7.85, 2.0, 2.56, 4.1, 5.33, 7.39, 15.66, 24.12, 29.51,
             45.48, 54.11, 47.81, 34.4, 48.66, 75.47, 63.8, 65.35, 49.61],
}


# ------------------------- Funciones del modelo E&P (compartidas)

def brent_senda(nivel_lp, n=5, año1=BRENT_AÑO1):
    """Brent año 1 = curva dic-27; converge linealmente al deck en el año 3 y queda ahí."""
    out = []
    for i in range(n):
        w = min(i / 2, 1.0)
        out.append(año1 + (nivel_lp - año1) * w)
    return out


def regresion_rp(xs, ys):
    mx, my = statistics.mean(xs), statistics.mean(ys)
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    a = my - b * mx
    r2 = 1 - sum((y - (a + b * x)) ** 2 for x, y in zip(xs, ys)) / sum((y - my) ** 2 for y in ys)
    return a, b, r2


def regimenes(xs, ys):
    g = {"<800": [y for x, y in zip(xs, ys) if x < 800],
         "800-1500": [y for x, y in zip(xs, ys) if 800 <= x <= 1500],
         ">1500": [y for x, y in zip(xs, ys) if x > 1500]}
    return {k: (statistics.median(v), len(v)) for k, v in g.items() if v}


def nav_reservas(reservas, prod_año, netback, tasa, capex_dev=0.0, tasa_imp=TASA_IMP):
    """PV de producir `reservas` (MMboe) con declino exponencial d = prod/reservas (la suma converge a las
    reservas). netback: USD/boe antes de impuestos; capex_dev: USD/boe de desarrollo (PUD). Flujo después de
    impuestos = (netback − capex_dev) × (1 − t). Devuelve USD M."""
    d = prod_año / reservas
    pv, q, t, acum = 0.0, prod_año, 1, 0.0
    while acum < reservas * 0.999 and t < 60:
        q_t = min(q, reservas - acum)
        pv += q_t * (netback - capex_dev) * (1 - tasa_imp) / (1 + tasa) ** (t - 0.5)
        acum += q_t
        q *= 1 - d
        t += 1
    return pv


def matriz_9(valuar_combo):
    """valuar_combo(macro, crudo) -> valor. Devuelve la tabla 3x3 y el valor esperado (probabilidades
    independientes: macro 30/45/25 × crudo 25/45/30)."""
    tabla, esp = {}, 0.0
    for m in ("bear", "base", "bull"):
        for c in ("bear", "base", "bull"):
            v = valuar_combo(m, c)
            tabla[(m, c)] = v
            esp += ESCENARIOS[m]["p"] * P_CRUDO[c] * v
    return tabla, esp
