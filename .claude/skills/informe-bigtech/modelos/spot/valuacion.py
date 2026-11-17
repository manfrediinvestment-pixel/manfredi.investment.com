"""Spotify (SPOT) — modelo de valuación del informe informes/spot.html.

Spotify reporta en EUR (IFRS, 6-K). El modelo corre en EUR y convierte a USD por acción al EUR/USD de la fecha del precio.

Métodos y pesos (regla vigente de informe-bigtech, 15/25/35/25):
  M1 DCF sobre NOPAT (capex y D&A mínimos y similares), tres escenarios ... 15%
  M2 Comparables (P/E 2027E de NFLX / SIRI / WMG) ....................... 25%
  M3 Reversión a la media propia (EV / resultado operativo TTM, 4 cierres)  35%
     (sep-2026 la excluía: el P/E propio estaba contaminado por el valor razonable de los canjeables)
  M4 Consenso (precio objetivo promedio) ................................ 25%

Uso:  python valuacion.py [--json]
"""
import json, os, sys

W = dict(dcf=.15, comps=.25, rev=.35, cons=.25)
lin = lambda a, z: [a + (z - a) * i / 4 for i in range(5)]


def dcf(rev0, g, m, r, gt, cash, sh, fx, tax=.23):
    rev, pv, f = rev0, 0.0, 0.0
    for i in range(5):
        rev *= 1 + g[i] / 100
        f = rev * m[i] / 100 * (1 - tax)
        pv += f / (1 + r) ** (i + 1)
    pvtv = f * (1 + gt) / (r - gt) / (1 + r) ** 5
    return (pv + pvtv + cash) / sh * fx, pvtv / (pv + pvtv)


def run(P):
    out, sc = {}, {}
    for k, s in P['esc'].items():
        v, tv = dcf(P['rev0'], s['g'], s['m'], s['wacc'], s['gt'], P['cash'], P['sh'], P['fx'])
        sc[k] = dict(v=round(v, 2), tv=round(tv * 100, 1))
    out['dcf'] = sc
    out['dcf_ev_25_45_30'] = round(.25 * sc['bear']['v'] + .45 * sc['base']['v'] + .30 * sc['bull']['v'], 2)
    b = P['esc']['base']
    out['grid'] = {f'{w:.1f}': [round(dcf(P['rev0'], b['g'], b['m'], w / 100, gg / 100, P['cash'], P['sh'], P['fx'])[0], 2)
                                for gg in P['grid_g']] for w in P['grid_wacc']}
    pe = P['pe']; avg = sum(pe.values()) / len(pe)
    out['comps'] = dict(eps_usd=round(P['eps_fwd'], 2), por_peer={k: round(x * P['eps_fwd'], 2) for k, x in pe.items()},
                        mult=round(avg, 2), v=round(avg * P['eps_fwd'], 2))
    vals = dict(dcf=sc['base']['v'], comps=out['comps']['v'], cons=P['pt'])
    if P.get('rev_rows'):
        rows = []
        for d, usd, fxd, sh, nc, ebit in P['rev_rows']:
            eur = usd / fxd
            ev = eur * sh - nc
            rows.append(dict(fecha=d, usd=usd, fx=fxd, eur=round(eur, 2), sh=sh, caja_neta=nc, ev=round(ev), ebit=ebit,
                             mult=round(ev / ebit, 2)))
        m = sum(r['mult'] for r in rows) / len(rows)
        v = (m * P['ebit_ttm'] + P['cash']) / P['sh'] * P['fx']
        out['rev'] = dict(filas=rows, mult_prom=round(m, 2), v=round(v, 2))
        vals['rev'] = out['rev']['v']
        out['blend'] = round(sum(W[k] * vals[k] for k in W), 2)
    else:   # sep: promedio simple de 3 (reversión excluida)
        out['blend'] = round(sum(vals.values()) / 3, 2)
    out['metodos'] = vals
    out['promedio_simple'] = round(sum(vals.values()) / len(vals), 2)
    out['gap'] = round((out['blend'] / P['price'] - 1) * 100, 1)
    lo, hi = -0.3, 1.0
    for _ in range(100):
        mid = (lo + hi) / 2
        v = dcf(P['rev0'], [mid * 100] * 5, b['m'], b['wacc'], b['gt'], P['cash'], P['sh'], P['fx'])[0]
        lo, hi = (mid, hi) if v < P['price'] else (lo, mid)
    out['dcf_inverso_g'] = round(mid * 100, 2)
    return out


# ---------------- Edición ago-2026 (2T 2026, precio $479.89; EUR/USD implícito 1.1557) ----------------
REPRO_AGO = dict(
    rev0=17190, cash=8980, sh=205.62, fx=1.1557, price=479.89,
    esc=dict(
        base=dict(g=lin(13.3, 7.5), m=lin(15.5, 20), wacc=.112, gt=.0325),       # $302.93 / 73.7% (lineal)
        bear=dict(g=[11, 8.5, 7.5, 6.5, 5.5], m=lin(14.8, 16.8), wacc=.122, gt=.025),     # $211.85 / 67.0%
        bull=dict(g=[14, 14, 12.5, 11.5, 10.5], m=lin(16, 22), wacc=.102, gt=.0375),      # $418.96 / 79.2%
    ),
    grid_wacc=[10.2, 10.7, 11.2, 11.7, 12.2], grid_g=[2.25, 2.75, 3.25, 3.75, 4.25],
    pe=dict(NFLX=20.48, SIRI=10.07, WMG=13.87), eps_fwd=14.51, pt=607.36,
)

# ---------------- Edición 3T 2026 (trimestre cerrado 30-sep-2026; precio cierre 16-nov-2026 $611.73) ----------------
# Fuentes: 6-K del 22-oct-2026 (Q3 2026 Update y estados intermedios), 6-K del 4-ago-2026 (comparativos 2025),
# 20-F FY2025 (XBRL); Tesoro 16-nov (5.12%); stockanalysis.com 17-nov; Yahoo Finance (SPOT y EUR/USD).
FX = 1.1025
RF, BETA, ERP = 5.12, 1.31, 5.0         # beta: promedio de fuentes de ago (1.58 / 1.04); stockanalysis hoy 1.46
KE = RF + BETA * ERP                    # 11.67% -> WACC Base 11.7% (caja neta, sin deuda financiera)
CASH = 6032 + 3856 - 391 - 62           # efectivo + inversiones CP - pasivos por arrendamiento = 9,435 (EUR M)
SH = 210.741268 - 5.215814              # acciones en circulación al 30-sep-2026 (emitidas - autocartera) = 205.53M
EBIT = {'1T25': 509, '2T25': 406, '3T25': 582, '4T25': 701, '1T26': 715, '2T26': 655, '3T26': 672}
REV_TTM = 4531 + 4533 + 4777 + 4969     # 18,810
EBIT_TTM = 701 + 715 + 655 + 672        # 2,743 (14.6%)
FCF_TTM = 834 + 824 + 797 + 735         # 3,190

NOV = dict(
    rev0=REV_TTM, cash=CASH, sh=SH, fx=FX, price=611.73,
    esc=dict(
        # Año 0 = TTM real. Crecimiento del año 1 anclado en la guía del 4T (EUR 5.2B, ~+15% con ~2.3 pb de tipo de
        # cambio) y en el consenso 2027 (+14.9%); margen final del Base = objetivo 2030 de la compañía (>20%).
        base=dict(g=lin(14, 7.5), m=lin(15.5, 20), wacc=.117, gt=.0325),
        bear=dict(g=[11, 8.5, 7.5, 6.5, 5.5], m=lin(14.8, 16.8), wacc=.127, gt=.025),
        bull=dict(g=[15, 14, 12.5, 11.5, 10.5], m=lin(16, 22), wacc=.107, gt=.0375),
    ),
    grid_wacc=[10.7, 11.2, 11.7, 12.2, 12.7], grid_g=[2.25, 2.75, 3.25, 3.75, 4.25],
    pe=dict(NFLX=16.11, SIRI=9.99, WMG=16.47), eps_fwd=15.24 * FX,       # EPS 2027E consenso EUR 15.24
    rev_rows=[  # (fecha, cierre USD, EUR/USD, acciones M, caja neta EUR M, resultado operativo TTM EUR M)
        ('2025-12-31', 580.71, 1.1747, 205.83, 5258 + 4209 - 1458 - 498, EBIT['1T25'] + EBIT['2T25'] + EBIT['3T25'] + EBIT['4T25']),
        ('2026-03-31', 484.91, 1.1574, 205.70, 8800 - 470, EBIT['2T25'] + EBIT['3T25'] + EBIT['4T25'] + EBIT['1T26']),
        ('2026-06-30', 459.13, 1.1413, 205.70, 9400 - 466, EBIT['3T25'] + EBIT['4T25'] + EBIT['1T26'] + EBIT['2T26']),
        ('2026-09-30', 487.38, 1.1327, SH, CASH, EBIT_TTM),
    ],
    ebit_ttm=EBIT_TTM, pt=637.26, pt_lo=451.36, pt_hi=737.15, pt_med=646.23,
)

if __name__ == '__main__':
    ago, nov = run(REPRO_AGO), run(NOV)
    print('== Reproducción ago-2026 ==')
    print(json.dumps(ago, indent=1, ensure_ascii=False))
    print('promedio simple publicado $375.04 -> modelo', ago['blend'])
    print('\n== Edición 3T 2026 ==  Ke %.2f%%  caja neta %d  margen op TTM %.1f%%' % (KE, CASH, EBIT_TTM / REV_TTM * 100))
    print(json.dumps(nov, indent=1, ensure_ascii=False))
    if '--json' in sys.argv:
        p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resultados.json')
        with open(p, 'w', encoding='utf-8') as fh:
            json.dump(dict(ago=ago, nov=nov, ke=round(KE, 2), cash=CASH, sh=round(SH, 2), rev_ttm=REV_TTM,
                           ebit_ttm=EBIT_TTM, fcf_ttm=FCF_TTM), fh, indent=1, ensure_ascii=False)
