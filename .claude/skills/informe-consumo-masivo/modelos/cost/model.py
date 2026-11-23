# Modelo de valuación COST (Costco Wholesale) — todos los números derivados del informe salen de acá.
# Marco: informe-consumo-masivo, bloque de RETAIL con foco en el MODELO DE MEMBRESÍA (cuotas = socios × cuota × renovación;
# mercadería = ventas × margen de mercadería). Año fiscal de 52/53 semanas que cierra el domingo más cercano al 31 de agosto:
# FY2026 = 1-sep-2025 a 30-ago-2026; FY2027 = 31-ago-2026 a 29-ago-2027.
# Fuentes: SEC EDGAR CIK 0000909832 — 10-K FY2017-FY2026 (el del FY2026 presentado el 7-oct-2026), comunicados 8-K ítem 2.02
# del 1T FY2017 al 4T FY2026 (anexos 99.1 y 99.2), 8-K del 14-oct-2026 (dividendo) y del 10-nov-2026 (dividendo especial de $30),
# DEF 14A 2025, XBRL companyfacts (data/annual.json). Ventas mensuales de septiembre y octubre de 2026: comunicados de Costco
# (GlobeNewswire, 7-oct y 4-nov-2026; data/monthly/*.txt). Mercado, consenso y pares: bloque compartido
# .claude/skills/_compartido/defensivos_nov26.json (cierre del viernes 20-nov-2026) y modelos/wmt/model.json (pares de retail).
import json, datetime, os, statistics as st
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
SH = json.load(open(ROOT/'.claude'/'skills'/'_compartido'/'defensivos_nov26.json', encoding='utf-8'))
WM = json.load(open(HERE.parent/'wmt'/'model.json', encoding='utf-8'))
M = {}
def put(k, v): M[k] = v; return v
ALT = os.environ.get('COST_PRICE_OVERRIDE')        # verify.py: corre el modelo con otro precio (anti-circularidad)

# ---------------- Mercado (cierre 20-nov-2026, bloque compartido) ----------------
PRICE = put('price', float(ALT) if ALT else SH['cost_precio']['cierre_20nov'])
assert ALT or PRICE == 1102.15
put('hi52', SH['cost_precio']['max_52s']); put('lo52', SH['cost_precio']['min_52s'])
RF = put('rf', SH['mercado']['treasury_10y']['valor_pct'])
ERP = put('erp', SH['mercado']['prima_riesgo']['erp_casa_pct']); put('erp_dam', SH['mercado']['prima_riesgo']['erp_damodaran_pct'])
SH_OUT = put('sh_out', 443.266)        # acciones en circulación al 30-ago-2026 (balance del comunicado del 4T), millones
SH_DIL = put('sh_dil', 444.364)        # diluidas promedio del 4T FY2026 (comunicado), millones
MKT_CAP = put('mkt_cap', PRICE*SH_OUT/1000)   # US$ miles de millones
put('pct_from_hi', (PRICE/M['hi52']-1)*100)

# ---------------- Consenso de EPS (S&P Global vía stockanalysis, bloque compartido y modelos/wmt) ----------------
CS = SH['consenso_tres']['tickers']['COST']
C27, C28 = put('c27', CS['eps_ajustado_fy_actual']), put('c28', CS['eps_ajustado_fy_siguiente'])
put('c26_real', CS['eps_fy_anterior_real'])
Q1C, Q2C = put('q1_27c', WM['peers']['COST']['q'][0]), put('q2_27c', WM['peers']['COST']['q'][1])
put('sales27c', CS['ventas_fy_actual']/1e9); put('sales28c', CS['ventas_fy_siguiente']/1e9)
# EPS de los próximos 12 meses = fracción de cada año fiscal (regla de la skill): al 20-nov-2026 pasaron 82 de los 364 días del FY2027
PHI = put('phi', 82/364)
NTM = put('eps_ntm', (1-PHI)*C27 + PHI*C28)
PE_NOW = put('pe_ntm_now', PRICE/NTM)
put('pe_c27', PRICE/C27); put('pe_c28', PRICE/C28); put('eps_g28', (C28/C27-1)*100); put('eps_g27', (C27/20.76-1)*100)
put('pe_wmtrule', PRICE/C27)          # con la regla del informe de WMT (año fiscal en curso) — referencia

# ---------------- EPS diluido trimestral (comunicados 8-K 2.02; Costco reporta GAAP, sin EPS "ajustado") ----------------
EPS = {2016: [1.09, 1.24, 1.24, 1.77], 2017: [1.24, 1.17, 1.59, 2.08], 2018: [1.45, 1.59, 1.70, 2.36],
       2019: [1.73, 2.01, 2.05, 2.47], 2020: [1.90, 2.10, 1.89, 3.13], 2021: [2.62, 2.14, 2.75, 3.76],
       2022: [2.98, 2.92, 3.04, 4.20], 2023: [3.07, 3.30, 2.93, 4.86], 2024: [3.58, 3.92, 3.78, 5.29],
       2025: [4.04, 4.02, 4.28, 5.87], 2026: [4.50, 4.58, 4.93, 6.75]}
FY_EPS = {2016: 5.33, 2017: 6.08, 2018: 7.09, 2019: 8.26, 2020: 9.02, 2021: 11.27, 2022: 13.14, 2023: 14.16, 2024: 16.56,
          2025: 18.21, 2026: 20.76}
for y, v in FY_EPS.items():
    assert abs(sum(EPS[y]) - v) < 0.025, (y, sum(EPS[y]), v)
# FY2027: 1T y 2T de consenso; 3T+4T = año − 1T − 2T, repartido con la estacionalidad real del FY2026 (4.93 : 6.75)
rest = C27 - Q1C - Q2C
EPS[2027] = [Q1C, Q2C, rest*4.93/(4.93+6.75), rest*6.75/(4.93+6.75)]
M['eps_fy'] = {str(y): v for y, v in FY_EPS.items()}; M['eps_fy']['2027'] = C27; M['eps_fy']['2028'] = C28
put('eps_cagr_10', ((FY_EPS[2026]/FY_EPS[2016])**(1/10)-1)*100)
put('eps_cagr_5', ((FY_EPS[2026]/FY_EPS[2021])**(1/5)-1)*100)
put('eps_q4_26', 6.75); put('eps_q4_25', 5.87); put('eps_q4_g', (6.75/5.87-1)*100)
put('ieepa_eps_q4', 0.15); put('eps_q4_g_ex', ((6.75-0.15)/5.87-1)*100)
put('eps_g26', (20.76/18.21-1)*100); put('eps_g26_ex', ((20.76-0.15)/18.21-1)*100)

# ---------------- Serie anual (SEC XBRL, data/annual.json) + cuotas de los 10-K ----------------
A = json.load(open(HERE/'data'/'annual.json'))
def a(tag, y): return A[tag][str(y)]/1e9
YRS = list(range(2016, 2027))
REV = {y: a('NetSales', y) for y in YRS}                           # el tag de ingresos de contratos = ingresos totales (incluye cuotas)
FEES = {2016: 2.646, 2017: 2.853, 2018: 3.142, 2019: 3.352, 2020: 3.541, 2021: 3.877, 2022: 4.224, 2023: 4.580, 2024: 4.828,
        2025: 5.323, 2026: 5.907}                                    # "Membership fees" de los 10-K (tabla de resultados)
NS = {y: REV[y] - FEES[y] for y in YRS}                              # ventas netas = ingresos totales − cuotas
assert abs(NS[2026] - 297.247) < 1e-6 and abs(NS[2025] - 269.912) < 1e-6 and abs(NS[2024] - 249.625) < 1e-6
COGS = {y: a('MerchCosts', y) for y in YRS}; SGA = {y: a('SGA', y) for y in YRS}; OI = {y: a('OI', y) for y in YRS}
NI = {y: a('NI', y) for y in YRS}; OCF = {y: a('OCF', y) for y in range(2017, 2027)}; CAPEX = {y: a('Capex', y) for y in YRS}
DA = {y: a('DA', y) for y in YRS}; INV = {y: a('Inventory', y) for y in range(2015, 2027)}; AP = {y: a('AP', y) for y in range(2015, 2027)}
DIVP = {y: a('Div', y) for y in YRS}; BUYB = {y: a('Buyback', y) for y in YRS}
OCF[2016] = 3.292                                                    # FY2016 (10-K FY2017, estado de flujos; el XBRL no lo trae como anual)
assert abs(OI[2026] - 11.685) < 1e-9 and abs(OCF[2026] - 15.817) < 1e-9
M['ann'] = {}
for y in YRS:
    M['ann'][str(y)] = dict(rev=REV[y], ns=NS[y], fees=FEES[y], oi=OI[y], gm=(NS[y]-COGS[y])/NS[y]*100, sga=SGA[y]/NS[y]*100,
                            om=OI[y]/REV[y]*100, fee_share=FEES[y]/OI[y]*100, merch_oi=OI[y]-FEES[y],
                            merch_m=(OI[y]-FEES[y])/NS[y]*100, turns=COGS[y]/((INV[y]+INV[y-1])/2), ap_inv=AP[y]/INV[y]*100,
                            ocf=OCF[y], capex=CAPEX[y], fcf=OCF[y]-CAPEX[y], ni=NI[y], div=DIVP[y], buyback=BUYB[y])
ANN = M['ann']
put('rev_cagr_10', ((REV[2026]/REV[2016])**(1/10)-1)*100); put('ns_cagr_10', ((NS[2026]/NS[2016])**(1/10)-1)*100)
put('fees_cagr_10', ((FEES[2026]/FEES[2016])**(1/10)-1)*100); put('oi_cagr_10', ((OI[2026]/OI[2016])**(1/10)-1)*100)
put('fees_g26', (FEES[2026]/FEES[2025]-1)*100); put('fees_g25', (FEES[2025]/FEES[2024]-1)*100)
put('ns_g26', (NS[2026]/NS[2025]-1)*100); put('ni_g26', (NI[2026]/NI[2025]-1)*100); put('oi_g26', (OI[2026]/OI[2025]-1)*100)
put('fee_share_26', ANN['2026']['fee_share']); put('fee_share_16', ANN['2016']['fee_share']); put('fee_share_21', ANN['2021']['fee_share'])
put('merch_oi_26', OI[2026]-FEES[2026]); put('merch_m_26', ANN['2026']['merch_m']); put('merch_m_16', ANN['2016']['merch_m'])
put('merch_m_21', ANN['2021']['merch_m'])
put('merch_dm_hist', (ANN['2026']['merch_m'] - ANN['2016']['merch_m'])/10*100)      # pb por año, 10 años
put('om_dm_hist', (ANN['2026']['om'] - ANN['2016']['om'])/10*100)                    # pb por año, margen operativo consolidado
put('merch_oi_cagr_10', (((OI[2026]-FEES[2026])/(OI[2016]-FEES[2016]))**(1/10)-1)*100)
put('gm_26', ANN['2026']['gm']); put('sga_26', ANN['2026']['sga']); put('om_26', ANN['2026']['om'])
put('gm_ex_gas_26', 11.22); put('sga_ex_gas_26', 9.26)                               # 10-K FY2026 (MD&A)
put('dio26', 365/ANN['2026']['turns']); put('dio16', 365/ANN['2016']['turns'])
put('ap_inv_26', ANN['2026']['ap_inv'])
put('gas_share', 11); put('digital_share', 11); put('exec_sales', 75.2)
put('gas_impact_ns', 3.501); put('fx_impact_ns', 1.332); put('gas_bps', 130); put('fx_bps', 49)
CAT = {'Alimentos y artículos de consumo': 116.788, 'No alimentos': 77.375, 'Alimentos frescos': 41.715,
       'Servicios del depósito y otros negocios': 61.369}                            # 10-K FY2026, nota 11
M['cat'] = CAT; assert abs(sum(CAT.values()) - NS[2026]) < 1e-6
for k, v in CAT.items(): pass
put('cat_food_pct', (CAT['Alimentos y artículos de consumo'] + CAT['Alimentos frescos'])/NS[2026]*100)
put('cat_anc_g', (61.369/51.170-1)*100); put('cat_core_g', ((116.788+77.375+41.715)/(109.564+71.190+37.988)-1)*100)

# ---------------- Segmentos (10-K FY2026, nota 11) ----------------
SEG = {'us': dict(name='Estados Unidos', rev=219.823, oi=7.647, rev25=200.046, oi25=6.878, da=2.082, capex=5.122, wh=647),
       'ca': dict(name='Canadá', rev=40.561, oi=2.107, rev25=36.923, oi25=1.849, da=0.219, capex=0.673, wh=115),
       'oi': dict(name='Otros internacionales', rev=42.770, oi=1.931, rev25=38.266, oi25=1.656, da=0.373, capex=0.640, wh=177)}
for k, s in SEG.items():
    s['m'] = s['oi']/s['rev']*100; s['g'] = (s['rev']/s['rev25']-1)*100; s['share'] = s['rev']/REV[2026]*100
    s['oi_share'] = s['oi']/OI[2026]*100; s['rev_wh'] = s['rev']/s['wh']*1000
M['seg'] = SEG
assert abs(sum(s['rev'] for s in SEG.values()) - REV[2026]) < 1e-6 and abs(sum(s['oi'] for s in SEG.values()) - OI[2026]) < 1e-6
put('intl_wh_share', (115+177)/939*100)

# ---------------- Membresía: socios, renovación, Executive (10-K y presentaciones trimestrales 99.2) ----------------
PAID = {2018: 51.6, 2019: 53.9, 2020: 58.1, 2021: 61.7, 2022: 65.8, 2023: 71.0, 2024: 76.2, 2025: 81.0, 2026: 84.1}   # millones, cierre de año
CARD = {2018: 94.3, 2019: 98.5, 2020: 105.5, 2021: 111.6, 2022: 118.9, 2023: 127.9, 2024: 136.8, 2025: 145.2, 2026: 150.4}
EXEC = {2024: 35.4, 2025: 38.7, 2026: 42.3}
REN_WW = {2017: 87.0, 2018: 88.0, 2019: 88.0, 2020: 88.0, 2021: 89.0, 2022: 90.0, 2023: 90.4, 2024: 90.5, 2025: 89.8, 2026: 89.8}
REN_US = {2017: 90.0, 2018: 90.0, 2019: 91.0, 2020: 91.0, 2021: 91.0, 2022: 93.0, 2023: 92.7, 2024: 92.9, 2025: 92.3, 2026: 92.3}
M['paid'] = PAID; M['card'] = CARD; M['ren_ww'] = REN_WW; M['ren_us'] = REN_US
FEE_PM = {y: FEES[y]/((PAID[y]+PAID[y-1])/2)*1000 for y in range(2019, 2027)}       # US$ por socio pago promedio
M['fee_pm'] = {str(y): v for y, v in FEE_PM.items()}
put('fee_pm_26', FEE_PM[2026]); put('fee_pm_19', FEE_PM[2019])
put('fee_pm_cagr', ((FEE_PM[2026]/FEE_PM[2019])**(1/7)-1)*100)
put('paid_g26', (PAID[2026]/PAID[2025]-1)*100); put('paid_cagr_8', ((PAID[2026]/PAID[2018])**(1/8)-1)*100)
put('exec_share_26', EXEC[2026]/PAID[2026]*100); put('exec_share_24', EXEC[2024]/PAID[2024]*100)
put('exec_g26', (EXEC[2026]/EXEC[2025]-1)*100)
put('adds_26', PAID[2026] - PAID[2025]*REN_WW[2026]/100)                             # altas brutas implícitas (aprox.)
put('lost_26', PAID[2025]*(1-REN_WW[2026]/100))
# Trimestres (presentaciones 99.2): 3T FY24 a 4T FY26
MQ = ['3T24', '4T24', '1T25', '2T25', '3T25', '4T25', '1T26', '2T26', '3T26', '4T26']
MEMQ = dict(ren_ww=[90.5, 90.5, 90.4, 90.5, 90.2, 89.8, 89.7, 89.7, 89.7, 89.8],
            ren_us=[93.0, 92.9, 92.8, 93.0, 92.7, 92.3, 92.2, 92.1, 92.2, 92.3],
            paid=[74.5, 76.2, 77.4, 78.4, 79.6, 81.0, 81.4, 82.1, 82.9, 84.1],
            paid_g=[7.8, 7.3, 7.6, 6.8, 6.8, 6.3, 5.2, 4.8, 4.1, 3.8],
            exec=[34.5, 35.4, 36.4, 36.9, 37.6, 38.7, 39.7, 40.4, 41.2, 42.3],
            exec_pen=[73.1, 73.5, 73.1, 73.8, 73.1, 74.2, 74.3, 75.8, 75.0, 75.6],
            fee_g=[7.6, 6.5, 7.8, 7.4, 10.4, 14.0, 14.0, 13.6, 10.7, 7.3],
            fee_g_fx=[8.0, 7.4, 7.8, 9.4, 11.4, 13.6, 14.0, 12.2, 9.9, 7.7])
M['mq'] = MQ; M['memq'] = MEMQ
# Cuotas trimestrales (comunicados): 1T FY24 a 4T FY26, US$ millones; 4T de 16 semanas (17 en el FY2023)
FEEQ = {2024: [1.082, 1.111, 1.123, 1.512], 2025: [1.166, 1.193, 1.240, 1.724], 2026: [1.329, 1.355, 1.373, 1.850]}
OIQ = {2024: [1.984, 2.062, 2.197, 3.042], 2025: [2.196, 2.316, 2.530, 3.341], 2026: [2.463, 2.606, 2.815, 3.801]}
NSQ = {2024: [56.717, 57.331, 57.392, 78.185], 2025: [60.985, 62.530, 61.965, 84.432], 2026: [65.978, 68.242, 69.154, 93.873]}
for y in FEEQ:
    assert abs(sum(FEEQ[y]) - FEES[y]) < 0.0015 and abs(sum(OIQ[y]) - OI[y]) < 0.0015 and abs(sum(NSQ[y]) - NS[y]) < 0.0015, y
M['feeq'] = FEEQ; M['oiq'] = OIQ
FQL = [f'{q}T{str(y)[2:]}' for y in (2024, 2025, 2026) for q in (1, 2, 3, 4)]
M['fee_share_q'] = [FEEQ[y][i]/OIQ[y][i]*100 for y in (2024, 2025, 2026) for i in range(4)]
put('fee_q4_g', (1.850/1.724-1)*100); put('fee_q3_g', (1.373/1.240-1)*100); put('fee_q1_26_g', (1.329/1.166-1)*100)
put('fee_share_q4_26', 1.850/3.801*100)
# Suba de cuota del 1-sep-2024 (8-K del 10-jul-2024 y 10-K): Gold Star/Business $60→$65, Executive $120→$130, tope de la
# recompensa 2% $1,000→$1,250; ~52 millones de membresías en EE.UU./Canadá, algo más de la mitad Executive. Aporte informado:
# ~40% del crecimiento de cuotas del FY2025 y ~30% del FY2026.
put('hike_members', 52.0); put('hike_share_25', 40); put('hike_share_26', 30)
put('hike_usd_25', (FEES[2025]-FEES[2024])*0.40); put('hike_usd_26', (FEES[2026]-FEES[2025])*0.30)
put('fees_g26_ex_hike', (FEES[2026]-FEES[2025])*0.70/FEES[2025]*100)
put('fees_g25_ex_hike', (FEES[2025]-FEES[2024])*0.60/FEES[2024]*100)
put('hike_runrate', 52.0*(0.5*5 + 0.5*10)/1000)          # cota: ~mitad Gold Star (+$5) y ~mitad Executive (+$10), US$ mil millones
put('def_fees_26', 3.006); put('def_fees_25', 2.854); put('rewards_liab_26', 3.037)
put('fee_hike_hist_years', 2024 - 2017); put('next_hike_est', 2024 + (2024 - 2017))

# ---------------- Ventas comparables sin nafta ni tipo de cambio (comunicados 99.1 y presentaciones 99.2) ----------------
# 3T FY24 a 4T FY26 (diez trimestres). Tráfico = frecuencia de compra (igual con y sin ajuste). Ticket ajustado publicado desde el
# 2T FY25; para 3T FY24-1T FY25 se deriva (1 + comparable ajustada) / (1 + tráfico) − 1 (en los trimestres publicados reproduce el dato).
QL = MQ
COMP = dict(us=[6.0, 6.3, 7.2, 8.6, 7.9, 6.0, 5.9, 6.4, 6.8, 7.2], ca=[7.4, 7.9, 6.7, 10.5, 7.8, 8.3, 9.0, 7.6, 6.2, 4.6],
            oi=[8.5, 9.3, 7.1, 10.3, 8.5, 7.2, 6.8, 7.1, 5.9, 6.2], tot=[6.5, 6.9, 7.1, 9.1, 8.0, 6.4, 6.4, 6.7, 6.6, 6.7])
TRX = dict(us=[5.5, 5.6, 4.9, 5.6, 5.5, 3.5, 2.6, 2.4, 1.8, 3.2], ca=[7.1, 7.7, 5.9, 5.8, 4.3, 5.3, 5.0, 4.3, 4.4, 2.5],
           oi=[7.4, 8.1, 5.3, 6.3, 4.8, 3.2, 3.1, 4.6, 2.9, 4.5], tot=[6.1, 6.4, 5.1, 5.7, 5.2, 3.7, 3.1, 3.1, 2.4, 3.3])
TKT_PUB = dict(us=[None, None, None, 2.8, 2.3, 2.4, 3.2, 3.9, 5.0, 3.9], tot=[None, None, None, 3.2, 2.7, 2.6, 3.2, 3.5, 4.2, 3.3])
TKT = {}
for r in ('us', 'ca', 'oi', 'tot'):
    TKT[r] = [round(((1+c/100)/(1+t/100)-1)*100, 1) for c, t in zip(COMP[r], TRX[r])]
for r in TKT_PUB:
    for i, v in enumerate(TKT_PUB[r]):
        if v is not None: assert abs(TKT[r][i] - v) <= 0.11, (r, i, TKT[r][i], v)
DIG = [20.7, 19.5, 13.2, 22.2, 15.7, 13.5, 20.5, 21.7, 20.8, 19.8]                # comparables digitales sin tipo de cambio
COMP_REP = [6.6, 5.4, 5.2, 6.8, 5.7, 5.7, 6.4, 7.4, 9.8, 9.4]                    # comparables totales reportadas (con nafta y FX)
M['ql'] = QL; M['comp'] = COMP; M['trx'] = TRX; M['tkt'] = TKT; M['dig'] = DIG; M['comp_rep'] = COMP_REP
def avg(xs): return sum(xs)/len(xs)
for r in ('us', 'ca', 'oi', 'tot'):
    put(f'{r}_comp_8q', avg(COMP[r][-8:])); put(f'{r}_trx_8q', avg(TRX[r][-8:])); put(f'{r}_tkt_8q', avg(TKT[r][-8:]))
    put(f'{r}_comp_4q', avg(COMP[r][-4:])); put(f'{r}_trx_4q', avg(TRX[r][-4:])); put(f'{r}_tkt_4q', avg(TKT[r][-4:]))
put('tot_trx_share_8q', M['tot_trx_8q']/M['tot_comp_8q']*100); put('tot_trx_share_4q', M['tot_trx_4q']/M['tot_comp_4q']*100)
put('tot_trx_first4', avg(TRX['tot'][2:6])); put('tot_tkt_first4', avg(TKT['tot'][2:6]))
put('dig_8q', avg(DIG[-8:]))
# Meses del 1T FY2027 (comunicados de ventas mensuales): septiembre (5 semanas al 4-oct) y octubre (4 semanas al 1-nov)
MON = dict(sep=dict(us=8.0, ca=4.9, oi=7.7, tot=7.6, rep=11.4, dig=19.1, ns=30.02, ns_py=26.58),
           oct=dict(us=8.1, ca=3.5, oi=6.9, tot=7.3, rep=11.1, dig=22.6, ns=24.50, ns_py=21.75),
           w9=dict(us=8.1, ca=4.3, oi=7.4, tot=7.5, rep=11.3, dig=20.6, ns=54.52, ns_py=48.33))
M['mon'] = MON
for k, v in MON.items(): v['g'] = (v['ns']/v['ns_py']-1)*100
put('labor_day_bps', 50); put('wh_nov', 945); put('wh_oct', 943)
put('gasfx_gap_9w', MON['w9']['rep'] - MON['w9']['tot'])

# ---------------- Depósitos (10-K y presentaciones) ----------------
WH = {2015: 686, 2016: 715, 2017: 741, 2018: 762, 2019: 782, 2020: 795, 2021: 815, 2022: 838, 2023: 861, 2024: 890, 2025: 914, 2026: 939}
M['wh'] = WH
WH27E = put('wh27e', 967); put('wh27_us', 665); put('wh27_ca', 120); put('wh27_oi', 182)
put('wh27_net', WH27E - WH[2026]); put('wh27_new', 33); put('wh27_reloc', 5)
put('wh_net_26', WH[2026]-WH[2025]); put('wh_net_25', WH[2025]-WH[2024])
put('wh_cagr_10', ((WH[2026]/WH[2016])**(1/10)-1)*100)
put('ns_per_wh_26', NS[2026]/((WH[2026]+WH[2025])/2)*1000); put('ns_per_wh_16', NS[2016]/((WH[2016]+WH[2015])/2)*1000)
put('ns_per_wh_cagr', ((M['ns_per_wh_26']/M['ns_per_wh_16'])**(1/10)-1)*100)
# aporte de depósitos nuevos (no comparables) al crecimiento de ventas: FY2025 y FY2026 (10-K: aumento de comparables en US$)
NONCOMP = {2025: (20.287-14.788)/NS[2024]*100, 2026: (27.335-22.457)/NS[2025]*100}
M['noncomp'] = {str(k): v for k, v in NONCOMP.items()}
NEWWH = put('newwh_pts', avg(list(NONCOMP.values())))
put('ns_g_comp_26', 22.457/NS[2025]*100)
put('ft_26', 3); put('tk_26', 5)                     # 10-K FY2026: frecuencia +3%, ticket +5% (comparables reportadas)

# ---------------- Trimestre 4T FY2026 (16 semanas) y año ----------------
Q4 = dict(ns=93.873, ns_py=84.432, fee=1.850, fee_py=1.724, oi=3.801, oi_py=3.341, ni=2.998, ni_py=2.610, gm=11.02, sga=8.94,
          gm_bp=-11, gm_bp_xg=20, sga_bp=27, sga_bp_xg=2, core_bp=-32, core_bp_xg=-9, coc_bp=18)
M['q4'] = Q4
put('q4_ns_g', (Q4['ns']/Q4['ns_py']-1)*100); put('q4_oi_g', (Q4['oi']/Q4['oi_py']-1)*100); put('q4_ni_g', (Q4['ni']/Q4['ni_py']-1)*100)
put('q4_fee_share', Q4['fee']/Q4['oi']*100)
put('ieepa_paid', 0.500); put('ieepa_refund_26', 0.184); put('ieepa_refund_after', 0.155); put('ieepa_gm_bps', 3)

# ---------------- Balance (comunicado del 4T / 10-K, 30-ago-2026) ----------------
CASH = put('cash', 20.207 + 1.094)              # caja + inversiones de corto plazo
DEBT = put('debt', 2.248 + 3.914)               # porción corriente + largo plazo (Senior Notes y otros)
FIN_L = put('fin_lease', A['FinLease']['2026']/1e9)
OP_L = put('op_lease', A['OpLease']['2026']/1e9)
NETCASH_DCF = put('net_cash_dcf', CASH - DEBT - FIN_L)          # sin arrendamientos operativos (sus pagos ya están en el resultado)
NETCASH_EV = put('net_cash_ev', CASH - DEBT - FIN_L - OP_L)     # con arrendamientos operativos (EV/EBITDA, como los pares)
put('card_recv', 2.842)
EBITDA26 = put('ebitda26', OI[2026] + DA[2026])
put('debt_ebitda', (DEBT + FIN_L)/EBITDA26)
put('debt_cur', 2.248); put('equity_26', 35.803); put('assets_26', 89.045)
SPECIAL = put('special', 30.0); put('special_total', 13.3); put('special_cash_pct', 13.3/CASH*100)
put('special_yield', SPECIAL/PRICE*100); put('cash_after_special', CASH - 13.3)
put('net_cash_after_special', NETCASH_DCF - 13.3)
put('special_ps_netcash', NETCASH_DCF/SH_DIL*1000)
# ROIC propio: resultado operativo × (1 − t) / capital invertido promedio (patrimonio + deuda + arrendamientos financieros − caja)
IC = {2025: 29.164 + 0.075 + 5.713 + 1.479 - (14.161 + 1.123), 2026: 35.803 + DEBT + FIN_L - CASH,
      2024: 23.622 + 0.103 + 5.794 + 1.400 - (9.906 + 1.238)}
TAXR = {2025: 25.1, 2026: 24.7}
put('roic_26', OI[2026]*(1-TAXR[2026]/100)/((IC[2026]+IC[2025])/2)*100)
put('roic_25', OI[2025]*(1-TAXR[2025]/100)/((IC[2025]+IC[2024])/2)*100)
put('ic_26', IC[2026])
# ROIC operativo (sin efecto de la caja): resultado × (1 − t) / (activo fijo neto + arrendamientos + capital de trabajo operativo)
OPCAP26 = 35.633 + 2.697 + (3.959 + 19.324 + 1.998) - (22.591 + 5.641 + 3.037 + 3.006 + 7.429)
OPCAP25 = 31.909 + 2.725 + (3.203 + 18.116 + 1.777) - (19.783 + 5.205 + 2.677 + 2.854 + 6.514)
put('opcap_26', OPCAP26); put('roic_op_26', OI[2026]*(1-TAXR[2026]/100)/((OPCAP26+OPCAP25)/2)*100)
put('nwc_26', (3.959 + 19.324 + 1.998) - (22.591 + 5.641 + 3.037 + 3.006 + 7.429))

# ---------------- Flujo, dividendo, recompras ----------------
put('fcf_26', OCF[2026]-CAPEX[2026]); put('fcf_25', OCF[2025]-CAPEX[2025])
put('fcf_conv_26', (OCF[2026]-CAPEX[2026])/NI[2026]*100); put('fcf_conv_25', (OCF[2025]-CAPEX[2025])/NI[2025]*100)
put('capex_ns_26', CAPEX[2026]/NS[2026]*100); put('capex_guide', 7.5); put('wc_26', 2.328); put('wc_25', 1.764)
put('capex_g27', (7.5/CAPEX[2026]-1)*100)
DIV_Q = put('div_q', 1.47); DIV = put('div_annual', 4*DIV_Q); put('div_yield', DIV/PRICE*100)
put('div_prev_q', 1.30); put('div_raise', (1.47/1.30-1)*100)
put('div_decl_26', 5.54); put('payout_reg', 5.54/20.76*100)
put('div_paid_26', DIVP[2026]); put('buyback_26', 0.847); put('buyback_sh_26', 0.891); put('buyback_px_26', 950.90)
put('buyback_px_25', 957.66); put('buyback_left', 1.115); put('buyback_new', 4.0); put('buyback_used', 3.1)
put('buyback_pct_mcap', 0.847/MKT_CAP*100)
put('buyback_vs_px', (PRICE/950.90-1)*100)
SPECIALS = [(2012, 7.0), (2015, 5.0), (2017, 7.0), (2020, 10.0), (2024, 15.0), (2026, 30.0)]
M['specials'] = SPECIALS; put('specials_sum', sum(v for _, v in SPECIALS))
put('special_vs_reg', SPECIAL/DIV)
# retorno total al accionista en diez años (FY2017-FY2026, sin el especial de dic-2026)
put('div_paid_10y', sum(DIVP[y] for y in range(2017, 2027))); put('buyback_10y', sum(BUYB[y] for y in range(2017, 2027)))
put('ni_10y', sum(NI[y] for y in range(2017, 2027)))
put('payout_10y', (M['div_paid_10y'] + M['buyback_10y'])/M['ni_10y']*100)
put('fcf_yield', M['fcf_26']/MKT_CAP*100)
put('div_minus_rf', M['div_yield'] - RF); put('fcf_minus_rf', M['fcf_yield'] - RF); put('rf_over_fcf', RF/M['fcf_yield'])
put('earn_yield', NTM/PRICE*100); put('earn_minus_rf', M['earn_yield'] - RF)
put('vanguard_pct', 43.455/SH_OUT*100); put('blackrock_pct', 34.782/SH_OUT*100)

# ---------------- Costo de capital ----------------
TAX = put('tax', 25.0)                                 # tasa normalizada (24.7% FY2026, 25.1% FY2025)
BETA = put('beta_cost', SH['cost_precio']['multiplos']['beta_5y'])
BETA_ADJ = put('beta_adj', 0.67*BETA + 0.33)
KE_FLOOR = put('ke_floor', RF + 2.5)
KE = put('ke', max(RF + BETA_ADJ*ERP, KE_FLOOR))
KD_PRE = put('kd_pre', RF + 0.50)                      # supuesto: emisor Aa3/A+ a ~50 pb sobre el Treasury
KD = put('kd', KD_PRE*(1-TAX/100))
DV = DEBT + FIN_L
WD = put('wd', DV/(DV + MKT_CAP)*100)
def wacc_of(ke): return (1-WD/100)*ke + WD/100*KD
WACC = put('wacc', wacc_of(KE))

# ---------------- DCF consolidado (Método 1a, 7.5%) ----------------
# Ventas netas = tráfico + ticket + depósitos nuevos; ingresos totales crecen igual; margen operativo sobre ingresos anclado en el
# promedio de diez años de su cambio anual; flujo = NOPAT + D&A − capex + liberación de capital de trabajo (w × aumento de ventas).
t = TAX/100
STUB = put('stub', 281/364)                            # 21-nov-2026 a 29-ago-2027 (resto del FY2027)
W_WC = put('w_wc', (1.764 + 2.328)/(NS[2026] - NS[2024]))   # capital de trabajo liberado por dólar de ventas nuevas, FY2025-FY2026
DA_NS26 = put('da_ns_26', DA[2026]/NS[2026]*100)
CAPEX27_NS = None
G27 = put('g27_ns', MON['w9']['tot'] + NEWWH)          # FY2027E: comparables de 9 semanas + depósitos nuevos (sin nafta ni FX)
SC = {
 'bear': dict(dw=+0.5, g=2.0, trx=round(M['tot_trx_4q'] - 1.0, 2), tkt=2.0, wh=round(NEWWH - 0.6, 2), dm=M['om_dm_hist'] - 10, capex=2.50),
 'base': dict(dw=0.0, g=2.5, trx=round(M['tot_trx_8q'], 2), tkt=2.5, wh=round(NEWWH, 2), dm=M['om_dm_hist'], capex=2.30),
 'bull': dict(dw=-0.5, g=3.0, trx=round(M['tot_trx_8q'] + 0.5, 2), tkt=3.0, wh=round(NEWWH + 0.4, 2), dm=M['om_dm_hist'] + 10, capex=2.15),
}
M['sc'] = SC
for k, s in SC.items(): put(f'g_{k}', s['trx'] + s['tkt'] + s['wh'])
DA_PATH = [0.92, 0.95, 0.98, 1.00, 1.02, 1.04]          # D&A / ventas netas, FY27-FY32 (sube con el capex de aperturas)
def capex_path(sc): return [7.5/(NS[2026]*(1+G27/100))*100] + [sc['capex']]*5
put('capex27_ns', 7.5/(NS[2026]*(1+G27/100))*100)
def cons_paths(sc_name, dcomp=0.0, dm=None):
    sc = SC[sc_name]; dm = sc['dm'] if dm is None else dm
    rows = []; ns = NS[2026]; rev = REV[2026]; m = ANN['2026']['om']; cx = capex_path(sc)
    for i in range(6):
        g = G27 if i == 0 else sc['trx'] + sc['tkt'] + sc['wh'] + dcomp
        ns_prev = ns; ns *= 1 + g/100; rev *= 1 + g/100; m += dm/100
        oi = rev*m/100; da = ns*DA_PATH[i]/100; capex = ns*cx[i]/100; wc = W_WC*(ns - ns_prev)
        fcf = oi*(1-t) + da - capex + wc
        rows.append(dict(y=2027+i, g=g, ns=ns, rev=rev, m=m, oi=oi, da=da, capex=capex, wc=wc, fcf=fcf))
    return rows
def disc(flows, w, g, last=None):
    pv = flows[0]*STUB*(1+w/100)**-(STUB/2)
    for i in range(1, 6): pv += flows[i]*(1+w/100)**-(STUB + i - 0.5)
    tvf = flows[5] if last is None else last
    pv_tv = tvf*(1+g/100)/((w-g)/100)*(1+w/100)**-(STUB+5)
    return pv, pv_tv
def term_fcf(row, g, margin_oi=None):
    # año terminal normalizado: el capital de trabajo liberado se ajusta al crecimiento a perpetuidad
    oi = row['oi'] if margin_oi is None else margin_oi
    return oi*(1-t) + row['da'] - row['capex'] + W_WC*row['ns']*g/100
def dcf(sc_name, w=None, g=None, dcomp=0.0, dm=None, detail=False):
    sc = SC[sc_name]; w = (WACC + sc['dw']) if w is None else w; g = sc['g'] if g is None else g
    rows = cons_paths(sc_name, dcomp, dm)
    pv, pv_tv = disc([r['fcf'] for r in rows], w, g, last=term_fcf(rows[5], g))
    ev = pv + pv_tv; eq = ev + NETCASH_DCF; ps = eq/SH_DIL*1000
    if detail: return dict(ps=ps, ev=ev, pv=pv, pv_tv=pv_tv, tv_share=pv_tv/ev*100, w=w, g=g, rows=rows)
    return ps
for k in SC:
    r = dcf(k, detail=True)
    for f in ('ps', 'ev', 'tv_share', 'w', 'g'): put(f'dcf_{k}' if f == 'ps' else f'dcf_{k}_{f}', r[f])
    rows = r['rows']
    put(f'dcf_{k}_nscagr', ((rows[5]['ns']/NS[2026])**(1/6)-1)*100); put(f'dcf_{k}_m32', rows[5]['m'])
    put(f'dcf_{k}_fcfm32', rows[5]['fcf']/rows[5]['rev']*100)
    if k == 'base':
        for i, row in enumerate(rows):
            row['pv'] = row['fcf']*(STUB if i == 0 else 1)*(1+r['w']/100)**-((STUB/2) if i == 0 else (STUB + i - 0.5))
        M['dcf_base_rows'] = rows
        put('base_oi27', rows[0]['oi']); put('base_oi27_g', (rows[0]['oi']/OI[2026]-1)*100)
        put('base_eps27', (rows[0]['oi'] + 0.566)*(1-t)/SH_DIL*1000)          # + otros ingresos netos del FY2026 (intereses)
        put('base_eps27_vs_c', (M['base_eps27']/C27-1)*100)
        put('base_fcf27_full', rows[0]['fcf']); put('base_fcfm27', rows[0]['fcf']/rows[0]['rev']*100)
put('dcf_gap', (M['dcf_base']/PRICE-1)*100)
put('dcf_pw', 0.25*M['dcf_bear'] + 0.45*M['dcf_base'] + 0.30*M['dcf_bull'])
for k in ('bear', 'bull'): put(f'dcf_{k}_gap', (M[f'dcf_{k}']/PRICE-1)*100)
# flujo libre real sin apalancar del FY2026 con la misma definición (para comparar con el año 1 del Base)
put('ufcf_26', OCF[2026] - 0.601*(1-t) + 0.145*(1-t) - CAPEX[2026]); put('ufcf_m26', M['ufcf_26']/REV[2026]*100)
put('ufcf_model_26', OI[2026]*(1-t) + DA[2026] - CAPEX[2026] + W_WC*(NS[2026]-NS[2025]))
# Sensibilidad a las comparables (−2 / 0 / +2 puntos por año, FY2028-FY2032)
put('dcf_comp_m2', dcf('base', dcomp=-2.0)); put('dcf_comp_p2', dcf('base', dcomp=+2.0))
put('dcf_comp_m2_d', (M['dcf_comp_m2']/M['dcf_base']-1)*100); put('dcf_comp_p2_d', (M['dcf_comp_p2']/M['dcf_base']-1)*100)
# Grilla WACC × g
WG = [WACC-1, WACC-0.5, WACC, WACC+0.5, WACC+1]; GG = [2.0, 2.25, 2.5, 2.75, 3.0]
M['grid_w'] = WG; M['grid_g'] = GG
M['grid'] = [[dcf('base', w=w, g=g) for g in GG] for w in WG]
assert abs(M['grid'][2][2] - M['dcf_base']) < 1e-9
put('grid_up', (M['grid'][1][2]/M['dcf_base']-1)*100); put('grid_dn', (M['grid'][3][2]/M['dcf_base']-1)*100)
put('grid_max', M['grid'][0][4]); put('grid_min', M['grid'][4][0])
def solve(f, lo, hi, target, inc=True):
    for _ in range(200):
        mid = (lo+hi)/2
        if (f(mid) < target) == inc: lo = mid
        else: hi = mid
    return (lo+hi)/2
put('impl_wacc', solve(lambda w: dcf('base', w=w), 2.6, 15.0, PRICE, inc=False))
put('impl_g', solve(lambda g: dcf('base', g=g), 0.0, WACC-0.05, PRICE, inc=True))
put('impl_dcomp', solve(lambda d: dcf('base', dcomp=d), 0.0, 40.0, PRICE, inc=True))
put('impl_ns_g', SC['base']['trx'] + SC['base']['tkt'] + SC['base']['wh'] + M['impl_dcomp'])
put('impl_dm', solve(lambda d: dcf('base', dm=d), 0.0, 300.0, PRICE, inc=True))
put('impl_m32', ANN['2026']['om'] + 6*M['impl_dm']/100)
put('wacc_minus_impl', WACC - M['impl_wacc'])
# Chequeo de sesgo
PEER_BETAS = [WM['peers'][k]['beta'] for k in ('TGT', 'KR', 'BJ', 'DG', 'DLTR')] + [WM['beta_wmt']]
PEER_BETA_MED = put('peer_beta_med', st.median(PEER_BETAS))
put('ke_peerbeta', max(RF + (0.67*PEER_BETA_MED + 0.33)*ERP, KE_FLOOR))
put('dcf_peerbeta', dcf('base', w=wacc_of(M['ke_peerbeta'])))
put('dcf_erp_dam', dcf('base', w=wacc_of(max(RF + BETA_ADJ*M['erp_dam'], KE_FLOOR))))
put('dcf_kefloor', dcf('base', w=wacc_of(KE_FLOOR)))
put('wacc_kefloor', wacc_of(KE_FLOOR))
# k de conversión de caja (método del informe de WMT) como alternativa al capital de trabajo explícito
num = sum(OCF[y] - inc*(1-t) + ie*(1-t) for y, inc, ie in ((2025, 0.469, 0.154), (2026, 0.601, 0.145)))
den = sum(OI[y]*(1-t) + DA[y] for y in (2025, 2026))
put('k_conv', num/den)
def dcf_k(k):
    rows = cons_paths('base'); fl = [k*(r['oi']*(1-t) + r['da']) - r['capex'] for r in rows]
    pv, pv_tv = disc(fl, WACC, 2.5); return (pv + pv_tv + NETCASH_DCF)/SH_DIL*1000
put('dcf_kmethod', dcf_k(M['k_conv']))

# ---------------- DCF por negocio (Método 1b, 7.5%): cuotas vs. mercadería ----------------
# Cuotas = socios pagos promedio × cuota por socio. Socios: S_t = S_{t−1} × renovación + altas; altas = altas implícitas del FY2026
# × (depósitos_t / depósitos_2026). Cuota por socio: crece al ritmo compuesto FY2019-FY2026 (incluye una suba de cuota y la
# mezcla Executive). El negocio de cuotas no tiene capex propio: los depósitos y el capital de trabajo se asignan a mercadería.
# Mercadería: ventas netas del Método 1a × margen de mercadería ((resultado operativo − cuotas) / ventas netas), anclado en el
# cambio anual de diez años; flujo = resultado × (1 − t) + D&A − capex + capital de trabajo.
MSC = {'bear': dict(ren=REN_WW[2026] - 1.0, fee_g=M['fee_pm_cagr'] - 0.75, whn=22, mdm=M['merch_dm_hist'] - 10),
       'base': dict(ren=REN_WW[2026], fee_g=M['fee_pm_cagr'], whn=WH27E - WH[2026], mdm=M['merch_dm_hist']),
       'bull': dict(ren=REN_WW[2026] + 0.7, fee_g=M['fee_pm_cagr'] + 0.75, whn=32, mdm=M['merch_dm_hist'] + 10)}
M['msc'] = MSC
def memb_paths(sc_name):
    s = MSC[sc_name]; S = PAID[2026]; fee = FEE_PM[2026]; wh = WH[2026]; out = []
    for i in range(6):
        wh = WH27E if i == 0 else wh + s['whn']
        adds = M['adds_26']*wh/WH[2026]
        S_new = S*s['ren']/100 + adds; fee *= 1 + s['fee_g']/100
        fees = (S + S_new)/2*fee/1000
        out.append(dict(y=2027+i, wh=wh, members=S_new, fee_pm=fee, fees=fees)); S = S_new
    return out
def biz(sc_name, w=None, g=None, detail=False):
    sc = SC[sc_name]; w = (WACC + sc['dw']) if w is None else w; g = sc['g'] if g is None else g
    mrows = memb_paths(sc_name); crow = cons_paths(sc_name); mm = ANN['2026']['merch_m']
    f_m, f_x = [], []
    for i in range(6):
        mm += MSC[sc_name]['mdm']/100
        crow[i]['merch_m'] = mm; crow[i]['merch_oi'] = crow[i]['ns']*mm/100
        f_m.append(mrows[i]['fees']*(1-t))
        f_x.append(crow[i]['merch_oi']*(1-t) + crow[i]['da'] - crow[i]['capex'] + crow[i]['wc'])
    pv_m, tv_m = disc(f_m, w, g)
    last = crow[5]; tf_x = term_fcf(last, g, margin_oi=last['merch_oi'])
    pv_x, tv_x = disc(f_x, w, g, last=tf_x)
    ev_m, ev_x = pv_m + tv_m, pv_x + tv_x
    eq = ev_m + ev_x + NETCASH_DCF; ps = eq/SH_DIL*1000
    if detail: return dict(ps=ps, ev_m=ev_m, ev_x=ev_x, mrows=mrows, crow=crow, f_m=f_m, f_x=f_x, w=w, g=g,
                           tvs_m=tv_m/ev_m*100, tvs_x=tv_x/ev_x*100 if ev_x else 0)
    return ps
for k in SC:
    r = biz(k, detail=True); put(f'biz_{k}', r['ps'])
    put(f'biz_{k}_memb_ps', r['ev_m']/SH_DIL*1000); put(f'biz_{k}_merch_ps', r['ev_x']/SH_DIL*1000)
    put(f'biz_{k}_fees32', r['mrows'][5]['fees']); put(f'biz_{k}_members32', r['mrows'][5]['members'])
    put(f'biz_{k}_mm32', r['crow'][5]['merch_m'])
    if k == 'base':
        M['biz_rows'] = [dict(y=mr['y'], wh=mr['wh'], members=mr['members'], fee_pm=mr['fee_pm'], fees=mr['fees'],
                              fees_g=(mr['fees']/(r['mrows'][i-1]['fees'] if i else FEES[2026])-1)*100,
                              ns=cr['ns'], merch_m=cr['merch_m'], merch_oi=cr['merch_oi'], oi=mr['fees'] + cr['merch_oi'],
                              fee_share=mr['fees']/(mr['fees'] + cr['merch_oi'])*100, fcf_m=r['f_m'][i], fcf_x=r['f_x'][i])
                         for i, (mr, cr) in enumerate(zip(r['mrows'], r['crow']))]
        put('biz_ev_m', r['ev_m']); put('biz_ev_x', r['ev_x']); put('biz_tvs_m', r['tvs_m']); put('biz_tvs_x', r['tvs_x'])
        put('biz_memb_share', r['ev_m']/(r['ev_m'] + r['ev_x'])*100)
        put('biz_netcash_ps', NETCASH_DCF/SH_DIL*1000)
        put('biz_fees27', r['mrows'][0]['fees']); put('biz_fees27_g', (r['mrows'][0]['fees']/FEES[2026]-1)*100)
        put('biz_members27', r['mrows'][0]['members']); put('biz_members27_g', (r['mrows'][0]['members']/PAID[2026]-1)*100)
        put('biz_oi27', r['mrows'][0]['fees'] + r['crow'][0]['merch_oi'])
        put('biz_fcfx_sum', sum(r['f_x'][1:])); put('biz_fcfm_sum', sum(r['f_m'][1:]))
        put('biz_members_ss', M['adds_26']/(1-REN_WW[2026]/100))     # techo de largo plazo con altas constantes (referencia)
put('biz_gap', (M['biz_base']/PRICE-1)*100)
for k in ('bear', 'bull'): put(f'biz_{k}_gap', (M[f'biz_{k}']/PRICE-1)*100)
put('biz_vs_dcf', M['biz_base'] - M['dcf_base'])
assert abs(M['biz_base_memb_ps'] + M['biz_base_merch_ps'] + M['biz_netcash_ps'] - M['biz_base']) < 1e-9
# Sensibilidad del negocio de cuotas: renovación −2 / 0 / +1 puntos y cuota por socio −1 / +1 punto por año
def biz_with(ren=None, fee_g=None):
    s0 = dict(MSC['base'])
    if ren is not None: MSC['base']['ren'] = ren
    if fee_g is not None: MSC['base']['fee_g'] = fee_g
    v = biz('base'); MSC['base'] = s0; return v
put('biz_ren_m2', biz_with(ren=REN_WW[2026]-2)); put('biz_ren_p1', biz_with(ren=REN_WW[2026]+1))
put('biz_fee_m1', biz_with(fee_g=M['fee_pm_cagr']-1)); put('biz_fee_p1', biz_with(fee_g=M['fee_pm_cagr']+1))
put('biz_ren_m2_d', M['biz_ren_m2'] - M['biz_base']); put('biz_ren_p1_d', M['biz_ren_p1'] - M['biz_base'])
put('biz_fee_m1_d', M['biz_fee_m1'] - M['biz_base']); put('biz_fee_p1_d', M['biz_fee_p1'] - M['biz_base'])
# Valor del precio de mercado que queda para la mercadería si las cuotas valen lo del Base
put('price_minus_memb', PRICE - M['biz_base_memb_ps'] - M['biz_netcash_ps'])
put('merch_pe_implied', M['price_minus_memb']*SH_DIL/1000/(M['merch_oi_26']*(1-t)))
put('memb_pe_base', M['biz_ev_m']/(FEES[2026]*(1-t)))

# ---------------- Comparables (Método 2, 25%) ----------------
# Pares de retail del informe de WMT (mismos precios del 20-nov y misma regla de EPS de los próximos cuatro trimestres): Walmart,
# Target, Kroger, BJ's, Dollar General y Dollar Tree. Amazon solo como referencia. Ningún paso usa el precio o el múltiplo de COST.
RT = SH['retail']['pares']
PEERS = {}
for kk in ('TGT', 'KR', 'BJ', 'DG', 'DLTR'):
    p = WM['peers'][kk]
    PEERS[kk] = dict(name=p['name'], cl=p['cl'], px=p['px'], ntm=p['ntm'], pe=p['pe'], comp=p['comp'], g=p['g'], eve=p['eve'],
                     beta=p['beta'], roic=RT[kk]['roic_pct'], dy=RT[kk]['div_yield_pct'] or 0.0)
PEERS['WMT'] = dict(name='Walmart', cl='Supercentro + club', px=WM['price'], ntm=WM['eps_ntm'], pe=WM['pe_ntm_now'], comp=WM['wmt_comp'],
                    g=WM['wmt_g'], eve=WM['wmt_eve'], beta=WM['beta_wmt'], roic=RT['WMT']['roic_pct'], dy=RT['WMT']['div_yield_pct'])
M['peers'] = PEERS
put('wmt_gm_26', WM['ann']['2026']['gm']); put('sams_comp_wmt', WM['sams']['comp'][-1])
AMZN = dict(WM['amzn']); AMZN['roic'] = RT['AMZN']['roic_pct']; M['amzn'] = AMZN
COST_COMP = put('cost_comp', COMP['tot'][-1])           # 4T FY2026, total compañía sin nafta ni FX (misma vara que los pares)
COST_G = put('cost_g', (C28/C27-1)*100)
COST_ROIC_SA = put('cost_roic_sa', SH['cost_precio']['multiplos']['roic_pct'])
put('cost_eve_sa', SH['cost_precio']['multiplos']['ev_ebitda']); put('cost_pe_sa', SH['cost_precio']['multiplos']['pe_fwd'])
def reg(xs, ys):
    mx, my = st.mean(xs), st.mean(ys)
    sxy = sum((x-mx)*(y-my) for x, y in zip(xs, ys)); sxx = sum((x-mx)**2 for x in xs); syy = sum((y-my)**2 for y in ys)
    b = sxy/sxx; return dict(slope=b, icpt=my-b*mx, r2=sxy**2/(sxx*syy), n=len(xs))
R2_MIN = put('r2_min', 0.50)
pl = list(PEERS.items())
def extreme(var):   # par extremo = el de mayor P/E (Walmart), salvo en crecimiento del EPS, donde Target ya está fuera
    return 'WMT'
REGS = {}
for key, var, x_cost in (('comp', 'comp', COST_COMP), ('g', 'g', COST_G), ('roic', 'roic', COST_ROIC_SA), ('beta', 'beta', BETA)):
    pk = [kp for kp in pl if not (key == 'g' and kp[0] == 'TGT')]
    R = reg([p[var] for _, p in pk], [p['pe'] for _, p in pk])
    ex = [kp for kp in pk if kp[0] != extreme(var)]
    Rx = reg([p[var] for _, p in ex], [p['pe'] for _, p in ex])
    ok = R['r2'] >= R2_MIN and Rx['r2'] >= R2_MIN and R['slope'] > 0 and Rx['slope'] > 0
    REGS[key] = dict(all=R, x=Rx, ok=1 if ok else 0, x_cost=x_cost, pe_cost=R['icpt'] + R['slope']*x_cost,
                     pe_cost_x=Rx['icpt'] + Rx['slope']*x_cost, xmin=min(p[var] for _, p in pk), xmax=max(p[var] for _, p in pk))
M['regs'] = REGS
REGE = reg([p['comp'] for _, p in pl], [p['eve'] for _, p in pl]); REGEx = reg([p['comp'] for kk, p in pl if kk != 'WMT'], [p['eve'] for kk, p in pl if kk != 'WMT'])
M['reg_eve'] = REGE; M['reg_eve_x'] = REGEx
put('reg_eve_ok', 1 if (REGE['r2'] >= R2_MIN and REGEx['r2'] >= R2_MIN) else 0)
put('any_reg_ok', max(v['ok'] for v in REGS.values()))
def pctl(xs, q):
    xs = sorted(xs); pos = (len(xs)-1)*q; lo = int(pos); fr = pos - lo
    return xs[lo] + (xs[min(lo+1, len(xs)-1)] - xs[lo])*fr
PES = [p['pe'] for p in PEERS.values()]; EVES = [p['eve'] for p in PEERS.values()]; COMPS = [p['comp'] for p in PEERS.values()]
put('peer_pe_med', pctl(PES, 0.5)); put('peer_pe_q3', pctl(PES, 0.75)); put('peer_pe_max', max(PES)); put('peer_pe_min', min(PES))
put('peer_eve_med', pctl(EVES, 0.5)); put('peer_eve_q3', pctl(EVES, 0.75)); put('peer_eve_max', max(EVES)); put('peer_eve_min', min(EVES))
put('peer_comp_med', pctl(COMPS, 0.5)); put('peer_comp_max', max(COMPS))
put('peer_roic_med', pctl([p['roic'] for p in PEERS.values()], 0.5)); put('peer_g_med', pctl([p['g'] for kk, p in PEERS.items() if kk != 'TGT'], 0.5))
put('cost_above_med', 1 if COST_COMP > M['peer_comp_med'] else 0)
put('cost_comp_top', 1 if COST_COMP > M['peer_comp_max'] else 0)
# Criterio declarado antes de correr: si alguna regresión (comparables, crecimiento del EPS, ROIC, beta) pasa R² ≥ 0.50 con todos
# los pares Y sin el extremo, con pendiente positiva, se usa su recta (la de mayor R² sin el extremo). Si ninguna pasa: mediana si
# las comparables de COST están debajo de la mediana del grupo, cuartil superior si están encima (regla del informe de WMT).
ok_keys = [k for k, v in REGS.items() if v['ok']]
if ok_keys:
    best = max(ok_keys, key=lambda k: REGS[k]['x']['r2']); PE_SEL = REGS[best]['pe_cost']; put('pe_rule', 'regresion_' + best)
else:
    PE_SEL = M['peer_pe_q3'] if M['cost_above_med'] else M['peer_pe_med']; put('pe_rule', 'q3' if M['cost_above_med'] else 'mediana')
put('pe_sel', PE_SEL)
EVE_SEL = put('eve_sel', (REGE['icpt'] + REGE['slope']*COST_COMP) if M['reg_eve_ok'] else (M['peer_eve_q3'] if M['cost_above_med'] else M['peer_eve_med']))
def eve_ps(mult): return (mult*EBITDA26 + NETCASH_EV)/SH_DIL*1000
COMP_PE = put('comp_pe', PE_SEL*NTM); COMP_EV = put('comp_ev', eve_ps(EVE_SEL))
COMPV = put('comp_val', (COMP_PE + COMP_EV)/2)
put('comp_med_only', (M['peer_pe_med']*NTM + eve_ps(M['peer_eve_med']))/2)
put('comp_high', (M['peer_pe_max']*NTM + eve_ps(M['peer_eve_max']))/2)
put('comp_low', min(M['comp_med_only'], COMPV))
put('comp_gap', (COMPV/PRICE-1)*100)
put('pe_vs_med', (PE_NOW/M['peer_pe_med']-1)*100); put('pe_vs_wmt', (PE_NOW/PEERS['WMT']['pe']-1)*100)
put('pe_vs_staples', (PE_NOW/SH['mercado']['sectores_pe_fwd']['consumer_staples']['pe_ajustado_20nov']-1)*100)
put('staples_pe', SH['mercado']['sectores_pe_fwd']['consumer_staples']['pe_ajustado_20nov'])
put('staples_pe_10', SH['mercado']['sectores_pe_fwd']['consumer_staples']['prom_10a'])
put('amzn_pe', AMZN['pe'])
# ¿Cuánto de la prima justifica la regresión aunque no pase? (referencia: la recta contra comparables extrapolada a COST)
put('comp_reg_ref', REGS['comp']['pe_cost']*NTM)
put('comp_roic_ref', REGS['roic']['pe_cost']*NTM)
# Valor "justificado por fundamentos" (referencia, fuera del blend): P/E = (1 − g/ROIC) / (ke − g) con g de largo plazo
def pe_just(roic, g, ke): return (1 - g/roic)/((ke - g)/100)/(1 + 0)
put('pe_just_cost', (1 - 2.5/M['roic_26'])/((KE - 2.5)/100))
put('pe_just_cost_hi', (1 - 2.5/M['roic_26'])/((KE - 2.5)/100)*(1 + 0))
# Prima por fundamentos con un tramo de alto crecimiento (5 años al ritmo del Base y luego 2.5%): P/E de dos etapas
def pe_two_stage(g1, roic, ke, g2=2.5, n=5):
    v = 0; e = 1.0
    for i in range(1, n+1):
        e *= 1 + g1/100; v += e*(1 - g1/roic)/(1 + ke/100)**i
    tv = e*(1 + g2/100)*(1 - g2/roic)/((ke - g2)/100)/(1 + ke/100)**n
    return v + tv
put('pe_2s_cost', pe_two_stage(M['g_base'], M['roic_26'], KE))
put('val_2s_cost', M['pe_2s_cost']*NTM)

# ---------------- Reversión (Método 3, 35%) ----------------
d = json.load(open(ROOT/'.claude'/'skills'/'_compartido'/'defensivos_nov26'/'yh'/'COST.mo.json'))['chart']['result'][0]
closes = {}
for ts, c in zip(d['timestamp'], d['indicators']['quote'][0]['close']):
    dt = datetime.datetime.fromtimestamp(ts, datetime.UTC)
    if c and dt.day == 1: closes[(dt.year, dt.month)] = c
QEND = {0: (11, -1), 1: (2, 0), 2: (5, 0), 3: (8, 0)}     # cierre del trimestre fiscal: nov (año fiscal − 1), feb, may, ago
seq = [(y, q) for y in range(2016, 2029) for q in range(4)]
win = []
for i, (fy, q) in enumerate(seq):
    mo, dy = QEND[q]; ym = (fy + dy, mo)
    if ym < (2016, 8) or ym > (2026, 8): continue
    nx = seq[i+1:i+5]; ntm = sum(EPS[a][b] for a, b in nx)
    win.append(dict(date=f'{ym[0]}-{ym[1]:02d}', fy=fy, q=q+1, price=closes[ym], ntm=ntm, pe=closes[ym]/ntm, cons=any(a >= 2027 for a, _ in nx)))
M['rev_window'] = win
put('rev_n', len(win)); put('rev_n_cons', sum(1 for w in win if w['cons']))
PE10 = put('pe10_avg', st.mean(w['pe'] for w in win))
put('pe10_min', min(w['pe'] for w in win)); put('pe10_max', max(w['pe'] for w in win))
MESES = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic']
_wm = max(win, key=lambda w: w['pe']); put('pe10_max_date', MESES[int(_wm['date'][5:])-1] + '-' + _wm['date'][:4])
put('pe5_avg', st.mean(w['pe'] for w in win if w['date'] >= '2021-11'))
# Regla de cambio de escalón (simétrica): ventana nueva solo si todos los cierres desde un punto superan el máximo (o quedan debajo
# del mínimo) de al menos 20 cierres previos (cinco años) durante al menos 8 trimestres. Incluye el último cierre trimestral (ago-2026).
RR_MIN_PRIOR, RR_MIN_AFTER = put('rr_min_prior', 20), put('rr_min_after', 8)
start = None; direction = ''
for i in range(RR_MIN_PRIOR, len(win)):
    if len(win) - i < RR_MIN_AFTER: break
    prev = [w['pe'] for w in win[:i]]; after = [w['pe'] for w in win[i:]]
    if all(x > max(prev) for x in after): start, direction = i, 'arriba'; break
    if all(x < min(prev) for x in after): start, direction = i, 'abajo'; break
put('rr_found', 1 if start is not None else 0); put('rr_dir', direction)
if start is not None:
    put('rr_start', win[start]['date']); put('rr_n', len(win) - start)
    PE_RR = put('pe_rr_avg', st.mean(w['pe'] for w in win[start:]))
    put('rr_prev_max', max(w['pe'] for w in win[:start])); put('rr_prev_avg', st.mean(w['pe'] for w in win[:start]))
    put('rr_prev_max_date', max(win[:start], key=lambda w: w['pe'])['date'])
    put('rr_last_pe', win[-1]['pe']); put('rr_last_margin', (win[-1]['pe']/M['rr_prev_max']-1)*100)
    put('pe_rr_min', min(w['pe'] for w in win[start:])); put('pe_rr_max', max(w['pe'] for w in win[start:]))
    put('rr_fys', len(set(w['fy'] for w in win[start:])))
else:
    PE_RR = put('pe_rr_avg', PE10)
# diagnóstico: en qué punto la regla estuvo más cerca de cumplirse (máximo de cierres seguidos por encima del máximo previo)
best_run = (0, None)
for i in range(RR_MIN_PRIOR, len(win)):
    pm = max(w['pe'] for w in win[:i]); run = 0
    for w in win[i:]:
        if w['pe'] > pm: run += 1
        else: break
    if run > best_run[0]: best_run = (run, win[i]['date'])
put('rr_best_run', best_run[0]); put('rr_best_run_start', best_run[1] or '')
fyavg = {}
for w in win: fyavg.setdefault(w['fy'], []).append(w['pe'])
M['pe_by_fy'] = {str(k): dict(avg=st.mean(v), mn=min(v), mx=max(v), n=len(v)) for k, v in fyavg.items()}
REV1 = put('rev1', PE_RR*NTM)
put('rev1_10y', PE10*NTM)
SPX_PE = put('spx_pe', SH['mercado']['sp500']['pe_fwd_ajustado_20nov']); SPX_PE10 = put('spx_pe10', SH['mercado']['sp500']['pe_fwd_10a'])
put('spx_pe_19', SH['mercado']['sp500']['pe_fwd_factset']); put('spx_px', SH['mercado']['sp500']['cierre_20nov'])
REL10 = put('rel10', PE10/SPX_PE10)
put('rel_now', PE_NOW/SPX_PE)
REV2 = put('rev2', REL10*SPX_PE*NTM)
put('rev2_19', REL10*M['spx_pe_19']*NTM)
REV = put('rev', (REV1 + REV2)/2)
put('rev_low', min(REV1, REV2, M['pe10_min']*NTM)); put('rev_high', max(REV1, REV2, M['pe10_max']*NTM))
put('rev_gap', (REV/PRICE-1)*100)
put('pe_now_vs_10', (PE_NOW/PE10-1)*100); put('rel_at_spx10', PE_NOW/SPX_PE10)
put('spx_vs_10', (SPX_PE/SPX_PE10-1)*100)
put('rev_19_d', (M['rev2_19'] - REV2)/2)
put('rev_pe_min_val', M['pe10_min']*NTM)

# ---------------- Consenso (Método 4, 25%) ----------------
CONS = put('cons', CS['pt_prom']); put('cons_low', CS['pt_min']); put('cons_high', CS['pt_max']); put('cons_n', CS['n_analistas'])
put('cons_gap', (CONS/PRICE-1)*100)

# ---------------- Blend ----------------
W = {'dcf': 0.075, 'biz': 0.075, 'comp': 0.25, 'rev': 0.35, 'cons': 0.25}
V = {'dcf': M['dcf_base'], 'biz': M['biz_base'], 'comp': COMPV, 'rev': REV, 'cons': CONS}
BLEND = put('blend', sum(W[k]*V[k] for k in W))
put('blend_gap', (BLEND/PRICE-1)*100)
for k in W: put(f'contrib_{k}', W[k]*V[k]); put(f'w_{k}', W[k]*100)
IND = ('dcf', 'biz', 'comp'); ANC = ('rev', 'cons')
put('indep', sum(W[k]*V[k] for k in IND)/sum(W[k] for k in IND)); put('anch', sum(W[k]*V[k] for k in ANC)/sum(W[k] for k in ANC))
put('indep_gap', (M['indep']/PRICE-1)*100); put('anch_gap', (M['anch']/PRICE-1)*100)
put('m1_avg', (M['dcf_base'] + M['biz_base'])/2); put('m1_gap', (M['m1_avg']/PRICE-1)*100)
def blend_with(**kw):
    v = dict(V); v.update(kw); return sum(W[k]*v[k] for k in W)
put('blend_rev10', blend_with(rev=(M['rev1_10y'] + REV2)/2))
put('blend_comp_med', blend_with(comp=M['comp_med_only']))
put('blend_ex_div', BLEND - SPECIAL); put('price_ex_div', PRICE - SPECIAL)
put('blend_ex_div_gap', (M['blend_ex_div']/M['price_ex_div']-1)*100)
put('blend_vs_cons', (BLEND/CONS-1)*100)
for k in ('dcf', 'biz', 'comp', 'rev', 'cons'): put(f'{k}_v_gap', (V[k]/PRICE-1)*100)
put('anch_minus_indep', M['anch'] - M['indep'])
# Postura (misma escala que las tarjetas del sitio): ±10% neutral; −10% a −25% neutral con sesgo bajista/cauteloso; < −25% bajista
put('stance_accent', 'down' if M['blend_gap'] < -25 else ('up' if M['blend_gap'] > 25 else 'neutral'))

# ---------------- Series para gráficos ----------------
FYL = [str(y) for y in YRS]
M['js_fy'] = json.dumps(['FY' + y[2:] for y in FYL])
M['js_ns'] = json.dumps([round(NS[y], 1) for y in YRS])
M['js_fees'] = json.dumps([round(FEES[y], 2) for y in YRS])
M['js_merch_oi'] = json.dumps([round(OI[y]-FEES[y], 2) for y in YRS])
M['js_fee_share'] = json.dumps([round(ANN[y]['fee_share'], 1) for y in FYL])
M['js_gm'] = json.dumps([round(ANN[y]['gm'], 2) for y in FYL]); M['js_sga'] = json.dumps([round(ANN[y]['sga'], 2) for y in FYL])
M['js_om'] = json.dumps([round(ANN[y]['om'], 2) for y in FYL]); M['js_mm'] = json.dumps([round(ANN[y]['merch_m'], 2) for y in FYL])
M['js_turns'] = json.dumps([round(ANN[y]['turns'], 2) for y in FYL]); M['js_apinv'] = json.dumps([round(ANN[y]['ap_inv'], 1) for y in FYL])
M['js_ocf'] = json.dumps([round(OCF[y], 2) for y in YRS]); M['js_capex'] = json.dumps([round(CAPEX[y], 2) for y in YRS])
M['js_fcf'] = json.dumps([round(OCF[y]-CAPEX[y], 2) for y in YRS])
M['js_ql'] = json.dumps([q[:2] + ' FY' + q[2:] for q in QL], ensure_ascii=False)
M['js_ql_m'] = json.dumps([q[:2] + ' FY' + q[2:] for q in QL] + ['Sep 26', 'Oct 26'], ensure_ascii=False)
M['js_trx'] = json.dumps(TRX['tot']); M['js_tkt'] = json.dumps(TKT['tot']); M['js_comp'] = json.dumps(COMP['tot'])
M['js_us_trx'] = json.dumps(TRX['us']); M['js_us_tkt'] = json.dumps(TKT['us']); M['js_us_comp'] = json.dumps(COMP['us'])
M['js_dig'] = json.dumps(DIG)
M['js_reg_comp'] = json.dumps([COMP['us'] + [MON['sep']['us'], MON['oct']['us']], COMP['ca'] + [MON['sep']['ca'], MON['oct']['ca']],
                               COMP['oi'] + [MON['sep']['oi'], MON['oct']['oi']]])
M['js_mq'] = json.dumps([q[:2] + ' FY' + q[2:] for q in MQ], ensure_ascii=False)
M['js_ren_ww'] = json.dumps(MEMQ['ren_ww']); M['js_ren_us'] = json.dumps(MEMQ['ren_us'])
M['js_paid'] = json.dumps(MEMQ['paid']); M['js_exec'] = json.dumps(MEMQ['exec']); M['js_fee_g'] = json.dumps(MEMQ['fee_g_fx'])
M['js_fq'] = json.dumps([q[:2] + ' FY' + q[2:] for q in FQL], ensure_ascii=False)
M['js_fee_share_q'] = json.dumps([round(x, 1) for x in M['fee_share_q']])
M['js_wh_y'] = json.dumps(['FY' + str(y)[2:] for y in range(2016, 2027)] + ['FY27E'])
M['js_wh'] = json.dumps([WH[y] for y in range(2016, 2027)] + [WH27E])
M['js_pe_labels'] = json.dumps([(w['date'][:4] if w['date'][5:] == '08' else '') for w in win])
M['js_pe_vals'] = json.dumps([round(w['pe'], 2) for w in win])
M['js_pe_10'] = json.dumps([round(PE10, 2)]*len(win))
M['js_pe_rr'] = json.dumps([None]*start + [round(PE_RR, 2)]*(len(win)-start))
M['js_pe_rel'] = json.dumps([round(REL10*SPX_PE10, 2)]*len(win))
SPARK = [closes[(2026, m)] for m in range(5, 11)] + [PRICE]
M['spark'] = [round(x, 2) for x in SPARK]
put('ret_ytd', (PRICE/closes[(2025, 12)]-1)*100); put('px_dec25', closes[(2025, 12)])
put('ret_1y', (PRICE/closes[(2025, 10)]-1)*100); put('px_aug26', closes[(2026, 8)]); put('ret_since_aug', (PRICE/closes[(2026, 8)]-1)*100)
put('px_sep26', closes[(2026, 9)]); put('ret_since_sep', (PRICE/closes[(2026, 9)]-1)*100)

# ---------------- Asserts que atan frases cualitativas de la plantilla a los números ----------------
if not ALT:
    assert 45 < M['fee_share_26'] < 55                          # "la mitad del resultado operativo"
    assert M['fee_share_16'] > 70                               # "más de 70% hace diez años"
    assert M['merch_m_26'] > 1.5*M['merch_m_21'] - 0.5          # el margen de mercadería sube
    assert M['tot_trx_4q'] < M['tot_trx_8q']                    # "el tráfico se desaceleró"
    assert all(x > 0 for x in TRX['tot'])                       # "tráfico positivo en todos los trimestres"
    assert TKT['tot'][-2] > TRX['tot'][-2]                      # "en el 3T FY2026 el ticket superó al tráfico"
    assert M['tot_trx_share_8q'] > 50 and M['tot_trx_share_4q'] < 50   # "más de la mitad en ocho trimestres; menos de la mitad en los últimos cuatro"
    assert PE_NOW > 2*M['peer_pe_med']                          # "más del doble de la mediana"
    assert PE_NOW > PEERS['WMT']['pe']                          # "más caro que Walmart"
    assert M['any_reg_ok'] == 0                                 # "ninguna regresión pasa el criterio"
    assert M['cost_comp_top'] == 1                              # "las comparables más altas del grupo"
    assert M['dcf_bull'] < PRICE and M['biz_bull'] < PRICE      # "ni el Bull llega al precio"
    assert M['cons'] < PRICE                                    # "ni el consenso llega al precio"
    assert M['anch'] < PRICE and M['indep'] < M['anch']
    assert M['impl_wacc'] < RF + 2.5                            # el WACC implícito queda debajo del piso del costo del equity
    assert M['rr_found'] == 1 and M['rr_dir'] == 'arriba'       # "la regla de cambio de escalón se cumple"
    assert 0 < M['rr_last_margin'] < 3                          # "el último cierre la cumple por poco (frágil)"
    assert M['rel_now'] > REL10                                 # el relativo está por encima del promedio
    assert M['blend_gap'] < -25 and M['stance_accent'] == 'down'
    assert M['buyback_px_26'] < PRICE
    assert TKT['us'][6] > TRX['us'][6] and TKT['us'][5] < TRX['us'][5]   # "el ticket supera al tráfico en EE.UU. desde el 1T FY2026"
    assert M['dcf_bull'] < PRICE/2 and M['indep'] < PRICE/2         # "ni el Bull llega a la mitad"; "menos de la mitad de su precio"
    assert M['impl_wacc'] < RF                                      # "por debajo de la propia tasa libre de riesgo"
    assert M['impl_m32'] > 3*M['om_26'] and M['impl_m32'] > M['gm_26']   # "más del triple ... por encima del margen bruto"
    assert M['pe10_max_date'] == 'feb-2025' and M['rr_last_pe'] < M['pe10_max']
    assert abs(M['wmt_gm_26'] - 2*M['gm_26']) < 4                   # "la mitad que Walmart"
    assert M['cons'] < PRICE and M['cons_gap'] < 0
    assert M['exec_share_26'] > 49.5 and M['memq']['ren_us'][-1] > 92   # "ya son la mitad"; "arriba de 92%"
    assert MEMQ['ren_ww'][-1] < MEMQ['ren_ww'][0]               # "la renovación mundial bajó desde 90.5%"
    assert M['paid_g26'] < M['paid_cagr_8']                     # el crecimiento de socios se desaceleró
    assert M['biz_base_merch_ps'] < M['biz_base_memb_ps']       # "las cuotas valen más que la mercadería"
    assert M['special_cash_pct'] > 50                           # "más de la mitad de la caja"
OUT = os.environ.get('COST_MODEL_OUT', str(HERE/'model.json'))
json.dump(M, open(OUT, 'w'), indent=1, default=float)
if __name__ == '__main__' and not ALT:
    for k, v in M.items():
        if isinstance(v, (int, float)) and not isinstance(v, bool): print(f'{k:24s} {v:,.4f}')
    print('peers:'); [print(' ', k, round(p['pe'], 2), p['comp'], round(p['g'], 1), p['eve'], p['roic'], p['beta']) for k, p in PEERS.items()]
    for k, v in REGS.items(): print('reg', k, {kk: round(vv, 3) for kk, vv in v['all'].items()}, {kk: round(vv, 3) for kk, vv in v['x'].items()}, v['ok'], round(v['pe_cost'], 1))
    print('reg_eve', REGE, REGEx)
    for w in win: print(w['date'], w['fy'], round(w['price'], 2), round(w['ntm'], 3), round(w['pe'], 2))
    for r in M['dcf_base_rows']: print({k: round(v, 3) for k, v in r.items()})
    for r in M['biz_rows']: print({k: round(v, 3) for k, v in r.items()})
