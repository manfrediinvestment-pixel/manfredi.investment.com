# Modelo de valuación PG (The Procter & Gamble Company) — todos los números derivados del informe salen de acá.
# Marco: informe-consumo-masivo, sub-industria cuidado personal y del hogar (HPC). Año fiscal julio-junio.
#
# El modelo de septiembre (edición FY2026, precio 25-sep-2026) no quedó guardado en el repo: se reconstruyó desde el HTML
# publicado. `run(SEP)` lo reproduce al centavo (assert contra PUB_SEP) y `run(NOV)` arma la edición 1T FY2027.
# Fuentes: 10-K FY2026 (4-ago-2026), 10-Q 1T FY2027 (22-oct-2026), comunicados 8-K ítem 2.02 (1T FY2017 a 1T FY2027),
# 8-K de emisiones de deuda (30-oct, 2-nov y 3-nov-2026), Yahoo, Nasdaq/Zacks (data/nasdaq_eps.json), stockanalysis
# (S&P Global; data/sa_stats.json), FactSet Earnings Insight (6-nov-2026). Corte de precios: cierre 12-nov-2026.
import json, datetime, statistics as st, os, copy
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
TXT = 'PG_PRICE' not in os.environ   # los assert que atan frases del texto a números solo corren con el precio de corte

# ---------------- EPS core trimestral (comunicados 8-K ítem 2.02), año fiscal julio-junio ----------------
EPS_Q = {2017:[1.03,1.08,0.96,0.85], 2018:[1.09,1.19,1.00,0.94], 2019:[1.12,1.25,1.06,1.10], 2020:[1.37,1.42,1.17,1.16],
         2021:[1.63,1.64,1.26,1.13], 2022:[1.61,1.66,1.33,1.21], 2023:[1.57,1.59,1.37,1.37], 2024:[1.83,1.84,1.52,1.40],
         2025:[1.93,1.88,1.54,1.48], 2026:[1.99,1.88,1.59,1.43]}
FY_CORE = {2020:5.12, 2021:5.66, 2022:5.81, 2023:5.90, 2024:6.59, 2025:6.83, 2026:6.89}
for y, v in FY_CORE.items(): assert abs(sum(EPS_Q[y]) - v) < 0.011, (y, sum(EPS_Q[y]))

def monthly_closes():
    d = json.load(open('yh/PG.mo.json'))['chart']['result'][0]; out = {}
    for ts, c in zip(d['timestamp'], d['indicators']['quote'][0]['close']):
        t = datetime.datetime.fromtimestamp(ts, datetime.UTC)
        if c: out[(t.year, t.month)] = c
    return out
CLOSES = monthly_closes()
def qclose(fy, q):  # cierre del trimestre fiscal q (0 = jul-sep) del año fiscal fy
    return CLOSES[(fy-1 if q < 2 else fy, [9, 12, 3, 6][q])]

# ---------------- Edición de septiembre (datos publicados el 28-sep-2026) ----------------
SEP = dict(
    ed='sep', price=146.23, rf=5.18, erp=5.0, tax=20.0, kd_spread=0.40,
    betas={'CL':0.32,'KMB':0.27,'CLX':0.54,'CHD':0.47,'KVUE':0.43,'UL':0.45}, beta_own=0.38,
    debt=11.296+22.842, cash=9.942, leases=1.028, nci=0.0, sh_dil=2412.7,
    mcap=339.27,   # capitalización de la fuente al 25-sep (no publicada): despejada, las 25 celdas de la grilla la acotan a 339.255-339.29: reproduce WACC, FCF yield y EV/EBITDA
    rev0=87.032, ebitda=20.497+3.160, sbc=0.524,
    vol=0.5, mix=0.4, m_base=22.5, m_bear=21.5, m_fy26=(19.556+0.688)/87.032*100,   # septiembre redondeó la mezcla (0.375 -> 0.4) y el margen (22.55 -> 22.5)
    c1=6.98, c2=7.40, g1=(88.78/87.032-1)*100, g2=(91.46/88.78-1)*100,   # consenso FY2027/FY2028 (stockanalysis): EPS y ventas
    peers={'CL':dict(pe=21.91,ev=14.41,vol=0.9), 'KMB':dict(pe=14.06,ev=10.93,vol=0.3), 'CLX':dict(pe=14.47,ev=11.80,vol=None),
           'CHD':dict(pe=24.69,ev=18.34,vol=4.3), 'UL':dict(pe=16.32,ev=13.02,vol=5.5)},
    eps_fill='fy27', rev_first=(2017, 0), rev_last=(2026, 3), spx_pe=19.2, spx_pe10=19.0,
    cons=160.61, cons_low=143.0, cons_high=186.0,
)

# ---------------- Edición 1T FY2027 (corte: cierre del 12-nov-2026) ----------------
NQ = json.load(open('data/nasdaq_eps.json')); SA = json.load(open('data/sa_stats.json'))
def nq(t, i): return NQ[t][i][1]
def yh_close(t, day):
    d = json.load(open(f'yh/{t}.d.json'))['chart']['result'][0]
    rows = [(datetime.datetime.fromtimestamp(a, datetime.UTC).date().isoformat(), c) for a, c in zip(d['timestamp'], d['indicators']['quote'][0]['close']) if c]
    return [r for r in rows if r[0] <= day][-1][1]
CUT = '2026-11-12'
# Orgánico del último trimestre de cada par (comunicados de cada compañía; volumen como lo define cada una)
PEER_INFO = {
 'KO': dict(name='Coca-Cola', grp='bebidas', fy='dic', org='+7% (3T26)', vol=5.0, vol_t='+5% (cajas)'),
 'PEP':dict(name='PepsiCo', grp='bebidas', fy='dic', org='+3.1% (3T26)', vol=None, vol_t='+3% bebidas; +1% alimentos'),
 'CL': dict(name='Colgate-Palmolive', grp='hpc', fy='dic', org='+3.6% (3T26)', vol=1.7, vol_t='+1.7%'),
 'KMB':dict(name='Kimberly-Clark', grp='hpc', fy='dic', org='−1.3% (3T26)', vol=None, vol_t='n. c.*'),
 'CHD':dict(name='Church & Dwight', grp='hpc', fy='dic', org='+5.1% (3T26)', vol=4.6, vol_t='+4.6%'),
 'CLX':dict(name='Clorox', grp='hpc', fy='jun', org='+18% (1T FY27)', vol=None, vol_t='n. c.**'),
 'UL': dict(name='Unilever', grp='hpc', fy='dic', org='+5.2% (3T26)', vol=2.9, vol_t='+2.9%'),
}
NOV = dict(
    ed='nov', price=float(os.environ.get('PG_PRICE', yh_close('PG', CUT))), rf=5.103, erp=5.0,
    tax=20.5,          # tasa efectiva core guiada FY2027: 20%-21% (22-oct-2026)
    kd_spread=0.40,
    betas={t: SA[t]['beta'] for t in ('CL','KMB','CHD','CLX','UL')}, beta_own=SA['PG']['beta'],
    betas_all={t: SA[t]['beta'] for t in PEER_INFO},
    debt=17.028+21.897, cash=15.365, leases=0.887, nci=0.239, sh_dil=2407.2, sh_out=2317.783,
    rev0=87.032, sbc=0.524+0.098-0.121,
    c1=nq('PG',0), c2=nq('PG',1), c3=nq('PG',2), cons=174.04, cons_low=151.0, cons_high=190.0, cons_med=176.0,
    spx_pe=17.7, spx_pe10=19.1, eps_fill='q1fy27', rev_first=(2017, 1), rev_last=(2027, 0),
)
# EBITDA core de los últimos doce meses = resultado operativo core + D&A (10-K y comunicados del 1T)
NOV['ebitda'] = (20.497 + 6.035 - 5.972) + (3.160 + 0.810 - 0.761)
NOV['mcap'] = NOV['price']*NOV['sh_out']/1000

# Descomposición del orgánico (comunicados; desde el 1T FY2027 P&G publica décimas): vol, precio, mezcla, orgánico, FX, reportado
ORGQ = {'1T25':(1,1,0,2,-1,-1), '2T25':(2,0,1,3,0,2), '3T25':(0,1,0,1,-2,-2), '4T25':(0,1,1,2,0,2), '1T26':(0,1,1,2,1,3),
        '2T26':(-1,1,0,0,1,1), '3T26':(2,1,0,3,4,7), '4T26':(0,0,0,0,1,2), '1T27':(2.4,0.4,1.1,4.0,0.0,4.0)}
Q8 = ['2T25','3T25','4T25','1T26','2T26','3T26','4T26','1T27']; Q4 = Q8[4:]
def avg(qs, i): return st.mean(ORGQ[q][i] for q in qs)
NOV['vol'] = avg(Q8, 0); NOV['mix'] = avg(Q8, 2)
# Margen de flujo operativo: año real (FY2026, OCF ajustado por el último pago del impuesto de transición) + guía FY2027
OCF26, CAPEX26, TT26 = 19.556, 4.409, 0.688
NE_G = 6.62*1.03*NOV['sh_dil']/1000 + 0.098        # EPS diluido guiado +1%/+5% (medio 3%) x acciones + minoritarios
REV_G = NOV['rev0']*1.03                            # ventas totales guiadas +2%/+4% (incluye Thorne desde el 1-oct)
OCF_G = 0.875*NE_G + 0.05*REV_G                     # FCF = 85%-90% de la utilidad neta; capex 4.5%-5.5% de las ventas
NOV['m_g27'] = OCF_G/REV_G*100
NOV['m_fy26'] = (OCF26+TT26)/NOV['rev0']*100
NOV['m_base'] = (OCF26+TT26+OCF_G)/(NOV['rev0']+REV_G)*100
NOV['m_bear'] = NOV['m_g27']
NOV['g1'] = (89.79/87.032-1)*100; NOV['g2'] = (92.60/89.79-1)*100   # consenso de ventas S&P Global FY2027/FY2028

PRICE_BASE = [1.0, 1.5, 2.0, 2.0, 2.0]; PRICE_BEAR = [1.0, 1.0, 1.5, 1.5, 1.5]; PRICE_BULL = [1.5, 2.0, 2.5, 2.5, 2.5]
T = [0.375, 1.25, 2.25, 3.25, 4.25]   # valuación al 30-sep-2026: FY2027 = 3 trimestres (oct-jun), mitad de período
YEARS = [2027, 2028, 2029, 2030, 2031]

def run(D):
    M = {'ed': D['ed']}
    def put(k, v): M[k] = v; return v
    nov = D['ed'] == 'nov'
    P = put('price', D['price'])
    # ---- costo de capital
    bmed = put('beta_med', st.median(D['betas'].values())); bl = put('beta_adj', 0.67*bmed + 0.33)
    blo = put('beta_adj_own', 0.67*D['beta_own'] + 0.33); put('beta_own', D['beta_own'])
    floor = put('ke_floor', D['rf'] + 2.5)
    KE = put('ke', max(D['rf'] + bl*D['erp'], floor)); KE_OWN = put('ke_own', max(D['rf'] + blo*D['erp'], floor))
    kd_pre = put('kd_pre', D['rf'] + D['kd_spread']); KD = put('kd', kd_pre*(1 - D['tax']/100))
    put('rf', D['rf']); put('tax', D['tax'])
    WD = put('wd', D['debt']/(D['debt'] + D['mcap'])*100)
    def wacc(ke): return (1-WD/100)*ke + WD/100*KD
    W = put('wacc', wacc(KE)); W_OWN = put('wacc_own', wacc(KE_OWN))
    if nov:
        b_all = put('beta_med_all', st.median(D['betas_all'].values()))
        put('wacc_all', wacc(max(D['rf'] + (0.67*b_all+0.33)*D['erp'], floor)))
    ND = put('net_debt', D['debt'] - D['cash']); put('debt', D['debt']); put('cash', D['cash'])
    NDL = put('net_debt_l', ND + D['leases']); put('leases', D['leases']); put('nci', D['nci'])
    SH = put('sh_dil', D['sh_dil']); put('mcap', D['mcap'])
    # ---- DCF
    SC = {'bear': dict(vol=D['vol']-1.0, price=PRICE_BEAR, mix=D['mix']-0.2, ocf=[D['m_bear']]*5, cap=[5.5]*5, dw=0.5, g=2.0),
          'base': dict(vol=D['vol'], price=PRICE_BASE, mix=D['mix'], ocf=[D['m_base']]*5, cap=[5.0]*5, dw=0.0, g=2.5),
          'bull': dict(vol=D['vol']+1.0, price=PRICE_BULL, mix=D['mix']+0.1, ocf=[D['m_base']+0.25*i for i in range(5)],
                       cap=[4.75, 4.5, 4.5, 4.5, 4.5], dw=-0.5, g=3.0)}
    def dcf(sc, w=None, g=None, dvol=0.0, ocf=None, sbc=0.0, detail=False):
        s = SC[sc]; w = W + s['dw'] if w is None else w; g = s['g'] if g is None else g
        r = D['rev0']; pv = 0; rows = []
        for i in range(5):
            gr = s['vol'] + dvol + s['price'][i] + s['mix']
            r *= 1 + gr/100
            m = (ocf[i] if ocf else s['ocf'][i]) - s['cap'][i]
            f = r*(m - sbc)/100     # sbc: compensación en acciones como % de las ventas (chequeo)
            p = f*(0.75 if i == 0 else 1)/(1 + w/100)**T[i]; pv += p
            rows.append(dict(g=gr, rev=r, fcf=f, pv=p))
        tv = f*(1 + g/100)/((w - g)/100)/(1 + w/100)**4.75
        ev = pv + tv; eq = ev - ND - D['nci']; fv = eq/SH*1000
        if detail: return dict(fv=fv, ev=ev, pv=pv, tv=tv, tvpct=tv/ev*100, rows=rows, eq=eq, w=w, g=g,
                               cagr=((r/D['rev0'])**0.2 - 1)*100)
        return fv
    for k in SC:
        d = dcf(k, detail=True)
        for kk in ('fv', 'ev', 'pv', 'tv', 'tvpct', 'eq', 'w', 'g', 'cagr'): put(f'dcf_{k}_{kk}', d[kk])
        put(f'dcf_{k}', d['fv']); M[f'dcf_{k}_rows'] = d['rows']
        put(f'dcf_{k}_vol', SC[k]['vol']); put(f'dcf_{k}_mix', SC[k]['mix']); put(f'dcf_{k}_ocf0', SC[k]['ocf'][0])
        put(f'dcf_{k}_ocf4', SC[k]['ocf'][4]); put(f'dcf_{k}_org27', SC[k]['vol']+SC[k]['price'][0]+SC[k]['mix'])
        put(f'dcf_{k}_org29', SC[k]['vol']+SC[k]['price'][2]+SC[k]['mix'])
    DCF = M['dcf_base']
    put('m_base', D['m_base']); put('m_bear', D['m_bear']); put('m_fy26', D['m_fy26']); put('vol', D['vol']); put('mix', D['mix'])
    put('dcf_gap', (DCF/P-1)*100)
    put('dcf_prob', 0.25*M['dcf_bear'] + 0.45*DCF + 0.30*M['dcf_bull'])
    put('dcf_simple', (M['dcf_bear'] + DCF + M['dcf_bull'])/3)
    put('dcf_own', dcf('base', w=W_OWN)); put('dcf_own_diff', M['dcf_own'] - DCF)
    put('dcf_m26', dcf('base', ocf=[D['m_fy26']]*5)); put('dcf_mg', dcf('base', ocf=[D['m_bear']]*5))
    put('dcf_vm2', dcf('base', dvol=-2)); put('dcf_vp2', dcf('base', dvol=2)); put('dcf_v0', dcf('base', dvol=-D['vol']))
    put('dcf_vm2_pct', (M['dcf_vm2']/DCF-1)*100); put('dcf_vp2_pct', (M['dcf_vp2']/DCF-1)*100)
    put('dcf_sbc', dcf('base', sbc=D['sbc']/D['rev0']*100) - DCF); put('dcf_sbc_pct', M['dcf_sbc']/DCF*100); put('sbc', D['sbc'])
    WG = [W-1, W-0.5, W, W+0.5, W+1]; GG = [1.5, 2.0, 2.5, 3.0, 3.5]
    M['grid'] = [[dcf('base', w=w, g=g) for g in GG] for w in WG]; M['grid_w'] = WG
    put('grid_wm05_pct', (M['grid'][1][2]/DCF-1)*100); put('grid_wp05_pct', (M['grid'][3][2]/DCF-1)*100)
    def solve(f, lo, hi, target):
        for _ in range(200):
            mid = (lo+hi)/2
            if (f(mid) - target)*(f(lo) - target) > 0: lo = mid
            else: hi = mid
        return (lo+hi)/2
    put('rev_wacc', solve(lambda w: dcf('base', w=w), 4.0, W, P)); put('rev_wacc_diff', W - M['rev_wacc'])
    put('rev_g', solve(lambda g: dcf('base', g=g), 2.5, W-0.3, P))
    put('rev_vol', D['vol'] + solve(lambda dv: dcf('base', dvol=dv), 0.0, 20.0, P))
    put('rev_vol_x', M['rev_vol']/D['vol'])
    # ---- Comparables
    NTM = put('eps_ntm', 0.75*D['c1'] + 0.25*D['c2']); put('c1', D['c1']); put('c2', D['c2'])
    put('pe_ntm_now', P/NTM); put('pe_fy2', P/D['c2'])
    EB = put('ebitda', D['ebitda'])
    if not nov:   # regla de septiembre: promedio simple, P/E y EV/EBITDA forward aplicados al FY2028 y descontados un año
        pes = [p['pe'] for p in D['peers'].values()]; evs = [p['ev'] for p in D['peers'].values()]
        pe_m = put('peer_pe', st.mean(pes)); ev_m = put('peer_ev', st.mean(evs))
        eb28 = put('ebitda_fy2', EB*(1+D['g1']/100)*(1+D['g2']/100))
        disc = 1 + KE/100
        put('comp_pe', pe_m*D['c2']/disc)
        def ev_ps(m, eb): return (m*eb - NDL)/SH*1000
        put('comp_ev', ev_ps(ev_m, eb28)/disc)
        put('comp_low', (st.median(pes)*NTM + ev_ps(st.median(evs), EB*(1+D['g1']/100)))/2)
        put('comp_high', (max(pes)*D['c2']/disc + ev_ps(max(evs), eb28)/disc)/2)
        put('pg_evx', (D['mcap'] + NDL)/(EB*(1+D['g1']/100)))
    else:         # regla vigente de la skill (tras KO): mediana, P/E sobre EPS de los próximos 12 meses, EV/EBITDA de 12 meses
        PE = {}
        for t, info in PEER_INFO.items():
            p = dict(info); px = yh_close(t, CUT); sa = SA[t]
            e1, e2, e3 = nq(t, 0), nq(t, 1), nq(t, 2)
            p['ntm'] = 0.25*e1 + 0.75*e2 if info['fy'] == 'dic' else 0.75*e1 + 0.25*e2
            p['px'] = px; p['pe'] = px/p['ntm']; p['g2'] = ((e3/e1)**0.5 - 1)*100
            r = px/sa['px_sa']; ev = sa['ev'] + sa['mcap']*(r-1)       # EV de stockanalysis llevado al cierre de corte
            p['evx'] = sa['evx']*ev/sa['ev']; p['dy'] = sa['dy']/r if sa['dy'] else 0.0; p['fcfy'] = sa['fcfy']/r
            p['beta'] = sa['beta']; p['e1'], p['e2'], p['e3'] = e1, e2, e3
            PE[t] = p
        M['peers'] = PE
        ev_ok = {t: p for t, p in PE.items() if t != 'KMB'}   # KMB: EV con Kenvue (cerró 2-nov), EBITDA de 12 meses sin Kenvue
        pes = sorted(p['pe'] for p in PE.values()); evs = sorted(p['evx'] for p in ev_ok.values())
        pe_m = put('peer_pe', st.median(pes)); ev_m = put('peer_ev', st.median(evs))
        put('peer_pe_mean', st.mean(pes)); put('peer_ev_mean', st.mean(evs))
        put('peer_pe_min', pes[0]); put('peer_pe_max', pes[-1]); put('peer_ev_min', evs[0]); put('peer_ev_max', evs[-1])
        put('kmb_evx', PE['KMB']['evx'])
        def ev_ps(m): return (m*EB - NDL - D['nci'])/SH*1000
        put('comp_pe', pe_m*NTM); put('comp_ev', ev_ps(ev_m))
        put('comp_low', (pes[0]*NTM + ev_ps(evs[0]))/2); put('comp_high', (pes[-1]*NTM + ev_ps(evs[-1]))/2)
        put('comp_mean', (st.mean(pes)*NTM + ev_ps(st.mean(evs)))/2)
        hpc = [p for p in PE.values() if p['grp'] == 'hpc']; hpc_ev = [p for t, p in ev_ok.items() if p['grp'] == 'hpc']
        put('peer_pe_hpc', st.median(p['pe'] for p in hpc)); put('peer_ev_hpc', st.median(p['evx'] for p in hpc_ev))
        put('comp_hpc', (M['peer_pe_hpc']*NTM + ev_ps(M['peer_ev_hpc']))/2)
        put('pg_evx', (D['mcap'] + NDL + D['nci'])/EB)
        put('pg_dy', 4.354/P*100); put('pg_fcfy', SA['PG']['fcfy']*SA['PG']['px_sa']/P)
        M['peer_pe_min_n'] = min(PE.values(), key=lambda p: p['pe'])['name']; M['peer_pe_max_n'] = max(PE.values(), key=lambda p: p['pe'])['name']
        M['peer_ev_min_n'] = min(ev_ok.values(), key=lambda p: p['evx'])['name']; M['peer_ev_max_n'] = max(ev_ok.values(), key=lambda p: p['evx'])['name']
        # sin cada par (el que más mueve el resultado se reporta en el texto)
        for t in PE:
            rest = [p for k, p in PE.items() if k != t]; rest_ev = [p for k, p in ev_ok.items() if k != t]
            put(f'comp_ex_{t}', (st.median(p['pe'] for p in rest)*NTM + ev_ps(st.median(p['evx'] for p in rest_ev)))/2)
        # regresiones (criterio declarado: R² >= 0.5 con pendiente positiva, con todos y sin el punto más extremo)
        def reg(xs, ys):
            mx, my = st.mean(xs), st.mean(ys); sxy = sum((x-mx)*(y-my) for x, y in zip(xs, ys))
            sxx = sum((x-mx)**2 for x in xs); syy = sum((y-my)**2 for y in ys)
            b = sxy/sxx; return dict(slope=b, icpt=my-b*mx, r2=sxy**2/(sxx*syy), n=len(xs))
        def reg_ex(items, key):
            mx = st.mean(p[key] for _, p in items); ext = max(items, key=lambda kp: abs(kp[1][key]-mx))
            rest = [kp for kp in items if kp[0] != ext[0]]
            r = reg([p[key] for _, p in rest], [p['pe'] for _, p in rest]); r['dropped'] = PE[ext[0]]['name']; return r
        allp = list(PE.items()); volp = [(k, p) for k, p in allp if p['vol'] is not None]
        M['reg_g'] = reg([p['g2'] for _, p in allp], [p['pe'] for _, p in allp]); M['reg_g_ex'] = reg_ex(allp, 'g2')
        M['reg_v'] = reg([p['vol'] for _, p in volp], [p['pe'] for _, p in volp]); M['reg_v_ex'] = reg_ex(volp, 'vol')
        ok = lambda a, b: all(M[k]['r2'] >= 0.5 and M[k]['slope'] > 0 for k in (a, b))
        M['reg_ok'] = ok('reg_g', 'reg_g_ex') or ok('reg_v', 'reg_v_ex')
        assert not M['reg_ok'], 'una regresión sostiene un ajuste: reescribir el Método 2'
        put('pg_g2', ((D['c3']/D['c1'])**0.5 - 1)*100); put('c3', D['c3'])
        put('pg_pe_vs_med', (M['pe_ntm_now']/pe_m - 1)*100); put('pg_ev_vs_med', (M['pg_evx']/ev_m - 1)*100)
    put('peer_pe_used', M['peer_pe']); COMP = put('comp', (M['comp_pe'] + M['comp_ev'])/2); put('comp_gap', (COMP/P-1)*100)
    # ---- Reversión: P/E forward "ex post" propio (precio / EPS core de los 12 meses siguientes)
    E = {y: list(v) for y, v in EPS_Q.items()}
    if D['eps_fill'] == 'fy27':
        s26 = [x/sum(E[2026]) for x in E[2026]]; E[2027] = [D['c1']*s for s in s26]
    else:   # 1T FY2027 real; resto del año = consenso menos el 1T con la estacionalidad del FY2026; FY2028 igual
        s26 = [x/sum(E[2026]) for x in E[2026]]
        rest = D['c1'] - 2.00; E[2027] = [2.00] + [rest*s/sum(s26[1:]) for s in s26[1:]]
        E[2028] = [D['c2']*s for s in s26]
    put('eps_q2_q4_27', sum(E[2027][1:])) if nov else None
    seq = [(y, q) for y in range(2017, 2029) for q in range(4)]
    win = []
    for i, (y, q) in enumerate(seq):
        if (y, q) < D['rev_first'] or (y, q) > D['rev_last']: continue
        nx = seq[i+1:i+5]; ntm = sum(E[a][b] for a, b in nx); px = qclose(y, q)
        lbl = ['sep', 'dic', 'mar', 'jun'][q] + '-' + str(y-1 if q < 2 else y)[2:]
        win.append(dict(fy=y, q=q, lbl=lbl, price=px, ntm=ntm, pe=px/ntm, excl=(y == 2019)))
    M['rev_window'] = win
    clean = [w for w in win if not w['excl']]
    PEC = put('rev_pe_avg', st.mean(w['pe'] for w in clean)); put('rev_n', len(clean)); put('rev_n_all', len(win))
    put('rev_pe_all', st.mean(w['pe'] for w in win)); put('rev_pe_ex24', st.mean(w['pe'] for w in clean if w['fy'] != 2024))
    put('rev_pe_min', min(w['pe'] for w in clean)); put('rev_pe_max', max(w['pe'] for w in clean))
    M['rev_by_year'] = {str(y): dict(avg=st.mean(w['pe'] for w in win if w['fy'] == y), lo=min(w['pe'] for w in win if w['fy'] == y),
                        hi=max(w['pe'] for w in win if w['fy'] == y), n=sum(1 for w in win if w['fy'] == y)) for y in sorted({w['fy'] for w in win})}
    R1 = put('rev1', PEC*NTM); put('rev1_all', M['rev_pe_all']*NTM); put('rev_excl_effect', R1 - M['rev1_all'])
    REL = put('rel_avg', PEC/D['spx_pe10']); put('rel_now', M['pe_ntm_now']/D['spx_pe'])
    R2 = put('rev2', REL*D['spx_pe']*NTM); put('rel_pe', REL*D['spx_pe'])
    put('spx_pe', D['spx_pe']); put('spx_pe10', D['spx_pe10'])
    put('spx_vs_avg', (D['spx_pe']/D['spx_pe10']-1)*100); put('pg_vs_avg', (M['pe_ntm_now']/PEC-1)*100)
    REVV = put('rev', (R1 + R2)/2); put('rev_gap', (REVV/P-1)*100)
    put('rev_low', M['rev_pe_min']*NTM); put('rev_high', M['rev_pe_max']*NTM)
    put('rev_all', (M['rev1_all'] + M['rev_pe_all']/D['spx_pe10']*D['spx_pe']*NTM)/2)
    if nov:
        # regla de cambio de escalón (simétrica, tras PEP): ¿todos los cierres desde un punto por encima del máximo (o por
        # debajo del mínimo) de los cinco años previos durante ocho trimestres o más?
        hits = []
        for i in range(20, len(win)-7):
            prev = [w['pe'] for w in win[i-20:i]]; rest = [w['pe'] for w in win[i:]]
            if min(rest) > max(prev) or max(rest) < min(prev): hits.append(win[i]['lbl'])
        M['step_hits'] = hits; assert not hits, hits
        # pandemia (regla ex post de KO): efecto de excluir los cierres cuyo EPS de 12 meses incluye el 3T-4T FY2020
        cov = [w for w in clean if not (w['fy'] == 2020 and w['q'] <= 2)]
        put('rev_pe_nocovid', st.mean(w['pe'] for w in cov))
        put('spx_pe_cut', D['spx_pe']*7592.40/7353.73)   # P/E del S&P al cierre de corte con el EPS de FactSet del 5-nov
        put('rev2_spx_cut', REL*M['spx_pe_cut']*NTM)
    # ---- Consenso
    CONS = put('cons', D['cons']); put('cons_low', D['cons_low']); put('cons_high', D['cons_high']); put('cons_gap', (CONS/P-1)*100)
    # ---- Blend
    Wt = {'dcf': 0.15, 'comp': 0.25, 'rev': 0.35, 'cons': 0.25}
    V = {'dcf': DCF, 'comp': COMP, 'rev': REVV, 'cons': CONS}
    BL = put('blend', sum(Wt[k]*V[k] for k in Wt)); put('blend_gap', (BL/P-1)*100)
    for k in Wt: put(f'ap_{k}', Wt[k]*V[k])
    put('indep', (0.15*DCF + 0.25*COMP)/0.40); put('anch', (0.35*REVV + 0.25*CONS)/0.60)
    put('indep_gap', (M['indep']/P-1)*100); put('anch_gap', (M['anch']/P-1)*100)
    put('blend_rev_all', BL + 0.35*(M['rev_all'] - REVV))
    if nov:
        put('blend_comp_mean', BL + 0.25*(M['comp_mean'] - COMP))
        for t in PEER_INFO: put(f'blend_ex_{t}', BL + 0.25*(M[f'comp_ex_{t}'] - COMP))
        put('blend_comp_hpc', BL + 0.25*(M['comp_hpc'] - COMP))
        put('blend_own', BL + 0.15*(M['dcf_own'] - DCF))
        put('blend_spx_cut', BL + 0.35*((R1 + M['rev2_spx_cut'])/2 - REVV))
    return M

# ---------------- 1) Reproducción de septiembre ----------------
PUB_SEP = dict(dcf_base=110.77, dcf_bear=78.54, dcf_bull=158.58, dcf_base_ev=291.4, dcf_bear_ev=213.7, dcf_bull_ev=406.8,
               dcf_base_tvpct=77.6, dcf_bear_tvpct=73.6, dcf_bull_tvpct=82.1, dcf_prob=117.05, dcf_simple=115.96,
               dcf_own=114.90, dcf_m26=116.02, dcf_mg=103.86, dcf_vm2=100.42, dcf_vp2=121.90, dcf_v0=108.11, dcf_sbc=-4.16,
               rev_wacc=6.71, rev_g=3.94, rev_vol=6.4, wacc=7.95, ke=8.30, kd=4.46, wd=9.1, wacc_own=7.77,
               comp_pe=124.97, comp_ev=120.67, comp=122.82, comp_low=117.68, comp_high=166.77, pg_evx=15.10,
               rev_pe_avg=22.58, rev1=159.98, rev2=161.66, rev=160.82, rev_low=122.09, rev_high=203.33, rel_avg=1.188,
               rel_now=1.075, rev_pe_all=22.27, rev_pe_ex24=22.53, rev_excl_effect=2.19,
               blend=143.76, indep=118.30, anch=160.73, blend_rev_all=142.99, pe_ntm_now=20.64)
MS = run(SEP)
MS['grid_check'] = [[round(v, 2) for v in r] for r in MS['grid']]
assert MS['grid_check'][2] == [95.46, 102.47, 110.77, 120.74, 132.95], MS['grid_check'][2]
assert MS['grid_check'][0] == [114.63, 124.96, 137.60, 153.45, 173.88], MS['grid_check'][0]
assert MS['grid_check'][4] == [81.45, 86.47, 92.27, 99.05, 107.06], MS['grid_check'][4]
diffs = []
for k, v in PUB_SEP.items():
    nd = len(str(v).split('.')[1]) if '.' in str(v) else 0
    got = round(MS[k], nd)
    if k in ('dcf_base_ev', 'dcf_bear_ev', 'dcf_bull_ev'): got = round(MS[k], 1)
    if abs(got - v) > 1e-9: diffs.append((k, MS[k], v))
# Residuos que no se pudieron cerrar (centavos en sub-cifras; las cuatro cifras del blend y el blend dan exacto):
TOL = {'dcf_bull': 0.006, 'dcf_m26': 0.006, 'comp': 0.009, 'comp_ev': 0.02, 'comp_low': 0.025, 'comp_high': 0.03}
MS['sep_residuals'] = {k: (MS[k], v) for k, v, in [(k, PUB_SEP[k]) for k in TOL]}
diffs = [d for d in diffs if not (d[0] in TOL and abs(d[1] - d[2]) <= TOL[d[0]])]
assert not diffs, diffs
pe_pub = [22.55, 20.56, 21.76, 20.65, 21.41, 21.32, 18.14, 17.23, 17.41, 18.57, 20.56, 21.42, 23.12, 22.3, 19.33, 21.13, 24.64, 24.58, 23.64, 23.22, 24.23, 28.7, 26.62, 24.37, 20.5, 23.64, 22.67, 23.03, 21.8, 21.77, 24.04, 24.15, 25.14, 24.33, 24.56, 23.12, 22.22, 20.65, 20.75, 21.01]
assert [round(w['pe'], 2) for w in MS['rev_window']] == pe_pub
# Diferencias con el HTML de septiembre que no son de redondeo (se declaran en el README):
#  - el texto dice mezcla de 0.38% y margen 22.5%; el cálculo usó 0.4 (la tabla de supuestos) y 22.5 redondeado de 22.55.
#  - capitalización de la fuente ($339.27 mil millones) no figura en el HTML: se despejó (la de 2,324.4 M de acciones del 10-K
#    da WACC 7.954% y Base $110.75).
#  - las regresiones de P/E contra crecimiento del EPS (R² 0.12 / 0.24) no se pueden reproducir: el crecimiento de cada par no
#    quedó publicado. La de volumen sí (abajo).
def reg2(xs, ys):
    mx, my = st.mean(xs), st.mean(ys); sxy = sum((x-mx)*(y-my) for x, y in zip(xs, ys))
    return sxy**2/(sum((x-mx)**2 for x in xs)*sum((y-my)**2 for y in ys))
vp = [(p['vol'], p['pe']) for p in SEP['peers'].values() if p['vol'] is not None]
assert round(reg2(*zip(*vp)), 2) == 0.05
vp2 = [x for x in vp if x[0] != 5.5]; assert round(reg2(*zip(*vp2)), 2) == 0.63

# ---------------- 2) Edición 1T FY2027 ----------------
M = run(NOV)
P = M['price']
M['m_g27'] = NOV['m_g27']; M['ne_g27'] = NE_G; M['rev_g27'] = REV_G; M['ocf_g27'] = OCF_G; M['ebitda_ttm'] = NOV['ebitda']
M['sep'] = {k: MS[k] for k in ('blend', 'dcf_base', 'comp', 'rev', 'cons', 'indep', 'anch', 'price', 'blend_gap', 'rev1', 'rev2',
                               'wacc', 'eps_ntm', 'rev_pe_avg', 'dcf_bear', 'dcf_bull', 'pe_ntm_now')}
# Puente contra septiembre: el modelo nuevo con el precio de septiembre aísla cuánto se movió por datos/método y cuánto por
# precio (el precio solo entra por los pesos de mercado del WACC; comparables, reversión y consenso no lo usan).
NOV_SEP_PX = dict(NOV, price=SEP['price'], mcap=SEP['price']*NOV['sh_out']/1000)
M_sp = run(NOV_SEP_PX)
M['bridge_model'] = M_sp['blend'] - MS['blend']; M['bridge_price'] = M['blend'] - M_sp['blend']
M['blend_at_sep_price'] = M_sp['blend']
for k in ('dcf_base', 'comp', 'rev', 'cons'): M[f'chg_{k}'] = M[k] - MS[k]
M['chg_blend'] = M['blend'] - MS['blend']; M['chg_price'] = (P/SEP['price']-1)*100
# Anti-circularidad: con el precio +25%, comparables, reversión y consenso no se mueven
M_hi = run(dict(NOV, price=P*1.25, mcap=P*1.25*NOV['sh_out']/1000))
for k in ('comp', 'rev', 'cons'): assert abs(M_hi[k] - M[k]) < 1e-9, k
M['dcf_at_p125'] = M_hi['dcf_base']
# Cambios de método respecto de septiembre, medidos sobre los datos de noviembre
M['meth_comp_mean'] = M['comp_mean'] - M['comp']          # promedio en lugar de mediana
M['m_base_sep_rule'] = (17.817+0.562+OCF26+TT26)/(84.284+87.032)*100   # regla de septiembre: FY2025 + FY2026 reales
M['dcf_sep_margin'] = None
NOV_M = dict(NOV, m_base=M['m_base_sep_rule']); M['dcf_sep_margin'] = run(NOV_M)['dcf_base']
M['meth_margin'] = M['dcf_base'] - M['dcf_sep_margin']
M['blend_sep_margin'] = M['blend'] + 0.15*(M['dcf_sep_margin'] - M['dcf_base'])

# ---------------- Datos descriptivos del trimestre (comunicado del 22-oct-2026 y 10-Q) ----------------
def pct(a, b): return (a/b - 1)*100
M['org8'] = {q: dict(zip(('vol', 'price', 'mix', 'org', 'fx', 'rep'), ORGQ[q])) for q in Q8}
for i, k in enumerate(('vol', 'price', 'mix', 'org')): M[f'{k}_8q'] = avg(Q8, i); M[f'{k}_4q'] = avg(Q4, i)
M['vol_8q_sep'] = 0.5; M['price_8q_sep'] = 0.75
Q1 = dict(sales=23.276, sales0=22.386, cogs=11.678, cogs0=10.887, sga=5.661, sga0=5.643, oi=5.937, oi0=5.856,
          core_gp=11.642, core_gp0=11.537, core_sga=5.607, core_sga0=5.566, core_oi=6.035, core_oi0=5.972,
          ne=4.731, ne0=4.750, eps=1.97, eps0=1.95, ceps=2.00, ceps0=1.99, ocf=5.767, ocf0=5.408, capex=1.366, capex0=1.200,
          div=2.603, div0=2.549, buy=1.250, buy0=1.250, da=0.810, da0=0.761, ne_tot=4.757, restr=0.192)
M['q1'] = Q1
M['q1_sales_g'] = pct(Q1['sales'], Q1['sales0'])
for a, b, k in (('sales', 'cogs', 'gm'),):
    M['q1_gm'] = (Q1['sales']-Q1['cogs'])/Q1['sales']*100; M['q1_gm0'] = (Q1['sales0']-Q1['cogs0'])/Q1['sales0']*100
M['q1_cgm'] = Q1['core_gp']/Q1['sales']*100; M['q1_cgm0'] = Q1['core_gp0']/Q1['sales0']*100
M['q1_csga'] = Q1['core_sga']/Q1['sales']*100; M['q1_csga0'] = Q1['core_sga0']/Q1['sales0']*100
M['q1_com'] = Q1['core_oi']/Q1['sales']*100; M['q1_com0'] = Q1['core_oi0']/Q1['sales0']*100
M['q1_om'] = Q1['oi']/Q1['sales']*100; M['q1_om0'] = Q1['oi0']/Q1['sales0']*100
M['q1_ne_g'] = pct(Q1['ne'], Q1['ne0']); M['q1_eps_g'] = pct(Q1['eps'], Q1['eps0']); M['q1_ceps_g'] = pct(Q1['ceps'], Q1['ceps0'])
M['q1_fcf'] = Q1['ocf'] - Q1['capex']; M['q1_fcf0'] = Q1['ocf0'] - Q1['capex0']
M['q1_fcf_conv'] = M['q1_fcf']/Q1['ne_tot']*100
M['q1_ret'] = Q1['div'] + Q1['buy']; M['q1_ret_fcf'] = M['q1_ret']/M['q1_fcf']*100
M['q1_capex_pct'] = Q1['capex']/Q1['sales']*100
# Segmentos 1T FY2027: ventas, resultado antes de impuestos y utilidad neta (US$ millones); volumen, precio, mezcla, orgánico
SEGQ = {'Belleza':(4410,1139,868,2.2,0.7,2.5,5.4,6.4,0.0), 'Cuidado personal y aseo':(1889,619,477,-0.4,3.5,1.5,4.5,4.0,0.2),
        'Salud':(3318,1029,783,-2.9,2.8,2.8,2.7,3.1,0.0), 'Tela y hogar':(8205,2080,1601,4.3,-0.3,0.8,4.8,4.2,0.0),
        'Bebés, femenino y familia':(5322,1390,1060,2.3,-1.2,1.8,3.0,2.9,0.0)}
# variación de la utilidad neta del segmento (%, comunicado)
SEG_NE_G = {'Belleza':-1, 'Cuidado personal y aseo':3, 'Salud':9, 'Tela y hogar':3, 'Bebés, femenino y familia':-4}
tot_s = sum(v[0] for v in SEGQ.values()); tot_n = sum(v[2] for v in SEGQ.values())
M['seg'] = {k: dict(sales=v[0], ebt=v[1], ne=v[2], vol=v[3], price=v[4], mix=v[5], org=v[6], rep=v[7], s_pct=v[0]/tot_s*100,
                    n_pct=v[2]/tot_n*100, ebt_m=v[1]/v[0]*100, ne_g=SEG_NE_G[k]) for k, v in SEGQ.items()}
M['seg_tot_sales'] = tot_s; M['seg_tot_ne'] = tot_n
# Balance (30-sep-2026 vs 30-jun-2026) y métricas
BS = dict(cash=(15.365, 9.942), dcur=(17.028, 11.296), ltd=(21.897, 22.842), inv=(8.485, 8.170), ap=(17.056, 16.306),
          gw=(41.197+21.359, 41.276+21.444), eq=(55.337, 54.311), assets=(133.132, 126.521))
M['bs'] = BS
M['nd_sep'] = BS['dcur'][0] + BS['ltd'][0] - BS['cash'][0]; M['nd_jun'] = BS['dcur'][1] + BS['ltd'][1] - BS['cash'][1]
M['nd_sep_m'] = M['nd_sep']*1000; M['nd_jun_m'] = M['nd_jun']*1000
M['nd_ebitda'] = M['nd_sep']/M['ebitda']; M['thorne'] = 3.9
M['nd_ebitda_pf'] = (M['nd_sep'] + M['thorne'])/M['ebitda']
M['gw_pct'] = BS['gw'][0]/BS['assets'][0]*100
M['bonds_usd'] = 0.75+0.75+1.25+1.25+0.352231; M['bonds_eur'] = 0.75+1.0+0.75+0.75
# Flujo de caja (10-K y comunicados)
CF = {'FY2022':(16.723,3.156,8.770,10.003), 'FY2023':(16.848,3.062,8.999,7.353), 'FY2024':(19.846,3.322,9.312,5.006),
      'FY2025':(17.817,3.773,9.872,6.500), 'FY2026':(19.556,4.409,10.232,5.028)}
M['cf'] = {k: dict(ocf=v[0], capex=v[1], fcf=v[0]-v[1], div=v[2], buy=v[3], ret=(v[2]+v[3])/(v[0]-v[1])*100) for k, v in CF.items()}
M['ttm_ocf'] = 19.556 + Q1['ocf'] - Q1['ocf0']; M['ttm_capex'] = 4.409 + Q1['capex'] - Q1['capex0']
M['ttm_fcf'] = M['ttm_ocf'] - M['ttm_capex']; M['ttm_rev'] = 87.032 + Q1['sales'] - Q1['sales0']
M['ttm_ocf_m'] = M['ttm_ocf']/M['ttm_rev']*100
# Dividendo
DPS_Q = 1.0885; M['dps'] = 4*DPS_Q; M['div_yield'] = M['dps']/P*100; M['payout_ntm'] = M['dps']/M['eps_ntm']*100
M['div_10y_cagr'] = ((4.354/2.6782)**(1/10) - 1)*100   # DPS anualizado abr-2026 vs. abr-2016 ($0.6695 x 4)
M['ret_guide'] = 10 + 5; M['fcfy_ttm'] = M['ttm_fcf']/M['mcap']*100
M['fcf_c27'] = 15.43; M['fcf_c27_m'] = M['fcf_c27']/89.79*100; M['ocf_c27_m'] = M['fcf_c27_m'] + 5.0
M['dy_spread'] = M['div_yield'] - M['rf']; M['fcfy_spread'] = M['fcfy_ttm'] - M['rf']
# Guía FY2027: vientos en contra (US$ millones después de impuestos) en julio y en octubre
M['hw_jul'] = dict(com=1000, int=150, nonop=150, fx=50, eps=0.56); M['hw_oct'] = dict(com=1400, int=300, nonop=150, fx=50, eps=0.79)
M['hw_jul_tot'] = sum(v for k, v in M['hw_jul'].items() if k != 'eps'); M['hw_oct_tot'] = sum(v for k, v in M['hw_oct'].items() if k != 'eps')
M['guide_eps_mid'] = 7.00; M['c1_vs_mid'] = (M['c1']/7.00-1)*100; M['eps_g27'] = (M['c1']/6.89-1)*100; M['eps_g28'] = (M['c2']/M['c1']-1)*100
M['eps_g29'] = (M['c3']/M['c2']-1)*100
M['rev_c27'] = 89.79; M['rev_c28'] = 92.60; M['rev_c27_g'] = (89.79/87.032-1)*100; M['rev_c28_g'] = (92.60/89.79-1)*100
M['dcf_rev27_vs_cons'] = (M['dcf_base_rows'][0]['rev']/89.79-1)*100
M['restr_q1'] = 0.192; M['restr_fy26'] = 1.2; M['restr_core_q1'] = 0.03
# Sparkline (7 cierres mensuales hasta el corte) para la tarjeta del sitio
sp = sorted(CLOSES.items())[-7:]; M['spark'] = [round(v, 2) for _, v in sp[:-1]] + [round(P, 2)]

# ---------------- Frases del texto atadas a números (solo con el precio de corte) ----------------
def chk(cond, frase):   # frases del texto atadas a números (solo con el precio de corte)
    if TXT: assert cond, frase

# ---------------- Formatos para el gráfico y salida ----------------
def jn(xs, d=2): return ', '.join(('%.*f' % (d, x)).rstrip('0').rstrip('.') if d else str(x) for x in xs)
M['js_pe'] = jn([w['pe'] for w in M['rev_window']]); M['js_pe_avg'] = jn([M['rev_pe_avg']]*len(M['rev_window']))
M['js_pe_lbl'] = json.dumps([w['lbl'] if w['q'] == 0 else '' for w in M['rev_window']])
M['rev_first_lbl'] = M['rev_window'][0]['lbl']; M['rev_last_lbl'] = M['rev_window'][-1]['lbl']
for i, k in enumerate(('vol', 'price', 'mix', 'org')): M[f'js_{k}8'] = jn([ORGQ[q][i] for q in Q8], 1)
M['js_q8'] = json.dumps(['%sT FY%s' % (q[0], q[2:]) for q in Q8])
SEG_ORDER = ['Belleza', 'Cuidado personal y aseo', 'Salud', 'Tela y hogar', 'Bebés, femenino y familia']
for k in ('vol', 'price', 'mix', 'org'): M[f'js_seg_{k}'] = jn([M['seg'][s][k] for s in SEG_ORDER], 1)
cs = sorted([(p['name'], p['pe'], False) for p in M['peers'].values()] + [('Procter & Gamble', M['pe_ntm_now'], True)], key=lambda x: -x[1])
M['js_comps_lbl'] = json.dumps([c[0] for c in cs], ensure_ascii=False); M['js_comps_val'] = jn([c[1] for c in cs])
M['js_comps_col'] = ', '.join('PALETTE.navy' if c[2] else 'PALETTE.blueLight' for c in cs)
M['pg_pe_rank'] = 1 + sum(1 for c in cs if c[1] > M['pe_ntm_now'])          # puesto de PG en el grupo (1 = más caro)
M['n_peers'] = len(M['peers'])
M['seg_order'] = SEG_ORDER
# cambios por método (aporte al blend) contra septiembre
for k, w in (('dcf_base', 0.15), ('comp', 0.25), ('rev', 0.35), ('cons', 0.25)): M[f'chg_ap_{k}'] = w*M[f'chg_{k}']
M['spx_pe_sep'] = SEP['spx_pe']; M['cons_sep'] = SEP['cons']
M['rev2_at_sep_spx'] = M['rel_avg']*SEP['spx_pe']*M['eps_ntm']      # lectura 2 con el P/E del S&P de septiembre
M['pe_prem_peers_sep'] = (MS['pe_ntm_now']/MS['peer_pe']-1)*100
M['pg_pe_vs_avg_sep'] = (MS['pe_ntm_now']/MS['rev_pe_avg']-1)*100
M['blend_q'] = (M['blend']/M['eps_ntm'])                              # P/E implícito en el blend
M['thorne_pct'] = 3.9/87.032*100
M['q1_ret_guide_pct'] = M['q1_ret']/15*100
M['vol_sep_bull'] = 1.5
M['rel_prem'] = (M['rel_avg']-1)*100
chk(M['peer_pe_min'] < M['pe_ntm_now'] and sorted(p['pe'] for p in M['peers'].values())[3] < M['pe_ntm_now'] < M['peers']['CL']['pe'], 'entre Clorox y Colgate: por encima de cuatro de siete')
M['pandemic_effect'] = (M['rev_pe_nocovid'] - M['rev_pe_avg'])*M['eps_ntm']
chk(M['blend'] < P and M['indep'] < P and M['anch'] < P and M['cons'] > P, 'los tres métodos propios por debajo del precio; solo el consenso arriba')
chk(M['vol_8q'] > M['vol_8q_sep'] and M['price_8q'] < M['price_8q_sep'], 'más volumen y menos precio que en septiembre')
chk(M['pe_ntm_now'] > M['rev_pe_avg'] and M['rel_now'] > M['rel_avg'], 'PG cotiza por encima de su promedio propio y relativo')
chk(M['rev'] < M['sep']['rev'] and M['rev1'] < M['sep']['rev1'], 'la reversión baja')
chk(M['dcf_vp2'] < P and M['dcf_bull'] < P, 'ni +2 puntos de volumen ni el Bull llegan al precio')
chk(M['peer_pe_max_n'] == 'Church & Dwight' and M['peer_pe_min_n'] == 'Kimberly-Clark', 'extremos del grupo')
chk(M['peer_ev_max_n'] == 'Coca-Cola' and M['peer_ev_min_n'] == 'PepsiCo', 'extremos EV/EBITDA')
chk(M['pg_pe_rank'] == 4, 'PG es el cuarto más caro de ocho')
chk(abs(M['bridge_price']) < 0.5, 'el precio casi no mueve el blend')
chk(M['dcf_base_rows'][0]['g'] > 1 and M['dcf_base_rows'][0]['g'] < 3, 'orgánico FY2027 del Base dentro de la guía')
chk(abs(M['m_base'] - M['ocf_c27_m']) < 0.1, 'el margen Base coincide con el consenso de FCF')
json.dump(M, open('model.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False, default=float)
json.dump(MS, open('model_sep.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False, default=float)
if TXT:
    for k in ('price', 'wacc', 'ke', 'dcf_bear', 'dcf_base', 'dcf_bull', 'comp_pe', 'comp_ev', 'comp', 'rev1', 'rev2', 'rev', 'cons',
              'blend', 'blend_gap', 'indep', 'anch', 'm_base', 'm_bear', 'vol', 'mix', 'eps_ntm', 'pe_ntm_now', 'rev_pe_avg',
              'peer_pe', 'peer_ev', 'pg_evx', 'bridge_model', 'bridge_price', 'meth_margin', 'meth_comp_mean', 'blend_comp_mean',
              'blend_ex_KMB', 'blend_ex_KO', 'blend_ex_PEP', 'blend_ex_CHD', 'blend_comp_hpc', 'rev_wacc', 'rev_g', 'rev_vol'):
        print(f'{k:16s} {M[k]:10.3f}')
    print('peers', {t: (round(p['pe'], 2), round(p['evx'], 2), round(p['g2'], 2)) for t, p in M['peers'].items()})
    print('reg', {k: (round(M[k]['r2'], 2), round(M[k]['slope'], 2), M[k].get('dropped')) for k in ('reg_g', 'reg_g_ex', 'reg_v', 'reg_v_ex')})
    print('septiembre reproducido: 0 diferencias en', len(PUB_SEP), 'cifras + grilla + 40 P/E + regresión de volumen')
