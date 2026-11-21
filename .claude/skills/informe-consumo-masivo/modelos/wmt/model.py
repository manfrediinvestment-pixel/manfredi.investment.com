# Modelo de valuación WMT (Walmart Inc.) — todos los números derivados del informe salen de acá.
# Marco: informe-consumo-masivo, bloque de RETAIL (ventas comparables tráfico vs. ticket, e-commerce, membresías,
# publicidad, rotación de inventario, ROIC). Año fiscal cerrado el 31 de enero: FY2027 = feb-2026 a ene-2027.
# Fuentes: 10-K FY2026 (31-ene-2026), 10-Q 1T/2T FY2027, comunicado 8-K ítem 2.02 del 3T FY2027 (19-nov-2026; el 10-Q del
# 3T todavía no está presentado), comunicados 8-K 2.02 desde el 1T FY2017, proxy 2026, SEC XBRL companyfacts
# (data/annual.json), Yahoo Finance, stockanalysis (S&P Global), FactSet Earnings Insight, Walmex (reportes 4T25 y 2T26).
# Precios: cierre del viernes 20-nov-2026 (data/comun_2026-11-20.json, bloque compartido con DIS).
# Edición anterior: cierre del 29-sep-2026, datos al 2T FY2027 (blend $82.75).
import json, datetime, statistics as st
from pathlib import Path
HERE = Path(__file__).resolve().parent
M = {}
def put(k, v): M[k] = v; return v

# ---------------- Mercado (cierre 20-nov-2026) ----------------
PRICE = put('price', 127.95)
RF = put('rf', 4.912)                 # ^TNX cierre 20-nov-2026
ERP = put('erp', 5.0)                 # prima fija del marco (referencia: Damodaran implícita 1-nov-2026 4.41%)
put('erp_dam', 4.41)
SH_DIL = put('sh_dil', 7952.0)        # diluidas promedio 3T FY27 (millones, comunicado)
SH_OUT = put('sh_out', 7931.0)        # básicas promedio 3T FY27 (el 10-Q con la cifra de portada todavía no está presentado)
MKT_CAP = put('mkt_cap', PRICE*SH_OUT/1000)     # US$ miles de millones
put('hi52', 135.16); put('lo52', 102.15)
put('px_apr26', 131.93)               # cierre de abril de 2026 (máximo de cierre mensual)
PRICE_SEP = put('price_sep', 106.80); BLEND_SEP = put('blend_sep', 82.75)   # edición anterior (cierre 29-sep-2026)

# ---------------- Consenso de EPS (stockanalysis / S&P Global, 21-nov-2026) ----------------
# Cambio de fuente: la API de Nasdaq/Zacks dejó de responder a pedidos automáticos; S&P Global para WMT y todos los pares.
C27, C28 = put('c27', 2.88784), put('c28', 3.23346)
put('c27_n', 36)
Q_CONS = {'4T27': 0.77834, '1T28': 0.73473}            # los dos trimestres siguientes (consenso trimestral)
M['q_cons'] = Q_CONS
GUIDE_LO, GUIDE_HI = put('guide_lo', 2.84), put('guide_hi', 2.89)
put('guide_mid', (GUIDE_LO+GUIDE_HI)/2)
put('guide_orig_lo', 2.75); put('guide_orig_hi', 2.85)
put('guide_aug_lo', 2.80); put('guide_aug_hi', 2.87)
# EPS de los próximos cuatro trimestres (4T FY27 a 3T FY28 = nov-2026 a oct-2027): consenso de los dos trimestres siguientes +
# la mitad del consenso del año fiscal siguiente (2T y 3T FY28). Misma regla para WMT y para los pares (S&P Global publica
# gratis solo dos trimestres). No incluye el 2T FY2027, el trimestre de las devoluciones de aranceles.
NTM = put('eps_ntm', Q_CONS['4T27'] + Q_CONS['1T28'] + 0.5*C28)
put('pe_ntm_now', PRICE/NTM)
put('pe_c28', PRICE/C28); put('pe_c27', PRICE/C27)
put('eps_g28', (C28/C27-1)*100)

# ---------------- EPS ajustado trimestral (comunicados 8-K 2.02; antes del split 3x1 de feb-2024 se divide por 3) ----------------
EPS_RAW = {2017: [0.98, 1.07, 0.98, 1.30], 2018: [1.00, 1.08, 1.00, 1.33], 2019: [1.14, 1.29, 1.08, 1.41],
           2020: [1.13, 1.27, 1.16, 1.38], 2021: [1.18, 1.56, 1.34, 1.39], 2022: [1.69, 1.78, 1.45, 1.53],
           2023: [1.30, 1.77, 1.50, 1.71], 2024: [1.47, 1.84, 1.53, 1.80], 2025: [0.60, 0.67, 0.58, 0.66],
           2026: [0.61, 0.68, 0.62, 0.74], 2027: [0.66, 0.81, 0.65]}
FY_ADJ = {2017: 4.32, 2018: 4.42, 2019: 4.91, 2020: 4.93, 2021: 5.48, 2022: 6.46, 2023: 6.29, 2024: 6.65, 2025: 2.51, 2026: 2.64}
for y, v in FY_ADJ.items():
    assert abs(sum(EPS_RAW[y]) - v) < 0.025, (y, sum(EPS_RAW[y]), v)
assert abs(sum(EPS_RAW[2027]) - 2.12) < 0.005          # EPS ajustado de nueve meses del comunicado del 3T: $2.12
EPS = {y: [x/3 if y <= 2024 else x for x in q] for y, q in EPS_RAW.items()}
EPS[2027] = EPS[2027] + [Q_CONS['4T27']]
EPS[2028] = [Q_CONS['1T28'], 0.25*C28, 0.25*C28]       # 2T y 3T FY28: mitad del consenso anual (misma regla que el NTM)
M['eps_fy'] = {str(y): (FY_ADJ[y]/3 if y <= 2024 else FY_ADJ[y]) for y in FY_ADJ}
M['eps_fy']['2027'] = C27; M['eps_fy']['2028'] = C28
put('eps_9m27', sum(EPS[2027][:3])); put('eps_9m26', sum(EPS[2026][:3]))
put('eps_9m_g', (M['eps_9m27']/M['eps_9m26']-1)*100)
put('eps_3q27', 0.65); put('eps_3q26', 0.62); put('eps_3q_g', (0.65/0.62-1)*100)
put('eps_2q27', 0.81); put('eps_2q27_guide_hi', 0.74)
put('tariff_eps_q2', 0.81 - 0.74)                  # EPS del 2T por encima del techo de la guía (efecto neto máximo de las devoluciones)
put('guide_raise_mid', (GUIDE_LO+GUIDE_HI)/2 - (2.75+2.85)/2)
put('guide_raise_mid_aug', (GUIDE_LO+GUIDE_HI)/2 - (2.80+2.87)/2)
put('q4_implied_lo', GUIDE_LO - 2.12); put('q4_implied_hi', GUIDE_HI - 2.12)   # 4T implícito en la guía
put('c27_vs_guide', C27 - M['guide_mid'])

# ---------------- Ventas comparables sin combustible (comunicados trimestrales) ----------------
# Serie de 14 trimestres: se agrega el 3T FY27 y sale el 1T FY24. Sam's Club revisó en el 3T FY27 ("immaterial correction",
# sin cambio en la comparable) el tráfico y el ticket de 3T FY26 a 2T FY27: 3.4/0.4, 5.0/−1.0, 5.1/−1.2, 5.8/−1.4
# (antes 3.9/−0.1, 5.3/−1.3, 6.2/−2.2, 7.0/−2.5). Fuente: presentación financiera del 3T FY27, "Supplemental information".
QL = ['2T24', '3T24', '4T24', '1T25', '2T25', '3T25', '4T25', '1T26', '2T26', '3T26', '4T26', '1T27', '2T27', '3T27']
US = dict(comp=[6.4, 4.9, 4.0, 3.8, 4.2, 5.3, 4.6, 4.5, 4.6, 4.5, 4.6, 4.1, 2.6, 2.9],
          trx=[2.9, 3.4, 4.3, 3.8, 3.6, 3.1, 2.8, 1.6, 1.5, 1.8, 2.6, 3.0, 1.5, 1.5],
          tkt=[3.4, 1.5, -0.3, 0.0, 0.6, 2.1, 1.8, 2.8, 3.1, 2.7, 2.0, 1.1, 1.1, 1.4],
          ecom=[230, 300, 240, 280, 300, 290, 290, 350, 420, 440, 520, 530, 510, 530])
SAMS = dict(comp=[5.5, 3.8, 3.1, 4.4, 5.2, 7.0, 6.8, 6.7, 5.9, 3.8, 4.0, 3.9, 4.4, 4.9],
            trx=[2.9, 4.0, 3.6, 5.4, 6.1, 6.4, 5.4, 4.8, 3.9, 3.4, 5.0, 5.1, 5.8, 5.1],
            tkt=[2.5, -0.2, -0.4, -1.0, -0.8, 0.5, 1.3, 1.7, 2.0, 0.4, -1.0, -1.2, -1.4, -0.3],
            ecom=[150, 170, 190, 180, 230, 290, 280, 350, 350, 330, 380, 400, 450, 520])
SAMS_OLD = {'3T26': (3.9, -0.1), '4T26': (5.3, -1.3), '1T27': (6.2, -2.2), '2T27': (7.0, -2.5)}
M['sams_old'] = SAMS_OLD
M['ql'] = QL; M['us'] = US; M['sams'] = SAMS
def avg(xs): return sum(xs)/len(xs)
for tag, D in (('us', US), ('sams', SAMS)):
    for k in ('comp', 'trx', 'tkt', 'ecom'):
        put(f'{tag}_{k}_8q', avg(D[k][-8:])); put(f'{tag}_{k}_4q', avg(D[k][-4:]))
    put(f'{tag}_trx_share_8q', M[f'{tag}_trx_8q']/M[f'{tag}_comp_8q']*100)
put('us_comp_q2_exhw', 3.4); put('us_mfp_bps', 125); put('sams_mfp_bps', 40); put('glp1_fy27_bps', 50); put('glp1_fy26_bps', 100)
put('us_lfl_infl_q2', 1.4)
put('us_mfp_bps_q3', 70); put('sams_mfp_bps_q3', 35); put('us_lfl_infl_q3', 1.2); put('us_grocery_infl_q3', 1.4)
put('us_comp_q3_exmfp', 2.9 + 0.70)                       # comparable de Walmart U.S. sumando de vuelta los ~70 pb de farmacia
put('sams_rev_trx_q2_d', 7.0 - 5.8)                       # cuánto bajó el tráfico revisado del 2T de Sam's

# ---------------- E-commerce, publicidad, membresías ----------------
ECOM = {'us': (65.4, 79.3, 99.6), 'intl': (24.8, 29.5, 35.8), 'sams': (9.9, 12.1, 15.0)}   # FY24, FY25, FY26 (10-K, nota 11)
NS = {'us': (441.817, 462.415, 482.975), 'intl': (114.641, 121.885, 130.423), 'sams': (86.179, 90.238, 93.015)}
M['ecom'] = ECOM
for i, y in enumerate(('24', '25', '26')):
    tot = sum(ECOM[k][i] for k in ECOM); ns = sum(NS[k][i] for k in NS)
    put(f'ecom_tot_{y}', tot); put(f'ecom_pct_{y}', tot/ns*100)
    for k in ECOM: put(f'ecom_{k}_pct_{y}', ECOM[k][i]/NS[k][i]*100)
put('ecom_g26', (M['ecom_tot_26']/M['ecom_tot_25']-1)*100); put('ecom_g25', (M['ecom_tot_25']/M['ecom_tot_24']-1)*100)
put('ecom_us_g26', (ECOM['us'][2]/ECOM['us'][1]-1)*100)
ECOM_Q = [21, 21, 27, 16, 22, 25, 27, 24, 26, 23, 17]  # crecimiento global trimestral, 1T FY25 a 3T FY27 (3T: Flipkart corrió los Big Billion Days al 4T)
M['ecom_q'] = ECOM_Q; put('ecom_q_avg', avg(ECOM_Q))
ADS = {'FY23': 2.7, 'FY24': 3.4, 'FY25': 4.4, 'FY26': 6.4}   # negocio global de publicidad (comunicados del 4T); FY26 incluye VIZIO
M['ads'] = ADS; put('ads_g26', (ADS['FY26']/ADS['FY25']-1)*100); put('ads_cagr', ((ADS['FY26']/ADS['FY23'])**(1/3)-1)*100)
MEMB = {'FY24': 3.1, 'FY25': 3.8, 'FY26': 4.4}               # ingresos por cuotas de membresía (10-K, nota 1)
M['memb'] = MEMB; put('memb_g26', (MEMB['FY26']/MEMB['FY25']-1)*100)
put('memb_q4', 15.1); put('memb_q1', 17.4); put('memb_q2', 17.0); put('sams_memb_q2', 6.0); put('intl_memb_q2', 28.0)
put('ads_q2', 38); put('connect_q2', 43); put('mkt_q2', 52); put('ads_intl_q2', 20)
# 3T FY27 (comunicado y presentación del 19-nov-2026)
put('ads_q3', 25); put('ads_us_q3', 37); put('connect_q3', 36); put('mkt_q3', 49); put('ads_intl_q3', -15)
put('ecom_q3', 17); put('ecom_us_q3', 23); put('ecom_sams_q3', 30); put('ecom_intl_q3', -2); put('ecom_share_q3', 24)
put('memb_q3', 17); put('sams_memb_q3', 2.2); put('us_memb_other_q3', 43.0); put('bbd_bps', 500); put('bundle_price', 120)
put('hm_rev26', ADS['FY26'] + MEMB['FY26'])                   # ingresos de los negocios de alto margen
# "Advertising income and membership fees represented nearly one third of our operating income this quarter" (CFO, 4T FY26)
OI_Q4 = 8.708
put('oi_q4_26', OI_Q4); put('hm_oi_q4', OI_Q4/3)
put('hm_rev_share', M['hm_rev26']/713.163*100)
REV_Q4 = put('rev_q4_26', 190.656)
put('om_q4_26', OI_Q4/REV_Q4*100); put('om_q4_ex_hm', (OI_Q4 - M['hm_oi_q4'])/REV_Q4*100)

# ---------------- Serie anual (SEC XBRL, data/annual.json) ----------------
A = json.load(open(HERE/'data'/'annual.json'))
def a(tag, y): return A[tag][str(y)]/1e9
YRS = list(range(2016, 2027))
REVY = {y: a('Revenues', y) for y in YRS}
NSY = {y: (a('RevenueFromContractWithCustomerExcludingAssessedTax', y) if str(y) in A['RevenueFromContractWithCustomerExcludingAssessedTax'] else None) for y in YRS}
NSY[2016] = 478.614                                        # ventas netas FY2016 (10-K FY2016)
COGS = {y: a('CostOfRevenue', y) for y in YRS}
SGA = {y: a('SellingGeneralAndAdministrativeExpense', y) for y in YRS}
OIY = {y: a('OperatingIncomeLoss', y) for y in YRS}
OCF = {y: a('NetCashProvidedByUsedInOperatingActivities', y) for y in YRS}
CAPEX = {y: a('PaymentsToAcquirePropertyPlantAndEquipment', y) for y in YRS}
INV = {y: a('InventoryNet', y) for y in YRS}
AP = {y: a('AccountsPayableCurrent', y) for y in YRS}
INV[2015] = 45.141                                          # inventario al 31-ene-2015 (10-K FY2015)
M['ann'] = {}
for y in YRS:
    gm = (NSY[y]-COGS[y])/NSY[y]*100
    M['ann'][str(y)] = dict(rev=REVY[y], ns=NSY[y], gm=gm, opex=SGA[y]/NSY[y]*100, om=OIY[y]/REVY[y]*100,
                            ocf=OCF[y], capex=CAPEX[y], fcf=OCF[y]-CAPEX[y], capex_pct=CAPEX[y]/REVY[y]*100,
                            turns=COGS[y]/((INV[y]+INV[y-1])/2), inv=INV[y], ap=AP[y], ap_inv=AP[y]/INV[y]*100,
                            ocf_m=OCF[y]/REVY[y]*100)
put('rev_cagr_10', ((REVY[2026]/REVY[2016])**(1/10)-1)*100)
put('rev_cagr_5', ((REVY[2026]/REVY[2021])**(1/5)-1)*100)
put('dio26', 365/M['ann']['2026']['turns']); put('dio16', 365/M['ann']['2016']['turns'])
ADJ_OI = {2024: 27.105, 2025: 29.504, 2026: 30.982}          # resultado operativo ajustado (comunicados del 4T)
for y, v in ADJ_OI.items(): put(f'adj_om_{y}', v/REVY[y]*100)
ROI = {'FY23': 12.7, 'FY24': 15.0, 'FY25': 15.5, 'FY26': 15.1, 'TTM 3T27': 15.4}   # ROI según Walmart (comunicados)
M['roi'] = ROI
# ROIC propio: resultado operativo ajustado después de impuestos / capital invertido promedio (patrimonio total + deuda
# financiera con arrendamientos financieros − caja). Balances de SEC XBRL y del comunicado del 2T FY27.
BAL = {  # patrimonio total (incluye no controlantes y redimibles), deuda financiera (con arrendamientos financieros), caja
    # SEC XBRL (data/balances.py): ShortTermBorrowings, LongTermDebtCurrent/Noncurrent, FinanceLeaseLiabilityCurrent/Noncurrent
    2024: dict(eq=90.349+0.222, debt=0.878+3.447+36.132+0.725+5.709, cash=9.867),
    2025: dict(eq=97.421+0.271, debt=3.068+2.598+33.401+0.800+5.923, cash=9.037),
    2026: dict(eq=105.887+0.293, debt=6.596+3.542+34.624+0.856+5.905, cash=10.727),
}
TAX = put('tax', 24.0)                                        # tasa efectiva ajustada guiada FY27: 23.5%-24.5%
for y in (2025, 2026):
    ic = lambda b: b['eq'] + b['debt'] - b['cash']
    put(f'roic_{y}', ADJ_OI[y]*(1-TAX/100)/((ic(BAL[y])+ic(BAL[y-1]))/2)*100)
# Conversión de FCF: FCF / utilidad neta ajustada (EPS ajustado × acciones diluidas)
DILY = {2025: 8.081, 2026: 8.022}                             # acciones diluidas promedio (SEC XBRL)
for y in (2025, 2026):
    put(f'fcf_{y}', OCF[y]-CAPEX[y]); put(f'adj_ni_{y}', FY_ADJ[y]*DILY[y])
    put(f'fcf_conv_{y}', (OCF[y]-CAPEX[y])/(FY_ADJ[y]*DILY[y])*100)
put('capex_pct_26', CAPEX[2026]/NSY[2026]*100); put('da26', 14.203); put('da_pct_26', 14.203/REVY[2026]*100)

# ---------------- Trimestre y semestre (comunicado 2T FY27) ----------------
Q2 = dict(rev=187.937, ns=186.100, gp=47.296, opex=39.750, oi=9.383, oi_py=7.286, adj_oi_py=7.876, oi_cc=9.248,
          rev_py=177.402, ns_py=175.750, gp_py=42.979, opex_py=37.345, ni=6.366, ni_py=7.026)
M['q2'] = Q2
put('q2_gm', Q2['gp']/Q2['ns']*100); put('q2_gm_py', Q2['gp_py']/Q2['ns_py']*100)
put('q2_opex', Q2['opex']/Q2['ns']*100); put('q2_opex_py', Q2['opex_py']/Q2['ns_py']*100)
put('q2_om', Q2['oi']/Q2['rev']*100); put('q2_om_py', Q2['adj_oi_py']/Q2['rev_py']*100)
put('tariff_refund', 2.9)
Q2_GUIDE_OI_HI = 10.0                                          # guía del 2T: resultado operativo (cc) +7% a +10%
put('q2_oi_guide_top', Q2['adj_oi_py']*(1+Q2_GUIDE_OI_HI/100))
put('tariff_net_q2', Q2['oi_cc'] - M['q2_oi_guide_top'])      # efecto neto máximo de las devoluciones en el 2T (US$ mil millones)
put('tariff_reinvested_pct', (1 - M['tariff_net_q2']/2.9)*100)
# 3T FY27 (comunicado del 19-nov-2026, trimestre al 31-oct-2026)
Q3 = dict(rev=188.835, ns=186.757, gp=45.754, opex=40.062, oi=7.770, oi_py=6.696, adj_oi_py=7.263, oi_cc=7.663,
          rev_py=179.496, ns_py=177.769, gp_py=43.063, opex_py=38.094, ni=4.945, ni_py=6.143, memb=2.078, memb_py=1.727,
          us_oi=6.324, us_oi_py=5.803, us_ns=124.969, us_ns_py=120.678, intl_oi=1.628, intl_adj_oi_py=1.422, intl_oi_cc=1.521,
          intl_ns=35.876, intl_ns_py=33.541, sams_oi=0.547, sams_oi_py=0.650, sams_ns=25.912, sams_ns_py=23.550, sams_ns_xf=22.3,
          corp_oi=-0.729, corp_oi_py=-0.457, fx_rev=1.234)
M['q3'] = Q3
put('q3_gm', Q3['gp']/Q3['ns']*100); put('q3_gm_py', Q3['gp_py']/Q3['ns_py']*100)
put('q3_opex', Q3['opex']/Q3['ns']*100); put('q3_opex_py', Q3['opex_py']/Q3['ns_py']*100)
put('q3_om', Q3['oi']/Q3['rev']*100); put('q3_om_py', Q3['adj_oi_py']/Q3['rev_py']*100)
put('q3_gm_bp', (M['q3_gm'] - M['q3_gm_py'])*100); put('q3_opex_bp', (M['q3_opex'] - M['q3_opex_py'])*100)
put('q3_rev_g', (Q3['rev']/Q3['rev_py']-1)*100); put('q3_rev_g_cc', 4.5)
put('q3_oi_g', (Q3['oi']/Q3['oi_py']-1)*100); put('q3_adj_oi_g', (Q3['oi']/Q3['adj_oi_py']-1)*100); put('q3_adj_oi_g_cc', 5.5)
put('q3_memb_g', (Q3['memb']/Q3['memb_py']-1)*100)
put('q3_us_oi_g', (Q3['us_oi']/Q3['us_oi_py']-1)*100); put('q3_us_ns_g', (Q3['us_ns']/Q3['us_ns_py']-1)*100)
put('q3_us_om', Q3['us_oi']/(Q3['us_ns']+0.951)*100); put('q3_us_om_py', Q3['us_oi_py']/(Q3['us_ns_py']+0.665)*100)
put('q3_intl_ns_g', (Q3['intl_ns']/Q3['intl_ns_py']-1)*100); put('q3_intl_ns_g_cc', 3.3)
put('q3_sams_oi_g', (Q3['sams_oi']/Q3['sams_oi_py']-1)*100); put('q3_sams_ns_g', (Q3['sams_ns']/Q3['sams_ns_py']-1)*100)
put('q3_corp_d', Q3['corp_oi'] - Q3['corp_oi_py'])
put('q3_ni_g', (Q3['ni']/Q3['ni_py']-1)*100)
put('q3_inv_loss_eps', 0.03); put('q3_tax_adj', 24.6)
# Nueve meses FY27 vs FY26
put('n9_rev', 554.523); put('n9_rev_py', 522.507); put('n9_rev_g', (554.523/522.507-1)*100)
put('n9_adj_oi', 24.827); put('n9_adj_oi_py', 22.274); put('n9_adj_oi_g', (24.827/22.274-1)*100); put('n9_adj_oi_g_cc', 9.6)
put('n9_ocf', 29.436); put('n9_ocf_py', 27.452); put('n9_capex', 22.621); put('n9_capex_py', 18.627)
put('n9_fcf', 29.436-22.621); put('n9_fcf_py', 27.452-18.627); put('n9_capex_ns', 22.621/548.541*100)
TTM_REV = put('ttm_rev', REVY[2026] - 522.507 + 554.523)
TTM_OCF = put('ttm_ocf', OCF[2026] - 27.452 + 29.436)
TTM_CAPEX = put('ttm_capex', CAPEX[2026] - 18.627 + 22.621)
put('ttm_ocf_m', TTM_OCF/TTM_REV*100); put('ttm_fcf', TTM_OCF-TTM_CAPEX)
put('ttm_adj_oi', 30.982 - 22.274 + 24.827)
put('ttm_da', 14.203 - 10.462 + 11.763)              # = 15.504 de la tabla de ROI del comunicado
assert abs(M['ttm_da'] - 15.504) < 1e-9

# ---------------- Segmentos (10-K FY2026, nota 11; ajustados según comunicado del 4T FY26) ----------------
SEG = {  # ingresos totales, resultado operativo ajustado, D&A y capex FY2026 (US$ miles de millones)
 'us':   dict(name='Walmart U.S.', rev=485.599, oi=25.158, da=9.390, capex=20.157, rev25=465.009, oi25=24.012, rev24=443.802, oi24=22.154),
 'sams': dict(name="Sam's Club U.S.", rev=95.540, oi=2.522, da=0.782, capex=0.914, rev25=92.561, oi25=2.404, rev24=88.230, oi24=2.192),
 'intl': dict(name='Walmart International', rev=131.988, oi=5.825, da=2.304, capex=3.197, rev25=123.363, oi25=5.501, rev24=116.049, oi24=4.909),
 'corp': dict(name='Corporativo y soporte', rev=0.036, oi=-2.523, da=1.727, capex=2.374),
}
for k, s in SEG.items():
    if k != 'corp':
        s['m'] = s['oi']/s['rev']*100; s['m25'] = s['oi25']/s['rev25']*100; s['m24'] = s['oi24']/s['rev24']*100
M['seg'] = SEG
put('seg_oi_share_us', SEG['us']['oi']/(SEG['us']['oi']+SEG['sams']['oi']+SEG['intl']['oi'])*100)
put('corp_pct', SEG['corp']['oi']/REVY[2026]*100)
put('ns_us_share', NSY and NS['us'][2]/(NS['us'][2]+NS['intl'][2]+NS['sams'][2])*100)
put('intl_share', NS['intl'][2]/(NS['us'][2]+NS['intl'][2]+NS['sams'][2])*100)
INTL_MKT = {'mx': 52.492, 'cn': 24.623, 'ca': 23.724, 'other': 29.584}   # FY2026 por mercado (10-K)
M['intl_mkt'] = INTL_MKT
put('cn_g26', (24.623/19.975-1)*100)
US_CAT = {'Almacén (grocery)': 285.482, 'Mercadería general': 115.060, 'Salud y bienestar': 69.547, 'Otros': 12.886}
M['us_cat'] = US_CAT; put('grocery_pct', 285.482/482.975*100); put('hw_g26', (69.547/62.092-1)*100)

# ---------------- Internacional: participaciones con marca de mercado o de transacción ----------------
WALMEX_PX = put('walmex_px', 54.42)       # MXN, cierre 20-nov-2026 (BMV)
WALMEX_SH = put('walmex_sh', 17.30)       # miles de millones de acciones (feb-2026)
MXN = put('mxn', 19.0901)                 # MXN por US$ (Yahoo, a la fecha de corte)
put('walmex_px_sep', 46.71); put('mxn_sep', 18.0068)
WALMEX_STAKE = put('walmex_stake', 70.5)  # participación de Walmart (~70%-71% según las fuentes)
put('walmex_mcap', WALMEX_PX*WALMEX_SH/MXN)
put('walmex_val', M['walmex_mcap']*WALMEX_STAKE/100)
put('walmex_hi52_mxn', 63.97)
WALMEX_OI_MXN = put('walmex_oi_mxn', 78.494 - 36.156 + 35.491)   # utilidad de operación de los últimos 12 meses a jun-2026 (MXN miles de millones)
put('walmex_om25', 78.494/(766.400+245.198)*100)
put('walmex_oi_usd', M['walmex_om25']/100*INTL_MKT['mx'])       # margen de Walmex × ventas de México y Centroamérica en dólares (10-K)
put('walmex_pe', M['walmex_mcap']*MXN/(23.652*2))                # referencia: capitalización / (2 × utilidad neta 1S26)
FLIP_VAL = put('flip_val', 37.0); FLIP_STAKE = put('flip_stake', 85.0)   # ronda de may-2024 (US$1,000 millones, Google $350M)
put('flip_mark', FLIP_VAL*FLIP_STAKE/100)
PP_VAL = put('pp_val', 9.0); PP_VAL_HI = put('pp_val_hi', 12.0); PP_STAKE = put('pp_stake', 73.0)
put('pp_mark', PP_VAL*PP_STAKE/100); put('pp_mark_hi', PP_VAL_HI*PP_STAKE/100)
# Pérdidas de los negocios de India (estados locales, a US$): Flipkart India ₹5,189 cr + Flipkart Internet ₹1,494 cr (año a mar-2025),
# PhonePe pérdida normalizada ₹1,377 cr (año a mar-2026), a ₹86 por dólar
INR = put('inr_avg', 86.0)
put('india_loss', (5189 + 1494 + 1377)/100/INR)                  # US$ miles de millones
MIN_MKT = put('minority_mkt', M['walmex_mcap']*(1-WALMEX_STAKE/100) + FLIP_VAL*(1-FLIP_STAKE/100) + PP_VAL*(1-PP_STAKE/100))
put('nci_book', 6.268 + 0.293)
put('intl_marks', M['walmex_val'] + M['flip_mark'] + M['pp_mark'])
put('intl_marks_ps', M['intl_marks']/SH_DIL*1000)

# ---------------- Balance (comunicado 3T FY27, 31-oct-2026) ----------------
DEBT_FIN = put('debt_fin', 12.277 + 3.221 + 41.962)
FIN_LEASE = put('fin_lease', 0.893 + 5.939)
OP_LEASE = put('op_lease', 1.734 + 15.126)
CASH = put('cash', 13.432)
assert abs(DEBT_FIN + FIN_LEASE - 64.292) < 0.01       # "Total debt of $64.3 billion" (comunicado)
put('debt_issued_oct', 6.5)
DEBT = put('debt', DEBT_FIN + FIN_LEASE)
NETDEBT_DCF = put('net_debt_dcf', DEBT - CASH)               # sin arrendamientos operativos (sus pagos ya están en el OCF)
NETDEBT_EV = put('net_debt_ev', DEBT + OP_LEASE - CASH)      # con arrendamientos operativos (EV/EBITDA)
put('ebitda_ttm_adj', M['ttm_adj_oi'] + M['ttm_da'])
put('nd_ebitda', NETDEBT_DCF/M['ebitda_ttm_adj'])
put('nd_ebitda_leases', NETDEBT_EV/M['ebitda_ttm_adj'])
put('inv_q2', 70.630); put('inv_g_q2', (70.630/65.354-1)*100); put('ap_q2', 71.410)   # (claves heredadas: ahora 31-oct-2026)
put('ap_inv_q2', 71.410/70.630*100)

# ---------------- Costo de capital ----------------
BETA_WMT = put('beta_wmt', 0.53)                              # stockanalysis, 5 años mensual (21-nov-2026; sep: 0.59)
BETA_ADJ = put('beta_adj', 0.67*BETA_WMT + 0.33)
KE_FLOOR = put('ke_floor', RF + 2.5)
KE = put('ke', max(RF + BETA_ADJ*ERP, KE_FLOOR))
KD_PRE = put('kd_pre', RF + 0.60)                             # supuesto: emisor AA/Aa2 a ~60 pb sobre el Treasury
KD = put('kd', KD_PRE*(1-TAX/100))
E = PRICE*SH_OUT/1000
WD = put('wd', DEBT/(DEBT+E)*100)
def wacc(ke): return (1-WD/100)*ke + WD/100*KD
WACC = put('wacc', wacc(KE))

# ---------------- Conversión de caja anclada en el OCF real ----------------
# k = (OCF + intereses después de impuestos − compensación en acciones) / (resultado operativo ajustado × (1−t) + D&A),
# FY2025 + FY2026 juntos. La compensación en acciones se trata como costo; el cargo de PhonePe ($0.722) ya está
# excluido del resultado ajustado, así que no se resta de nuevo.
t = TAX/100
INT = {2025: 2.245, 2026: 2.431}; SBC = {2025: 2.77, 2026: 3.603 - 0.722}; DA = {2025: 12.973, 2026: 14.203}
num = sum(OCF[y] + INT[y]*(1-t) - SBC[y] for y in (2025, 2026)); den = sum(ADJ_OI[y]*(1-t) + DA[y] for y in (2025, 2026))
K = put('k_conv', num/den)
put('k_26', (OCF[2026] + INT[2026]*(1-t) - SBC[2026])/(ADJ_OI[2026]*(1-t) + DA[2026]))
put('k_25', (OCF[2025] + INT[2025]*(1-t) - SBC[2025])/(ADJ_OI[2025]*(1-t) + DA[2025]))
put('sbc26', SBC[2026])

# ---------------- DCF consolidado por segmento (Método 1a, 7.5%) ----------------
YEARS = [2028, 2029, 2030, 2031, 2032]     # FY2028 (feb-2027 a ene-2028) a FY2032
STUB = put('stub', 72/365)                  # 21-nov-2026 a 31-ene-2027 (resto del FY2027; sep: un tercio)
CAPEX_PATH = {'bear': [4.00, 4.00, 4.00, 4.00, 4.00, 4.00], 'base': [3.95, 3.75, 3.60, 3.50, 3.50, 3.50], 'bull': [3.95, 3.60, 3.40, 3.25, 3.25, 3.25]}
DA_PATH = [2.05, 2.10, 2.15, 2.20, 2.25, 2.30]                    # D&A / ingresos, FY27 a FY32 (sube con el capex)
SC = {
 'bear': dict(dw=+0.5, g=2.0, us_trx=1.0, us_tkt=1.5, us_dm=0.05, sams_g=[3, 3, 3, 3, 3], sams_dm=0.0, intl_g=[6, 4, 4, 4, 4], intl_dm=0.0),
 'base': dict(dw=0.0, g=2.5, us_trx=round(M['us_trx_8q'], 1), us_tkt=2.0, us_dm=0.15, sams_g=[5.0, 4.75, 4.5, 4.25, 4.0], sams_dm=0.05, intl_g=[7, 6.5, 6, 5.5, 5], intl_dm=0.10),
 'bull': dict(dw=-0.5, g=3.0, us_trx=2.75, us_tkt=2.5, us_dm=0.25, sams_g=[5.5, 5.5, 5.5, 5.5, 5.5], sams_dm=0.10, intl_g=[8, 8, 7.5, 7, 6.5], intl_dm=0.15),
}
US_OTHER = put('us_other_g', 0.3)          # crecimiento fuera de comparables (tiendas nuevas y otros ingresos), puntos por año
# FY2027E: crecimiento real de los nueve meses de los ingresos totales de cada segmento (comunicado del 3T: U.S. +4.0%,
# Sam's +8.3% con combustible, Internacional +12.4% en dólares con +7.0% a moneda constante). Sep: 4.0 / 5.0 / 8.0.
# Margen: el de FY2026 + el cambio de los nueve meses en el margen ajustado del segmento, salvo U.S., que se deja en +0.17
# (el +0.41 de nueve meses incluye las devoluciones de aranceles del 2T). Chequeo: base_oi27_g contra la guía (+8.0% a +8.6% cc).
N9 = {'us': (367.327+2.627, 353.752+1.950, 20.467, 18.231), 'sams': (75.030+1.986, 69.252+1.889, 1.899, 1.866),
      'intl': (106.184+1.306, 94.496+1.151, 4.669, 3.949)}
FY27_G = {k: round((v[0]/v[1]-1)*100, 1) for k, v in N9.items()}
M['fy27_g'] = FY27_G
FY27_DM = {'us': 0.17, 'sams': round((N9['sams'][2]/N9['sams'][0] - N9['sams'][3]/N9['sams'][1])*100, 2),
           'intl': round((N9['intl'][2]/N9['intl'][0] - N9['intl'][3]/N9['intl'][1])*100, 2)}
M['fy27_dm'] = FY27_DM
def paths(sc, sc_name, dcomp=0.0, dm_us=None):
    rows = {}
    capex = CAPEX_PATH[sc_name]
    for k in ('us', 'sams', 'intl'):
        s = SEG[k]; rev = s['rev']*(1+FY27_G[k]/100); m = s['m'] + FY27_DM[k]
        r27 = dict(rev=rev, m=m, oi=rev*m/100); out = [r27]
        for i in range(5):
            if k == 'us': g = sc['us_trx'] + sc['us_tkt'] + US_OTHER + dcomp; dm = sc['us_dm'] if dm_us is None else dm_us
            elif k == 'sams': g = sc['sams_g'][i] + dcomp; dm = sc['sams_dm']
            else: g = sc['intl_g'][i]; dm = sc['intl_dm']
            rev *= 1 + g/100; m += dm
            out.append(dict(rev=rev, m=m, oi=rev*m/100, g=g))
        rows[k] = out
    tot = []
    for i in range(6):
        rev = sum(rows[k][i]['rev'] for k in rows)
        oi = sum(rows[k][i]['oi'] for k in rows) + M['corp_pct']/100*rev
        da = rev*DA_PATH[i]/100; cx = rev*capex[i]/100
        fcf = K*(oi*(1-t) + da) - cx
        tot.append(dict(y=2027+i, rev=rev, oi=oi, m=oi/rev*100, da=da, capex=cx, fcf=fcf, ocf_m=(K*(oi*(1-t)+da))/rev*100))
    return rows, tot
def dcf(sc_name, w=None, g=None, dcomp=0.0, dm_us=None, detail=False):
    sc = SC[sc_name]; w = (WACC + sc['dw']) if w is None else w; g = sc['g'] if g is None else g
    rows, tot = paths(sc, sc_name, dcomp, dm_us)
    pv = tot[0]['fcf']*STUB*(1+w/100)**-(STUB/2)
    for i in range(1, 6): pv += tot[i]['fcf']*(1+w/100)**-(STUB + i - 0.5)
    tv = tot[5]['fcf']*(1+g/100)/((w-g)/100); pv_tv = tv*(1+w/100)**-(STUB+5)
    ev = pv + pv_tv
    eq = ev - NETDEBT_DCF - MIN_MKT
    ps = eq/SH_DIL*1000
    if detail: return dict(ev=ev, eq=eq, ps=ps, pv=pv, pv_tv=pv_tv, tv_share=pv_tv/ev*100, w=w, g=g, rows=rows, tot=tot)
    return ps
for k in SC:
    r = dcf(k, detail=True)
    for f in ('ps', 'ev', 'tv_share', 'w', 'g', 'pv', 'pv_tv'): put(f'dcf_{k}_{f}' if f != 'ps' else f'dcf_{k}', r[f])
    tot = r['tot']
    put(f'dcf_{k}_revcagr', ((tot[5]['rev']/REVY[2026])**(1/6)-1)*100)
    put(f'dcf_{k}_m32', tot[5]['m']); put(f'dcf_{k}_fcfm32', tot[5]['fcf']/tot[5]['rev']*100)
    if k == 'base':
        wb = r['w']
        for i, row in enumerate(tot):
            row['pv'] = row['fcf']*(STUB if i == 0 else 1)*(1+wb/100)**-((STUB/2) if i == 0 else (STUB + i - 0.5))
            row['g'] = (row['rev']/(tot[i-1]['rev'] if i else REVY[2026])-1)*100
        M['dcf_base_tot'] = tot
        M['dcf_base_rows'] = {kk: v for kk, v in r['rows'].items()}
        put('base_ocf_m27', tot[0]['ocf_m']); put('base_oi27', tot[0]['oi']); put('base_oi27_g', (tot[0]['oi']/ADJ_OI[2026]-1)*100)
        put('base_rev27_g', (tot[0]['rev']/REVY[2026]-1)*100)
        put('base_us_g', SC['base']['us_trx'] + SC['base']['us_tkt'] + US_OTHER)
put('dcf_gap', (M['dcf_base']/PRICE-1)*100)
put('dcf_pw', 0.25*M['dcf_bear'] + 0.45*M['dcf_base'] + 0.30*M['dcf_bull'])
put('us_g_bear', SC['bear']['us_trx']+SC['bear']['us_tkt']+US_OTHER); put('us_g_bull', SC['bull']['us_trx']+SC['bull']['us_tkt']+US_OTHER)
# Sensibilidad a las comparables: −2 / 0 / +2 puntos por año en Walmart U.S. y Sam's Club (FY2028-FY2032)
put('dcf_comp_m2', dcf('base', dcomp=-2.0)); put('dcf_comp_p2', dcf('base', dcomp=+2.0))
put('dcf_comp_m2_d', (M['dcf_comp_m2']/M['dcf_base']-1)*100); put('dcf_comp_p2_d', (M['dcf_comp_p2']/M['dcf_base']-1)*100)
# Grilla WACC × g
WG = [WACC-1, WACC-0.5, WACC, WACC+0.5, WACC+1]; GG = [2.0, 2.25, 2.5, 2.75, 3.0]
M['grid_w'] = WG; M['grid_g'] = GG
M['grid'] = [[dcf('base', w=w, g=g) for g in GG] for w in WG]
assert abs(M['grid'][2][2] - M['dcf_base']) < 1e-9
put('grid_up', (M['grid'][1][2]/M['dcf_base']-1)*100); put('grid_dn', (M['grid'][3][2]/M['dcf_base']-1)*100)
put('grid_max', M['grid'][0][4]); put('grid_min', M['grid'][4][0])
# DCF inverso
def solve(f, lo, hi, target, inc=True):
    for _ in range(200):
        mid = (lo+hi)/2
        if (f(mid) < target) == inc: lo = mid
        else: hi = mid
    return (lo+hi)/2
put('impl_wacc', solve(lambda w: dcf('base', w=w), 3.0, 12.0, PRICE, inc=False))
put('impl_g', solve(lambda g: dcf('base', g=g), 0.0, WACC-0.2, PRICE, inc=True))
put('impl_dm', solve(lambda d: dcf('base', dm_us=d), 0.0, 3.0, PRICE, inc=True))
r_impl = dcf('base', dm_us=M['impl_dm'], detail=True); put('impl_us_m32', r_impl['rows']['us'][5]['m'])
put('impl_dcomp', solve(lambda d: dcf('base', dcomp=d), 0.0, 40.0, PRICE, inc=True))
put('impl_us_g', M['base_us_g'] + M['impl_dcomp'])
# Chequeos de sesgo (el DCF queda a más de 30%-40% del precio)
Ks = K
PEER_BETA_MED = put('peer_beta_med', st.median([0.85, 0.93, 0.36, 0.14, 0.19, 0.69]))   # betas de PEERS (se verifica abajo)
put('dcf_peerbeta', dcf('base', w=wacc(max(RF + (0.67*PEER_BETA_MED+0.33)*ERP, KE_FLOOR))))
put('dcf_erp_dam', dcf('base', w=wacc(max(RF + BETA_ADJ*M['erp_dam'], KE_FLOOR))))
put('dcf_kefloor', dcf('base', w=wacc(KE_FLOOR)))
K = M['k_26']; put('dcf_k26', dcf('base')); K = Ks
K = (num + SBC[2025] + SBC[2026])/den; put('dcf_k_sbc', dcf('base')); K = Ks
put('k_sbc', (num + SBC[2025] + SBC[2026])/den)

# ---------------- Suma de partes (Método 1b, 7.5%) ----------------
# Walmart U.S., Sam's Club y el resto de Internacional por DCF de su propio flujo; Walmex a precio de mercado; Flipkart a la
# última transacción real; PhonePe a la valuación de su salida a bolsa (suspendida); corporativo como costo capitalizado.
# El resto de Internacional excluye el resultado de Walmex y suma de vuelta las pérdidas de India, para no contarlos dos veces.
def seg_dcf(sc_name='base', w=None, g=None, detail=False):
    sc = SC[sc_name]; w = (WACC + sc['dw']) if w is None else w; g = sc['g'] if g is None else g
    rows, tot = paths(sc, sc_name)
    capex = CAPEX_PATH[sc_name]; cons_cx26 = CAPEX[2026]/REVY[2026]*100; cons_da26 = DA[2026]/REVY[2026]*100
    intl_rest_oi26 = SEG['intl']['oi'] - M['walmex_oi_usd'] + M['india_loss']
    out = {}
    for k in ('us', 'sams', 'intl_rest', 'corp'):
        flows = []
        for i in range(6):
            fx = capex[i]/cons_cx26; fd = DA_PATH[i]/cons_da26
            if k in ('us', 'sams'):
                r = rows[k][i]; oi = r['oi']; da = SEG[k]['da']/SEG[k]['rev']*r['rev']*fd; cx = SEG[k]['capex']/SEG[k]['rev']*r['rev']*fx
            elif k == 'intl_rest':
                gi = rows['intl'][i]['oi']/SEG['intl']['oi']
                oi = intl_rest_oi26*gi; da = SEG['intl']['da']/SEG['intl']['oi']*oi*fd; cx = SEG['intl']['capex']/SEG['intl']['oi']*oi*fx
            else:
                rev = tot[i]['rev']; oi = M['corp_pct']/100*rev; da = SEG['corp']['da']/REVY[2026]*rev*fd; cx = SEG['corp']['capex']/REVY[2026]*rev*fx
            flows.append(dict(oi=oi, fcf=K*(oi*(1-t) + da) - cx))
        pv = flows[0]['fcf']*STUB*(1+w/100)**-(STUB/2)
        for i in range(1, 6): pv += flows[i]['fcf']*(1+w/100)**-(STUB + i - 0.5)
        pv_tv = flows[5]['fcf']*(1+g/100)/((w-g)/100)*(1+w/100)**-(STUB+5)
        out[k] = dict(ev=pv+pv_tv, oi26=(SEG[k]['oi'] if k in SEG else intl_rest_oi26), oi28=flows[1]['oi'], pv_tv=pv_tv)
    ev_ops = sum(v['ev'] for v in out.values())
    eq = ev_ops + M['intl_marks'] - NETDEBT_DCF
    ps = eq/SH_DIL*1000
    if detail: return dict(parts=out, ev_ops=ev_ops, eq=eq, ps=ps, intl_rest_oi26=intl_rest_oi26)
    return ps
for k in SC:
    put(f'sotp_{k}', seg_dcf(k))
r = seg_dcf('base', detail=True)
put('sotp_base', r['ps']); put('intl_rest_oi26', r['intl_rest_oi26'])
M['sotp'] = {k: dict(ev=v['ev'], ps=v['ev']/SH_DIL*1000, oi26=v['oi26'], ev_oi=v['ev']/v['oi26'] if v['oi26'] > 0 else 0) for k, v in r['parts'].items()}
for nm, val in (('walmex', M['walmex_val']), ('flip', M['flip_mark']), ('pp', M['pp_mark'])):
    M['sotp'][nm] = dict(ev=val, ps=val/SH_DIL*1000)
M['sotp']['netdebt'] = dict(ev=-NETDEBT_DCF, ps=-NETDEBT_DCF/SH_DIL*1000)
put('sotp_sum_check', sum(v['ev'] for v in M['sotp'].values()) - r['eq'])
assert abs(M['sotp_sum_check']) < 1e-6
put('sotp_gap', (M['sotp_base']/PRICE-1)*100)
put('sotp_pp_hi', M['sotp_base'] + (M['pp_mark_hi']-M['pp_mark'])/SH_DIL*1000)
put('sotp_vs_dcf', M['sotp_base'] - M['dcf_base'])
put('intl_marks_share', M['intl_marks']/r['eq']*100)
put('sotp_us_share', M['sotp']['us']['ev']/r['eq']*100)
# Publicidad "aparte" (ilustrativo, NO se suma: ya está dentro del flujo de Walmart U.S.)
put('hm_oi_annual', M['hm_oi_q4']*4)                               # un tercio del resultado del 4T, anualizado (cota superior: el 4T es el trimestre más fuerte)
put('hm_oi_share_fy', M['hm_oi_annual']/ADJ_OI[2026]*100)

# ---------------- Comparables (Método 2, 25%) ----------------
PEERS = {  # precio: cierre 20-nov-2026 (Yahoo). Consenso S&P Global (stockanalysis, 21-nov-2026): q = los dos trimestres
 # siguientes; f1 = año fiscal en curso, f2 = año fiscal siguiente. NTM = q1 + q2 + la parte de f1/f2 que completa los cuatro
 # trimestres (ver ntm_rule). EV/EBITDA de los últimos 12 meses y beta de 5 años: stockanalysis. Comparables sin combustible
 # del último trimestre reportado (TGT y BJ reportaron el 3T al 31-oct-2026 el 18 y 20-nov; COST, KR, DG y DLTR sin cambios).
 'COST': dict(name='Costco', px=1102.15, q=[4.90522, 5.1187], f1=22.80045, f2=25.0437, left=4, comp=6.7, beta=0.85, eve=33.65, cl='Club de precios'),
 'TGT':  dict(name='Target', px=165.83, q=[2.68043, 1.92192], f1=11.03749, f2=9.76771, left=1, comp=5.6, beta=0.93, eve=10.07, cl='Tienda de descuento'),
 'KR':   dict(name='Kroger', px=68.44, q=[1.16258, 1.35662], f1=5.18992, f2=5.48368, left=2, comp=0.2, beta=0.36, eve=7.82, cl='Supermercado'),
 'BJ':   dict(name="BJ's Wholesale", px=104.82, q=[1.03893, 1.21358], f1=4.20+1.03893, f2=5.07235*(4.20+1.03893)/4.73388, left=1, comp=4.1, beta=0.14, eve=15.45, cl='Club de precios'),
 'DG':   dict(name='Dollar General', px=130.53, q=[1.40884, 2.03114], f1=7.89694, f2=8.30077, left=2, comp=3.5, beta=0.19, eve=12.00, cl='Dólar'),
 'DLTR': dict(name='Dollar Tree', px=137.96, q=[0.92441, 2.62318], f1=7.92882, f2=7.8869, left=2, comp=3.7, beta=0.69, eve=12.98, cl='Dólar'),
}
# BJ: el consenso anual de stockanalysis no estaba actualizado tras el 3T (4.73 contra 4.20 reales de nueve meses + 1.04 del 4T):
# f1 = nueve meses reales + consenso del 4T, f2 = f1 × el crecimiento que tenía el consenso viejo (supuesto declarado).
AMZN = dict(name='Amazon', px=246.82, q=[2.49111, 2.34857], f1=9.6025, f2=10.92608, left=1, beta=1.50, eve=15.56)
def ntm_rule(p):
    # left = trimestres del año fiscal en curso sin reportar. Con 1 o 2: los dos trimestres siguientes de consenso + la mitad
    # del año fiscal siguiente (los dos trimestres que faltan para completar cuatro). Con 4 (COST): el año fiscal en curso.
    if p['left'] == 4: return p['f1']
    return p['q'][0] + p['q'][1] + 0.5*p['f2']
for p in list(PEERS.values()) + [AMZN]:
    p['ntm'] = ntm_rule(p); p['pe'] = p['px']/p['ntm']; p['g'] = (p['f2']/p['f1']-1)*100
# TGT: su año fiscal en curso incluye devoluciones de aranceles (2T y 3T), así que f2/f1 da crecimiento negativo: se excluye de
# la regresión contra el crecimiento del EPS (no del P/E, que usa trimestres posteriores a las devoluciones).
M['peers'] = PEERS; M['amzn'] = AMZN
assert abs(st.median(p['beta'] for p in PEERS.values()) - PEER_BETA_MED) < 1e-12
put('ntm_wmt_check', ntm_rule(dict(left=1, q=[Q_CONS['4T27'], Q_CONS['1T28']], f1=C27, f2=C28)) - NTM)
assert abs(M['ntm_wmt_check']) < 1e-12
WMT_COMP = put('wmt_comp', (2.9*125.0 + 4.9*22.3)/(125.0 + 22.3))       # 3T FY27, U.S. + Sam's sin combustible, ponderado por ventas
WMT_COMP4 = put('wmt_comp4', (M['us_comp_4q']*125.0 + M['sams_comp_4q']*22.3)/(125.0+22.3))
WMT_G = put('wmt_g', (C28/C27-1)*100)
def reg(xs, ys):
    mx, my = st.mean(xs), st.mean(ys)
    sxy = sum((x-mx)*(y-my) for x, y in zip(xs, ys)); sxx = sum((x-mx)**2 for x in xs); syy = sum((y-my)**2 for y in ys)
    b = sxy/sxx; return dict(slope=b, icpt=my-b*mx, r2=sxy**2/(sxx*syy), n=len(xs))
pl = list(PEERS.items())
for key, var in (('comp', 'comp'), ('g', 'g')):
    pk = pl if key == 'comp' else [kp for kp in pl if kp[0] != 'TGT']
    R = reg([p[var] for _, p in pk], [p['pe'] for _, p in pk]); M[f'reg_{key}'] = R
    ex = [kp for kp in pk if kp[0] != 'COST']
    Rx = reg([p[var] for _, p in ex], [p['pe'] for _, p in ex]); M[f'reg_{key}_xcost'] = Rx
    x_wmt = WMT_COMP if key == 'comp' else WMT_G
    put(f'reg_{key}_pe_wmt', R['icpt'] + R['slope']*x_wmt)
R2_MIN = put('r2_min', 0.50)
put('reg_ok', 1 if (M['reg_comp']['r2'] >= R2_MIN and M['reg_comp_xcost']['r2'] >= R2_MIN) else 0)
put('reg_g_ok', 1 if (M['reg_g']['r2'] >= R2_MIN and M['reg_g_xcost']['r2'] >= R2_MIN) else 0)
# EV/EBITDA contra comparables, mismo criterio
M['reg_eve'] = reg([p['comp'] for _, p in pl], [p['eve'] for _, p in pl])
M['reg_eve_xcost'] = reg([p['comp'] for kk, p in pl if kk != 'COST'], [p['eve'] for kk, p in pl if kk != 'COST'])
put('reg_eve_ok', 1 if (M['reg_eve']['r2'] >= R2_MIN and M['reg_eve_xcost']['r2'] >= R2_MIN) else 0)
put('reg_eve_wmt', M['reg_eve']['icpt'] + M['reg_eve']['slope']*WMT_COMP)
put('reg_comp_pe_wmt4', M['reg_comp']['icpt'] + M['reg_comp']['slope']*WMT_COMP4)
put('reg_comp_xcost_pe_wmt', M['reg_comp_xcost']['icpt'] + M['reg_comp_xcost']['slope']*WMT_COMP)
PES = sorted(p['pe'] for p in PEERS.values())
def pctl(xs, q):   # percentil con interpolación lineal (método de Excel PERCENTIL.INC)
    pos = (len(xs)-1)*q; lo = int(pos); fr = pos - lo
    return xs[lo] + (xs[min(lo+1, len(xs)-1)] - xs[lo])*fr
put('peer_pe_med', pctl(PES, 0.5)); put('peer_pe_q3', pctl(PES, 0.75)); put('peer_pe_max', PES[-1]); put('peer_pe_min', PES[0])
put('peer_pe_mean', st.mean(PES))
COMPS_SORTED = sorted(p['comp'] for p in PEERS.values())
put('peer_comp_med', pctl(COMPS_SORTED, 0.5))
put('wmt_comp_rank_above_med', 1 if WMT_COMP > M['peer_comp_med'] else 0)
# Criterio: si la regresión contra las ventas comparables sostiene el ajuste (R² ≥ 0.50 con los seis pares Y sin el par
# extremo), se usa el múltiplo que la recta asigna a las comparables de WMT. Si no, múltiplo de pares: mediana si las
# comparables de WMT están por debajo de la mediana del grupo, cuartil superior si están por encima.
put('pe_sel_is_q3', M['wmt_comp_rank_above_med'])
PE_RULE = M['peer_pe_q3'] if M['wmt_comp_rank_above_med'] else M['peer_pe_med']
PE_SEL = put('pe_sel', M['reg_comp_pe_wmt'] if M['reg_ok'] else PE_RULE)
COMP_PE = put('comp_pe', PE_SEL*NTM)
EVES = sorted(p['eve'] for p in PEERS.values())
put('peer_eve_med', pctl(EVES, 0.5)); put('peer_eve_q3', pctl(EVES, 0.75)); put('peer_eve_max', EVES[-1])
EVE_RULE = M['peer_eve_q3'] if M['wmt_comp_rank_above_med'] else M['peer_eve_med']
EVE_SEL = put('eve_sel', M['reg_eve_wmt'] if M['reg_eve_ok'] else EVE_RULE)
WMT_EBITDA = put('wmt_ebitda_sa', 48.68)                          # EBITDA de los últimos 12 meses (stockanalysis, misma fuente que los pares)
WMT_EVE = put('wmt_eve', 22.24)
def eve_ps(mult): return (mult*WMT_EBITDA - NETDEBT_EV - MIN_MKT)/SH_DIL*1000
COMP_EV = put('comp_ev', eve_ps(EVE_SEL))
COMP = put('comp', (COMP_PE + COMP_EV)/2)
put('comp_low', min((M['peer_pe_med']*NTM + eve_ps(M['peer_eve_med']))/2, COMP))
put('comp_med_only', (M['peer_pe_med']*NTM + eve_ps(M['peer_eve_med']))/2)
put('comp_reg4', (M['reg_comp_pe_wmt4']*NTM + eve_ps(M['reg_eve']['icpt'] + M['reg_eve']['slope']*WMT_COMP4))/2)
put('comp_xcost_pe_val', M['reg_comp_xcost_pe_wmt']*NTM)
put('comp_high', (M['peer_pe_max']*NTM + eve_ps(M['peer_eve_max']))/2)
put('comp_gap', (COMP/PRICE-1)*100)
put('wmt_pe_vs_med', (M['pe_ntm_now']/M['peer_pe_med']-1)*100)
put('comp_pe_cost', M['peer_pe_max']*NTM)
put('comp_reg_pe_val', M['reg_comp_pe_wmt']*NTM)
put('amzn_pe', AMZN['pe'])
put('comp_wmt4_rank', 1 if WMT_COMP4 > M['peer_comp_med'] else 0)
put('comp_if_q3', (M['peer_pe_q3']*NTM + eve_ps(M['peer_eve_q3']))/2)

# ---------------- Reversión (Método 3, 35%) ----------------
d = json.load(open(HERE/'yh'/'WMT.mo.json'))['chart']['result'][0]
closes = {}
for ts, c in zip(d['timestamp'], d['indicators']['quote'][0]['close']):
    dt = datetime.datetime.fromtimestamp(ts, datetime.UTC)
    if c: closes[(dt.year, dt.month)] = c
seq = [(y, q) for y in range(2017, 2029) for q in range(4)]
QEND = {0: 4, 1: 7, 2: 10, 3: 1}      # mes de cierre del trimestre fiscal (abr, jul, oct, ene)
win = []
for i, (fy, q) in enumerate(seq):
    cal_y = fy - 1 if q < 3 else fy
    ym = (cal_y, QEND[q])
    if ym < (2016, 4) or ym > (2026, 10): continue
    nx = seq[i+1:i+5]
    ntm = sum(EPS[a][b] for a, b in nx)
    win.append(dict(date=f'{ym[0]}-{ym[1]:02d}', fy=fy, price=closes[ym], ntm=ntm, pe=closes[ym]/ntm))
M['rev_window'] = win
put('rev_n', len(win))
put('pe10_avg', st.mean(w['pe'] for w in win))
# Regla de re-rating: el escalón es "real" si desde un cierre en adelante TODOS los P/E superan el máximo de un rango previo
# establecido (al menos 20 cierres = cinco años) durante al menos 8 trimestres. La ventana nueva arranca en ese cierre.
# (Sin el mínimo de 20 cierres, la suba gradual de 15x a 24x de 2016-2021 dispararía la regla en 2017.)
RR_MIN_PRIOR, RR_MIN_AFTER = put('rr_min_prior', 20), put('rr_min_after', 8)
start = None
for i in range(RR_MIN_PRIOR, len(win)):
    prev_max = max(w['pe'] for w in win[:i])
    if all(w['pe'] > prev_max for w in win[i:]) and len(win) - i >= RR_MIN_AFTER:
        start = i; break
assert start is not None
put('rr_start', win[start]['date']); put('rr_n', len(win) - start)
put('rr_prev_max', max(w['pe'] for w in win[:start])); put('rr_prev_avg', st.mean(w['pe'] for w in win[:start]))
put('rr_fys', len(set(w['fy'] for w in win[start:])))
PE_RR = put('pe_rr_avg', st.mean(w['pe'] for w in win[start:]))
put('pe_rr_min', min(w['pe'] for w in win[start:])); put('pe_rr_max', max(w['pe'] for w in win[start:]))
put('pe_pre_min', min(w['pe'] for w in win[:start])); put('pe_pre_max', max(w['pe'] for w in win[:start]))
# P/E promedio por año fiscal
fyavg = {}
for w in win: fyavg.setdefault(w['fy'], []).append(w['pe'])
M['pe_by_fy'] = {str(k): dict(avg=st.mean(v), mn=min(v), mx=max(v), n=len(v)) for k, v in fyavg.items()}
REV1 = put('rev1', PE_RR*NTM)                                     # Lectura 1: P/E propio de la ventana post re-rating
# Lectura 2: P/E relativo al S&P 500, promedio de diez años (cociente de promedios: FactSet no publica serie trimestral)
# S&P 500: cierre del 20-nov-2026 (6,910.39) sobre el EPS de 12 meses de FactSet del 5-nov ($415.82); FactSet publicó 18.3x
# en su informe del 13-nov, antes de la caída de la semana del 17 al 20-nov. Promedio de diez años de FactSet: 19.1x.
SPX_PX, SPX_EPS = put('spx_px', 6910.39), put('spx_eps', 415.82)
SPX_PE, SPX_PE10 = put('spx_pe', SPX_PX/SPX_EPS), put('spx_pe10', 19.1)
put('spx_pe_13nov', 18.3)
REL10 = put('rel10', M['pe10_avg']/SPX_PE10)
put('rel_now', M['pe_ntm_now']/SPX_PE)
REV2 = put('rev2', REL10*SPX_PE*NTM)
REV = put('rev', (REV1 + REV2)/2)
put('rev2_13nov', REL10*M['spx_pe_13nov']*NTM); put('rev_13nov_d', (M['rev2_13nov']-REV2)/2)
put('rel_at_spx10', M['pe_ntm_now']/SPX_PE10)
put('rev_low', min(M['pe_rr_min']*NTM, REV2))
put('rev_high', M['pe_rr_max']*NTM)
put('rev1_min', M['pe_rr_min']*NTM)
put('rev_gap', (REV/PRICE-1)*100)
put('rev_10y_own', M['pe10_avg']*NTM)                             # referencia: P/E propio de diez años completo
put('rev_pre_own', M['rr_prev_avg']*NTM)
put('pe_now_vs_rr', (M['pe_ntm_now']/PE_RR-1)*100)
put('spx_vs_10', (SPX_PE/SPX_PE10-1)*100)

# ---------------- Consenso (Método 4, 25%) ----------------
# stockanalysis (S&P Global), 20-nov-2026 — misma fuente y mismo día que DIS (data/comun_2026-11-20.json)
CONS = put('cons', 135.90); put('cons_med', 138.0); put('cons_low', 81.0); put('cons_high', 155.0); put('cons_n', 41)
put('cons_sb', 28); put('cons_b', 10); put('cons_h', 5); put('cons_s', 0); put('cons_ss', 1); put('cons_sep', 127.43)
put('cons_gap', (CONS/PRICE-1)*100)

# ---------------- Blend ----------------
W = {'dcf': 0.075, 'sotp': 0.075, 'comp': 0.25, 'rev': 0.35, 'cons': 0.25}
V = {'dcf': M['dcf_base'], 'sotp': M['sotp_base'], 'comp': COMP, 'rev': REV, 'cons': CONS}
BLEND = put('blend', sum(W[k]*V[k] for k in W))
put('blend_gap', (BLEND/PRICE-1)*100)
for k in W: put(f'contrib_{k}', W[k]*V[k]); put(f'w_{k}', W[k]*100)
IND = ('dcf', 'sotp', 'comp'); ANC = ('rev', 'cons')
put('indep', sum(W[k]*V[k] for k in IND)/sum(W[k] for k in IND))
put('anch', sum(W[k]*V[k] for k in ANC)/sum(W[k] for k in ANC))
put('indep_gap', (M['indep']/PRICE-1)*100); put('anch_gap', (M['anch']/PRICE-1)*100)
put('m1_avg', (M['dcf_base'] + M['sotp_base'])/2)
def blend_with(**kw):
    v = dict(V); v.update(kw); return sum(W[k]*v[k] for k in W)
put('blend_rev10', blend_with(rev=(M['rev_10y_own'] + REV2)/2))       # reversión sin la regla de re-rating
put('blend_comp_q3', blend_with(comp=M['comp_if_q3']))
put('blend_vs_cons', (BLEND/CONS-1)*100)
for k in ('dcf_bull', 'dcf_bear', 'sotp_bull', 'sotp_bear'): put(f'{k}_gap', (M[k]/PRICE-1)*100)

# ---------------- Capital, dividendo, balance ----------------
DIV = put('div_annual', 0.99); put('div_yield', DIV/PRICE*100); put('div_prev', 0.94); put('div_raise', (0.99/0.94-1)*100)
put('div_streak', 53)                                             # años consecutivos de aumento del dividendo (desde 1974)
put('payout_eps', DIV/M['guide_mid']*100)
# Nueve meses FY27 (comunicado del 3T): 67.0 millones de acciones por $7.830 mil millones; quedan $22.4 de la autorización de $30.
# Claves heredadas *_1h = nueve meses; buyback_px_q2 = precio promedio pagado en el 3T.
put('buyback_auth', 30.0); put('buyback_left', 22.4); put('buyback_1h', 7.830); put('buyback_sh_1h', 67.0)
put('buyback_px_q2', (7.830-5.104)/(67.0-42.3)*1000)
put('buyback_px_9m', 7.830/67.0*1000)
put('div_paid_1h', 5.913)
put('fcf_yield', M['fcf_2026']/MKT_CAP*100); put('fcf_yield_ttm', M['ttm_fcf']/MKT_CAP*100)
put('walton_pct', 44.11)
put('capex_guide', 4.0)

# ---------------- Series para gráficos ----------------
M['js_ql'] = json.dumps([q[:2] + ' FY' + q[2:] for q in QL[2:]], ensure_ascii=False)
M['js_us_trx'] = json.dumps(US['trx'][2:]); M['js_us_tkt'] = json.dumps(US['tkt'][2:]); M['js_us_comp'] = json.dumps(US['comp'][2:])
M['js_sams_trx'] = json.dumps(SAMS['trx'][2:]); M['js_sams_tkt'] = json.dumps(SAMS['tkt'][2:]); M['js_sams_comp'] = json.dumps(SAMS['comp'][2:])
M['js_ecom_ql'] = json.dumps([f'{q}T FY{y}' for y in (25, 26) for q in (1, 2, 3, 4)] + ['1T FY27', '2T FY27', '3T FY27'])
M['js_ecom_q'] = json.dumps(ECOM_Q)
M['js_us_ecom'] = json.dumps(US['ecom'][3:])
assert len(US['ecom'][3:]) == len(ECOM_Q)
FYL = [str(y) for y in YRS]
M['js_fy'] = json.dumps(['FY' + y[2:] for y in FYL])
M['js_rev'] = json.dumps([round(REVY[y], 1) for y in YRS])
M['js_gm'] = json.dumps([round(M['ann'][y]['gm'], 2) for y in FYL])
M['js_opex'] = json.dumps([round(M['ann'][y]['opex'], 2) for y in FYL])
M['js_om'] = json.dumps([round(M['ann'][y]['om'], 2) for y in FYL])
M['js_turns'] = json.dumps([round(M['ann'][y]['turns'], 2) for y in FYL])
M['js_apinv'] = json.dumps([round(M['ann'][y]['ap_inv'], 1) for y in FYL])
M['js_ocf'] = json.dumps([round(OCF[y], 2) for y in YRS]); M['js_capex'] = json.dumps([round(CAPEX[y], 2) for y in YRS])
M['js_fcf'] = json.dumps([round(OCF[y]-CAPEX[y], 2) for y in YRS])
M['js_pe_labels'] = json.dumps([(w['date'][:4] if w['date'][5:] == '04' else '') for w in win])
M['js_pe_vals'] = json.dumps([round(w['pe'], 2) for w in win])
M['js_pe_rr_full'] = json.dumps([round(PE_RR, 2)]*len(win))
M['js_pe_10'] = json.dumps([round(M['pe10_avg'], 2)]*len(win))
# sparkline: últimos 7 cierres mensuales (may-2026 a oct-2026 + 20-nov-2026)
SPARK = [closes[(2026, m)] for m in range(5, 11)] + [PRICE]
M['spark'] = [round(x, 2) for x in SPARK]
put('ret_ytd', (PRICE/closes[(2025, 12)]-1)*100); put('px_dec25', closes[(2025, 12)])
put('ret_from_apr', (PRICE/closes[(2026, 4)]-1)*100)
put('ret_1y', (PRICE/closes[(2025, 10)]-1)*100)
# derivados de texto
put('pe_ntm_vs_10', (M['pe_ntm_now']/M['pe10_avg']-1)*100)
put('dcf_base_vs_sotp', (M['sotp_base']/M['dcf_base']-1)*100)
put('mkt_cap_b', MKT_CAP); put('ev_b', MKT_CAP + NETDEBT_EV + MIN_MKT)
put('ops_value_in_price', MKT_CAP - M['intl_marks'] + NETDEBT_DCF)
put('ops_ev_ebitda', M['ops_value_in_price']/WMT_EBITDA)
put('ads_g26_rep', 46)                               # crecimiento informado por Walmart (comunicado del 4T FY2026)
put('base_us_trx', SC['base']['us_trx'])
put('div_minus_rf', M['div_yield'] - RF); put('fcf_minus_rf', M['fcf_yield'] - RF); put('rf_over_fcf', RF/M['fcf_yield'])
put('walmex_minority', 100 - WALMEX_STAKE); put('flip_minority', 100 - FLIP_STAKE); put('pp_minority', 100 - PP_STAKE)
put('goodwill', 28.260); put('goodwill_pct', 28.260/293.914*100)
put('buyback_vs_apr', (M['buyback_px_q2']/closes[(2026, 4)]-1)*100)
put('wacc_minus_impl', WACC - M['impl_wacc'])
put('us_dm_hist', (SEG['us']['m'] - SEG['us']['m24'])/2*100)
CONS_M26 = ADJ_OI[2026]/REVY[2026]*100
put('guide_dm', (CONS_M26*(1+7.75/100)/(1+4.5/100) - CONS_M26)*100)
put('q2_gm_bp', (M['q2_gm'] - M['q2_gm_py'])*100); put('q2_opex_bp', (M['q2_opex'] - M['q2_opex_py'])*100)
put('q2_rev_g', (Q2['rev']/Q2['rev_py']-1)*100)
put('legal_fy26', 0.440 - 0.155)
gm_ser = {y: M['ann'][str(y)]['gm'] for y in YRS}
put('gm26_best_since', max(y for y in YRS if y < 2026 and gm_ser[y] >= gm_ser[2026]) if any(gm_ser[y] >= gm_ser[2026] for y in YRS if y < 2026) else 0)
put('capex_pct_min_1621', min(M['ann'][str(y)]['capex_pct'] for y in range(2016, 2022)))
put('capex_pct_max_1621', max(M['ann'][str(y)]['capex_pct'] for y in range(2016, 2022)))
put('turns_min_year', min(YRS, key=lambda y: M['ann'][str(y)]['turns']))

# ---------------- Antes → ahora (edición del 29-sep-2026, reproducida al centavo con el modelo de esa fecha) ----------------
SEP = {'dcf': 40.3169, 'sotp': 45.0756, 'comp': 52.3098, 'rev': 89.7505, 'cons': 127.43}
M['sep'] = SEP
for k in SEP: put(f'chg_{k}', V[k] - SEP[k])
put('blend_chg', BLEND - BLEND_SEP); put('blend_chg_pct', (BLEND/BLEND_SEP-1)*100)
put('price_chg_pct', (PRICE/PRICE_SEP-1)*100); put('blend_sep_gap', (BLEND_SEP/PRICE_SEP-1)*100)
for k in W: put(f'chg_contrib_{k}', W[k]*(V[k]-SEP[k]))
assert abs(sum(M[f'chg_contrib_{k}'] for k in W) - M['blend_chg']) < 0.01
# Asserts que atan las frases cualitativas de la plantilla a los números (si fallan, hay que reescribir el texto)
assert M['indep'] < PRICE/2                                    # "vale menos de la mitad de su precio"
assert M['anch'] < PRICE and CONS > PRICE and REV < PRICE       # "solo el consenso queda por encima"
assert M['pe_ntm_now'] > 2*M['peer_pe_med']                     # "más del doble que la mediana"
assert M['impl_wacc'] < RF                                      # "por debajo de la propia tasa libre de riesgo"
assert M['buyback_px_q2'] < PRICE                               # "por debajo del precio de la fecha de corte"
assert SPX_PE < SPX_PE10                                        # "el S&P cotiza por debajo de su promedio"
assert M['reg_ok'] == 1 and M['reg_comp']['r2'] < 0.55          # "apenas por encima del umbral"
assert WMT_COMP < M['peer_comp_med'] and WMT_COMP4 < M['peer_comp_med']   # "debajo de la mitad del grupo" / "apenas debajo"
assert M['n9_adj_oi_g_cc'] > 8.6                                # "por encima de la guía anual"
json.dump(M, open(HERE/'model.json', 'w'), indent=1, default=float)
if __name__ == '__main__':
    skip = ('js_',)
    for k, v in M.items():
        if isinstance(v, (int, float)) and not isinstance(v, bool): print(f'{k:24s} {v:,.4f}')
    print('peers:'); [print(' ', k, round(p['pe'], 2), p['comp'], round(p['g'], 1), p['eve']) for k, p in PEERS.items()]
    print('reg', M['reg_comp'], M['reg_comp_xcost'], M['reg_g'], M['reg_g_xcost'])
    print('sotp', {k: round(v['ev'], 1) for k, v in M['sotp'].items()})
    for w in win: print(w['date'], w['fy'], round(w['price'], 2), round(w['ntm'], 3), round(w['pe'], 2))
    for r in M['dcf_base_tot']: print(r)
