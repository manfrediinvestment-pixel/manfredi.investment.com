"""Mastercard (MA) — modelo de valuación del informe informes/ma.html.

Mismo marco de 5 métodos que Visa (pesos 15/10/25/30/20):
  M1 DCF Volumen/Take Rate (WACC)      M2 Retorno Total de Capital (Ke)
  M3 Comparables 75% V / 25% AXP (P/E forward x EPS de consenso 2027E)
  M4 Reversión (P/E al cierre de año calendario, ventana 3 años, sobre EPS GAAP TTM)
  M5 Consenso (precio objetivo promedio)

Uso:  python valuacion.py [--json]
"""
import json, sys, os

W = dict(m1=.15, m2=.10, m3=.25, m4=.30, m5=.20)


def dcf(rev0, g, m, r, gt, nd, sh):
    rev, pv, f = rev0, 0.0, 0.0
    for t, (gi, mi) in enumerate(zip(g, m), 1):
        rev *= 1 + gi
        f = rev * mi
        pv += f / (1 + r) ** t
    pvtv = f * (1 + gt) / (r - gt) / (1 + r) ** 5
    return (pv + pvtv - nd) / sh, pvtv / (pv + pvtv)


def tcr(rev0, g, m, p, ke, gt, sh):
    rev, pv, d = rev0, 0.0, 0.0
    for t, (gi, mi, pi) in enumerate(zip(g, m, p), 1):
        rev *= 1 + gi
        d = rev * mi * pi
        pv += d / (1 + ke) ** t
    return (pv + d * (1 + gt) / (ke - gt) / (1 + ke) ** 5) / sh


pct = lambda xs: [x / 100 for x in xs]
lin = lambda a, b: [a + (b - a) * i / 4 for i in range(5)]


def run(P):
    out, sc = {}, {}
    for name, s in P['esc'].items():
        v1, tvs = dcf(P['rev0'], pct(s['g']), pct(s['m']), s['wacc'], s['gt'], P['nd'], P['sh'])
        # Convención de MA (desde sep-2026): el M2 de Bear/Bull aplica payout, Ke y g terminal del escenario
        # sobre la trayectoria de FCF del caso BASE (en Visa se usa la FCF del propio escenario).
        fb = P['esc']['base']
        v2 = tcr(P['rev0'], pct(fb['g']), pct(fb['m']), pct(s['p']), s['ke'], s['gt'], P['sh'])
        sc[name] = dict(m1=round(v1, 2), tv_share=round(tvs * 100, 1), m2=round(v2, 2))
    out['escenarios'] = sc
    b = P['esc']['base']
    out['grid'] = {w: [round(dcf(P['rev0'], pct(b['g']), pct(b['m']), w / 100, gg / 100, P['nd'], P['sh'])[0], 2)
                       for gg in P['grid_g']] for w in P['grid_wacc']}
    eps = P['eps_fwd']
    c = {k: round(x * eps, 2) for k, x in P['pe_fwd'].items()}
    m3 = round(.75 * c['V'] + .25 * c['AXP'], 2)
    out['comps'] = dict(c, blend=m3)
    pes = {y: (px / e if e else px) for y, (px, e) in P['rev_hist'].items()}
    out['pe_hist'] = {y: round(v, 2) for y, v in pes.items()}
    def win(ys):
        a = sum(pes[y] for y in ys) / len(ys)
        return round(a, 2), round(a * P['eps_ttm'], 2)
    out['reversion'] = {k: win(ys) for k, ys in P['ventanas'].items()}
    vals = dict(m1=sc['base']['m1'], m2=sc['base']['m2'], m3=m3, m4=out['reversion']['3a'][1], m5=P['pt_avg'])
    out['metodos'] = vals
    out['blend'] = round(sum(W[k] * vals[k] for k in W), 2)
    out['gap'] = round((out['blend'] / P['price'] - 1) * 100, 1)
    out['ev_m1'] = round(.25 * sc['bear']['m1'] + .45 * sc['base']['m1'] + .30 * sc['bull']['m1'], 2)
    lo, hi = 0.0, 0.6
    for _ in range(100):
        mid = (lo + hi) / 2
        v = dcf(P['rev0'], [mid] * 5, pct(b['m']), b['wacc'], b['gt'], P['nd'], P['sh'])[0]
        lo, hi = (mid, hi) if v < P['price'] else (lo, mid)
    out['dcf_inverso_g'] = round(mid * 100, 2)
    return out


# Años calendario: (cierre de diciembre, EPS diluido GAAP). 2021/2022 = múltiplos publicados en sep (41.02x / 34.02x).
HIST = {'2021': (41.02, None), '2022': (34.02, None),
        '2023': (426.51, 11.83), '2024': (526.57, 13.89), '2025': (570.88, 16.52)}

# ---------------- Edición sep-2026 (2T 2026, precio $568.43) ----------------
# Base: crecimiento 11/9.5/9/7/6 reproduce M1 $431.19 y la grilla 5x5 (error total 0.12; 11/10/8/7.5/6 también).
# Bear/Bull: varias trayectorias dan el valor exacto; se eligen de pasos regulares (Bull con margen lineal).
REPRO_SEP = dict(
    rev0=35083, nd=13034, sh=894, price=568.43,
    esc=dict(
        base=dict(g=[11, 9.5, 9, 7, 6], m=lin(45, 47), wacc=.084, gt=.03, ke=.086, p=lin(115, 90)),
        bear=dict(g=[8, 7, 5, 4.5, 3], m=[43, 42.5, 41.5, 40.5, 40], wacc=.091, gt=.025, ke=.094, p=lin(90, 70)),
        bull=dict(g=[14, 12.5, 11, 9.5, 8], m=lin(46, 50), wacc=.077, gt=.035, ke=.078, p=lin(120, 105)),
    ),
    grid_wacc=[7.4, 7.9, 8.4, 8.9, 9.4], grid_g=[2.0, 2.5, 3.0, 3.5, 4.0],
    eps_fwd=23.02, pe_fwd=dict(V=25.98, MA=26.96, AXP=17.41),
    eps_ttm=18.18, rev_hist=HIST,
    ventanas={'3a': ['2023', '2024', '2025'], '4a': ['2022', '2023', '2024', '2025'],
              '5a': ['2021', '2022', '2023', '2024', '2025']},
    pt_avg=666.71,
)

# ---------------- Edición nov-2026 (3T 2026, cierre 30-sep-2026; precio 13-nov $661.19) ----------------
# Fuentes: 8-K y 10-Q del 29-oct-2026; XBRL FY2025; Tesoro 13-nov-2026 (5.15%); stockanalysis 15-nov-2026.
RF, BETA, ERP = 5.15, 0.77, 5.0
KE = RF + BETA * ERP                         # 9.00%
PRICE, SH = 661.19, 876                      # acciones diluidas promedio 3T26
DEBT = 1749 + 22189                          # corto + largo plazo (balance; sin duplicar)
CASH = 10147 + 317                           # efectivo + inversiones; excluye restringido y depósitos de clientes
KD_AT = 4.6 * (1 - .20)
WACC = (PRICE * SH * KE + DEBT * KD_AT) / (PRICE * SH + DEBT)

# TTM a sep-26 = FY2025 + 9M26 - 9M25
TTM = dict(rev=32791 + 27482 - 23985, ni=14968 + 12898 - 10908, eps=round(16.52 + 14.59 - 12.00, 2),
           op=18897 + 16356 - 13987, ocf=17648 + 11859 - 12646,
           capex=(489 + 726) + (667 + 474) - (377 + 548),
           recompras=11727 + 11893 - 8169, dividendos=2756 + 2311 - 2072, da=1143 + 934 - 846)
TTM['fcf'] = TTM['ocf'] - TTM['capex']

NOV = dict(
    rev0=TTM['rev'], nd=DEBT - CASH, sh=SH, price=PRICE,
    esc=dict(
        # Mismas trayectorias de crecimiento y payout; margen de FCF re-anclado al real TTM (42.5% vs 45.5%).
        base=dict(g=[11, 9.5, 9, 7, 6], m=lin(42.5, 44.5), wacc=.088, gt=.03, ke=.090, p=lin(115, 90)),
        bear=dict(g=[8, 7, 5, 4.5, 3], m=[40.5, 40, 39, 38, 37.5], wacc=.095, gt=.025, ke=.098, p=lin(90, 70)),
        bull=dict(g=[14, 12.5, 11, 9.5, 8], m=lin(43.5, 47.5), wacc=.081, gt=.035, ke=.082, p=lin(120, 105)),
    ),
    grid_wacc=[7.8, 8.3, 8.8, 9.3, 9.8], grid_g=[2.0, 2.5, 3.0, 3.5, 4.0],
    eps_fwd=23.16, pe_fwd=dict(V=28.32, MA=29.74, AXP=16.52),
    eps_ttm=TTM['eps'], rev_hist=HIST,
    ventanas=REPRO_SEP['ventanas'],
    pt_avg=720.69,
)

if __name__ == '__main__':
    sep, nov = run(REPRO_SEP), run(NOV)
    import copy
    S2 = copy.deepcopy(REPRO_SEP)   # sep con Rf correcto (5.00%): Ke 8.70, WACC 8.5
    for k, (w, ke) in dict(base=(.085, .087), bear=(.092, .095), bull=(.078, .079)).items():
        S2['esc'][k]['wacc'], S2['esc'][k]['ke'] = w, ke
    sep_rf = run(S2)['blend']
    print('== sep ==', json.dumps(sep, ensure_ascii=False))
    print('sep con Rf 5.00%:', sep_rf)
    print('TTM', TTM, 'fcf margin %.2f' % (TTM['fcf'] / TTM['rev'] * 100))
    print('Ke %.2f WACC %.2f ND %d' % (KE, WACC, NOV['nd']))
    print('== nov ==', json.dumps(nov, ensure_ascii=False, indent=1))
    if '--json' in sys.argv:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resultados.json'), 'w', encoding='utf-8') as fh:
            json.dump(dict(sep=sep, sep_rf_corregido=sep_rf, nov=nov, ttm=TTM, ke=round(KE, 2), wacc=round(WACC, 2),
                           nd=NOV['nd']), fh, indent=1, ensure_ascii=False)
