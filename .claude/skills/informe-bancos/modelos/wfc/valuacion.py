"""Valuación de WFC (Wells Fargo) — informe-bancos, actualización 3T 2026 (7-nov-2026).

Correr:  python valuacion.py
Primero reproduce al centavo el caso de septiembre-2026 (blend $92.08, DDM $93.27, RIM $102.60,
P/TBV $97.19) y después calcula la versión 3T26 publicada en informes/wfc.html.

Fuentes (todas oficiales salvo precio/consenso):
- 8-K 13-oct-2026 (EX-99.1 release, EX-99.2 supplement, EX-99.3 presentación) y 10-Q 3T26 (28-oct-2026):
  CET1 definitivo 10.03%, RWA Standardized $1,341.3B, TBVPS $44.46, SCB 2.5% hasta 31-dic-2027.
- XBRL companyfacts (valor de la presentación más reciente; WFC no reexpresó 2025):
  NetIncomeLoss, InterestIncomeExpenseNet, NoninterestIncome, NoninterestExpense,
  ProvisionForLoanLeaseAndOtherLosses, PaymentsForRepurchaseOfCommonStock, PaymentsOfDividendsCommonStock (YTD → trimestre).
- Precios de cierre sin ajustar por dividendos (Yahoo chart 'close'), 6-nov-2026. ^TNX 4.859%.
- TBVPS de cierre de año: supplements 4T24 (8-K 15-ene-2025: 4T23 $39.23, 4T24 $41.24) y 3T26 (4T25 $45.02).
- Consenso: stockanalysis.com (S&P Global, 27 analistas) — PT $97.38, rango $88–$108; EPS FY27E de peers igual que jpm/bac.
"""
def lin(a, b, n=5): return [a + (b - a) * i / (n - 1) for i in range(n)]

def ddm(eps0, g1, g5, p1, p5, k, gT):
    gs, ps = lin(g1, g5), lin(p1, p5); e = eps0; pv = 0
    for t in range(5):
        e *= 1 + gs[t]; d = e * ps[t]; pv += d / (1 + k) ** (t + 1)
    tv = d * (1 + gT) / (k - gT) / (1 + k) ** 5
    return pv + tv, tv / (pv + tv)

def rim(bv0, r1, r5, b1, b5, k, gT):
    rs, bs = lin(r1, r5), lin(b1, b5); bv = bv0; pv = 0
    for t in range(5):
        ri = (rs[t] - k) * bv; pv += ri / (1 + k) ** (t + 1); bv *= 1 + bs[t]
    tv = ri * (1 + gT) / (k - gT) / (1 + k) ** 5
    v = bv0 + pv + tv
    return v, tv / v

def ptbv(r, k, g): return (r - g) / (k - g)

W = [.1, .1, .1, .2, .3, .2]  # DDM, RIM, P/TBV just., comps, reversión, consenso

def caso(P, TBV, EPS0, EPSfwd, k, ddm_s, rim_s, pt_s, peers, hist, cons, gT, label):
    print(f'\n===== {label} =====  P={P} TBV={TBV} EPS0={EPS0} COE base={k["base"]}')
    D = {s: ddm(EPS0, *ddm_s[s], k[s], gT[s]) for s in k}
    R = {s: rim(TBV, *rim_s[s], k[s], gT[s]) for s in k}
    J = {s: ptbv(pt_s[s], k[s], gT[s]) for s in k}
    for s in k:
        print(f'  {s:4}  DDM {D[s][0]:8.2f} (TV {D[s][1]*100:4.0f}%)   RIM {R[s][0]:8.2f} (TV {R[s][1]*100:4.0f}%)   P/TBV {J[s]:.3f}x {J[s]*TBV:8.2f}')
    ptb = [p / t for p, t, e in peers.values()]; pe = [p / e for p, t, e in peers.values()]
    for n, (p, t, e) in peers.items(): print(f'  peer {n}: P/TBV {p/t:.3f}x  P/E {p/e:.2f}x')
    a1, a2 = sum(ptb) / len(ptb), sum(pe) / len(pe)
    c1, c2 = a1 * TBV, a2 * EPSfwd; comp = (c1 + c2) / 2
    print(f'  comps P/TBV {a1:.3f}x -> {c1:.2f} | P/E {a2:.3f}x -> {c2:.2f} | prom {comp:.2f}')
    mult = [p / t for p, t in hist]; rev = sum(mult) / len(mult) * TBV
    print('  reversión', [f'{m:.4f}x={m*TBV:.2f}' for m in mult], f'prom {sum(mult)/len(mult):.4f}x -> {rev:.2f}')
    V = [D['base'][0], R['base'][0], J['base'] * TBV, comp, rev, cons]
    blend = sum(w * v for w, v in zip(W, V))
    print('  métodos', [round(v, 2) for v in V], ' vs mercado', [f'{100*(v/P-1):+.1f}%' for v in V])
    print(f'  BLEND {blend:.2f}  ({100*(blend/P-1):+.1f}% vs {P})')
    ev = .25 * (D['bear'][0] + R['bear'][0]) / 2 + .45 * (D['base'][0] + R['base'][0]) / 2 + .30 * (D['bull'][0] + R['bull'][0]) / 2
    imp = (P / TBV) * (k['base'] - gT['base']) + gT['base']
    print(f'  EV prob {ev:.2f} | P/TBV mercado {P/TBV:.3f}x -> ROTCE implícito {imp*100:.2f}% | simple avg {sum(V)/6:.2f}')
    return dict(D=D, R=R, J=J, comp=(c1, c2, comp, a1, a2), rev=(mult, rev), V=V, blend=blend, ev=ev)

gT = {'bear': .025, 'base': .032, 'bull': .038}

# ---------- 1) Reproducción de septiembre-2026 (informe publicado 16-sep-2026) ----------
sep = caso(P=89.72, TBV=46.13, EPS0=6.88, EPSfwd=7.20,
           k={'bear': .1075, 'base': .0975, 'bull': .0875},
           ddm_s={'bear': (.03, .03, .55, .40), 'base': (.13, .08, .85, .60), 'bull': (.18, .10, .80, .70)},
           rim_s={'bear': (.11, .09, .02, .01), 'base': (.155, .17, .06, .09), 'bull': (.19, .21, .09, .13)},
           pt_s={'bear': .09, 'base': .17, 'bull': .21},
           peers={'JPM': (352.49, 352.49/3.11, 352.49/14.7), 'BAC': (59.52, 59.52/2.03, 59.52/12.6), 'C': (136.17, 136.17/1.35, 136.17/12.2)},
           hist=[(49.22, 39.23), (70.24, 41.23), (93.20, 45.02)], cons=100.63, gT=gT,
           label='REPRO SEP-2026 (publicado: DDM 93.27 / RIM 102.60 / PTBV 97.19 / comps 97.27 / rev 77.32 / blend 92.08)')
assert abs(sep['blend'] / 92.08 - 1) < .005, 'no reproduce septiembre'

# ---------- 2) Datos 3T26 ----------
NI = [5361, 5253, 6407, 5951]            # 4T25..3T26, XBRL NetIncomeLoss
EPSq = [1.62, 1.60, 2.00, 1.87]
NII = [12331, 12096, 12317, 12517]
NONII = [36215 - (8654 + 9114 + 9486), 9350, 10305, 9353]
EXP = [13726, 14330, 13661, 13743]
PROV = [1040, 1135, 914, 1029]
BB = [17516 - 12516, 4000, 7015 - 4000, 9515 - 7015]   # recompras (caja) por trimestre
DV = [5434 - 4036, 1387, 2753 - 1387, 4261 - 2753]      # dividendos comunes (caja)
ROTCEq = [14.5, 14.5, 17.7, 16.3]
print('\nTTM: NI', sum(NI), 'EPS', round(sum(EPSq), 2), 'NII', sum(NII), 'NonII', sum(NONII), 'Rev', sum(NII) + sum(NONII),
      'Exp', sum(EXP), 'Efic %.1f%%' % (100 * sum(EXP) / (sum(NII) + sum(NONII))), 'Prov', sum(PROV))
print('Recompras', sum(BB), BB, 'Div', sum(DV), DV)
print('Payout total TTM %.1f%% | div %.1f%% | 3T26 solo %.1f%%' % (100 * (sum(BB) + sum(DV)) / sum(NI), 100 * sum(DV) / sum(NI), 100 * (BB[3] + DV[3]) / NI[3]))
print('ROTCE prom 4T: %.2f' % (sum(ROTCEq) / 4))
Rf, beta, ERP = .04859, .92, .05; print('COE CAPM %.2f%% -> 9.5%%' % (100 * (Rf + beta * ERP)))
print('CET1 10-Q: 134,561/1,341,319 = %.2f%% ; colchón vs 8.5%% = %.2f pts = $%.1fB' % (100 * 134561 / 1341319, 100 * 134561 / 1341319 - 8.5, (134561 / 1341319 - .085) * 1341.319))
print('CRE nonaccrual %.2f%% | C&I %.2f%% | comerciales YoY %.1f%% | consumo YoY %.1f%% | total YoY %.1f%%' % (
      100 * 2716 / 132020, 100 * 1372 / 499337, 100 * (647145 / 563465 - 1), 100 * (400968 / 379637 - 1), 100 * (1048113 / 943102 - 1)))
print('TBVPS QoQ %.1f%% YoY %.1f%%' % (100 * (44.46 / 46.13 - 1), 100 * (44.46 / 44.18 - 1)))

P = 83.94; TBV = 44.46; EPS0 = round(sum(EPSq), 2)
k = {'bear': .105, 'base': .095, 'bull': .085}
nov = caso(P=P, TBV=TBV, EPS0=EPS0, EPSfwd=8.01, k=k,
           ddm_s={'bear': (.03, .03, .55, .40), 'base': (.13, .08, .75, .60), 'bull': (.18, .10, .80, .70)},
           rim_s={'bear': (.11, .09, .02, .01), 'base': (.1575, .17, .06, .09), 'bull': (.19, .21, .09, .13)},
           pt_s={'bear': .09, 'base': .17, 'bull': .21},
           peers={'JPM': (334.49, 112.64, 25.57), 'BAC': (49.42, 29.14, 5.19), 'C': (119.05, 101.59, 13.06)},
           hist=[(49.22, 39.23), (70.24, 41.24), (93.20, 45.02)], cons=97.38, gT=gT, label='3T26 (nov-2026)')
print(f'\nBlend nov vs sep: {nov["blend"]:.2f} vs 92.08 ({100*(nov["blend"]/92.08-1):+.1f}%)')
print('Consenso upside %.1f%%' % (100 * (97.38 / P - 1)))

# Sensibilidad RIM Base (COE x g)
print('\nGrilla RIM Base')
for kk in [.085, .09, .095, .10, .105]:
    print(f'  {kk*100:.1f}%', [round(rim(TBV, .1575, .17, .06, .09, kk, g)[0], 2) for g in [.022, .027, .032, .037, .042]])

# Football field: rangos
print('\nFootball:', [(round(nov['D']['bear'][0], 2), round(nov['D']['bull'][0], 2)), (round(nov['R']['bear'][0], 2), round(nov['R']['bull'][0], 2)),
       (round(nov['J']['bear'] * TBV, 2), round(nov['J']['bull'] * TBV, 2)), (round(min(nov['comp'][:2]), 2), round(max(nov['comp'][:2]), 2)),
       (round(min(nov['rev'][0]) * TBV, 2), round(max(nov['rev'][0]) * TBV, 2)), (88, 108)])
