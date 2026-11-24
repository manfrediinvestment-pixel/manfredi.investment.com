# Modelo de valuación LLY (Eli Lilly and Company) — todos los números derivados de informes/lly.html salen de acá.
# Marco: informe-salud, Módulo A (pharma): suma de partes por producto hasta la LOE + rNPV del pipeline (15%),
# comparables P/E forward contra 13 pharmas (25%), reversión al P/E propio (35%), consenso (25%).
# Fuentes: 8-K del 29-oct-2026 (comunicado del 3T 2026), 10-Q del 3T 2026 (29-oct-2026), 10-K 2025 (12-feb-2026),
# SEC XBRL companyfacts, Yahoo (precios y ^TNX), Nasdaq (consenso de EPS y precio objetivo, leído desde Chrome),
# stockanalysis.com (P/E forward y beta de pares, consenso de ingresos). Precio de corte: cierre del 12-nov-2026.
# La edición de septiembre (datos al 2T 2026) se reconstruye en sep_params.py (el script original no se guardó):
# model_sep.json guarda sus cuatro métodos recalculados y la diferencia contra lo publicado.
import json, os, copy, statistics as st, datetime
import numpy as np
from sotp import run, YEARS
import sep_params as S
from dcf_inv import dcf, lin_path, implied_g

CUT = '2026-11-12'
TXT = 'LLY_PRICE' not in os.environ
M = {}
def put(k, v): M[k] = v; return v

# ======================= 1. Datos del 3T 2026 (10-Q y comunicado, US$ millones) =======================
Q = ['1T25', '2T25', '3T25', '4T25', '1T26', '2T26', '3T26']
REVQ = put('rev_q', [12729, 15558, 17601, 19292, 19799, 22974, 24397])
MJ = {'3T25': 6515, '3T26': 10723}; ZB = {'3T25': 3588, '3T26': 5352}
TIRZQ = put('tirz_q', [6154, 8580, 10103, 11670, 12822, 14871, 16075])
assert TIRZQ[-1] == MJ['3T26'] + ZB['3T26'] and TIRZQ[2] == MJ['3T25'] + ZB['3T25']
COGSQ = [2224, 2448, 3008, 3372, 3577, 3268, 3933]
RDQ = [2734, 3336, 3466, 3801, 3510, 3819, 4247]
SGAQ = [2469, 2753, 2741, 3131, 2934, 3430, 3125]
IPRDQ = [1571, 154, 656, 529, 584, 2776, 4181]
put('gm_q', [round((1 - c / r) * 100, 1) for c, r in zip(COGSQ, REVQ)])
put('pm_q', [round((r - c - d - s) / r * 100, 1) for r, c, d, s in zip(REVQ, COGSQ, RDQ, SGAQ)])
# Comprobación contra lo que el comunicado publica para el 3T26 (83.9% de margen bruto)
assert M['gm_q'][-1] == 83.9
# Tercer trimestre (comunicado + 10-Q)
put('rev3', 24397); put('rev3_ly', 17601); put('rev3_g', (24397 / 17601 - 1) * 100)
put('cogs3', 3933); put('cogs3_ly', 3008); put('rd3', 4247); put('rd3_ly', 3466); put('sga3', 3125); put('sga3_ly', 2741)
put('iprd3', 4181); put('iprd3_ly', 656); put('oi3', 8608); put('oi3_ly', 7365); put('ni3', 6451); put('ni3_ly', 5583)
put('eps3', 7.22); put('eps3_ly', 6.21); put('epsng3', 7.48); put('epsng3_ly', 7.02); put('iprd_eps3', 4.57); put('iprd_eps3_ly', 0.71)
for k in ('cogs3', 'rd3', 'sga3', 'oi3', 'ni3', 'eps3', 'epsng3'):
    put(k + '_g', (M[k] / M[k + '_ly'] - 1) * 100)
put('gm3', (1 - 3933 / 24397) * 100); put('gm3_ly', (1 - 3008 / 17601) * 100); put('gm3_d', M['gm3'] - M['gm3_ly'])
put('gm3_ng', 84.4); put('rd3_pct', 4247 / 24397 * 100); put('sga3_pct', 3125 / 24397 * 100)
put('epsng_ex_iprd3', 7.48 + 4.57)
put('mj3', 10723); put('mj3_us', 4998); put('mj3_ous', 5725); put('mj3_g', (10723 / 6515 - 1) * 100)
put('mj3_us_g', 41); put('mj3_ous_g', 93)
put('zb3', 5352); put('zb3_us', 5267); put('zb3_g', (5352 / 3588 - 1) * 100); put('zb3_us_g', 48)
put('tirz3', 16075); put('tirz3_g', (16075 / 10103 - 1) * 100); put('tirz3_share', 16075 / 24397 * 100)
put('found3', 184); put('found2', 98); put('found9m', 281); put('kis3', 193); put('kis3_g', 175)
put('jay3', 228); put('ebg3', 202); put('omv3', 114); put('inl3', 73)
put('key_ex_inc3', 228 + 202 + 193 + 114 + 73)                       # Jaypirca, Ebglyss, Kisunla, Omvoh, Inluriyo
put('key_ex_inc3_ly', 143 + 127 + 70 + 65)
put('key_ex_inc3_g', (M['key_ex_inc3'] / M['key_ex_inc3_ly'] - 1) * 100)
put('jard3', 1578); put('jard_ms3', 410); put('jard_ms9m', 910); put('trul3', 904); put('verz3', 1511); put('taltz3', 856)
put('one_off3', 900); put('one_off26', 2000)
# Volumen y precio (10-Q, cambio porcentual contra el 3T25)
VP = put('vp', {'us': dict(vol=41, price=-7, fx=0, tot=34), 'ous': dict(vol=76, price=-29, fx=0, tot=47),
                 'tot': dict(vol=53, price=-15, fx=0, tot=39)})
put('us_price_ex_adj', -10)                                           # CFO en la llamada: −10% sin el ajuste de descuentos
put('us_rev3', 15136); put('ous_rev3', 9261); put('us_share3', 15136 / 24397 * 100)
put('vp_9m', {'vol': 59, 'price': -14, 'fx': 1, 'tot': 46})
# Guía 2026 (comunicado del 29-oct)
put('g_rev_lo', 91.0); put('g_rev_hi', 92.0); put('g_rev_lo_prev', 85.0); put('g_rev_hi_prev', 87.0)
put('g_pm_lo', 52.0); put('g_pm_hi', 52.5); put('g_pm_lo_prev', 49.0); put('g_pm_hi_prev', 50.5)
put('g_eps_lo', 35.00); put('g_eps_hi', 36.00); put('g_eps_lo_prev', 35.50); put('g_eps_hi_prev', 36.50)
put('g_tax_lo', 19.0); put('g_tax_hi', 20.0); put('g_eps_under', 4.07)
put('g_rev_mid', 91.5); put('g_pm_mid', 52.25); put('g_pm_mid_prev', 49.75); put('g_pm_up', 52.25 - 49.75)
REV9M = put('rev9m', 67170)
put('q4_implied', M['g_rev_mid'] * 1000 - REV9M)
# Últimos doce meses (4T25 = año 2025 del 10-K − nueve meses de 2025 del 10-Q; TTM = 4T25 + nueve meses de 2026)
FY25 = dict(rev=65179, cogs=11052, rd=13337, sga=11094, ni=20640, pretax=25731, ocf=16813, capex=7841, div=5384, buy=4108, da=1997, int=895.0)
N25 = dict(rev=45887, cogs=7680, rd=9536, sga=7963, ni=14002, pretax=17465, ocf=13588, capex=5294, div=4039, buy=2600, da=1411, int=672.4)
N26 = dict(rev=67170, cogs=10778, rd=11576, sga=9489, ni=20942, pretax=26503, ocf=27420, capex=8437, div=4635, buy=4334, da=1588, int=1055.0)
TTM = {k: FY25[k] - N25[k] + N26[k] for k in FY25}
assert TTM['rev'] == sum(REVQ[-4:]) and TTM['cogs'] == sum(COGSQ[-4:]) and TTM['rd'] == sum(RDQ[-4:]) and TTM['sga'] == sum(SGAQ[-4:])
put('ttm', TTM)
put('ttm_rev', TTM['rev'] / 1000); put('ttm_gm', (1 - TTM['cogs'] / TTM['rev']) * 100)
put('ttm_iprd', sum(IPRDQ[-4:])); put('ttm_rd_pct', TTM['rd'] / TTM['rev'] * 100)
REV_TTM_PREV = put('ttm_rev_prev', (45043 - 31510) + 45887)   # TTM a sep-2025: 4T24 (2024 − 9M24, XBRL) + 9M25
put('ttm_rev_g', (TTM['rev'] / REV_TTM_PREV - 1) * 100)
put('ttm_fcf', TTM['ocf'] - TTM['capex']); put('ttm_ocfm', TTM['ocf'] / TTM['rev'] * 100); put('ttm_fcfm', M['ttm_fcf'] / TTM['rev'] * 100)
put('ttm_capex_pct', TTM['capex'] / TTM['rev'] * 100)
put('ttm_shr', (TTM['div'] + TTM['buy']) / M['ttm_fcf'] * 100)
put('ebitda', (TTM['pretax'] + TTM['da'] + TTM['int']) / 1000)
EPSQ_NG = {'3T24': 1.18, '4T24': 5.32, '1T25': 3.34, '2T25': 6.31, '3T25': 7.02, '4T25': 7.54, '1T26': 8.56, '2T26': 8.38, '3T26': 7.48}
# EPS GAAP: 1T26 = 9M26 23.42 − 7.94 − 7.22; 4T25 = TTM publicado en septiembre ($29.80) − 3T25 6.21 − 1T26 − 2T26
EPSQ_GAAP = {'4T25': 7.39, '1T26': 8.26, '2T26': 7.94, '3T26': 7.22}
assert abs(sum(EPSQ_GAAP.values()) - (7.39 + 23.42)) < 1e-9
put('ttm_eps_gaap', sum(EPSQ_GAAP.values())); put('ttm_eps_ng', sum(list(EPSQ_NG.values())[-4:]))
put('ttm_ni', TTM['ni'])
# Ingresos por producto TTM (4T25 = 2025 − 9M25; TTM = 4T25 + 9M26), US$ millones
P_FY25 = dict(mj=22966, zb=13542, trul=4276, jard=3431, ocm=4006, verz=5723, oonc=3653, taltz=3563, oimm=1684, neuro=1391, oth=943)
P_9M25 = dict(mj=15556, zb=9281, trul=3239, jard=2663, ocm=2989, verz=4118, oonc=2650, taltz=2511, oimm=1195, neuro=932, oth=752)
P_9M26 = dict(mj=29328, zb=14440, trul=3042, jard=3924, ocm=3143, verz=4286, oonc=3151, taltz=2444, oimm=1611, neuro=1254, oth=546)
assert abs(sum(P_FY25.values()) - 65179) <= 2 and abs(sum(P_9M25.values()) - 45887) <= 2 and abs(sum(P_9M26.values()) - 67170) <= 2   # la tabla redondea cada producto
PT = {k: (P_FY25[k] - P_9M25[k] + P_9M26[k]) / 1000 for k in P_FY25}
assert abs(sum(PT.values()) - M['ttm_rev']) < 0.005
put('prod_ttm', PT); put('tirz_ttm', PT['mj'] + PT['zb']); put('tirz_ttm_share', M['tirz_ttm'] / M['ttm_rev'] * 100)
put('tirz_9m_share', (29328 + 14440) / 67170 * 100); put('inc_9m_share', 66)   # 10-Q: Mounjaro+Zepbound+Foundayo = 66%
put('rest_ttm', M['ttm_rev'] - M['tirz_ttm']); put('cardio_9m', 53877 / 67170 * 100)
put('loe_ttm', PT['trul'] + PT['jard'] + PT['taltz'] + PT['verz']); put('loe_ttm_share', M['loe_ttm'] / M['ttm_rev'] * 100)
put('new_launch_ann', M['key_ex_inc3'] * 4 / 1000)
# Balance (10-Q 3T26, 10-K 2025 y 2024)
BS = put('bs', {'s26': dict(cash=4885, std=2517, ltd=46986, inv=18194, gwi=9874 + 18084, eq=40271, ta=148072),
                'd25': dict(cash=7268, std=1635, ltd=40868, inv=13744, gwi=12419, eq=26535, ta=112476),
                'd24': dict(cash=3268, std=5117, ltd=28527, inv=7589, gwi=11936, eq=14272, ta=78715)})
for k, b in BS.items(): b['nd'] = b['std'] + b['ltd'] - b['cash']
DEBT = put('debt', (BS['s26']['std'] + BS['s26']['ltd']) / 1000); assert abs(DEBT - 49.503) < 1e-9   # = 10-Q, nota 8
ND = put('net_debt', BS['s26']['nd'] / 1000)
put('nd_jun', 45.958); put('nd_chg_9m', ND - BS['d25']['nd'] / 1000); put('nd_lev', ND / M['ebitda'])
put('inv_9m_g', (18194 / 13744 - 1) * 100); put('wip_share', 10688 / 18146 * 100)
put('rebates_liab', 24170); put('rebates_liab_d25', 17382)
put('bd_paid_9m', 18.2); put('capex9m', 8437); put('ocf9m', 27420); put('capex3', 8437 - 5259); put('ocf3', 27420 - 16023)
put('shares_out', 940.745); put('shares_dil', 894.0); put('div_q', 1.73)
# ======================= 2. Mercado y consenso =======================
PRICE = put('price', float(os.environ.get('LLY_PRICE', 1427.28)))   # cierre 12-nov-2026 (Yahoo)
put('price_sep', 1150.99); put('price_move', (PRICE / 1150.99 - 1) * 100)
put('price_oct28', 1288.30); put('price_oct30', 1417.54); put('price_oct30_g', (1417.54 / 1288.30 - 1) * 100)
RF = put('rf', 5.103); BETA = put('beta_raw', 0.39); ERP = put('erp', 5.0)                 # ^TNX 12-nov; beta 5 años (stockanalysis)
BETA_ADJ = put('beta_adj', 0.67 * BETA + 0.33); KE = put('ke', RF + BETA_ADJ * ERP)
TAX = put('tax', 19.5); KD = put('kd', 5.1); KD_AT = put('kd_at', KD * (1 - TAX / 100))
MCAP = put('mcap', PRICE * M['shares_dil'] / 1000); WD = put('wd', DEBT / (DEBT + MCAP) * 100)
WACC = put('wacc', (1 - WD / 100) * KE + WD / 100 * KD_AT)
put('div_yield', 4 * M['div_q'] / PRICE * 100)
C26, C27, C28 = put('c26', 35.70), put('c27', 50.71), put('c28', 58.72)       # Nasdaq (8, 8 y 3 estimaciones), 12-nov-2026
put('c26_n', 8); put('c27_n', 8); put('c27_hi', 59.81); put('c27_lo', 44.40); put('c27_up4w', 7)
put('c27_sep', 47.34); put('c27_sa', 50.64); put('c26_sa', 35.39)
put('rev_c26', 91.67); put('rev_c27', 106.49); put('rev_c27_sep', 94.29)    # stockanalysis (S&P Global)
put('rev_c27_g', (M['rev_c27'] / M['rev_c26'] - 1) * 100)
EPS9M = put('eps9m_ng', 24.41)
NTM = put('eps_ntm', (C26 - EPS9M) + 0.75 * C27)                                 # 4T26 implícito + tres trimestres de 2027
put('q4_eps_impl', C26 - EPS9M); put('pe_ntm', PRICE / NTM); put('pe_27', PRICE / C27)
# ======================= 3. Método 1 — suma de partes por producto + rNPV =======================
# Formas calibradas de septiembre (sep_params.CAL) + cambios del 3T26, cada uno con su fuente.
CM0 = put('cm0', (M['ocf9m'] / REV9M + N26['rd'] / REV9M * (1 - TAX / 100)) * 100)   # 9M26: OCF + I+D después de impuestos
put('ocf9m_pct', M['ocf9m'] / REV9M * 100); put('rd9m_pct', N26['rd'] / REV9M * 100); put('capex9m_pct', M['capex9m'] / REV9M * 100)
CX0 = M['capex9m_pct'] / 100; RD0 = M['rd9m_pct'] / 100
put('cm30', 55.0 + M['g_pm_up']); put('cm30_bear', 52.0 + M['g_pm_up']); put('cm30_bull', 57.0 + M['g_pm_up'])
# Nivel del 4T26 (de 2026 solo cuenta el cuarto trimestre): mezcla del 3T26 (Jardiance sin hitos) escalada al 4T implícito en la guía
Q3MIX = dict(tirz=16.075, found=0.184, jard=1.578 - 0.410, trul=0.904, verz=1.511, taltz=0.856)
Q3MIX['rest'] = 24.397 - 0.410 - sum(Q3MIX.values())
sc = (M['q4_implied'] / 1000) / sum(Q3MIX.values()); put('q4_scale', sc)
STUB = {k: v * sc * 4 for k, v in Q3MIX.items()}; put('stub', STUB)
TIRZ26 = put('tirz26e', (29328 + 14440) / 1000 + STUB['tirz'] / 4)            # 2026 calendario estimado
T27 = put('tirz27', TIRZ26 * (1 + M['rev_c27_g'] / 100))                       # crece como el consenso de ingresos 2027
SEPB = S.scen('base')
RATIO = {k: v for k, v in dict(plat=65.0 / 60.5, b27=57.0 / 60.5, b35=48.0 / 65.0, u27=62.0 / 60.5, u30=72.0 / 65.0).items()}
TP = put('tirz_plateau', T27 * RATIO['plat'])
put('tirz27_bear', T27 * RATIO['b27']); put('tirz35_bear', TP * RATIO['b35']); put('tirz27_bull', T27 * RATIO['u27']); put('tirz30_bull', TP * RATIO['u30'])
PH3_NEW = ['brenipatida (depresión mayor)', 'sofetabart mipitecán (cáncer de ovario)']
put('ph3_n', 7); put('ph3_n_sep', 5)
ACQ_NEW = put('acq_new', 2.610 + 0.954)                                       # AtaiBeckley + Curevo (10-Q, nota 4)
ACQ = put('acq', 17.52 + ACQ_NEW)
def p3(name, wacc=None, pos=None, loe2039=False, renewal=False):
    p = S.scen(name)
    p['wacc'] = (wacc if wacc is not None else WACC / 100) + {'base': 0, 'bear': 0.0075, 'bull': -0.0075}[name]
    p['tax'] = TAX / 100; p['net_debt'] = ND; p['acq'] = ACQ; p['ph3_n'] = 7
    c30 = {'base': M['cm30'], 'bear': M['cm30_bear'], 'bull': M['cm30_bull']}[name] / 100
    p['cm'] = {2026: CM0 / 100, 2030: c30}
    p['capex'] = {2026: CX0, 2030: {'base': 0.06, 'bear': 0.07, 'bull': 0.055}[name]}
    p['rd'] = {2026: RD0, 2030: {'base': 0.155, 'bear': 0.165, 'bull': 0.15}[name]}
    if name == 'base': tp = {2026: STUB['tirz'], 2027: T27, 2030: TP, 2035: TP}
    if name == 'bear': tp = {2026: STUB['tirz'], 2027: M['tirz27_bear'], 2035: M['tirz35_bear']}
    if name == 'bull': tp = {2026: STUB['tirz'], 2027: M['tirz27_bull'], 2030: M['tirz30_bull'], 2038: M['tirz30_bull']}
    p['tirz_path'] = tp
    fp = dict(p['found_path']); fp[2026] = STUB['found']; p['found_path'] = fp
    p['rest0'] = STUB['rest']
    leg = copy.deepcopy(p['leg'])
    for k in ('trul', 'jard', 'taltz', 'verz'): leg[k][2026] = STUB[k]
    p['leg'] = leg
    if pos is not None: p['reta_pos'] = pos
    if loe2039:
        p['tirz_loe'] = 2039; t = dict(p['tirz_path']); t[2038] = TP; p['tirz_path'] = t
    if renewal: p['renewal'] = True
    return p
R = {s: run(p3(s)) for s in ('base', 'bear', 'bull')}
B = R['base']
put('m1', B['fv']); put('m1_bear', R['bear']['fv']); put('m1_bull', R['bull']['fv'])
put('m1_ev', B['ev']); put('m1_eq', B['eq'])
CMP = B['C']
put('sotp', {k: v for k, v in CMP.items()}); put('sotp_ps', {k: v / M['shares_dil'] * 1000 for k, v in CMP.items()})
put('nd_ps', ND / M['shares_dil'] * 1000); put('ev_ps', B['ev'] / M['shares_dil'] * 1000)
for s in ('base', 'bear', 'bull'):
    put(f'rev30_{s}', R[s]['tot'][2030]); put(f'fcfm30_{s}', R[s]['fcfm'][2030] * 100)
    put(f'plat_share_{s}', R[s]['C']['platform'] / R[s]['ev'] * 100)
put('rev27_model', B['tot'][2027]); put('rev31_base', B['tot'][2031])
put('inc30', sum(B['R'][k][2030] for k in ('tirz', 'found', 'reta'))); put('inc35', sum(B['R'][k][2035] for k in ('tirz', 'found', 'reta')))
put('wacc_bear', WACC + 0.75); put('wacc_bull', WACC - 0.75)
put('m1_2039', run(p3('base', loe2039=True))['fv']); put('m1_renewal', run(p3('base', renewal=True))['fv'])
put('m1_renewal_gap', (M['m1_renewal'] / PRICE - 1) * 100)
put('m1_ev_w', 0.25 * M['m1_bear'] + 0.45 * M['m1'] + 0.30 * M['m1_bull'])
GW = [WACC / 100 + d for d in (-0.01, -0.005, 0, 0.005, 0.01)]; GP = [0.50, 0.70, 0.906, 0.95, 1.00]
put('grid_w', [w * 100 for w in GW]); put('grid_p', [p * 100 for p in GP])
put('grid', [[run(p3('base', wacc=w, pos=q))['fv'] for q in GP] for w in GW])
assert abs(M['grid'][2][2] - M['m1']) < 1e-9
# ======================= 4. DCF de referencia ("renovación perpetua") y DCF inverso =======================
put('dcf_rev0', M['g_rev_mid']); put('dcf_g0', M['rev_c27_g']); put('dcf_g1', 3.5)
put('dcf_m0', (M['ocf9m'] - M['capex9m']) / REV9M * 100); put('dcf_m1', 36.0 + M['g_pm_up'])
MP = lin_path(M['dcf_m0'] / 100, M['dcf_m1'] / 100, 6)
D = dcf(M['dcf_rev0'], lin_path(M['dcf_g0'] / 100, 0.035, 5), MP, WACC / 100, 0.03, ND, M['shares_dil'] / 1000)
put('dcf_fv', D['fv']); put('dcf_tv', D['tv_share'] * 100)
G = implied_g(PRICE, M['dcf_rev0'], MP, WACC / 100, 0.03, ND, M['shares_dil'] / 1000)
put('dcf_impl_g', G * 100); put('dcf_impl_rev31', M['dcf_rev0'] * (1 + G) ** 5)
put('dcf_impl_vs_base', (M['dcf_impl_rev31'] / M['rev31_base'] - 1) * 100)
put('dcf_impl_vs_c27', M['dcf_impl_rev31'] / M['rev_c27'])
# ======================= 5. Método 2 — comparables (13 pharmas, P/E forward de stockanalysis, 12-nov-2026) =======================
PEERS = put('peers', {'JNJ': 25.45, 'ABBV': 18.72, 'AMGN': 19.22, 'MRK': 17.45, 'GILD': 20.14, 'NVS': 16.65, 'AZN': 16.74,
                      'REGN': 11.83, 'NVO': 12.26, 'PFE': 10.18, 'GSK': 10.46, 'BMY': 9.67, 'SNY': 9.77})
PEER_X = put('peer_x', {'LLY': dict(pe=30.43, peg=1.46, eve=28.29, dy=0.48), 'JNJ': dict(pe=25.45, peg=3.55, eve=20.58, dy=1.89),
                        'ABBV': dict(pe=18.72, peg=1.38, eve=18.56, dy=2.47), 'MRK': dict(pe=17.45, peg=3.96, eve=13.78, dy=2.31),
                        'AZN': dict(pe=16.74, peg=None, eve=14.67, dy=1.75), 'NVO': dict(pe=12.26, peg=None, eve=6.99, dy=3.15),
                        'PFE': dict(pe=10.18, peg=None, eve=8.56, dy=5.97)})
FIVE = ['JNJ', 'ABBV', 'MRK', 'AZN', 'NVO', 'PFE']
put('six_avg_pe', st.mean(PEER_X[k]['pe'] for k in FIVE)); put('six_avg_eve', st.mean(PEER_X[k]['eve'] for k in FIVE))
put('six_avg_dy', st.mean(PEER_X[k]['dy'] for k in FIVE))
put('six_avg_pe_xnvo', st.mean(PEER_X[k]['pe'] for k in FIVE if k != 'NVO'))
v = sorted(PEERS.values()); put('peer_q3', float(np.percentile(v, 75))); put('peer_med', float(np.percentile(v, 50))); put('peer_max', max(v))
assert M['peer_q3'] == PEERS['ABBV'] and M['peer_med'] == PEERS['NVS']
vx = sorted(x for k, x in PEERS.items() if k != 'NVO'); put('peer_q3_xnvo', float(np.percentile(vx, 75)))
M2 = put('m2', M['peer_q3'] * C27 / (1 + KE / 100))
put('m2_lo', M['peer_med'] * NTM); put('m2_hi', M['peer_max'] * C27 / (1 + KE / 100))
put('m2_xnvo', M['peer_q3_xnvo'] * C27 / (1 + KE / 100))
put('lly_prem_q3', (PEER_X['LLY']['pe'] / M['peer_q3'] - 1) * 100); put('lly_prem_med', (PEER_X['LLY']['pe'] / M['peer_med'] - 1) * 100)
put('lly_prem_six', (PEER_X['LLY']['pe'] / M['six_avg_pe'] - 1) * 100)
# ======================= 6. Método 3 — reversión al P/E propio (cuatro cierres trimestrales, EPS no-GAAP TTM) =======================
REV = put('rev_rows', [dict(d='31-dic-2025', px=1074.68, eps=24.21), dict(d='31-mar-2026', px=919.77, eps=29.43),
                       dict(d='30-jun-2026', px=1199.43, eps=31.50), dict(d='30-sep-2026', px=1157.08, eps=31.96)])
assert abs(REV[-1]['eps'] - M['ttm_eps_ng']) < 1e-9
for r in REV: r['pe'] = r['px'] / r['eps']
put('rev_pe', st.mean(r['pe'] for r in REV)); M3 = put('m3', M['rev_pe'] * M['ttm_eps_ng'])
put('m3_lo', min(r['pe'] for r in REV) * M['ttm_eps_ng']); put('m3_hi', max(r['pe'] for r in REV) * M['ttm_eps_ng'])
# ======================= 7. Método 4 — consenso (Nasdaq, 12-nov-2026) =======================
M4 = put('m4', 1515.22); put('m4_lo', 940.0); put('m4_hi', 1700.0); put('m4_n', 24); put('m4_buy', 22); put('m4_hold', 1); put('m4_sell', 1)
put('m4_sa', 1460.0); put('m4_sa_med', 1570.0); put('m4_sep', 1325.0); put('m4_oct1', 1149.85)
# ======================= 8. Blend =======================
W = {'m1': 0.15, 'm2': 0.25, 'm3': 0.35, 'm4': 0.25}
for k, w in W.items(): put(k + '_ap', M[k] * w)
BL = put('blend', sum(M[k] * w for k, w in W.items())); put('blend_gap', (BL / PRICE - 1) * 100)
put('indep', (0.15 * M['m1'] + 0.25 * M['m2']) / 0.40); put('anch', (0.35 * M['m3'] + 0.25 * M['m4']) / 0.60)
put('indep_gap', (M['indep'] / PRICE - 1) * 100); put('anch_gap', (M['anch'] / PRICE - 1) * 100)
put('blend_xnvo', BL + 0.25 * (M['m2_xnvo'] - M['m2'])); put('blend_xnvo_gap', (M['blend_xnvo'] / PRICE - 1) * 100)
put('blend_xcons', (0.15 * M['m1'] + 0.25 * M['m2'] + 0.35 * M['m3']) / 0.75); put('blend_xcons_gap', (M['blend_xcons'] / PRICE - 1) * 100)
# ======================= 9. Septiembre recalculado y puente =======================
SEP_PUB = dict(m1=386.44, m2=750.91, m3=1168.81, m4=1325.00, blend=986.03, price=1150.99, bear=221.03, bull=643.14,
               r2039=430.97, renewal=662.39, dcf=723.66)
sb = run(S.scen('base')); sbear = run(S.scen('bear')); sbull = run(S.scen('bull'))
s2039 = S.scen('base'); s2039['tirz_loe'] = 2039; t = dict(s2039['tirz_path']); t[2038] = 65.0; s2039['tirz_path'] = t
sren = S.scen('base'); sren['renewal'] = True
KE_S = 5.11 + (0.67 * 0.50 + 0.33) * 5.0
SEP = dict(m1=sb['fv'], bear=sbear['fv'], bull=sbull['fv'], r2039=run(s2039)['fv'], renewal=run(sren)['fv'],
           m2=17.20 * 47.34 / (1 + KE_S / 100),
           m3=st.mean([763.00 / 21.99, 1074.68 / 24.21, 919.77 / 29.43, 1199.43 / 31.50]) * 31.50, m4=1325.00,
           dcf=dcf(86.6, lin_path(0.074, 0.035, 5), lin_path(0.275, 0.36, 6), 0.0822, 0.03, 45.958, 0.894)['fv'])
SEP['blend'] = 0.15 * SEP['m1'] + 0.25 * SEP['m2'] + 0.35 * SEP['m3'] + 0.25 * SEP['m4']
SEP['components'] = {k: v for k, v in sb['C'].items()}
SEP['diff_pct'] = {k: (SEP[k] / SEP_PUB[k] - 1) * 100 for k in SEP_PUB if k in SEP}
json.dump(dict(rebuilt=SEP, published=SEP_PUB), open('model_sep.json', 'w'), indent=1, default=float)
put('sep_rebuilt_m1', SEP['m1']); put('sep_m1_diff', SEP['diff_pct']['m1']); put('sep_bear_diff', SEP['diff_pct']['bear'])
put('sep_bull_diff', SEP['diff_pct']['bull']); put('sep_ren_diff', SEP['diff_pct']['renewal']); put('sep_dcf_diff', SEP['diff_pct']['dcf'])
put('sep_blend_diff', SEP['blend'] - SEP_PUB['blend'])
assert abs(SEP['m2'] - 750.91) < 0.01 and abs(SEP['m3'] - 1168.81) < 0.05 and abs(SEP['diff_pct']['m1']) < 0.5
put('blend_sep', SEP_PUB['blend']); put('blend_sep_gap', (SEP_PUB['blend'] / SEP_PUB['price'] - 1) * 100)
put('blend_chg', BL - SEP_PUB['blend']); put('blend_chg_pct', (BL / SEP_PUB['blend'] - 1) * 100)
for k in ('m1', 'm2', 'm3', 'm4'):
    put(k + '_sep', SEP_PUB[k]); put(k + '_chg', M[k] - SEP_PUB[k]); put(k + '_chg_ap', (M[k] - SEP_PUB[k]) * W[k])
# Puente de M1: se aplica cada cambio de a uno sobre la reconstrucción de septiembre (orden fijo)
steps = []; base_p = S.scen('base'); cur = run(base_p)['fv']
p_cur = copy.deepcopy(base_p)
def step(label, upd):
    global cur
    for k, v in upd(p_cur).items(): p_cur[k] = v
    nv = run(p_cur)['fv']; steps.append(dict(label=label, d=nv - cur)); cur = nv
p_final = p3('base')
step('Tirzepatida: 2027 y meseta anclados en el consenso 2027', lambda p: dict(tirz_path={2026: p['tirz_path'][2026], 2027: T27, 2030: TP, 2035: TP}))
step('Margen de contribución (9M26) y meta 2030 (+2.5 pp, guía)', lambda p: dict(cm=p_final['cm'], capex=p_final['capex'], rd=p_final['rd'], tax=p_final['tax']))
step('Nivel del 4T26 (resto, legados, Foundayo, 2026 de tirzepatida)', lambda p: dict(rest0=p_final['rest0'], leg=p_final['leg'], found_path=p_final['found_path'], tirz_path=p_final['tirz_path']))
step('Fase 3: de 5 a 7 activos', lambda p: dict(ph3_n=7))
step('Compras del 3T a costo (AtaiBeckley, Curevo)', lambda p: dict(acq=ACQ))
step('Deuda neta al 30-sep', lambda p: dict(net_debt=ND))
step('WACC (Treasury, beta y pesos)', lambda p: dict(wacc=p_final['wacc']))
assert abs(cur - M['m1']) < 1e-6, (cur, M['m1'])
put('m1_bridge', steps); put('m1_bridge_rebuild', SEP['m1'] - SEP_PUB['m1'])
# Puente del blend: modelo (todos los métodos) vs precio (efecto del precio solo en los pesos del WACC)
if TXT:
    import subprocess, sys
    o = subprocess.run([sys.executable, __file__], env=dict(os.environ, LLY_PRICE='1150.99'), capture_output=True, text=True, check=True)
    J = json.loads(open('model_pricesep.json', encoding='utf-8').read())
    put('blend_at_sep_price', J['blend']); put('bridge_price', BL - J['blend']); put('bridge_model', J['blend'] - SEP_PUB['blend'])
    put('gap_at_sep_price', (J['blend'] / 1150.99 - 1) * 100)
    o = subprocess.run([sys.executable, __file__], env=dict(os.environ, LLY_PRICE=str(PRICE * 1.25)), capture_output=True, text=True, check=True)
    J2 = json.loads(open('model_pricesep.json', encoding='utf-8').read())
    put('anti_m2', J2['m2'] - M['m2']); put('anti_m3', J2['m3'] - M['m3']); put('anti_m4', J2['m4'] - M['m4']); put('anti_m1', J2['m1'] - M['m1'])
    assert M['anti_m2'] == 0 and M['anti_m3'] == 0 and M['anti_m4'] == 0
    os.remove('model_pricesep.json')

# ======================= 10b. Derivados para el texto y los gráficos =======================
PTm = M['prod_ttm']
put('area_ttm', dict(cardio=PTm['mj'] + PTm['zb'] + PTm['trul'] + PTm['jard'] + PTm['ocm'], onc=PTm['verz'] + PTm['oonc'],
                     imm=PTm['taltz'] + PTm['oimm'], neuro=PTm['neuro'], oth=PTm['oth']))
put('area_share', {k: v / M['ttm_rev'] * 100 for k, v in M['area_ttm'].items()})
put('hist', [21.22, 19.97, 21.49, 22.32, 24.54, 28.32, 28.54, 34.12, 45.04, 65.18, round(M['ttm_rev'], 2)])
put('rev_q_b', [v / 1000 for v in REVQ]); put('tirz_q_b', [v / 1000 for v in TIRZQ])
put('ttm_b', {k: v / 1000 for k, v in TTM.items()})
put('ttm_fcf_b', M['ttm_fcf'] / 1000)
put('verz3_g', (1511 / 1470 - 1) * 100); put('trul3_g', (904 / 1052 - 1) * 100); put('taltz3_g', (856 / 902 - 1) * 100); put('jard3_g', (1578 / 959 - 1) * 100)
put('found_q_g', (184 / 98 - 1) * 100)
put('m1_gap', (M['m1'] / PRICE - 1) * 100); put('m2_gap', (M['m2'] / PRICE - 1) * 100); put('m3_gap', (M['m3'] / PRICE - 1) * 100); put('m4_gap', (M['m4'] / PRICE - 1) * 100)
put('m1_frac', M['m1'] / PRICE * 100); put('m2_frac', M['m2'] / PRICE * 100)
put('m3_pe_now', PRICE / M['ttm_eps_ng'])
put('pe27_vs_jnj', M['pe_27'])
put('cash_b', BS['s26']['cash'] / 1000); put('nd_chg_9m_b', M['nd_chg_9m'])
put('tirz_y', TIRZ26); put('tirz26_g', (TIRZ26 / ((15556 + 9281 + (22966 + 13542 - 15556 - 9281)) / 1000) - 1) * 100)
put('tirz25', (22966 + 13542) / 1000)
put('rev_c27_vs_sep', (M['rev_c27'] / M['rev_c27_sep'] - 1) * 100); put('c27_vs_sep', (C27 / M['c27_sep'] - 1) * 100)
put('m1_bridge_sum', sum(x['d'] for x in M['m1_bridge']))
put('m1_bridge_vals', [x['d'] for x in M['m1_bridge']])
put('sotp_ev_ps', B['ev'] / M['shares_dil'] * 1000)
put('m1_to_ren', M['m1_renewal'] / PRICE * 100)
put('grid_min', min(min(r) for r in M['grid'])); put('grid_max', max(max(r) for r in M['grid']))
put('div_y', 4 * 1.73); put('rd_es3', 1663); put('rd_ls3', 2584)
put('g_rev_g_lo', (M['g_rev_lo'] / 65.179 - 1) * 100); put('g_rev_g_hi', (M['g_rev_hi'] / 65.179 - 1) * 100); put('rev_c26_g', (M['rev_c26'] / 65.179 - 1) * 100)
MIXN = dict(mj='Mounjaro', zb='Zepbound', verz='Verzenio', jard='Jardiance', ocm='Otros cardiometabólicos', oonc='Otros oncología',
            trul='Trulicity', taltz='Taltz', oimm='Otros inmunología', neuro='Neurociencia', oth='Otros')
order = sorted(PTm, key=lambda k: -PTm[k])
put('mix_labels', [MIXN[k] for k in order]); put('mix_values', [round(PTm[k], 2) for k in order]); put('mix_keys', order)
put('loe_values', [round(PTm[k], 2) for k in ('trul', 'jard', 'taltz', 'verz')] + [round(M['tirz_ttm'], 2)])
put('cash_ocf', [7.37, 7.59, 4.24, 8.82, 16.81, round(TTM['ocf'] / 1000, 2)]); put('cash_capex', [1.31, 1.85, 3.45, 5.06, 7.84, round(TTM['capex'] / 1000, 2)])
put('cash_fcf', [round(a - b, 2) for a, b in zip(M['cash_ocf'], M['cash_capex'])])
put('comps_values', [PEER_X[k]['pe'] for k in ['LLY'] + FIVE])
put('est_values', [round(M['ttm_rev'], 2), M['g_rev_mid'], M['rev_c26'], M['rev_c27']])
put('sotp_chart', [round(CMP[k], 1) for k in ('tirz', 'rest', 'platform', 'reta', 'found', 'ph3', 'legacy', 'acq')] + [round(-CMP['rd'], 1), round(ND, 1)])
put('vp_chart', [VP['us']['vol'], VP['us']['price'], VP['ous']['vol'], VP['ous']['price'], VP['tot']['vol'], VP['tot']['price']])
put('ranges', [[M['m1_bear'], M['m1_bull']], [M['m2_lo'], M['m2_hi']], [M['m3_lo'], M['m3_hi']], [M['m4_lo'], M['m4_hi']]])
# ======================= 10. Frases del texto atadas a números =======================
if TXT:
    assert M['blend_gap'] < -15 and M['m1'] < M['m2'] < M['m3'] < M['m4']
    assert M['dcf_impl_g'] > 15
    assert M['m3'] < PRICE < M['m4'] and 0.30 < M['m1'] / PRICE < 0.37 and M['m2'] / PRICE < 2 / 3   # "un tercio", "ni dos tercios", "solo el consenso"
    assert M['mj3_ous'] > M['mj3_us'] and 99.5 < M['key_ex_inc3_g'] < 100.5 and M['new_launch_ann'] / M['ttm_rev'] < 0.04
    assert M['anch_gap'] < 0 and M['m1_renewal'] < PRICE and M['tirz_9m_share'] < 66 and M['m4'] - M['m4_sa'] < 60
    assert abs(M['m1_renewal_gap'] + 42) < 1 and M['pe_27'] > M['peer_x']['JNJ']['pe'] and M['m3_pe_now'] > max(r['pe'] for r in REV)
    assert M['rd3_g'] > 14.5 and M['sga3_g'] < M['rev3_g'] and abs(M['gm3_d'] - 1.0) < 0.05 and M['peer_x']['NVO']['pe'] < M['peer_med']
out = 'model.json' if TXT else 'model_pricesep.json'
json.dump(M, open(out, 'w', encoding='utf-8'), indent=1, default=float, ensure_ascii=False)
print(out, 'blend', round(BL, 2), 'gap', round(M['blend_gap'], 1), 'M1', round(M['m1'], 2), 'M2', round(M['m2'], 2), 'M3', round(M['m3'], 2), 'M4', M['m4'])
