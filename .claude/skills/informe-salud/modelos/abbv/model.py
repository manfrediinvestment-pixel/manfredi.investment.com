# Modelo de valuación ABBV (AbbVie Inc.) — todos los números derivados de informes/abbv.html salen de acá.
# Marco: informe-salud, Módulo A (pharma): suma de partes por producto hasta la LOE + rNPV del pipeline (15%),
# comparables P/E forward contra 13 pharmas (25%), reversión al P/E propio (35%), consenso (25%).
# Fuentes: 8-K del 30-oct-2026 (comunicado del 3T 2026), 10-Q del 3T 2026 (3-nov-2026), 10-K 2025 (20-feb-2026),
# comunicados de resultados 2020-2026 (8-K, Exhibit 99.1), 10-K 2019, 2022 y 2024 (historia de Humira), SEC XBRL
# companyfacts, FDA Orange Book (archivo de datos bajado el 22-nov-2026), research común de defensivos
# (.claude/skills/_compartido/defensivos_nov26.json: precios al 20-nov-2026, consenso S&P Global, WACC común, pares,
# tasas BIO, IRA). Precio de corte: cierre del 20-nov-2026.
import json, os, copy, statistics as st, datetime
from pathlib import Path
import numpy as np
from sotp import run, YEARS

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
J = json.load(open(ROOT / '.claude/skills/_compartido/defensivos_nov26.json', encoding='utf-8'))
TXT = 'ABBV_PRICE' not in os.environ
M = {}
def put(k, v): M[k] = v; return v

# ======================= 1. Trimestres (comunicados de resultados, US$ millones) =======================
Q = put('q_lab', ['1T25', '2T25', '3T25', '4T25', '1T26', '2T26', '3T26'])
REVQ = put('rev_q', [13343, 15423, 15776, 16618, 15002, 16990, 17404])
COGSQ = [4002, 4346, 5304, 4552, 4218, 4291, 4285]
SGAQ = [3293, 3253, 3569, 3895, 3578, 3632, 4087]
RDQ = [2067, 2131, 2319, 2579, 2472, 2344, 2567]
IPRDQ = [248, 823, 2680, 1265, 744, 291, 216]
EPSQ = put('eps_q', [0.72, 0.52, 0.10, 1.02, 0.39, 2.03, 2.37])
EPSAQ = put('epsa_q', [2.46, 2.97, 1.86, 2.71, 2.65, 3.65, 3.82])
# controles contra el 10-K 2025 y el 10-Q del 3T 2026
assert sum(REVQ[:4]) == 61160 and sum(REVQ[4:]) == 49396
assert sum(COGSQ[:4]) == 18204 and sum(COGSQ[4:]) == 12794 and sum(SGAQ[:4]) == 14010 and sum(SGAQ[4:]) == 11297
assert sum(RDQ[:4]) == 9096 and sum(RDQ[4:]) == 7383 and sum(IPRDQ[:4]) == 5016 and sum(IPRDQ[4:]) == 1251
assert abs(sum(EPSQ[4:]) - 4.79) < 1e-9 and abs(sum(EPSAQ[:4]) - 10.00) < 1e-9
put('gm_q', [round((1 - c / r) * 100, 1) for c, r in zip(COGSQ, REVQ)])
put('rd_q_pct', [round(d / r * 100, 1) for d, r in zip(RDQ, REVQ)])
assert M['gm_q'][-1] == 75.4                               # comunicado: margen bruto GAAP 75.4%
put('gm3_adj', 85.1); put('om3', 36.0); put('om3_adj', 48.7); put('sga3_adj', 21.2); put('rd3_adj', 13.9); put('tax3_adj', 13.6)
# Tercer trimestre
put('rev3', 17404); put('rev3_ly', 15776); put('rev3_g', (17404 / 15776 - 1) * 100); put('rev3_gop', 10.5)
put('cogs3', 4285); put('cogs3_ly', 5304); put('sga3', 4087); put('sga3_ly', 3569); put('rd3', 2567); put('rd3_ly', 2319)
put('iprd3', 216); put('iprd3_ly', 2680); put('oi3', 6267); put('oi3_ly', 1904); put('ni3', 4218); put('ni3_ly', 186)
put('eps3', 2.37); put('eps3_ly', 0.10); put('epsa3', 3.82); put('epsa3_ly', 1.86); put('iprd_eps3', 0.11); put('iprd_eps3_ly', 1.50)
for k in ('cogs3', 'sga3', 'rd3', 'oi3', 'epsa3'):
    put(k + '_g', (M[k] / M[k + '_ly'] - 1) * 100)
put('gm3', (1 - 4285 / 17404) * 100); put('gm3_ly', (1 - 5304 / 15776) * 100)
put('epsa3_x', 3.82 + 0.11); put('epsa3_ly_x', 1.86 + 1.50); put('epsa3_x_g', (M['epsa3_x'] / M['epsa3_ly_x'] - 1) * 100)
put('div_q', 1.73); put('div_q_new', 1.82); put('div_raise', (1.82 / 1.73 - 1) * 100); put('div_since13', 355)

# ======================= 2. Puente GAAP → ajustado (comunicados; por acción, después de impuestos) =======================
BR = put('bridge_q', {
    '3T25': dict(gaap=0.10, amort=0.89, imp=0.39, acq=0.12, cont=0.43, oth=-0.07, adj=1.86, iprd=1.50),
    '4T25': dict(gaap=1.02, amort=0.85, imp=0.00, acq=0.00, cont=0.77, oth=0.07, adj=2.71, iprd=0.71),
    '1T26': dict(gaap=0.39, amort=0.85, imp=0.00, acq=0.00, cont=1.31, oth=0.10, adj=2.65, iprd=0.41),
    '2T26': dict(gaap=2.03, amort=0.81, imp=0.00, acq=0.00, cont=0.83, oth=-0.02, adj=3.65, iprd=0.17),
    '3T26': dict(gaap=2.37, amort=0.79, imp=0.00, acq=0.22, cont=0.46, oth=-0.02, adj=3.82, iprd=0.11)})
for k, b in BR.items():
    assert abs(b['gaap'] + b['amort'] + b['imp'] + b['acq'] + b['cont'] + b['oth'] - b['adj']) < 0.005, k
TT = ['4T25', '1T26', '2T26', '3T26']
put('bridge_ttm', {f: sum(BR[q][f] for q in TT) for f in ('gaap', 'amort', 'imp', 'acq', 'cont', 'oth', 'adj', 'iprd')})
BT = M['bridge_ttm']
assert abs(BT['adj'] - sum(EPSAQ[-4:])) < 1e-9
# Antes de impuestos (US$ millones), mismos comunicados
PT = put('bridge_pt', {'4T25': dict(gaap=2668, amort=1784, acq=0, cont=1406, oth=51, adj=5909),
                       '1T26': dict(gaap=1039, amort=1748, acq=0, cont=2387, oth=395, adj=5569),
                       '2T26': dict(gaap=4278, amort=1689, acq=0, cont=1518, oth=128, adj=7613),
                       '3T26': dict(gaap=4829, amort=1669, acq=408, cont=829, oth=131, adj=7866)})
for k, b in PT.items(): assert b['gaap'] + b['amort'] + b['acq'] + b['cont'] + b['oth'] == b['adj'], k
put('bridge_pt_ttm', {f: sum(PT[q][f] for q in PT) for f in ('gaap', 'amort', 'acq', 'cont', 'oth', 'adj')})
put('ttm_eps_gaap', BT['gaap']); put('ttm_eps_adj', BT['adj']); put('ttm_iprd_eps', BT['iprd'])
put('ttm_adj_x_iprd', BT['adj'] + BT['iprd'])
put('amort_9m', 5106); put('cont_9m', 4734); put('amort_fy25', 7377); put('cont_fy25', 6.5)
put('adj_gap_ttm', BT['adj'] / BT['gaap'])

# ======================= 3. Ventas por producto (comunicados, US$ millones) =======================
KEYS = ['sky', 'rin', 'hum', 'vra', 'btxt', 'ubr', 'qul', 'vya', 'ven', 'imb', 'ela', 'epk', 'btxc', 'juv', 'aoth', 'mav', 'cre', 'lin']
P3 = dict(sky=5776, rin=2706, hum=683, vra=1068, btxt=1080, ubr=449, qul=398, vya=286, ven=803, imb=522, ela=224, epk=108,
          btxc=669, juv=222, aoth=285, mav=265, cre=361, lin=339)
P3LY = dict(sky=4708, rin=2184, hum=993, vra=934, btxt=985, ubr=354, qul=288, vya=138, ven=726, imb=706, ela=170, epk=69,
            btxc=637, juv=253, aoth=303, mav=312, cre=368, lin=326)
P9 = dict(sky=15764, rin=7350, hum=2127, vra=3044, btxt=3131, ubr=1180, qul=1044, vya=743, ven=2344, imb=1610, ela=633, epk=294,
          btxc=2065, juv=699, aoth=880, mav=911, cre=1067, lin=917)
P4Q25 = dict(sky=5006, rin=2374, hum=1246, vra=1022, btxt=990, ubr=339, qul=288, vya=183, ven=710, imb=671, ela=182, epk=81,
             btxc=717, juv=249, aoth=320, mav=324, cre=385, lin=175)
P3['rest'] = 17404 - sum(P3.values()); P3LY['rest'] = 15776 - sum(P3LY.values())
P9['rest'] = 49396 - sum(P9.values()); P4Q25['rest'] = 16618 - sum(P4Q25.values())
PTTM = {k: (P4Q25[k] + P9[k]) / 1000 for k in P3}
assert abs(sum(PTTM.values()) - (16618 + 49396) / 1000) < 1e-9
put('p3', P3); put('p3ly', P3LY); put('p9', P9); put('prod_ttm', PTTM)
put('p3_g', {k: (P3[k] / P3LY[k] - 1) * 100 for k in P3})
TTMREV = put('ttm_rev', (16618 + 49396) / 1000)
put('sky_rin3', 5776 + 2706); put('sky_rin3_share', (5776 + 2706) / 17404 * 100); put('sky_rin3_g', ((5776 + 2706) / (4708 + 2184) - 1) * 100)
put('sky_rin_ttm', PTTM['sky'] + PTTM['rin']); put('sky_rin_ttm_share', M['sky_rin_ttm'] / TTMREV * 100)
put('imm3', 9165); put('imm3_g', 16.3); put('neu3', 3389); put('neu3_g', 19.4); put('onc3', 1696); put('onc3_g', 0.8); put('aes3', 1176); put('aes3_g', -1.4)
put('aes3_gop', -1.8); put('btxc3_us_g', 2.4); put('btxc3_int_g', 8.6); put('juv3_us_g', -6.3); put('juv3_int_g', -15.4)
put('aes9_g', 2.0); put('aes_fy25', 4860); put('aes_fy25_g', -6.1)
put('mig3', 449 + 398); put('mig3_g', ((449 + 398) / (354 + 288) - 1) * 100)
put('imb9_us', 1009); put('imb9_us_ly', 1579); put('imb9_us_g', (1009 / 1579 - 1) * 100); put('imb3_us_g', -33.0)
put('us3', 13333); put('us3_share', 13333 / 17404 * 100); put('wholesalers', 82)
# Por área TTM y mezcla para el gráfico
AREA = dict(imm=['sky', 'rin', 'hum'], neu=['vra', 'btxt', 'ubr', 'qul', 'vya'], onc=['ven', 'imb', 'ela', 'epk'],
            aes=['btxc', 'juv', 'aoth'], oth=['mav', 'cre', 'lin', 'rest'])
put('area_ttm', {a: sum(PTTM[k] for k in ks) for a, ks in AREA.items()})
put('area_share', {a: v / TTMREV * 100 for a, v in M['area_ttm'].items()})
LBL = dict(sky='Skyrizi', rin='Rinvoq', hum='Humira', vra='Vraylar', btxt='Botox terapéutico', ubr='Ubrelvy', qul='Qulipta',
           vya='Vyalev', ven='Venclexta', imb='Imbruvica', ela='Elahere', epk='Epkinly', btxc='Botox Cosmetic', juv='Juvederm',
           aoth='Otros estética', mav='Mavyret', cre='Creon', lin='Linzess', rest='Resto')
order = sorted([k for k in PTTM if k != 'rest'], key=lambda k: -PTTM[k])[:12]
put('mix_labels', [LBL[k] for k in order]); put('mix_values', [round(PTTM[k], 2) for k in order])

# ======================= 4. Historia (10-K y comunicados) =======================
put('hist', [25.64, 28.22, 32.75, 33.27, 45.80, 56.20, 58.05, 54.32, 56.33, 61.16, round(TTMREV, 2)])
HUM = put('hum_hist', {'y': ['2017', '2018', '2019', '2020', '2021', '2022', '2023', '2024', '2025'],
                       'us': [12361, 13685, 14864, 16112, 17330, 18619, 12160, 7142, 3062],
                       'int': [6066, 6251, 4305, 3720, 3364, 2618, 2244, 1851, 1478]})
put('hum_us_b', [round(v / 1000, 2) for v in HUM['us']]); put('hum_int_b', [round(v / 1000, 2) for v in HUM['int']])
put('hum_peak', 21237); put('hum_peak_us', 18619)
HUM_US26 = put('hum_us26e', 1154 + 372)                    # 9M26 + 4T26 supuesto = 3T26 (comunicado, EE.UU. $372M)
US_CURVE = put('us_curve', [1 - 12160 / 18619, 1 - 7142 / 18619, 1 - 3062 / 18619, 1 - HUM_US26 / 18619])
INT_CURVE = put('int_curve', [1 - v / 6251 for v in [4305, 3720, 3364, 2618, 2244, 1851, 1478]])
put('hum_ttm', PTTM['hum']); put('hum_ttm_vs_peak', (1 - PTTM['hum'] * 1000 / 21237) * 100)
SR = put('sky_rin_hist', {'y': ['2020', '2021', '2022', '2023', '2024', '2025'], 'sky': [1.590, 2.939, 5.165, 7.763, 11.718, 17.562],
                          'rin': [0.731, 1.651, 2.522, 3.969, 5.971, 8.304]})
put('sky_rin_25', 17.562 + 8.304); put('hum_25', 4.540)
put('sky_q', [3425, 4423, 4708, 5006, 4483, 5505, 5776]); put('rin_q', [1718, 2028, 2184, 2374, 2119, 2525, 2706])
put('hum_q', [1121, 1180, 993, 1246, 688, 756, 683])
put('btxc_q', [556, 692, 637, 717, 668, 728, 669]); put('juv_q', [231, 260, 253, 249, 232, 245, 222])
assert M['sky_q'][-1] == P3['sky'] and M['rin_q'][4:] and sum(M['sky_q'][4:]) == P9['sky'] and sum(M['rin_q'][4:]) == P9['rin']
assert sum(M['hum_q'][4:]) == P9['hum'] and sum(M['btxc_q'][4:]) == P9['btxc'] and sum(M['juv_q'][4:]) == P9['juv']

# ======================= 5. Guía 2026 (comunicado del 30-oct-2026 y llamada de resultados) =======================
put('g_eps_lo', 13.95); put('g_eps_hi', 13.99); put('g_eps_lo_prev', 13.76); put('g_eps_hi_prev', 13.96)
put('g_eps_feb_lo', 14.37); put('g_eps_feb_hi', 14.57); put('g_iprd_ytd', 0.69); put('g_apogee', 0.14); put('g_apogee27', 0.46)
put('g_eps_mid', (13.95 + 13.99) / 2)
G26 = put('g26', dict(rev=67.8, sky=21.8, rin=10.3, imm=34.9, onc=6.6, ven=3.1, imb=2.1))   # llamada del 3T (prensa)
put('g26_feb_rev', 67.0); put('g_q4_rev', 18.4); put('g_q4_eps_lo', 3.83); put('g_q4_eps_hi', 3.87)
put('g26_sr', G26['sky'] + G26['rin']); put('g26_rev_g', (G26['rev'] / 61.16 - 1) * 100)
put('sr_guide27', 31.0); put('sr_guide27_sky', 20.0); put('sr_guide27_rin', 11.0)
REV9M = 49396
Q4IMP = put('q4_implied', G26['rev'] * 1000 - REV9M)
assert abs(Q4IMP / 1000 - M['g_q4_rev']) < 0.05

# ======================= 6. Doce meses (10-K 2025 − 9M25 del 10-Q 2025 + 9M26), balance y caja =======================
FY25 = dict(ocf=19030, capex=1214, div=11657, buy=980, cont=2865, dep=762)
N25 = dict(ocf=13812, capex=885, div=8746, buy=977, cont=2184, dep=559)
N26 = dict(ocf=14871, capex=888, div=9227, buy=1503, cont=2717, dep=574)
TTM = {k: FY25[k] - N25[k] + N26[k] for k in FY25}
TTM.update(rev=66014, cogs=4552 + 12794, sga=3895 + 11297, rd=2579 + 7383, iprd=1265 + 1251, intn=655 + 2024)
assert TTM['rev'] == sum(REVQ[-4:]) and TTM['rd'] == sum(RDQ[-4:]) and TTM['iprd'] == sum(IPRDQ[-4:])
put('ttm', TTM)
put('ttm_gm', (1 - TTM['cogs'] / TTM['rev']) * 100); put('ttm_rd_pct', TTM['rd'] / TTM['rev'] * 100)
put('ttm_fcf', TTM['ocf'] - TTM['capex']); put('ttm_fcfm', M['ttm_fcf'] / TTM['rev'] * 100); put('ttm_ocfm', TTM['ocf'] / TTM['rev'] * 100)
put('ttm_capex_pct', TTM['capex'] / TTM['rev'] * 100)
put('payout_fcf', TTM['div'] / M['ttm_fcf'] * 100); put('shr_fcf', (TTM['div'] + TTM['buy']) / M['ttm_fcf'] * 100)
put('ttm_cont_pct', TTM['cont'] / TTM['rev'] * 100)
PT_ADJ = M['bridge_pt_ttm']['adj']
INT_ADJ = put('int_adj_ttm', 655 + 2012)                   # interés neto ajustado: 4T25 (sin ajustes) + 9M26 ajustado
EBITDA = put('ebitda', (PT_ADJ + INT_ADJ + TTM['dep']) / 1000)
BS = put('bs', {'s26': dict(cash=10774, std=0, cltd=8673, ltd=72230, gw=37800, intg=56652, eq=-4583, ta=147680, cont=27312),
                'd25': dict(cash=5229, std=2499, cltd=6056, ltd=58941, gw=35640, intg=52641, eq=-3270, ta=133960, cont=25374),
                'd24': dict(cash=5524, std=0, cltd=6804, ltd=60340, gw=None, intg=None, eq=3325, ta=None, cont=None)})
for k, b in BS.items(): b['debt'] = b['std'] + b['cltd'] + b['ltd']; b['nd'] = b['debt'] - b['cash']
DEBT = put('debt', BS['s26']['debt'] / 1000); ND = put('net_debt', BS['s26']['nd'] / 1000)
CONT = put('contingent', BS['s26']['cont'] / 1000)
put('nd_ebitda', ND / EBITDA); put('nd_cont_ebitda', (ND + CONT) / EBITDA)
put('nd_chg_9m', (BS['s26']['nd'] - BS['d25']['nd']) / 1000)
put('apogee_paid', 10.6); put('apogee_eq', 10.9); put('apogee_iprd', 9.1); put('apogee_gw', 2.284); put('apogee_px', 135.11)
put('notes_26', 18.0); put('notes_mar', 8.0); put('notes_aug', 10.0); put('repaid_26', 2.0)
put('cont_rate', 5.4); put('cont_pay9', 2796); put('cont_end_sky', 2037)
# Calendario de vencimientos de capital (10-K 2025, Nota 10) + emisiones de 2026 (10-Q, Nota 9) − repago de mayo-2026
MAT = {'2026': 6000 - 2000, '2027': 5130, '2028': 4466 + 500 + 1000 + 750 + 1500, '2029': 8645, '2030': 1000 + 1250,
       '2031+': 39262 + (1500 + 1250 + 1500 + 1000 + 1500 + 500) + (1250 + 1250 + 1500 + 1250 + 500)}
put('mat', MAT); put('mat_tot', sum(MAT.values())); put('mat_vals', [round(v / 1000, 2) for v in MAT.values()])
put('mat_book', (8257 + 72150) / 1000)
assert abs(M['mat_tot'] / 1000 - M['mat_book']) < 0.5        # principal vs valor de libros (diferencias por euros y descuentos)
put('mat_27_28', (MAT['2027'] + MAT['2028']) / 1000)
put('rev_credit', 8.0); put('rating_moodys', 'A2'); put('rating_sp', 'A-')
# Capacidad de compra: hasta 3.0x deuda neta / EBITDA ajustado (estimación propia)
put('firepower', 3.0 * EBITDA - ND)
SH_OUT = put('shares_out', (1844582836 - 77073558) / 1e6); SH = put('shares_dil', 1772.0)
put('buy_9m_sh', 5); put('buy_9m_usd', 1.1)
put('cash_ocf', [22.78, 24.94, 22.84, 18.81, 19.03, round(TTM['ocf'] / 1000, 2)])
put('cash_capex', [0.79, 0.70, 0.78, 0.97, 1.21, round(TTM['capex'] / 1000, 2)])
put('cash_div', [9.26, 10.04, 10.54, 11.03, 11.66, round(TTM['div'] / 1000, 2)])
put('cash_fcf', [round(a - b, 2) for a, b in zip(M['cash_ocf'], M['cash_capex'])])
put('dps_hist', {'y': ['2013', '2015', '2017', '2019', '2021', '2023', '2025', '2027e'], 'v': [1.60, 2.04, 2.56, 4.28, 5.20, 5.92, 6.56, 7.28]})

# ======================= 7. Mercado, consenso y costo de capital (JSON común) =======================
A = J['todos_los_tickers']['ABBV']; CO = J['consenso_tres']['tickers']['ABBV']; TD = J['pharma']['tasa_descuento_comun']
PRICE = put('price', float(os.environ.get('ABBV_PRICE', A['cierre_20nov'])))
put('hi52', A['max_52s']); put('lo52', A['min_52s'])
C26 = put('c26', CO['eps_ajustado_fy_actual']); C27 = put('c27', CO['eps_ajustado_fy_siguiente'])
put('rev_c26', CO['ventas_fy_actual'] / 1e9); put('rev_c27', CO['ventas_fy_siguiente'] / 1e9)
put('rev_c27_g', (M['rev_c27'] / M['rev_c26'] - 1) * 100); put('c27_g', (C27 / C26 - 1) * 100)
EPS9M = put('eps9m_adj', 10.12)
NTM = put('eps_ntm', (C26 - EPS9M) + 0.75 * C27); put('q4_eps_impl', C26 - EPS9M)
put('pe_27', PRICE / C27); put('pe_ntm', PRICE / NTM); put('pe_ttm_adj', PRICE / BT['adj']); put('pe_ttm_gaap', PRICE / BT['gaap'])
put('div_yield', 4 * M['div_q_new'] / PRICE * 100); put('div_yield_cur', 4 * M['div_q'] / PRICE * 100)
put('mcap', PRICE * SH_OUT / 1000)
WACC = put('wacc', TD['wacc_pct']); put('wacc_bear', TD['wacc_bear_pct']); put('wacc_bull', TD['wacc_bull_pct'])
put('rf', TD['rf_pct']); put('erp', TD['erp_pct']); put('beta_peers', TD['beta_media_cruda_pares']); put('beta_blume', TD['beta_blume'])
KE = put('ke', TD['ke_pct']); put('kd', TD['kd_pre_impuestos_pct']); put('kd_at', TD['kd_pct']); put('tax_w', TD['tasa_impositiva_pct'])
put('dv_peers', TD['d_sobre_v_mediana_pares'] * 100); put('grid_w', TD['grilla_sensibilidad_pct'])
# WACC propia (solo referencia: usa la beta y el precio de ABBV; no entra al Método 1)
BOWN = put('beta_own', A['multiplos']['beta_5y']); put('beta_own_adj', 0.67 * BOWN + 0.33)
put('ke_own', M['rf'] + M['beta_own_adj'] * M['erp'])
WD_OWN = put('wd_own', DEBT / (DEBT + M['mcap']) * 100)
put('wacc_own', (1 - WD_OWN / 100) * M['ke_own'] + WD_OWN / 100 * M['kd_at'])
put('sp_pe', J['mercado']['sp500']['pe_fwd_ajustado_20nov']); put('hc_pe', J['mercado']['sectores_pe_fwd']['health_care']['pe_ajustado_20nov'])
put('hc_pe_10a', J['mercado']['sectores_pe_fwd']['health_care']['prom_10a'])

# ======================= 8. Método 1 — suma de partes por producto + rNPV =======================
TAX = put('tax', 14.5)                                      # tasa ajustada 9M26 (comunicado)
CM0 = put('cm0', (TTM['ocf'] + TTM['cont'] + TTM['intn'] * (1 - TAX / 100) + TTM['rd'] * (1 - TAX / 100)) / TTM['rev'] * 100)
put('cm0_parts', dict(ocf=TTM['ocf'] / TTM['rev'] * 100, cont=TTM['cont'] / TTM['rev'] * 100,
                      intn=TTM['intn'] * (1 - TAX / 100) / TTM['rev'] * 100, rd=TTM['rd'] * (1 - TAX / 100) / TTM['rev'] * 100))
CX0 = TTM['capex'] / TTM['rev']; RD0 = TTM['rd'] / TTM['rev']
# Nivel del 4T26: productos con guía (Skyrizi, Rinvoq, Imbruvica, Venclexta) = guía − 9M; el resto, mezcla del 3T escalada
GQ4 = dict(sky=G26['sky'] * 1000 - P9['sky'], rin=G26['rin'] * 1000 - P9['rin'], imb=G26['imb'] * 1000 - P9['imb'], ven=G26['ven'] * 1000 - P9['ven'])
sc = (Q4IMP - sum(GQ4.values())) / (17404 - sum(P3[k] for k in GQ4)); put('q4_scale', sc)
Q4 = {k: (GQ4[k] if k in GQ4 else P3[k] * sc) for k in P3}
assert abs(sum(Q4.values()) - Q4IMP) < 1e-6
put('q4', {k: v / 1000 for k, v in Q4.items()})
CAL26 = {k: (P9[k] + Q4[k]) / 1000 for k in P3}                 # 2026 calendario estimado
put('cal26', CAL26)
# Curvas de erosión
BIO = [0.86 * u + 0.14 * i for u, i in zip(US_CURVE, INT_CURVE[:4])]        # Humira, ponderado con la mezcla EE.UU./resto de Skyrizi (86/14)
put('bio_curve', BIO); put('bio_curve_us', US_CURVE)
SM = put('sm_curve', [0.80, 0.90])                                         # molécula pequeña en EE.UU.: −80% / −90% (skill)
BIO_TAIL, SM_TAIL = 0.15, 0.10
US_RIN = 5094 / 7350                                         # Rinvoq: EE.UU. 9M26 / total
put('rin_us', US_RIN * 100)
IRA = put('ira', dict(rin_med=15.0, rin_cut=40.0, vra=-10.0, lin=-25.0, btx=-5.0))
put('rin_ira', -US_RIN * IRA['rin_med'] / 100 * IRA['rin_cut'] / 100 * 100)
# Activos del pipeline: fase, área BIO, pico (US$ miles de millones) y fuente
EC = J['pharma']['exito_clinico']['probabilidad_acumulada_hasta_aprobacion']
PIPE = {
    'zumi': dict(name='Zumilokibart (dermatitis atópica)', phase='Fase 3 (inicio 2S26)', area='autoinmune', idx=2, peak=5.2, launch=2029, peak_year=2035, loe=2042, src='Guggenheim (pico de $5.2 mil millones tras los datos de fase 2)'),
    'ete': dict(name='Etentamig (mieloma múltiple)', phase='Presentado (BLA oct-2026)', area='oncologia', idx=3, peak=2.0, launch=2027, peak_year=2033, loe=2040, src='Supuesto propio (la compañía habla de un pico "de varios miles de millones")'),
    'temab': dict(name='Temab-A (colorrectal, pulmón)', phase='Fase 3 (jun-2026)', area='oncologia', idx=2, peak=2.0, launch=2029, peak_year=2035, loe=2042, src='Supuesto propio (ídem)'),
    'luti': dict(name='Lutikizumab (hidradenitis supurativa)', phase='Fase 3 positiva; presentación 2S27', area='autoinmune', idx=3, peak=1.5, launch=2028, peak_year=2034, loe=2041, src='Supuesto propio'),
    'a1480': dict(name='ABBV-1480 (pulmón, primera línea)', phase='Fase 3 (sep-2026)', area='oncologia', idx=2, peak=2.0, launch=2030, peak_year=2036, loe=2043, src='Supuesto propio'),
    'a706': dict(name='ABBV-706 (pulmón de células pequeñas)', phase='Fase 3 (abr-2026)', area='oncologia', idx=2, peak=1.0, launch=2029, peak_year=2034, loe=2042, src='Supuesto propio'),
}
for k, a in PIPE.items():
    a['pos'] = EC[a['area']][a['idx']] / 100; a['curve'] = BIO; a['tail'] = BIO_TAIL
put('pipe', {k: dict({kk: vv for kk, vv in a.items() if kk not in ('curve',)}, pos_pct=a['pos'] * 100) for k, a in PIPE.items()})
put('pos_zumi', PIPE['zumi']['pos'] * 100)
JUV_PEAK = put('juvmo_peak', 1.5)

def scen(name, wacc=None, pos_zumi=None, renewal=False, late=False):
    b = {'base': 0, 'bear': 1, 'bull': 2}[name]
    gm = [1.0, 0.7, 1.2][b]          # multiplicador del crecimiento 2027-2031 de Skyrizi, Rinvoq y migraña
    def gx(d): return {y: (v * gm if v > 0 and y <= 2031 else v) for y, v in d.items()}
    sky_loe = [2033, 2033, 2035][b] if not late else 2035
    rin_loe = [2037, 2037, 2038][b] if not late else 2038
    P = {}
    P['sky'] = dict(l26=CAL26['sky'], g=gx({2027: .16, 2028: .11, 2029: .08, 2030: .05, 2031: .03, 2032: .02}), loe=sky_loe,
                    curve=(US_CURVE if name == 'bear' else BIO), tail=BIO_TAIL)
    rin_adj = [M['rin_ira'] / 100, 2 * M['rin_ira'] / 100, 0.0][b]
    P['rin'] = dict(l26=CAL26['rin'], g=gx({2027: .19, 2028: .13, 2029: .09, 2030: .06, 2031: .04, 2034: .03}), adj={2029: rin_adj},
                    loe=rin_loe, curve=[0.60, 0.85, 0.90], tail=SM_TAIL)
    P['hum'] = dict(l26=CAL26['hum'], g={2027: -.30, 2028: -.20})
    P['vra'] = dict(l26=CAL26['vra'], g={2027: .05, 2028: .03, 2029: .02}, adj={2027: IRA['vra'] / 100 * [1, 1.5, 0.7][b]}, loe=[2030, 2030, 2031][b], curve=SM, tail=SM_TAIL)
    P['btxt'] = dict(l26=CAL26['btxt'], g={2027: .08, 2028: .06, 2030: .05, 2035: .03, 2040: .02}, adj={2028: [IRA['btx'] / 100, 2 * IRA['btx'] / 100, 0.0][b]}, terminal=True)
    P['mig'] = dict(l26=CAL26['ubr'] + CAL26['qul'], g=gx({2027: .17, 2028: .12, 2029: .08, 2030: .05, 2032: .03}), loe=[2034, 2034, 2036][b], curve=SM, tail=SM_TAIL)
    P['vya'] = dict(l26=CAL26['vya'], g={2027: .30, 2028: .18, 2029: .10, 2030: .07, 2032: .04}, loe=2036, curve=SM, tail=SM_TAIL)
    P['ven'] = dict(l26=CAL26['ven'], g={2027: .07, 2028: .05, 2029: .03, 2031: .02}, loe=2032, curve=SM, tail=SM_TAIL)
    P['imb'] = dict(l26=CAL26['imb'], g={2027: -.12, 2028: -.10}, loe=[2032, 2032, 2034][b], curve=SM, tail=SM_TAIL)
    P['ela'] = dict(l26=CAL26['ela'], g={2027: .20, 2028: .15, 2029: .10, 2030: .06, 2033: .04}, loe=2035, curve=BIO, tail=BIO_TAIL)
    P['epk'] = dict(l26=CAL26['epk'], g={2027: .45, 2028: .30, 2029: .20, 2030: .12, 2032: .05}, loe=2036, curve=BIO, tail=BIO_TAIL)
    P['aes'] = dict(l26=CAL26['btxc'] + CAL26['juv'] + CAL26['aoth'], g=[{2027: .01, 2028: .03, 2030: .035, 2035: .03, 2040: .02},
                    {2027: -.02, 2028: .00, 2030: .02, 2035: .02, 2040: .01}, {2027: .03, 2028: .05, 2030: .05, 2035: .04, 2040: .025}][b], terminal=True)
    P['mav'] = dict(l26=CAL26['mav'], g={2027: -.05}, loe=2032, curve=SM, tail=SM_TAIL)
    P['cre'] = dict(l26=CAL26['cre'], g={2027: -.03})
    P['lin'] = dict(l26=CAL26['lin'], g={2027: .0}, adj={2027: IRA['lin'] / 100}, loe=2029, curve=SM, tail=SM_TAIL)
    P['rest'] = dict(l26=CAL26['rest'], g={2027: -.05})
    q4map = dict(sky=['sky'], rin=['rin'], hum=['hum'], vra=['vra'], btxt=['btxt'], mig=['ubr', 'qul'], vya=['vya'], ven=['ven'], imb=['imb'],
                 ela=['ela'], epk=['epk'], aes=['btxc', 'juv', 'aoth'], mav=['mav'], cre=['cre'], lin=['lin'], rest=['rest'])
    for k, ks in q4map.items(): P[k]['q4'] = sum(Q4[x] for x in ks) / 1000
    pk = [1.0, 0.6, 1.3][b]
    pipe = {k: dict(a, peak=a['peak'] * pk) for k, a in PIPE.items()}
    pipe['juvmo'] = dict(name='Juvmo', peak=JUV_PEAK * pk, launch=2027, peak_year=2032, loe=2035, curve=SM, tail=SM_TAIL, pos=1.0)
    cm30 = CM0 / 100 + [0.0, -0.02, 0.015][b]
    p = dict(prod=P, pipe=pipe, wacc=(wacc if wacc is not None else [WACC, M['wacc_bear'], M['wacc_bull']][b] / 100),
             cm={2026: CM0 / 100, 2030: cm30}, capex={2026: CX0, 2030: [0.025, 0.030, 0.022][b]},
             rd={2026: RD0, 2030: [0.150, 0.160, 0.145][b]}, tax=TAX / 100, net_debt=ND, contingent=CONT, shares=SH / 1000,
             plat_share=0.40, plat_year=2040, plat_g=0.02, g_noloe=0.01, pos_key='zumi', pos_override=pos_zumi,
             renewal=renewal, renew_keys=('sky', 'rin'))
    return p

# El motor proyecta desde el nivel calendario 2026 (base de los crecimientos). Para que 2026 aporte solo el 4T real
# se corrige el flujo de 2026: (4T × 4) en lugar del calendario, con el mismo peso de 0.25.
def RUN(p):
    r = run(p)
    w = p['wacc']; df26 = (1 + w) ** -0.125
    cm26, cx26 = p['cm'][2026], p['capex'][2026]
    for k, spec in p['prod'].items():
        d = (spec['q4'] * 4 - r['R'][k][2026]) * (cm26 - cx26) * 0.25 * df26
        r['C'][k] += d
        drd = -(spec['q4'] * 4 - r['R'][k][2026]) * p['rd'][2026] * (1 - p['tax']) * 0.25 * df26
        r['C']['rd'] += drd
        r['ev'] += d + drd
        r['R'][k][2026] = spec['q4'] * 4
    r['tot'][2026] = sum(r['R'][k][2026] for k in r['R'])
    r['eq'] = r['ev'] - p['net_debt'] - p['contingent']; r['fv'] = r['eq'] / p['shares']
    return r

R = {s: RUN(scen(s)) for s in ('base', 'bear', 'bull')}
B = R['base']
put('m1', B['fv']); put('m1_bear', R['bear']['fv']); put('m1_bull', R['bull']['fv'])
put('m1_ev', B['ev']); put('m1_eq', B['eq'])
CMP = B['C']
GROUP = dict(sky=['sky'], rin=['rin'], neu=['vra', 'mig', 'vya', 'pipe_juvmo'], btx_aes=['btxt', 'aes'], onc=['ven', 'imb', 'ela', 'epk'],
             oth=['hum', 'mav', 'cre', 'lin', 'rest'], pipe=['pipe_' + k for k in PIPE], noloe_tv=['noloe_tv'], platform=['platform'], rd=['rd'])
SG = {g: sum(CMP[k] for k in ks) for g, ks in GROUP.items()}
assert abs(sum(SG.values()) - B['ev']) < 1e-9
put('sotp', SG); put('sotp_ps', {k: v / SH * 1000 for k, v in SG.items()})
put('sotp_pipe', {k: CMP['pipe_' + k] for k in PIPE}); put('sotp_pipe_ps', {k: CMP['pipe_' + k] / SH * 1000 for k in PIPE})
put('nd_ps', ND / SH * 1000); put('cont_ps', CONT / SH * 1000); put('ev_ps', B['ev'] / SH * 1000)
for s in ('base', 'bear', 'bull'):
    put(f'rev27_{s}', R[s]['tot'][2027]); put(f'rev30_{s}', R[s]['tot'][2030]); put(f'rev35_{s}', R[s]['tot'][2035])
    put(f'fcfm30_{s}', R[s]['fcfm'][2030] * 100)
    put(f'plat_share_{s}', R[s]['C']['platform'] / R[s]['ev'] * 100); put(f'noloe_share_{s}', R[s]['C']['noloe_tv'] / R[s]['ev'] * 100)
put('sky_path', {str(y): B['R']['sky'][y] for y in (2027, 2030, 2032, 2033, 2034, 2035, 2036)})
put('rin_path', {str(y): B['R']['rin'][y] for y in (2027, 2030, 2036, 2037, 2038)})
put('sr_peak', max(B['R']['sky'][y] + B['R']['rin'][y] for y in YEARS))
put('sr_peak_year', max(YEARS, key=lambda y: B['R']['sky'][y] + B['R']['rin'][y]))
put('rev27_vs_cons', (B['tot'][2027] / M['rev_c27'] - 1) * 100)
put('m1_rev_path', [round(B['tot'][y], 1) for y in range(2027, 2046)]); put('m1_rev_years', [str(y) for y in range(2027, 2046)])
put('m1_sr_path', [round(B['R']['sky'][y] + B['R']['rin'][y], 1) for y in range(2027, 2046)])
put('m1_late', RUN(scen('base', late=True))['fv']); put('m1_renewal', RUN(scen('base', renewal=True))['fv'])
put('m1_renewal_gap', (M['m1_renewal'] / PRICE - 1) * 100)
pfast = scen('base'); pfast['prod']['sky']['curve'] = US_CURVE
put('m1_fast', RUN(pfast)['fv'])
pnoira = scen('base'); pnoira['prod']['rin']['adj'] = {2029: 0.0}; pnoira['prod']['btxt']['adj'] = {2028: 0.0}
put('m1_noira', RUN(pnoira)['fv'])
put('m1_ev_w', 0.25 * M['m1_bear'] + 0.45 * M['m1'] + 0.30 * M['m1_bull'])
GW = [w / 100 for w in M['grid_w']]; GP = [0.30, 0.45, PIPE['zumi']['pos'], 0.80, 1.00]
put('grid_p', [p * 100 for p in GP])
put('grid', [[RUN(scen('base', wacc=w, pos_zumi=q))['fv'] for q in GP] for w in GW])
assert abs(M['grid'][2][2] - M['m1']) < 1e-9
put('grid_min', min(min(r) for r in M['grid'])); put('grid_max', max(max(r) for r in M['grid']))
put('m1_zumi_cost', M['m1'] - M['sotp_pipe_ps']['zumi'] + M['apogee_paid'] / SH * 1000)

# ======================= 9. Método 2 — comparables (13 pharmas del JSON común, P/E forward) =======================
PE = J['pharma']['comparables']['pares']
PEERS = put('peers', {k: PE[k]['pe_fwd'] for k in PE})
assert sorted(PEERS) == sorted(TD['pares_usados']) and 'ABBV' not in PEERS and 'PFE' not in PEERS
v = sorted(PEERS.values())
put('peer_q3', float(np.percentile(v, 75))); put('peer_med', float(np.percentile(v, 50))); put('peer_max', max(v)); put('peer_min', min(v))
ES = J['pharma']['comparables']['estadisticos']
assert abs(M['peer_q3'] - ES['pe_fwd_q3']) < 1e-9 and abs(M['peer_med'] - ES['pe_fwd_mediana']) < 1e-9
put('peer_q3_name', [k for k in PEERS if PEERS[k] == M['peer_q3']][0]); put('peer_med_name', [k for k in PEERS if PEERS[k] == M['peer_med']][0])
put('peer_max_name', [k for k in PEERS if PEERS[k] == M['peer_max']][0])
# Regresión P/E forward vs crecimiento esperado (dos definiciones)
def r2(xs, ys):
    xs, ys = np.array(xs), np.array(ys); b1, b0 = np.polyfit(xs, ys, 1); yh = b0 + b1 * xs
    return 1 - ((ys - yh) ** 2).sum() / ((ys - ys.mean()) ** 2).sum(), b1
# (a) crecimiento implícito en el PEG de stockanalysis (g = P/E ÷ PEG), solo pares con PEG
ga = {k: PE[k]['pe_fwd'] / PE[k]['peg'] for k in PE if PE[k].get('peg')}
# (b) crecimiento del EPS de consenso 2027 vs 2026, sin MRK y GILD (EPS 2026 deprimido por IPR&D, nota del JSON)
gb = {k: (PE[k]['eps_fy27'] / PE[k]['eps_fy26'] - 1) * 100 for k in PE if k not in ('MRK', 'GILD') and PE[k]['eps_fy26'] > 0}
REG = {}
for nm, gg in (('peg', ga), ('eps', gb)):
    ks = list(gg); r_all, s_all = r2([gg[k] for k in ks], [PEERS[k] for k in ks])
    ext = max(ks, key=lambda k: gg[k]); ks2 = [k for k in ks if k != ext]
    r_x, s_x = r2([gg[k] for k in ks2], [PEERS[k] for k in ks2])
    REG[nm] = dict(n=len(ks), r2=r_all, slope=s_all, ext=ext, n2=len(ks2), r2x=r_x, slopex=s_x)
put('reg', REG); put('reg_g', {'peg': ga, 'eps': gb})
REG_OK = max(REG['peg']['r2'], REG['eps']['r2'], REG['peg']['r2x'], REG['eps']['r2x']) >= 0.5
put('reg_ok', REG_OK)
assert not REG_OK                                         # el texto dice que la regresión no se sostiene
M2 = put('m2', M['peer_q3'] * C27 / (1 + KE / 100))
put('m2_lo', M['peer_med'] * NTM); put('m2_hi', M['peer_max'] * C27 / (1 + KE / 100))
pv = sorted(x for k, x in PEERS.items() if k != 'LLY'); put('peer_q3_xlly', float(np.percentile(pv, 75)))
put('m2_xlly', M['peer_q3_xlly'] * C27 / (1 + KE / 100))
put('m2_hc', M['hc_pe'] * NTM)
put('abbv_pe_fwd_sa', A['multiplos']['pe_fwd'])
put('prem_med', (M['abbv_pe_fwd_sa'] / M['peer_med'] - 1) * 100); put('prem_q3', (M['abbv_pe_fwd_sa'] / M['peer_q3'] - 1) * 100)
COMPS_ORDER = sorted(PEERS, key=lambda k: -PEERS[k])
put('comps_labels', COMPS_ORDER + ['ABBV (ref.)']); put('comps_values', [round(PEERS[k], 2) for k in COMPS_ORDER] + [round(M['abbv_pe_fwd_sa'], 2)])
put('peer_rows', [dict(t=k, pe=PE[k]['pe_fwd'], pe27=PE[k]['pe_fy27'], peg=PE[k]['peg'], eve=PE[k]['ev_ebitda'], dy=PE[k]['div_yield_pct'],
                       nde=PE[k]['deuda_ebitda']) for k in COMPS_ORDER])

# ======================= 10. Método 3 — reversión al P/E propio (EPS ajustado TTM tal como lo reporta ABBV) =======================
YH = ROOT / '.claude/skills/_compartido/defensivos_nov26/yh'
mo = json.load(open(YH / 'ABBV.mo.json'))['chart']['result'][0]
MC = {}
for t, c in zip(mo['timestamp'], mo['indicators']['quote'][0]['close']):
    if c: d = datetime.datetime.fromtimestamp(t, datetime.UTC).date(); MC[(d.year, d.month)] = c
EPSA = {(2023, 3): 2.46, (2023, 6): 2.91, (2023, 9): 2.95, (2023, 12): 2.79, (2024, 3): 2.31, (2024, 6): 2.65, (2024, 9): 3.00,
        (2024, 12): 2.16, (2025, 3): 2.46, (2025, 6): 2.97, (2025, 9): 1.86, (2025, 12): 2.71, (2026, 3): 2.65, (2026, 6): 3.65, (2026, 9): 3.82}
QE = sorted(EPSA)
MES = {3: 'mar', 6: 'jun', 9: 'sep', 12: 'dic'}; LAST = {3: 31, 6: 30, 9: 30, 12: 31}
ROWS = []
for i, q in enumerate(QE):
    if i < 3: continue
    ttm = sum(EPSA[x] for x in QE[i - 3:i + 1])
    ROWS.append(dict(d=f"{LAST[q[1]]}-{MES[q[1]]}-{q[0]}", px=MC[q], eps=round(ttm, 2), pe=MC[q] / ttm))
assert abs(ROWS[-1]['eps'] - BT['adj']) < 1e-9 and len(ROWS) == 12
put('rev_rows', ROWS)
put('rev_pe', st.mean(r['pe'] for r in ROWS)); M3 = put('m3', M['rev_pe'] * BT['adj'])
put('m3_lo', min(r['pe'] for r in ROWS) * BT['adj']); put('m3_hi', max(r['pe'] for r in ROWS) * BT['adj'])
put('rev_pe_min', min(r['pe'] for r in ROWS)); put('rev_pe_max', max(r['pe'] for r in ROWS))
# Alternativa: ventana previa a la LOE de Humira en EE.UU. (cierres de fin de año 2020-2022 sobre EPS ajustado anual)
PRE = [dict(d='31-dic-2020', px=MC[(2020, 12)], eps=10.56), dict(d='31-dic-2021', px=MC[(2021, 12)], eps=12.70), dict(d='31-dic-2022', px=MC[(2022, 12)], eps=13.77)]
for r in PRE: r['pe'] = r['px'] / r['eps']
put('pre_rows', PRE); put('pre_pe', st.mean(r['pe'] for r in PRE)); put('m3_pre', M['pre_pe'] * BT['adj'])
# Alternativa 2: EPS sin la IPR&D adquirida (no entra: ABBV compra pipeline todos los años)
put('m3_xiprd', M['rev_pe'] * M['ttm_adj_x_iprd'])
put('iprd_hist', {'2023': 778, '2024': 2757, '2025': 5016, 'ttm': TTM['iprd']})
put('m3_pe_now', PRICE / BT['adj'])
put('humira_gap_now', PTTM['hum'] / TTMREV * 100); put('hum_share_22', 21237 / 58054 * 100)

# ======================= 11. Método 4 — consenso =======================
M4 = put('m4', CO['pt_prom']); put('m4_lo', CO['pt_min']); put('m4_hi', CO['pt_max']); put('m4_n', CO['n_analistas']); put('m4_rec', CO['recomendacion'])

# ======================= 12. Blend =======================
W = {'m1': 0.15, 'm2': 0.25, 'm3': 0.35, 'm4': 0.25}
for k, w in W.items(): put(k + '_ap', M[k] * w); put(k + '_gap', (M[k] / PRICE - 1) * 100)
BL = put('blend', sum(M[k] * w for k, w in W.items())); put('blend_gap', (BL / PRICE - 1) * 100)
put('indep', (0.15 * M['m1'] + 0.25 * M['m2']) / 0.40); put('anch', (0.35 * M['m3'] + 0.25 * M['m4']) / 0.60)
put('indep_gap', (M['indep'] / PRICE - 1) * 100); put('anch_gap', (M['anch'] / PRICE - 1) * 100)
put('blend_xcons', (0.15 * M['m1'] + 0.25 * M['m2'] + 0.35 * M['m3']) / 0.75); put('blend_xcons_gap', (M['blend_xcons'] / PRICE - 1) * 100)
put('blend_pre', BL + 0.35 * (M['m3_pre'] - M3)); put('blend_pre_gap', (M['blend_pre'] / PRICE - 1) * 100)
put('blend_xlly', BL + 0.25 * (M['m2_xlly'] - M2)); put('blend_xlly_gap', (M['blend_xlly'] / PRICE - 1) * 100)
put('blend_m1ren', BL + 0.15 * (M['m1_renewal'] - M['m1'])); put('blend_m1ren_gap', (M['blend_m1ren'] / PRICE - 1) * 100)
put('ranges', [[M['m1_bear'], M['m1_bull']], [M['m2_lo'], M['m2_hi']], [M['m3_lo'], M['m3_hi']], [M['m4_lo'], M['m4_hi']]])
POST = put('postura', 'Neutral, con sesgo cauteloso')
put('m1_frac', M['m1'] / PRICE * 100)
SPK = sorted(MC)[-7:]; put('spark', [round(MC[k], 2) for k in SPK]); put('spark_months', [f'{k[0]}-{k[1]:02d}' for k in SPK])
assert abs(M['spark'][-1] - PRICE) < 0.01 or not TXT

# ======================= 13. Anti-circularidad: mismo modelo con el precio de ABBV 25% más alto =======================
if TXT:
    import subprocess, sys
    subprocess.run([sys.executable, __file__], env=dict(os.environ, ABBV_PRICE=str(PRICE * 1.25)), capture_output=True, text=True, check=True, cwd=HERE)
    J2 = json.load(open(HERE / 'model_price.json', encoding='utf-8'))
    for k in ('m1', 'm2', 'm3', 'm4'): put('anti_' + k, J2[k] - M[k])
    put('anti_blend', J2['blend'] - BL); put('anti_wacc_own', J2['wacc_own'] - M['wacc_own'])
    assert M['anti_m1'] == 0 and M['anti_m2'] == 0 and M['anti_m3'] == 0 and M['anti_m4'] == 0
    os.remove(HERE / 'model_price.json')

# ======================= 14. Cuadro PFE vs. ABBV vs. LLY vs. JNJ (dict `cmp`, mismas claves que el informe de PFE) =======================
LOE30 = ['hum', 'vra', 'lin', 'imb', 'btxt']                # LOE o precio negociado de Medicare antes de 2031
put('loe30_ttm', sum(PTTM[k] for k in LOE30)); put('loe30_pct', M['loe30_ttm'] / TTMREV * 100)
LOEV = [('Linzess (2029)', PTTM['lin']), ('Vraylar (2029)', PTTM['vra']), ('Imbruvica (2032)', PTTM['imb']), ('Venclexta (2032)', PTTM['ven']),
        ('Mavyret (2032)', PTTM['mav']), ('Skyrizi (2033)', PTTM['sky']), ('Ubrelvy (2033)', PTTM['ubr']), ('Qulipta (2035)', PTTM['qul']),
        ('Rinvoq (2037)', PTTM['rin'])]
put('loe_labels', [a for a, b in LOEV]); put('loe_values', [round(b, 2) for a, b in LOEV])
put('sr_loe_share', (PTTM['sky'] + PTTM['rin']) / TTMREV * 100)
CMPK = ['ticker', 'precio', 'fair_value', 'gap_pct', 'm1_sotp', 'm2_comp', 'm3_rev', 'm4_cons', 'indep', 'anclados', 'pe_fy27',
        'div_yield_pct', 'payout_fcf_pct', 'nd_ebitda', 'rd_ventas_pct', 'margen_bruto_pct', 'ventas_riesgo_loe_2030_pct',
        'crec_eps_fy27_pct', 'wacc_pct', 'postura']
cmp = dict(ticker='ABBV', precio=PRICE, fair_value=BL, gap_pct=M['blend_gap'], m1_sotp=M['m1'], m2_comp=M2, m3_rev=M3, m4_cons=M4,
           indep=M['indep'], anclados=M['anch'], pe_fy27=M['pe_27'], div_yield_pct=M['div_yield'], payout_fcf_pct=M['payout_fcf'],
           nd_ebitda=M['nd_ebitda'], rd_ventas_pct=M['ttm_rd_pct'], margen_bruto_pct=M['gm_q'][-1], ventas_riesgo_loe_2030_pct=M['loe30_pct'],
           crec_eps_fy27_pct=M['c27_g'], wacc_pct=WACC, postura=POST)
assert list(cmp) == CMPK
put('cmp', cmp)
LJ = J['pharma']['lly_jnj_3t26']; TK = J['todos_los_tickers']
def peer_cmp(t, mj):
    x = LJ[t]; c = TK[t]['consenso']
    MJ = json.load(open(HERE.parent / t.lower() / 'model.json', encoding='utf-8'))
    m = [x['m1_sotp'], x['m2_comp'], x['m3_rev'], x['m4_cons']]
    return dict(ticker=t, precio=x['cierre_20nov'], fair_value=x['fair_value_publicado'], gap_pct=x['gap_al_20nov_pct'], m1_sotp=m[0], m2_comp=m[1],
                m3_rev=m[2], m4_cons=m[3], indep=(0.15 * m[0] + 0.25 * m[1]) / 0.40, anclados=(0.35 * m[2] + 0.25 * m[3]) / 0.60,
                pe_fy27=x['pe_fy27_20nov'], div_yield_pct=x['div_yield_20nov_pct'], payout_fcf_pct=MJ['ttm']['div'] / MJ['ttm_fcf'] * 100,
                nd_ebitda=x['deuda_neta_ebitda'], rd_ventas_pct=x['rd_ventas_ttm_pct'], margen_bruto_pct=x['margen_bruto_3t_pct'],
                ventas_riesgo_loe_2030_pct=x.get('ventas_en_riesgo_loe_ttm_pct', x.get('ventas_en_riesgo_loe_pct')),
                crec_eps_fy27_pct=(c['eps_ajustado_fy_siguiente'] / c['eps_ajustado_fy_actual'] - 1) * 100,
                wacc_pct=x.get('wacc_pct', x.get('wacc_im_pct')), postura=mj)
CMPS = [peer_cmp('LLY', 'Neutral, con sesgo bajista'), cmp, peer_cmp('JNJ', 'Neutral, con sesgo bajista')]
assert abs(CMPS[0]['indep'] - LJ['LLY']['indep']) < 0.01
PFEJ = None
for pth in (HERE.parent / 'pfe' / 'model.json', Path('C:/Users/Equipo/Documents/manfredi-pfe/.claude/skills/informe-salud/modelos/pfe/model.json')):
    if pth.exists():
        PFEJ = json.load(open(pth, encoding='utf-8')).get('cmp'); put('pfe_src', str(pth.relative_to(pth.parents[5]) if 'manfredi-pfe' not in str(pth) else 'worktree manfredi-pfe')); break
if PFEJ:
    assert list(PFEJ) == CMPK, 'claves del cmp de PFE'
    CMPS = [PFEJ] + CMPS
put('cmp_rows', CMPS); put('cmp_has_pfe', bool(PFEJ))
put('rf_lly_jnj', 5.103)

# ======================= 15. Derivados para el texto =======================
put('rev_ttm_g', (TTMREV / ((15102 + 44542) / 1000) - 1) * 100)                  # TTM a sep-26 vs TTM a sep-25 (4T24 + 9M25)
put('est_values', [round(TTMREV, 2), G26['rev'], round(M['rev_c26'], 2), round(M['rev_c27'], 2)])
put('sotp_chart', [round(SG[k], 1) for k in ('sky', 'rin', 'btx_aes', 'neu', 'onc', 'oth', 'pipe', 'noloe_tv', 'platform')] + [round(-SG['rd'], 1), round(ND, 1), round(CONT, 1)])
put('bridge_chart', [round(BT[k], 2) for k in ('gaap', 'amort', 'cont', 'acq', 'oth')])
put('cash_ttm_b', {k: TTM[k] / 1000 for k in ('ocf', 'capex', 'div', 'buy', 'cont')}); put('ttm_fcf_b', M['ttm_fcf'] / 1000)
put('div_cov', M['ttm_fcf'] / TTM['div']); put('dps_27', 4 * 1.82)
put('div_cov_adj', BT['adj'] / (4 * 1.73))
put('hum_us_y1', US_CURVE[0] * 100); put('hum_us_y2', US_CURVE[1] * 100); put('hum_us_y3', US_CURVE[2] * 100); put('hum_us_y4', US_CURVE[3] * 100)
put('hum_int_y1', INT_CURVE[0] * 100); put('hum_int_y4', INT_CURVE[3] * 100); put('hum_int_y7', INT_CURVE[6] * 100)
put('bio_y1', BIO[0] * 100); put('bio_y2', BIO[1] * 100); put('bio_y3', BIO[2] * 100); put('bio_y4', BIO[3] * 100)
put('sky_loe_drop', (1 - B['R']['sky'][2035] / B['R']['sky'][2032]) * 100)
put('fcf27_base', B['fcf'][2027]); put('fcf33_base', B['fcf'][2033]); put('fcf38_base', B['fcf'][2038])
put('tot_peak_year', max(YEARS, key=lambda y: B['tot'][y])); put('tot_peak', max(B['tot'].values()))
put('tot_trough', min(B['tot'][y] for y in YEARS if y > M['tot_peak_year'])); put('rev38', B['tot'][2038])

put('mig_ttm', PTTM['ubr'] + PTTM['qul']); put('aes_ttm', PTTM['btxc'] + PTTM['juv'] + PTTM['aoth'])
put('bs_s26_gwi', BS['s26']['gw'] + BS['s26']['intg']); put('bs_d25_gwi', BS['d25']['gw'] + BS['d25']['intg'])
put('rin_ira_bear', 2 * M['rin_ira']); put('cm30_bear', CM0 - 2.0); put('cm30_bull', CM0 + 1.5)
# ======================= 16. Frases del texto atadas a números =======================
if TXT and not os.environ.get('NOASSERT'):
    assert M['m1'] < M['m3'] < M['m2'] < M['m4'], 'orden de métodos'
    assert M['m1'] < M['m3'] < PRICE < M['m2'] < M['m4']                 # "dos métodos por encima del precio (comparables y consenso), dos por debajo"
    assert -20 < M['blend_gap'] < -5                                     # postura "neutral, con sesgo cauteloso"
    assert M['m1_renewal'] < PRICE and M['anch_gap'] < 0 and M['indep_gap'] < 0
    assert M['m3_pre'] < M['m3'] and M['pre_pe'] < 13                   # la ventana previa a la LOE valuaba ~11x
    assert M['sky_rin3_g'] > 20 and M['hum_us_y3'] > 80 and M['hum_us_y1'] < 40
    assert M['imb9_us_g'] < -30 and M['aes3_g'] < 0 and M['juv3_int_g'] < -10
    assert M['nd_ebitda'] < 2.5 < M['nd_cont_ebitda'] and M['payout_fcf'] > 60
    assert M['sr_loe_share'] > 45 and 20 < M['loe30_pct'] < 25
    assert abs(M['rev27_vs_cons']) < 5, M['rev27_vs_cons']                # el Base 2027 queda cerca del consenso
    assert M['m1_frac'] < 40
out = HERE / ('model.json' if TXT else 'model_price.json')
json.dump(M, open(out, 'w', encoding='utf-8'), indent=1, default=float, ensure_ascii=False)
print(out.name, 'blend', round(BL, 2), 'gap', round(M['blend_gap'], 1), 'M1', round(M['m1'], 2), 'M2', round(M['m2'], 2), 'M3', round(M['m3'], 2), 'M4', M['m4'])
