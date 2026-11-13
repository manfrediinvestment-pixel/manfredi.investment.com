# Modelo de valuación JNJ (Johnson & Johnson) — todos los números derivados de informes/jnj.html salen de acá.
# Marco: informe-salud, conglomerado. Método 1 = suma de partes por segmento (Innovative Medicine producto por producto
# hasta la LOE + rNPV de la fase 3; MedTech por DCF), 15%; comparables P/E forward contra 13 pharmas y 5 medtech (25%);
# reversión al P/E propio (35%); consenso (25%).
# Fuentes: 8-K del 13-oct-2026 (comunicado del 3T 2026, Exhibits 99.1 y 99.2), 10-Q del 3T 2026 (21-oct-2026), 8-K del
# 21-ene-2026 (ventas 2025 por producto), 8-K del 14-abr-2026 y del 15-jul-2026, SEC XBRL companyfacts, Yahoo (precios y
# ^TNX), Nasdaq (consenso de EPS y precio objetivo, leído desde Chrome), stockanalysis.com (P/E forward y beta de pares,
# consenso de ingresos). Precio de corte: cierre del 12-nov-2026.
# La edición de septiembre (datos al 2T 2026) se reconstruye en sep_params.py (el script original no se guardó).
import json, os, copy, datetime
import numpy as np
from scipy.optimize import brentq
import sotp
import sep_params as S

CUT = '2026-11-12'
PRICE_ENV = os.environ.get('JNJ_PRICE')
M = {}
def put(k, v): M[k] = v; return v

# ======================= 1. Ventas por producto (Exhibit 99.2 de cada 8-K, US$ millones) =======================
P = json.load(open('raw/prod.json'))
FY25 = P['0000200406-26-000002']['TWELVE MONTHS']; Q4_25 = P['0000200406-26-000002']['FOURTH QUARTER']
H26 = P['0000200406-26-000146']['SIX MONTHS']; Q1_26 = P['0000200406-26-000076']['FIRST QUARTER']
Q2_26 = P['0000200406-26-000146']['SECOND QUARTER']
Q3 = P['0000200406-26-000189']['THIRD QUARTER']; N9 = P['0000200406-26-000189']['NINE MONTHS']
def g(d, n):
    for k in d:
        if k.startswith(n): return d[k]
    raise KeyError(n)
def q3(n): return g(Q3, n)[0]
def q3ly(n): return g(Q3, n)[1]
def ttm(n): return g(FY25, n)[0] - g(N9, n)[1] + g(N9, n)[0]
def e26(n):   # 2026e = nueve meses reales + 4T25 x (crecimiento del 3T26)
    a, b = g(Q3, n)
    return g(N9, n)[0] + g(Q4_25, n)[0] * (a / b if b else 1)
assert g(Q3, 'TOTAL INNOVATIVE')[0] + g(Q3, 'TOTAL MEDTECH')[0] == 25399
assert g(N9, 'TOTAL INNOVATIVE')[0] + g(N9, 'TOTAL MEDTECH')[0] == 74771
PRODS = ['DARZALEX', 'TREMFYA', 'STELARA', 'CARVYKTI', 'TECVAYLI', 'TALVEY', 'RYBREVANT', 'ERLEADA', 'IMBRUVICA',
         'SPRAVATO', 'CAPLYTA', 'INVEGA', 'SIMPONI', 'REMICADE', 'XARELTO', 'OPSUMIT', 'UPTRAVI', 'OTHER IMMUNOLOGY',
         'PULMONARY', 'INFECTIOUS', 'ONCOLOGY', 'IMMUNOLOGY', 'NEUROSCIENCE', 'TOTAL INNOVATIVE', 'TOTAL MEDTECH',
         'CARDIOVASCULAR', 'ELECTROPHYSIOLOGY', 'ABIOMED', 'SHOCKWAVE', 'OTHER CARDIOVASCULAR', 'SURGERY', 'ORTHOPAEDICS',
         'VISION', 'HIPS', 'KNEES', 'TRAUMA', 'SPINE']
KEY = {n.split()[0].lower() if n not in ('TOTAL INNOVATIVE', 'TOTAL MEDTECH', 'OTHER IMMUNOLOGY', 'OTHER CARDIOVASCULAR')
       else {'TOTAL INNOVATIVE': 'im', 'TOTAL MEDTECH': 'mt', 'OTHER IMMUNOLOGY': 'othimm', 'OTHER CARDIOVASCULAR': 'othcv'}[n]: n for n in PRODS}
for k, n in KEY.items():
    put(f'q3_{k}', q3(n) / 1000); put(f'q3ly_{k}', q3ly(n) / 1000); put(f'q3m_{k}', q3(n)); put(f'n9m_{k}', g(N9, n)[0])
    put(f'g3_{k}', (q3(n) / q3ly(n) - 1) * 100 if q3ly(n) else 0)
    put(f'ttm_{k}', ttm(n) / 1000); put(f'n9_{k}', g(N9, n)[0] / 1000)
    put(f'g9_{k}', (g(N9, n)[0] / g(N9, n)[1] - 1) * 100 if g(N9, n)[1] else 0)
# Crecimiento operativo (sin moneda) del 3T y de nueve meses, por segmento y total (Exhibit 99.2)
put('opg3_im', 7.9); put('opg3_mt', 2.5); put('opg3_tot', 6.0); put('opg3_adj', 6.1)
put('opg9_im', 7.4); put('opg9_mt', 3.5); put('opg9_tot', 6.0)
put('ste_drag3', 6.9)                                            # Stelara restó ~690 pb al crecimiento operativo de IM
put('opg3_mt_ortho', 3.4); put('opg3_mt_cv', 4.1); put('opg3_mt_surg', -1.0); put('opg3_mt_vis', 5.1)
put('opg3_mt_ep', 4.4); put('opg3_mt_abio', -1.5); put('opg3_mt_shock', 17.2)
put('opg3_dara', 15.6); put('opg3_trem', 68.2); put('opg3_ste', -54.0)
# Stelara: con y sin Stelara (reportado)
put('im_x_ste3', (q3('TOTAL INNOVATIVE') - q3('STELARA')) / 1000)
put('g3_im_x_ste', ((q3('TOTAL INNOVATIVE') - q3('STELARA')) / (q3ly('TOTAL INNOVATIVE') - q3ly('STELARA')) - 1) * 100)
put('g9_im_x_ste', ((g(N9, 'TOTAL INNOVATIVE')[0] - g(N9, 'STELARA')[0]) / (g(N9, 'TOTAL INNOVATIVE')[1] - g(N9, 'STELARA')[1]) - 1) * 100)
put('ste3_share_im', q3('STELARA') / q3('TOTAL INNOVATIVE') * 100)
put('ste_2024', 10.361); put('ste_2025', 6.078); put('ste_n9_26', g(N9, 'STELARA')[0] / 1000); put('ste_e26', e26('STELARA') / 1000)
put('ste_lvl26', M['ste_e26'] / M['ste_2024'] * 100)              # nivel 2026e sobre 2024 (año previo a biosimilares)
put('ste3_cons', 0.591)                                           # LSEG vía CNBC, 13-oct-2026
# Motores de reemplazo (3T26): ventas, crecimiento, peso en IM
for k in ('darzalex', 'tremfya', 'carvykti', 'rybrevant', 'spravato', 'caplyta'):
    put(f'sh3_{k}', M[f'q3_{k}'] / M['q3_im'] * 100)
put('mot6_q3', sum(M[f'q3_{k}'] for k in ('darzalex', 'tremfya', 'carvykti', 'rybrevant', 'spravato', 'caplyta')))
put('mot6_q3ly', sum(M[f'q3ly_{k}'] for k in ('darzalex', 'tremfya', 'carvykti', 'rybrevant', 'spravato', 'caplyta')))
put('mot6_g3', (M['mot6_q3'] / M['mot6_q3ly'] - 1) * 100); put('mot6_sh3', M['mot6_q3'] / M['q3_im'] * 100)
put('mot6_add', M['mot6_q3'] - M['mot6_q3ly']); put('ste_loss3', M['q3ly_stelara'] - M['q3_stelara'])
put('mot_vs_ste', M['mot6_add'] / M['ste_loss3'])
# Trimestrales para el gráfico de productos (3T25 a 3T26)
QS = {}
for k, n in (('dara', 'DARZALEX'), ('trem', 'TREMFYA'), ('ste', 'STELARA'), ('car', 'CARVYKTI')):
    QS[k] = [round(x / 1000, 2) for x in (g(Q3, n)[1], g(Q4_25, n)[0], g(Q1_26, n)[0], g(Q2_26, n)[0], g(Q3, n)[0])]
put('prod_q', QS)

# ======================= 2. Resultados del 3T26 y 9M (comunicado + 10-Q + XBRL, US$ millones) =======================
put('rev3', 25399); put('rev3_ly', 23993); put('rev3_g', (25399 / 23993 - 1) * 100)
put('cogs3', 8097); put('cogs3_ly', 7303); put('rd3', 4652); put('rd3_ly', 3672); put('sga3', 6285); put('sga3_ly', 5922)
put('pt3', 34); put('pt3_ly', 7493); put('ni3', 210); put('ni3_ly', 5152); put('eps3', 0.09); put('eps3_ly', 2.12)
put('epsadj3', 2.59); put('epsadj3_ly', 2.80); put('niadj3', 6339); put('niadj3_ly', 6801)
for k in ('cogs3', 'rd3', 'sga3', 'pt3', 'ni3', 'eps3', 'epsadj3'):
    put(k + '_g', (M[k] / M[k + '_ly'] - 1) * 100)
put('gm3', (1 - 8097 / 25399) * 100); put('gm3_ly', (1 - 7303 / 23993) * 100); put('gm3_d', M['gm3'] - M['gm3_ly'])
put('rd3_pct', 4652 / 25399 * 100); put('rd3_im', 3888); put('rd3_im_pct', 23.2); put('rd3_mt_pct', 8.8)
# Ítems de la conciliación del 3T26 (antes de impuestos)
put('lit3', 5519); put('amort3', 1240); put('sepcost3', 369); put('iprdimp3', 339); put('restr3', 195)
put('firefly', 1.0); put('firefly_cf', 0.964); put('sail_prem', 0.3); put('sail_eq', 0.5); put('sail_init', 0.8); put('sail_opt', 2.6)
put('tariff_rec', 0.2)
# Nueve meses
put('n9_rev', 74771); put('n9_rev_ly', 69629); put('n9_epsadj', 8.19); put('n9_epsadj_ly', 8.33)
# Trimestres (para la tabla y la reversión): ingresos, costo, I+D, SG&A
REVQ = put('rev_q', [23993, 24564, 24062, 25310, 25399])          # 3T25, 4T25, 1T26, 2T26, 3T26
COGSQ = [7303, 30256 - 22288, 8106, 8051, 8097]; RDQ = [3672, 14665 - 10413, 11832 - 4652 - 3653, 3653, 4652]
SGAQ = [5922, 23676 - 16923, 6034, 6432, 6285]
assert REVQ[1] == 94193 - 69629 and sum(REVQ[2:]) == 74771
put('gm_q', [round((1 - c / r) * 100, 1) for c, r in zip(COGSQ, REVQ)])
put('rd_q', [round(d / r * 100, 1) for d, r in zip(RDQ, REVQ)]); put('sga_q', [round(s / r * 100, 1) for s, r in zip(SGAQ, REVQ)])
# TTM (4T25 + nueve meses de 2026)
FY = dict(rev=94193, cogs=30256, rd=14665, sga=23676, pt=32581, ni=26804, ocf=24530, capex=4832, div=12381, buy=5953, da=7503)
N25 = dict(rev=69629, cogs=22288, rd=10413, sga=16923, pt=27615, ni=21688, ocf=17221, capex=2995, div=9250, buy=4029, da=5492)
N26 = dict(rev=74771, cogs=24254, rd=11832, sga=18751, pt=12771, ni=10979, ocf=18850, capex=3732, div=9585, buy=5958, da=6080)
TTM = {k: FY[k] - N25[k] + N26[k] for k in FY}
put('ttm', TTM); put('ttm_rev', TTM['rev'] / 1000); put('ttm_gm', (1 - TTM['cogs'] / TTM['rev']) * 100)
put('ttm_rd_pct', TTM['rd'] / TTM['rev'] * 100)
REV_TTM_LY = put('ttm_rev_ly', 88821 - 66301 + 69629)             # TTM a sep-2025: 4T24 (2024 − 9M24, XBRL) + 9M25
put('ttm_rev_g', (TTM['rev'] / REV_TTM_LY - 1) * 100)
put('ttm_fcf', TTM['ocf'] - TTM['capex']); put('ttm_ocfm', TTM['ocf'] / TTM['rev'] * 100); put('ttm_fcfm', M['ttm_fcf'] / TTM['rev'] * 100)
put('ttm_capexm', TTM['capex'] / TTM['rev'] * 100)
put('ttm_ni', TTM['ni']); put('ttm_pt', TTM['pt'])
EPSQ = put('eps_adj_q', {'3T23': 2.66, '4T23': 2.29, '1T24': 2.71, '2T24': 2.82, '3T24': 2.42, '4T24': 2.04, '1T25': 2.77,
                         '2T25': 2.77, '3T25': 2.80, '4T25': 2.46, '1T26': 2.70, '2T26': 2.90, '3T26': 2.59})
put('ttm_epsadj', round(2.46 + 2.70 + 2.90 + 2.59, 2)); put('ttm_eps_gaap', round(11.03 - 8.94 + 4.49, 2))
# Segmentos (10-Q, Nota de segmentos): resultado antes de impuestos y margen ajustado (9M26)
put('seg_im_pt9', 16632); put('seg_mt_pt9', 3192); put('seg_im_pt9_ly', 17208); put('seg_mt_pt9_ly', 3912)
put('seg_im_rd9', 9576); put('seg_mt_rd9', 2256)
IM_ADJ9 = put('seg_im_adj9', 16632 + 2300 + 300)                   # + amortización ($2.3B) + reestructuración ($0.3B)
MT_ADJ9 = put('seg_mt_adj9', 3192 + 1400 + 700 + 259 + 400)        # + amortización, separación de ortopedia, reestructuraciones, deterioro IPR&D
put('seg_im_adjm9', IM_ADJ9 / 48567 * 100); put('seg_mt_adjm9', MT_ADJ9 / 26204 * 100)
put('seg_im_rdm9', 9576 / 48567 * 100); put('seg_mt_rdm9', 2256 / 26204 * 100)
put('seg_im_ptm9', 16632 / 48567 * 100); put('seg_mt_ptm9', 3192 / 26204 * 100)
put('seg_im_ptm9_ly', 17208 / 44638 * 100); put('seg_mt_ptm9_ly', 3912 / 24991 * 100)
EPS_IM_SH = put('eps_im_share', IM_ADJ9 / (IM_ADJ9 + MT_ADJ9))
put('im_rev_share_ttm', M['ttm_im'] / M['ttm_rev'] * 100); put('mt_rev_share_ttm', M['ttm_mt'] / M['ttm_rev'] * 100)

# Guía 2026 (comunicado del 13-oct vs. 8-K del 29-jul)
put('g_rev_lo', 101.0); put('g_rev_hi', 101.4); put('g_rev_mid', 101.2); put('g_rev_mid_prev', 101.1)
put('g_oprev_mid', 100.7); put('g_oprev_mid_prev', 100.6); put('g_adjop_g', 6.6); put('g_adjop_g_prev', 6.5)
put('g_eps_lo', 11.05); put('g_eps_hi', 11.15); put('g_eps_mid', 11.10); put('g_eps_lo_prev', 10.96); put('g_eps_hi_prev', 11.11)
put('g_eps_mid_prev', 11.04); put('g_eps_up', 0.06); put('g_eps_g', 2.9); put('g_eps_jul15_lo', 11.60); put('g_eps_jul15_hi', 11.75)
put('q4_rev_implied', M['g_rev_mid'] - 74.771)
# 2026e por producto y segmento (para la suma de partes): 4T implícito en la guía, repartido por segmento con el
# crecimiento del 3T; dentro de IM, cada producto con nombre usa su 4T25 x crecimiento del 3T26 y la cartera madura es el resto
MT_Q4E = 8801 * (8642 / 8430) / 1000
put('mt26e', 26.204 + MT_Q4E); put('im26e', M['g_rev_mid'] - M['mt26e'])
LV = dict(dara26=e26('DARZALEX'), trem26=e26('TREMFYA'), ste26=e26('STELARA'), erl26=e26('ERLEADA'), imb26=e26('IMBRUVICA'),
          car26=e26('CARVYKTI'), spr26=e26('SPRAVATO'), cap26=e26('CAPLYTA'),
          onc26=e26('RYBREVANT') + e26('TECVAYLI') + e26('TALVEY'))
LV = {k: v / 1000 for k, v in LV.items()}
LV['ico26'] = 0.25; LV['ima26'] = 0.20                              # "Other Immunology" 9M26 = $0.30B (Icotyde + Imaavy), supuesto propio de reparto
LV['mat26'] = M['im26e'] - sum(LV.values())
put('lvl26', LV)

# ======================= 3. Balance y flujo (XBRL, US$ millones) =======================
BAL = put('bal', {'27-sep-2026': dict(cash=16910, ms=318, std=8852, ltd=35799, inv=15377, gwi=48474 + 46652, eq=81529, assets=197425),
                  '28-dic-2025': dict(cash=19709, ms=393, std=8495, ltd=39438, inv=14191, gwi=48772 + 50403, eq=81544, assets=199210),
                  '28-sep-2025': dict(cash=18231, ms=331, std=6387, ltd=39408, inv=14146, gwi=48048 + 48737, eq=79277, assets=192816)})
for k, b in BAL.items(): b['nd'] = b['std'] + b['ltd'] - b['cash'] - b['ms']
DEBT = put('debt', (8852 + 35799) / 1000)                          # LongTermDebtNoncurrent: sin la porción corriente (no se duplica)
ND = put('net_debt', BAL['27-sep-2026']['nd'] / 1000)
assert abs(DEBT - 44.651) < 1e-9 and abs(ND - 27.423) < 1e-9       # 10-Q: $44.6B de deuda y $27.4B de deuda neta
TALC = put('talc', 9.0); TALC_OV = put('talc_ov', 5.5); OPI = put('opioids', 0.9); put('talc_jun', 3.7)
put('talc_claims', 76500)
LIAB = put('liab', ND + TALC + OPI)
# EBITDA TTM (estimación propia): resultado antes de impuestos + litigios del 3T26 (talco, $5,519M) + intereses netos + D&A.
# Intereses netos TTM = 2025 (971 − 1,056) − 9M25 (757 − 819) + 9M26 (136, estado de resultados).
INT_NET = put('int_net_ttm', (971 - 1056) - (757 - 819) + 136)
EBITDA = put('ebitda', (TTM['pt'] + 5519 + INT_NET + TTM['da']) / 1000)
put('nd_ebitda', ND / EBITDA); put('liab_ebitda', LIAB / EBITDA)
put('lt_rate', 3.57)
# Flujo de caja (tabla 2022-2025 de septiembre + TTM a sep-2026)
CF = put('cf', {'2022': [21194, 4009, 11682, 6035, 79990], '2023': [22791, 4543, 11770, 5054, 85159],
                '2024': [24266, 4424, 11823, 2432, 88821], '2025': [24530, 4832, 12381, 5953, 94193],
                'TTM': [TTM['ocf'], TTM['capex'], TTM['div'], TTM['buy'], TTM['rev']]})
put('cf_rows', {k: dict(ocf=v[0], capex=v[1], fcf=v[0] - v[1], div=v[2], buy=v[3], ocfm=v[0] / v[4] * 100, fcfm=(v[0] - v[1]) / v[4] * 100)
                for k, v in CF.items()})
put('payout_ttm', (TTM['div'] + TTM['buy']) / M['ttm_fcf'] * 100)
put('fcf9m_est', 15.1); put('fcf9m_ly', 14.226)
put('div_q', 1.34); put('div_years', 64)

# ======================= 4. Precio, tasa y pares =======================
def yclose(t, day):
    d = json.load(open(f'yh/{t}.d.json'))['chart']['result'][0]
    rows = {datetime.datetime.fromtimestamp(a, datetime.UTC).date().isoformat(): c
            for a, c in zip(d['timestamp'], d['indicators']['quote'][0]['close']) if c}
    return rows[day]
PRICE = put('price', round(float(PRICE_ENV) if PRICE_ENV else yclose('JNJ', CUT), 2))
RF = put('rf', round(yclose('^TNX', CUT), 3))
put('price_sep', 269.17); put('price_chg', (PRICE / 269.17 - 1) * 100)
put('price_oct12', round(yclose('JNJ', '2026-10-12'), 2)); put('price_oct13', round(yclose('JNJ', '2026-10-13'), 2))
put('earn_day', (M['price_oct13'] / M['price_oct12'] - 1) * 100)
put('div_yield', 4 * 1.34 / PRICE * 100)
SH_OUT = put('shares_out', 2.40731)                                 # 15-oct-2026 (portada del 10-Q)
SH = put('shares_dil', 2.4486)                                      # promedio diluido del 3T26
put('mcap', PRICE * SH_OUT)
# Pares: P/E forward, EV/EBITDA, rendimiento y beta 5 años (stockanalysis.com, 13-nov-2026)
PEERS = put('peers', {
    'LLY': (30.83, 28.70, 0.48, 0.39, 1.46), 'ABBV': (18.78, 18.62, 2.46, 0.19, 1.40), 'AMGN': (19.18, 16.64, 2.16, 0.42, 3.51),
    'MRK': (17.48, 13.69, 2.31, 0.12, 3.96), 'GILD': (20.21, 15.53, 1.95, 0.37, 2.77), 'NVS': (16.56, 14.20, 1.93, 0.45, None),
    'AZN': (16.79, 14.67, 1.75, 0.16, None), 'REGN': (11.94, 13.95, 0.39, 0.10, 1.00), 'NVO': (12.24, 6.99, 3.08, 0.37, None),
    'PFE': (10.18, 8.53, 5.96, 0.30, None), 'GSK': (10.46, 8.39, 3.57, 0.28, None), 'BMY': (9.81, 8.80, 3.98, 0.19, None),
    'SNY': (9.76, 7.84, 4.99, 0.26, None)})
MEDT = put('medt', {'ABT': (18.66, 18.58, 2.31, 0.54, 1.96), 'MDT': (17.17, 13.74, 2.79, 0.57, 3.42), 'SYK': (19.30, 17.33, 1.14, 0.77, 2.31),
                    'BSX': (14.39, 13.54, None, 0.59, 1.39), 'BDX': (16.48, 14.16, 1.95, 0.28, 3.61)})
put('jnj_stats', dict(pe_f=25.74, ev_ebitda=20.79, dy=1.87, beta=0.20))
pe_ph = sorted(v[0] for v in PEERS.values()); pe_mt = sorted(v[0] for v in MEDT.values())
put('peer_q3', float(np.percentile(pe_ph, 75))); put('peer_med', float(np.median(pe_ph))); put('peer_max', max(pe_ph))
put('mt_q3', float(np.percentile(pe_mt, 75))); put('mt_med', float(np.median(pe_mt))); put('mt_max', max(pe_mt))
put('jnj_prem_med', (M['jnj_stats']['pe_f'] / M['peer_med'] - 1) * 100)
# Regresión P/E vs crecimiento (crecimiento = P/E forward / PEG)
def reg(d):
    xs = [v[0] / v[4] for v in d.values() if v[4]]; ys = [v[0] for v in d.values() if v[4]]
    b, a = np.polyfit(xs, ys, 1); yh = [a + b * x for x in xs]
    r2 = 1 - sum((y - h) ** 2 for y, h in zip(ys, yh)) / sum((y - np.mean(ys)) ** 2 for y in ys)
    return float(r2), float(b), len(xs)
r2, sl, n = reg(PEERS); put('reg_r2', r2); put('reg_slope', sl); put('reg_n', n)
r2x, slx, _ = reg({k: v for k, v in PEERS.items() if k != 'LLY'}); put('reg_r2_xlly', r2x); put('reg_slope_xlly', slx)
r2m, slm, nm = reg(MEDT); put('reg_r2_mt', r2m); put('reg_n_mt', nm)
# Betas de pares (Blume)
B_PH = put('beta_ph_raw', float(np.mean([v[3] for v in PEERS.values()]))); B_MT = put('beta_mt_raw', float(np.mean([v[3] for v in MEDT.values()])))
put('beta_im', 0.67 * B_PH + 0.33); put('beta_mt', 0.67 * B_MT + 0.33)
ERP = put('erp', 5.0); KD = put('kd_pre', 5.1); TAX = put('tax', 17.5); put('kd', KD * (1 - TAX / 100))
DV = put('dv', DEBT / (DEBT + M['mcap'])); put('dv_pct', DV * 100)
put('ke_im', RF + M['beta_im'] * ERP); put('ke_mt', RF + M['beta_mt'] * ERP)
put('wacc_im', (1 - DV) * M['ke_im'] + DV * M['kd']); put('wacc_mt', (1 - DV) * M['ke_mt'] + DV * M['kd'])
put('beta_own', 0.20); put('wacc_own', (1 - DV) * (RF + (0.67 * 0.20 + 0.33) * ERP) + DV * M['kd'])

# Consenso (Nasdaq, leído desde Chrome el 13-nov-2026) y stockanalysis (referencia)
C26 = put('c26', 11.12); C27 = put('c27', 11.56); put('c28', 13.84); put('c27_hi', 12.27); put('c27_lo', 10.75); put('c27_n', 9)
put('c27_down', 4)
put('c26_rev', 101.22); put('c27_rev', 107.75); put('c26_rev_g', (101.22 / 94.193 - 1) * 100); put('c27_rev_g', (107.75 / 101.22 - 1) * 100)
put('c26_g', (C26 / 10.79 - 1) * 100); put('c27_g', (C27 / C26 - 1) * 100)
put('pt_avg', 287.88); put('pt_lo', 260.0); put('pt_hi', 320.0); put('n_an', 17); put('n_buy', 11); put('n_hold', 6); put('n_sell', 0)
put('sa_pt', 279.41); put('sa_n', 23); put('sa_c27', 11.62); put('sa_pt_lo', 190.0)
put('pt_vs_price', (M['pt_avg'] / PRICE - 1) * 100)
put('pe_c27', PRICE / C27); put('pe_ttm', PRICE / M['ttm_epsadj']); put('pe_c26', PRICE / C26)

# ======================= 5. Método 1 — suma de partes (3T26) =======================
# Margen de contribución anclado en el flujo real TTM: OCF + I+D después de impuestos − capex, sobre ingresos. La I+D
# adquirida de Firefly (cargo no-caja de $0.96B, sumado de vuelta en el flujo operativo y pagado en inversión) se excluye.
RD_X = TTM['rd'] - 964
put('ttm_rd_x', RD_X); put('ttm_rd_x_pct', RD_X / TTM['rev'] * 100)
CM_CO = put('cm_co', (TTM['ocf'] + RD_X * (1 - TAX / 100) - TTM['capex']) / TTM['rev'] * 100)
put('cm_ocf', M['ttm_ocfm']); put('cm_rd', RD_X * (1 - TAX / 100) / TTM['rev'] * 100); put('cm_capex', M['ttm_capexm'])
RATIO = 0.431 / 0.215                                               # relación IM/MedTech de septiembre (resultado ajustado antes de I+D, D&A y capex)
SH_IM = M['ttm_im'] / M['ttm_rev']
CM_MT = CM_CO / (SH_IM * RATIO + (1 - SH_IM)); CM_IM = CM_MT * RATIO
put('cm_im', CM_IM); put('cm_mt', CM_MT)
IM_RD_TTM = (11850 - 8361 + 9576 - 964) / 1000                      # I+D de IM TTM sin el cargo de Firefly
MT_RD_TTM = (14665 - 11850 - 2052 + 2256) / 1000
put('rd_im_ttm', IM_RD_TTM / M['ttm_im'] * 100); put('rd_mt_ttm', MT_RD_TTM / M['ttm_mt'] * 100)
MT_FCFM = put('mt_fcfm', CM_MT - M['rd_mt_ttm'] * (1 - TAX / 100))
put('mt_fcfm30', MT_FCFM + (15.8 - 14.3))
put('ocf_q3', 18850 - 11130); put('ocf_q3_ly', 17221 - 8052)

def p3(name='base', **kw):
    p = S.scen(name)
    p.update(LV)
    p['dara26'] = LV['dara26']                                       # dato, no la escala calibrada de septiembre
    p.update(shares=SH, liab=LIAB, acq=4.835, tax=TAX / 100, wacc_im=M['wacc_im'] / 100, wacc_mt=M['wacc_mt'] / 100,
             mt26=M['mt26e'])
    d_im = CM_IM / 100 - 0.431; d_rd = M['rd_im_ttm'] / 100 - 0.192
    p['cm'] = {k: v + d_im for k, v in p['cm'].items()}
    p['rd'] = {2026: M['rd_im_ttm'] / 100, 2030: p['rd'][2030]}
    d_mt = MT_FCFM / 100 - 0.143
    p['mt_m'] = {k: v + d_mt for k, v in p['mt_m'].items()}
    gmt = 0.040 if name == 'base' else (0.025 if name == 'bear' else 0.050)   # MedTech 2027-2029 (9M26 operativo +3.5%)
    p['mt_g'] = {2027: gmt, 2029: gmt, 2034: 0.03, 2035: 0.03}
    dw = {'base': 0, 'bear': 0.0075, 'bull': -0.0075}[name]
    p['wacc_im'] += dw; p['wacc_mt'] += dw
    p.update(kw)
    return p
put('mt_g_base', 4.0)
RB = sotp.run(p3('base')); M1 = put('m1', RB['fv'])
C = RB['im']['C']
put('sotp', {k: float(v) for k, v in C.items()}); put('im_ev', RB['im']['ev']); put('mt_ev', RB['mt']['ev'])
put('mt_tv_share', RB['mt']['tv_share'] * 100); put('mt_ev_sales', RB['mt']['ev'] / M['mt26e'])
put('m1_ev', RB['ev']); put('m1_eq', RB['eq']); put('plat_share_ev', C['plat'] / RB['im']['ev'] * 100)
put('im_ps', RB['im_ps']); put('mt_ps', RB['mt_ps'])
put('w_im', 15 * RB['im_ps'] / M1); put('w_mt', 15 * RB['mt_ps'] / M1)
put('im_rev_27', RB['im']['tot'][2027]); put('im_rev_30', RB['im']['tot'][2030]); put('im_rev_35', RB['im']['tot'][2035])
put('rev27_model', RB['im']['tot'][2027] + RB['mt']['rev'][2027]); put('rev27_vs_cons', (M['rev27_model'] / 107.75 - 1) * 100)
RBe = sotp.run(p3('bear')); RBu = sotp.run(p3('bull'))
put('m1_bear', RBe['fv']); put('m1_bull', RBu['fv'])
put('im_rev_bear', [RBe['im']['tot'][2030], RBe['im']['tot'][2035]]); put('im_rev_bull', [RBu['im']['tot'][2030], RBu['im']['tot'][2035]])
put('m1_ew', 0.25 * RBe['fv'] + 0.45 * M1 + 0.30 * RBu['fv'])
put('m1_late', sotp.run(p3(dara_loe_us=2032, dara_loe_row=2034, trem_loe=2033, erl_loe=2041, spr_loe=2040, cap_loe=2040))['fv'])
put('m1_slow', sotp.run(p3(bio_e=[0.70, 0.45]))['fv']); put('m1_noph3', sotp.run(p3(ph3_n=0))['fv'])
pr = p3(); pr['renewal'] = True; put('m1_renewal', sotp.run(pr)['fv']); put('m1_ren_gap', (M['m1_renewal'] / PRICE - 1) * 100)
put('m1_ownbeta', sotp.run(p3(wacc_im=M['wacc_own'] / 100, wacc_mt=M['wacc_own'] / 100))['fv'])
put('m1_talc55', M1 + (TALC - TALC_OV) / SH)                       # con el tratamiento de septiembre (solo los $5.5B)
GRID_W = [-0.01, -0.005, 0, 0.005, 0.01]; GRID_P = [0.30, 0.40, 0.524, 0.70, 0.906]
grid = []
for dw in GRID_W:
    grid.append([sotp.run(p3(wacc_im=M['wacc_im'] / 100 + dw, wacc_mt=M['wacc_mt'] / 100 + dw, ph3_pos=pp))['fv'] for pp in GRID_P])
put('grid', grid); put('grid_w', [M['wacc_im'] + 100 * d for d in GRID_W]); assert abs(grid[2][2] - M1) < 1e-9
# Escenario explícito de ortopedia (no entra al Base): parte de MedTech atribuible a DePuy Synthes por ingresos
ORTHO26 = e26('ORTHOPAEDICS') / 1000; put('ortho26', ORTHO26); put('ortho_sh_mt', ORTHO26 / M['mt26e'] * 100)
put('ortho_dcf', RB['mt']['ev'] * ORTHO26 / M['mt26e'])
put('ortho_sale', 20.0)                                             # valor de venta informado por la prensa (no confirmado)
put('m1_ortho_sale', M1 + (M['ortho_sale'] - M['ortho_dcf']) / SH)
put('ortho_sale_ev_sales', M['ortho_sale'] / ORTHO26)
put('sep_cost9', 0.746); put('sep_cost9_m', 746)
# DCF de referencia y DCF inverso (mismo armado que septiembre)
W_EV = (RB['im']['ev'] * M['wacc_im'] + RB['mt']['ev'] * M['wacc_mt']) / RB['ev'] / 100
put('wacc_co', W_EV * 100)
def dcf(gr, w=W_EV, m0=None, m1=0.25, rev26=M['g_rev_mid'], perp=0.025, liab=LIAB, sh=SH):
    m0 = M['ttm_fcfm'] / 100 if m0 is None else m0
    pv, r, f, t = 0, rev26, 0, 0
    for y in range(2026, 2032):
        if y > 2026: r *= 1 + gr
        m = m0 + (m1 - m0) * (y - 2026) / 5
        f = r * m; t = 0.125 if y == 2026 else (y - 2027) + 0.75
        pv += f * (0.25 if y == 2026 else 1) * (1 + w) ** -t
    tv = f * (1 + perp) / (w - perp) * (1 + w) ** -t
    return (pv + tv - liab) / sh, tv / (pv + tv), r
v, s, _ = dcf(0.055); put('dcf_ref', v); put('dcf_tv_share', s * 100)
gi = brentq(lambda x: dcf(x)[0] - PRICE, 0, 0.4); put('dcf_g_impl', gi * 100); put('dcf_rev31', dcf(gi)[2])

# ======================= 6. Métodos 2, 3 y 4 =======================
def m2_of(ph, mt, c27=C27, sh=EPS_IM_SH):
    ph = sorted(ph); mt = sorted(mt)
    q_ph, q_mt = float(np.percentile(ph, 75)), float(np.percentile(mt, 75))
    return c27 * (sh * q_ph / (1 + M['ke_im'] / 100) + (1 - sh) * q_mt / (1 + M['ke_mt'] / 100)), q_ph, q_mt
DAYS_LEFT = (datetime.date(2026, 12, 31) - datetime.date.fromisoformat(CUT)).days / 365
put('ntm_w26', DAYS_LEFT)
NTM = put('eps_ntm', DAYS_LEFT * C26 + (1 - DAYS_LEFT) * C27)
M2, _, _ = m2_of(pe_ph, pe_mt); put('m2', M2)
put('m2_lo', NTM * (EPS_IM_SH * M['peer_med'] + (1 - EPS_IM_SH) * M['mt_med']))
put('m2_hi', C27 * (EPS_IM_SH * M['peer_max'] / (1 + M['ke_im'] / 100) + (1 - EPS_IM_SH) * M['mt_max'] / (1 + M['ke_mt'] / 100)))
# Comparable que más distorsiona: el que más mueve el Método 2 al sacarlo
loo = {}
for k in PEERS:
    loo[k] = m2_of([v[0] for kk2, v in PEERS.items() if kk2 != k], pe_mt)[0] - M2
for k in MEDT:
    loo[k] = m2_of(pe_ph, [v[0] for kk2, v in MEDT.items() if kk2 != k])[0] - M2
# Distorsiona el que más se aleja de la mediana del grupo (en J&J, Lilly a 30.8x); sacar cualquiera de los tres por
# encima del cuartil mueve el cuartil lo mismo, así que el criterio es la distancia, no el efecto.
DIST = max(PEERS, key=lambda k: abs(PEERS[k][0] - M['peer_med'])); put('m2_dist', DIST); put('m2_loo', loo)
M2X, QX, _ = m2_of([v[0] for k, v in PEERS.items() if k != DIST], pe_mt); put('m2_x', M2X); put('peer_q3_x', QX)
# Método 3: nueve cierres trimestrales (sep-24 a sep-26), EPS ajustado TTM tal como lo reporta J&J
WIN = [('30-sep-2024', 162.06, 10.24), ('31-dic-2024', 144.62, 9.98), ('31-mar-2025', 165.84, 10.05),
       ('30-jun-2025', 152.75, 10.00), ('30-sep-2025', 185.42, 10.38), ('31-dic-2025', 206.95, 10.79),
       ('31-mar-2026', 244.44, 10.73), ('30-jun-2026', 253.97, 10.86), ('30-sep-2026', 264.74, M['ttm_epsadj'])]
mo = json.load(open('yh/JNJ.mo.json'))['chart']['result'][0]
moc = {datetime.datetime.fromtimestamp(a, datetime.UTC).strftime('%Y-%m'): round(c, 2) for a, c in zip(mo['timestamp'], mo['indicators']['quote'][0]['close']) if c}
MON = {'sep': '09', 'dic': '12', 'mar': '03', 'jun': '06'}
for d, px, e in WIN:
    _, mm, yy = d.split('-'); assert moc[f'{yy}-{MON[mm]}'] == px, (d, px)
pes = [px / e for _, px, e in WIN]
put('m3_rows', [dict(d=d, px=px, eps=e, pe=px / e) for d, px, e in WIN])
put('m3_pe', float(np.mean(pes))); M3 = put('m3', M['m3_pe'] * M['ttm_epsadj'])
put('m3_lo', min(pes) * M['ttm_epsadj']); put('m3_hi', max(pes) * M['ttm_epsadj']); put('m3_gap', (M3 / PRICE - 1) * 100)
put('pe_ttm_now', PRICE / M['ttm_epsadj'])
put('m3_x_firefly', M['m3_pe'] * (M['ttm_epsadj'] + 0.41))          # referencia: sumando de vuelta Firefly y Sail (no se usa)
# Método 4
M4 = put('m4', M['pt_avg'])

# ======================= 7. Blend =======================
W = {'m1': 0.15, 'm2': 0.25, 'm3': 0.35, 'm4': 0.25}
BL = put('blend', sum(M[k] * w for k, w in W.items())); put('blend_gap', (BL / PRICE - 1) * 100)
for k, w in W.items(): put(k + '_ap', M[k] * w)
put('ap_im', M['im_ps'] * 0.15); put('ap_mt', M['mt_ps'] * 0.15)   # aporte = valor por acción x 15%; el peso mostrado es 15% x valor / M1
put('ind', (0.15 * M['m1'] + 0.25 * M['m2']) / 0.40); put('ind_gap', (M['ind'] / PRICE - 1) * 100)
put('anc', (0.35 * M['m3'] + 0.25 * M['m4']) / 0.60); put('anc_gap', (M['anc'] / PRICE - 1) * 100)
put('blend_x', BL + 0.25 * (M2X - M2)); put('blend_x_gap', (M['blend_x'] / PRICE - 1) * 100)
put('blend_sa', BL + 0.25 * (M['sa_pt'] - M4)); put('blend_sa_gap', (M['blend_sa'] / PRICE - 1) * 100)
for k in ('m1', 'm2', 'm3', 'm4'): put(k + '_gap', (M[k] / PRICE - 1) * 100)
put('m1_bear_gap', (M['m1_bear'] / PRICE - 1) * 100)

# ======================= 8. Septiembre: recálculo y puentes =======================
SEP_PUB = dict(m1=97.56, m2=193.08, m3=192.16, m4=277.91, blend=199.64, price=269.17)
sep_m1 = sotp.run(S.scen('base'))['fv']
SEP = dict(m1=sep_m1,
           m2=12.14 * (0.772 * 17.20 / 1.0782 + 0.228 * 17.10 / 1.0862),
           m3=float(np.mean([146.16 / 10.48, 162.06 / 10.24, 144.62 / 9.98, 165.84 / 10.05, 152.75 / 10.00, 185.42 / 10.38,
                             206.95 / 10.79, 244.44 / 10.73, 253.97 / 10.86])) * 10.86,
           m4=277.91)
SEP['blend'] = sum(SEP[k] * w for k, w in W.items())
put('sep_rebuilt', SEP); put('sep_pub', SEP_PUB)
put('sep_diff', {k: SEP[k] - SEP_PUB[k] for k in SEP_PUB if k in SEP})
put('sep_rebuilt_m1', sep_m1); put('sep_m1_diff_pct', (sep_m1 / 97.56 - 1) * 100)
put('blend_sep', 199.64); put('blend_sep_gap', (199.64 / 269.17 - 1) * 100)
put('blend_chg', BL - 199.64); put('blend_chg_pct', (BL / 199.64 - 1) * 100)
for k in ('m1', 'm2', 'm3', 'm4'): put(k + '_chg', M[k] - SEP_PUB[k])
# Puente del Método 1: de la reconstrucción de septiembre al 3T26, un cambio por vez (acumulativo)
steps = []
cur = S.scen('base'); prev = sep_m1
def step(label, fn):
    global cur, prev
    fn(cur); v = sotp.run(cur)['fv']; steps.append(dict(label=label, d=v - prev)); prev = v
def s_lvl(p):
    p.update(LV); p['mt26'] = M['mt26e']
def s_margin(p):
    p['cm'] = {k: v + CM_IM / 100 - 0.431 for k, v in p['cm'].items()}; p['rd'] = {2026: M['rd_im_ttm'] / 100, 2030: 0.18}
    p['mt_m'] = {k: v + MT_FCFM / 100 - 0.143 for k, v in p['mt_m'].items()}
def s_mtg(p): p['mt_g'] = {2027: 0.04, 2029: 0.04, 2034: 0.03, 2035: 0.03}
def s_wacc(p): p['wacc_im'] = M['wacc_im'] / 100; p['wacc_mt'] = M['wacc_mt'] / 100
def s_liab(p): p['liab'] = ND + TALC_OV + OPI; p['shares'] = SH
def s_talc(p): p['liab'] = LIAB
step('Niveles 2026 de cada producto y de MedTech (nueve meses reales + 4T de la guía)', s_lvl)
step('Margen de caja TTM (flujo operativo de 26.3% contra 28.2%) e I+D de IM', s_margin)
step('Crecimiento de MedTech 2027-2029 (4.0% contra 4.5%)', s_mtg)
step('Tasa libre de riesgo, betas de pares y peso de la deuda (WACC)', s_wacc)
step('Deuda neta al 27-sep (ya incluye Firefly y Sail) y acciones diluidas', s_liab)
step('Reserva total de talco ($9.0B) en lugar del compromiso de ovario ($5.5B)', s_talc)
assert abs(prev - M1) < 1e-6, (prev, M1)
put('m1_bridge', steps); put('m1_bridge_vals', [x['d'] for x in steps]); put('m1_bridge_sum', sum(x['d'] for x in steps))
put('m1_bridge_rebuild', sep_m1 - 97.56)
put('talc_ps', (TALC - TALC_OV) / SH); put('talc_blend', 0.15 * (TALC - TALC_OV) / SH)

# ======================= 9. Puente del blend: modelo vs precio; anti-circularidad =======================
if PRICE_ENV is None:
    import subprocess, sys
    J = json.loads(subprocess.run([sys.executable, __file__], env={**os.environ, 'JNJ_PRICE': '269.17'}, capture_output=True, text=True, check=True).stdout.split('@@JSON@@')[1])
    put('blend_at_sep_price', J['blend']); put('bridge_price', BL - J['blend']); put('bridge_model', J['blend'] - 199.64)
    put('gap_at_sep_price', (J['blend'] / 269.17 - 1) * 100)
    put('gap_chg', M['blend_gap'] - M['blend_sep_gap'])
    put('gap_chg_price', M['blend_gap'] - (BL / 269.17 - 1) * 100)          # solo por el precio más alto (mismo blend)
    put('gap_chg_model', (BL / 269.17 - 1) * 100 - M['blend_sep_gap'])
    J2 = json.loads(subprocess.run([sys.executable, __file__], env={**os.environ, 'JNJ_PRICE': str(round(PRICE * 1.25, 2))}, capture_output=True, text=True, check=True).stdout.split('@@JSON@@')[1])
    put('anti_m2', J2['m2'] - M['m2']); put('anti_m3', J2['m3'] - M['m3']); put('anti_m4', J2['m4'] - M['m4']); put('anti_m1', J2['m1'] - M['m1'])
    assert M['anti_m2'] == 0 and M['anti_m3'] == 0 and M['anti_m4'] == 0


# Exposición a vencimientos 2026-2033 (fechas Base de la tabla de la Sección 03), ingresos TTM a sep-2026
LOE = [('Simponi', 'SIMPONI', 2026), ('Xarelto', 'XARELTO', 2027), ('Opsumit', 'OPSUMIT', 2028), ('Darzalex', 'DARZALEX', 2029),
       ('Caplyta', 'CAPLYTA', 2029), ('Uptravi', 'UPTRAVI', 2030), ('Tremfya', 'TREMFYA', 2031), ('Invega', 'INVEGA', 2031),
       ('Erleada', 'ERLEADA', 2032), ('Imbruvica', 'IMBRUVICA', 2032), ('Spravato', 'SPRAVATO', 2033)]
put('loe_rows', [dict(n=a, y=y, v=ttm(n) / 1000) for a, n, y in LOE])
put('loe_sum', sum(ttm(n) for _, n, _ in LOE) / 1000); put('loe_share', M['loe_sum'] / M['ttm_rev'] * 100)
put('loe_share_im', M['loe_sum'] / M['ttm_im'] * 100); put('dara_share', M['ttm_darzalex'] / M['ttm_rev'] * 100)
# Innovative Medicine: doce mayores productos o grupos TTM; MedTech por franquicia TTM
IMG = [('Darzalex', 'DARZALEX'), ('Tremfya', 'TREMFYA'), ('Hipertensión pulmonar', 'PULMONARY'), ('Invega (inyectables)', 'INVEGA'),
       ('Erleada', 'ERLEADA'), ('Stelara', 'STELARA'), ('Enf. infecciosas', 'INFECTIOUS'), ('Xarelto', 'XARELTO'),
       ('Carvykti', 'CARVYKTI'), ('Imbruvica', 'IMBRUVICA'), ('Simponi', 'SIMPONI'), ('Spravato', 'SPRAVATO')]
im_rows = sorted([(a, ttm(n) / 1000) for a, n in IMG], key=lambda x: -x[1])
put('im_top', im_rows); put('im_rest', M['ttm_im'] - sum(v for _, v in im_rows))
MTG = [('Cirugía', 'SURGERY'), ('Ortopedia', 'ORTHOPAEDICS'), ('Electrofisiología', 'ELECTROPHYSIOLOGY'), ('Visión', 'VISION'),
       ('Abiomed', 'ABIOMED'), ('Shockwave', 'SHOCKWAVE'), ('Otros cardiovascular', 'OTHER CARDIOVASCULAR')]
put('mt_top', sorted([(a, ttm(n) / 1000) for a, n in MTG], key=lambda x: -x[1]))
put('ortho_ttm_sh', M['ttm_orthopaedics'] / M['ttm_mt'] * 100)
# Precio: doce meses y P/E de hace un año
dd = json.load(open('yh/JNJ.d.json'))['chart']['result'][0]
first = [(datetime.datetime.fromtimestamp(a, datetime.UTC).date().isoformat(), c) for a, c in zip(dd['timestamp'], dd['indicators']['quote'][0]['close']) if c][0]
put('px_1y_date', first[0]); put('px_1y', round(first[1], 2)); put('px_1y_chg', (PRICE / first[1] - 1) * 100)
put('pe_ttm_1y', 185.42 / 10.38)
put('ste_2y', 2 * 0 + M['ste_e26'])
put('q3_onc_g', M['g3_oncology']); put('q3_neuro_g', M['g3_neuroscience']); put('q3_imm_g', M['g3_immunology'])
put('ryb_tec_tal_q3', M['q3_rybrevant'] + M['q3_tecvayli'] + M['q3_talvey'])


# Claves auxiliares del texto
pb, pu = p3('bear'), p3('bull')
put('cm_im_bear30', pb['cm'][2030] * 100); put('cm_im_bull30', pu['cm'][2030] * 100)
put('wacc_im_bear', pb['wacc_im'] * 100); put('wacc_mt_bear', pb['wacc_mt'] * 100)
put('wacc_im_bull', pu['wacc_im'] * 100); put('wacc_mt_bull', pu['wacc_mt'] * 100)
PS = {k: v / SH for k, v in M['sotp'].items()}
PS.update(im_ev=M['im_ev'] / SH, mt_ev=M['mt_ev'] / SH, liab=LIAB / SH)
put('ps', PS); put('shares_dil_m', SH * 1000)
assert abs(sum(M['sotp'].values()) + M['mt_ev'] - LIAB - M['m1_eq']) < 1e-9
put('eps_im_share_pct', EPS_IM_SH * 100); put('ntm_w26_pct', DAYS_LEFT * 100)
put('lly_vs_med', (PEERS['LLY'][0] / M['peer_med'] - 1) * 100)


# ======================= 10. Postura y datos de gráficos =======================
put('stance', 'NEUTRAL, CON SESGO BAJISTA'); assert M['blend_gap'] < -15
put('hist_rev', [78.74, 79.99, 85.16, 88.82, 94.19, round(M['ttm_rev'], 2)])
put('ttm_rev_r', round(M['ttm_rev'], 2))

# Datos de los gráficos (charts_jnj.js)
def R2(v, n=2): return round(float(v), n)
CH = {}
CH['hist'] = [R2(x) for x in M['hist_rev']]
CH['mix_l'] = [a for a, _ in M['im_top']]; CH['mix_v'] = [R2(v) for _, v in M['im_top']]
COL = {'Darzalex': 'navy', 'Tremfya': 'blue', 'Stelara': 'red', 'Erleada': 'blueLight', 'Carvykti': 'blueLight', 'Spravato': 'blueLight'}
CH['mix_c'] = [COL.get(a, 'pale') for a in CH['mix_l']]
CH['mt_l'] = [a for a, _ in M['mt_top']]; CH['mt_v'] = [R2(v) for _, v in M['mt_top']]
MTC = {'Cirugía': 'navy', 'Ortopedia': 'gold', 'Electrofisiología': 'blue', 'Visión': 'blueLight', 'Abiomed': 'blue', 'Shockwave': 'blue'}
CH['mt_c'] = [MTC.get(a, 'pale') for a in CH['mt_l']]
CH['loe_l'] = [f"{r['n']} ({r['y']})" for r in M['loe_rows']]; CH['loe_v'] = [R2(r['v']) for r in M['loe_rows']]
LC = {2026: 'red', 2027: 'red', 2028: 'red'}
CH['loe_c'] = ['navy' if r['n'] == 'Darzalex' else 'blue' if r['n'] == 'Tremfya' else LC.get(r['y'], 'gold') for r in M['loe_rows']]
CH['gm'] = M['gm_q']; CH['rd'] = M['rd_q']; CH['sga'] = M['sga_q']
YRS = ('2022', '2023', '2024', '2025', 'TTM')
CH['cf_ocf'] = [R2(M['cf_rows'][k]['ocf'] / 1000) for k in YRS]
CH['cf_capex'] = [R2(M['cf_rows'][k]['capex'] / 1000) for k in YRS]
CH['cf_fcf'] = [R2(M['cf_rows'][k]['fcf'] / 1000) for k in YRS]
comps = [('JNJ', M['jnj_stats']['pe_f'], 'navy')] + [(k, PEERS[k][0], 'gold' if k == 'LLY' else 'pale') for k in ('LLY', 'ABBV', 'MRK', 'AZN', 'NVS', 'PFE')] \
        + [(k, MEDT[k][0], 'blueLight') for k in ('SYK', 'ABT', 'MDT', 'BDX', 'BSX')]
comps = [comps[0]] + sorted(comps[1:], key=lambda x: -x[1])
CH['comps_l'] = [a for a, _, _ in comps]; CH['comps_v'] = [R2(v) for _, v, _ in comps]; CH['comps_c'] = [c for _, _, c in comps]
CH['est'] = [R2(M['ttm_rev']), R2(M['g_rev_mid'], 1), R2(M['c26_rev']), R2(M['c27_rev'])]
SO = [('MedTech (DCF)', M['mt_ev'], 'gold'), ('Cartera madura IM', M['sotp']['mat'], 'pale'), ('Darzalex', M['sotp']['dara'], 'navy'),
      ('Tremfya', M['sotp']['trem'], 'blue'), ('Oncología en lanzamiento', M['sotp']['onc'], 'blueLight'),
      ('Plataforma I+D post-2040', M['sotp']['plat'], 'pale'), ('Icotyde', M['sotp']['ico'], 'blue'),
      ('Pipeline fase 3 (rNPV)', M['sotp']['ph3'], 'blueLight'), ('Erleada, Spravato, Carvykti y otros', M['sotp']['oth'], 'blueLight'),
      ('Activos adquiridos 2025-26', M['sotp']['acq'], 'pale'), ('I+D corporativa IM (se resta)', -M['sotp']['rd'], 'red'),
      ('Deuda neta, talco y opioides (se resta)', LIAB, 'red')]
CH['sotp_l'] = [a for a, _, _ in SO]; CH['sotp_v'] = [R2(v, 1) for _, v, _ in SO]; CH['sotp_c'] = [c for _, _, c in SO]
CH['ff'] = [[R2(M['m1_bear']), R2(M['m1_bull'])], [R2(M['m2_lo']), R2(M['m2_hi'])], [R2(M['m3_lo']), R2(M['m3_hi'])], [R2(M['pt_lo']), R2(M['pt_hi'])]]
put('ch', CH)

if PRICE_ENV is None:   # septiembre reconstruido (los cuatro métodos, su blend y los escenarios del Método 1)
    import subprocess as _sp, sys as _sys
    chk = {}
    for line in _sp.run([_sys.executable, 'check_sep.py'], capture_output=True, text=True, encoding='utf-8', env={**os.environ, 'PYTHONIOENCODING': 'utf-8'}).stdout.splitlines():
        parts = line.split()
        chk[' '.join(parts[:-5])] = dict(publicado=float(parts[-4]), reconstruido=float(parts[-2]))
    json.dump(dict(fecha_datos='2T 2026 (28-jun-2026)', precio=269.17, publicado=SEP_PUB, reconstruido=SEP,
                   diferencia=M['sep_diff'], metodo1_escenarios=chk, calibracion=S.CAL),
              open('model_sep.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
if PRICE_ENV is None:
    json.dump(M, open('model.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    print('blend', round(BL, 2), 'gap', round(M['blend_gap'], 1), 'M1', round(M1, 2), 'M2', round(M2, 2), 'M3', round(M3, 2), 'M4', M4,
          '| sep M1 rebuilt', round(sep_m1, 2), '| dist', DIST, round(M2X, 2))
else:
    print('@@JSON@@' + json.dumps({k: M[k] for k in ('blend', 'm1', 'm2', 'm3', 'm4')}) + '@@JSON@@')
