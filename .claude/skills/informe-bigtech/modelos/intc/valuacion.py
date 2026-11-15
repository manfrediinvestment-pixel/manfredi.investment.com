"""
Modelo de valuación INTC — actualización al 3T 2026 (trimestre cerrado 26-sep-2026; 8-K del 29-oct-2026, 10-Q del 30-oct-2026).

Correr:  python valuacion.py      (imprime todo y escribe resultados.json al lado)

Fuentes (verificadas contra el documento original):
  - 8-K Ex. 99.1 del 29-oct-2026: resultados, segmentos, guía 4T26, flujo de caja, balance, FCF ajustado.
  - 10-Q del 3T26: oferta pública del 12-ago-2026 (~242M acciones a $95, $23.0B brutos / $22.617B netos); recompra del 49%
    de Apollo en Ireland SCIP (8-abr-2026, $14.2B); acciones en garantía del gobierno (132M sin liberar; pasivo derivado
    $8.6B corriente + $5.1B no corriente, se cancela con acciones); compromisos de capex $19.6B; sustratos $5.3-6.1B;
    compra de Classiq (~$1.9B); interés minoritario $16.64B (Arizona SCIP 49% Brookfield + Mobileye).
  - SEC companyfacts XBRL: OCF, capex, inversiones de corto plazo (AvailableForSaleSecuritiesDebtSecuritiesCurrent).
  - Yahoo Finance chart API: cierre 13-nov-2026 $59.66; ^TNX 5.15% (4.62% al 5-ago-2026); TWD 32.94 por USD.
  - stockanalysis.com (S&P Global), 15-nov-2026: PT $90.65 (49 analistas, $63-$160, "Hold"); FY26E ingresos $61.74B,
    EPS $1.49; FY27E $69.13B, EPS $1.79. Peers en ../peers_semis_3t26.json.

Convención del DCF (la de agosto, reproducida al centavo): año 0 = ingresos FY2026E de consenso; crecimiento, margen de
OCF y capex/ingresos interpolados en línea recta del año 1 al 5; FCF = ingresos x (OCF% - capex%); descuento a fin de
año; VT = FCF5 x (1+g)/(WACC-g); equity = EV - deuda neta (- interés minoritario desde esta edición) ÷ acciones diluidas.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))

def lin(a, b, n=5):
    return [a + (b - a) * i / (n - 1) for i in range(n)]

def dcf(rev0, g, o, c, wacc, gt, claims, shares):
    r, revs, fcf = rev0, [], []
    for gi, oi, ci in zip(lin(*g), lin(*o), lin(*c)):
        r *= 1 + gi
        revs.append(r)
        fcf.append(r * (oi - ci))
    pv = sum(f / (1 + wacc) ** (i + 1) for i, f in enumerate(fcf))
    pvtv = fcf[-1] * (1 + gt) / (wacc - gt) / (1 + wacc) ** 5
    ev = pv + pvtv
    return {"fv": (ev - claims) / shares, "tv_share": pvtv / ev, "fcf": fcf, "revs": revs, "ev": ev}

R = {}

# ---------------------------------------------------------------------------
# 1) REPRODUCCIÓN DE AGOSTO (datos al 2T26, precio $101.06 al 5-ago-2026)
# ---------------------------------------------------------------------------
AUG = dict(rev0=63.03, net_debt=37.66, shares=5.104)
aug_cases = {
    "Bear": dict(g=(0.08, 0.03), o=(0.20, 0.24), c=(0.22, 0.14), wacc=0.115, gt=0.025),
    "Base": dict(g=(0.18, 0.06), o=(0.23, 0.32), c=(0.32, 0.16), wacc=0.105, gt=0.03),
    "Bull": dict(g=(0.28, 0.10), o=(0.28, 0.38), c=(0.28, 0.14), wacc=0.095, gt=0.035),
}
aug_pub = {"Bear": 5.23, "Base": 23.91, "Bull": 80.46}
R["aug_repro"] = {}
for k, c in aug_cases.items():
    r = dcf(AUG["rev0"], c["g"], c["o"], c["c"], c["wacc"], c["gt"], AUG["net_debt"], AUG["shares"])
    R["aug_repro"][k] = {"modelo": round(r["fv"], 2), "publicado": aug_pub[k], "fcf1": round(r["fcf"][0], 2)}
# Error de agosto: la deuda neta no restaba las inversiones de corto plazo ($16.853B al 27-jun-2026)
AUG_NET_DEBT_OK = 1.988 + 48.549 - 12.874 - 16.853
R["aug_net_debt_correcta"] = round(AUG_NET_DEBT_OK, 3)
R["aug_base_con_deuda_correcta"] = round(dcf(AUG["rev0"], **{k: v for k, v in aug_cases["Base"].items() if k in ("g", "o", "c", "wacc", "gt")},
                                             claims=AUG_NET_DEBT_OK, shares=AUG["shares"])["fv"], 2)
AUG_M = {"DCF Base": 23.91, "Comparables": 70.69, "Reversión": 16.73, "Consenso": 115.27}
W = {"DCF Base": 0.15, "Comparables": 0.25, "Reversión": 0.35, "Consenso": 0.25}
R["aug_blend_simple"] = round(sum(AUG_M.values()) / 4, 2)            # $56.65 publicado
R["aug_blend_regla_vigente"] = round(sum(AUG_M[k] * W[k] for k in W), 2)

# ---------------------------------------------------------------------------
# 2) DATOS DEL 3T26 (miles de millones USD)
# ---------------------------------------------------------------------------
PRICE, PRICE_AUG = 59.66, 101.06
PRICE_PRE, PRICE_POST = 92.07, 65.76          # cierres 29-oct (reporte tras el cierre) y 30-oct-2026
HI52, LO52 = 142.35, 32.89
TSY10, TSY10_AUG = 5.15, 4.62
q = ["3T25", "4T25", "1T26", "2T26", "3T26"]
rev = [13.653, 13.674, 13.577, 16.128, 16.513]
gp = [5.218, 4.943, 5.347, 6.509, 7.096]
opi = [0.683, 0.580, -3.136, 1.796, 2.522]
ni = [4.063, -0.591, -3.728, -11.033, 3.320]
eps = [0.90, -0.13, -0.73, -2.16, 0.60]
ocf = [2.546, 4.288, 1.096, 13.184 - 1.096 - 5.082, 5.082]
capex = [2.425, 3.488, 3.636, 10.216 - 3.636 - 4.024, 4.024]
ttm = lambda a: sum(a[1:5])
TTM = dict(rev=ttm(rev), gp=ttm(gp), opi=ttm(opi), ni=ttm(ni), eps=ttm(eps), ocf=ttm(ocf), capex=ttm(capex))
TTM["fcf"] = TTM["ocf"] - TTM["capex"]
for k in ("gp", "opi", "ocf", "capex", "fcf"):
    TTM[k + "_m"] = TTM[k] / TTM["rev"] * 100
TTM_YA = 14.260 + 12.667 + 12.859 + 13.653
TTM["rev_yoy"] = (TTM["rev"] / TTM_YA - 1) * 100
R["ttm"] = {k: round(v, 3) for k, v in TTM.items()}
R["quarters"] = {l: dict(rev=rev[i], gm=round(gp[i] / rev[i] * 100, 1), om=round(opi[i] / rev[i] * 100, 1),
                         ocf_m=round(ocf[i] / rev[i] * 100, 1), capex_m=round(capex[i] / rev[i] * 100, 1)) for i, l in enumerate(q)}
SEG = {"CCPG": (8.097, 8.535), "DCAI": (7.318, 4.117), "Intel Products": (15.415, 12.652), "Intel Foundry": (6.697, 4.235),
       "All Other": (0.692, 0.993)}
R["seg"] = {k: dict(rev=v[0], yoy=round((v[0] / v[1] - 1) * 100, 1)) for k, v in SEG.items()}
R["seg_oi"] = {"CCPG": 2.285, "DCAI": 3.039, "Intel Products": 5.324, "Intel Foundry": -1.853, "All Other": 0.179,
               "foundry_m": round(-1.853 / 6.697 * 100, 1), "dcai_m": round(3.039 / 7.318 * 100, 1), "ccpg_m": round(2.285 / 8.097 * 100, 1)}
R["q3"] = dict(rev_yoy=round((16.513 / 13.653 - 1) * 100, 1), rev_qoq=round((16.513 / 16.128 - 1) * 100, 1),
               gm=round(7.096 / 16.513 * 100, 1), om=round(2.522 / 16.513 * 100, 1), ocf_m=round(5.082 / 16.513 * 100, 1),
               capex_m=round(4.024 / 16.513 * 100, 1), escrow_gain=1.005, eps_ng=0.52, eps=0.60, adj_fcf=1.639,
               elim=round(16.513 - 15.415 - 6.697 - 0.692, 3), react=round((PRICE_POST / PRICE_PRE - 1) * 100, 1))
G = dict(lo=15.0, hi=16.0, mid=15.5, gm_gaap=37.1, gm_ng=38.0, eps=0.10, eps_ng=0.25)
G["yoy"] = (15.5 / 13.674 - 1) * 100
G["qoq"] = (15.5 / 16.513 - 1) * 100
G["fy26"] = 13.577 + 16.128 + 16.513 + 15.5
G["fy26_yoy"] = (G["fy26"] / 52.853 - 1) * 100
G["capex_9m_gross"] = 10.216
G["capex_q4_floor"] = 20.0 - 10.216
R["guide"] = {k: round(v, 2) for k, v in G.items()}

BAL = dict(cash=21.846, sti=32.159, st_debt=3.817, lt_debt=46.317, nci=16.642, escrow_liab=8.6 + 5.1,
           cash_jun=12.874, sti_jun=16.853, debt_jun=1.988 + 48.549, equity_intel=114.914, assets=228.574,
           capex_commit=19.6, offering_gross=23.0, offering_net=22.617, apollo=14.2, shares_dil=5.307, shares_dil_aug=5.104,
           shares_out=5.310, shares_out_dec=4.994)
BAL["liq"] = BAL["cash"] + BAL["sti"]
BAL["debt"] = BAL["st_debt"] + BAL["lt_debt"]
BAL["net_cash"] = BAL["liq"] - BAL["debt"]
BAL["claims"] = -BAL["net_cash"] + BAL["nci"]          # lo que se resta del EV: deuda neta (negativa) + minoritarios
BAL["dil_yoy"] = (5.307 / 4.531 - 1) * 100
R["bal"] = {k: round(v, 3) for k, v in BAL.items()}

# ---------------------------------------------------------------------------
# 3) CONSENSO Y PEERS
# ---------------------------------------------------------------------------
P = json.load(open(os.path.join(HERE, "..", "peers_semis_3t26.json")))
C = P["INTC"]
R["consenso"] = dict(pt=C["pt"], n=C["n"], lo=C["lo"], hi=C["hi"], rating=C["rating"], eps26=round(C["eps_this"], 2),
                     eps27=round(C["eps_next"], 2), rev26=round(C["rev_this"], 2), rev27=round(C["rev_next"], 2),
                     rev26_g=round((C["rev_this"] / 52.853 - 1) * 100, 1), rev27_g=round((C["rev_next"] / C["rev_this"] - 1) * 100, 1),
                     eps27_g=round((C["eps_next"] / C["eps_this"] - 1) * 100, 1), upside=round((C["pt"] / PRICE - 1) * 100, 1))
TWD = 32.94
tsm_eps27_adr = P["TSM"]["eps_next"] * 5 / TWD
pe = {"TSM": P["TSM"]["price"] / tsm_eps27_adr, "GFS": P["GFS"]["price"] / P["GFS"]["eps_next"], "AMD": P["AMD"]["price"] / P["AMD"]["eps_next"]}
panel = (pe["TSM"] + pe["GFS"]) / 2
EPS27 = C["eps_next"]
R["comps"] = dict(tsm_eps27_adr=round(tsm_eps27_adr, 2), pe={k: round(v, 2) for k, v in pe.items()}, panel=round(panel, 2),
                  eps27=round(EPS27, 2), fv=round(panel * EPS27, 2), fv_tsm=round(pe["TSM"] * EPS27, 2), fv_gfs=round(pe["GFS"] * EPS27, 2),
                  fv_amd=round(pe["AMD"] * EPS27, 2), intc_pe27=round(PRICE / EPS27, 2), intc_pe26=round(PRICE / C["eps_this"], 2))
COMPS = R["comps"]["fv"]

# Reversión: misma metodología que agosto (P/E mediana 2021-2025, 8.2x, sobre EPS 2027E de consenso)
REV = 8.2 * EPS27
R["reversion"] = dict(pe=8.2, eps27=round(EPS27, 2), fv=round(REV, 2))
# Chequeo: ventana de los últimos 4 cierres con EPS GAAP TTM — inutilizable (EPS TTM negativo en 3 de 4 cierres)
win = [("26-dic-2025", 36.20, 0.90 + (-0.13) + (-0.19) + (-0.67)), ("27-mar-2026", 43.13, 0.90 - 0.13 - 0.73 - 0.67),
       ("26-jun-2026", 128.32, 0.90 - 0.13 - 0.73 - 2.16), ("25-sep-2026", 123.00, -0.13 - 0.73 - 2.16 + 0.60)]
R["reversion"]["ventana_4t_eps_ttm"] = [(d, p, round(e, 2)) for d, p, e in win]

# ---------------------------------------------------------------------------
# 4) DCF — año 0 = FY2026E (9M reales + 4T guiado), año 1 = FY2027
# ---------------------------------------------------------------------------
REV0 = round(C["rev_this"], 2)
dW = round(TSY10 - TSY10_AUG, 2)          # +0.53 pp de tasa libre de riesgo desde agosto → +0.5 pp en los tres WACC
cases = {
    "Bear": dict(g=(0.05, 0.03), o=(0.24, 0.26), c=(0.26, 0.14), wacc=0.12, gt=0.025),
    "Base": dict(g=(0.12, 0.06), o=(0.27, 0.33), c=(0.36, 0.16), wacc=0.11, gt=0.03),
    "Bull": dict(g=(0.20, 0.10), o=(0.30, 0.38), c=(0.34, 0.14), wacc=0.10, gt=0.035),
}
R["dcf"] = {}
for k, c in cases.items():
    r = dcf(REV0, c["g"], c["o"], c["c"], c["wacc"], c["gt"], BAL["claims"], BAL["shares_dil"])
    R["dcf"][k] = dict(fv=round(r["fv"], 2), tv_share=round(r["tv_share"] * 100, 1), fcf=[round(x, 2) for x in r["fcf"]],
                       rev1=round(r["revs"][0], 2), rev5=round(r["revs"][-1], 2), capex1=round(r["revs"][0] * c["c"][0], 2),
                       wacc=c["wacc"] * 100, gt=c["gt"] * 100, ev=round(r["ev"], 2))
fv = {k: R["dcf"][k]["fv"] for k in cases}
R["dcf_simple"] = round(sum(fv.values()) / 3, 2)
R["dcf_prob"] = round(0.25 * fv["Bear"] + 0.45 * fv["Base"] + 0.30 * fv["Bull"], 2)
R["dcf_base_sin_nci"] = round(dcf(REV0, cases["Base"]["g"], cases["Base"]["o"], cases["Base"]["c"], 0.11, 0.03,
                                  -BAL["net_cash"], BAL["shares_dil"])["fv"], 2)
DCF = fv["Base"]
b = cases["Base"]
gw = [0.10, 0.105, 0.11, 0.115, 0.12]
gg = [0.02, 0.025, 0.03, 0.035, 0.04]
R["grid"] = {"wacc": [x * 100 for x in gw], "g": [x * 100 for x in gg],
             "fv": [[round(dcf(REV0, b["g"], b["o"], b["c"], w, x, BAL["claims"], BAL["shares_dil"])["fv"], 2) for x in gg] for w in gw]}

# DCF inverso: margen de OCF plano necesario (resto del Base igual) para llegar al precio
def solve(f, lo, hi):
    for _ in range(200):
        m = (lo + hi) / 2
        if f(m) < PRICE: lo = m
        else: hi = m
    return m
mm = solve(lambda x: dcf(REV0, b["g"], (x, x), b["c"], b["wacc"], b["gt"], BAL["claims"], BAL["shares_dil"])["fv"], 0, 1)
R["inverse"] = dict(ocf_flat=round(mm * 100, 1))
R["ocf_9m26_m"] = round(13.184 / (13.577 + 16.128 + 16.513) * 100, 1)

# ---------------------------------------------------------------------------
# 5) BLEND (regla vigente 15/25/35/25, sin SOTP)
# ---------------------------------------------------------------------------
M = {"DCF Base": DCF, "Comparables": COMPS, "Reversión": round(REV, 2), "Consenso": C["pt"]}
blend = sum(M[k] * W[k] for k in W)
R["methods"] = M
R["blend"] = round(blend, 2)
R["blend_gap"] = round((blend / PRICE - 1) * 100, 1)
R["blend_simple"] = round(sum(M.values()) / 4, 2)
R["blend_sin_consenso"] = round(sum(M[k] * W[k] for k in W if k != "Consenso") / 0.75, 2)
R["cambio_vs_aug_regla"] = round((blend / R["aug_blend_regla_vigente"] - 1) * 100, 1)
R["price"] = dict(now=PRICE, aug=PRICE_AUG, chg=round((PRICE / PRICE_AUG - 1) * 100, 1), hi52=HI52, lo52=LO52,
                  off_hi=round((PRICE / HI52 - 1) * 100, 1), mcap=round(PRICE * BAL["shares_out"], 1),
                  vs_offering=round((PRICE / 95 - 1) * 100, 1), pe26=round(PRICE / C["eps_this"], 1))

json.dump(R, open(os.path.join(HERE, "resultados.json"), "w"), indent=1, ensure_ascii=False)
if __name__ == "__main__":
    for k, v in R.items():
        print(k, "=>", v)
