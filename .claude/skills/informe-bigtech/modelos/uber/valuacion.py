"""Uber (UBER) — modelo de valuación del informe informes/uber.html.

Cinco métodos (pesos de la regla vigente de informe-bigtech; el DCF comparte su 15% con el SOTP):
  M1 DCF de flujo de caja (OCF - capex), tres escenarios ............ 7.5%
  M2 SOTP por segmento (EV/Ingresos anualizados del trimestre) ........ 7.5%
  M3 Comparables (P/E 2027E de LYFT / DASH / GRAB) ................... 25%
  M4 Reversión a la media propia (EV/Adjusted EBITDA, 4 cierres trim.) 35%
  M5 Consenso (precio objetivo promedio) ............................. 25%

Uso:  python valuacion.py          -> imprime reproducción de ago-2026 y la edición 3T 2026
      python valuacion.py --json   -> además escribe resultados.json (UTF-8)

Trayectorias: año por año EXPLÍCITAS. Las de ago no estaban documentadas; las de REPRO_AGO son las
que reproducen las cifras publicadas (ver comentarios).
"""
import json, os, sys

W = dict(dcf=.075, sotp=.075, comps=.25, rev=.35, cons=.25)


def dcf(rev0, g, m, c, r, gt, nd, sh):
    """Flujo = ingresos x (margen OCF - capex/ingresos). Devuelve (valor/acción, % EV desde terminal)."""
    rev, pv, f = rev0, 0.0, 0.0
    for t in range(5):
        rev *= 1 + g[t] / 100
        f = rev * (m[t] - c[t]) / 100
        pv += f / (1 + r) ** (t + 1)
    pvtv = f * (1 + gt) / (r - gt) / (1 + r) ** 5
    return (pv + pvtv - nd) / sh, pvtv / (pv + pvtv)


def run(P):
    out = {}
    sc = {}
    for k, s in P['esc'].items():
        v, tv = dcf(P['rev0'], s['g'], s['m'], s['c'], s['wacc'], s['gt'], P['nd'], P['sh'])
        sc[k] = dict(v=round(v, 2), tv=round(tv * 100, 1))
    out['dcf'] = sc
    out['dcf_ev_25_45_30'] = round(.25 * sc['bear']['v'] + .45 * sc['base']['v'] + .30 * sc['bull']['v'], 2)
    b = P['esc']['base']
    out['grid'] = {str(w): [round(dcf(P['rev0'], b['g'], b['m'], b['c'], w / 100, gg / 100, P['nd'], P['sh'])[0], 2)
                            for gg in P['grid_g']] for w in P['grid_wacc']}
    # SOTP
    ev = sum(P['seg_q'][k] * 4 * P['seg_x'][k] for k in P['seg_q'])
    out['sotp'] = dict(ev=round(ev), v=round((ev - P['nd']) / P['sh'], 2),
                       partes={k: round(P['seg_q'][k] * 4 * P['seg_x'][k]) for k in P['seg_q']})
    # comparables
    if 'pe' in P:
        c = {k: round(x * P['eps_fwd'], 2) for k, x in P['pe'].items()}
        avg = sum(P['pe'].values()) / len(P['pe'])
        out['comps'] = dict(por_peer=c, mult_prom=round(avg, 2), v=round(avg * P['eps_fwd'], 2))
        if P.get('comps_sin'):
            o = {k: x for k, x in P['pe'].items() if k != P['comps_sin']}
            out['comps']['sin_' + P['comps_sin']] = round(sum(o.values()) / len(o) * P['eps_fwd'], 2)
    else:  # ago: EV/Ingresos sobre ingreso consenso 2026
        avg = sum(P['evs'].values()) / len(P['evs'])
        out['comps'] = dict(mult_prom=round(avg, 2), v=round((avg * P['rev_fwd'] - P['nd']) / P['sh'], 2))
    if 'evs' in P and 'pe' in P:   # referencia: EV/Ingresos 2027E
        a = sum(P['evs'].values()) / len(P['evs'])
        out['comps']['ref_ev_ventas'] = dict(mult=round(a, 2), v=round((a * P['rev_fwd'] - P['nd']) / P['sh'], 2))
    # reversión EV/EBITDA ajustado
    rows = []
    for d, px, sh, nd, e in P['rev_rows']:
        evd = px * sh + nd
        rows.append(dict(fecha=d, precio=px, ev=round(evd / 1000, 1), ebitda=round(e / 1000, 2), mult=round(evd / e, 2)))
    m = sum(r['mult'] for r in rows) / len(rows)
    out['rev'] = dict(filas=rows, mult_prom=round(m, 2),
                      v=round((m * P['ebitda_ttm'] - P['nd']) / P['sh'], 2))
    out['cons'] = P['pt']
    vals = dict(dcf=sc['base']['v'], sotp=out['sotp']['v'], comps=out['comps']['v'], rev=out['rev']['v'], cons=P['pt'])
    out['metodos'] = vals
    out['promedio_simple'] = round(sum(vals.values()) / 5, 2)
    out['blend'] = round(sum(W[k] * vals[k] for k in W), 2)
    out['gap'] = round((out['blend'] / P['price'] - 1) * 100, 1)
    if P.get('comps_sin'):
        v2 = dict(vals, comps=out['comps']['sin_' + P['comps_sin']])
        out['blend_sin_' + P['comps_sin']] = round(sum(W[k] * v2[k] for k in W), 2)
    # DCF inverso: crecimiento constante 5 años que iguala el precio (márgenes/WACC/g del Base)
    lo, hi = -0.2, 0.6
    for _ in range(100):
        mid = (lo + hi) / 2
        v = dcf(P['rev0'], [mid * 100] * 5, b['m'], b['c'], b['wacc'], b['gt'], P['nd'], P['sh'])[0]
        lo, hi = (mid, hi) if v < P['price'] else (lo, mid)
    out['dcf_inverso_g'] = round(mid * 100, 2)
    return out


CAPEX = [0.6, 0.65, 0.7, 0.75, 0.8]
CAPEX_BULL = [0.6, 0.6375, 0.675, 0.7125, 0.75]

# ---------------- Edición ago-2026 (2T 2026, precio 7-ago $74.96) ----------------
REPRO_AGO = dict(
    rev0=55230, nd=7850, sh=2042.6, price=74.96,
    esc=dict(
        # Base: reproduce M1 $112.77 y la grilla 5x5 publicada (error total < $0.02 en 5 celdas testigo).
        base=dict(g=[13, 12.5, 9, 8.5, 6], m=[19.5, 21, 22.5, 24, 25], c=CAPEX, wacc=.105, gt=.03),
        # Bear: lineal, reproduce $58.10 / 66.2% exacto.
        bear=dict(g=[7, 6, 5, 4, 3], m=[18.8] * 5, c=CAPEX, wacc=.115, gt=.025),
        # Bull: una de varias trayectorias que reproducen $185.95 / 80.3%.
        bull=dict(g=[18, 16, 14, 9, 7], m=[20, 22, 24.5, 28, 29], c=CAPEX_BULL, wacc=.095, gt=.035),
    ),
    grid_wacc=[9.5, 10.0, 10.5, 11.0, 11.5], grid_g=[2.0, 2.5, 3.0, 3.5, 4.0],
    seg_q=dict(Mobility=7363, Delivery=5245, Freight=1583), seg_x=dict(Mobility=3.5, Delivery=3.0, Freight=0.5),
    evs=dict(LYFT=0.85, DASH=5.46, GRAB=3.30), rev_fwd=58000,
    rev_rows=[  # tal como se publicó (EV y EBITDA TTM de ago; ver nota de corrección en NOV)
        ('2025-09-30', 97.97, 2077.8, 2195, 8120), ('2025-12-31', 81.71, 2058.1, 3416, 8780),
        ('2026-03-31', 71.93, 2035.6, 4956, 9390), ('2026-06-30', 72.16, 2042.6, 7850, 10090)],
    ebitda_ttm=10090, pt=101.39,
)

# ---------------- Edición 3T 2026 (trimestre cerrado 30-sep-2026; precio cierre 16-nov-2026 $69.99) ----------------
# Fuentes: 8-K 4-nov-2026 (ex. 99.1) y 10-Q 4-nov-2026; 8-K de 4T25/1T26/2T26 (Adjusted EBITDA trimestral);
# Tesoro 16-nov-2026 (10 años 5.12%); stockanalysis.com 17-nov-2026 (beta 1.31, consenso, P/E 2027E de peers);
# Yahoo Finance (cierres). Peers compartidos: modelos/peers_software_3t26.json.
RF, BETA, ERP = 5.12, 1.31, 5.0
KE = RF + BETA * ERP                                     # 11.67%
PRICE, SH = 69.99, 2041.9                                # acciones en circulación al 30-oct-2026 (portada 10-Q)
DEBT = 15664                                             # LongTermDebt XBRL = total (porción corriente $0 al 30-sep)
CASH, STI = 9558, 510                                    # efectivo + inversiones de corto plazo
NCI = 388 + 916                                          # interés minoritario redimible + no redimible
ND = DEBT - CASH - STI + NCI                             # 6,900 (puente EV -> equity)
KD_AT = 6.0 * (1 - .23)                                  # tasa no-GAAP 23% (8-K)
E = PRICE * SH
WACC = (E * KE + DEBT * KD_AT) / (E + DEBT)              # ~11.0%

REV_TTM = 14366 + 13203 + 14191 + 14766                  # 56,526
OCF_TTM = 2883 + 2351 + 2862 + 2639                      # 10,735 -> 19.0%
CAPEX_TTM = 75 + 65 + 70 + 104                           # 314 -> 0.56%
ADJ = {'4T24': 1842, '1T25': 1868, '2T25': 2119, '3T25': 2256, '4T25': 2487, '1T26': 2481, '2T26': 2819, '3T26': 2963}
TTM = lambda qs: sum(ADJ[q] for q in qs)

NOV = dict(
    rev0=REV_TTM, nd=ND, sh=SH, price=PRICE,
    esc=dict(
        # Mismas trayectorias de crecimiento y margen que ago; Bear re-anclado al OCF TTM real (19.0%).
        base=dict(g=[13, 12.5, 9, 8.5, 6], m=[19.5, 21, 22.5, 24, 25], c=CAPEX, wacc=.11, gt=.03),
        bear=dict(g=[7, 6, 5, 4, 3], m=[19.0] * 5, c=CAPEX, wacc=.12, gt=.025),
        bull=dict(g=[18, 16, 14, 9, 7], m=[20, 22, 24.5, 28, 29], c=CAPEX_BULL, wacc=.10, gt=.035),
    ),
    grid_wacc=[10.0, 10.5, 11.0, 11.5, 12.0], grid_g=[2.0, 2.5, 3.0, 3.5, 4.0],
    seg_q=dict(Mobility=7520, Delivery=5488, Freight=1758), seg_x=dict(Mobility=3.5, Delivery=3.0, Freight=0.5),
    pe=dict(LYFT=8.21, DASH=22.25, GRAB=20.06), eps_fwd=4.41,          # EPS ajustado 2027E de consenso
    evs=dict(LYFT=0.82, DASH=4.07, GRAB=2.28), rev_fwd=66970,           # referencia EV/Ingresos 2027E
    rev_rows=[
        # (fecha, cierre, acciones, deuda neta + NCI de esa fecha, Adjusted EBITDA TTM real)
        ('2025-12-31', 81.71, 2058.1, 10521 - 7105 - 528 + 165 + 877, TTM(['1T25', '2T25', '3T25', '4T25'])),
        ('2026-03-31', 71.93, 2035.6, 10514 - 5558 - 533 + 171 + 890, TTM(['2T25', '3T25', '4T25', '1T26'])),
        ('2026-06-30', 72.16, 2042.6, 12723 - 4870 - 521 + 180 + 903, TTM(['3T25', '4T25', '1T26', '2T26'])),
        ('2026-09-30', 68.51, 2041.9, ND, TTM(['4T25', '1T26', '2T26', '3T26'])),
    ],
    ebitda_ttm=TTM(['4T25', '1T26', '2T26', '3T26']), pt=98.23, pt_lo=70, pt_hi=150, pt_med=99.40,
)

if __name__ == '__main__':
    ago = run(REPRO_AGO)
    nov = run(NOV)
    print('== Reproducción ago-2026 ==')
    print(json.dumps(ago, indent=1, ensure_ascii=False))
    print('promedio simple publicado $94.16 -> modelo', ago['promedio_simple'], '| ponderado con regla vigente', ago['blend'])
    print('\n== Edición 3T 2026 ==')
    print('Ke %.2f%%  WACC %.2f%%  deuda neta+NCI %d  rev TTM %d  OCF %.2f%%  capex %.2f%%' % (
        KE, WACC, ND, REV_TTM, OCF_TTM / REV_TTM * 100, CAPEX_TTM / REV_TTM * 100))
    print(json.dumps(nov, indent=1, ensure_ascii=False))
    if '--json' in sys.argv:
        p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resultados.json')
        with open(p, 'w', encoding='utf-8') as fh:
            json.dump(dict(ago=ago, nov=nov, ke=round(KE, 2), wacc=round(WACC, 2), nd=ND,
                           rev_ttm=REV_TTM, ocf_ttm=OCF_TTM, capex_ttm=CAPEX_TTM, adj_ebitda=ADJ), fh,
                      indent=1, ensure_ascii=False)
