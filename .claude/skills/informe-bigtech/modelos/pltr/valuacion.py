"""
Modelo de valuación PLTR — actualización al 3T 2026 (cierre 30-sep-2026, 8-K del 2-nov-2026, 10-Q del 3-nov-2026).

Correr:  python valuacion.py            (imprime todo y escribe resultados.json al lado)

Fuentes de los números de entrada:
  - 8-K Ex. 99.1 del 2-nov-2026: ingresos, segmentos de EE.UU., TCV, RDV comercial EE.UU., margen operativo ajustado,
    FCF ajustado, guía 4T26 y FY26, balance y flujo de caja de nueve meses.
  - 10-Q del 3-nov-2026: segmentos Gobierno/Comercial (Nota de segmentos), EE.UU. vs. resto del mundo, RPO $4.9B,
    acciones en circulación al 26-oct-2026, top 20 clientes.
  - SEC companyfacts XBRL: series trimestrales (ingresos, utilidad bruta, operativa, neta, OCF, capex, SBC, EPS diluido,
    acciones diluidas). Los trimestres 4T se aíslan restando los nueve meses del año fiscal; el OCF de cada trimestre
    se aísla restando el acumulado del trimestre anterior (en los 10-Q viene YTD).
  - Yahoo Finance chart API: cierre 6-nov-2026 de PLTR ($160.38), SNOW, CRWD, DDOG, NOW, ^TNX (4.859%) y cierres de
    fin de trimestre de PLTR.
  - stockanalysis.com (S&P Global): consenso PLTR al 5-nov-2026 (33 analistas, PT promedio $222.25, mediana $235,
    rango $80-273; ingresos 2026 $8.55B / 2027 $13.06B; EPS 2026 $1.70 / 2027 $2.51) y EPS de los comparables.
  - CRWD no publica consenso de EPS FY2028 gratuito: se deriva del EPS FY2027 ($1.26) por el crecimiento FY2028 de
    Zacks (+27.2%). Aproximado, etiquetado así en el informe.

Convenciones del DCF:
  - Año 1 = FY2027. Ingreso del año 1: consenso FY2027 en el Base; en Bear/Bull, crecimiento propio sobre el punto medio
    de la guía FY2026 ($8.532B). Crecimiento de los años 2-5 interpolado en línea recta.
  - Margen de OCF interpolado en línea recta del año 1 al 5, anclado en el OCF real TTM (56.2%).
  - FCF = ingresos x (margen de OCF - capex/ingresos). Descuento a fin de año; VT = FCF5 x (1+g)/(WACC-g).
  - Equity = EV + caja e inversiones (sin deuda); por acción = equity / acciones diluidas del 3T26.
"""
import json, os

def lin(a, b, n=5):
    return [a + (b - a) * i / (n - 1) for i in range(n)]

R = {}

# ---------------------------------------------------------------------------
# 1) DATOS TRIMESTRALES (millones de USD) — XBRL / 8-K
# ---------------------------------------------------------------------------
q      = ["3T25", "4T25", "1T26", "2T26", "3T26"]
rev    = [1181.092, 4475.446 - 3068.644, 1632.583, 1935.464, 2313.411]
gp     = [973.785, 3686.269 - 2495.433, 1416.785, 1638.594, 1930.125]
opinc  = [393.256, 1414.015 - 838.621, 753.998, 912.004, 1084.845]
ni     = [475.599, 1625.033 - 1016.357, 870.527, 1061.890, 1128.012]
ocf    = [1357.178 - 849.514, 2134.473 - 1357.178, 899.165, 2115.332 - 899.165, 3319.902 - 2115.332]
capex  = [20.610 - 13.818, 33.882 - 20.610, 7.401, 21.955 - 7.401, 29.969 - 21.955]
sbc    = [487.628 - 315.310, 684.033 - 487.628, 201.592, 466.801 - 201.592, 785.690 - 466.801]
eps    = [0.18, 0.23, 0.34, 0.41, 0.44]          # diluido GAAP (4T25 = 0.63 anual - 0.40 nueve meses)
dil    = [2571.057, None, 2570.924, 2568.694, 2573.926]

Qd = {}
for i, lab in enumerate(q):
    Qd[lab] = {"rev": round(rev[i], 1), "gp": round(gp[i], 1), "gm": round(gp[i] / rev[i] * 100, 1),
               "opinc": round(opinc[i], 1), "om": round(opinc[i] / rev[i] * 100, 1),
               "ni": round(ni[i], 1), "nm": round(ni[i] / rev[i] * 100, 1), "eps": eps[i],
               "ocf": round(ocf[i], 1), "ocf_m": round(ocf[i] / rev[i] * 100, 1), "capex": round(capex[i], 1),
               "fcf": round(ocf[i] - capex[i], 1), "fcf_m": round((ocf[i] - capex[i]) / rev[i] * 100, 1),
               "sbc": round(sbc[i], 1), "sbc_pct": round(sbc[i] / rev[i] * 100, 1)}
R["quarters"] = Qd

ttm = lambda a: sum(a[-4:])
T = {"rev": ttm(rev), "gp": ttm(gp), "opinc": ttm(opinc), "ni": ttm(ni), "ocf": ttm(ocf), "capex": ttm(capex),
     "sbc": ttm(sbc), "eps": round(ttm(eps), 2)}
T["fcf"] = T["ocf"] - T["capex"]
for k in ("gp", "opinc", "ni", "ocf", "fcf", "sbc", "capex"):
    T[k + "_m"] = T[k] / T["rev"] * 100
R["ttm"] = {k: (round(v, 2) if isinstance(v, float) else v) for k, v in T.items()}

# TTM al 3T25 = 4T24 + 1T25 + 2T25 + 3T25; 4T24 = anual 2024 menos nueve meses 2024 (XBRL: $2,037.988M)
rev_4t24 = 2865.507 - 2037.988
ttm_3t25 = rev_4t24 + 883.855 + 1003.697 + 1181.092
R["ttm"]["rev_yoy"] = round((T["rev"] / ttm_3t25 - 1) * 100, 1)
R["ttm"]["rev_ttm_3t25"] = round(ttm_3t25, 1)

# Trimestre 3T26 vs 3T25, segmentos
S = {"gov": 1145.540, "gov_prev": 632.676, "com": 1167.871, "com_prev": 548.416,
     "us_gov": 953.0, "us_com": 984.0, "us_gov_prev": 486.0, "us_com_prev": 397.0,
     "us": 1937.189, "us_prev": 882.571, "row": 376.222, "row_prev": 298.521,
     "gov_contrib_m": 70, "com_contrib_m": 77, "us_com_q2": 764.0, "us_gov_q2": 809.0}
S["intl_gov"] = S["gov"] - S["us_gov"]; S["intl_gov_prev"] = S["gov_prev"] - S["us_gov_prev"]
S["intl_com"] = S["com"] - S["us_com"]; S["intl_com_prev"] = S["com_prev"] - S["us_com_prev"]
for k in ("gov", "com", "us_gov", "us_com", "intl_gov", "intl_com", "us", "row"):
    S[k + "_yoy"] = (S[k] / S[k + "_prev"] - 1) * 100
S["us_com_qoq"] = (S["us_com"] / S["us_com_q2"] - 1) * 100
S["us_gov_qoq"] = (S["us_gov"] / S["us_gov_q2"] - 1) * 100
R["seg"] = {k: round(v, 1) for k, v in S.items()}
R["q3"] = {"rev_yoy": round((2313.411 / 1181.092 - 1) * 100, 1), "rev_qoq": round((2313.411 / 1935.464 - 1) * 100, 1),
           "om_adj": 61.7, "tcv": 2918, "tcv_yoy": 6, "us_com_tcv": 1463, "us_com_tcv_yoy": 11,
           "us_com_rdv": 6517, "us_com_rdv_yoy": 79, "us_com_rdv_qoq": 4, "rdv_q2_us_com": 6238,
           "rpo": 4.9, "rpo_q2": 4.9, "deals_1m": 212, "deals_5m": 107, "deals_10m": 64, "rule40": 158,
           "adj_fcf": 1216.077, "adj_fcf_m": 52.6, "ar": 1883.498, "ar_dec": 1042.065,
           "tax": 13.560, "pretax": 1148.001, "interest": 88.936}
R["q3"]["eff_tax"] = round(13.560 / 1148.001 * 100, 1)
R["q3"]["ar_growth"] = round((1883.498 / 1042.065 - 1) * 100, 1)

# Guía
G = {"q4_lo": 2649, "q4_hi": 2653, "fy_lo": 8530, "fy_hi": 8534, "fy_prev_lo": 8150, "fy_prev_hi": 8160,
     "fy_jun_lo": 7650, "fy_jun_hi": 7660, "uscom": 3559, "adj_oi_lo": 5245, "adj_oi_hi": 5249,
     "adj_fcf_lo": 4800, "adj_fcf_hi": 5000, "rev_9m": 5881.458, "fy25": 4475.446, "q4_25": rev[1]}
G["q4_mid"] = (G["q4_lo"] + G["q4_hi"]) / 2
G["q4_yoy"] = (G["q4_mid"] / G["q4_25"] - 1) * 100
G["fy_mid"] = (G["fy_lo"] + G["fy_hi"]) / 2
G["fy_yoy"] = (G["fy_mid"] / G["fy25"] - 1) * 100
G["fy_raise"] = G["fy_mid"] - (G["fy_prev_lo"] + G["fy_prev_hi"]) / 2
G["q4_implied_qoq"] = (G["q4_mid"] / 2313.411 - 1) * 100
G["adj_fcf_m_mid"] = (G["adj_fcf_lo"] + G["adj_fcf_hi"]) / 2 / G["fy_mid"] * 100
R["guide"] = {k: round(v, 2) for k, v in G.items()}

# ---------------------------------------------------------------------------
# 2) BALANCE
# ---------------------------------------------------------------------------
B = {"cash": 3619.414, "mkt": 6942.117, "debt": 0.0, "assets": 13412.976, "liab": 2067.876, "equity": 11227.981,
     "cash_jun": 2030.047, "mkt_jun": 7379.052, "assets_jun": 11678.564, "liab_jun": 1793.680, "equity_jun": 9774.194,
     "deferred": 661.255 + 32.660, "deposits": 512.573 + 0.268}
B["net_cash"] = B["cash"] + B["mkt"] - B["debt"]
B["net_cash_jun"] = B["cash_jun"] + B["mkt_jun"]
B["delta"] = B["net_cash"] - B["net_cash_jun"]
R["bal"] = {k: round(v, 1) for k, v in B.items()}

# ---------------------------------------------------------------------------
# 3) DCF — año 1 = FY2027
# ---------------------------------------------------------------------------
PRICE = 160.38            # cierre 6-nov-2026
PRICE_PRE = 178.34        # cierre 2-nov-2026 (reporte después del cierre)
PRICE_POST = 175.40       # cierre 3-nov-2026
PRICE_AUG = 171.54        # precio del informe anterior (18-ago-2026)
TSY10 = 4.859
SH_DIL = 2573.926         # millones, diluidas promedio 3T26
SH_OUT = 2306.705 + 101.787 + 1.005   # clase A + B + F al 26-oct-2026
NET_CASH = B["net_cash"]
REV0 = G["fy_mid"]        # 8,532
REV1_CONS = 13060.0
BETA_ADJ, ERP = 1.30, 5.0
wacc_base = round(TSY10 + BETA_ADJ * ERP, 1) / 100     # 11.4%
CAPM = 0.006              # capex/ingresos (TTM real 0.59%)

def dcf(rev1, g2_5, ocf_m, wacc, g, capm=CAPM, net_cash=NET_CASH, shares=SH_DIL):
    revs = [rev1]
    for x in lin(g2_5[0], g2_5[1], 4):
        revs.append(revs[-1] * (1 + x))
    om = lin(*ocf_m)
    fcf = [r * (o - capm) for r, o in zip(revs, om)]
    pv = sum(f / (1 + wacc) ** (i + 1) for i, f in enumerate(fcf))
    pvtv = fcf[-1] * (1 + g) / (wacc - g) / (1 + wacc) ** 5
    ev = pv + pvtv
    return {"fv": (ev + net_cash) / shares, "tv_share": pvtv / ev, "fcf": fcf, "revs": revs, "ev": ev}

cases = {
    "Bear": dict(rev1=REV0 * 1.45, g2_5=(0.28, 0.10), ocf=(0.55, 0.55), wacc=wacc_base + 0.014, g=0.025),
    "Base": dict(rev1=REV1_CONS,   g2_5=(0.36, 0.15), ocf=(0.56, 0.60), wacc=wacc_base,         g=0.030),
    "Bull": dict(rev1=REV0 * 1.58, g2_5=(0.42, 0.20), ocf=(0.57, 0.64), wacc=wacc_base - 0.013, g=0.035),
}
R["dcf"] = {}
for k, c in cases.items():
    r = dcf(c["rev1"], c["g2_5"], c["ocf"], c["wacc"], c["g"])
    growth = [c["rev1"] / REV0 - 1] + lin(*c["g2_5"], 4)
    R["dcf"][k] = {"fv": round(r["fv"], 2), "tv_share": round(r["tv_share"] * 100, 1),
                   "wacc": round(c["wacc"] * 100, 1), "g": round(c["g"] * 100, 1),
                   "growth": [round(x * 100, 1) for x in growth], "ocf": [round(x * 100, 1) for x in lin(*c["ocf"])],
                   "revs": [round(x / 1000, 2) for x in r["revs"]], "fcf": [round(x / 1000, 2) for x in r["fcf"]],
                   "ev": round(r["ev"] / 1000, 1)}
fvs = {k: R["dcf"][k]["fv"] for k in cases}
R["dcf_simple_avg"] = round(sum(fvs.values()) / 3, 2)
R["dcf_prob"] = round(0.25 * fvs["Bear"] + 0.45 * fvs["Base"] + 0.30 * fvs["Bull"], 2)
R["wacc_base"] = round(wacc_base * 100, 1)

b = cases["Base"]
waccs = [round(wacc_base + d, 4) for d in (-0.02, -0.01, 0, 0.01, 0.02)]
gs = [0.02, 0.025, 0.03, 0.035, 0.04]
R["grid"] = {"waccs": [round(w * 100, 1) for w in waccs], "gs": [x * 100 for x in gs],
             "vals": [[round(dcf(b["rev1"], b["g2_5"], b["ocf"], w, gg)["fv"], 2) for gg in gs] for w in waccs]}

def solve(fn, lo, hi, target, n=100):
    flo = fn(lo) - target
    for _ in range(n):
        mid = (lo + hi) / 2
        fm = fn(mid) - target
        if (fm > 0) == (flo > 0): lo, flo = mid, fm
        else: hi = mid
    return (lo + hi) / 2

# DCF inverso: año 1 fijo en el consenso 2027, crecimiento PLANO en los años 2-5 que reproduce el precio
f_flat = lambda gr: dcf(b["rev1"], (gr, gr), b["ocf"], b["wacc"], b["g"])["fv"]
g_need = solve(f_flat, 0.0, 1.5, PRICE)
rev5_need = b["rev1"] * (1 + g_need) ** 4
# idem con el caso Bull (márgenes, WACC y g del Bull)
bu = cases["Bull"]
f_flat_bull = lambda gr: dcf(REV1_CONS, (gr, gr), bu["ocf"], bu["wacc"], bu["g"])["fv"]
g_need_bull = solve(f_flat_bull, 0.0, 1.5, PRICE)
# margen de OCF del año 5 necesario con el crecimiento del Base
f_ocf = lambda m: dcf(b["rev1"], b["g2_5"], (b["ocf"][0], m), b["wacc"], b["g"])["fv"]
ocf_at_100 = f_ocf(1.0)
R["inverso"] = {"g_flat": round(g_need * 100, 1), "rev2031": round(rev5_need / 1000, 1),
                "rev2031_x_fy26": round(rev5_need / REV0, 1), "g_flat_bull": round(g_need_bull * 100, 1),
                "rev2031_bull": round(REV1_CONS * (1 + g_need_bull) ** 4 / 1000, 1),
                "fv_ocf_100": round(ocf_at_100, 2)}
# precio de agosto con el modelo nuevo (cuánto de la caída cerró la brecha)
R["inverso"]["g_flat_aug_price"] = round(solve(f_flat, 0.0, 1.5, PRICE_AUG) * 100, 1)

# ---------------------------------------------------------------------------
# 4) COMPARABLES — P/E sobre EPS 2027 (año calendario o fiscal más cercano)
# ---------------------------------------------------------------------------
EPS27 = 2.51
peers = {"SNOW": (275.88, 3.04, "FY ene-2028"), "CRWD": (216.90, round(1.26 * 1.272, 3), "FY ene-2028 (derivado)"),
         "DDOG": (179.04, 3.16, "CY2027"), "NOW": (101.97, 4.80, "CY2027")}
peer_rev_g = {"SNOW": 28.8, "CRWD": 24.9, "DDOG": 22.3, "NOW": 18.7}
pe = {k: v[0] / v[1] for k, v in peers.items()}
pe_avg = sum(pe.values()) / 4
s = sorted(pe.values()); pe_med = (s[1] + s[2]) / 2
R["comps"] = {"pe": {k: round(v, 1) for k, v in pe.items()}, "eps": {k: v[1] for k, v in peers.items()},
              "price": {k: v[0] for k, v in peers.items()}, "rev_g": peer_rev_g,
              "pe_avg": round(pe_avg, 2), "pe_med": round(pe_med, 2), "eps27": EPS27,
              "fv": round(pe_avg * EPS27, 2), "fv_med": round(pe_med * EPS27, 2),
              "implied": {k: round(v * EPS27, 2) for k, v in pe.items()},
              "pltr_pe27": round(PRICE / EPS27, 1), "pltr_pe26": round(PRICE / 1.70, 1),
              "pltr_pe_ttm": round(PRICE / T["eps"], 1),
              "pltr_ev_sales_ttm": round((PRICE * SH_OUT - NET_CASH) / T["rev"], 1),
              "pltr_ev_sales27": round((PRICE * SH_OUT - NET_CASH) / REV1_CONS, 1),
              "pltr_mcap_b": round(PRICE * SH_OUT / 1000, 1), "pltr_eps27_g": round((2.51 / 1.70 - 1) * 100, 1)}

# ---------------------------------------------------------------------------
# 5) REVERSIÓN — P/E sobre EPS TTM diluido en los últimos 4 cierres trimestrales
# ---------------------------------------------------------------------------
eps_series = {"4T24": 0.03, "1T25": 0.08, "2T25": 0.13, "3T25": 0.18, "4T25": 0.23, "1T26": 0.34, "2T26": 0.41, "3T26": 0.44}
order = list(eps_series)
qe_px = {"3T25": 182.42, "4T25": 177.75, "1T26": 146.28, "2T26": 116.67, "3T26": 187.05}
def window(labs):
    out = []
    for lab in labs:
        i = order.index(lab)
        e = round(sum(eps_series[o] for o in order[i - 3:i + 1]), 2)
        out.append((lab, qe_px[lab], e, round(qe_px[lab] / e, 1)))
    return out
w4 = window(["4T25", "1T26", "2T26", "3T26"])
w2 = window(["2T26", "3T26"])
pe4 = sum(x[3] for x in w4) / 4
pe2 = sum(x[3] for x in w2) / 2
R["rev"] = {"window": w4, "pe4": round(pe4, 1), "fv": round(pe4 * T["eps"], 2),
            "pe2": round(pe2, 1), "fv2": round(pe2 * T["eps"], 2),
            "pe_last": w4[-1][3], "fv_last": round(w4[-1][3] * T["eps"], 2),
            "fv_min": round(min(x[3] for x in w4) * T["eps"], 2), "fv_max": round(max(x[3] for x in w4) * T["eps"], 2)}

# ---------------------------------------------------------------------------
# 6) CONSENSO Y BLEND (15% DCF + 25% comps + 35% reversión + 25% consenso)
# ---------------------------------------------------------------------------
CONS = 222.25
W4 = {"DCF Base": 0.15, "Comparables": 0.25, "Reversión": 0.35, "Consenso": 0.25}
methods = {"DCF Base": fvs["Base"], "Comparables": R["comps"]["fv"], "Reversión": R["rev"]["fv"], "Consenso": CONS}
blend = sum(methods[k] * W4[k] for k in W4)
R["methods"] = {k: round(v, 2) for k, v in methods.items()}
R["contrib"] = {k: round(methods[k] * W4[k], 2) for k in W4}
R["blend"] = round(blend, 2)
R["blend_vs_price"] = round((blend / PRICE - 1) * 100, 1)
R["blend_simple"] = round(sum(methods.values()) / 4, 2)
R["method_vs_price"] = {k: round((v / PRICE - 1) * 100, 1) for k, v in methods.items()}
R["dcf_vs_price"] = {k: round((v / PRICE - 1) * 100, 1) for k, v in fvs.items()}
# sensibilidad: blend con la ventana de reversión de 2 trimestres
m2 = dict(methods); m2["Reversión"] = R["rev"]["fv2"]
R["blend_rev2"] = round(sum(m2[k] * W4[k] for k in W4), 2)
R["blend_rev2_vs_price"] = round((R["blend_rev2"] / PRICE - 1) * 100, 1)

# Informe anterior (18-ago-2026): promedio simple publicado y lo que daba con la ponderación vigente
AUG = {"DCF Base": 55.47, "Comparables": 164.00, "Reversión": 288.94, "Consenso": 191.68}
R["aug_blend_simple"] = round(sum(AUG.values()) / 4, 2)          # 175.02 publicado
R["aug_blend_weighted"] = round(sum(AUG[k] * W4[k] for k in W4), 2)
R["blend_vs_aug"] = round((blend / 175.02 - 1) * 100, 1)
R["blend_vs_aug_w"] = round((blend / R["aug_blend_weighted"] - 1) * 100, 1)

R["price"] = PRICE
R["price_vs_aug"] = round((PRICE / PRICE_AUG - 1) * 100, 1)
R["reaction"] = round((PRICE_POST / PRICE_PRE - 1) * 100, 1)
R["from_pre"] = round((PRICE / PRICE_PRE - 1) * 100, 1)
R["shares_out"] = round(SH_OUT, 1)
R["ff"] = {"DCF": [fvs["Bear"], fvs["Bull"]],
           "Comparables": [min(R["comps"]["implied"].values()), max(R["comps"]["implied"].values())],
           "Reversión": [R["rev"]["fv_min"], R["rev"]["fv_max"]],
           "Consenso": [80.0, 273.0]}

if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resultados.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(R, fh, ensure_ascii=False, indent=1)
    print(json.dumps(R, ensure_ascii=False, indent=1))
