# Modelo de valuación PEP (PepsiCo) — todos los números derivados del informe salen de acá.
# Marco: informe-consumo-masivo, sub-industria bebidas sin alcohol + alimentos/snacks (modelo integrado: fabrica,
# embotella y distribuye directo a la tienda). Pipeline copiado de modelos/ko/ y adaptado.
# Fuentes: 10-K 2025 (3-feb-2026) y 10-K 2016-2024, 10-Q 1T/2T 2026, comunicados 8-K ítem 2.02 (4T2015-2T2026), 8-K del
# 8-dic-2025 (plan con Elliott), carta de Elliott (2-sep-2025), Yahoo, Nasdaq/Zacks, stockanalysis (S&P Global),
# FactSet Earnings Insight, y modelos/ko/model.json para la comparación con Coca-Cola.
# Fecha de corte de precios: cierre del 1-oct-2026 (PEP, KO, pares, ^TNX).
import json, datetime, statistics as st, os
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)

M = {}
def put(k, v): M[k] = v; return v
CUT = '2026-10-01'
def yh_rows(t):
    d = json.load(open(f'yh/{t}.d.json'))['chart']['result'][0]
    return [(datetime.datetime.fromtimestamp(a, datetime.UTC).date().isoformat(), c)
            for a, c in zip(d['timestamp'], d['indicators']['quote'][0]['close']) if c]
def yh_close(t, day=CUT): return [r for r in yh_rows(t) if r[0] <= day][-1][1]
def yh_last(t): return yh_rows(t)[-1][1]
SA = json.load(open('data/sa_stats.json'))

# ---------------- Mercado (cierre 1-oct-2026) ----------------
PRICE = put('price', yh_close('PEP'))
RF = put('rf', yh_close('^TNX'))
ERP = put('erp', 5.0)
SH_DIL = put('sh_dil', 1369.0)       # diluidas promedio 2T26 (millones; comunicado del 2T26)
SH_OUT = put('sh_out', 1366.0)       # en circulación al 13-jun-2026 (balance del 2T26)
MKT_CAP = put('mkt_cap', PRICE*SH_OUT/1000)   # US$ miles de millones
SPX_PE, SPX_PE10 = put('spx_pe', 19.2), put('spx_pe10', 19.0)   # FactSet, 25-sep-2026 (mismo dato que KO y PG)
put('px_feb_hi', 169.74)             # cierre mensual de feb-2026 (Yahoo), máximo del año

# ---------------- Consenso de EPS core (Nasdaq / Zacks, 2-oct-2026) ----------------
NQ = json.load(open('data/nasdaq_eps.json'))
def nq(t):
    rows = NQ[t]['yearlyForecast']['rows']
    return [float(r['consensusEPSForecast']) for r in rows], [int(r['noOfEstimates']) for r in rows]
(C26, C27, C28, _), (n26, n27, n28, _) = nq('PEP')
put('c26', C26); put('c27', C27); put('c28', C28); put('c26_n', n26); put('c27_n', n27); put('c28_n', n28)
put('c26_sa', 8.55); put('c27_sa', 8.93)   # stockanalysis (S&P Global), 2-oct-2026, referencia
REV_C26 = put('rev_c26', 98.90)            # consenso de ventas 2026 (S&P Global, 21 analistas), US$ miles de millones
OI_C26 = put('oi_c26', 15.88)              # consenso de resultado operativo 2026 (S&P Global)
FCF_C26 = put('fcf_c26', 10.52)            # consenso de flujo de caja libre 2026 (S&P Global)
NI_C26_SA = put('ni_c26_sa', 11.32)        # consenso de utilidad neta 2026 (S&P Global)
EPS25 = put('eps25', 8.14); EPS24 = put('eps24', 8.16)
GUIDE_LO, GUIDE_HI = put('guide_lo', 5.0), put('guide_hi', 7.0)   # core EPS 2026, con monedas (guía del 9-jul-2026)
put('guide_eps_lo', EPS25*(1+GUIDE_LO/100)); put('guide_eps_hi', EPS25*(1+GUIDE_HI/100))
GUIDE_MID = put('guide_mid', (M['guide_eps_lo']+M['guide_eps_hi'])/2)
NTM = put('eps_ntm', 0.25*C26 + 0.75*C27)        # oct-2026 a sep-2027 (misma convención que KO y los pares)
put('pe_ntm_now', PRICE/NTM)
put('eps_g26', (C26/EPS25-1)*100); put('eps_g27', (C27/C26-1)*100); put('eps_g28', (C28/C27-1)*100)
put('pep_g2', ((C28/C26)**0.5-1)*100)
put('pe_c28', PRICE/C28)

# ---------------- EPS core trimestral (comunicados 8-K ítem 2.02; raw/eps_extract.py) ----------------
EPS = {2016:[0.89,1.35,1.40,1.20], 2017:[0.94,1.50,1.48,1.31], 2018:[0.96,1.61,1.59,1.49],
       2019:[0.97,1.54,1.56,1.45], 2020:[1.07,1.32,1.66,1.47], 2021:[1.21,1.72,1.79,1.53],
       2022:[1.29,1.86,1.97,1.67], 2023:[1.50,2.09,2.25,1.78], 2024:[1.61,2.28,2.31,1.96],
       2025:[1.48,2.12,2.29,2.26], 2026:[1.61,2.20]}
FYEPS = {2016:4.85, 2017:5.23, 2018:5.66, 2019:5.53, 2020:5.52, 2021:6.26, 2022:6.79, 2023:7.62, 2024:8.16, 2025:8.14}
GAAP = {2016:4.36, 2017:3.38, 2018:8.78, 2019:5.20, 2020:5.12, 2021:5.49, 2022:6.42, 2023:6.56, 2024:6.95, 2025:6.00}
for y, v in FYEPS.items():
    assert abs(sum(EPS[y]) - v) < 0.025, (y, sum(EPS[y]), v)
# 2S26 con el consenso anual y la estacionalidad de 2025 (el 4T es de 16 semanas); 2027-2028 con el consenso
s25 = [x/sum(EPS[2025]) for x in EPS[2025]]
h2 = C26 - sum(EPS[2026])
EPS[2026] = EPS[2026] + [h2*s25[2]/(s25[2]+s25[3]), h2*s25[3]/(s25[2]+s25[3])]
EPS[2027] = [C27*s for s in s25]; EPS[2028] = [C28*s for s in s25]
put('eps_2h26_impl', h2)
M['gaap_gap'] = {str(y): (GAAP[y]/FYEPS[y]-1)*100 for y in GAAP}
# Regla de ventana limpia (declarada): se excluye el año si los deterioros de marcas/inversiones y los efectos de leyes
# impositivas (no la reestructuración, que PepsiCo registra todos los años desde el plan de 2019) superan 10% del EPS core.
# US$ por acción, después de impuestos, según los 10-K de cada año (ítems "impairment and other charges" y reforma tributaria).
SHOCK = {2016:0.26,          # deterioro de la participación en Tingyi/TAB (10-K 2016)
         2017:1.70,          # reforma tributaria de EE.UU. (TCJ Act)
         2018:3.05+0.26+0.24,# beneficios impositivos por reorganización internacional y cierre de auditorías
         2019:0.01, 2020:0.0,
         2021:0.14,          # ajuste del TCJ Act por la auditoría 2014-2016 (el cargo por recompra de bonos, $0.49, es financiero)
         2022:0.69+0.78+0.06,# marcas en Rusia, SodaStream y TCJ Act (la ganancia por la venta de jugos, $2.08, no compensa)
         2023:0.73,          # SodaStream (marca y goodwill) y otros deterioros
         2024:0.42,          # Tropicana Brands Group (inversión y cuentas a cobrar)
         2025:1.09}          # Rockstar y Be & Cheery
EXCL_RULE = put('excl_rule', 10.0)
M['shock_pct'] = {str(y): SHOCK[y]/FYEPS[y]*100 for y in SHOCK}
EXCL = sorted(y for y in SHOCK if SHOCK[y]/FYEPS[y]*100 > EXCL_RULE)
M['excl_years'] = EXCL
put('excl_list', ', '.join(str(y) for y in EXCL[:-1]) + ' y ' + str(EXCL[-1]))
EXCL_KO = sorted(y for y in GAAP if abs(GAAP[y]/FYEPS[y]-1)*100 > EXCL_RULE)   # regla mecánica de KO, para mostrar
M['excl_ko_rule'] = EXCL_KO
put('excl_ko_rule_n', len(EXCL_KO))
put('excl_ko_rule_list', ', '.join(str(y) for y in EXCL_KO[:-1]) + ' y ' + str(EXCL_KO[-1]))

# ---------------- Descomposición del orgánico (comunicados; % sobre el trimestre del año anterior) ----------------
Q = ['3T23','4T23','1T24','2T24','3T24','4T24','1T25','2T25','3T25','4T25','1T26','2T26']
# reportado, ajuste por monedas, ajuste por compras/ventas, ajuste por la semana 53 (tal como figuran en la tabla de PepsiCo:
# lo que se suma al reportado para llegar al orgánico), orgánico, volumen orgánico (efecto en ventas), precio efectivo neto,
# volumen unitario de snacks ("convenient foods") y de bebidas (incluye cajas de embotelladoras franquiciadas)
ORG = {
 '3T23':(7, 2, 0, 0, 9, -2.5, 11, -1.5, 0), '4T23':(-0.5, 1.5, 0, 3, 4.5, -4, 9, -3, -2),
 '1T24':(2, 0.5, 0, 0, 3, -2, 5, -0.5, 0),  '2T24':(1, 1, 0, 0, 2, -3, 5, -2, 0),
 '3T24':(-1, 2, 0, 0, 1, -2, 3, -2, -2),    '4T24':(0, 2, 0, 0, 2, -1, 3, 1, 1),
 '1T25':(-2, 3, 0, 0, 1, -2, 3, -3, 0),     '2T25':(1, 1.5, 0, 0, 2, -1.5, 4, -1.5, 0),
 '3T25':(3, -0.5, -1, 0, 1, -3, 4, -1, -1), '4T25':(6, -2, -1, 0, 2, -2, 4.5, -2, 1),
 '1T26':(9, -3, -2.5, 0, 3, 0, 2, 4, 0),    '2T26':(6, -2, -2, 0, 2, 1, 2, 3, 2)}
M['org'] = {q: dict(rep=v[0], fx=-v[1], ad=-v[2], w53=-v[3], org=v[4], vol=v[5], price=v[6], cf=v[7], bev=v[8]) for q, v in ORG.items()}
L8 = Q[-8:]; L4 = Q[-4:]
def avg(key, qs): return st.mean(M['org'][q][key] for q in qs)
for key in ('org', 'vol', 'price', 'cf', 'bev'):
    put(f'{key}_8q', avg(key, L8)); put(f'{key}_4q', avg(key, L4))
put('price_3q', avg('price', Q[-3:])); put('org_12q', avg('org', Q)); put('vol_12q', avg('vol', Q))
put('price_2024_avg', avg('price', ['1T24','2T24','3T24','4T24'])); put('vol_2024_avg', avg('vol', ['1T24','2T24','3T24','4T24']))
put('neg_vol_q', sum(1 for q in Q if M['org'][q]['vol'] < 0))
# Norteamérica por negocio: PFNA (snacks y Quaker) y PBNA (bebidas). Desde 1T25 segmentos nuevos; 3T24 y 4T24 = FLNA + QFNA
# ponderados por las ventas del año anterior (3T23: 5,954 / 747; 4T23: 7,473 / 893), cálculo propio.
OLD = {'3T24': dict(w=(5954, 747), flna=(-1, -1, 0.5), qfna=(-13, -13, 0), pbna=(1, -3, 3)),
       '4T24': dict(w=(7473, 893), flna=(-2, -3, 1), qfna=(-2, -6, 4), pbna=(0, -3, 3))}
NA = {'1T25': dict(pfna=(-2, -3, 1), pbna=(1, -1, 2)), '2T25': dict(pfna=(-2, -1.5, 0), pbna=(1, -4, 4.5)),
      '3T25': dict(pfna=(-3, -4, 2), pbna=(2, -4, 6)), '4T25': dict(pfna=(-1, -2, 1), pbna=(2, -5, 7)),
      '1T26': dict(pfna=(1, 2, -1), pbna=(2, -4, 6)), '2T26': dict(pfna=(-2, 0, -2), pbna=(1, -2, 3))}
for q, o in OLD.items():
    a, b = o['w']
    NA[q] = dict(pfna=tuple((a*o['flna'][i] + b*o['qfna'][i])/(a+b) for i in range(3)), pbna=o['pbna'])
NQS = ['3T24','4T24','1T25','2T25','3T25','4T25','1T26','2T26']
M['na'] = {q: dict(pfna_org=NA[q]['pfna'][0], pfna_vol=NA[q]['pfna'][1], pfna_price=NA[q]['pfna'][2],
                   pbna_org=NA[q]['pbna'][0], pbna_vol=NA[q]['pbna'][1], pbna_price=NA[q]['pbna'][2]) for q in NQS}
for k in ('pfna_org', 'pfna_vol', 'pfna_price', 'pbna_org', 'pbna_vol', 'pbna_price'):
    put(f'{k}_8q', st.mean(M['na'][q][k] for q in NQS))
put('pbna_vol_neg_q', sum(1 for q in NQS if M['na'][q]['pbna_vol'] < 0))
ANN = {2019:(4.5, 2, 2), 2020:(4, 4, 0), 2021:(10, 2.5, 10), 2022:(14, 0, 3.5), 2023:(9, -2, -1), 2024:(2, -1, 0), 2025:(2, -2, 0)}  # orgánico, volumen snacks, volumen bebidas (comunicados del 4T)
M['ann_org'] = {str(y): dict(org=v[0], cf=v[1], bev=v[2]) for y, v in ANN.items()}

# ---------------- Consolidado (XBRL + comunicados) ----------------
REV = {2016:62.799, 2017:63.525, 2018:64.661, 2019:67.161, 2020:70.372, 2021:79.474, 2022:86.392, 2023:91.471, 2024:91.854, 2025:93.925}
M['rev_hist'] = {str(k): v for k, v in REV.items()}
put('rev_cagr_1625', ((REV[2025]/REV[2016])**(1/9)-1)*100)
COREGP = {2022:46.102, 2023:49.737, 2024:50.611, 2025:51.155}
COREOP = {2022:12.325, 2023:13.875, 2024:14.698, 2025:14.912}
M['comp_gm'] = {str(y): COREGP[y]/REV[y]*100 for y in COREGP}; M['comp_om'] = {str(y): COREOP[y]/REV[y]*100 for y in COREOP}
REV_1H26, REV_1H25 = 43.624, 40.645
COREOP_1H26, COREOP_1H25 = 7.117, 6.700
COREGP_1H26, COREGP_1H25 = 23.833, 22.509
M['comp_om']['1S26'] = COREOP_1H26/REV_1H26*100; M['comp_gm']['1S26'] = COREGP_1H26/REV_1H26*100
put('om_1h25', COREOP_1H25/REV_1H25*100); put('gm_1h25', COREGP_1H25/REV_1H25*100)
AM = {2021:5.1, 2022:5.2, 2023:5.7, 2024:5.9, 2025:5.4}     # publicidad y otras actividades de marketing (10-K)
ADV = {2021:3.5, 2022:3.5, 2023:3.8, 2024:3.9, 2025:3.4}    # de los cuales, publicidad
M['am_pct'] = {str(y): AM[y]/REV[y]*100 for y in AM}; M['adv_pct'] = {str(y): ADV[y]/REV[y]*100 for y in ADV}
put('am_cut25', AM[2024]-AM[2025]); put('am_cut25_pct_op', (AM[2024]-AM[2025])/COREOP[2025]*100)
DA25, DA_1H25, DA_1H26 = 3.451, 1.491, 1.639
TTM_REV = put('ttm_rev', REV[2025] - REV_1H25 + REV_1H26)
TTM_COI = put('ttm_coi', COREOP[2025] - COREOP_1H25 + COREOP_1H26)
TTM_DA = put('ttm_da', DA25 - DA_1H25 + DA_1H26)
EBITDA_TTM = put('ebitda_ttm', TTM_COI + TTM_DA)
put('ttm_om', TTM_COI/TTM_REV*100)
put('coi_1h26_g', (COREOP_1H26/COREOP_1H25-1)*100)
put('rev_1h26_g', (REV_1H26/REV_1H25-1)*100)

# Segmentos 2025 (10-K, nota 1): ventas, resultado operativo core (comunicado del 4T25), capex y D&A.
SEG = {  # ventas, OP core, capex, D&A (US$ miles de millones), fracción de alimentos
 'PFNA': (27.528, 6.545, 1.051, 0.969, 1.0), 'PBNA': (28.197, 3.285, 1.344, 1.093, 0.0),
 'IBF':  (4.997, 1.856, 0.124, 0.109, 0.0),  'EMEA': (18.025, 2.571, 0.744, 0.549, 0.63),
 'LAF':  (10.549, 2.144, 0.672, 0.417, 1.0), 'APF':  (4.629, 0.464, 0.257, 0.153, 1.0)}
CORP = dict(op=-1.953, capex=0.223, da=0.161)
SEG_1H = {'PFNA': ((12.700, 2.874), (12.689, 3.063)), 'PBNA': ((13.634, 1.631), (12.672, 1.589)),
          'IBF': ((2.347, 0.966), (2.127, 0.817)), 'EMEA': ((7.806, 1.068), (6.924, 0.890)),
          'LAF': ((4.874, 1.051), (4.209, 0.896)), 'APF': ((2.263, 0.352), (2.024, 0.254))}
SEG24 = {'PFNA': (27.431, 6.982), 'PBNA': (27.769, 3.104), 'IBF': (4.879, 1.708), 'EMEA': (16.658, 2.232), 'LAF': (10.568, 2.101), 'APF': (4.549, 0.391)}
M['seg'] = {}
for k, (r, op, cx, da, ff) in SEG.items():
    (r1, o1), (r0, o0) = SEG_1H[k]
    M['seg'][k] = dict(rev=r, op=op, om=op/r*100, om24=SEG24[k][1]/SEG24[k][0]*100, om_1h26=o1/r1*100, om_1h25=o0/r0*100,
                       capex=cx, da=da, share=r/REV[2025]*100, foods=ff)
put('corp_op', CORP['op'])
# Snacks (alimentos) vs. bebidas: EMEA se reparte 63/37 por ventas (10-K) y su resultado en la misma proporción (supuesto);
# los gastos corporativos no asignados se reparten por ventas.
def biz(field, foods=True):
    return sum(v[field]*(v['foods'] if foods else 1-v['foods']) for v in M['seg'].values())
FOODS_REV, BEV_REV = put('foods_rev', biz('rev')), put('bev_rev', biz('rev', False))
put('foods_share', FOODS_REV/REV[2025]*100); put('bev_share', BEV_REV/REV[2025]*100)
FS = FOODS_REV/REV[2025]
put('foods_op', biz('op') + FS*CORP['op']); put('bev_op', biz('op', False) + (1-FS)*CORP['op'])
put('foods_om', M['foods_op']/FOODS_REV*100); put('bev_om', M['bev_op']/BEV_REV*100)
put('foods_da', biz('da') + FS*CORP['da']); put('bev_da', biz('da', False) + (1-FS)*CORP['da'])
put('foods_capex', biz('capex') + FS*CORP['capex']); put('bev_capex', biz('capex', False) + (1-FS)*CORP['capex'])
for b in ('foods', 'bev'):
    put(f'{b}_ebitda', M[f'{b}_op'] + M[f'{b}_da']); put(f'{b}_ec', M[f'{b}_ebitda'] - M[f'{b}_capex'])
    put(f'{b}_capex_pct', M[f'{b}_capex']/M[f'{b}_rev']*100)
put('foods_cash_share', M['foods_ec']/(M['foods_ec']+M['bev_ec'])*100)
put('pfna_share', M['seg']['PFNA']['share']); put('pbna_share', M['seg']['PBNA']['share'])
put('na_share', M['pfna_share'] + M['pbna_share'])
put('us_rev', 52.228); put('us_rev_pct', 52.228/REV[2025]*100); put('intl_rev_pct', 100 - M['us_rev_pct'])
put('russia_pct', 4.768/REV[2025]*100); put('mexico_pct', 6.947/REV[2025]*100)
put('wmt_pct', 14.0)
put('bottler_pct', 36.0)   # bebidas de embotelladoras propias como % de las ventas (10-K 2025, nota 1)
put('pfna_om_drop', M['seg']['PFNA']['om24'] - M['seg']['PFNA']['om'])

# ---------------- Flujo de caja (10-K, comunicados) ----------------
OCF = {2019:9.649, 2020:10.613, 2021:11.616, 2022:10.811, 2023:13.442, 2024:12.507, 2025:12.087}
CAPEX = {2019:4.232, 2020:4.240, 2021:4.625, 2022:5.207, 2023:5.518, 2024:5.318, 2025:4.415}
TCJA = {2019:0.423, 2020:0.078, 2021:0.309, 2022:0.309, 2023:0.309, 2024:0.579, 2025:0.772}   # cuotas del impuesto de transición
OCF_ADJ = {y: OCF[y] + TCJA.get(y, 0) for y in OCF}
M['ocf'] = {str(y): OCF[y] for y in OCF}; M['ocf_adj'] = {str(y): OCF_ADJ[y] for y in OCF}
M['capex'] = {str(y): CAPEX[y] for y in CAPEX}; M['fcf_adj'] = {str(y): OCF_ADJ[y]-CAPEX[y] for y in OCF}
DIVP = {2021:5.815, 2022:6.172, 2023:6.682, 2024:7.229, 2025:7.638}
BUY = {2021:0.106, 2022:1.500, 2023:1.000, 2024:1.000, 2025:1.000}
M['divp'] = {str(y): v for y, v in DIVP.items()}; M['buy'] = {str(y): v for y, v in BUY.items()}
M['ret_fcf'] = {str(y): (DIVP[y]+BUY[y])/(OCF_ADJ[y]-CAPEX[y])*100 for y in DIVP}
M['ocf_adj_m'] = {str(y): OCF_ADJ[y]*1000 for y in OCF}; M['fcf_adj_m'] = {str(y): (OCF_ADJ[y]-CAPEX[y])*1000 for y in OCF}
TCJA26 = put('tcja26', 0.965)       # cuota final pagada en el 1S26 (10-Q); "cerca de US$ 1 mil millones" según la guía
PPE_SALES25 = put('ppe_sales25', 0.528)
put('ocf_1h26', 2.365); put('ocf_1h25', 0.996); put('capex_1h26', 1.266)
TAX = put('tax', 22.0)                      # tasa efectiva core guiada 2026
TAX25 = put('tax25', 19.5)                  # tasa efectiva core 2025
t = TAX/100
NI_C25 = put('ni_c25', 11.176)              # utilidad core 2025 (comunicado del 4T25)
NI_C26 = put('ni_c26', C26*SH_DIL/1000)
CONV_G26 = put('conv_g26', 80.0)            # guía: conversión de FCF de al menos 80% (incluye la cuota final del TCJA)
FCF_G26 = put('fcf_g26', CONV_G26/100*NI_C26)   # piso de la guía, definición de PepsiCo (con ventas de activo fijo)
CAPEX_G26_PCT = put('capex_g26_pct', 5.0)   # guía: capex por debajo de 5% de las ventas
put('fcf25_pep', OCF[2025] - CAPEX[2025] + PPE_SALES25)          # definición de PepsiCo
put('conv25_pep', M['fcf25_pep']/NI_C25*100)
put('conv25', (OCF_ADJ[2025]-CAPEX[2025])/NI_C25*100)            # misma definición que KO: OCF ajustado − capex
put('conv25_raw', (OCF[2025]-CAPEX[2025])/NI_C25*100)
put('capex_pct25', CAPEX[2025]/REV[2025]*100); put('capex_pct24', CAPEX[2024]/REV[2024]*100)
put('capex_pct23', CAPEX[2023]/REV[2023]*100)
put('conv_c26', FCF_C26/NI_C26_SA*100)
NETINT25 = put('netint25', 1.121); NETINT26 = put('netint26', 2*0.531)   # "net interest expense and other"; 1S26 anualizado

# ---------------- Dividendo ----------------
DPS = {2016:2.96, 2017:3.1675, 2018:3.5875, 2019:3.7925, 2020:4.0225, 2021:4.2475, 2022:4.525, 2023:4.945, 2024:5.33, 2025:5.6225}
M['dps'] = {str(y): v for y, v in DPS.items()}
DIV = put('div_annual', 5.92)               # anualizado desde junio de 2026 (comunicado del 3-feb-2026)
put('div_q', DIV/4)
put('div_yield', DIV/PRICE*100)
put('div_raise', (5.92/5.69-1)*100)
put('div_cagr', ((DPS[2025]/DPS[2016])**(1/9)-1)*100)
put('payout_eps', DIV/C26*100)
put('div_g26', 7.9)                         # guía de dividendos 2026 (US$ miles de millones)
put('payout_fcf', M['div_g26']/FCF_G26*100)                 # sobre el piso de la guía de FCF
put('payout_fcf_c', M['div_g26']/FCF_C26*100)               # sobre el consenso de FCF
put('payout_fcf25', DIVP[2025]/M['fcf25_pep']*100)
put('div_streak', 54)
put('fcf_yield', FCF_C26/MKT_CAP*100)       # consenso de FCF 2026 / capitalización (misma definición para KO)
put('buyback_g26', 1.0); put('cash_ret_g26', 8.9)

# ---------------- Balance (10-Q 2T26, 13-jun-2026) ----------------
DEBT = put('debt', 10.602 + 42.612)
CASH = put('cash', 10.251 + 0.465)
NETDEBT = put('net_debt', DEBT - CASH)
LEASES = put('leases', 3.846)               # pasivo por arrendamientos operativos (10-K 2025)
NETDEBT_L = put('net_debt_l', NETDEBT + LEASES)
NCI = put('nci', 0.172)
put('nd_ebitda', NETDEBT/EBITDA_TTM); put('nd_ebitda_l', NETDEBT_L/(EBITDA_TTM))
BS = {'jun': dict(cash=10251+465, dst=10602, dlt=42612, eqm=2180, gw=19093+13990+1187, eq=22098, ta=112189, ar=13496, inv=6734, ap=24504),
      'dec': dict(cash=9159+371, dst=6861, dlt=42321, eqm=2038, gw=18916+13847+1219, eq=20406, ta=107399, ar=11506, inv=5845, ap=25903)}
for v in BS.values(): v['nd'] = v['dst'] + v['dlt'] - v['cash']
M['bs'] = BS
assert abs(BS['jun']['nd']/1000 - NETDEBT) < 1e-9
put('gw_int_pct', BS['jun']['gw']/BS['jun']['ta']*100)
put('debt_st', 10.602)
EQM = put('eqm', 2.180)                     # participaciones por el método de participación (valor contable)

# ---------------- Celsius: acciones preferidas convertibles (10-K 2025, notas 4 y 9) ----------------
CELH_A, CELH_B = 0.550, 0.585               # costo de las series A (2022, a $25 por acción) y B (2025, a $51.75)
put('celh_sh', CELH_A/25 + CELH_B/51.75)    # miles de millones de acciones comunes si convierten
CELH_PX = put('celh_px', yh_close('CELH'))
put('celh_conv', M['celh_sh']*CELH_PX)
put('celh_redeem', CELH_A + CELH_B)
put('celh_fv25', 1.852)                     # valor razonable en libros al 27-dic-2025 (nivel 3)
CELH = put('celh_val', max(M['celh_conv'], M['celh_redeem']))
put('celh_conv_px', M['celh_redeem']/M['celh_sh'])   # precio de Celsius al que convertir iguala el rescate
NONOP = put('nonop', CELH + EQM)
put('nonop_ps', NONOP/SH_DIL*1000); put('celh_ps', CELH/SH_DIL*1000); put('eqm_ps', EQM/SH_DIL*1000)

# ---------------- Costo de capital ----------------
BETAS = {'KO': SA['KO']['beta'], 'KDP': SA['KDP']['beta'], 'MNST': SA['MNST']['beta']}   # stockanalysis, 5 años mensual
BETA_PEP = put('beta_pep', SA['PEP']['beta'])
M['betas'] = BETAS
beta_med = put('beta_med', st.median(BETAS.values()))
beta_adj = put('beta_adj', 0.67*beta_med + 0.33)
beta_adj_own = put('beta_adj_own', 0.67*BETA_PEP + 0.33)
KE_FLOOR = put('ke_floor', RF + 2.5)
KE = put('ke', max(RF + beta_adj*ERP, KE_FLOOR))
KE_OWN = put('ke_own', max(RF + beta_adj_own*ERP, KE_FLOOR))
KD_PRE = put('kd_pre', RF + 0.60)    # supuesto: bono largo A+/A1 ~60 pb sobre el Treasury (mismo que KO)
KD = put('kd', KD_PRE*(1-t))
E = MKT_CAP
WD = put('wd', DEBT/(DEBT+E)*100)
def wacc(ke): return (1-WD/100)*ke + WD/100*KD
WACC = put('wacc', wacc(KE)); WACC_OWN = put('wacc_own', wacc(KE_OWN))

# ---------------- Margen de caja anclado en el flujo operativo real ----------------
# FCF sin apalancar = OCF + cuota del TCJA (pago que no se repite: la última fue en 2026) + intereses netos x (1-t) - capex.
# No suma las ventas de activo fijo (misma definición que KO). Las participaciones (Celsius, participadas) se suman aparte.
F25 = put('f25', OCF_ADJ[2025] + NETINT25*(1-t) - CAPEX[2025])
F26 = put('f26', FCF_G26 + TCJA26 + NETINT26*(1-t) - 2*0.071)   # piso de la guía (menos ventas de activo fijo: 1S26 x 2)
put('f25_m', F25/REV[2025]*100); put('f26_m', F26/REV_C26*100)
M_BASE = put('m_base', (F25+F26)/(REV[2025]+REV_C26)*100)
put('m_raw25', (OCF[2025] + NETINT25*(1-t) - CAPEX[2025])/REV[2025]*100)   # sin sumar el TCJA
REV0 = put('rev0', REV_C26)
# Reparto del margen entre negocios: proporcional al resultado operativo core + D&A − capex de cada uno (2025)
CASH_F = M['foods_ec']; CASH_B = M['bev_ec']
SH_F = M['foods_share']/100
k_m = (M_BASE/100*REV[2025]) / (CASH_F + CASH_B)
put('m_foods', k_m*CASH_F/FOODS_REV*100); put('m_bev', k_m*CASH_B/BEV_REV*100)
assert abs((M['m_foods']*SH_F + M['m_bev']*(1-SH_F)) - M_BASE) < 1e-9
# chequeo pendiente desde KO: margen del DCF contra el FCF implícito del consenso (FCF de consenso 2026, sumándole de vuelta
# la cuota del TCJA y los intereses netos después de impuestos, y restando ventas de activo fijo como en F26)
put('m_cons_fcf', (FCF_C26 + TCJA26 + NETINT26*(1-t) - 2*0.071)/REV_C26*100)
put('m_vs_cons', M_BASE - M['m_cons_fcf'])

# ---------------- DCF (15%, o 7.5% si entra la suma de partes) ----------------
YEARS = [2027, 2028, 2029, 2030, 2031]
STUB = put('stub', 29.343/93.925)      # 4T (16 semanas) = 31% de las ventas de 2025: fracción de 2026 que queda al corte
PM_BASE = [2.0, 2.25, 2.5, 2.5, 2.5]   # mismo sendero de precio/mix que el Base de KO
SC = {
 'bear': dict(dw=+0.5, g=2.0, vf=[M['cf_8q']-1.5]*5, vb=[M['bev_8q']-1.5]*5, pm=[1.5, 1.75, 2.0, 2.0, 2.0], dm=[-1.0]*5),
 'base': dict(dw=0.0,  g=2.5, vf=[M['cf_8q']]*5,     vb=[M['bev_8q']]*5,     pm=PM_BASE,                 dm=[0.0]*5),
 'bull': dict(dw=-0.5, g=3.0, vf=[M['cf_8q']+1.0]*5, vb=[M['bev_8q']+1.0]*5, pm=[2.5, 2.75, 3.0, 3.0, 3.0],
              dm=[1/3*(1-t), 2/3*(1-t), 1-t, 1-t, 1-t]),   # +100 pb de margen operativo core en tres años (objetivo de la compañía)
}
def paths(sc, dvf=0.0, dvb=0.0):
    rf_, rb = REV0*SH_F, REV0*(1-SH_F); rows = []
    for i in range(5):
        gf = sc['vf'][i] + dvf + sc['pm'][i]; gb = sc['vb'][i] + dvb + sc['pm'][i]
        rf_ *= 1 + gf/100; rb *= 1 + gb/100
        mf = M['m_foods'] + sc['dm'][i]; mb = M['m_bev'] + sc['dm'][i]
        rev = rf_ + rb; fcf = rf_*mf/100 + rb*mb/100
        rows.append(dict(y=YEARS[i], gf=gf, gb=gb, rev_f=rf_, rev_b=rb, rev=rev, g=(rev/(rows[-1]['rev'] if rows else REV0)-1)*100,
                         m=fcf/rev*100, fcf=fcf, fcf_f=rf_*mf/100, fcf_b=rb*mb/100))
    return rows
def dcf(sc, w=None, g=None, dvf=0.0, dvb=0.0, m_shift=0.0, detail=False, nonop=None):
    w = (WACC + sc['dw']) if w is None else w
    g = sc['g'] if g is None else g
    rows = paths(sc, dvf, dvb)
    if m_shift:
        for r in rows:
            r['fcf'] += r['rev']*m_shift/100; r['m'] += m_shift
    stub = REV0*STUB*(M_BASE + m_shift)/100
    pv = stub*(1+w/100)**-(STUB/2)
    for i, r in enumerate(rows):
        r['pv'] = r['fcf']*(1+w/100)**-(STUB+i+0.5); pv += r['pv']
    tv = rows[-1]['fcf']*(1+g/100)/((w-g)/100)
    pv_tv = tv*(1+w/100)**-(STUB+5)
    ev = pv + pv_tv
    eq = ev - NETDEBT - NCI + (NONOP if nonop is None else nonop)
    ps = eq/SH_DIL*1000
    if detail: return dict(ev=ev, pv_fcf=pv, pv_tv=pv_tv, eq=eq, ps=ps, tv_share=pv_tv/ev*100, w=w, g=g, rows=rows, stub=stub)
    return ps
for k, sc in SC.items():
    r = dcf(sc, detail=True)
    for kk in ('ps', 'ev', 'tv_share', 'w', 'g', 'pv_fcf', 'pv_tv', 'eq'):
        M[f'dcf_{k}_{kk}' if kk != 'ps' else f'dcf_{k}'] = r[kk]
    M[f'dcf_{k}_cagr'] = ((r['rows'][-1]['rev']/REV0)**(1/5)-1)*100
    M[f'dcf_{k}_org27'] = r['rows'][0]['g']; M[f'dcf_{k}_org29'] = r['rows'][2]['g']
    M[f'dcf_{k}_vf'] = sc['vf'][0]; M[f'dcf_{k}_vb'] = sc['vb'][0]
    if k == 'base':
        M['dcf_base_rows'] = [{kk: x[kk] for kk in ('y', 'g', 'gf', 'gb', 'rev', 'rev_f', 'rev_b', 'm', 'fcf', 'fcf_f', 'fcf_b', 'pv')} for x in r['rows']]
        M['dcf_base_stub'] = r['stub']
DCF = M['dcf_base']
put('dcf_pw', 0.25*M['dcf_bear'] + 0.45*DCF + 0.30*M['dcf_bull'])
put('dcf_avg', (M['dcf_bear'] + DCF + M['dcf_bull'])/3)
put('dcf_gap', (DCF/PRICE-1)*100)
put('dcf_bear_gap', (M['dcf_bear']/PRICE-1)*100); put('dcf_bull_gap', (M['dcf_bull']/PRICE-1)*100)
put('dcf_base_ownbeta', dcf(SC['base'], w=WACC_OWN)); put('ownbeta_diff', M['dcf_base_ownbeta'] - DCF)
put('dcf_m_raw25', dcf(SC['base'], m_shift=M['m_raw25']-M_BASE))
put('dcf_m_f25', dcf(SC['base'], m_shift=M['f25_m']-M_BASE)); put('dcf_m_f26', dcf(SC['base'], m_shift=M['f26_m']-M_BASE))
put('dcf_m_cons', dcf(SC['base'], m_shift=M['m_cons_fcf']-M_BASE))
put('dcf_no_nonop', dcf(SC['base'], nonop=0.0)); put('dcf_celh_fv', dcf(SC['base'], nonop=M['celh_fv25'] + EQM))
put('sbc25', 0.288)
put('dcf_sbc', dcf(SC['base'], m_shift=-0.288/REV[2025]*100)); put('sbc_effect', M['dcf_sbc'] - DCF)
put('dcf_margin_target', dcf(dict(SC['base'], dm=SC['bull']['dm'])))
put('margin_target_effect', M['dcf_margin_target'] - DCF)
# Sensibilidad obligatoria: volumen de SNACKS −2 / 0 / +2 puntos (bebidas en el Base)
put('dcf_vol_m2', dcf(SC['base'], dvf=-2.0)); put('dcf_vol_p2', dcf(SC['base'], dvf=+2.0))
put('dcf_vol_zero', dcf(SC['base'], dvf=-M['cf_8q']))
put('dcf_vol_m2_pct', (M['dcf_vol_m2']/DCF-1)*100); put('dcf_vol_p2_pct', (M['dcf_vol_p2']/DCF-1)*100)
put('vol_m2', M['cf_8q']-2); put('vol_p2', M['cf_8q']+2)
put('dcf_bvol_m2', dcf(SC['base'], dvb=-2.0)); put('dcf_bvol_p2', dcf(SC['base'], dvb=+2.0))
put('dcf_allvol_m2', dcf(SC['base'], dvf=-2.0, dvb=-2.0)); put('dcf_allvol_p2', dcf(SC['base'], dvf=2.0, dvb=2.0))
# Grilla WACC x g
WG = [WACC-1, WACC-0.5, WACC, WACC+0.5, WACC+1]; GG = [1.5, 2.0, 2.5, 3.0, 3.5]
M['grid_w'] = WG; M['grid_g'] = GG
M['grid'] = [[dcf(SC['base'], w=w, g=g) for g in GG] for w in WG]
assert abs(M['grid'][2][2] - DCF) < 1e-9
put('grid_up', (M['grid'][1][2]/DCF-1)*100); put('grid_dn', (M['grid'][3][2]/DCF-1)*100)
def solve(f, lo, hi, target, inc=True):
    for _ in range(200):
        mid = (lo+hi)/2
        if (f(mid) < target) == inc: lo = mid
        else: hi = mid
    return (lo+hi)/2
put('impl_wacc', solve(lambda w: dcf(SC['base'], w=w), 4.0, 12.0, PRICE, inc=False))
put('impl_g', solve(lambda g: dcf(SC['base'], g=g), -3.0, WACC-0.2, PRICE, inc=True))
put('impl_dvf', solve(lambda d: dcf(SC['base'], dvf=d), -15.0, 30.0, PRICE, inc=True))
put('impl_vf', M['cf_8q'] + M['impl_dvf'])
put('impl_m', M_BASE + solve(lambda d: dcf(SC['base'], m_shift=d), -10, 30, PRICE, inc=True))
put('wacc_minus_impl', WACC - M['impl_wacc'])

# GLP-1: arrastre sobre el volumen (supuestos declarados en la Sección 10). Morgan Stanley: −3% de consumo de gaseosas,
# panificados y snacks salados hacia 2035 (9 años); exposición = PFNA completo + la mitad de PBNA (supuesto: gaseosas con azúcar
# y bebidas deportivas; PepsiCo no publica la mezcla). Rango de exposición: solo PFNA a PFNA + todo PBNA.
GLP1_MS = put('glp1_ms', 3.0); put('glp1_hh', 11.0)
put('glp1_exp_lo', M['pfna_share']); put('glp1_exp_hi', M['pfna_share'] + M['pbna_share'])
put('glp1_exp', M['pfna_share'] + 0.5*M['pbna_share'])
put('glp1_drag_f', GLP1_MS/9*M['pfna_share']/M['foods_share'])               # puntos de volumen de snacks por año
put('glp1_drag_b', GLP1_MS/9*0.5*M['pbna_share']/M['bev_share'])            # puntos de volumen de bebidas por año
put('dcf_glp1', dcf(SC['base'], dvf=-M['glp1_drag_f'], dvb=-M['glp1_drag_b']))
put('glp1_effect', M['dcf_glp1'] - DCF)

# ---------------- Pares: precios al corte, consenso y múltiplos ----------------
# P/E sobre EPS de los próximos 12 meses; EV/EBITDA (últimos 12 meses, con arrendamientos) de stockanalysis (2-oct-2026),
# llevado al cierre del 1-oct por la variación de la capitalización; EV/(EBITDA − capex) con los mismos datos.
PEERS = {
 'KO':   dict(name='Coca-Cola', grp='bebidas', fy='dic', org='+6% (2T26)', vol=5.0, vol_t='+5% (cajas)'),
 'KDP':  dict(name='Keurig Dr Pepper', grp='bebidas', fy='dic', org='+7.3% sin JDE Peet\'s (2T26)', vol=3.1, vol_t='+3.1% (volumen/mezcla)'),
 'MNST': dict(name='Monster Beverage', grp='bebidas', fy='dic', org='+17.9% a moneda constante (2T26)', vol=None, vol_t='n. c.'),
 'MDLZ': dict(name='Mondelez', grp='snacks', fy='dic', org='+2.2% (2T26)', vol=0.7, vol_t='+0.7% (volumen/mezcla)'),
 'PG':   dict(name='Procter & Gamble', grp='staples', fy='jun', org='0% (4T FY26)', vol=0.0, vol_t='0%'),
 'CL':   dict(name='Colgate-Palmolive', grp='staples', fy='dic', org='+2.4% (2T26)', vol=0.9, vol_t='+0.9%'),
 'PM':   dict(name='Philip Morris International', grp='staples', fy='dic', org='+7.6% (2T26)', vol=2.5, vol_t='+2.5% (envíos)'),
}
REF = {  # pares puros para la suma de partes que no están en el grupo de comparables
 'HSY':  dict(name='Hershey', grp='snacks', fy='dic', org='+3.6% (2T26)', vol=-8.0, vol_t='−8% (precio +12)'),
 'GIS':  dict(name='General Mills', grp='alimentos', fy='may', org='0% (1T FY27)', vol=-4.0, vol_t='−4%'),
}
def fill(k, p):
    (e1, e2, e3, _), _n = nq(k)
    p['px'] = yh_close(k); p['e1'], p['e2'], p['e3'] = e1, e2, e3
    if p['fy'] == 'dic': p['ntm'] = 0.25*e1 + 0.75*e2
    elif p['fy'] == 'jun': p['ntm'] = 0.75*e1 + 0.25*e2      # PG: FY jun-2027 y jun-2028
    else: p['ntm'] = 0.67*e1 + 0.33*e2                          # GIS: FY may-2027 y may-2028
    p['g2'] = ((e3/e1)**0.5-1)*100
    p['pe'] = p['px']/p['ntm']
    s = SA[k]; r = p['px']/yh_last(k)
    p['ev'] = s['ev']/1e9 + s['mcap']/1e9*(r-1)
    p['ebitda'] = s['ebitda']/1e9; p['capex'] = -s['capex']/1e9
    p['evx'] = p['ev']/p['ebitda']; p['evxc'] = p['ev']/(p['ebitda'] - p['capex'])
    p['capex_pct'] = p['capex']/(s['rev']/1e9)*100
    p['beta'] = s['beta']; p['dy'] = s['dy'] or 0.0; p['fcfy'] = s['fcfy']
for k, p in list(PEERS.items()) + list(REF.items()): fill(k, p)
M['peers'] = PEERS; M['ref'] = REF
pes = sorted(p['pe'] for p in PEERS.values())
PE_MED = put('peer_pe_med', st.median(pes)); put('peer_pe_mean', st.mean(pes))
put('peer_pe_min', pes[0]); put('peer_pe_max', pes[-1])
put('peer_pe_q1', st.quantiles(pes, n=4, method='inclusive')[0]); put('peer_pe_q3', st.quantiles(pes, n=4, method='inclusive')[2])
evs = sorted(p['evx'] for p in PEERS.values())
EV_MED = put('peer_ev_med', st.median(evs)); put('peer_ev_min', evs[0]); put('peer_ev_max', evs[-1])
put('peer_ev_q3', st.quantiles(evs, n=4, method='inclusive')[2])
put('peer_pe_min_name', min(PEERS.items(), key=lambda kp: kp[1]['pe'])[1]['name'])
put('peer_pe_max_name', max(PEERS.items(), key=lambda kp: kp[1]['pe'])[1]['name'])
put('peer_ev_min_name', min(PEERS.items(), key=lambda kp: kp[1]['evx'])[1]['name'])
put('peer_ev_max_name', max(PEERS.items(), key=lambda kp: kp[1]['evx'])[1]['name'])
# PepsiCo: EV/EBITDA propio (capitalización + deuda neta con arrendamientos + minoritarios − Celsius y participadas) / EBITDA core
PEP_EV = put('pep_ev', MKT_CAP + NETDEBT_L + NCI - NONOP)
put('pep_ev_ebitda', PEP_EV/EBITDA_TTM)
put('pep_evx_sa', SA['PEP']['evx'])
put('pep_pe_vs_med', (M['pe_ntm_now']/PE_MED-1)*100)
put('pep_capex_ttm', 4.415 - 1.507 + 1.266)
put('pep_evxc', PEP_EV/(EBITDA_TTM - M['pep_capex_ttm']))
def reg(xs, ys):
    mx = st.mean(xs); my = st.mean(ys)
    sxy = sum((x-mx)*(y-my) for x, y in zip(xs, ys)); sxx = sum((x-mx)**2 for x in xs); syy = sum((y-my)**2 for y in ys)
    b = sxy/sxx; return dict(slope=b, icpt=my-b*mx, r2=sxy**2/(sxx*syy), n=len(xs))
def reg_ex(items, key, ykey='pe'):
    mx = st.mean(p[key] for _, p in items)
    ext = max(items, key=lambda kp: abs(kp[1][key]-mx))
    rest = [kp for kp in items if kp[0] != ext[0]]
    r = reg([p[key] for _, p in rest], [p[ykey] for _, p in rest]); r['dropped'] = ext[1]['name']; return r
allp = list(PEERS.items())
M['reg_g'] = reg([p['g2'] for _, p in allp], [p['pe'] for _, p in allp]); M['reg_g_ex'] = reg_ex(allp, 'g2')
volp = [(k, p) for k, p in allp if p['vol'] is not None]
M['reg_v'] = reg([p['vol'] for _, p in volp], [p['pe'] for _, p in volp]); M['reg_v_ex'] = reg_ex(volp, 'vol')
M['reg_ev_g'] = reg([p['g2'] for _, p in allp], [p['evx'] for _, p in allp]); M['reg_ev_g_ex'] = reg_ex(allp, 'g2', 'evx')
R2_MIN = put('r2_min', 0.5)
def ok(a, b): return all(M[k]['r2'] >= R2_MIN and M[k]['slope'] > 0 for k in (a, b))
reg_ok = ok('reg_g', 'reg_g_ex') or ok('reg_v', 'reg_v_ex') or ok('reg_ev_g', 'reg_ev_g_ex')
M['reg_ok'] = reg_ok
put('reg_g_pep_pe', M['reg_g']['icpt'] + M['reg_g']['slope']*M['pep_g2'])
put('reg_g_ex_pep_pe', M['reg_g_ex']['icpt'] + M['reg_g_ex']['slope']*M['pep_g2'])
assert not reg_ok, 'si la regresión sostiene un ajuste, hay que reescribir el Método 2'
# Método elegido: mediana de los siete pares (sin ajuste), aplicada a EPS y EBITDA de PepsiCo. Ningún paso usa su precio.
COMP_PE = put('comp_pe', PE_MED*NTM)
def ev_to_ps(mult, ebitda=EBITDA_TTM): return (mult*ebitda - NETDEBT_L - NCI + NONOP)/SH_DIL*1000
COMP_EV = put('comp_ev', ev_to_ps(EV_MED))
COMP = put('comp', (COMP_PE + COMP_EV)/2)
put('comp_low', (M['peer_pe_min']*NTM + ev_to_ps(M['peer_ev_min']))/2)
put('comp_high', (M['peer_pe_max']*NTM + ev_to_ps(M['peer_ev_max']))/2)
put('comp_q1', (M['peer_pe_q1']*NTM + ev_to_ps(st.quantiles(evs, n=4, method='inclusive')[0]))/2)
put('comp_gap', (COMP/PRICE-1)*100)
put('comp_ev_pe_diff', COMP_PE - COMP_EV)
put('pe_needed', PRICE/NTM)
put('comp_reg_ex', (M['reg_g_ex_pep_pe']*NTM + COMP_EV)/2)
# sin Coca-Cola en el grupo (para la comparación PEP vs. KO: ¿cuánto pesa KO en la mediana?)
pes_noko = [p['pe'] for k, p in PEERS.items() if k != 'KO']; evs_noko = [p['evx'] for k, p in PEERS.items() if k != 'KO']
put('peer_pe_med_noko', st.median(pes_noko)); put('peer_ev_med_noko', st.median(evs_noko))
put('comp_noko', (st.median(pes_noko)*NTM + ev_to_ps(st.median(evs_noko)))/2)

# ---------------- Suma de partes: snacks y bebidas a múltiplos de pares puros ----------------
# Criterio declarado: EV/(EBITDA − capex) — corrige por intensidad de capital (sin eso, el múltiplo de un modelo de
# concentrado aplicado a un embotellador integrado infla el valor). Pares puros: snacks = Mondelez y Hershey (General Mills
# no aplica: cereales, yogur y mascotas); bebidas = Coca-Cola, Keurig Dr Pepper y Monster. Mediana de cada grupo.
SN = {'MDLZ': PEERS['MDLZ'], 'HSY': REF['HSY']}; BV = {'KO': PEERS['KO'], 'KDP': PEERS['KDP'], 'MNST': PEERS['MNST']}
SOTP_F_X = put('sotp_f_x', st.median(p['evxc'] for p in SN.values()))
SOTP_B_X = put('sotp_b_x', st.median(p['evxc'] for p in BV.values()))
put('sotp_b_x_kdp', BV['KDP']['evxc']); put('sotp_f_x_min', min(p['evxc'] for p in SN.values()))
put('sotp_b_x_min', min(p['evxc'] for p in BV.values()))
# EBITDA − capex de cada negocio: resultado core de los últimos 12 meses (segmentos) + D&A − capex (2025), corporativo por ventas
seg_ttm = {k: M['seg'][k]['op'] - SEG_1H[k][1][1] + SEG_1H[k][0][1] for k in SEG}
corp_ttm = TTM_COI - sum(seg_ttm.values())
put('corp_ttm', corp_ttm)
F_OP_TTM = sum(seg_ttm[k]*SEG[k][4] for k in SEG) + FS*corp_ttm
B_OP_TTM = sum(seg_ttm[k]*(1-SEG[k][4]) for k in SEG) + (1-FS)*corp_ttm
put('foods_op_ttm', F_OP_TTM); put('bev_op_ttm', B_OP_TTM)
F_EC = put('sotp_f_ec', F_OP_TTM + M['foods_da'] - M['foods_capex'])
B_EC = put('sotp_b_ec', B_OP_TTM + M['bev_da'] - M['bev_capex'])
SOTP_F_EV = put('sotp_f_ev', SOTP_F_X*F_EC); SOTP_B_EV = put('sotp_b_ev', M['sotp_b_x_kdp']*B_EC)
SOTP_EV = put('sotp_ev', SOTP_F_EV + SOTP_B_EV)
def sotp_ps(fx, bx): return ((fx*F_EC + bx*B_EC) - NETDEBT_L - NCI + NONOP)/SH_DIL*1000
SOTP_B_X_USED = put('sotp_b_x_used', M['sotp_b_x_kdp'])
SOTP = put('sotp', sotp_ps(SOTP_F_X, SOTP_B_X_USED))
put('sotp_med', sotp_ps(SOTP_F_X, SOTP_B_X))
put('sotp_eq', SOTP*SH_DIL/1000)
put('sotp_low', sotp_ps(M['sotp_f_x_min'], M['sotp_b_x_min']))
put('sotp_high', M['sotp_med'])   # techo: mediana de los tres pares de bebidas (Coca-Cola)
put('sotp_gap', (SOTP/PRICE-1)*100)
put('sotp_f_ps', SOTP_F_EV/SH_DIL*1000); put('sotp_b_ps', SOTP_B_EV/SH_DIL*1000)
put('sotp_f_pct', SOTP_F_EV/SOTP_EV*100)
put('sotp_implied_x', (SOTP_EV)/(F_EC+B_EC)); put('pep_mkt_x', PEP_EV/(F_EC+B_EC))
put('sotp_disc', (1 - M['pep_mkt_x']/M['sotp_implied_x'])*100)
# con EV/EBITDA simple (sin corregir por capex), solo como referencia de por qué no se usa
put('sotp_evx_plain', ((st.median([SN['MDLZ']['evx'], SN['HSY']['evx']])*(F_OP_TTM+M['foods_da']) +
                        st.median(p['evx'] for p in BV.values())*(B_OP_TTM+M['bev_da'])) - NETDEBT_L - NCI + NONOP)/SH_DIL*1000)
INTR = put('intr', (DCF + SOTP)/2)     # 15% intrínseco repartido 7.5 / 7.5

# ---------------- Reversión (35%) ----------------
d = json.load(open('yh/PEP.mo.json'))['chart']['result'][0]
closes = {}
for ts, c in zip(d['timestamp'], d['indicators']['quote'][0]['close']):
    dt = datetime.datetime.fromtimestamp(ts, datetime.UTC)
    if c: closes[(dt.year, dt.month)] = c
seq = [(y, q) for y in range(2016, 2029) for q in range(4)]
win = []
for i, (y, q) in enumerate(seq):
    ym = (y, 3*(q+1))
    if ym < (2016, 3) or ym > (2026, 9): continue
    nx = seq[i+1:i+5]
    ntm = sum(EPS[a][b] for a, b in nx)
    covid = (2020, 1) in nx   # el EPS de los 12 meses siguientes incluye el 2T 2020 (pandemia)
    win.append(dict(date=f'{ym[0]}-{ym[1]:02d}', y=ym[0], price=closes[ym], ntm=ntm, pe=closes[ym]/ntm, excl=ym[0] in EXCL, covid=covid))
M['rev_window'] = win
clean = [w for w in win if not w['excl'] and not w['covid']]
nocovid = [w for w in win if not w['covid']]
put('rev_n', len(clean)); put('rev_n_all', len(win)); put('rev_n_excl', len(win)-len(clean))
put('rev_n_covid', sum(1 for w in win if w['covid'])); put('rev_n_nocovid', len(nocovid))
put('rev_pe_covid_avg', st.mean(w['pe'] for w in win if w['covid']))
put('rev_pe_avg_withcovid', st.mean(w['pe'] for w in win if not w['excl']))
PE_CLEAN = put('rev_pe_avg', st.mean(w['pe'] for w in clean))
PE_ALL = put('rev_pe_avg_all', st.mean(w['pe'] for w in nocovid))
put('rev_pe_avg_raw', st.mean(w['pe'] for w in win))
put('rev_pe_min', min(w['pe'] for w in clean)); put('rev_pe_max', max(w['pe'] for w in clean))
put('rev_pe_last', win[-1]['pe'])
clean_ko = [w for w in win if w['y'] not in EXCL_KO and not w['covid']]
put('rev_pe_avg_korule', st.mean(w['pe'] for w in clean_ko)); put('rev_n_korule', len(clean_ko))
M['rev_by_year'] = {}
for y in range(2016, 2027):
    ws = [w for w in win if w['y'] == y]
    M['rev_by_year'][str(y)] = dict(avg=st.mean(w['pe'] for w in ws), lo=min(w['pe'] for w in ws), hi=max(w['pe'] for w in ws), excl=y in EXCL, n=len(ws))
    wc = [w for w in ws if not w['covid']]
    M['rev_by_year'][str(y)]['avg_nc'] = st.mean(w['pe'] for w in wc) if wc else None
# Regla de cambio de escalón (skill, bloque de retail; aplicada a la baja de forma simétrica, declarada): el régimen nuevo se
# reconoce solo si todos los cierres desde un punto quedan debajo del MÍNIMO de los cinco años previos (20 cierres) durante
# al menos ocho trimestres. Si se cumple, la Lectura 1 usa los cierres del régimen nuevo (con las mismas exclusiones).
STEP_N = put('step_n_min', 8)
step_i = None
for i in range(20, len(win)):
    floor = min(w['pe'] for w in win[i-20:i])
    if all(w['pe'] < floor for w in win[i:]) and len(win) - i >= STEP_N:
        step_i = i; break
M['step_ok'] = step_i is not None
assert M['step_ok'], 'el texto asume que la regla de cambio de escalón se cumple'
put('step_start', win[step_i]['date']); put('step_floor', min(w['pe'] for w in win[step_i-20:step_i]))
put('step_n', len(win) - step_i)
step_w = [w for w in win[step_i:] if not w['excl'] and not w['covid']]
put('step_n_clean', len(step_w))
PE_STEP = put('rev_pe_step', st.mean(w['pe'] for w in step_w))
put('rev_pe_step_all', st.mean(w['pe'] for w in win[step_i:]))
put('rev1_step_all', M['rev_pe_step_all']*NTM)
put('rev1_10y', PE_CLEAN*NTM)
R1 = put('rev1', PE_STEP*NTM)
put('rev1_all', PE_ALL*NTM); put('rev1_korule', M['rev_pe_avg_korule']*NTM)
put('rev_excl_effect', M['rev1_10y'] - M['rev1_all'])
put('rev1_withcovid', M['rev_pe_avg_withcovid']*NTM); put('covid_effect', M['rev1_withcovid'] - M['rev1_10y'])
REL = put('rel_avg', PE_ALL/SPX_PE10)
REL_NOW = put('rel_now', M['pe_ntm_now']/SPX_PE)
R2 = put('rev2', REL*SPX_PE*NTM)
put('rel_pe', REL*SPX_PE)
put('spx_vs_avg', (SPX_PE/SPX_PE10-1)*100); put('pep_vs_avg', (M['pe_ntm_now']/PE_ALL-1)*100)
put('pep_vs_avg_abs', -M['pep_vs_avg'])
put('pep_vs_clean', (M['pe_ntm_now']/PE_CLEAN-1)*100); put('pep_vs_step', (M['pe_ntm_now']/PE_STEP-1)*100)
REVV = put('rev', (R1 + R2)/2)
put('rev_low', min(w['pe'] for w in step_w)*NTM); put('rev_high', M['rev_pe_max']*NTM)
put('rev_10y', (M['rev1_10y'] + R2)/2)
put('rev_gap', (REVV/PRICE-1)*100)
put('rel_min', min(w['pe'] for w in nocovid)/SPX_PE10); put('rel_max', max(w['pe'] for w in nocovid)/SPX_PE10)
assert M['rel_now'] < M['rel_min'], 'el texto dice que el relativo actual está debajo del rango'
put('rev2_withcovid', M['rev_pe_avg_raw']/SPX_PE10*SPX_PE*NTM)
put('rel_now_vs_avg', (REL_NOW/REL-1)*100)
# P/E del último cierre de junio-2026 en la serie y de PEP al corte
put('pe_jun26', win[-1]['pe'])

# ---------------- Consenso (25%) ----------------
CONS = put('cons', 151.09); put('cons_med', 152.0); put('cons_low', 124.0); put('cons_high', 180.0); put('cons_n', 24)
put('cons_sb', 4); put('cons_b', 3); put('cons_h', 16); put('cons_s', 0); put('cons_ss', 1)
put('cons_gap', (CONS/PRICE-1)*100)
put('cons_buy', M['cons_sb'] + M['cons_b'])
put('jpm_tp', 138.0); put('jpm_tp_old', 170.0)

# ---------------- Blend ----------------
W = {'dcf': 0.075, 'sotp': 0.075, 'comp': 0.25, 'rev': 0.35, 'cons': 0.25}
V = {'dcf': DCF, 'sotp': SOTP, 'comp': COMP, 'rev': REVV, 'cons': CONS}
BLEND = put('blend', sum(W[k]*V[k] for k in W))
put('blend_gap', (BLEND/PRICE-1)*100)
for k in W: put(f'contrib_{k}', W[k]*V[k])
put('contrib_intr', W['dcf']*DCF + W['sotp']*SOTP)
IND = ('dcf', 'sotp', 'comp'); ANC = ('rev', 'cons')
put('indep', sum(W[k]*V[k] for k in IND)/sum(W[k] for k in IND))
put('anch', sum(W[k]*V[k] for k in ANC)/sum(W[k] for k in ANC))
put('indep_gap', (M['indep']/PRICE-1)*100); put('anch_gap', (M['anch']/PRICE-1)*100)
for k in V: put(f'{k}_gap_', (V[k]/PRICE-1)*100)
def blend_with(w=None, **kw):
    v = dict(V); v.update(kw); w = w or W; return sum(w[k]*v[k] for k in w)
put('blend_no_sotp', blend_with(w={'dcf': 0.15, 'comp': 0.25, 'rev': 0.35, 'cons': 0.25}))
put('blend_rev_10y', blend_with(rev=M['rev_10y']))
put('blend_rev_all', blend_with(rev=(M['rev1_all']+R2)/2))
put('blend_step_all', blend_with(rev=(M['rev1_step_all']+R2)/2))
put('blend_korule', blend_with(rev=(M['rev1_korule']+R2)/2))
put('blend_withcovid', blend_with(rev=(M['rev1_withcovid'] + M['rev2_withcovid'])/2))
put('blend_ownbeta', blend_with(dcf=M['dcf_base_ownbeta']))
put('blend_vs_cons', (BLEND/CONS-1)*100)
put('blend_indep_only', M['indep'])
# sin reversión (los otros tres métodos reponderados) — la lectura que más depende de que el volumen se recupere
put('blend_no_rev', sum(W[k]*V[k] for k in W if k != 'rev')/(1-W['rev']))
put('blend_glp1', blend_with(dcf=M['dcf_glp1']))

# ---------------- Comparación PepsiCo vs. Coca-Cola bajo la misma vara ----------------
# Los números de KO salen de modelos/ko/model.json. Lo único que se actualiza es lo que depende del precio: el cierre de KO
# al 1-oct-2026 (Yahoo, misma fecha de corte que PEP); el blend y los fair values de KO quedan como se publicaron.
K = json.load(open('../ko/model.json'))
KPX = put('ko_px', yh_close('KO'))
put('ko_px_model', K['price'])
KMC = put('ko_mkt_cap', KPX*K['sh_out']/1000)
C = {}
def both(key, pep, ko): C[key] = dict(pep=pep, ko=ko)
both('pe', M['pe_ntm_now'], KPX/K['eps_ntm'])
both('g2', M['pep_g2'], K['ko_g2'])
both('org8', M['org_8q'], K['org_8q'])
both('vol8', M['vol_8q'], K['conc_8q'])                  # volumen con efecto en ventas: volumen orgánico (PEP) / concentrado (KO)
both('price8', M['price_8q'], K['pm_8q'])
both('cons_vol8', M['bev_8q'], K['ucv_8q'])              # volumen del consumidor en bebidas: cajas del sistema
ko_org = K['org']
KQ = NQS
both('org4', M['org_4q'], st.mean(ko_org[q]['org'] for q in KQ[-4:]))
both('price4', M['price_4q'], st.mean(ko_org[q]['pm'] for q in KQ[-4:]))
both('vol4', M['vol_4q'], st.mean(ko_org[q]['conc'] for q in KQ[-4:]))
both('gm', M['comp_gm']['2025'], K['comp_gm']['2025'])
both('gm_1h', M['comp_gm']['1S26'], K['comp_gm']['1S26'])
both('om', M['comp_om']['2025'], K['comp_om']['2025'])
both('om_ttm', M['ttm_om'], K['ttm_coi']/K['ttm_rev']*100)
both('conv', M['conv25'], K['conv25'])                   # OCF ajustado por pagos extraordinarios − capex, / utilidad core
both('capex_pct', M['capex_pct25'], K['capex_pct25'])
both('da_pct', DA25/REV[2025]*100, K['ttm_da']/K['ttm_rev']*100)
# ROIC sobre capital operativo (misma fórmula): resultado core de los últimos 12 meses x (1 − tasa core) /
# (patrimonio + minoritarios + deuda − caja − participaciones por el método de participación). Excluye participadas de ambos lados.
PEP_IC = put('pep_ic', BS['jun']['eq']/1000 + NCI + DEBT - CASH - EQM)
KO_IC = put('ko_ic', K['equity_ko'] + K['nci'] + K['debt'] - K['cash'] - K['bs']['jul']['eqm']/1000)
both('roic', TTM_COI*(1-t)/PEP_IC*100, K['ttm_coi']*(1-K['tax']/100)/KO_IC*100)
both('nd_ebitda', M['nd_ebitda'], K['nd_ebitda']); both('nd_ebitda_l', M['nd_ebitda_l'], K['nd_ebitda_l'])
both('div_yield', M['div_yield'], K['div_annual']/KPX*100)
both('payout_eps', M['payout_eps'], K['payout_eps'])
both('payout_fcf', M['payout_fcf'], K['payout_fcf'])     # dividendos guiados / FCF guiado de cada compañía
both('streak', 54, K['div_streak'])
# múltiplos forward con la misma fuente para las dos: resultado operativo y FCF de consenso 2026 (S&P Global)
KO_OI_C26, KO_FCF_C26 = put('ko_oi_c26', 16.12), put('ko_fcf_c26', 12.12)
KO_EV = put('ko_ev', KMC + K['net_debt_l'] + K['nci'] - K['nonop'])     # mismo ajuste que en el modelo de KO (participaciones y CCBA)
both('ev_ebitda', PEP_EV/EBITDA_TTM, KO_EV/K['ebitda_ttm'])
both('ev_ebitda_f', PEP_EV/(OI_C26 + TTM_DA), KO_EV/(KO_OI_C26 + K['ttm_da']))
both('fcf_yield', M['fcf_yield'], KO_FCF_C26/KMC*100)
both('p_fcf', MKT_CAP/FCF_C26, KMC/KO_FCF_C26)
both('rel_now', M['rel_now'], (KPX/K['eps_ntm'])/SPX_PE)
both('rel_avg', M['rel_avg'], K['rel_avg'])
both('rel_vs_avg', (M['rel_now']/M['rel_avg']-1)*100, ((KPX/K['eps_ntm'])/SPX_PE/K['rel_avg']-1)*100)
both('intl', M['intl_rev_pct'], K['intl_rev_pct'])
both('glp1_exp', M['glp1_exp'], K['na_rev_pct']*K['sugar_ssd_pct']/100)
both('glp1_drag', (M['glp1_drag_f']*SH_F + M['glp1_drag_b']*(1-SH_F)), K['glp1_drag_pa'])
both('beta', BETA_PEP, K['beta_ko'])
both('wacc', WACC, K['wacc'])
both('dcf', DCF, K['dcf_base']); both('comp', COMP, K['comp']); both('rev', REVV, K['rev']); both('cons', CONS, K['cons'])
both('blend', BLEND, K['blend']); both('indep', M['indep'], K['indep']); both('anch', M['anch'], K['anch'])
both('px', PRICE, KPX)
both('blend_gap', (BLEND/PRICE-1)*100, (K['blend']/KPX-1)*100)
both('indep_gap', (M['indep']/PRICE-1)*100, (K['indep']/KPX-1)*100)
both('anch_gap', (M['anch']/PRICE-1)*100, (K['anch']/KPX-1)*100)
both('m_fcf', M_BASE, K['m_base'])                                     # margen de FCF sin apalancar del DCF
both('m_cons', M['m_cons_fcf'], (KO_FCF_C26 + K['netint26']*(1-K['tax']/100) - K['eqdiv25'])/K['rev_c26']*100)
both('tv_share', M['dcf_base_tv_share'], K['dcf_base_tv_share'])
M['cmp'] = C
put('ko_ret_ytd', (KPX/K['px_dec25']-1)*100); put('pep_ret_ytd', (PRICE/closes[(2025, 12)]-1)*100)
put('ko_blend_gap_model', K['blend_gap'])
# ¿Qué parte de la brecha de P/E explica el modelo de negocio? (1) conversión de caja: P/E x conversión = P/FCF-utilidad;
# llevar el P/E de PEP a la conversión de KO. (2) crecimiento: P/E que la regresión de los pares asigna a cada crecimiento.
GAP_PE = put('gap_pe', C['pe']['ko'] - C['pe']['pep'])
PE_PEP_CONV = put('pe_pep_conv', C['pe']['pep']*C['conv']['ko']/C['conv']['pep'])   # P/E que PEP "merecería" con la conversión de KO, a igual P/FCF
put('gap_conv', PE_PEP_CONV - C['pe']['pep'])
put('gap_conv_pct', M['gap_conv']/GAP_PE*100)
G_KO_PE = put('reg_g_ko_pe', M['reg_g']['icpt'] + M['reg_g']['slope']*K['ko_g2'])
put('gap_growth', M['reg_g_ko_pe'] - M['reg_g_pep_pe'])
put('gap_growth_pct', M['gap_growth']/GAP_PE*100)
put('gap_rest', GAP_PE - M['gap_conv'] - M['gap_growth']); put('gap_rest_pct', M['gap_rest']/GAP_PE*100)
put('pfcf_gap', (C['p_fcf']['ko']/C['p_fcf']['pep']-1)*100)
put('evxc_gap', (PEERS['KO']['evxc']/M['pep_evxc']-1)*100)

# ---------------- Series para gráficos y derivados de texto ----------------
M['js_pe_labels'] = json.dumps([(w['date'][:4] if w['date'][5:] == '03' else '') for w in win])
M['js_pe_vals'] = json.dumps([round(w['pe'], 2) for w in win])
M['js_pe_avg'] = json.dumps([round(PE_CLEAN, 2)]*len(win)); M['js_pe_step'] = json.dumps([None]*step_i + [round(PE_STEP, 2)]*(len(win)-step_i))
M['js_q'] = json.dumps([q[:2] + ' ' + q[2:] for q in Q])
M['js_q8'] = json.dumps([q[:2] + ' ' + q[2:] for q in NQS])
for key in ('vol', 'price', 'org', 'cf', 'bev'):
    M[f'js_{key}'] = json.dumps([M['org'][q][key] for q in Q])
    M[f'js8_{key}'] = json.dumps([M['org'][q][key] for q in NQS])
for key in ('pfna_vol', 'pfna_price', 'pfna_org', 'pbna_vol', 'pbna_price', 'pbna_org'):
    M[f'js_{key}'] = json.dumps([round(M['na'][q][key], 1) for q in NQS])
M['js8_ko_conc'] = json.dumps([ko_org[q]['conc'] for q in NQS]); M['js8_ko_pm'] = json.dumps([ko_org[q]['pm'] for q in NQS])
M['js8_ko_org'] = json.dumps([ko_org[q]['org'] for q in NQS]); M['js8_ko_ucv'] = json.dumps([ko_org[q]['ucv'] for q in NQS])
M['js_ann_y'] = json.dumps([str(y) for y in ANN]); M['js_ann_org'] = json.dumps([v[0] for v in ANN.values()])
M['js_ann_cf'] = json.dumps([v[1] for v in ANN.values()]); M['js_ann_bev'] = json.dumps([v[2] for v in ANN.values()])
put('px_dec25', closes[(2025, 12)]); put('ret_ytd', (PRICE/closes[(2025, 12)]-1)*100)
put('ret_from_hi', (PRICE/M['px_feb_hi']-1)*100); put('ret_from_hi_abs', -M['ret_from_hi'])
put('hi52', max(c for (y, m), c in closes.items() if (2025, 10) <= (y, m) <= (2026, 9)))
put('lo52', min(c for (y, m), c in closes.items() if (2025, 10) <= (y, m) <= (2026, 9)))
put('dcf_base_rev27', M['dcf_base_rows'][0]['rev']); put('dcf_base_rev31', M['dcf_base_rows'][-1]['rev'])
put('dcf_base_fcf27', M['dcf_base_rows'][0]['fcf'])
put('netdebt_ps', NETDEBT/SH_DIL*1000); put('nci_ps', NCI/SH_DIL*1000); put('netdebt_l_ps', NETDEBT_L/SH_DIL*1000)
put('ev_ps', M['dcf_base_ev']/SH_DIL*1000)
put('sotp_ev_ps', SOTP_EV/SH_DIL*1000)
put('ke_minus_floor', KE - KE_FLOOR)
put('div_minus_rf', M['div_yield'] - RF); put('fcf_minus_rf', M['fcf_yield'] - RF)
put('rf_minus_fcf', RF - M['fcf_yield'])
put('da_ebitda', TTM_DA/EBITDA_TTM*100)
put('inst_pct', 80.16); put('insider_pct', 0.12); put('short_pct', 1.90)
put('elliott_stake', 4.0); put('elliott_pct', 2.0); put('elliott_upside', 50.0)
put('ttm_rev_g', (TTM_REV/(REV[2025])-1)*100)
put('celh_ytd', (CELH_PX/[r for r in yh_rows('CELH') if r[0] <= '2025-12-31'][-1][1]-1)*100)
put('celh_dec25', [r for r in yh_rows('CELH') if r[0] <= '2025-12-31'][-1][1])
put('pe_hist_lo', min(w['pe'] for w in win))

# valores absolutos para la prosa (evitan dobles negativos)
put('grid_dn_abs', -M['grid_dn']); put('glp1_effect_abs', -M['glp1_effect']); put('sbc_effect_abs', -M['sbc_effect'])
put('ret_ytd_abs', -M['ret_ytd']); put('dcf_gap_abs', abs(M['dcf_gap']))
put('cf_8q_abs', abs(M['cf_8q'])); put('pbna_vol_8q_abs', abs(M['pbna_vol_8q'])); put('pfna_vol_8q_abs', abs(M['pfna_vol_8q']))
put('vol_8q_abs', abs(M['vol_8q'])); put('pfna_price_8q_abs', abs(M['pfna_price_8q']))
put('dcf_vol_m2_pct_abs', -M['dcf_vol_m2_pct'])

E99 = 99.0*SH_OUT/1000; WD99 = DEBT/(DEBT+E99)*100
put('dcf_at99', dcf(SC['base'], w=(1-WD99/100)*KE + WD99/100*KD))

# ---------------- Tokens adicionales del texto (con chequeos de que el texto describe bien los números) ----------------
for k in M['seg']: M['seg'][k]['capex_pct'] = M['seg'][k]['capex']/M['seg'][k]['rev']*100
put('om_gaap25', 11.498/REV[2025]*100); put('om_gaap24', 12.887/REV[2024]*100)
put('debt_dec24', 7082 + 37224); put('debt_dec25', 6861 + 42321)
put('pep_pe_vs_med_abs', -M['pep_pe_vs_med'])
put('gap_just_pct', M['gap_conv_pct'] + M['gap_growth_pct'])
put('ko_dcf_gap_abs', -(K['dcf_base']/KPX-1)*100)
assert M['fcf_yield'] > RF and M['div_yield'] < RF, 'el texto describe FCF yield > Treasury > dividendo'
put('rf_minus_div', RF - M['div_yield'])
put('stub_pct', STUB*100)
assert M['m_vs_cons'] < 0; put('m_vs_cons_abs', -M['m_vs_cons'])
assert M['margin_target_effect'] > 0
assert M['impl_wacc'] > WACC; put('impl_wacc_diff', M['impl_wacc'] - WACC)
put('bull_dm', 1 - t)
put('sotp_ec_tot', F_EC + B_EC)
put('netdebt_l_nci', NETDEBT_L + NCI); put('netdebt_l_nci_ps', (NETDEBT_L + NCI)/SH_DIL*1000)
put('peer_ev_q1', st.quantiles(evs, n=4, method='inclusive')[0])
put('comp_reg_pe', M['reg_g_pep_pe']*NTM)
MESES = ['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre']
put('step_start_txt', f"{MESES[int(M['step_start'][5:])-1]} de {M['step_start'][:4]}")
put('rel_now_vs_avg_abs', -M['rel_now_vs_avg'])
put('w53_4t23', M['org']['4T23']['ad'] + M['org']['4T23']['w53'])
assert M['gap_just_pct'] < 50, 'el título de la Sección 09 dice "menos de la mitad"'
assert M['rev_pe_min'] == min(w['pe'] for w in win), 'el texto dice que septiembre-2026 es el P/E más bajo de la década'
assert M['pep_ev_ebitda'] < min(p['evx'] for p in PEERS.values()), 'el texto dice que PEP tiene el EV/EBITDA más bajo del grupo'
assert sorted(p['pe'] for p in PEERS.values())[0] < M['pe_ntm_now'] < sorted(p['pe'] for p in PEERS.values())[1], 'solo KDP más barata'
assert M['pep_g2'] < min(p['g2'] for p in PEERS.values()), 'PEP es la que menos crece'
assert all(M[k] > PRICE for k in ('blend_no_sotp', 'blend_rev_10y', 'blend_no_rev')), 'el texto dice que todas las variantes quedan sobre el precio'

put('ko_blend_gap_abs', -C['blend_gap']['ko']); assert C['blend_gap']['ko'] < 0
put('eps_g25', (EPS25/EPS24-1)*100)
put('vote_laguarta', 947731772/(947731772+49828733)*100); put('vote_pohlad', 914405632/(914405632+86817565)*100)
put('om25_cf', M['comp_om']['2025'] - (M['am_pct']['2024'] - M['am_pct']['2025']))

M['shock_ps'] = {str(y): v for y, v in SHOCK.items()}; put('shock_2022_brands', 0.69+0.78)
assert M['impl_vf'] < 0; put('impl_vf_abs', -M['impl_vf'])

assert M['pbna_vol_neg_q'] == 8, 'el texto dice que PBNA perdió volumen en los ocho trimestres'
SPARK = [closes[(2026, m)] for m in range(4, 10)] + [PRICE]   # cierres mensuales abr-sep 2026 + cierre de corte
M['spark'] = [round(x, 2) for x in SPARK]

json.dump(M, open('model.json', 'w'), indent=1, default=float)
if __name__ == '__main__':
    for k, v in M.items():
        if isinstance(v, (int, float)) and not isinstance(v, bool): print(f'{k:24s} {v:,.4f}')
    print('peers:'); [print(' ', k, round(p['pe'], 2), round(p['g2'], 1), p['vol'], round(p['evx'], 2), round(p['evxc'], 2)) for k, p in list(PEERS.items()) + list(REF.items())]
    for k in ('reg_g', 'reg_g_ex', 'reg_v', 'reg_v_ex', 'reg_ev_g', 'reg_ev_g_ex'): print(k, {a: (round(b, 3) if isinstance(b, float) else b) for a, b in M[k].items()})
    for w in win: print(w['date'], round(w['price'], 2), round(w['ntm'], 3), round(w['pe'], 2), w['excl'], w['covid'])
    for k, v in C.items(): print(f'cmp {k:12s} PEP {v["pep"]:8.2f}  KO {v["ko"]:8.2f}')
    print(M['dcf_base_rows'])
