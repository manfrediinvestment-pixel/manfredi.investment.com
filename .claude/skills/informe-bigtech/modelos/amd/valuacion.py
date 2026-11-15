"""
Modelo de valuación AMD — actualización al 3T 2026 (trimestre cerrado 26-sep-2026; 8-K del 3-nov-2026, 10-Q del 4-nov-2026).

Correr:  python valuacion.py      (imprime todo y escribe resultados.json al lado)

Fuentes (verificadas contra el documento original):
  - 8-K Ex. 99.1 del 3-nov-2026: resultados, segmentos, conciliación GAAP/no-GAAP, flujo de caja, balance, guía 4T26.
  - 10-Q del 3T26: Nota 14 (warrants de clientes: pasivo $1.2B, valor razonable $178.58/acción, "most market conditions
    had been met"), impuestos (beneficio discreto por compensación en acciones $772M en el 3T), Nota 9 (deuda), adquisiciones
    pendientes (Taalas ~$2.9B efectivo + acciones; World Labs ~$8.2B solo acciones), recompras ($9.2B disponibles).
  - SEC companyfacts XBRL: OCF/capex trimestrales, acciones diluidas.
  - Yahoo Finance chart API: cierre 13-nov-2026 $534.06; cierres de fin de trimestre; ^TNX 5.154% al 13-nov-2026.
  - stockanalysis.com (S&P Global), 15-nov-2026: PT promedio $657.74 (54 analistas, $525-$1,250); FY26E ingresos $52.23B,
    EPS no-GAAP $8.08; FY27E ingresos $95.88B, EPS $17.69. Peers en ../peers_semis_3t26.json (mismo archivo para toda la ronda).

Convención del DCF (la de septiembre, reconstruida):
  - Año 0 = ingresos FY2026E; 5 años explícitos (FY2027-FY2031).
  - Crecimiento año 1 → año 5 con decaimiento GEOMÉTRICO; margen de FCF año 1 → año 5 lineal.
  - FCF descontado a fin de año; VT = FCF5 x (1+g)/(WACC-g); equity = EV + caja neta; ÷ acciones diluidas por escenario.
  - Con esta convención el Bull de septiembre reproduce $400.1 (publicado $400); el Base da $230.3 (publicado $226, +1.9%) y
    el Bear $88.6 (publicado $85, +4.2%). Septiembre no documentó la trayectoria año por año; con interpolación lineal da
    $91.9/$246.3/$451.6, más lejos. La diferencia es de redondeo de una trayectoria no publicada, no de inputs.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))

def geo(a, b, n=5):
    return [a * (b / a) ** (i / (n - 1)) for i in range(n)]

def lin(a, b, n=5):
    return [a + (b - a) * i / (n - 1) for i in range(n)]

def dcf(rev0, g, m, wacc, gt, net_cash, shares):
    r, revs, fcf = rev0, [], []
    for gi, mi in zip(geo(*g), lin(*m)):
        r *= 1 + gi
        revs.append(r)
        fcf.append(r * mi)
    pv = sum(f / (1 + wacc) ** (i + 1) for i, f in enumerate(fcf))
    pvtv = fcf[-1] * (1 + gt) / (wacc - gt) / (1 + wacc) ** 5
    ev = pv + pvtv
    return {"fv": (ev + net_cash) / shares, "tv_share": pvtv / ev, "fcf": fcf, "revs": revs, "ev": ev}

R = {}

# ---------------------------------------------------------------------------
# 1) REPRODUCCIÓN DE SEPTIEMBRE (datos al 2T26, precio $459.61 al 1-sep-2026)
# ---------------------------------------------------------------------------
SEP = dict(rev0=50.81, net_cash=9.89)
sep_cases = {
    "Bear": dict(g=(0.20, 0.06), m=(0.185, 0.20), wacc=0.135, gt=0.03, sh=1.72),
    "Base": dict(g=(0.38, 0.12), m=(0.21, 0.275), wacc=0.115, gt=0.04, sh=1.81),
    "Bull": dict(g=(0.55, 0.14), m=(0.22, 0.315), wacc=0.105, gt=0.045, sh=1.95),
}
sep_pub = {"Bear": 85, "Base": 226, "Bull": 400}
R["sep_repro"] = {}
for k, c in sep_cases.items():
    r = dcf(SEP["rev0"], c["g"], c["m"], c["wacc"], c["gt"], SEP["net_cash"], c["sh"])
    R["sep_repro"][k] = {"modelo": round(r["fv"], 2), "publicado": sep_pub[k], "dif_pct": round((r["fv"] / sep_pub[k] - 1) * 100, 1),
                         "tv_share": round(r["tv_share"] * 100, 1), "fcf1": round(r["fcf"][0], 2)}
SEP_M = {"DCF Base": 226, "SOTP": 232, "Comparables": 244, "Reversión": 246, "Consenso": 613.84}
W = {"DCF Base": 0.075, "SOTP": 0.075, "Comparables": 0.25, "Reversión": 0.35, "Consenso": 0.25}
R["sep_blend_simple"] = round(sum(SEP_M.values()) / 5, 2)                       # $312 publicado
R["sep_blend_publicado_custom"] = round(0.15 * (226 + 244 + 246) + 0.275 * (232 + 613.84), 2)   # ~$340 publicado
R["sep_blend_regla_vigente"] = round(sum(SEP_M[k] * W[k] for k in W), 2)

# ---------------------------------------------------------------------------
# 2) DATOS DEL 3T26 (miles de millones USD)
# ---------------------------------------------------------------------------
PRICE, PRICE_SEP = 534.06, 459.61
PRICE_REPORT, PRICE_POST = 483.90, 488.78       # cierres 3-nov (reporte tras el cierre) y 4-nov-2026
HI52, LO52 = 658.52, 188.22
TSY10 = 5.154
q = ["3T25", "4T25", "1T26", "2T26", "3T26"]
rev = [9.246, 10.270, 10.253, 11.536, 13.377]
gp = [4.780, 5.577, 5.416, 6.203, 7.210]
opi = [1.270, 1.752, 1.476, 1.990, 2.832]
ni = [1.243, 1.511, 1.383, 2.297, 2.428]
eps = [0.75, 0.92, 0.84, 1.38, 1.46]
eps_ng = [1.20, 1.53, 1.37, 1.66, 2.09]
ocf_c = [1.788, 2.304, 2.955, 2.366, 1.202]       # OCF de operaciones continuas (XBRL / 8-K)
capex = [0.258, 0.222, 0.389, 0.808, 0.648]
dil = [1.641, 1.643, 1.650, 1.659, 1.661]
seg_rev = {"Data Center": (8.546, 4.341, 6.718), "Client": (2.949, 2.750, 3.062), "Gaming": (0.773, 1.298, 0.779),
           "Embedded": (1.109, 0.857, 0.977)}
seg_oi = {"Data Center": (2.882, 1.074), "Client y Gaming": (0.573, 0.867), "Embedded": (0.453, 0.283)}
dc_hist = [3.674, 3.240, 4.341, 5.380, 5.775, 6.718, 8.546]      # 1T25..3T26 (1T25-4T25 de 8-K previos, 1T26 = 9M-2T-3T)
dc_hist[4] = 21.039 - 6.718 - 8.546
R["dc_1t26"] = round(dc_hist[4], 3)

ttm = lambda a: sum(a[1:5])
TTM = dict(rev=ttm(rev), gp=ttm(gp), opi=ttm(opi), ni=ttm(ni), eps=ttm(eps), eps_ng=ttm(eps_ng), ocf=ttm(ocf_c), capex=ttm(capex))
TTM["fcf"] = TTM["ocf"] - TTM["capex"]
for k in ("gp", "opi", "ni", "ocf", "fcf", "capex"):
    TTM[k + "_m"] = TTM[k] / TTM["rev"] * 100
# TTM hace un año (4T24+1T25+2T25+3T25) para la variación TTM vs TTM
TTM_YA = 7.658 + 7.438 + 7.685 + 9.246
TTM["rev_yoy"] = (TTM["rev"] / TTM_YA - 1) * 100
R["ttm"] = {k: round(v, 3) for k, v in TTM.items()}
R["q3"] = dict(rev_yoy=round((13.377 / 9.246 - 1) * 100, 1), rev_qoq=round((13.377 / 11.536 - 1) * 100, 1),
               gm=round(7.210 / 13.377 * 100, 1), om=round(2.832 / 13.377 * 100, 1), ocf_m=round(1.202 / 13.377 * 100, 1),
               fcf=round(1.202 - 0.648, 3), dc_yoy=round((8.546 / 4.341 - 1) * 100, 1), dc_share=round(8.546 / 13.377 * 100, 1),
               dc_m=round(2.882 / 8.546 * 100, 1), emb_yoy=round((1.109 / 0.857 - 1) * 100, 1), emb_m=round(0.453 / 1.109 * 100, 1),
               cg_m=round(0.573 / 3.722 * 100, 1), gaming_yoy=round((0.773 / 1.298 - 1) * 100, 1),
               client_yoy=round((2.949 / 2.750 - 1) * 100, 1), seg_sum=round(2.882 + 0.573 + 0.453, 3))
R["quarters"] = {lab: dict(rev=rev[i], gm=round(gp[i] / rev[i] * 100, 1), om=round(opi[i] / rev[i] * 100, 1),
                           ocf_m=round(ocf_c[i] / rev[i] * 100, 1)) for i, lab in enumerate(q)}

# EPS GAAP normalizado (Método 3): saca warrants, ganancias de inversiones y el beneficio fiscal discreto del 3T
q3_norm_ni = 2.428 + 1.097 - 0.067 - 0.772
EPS_NORM = 0.92 + (0.84 - 0.04) + (1.38 - 0.34) + q3_norm_ni / 1.661   # 1T26: ganancia $66M; 2T26: -$0.34 como en sep
R["eps_norm"] = dict(q3_norm_ni=round(q3_norm_ni, 3), q3_norm_eps=round(q3_norm_ni / 1.661, 3), ttm=round(EPS_NORM, 3))

# Balance al 26-sep-2026
BAL = dict(cash=7.404, sti=8.372, debt=7.079, debt_prev=3.226, goodwill=25.470, assets=94.812, equity=68.389,
           inv=11.463, ar=9.209, inv_dec=7.920, ar_dec=6.315, warrant_liab=1.2)
BAL["liq"] = BAL["cash"] + BAL["sti"]
BAL["net_cash"] = BAL["liq"] - BAL["debt"]
R["bal"] = {k: round(v, 3) for k, v in BAL.items()}

# Guía 4T26
G = dict(q4_mid=17.0, q4_lo=17.0 * 0.97, q4_hi=17.0 * 1.03, gm_ng=55)
G["q4_yoy"] = (17.0 / 10.270 - 1) * 100
G["q4_qoq"] = (17.0 / 13.377 - 1) * 100
G["fy26_impl"] = 35.166 + 17.0
G["fy26_yoy"] = (G["fy26_impl"] / 34.639 - 1) * 100
G["q4_run_rate"] = 17.0 * 4
R["guide"] = {k: round(v, 2) for k, v in G.items()}

# ---------------------------------------------------------------------------
# 3) CONSENSO Y PEERS (mismo archivo para toda la ronda de semis)
# ---------------------------------------------------------------------------
P = json.load(open(os.path.join(HERE, "..", "peers_semis_3t26.json")))
C = P["AMD"]
R["consenso"] = dict(pt=C["pt"], n=C["n"], lo=C["lo"], hi=C["hi"], rating=C["rating"], eps26=round(C["eps_this"], 2),
                     eps27=round(C["eps_next"], 2), rev26=round(C["rev_this"], 2), rev27=round(C["rev_next"], 2),
                     rev27_g=round((C["rev_next"] / C["rev_this"] - 1) * 100, 1), eps27_g=round((C["eps_next"] / C["eps_this"] - 1) * 100, 1),
                     eps26_g=round((C["eps_this"] / 4.17 - 1) * 100, 1), rev26_g=round((C["rev_this"] / 34.639 - 1) * 100, 1),
                     upside=round((C["pt"] / PRICE - 1) * 100, 1))
# P/E sobre el año fiscal que mejor coincide con el calendario 2027
pe27 = {"NVDA": P["NVDA"]["price"] / P["NVDA"]["eps_next"],    # FY ene-2028
        "AVGO": P["AVGO"]["price"] / P["AVGO"]["eps_next"],    # FY oct-2027
        "MRVL": P["MRVL"]["price"] / P["MRVL"]["eps_next"],    # FY ene-2028
        "QCOM": P["QCOM"]["price"] / P["QCOM"]["eps_this"]}    # FY sep-2027
R["pe27"] = {k: round(v, 2) for k, v in pe27.items()}
ai_avg = (pe27["NVDA"] + pe27["AVGO"] + pe27["MRVL"]) / 3
all_avg = sum(pe27.values()) / 4
EPS27 = C["eps_next"]
R["comps"] = dict(ai_avg=round(ai_avg, 2), all_avg=round(all_avg, 2), eps27=round(EPS27, 2),
                  fv_ai=round(ai_avg * EPS27, 2), fv_nvda=round(pe27["NVDA"] * EPS27, 2), fv_all=round(all_avg * EPS27, 2),
                  amd_pe26=round(PRICE / C["eps_this"], 2), amd_pe27=round(PRICE / EPS27, 2))
COMPS = R["comps"]["fv_ai"]

# ---------------------------------------------------------------------------
# 4) REVERSIÓN — ventana de los últimos 4 cierres de trimestre (EPS GAAP TTM reportado en cada fecha)
# ---------------------------------------------------------------------------
win = [("27-dic-2025", 214.99, 0.54 + 0.75 + 0.92 + 0.44), ("28-mar-2026", 201.99, 0.75 + 0.92 + 0.84 + 0.54),
       ("27-jun-2026", 521.58, 0.75 + 0.92 + 0.84 + 1.38), ("26-sep-2026", 630.63, 0.92 + 0.84 + 1.38 + 1.46)]
# (el EPS TTM al 27-dic-2025 es FY2025 = 0.44+0.54+0.75+0.92 = 2.65; al 28-mar-2026 = 0.54+0.75+0.92+0.84 = 3.05)
win[0] = ("27-dic-2025", 214.99, 0.44 + 0.54 + 0.75 + 0.92)
win[1] = ("28-mar-2026", 201.99, 0.54 + 0.75 + 0.92 + 0.84)
pes = [(d, p, round(e, 2), p / e) for d, p, e in win]
pe_avg = sum(x[3] for x in pes) / 4
pe_avg_ex = (pes[0][3] + pes[1][3]) / 2            # criterio de sep: sin los cierres de "pico"
REV_FV = pe_avg * EPS_NORM
R["reversion"] = dict(window=[(d, p, e, round(x, 1)) for d, p, e, x in pes], pe_avg=round(pe_avg, 2), eps_norm=round(EPS_NORM, 3),
                      fv=round(REV_FV, 2), pe_avg_ex_picos=round(pe_avg_ex, 2), fv_ex_picos=round(pe_avg_ex * EPS_NORM, 2),
                      fv_lo=round(min(x[3] for x in pes) * EPS_NORM, 2), fv_hi=round(max(x[3] for x in pes) * EPS_NORM, 2),
                      pe_now_reported=round(PRICE / TTM["eps"], 1), pe_now_norm=round(PRICE / EPS_NORM, 1))

# ---------------------------------------------------------------------------
# 5) DCF — año 0 = FY2026E (9M reales + 4T guiado = consenso), año 1 = FY2027
# ---------------------------------------------------------------------------
REV0 = round(C["rev_this"], 2)                        # 52.23
ke_spread = 11.5 - 4.8                                 # beta x ERP implícito de septiembre (6.7 pp)
WACC_BASE = round(TSY10 + ke_spread, 1) / 100          # 11.9%
cases = {
    "Bear": dict(g=(0.45, 0.06), m=(0.15, 0.20), wacc=WACC_BASE + 0.02, gt=0.03, sh=1.74),
    "Base": dict(g=(0.80, 0.10), m=(0.18, 0.28), wacc=WACC_BASE, gt=0.04, sh=1.86),
    "Bull": dict(g=(1.00, 0.14), m=(0.20, 0.32), wacc=WACC_BASE - 0.01, gt=0.045, sh=2.00),
}
R["dcf"] = {}
for k, c in cases.items():
    r = dcf(REV0, c["g"], c["m"], c["wacc"], c["gt"], BAL["net_cash"], c["sh"])
    R["dcf"][k] = dict(fv=round(r["fv"], 2), tv_share=round(r["tv_share"] * 100, 1), fcf1=round(r["fcf"][0], 2),
                       fcf5=round(r["fcf"][-1], 2), rev1=round(r["revs"][0], 2), rev5=round(r["revs"][-1], 2),
                       g_path=[round(x * 100, 1) for x in geo(*c["g"])], m_path=[round(x * 100, 1) for x in lin(*c["m"])],
                       wacc=round(c["wacc"] * 100, 2), gt=c["gt"] * 100, sh=c["sh"])
fv = {k: R["dcf"][k]["fv"] for k in cases}
R["dcf_simple"] = round(sum(fv.values()) / 3, 2)
R["dcf_prob"] = round(0.25 * fv["Bear"] + 0.45 * fv["Base"] + 0.30 * fv["Bull"], 2)
DCF = fv["Base"]

b = cases["Base"]
grid_w = [WACC_BASE - 0.01, WACC_BASE, WACC_BASE + 0.01, WACC_BASE + 0.02, WACC_BASE + 0.03]
grid_g = [0.03, 0.035, 0.04, 0.045, 0.05]
R["grid"] = {"wacc": [round(w * 100, 1) for w in grid_w], "g": [x * 100 for x in grid_g],
             "fv": [[round(dcf(REV0, b["g"], b["m"], w, gg, BAL["net_cash"], b["sh"])["fv"]) for gg in grid_g] for w in grid_w]}

# DCF inverso: (a) CAGR constante 5 años con la senda de margen del Base; (b) margen plano con la senda de crecimiento Base
def solve(f, lo, hi):
    for _ in range(200):
        mid = (lo + hi) / 2
        if f(mid) < PRICE: lo = mid
        else: hi = mid
    return mid
def fv_cagr(cg):
    r, fc = REV0, []
    for mi in lin(*b["m"]):
        r *= 1 + cg; fc.append(r * mi)
    pv = sum(x / (1 + b["wacc"]) ** (i + 1) for i, x in enumerate(fc))
    tv = fc[-1] * (1 + b["gt"]) / (b["wacc"] - b["gt"]) / (1 + b["wacc"]) ** 5
    return (pv + tv + BAL["net_cash"]) / b["sh"]
def fv_margin(mm):
    return dcf(REV0, b["g"], (mm, mm), b["wacc"], b["gt"], BAL["net_cash"], b["sh"])["fv"]
cg = solve(fv_cagr, 0.0, 2.0)
mm = solve(fv_margin, 0.0, 1.0)
R["inverse"] = dict(cagr=round(cg * 100, 1), rev5=round(REV0 * (1 + cg) ** 5, 1), margin=round(mm * 100, 1))

# ---------------------------------------------------------------------------
# 6) SOTP — negocio maduro + Instinct (estimación propia derivada del consenso)
# ---------------------------------------------------------------------------
dc26 = 21.039 + 12.5           # 9M real + 4T estimado (17.0 guiado menos ~4.5 de Client, Gaming y Embedded)
inst26 = dc26 - 12.5           # EPYC ~12.5 en FY26 (propio)
mature26 = REV0 - inst26
nondc27 = 2.949 * 4 * 1.04 + 0.773 * 4 + 1.109 * 4 * 1.05
epyc27 = 12.5 * 1.35
inst27 = C["rev_next"] - nondc27 - epyc27
S = dict(dc26=dc26, inst26=inst26, mature26=mature26, inst27=inst27, epyc27=epyc27, nondc27=nondc27)
S["ev_mature"] = mature26 * 4.5
S["ev_inst_cons"] = inst27 * 8
S["ev_inst_bull"] = inst27 * 12
S["fv_cons"] = (S["ev_mature"] + S["ev_inst_cons"] + BAL["net_cash"]) / 1.86
S["fv_bull"] = (S["ev_mature"] + S["ev_inst_bull"] + BAL["net_cash"]) / 2.00
S["fv_bull_nodil"] = (S["ev_mature"] + S["ev_inst_bull"] + BAL["net_cash"]) / 1.661
R["sotp"] = {k: round(v, 2) for k, v in S.items()}
SOTP = round(S["fv_cons"], 2)

# ---------------------------------------------------------------------------
# 7) BLEND (regla vigente 7.5/7.5/25/35/25)
# ---------------------------------------------------------------------------
M = {"DCF Base": DCF, "SOTP": SOTP, "Comparables": COMPS, "Reversión": round(REV_FV, 2), "Consenso": C["pt"]}
blend = sum(M[k] * W[k] for k in W)
R["methods"] = M
R["blend"] = round(blend, 2)
R["blend_gap"] = round((blend / PRICE - 1) * 100, 1)
R["blend_simple"] = round(sum(M.values()) / 5, 2)
R["blend_sin_consenso"] = round(sum(M[k] * W[k] for k in W if k != "Consenso") / (1 - W["Consenso"]), 2)
R["blend_sep_regla"] = R["sep_blend_regla_vigente"]
R["cambio_vs_sep_regla"] = round((blend / R["sep_blend_regla_vigente"] - 1) * 100, 1)
R["price"] = dict(now=PRICE, sep=PRICE_SEP, chg=round((PRICE / PRICE_SEP - 1) * 100, 1), hi52=HI52, lo52=LO52,
                  off_hi=round((PRICE / HI52 - 1) * 100, 1), mcap=round(PRICE * 1.640, 1),
                  pe_ttm=round(PRICE / TTM["eps"], 1), ps_ttm=round(PRICE * 1.661 / TTM["rev"], 1),
                  pfcf=round(PRICE * 1.661 / TTM["fcf"], 1))

json.dump(R, open(os.path.join(HERE, "resultados.json"), "w"), indent=1, ensure_ascii=False)
if __name__ == "__main__":
    for k, v in R.items():
        print(k, "=>", v)
