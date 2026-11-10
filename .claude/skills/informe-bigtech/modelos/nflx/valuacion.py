"""
Modelo de valuación NFLX — actualización al 3T 2026 (cierre 30-sep-2026, carta/8-K del 20-oct-2026, 10-Q del 21-oct-2026).

Correr:  python valuacion.py            (imprime todo y escribe resultados.json al lado)

Fuentes de los números de entrada (verificadas a mano contra el documento original):
  - 8-K Ex. 99.1 del 20-oct-2026 (carta a accionistas 3T26): resultados trimestrales 3T25-3T26, guía 4T26, regiones,
    flujo de caja, balance, deuda neta no-GAAP ($7,113.85M), recompras (63.9M acciones por $4.8B, $22.3B remanente),
    publicidad 2026 ~$2.7B (antes ~$3B), FCF 2026 ~$12.0B (antes $12.5B).
  - 10-Q del 21-oct-2026: Nota 6 (comisión de terminación de $2.8B cobrada en el 1T26, registrada en "Interest and other
    income"), Nota 7 deuda, 4,106,325,903 acciones al 30-sep-2026, publicidad +$256M interanual en el 3T, pagos no
    rutinarios de $729M en Brasil (9M26), costo de Brasil de $619M en el 3T25 (en costo de ingresos).
  - 8-K del 27-feb-2026 (Item 1.02): terminación del acuerdo con WBD y cobro de los $2.8B.
  - Carta 4T25 (8-K del 20-ene-2026): acuerdo WBD reformulado a $27.75 por acción todo en efectivo, puente de $42.2B,
    pausa de recompras; contenido 4T24/3T25/4T25 (altas y amortización); $60M de costos del puente en el 4T25.
  - Carta 3T25 (8-K del 21-oct-2025): cargo de Brasil ~$619M, "más de cinco puntos" de margen.
  - SEC companyfacts XBRL: EPS diluido trimestral 2024-2026 (los trimestres 2024 vienen SIN ajustar por el split
    10x1 del 14-nov-2025 -> se dividen por 10 abajo), ingresos, costo de ingresos, OCF, capex, recompras.
  - Yahoo Finance chart API (precios ya ajustados por el split): cierre 9-nov-2026 $63.95, cierres de fin de trimestre,
    ^TNX 4.864% (9-nov-2026), betas propios contra ^GSPC (5 años mensual 1.62, 2 años semanal 0.94).
  - stockanalysis.com: NFLX PT promedio $84.76 (51 analistas, rango $57-$126; consenso actualizado 22-oct-2026),
    ingresos FY26 $51.12B / FY27 $56.60B, EPS FY26 $3.57 / FY27 $3.77. Pares (9-nov-2026): DIS FY27 (sep) $7.50,
    SPOT 2027 EUR 15.24 (EURUSD 1.1225), ROKU 2027 $4.00; GOOGL 2027 $15.19 (6-nov-2026, el mismo dato del modelo META).

Convenciones del DCF (las mismas del informe de agosto, reproducido abajo):
  - 5 años explícitos, año 1 = un año de ingresos guiado/consenso; crecimiento y márgenes en línea recta año 1 -> 5.
  - FCF = ingresos x margen operativo x conversión FCF/EBIT. En agosto la conversión no estaba publicada: se despeja
    (78.9% en el Base). En esta versión se publica y se ancla en el FCF real.
  - Descuento a fin de año; VT = FCF5 x (1+g)/(WACC-g) descontado 5 años; equity = EV - deuda neta.
"""
import json, os

def lin(a, b, n=5):
    return [a + (b - a) * i / (n - 1) for i in range(n)]

R = {}

# ---------------------------------------------------------------------------
# 1) REPRODUCCIÓN DEL INFORME DE AGOSTO/SEPTIEMBRE (datos al 2T26, precio $73.33 del 3-ago-2026)
#    Publicado: año 1 = $51.2B (guía 2026), crecimiento y margen operativo por escenario, deuda neta $5.3B,
#    4,261M acciones. Lo único no publicado es la conversión FCF/EBIT: se despeja de cada fair value.
# ---------------------------------------------------------------------------
def dcf_ago(g, m, wacc, gt, conv, rev1=51.2, nd=5.3, sh=4.261):
    revs = [rev1]
    for x in lin(*g)[1:]:
        revs.append(revs[-1] * (1 + x))
    f = [r * mm * conv for r, mm in zip(revs, lin(*m))]
    pv = sum(x / (1 + wacc) ** (i + 1) for i, x in enumerate(f))
    pvtv = f[-1] * (1 + gt) / (wacc - gt) / (1 + wacc) ** 5
    ev = pv + pvtv
    return (ev - nd) / sh, pvtv / ev

AGO = {"Bear": ((0.13, 0.03), (0.31, 0.315), 0.114, 0.030, 36.69, 69),
       "Base": ((0.13, 0.06), (0.315, 0.37), 0.104, 0.035, 57.81, 75.6),
       "Bull": ((0.15, 0.08), (0.315, 0.405), 0.094, 0.040, 88.83, 82)}
R["ago_repro"] = {}
for k, (g, m, w, gt, pub, tvp) in AGO.items():
    ev1 = dcf_ago(g, m, w, gt, 1.0)[0] * 4.261 + 5.3
    conv = (pub * 4.261 + 5.3) / ev1
    fv, tv = dcf_ago(g, m, w, gt, conv)
    R["ago_repro"][k] = {"conv_implicita": round(conv, 4), "fv": round(fv, 2), "publicado": pub,
                         "tv_modelo": round(tv * 100, 1), "tv_publicado": tvp}
CONV_AGO = R["ago_repro"]["Base"]["conv_implicita"]
GRID_AGO_PUB = [[59.85, 63.73, 68.27, 73.66, 80.16], [55.52, 58.82, 62.63, 67.09, 72.38], [51.76, 54.58, 57.81, 61.55, 65.93],
                [48.44, 50.88, 53.65, 56.83, 60.50], [45.50, 47.63, 50.02, 52.75, 55.86]]
dif = []
for i, w in enumerate([0.094, 0.099, 0.104, 0.109, 0.114]):
    for j, gg in enumerate([0.025, 0.03, 0.035, 0.04, 0.045]):
        dif.append(abs(dcf_ago(AGO["Base"][0], AGO["Base"][1], w, gg, CONV_AGO)[0] - GRID_AGO_PUB[i][j]))
R["ago_grid_max_dif"] = round(max(dif), 2)
AGO_METHODS = {"DCF Base": 57.81, "Comparables": 64.08, "Consenso": 94.33}
R["ago_blend_simple_3"] = round(sum(AGO_METHODS.values()) / 3, 2)          # 72.07 publicado
AGO_PRICE = 73.33
W4 = {"DCF Base": 0.15, "Comparables": 0.25, "Reversión": 0.35, "Consenso": 0.25}

# ---------------------------------------------------------------------------
# 2) DATOS TRIMESTRALES (miles de millones de USD; EPS por acción post-split)
# ---------------------------------------------------------------------------
PRICE = 63.95               # cierre 9-nov-2026
PRICE_PRE = 68.69           # cierre 20-oct-2026 (reporte después del cierre)
PRICE_POST = 65.04          # cierre 21-oct-2026
TSY10 = 4.864
HI52 = 116.73               # máximo intradiario de 52 semanas (Yahoo)

q = ["4T24", "1T25", "2T25", "3T25", "4T25", "1T26", "2T26", "3T26"]
rev   = [10.247, 10.543, 11.079, 11.510307, 12.051, 12.250, 12.560, 12.874176]
cor   = [5.766, 5.263, 5.325, 6.164, 6.522, 5.888, 6.037, 6.079]
opinc = [2.273, 3.347, 3.775, 3.248, 2.957, 3.957, 4.193, 4.459]
ni    = [1.869, 2.890, 3.125, 2.547, 2.419, 5.283, 3.401, 3.664]
ocf   = [1.537, 2.789, 2.423, 2.825, 2.112, 5.290, 1.744, 3.162]
capex = [0.159, 0.128, 0.156, 0.165, 0.240, 0.196, 0.219, 0.279]
buyb  = [1.700, 3.536, 1.654, 1.857, 2.079, 1.271, 4.714, 4.797]
dil   = [4.377, 4.370, 4.349, 4.340, 4.317, 4.298, 4.261, 4.195]
# Contenido: altas (additions) y amortización; pagos en efectivo = altas + cambio en pasivos de contenido
c_add = {"4T24": 4.429, "3T25": 4.654, "4T25": 5.057, "1T26": 14.934 - 5.160 - 4.928, "2T26": 4.928, "3T26": 5.160}
c_dl  = {"4T24": -0.1395, "3T25": 0.0243, "4T25": -0.0098, "2T26": -0.1818, "3T26": 0.0935}
c_dl["1T26"] = -0.0431 - c_dl["2T26"] - c_dl["3T26"]
c_am  = {"4T24": 4.1615, "3T25": 4.0027, "4T25": 4.7642, "1T26": 12.7647 - 4.2355 - 4.3113, "2T26": 4.3113, "3T26": 4.2355}
c_pay = {k: c_add[k] - c_dl[k] for k in c_add}
R["content"] = {k: {"pagos": round(c_pay[k], 3), "amort": round(c_am[k], 3), "ratio": round(c_pay[k] / c_am[k], 2)} for k in c_add}
ttmq = ["4T25", "1T26", "2T26", "3T26"]
R["content_ttm"] = {"pagos": round(sum(c_pay[k] for k in ttmq), 3), "amort": round(sum(c_am[k] for k in ttmq), 3),
                    "ratio": round(sum(c_pay[k] for k in ttmq) / sum(c_am[k] for k in ttmq), 3),
                    "ratio_fy25": round((17.0966 + 0.6108) / 16.4222, 3)}
R["content_9m26_ratio"] = round((14.934 + 0.0431) / 12.7647, 3)

# Extraordinarios (después de impuestos)
#   3T25: Brasil $619M antes de impuestos (costo de ingresos), tasa efectiva del trimestre 18.1% (562.5/3,109.4)
#   4T25: ~$60M de costos del préstamo puente WBD (gasto de intereses), a la tasa del trimestre
#   1T26: comisión de terminación $2.8B; impuesto del 1T menos el impuesto "normal" (tasa media 2T-3T26) sobre el
#         resultado antes de impuestos sin la comisión
etr_q3_25 = 0.5625 / 3.1094
pre_q1 = 14.9326 - 4.0686 - 4.3169
tax_q1 = 2.5844 - 0.6672 - 0.6530
etr_norm = (0.6672 + 0.6530) / (4.0686 + 4.3169)
core_q1_ni = (pre_q1 - 2.8) * (1 - etr_norm)
fee_after_tax = 5.283 - core_q1_ni
adj_ni = {"3T25": 0.619 * (1 - etr_q3_25), "4T25": 0.060 * (1 - 0.15), "1T26": -fee_after_tax}
R["extra"] = {"brasil_neto": round(adj_ni["3T25"], 3), "puente_neto": round(adj_ni["4T25"], 3),
              "comision_neta": round(fee_after_tax, 3), "impuesto_comision": round(2.8 - fee_after_tax, 3),
              "etr_normal": round(etr_norm * 100, 1)}
core_ni = [n + adj_ni.get(l, 0) for l, n in zip(q, ni)]
# EPS diluido reportado (post-split; 2024 dividido por 10)
eps = [0.427, 0.66, 0.72, 0.59, 0.56, 1.23, 0.80, 0.87]
core_eps = [e + adj_ni.get(l, 0) / sh for l, e, sh in zip(q, eps, dil)]
R["quarters"] = {l: {"rev": rev[i], "gm": round((rev[i] - cor[i]) / rev[i] * 100, 1), "opinc": opinc[i],
                     "op_m": round(opinc[i] / rev[i] * 100, 1), "ni": ni[i], "core_ni": round(core_ni[i], 3),
                     "eps": eps[i], "core_eps": round(core_eps[i], 3), "ocf": ocf[i], "fcf": round(ocf[i] - capex[i], 3),
                     "buyback": buyb[i], "dil": dil[i]} for i, l in enumerate(q)}
R["yoy_rev"] = {l: round((rev[i] / rev[i - 4] - 1) * 100, 1) for i, l in enumerate(q) if i >= 4}

ttm = lambda a: sum(a[-4:])
T = {"rev": ttm(rev), "opinc": ttm(opinc), "ni": ttm(ni), "core_ni": ttm(core_ni), "ocf": ttm(ocf), "capex": ttm(capex),
     "eps": ttm(eps), "core_eps": ttm(core_eps), "buyback": ttm(buyb)}
T["fcf"] = T["ocf"] - T["capex"]
T["op_m"] = T["opinc"] / T["rev"] * 100
T["fcf_clean"] = T["fcf"] - 2.8 + R["extra"]["impuesto_comision"] + 0.729       # sin comisión, su impuesto ni Brasil
T["fcf_clean_m"] = T["fcf_clean"] / T["rev"] * 100
T["fcf_clean_conv"] = T["fcf_clean"] / T["opinc"] * 100
T["da"] = 0.086 + 0.099 + 0.101 + 0.107
T["ebitda"] = T["opinc"] + T["da"]
T["rev_prev"] = sum(rev[:4])
T["rev_yoy"] = (T["rev"] / T["rev_prev"] - 1) * 100
R["ttm"] = {k: round(v, 3) for k, v in T.items()}

# 3T26 contra 3T25 (reportado y comparable sin Brasil) y contra la guía de julio
Q = {"rev_yoy": (12.874176 / 11.510307 - 1) * 100, "op_m": 4.459 / 12.874 * 100, "op_m_prev": 3.248 / 11.510 * 100,
     "op_m_prev_ex": (3.248 + 0.619) / 11.510 * 100, "opinc_yoy": (4.459 / 3.248 - 1) * 100,
     "opinc_yoy_ex": (4.459 / (3.248 + 0.619) - 1) * 100, "eps_yoy": (0.87 / 0.59 - 1) * 100,
     "eps_prev_ex": core_eps[q.index("3T25")], "eps_yoy_ex": (0.87 / core_eps[q.index("3T25")] - 1) * 100,
     "gm": (12.874 - 6.079) / 12.874 * 100, "gm_prev_ex": (11.510 - 6.164 + 0.619) / 11.510 * 100,
     "rev_vs_guide": (12.874 / 12.86 - 1) * 100, "eps_vs_guide": 0.87 - 0.82, "ni_vs_guide": 3.664 - 3.45,
     "ads_inc": 0.256, "subs_inc": 1.057, "fx": 0.101, "fcf": 3.162 - 0.279, "buyback": 4.797,
     "bb_shares": 63.9, "bb_avg_px": 4.797 / 0.0639, "reaction": (PRICE_POST / PRICE_PRE - 1) * 100}
R["q3"] = {k: round(v, 2) for k, v in Q.items()}

# Guía 4T26 contra consenso previo (consenso: CNBC/LSEG e investinglive, 20-oct-2026)
G = {"q4_rev": 13.442, "q4_om": 26.0, "q4_opinc": 3.500, "q4_eps": 0.67, "q4_ni": 2.787,
     "cons_rev": 13.5, "cons_eps": 0.73, "cons_om": 28.0, "cons_opinc": 3.7, "layoff_bp": 120,
     "fy_rev": 51.1, "fy_om": 31.5, "fy_ads": 2.7, "fy_ads_prev": 3.0, "fy25_ads": 1.5, "fcf": 12.0, "fcf_prev": 12.5}
G["q4_rev_yoy"] = (G["q4_rev"] / 12.051 - 1) * 100
G["q4_om_prev"] = 2.957 / 12.051 * 100
G["q4_om_ex_layoff"] = G["q4_om"] + G["layoff_bp"] / 100
G["q4_eps_vs_cons"] = (G["q4_eps"] / G["cons_eps"] - 1) * 100
G["fy_rev_check"] = 37.684 + G["q4_rev"]
G["fy_rev_yoy"] = (G["fy_rev_check"] / 45.183 - 1) * 100
G["fy_opinc"] = 12.608 + G["q4_opinc"]
G["fy_om_check"] = G["fy_opinc"] / G["fy_rev_check"] * 100
G["fy_opinc_yoy"] = (G["fy_opinc"] / 13.327 - 1) * 100
G["ads_yoy"] = (G["fy_ads"] / G["fy25_ads"] - 1) * 100
G["ads_share"] = G["fy_ads"] / G["fy_rev_check"] * 100
G["fcf_clean"] = G["fcf"] - 2.8 + R["extra"]["impuesto_comision"] + 0.729
G["fcf_clean_m"] = G["fcf_clean"] / G["fy_rev_check"] * 100
G["fcf_clean_conv"] = G["fcf_clean"] / G["fy_opinc"] * 100
R["guide"] = {k: round(v, 3) for k, v in G.items()}

# ---------------------------------------------------------------------------
# 3) BALANCE (30-sep-2026) — deuda: corto + largo plazo contable (LongTermDebt NO se suma dos veces)
# ---------------------------------------------------------------------------
B = dict(cash=8.194, sti=0.029, debt_st=2.475, debt_lt=12.658, debt_issue=0.059, debt_hedge=0.145,
         content_oblig=25.223, content_oblig_12m=11.777, shares_out=4.106326, bb_left=22.3, equity=29.286)
B["debt_carrying"] = B["debt_st"] + B["debt_lt"]
B["debt_gross"] = B["debt_carrying"] + B["debt_issue"] + B["debt_hedge"]        # = $15.34B de la carta
B["net_debt"] = B["debt_gross"] - B["cash"] - B["sti"]                          # = no-GAAP de la compañía $7.11B
B["net_debt_ebitda"] = B["net_debt"] / T["ebitda"]
B["net_debt_jun"] = 14.4 - 9.10
R["bal"] = {k: round(v, 3) for k, v in B.items()}

# WBD: contrafáctico con los términos de enero-2026 (no es un escenario de valuación: el acuerdo terminó el 27-feb-2026
# y Paramount cerró la compra el 6-oct-2026). Deuda neta pro forma = actual + EV de la operación ($82.7B), sobre el
# EBITDA de Netflix sola (no publicamos EBITDA de los activos de WB).
WBD = {"px": 27.75, "ev": 82.7, "eq": 72.0, "bridge": 42.2, "fee": 2.8}
WBD["nd_pf"] = B["net_debt"] + WBD["ev"]
WBD["nd_pf_x"] = WBD["nd_pf"] / T["ebitda"]
WBD["fee_per_share"] = R["extra"]["comision_neta"] / 4.298
R["wbd"] = {k: round(v, 3) for k, v in WBD.items()}

# ---------------------------------------------------------------------------
# 4) WACC y DCF ACTUALIZADO — año 1 = FY2027 (consenso $56.60B, +10.8% sobre la guía 2026)
# ---------------------------------------------------------------------------
BETA_5Y, BETA_2Y = 1.62, 0.94          # propios, contra ^GSPC (Yahoo): 5 años mensual / 2 años semanal
BETA = round((BETA_5Y + BETA_2Y) / 2, 2)
ERP, KD_AT = 5.0, 4.4                  # KD: cupón de la emisión de jul-2026 (5.25%) después de impuestos (~16%)
mcap = PRICE * B["shares_out"]
ke = TSY10 + BETA * ERP
wd = B["debt_gross"] / (mcap + B["debt_gross"])
wacc_base = round((1 - wd) * ke + wd * KD_AT, 1) / 100
R["wacc"] = {"beta": BETA, "ke": round(ke, 2), "wd": round(wd * 100, 1), "mcap": round(mcap, 1), "wacc_base": wacc_base}

REV1 = 56.60
SHARES = 4.195                         # diluidas del 3T26
R["rev1_growth"] = round((REV1 / G["fy_rev_check"] - 1) * 100, 1)

def dcf(rev1, g2_5, om, conv, wacc, g, nd=B["net_debt"], sh=SHARES):
    revs = [rev1]
    for x in lin(g2_5[0], g2_5[1], 4):
        revs.append(revs[-1] * (1 + x))
    oms, cvs = lin(*om), lin(*conv)
    fcf = [r * o * c for r, o, c in zip(revs, oms, cvs)]
    pv = sum(f / (1 + wacc) ** (i + 1) for i, f in enumerate(fcf))
    pvtv = fcf[-1] * (1 + g) / (wacc - g) / (1 + wacc) ** 5
    ev = pv + pvtv
    return {"fv": (ev - nd) / sh, "tv_share": pvtv / ev, "fcf": fcf, "revs": revs, "ev": ev}

cases = {
    # Bear: ingresos 2027 1.9% debajo del consenso; margen estancado en el nivel 2026 (+0.5 pp); conversión sin mejora
    "Bear": dict(rev1=55.5, g2_5=(0.08, 0.03), om=(0.32, 0.325), conv=(0.67, 0.70), wacc=wacc_base + 0.01, g=0.03),
    "Base": dict(rev1=REV1, g2_5=(0.10, 0.06), om=(0.335, 0.38), conv=(0.70, 0.76), wacc=wacc_base, g=0.035),
    "Bull": dict(rev1=57.5, g2_5=(0.12, 0.08), om=(0.34, 0.41), conv=(0.72, 0.79), wacc=wacc_base - 0.01, g=0.04),
}
R["dcf"] = {}
for k, c in cases.items():
    r = dcf(c["rev1"], c["g2_5"], c["om"], c["conv"], c["wacc"], c["g"])
    R["dcf"][k] = {"fv": round(r["fv"], 2), "tv_share": round(r["tv_share"] * 100, 1), "fcf1": round(r["fcf"][0], 2),
                   "fcf5": round(r["fcf"][-1], 2), "rev1": c["rev1"], "rev5": round(r["revs"][-1], 2),
                   "wacc": round(c["wacc"] * 100, 2), "g": round(c["g"] * 100, 1),
                   "fcf_m1": round(r["fcf"][0] / c["rev1"] * 100, 1), "fcf": [round(x, 2) for x in r["fcf"]]}
fvs = {k: R["dcf"][k]["fv"] for k in cases}
R["dcf_simple_avg"] = round(sum(fvs.values()) / 3, 2)
R["dcf_prob"] = round(0.25 * fvs["Bear"] + 0.45 * fvs["Base"] + 0.30 * fvs["Bull"], 2)
b = cases["Base"]
# Mismo Base con la conversión de agosto (78.9% plana): aísla la corrección de calibración
R["base_conv_agosto"] = round(dcf(b["rev1"], b["g2_5"], b["om"], (CONV_AGO, CONV_AGO), b["wacc"], b["g"])["fv"], 2)
# Mismo Base con el WACC de agosto (10.4%)
R["base_wacc_agosto"] = round(dcf(b["rev1"], b["g2_5"], b["om"], b["conv"], 0.104, b["g"])["fv"], 2)

waccs = [round(wacc_base + d, 4) for d in (-0.01, -0.005, 0, 0.005, 0.01)]
gs = [0.025, 0.03, 0.035, 0.04, 0.045]
R["grid"] = {"waccs": [round(w * 100, 2) for w in waccs], "gs": [round(x * 100, 1) for x in gs],
             "vals": [[round(dcf(b["rev1"], b["g2_5"], b["om"], b["conv"], w, gg)["fv"], 2) for gg in gs] for w in waccs]}

def solve(fn, lo, hi, target, n=80):
    for _ in range(n):
        mid = (lo + hi) / 2
        if (fn(mid) - target) * (fn(lo) - target) <= 0: hi = mid
        else: lo = mid
    return (lo + hi) / 2
f_om = lambda m: dcf(b["rev1"], b["g2_5"], (b["om"][0], m), b["conv"], b["wacc"], b["g"])["fv"]
R["inverso_om5"] = round(solve(f_om, 0.30, 0.60, PRICE) * 100, 1)

# ---------------------------------------------------------------------------
# 5) COMPARABLES — P/E sobre EPS 2027E (DIS: FY27 cerrado en sep-2027; SPOT en EUR convertido a USD)
#    WBD dejó de cotizar el 6-oct-2026 (absorbida por Paramount -> Skydance): sin múltiplo, fuera del panel.
# ---------------------------------------------------------------------------
EURUSD = 1.1225
peers = {"DIS": (119.12, 7.50), "SPOT": (609.10, 15.24 * EURUSD), "GOOGL": (288.15, 15.19), "ROKU": (159.93, 4.00)}
EPS27 = 3.77
pe = {k: v[0] / v[1] for k, v in peers.items()}
pe_avg = sum(pe.values()) / len(pe)
pe_ex = sum(v for k, v in pe.items() if k != "ROKU") / 3
srt = sorted(pe.values()); pe_med = (srt[1] + srt[2]) / 2
R["comps"] = {"pe": {k: round(v, 2) for k, v in pe.items()}, "pe_avg": round(pe_avg, 2), "pe_ex_roku": round(pe_ex, 2),
              "pe_med": round(pe_med, 2), "eps27": EPS27, "fv": round(pe_avg * EPS27, 2),
              "fv_ex_roku": round(pe_ex * EPS27, 2), "fv_med": round(pe_med * EPS27, 2),
              "implied": {k: round(v * EPS27, 2) for k, v in pe.items()},
              "nflx_fwd27": round(PRICE / EPS27, 2), "nflx_fwd26": round(PRICE / 3.57, 2),
              "nflx_ttm_core": round(PRICE / T["core_eps"], 2), "nflx_ttm_gaap": round(PRICE / T["eps"], 2),
              "eps27_growth_vs_core26": None}

# ---------------------------------------------------------------------------
# 6) REVERSIÓN — P/E propio sobre EPS TTM sin extraordinarios (10-Q/10-K), en cierres trimestrales ajustados por split
# ---------------------------------------------------------------------------
pre_eps = {"1T24": 0.528, "2T24": 0.488, "3T24": 0.540}      # 10-Q 2024: $5.28 / $4.88 / $5.40 antes del split
all_lab = list(pre_eps) + q
all_eps = list(pre_eps.values()) + core_eps
qe_px = {"4T24": 89.13, "1T25": 93.25, "2T25": 133.91, "3T25": 119.89, "4T25": 93.76, "1T26": 96.15,
         "2T26": 71.40, "3T26": 69.58}
def window(labs):
    out = []
    for lab in labs:
        i = all_lab.index(lab)
        e = sum(all_eps[i - 3:i + 1])
        out.append((lab, qe_px[lab], round(e, 3), round(qe_px[lab] / e, 2)))
    return out
w4 = window(["4T25", "1T26", "2T26", "3T26"])
w8 = window(q)
pe4 = sum(x[3] for x in w4) / 4
pe8 = sum(x[3] for x in w8) / 8
R["rev"] = {"window": w4, "window8": w8, "pe4": round(pe4, 2), "pe8": round(pe8, 2), "eps_core_ttm": round(T["core_eps"], 3),
            "fv": round(pe4 * T["core_eps"], 2), "fv8": round(pe8 * T["core_eps"], 2),
            "pe_last2": round((w4[2][3] + w4[3][3]) / 2, 2), "fv_last2": round((w4[2][3] + w4[3][3]) / 2 * T["core_eps"], 2)}
# Reversión equivalente de agosto (ventana 3T25-2T26 sobre EPS TTM limpio al 2T26) para comparar en serio
w4_ago = window(["3T25", "4T25", "1T26", "2T26"])
pe4_ago = sum(x[3] for x in w4_ago) / 4
eps_ago = sum(all_eps[all_lab.index("2T26") - 3:all_lab.index("2T26") + 1])
R["rev_ago"] = {"window": w4_ago, "pe4": round(pe4_ago, 2), "eps": round(eps_ago, 3), "fv": round(pe4_ago * eps_ago, 2)}

# ---------------------------------------------------------------------------
# 7) CONSENSO y BLEND (15% DCF + 25% comps + 35% reversión + 25% consenso)
# ---------------------------------------------------------------------------
CONS = 84.76
CONS_AGO = 94.33
R["cons_pt_change"] = round((CONS / CONS_AGO - 1) * 100, 1)
# EPS de consenso 2026 sin la comisión de WBD (después de impuestos, por acción diluida del 1T26)
R["eps26_clean"] = round(3.57 - WBD["fee_per_share"], 3)
R["eps27_growth_rep"] = round((3.77 / 3.57 - 1) * 100, 1)
R["eps27_growth_clean"] = round((3.77 / R["eps26_clean"] - 1) * 100, 1)
REG = {"UCAN": 5.628215, "EMEA": 4.106572, "LATAM": 1.602603, "APAC": 1.536786}
R["region_share"] = {k: round(v / 12.874176 * 100, 1) for k, v in REG.items()}
methods ={"DCF Base": fvs["Base"], "Comparables": R["comps"]["fv"], "Reversión": R["rev"]["fv"], "Consenso": CONS}
blend = sum(methods[k] * W4[k] for k in W4)
R["methods"] = {k: round(v, 2) for k, v in methods.items()}
R["contrib"] = {k: round(methods[k] * W4[k], 2) for k in W4}
R["blend"] = round(blend, 2)
R["blend_vs_price"] = round((blend / PRICE - 1) * 100, 1)
R["blend_simple"] = round(sum(methods.values()) / 4, 2)
m_ex = dict(methods, Comparables=R["comps"]["fv_ex_roku"])
R["blend_ex_roku"] = round(sum(m_ex[k] * W4[k] for k in W4), 2)
R["blend_ex_roku_vs_price"] = round((R["blend_ex_roku"] / PRICE - 1) * 100, 1)
m_r2 = dict(methods, Reversión=R["rev"]["fv_last2"])
R["blend_rev2"] = round(sum(m_r2[k] * W4[k] for k in W4), 2)
R["blend_rev2_vs_price"] = round((R["blend_rev2"] / PRICE - 1) * 100, 1)
# Agosto: promedio simple de 3 (publicado) y recalculado con la ponderación vigente + reversión propia equivalente
ago_w = {"DCF Base": 57.81, "Comparables": 64.08, "Reversión": R["rev_ago"]["fv"], "Consenso": 94.33}
R["ago_blend_ponderado"] = round(sum(ago_w[k] * W4[k] for k in W4), 2)
R["blend_vs_ago_publicado"] = round((blend / 72.07 - 1) * 100, 1)
R["blend_vs_ago_ponderado"] = round((blend / R["ago_blend_ponderado"] - 1) * 100, 1)
R["ago_ponderado_vs_price"] = round((R["ago_blend_ponderado"] / AGO_PRICE - 1) * 100, 1)
R["price"] = PRICE
R["price_vs_ago"] = round((PRICE / AGO_PRICE - 1) * 100, 1)
R["price_vs_hi52"] = round((PRICE / HI52 - 1) * 100, 1)
R["from_pre"] = round((PRICE / PRICE_PRE - 1) * 100, 1)
R["mcap"] = round(mcap, 1)
R["method_vs_price"] = {k: round((v / PRICE - 1) * 100, 1) for k, v in methods.items()}
R["dcf_vs_price"] = {k: round((v / PRICE - 1) * 100, 1) for k, v in fvs.items()}
pes4 = [x[3] for x in w4]
R["ff"] = {"DCF": [fvs["Bear"], fvs["Bull"]],
           "Comparables": [min(R["comps"]["implied"].values()), max(R["comps"]["implied"].values())],
           "Reversión": [round(min(pes4) * T["core_eps"], 2), round(max(pes4) * T["core_eps"], 2)],
           "Consenso": [57.0, 126.0]}

if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resultados.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(R, fh, ensure_ascii=False, indent=1)
    print(json.dumps(R, ensure_ascii=False, indent=1))
