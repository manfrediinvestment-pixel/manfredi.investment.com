"""Shopify (SHOP) — modelo de valuación del informe informes/shop.html.

Cuatro métodos, pesos de la regla vigente de informe-bigtech (15/25/35/25):
  M1 DCF sobre margen de flujo de caja libre (capex ~0), tres escenarios ... 15%
  M2 Comparables (P/E 2027E de MELI / AMZN / SE / XYZ) .................... 25%
  M3 Reversión (precio / FCF TTM, 4 cierres trimestrales) ................. 35%
  M4 Consenso (precio objetivo promedio) .................................. 25%

DCF: año 1 = ingreso de consenso del primer año proyectado (igual en los tres escenarios); años 2-5 crecen
según el escenario; flujo = ingreso x margen de FCF. Se suma caja + inversiones (Shopify no tiene deuda).

Uso:  python valuacion.py [--json]
"""
import json, os, sys

W = dict(dcf=.15, comps=.25, rev=.35, cons=.25)


def dcf(rev1, g, m, r, gt, cash, sh):
    revs = [rev1]
    for x in g:
        revs.append(revs[-1] * (1 + x / 100))
    pv, f = 0.0, 0.0
    for t, (R, M) in enumerate(zip(revs, m)):
        f = R * M / 100
        pv += f / (1 + r) ** (t + 1)
    pvtv = f * (1 + gt) / (r - gt) / (1 + r) ** 5
    return (pv + pvtv + cash) / sh, pvtv / (pv + pvtv)


def run(P):
    out, sc = {}, {}
    for k, s in P['esc'].items():
        v, tv = dcf(P['rev1'], s['g'], s['m'], s['wacc'], s['gt'], P['cash'], P['sh'])
        sc[k] = dict(v=round(v, 2), tv=round(tv * 100, 1))
    out['dcf'] = sc
    out['dcf_ev_25_45_30'] = round(.25 * sc['bear']['v'] + .45 * sc['base']['v'] + .30 * sc['bull']['v'], 2)
    b = P['esc']['base']
    out['grid'] = {f'{w:.1f}': [round(dcf(P['rev1'], b['g'], b['m'], w / 100, gg / 100, P['cash'], P['sh'])[0], 2)
                                for gg in P['grid_g']] for w in P['grid_wacc']}
    if 'comps_fixed' in P:
        out['comps'] = dict(v=P['comps_fixed'])
    else:
        pe = P['pe']; avg = sum(pe.values()) / len(pe)
        out['comps'] = dict(por_peer={k: round(x * P['eps_fwd'], 2) for k, x in pe.items()}, mult=round(avg, 2),
                            v=round(avg * P['eps_fwd'], 2))
    rows = [dict(fecha=d, precio=px, sh=sh, fcf=f, mult=round(px * sh / f, 2)) for d, px, sh, f in P['rev_rows']]
    m = sum(r['mult'] for r in rows) / len(rows)
    out['rev'] = dict(filas=rows, mult_prom=round(m, 2), v=round(m * P['fcf_ttm'] / P['sh'], 2))
    vals = dict(dcf=sc['base']['v'], comps=out['comps']['v'], rev=out['rev']['v'], cons=P['pt'])
    out['metodos'] = vals
    out['promedio_simple'] = round(sum(vals.values()) / 4, 2)
    out['blend'] = round(sum(W[k] * vals[k] for k in W), 2)
    out['gap'] = round((out['blend'] / P['price'] - 1) * 100, 1)
    # DCF inverso: crecimiento constante de los años 2-5 que iguala el precio (márgenes/WACC/g del Base)
    lo, hi = -0.2, 1.5
    for _ in range(100):
        mid = (lo + hi) / 2
        v = dcf(P['rev1'], [mid * 100] * 4, b['m'], b['wacc'], b['gt'], P['cash'], P['sh'])[0]
        lo, hi = (mid, hi) if v < P['price'] else (lo, mid)
    out['dcf_inverso_g'] = round(mid * 100, 2)
    return out


# ---------------- Edición sep-2026 (2T 2026, precio 10-sep $127.20) ----------------
REPRO_SEP = dict(
    rev1=15230, cash=9107, sh=1303, price=127.20,
    esc=dict(
        # Base: reproduce $56.04 y la grilla publicada (error total $0.008 en 5 celdas).
        base=dict(g=[24, 19, 15, 12], m=[18.5, 19, 21, 21.5, 22], wacc=.115, gt=.035),
        bear=dict(g=[18, 13, 9, 7], m=[17] * 5, wacc=.125, gt=.03),          # $34.58 / 67.4% exacto
        bull=dict(g=[28, 24, 20, 16], m=[19, 21, 23, 25, 27], wacc=.105, gt=.04),   # lineal, $90.42 exacto
    ),
    grid_wacc=[10.5, 11.0, 11.5, 12.0, 12.5], grid_g=[2.5, 3.0, 3.5, 4.0, 4.5],
    comps_fixed=60.00,     # sep: promedio redondeado de P/E (27.0x x $2.45 = $66.15) y EV/beneficio bruto ($54.96)
    rev_rows=[('2025-09-30', 148.61, 1297, 1898), ('2025-12-31', 160.97, 1300.5, 2007),
              ('2026-03-31', 118.62, 1301, 2120), ('2026-06-30', 114.18, 1304, 2352)],
    fcf_ttm=2352, pt=171.15,
)

# ---------------- Edición 3T 2026 (trimestre cerrado 30-sep-2026; precio cierre 16-nov-2026 $147.81) ----------------
# Fuentes: 8-K y 10-Q del 3-nov-2026; Tesoro 16-nov-2026 (5.12%); stockanalysis.com 17-nov-2026; Yahoo Finance.
RF, BETA, ERP = 5.12, 1.5, 5.0          # beta ~1.5 como en sep (stockanalysis publica 2.66 a 5 años; ver informe)
KE = RF + BETA * ERP                    # 12.62% -> WACC Base 12.0% (caja neta ~6% del EV, mismo ajuste que sep)
CASH = 1868 + 2859 + 524 + 4911         # efectivo + valores negociables + inversiones LP + participaciones = 10,162
SH = 1290.73                            # acciones diluidas promedio 3T 2026
FCF_Q = dict(q425=725 - 10, q126=481 - 5, q226=658 - 4, q326=818 - 2)
FCF_TTM = sum(FCF_Q.values())           # 2,661
REV_TTM = 3672 + 3170 + 3583 + 3742     # 14,167

NOV = dict(
    rev1=19360, cash=CASH, sh=SH, price=147.81,
    esc=dict(
        # Horizonte corrido un año (2027-2031): año 1 = consenso de ingresos 2027. Crecimiento de los años 2-5 = la
        # trayectoria de sep corrida un año; margen de FCF re-anclado (TTM 18.8%, 3T 22%, 4T guiado como 4T25 ~19.5%).
        base=dict(g=[19, 15, 12, 10], m=[19.5, 20.5, 21.5, 22, 22.5], wacc=.12, gt=.035),
        bear=dict(g=[13, 9, 7, 5], m=[18.0] * 5, wacc=.13, gt=.03),
        bull=dict(g=[24, 20, 16, 13], m=[20, 22, 24, 26, 27], wacc=.11, gt=.04),
    ),
    grid_wacc=[11.0, 11.5, 12.0, 12.5, 13.0], grid_g=[2.5, 3.0, 3.5, 4.0, 4.5],
    pe=dict(MELI=27.40, AMZN=23.58, SE=15.02, XYZ=15.42), eps_fwd=2.46,
    rev_rows=[('2025-12-31', 160.97, 1300.5, 2007), ('2026-03-31', 118.62, 1301, 2120),
              ('2026-06-30', 114.18, 1304, 2352), ('2026-09-30', 148.30, SH, FCF_TTM)],
    fcf_ttm=FCF_TTM, pt=177.18, pt_lo=120, pt_hi=220, pt_med=180,
)

if __name__ == '__main__':
    sep, nov = run(REPRO_SEP), run(NOV)
    print('== Reproducción sep-2026 ==')
    print(json.dumps(sep, indent=1, ensure_ascii=False))
    print('promedio simple publicado $110.38 -> modelo', sep['promedio_simple'], '| ponderado regla vigente', sep['blend'])
    print('\n== Edición 3T 2026 ==  Ke %.2f%%  caja+inv %d  FCF TTM %d (%.1f%%)' % (KE, CASH, FCF_TTM, FCF_TTM / REV_TTM * 100))
    print(json.dumps(nov, indent=1, ensure_ascii=False))
    if '--json' in sys.argv:
        p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resultados.json')
        with open(p, 'w', encoding='utf-8') as fh:
            json.dump(dict(sep=sep, nov=nov, ke=round(KE, 2), cash=CASH, fcf_ttm=FCF_TTM, rev_ttm=REV_TTM, fcf_q=FCF_Q),
                      fh, indent=1, ensure_ascii=False)
