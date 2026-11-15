"""Visa (V) — modelo de valuación del informe informes/v.html.

Marco de 5 métodos para redes de pago (pesos 15/10/25/30/20):
  M1 DCF Volumen/Take Rate (flujo a la firma, WACC)
  M2 Retorno Total de Capital (FCF x payout, al costo de equity)
  M3 Comparables (75% MA / 25% AXP, P/E forward sobre EPS de consenso del año fiscal en curso)
  M4 Reversión a la media propia (P/E al cierre fiscal 30-sep, ventana 3 años, sobre EPS GAAP TTM)
  M5 Consenso (precio objetivo promedio)

Uso:  python valuacion.py          -> imprime reproducción de sep-2026 y la edición 4T FY2026
      python valuacion.py --json   -> además escribe resultados.json (UTF-8)

Trayectorias: interpolación año por año EXPLÍCITA (las de sep no estaban documentadas;
ver REPRO_SEP abajo para cuáles reproducen sus cifras).
"""
import json, sys, os

W = dict(m1=.15, m2=.10, m3=.25, m4=.30, m5=.20)


def dcf(rev0, g, m, r, gt, nd, sh):
    rev, pv, f = rev0, 0.0, 0.0
    for t, (gi, mi) in enumerate(zip(g, m), 1):
        rev *= 1 + gi
        f = rev * mi
        pv += f / (1 + r) ** t
    tv = f * (1 + gt) / (r - gt)
    pvtv = tv / (1 + r) ** 5
    return (pv + pvtv - nd) / sh, pvtv / (pv + pvtv)


def tcr(rev0, g, m, p, ke, gt, sh):
    """Retorno total de capital: FCF x payout, descontado al Ke; terminal sobre la última distribución."""
    rev, pv, d = rev0, 0.0, 0.0
    for t, (gi, mi, pi) in enumerate(zip(g, m, p), 1):
        rev *= 1 + gi
        d = rev * mi * pi
        pv += d / (1 + ke) ** t
    return (pv + d * (1 + gt) / (ke - gt) / (1 + ke) ** 5) / sh


def pct(xs):
    return [x / 100 for x in xs]


def blend(v):
    return sum(W[k] * v[k] for k in W)


def run(P):
    out = {}
    sc = {}
    for name, s in P['esc'].items():
        v1, tvs = dcf(P['rev0'], pct(s['g']), pct(s['m']), s['wacc'], s['gt'], P['nd'], P['sh'])
        v2 = tcr(P['rev0'], pct(s['g']), pct(s['m']), pct(s['p']), s['ke'], s['gt'], P['sh'])
        sc[name] = dict(m1=round(v1, 2), tv_share=round(tvs * 100, 1), m2=round(v2, 2))
    out['escenarios'] = sc
    # sensibilidad base
    b = P['esc']['base']
    grid = {}
    for w in P['grid_wacc']:
        grid[w] = [round(dcf(P['rev0'], pct(b['g']), pct(b['m']), w / 100, gg / 100, P['nd'], P['sh'])[0], 2)
                   for gg in P['grid_g']]
    out['grid'] = grid
    # comparables
    eps = P['eps_fwd']
    c = {k: round(x * eps, 2) for k, x in P['pe_fwd'].items()}
    m3 = round(.75 * c['MA'] + .25 * c['AXP'], 2)
    out['comps'] = dict(c, blend=m3)
    # reversión
    pes = {y: px / e for y, (px, e) in P['rev_hist'].items()}
    def win(ys):
        a = sum(pes[y] for y in ys) / len(ys)
        return round(a, 2), round(a * P['eps_ttm'], 2)
    out['pe_hist'] = {y: round(v, 2) for y, v in pes.items()}
    out['reversion'] = {k: win(ys) for k, ys in P['ventanas'].items()}
    m4 = out['reversion']['3a'][1]
    vals = dict(m1=sc['base']['m1'], m2=sc['base']['m2'], m3=m3, m4=m4, m5=P['pt_avg'])
    out['metodos'] = vals
    out['blend'] = round(blend(vals), 2)
    out['gap'] = round((out['blend'] / P['price'] - 1) * 100, 1)
    # valor esperado M1 25/45/30
    out['ev_m1'] = round(.25 * sc['bear']['m1'] + .45 * sc['base']['m1'] + .30 * sc['bull']['m1'], 2)
    # DCF inverso: g constante 5 años que iguala precio (margen/WACC/g base)
    lo, hi = 0.0, 0.5
    for _ in range(100):
        mid = (lo + hi) / 2
        v = dcf(P['rev0'], [mid] * 5, pct(b['m']), b['wacc'], b['gt'], P['nd'], P['sh'])[0]
        lo, hi = (mid, hi) if v < P['price'] else (lo, mid)
    out['dcf_inverso_g'] = round(mid * 100, 2)
    return out


# ---------------- Edición sep-2026 (Q3 FY2026, precio 15-sep $375.62) ----------------
REPRO_SEP = dict(
    rev0=44488, nd=10066, sh=1895, price=375.62,
    esc=dict(
        # Base: reproduce al centavo M1 $268.94 y TODA la grilla 5x5 (error total 0.1).
        base=dict(g=[12, 10, 8, 7, 6], m=[47, 47.5, 48, 48.5, 49], wacc=.085, gt=.03, ke=.087,
                  p=[110, 105, 100, 97.5, 95]),           # M2 $254.95 vs $254.90 publicado (tramo medio sin documentar)
        # Bear/Bull: varias trayectorias dan el valor exacto; éstas son de pasos regulares.
        bear=dict(g=[7, 6, 5, 4, 3], m=[45, 44, 43, 42.5, 42], wacc=.092, gt=.025, ke=.095,
                  p=[100, 93.75, 87.5, 81.25, 75]),
        bull=dict(g=[15, 13, 11, 9, 8], m=[48, 49.5, 50.5, 51.5, 52], wacc=.078, gt=.035, ke=.079,
                  p=[115, 113.25, 111.5, 109.75, 108]),
    ),
    grid_wacc=[7.5, 8.0, 8.5, 9.0, 9.5], grid_g=[2.0, 2.5, 3.0, 3.5, 4.0],
    eps_fwd=14.98, pe_fwd=dict(MA=26.96, V=25.98, AXP=17.41),
    eps_ttm=11.75,
    rev_hist={
        'FY2023': (230.01, 8.28), 'FY2024': (274.95, 9.73), 'FY2025': (341.38, 10.20)},
    ventanas={'3a': ['FY2023', 'FY2024', 'FY2025']},
    pt_avg=419.36,
)

# ---------------- Edición nov-2026 (4T FY2026, cierre 30-sep-2026; precio 13-nov $425.76) ----------------
# Fuentes: 8-K 27-oct-2026 (ex. 99.1) y 10-K 5-nov-2026; Tesoro 13-nov-2026 (10 años 5.15%);
# stockanalysis.com 15-nov-2026 (P/E fwd, beta, consenso, precio objetivo); Yahoo Finance (cierres).
RF, BETA, ERP = 5.15, 0.79, 5.0
KE = RF + BETA * ERP                      # 9.10%
CASH = 12938 + 1145 + 94                  # efectivo + inversiones (corto y largo plazo) = $14,177M; escrow excluido
DEBT = 2716 + 19355                       # porción corriente + largo plazo (balance; sin duplicar) = $22,071M
PRICE = 425.76
SH = 1882                                 # acciones clase A diluidas as-converted, promedio 4T FY26
MKT_E = PRICE * SH
KD_AT = 4.6 * (1 - .179)                  # costo de deuda antes de impuestos ~4.6% x (1 - tasa no-GAAP 17.9%)
WACC = (MKT_E * KE + DEBT * KD_AT) / (MKT_E + DEBT)

NOV = dict(
    rev0=45903, nd=DEBT - CASH, sh=SH, price=PRICE,
    esc=dict(
        # Mismo marco y mismas trayectorias de crecimiento; margen de FCF re-anclado al real FY26 (48.05% vs 47.2% TTM jun).
        base=dict(g=[12, 10, 8, 7, 6], m=[48, 48.5, 49, 49.5, 50], wacc=.09, gt=.03, ke=.091,
                  p=[110, 105, 100, 97.5, 95]),
        bear=dict(g=[7, 6, 5, 4, 3], m=[46, 45, 44, 43.5, 43], wacc=.097, gt=.025, ke=.099,
                  p=[100, 93.75, 87.5, 81.25, 75]),
        bull=dict(g=[15, 13, 11, 9, 8], m=[49, 50.5, 51.5, 52.5, 53], wacc=.083, gt=.035, ke=.084,
                  p=[115, 113.25, 111.5, 109.75, 108]),
    ),
    grid_wacc=[8.0, 8.5, 9.0, 9.5, 10.0], grid_g=[2.0, 2.5, 3.0, 3.5, 4.0],
    eps_fwd=15.03, pe_fwd=dict(MA=29.74, V=28.32, AXP=16.52),
    eps_ttm=12.32,
    rev_hist={
        'FY2022': (177.65, 7.00),   # cierre 30-sep-2022 / EPS FY22 = 25.38x (mismo múltiplo que sep)
        'FY2023': (230.01, 8.28), 'FY2024': (274.95, 9.73), 'FY2025': (341.38, 10.20), 'FY2026': (359.33, 12.32)},
    ventanas={'3a': ['FY2024', 'FY2025', 'FY2026'], '4a': ['FY2023', 'FY2024', 'FY2025', 'FY2026'],
              '5a': ['FY2022', 'FY2023', 'FY2024', 'FY2025', 'FY2026']},
    pt_avg=449.06, pt_lo=330.0, pt_hi=500.0,
)

if __name__ == '__main__':
    sep = run(REPRO_SEP)
    nov = run(NOV)
    print('== Reproducción sep-2026 ==')
    print(json.dumps(sep, indent=1, ensure_ascii=False))
    print('blend publicado $346.90 -> modelo', sep['blend'])
    print('\n== Edición 4T FY2026 ==')
    print('Ke %.2f%%  WACC %.2f%%  deuda neta %d' % (KE, WACC, NOV['nd']))
    print(json.dumps(nov, indent=1, ensure_ascii=False))
    if '--json' in sys.argv:
        p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resultados.json')
        with open(p, 'w', encoding='utf-8') as fh:
            json.dump(dict(sep=sep, nov=nov, ke=round(KE, 2), wacc=round(WACC, 2), nd=NOV['nd']), fh,
                      indent=1, ensure_ascii=False)
