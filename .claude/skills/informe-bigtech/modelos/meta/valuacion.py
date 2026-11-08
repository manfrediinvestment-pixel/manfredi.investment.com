"""
Modelo de valuación META — actualización al 3T 2026 (cierre 30-sep-2026, 8-K del 21-oct-2026, 10-Q del 22-oct-2026).

Correr:  python valuacion.py            (imprime todo y escribe resultados.json al lado)

Fuentes de los números de entrada (verificadas a mano contra el documento original):
  - 8-K Ex. 99.1 del 21-oct-2026 (resultados, segmentos, flujo de caja, balance, guía 4T26, cargo de $9.89B,
    EPS sin el cargo $7.40, clase C).
  - 10-Q del 22-oct-2026 (Nota 5 ventures de centros de datos, Nota 8 pasivos legales, Nota 9 deuda, Nota 10
    compromisos, Nota 12 impuestos, ARPP).
  - 8-K del 29-oct-2026 (preferida convertible obligatoria 6.50%, 250M depositary shares = $12.5B; forward de 40M
    acciones a $622.91875) y 8-K del 5-nov-2026 (bonos por $15.0B; opción de +6M acciones del forward ejercida).
    Prospecto 424B5 del 28-oct-2026: conversión entre 1.3620 y 1.6000 acciones por preferida de $1,000.
  - SEC companyfacts XBRL (series trimestrales: ingresos, operativo, utilidad neta, OCF, capex, leasing financiero).
  - Yahoo Finance chart API: cierres al 6-nov-2026, cierres de fin de trimestre, ^TNX 4.859% al 6-nov-2026.
  - stockanalysis.com (6-nov-2026): PT promedio $850.10 (61 analistas), ingresos FY26 $256.88B / FY27 $312.63B,
    EPS FY26 $29.73 / FY27 $35.59; EPS 2027 de PINS ($2.28) y RDDT ($9.29, 4-nov).

Convenciones del DCF (las mismas que se usan para reproducir el informe anterior):
  - 5 años explícitos; crecimiento, margen de OCF y capex/ingresos interpolados en línea recta del año 1 al 5.
  - FCF = ingresos x (margen de OCF - capex/ingresos); en la versión nueva el capex del año 1 va en dólares.
  - Descuento a fin de año; VT = FCF5 x (1+g)/(WACC-g) descontado 5 años.
  - Equity = EV - deuda neta; por acción = equity / acciones.
Todas las cifras por acción son PREVIAS al dividendo de clase C (que funciona como un split 2x1 desde ene-2027).
"""
import json, os

def lin(a, b, n=5):
    return [a + (b - a) * i / (n - 1) for i in range(n)]

R = {}

# ---------------------------------------------------------------------------
# 1) REPRODUCCIÓN DEL INFORME ANTERIOR (datos al 2T26, precio $556.71 del 31-jul-2026)
#    Publicado: ingresos base TTM $228.25B, crecimiento 20%->10%, OCF 54%->60%, capex 50%->25%,
#    WACC 10%, g 3%, caja neta +$6.60B. Las acciones no estaban declaradas: se despejan del Base.
# ---------------------------------------------------------------------------
def dcf_sep(rev0, g, ocf, capm, wacc, gt, net_cash, shares):
    revs, r = [], rev0
    for x in lin(*g):
        r *= 1 + x
        revs.append(r)
    fcf = [rv * (o - c) for rv, o, c in zip(revs, lin(*ocf), lin(*capm))]
    pv = sum(f / (1 + wacc) ** (i + 1) for i, f in enumerate(fcf))
    pvtv = fcf[-1] * (1 + gt) / (wacc - gt) / (1 + wacc) ** 5
    ev = pv + pvtv
    return (ev + net_cash) / shares, pvtv / ev, fcf[0]

SEP_CASES = {"Bear": ((0.16, 0.06), (0.50, 0.52), (0.55, 0.35), 0.11, 0.025),
             "Base": ((0.20, 0.10), (0.54, 0.60), (0.50, 0.25), 0.10, 0.03),
             "Bull": ((0.24, 0.13), (0.57, 0.64), (0.45, 0.18), 0.09, 0.035)}
SEP_PUB = {"Bear": 208.93, "Base": 688.32, "Bull": 1338.60}
base_ev_share = dcf_sep(228.25, *SEP_CASES["Base"][:4], SEP_CASES["Base"][4], 6.60, 1.0)[0]
sep_shares = base_ev_share / 688.32           # acciones implícitas en el Base publicado
R["sep_shares_implicitas"] = round(sep_shares, 4)
R["sep_repro"] = {}
for k, c in SEP_CASES.items():
    fv, tv, f1 = dcf_sep(228.25, c[0], c[1], c[2], c[3], c[4], 6.60, sep_shares)
    R["sep_repro"][k] = {"modelo": round(fv, 2), "publicado": SEP_PUB[k], "dif_pct": round((fv / SEP_PUB[k] - 1) * 100, 1),
                         "tv_share": round(tv * 100, 1), "fcf1": round(f1, 1)}
SEP_METHODS = {"DCF Base": 688.32, "Comparables": 852.00, "Reversión": 814.95, "Consenso": 834.50}
W4 = {"DCF Base": 0.15, "Comparables": 0.25, "Reversión": 0.35, "Consenso": 0.25}
R["sep_blend_simple"] = round(sum(SEP_METHODS.values()) / 4, 2)              # 797.44 publicado
R["sep_blend_ponderado_regla_actual"] = round(sum(SEP_METHODS[k] * W4[k] for k in W4), 2)
SEP_PRICE = 556.71

# ---------------------------------------------------------------------------
# 2) DATOS TRIMESTRALES (miles de millones de USD)
# ---------------------------------------------------------------------------
PRICE = 610.15              # cierre 6-nov-2026
PRICE_PRE = 697.52          # cierre 21-oct-2026 (reporte después del cierre)
PRICE_POST = 648.85         # cierre 22-oct-2026
TSY10 = 4.859

q = ["3T24", "4T24", "1T25", "2T25", "3T25", "4T25", "1T26", "2T26", "3T26"]
rev   = [40.589, 48.385, 42.314, 47.516, 51.242, 59.893, 56.311, 60.801, 64.601]
opinc = [17.350, 23.364, 17.555, 20.441, 20.535, 24.745, 22.872, 18.775, 12.988]
ni    = [15.688, 20.838, 16.644, 18.337, 2.709, 22.768, 26.773, 15.848, 9.860]
ocf   = [24.724, 27.988, 24.026, 25.561, 29.999, 36.214, 32.226, 31.862, 32.786]
ppe   = [8.258, 14.425, 12.941, 16.538, 18.829, 21.383, 18.997, 30.116, 33.942]
flp   = [0.944, 0.411, 0.751, 0.474, 0.545, 0.754, 0.843, 0.962, 0.964]
eps   = [6.03, 8.02, 6.43, 7.14, 1.05, 8.88, 10.44, 6.18, 3.83]          # diluido GAAP reportado
dil   = [2.602, 2.598, 2.590, 2.570, 2.572, 2.564, 2.564, 2.565, 2.573]   # diluidas (XBRL; 3T24 y 4T derivadas de NI/EPS)
rd    = [11.177, 12.180, 12.150, 12.942, 15.144, 17.135, 17.699, 21.656, 20.054]
foa_oi = {"3T25": 24.967, "3T26": 17.117}
rl_oi  = {"3T25": -4.432, "3T26": -4.129}

# Partidas no recurrentes (efecto en utilidad neta, después de impuestos)
#   3T25: cargo impositivo discreto de $15.93B (OBBBA)                         -> +15.93
#   1T26: beneficio impositivo discreto de $8.03B (CAMT, Notice 2026-7)          -> -8.03
#   2T26: cargos legales $2.40B + indemnizaciones $1.18B (antes de impuestos). Indemnizaciones al 21%; el cargo legal
#         con la misma relación neta/bruta que Meta declaró para el acuerdo con los fiscales en el 3T26
#         (EPS +$3.57 x 2,573M acciones / $9.89B = 92.9% -> crédito fiscal efectivo de 7.1%).
#   3T26: acuerdo con los fiscales generales $9.89B -> EPS +$3.57 (cifra de Meta)
LEGAL_NET = 3.57 * 2.573 / 9.89
adj_ni = {"3T25": 15.93, "1T26": -8.03, "2T26": 1.18 * 0.79 + 2.40 * LEGAL_NET, "3T26": 3.57 * 2.573}
core_ni = [n + adj_ni.get(lab, 0) for lab, n in zip(q, ni)]
core_eps = [e + adj_ni.get(lab, 0) / sh for lab, e, sh in zip(q, eps, dil)]   # EPS reportado + ajuste
core_eps[q.index("3T25")] = 7.25     # Meta: EPS sin el cargo impositivo
core_eps[q.index("3T26")] = 7.40     # Meta: EPS sin el cargo legal
R["legal_net_ratio"] = round(LEGAL_NET, 4)
R["quarters"] = {lab: {"rev": rev[i], "opinc": opinc[i], "op_m": round(opinc[i] / rev[i] * 100, 1),
                       "ni": ni[i], "core_ni": round(core_ni[i], 3), "eps": eps[i], "core_eps": round(core_eps[i], 2),
                       "ocf": ocf[i], "ocf_m": round(ocf[i] / rev[i] * 100, 1),
                       "capex": round(ppe[i] + flp[i], 3), "fcf": round(ocf[i] - ppe[i] - flp[i], 3),
                       "rd_pct": round(rd[i] / rev[i] * 100, 1)} for i, lab in enumerate(q)}
R["yoy_rev"] = {lab: round((rev[i] / rev[i - 4] - 1) * 100, 1) for i, lab in enumerate(q) if i >= 4}

ttm = lambda a: sum(a[-4:])
T = {"rev": ttm(rev), "opinc": ttm(opinc), "ni": ttm(ni), "core_ni": ttm(core_ni), "ocf": ttm(ocf),
     "capex": ttm(ppe) + ttm(flp), "eps_gaap": ttm(eps), "eps_core": ttm(core_eps), "rd": ttm(rd)}
T["fcf"] = T["ocf"] - T["capex"]
T["op_m"] = T["opinc"] / T["rev"] * 100
T["opinc_ex_legal"] = T["opinc"] + 9.89 + 2.40 + 1.18
T["op_m_ex"] = T["opinc_ex_legal"] / T["rev"] * 100
T["ocf_m"] = T["ocf"] / T["rev"] * 100
T["fcf_m"] = T["fcf"] / T["rev"] * 100
T["fcf_prev"] = sum(ocf[-8:-4]) - sum(ppe[-8:-4]) - sum(flp[-8:-4])   # TTM al 3T25
R["ttm"] = {k: round(v, 3) for k, v in T.items()}

# Trimestre 3T26 vs 3T25
Q = {"rev_yoy": (64.601 / 51.242 - 1) * 100, "ads_yoy": (63.061 / 50.082 - 1) * 100,
     "other_yoy": (1.097 / 0.690 - 1) * 100, "rl_rev_yoy": (0.443 / 0.470 - 1) * 100,
     "opinc_ex": 12.988 + 9.89, "op_m_ex": (12.988 + 9.89) / 64.601 * 100, "op_m": 12.988 / 64.601 * 100,
     "opinc_ex_yoy": ((12.988 + 9.89) / 20.535 - 1) * 100,
     "foa_m": 17.117 / 64.158 * 100, "foa_m_ex": (17.117 + 9.89) / 64.158 * 100, "foa_m_prev": 24.967 / 50.772 * 100,
     "core_eps_yoy": (7.40 / 7.25 - 1) * 100, "gaap_eps_yoy": (3.83 / 1.05 - 1) * 100,
     "costs_yoy": (51.613 / 30.707 - 1) * 100, "costs_ex_yoy": ((51.613 - 9.89) / 30.707 - 1) * 100,
     "arpp": 17.72, "arpp_yoy": 23, "dap": 3.64, "imp": 10, "ppa": 14,
     "fcf": 32.786 - 33.942 - 0.964, "capex": 33.942 + 0.964,
     "rl_9m": -12.775, "rl_q4_impl_lo": -18 + 12.775, "rl_q4_impl_hi": -19 + 12.775}
R["q3"] = {k: round(v, 2) for k, v in Q.items()}

# Guía
G = {"q4_lo": 73.0, "q4_hi": 76.0, "q4_cons_pre": None,
     "exp_lo": 175.0, "exp_hi": 179.0, "exp_ex_lo": 175.0 - 9.9, "exp_ex_hi": 179.0 - 9.9,
     "capex_lo": 135.0, "capex_hi": 145.0, "capex_9m": 83.055 + 2.769}
G["q4_mid"] = (G["q4_lo"] + G["q4_hi"]) / 2
G["q4_mid_yoy"] = (G["q4_mid"] / 59.893 - 1) * 100
G["q4_lo_yoy"] = (G["q4_lo"] / 59.893 - 1) * 100
G["q4_hi_yoy"] = (G["q4_hi"] / 59.893 - 1) * 100
G["fy26_rev_mid"] = 181.712 + G["q4_mid"]
G["fy26_rev_vs_cons"] = (G["fy26_rev_mid"] / 256.88 - 1) * 100
G["q4_cons_implied"] = 256.88 - 181.712                     # consenso FY26 menos 9M real
G["q4_capex_lo"] = G["capex_lo"] - G["capex_9m"]
G["q4_capex_hi"] = G["capex_hi"] - G["capex_9m"]
G["fy26_opinc_mid"] = G["fy26_rev_mid"] - (G["exp_lo"] + G["exp_hi"]) / 2
G["fy26_opinc_mid_ex"] = G["fy26_opinc_mid"] + 9.89
G["fy25_opinc"] = 83.276
G["fy26_capex_yoy"] = (140.0 / (69.691 + 2.524) - 1) * 100
R["guide"] = {k: (round(v, 3) if isinstance(v, float) else v) for k, v in G.items()}

# ---------------------------------------------------------------------------
# 3) BALANCE Y FINANCIAMIENTO
# ---------------------------------------------------------------------------
B = dict(cash=11.222, mkt=71.227, debt_face=84.000, debt_noncur=80.922, debt_cur=2.747, op_lease=2.522 + 28.651,
         legal_cur=11.577, legal_noncur=8.304, ag_accrued=11.89, ag_contingent=5.3, restricted=0.597 + 12.535,
         equity=272.386, ppe=253.222, ppe_dec=176.400, jv_rvg=41.493, jv_leases=18.476, jv_funding=3.703,
         jv_carrying=4.732, unc_leases=355.73, commitments=454.52, commit_2027=121.41)
B["cash_mkt"] = B["cash"] + B["mkt"]
B["debt_carrying"] = B["debt_noncur"] + B["debt_cur"]       # LongTermDebt no corriente + corriente (sin duplicar)
B["net_debt_sep_def"] = B["debt_carrying"] - B["cash_mkt"]     # misma definición que el informe anterior
B["legal_total"] = B["legal_cur"] + B["legal_noncur"]
B["jv_total"] = B["jv_carrying"] + B["jv_leases"] + B["jv_funding"] + B["jv_rvg"]
B["ebitda_ttm_ex"] = T["opinc_ex_legal"] + (5.411 + 5.999 + 6.356 + 7.154)
B["debt_ebitda"] = B["debt_carrying"] / B["ebitda_ttm_ex"]
B["ppe_growth"] = (B["ppe"] / B["ppe_dec"] - 1) * 100
# Después del cierre del trimestre
F = dict(notes_nov=15.0, pref=12.5, pref_shares_max=12.5e9 / 1000 * 1.6 / 1e9, pref_shares_min=12.5e9 / 1000 * 1.362 / 1e9,
         fwd_shares=0.046, fwd_price=622.91875)
F["fwd_proceeds"] = F["fwd_shares"] * F["fwd_price"]
F["new_capital"] = F["notes_nov"] + F["pref"] + F["fwd_proceeds"]
F["pref_initial_price"] = 1000 / 1.6
F["pref_threshold"] = 1000 / 1.362
# Deuda neta para la valuación (pro forma): deuda contable - caja y títulos + acuerdo con los fiscales devengado
# - preferida cobrada - forward a cobrar. Los $15B de bonos de nov entran como deuda y como caja: neutros.
# NO se suman: leasing operativo (queda en el OCF), leasing financiero (su capital ya se resta como capex en el FCF),
# compromisos con los ventures de centros de datos (los alquileres futuros quedan dentro de margen/capex proyectado),
# garantías de valor residual (contingentes, no probables: van al escenario Bear y a riesgos).
B["net_debt_val"] = B["net_debt_sep_def"] + B["ag_accrued"] - F["pref"] - F["fwd_proceeds"]
SH_DIL = 2.573
SHARES = SH_DIL + F["pref_shares_max"] + F["fwd_shares"]
F["shares_pf"] = SHARES
F["dilution_pct"] = (SHARES / SH_DIL - 1) * 100
R["bal"] = {k: round(v, 3) for k, v in B.items()}
R["fin"] = {k: round(v, 4) for k, v in F.items()}

# ---------------------------------------------------------------------------
# 4) DCF ACTUALIZADO — año 1 = FY2027
# ---------------------------------------------------------------------------
def dcf(rev1, g2_5, ocf_m, capm, cap1, wacc, g, net_debt, shares):
    revs = [rev1]
    for x in lin(g2_5[0], g2_5[1], 4):
        revs.append(revs[-1] * (1 + x))
    om, cm = lin(*ocf_m), lin(*capm)
    capex = [cap1] + [r * c for r, c in zip(revs[1:], cm[1:])]
    fcf = [r * o - c for r, o, c in zip(revs, om, capex)]
    pv = sum(f / (1 + wacc) ** (i + 1) for i, f in enumerate(fcf))
    tv = fcf[-1] * (1 + g) / (wacc - g)
    pvtv = tv / (1 + wacc) ** 5
    ev = pv + pvtv
    return {"fv": (ev - net_debt) / shares, "tv_share": pvtv / ev, "fcf": fcf, "revs": revs, "ev": ev, "capex": capex}

REV0 = 256.88      # consenso FY2026 (9M real $181.71B + 4T implícito $75.17B, dentro de la guía $73-76B)
REV1 = 312.63      # consenso FY2027 (+21.7%)
ERP, BETA, KD_AT = 5.0, 1.20, 5.0       # KD: cupones de los bonos de nov-2026 (5.85%-7.50%) después de impuestos
mcap = PRICE * 2.55624                   # acciones A+B en circulación al 16-oct-2026
debt_all = B["debt_face"] + F["notes_nov"]
ke = TSY10 + BETA * ERP
wd = debt_all / (mcap + debt_all)
wacc_base = round((1 - wd) * ke + wd * KD_AT, 1) / 100
R["wacc"] = {"ke": round(ke, 2), "wd": round(wd * 100, 1), "mcap": round(mcap, 1), "wacc_base": wacc_base}
R["rev1_growth"] = round((REV1 / REV0 - 1) * 100, 1)

cases = {
    "Bear": dict(g2_5=(0.12, 0.06), ocf=(0.48, 0.50), capm=(230 / REV1, 0.33), cap1=230.0,
                 wacc=wacc_base + 0.005, g=0.025),
    "Base": dict(g2_5=(0.16, 0.09), ocf=(0.52, 0.57), capm=(200 / REV1, 0.27), cap1=200.0,
                 wacc=wacc_base, g=0.03),
    "Bull": dict(g2_5=(0.19, 0.11), ocf=(0.54, 0.60), capm=(180 / REV1, 0.22), cap1=180.0,
                 wacc=wacc_base - 0.01, g=0.035),
}
R["dcf"] = {}
for k, c in cases.items():
    nd = B["net_debt_val"] + (B["jv_rvg"] * 0.25 if k == "Bear" else 0)   # Bear: 25% de las garantías de valor residual
    r = dcf(REV1, c["g2_5"], c["ocf"], c["capm"], c["cap1"], c["wacc"], c["g"], nd, SHARES)
    R["dcf"][k] = {"fv": round(r["fv"], 2), "tv_share": round(r["tv_share"] * 100, 1), "fcf1": round(r["fcf"][0], 1),
                   "fcf5": round(r["fcf"][-1], 1), "rev5": round(r["revs"][-1], 1), "wacc": round(c["wacc"] * 100, 2),
                   "g": c["g"] * 100, "capm1": round(c["capm"][0] * 100, 1), "capex5": round(r["capex"][-1], 1),
                   "net_debt": round(nd, 2), "fcf": [round(x, 1) for x in r["fcf"]]}
fvs = {k: R["dcf"][k]["fv"] for k in cases}
R["dcf_simple_avg"] = round(sum(fvs.values()) / 3, 2)
R["dcf_prob"] = round(0.25 * fvs["Bear"] + 0.45 * fvs["Base"] + 0.30 * fvs["Bull"], 2)

b = cases["Base"]
waccs = [round(wacc_base + d, 4) for d in (-0.01, -0.005, 0, 0.005, 0.01)]
gs = [0.02, 0.025, 0.03, 0.035, 0.04]
grid_fn = lambda w, gg: dcf(REV1, b["g2_5"], b["ocf"], b["capm"], b["cap1"], w, gg, B["net_debt_val"], SHARES)["fv"]
R["grid"] = {"waccs": [round(w * 100, 2) for w in waccs], "gs": [x * 100 for x in gs],
             "vals": [[round(grid_fn(w, gg), 2) for gg in gs] for w in waccs]}

def solve(fn, lo, hi, target, n=80):
    for _ in range(n):
        mid = (lo + hi) / 2
        if (fn(mid) - target) * (fn(lo) - target) <= 0: hi = mid
        else: lo = mid
    return (lo + hi) / 2
f_ocf = lambda m: dcf(REV1, b["g2_5"], (b["ocf"][0], m), b["capm"], b["cap1"], b["wacc"], b["g"], B["net_debt_val"], SHARES)["fv"]
f_cap = lambda m: dcf(REV1, b["g2_5"], b["ocf"], (b["capm"][0], m), b["cap1"], b["wacc"], b["g"], B["net_debt_val"], SHARES)["fv"]
R["inverso"] = {"ocf5": round(solve(f_ocf, 0.40, 0.80, PRICE) * 100, 1), "capm5": round(solve(f_cap, 0.0, 0.40, PRICE) * 100, 1)}
# Mismo Base sin la dilución ni el capital nuevo (para aislar el efecto del financiamiento)
R["base_sin_financiamiento"] = round(dcf(REV1, b["g2_5"], b["ocf"], b["capm"], b["cap1"], b["wacc"], b["g"],
                                         B["net_debt_sep_def"] + B["ag_accrued"], SH_DIL)["fv"], 2)

# ---------------------------------------------------------------------------
# 5) COMPARABLES — P/E sobre EPS 2027 (año calendario; MSFT promedia FY27 y FY28 de junio; AAPL FY27 de septiembre)
# ---------------------------------------------------------------------------
peers = {"GOOGL": (284.78, 15.19), "AMZN": (259.30, 10.90), "MSFT": (530.61, (20.00 + 24.18) / 2), "AAPL": (342.37, 9.44)}
ads_ref = {"PINS": (18.96, 2.28), "RDDT": (95.10, 9.29)}
EPS27 = 35.59
pe = {k: v[0] / v[1] for k, v in peers.items()}
pe_avg = sum(pe.values()) / len(pe)
s = sorted(pe.values()); pe_med = (s[1] + s[2]) / 2
pe_ex_aapl = sum(v for k, v in pe.items() if k != "AAPL") / 3
R["comps"] = {"pe": {k: round(v, 1) for k, v in pe.items()}, "pe_avg": round(pe_avg, 2), "pe_med": round(pe_med, 2),
              "pe_ex_aapl": round(pe_ex_aapl, 2), "eps27": EPS27, "fv": round(pe_avg * EPS27, 2),
              "fv_med": round(pe_med * EPS27, 2), "fv_ex_aapl": round(pe_ex_aapl * EPS27, 2),
              "implied": {k: round(v * EPS27, 2) for k, v in pe.items()},
              "ads_ref_pe": {k: round(v[0] / v[1], 1) for k, v in ads_ref.items()},
              "meta_fwd_pe": round(PRICE / EPS27, 1), "meta_fwd26_pe": round(PRICE / 29.73, 1),
              "meta_core_ttm_pe": round(PRICE / T["eps_core"], 1), "meta_gaap_ttm_pe": round(PRICE / T["eps_gaap"], 1),
              "eps27_growth": round((35.59 / 29.73 - 1) * 100, 1)}

# ---------------------------------------------------------------------------
# 6) REVERSIÓN — P/E sobre EPS TTM SIN EXTRAORDINARIOS (10-Q/10-K) en cierres trimestrales
# ---------------------------------------------------------------------------
pre = {"1T24": 4.71, "2T24": 5.16}                        # EPS diluido 10-Q (sin partidas extraordinarias materiales)
all_lab = ["1T24", "2T24"] + q
all_eps = [pre["1T24"], pre["2T24"]] + core_eps
qe_px = {"4T24": 585.51, "1T25": 576.36, "2T25": 738.09, "3T25": 734.38,
         "4T25": 660.09, "1T26": 572.13, "2T26": 563.29, "3T26": 725.18}
def window(labs):
    out = []
    for lab in labs:
        i = all_lab.index(lab)
        e = sum(all_eps[i - 3:i + 1])
        out.append((lab, qe_px[lab], round(e, 2), round(qe_px[lab] / e, 2)))
    return out
w4 = window(["4T25", "1T26", "2T26", "3T26"])
w8 = window(["4T24", "1T25", "2T25", "3T25", "4T25", "1T26", "2T26", "3T26"])
pe4 = sum(x[3] for x in w4) / 4
pe8 = sum(x[3] for x in w8) / 8
R["rev"] = {"window": w4, "window8": w8, "pe4": round(pe4, 2), "pe8": round(pe8, 2),
            "eps_core_ttm": round(T["eps_core"], 2), "fv": round(pe4 * T["eps_core"], 2), "fv8": round(pe8 * T["eps_core"], 2),
            "sep_vendor_pe": [26.46, 27.87], "sep_vendor_fv_on_eps": round((26.46 + 27.87) / 2 * T["eps_core"], 2)}

# ---------------------------------------------------------------------------
# 7) CONSENSO y BLEND (15% DCF + 25% comps + 35% reversión + 25% consenso)
# ---------------------------------------------------------------------------
CONS = 850.10
methods = {"DCF Base": fvs["Base"], "Comparables": R["comps"]["fv"], "Reversión": R["rev"]["fv"], "Consenso": CONS}
blend = sum(methods[k] * W4[k] for k in W4)
R["methods"] = {k: round(v, 2) for k, v in methods.items()}
R["contrib"] = {k: round(methods[k] * W4[k], 2) for k in W4}
R["blend"] = round(blend, 2)
R["blend_vs_price"] = round((blend / PRICE - 1) * 100, 1)
R["blend_vs_sep"] = round((blend / 797.44 - 1) * 100, 1)
R["blend_vs_sep_ponderado"] = round((blend / R["sep_blend_ponderado_regla_actual"] - 1) * 100, 1)
R["blend_simple"] = round(sum(methods.values()) / 4, 2)
R["price"] = PRICE
R["price_vs_sep"] = round((PRICE / SEP_PRICE - 1) * 100, 1)
R["reaction"] = round((PRICE_POST / PRICE_PRE - 1) * 100, 1)
R["from_pre"] = round((PRICE / PRICE_PRE - 1) * 100, 1)
R["mcap"] = round(mcap, 1)
R["method_vs_price"] = {k: round((v / PRICE - 1) * 100, 1) for k, v in methods.items()}
R["dcf_vs_price"] = {k: round((v / PRICE - 1) * 100, 1) for k, v in fvs.items()}
pes4 = [x[3] for x in w4]
R["ff"] = {"DCF": [fvs["Bear"], fvs["Bull"]],
           "Comparables": [min(R["comps"]["implied"].values()), max(R["comps"]["implied"].values())],
           "Reversión": [round(min(pes4) * T["eps_core"], 2), round(max(pes4) * T["eps_core"], 2)],
           "Consenso": [629.06, 1050.0]}
f_cap1 = lambda c1: dcf(REV1, b["g2_5"], b["ocf"], (c1 / REV1, b["capm"][1]), c1, b["wacc"], b["g"], B["net_debt_val"], SHARES)["fv"]
R["capex_sens_10b"] = round(f_cap1(200.0) - f_cap1(210.0), 2)          # $ por acción por cada +$10B de capex 2027
R["blend_post_split"] = round(blend / 2, 2)
R["price_post_split"] = round(PRICE / 2, 2)

if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resultados.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(R, fh, ensure_ascii=False, indent=1)
    print(json.dumps(R, ensure_ascii=False, indent=1))
