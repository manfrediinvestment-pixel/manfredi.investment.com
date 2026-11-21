"""Berkshire Hathaway (BRK.B) — modelo SOTP propio del informe `informes/brk.b.html`.

Marco (primer holding del sitio, no DDM ni WACC único):
  Método 1  Suma de las partes (50%)
     1. Cartera neta = acciones cotizadas a mercado − impuesto diferido 21% sobre la
        ganancia no realizada + Occidental/Kraft Heinz/Berkadia a mercado (impuesto sobre
        ganancia vs. valor libro, posición por posición) + caja/T-bills + renta fija
        − deuda de seguros y otros − float completo.
     2. Seguros = (suscripción normalizada + float × letra 3m × (1−21%)) × P/E fwd mediano aseguradoras.
     3. BNSF, BHE, Manufactura/servicios/retail (MSR) = utilidad TTM × P/E fwd de comparables
        (+ Taylor Morrison al costo).
  Método 2  Reversión del P/B propio: mediana 10 años de P/B de cierre × valor libro por acción (30%)
  Método 3  Consenso: precio objetivo promedio (20%)

Uso:  python valuacion.py            → reproduce la edición de sep-2026 (2T26) y corre la de nov-2026 (3T26)
Salida: resultados.json (UTF-8) con todas las cifras que usa el HTML.
"""
import json, os, statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
TAX = 0.21
W = {'sotp': 0.50, 'rev': 0.30, 'cons': 0.20}

# --- Pesos de los subgrupos de MSR: utilidad antes de impuestos 2025 (10-K 2025) ---
MSR_W = {'ind': 6808, 'cons_build': 3971, 'consumo': 1792, 'serv': 4905}

# --- Historial de P/B (Método 2): valor libro/acción B propio y precio de cierre de año ---
PB_HIST = [  # año, VL/acción B, precio BRK.B
    (2016, 114.36, 162.98), (2017, 141.17, 198.22), (2018, 141.67, 204.18), (2019, 174.28, 226.50),
    (2020, 191.35, 231.87), (2021, 228.41, 299.00), (2022, 216.21, 308.90), (2023, 259.58, 356.66),
    (2024, 301.00, 453.28), (2025, 332.55, 502.65)]
PB_BUYBACK_SEP = 1.3080  # P/B ponderado de recompras 2018-1S26 sobre $82.723M (informe sep)
# Recompras 3T26 (10-Q 3T26, Parte II Ítem 2): (acciones A, precio A, acciones B, precio B) por mes
BUY_3T26 = [(2465, 745578.23, 3131323, 496.24), (88, 755245.63, 1548314, 503.99), (1983, 758332.88, 7705322, 506.64)]
BVPS_JUN26, BVPS_SEP26 = 348.26, 761368 / (1418900 * 1500 / 1e6)
BUY3_USD = sum(a * pa + b * pb for a, pa, b, pb in BUY_3T26) / 1e6
BUY3_SH = sum(a * 1500 + b for a, pa, b, pb in BUY_3T26) / 1e6
BUY3_PX = BUY3_USD / BUY3_SH
BUY3_PB = BUY3_PX / ((BVPS_JUN26 + BVPS_SEP26) / 2)
PB_BUYBACK = (PB_BUYBACK_SEP * 82723 + BUY3_PB * BUY3_USD) / (82723 + BUY3_USD)

# Segmentos después de impuestos ($M) — tabla de desagregación del MD&A
SEG = {  # uw, inv, bnsf, bhe, msr, other
    '3T25': (2369, 3181, 1449, 1489, 3616, 1381),
    '4T25': (1561, None, 1347, 691, 3370, None),
    '3T26': (1352, 2734, 1729, 1612, 4042, 1236),
}
TTM_JUN26 = (7378, 11991, 5731, 4185, 14655, 4074)   # informe sep (3T25..2T26)
FY2025 = {'uw': 4481 * 5 - 0, 'bnsf': 5476, 'bhe': 3979, 'msr': 13647}  # uw: ver UW_5Y
UW_5Y = 4481  # promedio 2021-2025 suscripción después de impuestos

# Posiciones principales del 13F que se actualizan a precio de mercado (cusip → ticker)
MAIN9 = {'037833100': 'AAPL', '025816109': 'AXP', '191216100': 'KO', '02079K305': 'GOOGL',
         '02079K107': 'GOOG', '060505104': 'BAC', '166764100': 'CVX', '615369105': 'MCO',
         'H1467J104': 'CB'}
OXY_SH = 264941431
KHC_SH = 325634818


def load(name):
    with open(os.path.join(HERE, 'data', name), encoding='utf-8') as f:
        return json.load(f)


def wavg(mults):
    tot = sum(MSR_W.values())
    return sum(MSR_W[k] * mults[k] for k in MSR_W) / tot


def shares_13f(f13, q):
    out = {}
    for k, v in f13[q].items():
        cus = k.split('|')[2]
        if cus in MAIN9:
            out[MAIN9[cus]] = v[1]
    return out


# ------------------------------------------------------------------------------------------
def edition_sep():
    px = load('precios.json')['cierres']
    f13 = load('13f_2t26_3t26.json')
    sh = shares_13f(f13, 'jun')
    d0, d1 = '2026-06-30', '2026-09-22'
    delta = sum(sh[t] * (px[t][d1] - px[t][d0]) for t in sh) / 1e6
    return dict(
        label='sep-2026 (2T26)', price=503.49, shares_b=2147.5,
        eq_bs=323779, unreal_bs=217258, delta_main=delta,
        oxy_px=px['OXY'][d1], khc_px=px['KHC'][d1], oxy_bv=10727, khc_bv=8760, berkadia=461,
        cash=359230 - 6800, fixed=17034, debt=43302, float_=177500, tbill=4.005,
        unpaid_buyback=0.0,
        uw_ttm=TTM_JUN26[0], bnsf=TTM_JUN26[2], bhe=TTM_JUN26[3], msr=TTM_JUN26[4], tmhc=6800,
        # múltiplos exactos del script de sep (pie de la tabla SOTP: 12.01x, 21.01x, 17.24x, 18.07x)
        m_ins=12.01, m_bnsf=21.01, m_bhe=17.24, m_msr=(271570 - 6800) / 14655,  # MSR despejado del valor publicado
        bear=dict(m_ins=8.1, m_bnsf=20.3, m_bhe=(7.7 + 9.0 + 17.1) / 3,
                  m_msr=wavg({'ind': 18.3, 'cons_build': 11.4, 'consumo': 13.2, 'serv': 7.9})),
        bull=dict(m_ins=12.4, m_bnsf=22.9, m_bhe=18.2,
                  m_msr=wavg({'ind': 27.3, 'cons_build': 17.5, 'consumo': 19.7, 'serv': 27.6})),
        bvps=348.26, consensus=547.67, cons_lo=510.0, cons_hi=604.0,
    )


def edition_nov():
    px = load('precios.json')['cierres']
    f13 = load('13f_2t26_3t26.json')
    cp = load('comparables_2026-11-20.json')['datos']
    fpe = {k: v['forwardPE'] for k, v in cp.items()}
    sh = shares_13f(f13, 'sep')
    d0, d1 = '2026-09-30', '2026-11-20'
    delta = sum(sh[t] * (px[t][d1] - px[t][d0]) for t in sh) / 1e6
    ttm = [TTM_JUN26[i] - SEG['3T25'][i] + SEG['3T26'][i] for i in range(6)]
    shares_b = 1418900 * 1500 / 1e6
    groups = {
        'ins': ['PGR', 'TRV', 'CB', 'ALL'], 'rail': ['UNP', 'CSX'], 'util': ['DUK', 'SO', 'AEP', 'XEL', 'NEE', 'PCG', 'EIX'],
        'ind': ['ITW', 'HON', 'EMR', 'PH', 'MMM'], 'cons_build': ['MAS', 'OC', 'DHI', 'LEN'],
        'consumo': ['THO', 'WGO', 'CLX'], 'serv': ['SYY', 'CASY', 'PAG', 'LAD']}
    med = {g: st.median([fpe[t] for t in ts]) for g, ts in groups.items()}
    mn = {g: min(fpe[t] for t in ts) for g, ts in groups.items()}
    mx = {g: max(fpe[t] for t in ts) for g, ts in groups.items()}
    return dict(
        label='nov-2026 (3T26)', price=px['BRK-B']['2026-11-20'], shares_b=shares_b,
        eq_bs=335515, unreal_bs=227053, delta_main=delta,
        oxy_px=px['OXY'][d1], khc_px=px['KHC'][d1], oxy_bv=11359, khc_bv=8831, berkadia=460,
        # caja + T-bills de seguros y otros neta de compras sin liquidar (MD&A: $352.3B); TMHC ya pagada en julio
        cash=36034 + 336735 - 20489, fixed=17082, debt=45767, float_=178500, tbill=px['^IRX']['2026-11-20'],
        # recompras de septiembre liquidadas en octubre: tesorería adquirida 9M $14.409B vs. caja $13.757B
        unpaid_buyback=(93348 - 78939) - 13757,
        uw_ttm=ttm[0], bnsf=ttm[2], bhe=ttm[3], msr=ttm[4], tmhc=6800, ttm=ttm,
        m_ins=med['ins'], m_bnsf=st.mean([fpe['UNP'], fpe['CSX']]), m_bhe=med['util'], m_msr=wavg(med),
        med=med,
        bear=dict(m_ins=fpe['ALL'], m_bnsf=min(fpe['UNP'], fpe['CSX']),
                  m_bhe=st.mean([fpe['PCG'], fpe['EIX'], fpe['XEL']]), m_msr=wavg(mn)),
        bull=dict(m_ins=fpe['PGR'], m_bnsf=fpe['NSC'], m_bhe=st.median([fpe['DUK'], fpe['SO'], fpe['AEP'], fpe['NEE']]),
                  m_msr=wavg(mx)),
        bvps=761368 / shares_b, consensus=564.67, cons_lo=510.0, cons_hi=628.0,
        fpe=fpe, beta={k: v['beta'] for k, v in cp.items()}, groups=groups,
    )


# ------------------------------------------------------------------------------------------
def sotp(e, port_chg=0.0, mult_chg=0.0, case='base', float_as_equity=False):
    """Devuelve dict con componentes ($M) y por acción. port_chg: cambio de la cartera cotizada y
    participaciones; mult_chg: cambio proporcional de los 4 múltiplos operativos."""
    eq_mkt0 = e['eq_bs'] + e['delta_main']
    unreal0 = e['unreal_bs'] + e['delta_main']
    eq_mkt = eq_mkt0 * (1 + port_chg)
    unreal = unreal0 + eq_mkt0 * port_chg
    dtl = TAX * unreal
    oxy = OXY_SH * e['oxy_px'] / 1e6 * (1 + port_chg)
    khc = KHC_SH * e['khc_px'] / 1e6 * (1 + port_chg)
    eqm = oxy + khc + e['berkadia'] - TAX * (max(0, oxy - e['oxy_bv']) + max(0, khc - e['khc_bv']))
    cash_fixed = e['cash'] + e['fixed'] - e['unpaid_buyback']
    port = eq_mkt - dtl + eqm + cash_fixed - e['debt'] - e['float_']

    sc = e[case] if case in ('bear', 'bull') else {}
    m_ins = sc.get('m_ins', e['m_ins']) * (1 + mult_chg)
    m_bnsf = sc.get('m_bnsf', e['m_bnsf']) * (1 + mult_chg)
    m_bhe = sc.get('m_bhe', e['m_bhe']) * (1 + mult_chg)
    m_msr = sc.get('m_msr', e['m_msr']) * (1 + mult_chg)
    uw = {'base': (UW_5Y + e['uw_ttm']) / 2, 'bear': UW_5Y, 'bull': e['uw_ttm']}[case]
    bnsf_e = FY2025['bnsf'] if case == 'bear' else e['bnsf']
    bhe_e = FY2025['bhe'] if case == 'bear' else e['bhe']
    msr_e = FY2025['msr'] if case == 'bear' else e['msr']
    float_y = e['float_'] * e['tbill'] / 100 * (1 - TAX)
    ins = (uw + float_y) * m_ins
    bnsf = bnsf_e * m_bnsf
    bhe = bhe_e * m_bhe
    msr = msr_e * m_msr + e['tmhc']
    total = port + ins + bnsf + bhe + msr
    if float_as_equity:
        total += e['float_'] - float_y * m_ins
    n = e['shares_b']
    return dict(eq_mkt=eq_mkt, unreal=unreal, dtl=dtl, eqm=eqm, cash_fixed=cash_fixed, port=port,
                uw=uw, float_y=float_y, ins_base=uw + float_y, ins=ins, bnsf=bnsf, bhe=bhe, msr=msr,
                total=total, m_ins=m_ins, m_bnsf=m_bnsf, m_bhe=m_bhe, m_msr=m_msr,
                ps={k: v / n for k, v in dict(port=port, ins=ins, bnsf=bnsf, bhe=bhe, msr=msr, total=total).items()})


def run(e):
    base = sotp(e)
    bear = sotp(e, port_chg=-0.20, case='bear')
    bull = sotp(e, case='bull')
    pbs = sorted(p / b for _, b, p in PB_HIST)
    pb_med = st.median(pbs)
    rev = pb_med * e['bvps']
    blend = W['sotp'] * base['ps']['total'] + W['rev'] * rev + W['cons'] * e['consensus']
    grid = [[sotp(e, port_chg=pc, mult_chg=mc)['ps']['total'] for pc in (-.2, -.1, 0, .1, .2)]
            for mc in (-.2, -.1, 0, .1, .2)]
    # múltiplo operativo que justifica el precio (cartera sin cambio)
    lo, hi = -0.9, 2.0
    for _ in range(100):
        mid = (lo + hi) / 2
        if sotp(e, mult_chg=mid)['ps']['total'] < e['price']:
            lo = mid
        else:
            hi = mid
    return dict(
        label=e['label'], price=e['price'], shares_b=e['shares_b'], bvps=e['bvps'], pb_now=e['price'] / e['bvps'],
        base=base, bear=bear['ps']['total'], bull=bull['ps']['total'],
        expected=0.25 * bear['ps']['total'] + 0.5 * base['ps']['total'] + 0.25 * bull['ps']['total'],
        float_eq=sotp(e, float_as_equity=True)['ps']['total'],
        pb_med=pb_med, pb_3y=st.mean([p / b for y, b, p in PB_HIST if y >= 2023]), rev=rev,
        rev_3y=st.mean([p / b for y, b, p in PB_HIST if y >= 2023]) * e['bvps'], rev_buyback=(PB_BUYBACK_SEP if e['label'].startswith('sep') else PB_BUYBACK) * e['bvps'],
        rev_rows=[(y, b, p, p / b, p / b * e['bvps']) for y, b, p in PB_HIST],
        consensus=e['consensus'], cons_range=(e['cons_lo'], e['cons_hi']),
        blend=blend, simple=(base['ps']['total'] + rev + e['consensus']) / 3,
        updown=blend / e['price'] - 1, grid=grid, mult_to_price=lo,
        scen_mults=dict(base=dict(ins=e['m_ins'], bnsf=e['m_bnsf'], bhe=e['m_bhe'], msr=e['m_msr']),
                        bear=e['bear'], bull=e['bull']),
        delta_main=e['delta_main'],
        pb_buyback=PB_BUYBACK_SEP if e['label'].startswith('sep') else PB_BUYBACK,
    )


def derivados(r):
    """Cifras del texto del informe nov-2026 (3T26)."""
    px = load('precios.json')['cierres']
    f13 = load('13f_2t26_3t26.json')
    sh = shares_13f(f13, 'sep')
    d1 = '2026-11-20'
    pos = {t: sh[t] * px[t][d1] / 1e9 for t in sh}
    pos['GOOGL+GOOG'] = pos.pop('GOOGL') + pos.pop('GOOG')
    pos['OXY (particip.)'] = OXY_SH * px['OXY'][d1] / 1e9
    pos['KHC (particip.)'] = KHC_SH * px['KHC'][d1] / 1e9
    # TTM y trimestres ($M)
    op_q = {'4T24': 14527, '1T25': 9641, '2T25': 11160, '3T25': 13485, '4T25': 10200, '1T26': 11346, '2T26': 12983, '3T26': 12705}
    ni_q = {'4T24': 19694, '1T25': 4603, '2T25': 12370, '3T25': 30796, '4T25': 19199, '1T26': 10106, '2T26': 25667, '3T26': 22112}
    ttm_op = sum(op_q[q] for q in ('4T25', '1T26', '2T26', '3T26'))
    ttm_op_prev = sum(op_q[q] for q in ('4T24', '1T25', '2T25', '3T25'))
    ttm_ni = sum(ni_q[q] for q in ('4T25', '1T26', '2T26', '3T26'))
    eq5 = [698155, 717419, 727181, 747910, 761368]
    avg_eq = sum(eq5) / 5
    n = r['shares_b']
    cash = 36034 + 336735 - 20489
    mcap = r['price'] * n
    # Chequeo cruzado (no entra al blend): las 5 mayores posiciones a fair value de los informes propios
    fv_inf = {'AAPL': 263.56, 'AXP': 332.04, 'KO': 79.03, 'BAC': 53.61, 'GOOGL': 330.28, 'GOOG': 330.28}
    mkt5 = sum(sh[t] * px[t][d1] for t in fv_inf) / 1e6
    fv5 = sum(sh[t] * fv_inf[t] for t in fv_inf) / 1e6
    cross = dict(mkt5=mkt5, fv5=fv5, diff=fv5 - mkt5, diff_after_tax=(fv5 - mkt5) * (1 - TAX),
                 ps=(fv5 - mkt5) * (1 - TAX) / r['shares_b'],
                 por_ticker={t: dict(sh=sh[t], px=px[t][d1], fv=fv_inf[t], gap=fv_inf[t] / px[t][d1] - 1) for t in fv_inf})
    return dict(
        cross=cross,
        pos_nov20_b=pos, op_q=op_q, ni_q=ni_q, ttm_op=ttm_op, ttm_op_prev=ttm_op_prev,
        ttm_op_chg=ttm_op / ttm_op_prev - 1, ttm_ni=ttm_ni, ttm_inv_gains=42249 - 17311 + 9407, ttm_impair=-4495,
        ttm_rev=384687 - 94972 + 105647, op_ps=ttm_op / n, ni_ps=ttm_ni / n, avg_eq=avg_eq,
        roe_op=ttm_op / avg_eq, roe_gaap=ttm_ni / avg_eq, eq_assets=761368 / 1303907, cash=cash,
        cash_eq=cash / 761368, rate100=cash * 0.01 * (1 - TAX), rate100_ps=cash * 0.01 * (1 - TAX) / n,
        rate100_pct=cash * 0.01 * (1 - TAX) / ttm_op, excess=cash - 30000, mcap=mcap, excess_mcap=(cash - 30000) / mcap,
        op_3t_chg=12705 / 13485 - 1, pe_fwd_2026=r['price'] / 23.13, pe_fwd_2027=r['price'] / 22.10,
        # acciones al 28-oct-2026 (portada 10-Q): 480,476 A + 1,403,805,594 B
        sh_oct28=(480476 * 1500 + 1403805594) / 1e6,
    )


def main():
    sep, nov = edition_sep(), edition_nov()
    r_sep, r_nov = run(sep), run(nov)
    # --- chequeo de reproducción de la edición publicada (sep) ---
    pub = dict(port=213.44, ins=64.57, bnsf=56.07, bhe=33.60, msr=126.46, total=494.13)
    for k, v in pub.items():
        got = r_sep['base']['ps'][k]
        assert abs(got - v) < 0.06, (k, got, v)
    assert abs(r_sep['rev'] - 492.67) < 0.05, r_sep['rev']
    assert abs(r_sep['blend'] - 504.40) < 0.05, r_sep['blend']
    assert abs(r_sep['delta_main'] - 11689) < 3, r_sep['delta_main']
    for k, v in (('bear', 384.78), ('bull', 554.62), ('float_eq', 545.37), ('expected', 481.91)):
        print(f'  sep {k}: {r_sep[k]:.2f} (publicado {v})')

    # --- extras de la edición nov ---
    e = nov
    rf = 4.912  # Tesoro 10 años, cierre 20-nov-2026 (^TNX)
    erp = 5.0
    beta = e['beta']
    coe = {}
    for seg, ts, m in (('BNSF (UNP, CSX)', ['UNP', 'CSX'], e['m_bnsf']),
                       ('BHE (utilities)', ['DUK', 'SO', 'AEP', 'XEL', 'NEE'], e['m_bhe']),
                       ('Seguros (PGR, TRV, CB, ALL)', ['PGR', 'TRV', 'CB', 'ALL'], e['m_ins']),
                       ('MSR (industriales)', ['ITW', 'HON', 'EMR', 'PH', 'MMM'], e['m_msr'])):
        b = st.mean([beta[t] for t in ts])
        k = rf + b * erp
        coe[seg] = dict(beta=b, k=k, mult=m, g=k - 100 / m)
    ttm = e['ttm']
    out = dict(sep=r_sep, nov=r_nov, ttm_sep26=dict(zip(['uw', 'inv', 'bnsf', 'bhe', 'msr', 'other'], ttm), total=sum(ttm)),
               med=e['med'], fpe=e['fpe'], beta=beta, coe=coe, rf=rf)
    out['buy3'] = dict(usd=BUY3_USD, sh=BUY3_SH, px=BUY3_PX, pb=BUY3_PB, pb_all=PB_BUYBACK)
    out['derivados'] = derivados(r_nov)
    with open(os.path.join(HERE, 'resultados.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1, default=float)

    for r in (r_sep, r_nov):
        b = r['base']
        print(f"\n== {r['label']}  precio ${r['price']:.2f}  acciones {r['shares_b']:.2f}M  VL/acc ${r['bvps']:.2f} (P/B {r['pb_now']:.3f}x)")
        print(f"  cartera neta ${b['port']:,.0f}M  {b['ps']['port']:.2f} | eq mkt {b['eq_mkt']:,.0f} dtl {b['dtl']:,.0f} eqm {b['eqm']:,.0f} caja+fijo {b['cash_fixed']:,.0f}")
        print(f"  seguros  ({b['uw']:,.0f}+{b['float_y']:,.0f}) x{b['m_ins']:.3f} = {b['ins']:,.0f}  {b['ps']['ins']:.2f}")
        print(f"  BNSF x{b['m_bnsf']:.3f} {b['bnsf']:,.0f} {b['ps']['bnsf']:.2f} | BHE x{b['m_bhe']:.3f} {b['bhe']:,.0f} {b['ps']['bhe']:.2f} | MSR x{b['m_msr']:.3f} {b['msr']:,.0f} {b['ps']['msr']:.2f}")
        print(f"  SOTP ${b['total']:,.0f}M = {b['ps']['total']:.2f}  bear {r['bear']:.2f} bull {r['bull']:.2f} esperado {r['expected']:.2f} float-eq {r['float_eq']:.2f}")
        print(f"  reversión {r['pb_med']:.4f}x → {r['rev']:.2f} (3a {r['rev_3y']:.2f}, recompras {r['rev_buyback']:.2f})  consenso {r['consensus']:.2f}")
        print(f"  BLEND {r['blend']:.2f}  vs precio {r['updown']*100:+.1f}%  simple {r['simple']:.2f}  múltiplos para justificar precio {r['mult_to_price']*100:+.1f}%")
    print('\nTTM sep-26', out['ttm_sep26'])
    print('medianas', {k: round(v, 3) for k, v in e['med'].items()})
    for k, v in coe.items():
        print(f"  {k}: beta {v['beta']:.2f} k {v['k']:.2f}% x{v['mult']:.2f} g {v['g']:.2f}%")


if __name__ == '__main__':
    main()
