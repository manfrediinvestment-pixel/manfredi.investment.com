"""
Modelo de valuación ARM — actualización al 2T FY2027 (trimestre cerrado 30-sep-2026; 6-K con Ex. 99.1/99.2 del 4-nov-2026).

Correr:  python valuacion.py      (imprime todo y escribe resultados.json al lado)

Arm se valúa con la vara del software premium (pedido explícito del usuario, ver memoria project_informe_arm).

Fuentes (verificadas contra el documento original):
  - 6-K del 4-nov-2026, Ex. 99.2 (carta a accionistas): ingresos $1,443M (+27%), regalías $670M (+8%, con impacto de la
    memoria), licencias $773M (+50%), ACV $1,790M (+12%), EPS GAAP $0.12 / no-GAAP $0.52, OCF 3T $207M y TTM $1,734M,
    FCF no-GAAP TTM $1,096M, caja + inversiones CP $3,621M, SBC del trimestre $376M, guía 3T FY27 ($1.54B ±$50M, EPS
    no-GAAP $0.56 ±$0.04), CPU AGI: "hasta $2B" de ingresos en FY27-28, con mayor confianza.
  - Yahoo Finance chart API: cierre 13-nov-2026 $190.53; cierres de fin de trimestre; ^TNX 5.15% (4.81% al 8-sep-2026).
  - stockanalysis.com (S&P Global), 15-nov-2026: PT $272.43 (43 analistas, $125-$500, "Buy"); FY27E (mar-27) ingresos
    $6.101B, EPS no-GAAP $2.27; FY28E $8.376B, EPS $3.07. Canasto de software: consenso y valor de empresa de
    stockanalysis (statistics), precios de Yahoo (13-nov-2026).

Convención del DCF (la de septiembre, reproducida): año 1 = FY2027 (consenso); crecimiento FY2028-FY2031 lineal; margen de
OCF y capex/ingresos lineales; FCF = ingresos x (OCF% - capex%); descuento a fin de año; equity = EV + caja neta.
Septiembre se reproduce al centavo con 1,090M acciones (el texto citaba ~1,078M); los % de EV desde el terminal coinciden.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))

def lin(a, b, n):
    return [a + (b - a) * i / (n - 1) for i in range(n)]

def dcf(rev1, g, o, c, wacc, gt, nc, sh):
    revs = [rev1]
    for x in lin(g[0], g[1], 4):
        revs.append(revs[-1] * (1 + x))
    fcf = [r * (oo - cc) for r, oo, cc in zip(revs, lin(o[0], o[1], 5), lin(c[0], c[1], 5))]
    pv = sum(f / (1 + wacc) ** (i + 1) for i, f in enumerate(fcf))
    pvtv = fcf[-1] * (1 + gt) / (wacc - gt) / (1 + wacc) ** 5
    ev = pv + pvtv
    return {"fv": (ev + nc) / sh, "tv_share": pvtv / ev, "fcf": fcf, "revs": revs}

R = {}
sep = {"Bear": dict(g=(0.14, 0.07), o=(0.30, 0.31), c=(0.10, 0.09), wacc=0.12, gt=0.03),
       "Base": dict(g=(0.21, 0.11), o=(0.34, 0.40), c=(0.10, 0.065), wacc=0.11, gt=0.035),
       "Bull": dict(g=(0.26, 0.15), o=(0.36, 0.46), c=(0.09, 0.06), wacc=0.10, gt=0.04)}
sep_pub = {"Bear": 20.63, "Base": 39.32, "Bull": 64.63}
R["sep_repro_1090"] = {k: dict(modelo=round(dcf(6.05, **{**c}, nc=4.0, sh=1.0903)["fv"], 2), publicado=sep_pub[k]) for k, c in sep.items()}
R["sep_repro_1078"] = {k: round(dcf(6.05, **{**c}, nc=4.0, sh=1.078)["fv"], 2) for k, c in sep.items()}
SEP_M = {"DCF Base": 39.32, "SOTP": 122.01, "Comparables": 149.41, "Reversión": 154.19, "Consenso": 290.00}
W = {"DCF Base": 0.075, "SOTP": 0.075, "Comparables": 0.25, "Reversión": 0.35, "Consenso": 0.25}
R["sep_blend_simple"] = round(sum(SEP_M.values()) / 5, 2)
R["sep_blend_regla_vigente"] = round(sum(SEP_M[k] * W[k] for k in W), 2)

# DATOS 2T FY27
PRICE, PRICE_SEP, HI52, LO52 = 190.53, 261.53, 452.70, 100.02
PRICE_PRE, PRICE_POST = 191.80, 166.72
Q = dict(rev=1.443, rev_ya=1.135, roy=0.670, roy_ya=0.620, lic=0.773, lic_ya=0.515, acv=1.790, gm=97.1, gm_ng=97.9,
         opi=0.201, opi_ng=0.638, eps=0.12, eps_ng=0.52, eps_ng_ya=0.39, ocf=0.207, sbc=0.376, capex=0.072, sh=1.079)
for k in ("rev", "roy", "lic"):
    Q[k + "_yoy"] = (Q[k] / Q[k + "_ya"] - 1) * 100
Q["om"] = Q["opi"] / Q["rev"] * 100
Q["om_ng"] = Q["opi_ng"] / Q["rev"] * 100
Q["react"] = (PRICE_POST / PRICE_PRE - 1) * 100
R["q2"] = {k: round(v, 3) for k, v in Q.items()}
TTM = dict(rev=5.156 - 1.135 + 1.443, ocf=1.734, fcf=1.096, sbc=1.154 - 0.265 + 0.376, eps_ng=1.87 - 0.39 + 0.52, cash=3.621)
TTM["ocf_m"] = TTM["ocf"] / TTM["rev"] * 100
TTM["fcf_m"] = TTM["fcf"] / TTM["rev"] * 100
TTM["capex_m"] = (TTM["ocf"] - TTM["fcf"]) / TTM["rev"] * 100
TTM["sbc_m"] = TTM["sbc"] / TTM["rev"] * 100
TTM["rev_yoy"] = (TTM["rev"] / (5.156 - 0.0) - 1) * 100   # referencia contra el TTM de sep (no interanual)
R["ttm"] = {k: round(v, 3) for k, v in TTM.items()}
G = dict(rev=1.54, lo=1.49, hi=1.59, eps=0.56, opex=0.825)
G["fy27_impl"] = 2.732 + 1.54
R["guide"] = {k: round(v, 3) for k, v in G.items()}

P = json.load(open(os.path.join(HERE, "..", "peers_semis_3t26.json")))
C = P["ARM"]
R["consenso"] = dict(pt=C["pt"], n=C["n"], lo=C["lo"], hi=C["hi"], rating=C["rating"], rev27=round(C["rev_this"], 3),
                     rev28=round(C["rev_next"], 3), eps27=round(C["eps_this"], 2), eps28=round(C["eps_next"], 2),
                     rev27_g=round((C["rev_this"] / 4.92 - 1) * 100, 1), rev28_g=round((C["rev_next"] / C["rev_this"] - 1) * 100, 1),
                     eps28_g=round((C["eps_next"] / C["eps_this"] - 1) * 100, 1), upside=round((C["pt"] / PRICE - 1) * 100, 1))

# CANASTO SOFTWARE PREMIUM (año fiscal que más se superpone con 2027)
B = {"NOW": (102.25, 107.58, 19.263, 4.802), "CRWD": (226.61, 228.34, 7.382, 1.61), "SNOW": (291.00, 100.99, 8.164, 3.064),
     "PLTR": (167.99, 394.44, 13.121, 2.539), "ADBE": (243.08, 95.75, 29.036, 27.407), "CDNS": (323.01, 89.90, 7.334, 9.845),
     "SNPS": (455.20, 94.47, 11.003, 18.645)}
evs = {k: v[1] / v[2] for k, v in B.items()}
pes = {k: v[0] / v[3] for k, v in B.items()}
evs_avg, pe_avg = sum(evs.values()) / 7, sum(pes.values()) / 7
EVS_APPLIED = evs_avg * 1.12          # misma prima de 12% que septiembre por el margen bruto de 97% de Arm
REV28, EPS28 = C["rev_next"], C["eps_next"]
SH = 1.0903
fv_evs = (EVS_APPLIED * REV28 + TTM["cash"]) / SH
fv_pe = pe_avg * EPS28
COMPS = (fv_evs + fv_pe) / 2
R["comps"] = dict(evs={k: round(v, 2) for k, v in evs.items()}, pes={k: round(v, 2) for k, v in pes.items()},
                  evs_avg=round(evs_avg, 2), evs_applied=round(EVS_APPLIED, 2), pe_avg=round(pe_avg, 2), rev28=round(REV28, 3),
                  eps28=round(EPS28, 2), fv_evs=round(fv_evs, 2), fv_pe=round(fv_pe, 2), fv=round(COMPS, 2),
                  arm_evs28=round((PRICE * SH - TTM["cash"]) / REV28, 2), arm_pe28=round(PRICE / EPS28, 2), arm_pe27=round(PRICE / C["eps_this"], 2))

# REVERSIÓN — P/E no-GAAP de los últimos 4 cierres de trimestre fiscal (EPS TTM aproximados como en sep)
win = [("31-dic-2025", 109.31, 1.77), ("31-mar-2026", 151.28, 1.77), ("30-jun-2026", 354.57, 1.87), ("30-sep-2026", 289.66, TTM["eps_ng"])]
pes_w = [p / e for _, p, e in win]
REV = sum(pes_w) / 4 * TTM["eps_ng"]
R["reversion"] = dict(window=[(d, p, round(e, 2), round(p / e, 1)) for d, p, e in win], pe_avg=round(sum(pes_w) / 4, 2),
                      eps_ttm=round(TTM["eps_ng"], 2), fv=round(REV, 2), fv_lo=round(min(pes_w) * TTM["eps_ng"], 2),
                      fv_hi=round(max(pes_w) * TTM["eps_ng"], 2), fv_crit_sep=round((pes_w[0] + pes_w[1]) / 2 * TTM["eps_ng"], 2),
                      pe_now=round(PRICE / TTM["eps_ng"], 1))

# SOTP: PI a 20x ingresos FY28E sin la mitad del objetivo de CPU AGI + CPU AGI $8B + caja
AGI_FY28 = 1.0
S = dict(ip_rev=REV28 - AGI_FY28, ip_ev=20 * (REV28 - AGI_FY28), agi=8.0, cash=TTM["cash"])
S["fv"] = (S["ip_ev"] + S["agi"] + S["cash"]) / SH
S["fv_15x"] = (15 * S["ip_rev"] + S["agi"] + S["cash"]) / SH
S["fv_25x_agi15"] = (25 * S["ip_rev"] + 15 + S["cash"]) / SH
R["sotp"] = {k: round(v, 2) for k, v in S.items()}
SOTP = R["sotp"]["fv"]

# DCF — año 1 = FY2027 (consenso), crecimiento FY2028 = consenso
REV1 = round(C["rev_this"], 3)
g28 = round((C["rev_next"] / C["rev_this"] - 1), 3)
cases = {"Bear": dict(g=(0.20, 0.07), o=(0.30, 0.31), c=(0.11, 0.09), wacc=0.123, gt=0.03),
         "Base": dict(g=(g28, 0.11), o=(0.33, 0.40), c=(0.10, 0.065), wacc=0.113, gt=0.035),
         "Bull": dict(g=(0.42, 0.15), o=(0.35, 0.46), c=(0.09, 0.06), wacc=0.103, gt=0.04)}
R["dcf"] = {}
for k, c in cases.items():
    r = dcf(REV1, c["g"], c["o"], c["c"], c["wacc"], c["gt"], TTM["cash"], SH)
    R["dcf"][k] = dict(fv=round(r["fv"], 2), tv_share=round(r["tv_share"] * 100, 1), fcf1=round(r["fcf"][0], 3),
                       rev5=round(r["revs"][-1], 2), g=[round(x * 100, 1) for x in c["g"]], wacc=round(c["wacc"] * 100, 1), gt=c["gt"] * 100)
fv = {k: R["dcf"][k]["fv"] for k in cases}
R["dcf_simple"] = round(sum(fv.values()) / 3, 2)
R["dcf_prob"] = round(0.25 * fv["Bear"] + 0.45 * fv["Base"] + 0.30 * fv["Bull"], 2)
DCF = fv["Base"]
b = cases["Base"]
gw = [0.103, 0.108, 0.113, 0.118, 0.123]
gg = [0.025, 0.03, 0.035, 0.04, 0.045]
R["grid"] = {"wacc": [x * 100 for x in gw], "g": [x * 100 for x in gg],
             "fv": [[round(dcf(REV1, b["g"], b["o"], b["c"], w, x, TTM["cash"], SH)["fv"], 2) for x in gg] for w in gw]}

M = {"DCF Base": DCF, "SOTP": SOTP, "Comparables": round(COMPS, 2), "Reversión": round(REV, 2), "Consenso": C["pt"]}
blend = sum(M[k] * W[k] for k in W)
R["methods"] = M
R["blend"] = round(blend, 2)
R["blend_gap"] = round((blend / PRICE - 1) * 100, 1)
R["blend_simple"] = round(sum(M.values()) / 5, 2)
R["blend_sin_consenso"] = round(sum(M[k] * W[k] for k in W if k != "Consenso") / 0.75, 2)
R["cambio_vs_sep_regla"] = round((blend / R["sep_blend_regla_vigente"] - 1) * 100, 1)
R["price"] = dict(now=PRICE, sep=PRICE_SEP, chg=round((PRICE / PRICE_SEP - 1) * 100, 1), off_hi=round((PRICE / HI52 - 1) * 100, 1),
                  mcap=round(PRICE * SH, 1), ev=round(PRICE * SH - TTM["cash"], 1))
json.dump(R, open(os.path.join(HERE, "resultados.json"), "w"), indent=1, ensure_ascii=False)
if __name__ == "__main__":
    for k, v in R.items():
        print(k, "=>", v)
