"""
Modelo de valuación TXN — actualización al 3T 2026 (trimestre cerrado 30-sep-2026; 8-K Ex. 99 del 21-oct-2026, 10-Q del 23-oct-2026).

Correr:  python valuacion.py      (imprime todo y escribe resultados.json al lado)

Fuentes (verificadas contra el documento original):
  - 8-K Ex. 99 del 21-oct-2026: resultados, segmentos, balance, flujo de caja, FCF TTM $8.422B (incluye $1.104B de
    incentivos CHIPS), guía 4T26 (ingresos $5.80-6.30B, EPS $2.45-2.79).
  - 8-K del 17-sep-2026 (dividendo +7% a $1.52 trimestral) y 8-K del 9-nov-2026 (emisión de $2.0B en notas, posterior al
    cierre: no cambia la deuda neta porque la caja entra).
  - SEC companyfacts XBRL: series trimestrales. Yahoo Finance chart API: cierre 13-nov-2026 $303.60, cierres de fin de
    trimestre, ^TNX 5.15% (4.81% al 8-sep-2026).
  - stockanalysis.com (S&P Global), 15-nov-2026: PT $338.79 (35 analistas, $250-$422); FY26E ingresos $22.40B, EPS $9.09;
    FY27E $26.30B, EPS $11.63. Peers en ../peers_semis_3t26.json.

Convención del DCF (la de septiembre): 5 años explícitos; crecimiento del año 2 al 5 y margen de FCF del año 1 al 5 en
línea recta; descuento a fin de año; VT = FCF5 x (1+g)/(WACC-g); equity = EV - deuda neta; ÷ acciones diluidas.
Septiembre NO reproduce al centavo: con su propia deuda neta ($7.051B) y 913M acciones el Base da $131.94 (+1.6%). Los tres
escenarios publicados se reproducen (±$0.10) con 911M acciones y ~$9.26B restados del EV, es decir, el DCF restaba más que la
deuda neta de su propia tabla. Los % de EV desde el terminal sí coinciden (67.2/74.4/81.5 vs 67.1/74.2/81.5).
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))

def lin(a, b, n):
    return [a + (b - a) * i / (n - 1) for i in range(n)]

def dcf(rev1, g2_5, m, wacc, gt, net_debt, shares):
    revs = [rev1]
    for x in lin(g2_5[0], g2_5[1], 4):
        revs.append(revs[-1] * (1 + x))
    fcf = [r * mm for r, mm in zip(revs, lin(m[0], m[1], 5))]
    pv = sum(f / (1 + wacc) ** (i + 1) for i, f in enumerate(fcf))
    pvtv = fcf[-1] * (1 + gt) / (wacc - gt) / (1 + wacc) ** 5
    ev = pv + pvtv
    return {"fv": (ev - net_debt) / shares, "tv_share": pvtv / ev, "fcf": fcf, "revs": revs, "ev": ev}

R = {}
# 1) SEPTIEMBRE (datos al 2T26, precio $261.00)
sep = {"Bear": dict(g=(0.05, 0.02), m=(0.30, 0.26), wacc=0.105, gt=0.025),
       "Base": dict(g=(0.14, 0.05), m=(0.335, 0.30), wacc=0.095, gt=0.03),
       "Bull": dict(g=(0.18, 0.07), m=(0.345, 0.365), wacc=0.085, gt=0.035)}
sep_pub = {"Bear": 72.81, "Base": 129.88, "Bull": 226.51}
R["sep_repro_tabla"] = {k: round(dcf(21.9, c["g"], c["m"], c["wacc"], c["gt"], 7.051, 0.913)["fv"], 2) for k, c in sep.items()}
R["sep_repro_ajuste"] = {k: round(dcf(21.9, c["g"], c["m"], c["wacc"], c["gt"], 9.26, 0.9111)["fv"], 2) for k, c in sep.items()}
R["sep_tv_share"] = {k: round(dcf(21.9, c["g"], c["m"], c["wacc"], c["gt"], 7.051, 0.913)["tv_share"] * 100, 1) for k, c in sep.items()}
SEP_M = {"DCF Base": 129.88, "Comparables": 213.20, "Reversión": 235.62, "Consenso": 324.71}
W = {"DCF Base": 0.15, "Comparables": 0.25, "Reversión": 0.35, "Consenso": 0.25}
R["sep_blend_simple"] = round(sum(SEP_M.values()) / 4, 2)
R["sep_blend_regla_vigente"] = round(sum(SEP_M[k] * W[k] for k in W), 2)

# 2) DATOS 3T26 (miles de millones)
PRICE, PRICE_SEP, HI52, LO52 = 303.60, 261.00, 334.03, 152.73
PRICE_PRE, PRICE_POST = 284.65, 279.50
q = ["3T25", "4T25", "1T26", "2T26", "3T26"]
rev = [4.742, 4.423, 4.825, 5.463, 6.055]
gp = [2.723, 2.472, 2.799, 3.352, 3.887]
op = [1.663, 1.473, 1.808, 2.310, 2.874]
ni = [1.364, 1.163, 1.545, 1.980, 2.425]
eps = [1.48, 1.27, 1.68, 2.14, 2.62]
ocf = [2.190, 2.254, 1.520, 9.896 - 2.254 - 1.520 - 3.419, 3.419]
capex = [1.197, 0.925, 0.676, 2.578 - 0.925 - 0.676 - 0.463, 0.463]
t4 = lambda a: sum(a[1:5])
TTM = dict(rev=t4(rev), gp=t4(gp), op=t4(op), ni=t4(ni), eps=t4(eps), ocf=9.896, capex=2.578, chips=1.104, fcf_co=8.422)
TTM["fcf_ex_chips"] = TTM["ocf"] - TTM["capex"]
for k in ("gp", "op", "ni", "ocf", "capex", "fcf_co", "fcf_ex_chips"):
    TTM[k + "_m"] = TTM[k] / TTM["rev"] * 100
TTM["rev_yoy"] = (TTM["rev"] / 17.266 - 1) * 100
R["ttm"] = {k: round(v, 3) for k, v in TTM.items()}
R["quarters"] = {l: dict(rev=rev[i], gm=round(gp[i] / rev[i] * 100, 1), om=round(op[i] / rev[i] * 100, 1),
                         ocf_m=round(ocf[i] / rev[i] * 100, 1), capex=round(capex[i], 3)) for i, l in enumerate(q)}
R["q3"] = dict(rev_yoy=round((6.055 / 4.742 - 1) * 100, 1), rev_qoq=round((6.055 / 5.463 - 1) * 100, 1),
               gm=round(3.887 / 6.055 * 100, 1), om=round(2.874 / 6.055 * 100, 1), eps_yoy=round((2.62 / 1.48 - 1) * 100, 1),
               analog=4.911, analog_yoy=round((4.911 / 3.729 - 1) * 100, 1), analog_m=round(2.505 / 4.911 * 100, 1),
               emb=0.858, emb_yoy=round((0.858 / 0.709 - 1) * 100, 1), emb_m=round(0.227 / 0.858 * 100, 1),
               other=0.286, analog_share=round(4.911 / 6.055 * 100, 1), fcf_q=2.956, react=round((PRICE_POST / PRICE_PRE - 1) * 100, 1))
G = dict(lo=5.80, hi=6.30, mid=6.05, eps_lo=2.45, eps_hi=2.79, eps_mid=2.62)
G["yoy"] = (6.05 / 4.423 - 1) * 100
G["qoq"] = (6.05 / 6.055 - 1) * 100
G["fy26"] = 4.825 + 5.463 + 6.055 + 6.05
G["fy26_yoy"] = (G["fy26"] / 17.682 - 1) * 100
R["guide"] = {k: round(v, 2) for k, v in G.items()}
BAL = dict(cash=4.211, sti=3.931, debt_cur=0.650, debt_lt=12.905, equity=19.185, assets=36.839, inventory=4.672,
           ppe_gross=18.072, notes_nov=2.0, shares_dil=0.921, div_q=1.52)
BAL["liq"] = BAL["cash"] + BAL["sti"]
BAL["debt"] = BAL["debt_cur"] + BAL["debt_lt"]
BAL["net_debt"] = BAL["debt"] - BAL["liq"]
BAL["nd_ocf"] = BAL["net_debt"] / TTM["ocf"]
BAL["div_yield"] = BAL["div_q"] * 4 / PRICE * 100
BAL["payout_fcf"] = 5.810 / 8.422 * 100
R["bal"] = {k: round(v, 3) for k, v in BAL.items()}

# 3) CONSENSO Y PEERS
P = json.load(open(os.path.join(HERE, "..", "peers_semis_3t26.json")))
C = P["TXN"]
R["consenso"] = dict(pt=C["pt"], n=C["n"], lo=C["lo"], hi=C["hi"], rating=C["rating"], eps26=round(C["eps_this"], 2),
                     eps27=round(C["eps_next"], 2), rev26=round(C["rev_this"], 2), rev27=round(C["rev_next"], 2),
                     rev27_g=round((C["rev_next"] / C["rev_this"] - 1) * 100, 1), rev26_g=round((C["rev_this"] / 17.682 - 1) * 100, 1),
                     eps27_g=round((C["eps_next"] / C["eps_this"] - 1) * 100, 1), upside=round((C["pt"] / PRICE - 1) * 100, 1))
pe27 = {"ADI": P["ADI"]["price"] / P["ADI"]["eps_next"],      # FY oct-2027
        "NXPI": P["NXPI"]["price"] / P["NXPI"]["eps_next"],   # FY dic-2027
        "MCHP": P["MCHP"]["price"] / P["MCHP"]["eps_next"],   # FY mar-2028 (9 de sus 12 meses caen en 2027)
        "ON": P["ON"]["price"] / P["ON"]["eps_next"]}         # FY dic-2027
avg = sum(pe27.values()) / 4
EPS27 = C["eps_next"]
R["comps"] = dict(pe27={k: round(v, 2) for k, v in pe27.items()}, avg=round(avg, 2), eps27=round(EPS27, 2),
                  fv=round(avg * EPS27, 2), fv_lo=round(min(pe27.values()) * EPS27, 2), fv_hi=round(max(pe27.values()) * EPS27, 2),
                  txn_pe27=round(PRICE / EPS27, 2), txn_pe26=round(PRICE / C["eps_this"], 2), prem_25x=round(25 * EPS27, 2))
COMPS = R["comps"]["fv"]

# 4) REVERSIÓN — últimos 4 cierres de trimestre, EPS GAAP TTM vigente
win = [("31-dic-2025", 173.49, 1.28 + 1.41 + 1.48 + 1.27), ("31-mar-2026", 194.14, 1.41 + 1.48 + 1.27 + 1.68),
       ("30-jun-2026", 298.07, 1.48 + 1.27 + 1.68 + 2.14), ("30-sep-2026", 280.09, 1.27 + 1.68 + 2.14 + 2.62)]
pes = [p / e for _, p, e in win]
pe_avg = sum(pes) / 4
REV = pe_avg * TTM["eps"]
R["reversion"] = dict(window=[(d, p, round(e, 2), round(p / e, 2)) for d, p, e in win], pe_avg=round(pe_avg, 2),
                      eps_ttm=round(TTM["eps"], 2), fv=round(REV, 2), pe10=24.7, fv_pe10_27=round(24.7 * EPS27, 2),
                      fv_lo=round(min(pes) * TTM["eps"], 2), fv_hi=round(max(pes) * TTM["eps"], 2))

# 5) DCF — año 1 = 2027 (año 0 = FY2026E de consenso ≈ 9M reales + punto medio de la guía del 4T)
REV1 = round(C["rev_next"], 2)
WACC_BASE = 0.103     # CAPM 5.15% + 1.05 x 5.0% = 10.4% de costo de equity; con ~4% de deuda a costo bajo → 10.3%
cases = {"Bear": dict(g=(0.04, 0.02), m=(0.31, 0.26), wacc=WACC_BASE + 0.01, gt=0.025),
         "Base": dict(g=(0.10, 0.05), m=(0.35, 0.31), wacc=WACC_BASE, gt=0.03),
         "Bull": dict(g=(0.14, 0.07), m=(0.37, 0.38), wacc=WACC_BASE - 0.01, gt=0.035)}
R["dcf"] = {}
for k, c in cases.items():
    r = dcf(REV1, c["g"], c["m"], c["wacc"], c["gt"], BAL["net_debt"], BAL["shares_dil"])
    R["dcf"][k] = dict(fv=round(r["fv"], 2), tv_share=round(r["tv_share"] * 100, 1), fcf1=round(r["fcf"][0], 2),
                       fcf5=round(r["fcf"][-1], 2), rev5=round(r["revs"][-1], 2), wacc=round(c["wacc"] * 100, 1), gt=c["gt"] * 100)
fv = {k: R["dcf"][k]["fv"] for k in cases}
R["dcf_simple"] = round(sum(fv.values()) / 3, 2)
R["dcf_prob"] = round(0.25 * fv["Bear"] + 0.45 * fv["Base"] + 0.30 * fv["Bull"], 2)
DCF = fv["Base"]
b = cases["Base"]
gw = [WACC_BASE - 0.01, WACC_BASE - 0.005, WACC_BASE, WACC_BASE + 0.005, WACC_BASE + 0.01]
gg = [0.02, 0.025, 0.03, 0.035, 0.04]
R["grid"] = {"wacc": [round(x * 100, 1) for x in gw], "g": [x * 100 for x in gg],
             "fv": [[round(dcf(REV1, b["g"], b["m"], w, x, BAL["net_debt"], BAL["shares_dil"])["fv"], 2) for x in gg] for w in gw]}
def solve(f, lo, hi):
    for _ in range(200):
        m = (lo + hi) / 2
        if f(m) < PRICE: lo = m
        else: hi = m
    return m
R["inverse"] = dict(fcf_m_flat=round(solve(lambda x: dcf(REV1, b["g"], (x, x), b["wacc"], b["gt"], BAL["net_debt"], BAL["shares_dil"])["fv"], 0, 1) * 100, 1),
                    g_flat=round(solve(lambda x: dcf(REV1, (x, x), b["m"], b["wacc"], b["gt"], BAL["net_debt"], BAL["shares_dil"])["fv"], 0, 1) * 100, 1))

# 6) BLEND
M = {"DCF Base": DCF, "Comparables": COMPS, "Reversión": round(REV, 2), "Consenso": C["pt"]}
blend = sum(M[k] * W[k] for k in W)
R["methods"] = M
R["blend"] = round(blend, 2)
R["blend_gap"] = round((blend / PRICE - 1) * 100, 1)
R["blend_simple"] = round(sum(M.values()) / 4, 2)
R["blend_sin_consenso"] = round(sum(M[k] * W[k] for k in W if k != "Consenso") / 0.75, 2)
R["cambio_vs_sep_regla"] = round((blend / R["sep_blend_regla_vigente"] - 1) * 100, 1)
R["price"] = dict(now=PRICE, sep=PRICE_SEP, chg=round((PRICE / PRICE_SEP - 1) * 100, 1), off_hi=round((PRICE / HI52 - 1) * 100, 1),
                  mcap=round(PRICE * 0.914, 1), pe_ttm=round(PRICE / TTM["eps"], 1), p_fcf=round(PRICE * 0.921 / 8.422, 1))
json.dump(R, open(os.path.join(HERE, "resultados.json"), "w"), indent=1, ensure_ascii=False)
if __name__ == "__main__":
    for k, v in R.items():
        print(k, "=>", v)
