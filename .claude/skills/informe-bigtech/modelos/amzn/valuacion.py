"""
Modelo de valuación AMZN — actualización al 3T 2026 (cierre 30-sep-2026, 8-K del 29-oct-2026, 10-Q del 30-oct-2026).

Correr:  python valuacion.py            (imprime todo y escribe resultados.json al lado)

Fuentes de los números de entrada (todas verificadas a mano contra el documento original):
  - 8-K Ex. 99.1 del 29-oct-2026 (segmentos, flujo de caja, balance, métricas suplementarias, guía 4T26).
  - 10-Q del 3T26 (deuda Nota 5, leasing Nota 3, Anthropic/OpenAI Nota 2, RPO $578B, "Other income (expense), net").
  - SEC companyfacts XBRL (series trimestrales de utilidad neta y "OtherNonoperatingIncomeExpense").
  - Yahoo Finance chart API: cierres al 6-nov-2026 y cierres de fin de trimestre; ^TNX 4.859% al 6-nov-2026.
  - stockanalysis.com (6-nov-2026): consenso PT $326.99 (61 analistas), ingresos FY26 $829.0B / FY27 $958.65B,
    EPS FY27 $10.90; EPS próximos de los comparables.

Convenciones del DCF (las mismas que se usan para reproducir septiembre):
  - 5 años explícitos; crecimiento del año 2 al 5, margen de OCF y capex/ingresos del año 1 al 5 interpolados en línea recta.
  - FCF = ingresos x margen de OCF - capex (capex del año 1 en dólares, fijado por escenario).
  - Descuento a fin de año; VT = FCF5 x (1+g)/(WACC-g) descontado 5 años.
  - Equity = EV - deuda neta; por acción = equity / acciones diluidas.
"""
import json, os

def lin(a, b, n=5):
    return [a + (b - a) * i / (n - 1) for i in range(n)]

def dcf(rev1, g2_5, ocf, capm, cap1, wacc, g, net_debt, shares):
    revs = [rev1]
    for x in lin(g2_5[0], g2_5[1], 4):
        revs.append(revs[-1] * (1 + x))
    om, cm = lin(*ocf), lin(*capm)
    capex = [cap1] + [r * c for r, c in zip(revs[1:], cm[1:])]
    fcf = [r * o - c for r, o, c in zip(revs, om, capex)]
    pv = sum(f / (1 + wacc) ** (i + 1) for i, f in enumerate(fcf))
    tv = fcf[-1] * (1 + g) / (wacc - g)
    pvtv = tv / (1 + wacc) ** 5
    ev = pv + pvtv
    return {"fv": (ev - net_debt) / shares, "tv_share": pvtv / ev, "fcf": fcf, "revs": revs,
            "ev": ev, "capex": capex}

R = {}

# ---------------------------------------------------------------------------
# 1) REPRODUCCIÓN DEL CASO DE SEPTIEMBRE (informe publicado con datos al 2T26)
# ---------------------------------------------------------------------------
SEP = dict(rev1=825.58, net_debt=54.78, shares=10.903)
sep_cases = {
    "Bear": dict(g2_5=(0.095, 0.06), ocf=(0.195, 0.235), capm=(230 / 825.58, 0.155), cap1=230, wacc=0.105, g=0.025),
    "Base": dict(g2_5=(0.13, 0.08), ocf=(0.21, 0.28), capm=(220 / 825.58, 0.115), cap1=220, wacc=0.10, g=0.03),
    "Bull": dict(g2_5=(0.155, 0.10), ocf=(0.225, 0.305), capm=(205 / 825.58, 0.085), cap1=205, wacc=0.09, g=0.035),
}
sep_pub = {"Bear": 57.72, "Base": 185.24, "Bull": 365.57}
R["sep_repro"] = {}
for k, c in sep_cases.items():
    r = dcf(SEP["rev1"], c["g2_5"], c["ocf"], c["capm"], c["cap1"], c["wacc"], c["g"], SEP["net_debt"], SEP["shares"])
    R["sep_repro"][k] = {"modelo": round(r["fv"], 2), "publicado": sep_pub[k], "tv_share": round(r["tv_share"] * 100, 1),
                         "fcf1": round(r["fcf"][0], 1)}
sep_methods = {"DCF Base": 185.24, "Comparables": 261.10, "SOTP": 277.28, "Reversión": 374.79, "Consenso": 318.93}
R["sep_blend_simple"] = round(sum(sep_methods.values()) / 5, 2)               # 283.47 publicado
W = {"DCF Base": 0.075, "SOTP": 0.075, "Comparables": 0.25, "Reversión": 0.35, "Consenso": 0.25}
R["sep_blend_ponderado_regla_actual"] = round(sum(sep_methods[k] * W[k] for k in W), 2)

# ---------------------------------------------------------------------------
# 2) DATOS DEL 3T26 (millones -> miles de millones)
# ---------------------------------------------------------------------------
PRICE = 259.30              # cierre 6-nov-2026 (viernes, último día hábil antes de la publicación)
PRICE_PRE = 243.79          # cierre 29-oct-2026 (día del reporte, publicado después del cierre)
PRICE_POST = 240.35         # cierre 30-oct-2026
SEP_PRICE = 270.20
SHARES = 10.929             # diluidas, promedio ponderado 3T26
SHARES_OUT = 10.811         # en circulación al 30-sep-2026
TSY10 = 4.859

q_labels = ["4T24", "1T25", "2T25", "3T25", "4T25", "1T26", "2T26", "3T26"]
rev   = [187.792, 155.667, 167.702, 180.169, 213.386, 181.519, 200.606, 201.944]
opinc = [21.203, 18.405, 19.171, 17.422, 24.977, 23.852, 27.461, 28.076]
ni    = [20.004, 17.127, 18.164, 21.187, 21.192, 30.255, 62.647, 20.685]
oth   = [0.468, 2.749, 1.117, 10.186, 1.177, 15.647, 53.415, -0.703]   # "Other income (expense), net" (marcas)
ocf_q = [45.636, 17.015, 32.515, 35.525, 54.459, 26.032, 45.387, 42.422]
dil   = [20.004 / 1.86, 10.793, 10.806, 10.845, 21.192 / 1.95, 10.874, 10.903, 10.929]
# acciones diluidas: XBRL WeightedAverageNumberOfDilutedSharesOutstanding; los 4T no vienen trimestrales en XBRL y se
# derivan de utilidad neta / EPS diluido reportado (4T24 $1.86, 4T25 $1.95)
TAX = 0.23   # tasa efectiva 9M26 (33,939 / 147,560 = 23.0%)

core_ni = [n - o * (1 - TAX) for n, o in zip(ni, oth)]
core_eps_q = [c / s for c, s in zip(core_ni, dil)]
R["quarters"] = {lab: {"rev": rev[i], "opinc": opinc[i], "op_m": round(opinc[i] / rev[i] * 100, 1),
                       "ni": ni[i], "net_m": round(ni[i] / rev[i] * 100, 1), "core_ni": round(core_ni[i], 2),
                       "core_eps": round(core_eps_q[i], 2), "ocf_m": round(ocf_q[i] / rev[i] * 100, 1)}
                 for i, lab in enumerate(q_labels)}

ttm = lambda arr, end=8: sum(arr[end - 4:end])
TTM = {"rev": ttm(rev), "opinc": ttm(opinc), "ni": ttm(ni), "core_ni": ttm(core_ni), "ocf": ttm(ocf_q),
       "core_eps": sum(core_eps_q[4:8]), "gaap_eps": 1.95 + 2.78 + 5.75 + 1.89}
TTM["op_m"] = TTM["opinc"] / TTM["rev"] * 100
TTM["ocf_m"] = TTM["ocf"] / TTM["rev"] * 100
R["ttm"] = {k: round(v, 3) for k, v in TTM.items()}

# Flujo de caja TTM (8-K, columna de doce meses)
CF = dict(ocf=168.300, capex_gross=215.192, proceeds=4.535, fl_principal=1.681, fo_principal=0.333,
          fl_acquired=4.543)
CF["capex_net"] = CF["capex_gross"] - CF["proceeds"]                         # 210.657
CF["fcf"] = CF["ocf"] - CF["capex_net"]                                       # -42.357 (cifra de Amazon)
CF["fcf_less_principal"] = CF["fcf"] - CF["fl_principal"] - CF["fo_principal"]
CF["fcf_less_leases"] = CF["fcf"] - CF["fl_acquired"] - CF["fo_principal"]
CF["capex_9m_net"] = 175.670 - 3.482
CF["q4_implied_capex"] = 220.0 - CF["capex_9m_net"]
R["cf"] = {k: round(v, 3) for k, v in CF.items()}

# Balance al 30-sep-2026 (sin duplicar: LongTermDebt XBRL = valor nominal total, ya incluye la porción corriente)
BAL = dict(cash=55.783, mkt_sec=58.443, ltd_noncurrent=173.125, ltd_current=6.827, st_borrow=0.380,
           fin_lease=14.495, fin_oblig=9.726, op_lease=100.288, face_ltd=180.887)
BAL["debt_total"] = BAL["ltd_noncurrent"] + BAL["ltd_current"] + BAL["st_borrow"]
BAL["net_debt"] = BAL["debt_total"] + BAL["fin_lease"] + BAL["fin_oblig"] - BAL["cash"] - BAL["mkt_sec"]
BAL["net_debt_sep_def"] = BAL["face_ltd"] - BAL["cash"]          # misma definición que septiembre
BAL["ebitda_ttm"] = TTM["opinc"] + (19.471 + 18.945 + 19.988 + 20.949)
BAL["debt_ebitda"] = (BAL["debt_total"] + BAL["fin_lease"] + BAL["fin_oblig"]) / BAL["ebitda_ttm"]
BAL["anthropic"] = 92.5 + 146.2
BAL["openai"] = 50.0
R["bal"] = {k: round(v, 3) for k, v in BAL.items()}

# Segmentos 3T26 y nube de los pares (mismo trimestre calendario)
SEG = {"North America": (112.852, 8.723, 0.06), "International": (43.108, 1.580, 0.05), "AWS": (45.984, 17.773, 0.393)}
R["seg"] = {k: {"rev": v[0], "oi": v[1], "m": round(v[1] / v[0] * 100, 1), "share": round(v[0] / 201.944 * 100, 1),
                "oi_share": round(v[1] / 28.076 * 100, 1)} for k, v in SEG.items()}
R["aws_run_rate"] = round(45.984 * 4, 2)
R["rpo_qoq"] = round((578 / 364 - 1) * 100, 1)

# Guía 4T26 vs consenso
G = dict(rev_lo=240.0, rev_hi=247.0, oi_lo=28.5, oi_hi=33.5, rev_cons=244.16, oi_cons=33.0)
G["rev_mid"] = (G["rev_lo"] + G["rev_hi"]) / 2
G["oi_mid"] = (G["oi_lo"] + G["oi_hi"]) / 2
G["oi_mid_vs_cons"] = (G["oi_mid"] / G["oi_cons"] - 1) * 100
G["rev_mid_vs_cons"] = (G["rev_mid"] / G["rev_cons"] - 1) * 100
G["oi_mid_yoy"] = (G["oi_mid"] / 24.977 - 1) * 100
G["fy26_rev_guide_mid"] = 584.069 + G["rev_mid"]
# EPS FY26 sin marcas: 9M core + 4T con el punto medio de la guía operativa, interés neto del 3T, tasa 23%
q4_core = (G["oi_mid"] + (1.187 - 1.691)) * (1 - TAX) / SHARES
G["fy26_core_eps"] = sum(core_eps_q[5:8]) + q4_core
R["guide"] = {k: round(v, 3) for k, v in G.items()}

# ---------------------------------------------------------------------------
# 3) DCF ACTUALIZADO — año 1 = FY2027
# ---------------------------------------------------------------------------
REV0 = 829.0       # consenso FY2026 (9M reales + 4T guiado)
REV1 = 958.65      # consenso FY2027 (+15.6%), coherente con AWS +40% (Jassy, call 29-oct-2026)
ERP, BETA, KD_AT = 5.0, 1.15, 4.0
mcap = PRICE * SHARES_OUT
debt_all = BAL["debt_total"] + BAL["fin_lease"] + BAL["fin_oblig"]
ke = TSY10 + BETA * ERP
wd = debt_all / (mcap + debt_all)
wacc_base = round((1 - wd) * ke + wd * KD_AT, 1) / 100
R["wacc"] = {"ke": round(ke, 2), "wd": round(wd * 100, 1), "mcap": round(mcap, 1), "wacc_base": wacc_base}

cases = {
    "Bear": dict(g2_5=(0.10, 0.06), ocf=(0.21, 0.24), capm=(300 / REV1, 0.155), cap1=300.0,
                 wacc=wacc_base + 0.005, g=0.025),
    "Base": dict(g2_5=(0.15, 0.09), ocf=(0.22, 0.29), capm=(280 / REV1, 0.125), cap1=280.0,
                 wacc=wacc_base, g=0.03),
    "Bull": dict(g2_5=(0.175, 0.11), ocf=(0.23, 0.31), capm=(265 / REV1, 0.10), cap1=265.0,
                 wacc=wacc_base - 0.01, g=0.035),
}
R["dcf"] = {}
for k, c in cases.items():
    r = dcf(REV1, c["g2_5"], c["ocf"], c["capm"], c["cap1"], c["wacc"], c["g"], BAL["net_debt"], SHARES)
    R["dcf"][k] = {"fv": round(r["fv"], 2), "tv_share": round(r["tv_share"] * 100, 1), "fcf1": round(r["fcf"][0], 1),
                   "fcf5": round(r["fcf"][-1], 1), "rev5": round(r["revs"][-1], 1), "wacc": round(c["wacc"] * 100, 2),
                   "g": c["g"] * 100, "capm1": round(c["capm"][0] * 100, 1), "capex5": round(r["capex"][-1], 1),
                   "fcf": [round(x, 1) for x in r["fcf"]]}
fvs = {k: R["dcf"][k]["fv"] for k in cases}
R["dcf_simple_avg"] = round(sum(fvs.values()) / 3, 2)
R["dcf_prob"] = round(0.25 * fvs["Bear"] + 0.45 * fvs["Base"] + 0.30 * fvs["Bull"], 2)

# Grilla WACC x g del Base
b = cases["Base"]
waccs = [round(wacc_base + d, 4) for d in (-0.01, -0.005, 0, 0.005, 0.01)]
gs = [0.02, 0.025, 0.03, 0.035, 0.04]
R["grid"] = {"waccs": [round(w * 100, 2) for w in waccs], "gs": [x * 100 for x in gs],
             "vals": [[round(dcf(REV1, b["g2_5"], b["ocf"], b["capm"], b["cap1"], w, gg, BAL["net_debt"], SHARES)["fv"], 2)
                       for gg in gs] for w in waccs]}


# DCF inverso: margen de OCF del año 5 (resto del Base fijo) que iguala el precio; y WACC que lo iguala
def solve(fn, lo, hi, target, n=80):
    for _ in range(n):
        mid = (lo + hi) / 2
        if (fn(mid) - target) * (fn(lo) - target) <= 0: hi = mid
        else: lo = mid
    return (lo + hi) / 2
f_ocf = lambda m: dcf(REV1, b["g2_5"], (b["ocf"][0], m), b["capm"], b["cap1"], b["wacc"], b["g"], BAL["net_debt"], SHARES)["fv"]
f_wacc = lambda w: dcf(REV1, b["g2_5"], b["ocf"], b["capm"], b["cap1"], w, b["g"], BAL["net_debt"], SHARES)["fv"]
R["inverso"] = {"ocf5": round(solve(f_ocf, 0.2, 0.5, PRICE) * 100, 1), "wacc": round(solve(f_wacc, 0.06, 0.12, PRICE) * 100, 2)}

# Mismo Base con las convenciones de septiembre (para aislar el efecto de la deuda neta nueva)
R["base_con_deuda_sep_def"] = round(dcf(REV1, b["g2_5"], b["ocf"], b["capm"], b["cap1"], b["wacc"], b["g"],
                                        BAL["net_debt_sep_def"], SHARES)["fv"], 2)

# ---------------------------------------------------------------------------
# 4) COMPARABLES — P/E sobre EPS 2027 (año calendario; MSFT promedia FY27 y FY28 de junio)
# ---------------------------------------------------------------------------
peers = {
    "MSFT": (530.61, (20.00 + 24.18) / 2),
    "GOOGL": (284.78, 15.19),
    "META": (610.15, 35.59),
    "WMT": (125.52, 3.23),     # FY ene-2028 ~ año calendario 2027
    "SHOP": (148.91, 2.45),
}
pe = {k: v[0] / v[1] for k, v in peers.items()}
EPS27 = 10.90
pe_avg = sum(pe.values()) / len(pe)
pe_sorted = sorted(pe.values())
pe_med = pe_sorted[len(pe_sorted) // 2]
R["comps"] = {"pe": {k: round(v, 1) for k, v in pe.items()}, "pe_avg": round(pe_avg, 2), "pe_med": round(pe_med, 2),
              "eps27": EPS27, "fv": round(pe_avg * EPS27, 2), "fv_med": round(pe_med * EPS27, 2),
              "amzn_fwd_pe": round(PRICE / EPS27, 1), "amzn_core_ttm_pe": round(PRICE / TTM["core_eps"], 1),
              "amzn_gaap_ttm_pe": round(PRICE / TTM["gaap_eps"], 1),
              "implied": {k: round(v * EPS27, 2) for k, v in pe.items()},
              "fv_ex_shop": round(sum(v for k, v in pe.items() if k != "SHOP") / 4 * EPS27, 2)}

# ---------------------------------------------------------------------------
# 5) SOTP — AWS 10x tasa anualizada, resto 2.2x ingresos TTM (TTM ex-AWS exacto: Amazon publica el TTM de AWS)
# ---------------------------------------------------------------------------
aws_rr = 45.984 * 4
non_aws_ttm = 797.455 - 161.382
def sotp(m_aws, m_rest):
    ev = aws_rr * m_aws + non_aws_ttm * m_rest
    return ev, (ev - BAL["net_debt"]) / SHARES
ev10, fv10 = sotp(10, 2.2)
ev13, fv13 = sotp(13, 2.2)
R["sotp"] = {"aws_rr": round(aws_rr, 2), "non_aws_ttm": round(non_aws_ttm, 3), "ev_aws": round(aws_rr * 10, 1),
             "ev_rest": round(non_aws_ttm * 2.2, 1), "ev": round(ev10, 1), "fv": round(fv10, 2), "fv13": round(fv13, 2),
             "fv_sin_deuda": round(ev10 / SHARES, 2),
             "stakes_per_share": round((BAL["anthropic"] + BAL["openai"]) / SHARES, 2)}

# ---------------------------------------------------------------------------
# 6) REVERSIÓN — ventana limpia: P/E sobre EPS TTM SIN MARCAS en los últimos 4 cierres trimestrales
# ---------------------------------------------------------------------------
qe_px = {"4T25": 230.82, "1T26": 208.27, "2T26": 238.34, "3T26": 249.15,
         "4T24": 219.39, "1T25": 190.26, "2T25": 219.39, "3T25": 219.57}
win = []
for i in range(4, 8):
    eps_ttm = sum(core_eps_q[i - 3:i + 1]) if i >= 3 else None
    win.append((q_labels[i], qe_px[q_labels[i]], eps_ttm, qe_px[q_labels[i]] / eps_ttm))
# ventana larga (8 cierres) necesita EPS core del 1T24-3T24: se reconstruye con la misma fórmula
pre = {"1T24": (10.431, -2.673, 10.670), "2T24": (13.485, -0.018, 10.708), "3T24": (15.328, -0.027, 10.735)}
pre_eps = [(n - o * (1 - TAX)) / s for n, o, s in pre.values()]
all_eps = pre_eps + core_eps_q            # 1T24 .. 3T26 (11 trimestres)
labels_all = ["1T24", "2T24", "3T24"] + q_labels
win8 = []
for i in range(3, 11):
    eps_ttm = sum(all_eps[i - 3:i + 1])
    lab = labels_all[i]
    win8.append((lab, qe_px[lab], eps_ttm, qe_px[lab] / eps_ttm))
pe4 = sum(w[3] for w in win) / 4
pe8 = sum(w[3] for w in win8) / 8
R["rev"] = {"window": [(w[0], w[1], round(w[2], 2), round(w[3], 1)) for w in win],
            "window8": [(w[0], w[1], round(w[2], 2), round(w[3], 1)) for w in win8],
            "pe4": round(pe4, 2), "pe8": round(pe8, 2), "eps_core_ttm": round(TTM["core_eps"], 2),
            "fv": round(pe4 * TTM["core_eps"], 2), "fv8": round(pe8 * TTM["core_eps"], 2)}

# ---------------------------------------------------------------------------
# 7) CONSENSO y BLEND (7.5% DCF + 7.5% SOTP + 25% comps + 35% reversión + 25% consenso)
# ---------------------------------------------------------------------------
CONS = 326.99
methods = {"DCF Base": fvs["Base"], "SOTP": R["sotp"]["fv"], "Comparables": R["comps"]["fv"],
           "Reversión": R["rev"]["fv"], "Consenso": CONS}
blend = sum(methods[k] * W[k] for k in W)
R["methods"] = {k: round(v, 2) for k, v in methods.items()}
R["contrib"] = {k: round(methods[k] * W[k], 2) for k in W}
R["blend"] = round(blend, 2)
R["blend_vs_price"] = round((blend / PRICE - 1) * 100, 1)
R["blend_vs_sep"] = round((blend / 283.47 - 1) * 100, 1)
R["blend_simple"] = round(sum(methods.values()) / 5, 2)
R["price"] = PRICE
R["price_vs_sep"] = round((PRICE / SEP_PRICE - 1) * 100, 1)
R["reaction"] = round((PRICE_POST / PRICE_PRE - 1) * 100, 1)
R["mcap"] = round(PRICE * SHARES_OUT, 1)
R["method_vs_price"] = {k: round((v / PRICE - 1) * 100, 1) for k, v in methods.items()}

if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resultados.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(R, fh, ensure_ascii=False, indent=1)
    print(json.dumps(R, ensure_ascii=False, indent=1))
