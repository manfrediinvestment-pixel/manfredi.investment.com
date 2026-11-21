"""Intuit (INTU) — modelo de valuación del informe informes/intu.html.

Cuatro métodos, pesos de la regla vigente de informe-bigtech (15/25/35/25):
  M1 DCF (OCF - capex), tres escenarios ........................ 15%
  M2 Comparables (P/E 2027E de ADBE / CRM / NOW) ............... 25%
  M3 Reversión a la media propia (P/E GAAP TTM, ventana limpia) . 35%
  M4 Consenso (precio objetivo promedio, S&P Global) ........... 25%

Edición sep-2026 (4T FY2026, precio 4-sep $332.70): promedio SIMPLE de los cuatro = $420.96.
Edición nov-2026 (1T FY2027, precio cierre 20-nov $270.44): DCF pro forma SIN Mailchimp + caja de la venta.

Uso:  python valuacion.py          -> reproducción de sep-2026 y edición 1T FY2027
      python valuacion.py --json   -> además escribe resultados.json (UTF-8)
"""
import json, os, sys

W = dict(dcf=.15, comps=.25, rev=.35, cons=.25)
lin = lambda a, z: [round(a + (z - a) * i / 4, 6) for i in range(5)]


def dcf(rev0, g, m, c, r, gt, nd, sh, extra=0.0):
    """Valor por acción. extra = activos fuera del flujo (caja de la venta de Mailchimp)."""
    rev, pv, f = rev0, 0.0, 0.0
    for t in range(5):
        rev *= 1 + g[t] / 100
        f = rev * (m[t] - c[t]) / 100
        pv += f / (1 + r) ** (t + 1)
    pvtv = f * (1 + gt) / (r - gt) / (1 + r) ** 5
    return (pv + pvtv + extra - nd) / sh, pvtv / (pv + pvtv), rev0 * (1 + g[0] / 100) * (m[0] - c[0]) / 100


def run(P):
    out, sc = {}, {}
    X = P.get('extra', 0.0)
    for k, s in P['esc'].items():
        v, tv, f1 = dcf(P['rev0'], s['g'], s['m'], s['c'], s['wacc'], s['gt'], P['nd'], P['sh'], X)
        sc[k] = dict(v=round(v, 2), tv=round(tv * 100, 1), fcf1=round(f1, 0), wacc=round(s['wacc'] * 100, 2),
                     g=s['g'], m=s['m'], c=s['c'], gt=s['gt'] * 100)
    out['dcf'] = sc
    out['dcf_ev_25_45_30'] = round(.25 * sc['bear']['v'] + .45 * sc['base']['v'] + .30 * sc['bull']['v'], 2)
    out['dcf_prom_simple'] = round((sc['bear']['v'] + sc['base']['v'] + sc['bull']['v']) / 3, 2)
    b = P['esc']['base']
    out['grid'] = {f'{w:.2f}': [round(dcf(P['rev0'], b['g'], b['m'], b['c'], w / 100, gg / 100, P['nd'], P['sh'], X)[0], 2)
                                for gg in P['grid_g']] for w in P['grid_wacc']}
    # M2 comparables
    pe = P['pe']
    avg = sum(pe.values()) / len(pe)
    out['comps'] = dict(por_peer={k: round(x * P['eps_fwd'], 2) for k, x in pe.items()},
                        mult=round(avg, 2), eps=P['eps_fwd'], v=round(avg * P['eps_fwd'], 2))
    # M3 reversión
    rows = [dict(fecha=d, precio=px, eps=e, pe=round(px / e, 2)) for d, px, e in P['rev_rows']]
    m = sum(r['pe'] for r in rows) / len(rows)
    out['rev'] = dict(filas=rows, pe_prom=round(m, 2), eps_ttm=P['eps_ttm'], v=round(m * P['eps_ttm'], 2))
    vals = dict(dcf=sc['base']['v'], comps=out['comps']['v'], rev=out['rev']['v'], cons=P['pt'])
    out['metodos'] = vals
    out['promedio_simple'] = round(sum(vals.values()) / 4, 2)
    out['blend'] = round(sum(W[k] * vals[k] for k in W), 2)
    out['gap'] = round((out['blend'] / P['price'] - 1) * 100, 1)
    out['gap_simple'] = round((out['promedio_simple'] / P['price'] - 1) * 100, 1)
    # DCF inverso: crecimiento constante años 1-5 que iguala el precio con el margen/WACC/g del Base
    lo, hi = -0.3, 0.8
    for _ in range(100):
        mid = (lo + hi) / 2
        v = dcf(P['rev0'], [mid * 100] * 5, b['m'], b['c'], b['wacc'], b['gt'], P['nd'], P['sh'], X)[0]
        lo, hi = (mid, hi) if v < P['price'] else (lo, mid)
    out['dcf_inverso_g'] = round(mid * 100, 2)
    # margen de OCF constante que iguala el precio con el crecimiento del Base
    lo, hi = 0.0, 60.0
    for _ in range(100):
        mid = (lo + hi) / 2
        v = dcf(P['rev0'], b['g'], [mid] * 5, b['c'], b['wacc'], b['gt'], P['nd'], P['sh'], X)[0]
        lo, hi = (mid, hi) if v < P['price'] else (lo, mid)
    out['dcf_inverso_margen'] = round(mid, 2)
    return out


# ---------------- Edición sep-2026 (4T FY2026, precio 4-sep $332.70) ----------------
# Base: reproduce $478.99 / 71.8% y la grilla 5x5 publicada CELDA POR CELDA (WACC 10.79% = 4.79% + 1.20 x 5%).
# Acciones 271.65 M: despejadas del Base publicado (cap. de mercado ~$91.0B / $332.70 = 273.5 M, coherente).
# Bear / Bull: trayectorias intermedias sin documentar en sep -> estas reproducen con <0.05% de diferencia.
REPRO_SEP = dict(
    rev0=21450, nd=470, sh=271.65191817, price=332.70,
    esc=dict(
        base=dict(g=lin(9.5, 6.0), m=lin(36.5, 39.0), c=[1.0] * 5, wacc=.1079, gt=.03),
        bear=dict(g=[8.5, 7.0, 5.0, 4.0, 3.0], m=[35.5, 34.75, 34.25, 34.0, 34.0], c=[1.0] * 5, wacc=.1179, gt=.0225),
        bull=dict(g=lin(11.0, 9.0), m=lin(38.0, 43.5), c=[0.9] * 5, wacc=.0999, gt=.035),
    ),
    grid_wacc=[9.79, 10.29, 10.79, 11.29, 11.79], grid_g=[2.0, 2.5, 3.0, 3.5, 4.0],
    # sep: P/E forward NTM de ADBE/CRM/NOW/WDAY sobre el EPS implícito $24.18 (base MIXTA, ver nota en informe)
    pe=dict(ADBE=10.3, WDAY=16.3, CRM=17.7, NOW=31.2), eps_fwd=24.18,
    # sep: precios APROXIMADOS (~$335 / ~$340); los cierres reales fueron $388.50 y $316.07
    rev_rows=[('2026-04-30', 335.0, 16.44), ('2026-07-31', 340.0, 16.46)],
    eps_ttm=16.46, pt=411.70,
)

# ---------------- Edición nov-2026 (1T FY2027, precio cierre 20-nov $270.44) ----------------
PRICE = 270.44
RF = 4.92            # Tesoro 10 años, 20-nov-2026 (home.treasury.gov, curva par diaria)
BETA, ERP = 1.20, 5.0
KE = RF + BETA * ERP  # 10.92%

# Datos duros (8-K Ex. 99.01 del 19-nov-2026, 10-Q del 1T FY27, 8-K de segmentos reexpresados)
FY26_REV = 21448
MC_FY26_REV, MC_FY26_SEG_OI = 1272, 604          # Mailchimp FY26 reexpresado (8-K 19-nov, Ex. 99.01)
GUIA_FY27 = (23081, 23365)                          # guía actualizada 19-nov (antes 23,280-23,510)
GUIA_MC_FY27 = (1256, 1266)
Q1_REV, Q1_REV_PY = 4354, 3885
TTM_REV = FY26_REV - Q1_REV_PY + Q1_REV             # 21,917
TTM_OCF = 8838 - 637 + 1062                         # 9,263
TTM_DT = 1279 - 58 + 52                             # impuestos diferidos (add-back no-caja) 1,273
TTM_CAPEX = 221 - 38 + 75                           # 258
CASH_INV, DEBT = 4042 + 1279, 500 + 6422            # al 31-oct-2026
ND = DEBT - CASH_INV                                # 1,601
SH = 264.015                                        # acciones en circulación al 12-nov-2026 (portada del 10-Q)
MC_CASH, MC_STOCK = 3310, 368                       # contraprestación de Bending Spoons
EXTRA = MC_CASH + MC_STOCK                          # 3,678: se suma al EV (impuesto no modelado, ver nota)

REV0 = FY26_REV - MC_FY26_REV                       # 20,176: FY26 pro forma sin Mailchimp
g1_mid = ((sum(GUIA_FY27) - sum(GUIA_MC_FY27)) / 2 / REV0 - 1) * 100   # 8.85%
g1_lo = ((GUIA_FY27[0] - GUIA_MC_FY27[0]) / REV0 - 1) * 100            # 8.17%
g1_hi = ((GUIA_FY27[1] - GUIA_MC_FY27[1]) / REV0 - 1) * 100            # 9.53%

NOV = dict(
    rev0=REV0, nd=ND, sh=SH, price=PRICE, extra=EXTRA,
    esc=dict(
        base=dict(g=lin(round(g1_mid, 2), 6.0), m=lin(36.5, 39.0), c=[1.2] * 5, wacc=KE / 100, gt=.03),
        bear=dict(g=[7.5, 6.5, 5.0, 4.0, 3.0], m=[35.5, 34.75, 34.25, 34.0, 34.0], c=[1.2] * 5,
                  wacc=(KE + 1.0) / 100, gt=.0225),
        bull=dict(g=lin(10.5, 9.0), m=lin(38.0, 43.5), c=[1.1] * 5, wacc=(KE - 0.8) / 100, gt=.035),
    ),
    grid_wacc=[KE - 1, KE - .5, KE, KE + .5, KE + 1], grid_g=[2.0, 2.5, 3.0, 3.5, 4.0],
    # P/E 2027E = precio 20-nov / EPS ajustado de consenso del año fiscal que cubre la mayor parte de 2027.
    # Los tres EXCLUYEN compensación en acciones -> se aplican al EPS FY27 de Intuit en la MISMA base:
    # guía no-GAAP nueva (punto medio $23.00, con SBC) + $5.81 de SBC por acción (8-K 25-ago-2026) = $28.81.
    pe=None, eps_fwd=round((22.88 + 23.12) / 2 + 5.81, 2),
    # Reversión: P/E GAAP TTM (el GAAP SIEMPRE incluyó SBC -> sin mezcla de definiciones) en los tres cierres
    # de trimestre fiscal posteriores al cambio de régimen. Precios: cierres reales Yahoo Finance.
    rev_rows=[('2026-04-30', 388.50, 16.44), ('2026-07-31', 316.07, 16.46), ('2026-10-30', 341.09, 17.46)],
    eps_ttm=17.46, pt=391.05,
)


def peers_pe():
    here = os.path.dirname(os.path.abspath(__file__))
    d = json.load(open(os.path.join(here, '..', 'peers_software_3t26.json'), encoding='utf-8'))
    s = d['cierre_2026_11_20']
    return {k: round(s[k]['precio'] / s[k]['eps_2027e'], 2) for k in ('ADBE', 'CRM', 'NOW')}, s


def extras(r):
    """Chequeos que van al texto del informe."""
    e = {}
    e['ttm'] = dict(rev=TTM_REV, ocf=TTM_OCF, ocf_margin=round(TTM_OCF / TTM_REV * 100, 2),
                    impuestos_diferidos=TTM_DT, ocf_margin_sin_dt=round((TTM_OCF - TTM_DT) / TTM_REV * 100, 2),
                    capex=TTM_CAPEX, capex_pct=round(TTM_CAPEX / TTM_REV * 100, 2), fcf=TTM_OCF - TTM_CAPEX)
    e['guia_sin_mc'] = dict(g1_lo=round(g1_lo, 2), g1_mid=round(g1_mid, 2), g1_hi=round(g1_hi, 2))
    # Mailchimp: lo que se cobra vs. lo que se pierde
    b = NOV['esc']['base']
    mc_fcf = MC_FY26_REV * (b['m'][0] - b['c'][0]) / 100          # FCF que se va con el mismo margen del Base
    mc_ni_seg = MC_FY26_SEG_OI * (1 - .24)                         # resultado de segmento después de impuesto 24%
    r_ = b['wacc']
    # valor de Mailchimp como negocio propio: ingresos -1% anual 5 años, mismo margen, terminal 0%
    rev, pv, f = MC_FY26_REV, 0.0, 0.0
    for t in range(5):
        rev *= 0.99
        f = rev * (b['m'][t] - b['c'][t]) / 100
        pv += f / (1 + r_) ** (t + 1)
    tv = f / r_ / (1 + r_) ** 5
    e['mailchimp'] = dict(fcf_perdido=round(mc_fcf, 0), resultado_segmento_post_imp=round(mc_ni_seg, 0),
                          valor_en_marcha=round(pv + tv, 0), precio=EXTRA,
                          precio_sobre_oi_segmento=round(EXTRA / MC_FY26_SEG_OI, 2),
                          diferencia_por_accion=round((EXTRA - (pv + tv)) / SH, 2),
                          caja_por_accion=round(EXTRA / SH, 2), impuesto_1b_por_accion=round(1000 / SH, 2))
    # DCF consolidado como si Mailchimp siguiera (sin venta) para aislar el efecto
    cons = dict(NOV, rev0=FY26_REV, extra=0.0)
    cons['esc'] = dict(cons['esc'])
    gcons = ((sum(GUIA_FY27) / 2) / FY26_REV - 1) * 100
    cons['esc']['base'] = dict(b, g=lin(round(gcons, 2), 6.0))
    v = dcf(FY26_REV, cons['esc']['base']['g'], b['m'], b['c'], b['wacc'], b['gt'], ND, SH)[0]
    e['base_consolidado_sin_venta'] = dict(g1=round(gcons, 2), v=round(v, 2))
    # sensibilidad: FCF después de compensación en acciones (SBC como costo, guía FY27 $2,020M = 8.7% de ingresos)
    sbc_pct = 2020 / (sum(GUIA_FY27) / 2) * 100
    v2 = dcf(REV0, b['g'], [x - sbc_pct for x in b['m']], b['c'], b['wacc'], b['gt'], ND, SH, EXTRA)[0]
    e['base_fcf_menos_sbc'] = dict(sbc_pct=round(sbc_pct, 2), v=round(v2, 2))
    # reversión: chequeo con la base no-GAAP NUEVA (con SBC), solo hay dos cierres con TTM reexpresado
    nr = [('2026-07-31', 316.07, 18.63), ('2026-10-30', 341.09, round(18.63 - 1.87 + 2.91, 2))]
    pe_n = sum(p / x for _, p, x in nr) / 2
    e['rev_nongaap_nueva'] = dict(filas=[(d, p, x, round(p / x, 2)) for d, p, x in nr], pe=round(pe_n, 2),
                                  v=round(pe_n * nr[-1][2], 2))
    # reversión con los 4 cierres (incluye ene-26, a mitad de la compresión) -> techo del football field
    four = [('2026-01-30', 498.92, 15.37)] + list(NOV['rev_rows'])
    pe4 = sum(p / x for _, p, x in four) / 4
    e['rev_4_cierres'] = dict(pe=round(pe4, 2), v=round(pe4 * NOV['eps_ttm'], 2))
    # reversión sep con precios reales
    pr = (388.50 / 16.44 + 316.07 / 16.46) / 2
    e['rev_sep_precios_reales'] = dict(pe=round(pr, 2), v=round(pr * 16.46, 2))
    # comparables mal hechos (P/E ex-SBC de pares sobre EPS con SBC) para mostrar la diferencia
    e['comps_base_mezclada'] = round(r['comps']['mult'] * 23.00, 2)
    return e


def main():
    sep = run(REPRO_SEP)
    pe, peers = peers_pe()
    NOV['pe'] = pe
    nov = run(NOV)
    nov['extras'] = extras(nov)
    # sep re-ponderado con la regla vigente (15/25/35/25)
    sv = sep['metodos']
    sep_w = round(sum(W[k] * sv[k] for k in W), 2)
    out = dict(sep=sep, sep_ponderado_regla_vigente=sep_w, nov=nov,
               supuestos=dict(rf=RF, beta=BETA, erp=ERP, ke=round(KE, 2), nd=ND, sh=SH, rev0=REV0, extra=EXTRA))
    print('SEP  base %.2f (pub 478.99) bear %.2f (321.78) bull %.2f (693.47) tv %.1f/%.1f/%.1f' % (
        sep['dcf']['base']['v'], sep['dcf']['bear']['v'], sep['dcf']['bull']['v'],
        sep['dcf']['bear']['tv'], sep['dcf']['base']['tv'], sep['dcf']['bull']['tv']))
    print('SEP  comps %.2f (455.73) rev %.2f (337.43) simple %.2f (420.96) | ponderado regla vigente %.2f' % (
        sep['comps']['v'], sep['rev']['v'], sep['promedio_simple'], sep_w))
    print('SEP  grilla', sep['grid'])
    print('NOV  ', json.dumps({k: nov[k] for k in ('metodos', 'blend', 'gap', 'promedio_simple', 'dcf_ev_25_45_30',
                                                   'dcf_inverso_g', 'dcf_inverso_margen')}, ensure_ascii=False))
    for k, s in nov['dcf'].items():
        print('NOV  %-4s %.2f tv %.1f fcf1 %.0f wacc %.2f g %s' % (k, s['v'], s['tv'], s['fcf1'], s['wacc'], s['g']))
    print('NOV  comps', nov['comps'])
    print('NOV  rev', nov['rev'])
    print('NOV  grilla', nov['grid'])
    print('NOV  extras', json.dumps(nov['extras'], ensure_ascii=False))
    if '--json' in sys.argv:
        here = os.path.dirname(os.path.abspath(__file__))
        json.dump(out, open(os.path.join(here, 'resultados.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    return out


if __name__ == '__main__':
    main()
