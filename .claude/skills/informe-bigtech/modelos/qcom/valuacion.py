"""
Modelo de valuación QCOM — actualización al 4T del año fiscal 2026 (trimestre cerrado 27-sep-2026; 8-K Ex. 99.1 y 10-K
del 4-nov-2026).

Correr:  python valuacion.py      (imprime todo y escribe resultados.json al lado)

Fuentes (verificadas contra el documento original):
  - 8-K Ex. 99.1 del 4-nov-2026: resultados del 4T y del año fiscal, segmentos (QCT/QTL), flujos de QCT (handsets, auto,
    IoT), guía del 1T FY27 (ingresos $10.4-11.2B, QCT $9.0-9.6B incluido Data Center, EPS no-GAAP $2.15-2.35), retorno de
    capital, balance y flujo de caja anual. Renovación de licencias QTL con Apple, Huawei y Transsion; colaboración con
    Amazon para centros de datos; meta de Data Center de $5B para FY27; ingresos no-handset +60% en FY27.
  - 8-K del 13-nov-2026: emisión de $4.0B en notas (2028-2036), posterior al cierre (neutra para la deuda neta).
  - SEC companyfacts XBRL (D&A anual). Yahoo Finance chart API: cierre 13-nov-2026 $172.47, cierres de fin de trimestre,
    ^TNX 5.15% (4.81% al 8-sep-2026).
  - stockanalysis.com (S&P Global), 15-nov-2026: PT $185.96 (37 analistas, $100-$320, "Hold"); FY27E ingresos $45.42B,
    EPS $9.59; FY28E $52.48B, EPS $12.21. Peers en ../peers_semis_3t26.json.

Convención del DCF (la de septiembre): año 0 = ingresos del año fiscal; crecimiento y margen de FCF lineales del año 1 al 5;
descuento a fin de año; VT = FCF5 x (1+g)/(WACC-g); equity = EV - deuda neta; acciones constantes.
Septiembre: el caso Base reproduce ($162.11 contra $162.14); Bear y Bull no ($94.40 y $290.21 contra $103.03 y $298.77):
ambos quedan ~$8.6 por acción abajo con la trayectoria declarada; esos dos escenarios no documentaron su senda año a año.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))

def lin(a, b, n=5):
    return [a + (b - a) * i / (n - 1) for i in range(n)]

def dcf(rev0, g, m, wacc, gt, nd, sh):
    r, revs, fcf = rev0, [], []
    for gi, mi in zip(lin(*g), lin(*m)):
        r *= 1 + gi
        revs.append(r)
        fcf.append(r * mi)
    pv = sum(f / (1 + wacc) ** (i + 1) for i, f in enumerate(fcf))
    pvtv = fcf[-1] * (1 + gt) / (wacc - gt) / (1 + wacc) ** 5
    ev = pv + pvtv
    return {"fv": (ev - nd) / sh, "tv_share": pvtv / ev, "fcf": fcf, "revs": revs}

R = {}
sep = {"Bear": dict(g=(-0.04, 0.03), m=(0.236, 0.236), wacc=0.11, gt=0.025),
       "Base": dict(g=(0.05, 0.035), m=(0.24, 0.27), wacc=0.10, gt=0.03),
       "Bull": dict(g=(0.12, 0.06), m=(0.25, 0.31), wacc=0.09, gt=0.035)}
sep_pub = {"Bear": 103.03, "Base": 162.14, "Bull": 298.77}
R["sep_repro"] = {k: dict(modelo=round(dcf(42.9, c["g"], c["m"], c["wacc"], c["gt"], 6.97, 1.05)["fv"], 2), publicado=sep_pub[k]) for k, c in sep.items()}
SEP_M = {"DCF Base": 162.14, "SOTP": 133.84, "Comparables": 201.70, "Reversión": 158.54, "Consenso": 193.10}
W = {"DCF Base": 0.075, "SOTP": 0.075, "Comparables": 0.25, "Reversión": 0.35, "Consenso": 0.25}
R["sep_blend_simple"] = round(sum(SEP_M.values()) / 5, 2)
R["sep_blend_regla_vigente"] = round(sum(SEP_M[k] * W[k] for k in W), 2)

# DATOS 4T FY26 / FY26 (miles de millones)
PRICE, PRICE_SEP, HI52, LO52 = 172.47, 176.43, 259.92, 121.99
PRICE_PRE, PRICE_POST = 173.19, 156.75
FY = dict(rev=43.120, rev_ng=43.240, opi=8.658, da=1.630, ni=13.628, eps=12.70, eps_ng=10.54, ocf=11.145, capex=2.494,
          buyback=7.817, div=3.854, rev25=44.284, eps_ng25=12.03, ocf25=14.012, capex25=1.192, qct_ebt=10.101, qtl_ebt=4.022,
          qct=37.208, qtl=5.556, handsets=24.072, auto=6.004, iot=7.132, tax_benefit=5.7)
FY["fcf"] = FY["ocf"] - FY["capex"]
FY["fcf_m"] = FY["fcf"] / FY["rev"] * 100
FY["fcf25_m"] = (FY["ocf25"] - FY["capex25"]) / FY["rev25"] * 100
FY["ebitda"] = FY["opi"] + FY["da"]
FY["rev_yoy"] = (FY["rev"] / FY["rev25"] - 1) * 100
FY["return"] = FY["buyback"] + FY["div"]
FY["return_pct_fcf"] = FY["return"] / FY["fcf"] * 100
FY["nonhandset"] = FY["auto"] + FY["iot"]
FY["nonhandset27_target"] = FY["nonhandset"] * 1.6
R["fy"] = {k: round(v, 3) for k, v in FY.items()}
Q = dict(rev=10.322, rev_ng=10.442, rev_ya=11.270, qct=9.015, qct_ya=9.821, qct_ebt=2.142, qtl=1.304, qtl_ya=1.409, qtl_ebt=0.918,
         handsets=5.137, handsets_ya=6.961, auto=1.990, auto_ya=1.053, iot=1.888, iot_ya=1.807, eps=1.17, eps_ng=2.17, eps_ng_ya=3.00,
         ebt=1.173, ebt_ng=2.666)
for k in ("rev", "qct", "qtl", "handsets", "auto", "iot"):
    Q[k + "_yoy"] = (Q[k] / Q[k + "_ya"] - 1) * 100
Q["qct_m"] = Q["qct_ebt"] / Q["qct"] * 100
Q["qtl_m"] = Q["qtl_ebt"] / Q["qtl"] * 100
Q["autoiot_yoy"] = ((Q["auto"] + Q["iot"]) / (Q["auto_ya"] + Q["iot_ya"]) - 1) * 100
Q["eps_ng_yoy"] = (Q["eps_ng"] / Q["eps_ng_ya"] - 1) * 100
Q["react"] = (PRICE_POST / PRICE_PRE - 1) * 100
R["q4"] = {k: round(v, 3) for k, v in Q.items()}
G = dict(lo=10.4, hi=11.2, mid=10.8, qct_lo=9.0, qct_hi=9.6, qtl_lo=1.3, qtl_hi=1.5, eps_lo=2.15, eps_hi=2.35, eps_mid=2.25)
G["yoy"] = (10.8 / 12.252 - 1) * 100
G["eps_yoy"] = (2.25 / 2.78 - 1) * 100
R["guide"] = {k: round(v, 2) for k, v in G.items()}
BAL = dict(cash=4.636, mkt=3.045, st_debt=2.492, lt_debt=12.620, equity=30.401, assets=60.829, sh=1.073, notes_nov=4.0)
BAL["liq"] = BAL["cash"] + BAL["mkt"]
BAL["debt"] = BAL["st_debt"] + BAL["lt_debt"]
BAL["net_debt"] = BAL["debt"] - BAL["liq"]
BAL["nd_ebitda"] = BAL["net_debt"] / FY["ebitda"]
R["bal"] = {k: round(v, 3) for k, v in BAL.items()}

# CONSENSO Y PEERS
P = json.load(open(os.path.join(HERE, "..", "peers_semis_3t26.json")))
C = P["QCOM"]
R["consenso"] = dict(pt=C["pt"], n=C["n"], lo=C["lo"], hi=C["hi"], rating=C["rating"], eps27=round(C["eps_this"], 2),
                     eps28=round(C["eps_next"], 2), rev27=round(C["rev_this"], 2), rev28=round(C["rev_next"], 2),
                     rev27_g=round((C["rev_this"] / FY["rev"] - 1) * 100, 1), eps27_g=round((C["eps_this"] / FY["eps_ng"] - 1) * 100, 1),
                     rev28_g=round((C["rev_next"] / C["rev_this"] - 1) * 100, 1), eps28_g=round((C["eps_next"] / C["eps_this"] - 1) * 100, 1),
                     upside=round((C["pt"] / PRICE - 1) * 100, 1))
EPS27 = C["eps_this"]          # QCOM FY sep-2027
pe27 = {"NVDA": P["NVDA"]["price"] / P["NVDA"]["eps_next"], "AVGO": P["AVGO"]["price"] / P["AVGO"]["eps_next"],
        "TXN": P["TXN"]["price"] / P["TXN"]["eps_next"], "ARM": P["ARM"]["price"] / P["ARM"]["eps_this"]}
panel = (pe27["NVDA"] + pe27["AVGO"] + pe27["TXN"]) / 3
R["comps"] = dict(pe27={k: round(v, 2) for k, v in pe27.items()}, panel=round(panel, 2), eps27=round(EPS27, 2),
                  fv=round(panel * EPS27, 2), fv_nvda=round(pe27["NVDA"] * EPS27, 2), fv_txn=round(pe27["TXN"] * EPS27, 2),
                  qcom_pe27=round(PRICE / EPS27, 2), qcom_pe26=round(PRICE / FY["eps_ng"], 2),
                  ev_ebitda_fy26=round((PRICE * BAL["sh"] + BAL["net_debt"]) / FY["ebitda"], 2))
COMPS = R["comps"]["fv"]

# SOTP: EBT de segmento anualizado del 4T FY26 (misma metodología que sep, que usaba el 3T)
qct_a, qtl_a = Q["qct_ebt"] * 4, Q["qtl_ebt"] * 4
def sotp(mq, ml): return ((qct_a * mq + qtl_a * ml) - BAL["net_debt"]) / BAL["sh"]
R["sotp"] = dict(qct_annual=round(qct_a, 3), qtl_annual=round(qtl_a, 3), ev=round(qct_a * 12 + qtl_a * 12, 2),
                 fv=round(sotp(12, 12), 2), lo=round(sotp(9, 10), 2), hi=round(sotp(14, 15), 2),
                 fy_basis=round(((FY["qct_ebt"] * 12 + FY["qtl_ebt"] * 12) - BAL["net_debt"]) / BAL["sh"], 2))
SOTP = R["sotp"]["fv"]

# REVERSIÓN: P/E no-GAAP de los últimos 4 cierres de trimestre fiscal
win = [("28-dic-2025", 174.81, 2.85 + 2.77 + 3.00 + 3.50), ("29-mar-2026", 127.11, 2.77 + 3.00 + 3.50 + 2.65),
       ("28-jun-2026", 189.39, 3.00 + 3.50 + 2.65 + 2.21), ("27-sep-2026", 201.97, 10.54)]
pes = [p / e for _, p, e in win]
pe_avg = sum(pes) / 4
REV = pe_avg * FY["eps_ng"]
R["reversion"] = dict(window=[(d, p, round(e, 2), round(p / e, 2)) for d, p, e in win], pe_avg=round(pe_avg, 2),
                      fv=round(REV, 2), fv_lo=round(min(pes) * FY["eps_ng"], 2), fv_hi=round(max(pes) * FY["eps_ng"], 2),
                      pe_now=round(PRICE / FY["eps_ng"], 2))

# DCF — año 0 = FY2026 real, año 1 = FY2027
WB = 0.103     # septiembre 10.0% + 0.34 pp de Treasury (4.81% → 5.15%), redondeado
cases = {"Bear": dict(g=(-0.04, 0.03), m=(0.20, 0.20), wacc=WB + 0.01, gt=0.025),
         "Base": dict(g=(0.053, 0.035), m=(0.21, 0.26), wacc=WB, gt=0.03),
         "Bull": dict(g=(0.12, 0.06), m=(0.23, 0.30), wacc=WB - 0.01, gt=0.035)}
R["dcf"] = {}
for k, c in cases.items():
    r = dcf(FY["rev"], c["g"], c["m"], c["wacc"], c["gt"], BAL["net_debt"], BAL["sh"])
    R["dcf"][k] = dict(fv=round(r["fv"], 2), tv_share=round(r["tv_share"] * 100, 1), fcf1=round(r["fcf"][0], 2),
                       rev1=round(r["revs"][0], 2), rev5=round(r["revs"][-1], 2), wacc=round(c["wacc"] * 100, 1), gt=c["gt"] * 100)
fv = {k: R["dcf"][k]["fv"] for k in cases}
R["dcf_simple"] = round(sum(fv.values()) / 3, 2)
R["dcf_prob"] = round(0.25 * fv["Bear"] + 0.45 * fv["Base"] + 0.30 * fv["Bull"], 2)
DCF = fv["Base"]
b = cases["Base"]
gw = [WB - 0.01, WB - 0.005, WB, WB + 0.005, WB + 0.01]
gg = [0.02, 0.025, 0.03, 0.035, 0.04]
R["grid"] = {"wacc": [round(x * 100, 1) for x in gw], "g": [x * 100 for x in gg],
             "fv": [[round(dcf(FY["rev"], b["g"], b["m"], w, x, BAL["net_debt"], BAL["sh"])["fv"], 2) for x in gg] for w in gw]}

M = {"DCF Base": DCF, "SOTP": SOTP, "Comparables": COMPS, "Reversión": round(REV, 2), "Consenso": C["pt"]}
blend = sum(M[k] * W[k] for k in W)
R["methods"] = M
R["blend"] = round(blend, 2)
R["blend_gap"] = round((blend / PRICE - 1) * 100, 1)
R["blend_simple"] = round(sum(M.values()) / 5, 2)
R["blend_sin_consenso"] = round(sum(M[k] * W[k] for k in W if k != "Consenso") / 0.75, 2)
R["cambio_vs_sep_regla"] = round((blend / R["sep_blend_regla_vigente"] - 1) * 100, 1)
R["price"] = dict(now=PRICE, sep=PRICE_SEP, chg=round((PRICE / PRICE_SEP - 1) * 100, 1), off_hi=round((PRICE / HI52 - 1) * 100, 1),
                  mcap=round(PRICE * BAL["sh"], 1), div_yield=round(0.92 * 4 / PRICE * 100, 2))
json.dump(R, open(os.path.join(HERE, "resultados.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
if __name__ == "__main__":
    for k, v in R.items():
        print(k, "=>", v)
