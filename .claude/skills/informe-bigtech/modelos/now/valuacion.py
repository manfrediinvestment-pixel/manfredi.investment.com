"""ServiceNow (NOW) — modelo de valuación del informe informes/now.html.

Cuatro métodos, pesos de la regla vigente de informe-bigtech (15/25/35/25):
  M1 DCF (OCF - capex), tres escenarios ...................... 15%
  M2 Comparables (P/E 2027E de CRM / WDAY / SAP / PLTR) ...... 25%  (se muestra también sin PLTR)
  M3 Reversión a la media propia (P/E GAAP TTM, 4 cierres) ... 35%
  M4 Consenso (precio objetivo promedio) ..................... 25%

Uso:  python valuacion.py          -> reproducción de sep-2026 y edición 3T 2026
      python valuacion.py --json   -> además escribe resultados.json (UTF-8)
"""
import json, os, sys

W = dict(dcf=.15, comps=.25, rev=.35, cons=.25)


def dcf(rev0, g, m, c, r, gt, nd, sh):
    rev, pv, f = rev0, 0.0, 0.0
    for t in range(5):
        rev *= 1 + g[t] / 100
        f = rev * (m[t] - c[t]) / 100
        pv += f / (1 + r) ** (t + 1)
    pvtv = f * (1 + gt) / (r - gt) / (1 + r) ** 5
    return (pv + pvtv - nd) / sh, pvtv / (pv + pvtv)


def run(P):
    out, sc = {}, {}
    for k, s in P['esc'].items():
        v, tv = dcf(P['rev0'], s['g'], s['m'], s['c'], s['wacc'], s['gt'], P['nd'], P['sh'])
        sc[k] = dict(v=round(v, 2), tv=round(tv * 100, 1))
    out['dcf'] = sc
    out['dcf_ev_25_45_30'] = round(.25 * sc['bear']['v'] + .45 * sc['base']['v'] + .30 * sc['bull']['v'], 2)
    b = P['esc']['base']
    out['grid'] = {f'{w:.2f}': [round(dcf(P['rev0'], b['g'], b['m'], b['c'], w / 100, gg / 100, P['nd'], P['sh'])[0], 2)
                                for gg in P['grid_g']] for w in P['grid_wacc']}
    pe = P['pe']
    out['comps'] = dict(por_peer={k: round(x * P['eps_fwd'], 2) for k, x in pe.items()})
    avg = sum(pe.values()) / len(pe)
    ex = {k: x for k, x in pe.items() if k != 'PLTR'}
    avg_ex = sum(ex.values()) / len(ex)
    out['comps'].update(mult=round(avg, 2), v=round(avg * P['eps_fwd'], 2),
                        mult_sin_pltr=round(avg_ex, 2), v_sin_pltr=round(avg_ex * P['eps_fwd'], 2))
    rows = [dict(fecha=d, precio=px, eps=e, pe=round(px / e, 2)) for d, px, e in P['rev_rows']]
    m = sum(r['pe'] for r in rows) / len(rows)
    out['rev'] = dict(filas=rows, pe_prom=round(m, 2), v=round(m * P['eps_ttm'], 2))
    vals = dict(dcf=sc['base']['v'], comps=out['comps']['v'], rev=out['rev']['v'], cons=P['pt'])
    out['metodos'] = vals
    out['promedio_simple'] = round(sum(vals.values()) / 4, 2)
    out['blend'] = round(sum(W[k] * vals[k] for k in W), 2)
    out['gap'] = round((out['blend'] / P['price'] - 1) * 100, 1)
    v2 = dict(vals, comps=out['comps']['v_sin_pltr'])
    out['blend_sin_pltr'] = round(sum(W[k] * v2[k] for k in W), 2)
    lo, hi = -0.3, 0.8
    for _ in range(100):
        mid = (lo + hi) / 2
        v = dcf(P['rev0'], [mid * 100] * 5, b['m'], b['c'], b['wacc'], b['gt'], P['nd'], P['sh'])[0]
        lo, hi = (mid, hi) if v < P['price'] else (lo, mid)
    out['dcf_inverso_g'] = round(mid * 100, 2)
    return out


lin = lambda a, z: [a + (z - a) * i / 4 for i in range(5)]

# ---------------- Edición sep-2026 (2T 2026, precio 4-sep $141.26) ----------------
REPRO_SEP = dict(
    rev0=14732, nd=5014, sh=1034.3, price=141.26,
    esc=dict(
        # Base: reproduce $132.18 / 78.3% y la grilla 5x5 publicada (error total $0.01 en 5 celdas testigo).
        base=dict(g=[19, 16.5, 14, 12, 10], m=lin(38, 42), c=[5] * 5, wacc=.0931, gt=.03),
        # Bear / Bull: margen lineal; crecimiento intermedio sin documentar -> una de varias trayectorias que reproducen.
        bear=dict(g=[12, 10.5, 8.25, 5.25, 5], m=lin(33, 35), c=[4.5] * 5, wacc=.1017, gt=.02),
        bull=dict(g=[24, 19.75, 18, 17.5, 14], m=lin(42, 47), c=[5.5] * 5, wacc=.086, gt=.035),
    ),
    grid_wacc=[8.31, 8.81, 9.31, 9.81, 10.31], grid_g=[2.0, 2.5, 3.0, 3.5, 4.0],
    # sep aplicaba P/E forward NTM de los peers al EPS forward implícito de NOW ($4.53)
    pe=dict(CRM=18.03, WDAY=17.18, SAP=24.06, PLTR=91.59), eps_fwd=141.26 / 31.18,
    rev_rows=[('2025-09-30', 184.06, 1.66), ('2025-12-31', 153.19, 1.67), ('2026-03-31', 104.55, 1.68),
              ('2026-06-30', 99.28, 1.60)],
    eps_ttm=1.60, pt=141.19,
)

# ---------------- Edición 3T 2026 (trimestre cerrado 30-sep-2026; precio cierre 16-nov-2026 $99.37) ----------------
# Fuentes: 8-K y 10-Q del 28-oct-2026; Tesoro 16-nov-2026 (5.12%); stockanalysis.com 17-nov-2026 (beta 0.98, consenso,
# P/E 2027E de peers, modelos/peers_software_3t26.json); Yahoo Finance (cierres).
RF, ERP = 5.12, 5.0
PRICE = 99.37
SH = 1043.01                                 # acciones diluidas promedio del 3T 2026 (misma convención que sep)
DEBT = 5438 + 2086                           # bonos (LongTermDebt XBRL) + papel comercial de corto plazo
CASH = 2393 + 2214 + 2354                    # efectivo + valores negociables corrientes y no corrientes
ND = DEBT - CASH                             # 563
KD_AT = 5.19 * (1 - .28)


def wacc(beta):
    ke = RF + beta * ERP
    e = PRICE * 1038
    return (e * ke + DEBT * KD_AT) / (e + DEBT) / 100, ke


W_BASE, KE_BASE = wacc(0.98)
W_BEAR, _ = wacc(1.15)
W_BULL, _ = wacc(0.82)
REV_TTM = 3568 + 3770 + 3987 + 4106          # 15,431
OCF_TTM = 2238 + 1670 + 587 + 839            # 5,334 -> 34.6%
CAPEX_TTM = 238 + 141 + 114 + 91             # 584 -> 3.8%

NOV = dict(
    rev0=REV_TTM, nd=ND, sh=SH, price=PRICE,
    esc=dict(
        # Mismas trayectorias de crecimiento y margen de OCF que sep; capex re-anclado al real (3.8% TTM, 3% en 9M26,
        # guía de "capex reducido"): 4.0% Base, 3.5% Bear, 4.5% Bull.
        base=dict(g=[19, 16.5, 14, 12, 10], m=lin(38, 42), c=[4.0] * 5, wacc=round(W_BASE, 4), gt=.03),
        bear=dict(g=[12, 10.5, 8.25, 5.25, 5], m=lin(33, 35), c=[3.5] * 5, wacc=round(W_BEAR, 4), gt=.02),
        bull=dict(g=[24, 19.75, 18, 17.5, 14], m=lin(42, 47), c=[4.5] * 5, wacc=round(W_BULL, 4), gt=.035),
    ),
    grid_wacc=[round(W_BASE * 100 + d, 2) for d in (-1, -.5, 0, .5, 1)], grid_g=[2.0, 2.5, 3.0, 3.5, 4.0],
    pe=dict(CRM=13.41, WDAY=14.66, SAP=24.98, PLTR=63.15), eps_fwd=4.80,   # EPS no-GAAP 2027E de consenso
    rev_rows=[('2025-12-31', 153.19, 1.67), ('2026-03-31', 104.55, 1.68), ('2026-06-30', 99.28, 1.60),
              ('2026-09-30', 134.01, 1.39)],                                # EPS GAAP TTM: 0.38+0.45+0.29+0.27
    eps_ttm=1.39, pt=155.82, pt_lo=72, pt_hi=266, pt_med=155,
)

if __name__ == '__main__':
    sep, nov = run(REPRO_SEP), run(NOV)
    print('== Reproducción sep-2026 ==')
    print(json.dumps(sep, indent=1, ensure_ascii=False))
    print('promedio simple publicado $143.75 -> modelo', sep['promedio_simple'], '| ponderado regla vigente', sep['blend'])
    print('\n== Edición 3T 2026 ==')
    print('Ke %.2f%%  WACC base %.2f%% bear %.2f%% bull %.2f%%  deuda neta %d  OCF %.1f%%  capex %.1f%%' % (
        KE_BASE, W_BASE * 100, W_BEAR * 100, W_BULL * 100, ND, OCF_TTM / REV_TTM * 100, CAPEX_TTM / REV_TTM * 100))
    print(json.dumps(nov, indent=1, ensure_ascii=False))
    if '--json' in sys.argv:
        p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resultados.json')
        with open(p, 'w', encoding='utf-8') as fh:
            json.dump(dict(sep=sep, nov=nov, ke=round(KE_BASE, 2), wacc=dict(base=round(W_BASE * 100, 2),
                      bear=round(W_BEAR * 100, 2), bull=round(W_BULL * 100, 2)), nd=ND, rev_ttm=REV_TTM,
                      ocf_ttm=OCF_TTM, capex_ttm=CAPEX_TTM), fh, indent=1, ensure_ascii=False)
