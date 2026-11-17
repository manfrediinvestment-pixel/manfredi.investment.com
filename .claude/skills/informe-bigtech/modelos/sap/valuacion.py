"""SAP SE (SAP, ADR NYSE) — modelo de valuación del informe informes/sap.html.

Todo el modelo corre en EUR (SAP reporta en EUR/IFRS) y se convierte a USD por ADR (1 ADR = 1 acción) al EUR/USD
de la fecha del precio de referencia.

Cuatro métodos, pesos de la regla vigente de informe-bigtech (15/25/35/25):
  M1 DCF (OCF - capex) en EUR, tres escenarios, WACC sobre Bund ... 15%
  M2 Comparables (P/E 2027E de MSFT / ORCL / CRM / WDAY) .......... 25%
  M3 Reversión (P/E no-IFRS TTM, 4 cierres trimestrales, en EUR) .. 35%
  M4 Consenso (precio objetivo promedio del ADR) .................. 25%

Uso:  python valuacion.py [--json]
"""
import json, os, sys

W = dict(dcf=.15, comps=.25, rev=.35, cons=.25)
lin = lambda a, z: [a + (z - a) * i / 4 for i in range(5)]


def dcf(rev0, g, m, c, r, gt, nd, sh, fx):
    """nd = deuda neta (+) o caja neta (-) en EUR millones; devuelve USD por ADR."""
    rev, pv, f = rev0, 0.0, 0.0
    for t in range(5):
        rev *= 1 + g[t] / 100
        f = rev * (m[t] - c[t]) / 100
        pv += f / (1 + r) ** (t + 1)
    pvtv = f * (1 + gt) / (r - gt) / (1 + r) ** 5
    return (pv + pvtv - nd) / sh * fx, pvtv / (pv + pvtv)


def run(P):
    out, sc = {}, {}
    for k, s in P['esc'].items():
        v, tv = dcf(P['rev0'], s['g'], s['m'], s['c'], s['wacc'], s['gt'], P['nd'], P['sh'], P['fx'])
        sc[k] = dict(v=round(v, 2), tv=round(tv * 100, 1))
    out['dcf'] = sc
    out['dcf_ev_25_45_30'] = round(.25 * sc['bear']['v'] + .45 * sc['base']['v'] + .30 * sc['bull']['v'], 2)
    b = P['esc']['base']
    out['grid'] = {f'{w:.2f}': [round(dcf(P['rev0'], b['g'], b['m'], b['c'], w / 100, gg / 100, P['nd'], P['sh'], P['fx'])[0], 2)
                                for gg in P['grid_g']] for w in P['grid_wacc']}
    eps_usd = P['eps_fwd_eur'] * P['fx']
    pe = P['pe']
    avg = sum(pe.values()) / len(pe)
    out['comps'] = dict(eps_usd=round(eps_usd, 2), por_peer={k: round(x * eps_usd, 2) for k, x in pe.items()},
                        mult=round(avg, 2), v=round(avg * eps_usd, 2))
    rows = []
    for d, adr, fxd, e in P['rev_rows']:
        eur = adr / fxd
        rows.append(dict(fecha=d, adr=adr, fx=fxd, eur=round(eur, 2), eps=e, pe=round(eur / e, 2)))
    m = sum(r['pe'] for r in rows) / len(rows)
    out['rev'] = dict(filas=rows, pe_prom=round(m, 2), v=round(m * P['eps_ttm'] * P['fx'], 2))
    if 'pe_10a' in P:
        out['rev']['ref_10a'] = round(P['pe_10a'] * P['eps_ttm'] * P['fx'], 2)
    vals = dict(dcf=sc['base']['v'], comps=out['comps']['v'], rev=out['rev']['v'], cons=P['pt'])
    out['metodos'] = vals
    out['promedio_simple'] = round(sum(vals.values()) / 4, 2)
    out['blend'] = round(sum(W[k] * vals[k] for k in W), 2)
    out['gap'] = round((out['blend'] / P['price'] - 1) * 100, 1)
    lo, hi = -0.3, 0.8
    for _ in range(100):
        mid = (lo + hi) / 2
        v = dcf(P['rev0'], [mid * 100] * 5, b['m'], b['c'], b['wacc'], b['gt'], P['nd'], P['sh'], P['fx'])[0]
        lo, hi = (mid, hi) if v < P['price'] else (lo, mid)
    out['dcf_inverso_g'] = round(mid * 100, 2)
    return out


# ---------------- Edición sep-2026 (2T 2026, precio 4-sep $215.11, EUR/USD 1.1633) ----------------
REPRO_SEP = dict(
    rev0=36800, nd=0, sh=1158, fx=1.1633, price=215.11,
    esc=dict(  # lineal (así lo declaraba el informe): Base $185.93 vs $185.97 publicado, Bull $265.00 vs $264.99, Bear $124.04 vs $124.51
        base=dict(g=lin(9, 7), m=lin(25, 28), c=lin(2, 2.5), wacc=.09, gt=.025),
        bear=dict(g=lin(7, 3), m=lin(24, 25), c=[2.5] * 5, wacc=.0975, gt=.02),
        bull=dict(g=lin(11, 8), m=lin(25.5, 30), c=[2.0] * 5, wacc=.0825, gt=.03),
    ),
    grid_wacc=[8.0, 8.5, 9.0, 9.5, 10.0], grid_g=[1.5, 2.0, 2.5, 3.0, 3.5],
    pe=dict(MSFT=25.0, ORCL=19.7, CRM=17.68, WDAY=16.26), eps_fwd_eur=7.00,
    # tal como se publicó: precios en EUR convertidos con tipos de cambio que no eran los de cada fecha
    rev_rows=[('2025-09-30', 267.21, 267.21 / 231.2, 5.74), ('2025-12-31', 242.91, 242.91 / 217.4, 6.15),
              ('2026-03-31', 171.21, 171.21 / 153.4, 6.43), ('2026-06-30', 154.11, 154.11 / 141.4, 6.52)],
    eps_ttm=6.52, pt=247.25,
)

# ---------------- Edición 3T 2026 (trimestre cerrado 30-sep-2026; precio cierre 16-nov-2026 $233.83) ----------------
# Fuentes: Quarterly Statement Q3 2026 (6-K del 26-oct-2026, publicado 21-oct); 20-F FY2025 (XBRL ifrs-full);
# Yahoo Finance (ADR y EUR/USD); stockanalysis.com 17-nov-2026 (consenso en EUR, precio objetivo del ADR, beta);
# Bund 10 años ~3.3% (Trading Economics, 12-nov-2026); Tesoro 10 años 5.12% (16-nov-2026).
FX = 1.1025
PRICE = 233.83
BUND, BETA, ERP_EU = 3.30, 1.05, 5.5
KE = BUND + BETA * ERP_EU                    # 9.08% -> WACC Base 9.5% (mismo redondeo hacia arriba que sep: 8.5 -> 9.0)
CASH, OFA_CP = 9364, 1633                    # efectivo + otros activos financieros corrientes (inversiones CP)
FIN_LIAB = 2053 + 8535                       # pasivos financieros corrientes + no corrientes (bonos, préstamos, leasing)
NCI = 513
ND = FIN_LIAB - CASH - OFA_CP + NCI          # +104 (deuda neta + minoritarios, EUR millones)
SH = 1157                                    # acciones diluidas promedio 3T 2026
REV_TTM = (36800 - 27116) + 29703            # 39,387
OCF_TTM = (9156 - 7859) + 8586               # 9,883 -> 25.1%
CAPEX_TTM = (739 - 559) + 521                # 701 -> 1.8%
EPS_NONIFRS_TTM = round(6.15 - 4.53 + 5.20, 2)   # 6.82 (básico)

NOV = dict(
    rev0=REV_TTM, nd=ND, sh=SH, fx=FX, price=PRICE,
    esc=dict(
        # Crecimiento re-anclado a la guía (total +10.6% cc en 2026 "y acelerando en 2027"; consenso 2027 +12.0%;
        # backlog de nube +26% cc). Margen de OCF del año 1 entre el TTM (25.1%) y la guía de FCF de ~EUR 10B (~26.5%).
        base=dict(g=lin(11.5, 7), m=lin(26, 28), c=lin(2, 2.5), wacc=.095, gt=.025),
        bear=dict(g=lin(8, 3), m=[25.0] * 5, c=[2.5] * 5, wacc=.1025, gt=.02),
        bull=dict(g=lin(13, 8), m=lin(26.5, 30), c=[2.0] * 5, wacc=.0875, gt=.03),
    ),
    grid_wacc=[8.5, 9.0, 9.5, 10.0, 10.5], grid_g=[1.5, 2.0, 2.5, 3.0, 3.5],
    pe=dict(MSFT=25.89, ORCL=10.77, CRM=13.41, WDAY=14.66), eps_fwd_eur=8.49,   # EPS no-IFRS 2027E (EUR)
    rev_rows=[('2025-12-31', 242.91, 1.1747, 6.15), ('2026-03-31', 171.21, 1.1574, 6.43),
              ('2026-06-30', 154.11, 1.1413, 6.52), ('2026-09-30', 208.48, 1.1327, EPS_NONIFRS_TTM)],
    eps_ttm=EPS_NONIFRS_TTM, pe_10a=22.0, pt=284.50, pt_lo=260, pt_hi=333, pt_med=281.50,
)
KE_USD = 5.12 + BETA * 5.0                   # 10.37%: referencia con Rf del Tesoro

if __name__ == '__main__':
    sep, nov = run(REPRO_SEP), run(NOV)
    print('== Reproducción sep-2026 ==')
    print(json.dumps(sep, indent=1, ensure_ascii=False))
    print('promedio simple publicado $205.76 -> modelo', sep['promedio_simple'], '| ponderado regla vigente', sep['blend'])
    print('\n== Edición 3T 2026 ==  Ke %.2f%%  ND %d  OCF %.1f%%  capex %.1f%%  EPS TTM %.2f' % (
        KE, ND, OCF_TTM / REV_TTM * 100, CAPEX_TTM / REV_TTM * 100, EPS_NONIFRS_TTM))
    print(json.dumps(nov, indent=1, ensure_ascii=False))
    usd = dcf(NOV['rev0'], NOV['esc']['base']['g'], NOV['esc']['base']['m'], NOV['esc']['base']['c'], .105, .025, ND, SH, FX)[0]
    print('Base con WACC 10.5%% (Rf Tesoro): %.2f' % usd)
    if '--json' in sys.argv:
        p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resultados.json')
        with open(p, 'w', encoding='utf-8') as fh:
            json.dump(dict(sep=sep, nov=nov, ke=round(KE, 2), ke_usd=round(KE_USD, 2), base_wacc_usd=round(usd, 2),
                           nd=ND, rev_ttm=REV_TTM, ocf_ttm=OCF_TTM, capex_ttm=CAPEX_TTM, eps_ttm=EPS_NONIFRS_TTM),
                      fh, indent=1, ensure_ascii=False)
