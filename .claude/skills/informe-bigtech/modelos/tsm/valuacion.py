"""
Modelo de valuación TSM (ADR) — actualización al 3T 2026 (trimestre cerrado 30-sep-2026; 6-K del 15-oct-2026 con comunicado y
presentación, 6-K del 10-nov-2026 con ingresos de octubre, 6-K de la junta y estados financieros del 11/13-nov-2026).

Correr:  python valuacion.py      (imprime todo y escribe resultados.json al lado)

1 ADR = 5 acciones ordinarias; 25,932M acciones → 5,186.4M ADR equivalentes. Cifras en US$ salvo indicación.
Fuentes:
  - 6-K del 15-oct-2026: ingresos 3T US$46.72B (NT$1,494.24B), margen bruto 66.4%, operativo 58.7%, EPS NT$29.43 (US$4.60
    por ADR); guía 4T US$52.3-54.3B (margen bruto 65-67%, operativo 56.5-58.5%); 2026 ~+44% en dólares. Presentación: caja
    y valores negociables NT$4,016.98B, deuda de largo plazo con intereses NT$818.38B; OCF 3T NT$919.77B, capex NT$443.21B.
  - 6-K del 10-nov-2026: ingresos de octubre NT$586.89B (+14.7% m/m, +59.7% a/a); enero-octubre NT$4,485.62B (+43.3%).
  - 6-K de la junta (nov-2026): dividendo NT$9.0 por acción del 3T; asignaciones de capital ~US$40.93B; hasta US$500M en
    Anthropic (en su OPI) y hasta US$500M en OpenAI.
  - Yahoo Finance: cierre del ADR 13-nov-2026 US$398.73; TWD 32.94 por USD; ^TNX 5.15% (4.78% al 4-sep-2026).
  - stockanalysis.com (S&P Global), 15-nov-2026: PT US$586.69 (21 analistas, US$440-1,000); EPS 2026E NT$110.63, 2027E
    NT$149.53; ingresos 2026E NT$5,582B, 2027E NT$7,691B. Peers en ../peers_semis_3t26.json.

Septiembre NO reproduce al centavo: con interpolación lineal el Base da US$273.15 (+3.8%); con decaimiento geométrico del
crecimiento, US$264.94 (+0.7%) — la trayectoria año a año no estaba documentada. Esta edición usa la geométrica.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
FX = 32.94
ADR = 25.932 / 5

def lin(a, b, n):
    return [a + (b - a) * i / (n - 1) for i in range(n)]

def geo(a, b, n):
    return [a * (b / a) ** (i / (n - 1)) for i in range(n)]

def dcf(rev1, g, o, c, wacc, gt, nc, sh, gf=geo):
    revs = [rev1]
    for x in gf(g[0], g[1], 4):
        revs.append(revs[-1] * (1 + x))
    fcf = [r * (oo - cc) for r, oo, cc in zip(revs, lin(o[0], o[1], 5), lin(c[0], c[1], 5))]
    pv = sum(f / (1 + wacc) ** (i + 1) for i, f in enumerate(fcf))
    pvtv = fcf[-1] * (1 + gt) / (wacc - gt) / (1 + wacc) ** 5
    ev = pv + pvtv
    return {"fv": (ev + nc) / sh, "tv_share": pvtv / ev, "fcf": fcf, "revs": revs}

R = {}
sep = {"Bear": dict(g=(0.14, 0.04), o=(0.60, 0.56), c=(0.37, 0.33), wacc=0.115, gt=0.025),
       "Base": dict(g=(0.32, 0.12), o=(0.60, 0.63), c=(0.36, 0.30), wacc=0.105, gt=0.03),
       "Bull": dict(g=(0.40, 0.16), o=(0.61, 0.66), c=(0.36, 0.24), wacc=0.09, gt=0.035)}
sep_pub = {"Bear": 115.26, "Base": 263.11, "Bull": 539.17}
R["sep_repro_lin"] = {k: round(dcf(173, **c, nc=77, sh=5.187, gf=lin)["fv"], 2) for k, c in sep.items()}
R["sep_repro_geo"] = {k: dict(modelo=round(dcf(173, **c, nc=77, sh=5.187)["fv"], 2), publicado=sep_pub[k]) for k, c in sep.items()}
SEP_M = {"DCF Base": 263.11, "Comparables": 442.93, "Reversión": 420.27, "Consenso": 554.45}
W = {"DCF Base": 0.15, "Comparables": 0.25, "Reversión": 0.35, "Consenso": 0.25}
R["sep_blend_simple"] = round(sum(SEP_M.values()) / 4, 2)
R["sep_blend_regla_vigente"] = round(sum(SEP_M[k] * W[k] for k in W), 2)

PRICE, PRICE_SEP, HI52, LO52 = 398.73, 428.91, 487.47, 266.82
PRICE_PRE, PRICE_POST = 422.25, 412.61
Q = dict(rev=46.72, rev_ya=33.10, rev_q2=40.20, gm=66.4, gm_ya=59.5, om=58.7, eps_adr=4.60, ni_nt=763.06,
         ocf_nt=919.77, capex_nt=443.21, fcf_nt=476.56, n2=8, n3=33, n5=28, n7=10)
Q["yoy"] = (Q["rev"] / Q["rev_ya"] - 1) * 100
Q["qoq"] = (Q["rev"] / Q["rev_q2"] - 1) * 100
Q["adv"] = Q["n2"] + Q["n3"] + Q["n5"] + Q["n7"]
Q["ocf_m"] = Q["ocf_nt"] / 1494.24 * 100
Q["capex_m"] = Q["capex_nt"] / 1494.24 * 100
Q["react"] = (PRICE_POST / PRICE_PRE - 1) * 100
R["q3"] = {k: round(v, 3) for k, v in Q.items()}
G = dict(lo=52.3, hi=54.3, mid=53.3, gm_lo=65, gm_hi=67, om_lo=56.5, om_hi=58.5)
G["q4_yoy"] = None
G["fy26_usd"] = 35.9 + 40.20 + 46.72 + 53.3
G["q4_qoq"] = (53.3 / 46.72 - 1) * 100
R["guide"] = {k: (round(v, 2) if v is not None else None) for k, v in G.items()}
R["oct"] = dict(nt=586.89, mom=14.7, yoy=59.7, ytd_nt=4485.62, ytd_yoy=43.3, usd=round(586.89 / FX, 2))
# TTM (US$): edición de sep (TTM al 2T26: OCF 83.6, ingresos 142.9, capex 47.0) + 3T26 - 3T25
q3_25 = dict(rev=33.10, ocf=426.83 / 29.91, capex=287.45 / 29.91, eps=2.92)
q3_26 = dict(rev=46.72, ocf=919.77 / 31.98, capex=443.21 / 31.98, eps=4.60)
TTM = dict(rev=142.9 - q3_25["rev"] + q3_26["rev"], ocf=83.6 - q3_25["ocf"] + q3_26["ocf"],
           capex=47.0 - q3_25["capex"] + q3_26["capex"], eps_adr=13.86 - q3_25["eps"] + q3_26["eps"])
TTM["ocf_m"] = TTM["ocf"] / TTM["rev"] * 100
TTM["capex_m"] = TTM["capex"] / TTM["rev"] * 100
TTM["fcf_m"] = TTM["ocf_m"] - TTM["capex_m"]
R["ttm"] = {k: round(v, 3) for k, v in TTM.items()}
BAL = dict(cash_nt=4016.98, debt_nt=818.38, cash_nt_jun=3518.01, debt_nt_jun=864.27, equity_nt=7043.23, roe=45.5)
BAL["net_cash"] = (BAL["cash_nt"] - BAL["debt_nt"]) / FX
BAL["net_cash_jun_fx_hoy"] = (BAL["cash_nt_jun"] - BAL["debt_nt_jun"]) / FX
R["bal"] = {k: round(v, 2) for k, v in BAL.items()}

P = json.load(open(os.path.join(HERE, "..", "peers_semis_3t26.json")))
C = P["TSM"]
EPS26 = C["eps_this"] * 5 / FX
EPS27 = C["eps_next"] * 5 / FX
g27 = C["rev_next"] / C["rev_this"] - 1
R["consenso"] = dict(pt=C["pt"], n=C["n"], lo=C["lo"], hi=C["hi"], rating=C["rating"], eps26_nt=round(C["eps_this"], 2),
                     eps27_nt=round(C["eps_next"], 2), eps26_adr=round(EPS26, 2), eps27_adr=round(EPS27, 2),
                     rev26_nt=round(C["rev_this"], 1), rev27_nt=round(C["rev_next"], 1), rev27_g=round(g27 * 100, 1),
                     upside=round((C["pt"] / PRICE - 1) * 100, 1))
pe27 = {"NVDA": P["NVDA"]["price"] / P["NVDA"]["eps_next"], "ASML": P["ASML"]["price"] / P["ASML"]["eps_next"],
        "GFS": P["GFS"]["price"] / P["GFS"]["eps_next"]}
panel = sum(pe27.values()) / 3
R["comps"] = dict(pe27={k: round(v, 2) for k, v in pe27.items()}, panel=round(panel, 2), eps27_adr=round(EPS27, 2),
                  fv=round(panel * EPS27, 2), fv_lo=round(min(pe27.values()) * EPS27, 2), fv_hi=round(max(pe27.values()) * EPS27, 2),
                  tsm_pe27=round(PRICE / EPS27, 2), tsm_pe26=round(PRICE / EPS26, 2))
COMPS = R["comps"]["fv"]

win = [("31-dic-2025", 303.89, 10.55), ("31-mar-2026", 337.95, 11.92), ("30-jun-2026", 477.57, 13.86), ("30-sep-2026", 456.19, TTM["eps_adr"])]
pes = [p / e for _, p, e in win]
REV = sum(pes) / 4 * TTM["eps_adr"]
R["reversion"] = dict(window=[(d, p, round(e, 2), round(p / e, 2)) for d, p, e in win], pe_avg=round(sum(pes) / 4, 2),
                      eps_ttm=round(TTM["eps_adr"], 2), fv=round(REV, 2), fv_lo=round(min(pes) * TTM["eps_adr"], 2),
                      fv_hi=round(max(pes) * TTM["eps_adr"], 2), pe_now=round(PRICE / TTM["eps_adr"], 1))

# DCF — año 1 = 2027 (2026 ≈ 9M reales + guía del 4T; 2027 = 2026 x crecimiento de consenso en NT$)
REV26 = G["fy26_usd"]
REV1 = REV26 * (1 + g27)
cases = {"Bear": dict(g=(0.10, 0.03), o=(0.60, 0.56), c=(0.36, 0.33), wacc=0.119, gt=0.025),
         "Base": dict(g=(0.22, 0.10), o=(0.62, 0.63), c=(0.34, 0.28), wacc=0.109, gt=0.03),
         "Bull": dict(g=(0.30, 0.14), o=(0.63, 0.66), c=(0.33, 0.24), wacc=0.094, gt=0.035)}
R["dcf"] = {}
for k, c in cases.items():
    r = dcf(REV1, c["g"], c["o"], c["c"], c["wacc"], c["gt"], BAL["net_cash"], ADR)
    R["dcf"][k] = dict(fv=round(r["fv"], 2), tv_share=round(r["tv_share"] * 100, 1), fcf1=round(r["fcf"][0], 2),
                       rev1=round(r["revs"][0], 2), rev5=round(r["revs"][-1], 2), wacc=round(c["wacc"] * 100, 1), gt=c["gt"] * 100,
                       capex1=round(r["revs"][0] * c["c"][0], 1))
fv = {k: R["dcf"][k]["fv"] for k in cases}
R["dcf_simple"] = round(sum(fv.values()) / 3, 2)
R["dcf_prob"] = round(0.25 * fv["Bear"] + 0.45 * fv["Base"] + 0.30 * fv["Bull"], 2)
DCF = fv["Base"]
b = cases["Base"]
gw = [0.099, 0.104, 0.109, 0.114, 0.119]
gg = [0.02, 0.025, 0.03, 0.035, 0.04]
R["grid"] = {"wacc": [round(x * 100, 1) for x in gw], "g": [x * 100 for x in gg],
             "fv": [[round(dcf(REV1, b["g"], b["o"], b["c"], w, x, BAL["net_cash"], ADR)["fv"], 2) for x in gg] for w in gw]}
R["rev26"], R["rev27"], R["g27"] = round(REV26, 2), round(REV1, 2), round(g27 * 100, 1)

M = {"DCF Base": DCF, "Comparables": COMPS, "Reversión": round(REV, 2), "Consenso": C["pt"]}
blend = sum(M[k] * W[k] for k in W)
R["methods"] = M
R["blend"] = round(blend, 2)
R["blend_gap"] = round((blend / PRICE - 1) * 100, 1)
R["blend_simple"] = round(sum(M.values()) / 4, 2)
R["blend_sin_consenso"] = round(sum(M[k] * W[k] for k in W if k != "Consenso") / 0.75, 2)
R["cambio_vs_sep_regla"] = round((blend / R["sep_blend_regla_vigente"] - 1) * 100, 1)
R["price"] = dict(now=PRICE, sep=PRICE_SEP, chg=round((PRICE / PRICE_SEP - 1) * 100, 1), off_hi=round((PRICE / HI52 - 1) * 100, 1),
                  mcap=round(PRICE * ADR, 1), pe_ttm=round(PRICE / TTM["eps_adr"], 1))
json.dump(R, open(os.path.join(HERE, "resultados.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
if __name__ == "__main__":
    for k, v in R.items():
        print(k, "=>", v)
