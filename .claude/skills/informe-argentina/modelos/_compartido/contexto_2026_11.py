"""Espejo de máquina de contexto-2026-11.md (fechas y fuentes en el .md). Corte: 20-nov-2026."""
import json, os

FECHA_CORTE = "2026-11-20"

# --- Macro ---
RP_SPOT = 1070          # pb, EMBI 20-nov-2026
RP_PROM_90D = 653       # pb, 24-ago → 20-nov-2026
RP_NORMALIZACION = 550  # pb, nivel de "normalización" que discute el mercado (skill)
CCL = 1806.2            # venta, 20/21-nov
MEP = 1743.1
OFICIAL_MAYORISTA = 1564.8
IPC_OCT26_MM = 0.022
IPC_12M = 0.332
REEXP_JUN_OCT26 = 1.021 * 1.017 * 1.019 * 1.022   # jul-ago-sep-oct 2026 (INDEC)
REM_IPC_12M = 0.218
REM_PBI_2026 = 0.007

# --- Costo de capital ---
RF = 0.0491             # UST 10Y 20-nov-2026
ERP = 0.0423            # Damodaran ctryprem ene-2026
CRP_DAMODARAN_AR = 0.0971
BETA_BANCOS = 0.76      # Damodaran Bank (Money Center) EE.UU., ene-2026
INFL_USA = 0.025
CRP_PEERS = {"BR": 0.0324, "MX": 0.0246, "CO": 0.0285, "PE": 0.0207, "CL": 0.0110}

# --- Escenarios macro (riesgo país año 1 → largo plazo, pb) y probabilidades ---
# Base: spot → punto medio entre spot y 550. Bear anclado en PASO 2019 (872 → 1.472 → >2.000 en sep-19).
# Probabilidades: año preelectoral (oct-2027) y estrés de noviembre → más peso a la cola mala.
ESCENARIOS = {
    "bear": {"rp1": 1500, "rp_lp": 1000, "p": 0.30},
    "base": {"rp1": RP_SPOT, "rp_lp": (RP_SPOT + RP_NORMALIZACION) / 2, "p": 0.45},
    "bull": {"rp1": RP_SPOT, "rp_lp": 500, "p": 0.25},
}

# --- Comparables Latam (23-nov-2026): P/BV, P/E fwd, ROE, país ---
PEERS = {
    "Itaú Unibanco":   (1.91, 7.95, 0.210, "BR"),
    "Bradesco":        (0.78, 5.08, 0.142, "BR"),
    "Banorte":         (2.12, 8.28, 0.249, "MX"),
    "Bancolombia":     (1.80, 7.29, 0.191, "CO"),
    "Credicorp":       (2.45, 10.36, 0.199, "PE"),
    "Banco de Chile":  (3.27, 13.87, 0.211, "CL"),
    "Santander Chile": (3.01, 11.73, 0.233, "CL"),
}
PARES_LOCALES = {  # P/BV (PN jun-26 reexpresado), P/E 2T26 anualizado, ROE 2T26
    "BBVA Argentina": (0.71, 5.9, 0.121),
    "Supervielle":    (0.55, 12.8, 0.044),
}

# --- Consenso (USD por ADR), ventana 22-ago → 20-nov-2026 ---
CCL_IMPLICITO = 1802.1
CONSENSO = {
    "GGAL": [("Morgan Stanley", "12/13-oct-2026", 70.0), ("UBS", "12/13-oct-2026", 45.0),
             ("Santander", "12/13-oct-2026", 103.0),
             ("Allaria", "27-oct-2026", 15500 * 10 / CCL_IMPLICITO)],
    "BMA": [("Morgan Stanley", "12/13-oct-2026", 108.0), ("UBS", "12/13-oct-2026", 90.0),
            ("Santander", "12/13-oct-2026", 150.0),
            ("Allaria", "27-oct-2026", 22600 * 10 / CCL_IMPLICITO),
            ("Citi", "13-nov-2026", 15500 * 10 / CCL_IMPLICITO)],
}


def serie():
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "serie-trimestral.json")
    return json.load(open(p, encoding="utf-8"))["filas"]
