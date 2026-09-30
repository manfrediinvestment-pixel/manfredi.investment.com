# Modelo de valuación KO (The Coca-Cola Company) — todos los números derivados del informe salen de acá.
# Marco: informe-consumo-masivo, sub-industria bebidas sin alcohol (modelo de concentrado / franquicia).
# Fuentes: 10-K 2025 (20-feb-2026), 10-Q 1T/2T 2026, comunicados 8-K ítem 2.02 (1T2016-2T2026), 8-K de sucesión
# (10-dic-2025, 19-feb-2026, 25-jun-2026), 8-K fairlife (16-jul-2026), DEF 14A 2026, Yahoo, Nasdaq/Zacks,
# stockanalysis (S&P Global), FactSet Earnings Insight. Fecha de corte de precios: cierre 29-sep-2026.
import json, datetime, statistics as st

M = {}
def put(k, v): M[k] = v; return v
def yh_daily(t, last='2026-09-29'):
    d = json.load(open(f'yh/{t}.d.json'))['chart']['result'][0]
    rows = [(datetime.datetime.fromtimestamp(a, datetime.UTC).date().isoformat(), c)
            for a, c in zip(d['timestamp'], d['indicators']['quote'][0]['close']) if c]
    dec = [r for r in rows if r[0] <= '2025-12-31'][-1][1]
    now = [r for r in rows if r[0] <= last][-1][1]
    return dec, now

# ---------------- Mercado (cierre 29-sep-2026) ----------------
PRICE = put('price', 86.84)
RF = put('rf', 5.255)                # ^TNX cierre 29-sep-2026
ERP = put('erp', 5.0)
SH_DIL = put('sh_dil', 4313.0)       # diluidas promedio 2T26 (millones)
SH_OUT = put('sh_out', 4303.0)       # 7,040 emitidas - 2,737 en tesorería (10-Q 2T26)
MKT_CAP = put('mkt_cap', PRICE*SH_OUT/1000)   # US$ miles de millones
SPX_PE, SPX_PE10 = put('spx_pe', 19.2), put('spx_pe10', 19.0)   # FactSet, 25-sep-2026 (mismo dato que PG)

# ---------------- Consenso de EPS comparable (Nasdaq / Zacks, 29-sep-2026) ----------------
C26, C27, C28 = put('c26', 3.29), put('c27', 3.53), put('c28', 3.77)
put('c26_n', 10); put('c27_n', 10); put('c28_n', 5)
put('c26_sa', 3.30); put('c27_sa', 3.53)   # stockanalysis (S&P Global), 28-sep-2026, referencia
REV_C26 = put('rev_c26', 49.72)            # consenso de ventas 2026 (S&P Global), US$ miles de millones
EPS25 = put('eps25', 3.00)
GUIDE_LO, GUIDE_HI = put('guide_lo', 9.0), put('guide_hi', 10.0)   # crecimiento del EPS comparable 2026 (28-jul-2026)
put('guide_eps_lo', EPS25*(1+GUIDE_LO/100)); put('guide_eps_hi', EPS25*(1+GUIDE_HI/100))
GUIDE_MID = put('guide_mid', (M['guide_eps_lo']+M['guide_eps_hi'])/2)
NTM = put('eps_ntm', 0.25*C26 + 0.75*C27)        # oct-2026 a sep-2027
put('pe_ntm_now', PRICE/NTM)
put('eps_g26', (C26/EPS25-1)*100); put('eps_g27', (C27/C26-1)*100); put('eps_g28', (C28/C27-1)*100)
put('ko_g2', ((C28/C26)**0.5-1)*100)

# ---------------- EPS trimestral (comunicados 8-K ítem 2.02) ----------------
EPS = {2016:[0.45,0.60,0.49,0.37], 2017:[0.43,0.59,0.50,0.39], 2018:[0.47,0.61,0.58,0.42],
       2019:[0.48,0.63,0.56,0.44], 2020:[0.51,0.42,0.55,0.47], 2021:[0.55,0.68,0.65,0.45],
       2022:[0.64,0.70,0.69,0.45], 2023:[0.68,0.78,0.74,0.49], 2024:[0.72,0.84,0.77,0.55],
       2025:[0.73,0.87,0.82,0.58], 2026:[0.86,0.97]}
FYEPS = {2016:1.91, 2017:1.91, 2018:2.08, 2019:2.11, 2020:1.95, 2021:2.32, 2022:2.48, 2023:2.69, 2024:2.88, 2025:3.00}
GAAP = {2016:1.49, 2017:0.29, 2018:1.57, 2019:2.07, 2020:1.79, 2021:2.25, 2022:2.19, 2023:2.47, 2024:2.46, 2025:3.04}
for y, v in FYEPS.items():
    assert abs(sum(EPS[y]) - v) < 0.015, (y, sum(EPS[y]), v)
# 2S26 con el consenso anual y la estacionalidad de 2025; 2027 con el consenso y la misma estacionalidad
s25 = [x/sum(EPS[2025]) for x in EPS[2025]]
h2 = C26 - sum(EPS[2026])
EPS[2026] = EPS[2026] + [h2*s25[2]/(s25[2]+s25[3]), h2*s25[3]/(s25[2]+s25[3])]
EPS[2027] = [C27*s for s in s25]; EPS[2028] = [C28*s for s in s25]
put('eps_2h26_impl', h2)
M['gaap_gap'] = {str(y): (GAAP[y]/FYEPS[y]-1)*100 for y in GAAP}
EXCL_RULE = put('excl_rule', 10.0)   # se excluye el año si el EPS GAAP se aparta más de 10% del comparable
EXCL = sorted(y for y in GAAP if abs(GAAP[y]/FYEPS[y]-1)*100 > EXCL_RULE)
M['excl_years'] = EXCL
put('excl_list', ', '.join(str(y) for y in EXCL[:-1]) + ' y ' + str(EXCL[-1]))

# ---------------- Descomposición del orgánico (comunicados, % sobre el trimestre del año anterior) ----------------
Q = ['3T23','4T23','1T24','2T24','3T24','4T24','1T25','2T25','3T25','4T25','1T26','2T26']
ORG = {  # concentrado, precio/mix, monedas, compras/ventas, reportado, orgánico, unit case volume
 '3T23':(2,9,-2,-1,8,11,2),  '4T23':(3,9,-4,-1,7,12,2),  '1T24':(-2,13,-6,-2,3,11,1), '2T24':(6,9,-6,-5,3,15,2),
 '3T24':(-2,10,-5,-4,-1,9,-1),'4T24':(5,9,-3,-5,6,14,2), '1T25':(1,5,-5,-3,-2,6,2),  '2T25':(-1,6,-3,0,1,5,-1),
 '3T25':(0,6,0,0,5,6,1),     '4T25':(4,1,-2,-1,2,5,1),   '1T26':(8,2,3,-1,12,10,3),  '2T26':(4,2,2,-1,7,6,5)}
INFL = {'1T24':6, '2T24':5, '3T24':4, '4T24':4}   # puntos de precio/mix de "mercados con inflación intensa" (KO)
M['org'] = {q: dict(conc=v[0], pm=v[1], fx=v[2], ad=v[3], rep=v[4], org=v[5], ucv=v[6], infl=INFL.get(q)) for q, v in ORG.items()}
L8 = Q[-8:]; L4 = Q[-4:]
put('ucv_8q', st.mean(ORG[q][6] for q in L8)); put('ucv_4q', st.mean(ORG[q][6] for q in L4))
put('pm_8q', st.mean(ORG[q][1] for q in L8)); put('pm_4q', st.mean(ORG[q][1] for q in L4))
put('conc_8q', st.mean(ORG[q][0] for q in L8)); put('conc_4q', st.mean(ORG[q][0] for q in L4))
put('org_8q', st.mean(ORG[q][5] for q in L8)); put('org_4q', st.mean(ORG[q][5] for q in L4))
put('ucv_12q', st.mean(ORG[q][6] for q in Q))
put('pm_3q', st.mean(ORG[q][1] for q in Q[-3:]))
for q in INFL: M['org'][q]['pm_ex'] = ORG[q][1] - INFL[q]; M['org'][q]['org_ex'] = ORG[q][5] - INFL[q]
put('infl_2024_avg', st.mean(INFL.values())); put('pm_ex_2024_avg', st.mean(ORG[q][1]-INFL[q] for q in INFL))
put('org_ex_2024_avg', st.mean(ORG[q][5]-INFL[q] for q in INFL))
ANN = {2019:(6,2), 2020:(-9,-6), 2021:(16,8), 2022:(16,5), 2023:(12,2), 2024:(12,1), 2025:(5,0)}  # orgánico, UCV
M['ann_org'] = {str(y): dict(org=v[0], ucv=v[1]) for y, v in ANN.items()}
put('pm_fy24', 11); put('pm_fy25', 4); put('infl_fy24', 5); put('pm_fy23', 10)
put('pm_ex_fy24', 11-5)

# ---------------- Consolidado (XBRL + comunicados) ----------------
REV = {2016:41.863, 2017:36.212, 2018:34.300, 2019:37.266, 2020:33.014, 2021:38.655, 2022:43.004, 2023:45.754, 2024:47.061, 2025:47.941}
M['rev_hist'] = {str(k): v for k, v in REV.items()}
put('rev_cagr_1925', ((REV[2025]/REV[2019])**(1/6)-1)*100)
put('rev_drop_1618', (REV[2018]/REV[2016]-1)*100)
COMP = {2022:(43.046,12.345,58.6), 2023:(45.784,13.336,59.7), 2024:(46.897,14.085,61.1), 2025:(48.062,15.013,61.5)}
COMP_1H26 = (25.844, 9.058, 62.9); COMP_1H25 = (23.833, 8.168, 62.4)
M['comp_om'] = {str(y): v[1]/v[0]*100 for y, v in COMP.items()}; M['comp_om']['1S26'] = COMP_1H26[1]/COMP_1H26[0]*100
M['comp_gm'] = {str(y): v[2] for y, v in COMP.items()}; M['comp_gm']['1S26'] = COMP_1H26[2]
ADV = {2021:4.0, 2022:4.0, 2023:5.0, 2024:5.1, 2025:5.4}    # publicidad (10-K; XBRL redondea a US$ 0.1 mil millones)
M['adv_pct'] = {str(y): ADV[y]/REV[y]*100 for y in ADV}
GM = {2021:(38.655-15.357)/38.655*100, 2022:(43.004-18.000)/43.004*100, 2023:(45.754-18.520)/45.754*100,
      2024:(47.061-18.324)/47.061*100, 2025:(47.941-18.397)/47.941*100}
M['gm_gaap'] = {str(y): v for y, v in GM.items()}
put('om_gaap25', 13.762/47.941*100); put('om_gaap24', 9.992/47.061*100)
DA25, DA_1H25, DA_1H26 = 1.050, 0.546, 0.530
TTM_COI = put('ttm_coi', COMP[2025][1] - COMP_1H25[1] + COMP_1H26[1])
TTM_DA = put('ttm_da', DA25 - DA_1H25 + DA_1H26)
EBITDA_TTM = put('ebitda_ttm', TTM_COI + TTM_DA)
put('ttm_rev', 47.941 - 23.664 + 25.852)
put('ebitda25', COMP[2025][1] + DA25)
put('coi_1h26_g', (COMP_1H26[1]/COMP_1H25[1]-1)*100)

# ---------------- Flujo de caja (10-K, 10-Q) ----------------
OCF = {2019:10.471, 2020:9.844, 2021:12.625, 2022:11.018, 2023:11.599, 2024:6.805, 2025:7.408}
CAPEX = {2019:2.054, 2020:1.177, 2021:1.367, 2022:1.484, 2023:1.852, 2024:2.064, 2025:2.112}
ONEOFF = {2024:6.0, 2025:6.1}    # depósito al IRS (sep-2024) y pago final de fairlife (mar-2025), dentro del OCF
OCF_ADJ = {y: OCF[y] + ONEOFF.get(y, 0) for y in OCF}
M['ocf'] = {str(y): OCF[y] for y in OCF}; M['ocf_adj'] = {str(y): OCF_ADJ[y] for y in OCF}
M['capex'] = {str(y): CAPEX[y] for y in CAPEX}; M['fcf_adj'] = {str(y): OCF_ADJ[y]-CAPEX[y] for y in OCF}
DIVP = {2021:7.252, 2022:7.616, 2023:7.952, 2024:8.359, 2025:8.779}
BUY = {2021:0.111, 2022:1.418, 2023:2.289, 2024:1.795, 2025:0.746}
M['divp'] = {str(y): v for y, v in DIVP.items()}; M['buy'] = {str(y): v for y, v in BUY.items()}
M['ret_fcf'] = {str(y): (DIVP[y]+BUY[y])/(OCF_ADJ[y]-CAPEX[y])*100 for y in DIVP}
OCF_G26, CAPEX_G26 = put('ocf_g26', 14.6), put('capex_g26', 2.2)
put('fcf_g26', OCF_G26 - CAPEX_G26)
OCF_1H26 = put('ocf_1h26', 7.543); put('capex_1h26', 0.684)
put('ocf_1h26_m', OCF_1H26/25.852*100)
put('ocf25_adj_m', OCF_ADJ[2025]/REV[2025]*100); put('ocf_g26_m', OCF_G26/REV_C26*100)
put('ttm_ocf_adj', OCF_ADJ[2025] - (-1.391 + 6.1) + OCF_1H26)   # 1S25 ajustado por fairlife
put('ttm_ocf_m', M['ttm_ocf_adj']/M['ttm_rev']*100)
EQDIV25 = put('eqdiv25', 0.993); EQINC25 = put('eqinc25', 2.031)
EQINC_1H26 = 0.988; EQDIV_1H26 = put('eqdiv_1h26', EQINC_1H26 - 0.520)
put('eqinc_1h26', EQINC_1H26)
INT_EXP25, INT_INC25 = 1.654, 0.786
NETINT25 = put('netint25', INT_EXP25 - INT_INC25)
NETINT26 = put('netint26', 2*(0.744 - 0.420))   # 1S26 anualizado
TAX = put('tax', 19.9)                          # tasa efectiva subyacente guiada 2026
t = TAX/100
NI_C25 = put('ni_c25', EPS25*4.315)               # utilidad comparable 2025 (EPS x diluidas), US$ miles de millones
NI_C26 = put('ni_c26', C26*SH_DIL/1000)
put('conv25', (OCF_ADJ[2025]-CAPEX[2025])/NI_C25*100)
put('conv26', M['fcf_g26']/NI_C26*100)
# conversión sin la parte no cobrada de las ganancias de participadas (equity income - dividendos recibidos)
put('conv25_ex_eq', (OCF_ADJ[2025]-CAPEX[2025])/(NI_C25-(EQINC25-EQDIV25))*100)
put('capex_pct25', CAPEX[2025]/REV[2025]*100); put('capex_pct_g26', CAPEX_G26/REV_C26*100)

# ---------------- Dividendo ----------------
DPS = {2016:1.40, 2017:1.48, 2018:1.56, 2019:1.60, 2020:1.64, 2021:1.68, 2022:1.76, 2023:1.84, 2024:1.94, 2025:2.04, 2026:2.12}
M['dps'] = {str(y): v for y, v in DPS.items()}
DIV = put('div_annual', DPS[2026]); put('div_yield', DIV/PRICE*100)
put('div_raise', (DPS[2026]/DPS[2025]-1)*100); put('div_cagr10', ((DPS[2026]/DPS[2016])**0.1-1)*100)
put('payout_eps', DIV/C26*100); put('payout_fcf', DIV*SH_OUT/1000/M['fcf_g26']*100)
put('div_streak', 64)
put('fcf_yield', M['fcf_g26']/MKT_CAP*100)

# ---------------- Balance (10-Q 2T26, 3-jul-2026) ----------------
DEBT = put('debt', 0.048 + 6.494 + 37.001)
CASH = put('cash', 12.907 + 0.622 + 2.842)       # caja + inversiones de corto plazo + títulos negociables
NETDEBT = put('net_debt', DEBT - CASH)
LEASES = put('leases', 1.722)                     # pasivo por arrendamientos operativos (10-K 2025)
NETDEBT_L = put('net_debt_l', NETDEBT + LEASES)
NCI = put('nci', 2.165)
put('nd_ebitda', NETDEBT/EBITDA_TTM); put('nd_ebitda_l', NETDEBT_L/EBITDA_TTM)
put('gw_int', 15.456 + 12.500); put('gw_int_pct', (15.456+12.500)/107.922*100)
put('assets', 107.922); put('equity_ko', 36.150)
put('debt_st', 0.048 + 6.494)
put('irs_dep', 6.0); put('irs_int', 0.514); put('irs_reserve', 0.529); put('irs_contingent', 14.0); put('irs_etr', 3.8)
put('irs_win_ps', (6.0+0.514)/SH_DIL*1000)
put('irs_2h26_accrual', 0.9)   # 1S26: la contingencia creció ~US$0.9 mil millones (10-Q)

# ---------------- Participaciones en embotelladoras y en Monster (10-K 2025, 31-dic-2025) ----------------
STAKES = {  # valor de mercado y valor contable al 31-dic-2025 (US$ millones), ticker, tipo de cambio
 'MNST': ('Monster Beverage', 15659, 5593, 'MNST', None),
 'CCEP': ('Coca-Cola Europacific Partners', 7163, 3926, 'CCEP', None),
 'KOF':  ('Coca-Cola FEMSA', 5543, 2236, 'KOF', None),
 'CCH':  ('Coca-Cola HBC', 4051, 1391, 'CCH.L', ('GBPUSD=X', 'mul')),
 'CCBJ': ('Coca-Cola Bottlers Japan', 822, 459, '2579.T', ('JPY=X', 'div')),
 'CCI':  ('Coca-Cola İçecek', 770, 288, 'CCOLA.IS', ('TRY=X', 'div')),
 'AKO':  ('Embotelladora Andina', 278, 106, 'AKO-B', None),
}
TAX_GAIN = put('tax_gain', 21.0)
M['stakes'] = {}
for k, (name, fv, cv, tk, fx) in STAKES.items():
    p0, p1 = yh_daily(tk); r = p1/p0
    if fx:
        f0, f1 = yh_daily(fx[0]); r *= (f1/f0) if fx[1] == 'mul' else (f0/f1)
    now = fv*r
    M['stakes'][k] = dict(name=name, fv_dec=fv/1000, cv=cv/1000, now=now/1000, chg=(r-1)*100,
                          aftertax=(now - max(now-cv, 0)*TAX_GAIN/100)/1000)
STK_NOW = put('stk_now', sum(s['now'] for s in M['stakes'].values()))
STK_DEC = put('stk_dec', sum(s['fv_dec'] for s in M['stakes'].values()))
STK_CV = put('stk_cv', sum(s['cv'] for s in M['stakes'].values()))
STK_AT = put('stk_at', sum(s['aftertax'] for s in M['stakes'].values()))
put('stk_ps', STK_AT/SH_DIL*1000); put('stk_now_ps', STK_NOW/SH_DIL*1000)
put('stk_pct_mcap', STK_NOW/MKT_CAP*100)
UNLISTED = put('unlisted', 20.235 - 13.999)      # participaciones no cotizantes a valor contable (31-dic-2025)
CCBA_EQ = put('ccba_eq', 3.4); CCBA_KO = put('ccba_ko_pct', 66.52)
CCBA_VAL = put('ccba_val', CCBA_EQ*CCBA_KO/100)
put('ccba_proceeds', CCBA_EQ*41.52/100); put('ccba_retained', CCBA_EQ*25/100)
# CCBA sale del consolidado a fin de 2026: ingresos y EBIT 2024 = pro forma CCHBC+CCBA (EUR 14.1 / 1.4 mil millones)
# menos CCHBC solo (EUR 10.8 / 1.19), a 1.082 US$/EUR (promedio 2024). Aproximación: cifras redondeadas.
EURUSD24 = 1.082
CCBA_REV = put('ccba_rev', (14.1-10.8)*EURUSD24)
CCBA_EBIT = put('ccba_ebit', (1.4-1.192)*EURUSD24)
CCBA_FCF = put('ccba_fcf', CCBA_EBIT*(1-0.25))    # D&A ~ capex; impuesto 25% (supuesto)
put('ccba_rev_pct', CCBA_REV/REV[2025]*100)
NONOP = put('nonop', STK_AT + UNLISTED + CCBA_VAL)   # activos no operativos que se suman al valor de empresa
put('nonop_ps', NONOP/SH_DIL*1000)

# ---------------- Costo de capital ----------------
BETAS = {'PEP': 0.36, 'KDP': 0.41, 'MNST': 0.51}   # stockanalysis, 5 años mensual
BETA_KO = put('beta_ko', 0.34)
beta_med = put('beta_med', st.median(BETAS.values()))
beta_adj = put('beta_adj', 0.67*beta_med + 0.33)
beta_adj_own = put('beta_adj_own', 0.67*BETA_KO + 0.33)
KE_FLOOR = put('ke_floor', RF + 2.5)
KE = put('ke', max(RF + beta_adj*ERP, KE_FLOOR))
KE_OWN = put('ke_own', max(RF + beta_adj_own*ERP, KE_FLOOR))
KD_PRE = put('kd_pre', RF + 0.60)    # supuesto: bono largo A+/A1 ~60 pb sobre el Treasury
KD = put('kd', KD_PRE*(1-t))
E = PRICE*SH_OUT/1000
WD = put('wd', DEBT/(DEBT+E)*100)
def wacc(ke): return (1-WD/100)*ke + WD/100*KD
WACC = put('wacc', wacc(KE)); WACC_OWN = put('wacc_own', wacc(KE_OWN))

# ---------------- Margen de caja anclado en el OCF real ----------------
# FCF sin apalancar y sin dividendos de participadas = OCF ajustado + intereses netos x (1-t) - capex - dividendos
# recibidos de participadas (las participaciones se suman aparte, a valor de mercado: no se cuentan dos veces).
F25 = put('f25', OCF_ADJ[2025] + NETINT25*(1-t) - CAPEX[2025] - EQDIV25)
F26 = put('f26', OCF_G26 + NETINT26*(1-t) - CAPEX_G26 - EQDIV25)
put('f25_m', F25/REV[2025]*100); put('f26_m', F26/REV_C26*100)
M_CONS = put('m_cons', (F25+F26)/(REV[2025]+REV_C26)*100)
M_BASE = put('m_base', (F25+F26-2*CCBA_FCF)/(REV[2025]+REV_C26-2*CCBA_REV)*100)
put('m_ccba_effect', M_BASE - M_CONS)
REV0 = put('rev0', REV_C26 - CCBA_REV)          # base 2026E sin CCBA
put('m_1h26', (OCF_1H26 + (0.744-0.420)*(1-t) - 0.684 - EQDIV_1H26)/25.852*100)
put('m_ttm', (M['ttm_ocf_adj'] + (NETINT25 - (0.832-0.368) + (0.744-0.420))*(1-t) - (CAPEX[2025]-0.751+0.684)
              - (EQDIV25 - (0.912-0.387) + EQDIV_1H26))/M['ttm_rev']*100)

# ---------------- DCF (15%) ----------------
YEARS = [2027, 2028, 2029, 2030, 2031]
SC = {
 'bear': dict(dw=+0.5, g=2.0, vol=[0.0]*5,  pm=[1.5, 1.75, 2.0, 2.0, 2.0], dm=[-1.0]*5),
 'base': dict(dw=0.0,  g=2.5, vol=[M['ucv_8q']]*5, pm=[2.0, 2.25, 2.5, 2.5, 2.5], dm=[0.0]*5),
 'bull': dict(dw=-0.5, g=3.0, vol=[2.5]*5,  pm=[2.5, 2.75, 3.0, 3.0, 3.0], dm=[0.25, 0.5, 0.75, 1.0, 1.25]),
}
STUB = 0.25   # oct-dic 2026
def paths(sc, dvol=0.0):
    rev = REV0; rows = []
    for i in range(5):
        g = sc['vol'][i] + dvol + sc['pm'][i]
        rev *= 1 + g/100
        m = M_BASE + sc['dm'][i]
        rows.append(dict(y=YEARS[i], g=g, rev=rev, m=m, fcf=rev*m/100))
    return rows
def dcf(sc, w=None, g=None, dvol=0.0, m_shift=0.0, detail=False, nonop=None):
    w = (WACC + sc['dw']) if w is None else w
    g = sc['g'] if g is None else g
    rows = paths(sc, dvol)
    if m_shift:
        for r in rows: r['m'] += m_shift; r['fcf'] = r['rev']*r['m']/100
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
    if k == 'base':
        M['dcf_base_rows'] = [dict(y=x['y'], g=x['g'], rev=x['rev'], m=x['m'], fcf=x['fcf'], pv=x['pv']) for x in r['rows']]
        M['dcf_base_stub'] = r['stub']
DCF = M['dcf_base']
put('dcf_core_ps', (M['dcf_base_ev'] - NETDEBT - NCI)/SH_DIL*1000)
put('dcf_pw', 0.25*M['dcf_bear'] + 0.45*DCF + 0.30*M['dcf_bull'])
put('dcf_avg', (M['dcf_bear'] + DCF + M['dcf_bull'])/3)
put('dcf_gap', (DCF/PRICE-1)*100)
put('dcf_bear_gap', (M['dcf_bear']/PRICE-1)*100); put('dcf_bull_gap', (M['dcf_bull']/PRICE-1)*100)
put('dcf_base_ownbeta', dcf(SC['base'], w=WACC_OWN)); put('ownbeta_diff', M['dcf_base_ownbeta'] - DCF)
put('dcf_m_cons', dcf(SC['base'], m_shift=M_CONS-M_BASE))
put('dcf_m_f26', dcf(SC['base'], m_shift=M['f26_m']-M_BASE))
put('dcf_m_ttm', dcf(SC['base'], m_shift=M['m_ttm']-M_BASE))
put('dcf_m_1h26', dcf(SC['base'], m_shift=M['m_1h26']-M_BASE))
put('dcf_no_tax_gain', dcf(SC['base'], nonop=STK_NOW + UNLISTED + CCBA_VAL))
put('tax_gain_effect', DCF - M['dcf_no_tax_gain'])
# alternativa: dividendos de participadas dentro del FCF (en lugar de sumarlas a mercado)
put('eqdiv_m', EQDIV25/REV[2025]*100)
# (el margen sube en los dividendos recibidos sobre la misma base de ventas sin CCBA; se suma solo CCBA)
put('eqdiv_m_base', 2*EQDIV25/(REV[2025]+REV_C26-2*CCBA_REV)*100)
put('dcf_eqdiv_alt', dcf(SC['base'], m_shift=M['eqdiv_m_base'], nonop=CCBA_VAL))
# compensación en acciones tratada como costo de caja (279 millones en 2025)
put('sbc25', 0.279)
put('dcf_sbc', dcf(SC['base'], m_shift=-0.279/REV[2025]*100)); put('sbc_effect', M['dcf_sbc'] - DCF)
# volumen -2/0/+2 puntos vs Base (cinco años explícitos)
put('dcf_vol_m2', dcf(SC['base'], dvol=-2.0)); put('dcf_vol_p2', dcf(SC['base'], dvol=+2.0))
put('dcf_vol_zero', dcf(SC['base'], dvol=-M['ucv_8q']))
put('dcf_vol_m2_pct', (M['dcf_vol_m2']/DCF-1)*100); put('dcf_vol_p2_pct', (M['dcf_vol_p2']/DCF-1)*100)
put('vol_m2', M['ucv_8q']-2); put('vol_p2', M['ucv_8q']+2)
# Grilla WACC x g
WG = [WACC-1, WACC-0.5, WACC, WACC+0.5, WACC+1]; GG = [1.5, 2.0, 2.5, 3.0, 3.5]
M['grid_w'] = WG; M['grid_g'] = GG
M['grid'] = [[dcf(SC['base'], w=w, g=g) for g in GG] for w in WG]
assert abs(M['grid'][2][1+1] - DCF) < 1e-9
put('grid_up', (M['grid'][1][2]/DCF-1)*100); put('grid_dn', (M['grid'][3][2]/DCF-1)*100)
def solve(f, lo, hi, target, inc=True):
    for _ in range(200):
        mid = (lo+hi)/2
        if (f(mid) < target) == inc: lo = mid
        else: hi = mid
    return (lo+hi)/2
put('impl_wacc', solve(lambda w: dcf(SC['base'], w=w), 4.0, 12.0, PRICE, inc=False))
put('impl_g', solve(lambda g: dcf(SC['base'], g=g), 0.0, WACC-0.2, PRICE, inc=True))
put('impl_dvol', solve(lambda d: dcf(SC['base'], dvol=d), -10.0, 30.0, PRICE, inc=True))
put('impl_vol', M['ucv_8q'] + M['impl_dvol'])
put('impl_m', M_BASE + solve(lambda d: dcf(SC['base'], m_shift=d), -10, 30, PRICE, inc=True))
put('wacc_minus_impl', WACC - M['impl_wacc'])
put('ke_impl', (M['impl_wacc'] - WD/100*KD)/(1-WD/100))
# IRS: resultados extremos del litigio sobre el DCF Base (no entran al Base)
put('irs_lose_ps', -(M['irs_contingent'] + 0.9)/SH_DIL*1000)   # contingencia 2010-2025 + 1S26
PRETAX25 = put('pretax25', 15.998)
put('irs_etr_annual', M['irs_etr']/100*PRETAX25)                 # 3.8 pp sobre la utilidad antes de impuestos 2025
put('irs_lose_etr_ps', -M['irs_etr_annual']/((WACC-2.5)/100)/SH_DIL*1000)   # perpetuidad creciente al WACC - 2.5%
put('irs_lose_total_ps', M['irs_lose_ps'] + M['irs_lose_etr_ps'])

# ---------------- Comparables (25%) ----------------
# P/E sobre EPS de los próximos 12 meses (oct-2026 a sep-2027); precios 29-sep-2026; EV/EBITDA de stockanalysis.
PEERS = {
 'PEP':  dict(name='PepsiCo', grp='bebidas', px=128.69, e1=8.56, e2=8.95, e3=9.39, fy='dic', evx=11.55, beta=0.36, dy=4.60, fcfy=5.28, org='+2.4% (2T26)', vol=2.0, vol_t='+2% bebidas; +3% alimentos'),
 'KDP':  dict(name='Keurig Dr Pepper', grp='bebidas', px=31.03, e1=2.30, e2=2.52, e3=2.77, fy='dic', evx=15.44, beta=0.41, dy=2.97, fcfy=4.67, org='+7.3% sin JDE Peet\'s (2T26)', vol=3.1, vol_t='+3.1% (volumen/mezcla)'),
 'MNST': dict(name='Monster Beverage', grp='bebidas', px=41.74, e1=1.11, e2=1.26, e3=1.51, fy='dic', evx=26.74, beta=0.51, dy=0.0, fcfy=2.57, org='+17.9% a moneda constante (2T26)', vol=None, vol_t='n. c.'),
 'PG':   dict(name='Procter & Gamble', grp='staples', px=148.32, e1=6.99, e2=7.42, e3=7.85, fy='jun', evx=14.93, beta=0.38, dy=2.94, fcfy=4.40, org='0% (4T FY26)', vol=0.0, vol_t='0%'),
 'CL':   dict(name='Colgate-Palmolive', grp='staples', px=86.46, e1=3.87, e2=4.07, e3=4.40, fy='dic', evx=15.12, beta=0.32, dy=2.45, fcfy=5.60, org='+2.4% (2T26)', vol=0.9, vol_t='+0.9%'),
 'PM':   dict(name='Philip Morris International', grp='staples', px=193.90, e1=8.44, e2=9.22, e3=10.12, fy='dic', evx=19.17, beta=0.40, dy=3.30, fcfy=4.21, org='+7.6% (2T26)', vol=2.5, vol_t='+2.5% (envíos)'),
}
for k, p in PEERS.items():
    if p['fy'] == 'dic': p['ntm'] = 0.25*p['e1'] + 0.75*p['e2']; p['g2'] = ((p['e3']/p['e1'])**0.5-1)*100
    else: p['ntm'] = 0.75*p['e1'] + 0.25*p['e2']; p['g2'] = ((p['e3']/p['e1'])**0.5-1)*100   # PG: FY jun-2027..jun-2029
    p['pe'] = p['px']/p['ntm']
M['peers'] = PEERS
pes = sorted(p['pe'] for p in PEERS.values())
PE_MED = put('peer_pe_med', st.median(pes)); put('peer_pe_mean', st.mean(pes))
put('peer_pe_min', pes[0]); put('peer_pe_max', pes[-1])
put('peer_pe_q3', st.quantiles(pes, n=4, method='inclusive')[2])
put('peer_pe_q1', st.quantiles(pes, n=4, method='inclusive')[0])
put('bev_pe_med', st.median(p['pe'] for p in PEERS.values() if p['grp'] == 'bebidas'))
put('stp_pe_med', st.median(p['pe'] for p in PEERS.values() if p['grp'] == 'staples'))
evs = sorted(p['evx'] for p in PEERS.values())
EV_MED = put('peer_ev_med', st.median(evs)); put('peer_ev_min', evs[0]); put('peer_ev_max', evs[-1])
put('peer_ev_q3', st.quantiles(evs, n=4, method='inclusive')[2])
put('ko_evx_sa', 23.62)
put('ko_ev_ebitda', (MKT_CAP + NETDEBT_L + NCI - STK_NOW - UNLISTED - CCBA_VAL)/(EBITDA_TTM - CCBA_EBIT))
put('ko_pe_vs_med', (M['pe_ntm_now']/PE_MED-1)*100)
def reg(xs, ys):
    mx = st.mean(xs); my = st.mean(ys)
    sxy = sum((x-mx)*(y-my) for x, y in zip(xs, ys)); sxx = sum((x-mx)**2 for x in xs); syy = sum((y-my)**2 for y in ys)
    b = sxy/sxx; return dict(slope=b, icpt=my-b*mx, r2=sxy**2/(sxx*syy), n=len(xs))
def reg_ex(items, key):
    mx = st.mean(p[key] for _, p in items)
    ext = max(items, key=lambda kp: abs(kp[1][key]-mx))
    rest = [kp for kp in items if kp[0] != ext[0]]
    r = reg([p[key] for _, p in rest], [p['pe'] for _, p in rest]); r['dropped'] = ext[0]; return r
allp = list(PEERS.items())
M['reg_g'] = reg([p['g2'] for _, p in allp], [p['pe'] for _, p in allp])
M['reg_g_ex'] = reg_ex(allp, 'g2')
volp = [(k, p) for k, p in allp if p['vol'] is not None]
M['reg_v'] = reg([p['vol'] for _, p in volp], [p['pe'] for _, p in volp])
M['reg_v_ex'] = reg_ex(volp, 'vol')
R2_MIN = put('r2_min', 0.5)
reg_ok = all(M[k]['r2'] >= R2_MIN and M[k]['slope'] > 0 for k in ('reg_g', 'reg_g_ex')) or \
         all(M[k]['r2'] >= R2_MIN and M[k]['slope'] > 0 for k in ('reg_v', 'reg_v_ex'))
M['reg_ok'] = reg_ok
put('reg_g_ko_pe', M['reg_g']['icpt'] + M['reg_g']['slope']*M['ko_g2'])
put('reg_v_ko_pe', M['reg_v']['icpt'] + M['reg_v']['slope']*M['ucv_4q'])
assert not reg_ok, 'si la regresión sostiene un ajuste, hay que reescribir el Método 2'
# Método elegido: mediana de los seis pares (sin ajuste por calidad), aplicada a EPS y EBITDA de KO
EBITDA_KO = put('ebitda_ko', EBITDA_TTM - CCBA_EBIT)
COMP_PE = put('comp_pe', PE_MED*NTM)
def ev_to_ps(mult): return (mult*EBITDA_KO - NETDEBT_L - NCI + NONOP)/SH_DIL*1000
COMP_EV = put('comp_ev', ev_to_ps(EV_MED))
COMP = put('comp', (COMP_PE + COMP_EV)/2)
put('comp_low', (M['peer_pe_min']*NTM + ev_to_ps(M['peer_ev_min']))/2)
put('comp_high', (M['peer_pe_max']*NTM + ev_to_ps(M['peer_ev_max']))/2)
put('comp_q3', (M['peer_pe_q3']*NTM + ev_to_ps(M['peer_ev_q3']))/2)
put('comp_bev', M['bev_pe_med']*NTM)
put('comp_gap', (COMP/PRICE-1)*100)
put('comp_ev_pe_diff', COMP_PE - COMP_EV)
put('pe_needed', PRICE/NTM)

# ---------------- Reversión (35%) ----------------
d = json.load(open('yh/KO.mo.json'))['chart']['result'][0]
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
    covid = (2020, 1) in nx   # el EPS de los 12 meses siguientes incluye el 2T 2020 (pandemia): P/E ex post inflado
    win.append(dict(date=f'{ym[0]}-{ym[1]:02d}', y=ym[0], price=closes[ym], ntm=ntm, pe=closes[ym]/ntm, excl=ym[0] in EXCL, covid=covid))
M['rev_window'] = win
clean = [w for w in win if not w['excl'] and not w['covid']]
nocovid = [w for w in win if not w['covid']]
put('rev_n', len(clean)); put('rev_n_all', len(win)); put('rev_n_excl', len(win)-len(clean))
put('rev_n_covid', sum(1 for w in win if w['covid'])); put('rev_n_nocovid', len(nocovid))
put('rev_pe_covid_avg', st.mean(w['pe'] for w in win if w['covid']))
put('rev_pe_avg_withcovid', st.mean(w['pe'] for w in win if not w['excl']))
PE_CLEAN = put('rev_pe_avg', st.mean(w['pe'] for w in clean))
PE_ALL = put('rev_pe_avg_all', st.mean(w['pe'] for w in nocovid))   # todos los años, sin las 4 observaciones de la pandemia
put('rev_pe_avg_raw', st.mean(w['pe'] for w in win))
put('rev_pe_min', min(w['pe'] for w in clean)); put('rev_pe_max', max(w['pe'] for w in clean))
put('rev_pe_excl_avg', st.mean(w['pe'] for w in win if w['excl']))
clean25 = [w for w in clean if w['y'] != 2025]
put('rev_pe_avg_ex25', st.mean(w['pe'] for w in clean25))
M['rev_by_year'] = {}
for y in range(2016, 2027):
    ws = [w for w in win if w['y'] == y]
    M['rev_by_year'][str(y)] = dict(avg=st.mean(w['pe'] for w in ws), lo=min(w['pe'] for w in ws), hi=max(w['pe'] for w in ws), excl=y in EXCL, n=len(ws))
    wc = [w for w in ws if not w['covid']]
    M['rev_by_year'][str(y)]['avg_nc'] = st.mean(w['pe'] for w in wc) if wc else None
R1 = put('rev1', PE_CLEAN*NTM)
put('rev1_all', PE_ALL*NTM); put('rev1_ex25', M['rev_pe_avg_ex25']*NTM)
put('rev_excl_effect', R1 - M['rev1_all'])
put('rev1_withcovid', M['rev_pe_avg_withcovid']*NTM); put('covid_effect', R1 - M['rev1_withcovid'])
# Lectura 2: P/E relativo al S&P 500 (promedio de los 42 cierres de KO / promedio de diez años del S&P de FactSet)
REL = put('rel_avg', PE_ALL/SPX_PE10)
REL_NOW = put('rel_now', M['pe_ntm_now']/SPX_PE)
R2 = put('rev2', REL*SPX_PE*NTM)
put('rel_pe', REL*SPX_PE)
put('spx_vs_avg', (SPX_PE/SPX_PE10-1)*100); put('ko_vs_avg', (M['pe_ntm_now']/PE_ALL-1)*100)
put('ko_vs_clean', (M['pe_ntm_now']/PE_CLEAN-1)*100)
REVV = put('rev', (R1 + R2)/2)
put('rev_low', M['rev_pe_min']*NTM); put('rev_high', M['rev_pe_max']*NTM)
put('rev_gap', (REVV/PRICE-1)*100)
put('rel_min', min(w['pe'] for w in nocovid)/SPX_PE10); put('rel_max', max(w['pe'] for w in nocovid)/SPX_PE10)
assert M['rel_now'] > M['rel_max'], 'el texto dice que el relativo actual supera el rango'
put('rev2_withcovid', M['rev_pe_avg_raw']/SPX_PE10*SPX_PE*NTM)

# ---------------- Consenso (25%) ----------------
CONS = put('cons', 94.70); put('cons_med', 96.0); put('cons_low', 75.0); put('cons_high', 104.0); put('cons_n', 24)
put('cons_sb', 12); put('cons_b', 7); put('cons_h', 4); put('cons_s', 1); put('cons_ss', 0)
put('cons_gap', (CONS/PRICE-1)*100)

# ---------------- Blend ----------------
W = {'dcf': 0.15, 'comp': 0.25, 'rev': 0.35, 'cons': 0.25}
V = {'dcf': DCF, 'comp': COMP, 'rev': REVV, 'cons': CONS}
BLEND = put('blend', sum(W[k]*V[k] for k in W))
put('blend_gap', (BLEND/PRICE-1)*100)
for k in W: put(f'contrib_{k}', W[k]*V[k])
put('indep', (W['dcf']*V['dcf'] + W['comp']*V['comp'])/(W['dcf']+W['comp']))
put('anch', (W['rev']*V['rev'] + W['cons']*V['cons'])/(W['rev']+W['cons']))
put('indep_gap', (M['indep']/PRICE-1)*100); put('anch_gap', (M['anch']/PRICE-1)*100)
for k in ('dcf', 'comp', 'rev', 'cons'): put(f'{k}_gap_', (V[k]/PRICE-1)*100)
def blend_with(**kw):
    v = dict(V); v.update(kw); return sum(W[k]*v[k] for k in W)
put('blend_rev_all', blend_with(rev=(M['rev1_all']+R2)/2))
put('rev_withcovid', (M['rev1_withcovid'] + M['rev2_withcovid'])/2); put('blend_withcovid', blend_with(rev=M['rev_withcovid']))
put('blend_ownbeta', blend_with(dcf=M['dcf_base_ownbeta']))
# litigio IRS: afecta al DCF y a la mitad EV/EBITDA de los comparables (el P/E se aplica sobre EPS, que no lo incluye)
put('blend_irs_win', BLEND + (0.15 + 0.25*0.5)*M['irs_win_ps'])
put('blend_irs_lose', BLEND + (0.15 + 0.25*0.5)*M['irs_lose_total_ps'])
put('blend_vs_cons', (BLEND/CONS-1)*100)

# ---------------- Series para gráficos y derivados de texto ----------------
M['js_pe_labels'] = json.dumps([(w['date'][:4] if w['date'][5:] == '03' else '') for w in win])
M['js_pe_vals'] = json.dumps([round(w['pe'], 2) for w in win])
M['js_pe_avg'] = json.dumps([round(PE_CLEAN, 2)]*len(win))
M['js_q'] = json.dumps([q[:2] + ' ' + q[2:] for q in Q])
for key, idx in (('conc', 0), ('pm', 1), ('org', 5), ('ucv', 6)):
    M[f'js_{key}'] = json.dumps([ORG[q][idx] for q in Q])
M['js_ann_y'] = json.dumps([str(y) for y in ANN]); M['js_ann_org'] = json.dumps([v[0] for v in ANN.values()])
M['js_ann_ucv'] = json.dumps([v[1] for v in ANN.values()])
SPARK = [closes[(2026, m)] for m in range(3, 9)] + [PRICE]
M['spark'] = [round(x, 2) for x in SPARK]
put('px_dec25', closes[(2025, 12)]); put('ret_ytd', (PRICE/closes[(2025, 12)]-1)*100)
put('hi52', max(c for (y, m), c in closes.items() if (y, m) >= (2025, 10))); put('lo52', min(c for (y, m), c in closes.items() if (y, m) >= (2025, 10)))
# segmentos 2025 (comparables) y resultado operativo reportado
M['seg'] = {'emea': (11.548, 4.298), 'latam': (6.379, 3.742), 'na': (19.599, 5.070), 'apac': (5.666, 2.042), 'bi': (5.735, 0.426)}
put('us_rev_pct', (8.956+10.171)/REV[2025]*100); put('intl_rev_pct', 100 - M['us_rev_pct'])
put('conc_rev_pct', 59); put('conc_vol_pct', 85)
put('eqsales_pct', 19.044/REV[2025]*100)
put('ucv_bn', 33.8)
put('glp1_ms', 3.0); put('ssd_pct', 69)
put('dcf_base_rev27', M['dcf_base_rows'][0]['rev']); put('dcf_base_rev31', M['dcf_base_rows'][-1]['rev'])
put('dcf_base_fcf27', M['dcf_base_rows'][0]['fcf'])
put('pe_c28', PRICE/C28)
put('stk_gain', STK_NOW - STK_DEC); put('stk_gain_pct', (STK_NOW/STK_DEC-1)*100)
put('mnst_share_stk', M['stakes']['MNST']['now']/STK_NOW*100)
put('nonop_pct_price', M['nonop_ps']/PRICE*100)
put('eqinc_pct_ni', EQINC25/NI_C25*100)

# GLP-1: exposición y arrastre estimado sobre el volumen (supuestos declarados en la Sección 10)
ZERO_SHARE = put('zero_share', 15.0)    # "mid-teens" % del volumen de gaseosas (Quincey, feb-2026): se toma 15%
put('sugar_ssd_pct', M['ssd_pct']*(1-ZERO_SHARE/100))
put('na_rev_pct', 40.8)
put('glp1_drag_pa', M['glp1_ms']/9*M['na_rev_pct']/100*M['sugar_ssd_pct']/100)   # 3% en 9 años (2026-2035) sobre NA
put('dcf_glp1', dcf(SC['base'], dvol=-M['glp1_drag_pa']))
put('glp1_effect', M['dcf_glp1'] - DCF)
put('ccba_ps', CCBA_VAL/SH_DIL*1000); put('unlisted_ps', UNLISTED/SH_DIL*1000)
put('netdebt_ps', NETDEBT/SH_DIL*1000); put('nci_ps', NCI/SH_DIL*1000)
put('ev_ps', M['dcf_base_ev']/SH_DIL*1000)
put('fcf_base_sum5', sum(r['fcf'] for r in M['dcf_base_rows']))
put('stk_tax', STK_NOW - STK_AT)
put('rev_ex_ccba_growth27', M['dcf_base_org27'])

# ---------------- Derivados para tablas y texto (todo lo que no es dato textual de una fuente) ----------------
BS = {'jul': dict(cash=12907+622+2842, dst=48+6494, dlt=37001, irs=6000+514, eqm=20782, gw=15456+12500, hfs=5438-2442, eq=36150, ta=107922),
      'dec': dict(cash=10270+3602+1934, dst=1551+1822, dlt=42119, irs=6000+385, eqm=20235, gw=15491+12531, hfs=5342-2570, eq=32169, ta=104816)}
for v in BS.values(): v['nd'] = v['dst'] + v['dlt'] - v['cash']
M['bs'] = BS
assert abs(BS['jul']['nd']/1000 - NETDEBT) < 1e-9
M['ocf_adj_m'] = {str(y): OCF_ADJ[y]*1000 for y in OCF}; M['fcf_adj_m'] = {str(y): (OCF_ADJ[y]-CAPEX[y])*1000 for y in OCF}
put('om_gaap_1h26', 9.031/25.852*100); put('om_gaap_1h25', 7.939/23.664*100)
put('eps_c_1h26', EPS[2026][0]+EPS[2026][1]); put('eps_c_1h25', EPS[2025][0]+EPS[2025][1])
put('bodyarmor_imp', 760+960)
put('pm_2024_avg', st.mean(ORG[q][1] for q in INFL)); put('org_2024_avg', st.mean(ORG[q][5] for q in INFL))
put('cons_buy', M['cons_sb'] + M['cons_b'])
put('irs_ratio', -M['irs_lose_total_ps']/M['irs_win_ps'])
put('impl_vol_x', M['impl_vol']/M['ucv_8q'])
put('ccba_fcf_m', CCBA_FCF/CCBA_REV*100)
put('ke_minus_floor', KE - KE_FLOOR)
put('div_minus_rf', M['div_yield'] - RF); put('fcf_minus_rf', M['fcf_yield'] - RF)
put('rf_minus_div', RF - M['div_yield']); put('rf_minus_fcf', RF - M['fcf_yield'])
put('da_ebitda_ko', TTM_DA/EBITDA_TTM*100)
put('inst_pct', 67.25)

# valores absolutos para la prosa (evitan dobles negativos del tipo "cayeron −18%")
put('rev_drop_1618_abs', -M['rev_drop_1618']); put('irs_lose_abs', -M['irs_lose_total_ps'])
put('covid_effect_abs', M['rev1_withcovid'] - M['rev1']); put('grid_dn_abs', -M['grid_dn']); put('glp1_effect_abs', -M['glp1_effect']); put('sbc_effect_abs', -M['sbc_effect'])

json.dump(M, open('model.json', 'w'), indent=1, default=float)
if __name__ == '__main__':
    for k, v in M.items():
        if isinstance(v, (int, float)) and not isinstance(v, bool): print(f'{k:24s} {v:,.4f}')
    print('peers:'); [print(' ', k, round(p['pe'], 2), round(p['g2'], 1), p['vol'], p['evx']) for k, p in PEERS.items()]
    for k in ('reg_g', 'reg_g_ex', 'reg_v', 'reg_v_ex'): print(k, {a: (round(b, 3) if isinstance(b, float) else b) for a, b in M[k].items()})
    print('stakes', {k: (round(s['now'], 2), round(s['chg'], 1), round(s['aftertax'], 2)) for k, s in M['stakes'].items()})
    for w in win: print(w['date'], round(w['price'], 2), round(w['ntm'], 3), round(w['pe'], 2), w['excl'])
    print(M['dcf_base_rows'])
