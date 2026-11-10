"""
Modelo de valuación TSLA — actualización al 3T 2026 (cierre 30-sep-2026; Update Letter / 8-K del 21-oct-2026;
10-Q del 22-oct-2026).

Correr:  python valuacion.py            (imprime todo y escribe resultados.json al lado)

Fuentes de los números de entrada (verificadas a mano contra el documento original):
  - Q3 2026 Update (8-K Ex. 99.1 del 21-oct-2026): estado de resultados, balance, flujo de caja y conciliación
    no-GAAP de 3T25-3T26; series trimestrales de Adjusted EBITDA, OCF y capex desde 1T23.
  - Update letters del 3T25 (8-K 22-oct-2025) y 3T24 (8-K 23-oct-2024): créditos regulatorios, restructuración,
    balance y acciones diluidas de 3T23-2T25.
  - 10-Q del 22-oct-2026: Nota 8 (deuda), Nota 2 (SpaceX a valor razonable $2,865M), aranceles IEEPA reintegrados
    ($526M + $260M en costo, -$339M en ingresos de energía), reversión de $475M de créditos regulatorios,
    plan 2025 del CEO (423,743,904 acciones; 12 tramos), acciones en circulación al 15-oct-2026 (3,952,757,946),
    guía de capex 2026 (más de $20 mil millones).
  - 8-K del 2-oct-2026 (entregas 3T26) y 8-K del 29-sep-2026 (líneas de crédito por $30 mil millones, sin uso).
  - Yahoo Finance chart API: cierres al 9-nov-2026 (TSLA $378.05, GM, F, TM, GOOGL; 1211.HK HK$72.45),
    cierres de fin de trimestre, ^TNX 4.864%, USD/JPY 158.05, USD/CNY 6.6704, USD/HKD 7.843.
  - stockanalysis.com (9-nov-2026): consenso TSLA (PT promedio $413.10, 44 analistas; ingresos FY26 $107.86B,
    FY27 $122.46B; EPS FY26 $1.72, FY27 $2.16) y EPS 2027 de los comparables.
  - Waymo: ronda de $16 mil millones a $126 mil millones (feb-2026). Figure AI: Serie C a $39 mil millones (sep-2025).

Convenciones del DCF (las mismas que el informe anterior y META):
  - 5 años explícitos (año 1 = FY2027); crecimiento, margen de OCF y capex/ingresos interpolados en línea recta.
  - FCF = ingresos x margen de OCF - capex; el capex del año 1 va en dólares.
  - Descuento a fin de año; VT = FCF5 x (1+g)/(WACC-g) descontado 5 años.
  - Equity = EV + caja neta + inversiones no operativas (SpaceX, bitcoin); por acción = equity / 3,541M diluidas.
    Las 423.7M acciones restringidas del plan 2025 del CEO no entran: solo se ganan con capitalización >= $2 billones.
"""
import json, os

def lin(a, b, n=5):
    return [a + (b - a) * i / (n - 1) for i in range(n)]

R = {}
TAX = 0.22      # tasa para llevar partidas antes de impuestos a netas (la conciliación de Tesla implica ~22%)

# ---------------------------------------------------------------------------
# 1) DATOS TRIMESTRALES (miles de millones de USD; acciones en millones)
# ---------------------------------------------------------------------------
q      = ["4T23", "1T24", "2T24", "3T24", "4T24", "1T25", "2T25", "3T25", "4T25", "1T26", "2T26", "3T26"]
rev    = [25.167, 21.301, 25.500, 25.182, 25.707, 19.335, 22.496, 28.095, 24.901, 22.387, 28.236, 28.046]
gp     = [4.438, 3.696, 4.578, 4.997, 4.179, 3.153, 3.878, 5.054, 5.009, 4.720, 4.751, 5.494]
opinc  = [2.064, 1.171, 1.605, 2.717, 1.583, 0.399, 0.923, 1.624, 1.409, 0.941, 0.398, 0.718]
ni     = [7.928, 1.390, 1.400, 2.173, 2.128, 0.409, 1.172, 1.373, 0.840, 0.477, 1.114, 0.787]   # atribuible, 2024 reexpresado
credit = [0.433, 0.442, 0.890, 0.739, 0.692, 0.595, 0.439, 0.417, 0.542, 0.380, 0.146, 0.113]
restr  = [0.000, 0.000, 0.622, 0.055, 0.007, 0.094, 0.000, 0.238, 0.162, 0.000, 0.000, 0.000]
ebitda = [3.953, 3.384, 3.674, 4.665, 4.333, 2.814, 3.401, 4.227, 4.154, 3.668, 3.273, 3.900]   # Adjusted EBITDA de Tesla
dig    = [0.000, -0.335, 0.100, -0.007, -0.347, 0.125, -0.284, -0.080, 0.307, 0.222, 0.112, -0.288]  # (ganancia) pérdida bitcoin
# 4T23: liberación de reserva de valuación de impuestos diferidos (+$5.93B, extraordinaria)
spx_net = {"2T26": -0.763, "3T26": 0.108}       # SpaceX (ganancia) pérdida, neta (cifra de Tesla)
tax_it  = {"4T23": -5.927, "2T26": -0.274, "3T26": 0.044}       # partidas impositivas (cifra de Tesla)
tariff  = {"3T26": 0.526 + 0.260 - 0.339}       # reintegro de aranceles IEEPA, neto (10-Q)
ocf    = [4.370, 0.242, 3.612, 6.255, 4.814, 2.156, 2.540, 6.238, 3.813, 3.937, 4.697, 6.263]
capex  = [2.307, 2.777, 2.272, 3.513, 2.780, 1.492, 2.394, 2.248, 2.393, 2.493, 5.789, 4.732]
dil    = {"3T24": 3497, "4T24": 3517, "1T25": 3521, "2T25": 3519, "3T25": 3526, "4T25": 3539,
          "1T26": 3538, "2T26": 3540, "3T26": 3541}
cashinv = {"3T24": 33.648, "4T24": 36.563, "1T25": 36.996, "2T25": 36.782, "3T25": 41.647, "4T25": 44.059,
           "1T26": 44.743, "2T26": 43.524, "3T26": 45.447}
debt    = {"3T24": 2.291 + 5.405, "4T24": 2.456 + 5.757, "1T25": 2.237 + 5.292, "2T25": 2.040 + 5.180,
           "3T25": 1.924 + 5.778, "4T25": 1.640 + 6.736, "1T26": 1.447 + 7.782, "2T26": 1.418 + 7.924,
           "3T26": 1.387 + 8.136}             # deuda + leasing financiero (corriente + no corriente, sin duplicar)
digital = {"3T24": 0.729, "4T24": 1.076, "1T25": 0.951, "2T25": 1.235, "3T25": 1.315, "4T25": 1.008,
           "1T26": 0.786, "2T26": 0.674, "3T26": 0.962}
spacex_fv = {"1T26": 2.002, "2T26": 3.007, "3T26": 2.865}     # 2T26 = costo + ganancia de $1,005M
qe_px = {"3T24": 261.63, "4T24": 403.84, "1T25": 259.16, "2T25": 317.66, "3T25": 444.72, "4T25": 449.72,
         "1T26": 371.75, "2T26": 420.60, "3T26": 354.81}

# Núcleo "sin créditos ni extraordinarios"
core_ebitda = [e - c + r - tariff.get(lab, 0) for lab, e, c, r in zip(q, ebitda, credit, restr)]
core_ni = []
for i, lab in enumerate(q):
    x = ni[i] + dig[i] * (1 - TAX) + spx_net.get(lab, 0) + tax_it.get(lab, 0)
    x += (restr[i] - credit[i] - tariff.get(lab, 0)) * (1 - TAX)
    core_ni.append(x)

def ttm(arr, lab):
    i = q.index(lab)
    return sum(arr[i - 3:i + 1])

R["quarters"] = {}
for i, lab in enumerate(q):
    R["quarters"][lab] = {"rev": rev[i], "gm": round(gp[i] / rev[i] * 100, 1), "op_m": round(opinc[i] / rev[i] * 100, 1),
                          "credit": credit[i], "credit_pct_op": round(credit[i] / opinc[i] * 100, 0),
                          "core_ebitda": round(core_ebitda[i], 3), "core_ni": round(core_ni[i], 3),
                          "ocf": ocf[i], "capex": capex[i], "fcf": round(ocf[i] - capex[i], 3),
                          "capex_pct": round(capex[i] / rev[i] * 100, 1)}
R["yoy_rev"] = {lab: round((rev[i] / rev[i - 4] - 1) * 100, 1) for i, lab in enumerate(q) if i >= 4}

T = {lab: {"rev": ttm(rev, lab), "opinc": ttm(opinc, lab), "ni": ttm(ni, lab), "credit": ttm(credit, lab),
           "core_ebitda": ttm(core_ebitda, lab), "core_ni": ttm(core_ni, lab), "ebitda": ttm(ebitda, lab),
           "ocf": ttm(ocf, lab), "capex": ttm(capex, lab)} for lab in q[3:]}  # TTM desde 3T24
for lab, t in T.items():
    t["fcf"] = t["ocf"] - t["capex"]
    t["op_m"] = t["opinc"] / t["rev"] * 100
    t["ocf_m"] = t["ocf"] / t["rev"] * 100
    t["credit_share_op"] = t["credit"] / t["opinc"] * 100
R["ttm"] = {lab: {k: round(v, 3) for k, v in t.items()} for lab, t in T.items() if lab in ("4T24", "3T25", "2T26", "3T26")}

# ---------------------------------------------------------------------------
# 2) TRIMESTRE 3T26 — autos, créditos, energía
# ---------------------------------------------------------------------------
deliv = {"3T25": 497099, "2T26": 480126, "3T26": 486532}
lease = {"3T25": 10230, "2T26": 7580, "3T26": 6911}
auto_sales = {"3T25": 20.359, "2T26": 20.006, "3T26": 20.094}
auto_cogs_sales = {"3T25": 17.365, "2T26": 16.866, "3T26": 16.570}
A = {}
for lab in deliv:
    cash_units = deliv[lab] - lease[lab]
    A[lab] = {"asp": round(auto_sales[lab] * 1e9 / cash_units), "cost_unit": round(auto_cogs_sales[lab] * 1e9 / cash_units)}
auto_rev, auto_cogs = 20.560, 16.754
Q = {"deliv_yoy": (486532 / 497099 - 1) * 100, "prod": 464391, "prod_yoy": (464391 / 447450 - 1) * 100,
     "deliv_qoq": (486532 / 480126 - 1) * 100,
     "auto_gm": (auto_rev - auto_cogs) / auto_rev * 100,
     "auto_gm_ex_credit": (auto_rev - auto_cogs - 0.113) / (auto_rev - 0.113) * 100,
     "auto_gm_ex_credit_ex_tariff": (auto_rev - auto_cogs - 0.113 - 0.260) / (auto_rev - 0.113) * 100,
     "credit_gross": 0.113 + 0.475, "credit_9m": 0.380 + 0.146 + 0.113, "credit_9m_prev": 0.595 + 0.439 + 0.417,
     "energy_gm": (2.881 - 1.927) / 2.881 * 100, "energy_gp": 2.881 - 1.927,
     "energy_gm_ex_tariff": ((2.881 + 0.339) - (1.927 + 0.526)) / (2.881 + 0.339) * 100,
     "energy_gp_ex_tariff": (2.881 + 0.339) - (1.927 + 0.526),
     "energy_gp_prev": 3.415 - 2.342, "energy_gm_prev": (3.415 - 2.342) / 3.415 * 100,
     "services_gp": 4.605 - 3.871, "services_gm": (4.605 - 3.871) / 4.605 * 100,
     "op_m": 0.718 / 28.046 * 100, "op_m_prev": 1.624 / 28.095 * 100,
     "opinc_yoy": (0.718 / 1.624 - 1) * 100, "rd_yoy": (2.761 / 1.630 - 1) * 100,
     "sbc": 1.165, "ceo_award_sbc": 0.275, "opinc_ex_credit": 0.718 - 0.113,
     "opinc_ex_credit_tariff": 0.718 - 0.113 - 0.447,
     "fcf": 6.263 - 4.732, "storage_gwh": 13.7, "storage_gwh_prev": 12.5, "fsd_subs": 1.74, "fsd_subs_prev": 1.04,
     "inv_days": 11, "inventory": 14.092}
Q["fsd_yoy"] = (1.74 / 1.04 - 1) * 100
R["q3"] = {k: round(v, 2) for k, v in Q.items()}
R["auto_units"] = A

# ---------------------------------------------------------------------------
# 3) BALANCE Y ACCIONES
# ---------------------------------------------------------------------------
PRICE = 378.05            # cierre 9-nov-2026
PRICE_PRE = 386.47        # cierre 21-oct-2026 (reporte después del cierre)
PRICE_POST = 374.58       # cierre 22-oct-2026
PRICE_SEP = 311.21        # cierre 31-jul-2026, precio del informe anterior
TSY10 = 4.864
SH = 3.541                # diluidas (miles de millones) del 3T26
SH_OUT = 3.952758         # en circulación al 15-oct-2026 (incluye 423.7M restringidas del plan 2025)
AWARD = 0.423744
B = {"cash": cashinv["3T26"], "debt": debt["3T26"], "debt_principal": 9.284, "fin_leases": 0.256,
     "digital": digital["3T26"], "spacex": spacex_fv["3T26"], "equity": 89.289, "inventory": 14.092,
     "credit_lines": 30.0, "china_wc": 5.966, "recourse": 0.002}
B["net_cash"] = B["cash"] - B["debt"]
B["non_op"] = B["digital"] + B["spacex"]
B["net_cash_plus"] = B["net_cash"] + B["non_op"]
B["net_cash_2t26"] = cashinv["2T26"] - debt["2T26"]
B["mcap_out"] = PRICE * SH_OUT
B["mcap_dil"] = PRICE * SH
B["award_dilution"] = AWARD / (SH_OUT - AWARD) * 100
B["award_2t_px"] = 2000 / SH_OUT
R["bal"] = {k: round(v, 3) for k, v in B.items()}

# Capex / FCF
C = {"capex_9m": 2.493 + 5.789 + 4.732, "guide": 20.0}
C["capex_q4_impl"] = C["guide"] - C["capex_9m"]
C["capex_2025"] = 1.492 + 2.394 + 2.248 + 2.393
C["guide_vs_2025"] = (C["guide"] / C["capex_2025"] - 1) * 100
C["fcf_ttm"] = T["3T26"]["fcf"]
C["fcf_ttm_prev"] = T["3T25"]["fcf"]
C["capex_ttm_pct"] = T["3T26"]["capex"] / T["3T26"]["rev"] * 100
C["ocf_9m"] = 3.937 + 4.697 + 6.263
C["ocf_9m_m"] = C["ocf_9m"] / (22.387 + 28.236 + 28.046) * 100
C["wc_q3"] = -0.565 - 0.313 + 0.040 - 1.818 + 3.991 + 1.255     # variación de capital de trabajo del 3T26
R["capex"] = {k: round(v, 3) for k, v in C.items()}

# ---------------------------------------------------------------------------
# 4) DCF DEL NEGOCIO ACTUAL (autos + energía + servicios) — año 1 = FY2027
#    El capex del año 1 incluye toda la inversión guiada (también la de IA/Optimus/Cybercab): el negocio actual
#    la paga. Por eso el SOTP no vuelve a restar esa inversión.
# ---------------------------------------------------------------------------
def dcf(rev1, g2_5, ocf_m, capm5, cap1, wacc, g, net_plus, shares):
    revs = [rev1]
    for x in lin(g2_5[0], g2_5[1], 4):
        revs.append(revs[-1] * (1 + x))
    om = lin(*ocf_m)
    cm = lin(cap1 / rev1, capm5)
    capx = [cap1] + [r * c for r, c in zip(revs[1:], cm[1:])]
    fcf = [r * o - c for r, o, c in zip(revs, om, capx)]
    pv = sum(f / (1 + wacc) ** (i + 1) for i, f in enumerate(fcf))
    tv = fcf[-1] * (1 + g) / (wacc - g)
    pvtv = tv / (1 + wacc) ** 5
    ev = pv + pvtv
    return {"fv": (ev + net_plus) / shares, "tv_share": pvtv / ev, "fcf": fcf, "revs": revs, "ev": ev,
            "capex": capx, "pv_explicit": pv}

REV0 = 107.86      # consenso FY2026 (9M real $78.67B + 4T implícito $29.19B)
REV1 = 122.46      # consenso FY2027 (+13.5%)
ERP = 5.0
WACC_BASE = 0.11   # misma tasa del informe anterior (beta implícita ~1.23 sobre el 10 años de 4.86%)
cases = {
    "Bear": dict(g2_5=(0.06, 0.03), ocf=(0.16, 0.17), capm5=0.08, cap1=20.0, wacc=WACC_BASE + 0.01, g=0.025),
    "Base": dict(g2_5=(0.10, 0.06), ocf=(0.18, 0.22), capm5=0.09, cap1=24.0, wacc=WACC_BASE, g=0.03),
    "Bull": dict(g2_5=(0.14, 0.08), ocf=(0.19, 0.25), capm5=0.09, cap1=26.0, wacc=WACC_BASE - 0.01, g=0.035),
}
R["wacc"] = {"rf": TSY10, "beta_impl": round((WACC_BASE * 100 - TSY10) / ERP, 2), "base": WACC_BASE * 100,
             "capm_beta_179": round(TSY10 + 1.79 * ERP, 2)}
R["rev0"], R["rev1"], R["rev1_growth"] = REV0, REV1, round((REV1 / REV0 - 1) * 100, 1)
R["rev0_q4_impl"] = round(REV0 - (22.387 + 28.236 + 28.046), 3)
R["dcf"] = {}
for k, c in cases.items():
    r = dcf(REV1, c["g2_5"], c["ocf"], c["capm5"], c["cap1"], c["wacc"], c["g"], B["net_cash_plus"], SH)
    R["dcf"][k] = {"fv": round(r["fv"], 2), "tv_share": round(r["tv_share"] * 100, 1), "fcf1": round(r["fcf"][0], 2),
                   "fcf5": round(r["fcf"][-1], 2), "rev5": round(r["revs"][-1], 1), "wacc": round(c["wacc"] * 100, 1),
                   "g": round(c["g"] * 100, 1), "capm1": round(c["cap1"] / REV1 * 100, 1), "ev": round(r["ev"], 1),
                   "fcf": [round(x, 2) for x in r["fcf"]], "revs": [round(x, 1) for x in r["revs"]],
                   "pv_explicit": round(r["pv_explicit"], 2)}
fvs = {k: R["dcf"][k]["fv"] for k in cases}
R["dcf_prob"] = round(0.25 * fvs["Bear"] + 0.45 * fvs["Base"] + 0.30 * fvs["Bull"], 2)
R["dcf_simple"] = round(sum(fvs.values()) / 3, 2)
b = cases["Base"]
waccs = [0.10, 0.105, 0.11, 0.115, 0.12]
gs = [0.02, 0.025, 0.03, 0.035, 0.04]
gfn = lambda w, gg: dcf(REV1, b["g2_5"], b["ocf"], b["capm5"], b["cap1"], w, gg, B["net_cash_plus"], SH)["fv"]
R["grid"] = {"waccs": [w * 100 for w in waccs], "gs": [x * 100 for x in gs],
             "vals": [[round(gfn(w, gg), 2) for gg in gs] for w in waccs]}
base_r = dcf(REV1, b["g2_5"], b["ocf"], b["capm5"], b["cap1"], b["wacc"], b["g"], B["net_cash_plus"], SH)
R["dcf_base_ev"] = round(base_r["ev"], 2)
R["dcf_base_equity"] = round(base_r["ev"] + B["net_cash_plus"], 2)
# Base con la cuenta de acciones del informe anterior (en circulación, incluye el plan 2025)
R["dcf_base_out_shares"] = round((base_r["ev"] + B["net_cash_plus"]) / SH_OUT, 2)

def solve(fn, lo, hi, target, n=100):
    for _ in range(n):
        mid = (lo + hi) / 2
        if (fn(mid) - target) * (fn(lo) - target) <= 0: hi = mid
        else: lo = mid
    return (lo + hi) / 2
f_ocf = lambda m: dcf(REV1, b["g2_5"], (b["ocf"][0], m), b["capm5"], b["cap1"], b["wacc"], b["g"], B["net_cash_plus"], SH)["fv"]
f_g = lambda gg: dcf(REV1, (gg, gg), b["ocf"], b["capm5"], b["cap1"], b["wacc"], b["g"], B["net_cash_plus"], SH)["fv"]
ocf5_req = solve(f_ocf, 0.20, 1.5, PRICE)
g_req = solve(f_g, 0.0, 1.0, PRICE)
rev5_req = REV1 * (1 + g_req) ** 4
R["inverso"] = {"ocf5": round(ocf5_req * 100, 1), "g2_5": round(g_req * 100, 1), "rev5": round(rev5_req, 0)}

# ---------------------------------------------------------------------------
# 5) SOTP: negocio actual + opcionalidades ponderadas por probabilidad, con la caja neta explícita
# ---------------------------------------------------------------------------
WAYMO, FIGURE = 126.0, 39.0
P = {"Bear": (0.25, 0.15), "Base": (0.50, 0.30), "Bull": (1.00, 0.60)}     # (robotaxi, optimus)
R["sotp"] = {}
for k, (pr, po) in P.items():
    core = dcf(REV1, cases[k]["g2_5"], cases[k]["ocf"], cases[k]["capm5"], cases[k]["cap1"], cases[k]["wacc"],
               cases[k]["g"], 0.0, 1.0)["ev"]
    rt, op = pr * WAYMO, po * FIGURE
    eq = core + rt + op + B["net_cash"] + B["non_op"]
    R["sotp"][k] = {"core_ev": round(core, 2), "robotaxi": round(rt, 2), "optimus": round(op, 2),
                    "net_cash": round(B["net_cash"], 3), "non_op": round(B["non_op"], 3), "equity": round(eq, 2),
                    "fv": round(eq / SH, 2), "core_ps": round(core / SH, 2), "rt_ps": round(rt / SH, 2),
                    "op_ps": round(op / SH, 2), "cash_ps": round((B["net_cash"] + B["non_op"]) / SH, 2),
                    "p_rt": pr, "p_op": po}
sb = R["sotp"]["Base"]
# Sensibilidad: robotaxi 25%-150% de Waymo con el resto fijo
R["sotp_sens"] = {f"{int(p * 100)}%": round((sb["core_ev"] + p * WAYMO + sb["optimus"] + B["net_cash_plus"]) / SH, 2)
                  for p in (0.25, 0.5, 1.0, 1.5)}
# SOTP inverso: cuánto tienen que valer las opcionalidades para justificar el precio
implied_opt = PRICE * SH - (sb["core_ev"] + B["net_cash_plus"])
R["sotp_inverso"] = {"mcap_dil": round(PRICE * SH, 1), "implied_opt": round(implied_opt, 1),
                     "x_waymo": round(implied_opt / WAYMO, 2), "x_waymo_figure": round(implied_opt / (WAYMO + FIGURE), 2),
                     "opt_share_of_price": round(implied_opt / (PRICE * SH) * 100, 1)}

# ---------------------------------------------------------------------------
# 6) COMPARABLES — P/E 2027 (año calendario; Toyota usa el año fiscal a mar-2028)
# ---------------------------------------------------------------------------
JPY, CNY, HKD = 158.05, 6.6704, 7.843
peers = {
    "TM":    (218.51, 10 * 352.07 / JPY),                  # ADR = 10 acciones; EPS FY mar-28 en yenes
    "GM":    (89.65, 14.80),
    "F":     (12.52, 1.89),
    "BYD":   (72.45 * CNY / HKD, 5.20),                    # 1211.HK en HKD, EPS en CNY
    "GOOGL": (288.15, 15.44),
}
EPS27, EPS26 = 2.16, 1.72
pe = {k: v[0] / v[1] for k, v in peers.items()}
def avg(keys): return sum(pe[k] for k in keys) / len(keys)
all5 = list(pe)
sets = {"Los cinco": all5, "Solo autos (sin GOOGL)": ["TM", "GM", "F", "BYD"],
        "Sin GM ni F": ["TM", "BYD", "GOOGL"], "Sin GOOGL ni F/GM": ["TM", "BYD"]}
R["comps"] = {"pe": {k: round(v, 2) for k, v in pe.items()}, "eps27": EPS27,
              "implied": {k: round(v * EPS27, 2) for k, v in pe.items()},
              "sets": {n: {"pe": round(avg(ks), 2), "fv": round(avg(ks) * EPS27, 2)} for n, ks in sets.items()},
              "tsla_pe27": round(PRICE / EPS27, 1), "tsla_pe26": round(PRICE / EPS26, 1),
              "eps27_growth": round((EPS27 / EPS26 - 1) * 100, 1), "tm_eps_usd": round(peers["TM"][1], 2),
              "byd_px_cny": round(peers["BYD"][0], 2)}
COMPS = R["comps"]["sets"]["Los cinco"]["fv"]

# ---------------------------------------------------------------------------
# 7) REVERSIÓN — múltiplos PROPIOS sobre resultados SIN créditos regulatorios ni extraordinarios
#    EV/EBITDA núcleo (método) y P/E núcleo (control). Ventana: 8 cierres trimestrales.
# ---------------------------------------------------------------------------
def ev_at(lab, px):
    return px * dil[lab] / 1000 - cashinv[lab] + debt[lab] - digital[lab] - spacex_fv.get(lab, 0)
def window(labs):
    out = []
    for lab in labs:
        e = T[lab]["core_ebitda"]; n = T[lab]["core_ni"]
        eps = n / (dil[lab] / 1000)
        out.append({"q": lab, "px": qe_px[lab], "ev": round(ev_at(lab, qe_px[lab]), 1), "ebitda": round(e, 3),
                    "ev_ebitda": round(ev_at(lab, qe_px[lab]) / e, 2), "eps": round(eps, 3), "pe": round(qe_px[lab] / eps, 1)})
    return out
def value_from(mult, lab):
    return (mult * T[lab]["core_ebitda"] + cashinv[lab] - debt[lab] + digital[lab] + spacex_fv.get(lab, 0)) / (dil[lab] / 1000)
W8 = ["4T24", "1T25", "2T25", "3T25", "4T25", "1T26", "2T26", "3T26"]
W4 = W8[-4:]
w8, w4 = window(W8), window(W4)
m8 = sum(x["ev_ebitda"] for x in w8) / 8
m4 = sum(x["ev_ebitda"] for x in w4) / 4
pe8 = sum(x["pe"] for x in w8) / 8
eps_core_now = T["3T26"]["core_ni"] / SH
R["rev"] = {"window": w8, "m8": round(m8, 2), "m4": round(m4, 2), "core_ebitda_ttm": round(T["3T26"]["core_ebitda"], 3),
            "fv": round(value_from(m8, "3T26"), 2), "fv4": round(value_from(m4, "3T26"), 2),
            "pe8": round(pe8, 1), "eps_core_ttm": round(eps_core_now, 3), "fv_pe": round(pe8 * eps_core_now, 2),
            "ev_ebitda_now": round(ev_at("3T26", PRICE) / T["3T26"]["core_ebitda"], 1),
            "pe_now": round(PRICE / eps_core_now, 0),
            "minmax": [round(value_from(min(x["ev_ebitda"] for x in w8), "3T26"), 2),
                       round(value_from(max(x["ev_ebitda"] for x in w8), "3T26"), 2)],
            "eps_gaap_ttm": round(sum([0.24, 0.13, 0.32, 0.22]), 2), "eps_nongaap_ttm": round(sum([0.50, 0.41, 0.33, 0.48]), 2),
            "core_ebitda_yoy": round((T["3T26"]["core_ebitda"] / T["3T25"]["core_ebitda"] - 1) * 100, 1)}
REV = R["rev"]["fv"]

# ---------------------------------------------------------------------------
# 8) CONSENSO y BLEND — 7.5% DCF + 7.5% SOTP + 25% comparables + 35% reversión + 25% consenso
# ---------------------------------------------------------------------------
CONS = 413.10
WTS = {"DCF negocio actual": 0.075, "SOTP": 0.075, "Comparables": 0.25, "Reversión": 0.35, "Consenso": 0.25}
methods = {"DCF negocio actual": fvs["Base"], "SOTP": sb["fv"], "Comparables": COMPS, "Reversión": REV, "Consenso": CONS}
blend = sum(methods[k] * WTS[k] for k in WTS)
R["methods"] = {k: round(v, 2) for k, v in methods.items()}
R["weights"] = WTS
R["contrib"] = {k: round(methods[k] * WTS[k], 2) for k in WTS}
R["blend"] = round(blend, 2)
R["blend_vs_price"] = round((blend / PRICE - 1) * 100, 1)
R["method_vs_price"] = {k: round((v / PRICE - 1) * 100, 1) for k, v in methods.items()}
R["blend_simple"] = round(sum(methods.values()) / 5, 2)
# Blend con distintos sets de comparables
R["blend_alt_comps"] = {}
for n, s in R["comps"]["sets"].items():
    mm = dict(methods); mm["Comparables"] = s["fv"]
    bb = sum(mm[k] * WTS[k] for k in WTS)
    R["blend_alt_comps"][n] = {"blend": round(bb, 2), "vs_price": round((bb / PRICE - 1) * 100, 1)}
# Sensibilidad del blend a la ventana de reversión y al P/E núcleo
for tag, val in (("rev4", R["rev"]["fv4"]), ("rev_pe", R["rev"]["fv_pe"])):
    mm = dict(methods); mm["Reversión"] = val
    R["blend_" + tag] = round(sum(mm[k] * WTS[k] for k in WTS), 2)
R["price"] = PRICE
R["reaction"] = round((PRICE_POST / PRICE_PRE - 1) * 100, 1)
R["from_pre"] = round((PRICE / PRICE_PRE - 1) * 100, 1)
R["price_vs_sep"] = round((PRICE / PRICE_SEP - 1) * 100, 1)
R["px_q3_end"] = qe_px["3T26"]
R["px_nov5"] = 343.69
R["px_nov4"] = 385.19

# ---------------------------------------------------------------------------
# 9) EL INFORME ANTERIOR (datos al 2T26, precio $311.21 del 31-jul-2026) Y SU RECONSTRUCCIÓN
#    Publicado: portada con RANGO $13-$425; valor central citado = DCF ponderado 25/45/30 = $92.03.
#    Reconstrucción con la regla nueva: mismos valores de método publicados donde la metodología no cambió
#    (DCF Base $77.77, comparables $24.93, consenso $398.30); SOTP con las mismas probabilidades nuevas sobre los
#    datos de entonces (3,949.5M acciones); reversión recalculada con la regla nueva (EV/EBITDA propio sin créditos,
#    ventana 3T24-2T26, caja y deuda al 2T26).
# ---------------------------------------------------------------------------
SEP = {"bear": 13.33, "base": 77.77, "bull": 178.99, "prob": 92.03, "sotp100": 119.55, "comps": 24.93,
       "rev_vendor": 182.82, "cons": 398.30, "waymo_ps": 31.90, "figure_ps": 9.87, "shares": 3.9495}
R["sep_prob_check"] = round(0.25 * SEP["bear"] + 0.45 * SEP["base"] + 0.30 * SEP["bull"], 2)
sep_sotp = SEP["base"] + P["Base"][0] * SEP["waymo_ps"] + P["Base"][1] * SEP["figure_ps"]
W8s = ["3T24", "4T24", "1T25", "2T25", "3T25", "4T25", "1T26", "2T26"]
w8s = window(W8s)
m8s = sum(x["ev_ebitda"] for x in w8s) / 8
sep_rev = value_from(m8s, "2T26")
sep_methods = {"DCF negocio actual": SEP["base"], "SOTP": sep_sotp, "Comparables": SEP["comps"],
               "Reversión": sep_rev, "Consenso": SEP["cons"]}
sep_blend = sum(sep_methods[k] * WTS[k] for k in WTS)
sep_methods_v = dict(sep_methods); sep_methods_v["Reversión"] = SEP["rev_vendor"]
R["sep"] = {"price": PRICE_SEP, "methods": {k: round(v, 2) for k, v in sep_methods.items()},
            "window": w8s, "m8": round(m8s, 2), "core_ebitda_ttm": round(T["2T26"]["core_ebitda"], 3),
            "blend": round(sep_blend, 2), "blend_vs_price": round((sep_blend / PRICE_SEP - 1) * 100, 1),
            "blend_vendor_rev": round(sum(sep_methods_v[k] * WTS[k] for k in WTS), 2),
            "old_central": SEP["prob"], "old_range": [13, 425]}
R["blend_vs_sep"] = round((blend / sep_blend - 1) * 100, 1)
R["blend_vs_old_central"] = round((blend / SEP["prob"] - 1) * 100, 1)

# Football field
R["ff"] = {"DCF negocio actual": [fvs["Bear"], fvs["Bull"]],
           "SOTP": [R["sotp"]["Bear"]["fv"], R["sotp"]["Bull"]["fv"]],
           "Comparables": [min(R["comps"]["implied"].values()), max(R["comps"]["implied"].values())],
           "Reversión": R["rev"]["minmax"],
           "Consenso": [128.11, 600.0]}

if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resultados.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(R, fh, ensure_ascii=False, indent=1)
    print(json.dumps(R, ensure_ascii=False, indent=1))
