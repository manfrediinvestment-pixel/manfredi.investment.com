"""Valuación de Anthropic, PBC (ANT) — informe inicial (salida a bolsa 19-nov-2026).

Fuente de datos: prospecto final 424B4 (SEC EDGAR, CIK 2130357, presentado 19-nov-2026) y FWP de pricing del 18-nov-2026.
Todos los números del informe salen de este script:  python valuacion.py [precio]
"""
import json, sys

PRICE = float(sys.argv[1]) if len(sys.argv) > 1 else 97.03
IPO = 83.00

# ---------- Acciones (prospecto, "The Offering") ----------
A_PRE, N_PRE = 6_626_752_642, 5_323_285_271          # al 30-sep-2026, ya convertidas las preferidas, incl. Public Benefit Fund (846.8M N)
A_IPO, N_PP = 956_351_354, 313_253_007               # oferta primaria + colocación privada concurrente
BASIC = A_PRE + N_PRE + A_IPO + N_PP
OPTIONS, OPT_STRIKE = 1_774_342_693, 2.91
RSU = 1_026_660_010 + 47_041_287
AMZN_NOTES_EXTRA = 3_484_128_662 - 1_936_452_353      # conversión total de las notas de Amazon (hoy limitadas por tope)
MATCHING = 553_441_297 + 27_991_850                   # obligación de matching de donaciones ya devengada + emitida post 30-sep
ACQ = 561_963 + 848_882

def diluted(price):
    opt_net = OPTIONS * (1 - OPT_STRIKE / price)       # método del tesoro
    return BASIC + opt_net + RSU + AMZN_NOTES_EXTRA + MATCHING + ACQ

# ---------- Caja (pro forma ajustado, prospecto) ----------
CASH = 232.351   # $B: caja + inversiones CP al 30-sep-2026 + neto de la oferta y la colocación privada, menos retenciones de RSU
IPO_NET = 104.8  # $B neto de la oferta + colocación privada

# ---------- Ingresos reales ----------
Q = {'1T25':0.376,'2T25':0.787,'3T25':1.382,'4T25':2.040,'1T26':4.731,'2T26':11.555,'3T26':16.956}
REV_9M26 = 33.242
RUNRATE_SEP, RUNRATE_OCT = 71.0, 81.0
# 4T26 estimado: run-rate de octubre / 4, con ajuste estacional de fin de año (−20% durante 2 de 13 semanas, prospecto)
Q4_26 = RUNRATE_OCT / 4 * (1 - 0.20 * 2 / 13)
REV_2026 = REV_9M26 + Q4_26

# ---------- DCF: horizonte explícito de 10 años (2027-2036) ----------
SCEN = {
  'bear': dict(g=[0.90,0.35,0.22,0.15,0.10,0.08,0.06,0.05,0.04,0.03],
               m=[0.06,0.09,0.11,0.13,0.14,0.15,0.16,0.17,0.18,0.18], wacc=0.125, tg=0.030),
  'base': dict(g=[1.40,0.60,0.40,0.28,0.20,0.15,0.12,0.10,0.08,0.06],
               m=[0.10,0.15,0.19,0.22,0.24,0.26,0.27,0.28,0.28,0.28], wacc=0.115, tg=0.035),
  'bull': dict(g=[1.70,0.75,0.50,0.35,0.25,0.20,0.15,0.12,0.10,0.08],
               m=[0.13,0.19,0.24,0.28,0.31,0.33,0.34,0.35,0.35,0.35], wacc=0.105, tg=0.040),
}
YEARS = list(range(2027, 2037))

def dcf(s, wacc=None, tg=None, price=PRICE, growth=None):
    wacc = s['wacc'] if wacc is None else wacc
    tg = s['tg'] if tg is None else tg
    g = s['g'] if growth is None else growth
    rev, revs, fcfs, pv = REV_2026, [], [], 0.0
    for i, (gi, mi) in enumerate(zip(g, s['m'])):
        rev *= 1 + gi
        revs.append(rev)
        f = rev * mi
        fcfs.append(f)
        pv += f / (1 + wacc) ** (i + 1)
    tv = fcfs[-1] * (1 + tg) / (wacc - tg)
    pv_tv = tv / (1 + wacc) ** len(g)
    ev = pv + pv_tv
    eq = ev + CASH
    return dict(fv=eq * 1e9 / diluted(price), ev=ev, tvshare=pv_tv / ev, revs=revs, fcfs=fcfs)

res = {k: dcf(v) for k, v in SCEN.items()}

# Grilla de sensibilidad (caso Base)
waccs = [0.105, 0.110, 0.115, 0.120, 0.125]
tgs = [0.025, 0.030, 0.035, 0.040, 0.045]
grid = [[round(dcf(SCEN['base'], w, t)['fv'], 2) for t in tgs] for w in waccs]

# DCF inverso: factor uniforme sobre el crecimiento 2028-2036 (2027 fijo en consenso) que iguala el precio
def solve_growth_factor():
    lo, hi = 0.0, 3.0
    for _ in range(80):
        mid = (lo + hi) / 2
        g = [SCEN['base']['g'][0]] + [x * mid for x in SCEN['base']['g'][1:]]
        if dcf(SCEN['base'], growth=g)['fv'] > PRICE: hi = mid
        else: lo = mid
    g = [SCEN['base']['g'][0]] + [x * lo for x in SCEN['base']['g'][1:]]
    return lo, g, dcf(SCEN['base'], growth=g)

inv_k, inv_g, inv_r = solve_growth_factor()

# Margen terminal que justifica el precio con el crecimiento Base
def solve_margin():
    lo, hi = 0.0, 0.8
    base = SCEN['base']
    for _ in range(80):
        mid = (lo + hi) / 2
        scale = mid / base['m'][-1]
        s = dict(base, m=[x * scale for x in base['m']])
        if dcf(s)['fv'] > PRICE: hi = mid
        else: lo = mid
    return lo
inv_margin = solve_margin()

# ---------- Método 2: comparables, EV / ventas del próximo año fiscal ----------
PEERS = {  # EV ($B, stockanalysis 19-nov-2026 / informes propios), ventas próximo año ($B, consenso S&P Global)
  'MSFT': dict(ev=3800.0, rev=395.97, growth=0.193, note='FY jun-2027'),
  'NVDA': dict(ev=148.56 * 24.186 - 65.36, rev=721.0, growth=0.70, note='FY ene-2028'),
  'PLTR': dict(ev=363.96, rev=13.11, growth=0.533, note='2027'),
}
for p in PEERS.values(): p['mult'] = p['ev'] / p['rev']
peer_avg = sum(p['mult'] for p in PEERS.values()) / len(PEERS)
REV_2027_BASE = res['base']['revs'][0]
def comps_fv(mult, price=PRICE): return (mult * REV_2027_BASE + CASH) * 1e9 / diluted(price)
comps = comps_fv(peer_avg)
comps_lo = comps_fv(min(p['mult'] for p in PEERS.values()))
comps_hi = comps_fv(max(p['mult'] for p in PEERS.values()))
comps_ex_pltr = comps_fv((PEERS['MSFT']['mult'] + PEERS['NVDA']['mult']) / 2)

# ---------- Método 3: múltiplo de sus propias rondas (reemplaza reversión histórica) ----------
ROUNDS = [  # post-money $B, run-rate $B anunciado por la compañía
  ('Serie F (sep-2025)', 183.0, 5.0),
  ('Serie G (feb-2026)', 380.0, 14.0),
  ('Serie H (may-2026)', 965.0, 47.0),
]
round_mults = [(n, pm, rr, pm / rr) for n, pm, rr in ROUNDS]
window = [m for n, pm, rr, m in round_mults if '2026' in n]      # ventana limpia: régimen 2026
win_mult = sum(window) / len(window)
own_fv = (win_mult * RUNRATE_OCT + IPO_NET) * 1e9 / diluted(PRICE)
own_lo = (min(window) * RUNRATE_OCT + IPO_NET) * 1e9 / diluted(PRICE)
own_hi = (max(window) * RUNRATE_OCT + IPO_NET) * 1e9 / diluted(PRICE)
ipo_mult = (IPO * diluted(IPO) / 1e9 - IPO_NET) / RUNRATE_OCT
mkt_mult = (PRICE * diluted(PRICE) / 1e9 - IPO_NET) / RUNRATE_OCT

# ---------- Método 4: precios objetivo iniciales ----------
TARGETS = [('Needham (Scott Berg)', 150.0), ('Melius Research (2 años)', 155.0), ('Citizens JMP (Patrick Walravens)', 125.0),
           ('New Street (Pierre Ferragu)', 105.0), ('Morningstar (fair value)', 92.0)]
cons = sum(t for _, t in TARGETS) / len(TARGETS)
cons_ex_melius = sum(t for n, t in TARGETS if 'Melius' not in n) / (len(TARGETS) - 1)

W = dict(dcf=0.15, comps=0.25, own=0.35, cons=0.25)
blend = W['dcf'] * res['base']['fv'] + W['comps'] * comps + W['own'] * own_fv + W['cons'] * cons
simple = (res['base']['fv'] + comps + own_fv + cons) / 4
pw = 0.25 * res['bear']['fv'] + 0.45 * res['base']['fv'] + 0.30 * res['bull']['fv']
blend_ex_cons = (W['dcf'] * res['base']['fv'] + W['comps'] * comps + W['own'] * own_fv) / (1 - W['cons'])
blend_bear = W['dcf'] * res['bear']['fv'] + W['comps'] * comps + W['own'] * own_fv + W['cons'] * cons
blend_ex_pltr = W['dcf'] * res['base']['fv'] + W['comps'] * comps_ex_pltr + W['own'] * own_fv + W['cons'] * cons

pct = lambda v: (v / PRICE - 1) * 100
out = dict(
  price=PRICE, diluted_shares_B=diluted(PRICE) / 1e9, basic_shares_B=BASIC / 1e9,
  mcap_basic_B=PRICE * BASIC / 1e9, mcap_diluted_B=PRICE * diluted(PRICE) / 1e9,
  ev_diluted_B=PRICE * diluted(PRICE) / 1e9 - CASH,
  rev_2026E=REV_2026, q4_26E=Q4_26, ttm=sum(list(Q.values())[-4:]),
  dcf={k: dict(fv=round(v['fv'], 2), pct=round(pct(v['fv']), 1), tv=round(v['tvshare'] * 100, 1),
               rev=[round(x, 1) for x in v['revs']], fcf=[round(x, 1) for x in v['fcfs']]) for k, v in res.items()},
  dcf_simple=round(sum(v['fv'] for v in res.values()) / 3, 2), dcf_pw=round(pw, 2),
  grid=grid, inv_growth_factor=round(inv_k, 3), inv_growth=[round(x * 100, 1) for x in inv_g],
  inv_rev_2036=round(inv_r['revs'][-1], 1), inv_margin=round(inv_margin * 100, 1),
  peers={k: dict(mult=round(v['mult'], 2), ev=round(v['ev'], 1)) for k, v in PEERS.items()},
  peer_avg=round(peer_avg, 2), comps=round(comps, 2), comps_lo=round(comps_lo, 2), comps_hi=round(comps_hi, 2),
  comps_ex_pltr=round(comps_ex_pltr, 2), ant_ev_rev27=round((PRICE * diluted(PRICE) / 1e9 - CASH) / REV_2027_BASE, 2),
  rounds=[(n, pm, rr, round(m, 1)) for n, pm, rr, m in round_mults], win_mult=round(win_mult, 2),
  own=round(own_fv, 2), own_lo=round(own_lo, 2), own_hi=round(own_hi, 2),
  ipo_mult=round(ipo_mult, 1), mkt_mult=round(mkt_mult, 1),
  cons=round(cons, 2), cons_ex_melius=round(cons_ex_melius, 2),
  blend=round(blend, 2), blend_pct=round(pct(blend), 1), simple=round(simple, 2),
  blend_ex_cons=round(blend_ex_cons, 2), blend_bear=round(blend_bear, 2), blend_ex_pltr=round(blend_ex_pltr, 2),
  pcts=dict(comps=round(pct(comps), 1), own=round(pct(own_fv), 1), cons=round(pct(cons), 1)),
)
print(json.dumps(out, indent=1, ensure_ascii=False))
json.dump(out, open(__file__.replace('valuacion.py', 'resultados.json'), 'w'), indent=1, ensure_ascii=False)
