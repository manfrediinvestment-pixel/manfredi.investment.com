# Modelo de valuación UNH (UnitedHealth Group) — todos los números derivados del informe salen de acá.
# Marco: informe-salud, Módulo C (managed care) + regla de conglomerados (SOTP UnitedHealthcare + Optum).
# Fuentes: 10-K 2025, 10-Q 1T/2T 2026, comunicados 8-K ítem 2.02 (2016-2026), proxy 2026, Yahoo, Nasdaq/Zacks,
# stockanalysis (S&P Global). Fecha de corte de precios: cierre 28-sep-2026.
import json, datetime, statistics as st

M = {}
def put(k, v): M[k] = v; return v

# ---------------- Mercado (cierre 28-sep-2026) ----------------
PRICE = put('price', 377.83)
RF = put('rf', 5.24)                 # ^TNX cierre 28-sep-2026
ERP = put('erp', 5.0)
SH_DIL = put('sh_dil', 906.0)        # diluidas promedio 2T26 (millones)
SH_OUT = put('sh_out', 905.0)        # en circulación 30-jun-2026 (10-Q)
MKT_CAP = put('mkt_cap', PRICE*SH_OUT/1000)   # US$ miles de millones
put('hi52', 461.62); put('lo52', 255.97)

# ---------------- Consenso de EPS (Nasdaq / Zacks, 29-sep-2026) ----------------
C26, C27, C28 = put('c26', 19.85), put('c27', 22.54), put('c28', 26.35)
put('c26_n', 12); put('c27_n', 14); put('c28_n', 7)
put('c26_sa', 19.87)                 # stockanalysis (S&P Global), 25 analistas, 15-sep-2026 (referencia)
GUIDE_LO, GUIDE_HI = put('guide_lo', 19.50), put('guide_hi', 20.00)
GUIDE_MID = put('guide_mid', (GUIDE_LO+GUIDE_HI)/2)
# EPS de los próximos 12 meses (oct-2026 a sep-2027) con el consenso de los dos años, no con el P/E forward
NTM = put('eps_ntm', 0.25*C26 + 0.75*C27)
NTM1 = put('eps_ntm1', 0.25*C27 + 0.75*C28)   # oct-2027 a sep-2028
put('pe_ntm_now', PRICE/NTM)
put('eps_g27', (C27/C26-1)*100); put('eps_g28', (C28/C27-1)*100)

# ---------------- EPS ajustado trimestral (comunicados 8-K ítem 2.02) ----------------
EPS = {2016:[1.81,1.96,2.17,2.11], 2017:[2.37,2.46,2.66,2.59], 2018:[3.04,3.14,3.41,3.28],
       2019:[3.73,3.60,3.88,3.90], 2020:[3.72,7.12,3.51,2.52], 2021:[5.31,4.70,4.52,4.48],
       2022:[5.49,5.57,5.79,5.34], 2023:[6.26,6.14,6.56,6.16], 2024:[6.91,6.80,7.15,6.81],
       2025:[7.20,4.08,2.92,2.11], 2026:[7.23,6.38]}
FYEPS = {2016:8.05,2017:10.08,2018:12.88,2019:15.11,2020:16.88,2021:19.02,2022:22.19,2023:25.12,2024:27.66,2025:16.35}
for y,v in FYEPS.items():
    assert abs(sum(EPS[y])-v) < 0.06, (y, sum(EPS[y]), v)
# 2S26 con el consenso anual; 2027-2028 con la estacionalidad de 2024 (último año normal)
h2 = C26 - sum(EPS[2026]); s24 = [x/sum(EPS[2024]) for x in EPS[2024]]
EPS[2026] = EPS[2026] + [h2*s24[2]/(s24[2]+s24[3]), h2*s24[3]/(s24[2]+s24[3])]
EPS[2027] = [C27*s for s in s24]; EPS[2028] = [C28*s for s in s24]
M['eps_fy'] = {str(k): (sum(v) if k not in FYEPS else FYEPS[k]) for k,v in EPS.items()}

# ---------------- Historia de MCR (XBRL: costos médicos / primas) ----------------
MCR = {2010:80.61,2011:80.81,2012:80.44,2013:81.84,2014:81.21,2015:81.69,2016:81.21,2017:82.07,2018:81.65,
       2019:82.47,2020:79.11,2021:82.62,2022:81.99,2023:83.174,2024:85.549,2025:89.146}
MCR_ADJ25 = put('mcr_adj25', 88.9)   # 2025 ajustado (sin 20 pb de contratos a pérdida del cargo del 4T25)
MCR_G26 = put('mcr_g26', 88.1)       # guía 2026 (16-jul-2026), ±25 pb
M['mcr_hist'] = {str(k):v for k,v in MCR.items()}
# MLR de mitad de ciclo: promedio 2023-2026E (4 años, régimen de producto y regulatorio actual)
MID_WIN = [MCR[2023], MCR[2024], MCR_ADJ25, MCR_G26]
MLR_MID = put('mlr_mid', st.mean(MID_WIN))
put('mlr_1624', st.mean([MCR[y] for y in range(2016,2025) if y != 2020]))   # referencia, 8 años sin 2020
put('mlr_1022', st.mean([MCR[y] for y in range(2010,2023) if y != 2020]))
put('mlr_gap', MCR_G26 - MLR_MID)
# MCR trimestral contra el mismo trimestre del año anterior (comunicados)
MCRQ = {'1T23':82.2,'2T23':83.2,'3T23':82.3,'4T23':85.0,'1T24':84.3,'2T24':85.1,'3T24':85.2,'4T24':87.6,'1T25':84.8,'2T25':89.4,'3T25':89.9,'4T25':92.4,'1T26':83.9,'2T26':86.7}
M['mcrq'] = MCRQ
put('mcr_yoy_1t26', MCRQ['1T26']-MCRQ['1T25']); put('mcr_yoy_2t26', MCRQ['2T26']-MCRQ['2T25'])
DCP = {'4T23':47.9,'2T24':45.2,'4T24':47.0,'1T25':45.5,'2T25':44.5,'3T25':46.2,'4T25':44.1,'1T26':48.6,'2T26':47.0}
M['dcp'] = DCP
RESDEV = {'2022':None}
put('pyd_1h26', 1250); put('pyd_1h25', 320); put('pyd_fy25', 140); put('pyd_2q26', 860)

# ---------------- Consolidado ----------------
REV25, REV24 = 447567, 400278
REV_1H26, REV_1H25, REV_1H24 = 223753, 221191, 198651
OCF25, OCF24 = 19697, 24204
OCF_1H26, OCF_1H25, OCF_1H24 = 19964, 12644, 7890
OCF_G26 = put('ocf_g26', 24000)
REV_C26 = put('rev_c26', 447083)             # consenso de ingresos 2026 (S&P Global)
INT26, INT25 = 3700, 4002                     # intereses: guía 2026 (~3,700) y real 2025
TAX = put('tax', 18.5)                        # tasa efectiva guiada 2026
TTM_REV = put('ttm_rev', REV25 - REV_1H25 + REV_1H26)
TTM_OCF = put('ttm_ocf', OCF25 - OCF_1H25 + OCF_1H26)
put('ttm_ocf_m', TTM_OCF/TTM_REV*100)
put('ocf_8q_m', (OCF24-OCF_1H24+OCF25+OCF_1H26-OCF_1H25)/(REV24-REV_1H24+REV25+REV_1H26-REV_1H25)*100)
put('ocf_win_m', (OCF25+OCF_G26)/(REV25+REV_C26)*100)
put('ocf25_m', OCF25/REV25*100); put('ocf_g26_m', OCF_G26/REV_C26*100)
put('ocf_2h26_impl', OCF_G26-OCF_1H26)

# ---------------- Segmentos (10-K 2025, 10-Q 2T26, comunicado 16-jul-2026) ----------------
# Base 2026E: ingresos = 2 x 1S26 (Optum Health: 4 x 2T26 por la caída de pacientes); resultado = guía ajustada.
SEG = {
 'uhc':     dict(name='UnitedHealthcare', rev26=172282*2/1000, oe26=12000/1000, rev25=344.903, oe25=9.425, da=883/344903, capex=816/344903),
 'health':  dict(name='Optum Health',    rev26=23472*4/1000,  oe26=2215/1000,  rev25=101.957, oe25=1.449, da=1211/101957, capex=1237/101957),
 'insight': dict(name='Optum Insight',   rev26=10527*2/1000,  oe26=4750/1000,  rev25=19.417,  oe25=4.564, da=1422/19417, capex=1170/19417),
 'rx':      dict(name='Optum Rx',        rev26=74028*2/1000,  oe26=6250/1000,  rev25=154.726, oe25=6.125, da=845/154726, capex=399/154726),
}
for k,s in SEG.items(): s['m26'] = s['oe26']/s['rev26']*100
M['seg'] = SEG
put('oe26_total', sum(s['oe26'] for s in SEG.values()))
# Márgenes históricos por segmento (resultado operativo reportado / ingresos; 2025 ajustado y recast)
M['seg_hist'] = {
 'uhc':     {'2023':16415/281360*100, '2024':15584/298208*100, '2025':9425/344903*100, '1S26':9636/172282*100},
 'health':  {'2023':6560/95319*100,   '2024':7770/105358*100,  '2025':1.4, '1S26':2486/47583*100},
 'insight': {'2023':4268/18932*100,   '2024':3097/18757*100,   '2025':21.7, '1S26':2147/10450*100},
 'rx':      {'2023':5115/116087*100,  '2024':5836/133231*100,  '2025':4.0, '1S26':2674/74028*100},
}
# Sub-segmentos de UnitedHealthcare (ingresos; UNH no reporta resultado por sub-segmento)
UHC_SUB = {'ei_dom':(19048,38254,76.3),'ei_glob':(944,1856,2.9),'mr':(42390,84472,171.3),'cs':(23635,47700,94.4)}
M['uhc_sub'] = {k:dict(q2=v[0]/1000, h1=v[1]/1000, fy25=v[2]) for k,v in UHC_SUB.items()}
# Descomposición del margen 2026 de UHC con los rangos dichos por la gerencia (Wells Fargo, 9-sep-2026)
MR26 = 84472*2/1000; CS26 = 47700*2/1000; EI26 = (38254+1856)*2/1000
MA_M = put('ma_m26', 3.5)       # "mitad superior" del rango 2%-4% (supuesto: 3.5%)
MCD_M = put('mcd_m26', -1.2)    # cerca del extremo bueno de -1.1% a -1.7% (supuesto: -1.2%)
put('mr26', MR26); put('cs26', CS26); put('ei26', EI26)
put('mr_oe26', MR26*MA_M/100); put('cs_oe26', CS26*MCD_M/100)
put('ei_oe26', SEG['uhc']['oe26'] - M['mr_oe26'] - M['cs_oe26']); put('ei_m26', M['ei_oe26']/EI26*100)
# Membresía (miles)
MEMB = {'risk':(8165,7655),'fee':(21485,22265),'ma':(8445,7565),'mcd':(7380,6780),'medsup':(4285,4260),'total':(49760,48525)}
M['memb'] = MEMB
put('ma_chg', MEMB['ma'][1]-MEMB['ma'][0]); put('mcd_chg', MEMB['mcd'][1]-MEMB['mcd'][0])
put('fee_share', MEMB['fee'][1]/(MEMB['fee'][1]+MEMB['risk'][1])*100)

# Primas de UHC 2026E (proporción primas/ingresos de UHC 2025, 10-K) para traducir MLR a margen
UHC_PREM_SHARE = put('uhc_prem_share', 332390/344903*100)
UHC_PREM26 = put('uhc_prem26', SEG['uhc']['rev26']*UHC_PREM_SHARE/100)
M_NORM = put('uhc_m_norm', SEG['uhc']['m26'] + (MCR_G26-MLR_MID)*UHC_PREM_SHARE/100)
put('mlr_100bp_eps', 1.0/100*UHC_PREM26*(1-TAX/100)/SH_DIL*1000)
EPS_NORM = put('eps_norm', GUIDE_MID + (MCR_G26-MLR_MID)*M['mlr_100bp_eps'])

# ---------------- Costo de capital ----------------
BETAS = {'ELV':0.70,'CI':0.32,'CVS':0.58,'HUM':0.75,'CNC':1.11,'MOH':0.75}   # stockanalysis, 5 años mensual
BETA_UNH = put('beta_unh', 0.62)
beta_med = put('beta_med', st.median(BETAS.values()))
beta_adj = put('beta_adj', 0.67*beta_med + 0.33)
beta_adj_own = put('beta_adj_own', 0.67*BETA_UNH + 0.33)
KE_FLOOR = put('ke_floor', RF + 2.5)
KE = put('ke', max(RF + beta_adj*ERP, KE_FLOOR))
KE_OWN = put('ke_own', max(RF + beta_adj_own*ERP, KE_FLOOR))
KD_PRE = put('kd_pre', RF + 0.90)    # supuesto: bono largo A+ ~90 pb sobre el Treasury
KD = put('kd', KD_PRE*(1-TAX/100))
DEBT = put('debt', 3827 + 69501)     # 30-jun-2026
E = PRICE*SH_OUT
WD = put('wd', DEBT/(DEBT+E)*100)
def wacc(ke): return (1-WD/100)*ke + WD/100*KD
WACC = put('wacc', wacc(KE)); WACC_OWN = put('wacc_own', wacc(KE_OWN))

# ---------------- Deuda neta: caja regulada separada ----------------
CASH_CE = put('cash_ce', 28585); CASH_FREE = put('cash_free', 1100)          # 10-Q 2T26: US$1.1 mil millones de uso corporativo general
CASH_STI = put('cash_sti', 31468); LTI = put('lti', 57716)
put('cash_reg', CASH_CE - CASH_FREE)
put('invest_total', 81000)
NCI = put('nci', 1436 + 6066)        # participaciones no controladoras (redimibles + no redimibles)
ALEGEUS = put('alegeus', 3000)       # compra cerrada 2-jul-2026: 1.5 pagado + 1.5 a pagar en 12 meses
LEASES = put('leases', 4615)         # pasivo por arrendamientos operativos 31-dic-2025 (NO se resta: pagos ya en el OCF)
NETDEBT_DCF = put('net_debt_dcf', DEBT - CASH_FREE + ALEGEUS)
put('net_debt_all_cash', DEBT - CASH_STI)
put('claims_payable', 38930); put('ibnr', 26500)
put('debt_cap', 41.2)

# ---------------- Conversión a caja anclada en el OCF real ----------------
# k = OCF sin apalancar / (NOPAT ajustado + D&A), ventana 2025 real + 2026 guía (neutraliza el adelanto de pagos
# de CMS: parte de lo cobrado en 2025 correspondía a 2026, y el 2T26 trae otro pago adelantado).
t = TAX/100
ADJ_OE25 = 21700; ADJ_OE26 = 25215; DA25 = 4361; DA26 = 4400
SBC25, SBC26 = 971, 624*2           # compensación en acciones: se trata como costo (se descuenta del OCF)
k_num = (OCF25 + INT25*(1-t) - SBC25) + (OCF_G26 + INT26*(1-t) - SBC26)
k_den = (ADJ_OE25*(1-t) + DA25) + (ADJ_OE26*(1-t) + DA26)
K = put('k_conv', k_num/k_den)
put('k_conv_with_sbc', (k_num + SBC25 + SBC26)/k_den)
put('sbc25', SBC25); put('sbc26', SBC26)
# referencia: el mismo cociente con el TTM real (3T25-2T26)
TTM_ADJ_OE = 21700 - 14269 + 16943   # 2025 ajustado - 1S25 + 1S26 ajustado (aprox: 1S25 sin ajustes relevantes)
TTM_INT = 4002 - 2025 + 1917
put('k_ttm', (TTM_OCF + TTM_INT*(1-t) - (971-572+624))/(TTM_ADJ_OE*(1-t) + (4361-2145+2069)))

# ---------------- SOTP por DCF (15%) ----------------
YEARS = [2027,2028,2029,2030,2031]
MID = MLR_MID
def uhc_margins(sc, dmlr=0.0):
    # año 1 a mitad de camino entre 2026 y el normalizado; desde 2028, MLR de mitad de ciclo (+ dmlr)
    m_norm = SEG['uhc']['m26'] + (MCR_G26 - (MID + sc['uhc_dmlr'] + dmlr))*UHC_PREM_SHARE/100
    m26 = SEG['uhc']['m26']
    return [m26 + (m_norm-m26)*0.5] + [m_norm]*4
SC = {
 'bear': dict(dw=+0.5, g=2.0, uhc_dmlr=+0.75,
              uhc_g=[1.0,4.0,4.0,4.0,4.0], health_g=[-5,2,4,4,4], health_m=[2.5,3.0,3.5,3.5,3.5],
              insight_g=[3,4,4,4,4], insight_m=[20,20,20,20,20], rx_g=[1,3,3,3,3], rx_m=[3.8,3.6,3.6,3.6,3.6]),
 'base': dict(dw=0.0, g=2.5, uhc_dmlr=0.0,
              uhc_g=[2.0,5.0,5.0,5.0,4.5], health_g=[-3,4,6,6,5], health_m=[3.5,4.5,5.5,5.5,5.5],
              insight_g=[5,6,6,6,5], insight_m=[22,22,22,22,22], rx_g=[2,5,5,5,4], rx_m=[4.1,4.0,4.0,4.0,4.0]),
 'bull': dict(dw=-0.5, g=3.0, uhc_dmlr=-0.5,
              uhc_g=[3.0,6.0,6.0,5.5,5.0], health_g=[0,6,8,8,6], health_m=[4.0,6.0,7.0,7.0,7.0],
              insight_g=[6,8,8,7,6], insight_m=[22.5,23,23,23,23], rx_g=[3,6,6,5,5], rx_m=[4.2,4.2,4.2,4.2,4.2]),
}
STUB = 0.25   # oct-dic 2026
def seg_paths(sc, dmlr=0.0, dg_uhc=0.0):
    P = {}
    for key in SEG:
        s = SEG[key]
        if key == 'uhc':
            g = [x+dg_uhc for x in sc['uhc_g']]; m = uhc_margins(sc, dmlr)
        else:
            g = sc[f'{key}_g']; m = sc[f'{key}_m']
        rev = s['rev26']; rows = []
        # 4T26 (stub): resultado a la tasa de la guía 2026
        stub_oe = s['oe26']*STUB
        stub_fcf = K*(stub_oe*(1-t) + s['rev26']*STUB*s['da']) - s['rev26']*STUB*s['capex']
        for i in range(5):
            rev *= 1 + g[i]/100
            oe = rev*m[i]/100
            fcf = K*(oe*(1-t) + rev*s['da']) - rev*s['capex']
            rows.append(dict(y=YEARS[i], rev=rev, m=m[i], oe=oe, fcf=fcf))
        P[key] = dict(stub=stub_fcf, rows=rows)
    return P
def dcf(sc, w=None, g=None, dmlr=0.0, dg_uhc=0.0, detail=False):
    w = (WACC + sc['dw']) if w is None else w
    g = sc['g'] if g is None else g
    P = seg_paths(sc, dmlr, dg_uhc)
    out = {}; ev = 0; pv_tv_tot = 0
    for key, p in P.items():
        pv = p['stub']*(1+w/100)**-(STUB/2)
        for i, r in enumerate(p['rows']):
            tt = STUB + i + 0.5
            pv += r['fcf']*(1+w/100)**-tt
        tv = p['rows'][-1]['fcf']*(1+g/100)/((w-g)/100)
        pv_tv = tv*(1+w/100)**-(STUB+5)
        out[key] = dict(ev=pv+pv_tv, pv_fcf=pv, pv_tv=pv_tv, oe26=SEG[key]['oe26'], oe31=p['rows'][-1]['oe'], m31=p['rows'][-1]['m'])
        ev += pv + pv_tv; pv_tv_tot += pv_tv
    eq = ev - NETDEBT_DCF/1000 - NCI/1000
    ps = eq/SH_DIL*1000
    if detail: return dict(seg=out, ev=ev, eq=eq, ps=ps, tv_share=pv_tv_tot/ev*100, w=w, g=g, paths=P)
    return ps
for k, sc in SC.items():
    r = dcf(sc, detail=True)
    M[f'dcf_{k}'] = r['ps']; M[f'dcf_{k}_tvshare'] = r['tv_share']; M[f'dcf_{k}_ev'] = r['ev']; M[f'dcf_{k}_wacc'] = r['w']
    M[f'dcf_{k}_g'] = r['g']
    if k == 'base':
        M['sotp'] = {kk: dict(ev=v['ev'], pv_tv=v['pv_tv'], ps=v['ev']/SH_DIL*1000, share=v['ev']/r['ev']*100,
                             ev_oe26=v['ev']/v['oe26'], m31=v['m31'], oe31=v['oe31'],
                             oe27=r['paths'][kk]['rows'][0]['oe'], oe28=r['paths'][kk]['rows'][1]['oe'],
                             m27=r['paths'][kk]['rows'][0]['m'], m28=r['paths'][kk]['rows'][1]['m'],
                             ev_oe28=v['ev']/r['paths'][kk]['rows'][1]['oe'], tvshare=v['pv_tv']/v['ev']*100) for kk, v in r['seg'].items()}
        M['sotp_tot'] = dict(ev=r['ev'], oe26=sum(SEG[kk]['oe26'] for kk in SEG), oe28=sum(r['paths'][kk]['rows'][1]['oe'] for kk in SEG),
                             oe31=sum(v['oe31'] for v in r['seg'].values()))
        M['sotp_tot']['ev_oe28'] = r['ev']/M['sotp_tot']['oe28']; M['sotp_tot']['ev_oe26'] = r['ev']/M['sotp_tot']['oe26']
        M['sotp_tot']['m28'] = M['sotp_tot']['oe28']/sum(r['paths'][kk]['rows'][1]['rev'] for kk in SEG)*100
        M['dcf_base_eq'] = r['eq']
        M['dcf_base_paths'] = {kk: [dict(y=x['y'], rev=x['rev'], m=x['m'], oe=x['oe'], fcf=x['fcf']) for x in v['rows']] for kk, v in r['paths'].items()}
put('dcf_pw', 0.25*M['dcf_bear'] + 0.45*M['dcf_base'] + 0.30*M['dcf_bull'])
put('dcf_avg', (M['dcf_bear'] + M['dcf_base'] + M['dcf_bull'])/3)
put('dcf_gap', (M['dcf_base']/PRICE-1)*100)
put('dcf_base_ownbeta', dcf(SC['base'], w=WACC_OWN)); put('ownbeta_diff', M['dcf_base_ownbeta']-M['dcf_base'])
# Pesos del 15% intrínseco por segmento, según lo que aporta cada uno al valor de empresa
for kk, v in M['sotp'].items(): put(f'w_{kk}', 15*v['share']/100)
# Sensibilidad MLR -100/0/+100 pb (desde 2028; 2027 a mitad de camino)
put('dcf_mlr_m100', dcf(SC['base'], dmlr=-1.0)); put('dcf_mlr_p100', dcf(SC['base'], dmlr=+1.0))
put('dcf_mlr_m50', dcf(SC['base'], dmlr=-0.5)); put('dcf_mlr_p50', dcf(SC['base'], dmlr=+0.5))
put('dcf_mlr_at_g26', dcf(SC['base'], dmlr=MCR_G26-MID))   # si el MLR se queda en la guía 2026
# Grilla WACC x g
WG = [WACC-1, WACC-0.5, WACC, WACC+0.5, WACC+1]; GG = [1.5, 2.0, 2.5, 3.0, 3.5]
M['grid_w'] = WG; M['grid_g'] = GG
M['grid'] = [[dcf(SC['base'], w=w, g=g) for g in GG] for w in WG]
assert abs(M['grid'][2][2] - M['dcf_base']) < 1e-9
put('grid_up', (M['grid'][1][2]/M['dcf_base']-1)*100); put('grid_dn', (M['grid'][3][2]/M['dcf_base']-1)*100)
# DCF inverso
def solve(f, lo, hi, target, inc=True):
    for _ in range(100):
        mid = (lo+hi)/2
        if (f(mid) < target) == inc: lo = mid
        else: hi = mid
    return (lo+hi)/2
put('impl_wacc', solve(lambda w: dcf(SC['base'], w=w), 5.0, 12.0, PRICE, inc=False))
put('impl_g', solve(lambda g: dcf(SC['base'], g=g), 0.0, WACC-0.3, PRICE, inc=True))
put('impl_dmlr', solve(lambda d: dcf(SC['base'], dmlr=d), -5.0, 5.0, PRICE, inc=False))
put('impl_mlr', MID + M['impl_dmlr'])
put('impl_dg_uhc', solve(lambda d: dcf(SC['base'], dg_uhc=d), -20.0, 10.0, PRICE, inc=True))
put('impl_uhc_g', 5.0 + M['impl_dg_uhc'])
put('impl_uhc_m', SEG['uhc']['m26'] + (MCR_G26 - M['impl_mlr'])*UHC_PREM_SHARE/100)
put('wacc_minus_impl', WACC - M['impl_wacc'])
Ksave = K; K = M['k_conv_with_sbc']; put('dcf_base_with_sbc', dcf(SC['base'])); K = Ksave
put('sbc_effect', M['dcf_base_with_sbc']-M['dcf_base'])
# DCF con k del TTM (referencia del OCF real atípico)
Ksave = K; K = M['k_ttm']; put('dcf_base_kttm', dcf(SC['base'])); K = Ksave
put('kttm_diff', M['dcf_base_kttm']-M['dcf_base'])

# ---------------- Comparables (25%) ----------------
# P/E sobre EPS de los próximos 12 meses (0.25 x 2026 + 0.75 x 2027), precios 28-sep-2026.
PEERS = {
 'ELV': dict(name='Elevance Health', px=394.59, e26=27.18, e27=29.32, e28=33.30, pre=33.14, pre_y=2023, beta=0.70, pt=450.44),
 'CI':  dict(name='Cigna Group',     px=271.83, e26=30.51, e27=33.38, e28=36.95, pre=27.33, pre_y=2024, beta=0.32, pt=342.50),
 'CVS': dict(name='CVS Health',      px=87.85,  e26=8.02,  e27=8.51,  e28=9.53,  pre=8.74,  pre_y=2023, beta=0.58, pt=113.25),
 'HUM': dict(name='Humana',          px=389.63, e26=9.00,  e27=15.36, e28=27.45, pre=26.09, pre_y=2023, beta=0.75, pt=431.67),
 'CNC': dict(name='Centene',         px=62.53,  e26=4.89,  e27=5.34,  e28=6.83,  pre=7.17,  pre_y=2024, beta=1.11, pt=68.56),
 'MOH': dict(name='Molina',          px=189.64, e26=5.29,  e27=9.76,  e28=13.01, pre=22.65, pre_y=2024, beta=0.75, pt=203.07),
}
for k, p in PEERS.items():
    p['ntm'] = 0.25*p['e26'] + 0.75*p['e27']; p['pe'] = p['px']/p['ntm']
    p['ratio'] = p['ntm']/p['pre']*100; p['g2'] = ((p['e28']/p['e26'])**0.5-1)*100
# Regla de exclusión: EPS de los próximos 12 meses todavía >25% debajo de su máximo 2023-2024 (año de reseteo)
for k, p in PEERS.items(): p['excl'] = p['ratio'] < 75
M['peers'] = PEERS
CLEAN = {k: p for k, p in PEERS.items() if not p['excl']}
put('n_clean', len(CLEAN))
pe_mean = put('peer_pe_mean', st.mean(p['pe'] for p in CLEAN.values()))
pe_med = put('peer_pe_med', st.median(p['pe'] for p in CLEAN.values()))
pe_max = put('peer_pe_max', max(p['pe'] for p in CLEAN.values()))
pe_min = put('peer_pe_min', min(p['pe'] for p in CLEAN.values()))
put('peer_pe_mean_all', st.mean(p['pe'] for p in PEERS.values()))
put('unh_ratio', NTM/27.66*100)
put('unh_g2', ((C28/C26)**0.5-1)*100)
COMP = put('comp', pe_mean*NTM1/(1+KE/100))
put('comp_low', pe_med*NTM); put('comp_high', pe_max*NTM1/(1+KE/100))
put('comp_gap', (COMP/PRICE-1)*100)
put('unh_pe_vs_peer', (M['pe_ntm_now']/pe_mean-1)*100)
put('comp_all', M['peer_pe_mean_all']*NTM1/(1+KE/100))
put('comp_ntm_only', pe_mean*NTM)
# Regresiones P/E vs crecimiento de EPS a dos años (2026->2028)
def reg(xs, ys):
    mx = st.mean(xs); my = st.mean(ys)
    sxy = sum((x-mx)*(y-my) for x,y in zip(xs,ys)); sxx = sum((x-mx)**2 for x in xs); syy = sum((y-my)**2 for y in ys)
    b = sxy/sxx; return dict(slope=b, icpt=my-b*mx, r2=sxy**2/(sxx*syy), n=len(xs))
allp = list(PEERS.items())
M['reg_all'] = reg([p['g2'] for _,p in allp], [p['pe'] for _,p in allp])
mx = st.mean(p['g2'] for _,p in allp); ext = max(allp, key=lambda kp: abs(kp[1]['g2']-mx))
rest = [kp for kp in allp if kp[0] != ext[0]]
M['reg_all_ex'] = reg([p['g2'] for _,p in rest], [p['pe'] for _,p in rest]); M['reg_all_ex']['dropped'] = ext[0]
cl = list(CLEAN.items())
M['reg_clean'] = reg([p['g2'] for _,p in cl], [p['pe'] for _,p in cl])
# con la ecuación de los 6 (si se aplicara): P/E que "correspondería" al crecimiento de UNH
put('reg_all_unh_pe', M['reg_all']['icpt'] + M['reg_all']['slope']*M['unh_g2'])
put('reg_all_ex_unh_pe', M['reg_all_ex']['icpt'] + M['reg_all_ex']['slope']*M['unh_g2'])
# Referencias de múltiplo para los segmentos de Optum (EV/EBIT TTM, stockanalysis 29-sep-2026)
M['optum_refs'] = {
 'rx': [('Cigna (Evernorth + seguros)', 8.83), ('CVS (Caremark + Aetna + farmacias)', 14.26)],
 'insight': [('Waystar (ciclo de ingresos y pagos)', 21.08), ('HealthEquity (cuentas de salud)', 22.28)],
 'health': [('DaVita (proveedor con riesgo en riñón)', 11.29), ('Privia (red médica en valor)', 46.88)],
}

# ---------------- Reversión (35%) ----------------
d = json.load(open('yh/UNH.mo.json'))['chart']['result'][0]
closes = {}
for ts, c in zip(d['timestamp'], d['indicators']['quote'][0]['close']):
    dt = datetime.datetime.fromtimestamp(ts, datetime.UTC)
    if c: closes[(dt.year, dt.month)] = c
seq = [(y, q) for y in range(2016, 2029) for q in range(4)]
win = []
for i, (y, q) in enumerate(seq):
    ym = (y, 3*(q+1))
    if ym < (2016, 3) or ym > (2026, 6): continue
    nx = seq[i+1:i+5]
    ntm = sum(EPS[a][b] for a, b in nx)
    reset = any((a == 2025 and b >= 1) for a, b in nx) or ym >= (2025, 9)
    win.append(dict(date=f'{ym[0]}-{ym[1]:02d}', price=closes[ym], ntm=ntm, pe=closes[ym]/ntm, reset=reset))
M['rev_window'] = win
clean = [w for w in win if not w['reset']]
put('rev_n', len(clean)); put('rev_n_all', len(win)); put('rev_n_excl', len(win)-len(clean))
put('rev_first', clean[0]['date']); put('rev_last', clean[-1]['date'])
put('rev_excl_first', [w for w in win if w['reset']][0]['date']); put('rev_excl_last', [w for w in win if w['reset']][-1]['date'])
PE_CLEAN = put('rev_pe_avg', st.mean(w['pe'] for w in clean))
put('rev_pe_avg_all', st.mean(w['pe'] for w in win))
put('rev_pe_avg_reset', st.mean(w['pe'] for w in win if w['reset']))
put('rev_pe_min', min(w['pe'] for w in clean)); put('rev_pe_max', max(w['pe'] for w in clean))
put('rev_pe_last8', st.mean(w['pe'] for w in clean[-8:]))
REV = put('rev', PE_CLEAN*EPS_NORM)
put('rev_low', M['rev_pe_min']*EPS_NORM); put('rev_high', M['rev_pe_max']*EPS_NORM)
put('rev_on_ntm', PE_CLEAN*NTM)                     # mismo P/E sobre el EPS de consenso (sin normalizar)
put('rev_all_on_norm', M['rev_pe_avg_all']*EPS_NORM)  # sin excluir el reseteo
put('rev_excl_effect', REV - M['rev_all_on_norm'])
put('rev_gap', (REV/PRICE-1)*100)
put('rev_mlr_m100', PE_CLEAN*(EPS_NORM + M['mlr_100bp_eps'])); put('rev_mlr_p100', PE_CLEAN*(EPS_NORM - M['mlr_100bp_eps']))

# ---------------- Consenso (25%) ----------------
CONS = put('cons', 471.10); put('cons_med', 480.0); put('cons_low', 370.0); put('cons_high', 529.0); put('cons_n', 21)
put('cons_gap', (CONS/PRICE-1)*100)

# ---------------- Blend ----------------
W = {'dcf': 0.15, 'comp': 0.25, 'rev': 0.35, 'cons': 0.25}
V = {'dcf': M['dcf_base'], 'comp': COMP, 'rev': REV, 'cons': CONS}
BLEND = put('blend', sum(W[k]*V[k] for k in W))
put('blend_gap', (BLEND/PRICE-1)*100)
for k in W: put(f'contrib_{k}', W[k]*V[k])
put('indep', (W['dcf']*V['dcf'] + W['comp']*V['comp'])/(W['dcf']+W['comp']))
put('anch', (W['rev']*V['rev'] + W['cons']*V['cons'])/(W['rev']+W['cons']))
put('indep_gap', (M['indep']/PRICE-1)*100); put('anch_gap', (M['anch']/PRICE-1)*100)
def blend_with(dcfv=None, revv=None, compv=None):
    v = dict(V)
    if dcfv is not None: v['dcf'] = dcfv
    if revv is not None: v['rev'] = revv
    if compv is not None: v['comp'] = compv
    return sum(W[k]*v[k] for k in W)
put('blend_mlr_m100', blend_with(dcfv=M['dcf_mlr_m100'], revv=M['rev_mlr_m100']))
put('blend_mlr_p100', blend_with(dcfv=M['dcf_mlr_p100'], revv=M['rev_mlr_p100']))
put('blend_rev_all', blend_with(revv=M['rev_all_on_norm']))
put('blend_rev_ntm', blend_with(revv=M['rev_on_ntm']))
put('blend_comp_all', blend_with(compv=M['comp_all']))
for k in ('m100', 'p100'):
    put(f'blend_mlr_{k}_gap', (M[f'blend_mlr_{k}']/PRICE-1)*100)
put('dcf_mlr_m100_gap', (M['dcf_mlr_m100']/PRICE-1)*100); put('dcf_mlr_p100_gap', (M['dcf_mlr_p100']/PRICE-1)*100)
put('rev_mlr_m100_gap', (M['rev_mlr_m100']/PRICE-1)*100); put('rev_mlr_p100_gap', (M['rev_mlr_p100']/PRICE-1)*100)

# ---------------- Capital, dividendo, balance ----------------
DIV = put('div_annual', 9.28); put('div_yield', DIV/PRICE*100)
put('div_prev', 8.84); put('div_raise', (9.28/8.84-1)*100)
put('buyback_26', 5000); put('buyback_1h26', 1646); put('div_paid_1h26', 4092)
put('sub_div_2024', 9200); put('sub_net_infusion_2025', 535)
put('parent_cash_25', 303); put('parent_debt_25', 5887+71794)
put('payout_eps', DIV/GUIDE_MID*100)
put('ndebt_ebitda', (DEBT - CASH_FREE)/(ADJ_OE26 + DA26))
put('fcf_g26', OCF_G26 - 3800); put('fcf_yield', (OCF_G26-3800)/(MKT_CAP*1000)*100)
put('mktcap_b', MKT_CAP)

# ---------------- Series para gráficos ----------------
M['ann'] = dict(rev={2019:242.155,2020:257.141,2021:287.597,2022:324.162,2023:371.622,2024:400.278,2025:447.567},
                eps={y: FYEPS[y] for y in range(2019, 2026)})
# serie trimestral de P/E (etiquetas solo en marzo, para que no se encimen)
mon = ['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic']
M['js_pe_labels'] = json.dumps([(f"{w['date'][:4]}" if w['date'][5:] == '03' else '') for w in win], ensure_ascii=False)
M['js_pe_vals'] = json.dumps([round(w['pe'], 2) for w in win])
M['js_pe_avg'] = json.dumps([round(PE_CLEAN, 2)]*len(win))
M['js_mcr_years'] = json.dumps([str(y) for y in range(2016, 2026)] + ['2026G'])
M['js_mcr_vals'] = json.dumps([MCR[y] for y in range(2016, 2026)] + [MCR_G26])
M['js_mcr_mid'] = json.dumps([round(MLR_MID, 2)]*11)
# sparkline: últimos 7 cierres mensuales (mar-2026 a ago-2026 + 28-sep-2026)
SPARK = [closes[(2026, m)] for m in range(3, 9)] + [PRICE]
M['spark'] = [round(x, 2) for x in SPARK]
put('ret_ytd', (PRICE/closes[(2025, 12)]-1)*100)
put('px_dec25', closes[(2025, 12)])

# EPS ajustado implícito en el caso Base (intereses ~3.7 mil millones, participaciones no controladoras ~0.75,
# amortización de intangibles ~1.345 antes de impuestos, 906 millones de acciones constantes: sin recompras)
def impl_eps(oe): return ((oe - 3.7)*(1-t) - 0.75 + 1.345*(1-t))/SH_DIL*1000
OE27 = sum(M['dcf_base_paths'][kk][0]['oe'] for kk in SEG); OE28 = sum(M['dcf_base_paths'][kk][1]['oe'] for kk in SEG)
put('impl_eps27', impl_eps(OE27)); put('impl_eps28', impl_eps(OE28))
put('impl_eps27_vs', (M['impl_eps27']/C27-1)*100); put('impl_eps28_vs', (M['impl_eps28']/C28-1)*100)
put('impl_eps26_chk', impl_eps(25.215))
Q_LAB = ['1T23','2T23','3T23','4T23','1T24','2T24','3T24','4T24','1T25','2T25','3T25','4T25','1T26','2T26']
M['js_mcrq_labels'] = json.dumps(Q_LAB); M['js_mcrq_vals'] = json.dumps([MCRQ[q] for q in Q_LAB])
YOY = ['1T25','2T25','3T25','4T25','1T26','2T26']
M['yoy'] = {q: round(MCRQ[q] - MCRQ[q[:2]+str(int(q[2:])-1)], 1) for q in YOY}
M['js_yoy_labels'] = json.dumps(YOY); M['js_yoy_vals'] = json.dumps([M['yoy'][q] for q in YOY])
M['js_mcr_mid_q'] = json.dumps([round(MLR_MID,2)]*len(Q_LAB))
# derivados de texto
put('mlr_mid_p100', MLR_MID+1); put('uhc_prem_frac', UHC_PREM_SHARE/100)
put('mcr_rise_bp', (MCR_ADJ25-MCR[2023])*100); put('mcr_back_bp', (MCR_ADJ25-MCR_G26)*100)
put('dcp_yoy', DCP['2T26']-DCP['2T25'])
put('sotp_uhc_pct', M['sotp']['uhc']['share']); put('sotp_optum_pct', 100-M['sotp']['uhc']['share'])
put('mlr_mid_minus_1624', MLR_MID - M['mlr_1624'])
put('uhc_m_norm_minus_26', M_NORM - SEG['uhc']['m26'])
put('eps_norm_vs_c27', (EPS_NORM/C27-1)*100); put('eps_norm_vs_c28', (EPS_NORM/C28-1)*100)
put('pe_on_norm', PRICE/EPS_NORM)
put('dcf_bull_gap', (M['dcf_bull']/PRICE-1)*100); put('dcf_bear_gap', (M['dcf_bear']/PRICE-1)*100)
put('blend_vs_cons', (BLEND/CONS-1)*100)
put('health_m_target_lo', 6.0); put('health_m_target_hi', 8.0)

json.dump(M, open('model.json', 'w'), indent=1, default=float)
if __name__ == '__main__':
    for k, v in M.items():
        if isinstance(v, (int, float)) and not isinstance(v, bool): print(f'{k:24s} {v:,.4f}')
    print('peers:'); [print(' ', k, round(p['pe'],2), round(p['ratio'],1), round(p['g2'],1), p['excl']) for k,p in PEERS.items()]
    print('reg', M['reg_all'], M['reg_all_ex'], M['reg_clean'])
    print('sotp', {k: (round(v['ev'],1), round(v['share'],1), round(v['ev_oe26'],1)) for k,v in M['sotp'].items()})
    for w in win: print(w['date'], round(w['price'],2), round(w['ntm'],2), round(w['pe'],2), w['reset'])
