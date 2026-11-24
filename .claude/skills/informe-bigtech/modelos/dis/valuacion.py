# Modelo de valuación DIS (The Walt Disney Company) — informe-bigtech.
# Edición nov-2026: 4T y año fiscal 2026 (cerrado el 3-oct-2026, año de 53 semanas; 8-K y 10-K del 17-nov-2026).
# Precio: cierre del viernes 20-nov-2026 (bloque común con WMT: data/comun_2026-11-20.json).
# Trabaja con el EPS AJUSTADO de Disney (el GAAP está distorsionado por Hulu, A+E, Fubo/NFL y amortización de Fox).
#
# 1) SEP: reconstrucción del DCF publicado en sep-2026 (informes/dis.html al 3T FY26, precio $104.16 del 8-sep-2026).
#    El informe declaraba OCF y capex del año 1 y del año 5 de cada escenario, WACC, g, deuda neta, minoritarias y acciones;
#    no publicaba los años intermedios ni el monto exacto de intereses. Con interpolación LINEAL y el interés después de
#    impuestos despejado para que el Base dé exactamente $102.32 (0.7174 mil millones; el texto decía "~0.8") la grilla
#    5x5 publicada se reproduce con ±$0.22 y Bear/Bull con −$0.32 / −$0.99 (residuos documentados en el README).
# 2) NOV: la misma estructura con los datos nuevos. Cinco métodos con los pesos de la casa (7.5 DCF / 7.5 SOTP / 25 / 35 / 25).
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent
R = {}
def put(k, v): R[k] = v; return v

def lin(a, b): return [a + (b - a)*i/4 for i in range(5)]
def dcf(o1, o5, c1, c5, w, g, intr, nd, nci, sh, detail=False):
    o = lin(o1, o5); c = lin(c1, c5); w /= 100; g /= 100
    f = [o[i] + intr - c[i] for i in range(5)]
    pvs = [f[i]/(1+w)**(i+1) for i in range(5)]
    tv = f[4]*(1+g)/(w-g); pvtv = tv/(1+w)**5
    ev = sum(pvs) + pvtv; ps = (ev - nd - nci)/sh*1000
    if detail: return dict(ps=ps, ev=ev, tv_share=pvtv/ev*100, ocf=o, capex=c, fcf=f, pv=pvs, pvtv=pvtv)
    return ps
def solve(fn, lo, hi, target, inc=True):
    for _ in range(200):
        m = (lo+hi)/2
        if (fn(m) < target) == inc: lo = m
        else: hi = m
    return (lo+hi)/2

# =============================== 1) Septiembre 2026 (reconstrucción) ===============================
SEP = dict(price=104.16, nd=40.856, nci=6.810, sh=1727,
           sc=dict(bear=(18.5, 20.5, 9.5, 9.0, 10.6, 2.5), base=(19.5, 25.2, 9.0, 8.0, 9.8, 3.0), bull=(20.0, 29.0, 9.0, 7.5, 9.0, 3.5)),
           pub=dict(bear=50.25, base=102.32, bull=167.93, comp=95.36, sotp=98.01, rev=108.12, cons=127.61, blend=106.28))
def sep_dcf(k, w=None, g=None, intr=None):
    o1, o5, c1, c5, ww, gg = SEP['sc'][k]
    return dcf(o1, o5, c1, c5, ww if w is None else w, gg if g is None else g, R['sep_intr'] if intr is None else intr, SEP['nd'], SEP['nci'], SEP['sh'])
put('sep_intr', solve(lambda x: sep_dcf('base', intr=x), 0, 2, 102.32))
SEP_GRID_PUB = [[106.83, 115.51, 125.69, 137.79, 152.41], [97.19, 104.55, 113.07, 123.07, 134.95], [88.80, 95.10, 102.32, 110.69, 120.51],
                [81.42, 86.86, 93.05, 100.14, 108.36], [74.89, 79.63, 84.97, 91.04, 98.01]]
WG_SEP = [8.8, 9.3, 9.8, 10.3, 10.8]; GG = [2.0, 2.5, 3.0, 3.5, 4.0]
R['sep_grid_resid'] = [[round(sep_dcf('base', w=w, g=g) - SEP_GRID_PUB[i][j], 2) for j, g in enumerate(GG)] for i, w in enumerate(WG_SEP)]
put('sep_grid_maxresid', max(abs(x) for row in R['sep_grid_resid'] for x in row))
for k in ('bear', 'base', 'bull'): put(f'sep_dcf_{k}', sep_dcf(k)); put(f'sep_dcf_{k}_resid', R[f'sep_dcf_{k}'] - SEP['pub'][k])
assert abs(R['sep_dcf_base'] - 102.32) < 1e-6 and R['sep_grid_maxresid'] < 0.25
# Blend de septiembre: publicado como promedio simple; con la regla vigente (ponderado 7.5/7.5/25/35/25) habría dado:
W = dict(dcf=0.075, sotp=0.075, comp=0.25, rev=0.35, cons=0.25)
P = SEP['pub']
put('sep_blend_simple', (P['base'] + P['comp'] + P['sotp'] + P['rev'] + P['cons'])/5)
assert abs(R['sep_blend_simple'] - 106.28) < 0.006
put('sep_blend_w', W['dcf']*P['base'] + W['sotp']*P['sotp'] + W['comp']*P['comp'] + W['rev']*P['rev'] + W['cons']*P['cons'])
put('sep_blend_w_gap', (R['sep_blend_w']/SEP['price'] - 1)*100)
# SOTP de septiembre (reproducción): 14x / 11x / 10x sobre la utilidad de segmentos TTM a jun-26, corporativo a 10x
put('sep_sotp_check', ((10.819*14 + 4.807*11 + 2.612*10 - 1.357*10) - 40.856 - 6.810)/1727*1000)

# =============================== 2) Noviembre 2026 ===============================
PRICE = put('price', 117.98); put('hi52', 123.37); put('lo52', 92.19)
RF = put('rf', 4.912); ERP = put('erp', 5.0); put('erp_dam', 4.41)
SH_OUT = put('sh_out', 1708.029668)            # acciones al 11-nov-2026 (portada del 10-K)
SH_DIL_Q4 = put('sh_dil_q4', 1731); SH_DIL_FY = put('sh_dil_fy', 1759)
# Balance al 3-oct-2026 (comunicado / 10-K)
CASH = put('cash', 6.679); DEBT_ST = put('debt_st', 7.331); DEBT_LT = put('debt_lt', 37.142)
DEBT = put('debt', DEBT_ST + DEBT_LT); ND = put('nd', DEBT - CASH)
NCI = put('nci', 7.105); put('nd_sep', 40.856)
put('equity', 111.600); put('goodwill', 74.700); put('intang', 9.473); put('gw_int', 74.700 + 9.473)
# Resultados FY2026 (53 semanas) y trimestres
FY = dict(rev=102.344, rev_py=94.425, seg_oi=19.728, seg_oi_py=17.551, pretax=14.212, ni=9.899, eps_gaap=5.63, eps_adj=7.02,
          eps_adj_py=5.93, eps_adj_ex53=6.85, ocf=19.270, ocf_py=18.101, capex=8.698, capex_py=8.024, fcf=10.572, fcf_py=10.077,
          da=5.605, int_net=1.157, buyback=9.000, div_paid=2.634, corp=1.461, w53_rev=1.6, w53_oi=0.490, w53_eps=0.17)
Q4 = dict(rev=25.947, rev_py=22.464, seg_oi=4.970, seg_oi_py=3.480, seg_oi_ex53=4.480, pretax=3.507, ni=2.612, eps_gaap=1.51,
          eps_adj=1.77, eps_adj_py=1.11, eps_adj_ex53=1.59, ocf=6.755, capex=1.918, fcf=4.837, svod_rev=6.050, svod_oi=0.824,
          svod_oi_py=0.402, svod_oi_53=0.160, exp_rev=10.105, exp_oi=2.250, exp_oi_py=1.878, ent_rev=11.893, ent_oi=1.327,
          ent_oi_py=0.691, spo_rev=4.614, spo_oi=1.393, spo_oi_py=0.911, buyback=1.8)
Q3 = dict(rev=25.248, seg_oi=5.555, pretax=3.645, ni=2.64, eps_gaap=1.51, eps_adj=2.06, sh=1743)
R['fy'] = FY; R['q4'] = Q4; R['q3'] = Q3
put('fy_rev_g', (FY['rev']/FY['rev_py']-1)*100); put('fy_segoi_g', (FY['seg_oi']/FY['seg_oi_py']-1)*100)
put('fy_seg_m', FY['seg_oi']/FY['rev']*100); put('q4_seg_m', Q4['seg_oi']/Q4['rev']*100); put('q3_seg_m', Q3['seg_oi']/Q3['rev']*100)
put('q4_rev_g', (Q4['rev']/Q4['rev_py']-1)*100); put('q4_segoi_g', (Q4['seg_oi']/Q4['seg_oi_py']-1)*100)
put('fy_eps_g', (FY['eps_adj']/FY['eps_adj_py']-1)*100); put('fy_eps_g_ex53', (FY['eps_adj_ex53']/FY['eps_adj_py']-1)*100)
put('svod_m_q4', Q4['svod_oi']/Q4['svod_rev']*100); put('svod_m_fy', 11.5); put('svod_oi_fy', 2.568); put('svod_oi_fy_py', 1.302)
put('ocf_m_fy', FY['ocf']/FY['rev']*100); put('nd_ebitda', ND/(FY['seg_oi'] + FY['da'])); put('nd_segoi', ND/FY['seg_oi'])
put('fcf_conv', FY['fcf']/(FY['eps_adj']*SH_DIL_FY/1000)*100)
put('payout_fcf', (FY['buyback'] + FY['div_paid'])/FY['fcf']*100)
# Segmentos FY2026 tal como se reportaron, sin la semana 53 y sin la participación en ganancias de A+E (vendida el 30-sep-2026)
SEG = dict(exp=dict(oi=11.191, w53=0.180, eq=0.0, rev=39.566), ent=dict(oi=5.443, w53=0.230, eq=0.408, rev=46.562), spo=dict(oi=3.094, w53=0.080, eq=0.0, rev=18.632))
for k, s in SEG.items(): s['adj'] = s['oi'] - s['w53'] - s['eq']; s['m'] = s['oi']/s['rev']*100
R['seg'] = SEG
put('seg_rev_tot', sum(s['rev'] for s in SEG.values())); put('seg_oi_tot', sum(s['oi'] for s in SEG.values()))
for k, s in SEG.items(): put(f'seg_{k}_share_oi', s['oi']/R['seg_oi_tot']*100); put(f'seg_{k}_share_rev', s['rev']/R['seg_rev_tot']*100)
RECAST = dict(exp=8.859, ent=7.367, spo=3.094)                    # FY2026 recalculado con el nuevo reporte (8-K 7.01 del 17-nov)
R['recast'] = RECAST

# Consenso (S&P Global vía stockanalysis.com, 21-nov-2026; misma fuente y mismo día que WMT)
C27, C28 = put('c27', 7.56309), put('c28', 8.51419); put('c27_n', 27)
Q_CONS = dict(q1=2.05511, q2=1.83959); R['q_cons'] = Q_CONS
put('c27_g', (C27/FY['eps_adj']-1)*100); put('c27_g_ex53', (C27/FY['eps_adj_ex53']-1)*100); put('c28_g', (C28/C27-1)*100)
NTM = put('eps_ntm', C27)                                        # DIS tiene los cuatro trimestres del FY2027 por reportar
put('pe_ntm', PRICE/NTM); put('pe_c28', PRICE/C28); put('pe_ttm', PRICE/FY['eps_adj_ex53'])
CONS = put('cons', 131.34); put('cons_med', 135.0); put('cons_low', 86.0); put('cons_high', 144.0); put('cons_n', 31)
put('cons_sb', 22); put('cons_b', 5); put('cons_h', 4); put('cons_s', 0); put('cons_ss', 1)
put('cons_gap', (CONS/PRICE-1)*100)

# ---------- Método 1a — DCF (misma estructura que septiembre, un año más adelante) ----------
BETA = put('beta', 1.30); put('beta_sa', 1.43)                    # 1.30 por el mismo criterio de sep; stockanalysis 1.43
KE = put('ke', RF + BETA*ERP)
TAX = put('tax', 21.0); KD_PRE = put('kd_pre', RF + 0.40); KD = put('kd', KD_PRE*(1-TAX/100))   # spread de sep: 5.19% antes de imp. con Rf 4.8%
E = PRICE*SH_OUT/1000; put('mkt_cap', E)
WD = put('wd', DEBT/(DEBT+E)*100)
WACC = put('wacc', (1-WD/100)*KE + WD/100*KD)
INTR = put('intr', FY['int_net']*(1-TAX/100))                     # intereses netos FY2026 después de impuestos (sep: 0.72 despejado)
# Año 1 = FY2027 anclado en la guía (OCF ~$20 mil millones, capex ~$9 mil millones); año 5 = FY2031 con el mismo crecimiento
# implícito del OCF (año 5 / año 1) que cada escenario tenía en septiembre; capex de septiembre sin cambios.
SC = {}
for k, (o1s, o5s, c1, c5, _, _) in SEP['sc'].items():
    o1 = {'bear': 19.0, 'base': 20.0, 'bull': 20.5}[k]
    SC[k] = dict(o1=o1, o5=o1*o5s/o1s, c1=c1, c5=c5, w=WACC + {'bear': 0.8, 'base': 0.0, 'bull': -0.8}[k], g=SEP['sc'][k][5], gr=(o5s/o1s)**0.25*100-100)
R['sc'] = SC
for k, s in SC.items():
    d = dcf(s['o1'], s['o5'], s['c1'], s['c5'], s['w'], s['g'], INTR, ND, NCI, SH_OUT, detail=True)
    put(f'dcf_{k}', d['ps']); put(f'dcf_{k}_tv', d['tv_share']); put(f'dcf_{k}_ev', d['ev'])
    if k == 'base': R['dcf_base_detail'] = d
put('dcf_pw', 0.25*R['dcf_bear'] + 0.45*R['dcf_base'] + 0.30*R['dcf_bull'])
put('dcf_avg3', (R['dcf_bear'] + R['dcf_base'] + R['dcf_bull'])/3)
b = SC['base']
def dcf_base(w=None, g=None, o5=None, intr=None, beta=None, erp=None):
    ww = w
    if ww is None and (beta is not None or erp is not None):
        ke = RF + (BETA if beta is None else beta)*(ERP if erp is None else erp); ww = (1-WD/100)*ke + WD/100*KD
    return dcf(b['o1'], b['o5'] if o5 is None else o5, b['c1'], b['c5'], WACC if ww is None else ww, b['g'] if g is None else g,
               INTR if intr is None else intr, ND, NCI, SH_OUT)
WG = [WACC-1, WACC-0.5, WACC, WACC+0.5, WACC+1]; R['grid_w'] = WG; R['grid_g'] = GG
R['grid'] = [[dcf_base(w=w, g=g) for g in GG] for w in WG]
assert abs(R['grid'][2][2] - R['dcf_base']) < 1e-9
put('dcf_beta_sa', dcf_base(beta=1.43)); put('dcf_erp_dam', dcf_base(erp=4.41)); put('dcf_intr_sep', dcf_base(intr=R['sep_intr']))
put('impl_wacc', solve(lambda w: dcf_base(w=w), 5, 14, PRICE, inc=False))
put('impl_o5', solve(lambda x: dcf_base(o5=x), 15, 60, PRICE))
put('impl_o_cagr', ((R['impl_o5']/b['o1'])**0.25-1)*100)
put('dcf_gap', (R['dcf_base']/PRICE-1)*100)

# ---------- Método 1b — Suma de partes por segmento (mismos múltiplos que septiembre) ----------
MULT = dict(exp=(14, 12, 16), ent=(11, 9, 13), spo=(10, 8, 12)); CORP_MULT = 10
def sotp(i):
    ev = sum(SEG[k]['adj']*MULT[k][i] for k in SEG) - FY['corp']*CORP_MULT
    return dict(ev=ev, eq=ev - ND - NCI, ps=(ev - ND - NCI)/SH_OUT*1000)
for i, nm in enumerate(('base', 'low', 'high')):
    s = sotp(i); put(f'sotp_{nm}', s['ps'])
    if nm == 'base': put('sotp_ev', s['ev']); put('sotp_eq', s['eq'])
for k in SEG: put(f'sotp_{k}_ev', SEG[k]['adj']*MULT[k][0])
put('sotp_corp_ev', -FY['corp']*CORP_MULT)
put('sotp_exp_share', R['sotp_exp_ev']/(R['sotp_exp_ev'] + R['sotp_ent_ev'] + R['sotp_spo_ev'])*100)
# Referencia: con la estructura nueva (Consumer Products dentro de Entertainment) y los mismos múltiplos
put('sotp_recast', ((RECAST['exp']-0.180)*14 + (RECAST['ent']-0.230)*11 + (RECAST['spo']-0.080)*10 - FY['corp']*10 - ND - NCI)/SH_OUT*1000)
put('sotp_gap', (R['sotp_base']/PRICE-1)*100)

# ---------- Método 2 — Comparables (P/E promedio NFLX / CMCSA / FOXA sobre el EPS de los próximos 4 trimestres) ----------
# Precio 20-nov-2026; consenso S&P Global (stockanalysis, 21-nov-2026). NTM = dos trimestres de consenso + la parte del año fiscal
# que completa cuatro (misma regla que WMT). FOXA cierra el año en junio y ya reportó el 1T FY2027 ($2.54, año electoral).
PEERS = dict(
    NFLX=dict(name='Netflix', px=56.73, ntm=0.67580 + 0.92839 + 0.5*3.77134, f1=3.57147, f2=3.77134),
    CMCSA=dict(name='Comcast', px=24.90, ntm=0.60696 + 0.79585 + 0.5*3.52187, f1=3.49915, f2=3.52187),
    FOXA=dict(name='Fox Corp.', px=62.91, ntm=(5.61667 - 2.54) + 0.25*5.59, f1=5.61667, f2=5.59))
for p in PEERS.values(): p['pe'] = p['px']/p['ntm']
R['peers'] = PEERS
PE_AVG = put('peer_pe_avg', sum(p['pe'] for p in PEERS.values())/3)
COMP = put('comp', PE_AVG*NTM)
put('comp_low', min(p['pe'] for p in PEERS.values())*NTM); put('comp_high', max(p['pe'] for p in PEERS.values())*NTM)
put('comp_xnflx', (PEERS['CMCSA']['pe'] + PEERS['FOXA']['pe'])/2*NTM)
put('comp_gap', (COMP/PRICE-1)*100)

# ---------- Método 3 — Reversión, ventana limpia (últimos cuatro cierres de trimestre fiscal) ----------
# P/E = precio de cierre (Yahoo) / EPS ajustado de los cuatro trimestres terminados en esa fecha (comunicados de Disney).
EPSQ = {'1T25': 1.76, '2T25': 1.45, '3T25': 1.61, '4T25': 1.11, '1T26': 1.63, '2T26': 1.57, '3T26': 2.06, '4T26': 1.77}
assert abs(sum(EPSQ[q] for q in ('1T25', '2T25', '3T25', '4T25')) - 5.93) < 0.005
assert abs(sum(EPSQ[q] for q in ('1T26', '2T26', '3T26', '4T26')) - 7.02) < 0.015
WIN = [('2025-12-26', 113.56, ['2T25', '3T25', '4T25', '1T26'], 0.0), ('2026-03-27', 92.42, ['3T25', '4T25', '1T26', '2T26'], 0.0),
       ('2026-06-26', 98.79, ['4T25', '1T26', '2T26', '3T26'], 0.0), ('2026-10-02', 102.19, ['1T26', '2T26', '3T26', '4T26'], 0.18)]
R['rev_window'] = []
for dt, px, qs, w53 in WIN:
    ttm = sum(EPSQ[q] for q in qs) - w53
    R['rev_window'].append(dict(date=dt, px=px, ttm=ttm, pe=px/ttm))
PE_REV = put('pe_rev', sum(x['pe'] for x in R['rev_window'])/4)
EPS_TTM = put('eps_ttm', FY['eps_adj_ex53'])                     # TTM sin la semana 53 (la misma base del último P/E)
REV = put('rev', PE_REV*EPS_TTM)
put('rev_low', min(x['pe'] for x in R['rev_window'])*EPS_TTM); put('rev_high', max(x['pe'] for x in R['rev_window'])*EPS_TTM)
put('rev_with53', PE_REV*FY['eps_adj'])
put('rev_ntm', PE_REV*NTM)                                       # referencia: el mismo múltiplo sobre el EPS de los próximos 12 meses
put('rev_gap', (REV/PRICE-1)*100)

# ---------- Blend ----------
V = dict(dcf=R['dcf_base'], sotp=R['sotp_base'], comp=COMP, rev=REV, cons=CONS)
BLEND = put('blend', sum(W[k]*V[k] for k in W))
put('blend_gap', (BLEND/PRICE-1)*100)
for k in W: put(f'contrib_{k}', W[k]*V[k])
IND = ('dcf', 'sotp', 'comp'); ANC = ('rev', 'cons')
put('indep', sum(W[k]*V[k] for k in IND)/sum(W[k] for k in IND)); put('anch', sum(W[k]*V[k] for k in ANC)/sum(W[k] for k in ANC))
put('blend_simple', sum(V.values())/5)
# Antes → ahora
SEPV = dict(dcf=P['base'], sotp=P['sotp'], comp=P['comp'], rev=P['rev'], cons=P['cons'])
for k in W: put(f'chg_{k}', V[k] - SEPV[k]); put(f'chg_contrib_{k}', W[k]*(V[k] - SEPV[k]))
put('blend_chg_vs_w', BLEND - R['sep_blend_w']); put('blend_chg_vs_pub', BLEND - P['blend'])
put('blend_chg_pct_w', (BLEND/R['sep_blend_w']-1)*100); put('price_chg', (PRICE/SEP['price']-1)*100)
put('sep_gap_pub', (P['blend']/SEP['price']-1)*100)
assert abs(sum(R[f'chg_contrib_{k}'] for k in W) - R['blend_chg_vs_w']) < 1e-9
# Rendimientos
put('div_fy27', 2.00); put('div_fy26', 1.50); put('div_yield', 2.00/PRICE*100)
put('fcf_guide', 11.0); put('fcf_yield_guide', 11.0/E*100); put('buyback_fy27', 9.0)

json.dump(R, open(HERE/'resultados.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False, default=float)
if __name__ == '__main__':
    for k, v in R.items():
        if isinstance(v, (int, float)): print(f'{k:22s} {v:,.4f}')
    print('peers', {k: round(p['pe'], 2) for k, p in PEERS.items()})
    print('window', [(x['date'], round(x['pe'], 2)) for x in R['rev_window']])
    print('sep grid resid', R['sep_grid_resid'])
