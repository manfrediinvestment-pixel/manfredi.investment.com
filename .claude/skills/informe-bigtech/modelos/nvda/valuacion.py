"""
Modelo de valuación NVDA — actualización al 3T FY2027 (trimestre cerrado 25-oct-2026; 8-K del 17-nov-2026 con
comunicado Ex. 99.1, comentario de la CFO Ex. 99.2 e información suplementaria Ex. 99.3). El 10-Q todavía no estaba presentado.

Correr:  python valuacion.py      (imprime todo y escribe resultados.json al lado, UTF-8)

Fuentes (verificadas contra el documento original):
  - 8-K 17-nov-2026 (Ex. 99.1/99.2/99.3): resultados, balance, flujo de caja, conciliación GAAP/no-GAAP, plataformas,
    compromisos ($390B suministro, $118B garantías), concentración de clientes, DSO, guía 4T FY27.
  - 8-K 11/12-nov-2026: renuncia de Jensen Huang, Colette Kress CEO interina, Harvey C. Jones presidente del directorio.
  - 8-K 2-sep-2026: adquisición de Hugging Face (~$11.9B + hasta ~$1.0B de retención).
  - 8-K de 1T FY27 (20-may-2026) y 2T FY27 (26-ago-2026): EPS no-GAAP reexpresado con compensación en acciones
    (1T26 0.78, 2T26 1.01, 3T26 1.27, 4T26 1.59, 1T27 1.87, 2T27 2.22) y el 4T FY26 standalone.
  - Yahoo Finance chart API: cierre 17-nov-2026 $155.46; cierres de fin de trimestre fiscal; ^TNX 5.103% al 17-nov-2026.
  - stockanalysis.com (S&P Global), bajado 18-nov-2026: PT promedio $247.76 (55 PT, 61 analistas, $130-$425);
    FY27E ingresos $424.04B, EPS $9.65; FY28E ingresos $723.91B, EPS $16.61.
  - Peers: ../peers_semis_3t26.json (cierre 13-nov-2026, mismo archivo de toda la ronda de semis).

Convención del DCF:
  - Año 0 = FY2027E (9M reales + 4T guiado ≈ consenso $424.04B); 5 años explícitos FY2028-FY2032.
  - Trayectorias AÑO POR AÑO explícitas (crecimiento, margen de OCF, capex/ingresos), documentadas en el informe.
  - FCF = OCF − capex, descontado a fin de año; VT = FCF5 x (1+g)/(WACC−g); equity = EV + caja neta; ÷ acciones diluidas.
  - El DCF de agosto (Base $205.49) NO se puede reproducir exacto: no documentó la forma de la trayectoria. Con
    decaimiento geométrico del crecimiento y margen lineal da Bear $99.31 / Base $221.48 / Bull $425.54 (FCF año 1
    idéntico al publicado, +3.9%/+7.8%/+12.0%). La diferencia es de trayectoria no publicada, no de inputs.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
R = {}

def lin(a, b, n=5):
    return [a + (b - a) * i / (n - 1) for i in range(n)]

def geo(a, b, n=5):
    return [a * (b / a) ** (i / (n - 1)) for i in range(n)]

def dcf(rev0, g, m, c, wacc, gt, net_cash, shares):
    r, revs, fcf = rev0, [], []
    for gi, mi, ci in zip(g, m, c):
        r *= 1 + gi
        revs.append(r)
        fcf.append(r * (mi - ci))
    pv = sum(f / (1 + wacc) ** (i + 1) for i, f in enumerate(fcf))
    pvtv = fcf[-1] * (1 + gt) / (wacc - gt) / (1 + wacc) ** 5
    ev = pv + pvtv
    return {"fv": (ev + net_cash) / shares, "tv_share": pvtv / ev, "fcf": fcf, "revs": revs, "ev": ev}

# ---------------------------------------------------------------------------
# 1) INTENTO DE REPRODUCCIÓN DE AGOSTO (datos al 2T FY27, precio $217.79)
# ---------------------------------------------------------------------------
AUG = {"Bear": ((.32, .07), (.36, .42), (.035, .05), .113, .025, 95.61),
       "Base": ((.52, .12), (.45, .50), (.03, .04), .103, .03, 205.49),
       "Bull": ((.68, .17), (.49, .54), (.025, .035), .093, .035, 380.05)}
R["aug_repro"] = {}
for k, (g, m, c, w, gt, pub) in AUG.items():
    r = dcf(302.97, geo(*g), lin(*m), lin(*c), w, gt, 66.0, 24.285)
    R["aug_repro"][k] = dict(modelo=round(r["fv"], 2), publicado=pub, dif_pct=round((r["fv"] / pub - 1) * 100, 1),
                             fcf1=round(r["fcf"][0], 1))
AUG_M = {"DCF Base": 205.49, "Comparables": 381.32, "Reversión": 397.75, "Consenso": 325.99}
W = {"DCF Base": 0.15, "Comparables": 0.25, "Reversión": 0.35, "Consenso": 0.25}
R["aug_blend_simple_publicado"] = round(sum(AUG_M.values()) / 4, 2)          # $327.64 publicado
R["aug_blend_regla_vigente"] = round(sum(AUG_M[k] * W[k] for k in W), 2)

# ---------------------------------------------------------------------------
# 2) DATOS (miles de millones USD salvo por acción)
# ---------------------------------------------------------------------------
PRICE, PRICE_AUG = 155.46, 217.79          # cierre 17-nov-2026 (reportó tras el cierre) / precio del informe de agosto
PRICE_1811 = 151.62                         # 18-nov-2026 (sesión del día siguiente al reporte)
HI52, HI52_DATE = 239.24, "6-oct-2026"     # máximo de cierre 52 semanas
TSY10 = 5.103
q = ["3T FY26", "4T FY26", "1T FY27", "2T FY27", "3T FY27"]
rev = [57.006, 68.127, 81.615, 96.222, 115.844]
gp = [41.849, 51.093, 61.157, 72.142, 86.676]
opi = [36.010, 44.299, 53.536, 63.734, 77.520]
ni = [31.910, 42.960, 58.321, 59.688, 65.287]
eps = [1.30, 1.76, 2.39, 2.46, 2.70]
eps_ng = [1.27, 1.59, 1.87, 2.22, 2.68]      # no-GAAP reexpresado (incluye compensación en acciones)
ocf = [23.750, 36.190, 50.344, 24.077, 48.253]
capex = [1.637, 1.284, 1.757, 2.677, 4.422]   # compras de PP&E e intangibles
fcf_co = [22.089, 34.902, 48.554, 21.341, 43.777]  # FCF según NVIDIA (resta también pagos de principal)
rd = [4.705, None, 6.32, 7.05, 7.454]
dil = [24.483, 24.432, 24.391, 24.285, 24.186]

ttm = lambda a: sum(a[1:5])
TTM = dict(rev=ttm(rev), gp=ttm(gp), opi=ttm(opi), ni=ttm(ni), eps=ttm(eps), eps_ng=ttm(eps_ng), ocf=ttm(ocf),
           capex=ttm(capex), fcf_co=ttm(fcf_co))
TTM["fcf"] = TTM["ocf"] - TTM["capex"]
for k in ("gp", "opi", "ni", "ocf", "fcf", "capex", "fcf_co"):
    TTM[k + "_m"] = TTM[k] / TTM["rev"] * 100
TTM_YA = 39.331 + 147.811                      # 4T FY25 + 9M FY26
TTM["rev_yoy"] = (TTM["rev"] / TTM_YA - 1) * 100
R["ttm"] = {k: round(v, 3) for k, v in TTM.items()}
R["ttm_aug_eps_ng_correcto"] = round(1.27 + 1.59 + 1.87 + 2.22, 2)   # agosto publicó $7.01 (usaba 4T26 sin reexpresar)

R["q3"] = dict(rev_yoy=round((115.844 / 57.006 - 1) * 100, 1), rev_qoq=round((115.844 / 96.222 - 1) * 100, 1),
               gm=round(86.676 / 115.844 * 100, 1), om=round(77.520 / 115.844 * 100, 1), nm=round(65.287 / 115.844 * 100, 1),
               ocf_m=round(48.253 / 115.844 * 100, 1), rd_pct=round(7.454 / 115.844 * 100, 1),
               dc=107.6, dc_yoy=round((107.6 / 51.2 - 1) * 100, 1), dc_qoq=round((107.6 / 89.0 - 1) * 100, 1),
               dc_share=round(107.6 / 115.844 * 100, 1), hyp=60.1, hyp_yoy=round((60.1 / 35.1 - 1) * 100, 1),
               hyp_qoq=round((60.1 / 48.7 - 1) * 100, 1), acie=47.5, acie_yoy=round((47.5 / 16.1 - 1) * 100, 1),
               acie_qoq=round((47.5 / 40.3 - 1) * 100, 1), edge=8.2, edge_yoy=round((8.2 / 5.8 - 1) * 100, 1),
               edge_qoq=round((8.2 / 7.2 - 1) * 100, 1), hyp_share=round(60.1 / 115.844 * 100, 1),
               acie_share=round(47.5 / 115.844 * 100, 1), edge_share=round(8.2 / 115.844 * 100, 1),
               ni_yoy=round((65.287 / 31.910 - 1) * 100, 1), eps_ng_yoy=round((2.68 / 1.27 - 1) * 100, 1),
               rev_surprise=round((115.844 / 109.15 - 1) * 100, 1), eps_surprise=round((2.68 / 2.47 - 1) * 100, 1),
               ocf_qoq=round((48.253 / 24.077 - 1) * 100, 1), china_hq=11.050, china_share=round(11.050 / 115.844 * 100, 1),
               us_share=round(72.899 / 115.844 * 100, 1), taiwan_share=round(30.295 / 115.844 * 100, 1))
R["quarters"] = {lab: dict(rev=rev[i], gm=round(gp[i] / rev[i] * 100, 1), om=round(opi[i] / rev[i] * 100, 1),
                           ocf_m=round(ocf[i] / rev[i] * 100, 1), eps_ng=eps_ng[i]) for i, lab in enumerate(q)}

# Balance al 25-oct-2026 (y 26-jul-2026 del informe de agosto)
BAL = dict(cash=29.089, debt_sec=24.423, eq_sec=44.219, ar=81.033, inv=39.724, ppe=19.227, nonmkt=65.528,
           goodwill=26.451, assets=372.188, liab=105.522, equity=266.666, ltd=32.371, std=0.0,
           ap=21.074, lt_locked=4.669, lockup_short=21.0)
BAL["liq"] = BAL["cash"] + BAL["debt_sec"] + BAL["eq_sec"]
BAL["net_cash"] = BAL["liq"] - BAL["ltd"] - BAL["std"]
BAL["cash_debt"] = BAL["cash"] + BAL["debt_sec"]
BAL["portfolio"] = BAL["eq_sec"] + BAL["nonmkt"] + BAL["lt_locked"]
JUL = dict(liq=99.37, net_cash=66.00, ar=63.1, inv=31.58, nonmkt=51.16, eq_sec=42.78, ltd=32.37, std=1.00, equity=228.98)
BAL["ar_qoq"] = (BAL["ar"] / JUL["ar"] - 1) * 100
BAL["inv_qoq"] = (BAL["inv"] / JUL["inv"] - 1) * 100
BAL["ar_vs_jan"] = (BAL["ar"] / 38.466 - 1) * 100
BAL["inv_vs_jan"] = (BAL["inv"] / 21.403 - 1) * 100
BAL["nonmkt_vs_jan"] = BAL["nonmkt"] / 22.251
R["bal"] = {k: round(v, 3) for k, v in BAL.items()}

# Retorno de capital 3T y 9M
CAP = dict(bb_q3=22.122, div_q3=6.026, bb_9m=61.166, div_9m=12.316)
CAP["ret_q3"] = CAP["bb_q3"] + CAP["div_q3"]
CAP["ret_9m"] = CAP["bb_9m"] + CAP["div_9m"]
CAP["ret_q3_vs_fcf"] = CAP["ret_q3"] / 43.777 * 100
R["cap"] = {k: round(v, 3) for k, v in CAP.items()}

# Guía 4T FY27 (incluye una semana extra)
G = dict(q4=130.0, q4_lo=130 * 0.97, q4_hi=130 * 1.03, gm_lo=71.0, gm_hi=72.0, opex=11.0)
G["q4_yoy"] = (130.0 / 68.127 - 1) * 100
G["q4_qoq"] = (130.0 / 115.844 - 1) * 100
G["fy27_impl"] = 293.681 + 130.0
G["fy27_yoy"] = (G["fy27_impl"] / 215.938 - 1) * 100
G["fy28_75"] = G["fy27_impl"] * 1.75
R["guide"] = {k: round(v, 2) for k, v in G.items()}

# ---------------------------------------------------------------------------
# 3) CONSENSO (S&P Global vía stockanalysis.com, 18-nov-2026)
# ---------------------------------------------------------------------------
C = dict(pt=247.76, n=61, n_pt=55, lo=130.0, hi=425.0, median=240.0, eps27=9.65, eps28=16.61, rev27=424.04, rev28=723.91,
         sb=34, b=11, h=14, s=0, ss=2, pt_aug=325.99, eps27_aug=9.29, rev27_aug=411.25)
C["upside"] = (C["pt"] / PRICE - 1) * 100
C["rev28_g"] = (C["rev28"] / C["rev27"] - 1) * 100
C["eps28_g"] = (C["eps28"] / C["eps27"] - 1) * 100
C["pt_chg"] = (C["pt"] / C["pt_aug"] - 1) * 100
C["eps27_rev"] = (C["eps27"] / C["eps27_aug"] - 1) * 100
C["rev27_rev"] = (C["rev27"] / C["rev27_aug"] - 1) * 100
C["pe27"] = PRICE / C["eps27"]
C["pe28"] = PRICE / C["eps28"]
R["consenso"] = {k: round(v, 2) for k, v in C.items()}

# ---------------------------------------------------------------------------
# 4) COMPARABLES — P/E sobre el año fiscal que mejor coincide con el calendario 2027 (mismo criterio que la ronda)
# ---------------------------------------------------------------------------
P = json.load(open(os.path.join(HERE, "..", "peers_semis_3t26.json"), encoding="utf-8"))
TWD = 32.94
pe27 = {"AMD": P["AMD"]["price"] / P["AMD"]["eps_next"],                       # FY dic-2027
        "AVGO": P["AVGO"]["price"] / P["AVGO"]["eps_next"],                    # FY oct-2027
        "TSM": P["TSM"]["price"] / (P["TSM"]["eps_next"] * 5 / TWD)}          # FY dic-2027, ADR = 5 acciones, NT$→US$
R["pe27"] = {k: round(v, 2) for k, v in pe27.items()}
avg3 = sum(pe27.values()) / 3
avg_ex = (pe27["AVGO"] + pe27["TSM"]) / 2
COMPS = avg3 * C["eps28"]
R["comps"] = dict(avg3=round(avg3, 2), avg_ex_amd=round(avg_ex, 2), eps28=C["eps28"], fv=round(COMPS, 2),
                  fv_ex_amd=round(avg_ex * C["eps28"], 2), fv_lo=round(min(pe27.values()) * C["eps28"], 2),
                  fv_hi=round(max(pe27.values()) * C["eps28"], 2), nvda_pe28=round(C["pe28"], 2),
                  nvda_pe28_1311=round(162.85 / C["eps28"], 2))

# ---------------------------------------------------------------------------
# 5) REVERSIÓN — ventana de los últimos 4 cierres de trimestre fiscal, P/E sobre EPS no-GAAP TTM reexpresado
#     (no-GAAP porque el GAAP está contaminado por ganancias de cartera: $15.9B en 1T FY27, $7.8B en 2T FY27)
#     El cierre de ene-2026 incluye el cargo H20 de $4.5B del 1T FY26: se suma $0.15 por acción (EPS no-GAAP ex-H20
#     $0.96 vs. $0.81 informado por NVIDIA en may-2025).
# ---------------------------------------------------------------------------
win = [("23-ene-2026", 187.67, 0.78 + 1.01 + 1.27 + 1.59 + 0.15),
       ("24-abr-2026", 208.27, 1.01 + 1.27 + 1.59 + 1.87),
       ("24-jul-2026", 206.84, 1.27 + 1.59 + 1.87 + 2.22),
       ("23-oct-2026", 210.96, 1.59 + 1.87 + 2.22 + 2.68)]
pes = [(d, p, round(e, 2), p / e) for d, p, e in win]
pe_avg = sum(x[3] for x in pes) / 4
REV_FV = pe_avg * TTM["eps_ng"]
R["reversion"] = dict(window=[(d, p, e, round(x, 1)) for d, p, e, x in pes], pe_avg=round(pe_avg, 2),
                      eps_ttm=round(TTM["eps_ng"], 2), fv=round(REV_FV, 2),
                      fv_lo=round(min(x[3] for x in pes) * TTM["eps_ng"], 2), fv_hi=round(max(x[3] for x in pes) * TTM["eps_ng"], 2),
                      pe_now_ng=round(PRICE / TTM["eps_ng"], 1), pe_now_gaap=round(PRICE / TTM["eps"], 1))

# ---------------------------------------------------------------------------
# 6) DCF — año 0 = FY2027E, años FY2028-FY2032
# ---------------------------------------------------------------------------
REV0 = C["rev27"]
SPREAD = 10.3 - 4.79                       # beta x ERP implícito de agosto (5.51 pp), sin cambio de juicio
WACC_BASE = round(TSY10 + SPREAD, 1) / 100  # 10.6%
SH = 24.186                                 # acciones diluidas promedio 3T FY27
NET = BAL["net_cash"]
cases = {
    # Bear: ciclo de digestión — FY28 crece menos que la guía y FY29 cae 10% (como FY2023: ingresos planos y OCF −38%),
    # el margen de OCF retrocede al nivel de FY2026 y el capex sigue subiendo (compromisos de $390B ya firmados).
    "Bear": dict(g=[0.40, -0.10, 0.00, 0.04, 0.04], m=[0.40, 0.38, 0.37, 0.37, 0.37], c=[0.045, 0.05, 0.05, 0.05, 0.05],
                 wacc=WACC_BASE + 0.01, gt=0.025),
    # Base: FY28 = consenso (+70%, la compañía habla de ~75%), después desaceleración marcada; margen de OCF anclado en el
    # TTM real (43.9%) y capex subiendo de 2.8% a 4% de ingresos.
    "Base": dict(g=[0.70, 0.25, 0.12, 0.08, 0.06], m=[0.44, 0.45, 0.46, 0.46, 0.46], c=[0.035, 0.0375, 0.04, 0.04, 0.04],
                 wacc=WACC_BASE, gt=0.03),
    # Bull: FY28 por encima de la guía y una desaceleración más lenta; margen de OCF con normalización del cobro (DSO).
    "Bull": dict(g=[0.80, 0.35, 0.18, 0.10, 0.07], m=[0.46, 0.48, 0.49, 0.50, 0.50], c=[0.03, 0.0325, 0.035, 0.035, 0.035],
                 wacc=WACC_BASE - 0.01, gt=0.035),
}
R["dcf"] = {}
for k, c in cases.items():
    r = dcf(REV0, c["g"], c["m"], c["c"], c["wacc"], c["gt"], NET, SH)
    R["dcf"][k] = dict(fv=round(r["fv"], 2), tv_share=round(r["tv_share"] * 100, 1), fcf1=round(r["fcf"][0], 1),
                       fcf5=round(r["fcf"][-1], 1), rev1=round(r["revs"][0], 1), rev5=round(r["revs"][-1], 1),
                       revs=[round(x, 1) for x in r["revs"]], fcfs=[round(x, 1) for x in r["fcf"]],
                       g=[round(x * 100, 1) for x in c["g"]], m=[round(x * 100, 1) for x in c["m"]],
                       capex=[round(x * 100, 2) for x in c["c"]], wacc=round(c["wacc"] * 100, 1), gt=round(c["gt"] * 100, 1),
                       ev=round(r["ev"], 1), gap=round((r["fv"] / PRICE - 1) * 100, 1))
fv = {k: R["dcf"][k]["fv"] for k in cases}
R["dcf_simple"] = round(sum(fv.values()) / 3, 2)
R["dcf_prob"] = round(0.25 * fv["Bear"] + 0.45 * fv["Base"] + 0.30 * fv["Bull"], 2)
DCF = fv["Base"]

b = cases["Base"]
grid_w = [WACC_BASE - 0.01, WACC_BASE - 0.005, WACC_BASE, WACC_BASE + 0.005, WACC_BASE + 0.01]
grid_g = [0.02, 0.025, 0.03, 0.035, 0.04]
R["grid"] = {"wacc": [round(w * 100, 1) for w in grid_w], "g": [round(x * 100, 1) for x in grid_g],
             "fv": [[round(dcf(REV0, b["g"], b["m"], b["c"], w, gg, NET, SH)["fv"], 2) for gg in grid_g] for w in grid_w]}

# DCF inverso: con FY28 = consenso (+70%) fijo, ¿qué crecimiento constante FY29-FY32 justifica el precio?
def solve(f, lo, hi, target=PRICE):
    for _ in range(200):
        mid = (lo + hi) / 2
        if f(mid) < target: lo = mid
        else: hi = mid
    return mid
def fv_after(gx):
    return dcf(REV0, [0.70, gx, gx, gx, gx], b["m"], b["c"], b["wacc"], b["gt"], NET, SH)["fv"]
gx = solve(fv_after, -0.6, 0.6)
def fv_margin(mm):
    return dcf(REV0, b["g"], [mm] * 5, b["c"], b["wacc"], b["gt"], NET, SH)["fv"]
mm = solve(fv_margin, 0.0, 1.0)
rev_inv = REV0 * 1.70 * (1 + gx) ** 4
R["inverse"] = dict(g_after=round(gx * 100, 1), rev_fy32=round(rev_inv, 1), rev_fy28=round(REV0 * 1.7, 1),
                    ocf_margin_flat=round(mm * 100, 1))

# ---------------------------------------------------------------------------
# 7) BLEND (regla vigente 15/25/35/25)
# ---------------------------------------------------------------------------
M = {"DCF Base": DCF, "Comparables": round(COMPS, 2), "Reversión": round(REV_FV, 2), "Consenso": C["pt"]}
blend = sum(M[k] * W[k] for k in W)
R["methods"] = M
R["blend"] = round(blend, 2)
R["blend_gap"] = round((blend / PRICE - 1) * 100, 1)
R["blend_simple"] = round(sum(M.values()) / 4, 2)
R["blend_sin_consenso"] = round(sum(M[k] * W[k] for k in W if k != "Consenso") / (1 - W["Consenso"]), 2)
M_ex = dict(M); M_ex["Comparables"] = R["comps"]["fv_ex_amd"]
R["blend_sin_amd"] = round(sum(M_ex[k] * W[k] for k in W), 2)
R["blend_bear_dcf"] = round(sum((fv["Bear"] if k == "DCF Base" else M[k]) * W[k] for k in W), 2)
R["blend_vs_aug"] = round((blend / R["aug_blend_simple_publicado"] - 1) * 100, 1)
R["mkt"] = dict(price=PRICE, price_1811=PRICE_1811, hi52=HI52, from_hi=round((PRICE / HI52 - 1) * 100, 1),
                vs_aug=round((PRICE / PRICE_AUG - 1) * 100, 1), mcap=round(PRICE * SH, 0),
                pe_ttm_gaap=round(PRICE / TTM["eps"], 1), pe_ttm_ng=round(PRICE / TTM["eps_ng"], 1),
                ev_fcf=round((PRICE * SH - NET) / TTM["fcf"], 1), wacc=round(WACC_BASE * 100, 1))

if __name__ == "__main__":
    json.dump(R, open(os.path.join(HERE, "resultados.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for k, v in R.items():
        print(k, "=>", v)
