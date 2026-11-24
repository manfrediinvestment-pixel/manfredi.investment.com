"""
Modelo de valuación ASML — actualización al 3T 2026 (trimestre cerrado 27-sep-2026; 6-K del 14-oct-2026 con comunicado,
presentación y estados financieros US GAAP).

Correr:  python valuacion.py      (imprime todo y escribe resultados.json al lado)

Valuación en euros, convertida a dólares (precio del ADR en Nasdaq) al EUR/USD de cierre (1.11 al 13-nov-2026).
Fuentes:
  - 6-K del 14-oct-2026: ventas 3T €11,662M (Installed Base €3,289M), margen bruto 57.5%, operativo 44.4%, utilidad neta
    €4,960M (incluye ganancia de €509.7M por inversiones de capital), EPS diluido €12.93; guía 4T €14.2-15.2B (margen ~57%)
    y 2026 €44-45B (margen ~56%); "la oferta planificada para 2027 y 2028 no va a cubrir del todo la demanda"; recompras
    €4.1B en el 3T; dividendo interino €1.88. Balance: caja €8,030.9M + inversiones CP €4,704.2M, deuda LP €1,963.0M,
    pasivos por contratos €9,300.6M (desde €3,570.3M en junio). OCF trimestral 3T25..3T26: 559.1 / 11,410.3 / (2,185.6) /
    1,703.0 / 11,797.6; capex 295.9 / 447.9 / 402.4 / 299.4 / 413.3; intangibles 19.5 / 22.5 / 19.9 / 86.6 / 33.9.
  - Yahoo Finance: ADR US$1,495.16 (13-nov-2026); cierres de fin de trimestre; EUR/USD (2 decimales).
  - stockanalysis.com (S&P Global), 15-nov-2026: PT US$2,114 (41 analistas, US$852.82-2,801); ventas 2026E €44.48B, 2027E
    €57.35B; EPS 2026E €41.33, 2027E €56.22. Peers en ../peers_semis_3t26.json.

Septiembre NO reproduce al centavo: lineal Base US$843.48 (+2.4%); geométrico US$827.59 (+0.5%, % del EV desde terminal
idéntico, 77.3%). Se adopta la geométrica. La reversión de septiembre era consistente en moneda (P/E = precio US$ /
(EPS € x EUR/USD de cada fecha)); se reproduce: 43.32x y US$1,387.97 contra US$1,386.19 publicado (redondeo del tipo de cambio).
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
FX = 1.11

def lin(a, b, n):
    return [a + (b - a) * i / (n - 1) for i in range(n)]

def geo(a, b, n):
    return [a * (b / a) ** (i / (n - 1)) for i in range(n)]

def dcf(rev1, g, o, c, wacc, gt, nc, sh, fx, gf=geo):
    revs = [rev1]
    for x in gf(g[0], g[1], 4):
        revs.append(revs[-1] * (1 + x))
    fcf = [r * (oo - cc) for r, oo, cc in zip(revs, lin(o[0], o[1], 5), lin(c[0], c[1], 5))]
    pv = sum(f / (1 + wacc) ** (i + 1) for i, f in enumerate(fcf))
    pvtv = fcf[-1] * (1 + gt) / (wacc - gt) / (1 + wacc) ** 5
    ev = pv + pvtv
    return {"fv": (ev + nc) / sh * fx, "tv_share": pvtv / ev, "fcf": fcf, "revs": revs}

R = {}
sep = {"Bear": dict(g=(0.05, 0.02), o=(0.30, 0.32), c=(0.045, 0.05), wacc=0.10, gt=0.025),
       "Base": dict(g=(0.15, 0.05), o=(0.33, 0.35), c=(0.045, 0.055), wacc=0.09, gt=0.03),
       "Bull": dict(g=(0.20, 0.10), o=(0.33, 0.38), c=(0.045, 0.048), wacc=0.08, gt=0.035)}
sep_pub = {"Bear": 500.28, "Base": 823.41, "Bull": 1415.25}
R["sep_repro_lin"] = {k: round(dcf(44.0, **c, nc=5.5971, sh=0.3841, fx=1.1631, gf=lin)["fv"], 2) for k, c in sep.items()}
R["sep_repro_geo"] = {k: dict(modelo=round(dcf(44.0, **c, nc=5.5971, sh=0.3841, fx=1.1631)["fv"], 2), publicado=sep_pub[k]) for k, c in sep.items()}
# Reproducción de la reversión de sep: P/E en moneda consistente (precio US$ / (EPS € × EUR/USD de cada fecha))
sep_win = [(968.09, 24.22, 1.17), (1069.86, 24.72, 1.17), (1253.96, 25.87, 1.15), (1883.11, 27.55, 1.14)]
sep_pe_ok = sum(p / (e * f) for p, e, f in sep_win) / 4
R["sep_reversion_repro"] = dict(pe_consistente=round(sep_pe_ok, 2), fv=round(sep_pe_ok * 27.55 * 1.1631, 2), publicado=1386.19)
SEP_M = {"DCF Base": 823.41, "Comparables": 1599.10, "Reversión": 1386.19, "Consenso": 2168.00}
W = {"DCF Base": 0.15, "Comparables": 0.25, "Reversión": 0.35, "Consenso": 0.25}
R["sep_blend_simple"] = round(sum(SEP_M.values()) / 4, 2)
R["sep_blend_regla_vigente"] = round(sum(SEP_M[k] * W[k] for k in W), 2)

PRICE, PRICE_SEP, HI52, LO52 = 1495.16, 1764.85, 1999.96, 946.11
PRICE_PRE, PRICE_POST = 1650.00, 1657.44
q = ["3T25", "4T25", "1T26", "2T26", "3T26"]
rev = [7.516, 9.7181, 8.7669, 9.3265, 11.662]
opi = [2.4684, 3.4311, 3.1578, 3.4561, 5.1728]
eps = [5.48, 7.34, 7.15, 7.58, 12.93]
ocf = [0.5591, 11.4103, -2.1856, 1.7030, 11.7976]
capex = [0.2959 + 0.0195, 0.4479 + 0.0225, 0.4024 + 0.0199, 0.2994 + 0.0866, 0.4133 + 0.0339]
t4 = lambda a: sum(a[1:5])
GAIN = 0.5097
SH = 4.9604 / 12.93            # acciones diluidas del 3T (miles de millones)
TTM = dict(rev=t4(rev), opi=t4(opi), eps=t4(eps), ocf=t4(ocf), capex=t4(capex), contract_liab_chg=9.3006 - 3.5723)
TTM["eps_norm"] = TTM["eps"] - GAIN / SH
TTM["ocf_m"] = TTM["ocf"] / TTM["rev"] * 100
TTM["ocf_ex_prepay_m"] = (TTM["ocf"] - TTM["contract_liab_chg"]) / TTM["rev"] * 100
TTM["capex_m"] = TTM["capex"] / TTM["rev"] * 100
TTM["opi_m"] = TTM["opi"] / TTM["rev"] * 100
TTM["rev_yoy"] = (TTM["rev"] / (7.7416 + 7.7419 + 7.6918 + 7.516) - 1) * 100 if False else None
R["ttm"] = {k: (round(v, 3) if v is not None else None) for k, v in TTM.items()}
R["sh"] = round(SH, 4)
Q = dict(rev=11.662, rev_ya=7.516, rev_q2=9.3265, ibm=3.289, gm=57.5, om=44.4, ni=4.9604, eps=12.93, units_new=113, units_used=8,
         buyback=4.071, div=1.88, react=(PRICE_POST / PRICE_PRE - 1) * 100)
Q["yoy"] = (Q["rev"] / Q["rev_ya"] - 1) * 100
Q["qoq"] = (Q["rev"] / Q["rev_q2"] - 1) * 100
Q["eps_norm"] = Q["eps"] - GAIN / SH
R["q3"] = {k: round(v, 3) for k, v in Q.items()}
G = dict(q4_lo=14.2, q4_hi=15.2, q4_mid=14.7, gm=57, fy_lo=44, fy_hi=45, fy_mid=44.5, fy_gm=56)
G["q4_yoy"] = (14.7 / 9.7181 - 1) * 100
G["fy_yoy"] = (44.5 / 32.667 - 1) * 100
R["guide"] = {k: round(v, 2) for k, v in G.items()}
BAL = dict(cash=8.0309, sti=4.7042, ltd=1.963, contract_liab=9.3006, contract_liab_jun=3.5703)
BAL["liq"] = BAL["cash"] + BAL["sti"]
BAL["net_cash"] = BAL["liq"] - BAL["ltd"]
R["bal"] = {k: round(v, 3) for k, v in BAL.items()}

P = json.load(open(os.path.join(HERE, "..", "peers_semis_3t26.json")))
C = P["ASML"]
R["consenso"] = dict(pt=C["pt"], n=C["n"], lo=C["lo"], hi=C["hi"], rating=C["rating"], rev26=round(C["rev_this"], 2),
                     rev27=round(C["rev_next"], 2), eps26=round(C["eps_this"], 2), eps27=round(C["eps_next"], 2),
                     rev27_g=round((C["rev_next"] / C["rev_this"] - 1) * 100, 1), eps27_g=round((C["eps_next"] / C["eps_this"] - 1) * 100, 1),
                     upside=round((C["pt"] / PRICE - 1) * 100, 1))
EPS27_USD = C["eps_next"] * FX
pe27 = {"AMAT": P["AMAT"]["price"] / P["AMAT"]["eps_this"],   # FY oct-2027
        "LRCX": P["LRCX"]["price"] / P["LRCX"]["eps_this"],   # FY jun-2027
        "KLAC": P["KLAC"]["price"] / P["KLAC"]["eps_this"]}   # FY jun-2027
panel = sum(pe27.values()) / 3
R["comps"] = dict(pe27={k: round(v, 2) for k, v in pe27.items()}, panel=round(panel, 2), eps27_eur=round(C["eps_next"], 2),
                  eps27_usd=round(EPS27_USD, 2), fv=round(panel * EPS27_USD, 2), fv_lo=round(min(pe27.values()) * EPS27_USD, 2),
                  fv_hi=round(max(pe27.values()) * EPS27_USD, 2), asml_pe27=round(PRICE / EPS27_USD, 2),
                  asml_pe26=round(PRICE / (C["eps_this"] * FX), 2))
COMPS = R["comps"]["fv"]

win = [("31-dic-2025", 1069.86, 24.72, 1.17), ("27-mar-2026", 1302.47, 25.87, 1.15), ("26-jun-2026", 1794.62, 27.55, 1.14),
       ("25-sep-2026", 1743.94, TTM["eps"], 1.14)]
pes = [p / (e * f) for _, p, e, f in win]
pe_avg = sum(pes) / 4
REV = pe_avg * TTM["eps_norm"] * FX
R["reversion"] = dict(window=[(d, p, round(e, 2), f, round(p / (e * f), 2)) for d, p, e, f in win], pe_avg=round(pe_avg, 2),
                      eps_norm=round(TTM["eps_norm"], 2), fv=round(REV, 2),
                      fv_lo=round(min(pes) * TTM["eps_norm"] * FX, 2), fv_hi=round(max(pes) * TTM["eps_norm"] * FX, 2),
                      pe_now=round(PRICE / (TTM["eps_norm"] * FX), 1))

# DCF — año 1 = 2027 (consenso; la compañía dice que la demanda supera la oferta planificada para 2027 y 2028)
REV1 = round(C["rev_next"], 3)
cases = {"Bear": dict(g=(0.05, 0.02), o=(0.32, 0.32), c=(0.05, 0.05), wacc=0.10, gt=0.025),
         "Base": dict(g=(0.15, 0.05), o=(0.35, 0.36), c=(0.055, 0.055), wacc=0.09, gt=0.03),
         "Bull": dict(g=(0.20, 0.10), o=(0.37, 0.40), c=(0.05, 0.05), wacc=0.08, gt=0.035)}
R["dcf"] = {}
for k, c in cases.items():
    r = dcf(REV1, c["g"], c["o"], c["c"], c["wacc"], c["gt"], BAL["net_cash"], SH, FX)
    R["dcf"][k] = dict(fv=round(r["fv"], 2), tv_share=round(r["tv_share"] * 100, 1), fcf1=round(r["fcf"][0], 2),
                       rev5=round(r["revs"][-1], 2), wacc=c["wacc"] * 100, gt=c["gt"] * 100)
fv = {k: R["dcf"][k]["fv"] for k in cases}
R["dcf_simple"] = round(sum(fv.values()) / 3, 2)
R["dcf_prob"] = round(0.25 * fv["Bear"] + 0.45 * fv["Base"] + 0.30 * fv["Bull"], 2)
DCF = fv["Base"]
b = cases["Base"]
gw = [0.08, 0.085, 0.09, 0.095, 0.10]
gg = [0.02, 0.025, 0.03, 0.035, 0.04]
R["grid"] = {"wacc": [x * 100 for x in gw], "g": [x * 100 for x in gg],
             "fv": [[round(dcf(REV1, b["g"], b["o"], b["c"], w, x, BAL["net_cash"], SH, FX)["fv"]) for x in gg] for w in gw]}

M = {"DCF Base": DCF, "Comparables": COMPS, "Reversión": round(REV, 2), "Consenso": C["pt"]}
blend = sum(M[k] * W[k] for k in W)
R["methods"] = M
R["blend"] = round(blend, 2)
R["blend_gap"] = round((blend / PRICE - 1) * 100, 1)
R["blend_simple"] = round(sum(M.values()) / 4, 2)
R["blend_sin_consenso"] = round(sum(M[k] * W[k] for k in W if k != "Consenso") / 0.75, 2)
R["cambio_vs_sep_regla"] = round((blend / R["sep_blend_regla_vigente"] - 1) * 100, 1)
R["price"] = dict(now=PRICE, sep=PRICE_SEP, chg=round((PRICE / PRICE_SEP - 1) * 100, 1), off_hi=round((PRICE / HI52 - 1) * 100, 1),
                  mcap_usd=round(PRICE * SH, 1), pe_ttm_norm=R["reversion"]["pe_now"])
json.dump(R, open(os.path.join(HERE, "resultados.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
if __name__ == "__main__":
    for k, v in R.items():
        print(k, "=>", v)
