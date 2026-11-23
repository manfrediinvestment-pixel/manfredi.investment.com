# Modelo de valuación PFE (Pfizer Inc.) — todos los números derivados de informes/pfe.html salen de acá.
# Marco: informe-salud, Módulo A (pharma): suma de partes por producto hasta la LOE + rNPV del pipeline (15%),
# comparables P/E forward contra los 13 pares comunes (25%), reversión al P/E propio (35%), consenso (25%).
# Fuentes: 8-K del 3-nov-2026 (comunicado del 3T26, raw/0000078003-26-000125_*), 10-Q del 3T26 (raw/0000078003-26-000127_*),
# 10-K 2025 (raw/0000078003-26-000026_*), comunicado del 4T25 (raw/0000078003-26-000005_*), guía 2026 (raw/0000078003-25-000167_*),
# comunicados históricos (raw/rel/), XBRL companyfacts (raw/companyfacts.json), Orange Book (raw/ob_pfe.json),
# research común de defensivos (.claude/skills/_compartido/defensivos_nov26.json: precio, consenso, tasa común,
# pares, tasas BIO, IRA). Precio de referencia: cierre del 20-nov-2026.
import json, os, copy, statistics as st
from pathlib import Path
import numpy as np
from sotp import run, YEARS, lin

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
TXT = 'PFE_PRICE' not in os.environ
SH = json.load(open(ROOT / '.claude/skills/_compartido/defensivos_nov26.json', encoding='utf-8'))
PH = SH['pharma']
PROD = json.load(open(HERE / 'raw/prod.json', encoding='utf-8'))
OBK = json.load(open(HERE / 'raw/ob_pfe.json', encoding='utf-8'))
M = {}
def put(k, v): M[k] = v; return v

# ======================= 1. Ventas por producto (comunicados, US$ millones) =======================
R3 = PROD['0000078003-26-000125_pfe-9272026xex99.htm.txt']
Q3, N26 = R3['THIRD-QUARTER 2026'], R3['NINE MONTHS 2026']
R4 = PROD['0000078003-26-000005_pfe-12312025xex99.htm.txt']
FY25, Q425 = R4['TWELVE MONTHS 2025'], R4['FOURTH-QUARTER 2025']
def ww(t, n, i=0): return t[n][i]
def n9(n): return N26[n][0], N26[n][1]          # 9M26, 9M25
TOT9, TOT9P = n9('TOTAL REVENUES'); TOTFY25 = ww(FY25, 'TOTAL REVENUES')
assert (TOT9, TOT9P, TOTFY25) == (46067, 45022, 62579)
def ttm(n, fyname=None): return ww(FY25, fyname or n) - N26[n][1] + N26[n][0]
TTM_REV = put('ttm_rev_m', ttm('TOTAL REVENUES'))
put('ttm_rev', TTM_REV / 1000)
P = dict(eliq='Eliquis', ibr='Ibrance', xtd='Xtandi', xelj='Xeljanz', vyn='Vyndaqel family', prev='Prevnar family',
         pad='Padcev', tuk='Tukysa', tiv='Tivdak', adc='Adcetris', nur='Nurtec ODT/Vydura', lor='Lorbrena', abr='Abrysvo',
         org='Orgovyx', elr='Elrexfio', cib='Cibinqo', inl='Inlyta', bos='Bosulif', braf='Braftovi/Mektovi', talz='Talzenna',
         com='Comirnaty', pax='Paxlovid', onb='Oncology biosimilars')
PT = {k: ttm(v) for k, v in P.items()}
put('prod_ttm', {k: v / 1000 for k, v in PT.items()})
GROUPS = dict(seagen=['pad', 'tuk', 'tiv'], launch=['nur', 'lor', 'abr', 'org', 'elr', 'cib'],
              loeg=['inl', 'bos', 'braf', 'adc', 'talz'], covid=['com', 'pax'])
put('g_ttm', {g: sum(PT[k] for k in ks) / 1000 for g, ks in GROUPS.items()})
# Participación de EE.UU. (nueve meses de 2026, tabla del comunicado: mundial, EE.UU., internacional)
def us9(n): return N26[n][2] / N26[n][0]
US = put('us_share', {k: us9(P[k]) for k in ('eliq', 'ibr', 'xelj', 'vyn', 'prev')})
put('us_share_tot', N26['TOTAL REVENUES'][2] / TOT9 * 100)
# 4T26: nivel del 3T26 escalado al 4T implícito en la guía; COVID con su estacionalidad (4T25 x caída interanual del 3T)
G_REV_LO, G_REV_HI = put('g_rev_lo', 62.0), put('g_rev_hi', 64.0)
G_REV_MID = put('g_rev_mid', (G_REV_LO + G_REV_HI) / 2)
put('g_rev_lo_prev', 60.5); put('g_rev_hi_prev', 62.5)
Q4_IMPL = put('q4_impl', G_REV_MID * 1000 - TOT9)
cov_q3 = Q3['Comirnaty'][0] + Q3['Paxlovid'][0]; cov_q3p = Q3['Comirnaty'][1] + Q3['Paxlovid'][1]
COV_Q4 = put('cov_q4', (Q425['Comirnaty'][0] + Q425['Paxlovid'][0]) * cov_q3 / cov_q3p)
SC = put('q4_scale', (Q4_IMPL - COV_Q4) / (Q3['TOTAL REVENUES'][0] - cov_q3))
def q4(k):
    n = P[k]
    if k in ('com', 'pax'): return Q425[n][0] * cov_q3 / cov_q3p
    return Q3[n][0] * SC
Y26 = {k: (N26[P[k]][0] + q4(k)) / 1000 for k in P}     # 2026 calendario estimado, US$ miles de millones
put('y26', Y26)
Y26_TOT = G_REV_MID
Y26_REST = put('y26_rest', Y26_TOT - sum(Y26.values()) + Y26['onb'])   # resto incluye biosimilares oncológicos
REST_TTM = put('rest_ttm', TTM_REV / 1000 - sum(PT[k] for k in P if k != 'onb') / 1000)
# Historia de ingresos y COVID (comunicados del 4T de cada año; cada año tomado de la columna "año anterior" del comunicado
# siguiente cuando fue reexpresado)
def fy(f, y, n): return PROD[f][f'TWELVE MONTHS {y}'][n]
HIST = {
    2020: (41651, 154, 0),
    2021: (fy('rel_2022-02-08.txt', 2021, 'TOTAL REVENUES')[0], fy('rel_2022-02-08.txt', 2021, 'Comirnaty direct sales and alliance revenues')[0], fy('rel_2022-02-08.txt', 2021, 'Paxlovid')[0]),
    2022: (fy('rel_2023-01-31.txt', 2022, 'TOTAL REVENUES')[0], fy('rel_2023-01-31.txt', 2022, 'Comirnaty direct sales and alliance revenues')[0], fy('rel_2023-01-31.txt', 2022, 'Paxlovid')[0]),
    2023: (fy('rel_2025-02-04.txt', 2024, 'TOTAL REVENUES')[1], fy('rel_2025-02-04.txt', 2024, 'Comirnaty')[1], fy('rel_2025-02-04.txt', 2024, 'Paxlovid')[1]),
    2024: (fy('rel_2025-02-04.txt', 2024, 'TOTAL REVENUES')[0], fy('rel_2025-02-04.txt', 2024, 'Comirnaty')[0], fy('rel_2025-02-04.txt', 2024, 'Paxlovid')[0]),
    2025: (TOTFY25, ww(FY25, 'Comirnaty'), ww(FY25, 'Paxlovid')),
}
assert HIST[2021][0] == 81288 and HIST[2022][0] == 100330 and HIST[2023][0] == 59553
put('hist_years', [str(y) for y in HIST] + ['TTM'])
put('hist_cov', [round((c + p) / 1000, 2) for t, c, p in HIST.values()] + [round((PT['com'] + PT['pax']) / 1000, 2)])
put('hist_xcov', [round((t - c - p) / 1000, 2) for t, c, p in HIST.values()] + [round((TTM_REV - PT['com'] - PT['pax']) / 1000, 2)])
put('hist_tot', [round(t / 1000, 2) for t, c, p in HIST.values()] + [round(TTM_REV / 1000, 2)])
put('cov_peak', (HIST[2022][1] + HIST[2022][2]) / 1000); put('cov_ttm', (PT['com'] + PT['pax']) / 1000)
put('cov_drop_pct', (1 - M['cov_ttm'] / M['cov_peak']) * 100)
put('xcov_2022', M['hist_xcov'][2]); put('xcov_ttm', M['hist_xcov'][-1]); put('xcov_2020', M['hist_xcov'][0])
put('xcov_g_20_ttm', (M['xcov_ttm'] / M['xcov_2020'] - 1) * 100)
put('rev_peak', HIST[2022][0] / 1000); put('cov_share_2022', (HIST[2022][1] + HIST[2022][2]) / HIST[2022][0] * 100)
put('cov_share_ttm', M['cov_ttm'] / M['ttm_rev'] * 100)

# ======================= 2. Trimestre y TTM (comunicado y 10-Q, US$ millones) =======================
put('rev3', 16583); put('rev3_ly', 16654); put('rev3_g', (16583 / 16654 - 1) * 100)
put('rev3_xcov_g_op', 7); put('launch_g_op', 32)                         # comunicado: +7% operacional sin COVID; +32% lanzados y adquiridos
put('cogs3', 4028); put('cogs3_ly', 4172); put('sia3', 3279); put('sia3_ly', 3186); put('rd3', 3016); put('rd3_ly', 2546)
put('iprd3', 669); put('iprd3_ly', 1390); put('amort3', 1128); put('restr3', 791)
put('ni3', 3242); put('ni3_ly', 3541); put('eps3', 0.56); put('eps3_ly', 0.62); put('epsa3', 0.87); put('epsa3_ly', 0.87)
for k in ('cogs3', 'sia3', 'rd3', 'ni3'): put(k + '_g', (M[k] / M[k + '_ly'] - 1) * 100)
put('gm3', (1 - 4028 / 16583) * 100); put('gm3_ly', (1 - 4172 / 16654) * 100)
put('gm3_adj', (1 - 3843 / 16583) * 100); put('rd3_pct', 3016 / 16583 * 100)
put('eliq3_g', (Q3['Eliquis'][0] / Q3['Eliquis'][1] - 1) * 100); put('eliq3_us_g', (Q3['Eliquis'][2] / Q3['Eliquis'][3] - 1) * 100)
put('pad3_g', (Q3['Padcev'][0] / Q3['Padcev'][1] - 1) * 100); put('vyn3_g', (Q3['Vyndaqel family'][0] / Q3['Vyndaqel family'][1] - 1) * 100)
put('pax3_g', (Q3['Paxlovid'][0] / Q3['Paxlovid'][1] - 1) * 100); put('com3_g', (Q3['Comirnaty'][0] / Q3['Comirnaty'][1] - 1) * 100)
put('prev3_g', (Q3['Prevnar family'][0] / Q3['Prevnar family'][1] - 1) * 100); put('xelj3_us_g', (Q3['Xeljanz'][2] / Q3['Xeljanz'][3] - 1) * 100)
put('bos3_g', (Q3['Bosulif'][0] / Q3['Bosulif'][1] - 1) * 100); put('ibr3_ous_g', (Q3['Ibrance'][4] / Q3['Ibrance'][5] - 1) * 100)
put('nur3_g', (Q3['Nurtec ODT/Vydura'][0] / Q3['Nurtec ODT/Vydura'][1] - 1) * 100); put('lor3_g', (Q3['Lorbrena'][0] / Q3['Lorbrena'][1] - 1) * 100)
put('eliq3', Q3['Eliquis'][0]); put('pad3', Q3['Padcev'][0]); put('vyn3', Q3['Vyndaqel family'][0]); put('pax3', Q3['Paxlovid'][0]); put('com3', Q3['Comirnaty'][0])
put('prev3', Q3['Prevnar family'][0])
# Guía 2026 (comunicado del 3-nov-2026)
put('g_eps_lo', 2.95); put('g_eps_hi', 3.05); put('g_eps_lo_prev', 2.80); put('g_eps_hi_prev', 3.00); put('g_eps_dec_lo', 2.80); put('g_eps_dec_hi', 3.00)
put('g_rd_lo', 10.8); put('g_rd_hi', 11.8); put('g_sia_lo', 12.5); put('g_sia_hi', 13.5); put('g_tax', 15.0); put('innovent_eps', 0.10)
put('g_rev_dec_lo', 59.5); put('g_rev_dec_hi', 62.5); put('loe_2026_hit', 1.1); put('cov_2026_g', 5.0)
# Estado de resultados TTM = 2025 (10-K / comunicado) − 9M25 + 9M26 (comunicado del 3T26)
FYG = dict(rev=62579, cogs=16067, sia=13794, rd=10437, iprd=1613, amort=4874, ni=7771, eps=1.36, ocf=11704, capex=2629, div=9771, da=6592)
N25G = dict(rev=45022, cogs=10795, sia=9632, rd=7231, iprd=1401, amort=3644, ni=9419, eps=1.65, ocf=6356, capex=1784, div=7326, da=4905)
N26G = dict(rev=46067, cogs=11668, sia=9651, rd=8315, iprd=822, amort=3497, ni=5681, eps=0.99, ocf=8825, capex=1542, div=7347, da=4812)
TTM = {k: FYG[k] - N25G[k] + N26G[k] for k in FYG}
assert TTM['rev'] == TTM_REV
TTM['eps'] = round(TTM['eps'], 2); put('ttm', TTM)
put('ttm_gm', (1 - TTM['cogs'] / TTM['rev']) * 100); put('ttm_rd_pct', TTM['rd'] / TTM['rev'] * 100)
put('ttm_sia_pct', TTM['sia'] / TTM['rev'] * 100)
FCF = put('ttm_fcf', TTM['ocf'] - TTM['capex']); put('ttm_ocfm', TTM['ocf'] / TTM['rev'] * 100); put('ttm_fcfm', FCF / TTM['rev'] * 100)
put('ttm_capex_pct', TTM['capex'] / TTM['rev'] * 100); put('ocf9m_pct', N26G['ocf'] / N26G['rev'] * 100)
# Ajustado (non-GAAP) TTM
FYA = dict(cogs=15141, sia=13642, rd=10212, iprd=1613, inc=18406); N25A = dict(cogs=10075, sia=9562, rd=7096, iprd=1401, inc=14620)
N26A = dict(cogs=10905, sia=9481, rd=8107, iprd=822, inc=13715)
TA = {k: FYA[k] - N25A[k] + N26A[k] for k in FYA}; put('ttm_adj', TA)
EPSQ = put('epsa_q', {'1T24': 0.82, '2T24': 0.60, '3T24': 1.06, '4T24': 0.63, '1T25': 0.92, '2T25': 0.78, '3T25': 0.87,
                      '4T25': 0.66, '1T26': 0.75, '2T26': 0.77, '3T26': 0.87})
assert abs(EPSQ['1T26'] + EPSQ['2T26'] + EPSQ['3T26'] - 2.39) < 1e-9
EPS_TTM = put('ttm_epsa', round(sum(list(EPSQ.values())[-4:]), 2))
put('ttm_eps', TTM['eps'])
put('ttm_ebit_adj', TTM_REV - TA['cogs'] - TA['sia'] - TA['rd'] - TA['iprd'])
put('ttm_opm_adj', M['ttm_ebit_adj'] / TTM_REV * 100)
DEP = put('ttm_dep', TTM['da'] - TTM['amort'])
EBITDA = put('ebitda', (M['ttm_ebit_adj'] + DEP) / 1000)
# Puente GAAP -> ajustado (TTM, US$ millones, antes de impuestos salvo la línea de impuestos)
BR_FY = dict(amort=4874, acq=1285, disc=-25, restr=1554, imp=4940, eq=67, act=-320, oth=1223, tax=-2962)
BR_9M25 = dict(amort=3644, acq=814, disc=-25, restr=1050, imp=577, eq=94, act=-57, oth=914, tax=-1810)
BR_9M26 = dict(amort=3497, acq=1537, disc=-16, restr=1611, imp=4325, eq=121, act=-12, oth=-826, tax=-2203)
BR = {k: BR_FY[k] - BR_9M25[k] + BR_9M26[k] for k in BR_FY}
assert abs(TTM['ni'] + sum(BR.values()) - TA['inc']) <= 3, (TTM['ni'] + sum(BR.values()), TA['inc'])
put('bridge', BR); put('bridge_gap', TA['inc'] - TTM['ni'] - sum(BR.values()))
put('bridge_amort_ps', BR['amort'] / 5739)

# ======================= 3. Balance, deuda y dividendo (10-Q 3T26, 10-K 2025) =======================
BS = put('bs', {'s26': dict(cash=1824, sti=12448, std=2674, ltd=59997, gw=71464, ia=45956, eq=89001, ta=204544, inv=10022),
                'd25': dict(cash=1142, sti=12454, std=3154, ltd=61641, gw=71264, ia=53731, eq=86476, ta=208160, inv=10654),
                'd24': dict(cash=1043, sti=19434, std=6946, ltd=57405, gw=68527, ia=55411, eq=88203, ta=213396, inv=10851)})
for b in BS.values(): b['debt'] = b['std'] + b['ltd']; b['nd'] = b['debt'] - b['cash'] - b['sti']
DEBT = put('debt', BS['s26']['debt'] / 1000); ND = put('net_debt', BS['s26']['nd'] / 1000)
put('nd_lev', ND / EBITDA); put('nd_chg_9m', ND - BS['d25']['nd'] / 1000)
MAT = put('maturities', {'2027': 2.081 + 0.5, '2028': 5.660, '2029': 2.631, '2030': 6.250, '2031-35': 10.424})   # 10-K 2025, nota 7D (principal)
put('mat_27_30', sum(MAT[k] for k in ('2027', '2028', '2029', '2030')))
put('seagen_paid', 43.4); put('seagen_cons', 44.2); put('metsera_fv', 8.0); put('metsera_cvr_fv', 0.632); put('metsera_ps', 65.60)
put('metsera_cvr_ps', 20.65); put('metsera_cvr_max', 2.3); put('metsera_iprd', 7.9)
# Capacidad de compra: deuda adicional hasta 3.0x EBITDA ajustado (estimación propia, nivel de calificación A según el rango de pares)
put('firepower', 3.0 * EBITDA - ND)
DPS = put('dps', 1.72); put('div_q', 0.43)
put('dps_hist', [1.22, 1.30, 1.38, 1.46, 1.53, 1.57, 1.61, 1.65, 1.69, 1.72])     # XBRL CommonStockDividendsPerShareDeclared 2016-2025
put('dps_cagr', ((1.72 / 1.22) ** (1 / 9) - 1) * 100)
put('div_cover_fcf', FCF / TTM['div']); put('payout_fcf', TTM['div'] / FCF * 100)
put('payout_adj', DPS / EPS_TTM * 100); put('payout_gaap', DPS / TTM['eps'] * 100)
put('fcf_ps', FCF / 5739)
put('shares_dil', 5.74)        # guía 2026, miles de millones de acciones diluidas
put('shares_out', 5.700)       # acciones básicas promedio 3T26 (comunicado)
put('dec25_payable', 2445)

# ======================= 4. Mercado, consenso y tasa común (research común del 20-nov) =======================
PRICE = put('price', float(os.environ.get('PFE_PRICE', SH['pfe_precio']['cierre_20nov'])))
CO = SH['consenso_tres']['tickers']['PFE']
C26, C27 = put('c26', CO['eps_ajustado_fy_actual']), put('c27', CO['eps_ajustado_fy_siguiente'])
put('rev_c26', CO['ventas_fy_actual'] / 1e9); put('rev_c27', CO['ventas_fy_siguiente'] / 1e9)
put('c27_g', (C27 / C26 - 1) * 100); put('rev_c27_g', (M['rev_c27'] / M['rev_c26'] - 1) * 100)
put('pe_27', PRICE / C27); put('pe_ttm_adj', PRICE / EPS_TTM); put('pe_ttm_gaap', PRICE / TTM['eps'])
put('div_yield', DPS / PRICE * 100); put('tsy', SH['mercado']['treasury_10y']['valor_pct'])
put('yield_spread', M['div_yield'] - M['tsy'])
put('hi52', SH['pfe_precio']['max_52s']); put('lo52', SH['pfe_precio']['min_52s'])
TD = PH['tasa_descuento_comun']
WACC = put('wacc', TD['wacc_pct']); put('wacc_bear', TD['wacc_bear_pct']); put('wacc_bull', TD['wacc_bull_pct'])
KE = put('ke', TD['ke_pct']); put('rf', TD['rf_pct']); put('beta_blume', TD['beta_blume']); put('beta_raw_peers', TD['beta_media_cruda_pares'])
put('kd', TD['kd_pre_impuestos_pct']); put('kd_at', TD['kd_pct']); put('wd_peers', TD['d_sobre_v_mediana_pares'] * 100); put('erp', TD['erp_pct'])
# WACC propia de referencia (beta propia de 5 años con Blume y estructura de capital propia al 20-nov)
BETA_OWN = put('beta_own', SH['pfe_precio']['multiplos']['beta_5y'])
KE_OWN = M['rf'] + (0.67 * BETA_OWN + 0.33) * M['erp']
WD_OWN = put('wd_own', DEBT / (DEBT + PRICE * M['shares_dil']) * 100)
put('wacc_own', (1 - WD_OWN / 100) * KE_OWN + WD_OWN / 100 * M['kd_at'])

# ======================= 5. Método 1 — suma de partes por producto + rNPV =======================
TAX = put('tax', 15.0)
CM0 = put('cm0', (TTM['ocf'] / TTM_REV + TTM['rd'] / TTM_REV * (1 - TAX / 100)) * 100)   # OCF + I+D después de impuestos, TTM
CX0, RD0 = M['ttm_capex_pct'] / 100, M['ttm_rd_pct'] / 100
put('cm30', 39.0); put('cm30_bear', 36.0); put('cm30_bull', 41.0)
put('rd30', 19.0); put('rd30_bear', 20.0); put('rd30_bull', 18.0)
put('cost_prog_total', 6.7); put('cost_prog_2025', 5.1); put('cost_prog_add', 1.0); put('mfg_prog_total', 3.0); put('mfg_prog_26', 1.3)
put('metsera_syn', 0.6)
put('cost_left', (M['cost_prog_total'] - M['cost_prog_2025'] - 0.6) + (M['mfg_prog_total'] - M['mfg_prog_26']))
# Curvas de erosión (caída año 1, caída acumulada año 2, cola anual), ancladas en análogos de la propia Pfizer (comunicados):
#  - Lipitor EE.UU. (LOE 30-nov-2011): 4T12 $61M vs 4T11 $816M (−93%); Lyrica EE.UU. (LOE jul-2019): 4T19 $88M vs 4T18 $951M (−91%)
#  - Lipitor internacional: 2013 $1,883M vs 2012 $3,016M (−38%)
#  - Humira (AbbVie, biológico): −32% mundial en 2023 (primer año) y −39.9% en EE.UU. en el 1T24 interanual (prensa)
def relv(f, tab, n): return PROD[f][tab][n] if f in PROD else None
ANALOG = put('analog', dict(lip_us_q4_12=61, lip_us_q4_11=816, lyr_us_q4_19=88, lyr_us_q4_18=951, lip_int_13=1883, lip_int_12=3016,
                             lyr_us_19=2012, lyr_us_18=3594, hum_y1=32.0, hum_q1_24_us=39.9))
put('lip_drop', (1 - 61 / 816) * 100); put('lyr_drop', (1 - 88 / 951) * 100); put('lip_int_drop', (1 - 1883 / 3016) * 100)
CUR = put('curves', dict(us_sm=(0.80, 0.92, 0.10), ex_sm=(0.35, 0.60, 0.15), bio=(0.32, 0.60, 0.15), vac=(0.20, 0.40, 0.15)))
# Fechas de LOE (10-K 2025 "Patents and Other Intellectual Property Rights" + Orange Book + acuerdos de litigio del 10-Q)
OBP = OBK['productos']
LOE = put('loe', dict(
    eliq_us=2028.25,          # acuerdos: genéricos el 1-abr-2028 (10-K, nota 5); compuesto nov-2026 / formulación 2031 (Orange Book)
    ibr_us=2027.17,           # patente de sustancia 5-mar-2027 (Orange Book; 10-K: 2027)
    ibr_ex=2028.0,            # Europa / Japón 2028 (10-K)
    xtd_us=2027.62,           # patente de sustancia 13-ago-2027 (Orange Book)
    xelj_us=2026.45,          # compuesto dic-2025 + exclusividad pediátrica 8-jun-2026 (Orange Book)
    xelj_ex=2028.0,           # Europa 2028 (10-K)
    vyn_us=2031.42,           # acuerdos: genéricos de Vyndamax el 1-jun-2031 (10-Q, nota 16A1), sujeto al juicio con Apotex
    vyn_ex=2027.0,            # Europa 2026 (10-K) y Japón 2026/2029: se toma ene-2027 como fecha promedio fuera de EE.UU.
    prev=2035.0,              # Prevnar 20, EE.UU. 2035 (10-K)
    seagen=2033.5,            # Padcev EE.UU. 2033 (10-K); Tukysa 2034, Tivdak 2035
    launch=2034.0))           # Nurtec 2034, Lorbrena 2033, Abrysvo 2036, Cibinqo 2036, Elrexfio 2036 (10-K): promedio
assert OBP['ELIQUIS']['sustancia'] == ['2026-11-21'] and OBP['IBRANCE']['sustancia'][0] == '2027-03-05'
assert OBP['XTANDI']['sustancia'] == ['2027-08-13'] and OBP['VYNDAMAX']['ultima'] == '2035-08-31'
put('ob_date', OBK['meta']['fecha_archivo']); put('ob_eliq_form', OBP['ELIQUIS']['producto_ultima'])
IRA = {r['farmaco']: r for r in PH['ira_medicare']['farmacos']}
put('ira_eliq', IRA['Eliquis']['descuento_pct']); put('ira_ibr', IRA['Ibrance']['descuento_pct']); put('ira_xtd', IRA['Xtandi']['descuento_pct'])
put('ira_eliq_spend', IRA['Eliquis']['gasto_medicare_usd'] / 1e9); put('ira_xelj_spend', IRA['Xeljanz; Xeljanz XR']['gasto_medicare_usd'] / 1e9)
put('vyn_ira_cut', 20.0)       # supuesto propio: Vyndamax elegible para la ronda 2029 (aprobado may-2019); efecto neto sobre EE.UU.
BIO = PH['exito_clinico']['probabilidad_acumulada_hasta_aprobacion']
def pos(area, phase):  # phase: 1, 2, 3 o 'pres'
    return BIO[area][{1: 0, 2: 1, 3: 2, 'pres': 3}[phase]] / 100
# Pipeline: fase y área (tasa BIO, Figura 5b), pico de ventas (US$ miles de millones) y su fuente
PIPE0 = [
    dict(key='bero', name='Berobenatide (MET-097i, GLP-1 mensual)', area='metabolica', phase=3, peak=3.0, launch=2029, loe=2041.0, curve='bio',
         src='Leerink (D. Risinger, sep-2025): más de $5B de pico combinado para la cartera de Metsera; se asignan $3B a la monoterapia'),
    dict(key='combo', name='MET-097i + MET-233i (GLP-1 + amilina)', area='metabolica', phase=2, peak=2.5, launch=2031, loe=2043.0, curve='bio',
         src='Resto del pico combinado de Leerink (>$5B) para la combinación'),
    dict(key='pd1v', name='PF-08634404 (PD-1 x VEGF, de 3SBio)', area='oncologia', phase=3, peak=4.0, launch=2029, loe=2042.0, curve='bio', roy=0.10,
         src='Supuesto propio (sin consenso público); Pfizer pagó $1.25B por adelantado y hasta $4.8B en hitos'),
    dict(key='atir', name='Atirmociclib (inhibidor de CDK4)', area='oncologia', phase=3, peak=2.0, launch=2029, loe=2040.0, curve='us_sm',
         src='Supuesto propio: la mitad del pico histórico de Ibrance (~$5B)'),
    dict(key='mevro', name='Mevrometostat (EZH2) + Xtandi', area='oncologia', phase=3, peak=1.5, launch=2028, loe=2038.0, curve='us_sm',
         src='Supuesto propio'),
    dict(key='elrx', name='Elrexfio, nuevas indicaciones (MM-32 positivo)', area='oncologia', phase='pres', peak=1.2, launch=2027, loe=2036.0, curve='bio',
         src='Supuesto propio; MM-32 cumplió su objetivo primario (oct-2026)'),
    dict(key='tilr', name='Tilrekimig (IL-4/IL-13/TSLP)', area='autoinmune', phase=3, peak=3.0, launch=2030, loe=2043.0, curve='bio',
         src='Supuesto propio (dermatitis atópica, asma y EPOC)'),
    dict(key='pnc25', name='Vacuna neumocócica de 25 valencias (incremental)', area='infecciosas', phase=3, peak=1.5, launch=2029, loe=2045.0, curve='vac',
         src='Supuesto propio: incremental sobre Prevnar 20 (defensa de la franquicia)'),
    dict(key='lyme', name='Vacuna contra la enfermedad de Lyme (VLA15)', area='infecciosas', phase='pres', peak=0.8, launch=2027, loe=2045.0, curve='vac', roy=0.15,
         src='Supuesto propio; regalías e hitos a Valneva'),
    dict(key='osiv', name='Osivelotor (anemia falciforme)', area='hematologia', phase=3, peak=1.0, launch=2029, loe=2042.0, curve='us_sm', src='Supuesto propio'),
    dict(key='otros3', name='Resto de fase 3 (dazukibart, disitamab vedotin, sigvotatug 1L, C. difficile, estreptococo B, ibuzatrelvir)',
         area='todas', phase=3, peak=4.1, launch=2029, loe=2041.0, curve='bio', roy=0.03,
         src='Supuesto propio: 6 activos, $0.4B-$0.8B de pico cada uno'),
    dict(key='litf', name='Litfulo en vitiligo (presentado en la UE)', area='autoinmune', phase='pres', peak=0.6, launch=2027, loe=2034.0, curve='us_sm',
         src='Supuesto propio'),
]
for a in PIPE0: a['pos'] = pos(a['area'], a['phase'])
# Los ensayos de fase 3 de dos activos se cuentan con la tasa de su área (BIO, Fig. 5b); el "resto" usa la tasa de todas las áreas.
CVR = [dict(usd=4.60 * 111.4e-3, prob=BIO['metabolica'][1] / BIO['metabolica'][1] * PH['exito_clinico']['transicion_por_fase']['metabolica'][1] / 100, year=2027.5),
       dict(usd=6.40 * 111.4e-3, prob=BIO['metabolica'][2] / 100, year=2029.0),
       dict(usd=9.65 * 111.4e-3, prob=BIO['metabolica'][1] / 100, year=2031.0)]
put('metsera_shares', 2.3 / 20.65)          # acciones de Metsera implícitas en el tope del CVR ($2.3B / $20.65)
for c in CVR: c['usd'] = c['usd'] / 111.4e-3 * M['metsera_shares']
ACQ = put('acq', 0.65)          # licencia de Innovent (3T26), a costo de transacción
def g(d): return d
def build(name, wacc=None, pos1=None, renewal=False, vyn_bull=False, cm30=None, wacc_delta=True):
    s = {'base': 0, 'bear': 1, 'bull': 2}[name]
    pick = lambda b, be, bu: (b, be, bu)[s]
    p = dict(stub=0.25, tax=TAX / 100, shares=M['shares_dil'], net_debt=ND, acq=ACQ, plat_share=0.40, plat_year=2040, plat_g=0.02)
    p['wacc'] = (wacc if wacc is not None else WACC / 100) + ((0, 0.0075, -0.0075)[s] if wacc is None else 0)
    c30 = cm30 if cm30 is not None else pick(M['cm30'], M['cm30_bear'], M['cm30_bull'])
    p['cm'] = {2026: CM0 / 100, 2030: c30 / 100}
    p['capex'] = {2026: CX0, 2030: pick(0.04, 0.045, 0.035)}
    p['rd'] = {2026: RD0, 2030: pick(M['rd30'], M['rd30_bear'], M['rd30_bull']) / 100}
    C = CUR
    y = Y26
    eu, iu, xu, ju, vu = US['eliq'], US['ibr'], 1.0, US['xelj'], US['vyn']
    vyn_us_loe = pick(LOE['vyn_us'], 2029.0, 2035.67)
    pr = {
        'eliq': [dict(v26=y['eliq'] * eu, g={2027: pick(-0.03, -0.08, 0.0)}, loe=pick(LOE['eliq_us'], 2027.5, LOE['eliq_us']), curve=C['us_sm']),
                 dict(v26=y['eliq'] * (1 - eu), g={2027: pick(-0.12, -0.18, -0.08)}, loe=None, curve=C['ex_sm'])],
        'ibr': [dict(v26=y['ibr'] * iu, g={2027: 0.0}, ira=(2027, 0.15), loe=LOE['ibr_us'], curve=C['us_sm']),
                dict(v26=y['ibr'] * (1 - iu), g={2027: -0.10}, loe=LOE['ibr_ex'], curve=C['ex_sm'])],
        'xtd': [dict(v26=y['xtd'], g={2027: -0.03}, ira=(2027, 0.15), loe=LOE['xtd_us'], curve=C['us_sm'])],
        'xelj': [dict(v26=y['xelj'] * ju, g={2027: 0.0}, loe=LOE['xelj_us'], curve=C['us_sm']),
                 dict(v26=y['xelj'] * (1 - ju), g={2027: -0.05}, loe=LOE['xelj_ex'], curve=C['ex_sm'])],
        'vyn': [dict(v26=y['vyn'] * vu, g={2027: pick(0.08, 0.04, 0.10), 2028: pick(0.06, 0.02, 0.08), 2029: pick(0.04, 0.0, 0.06), 2031: 0.0},
                     ira=None if s == 2 else (2029, M['vyn_ira_cut'] / 100 * (1.5 if s == 1 else 1.0)), loe=vyn_us_loe, curve=C['us_sm']),
                dict(v26=y['vyn'] * (1 - vu), g={2027: 0.0}, loe=pick(LOE['vyn_ex'], 2027.0, 2029.25), curve=C['ex_sm'])],
        'prev': [dict(v26=y['prev'], g={2027: pick(-0.03, -0.06, 0.0), 2030: pick(-0.03, -0.06, 0.0), 2031: 0.0}, loe=LOE['prev'], curve=C['vac'])],
        'seagen': [dict(v26=sum(y[k] for k in GROUPS['seagen']), g={2027: pick(0.18, 0.12, 0.22), 2028: pick(0.12, 0.08, 0.15), 2029: pick(0.08, 0.04, 0.10),
                        2030: pick(0.05, 0.02, 0.07), 2031: 0.02, 2032: 0.0}, loe=LOE['seagen'], curve=C['bio'])],
        'launch': [dict(v26=sum(y[k] for k in GROUPS['launch']), g={2027: pick(0.12, 0.07, 0.15), 2028: pick(0.10, 0.05, 0.12), 2029: pick(0.07, 0.03, 0.09),
                        2030: pick(0.05, 0.02, 0.06), 2031: 0.02, 2033: 0.0}, loe=LOE['launch'], curve=(0.50, 0.75, 0.15))],
        'loeg': [dict(v26=sum(y[k] for k in GROUPS['loeg']), g={2027: -0.20, 2030: -0.20, 2031: -0.35}, loe=None, curve=None)],
        'covid': [dict(v26=y['com'] + y['pax'], g={2027: pick(-0.15, -0.25, -0.10), 2028: pick(-0.10, -0.15, -0.05), 2030: pick(-0.10, -0.15, -0.05), 2031: -0.05}, loe=None, curve=None)],
        'rest': [dict(v26=Y26_REST, g={2027: pick(-0.02, -0.04, 0.0)}, loe=None, curve=None)],
    }
    p['products'] = pr
    p['renew_keys'] = ('eliq', 'vyn', 'prev', 'ibr', 'xtd')
    pipe = copy.deepcopy(PIPE0)
    for a in pipe:
        a['curve'] = C[a['curve']]
        a['peak'] *= pick(1.0, 0.6, 1.3)
        if a['key'] == ASSET1 and pos1 is not None: a['pos'] = pos1
    p['pipeline'] = pipe
    p['cvr'] = copy.deepcopy(CVR)
    if renewal: p['renewal'] = True
    # el stub del 4T26 usa el nivel 2026 calendario; se escala para que la suma del 4T reproduzca el 4T implícito en la guía
    return p
ASSET1 = None
# El activo #1 del pipeline es el de mayor rNPV en el Base (se determina corriendo el Base una vez)
_b = run(build('base'))
ASSET1 = put('asset1', max((a['key'] for a in PIPE0 if a['key'] != 'otros3'), key=lambda k: _b['C'][k]))   # el grupo 'resto' no es un activo
A1 = next(a for a in PIPE0 if a['key'] == ASSET1)
put('asset1_name', A1['name']); put('asset1_pos', A1['pos'] * 100)
R = {s: run(build(s)) for s in ('base', 'bear', 'bull')}
B = R['base']
assert abs(B['fv'] - _b['fv']) < 1e-12
put('m1', B['fv']); put('m1_bear', R['bear']['fv']); put('m1_bull', R['bull']['fv'])
put('m1_ev', B['ev']); put('m1_eq', B['eq'])
CMP = B['C']
put('sotp', dict(CMP)); put('sotp_ps', {k: v / M['shares_dil'] for k, v in CMP.items()})
PIPE_KEYS = [a['key'] for a in PIPE0]
put('pipe_total', sum(CMP[k] for k in PIPE_KEYS)); put('pipe_total_ps', M['pipe_total'] / M['shares_dil'])
put('metsera_rnpv', CMP['bero'] + CMP['combo'] + CMP['cvr'])
put('seagen_v', CMP['seagen']); put('seagen_v_ps', CMP['seagen'] / M['shares_dil'])
put('nd_ps', ND / M['shares_dil']); put('ev_ps', B['ev'] / M['shares_dil'])
for s in ('base', 'bear', 'bull'):
    put(f'rev30_{s}', R[s]['tot'][2030]); put(f'fcfm30_{s}', R[s]['fcfm'][2030] * 100)
    put(f'plat_share_{s}', R[s]['C']['platform'] / R[s]['ev'] * 100)
    put(f'rev35_{s}', R[s]['tot'][2035])
put('rev27_model', B['tot'][2027]); put('rev28_model', B['tot'][2028]); put('rev29_model', B['tot'][2029])
put('rev_trough_year', min(range(2026, 2032), key=lambda y: B['tot'][y])); put('rev_trough', B['tot'][M['rev_trough_year']])
put('rev27_vs_cons', (B['tot'][2027] / M['rev_c27'] - 1) * 100)
put('rev_path', [round(B['tot'][y], 2) for y in range(2026, 2036)])
put('rev_path_loe', [round(sum(B['R'][k][y] for k in ('eliq', 'ibr', 'xtd', 'xelj', 'vyn')), 2) for y in range(2026, 2036)])
put('rev_path_new', [round(sum(B['R'][k][y] for k in ['seagen', 'launch'] + PIPE_KEYS), 2) for y in range(2026, 2036)])
put('rev_path_other', [round(a - b - c, 2) for a, b, c in zip(M['rev_path'], M['rev_path_loe'], M['rev_path_new'])])
put('rev_path_pipe', [round(sum(B['R'][k][y] for k in PIPE_KEYS), 2) for y in range(2026, 2036)])
put('pipe30', sum(B['R'][k][2030] for k in PIPE_KEYS)); put('pipe35', sum(B['R'][k][2035] for k in PIPE_KEYS))
pv = build('base'); pv['products']['vyn'][0]['loe'] = 2035.67; put('m1_vyn2035', run(pv)['fv'])
pe = build('base'); pe['products']['eliq'][0]['loe'] = 2031.17; put('m1_eliq2031', run(pe)['fv'])
put('m1_renewal', run(build('base', renewal=True))['fv']); put('m1_renewal_gap', (M['m1_renewal'] / PRICE - 1) * 100)
put('m1_ev_w', 0.25 * M['m1_bear'] + 0.45 * M['m1'] + 0.30 * M['m1_bull'])
pn = build('base'); pn['pipeline'] = []; pn['cvr'] = []; put('m1_nopipe', run(pn)['fv'])
pb = build('base'); pb['wacc'] = M['wacc_own'] / 100; put('m1_wacc_own', run(pb)['fv'])
# Sensibilidad: WACC (grilla común) x probabilidad del activo #1
GW = put('grid_w', TD['grilla_sensibilidad_pct'])
GP = sorted({0.25, 0.40, round(A1['pos'], 4), 0.75, 0.906})
assert len(GP) == 5
put('grid_p', [x * 100 for x in GP]); put('grid_base_col', GP.index(round(A1['pos'], 4)))
put('grid', [[run(build('base', wacc=w / 100, pos1=q))['fv'] for q in GP] for w in GW])
assert abs(M['grid'][2][M['grid_base_col']] - M['m1']) < 1e-9
put('grid_min', min(min(r) for r in M['grid'])); put('grid_max', max(max(r) for r in M['grid']))
# Tabla del pipeline (para el informe)
put('pipe_rows', [dict(name=a['name'], area=a['area'], phase=a['phase'], pos=a['pos'] * 100, peak=a['peak'], launch=a['launch'],
                       radj=a['peak'] * a['pos'], v=CMP[a['key']], src=a['src']) for a in PIPE0])
AREA_ES = dict(metabolica='Metabólica', oncologia='Oncología', autoinmune='Autoinmune', infecciosas='Infecciosas (vacunas)', hematologia='Hematología', todas='Todas las áreas')
PHASE_ES = {1: 'Fase 1', 2: 'Fase 2', 3: 'Fase 3', 'pres': 'Presentado'}
for r, a in zip(M['pipe_rows'], PIPE0): r['area_es'] = AREA_ES[a['area']]; r['phase_es'] = PHASE_ES[a['phase']]
put('pipe_radj_peak', sum(a['peak'] * a['pos'] for a in PIPE0))
# Revenue gap: ventas TTM que pierden exclusividad en EE.UU. (o en todos sus mercados) hasta fin de 2030
LOE_ROWS = [  # clave, producto, tipo, LOE EE.UU., LOE Europa, IRA, fracción en riesgo hasta 2030 (1 = todo el producto)
    ('eliq', 'Eliquis (apixabán)', 'Molécula pequeña', '1-abr-2028 (acuerdos)', '2026', 'Precio negociado desde 2026 (−56% sobre lista)', 1.0),
    ('vyn', 'Vyndaqel / Vyndamax (tafamidis)', 'Molécula pequeña', '1-jun-2031 (acuerdos)', '2026', 'Elegible; no seleccionado aún', 1 - US['vyn']),
    ('ibr', 'Ibrance (palbociclib)', 'Molécula pequeña', 'mar-2027', '2028', 'Precio negociado desde 2027 (−50%)', 1.0),
    ('xtd', 'Xtandi (enzalutamida)', 'Molécula pequeña', 'ago-2027', 'Astellas', 'Precio negociado desde 2027 (−48%)', 1.0),
    ('xelj', 'Xeljanz (tofacitinib)', 'Molécula pequeña', 'jun-2026', '2028', 'Ronda 2028 (precio no publicado al corte)', 1.0),
    ('inl', 'Inlyta (axitinib)', 'Molécula pequeña', 'dic-2030 (Orange Book)', 'n.d.', '—', 1.0),
    ('adc', 'Adcetris (brentuximab vedotin)', 'Biológico (ADC)', '2026', 'Takeda', '—', 1.0),
    ('braf', 'Braftovi / Mektovi', 'Molécula pequeña', '2030 / 2026', 'Pierre Fabre', '—', 1.0),
    ('bos', 'Bosulif (bosutinib)', 'Molécula pequeña', 'nov-2026', 'n.d.', '—', 1.0),
    ('talz', 'Talzenna (talazoparib)', 'Molécula pequeña', '2029', '2034', '—', 1.0),
]
put('loe_rows', [dict(k=k, name=n, tipo=t, us=u, eu=e, ira=i, ttm=PT[k] / 1000, share=PT[k] / TTM_REV * 100, frac=f) for k, n, t, u, e, i, f in LOE_ROWS])
GAP30 = put('gap30', sum(PT[k] * f for k, n, t, u, e, i, f in LOE_ROWS) / 1000)
put('gap30_pct', GAP30 / M['ttm_rev'] * 100)
put('gap31', GAP30 + PT['vyn'] * US['vyn'] / 1000); put('gap31_pct', M['gap31'] / M['ttm_rev'] * 100)
put('gap_big5', sum(PT[k] for k in ('eliq', 'ibr', 'xtd', 'xelj')) / 1000 + PT['vyn'] * (1 - US['vyn']) / 1000)
put('eliq_share', PT['eliq'] / TTM_REV * 100)
put('vyn_ex_ttm', PT['vyn'] * (1 - US['vyn']) / 1000)

# ======================= 6. Método 2 — comparables (13 pares comunes, P/E forward) =======================
PRS = PH['comparables']['pares']
PEERS = put('peers', {k: v['pe_fwd'] for k, v in PRS.items()})
assert len(PEERS) == 13 and 'PFE' not in PEERS and 'ABBV' not in PEERS
v = sorted(PEERS.values())
put('peer_q3', float(np.percentile(v, 75))); put('peer_med', float(np.percentile(v, 50))); put('peer_max', max(v)); put('peer_min', min(v))
assert abs(M['peer_q3'] - PH['comparables']['estadisticos']['pe_fwd_q3']) < 1e-9 and abs(M['peer_med'] - PH['comparables']['estadisticos']['pe_fwd_mediana']) < 1e-9
# Regresión P/E forward vs crecimiento de EPS 2027/2026 (sin MRK ni GILD: su EPS 2026 está deprimido por IPR&D, nota del JSON)
RX = {k: (PRS[k]['eps_fy27'] / PRS[k]['eps_fy26'] - 1) * 100 for k in PRS if k not in ('MRK', 'GILD')}
xs = np.array(list(RX.values())); ys = np.array([PEERS[k] for k in RX])
def r2(x, y):
    b, a = np.polyfit(x, y, 1); pr = a + b * x
    return float(1 - ((y - pr) ** 2).sum() / ((y - y.mean()) ** 2).sum()), float(a), float(b)
R2A, AA, BA = r2(xs, ys)
ext = list(RX)[int(np.argmax(np.abs(xs - xs.mean())))]
mask = np.array([k != ext for k in RX]); R2B, AB, BB = r2(xs[mask], ys[mask])
put('reg_n', len(RX)); put('reg_r2', R2A); put('reg_r2_x', R2B); put('reg_ext', ext); put('reg_slope', BA); put('reg_slope_x', BB)
put('reg_pe_pfe', AB + BB * M['c27_g']); put('reg_fv', M['reg_pe_pfe'] * C27 / (1 + KE / 100))
put('reg_pts', [[round(float(a), 2), round(float(b), 2)] for a, b in zip(xs, ys)]); put('reg_names', list(RX))
REG_OK = R2B >= 0.30
assert not REG_OK      # la regresión no se sostiene sin el extremo: se usa el criterio de la skill
NTM = put('eps_ntm', (C26 - 2.39) + 0.75 * C27); put('q4_eps_impl', C26 - 2.39)
# Decisión del coordinador (22-nov-2026, igual en ABBV): la regresión no se sostiene -> regla de la casa desde KO: MEDIANA del
# P/E forward de los 13 pares sobre el EPS 2027 de consenso, descontado un año al costo de equity común. El cuartil superior
# mete un premio por calidad que la regresión no respalda: queda como referencia, fuera del blend.
M2 = put('m2', M['peer_med'] * C27 / (1 + KE / 100))
put('m2_q3', M['peer_q3'] * C27 / (1 + KE / 100)); put('m2_ntm', M['peer_med'] * NTM)
put('m2_hi', M['peer_max'] * C27 / (1 + KE / 100))
q3_name = min(PEERS, key=lambda k: abs(PEERS[k] - M['peer_q3'])); max_name = max(PEERS, key=PEERS.get); med_name = min(PEERS, key=lambda k: abs(PEERS[k] - M['peer_med']))
put('q3_name', q3_name); put('max_name', max_name); put('med_name', med_name)
# Referencia (no entra al método): pares con precipicio de patentes en curso o reciente (BMY, SNY, GSK, NVO)
CLIFF = ['BMY', 'SNY', 'GSK', 'NVO']
put('cliff_pe', st.mean(PEERS[k] for k in CLIFF)); put('cliff_fv', M['cliff_pe'] * C27 / (1 + KE / 100))
put('m2_lo', M['cliff_fv'])   # piso del rango del football field: subgrupo de pares en precipicio
put('pfe_pe_fwd', SH['pfe_precio']['multiplos']['pe_fwd']); put('abbv_pe_fwd', PH['comparables']['referencia_cruzada']['ABBV']['pe_fwd'])
put('pfe_disc_med', (M['pfe_pe_fwd'] / M['peer_med'] - 1) * 100)
put('hc_pe', SH['mercado']['sectores_pe_fwd']['health_care']['pe_ajustado_20nov']); put('sp_pe', SH['mercado']['sp500']['pe_fwd_ajustado_20nov'])
PEER_TAB = ['LLY', 'JNJ', 'MRK', 'BMY', 'AMGN', 'GILD', 'NVO', 'AZN', 'NVS', 'GSK', 'SNY', 'REGN', 'VRTX']
put('peer_rows', [dict(t=k, pe=PRS[k]['pe_fwd'], eve=PRS[k]['ev_ebitda'], dy=PRS[k]['div_yield_pct'] or 0.0, nde=PRS[k]['deuda_ebitda']) for k in PEER_TAB])
put('comps_labels', ['PFE'] + sorted(PEER_TAB, key=lambda k: -PEERS[k]))
put('comps_values', [round(M['pfe_pe_fwd'], 2)] + [round(PEERS[k], 2) for k in sorted(PEER_TAB, key=lambda k: -PEERS[k])])

# ======================= 7. Método 3 — reversión al P/E propio (ventana limpia) =======================
# Ventana: ocho cierres trimestrales 4T24-3T26 (después de la COVID y con las fechas del precipicio ya públicas), P/E sobre
# EPS ajustado TTM tal como lo reporta Pfizer (incluye IPR&D adquirida: Pfizer compra pipeline todos los años).
PXQ = {'31-dic-2024': 26.53, '31-mar-2025': 25.34, '30-jun-2025': 24.24, '30-sep-2025': 25.48, '31-dic-2025': 24.90,
       '31-mar-2026': 28.08, '30-jun-2026': 24.08, '30-sep-2026': 28.52}
d = json.load(open(ROOT / '.claude/skills/_compartido/defensivos_nov26/yh/PFE.d.json'))['chart']['result'][0]
import datetime as dt
DD = {dt.datetime.fromtimestamp(a, dt.UTC).strftime('%Y-%m-%d'): c for a, c in zip(d['timestamp'], d['indicators']['quote'][0]['close']) if c}
for lab, iso in zip(PXQ, ['2024-12-31', '2025-03-31', '2025-06-30', '2025-09-30', '2025-12-31', '2026-03-31', '2026-06-30', '2026-09-30']):
    assert abs(DD[iso] - PXQ[lab]) < 0.006, (lab, DD[iso])
qs = list(EPSQ)
EPS_TTM_Q = {'31-dic-2024': 3.11}
for i, lab in enumerate(list(PXQ)[1:]):
    j = qs.index({'31-mar-2025': '1T25', '30-jun-2025': '2T25', '30-sep-2025': '3T25', '31-dic-2025': '4T25', '31-mar-2026': '1T26',
                  '30-jun-2026': '2T26', '30-sep-2026': '3T26'}[lab])
    EPS_TTM_Q[lab] = round(sum(EPSQ[q] for q in qs[j - 3:j + 1]), 2)
EPS_TTM_Q['31-dic-2025'] = 3.22                      # EPS ajustado 2025 publicado (la suma trimestral da 3.23 por redondeo)
REV = put('rev_rows', [dict(d=k, px=PXQ[k], eps=EPS_TTM_Q[k], pe=PXQ[k] / EPS_TTM_Q[k]) for k in PXQ])
assert REV[-1]['eps'] == EPS_TTM
put('rev_pe', st.mean(r['pe'] for r in REV)); M3 = put('m3', M['rev_pe'] * EPS_TTM)
put('m3_lo', min(r['pe'] for r in REV) * EPS_TTM); put('m3_hi', max(r['pe'] for r in REV) * EPS_TTM)
put('pe_now_ttm', PRICE / EPS_TTM)
# Referencias: (a) sin el ajuste de ventana: cierres de fin de año 2015-2025 (incluye los años COVID); (b) precipicio de Lipitor 2011-2013.
SPIN = 1.054   # Yahoo trata la escisión de Upjohn/Viatris (nov-2020) como un "split" 1054:1000: los cierres previos se multiplican por 1.054
mo = json.load(open(HERE / 'yh/PFE.mo25.json'))['chart']['result'][0]
assert abs(mo['events']['splits']['1604203200']['numerator'] / mo['events']['splits']['1604203200']['denominator'] - SPIN) < 1e-9
MO = {dt.datetime.fromtimestamp(a, dt.UTC).strftime('%Y-%m'): c for a, c in zip(mo['timestamp'], mo['indicators']['quote'][0]['close']) if c}
EPS_FY = put('epsa_fy', {2011: 2.27, 2012: 2.19, 2013: 2.22, 2015: 2.20, 2016: 2.40, 2017: 2.65, 2018: 3.00, 2019: 2.95, 2020: 2.22,
                         2021: 4.42, 2022: 6.58, 2023: 1.84, 2024: 3.11, 2025: 3.22})
def ye(y): return MO[f'{y}-12'] * (SPIN if y < 2020 else 1.0)
FYPE = put('fy_pe', {str(y): ye(y) / EPS_FY[y] for y in EPS_FY})
put('pe_all', st.mean(FYPE[str(y)] for y in range(2015, 2026))); put('m3_all', M['pe_all'] * EPS_TTM)
put('pe_lip', st.mean(FYPE[str(y)] for y in (2011, 2012, 2013))); put('m3_lip', M['pe_lip'] * EPS_TTM)
put('pe_precovid', st.mean(FYPE[str(y)] for y in range(2015, 2020))); put('m3_precovid', M['pe_precovid'] * EPS_TTM)
put('fy_pe_chart_years', [str(y) for y in range(2015, 2026)]); put('fy_pe_chart', [round(FYPE[str(y)], 2) for y in range(2015, 2026)])
put('px_2012', ye(2012)); put('px_2013', ye(2013)); put('px_2011', ye(2011))

# ======================= 8. Método 4 — consenso (S&P Global vía stockanalysis, 22-nov-2026) =======================
M4 = put('m4', CO['pt_prom']); put('m4_lo', CO['pt_min']); put('m4_hi', CO['pt_max']); put('m4_n', CO['n_analistas']); put('m4_rec', CO['recomendacion'])

# ======================= 9. Blend =======================
W = {'m1': 0.15, 'm2': 0.25, 'm3': 0.35, 'm4': 0.25}
for k, w in W.items(): put(k + '_ap', round(M[k], 2) * w)
BL = put('blend', round(sum(round(M[k], 2) * w for k, w in W.items()), 2)); put('blend_gap', (BL / PRICE - 1) * 100)
for k in W: put(k + '_gap', (M[k] / PRICE - 1) * 100)
put('indep', (0.15 * M['m1'] + 0.25 * M['m2']) / 0.40); put('anch', (0.35 * M['m3'] + 0.25 * M['m4']) / 0.60)
put('indep_gap', (M['indep'] / PRICE - 1) * 100); put('anch_gap', (M['anch'] / PRICE - 1) * 100)
put('blend_q3', BL + 0.25 * (M['m2_q3'] - M['m2'])); put('blend_q3_gap', (M['blend_q3'] / PRICE - 1) * 100)
put('blend_cliff', BL + 0.25 * (M['cliff_fv'] - M['m2'])); put('blend_cliff_gap', (M['blend_cliff'] / PRICE - 1) * 100)
put('blend_xcons', (0.15 * M['m1'] + 0.25 * M['m2'] + 0.35 * M['m3']) / 0.75); put('blend_xcons_gap', (M['blend_xcons'] / PRICE - 1) * 100)
put('blend_lip', BL + 0.35 * (M['m3_lip'] - M['m3'])); put('blend_all', BL + 0.35 * (M['m3_all'] - M['m3']))
put('ranges', [[M['m1_bear'], M['m1_bull']], [M['m2_lo'], M['m2_hi']], [M['m3_lo'], M['m3_hi']], [M['m4_lo'], M['m4_hi']]])
# Postura: sale del número (misma escala que las tarjetas: |brecha| < 5% neutral; 5-15% neutral con sesgo; > 15% fuera de neutral)
g_ = M['blend_gap']
POST = put('postura', 'neutral' if abs(g_) < 5 else ('neutral, con sesgo constructivo' if 0 < g_ <= 15 else
            'neutral, con sesgo cauteloso' if -15 <= g_ < 0 else ('constructiva' if g_ > 0 else 'neutral, con sesgo bajista')))
put('card_accent', 'neutral' if abs(g_) <= 15 else ('up' if g_ > 0 else 'down'))
put('postura_up', POST.upper())

# Anti-circularidad: el modelo corrido con otro precio de PFE da lo mismo en M1, M2, M3 y M4 (la tasa común no usa el precio de PFE)
if TXT:
    import subprocess, sys
    subprocess.run([sys.executable, __file__], env=dict(os.environ, PFE_PRICE=str(round(PRICE * 1.25, 4))), capture_output=True, text=True, check=True, cwd=HERE)
    J2 = json.loads(open(HERE / 'model_price.json', encoding='utf-8').read())
    for k in ('m1', 'm2', 'm3', 'm4'): put('anti_' + k, J2[k] - M[k])
    put('anti_price', J2['price']); put('anti_wacc_own', J2['wacc_own'] - M['wacc_own'])
    os.remove(HERE / 'model_price.json')
    assert M['anti_m1'] == 0 and M['anti_m2'] == 0 and M['anti_m3'] == 0 and M['anti_m4'] == 0

# ======================= 10. Cuadro PFE vs ABBV vs LLY vs JNJ (dict cmp, mismas claves en el informe de ABBV) =======================
CMP_KEYS = ['ticker', 'precio', 'fair_value', 'gap_pct', 'm1_sotp', 'm2_comp', 'm3_rev', 'm4_cons', 'indep', 'anclados', 'pe_fy27',
            'div_yield_pct', 'payout_fcf_pct', 'nd_ebitda', 'rd_ventas_pct', 'margen_bruto_pct', 'ventas_riesgo_loe_2030_pct',
            'crec_eps_fy27_pct', 'wacc_pct', 'postura']
cmp = put('cmp', dict(ticker='PFE', precio=PRICE, fair_value=BL, gap_pct=M['blend_gap'], m1_sotp=M['m1'], m2_comp=M['m2'], m3_rev=M['m3'],
                      m4_cons=M['m4'], indep=M['indep'], anclados=M['anch'], pe_fy27=M['pe_27'], div_yield_pct=M['div_yield'],
                      payout_fcf_pct=M['payout_fcf'], nd_ebitda=M['nd_lev'], rd_ventas_pct=M['ttm_rd_pct'], margen_bruto_pct=M['gm3'],
                      ventas_riesgo_loe_2030_pct=M['gap30_pct'], crec_eps_fy27_pct=M['c27_g'], wacc_pct=WACC, postura=POST))
assert list(cmp) == CMP_KEYS
LJ = PH['lly_jnj_3t26']
def ref(t, d):
    m1, m2, m3, m4 = d['m1_sotp'], d['m2_comp'], d['m3_rev'], d['m4_cons']
    return dict(ticker=t, precio=d['cierre_20nov'], fair_value=d['fair_value_publicado'], gap_pct=d['gap_al_20nov_pct'], m1_sotp=m1, m2_comp=m2,
                m3_rev=m3, m4_cons=m4, indep=(0.15 * m1 + 0.25 * m2) / 0.40, anclados=(0.35 * m3 + 0.25 * m4) / 0.60, pe_fy27=d['pe_fy27_20nov'],
                div_yield_pct=d['div_yield_20nov_pct'], payout_fcf_pct=None, nd_ebitda=d['deuda_neta_ebitda'],
                rd_ventas_pct=d['rd_ventas_ttm_pct'], margen_bruto_pct=d['margen_bruto_3t_pct'],
                ventas_riesgo_loe_2030_pct=d.get('ventas_en_riesgo_loe_ttm_pct', d.get('ventas_en_riesgo_loe_pct')),
                crec_eps_fy27_pct=(PRS[t]['eps_fy27'] / PRS[t]['eps_fy26'] - 1) * 100,
                wacc_pct=d.get('wacc_pct', d.get('wacc_im_pct')), postura='neutral, con sesgo bajista')
CMPS = {'PFE': cmp, 'LLY': ref('LLY', LJ['LLY']), 'JNJ': ref('JNJ', LJ['JNJ'])}
for t in ('LLY', 'JNJ'): assert list(CMPS[t]) == CMP_KEYS
put('cmp_refs', {t: CMPS[t] for t in ('LLY', 'JNJ')})
put('lly_pub_price', LJ['LLY']['precio_de_publicacion']); put('jnj_pub_price', LJ['JNJ']['precio_de_publicacion'])

# ======================= 11. Derivados para texto y gráficos =======================
MIXN = dict(eliq='Eliquis', vyn='Vyndaqel', prev='Prevnar', ibr='Ibrance', com='Comirnaty', pad='Padcev', xtd='Xtandi', nur='Nurtec',
            onb='Biosimilares onc.', lor='Lorbrena', abr='Abrysvo', xelj='Xeljanz', inl='Inlyta', pax='Paxlovid', braf='Braftovi/Mektovi', adc='Adcetris')
order = sorted(MIXN, key=lambda k: -PT[k])
put('mix_labels', [MIXN[k] for k in order]); put('mix_values', [round(PT[k] / 1000, 2) for k in order]); put('mix_keys', order)
put('mix_loe', [k in ('eliq', 'ibr', 'xtd', 'xelj', 'inl', 'adc', 'braf') for k in order])
put('loe_chart_labels', ['Xeljanz (2026)', 'Ibrance (2027)', 'Xtandi (2027)', 'Eliquis (2028)', 'Vyndaqel ex-EE.UU. (2026-29)', 'Otros (2026-30)', 'Vyndaqel EE.UU. (2031)'])
put('loe_chart_values', [round(x, 2) for x in (PT['xelj'] / 1000, PT['ibr'] / 1000, PT['xtd'] / 1000, PT['eliq'] / 1000, M['vyn_ex_ttm'],
                                                 sum(PT[k] for k in ('inl', 'adc', 'braf', 'bos', 'talz')) / 1000, PT['vyn'] * US['vyn'] / 1000)])
put('sotp_chart_labels', ['Eliquis', 'Vyndaqel', 'Prevnar', 'Seagen (Padcev, Tukysa, Tivdak)', 'Lanzamientos recientes', 'Resto del portafolio',
                          'COVID (Comirnaty, Paxlovid)', 'Ibrance + Xtandi + Xeljanz', 'Otros con LOE 2026-30', 'Pipeline (rNPV)', 'Plataforma post-2040',
                          'Licencia Innovent (a costo)', 'CVR Metsera', 'I+D corporativa', 'Deuda neta'])
put('sotp_chart', [round(x, 1) for x in (CMP['eliq'], CMP['vyn'], CMP['prev'], CMP['seagen'], CMP['launch'], CMP['rest'], CMP['covid'],
                                         CMP['ibr'] + CMP['xtd'] + CMP['xelj'], CMP['loeg'], M['pipe_total'], CMP['platform'], CMP['acq'], CMP['cvr'], CMP['rd'], -ND)])
put('sotp_short', CMP['ibr'] + CMP['xtd'] + CMP['xelj']); put('sotp_short_ps', M['sotp_short'] / M['shares_dil'])
CF = {'2023': dict(ocf=8700, capex=3907, div=9247), '2024': dict(ocf=12744, capex=2909, div=9512), '2025': dict(ocf=11704, capex=2629, div=9771)}   # 10-K 2025
for c in CF.values(): c['fcf'] = c['ocf'] - c['capex']; c['cov'] = c['fcf'] / c['div']
put('cf_hist', CF)
put('fcf30', R['base']['fcf'][2030] + 0.0); put('fcf30_b', M['fcfm30_base'] / 100 * M['rev30_base'])
put('pfe_eve', SH['pfe_precio']['multiplos']['ev_ebitda']); put('pfe_de_sa', SH['pfe_precio']['multiplos']['deuda_ebitda'])
put('amort3_ly', 1223); put('epsa3_g', (M['epsa3'] / M['epsa3_ly'] - 1) * 100)
put('margin_q_labels', ['1T25', '2T25', '3T25', '4T25', '1T26', '2T26', '3T26'])
REVQ = [13715, 14653, 16654, 17557, 13576, 15908, 16583]; COGSQ = [3074, 3549, 4172, 5272, 3627, 4013, 4028]
assert sum(REVQ[:3]) == 45022 and sum(REVQ[4:]) == 46067 and sum(COGSQ[:3]) == 10795 and sum(COGSQ[4:]) == 11668 and sum(REVQ[:4]) == 62579 and sum(COGSQ[:4]) == 16067
put('rev_q', [round(x / 1000, 2) for x in REVQ]); put('gm_q', [round((1 - c / r) * 100, 1) for c, r in zip(COGSQ, REVQ)])
put('cash_years', ['2021', '2022', '2023', '2024', '2025', 'TTM'])
put('cash_ocf', [32.58, 29.27, 8.70, 12.74, 11.70, round(TTM['ocf'] / 1000, 2)]); put('cash_div', [8.73, 8.98, 9.25, 9.51, 9.77, round(TTM['div'] / 1000, 2)])
put('cash_fcf', [round(a - b, 2) for a, b in zip(M['cash_ocf'], [2.71, 3.24, 3.91, 2.91, 2.63, round(TTM['capex'] / 1000, 2)])])
put('price_hist_labels', [k for k in sorted(MO) if k >= '2020-12'][::3] + ['2026-11'])
put('price_hist', [round(MO[k], 2) for k in sorted(MO) if k >= '2020-12'][::3] + [round(PRICE, 2)])
SPK = [k for k in sorted(MO) if k <= '2026-11'][-7:]
put('spark', [round(MO[k], 2) for k in SPK])
put('price_peak21', max(MO[k] for k in MO if '2021-01' <= k <= '2022-12')); put('price_drawdown', (PRICE / M['price_peak21'] - 1) * 100)
put('m1_frac', M['m1'] / PRICE * 100)
put('div_ttm_b', TTM['div'] / 1000); put('fcf_b', FCF / 1000); put('ocf_b', TTM['ocf'] / 1000)
put('est_values', [round(M['ttm_rev'], 2), G_REV_MID, round(M['rev_c26'], 2), round(M['rev_c27'], 2), round(M['rev27_model'], 2)])
put('eps_est', [EPS_TTM, round((M['g_eps_lo'] + M['g_eps_hi']) / 2, 2), round(C26, 2), round(C27, 2)])
put('seagen_ttm_b', M['g_ttm']['seagen']); put('seagen_y26', sum(Y26[k] for k in GROUPS['seagen']))
put('launch_y26', sum(Y26[k] for k in GROUPS['launch']))
put('seagen_30', B['R']['seagen'][2030]); put('launch_30', B['R']['launch'][2030])

# ======================= 12. Frases del texto atadas a números =======================
if TXT:
    assert 30 < M['gap30_pct'] < 40 and M['gap31_pct'] > 40                       # "más de un tercio", "más de 40% con Vyndaqel EE.UU."
    assert M['m1'] < PRICE and M['m3'] < PRICE < M['m4'] < M['m2'] < M['m2_q3']     # orden de los métodos que cita la Sección 13
    assert 0 < M['blend_gap'] < 5 and M['postura'] == 'neutral' and M['blend_cliff_gap'] < 0 < M['blend_q3_gap']
    assert M['m1'] / PRICE < 0.40 and M['m2'] / PRICE > 1.5 and abs(M['m3_gap']) < 10 and 10 < M['indep_gap'] < 15 and M['anch_gap'] < 0
    assert M['div_cover_fcf'] > 1.0 and M['cf_hist']['2023']['cov'] < 1 and M['cf_hist']['2025']['cov'] < 1 and M['fcf30_b'] < M['div_ttm_b'] and M['payout_adj'] < 60 and M['div_yield'] > M['tsy']
    assert M['cov_drop_pct'] > 90 and M['eliq3_g'] > 20 and M['pax3_g'] < -60
    assert M['c27_g'] < 0 and M['pe_27'] < M['peer_min'] + 0.5
    assert M['pe_27'] < 10 and M['pe_ttm_adj'] < 10 and M['nd_chg_9m'] < 0 and sorted(k for k in PEERS if PEERS[k] < M['pfe_pe_fwd']) == ['BMY', 'SNY']
    assert M['nd_lev'] < 2.5 and M['m1'] < M['m1_renewal'] < PRICE and M['m1'] / PRICE < 0.40
    assert M['rev_trough_year'] in (2028, 2029, 2030)
out = 'model.json' if TXT else 'model_price.json'
json.dump(M, open(HERE / out, 'w', encoding='utf-8'), indent=1, default=float, ensure_ascii=False)
print(out, 'blend', round(BL, 2), 'gap', round(M['blend_gap'], 1), 'M1', round(M['m1'], 2), 'M2', round(M['m2'], 2), 'M3', round(M['m3'], 2), 'M4', M['m4'])
