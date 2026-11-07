"""Valuación de GS (Goldman Sachs) — informe-bancos, actualización 3T 2026 (7-nov-2026).

Correr:  python valuacion.py
Mismo modelo que modelos/wfc y modelos/c (DDM de payout total y RIM con trayectorias lineales
año 1 -> año 5, terminal de Gordon sobre el último flujo; P/TBV justificado con el COE y la g del
caso Base en los tres escenarios, como en sep-2026).

1) check_septiembre(): con los supuestos publicados el 11-sep-2026 (P $1,029.18, TBVPS propio
   $344.68, EPS TTM $64.79, COE 11.4%) este modelo da RIM Base $566.43 (publicado $564.39, +0.4%),
   P/TBV justificado $538.04 (igual al centavo) y DDM Base $647.83 (publicado $693.01, -6.5%).
   El DDM de sep no se guardó con script y no cierra con ninguna convención probada (trayectoria
   lineal / escalón de g y de payout, terminal sobre dividendo o sobre EPS, EPS TTM o FY26E); el
   "% del valor desde el terminal" sí coincide (69% vs 70% publicado). El blend de sep se reproduce
   al centavo con los valores publicados ($836.60); con los de este script daría $832.29 (-0.5%).
   Mismo tratamiento que C: se documenta la diferencia y se sigue con el modelo del panel.

2) Cambios de método de la versión 3T26 (no de supuestos):
   - TBVPS OFICIAL de la compañía (tangible common equity / basic shares, presentación y 10-Q),
     no el propio sobre acciones en circulación que usaba sep ($344.68 en 2T26 vs. $336.61 oficial).
   - Reversión con precios de cierre sin ajustar y TBVPS oficiales de cierre de año.
   - Comparables con P/E sobre EPS FY2027E (como JPM/BAC/C/WFC), ya no FY2026E.

Fuentes: 8-K del 13-oct-2026 (Ex. 99.1 comunicado, Ex. 99.2 presentación), 10-Q del 3T26 presentado
el 2-nov-2026 (CET1/RWA definitivos, requerimientos, SLR, TBVPS), 8-K de resultados 4T25/1T26/2T26,
10-K 2025 (ROTE anual 2023-2025, metas de ciclo), 8-K 4T24 (TBVPS 4T23 $292.52, 4T24 $316.02).
MS: 8-K del 14-oct-2026. Precios: Yahoo chart 'close' (sin ajustar) al 6-nov-2026; ^TNX 4.859%.
Consenso: stockanalysis.com (S&P Global, 26 analistas, 6-nov-2026). ROTE 2021 24.3% y 2022 11.0%: 8-K 4T22.
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
gT = {'bear': .025, 'base': .032, 'bull': .038}
DDM_S = {'bear': (-.15, .02, .50, .50), 'base': (0, .04, .80, .85), 'bull': (.08, .05, .90, 1.0)}
RIM_S = {'bear': (.12, .10, .02, .03), 'base': (.18, .16, .05, .06), 'bull': (.24, .22, .07, .09)}
PT_S = {'bear': .10, 'base': .16, 'bull': .22}


def valuar(P, TBV, EPS0, EPSfwd, k, peers, hist, cons, label):
    print(f'\n===== {label} =====  P={P} TBV={TBV} EPS0={EPS0} COE base={k["base"]}')
    D = {s: ddm(EPS0, *DDM_S[s], k[s], gT[s]) for s in k}
    R = {s: rim(TBV, *RIM_S[s], k[s], gT[s]) for s in k}
    J = {s: ptbv(PT_S[s], k['base'], gT['base']) for s in k}   # sep: COE/g Base en los 3 escenarios
    for s in k:
        print(f'  {s:4}  DDM {D[s][0]:9.2f} (TV {D[s][1]*100:3.0f}%)  RIM {R[s][0]:9.2f} (TV {R[s][1]*100:3.0f}%)  P/TBV {J[s]:.3f}x {J[s]*TBV:9.2f}')
    ap = []
    for n, (p, t, e) in peers.items():
        print(f'  peer {n}: P/TBV {p/t:.3f}x -> {p/t*TBV:.2f} | P/E {p/e:.3f}x -> {p/e*EPSfwd:.2f}')
        ap += [p / t * TBV, p / e * EPSfwd]
    comp = sum(ap) / len(ap)
    print(f'  comparables (promedio de {len(ap)} enfoques) {comp:.2f}  piso {min(ap):.2f} techo {max(ap):.2f}')
    mult = [p / t for p, t in hist]; m3 = sum(mult) / len(mult); rev = m3 * TBV
    print('  reversión', [f'{m:.3f}x={m*TBV:.2f}' for m in mult], f'prom {m3:.3f}x -> {rev:.2f}')
    V = [D['base'][0], R['base'][0], J['base'] * TBV, comp, rev, cons]
    blend = sum(w * v for w, v in zip(W, V))
    print('  métodos', [round(v, 2) for v in V], [f'{100*(v/P-1):+.1f}%' for v in V])
    print(f'  BLEND {blend:.2f}  ({100*(blend/P-1):+.1f}% vs {P})')
    ev = sum(w * (D[s][0] + R[s][0]) / 2 for s, w in (('bear', .25), ('base', .45), ('bull', .30)))
    imp = (P / TBV) * (k['base'] - gT['base']) + gT['base']
    print(f'  EV prob DDM+RIM {ev:.2f} ({100*(ev/blend-1):+.1f}% vs blend) | P/TBV {P/TBV:.3f}x -> ROTCE implícito {imp*100:.2f}%')
    return dict(D=D, R=R, J=J, comp=(comp, min(ap), max(ap), ap), rev=(mult, m3, rev), V=V, blend=blend, ev=ev, imp=imp)


# ---------- 1) Septiembre-2026 ----------
k_sep = {'bear': .124, 'base': .114, 'bull': .104}
print('\n===== CHECK SEP-2026 (publicado: DDM 252.58/693.01/1144.48, RIM 270.16/564.39/1047.97, P/TBV 285.83/538.04/790.24) =====')
for s in k_sep:
    d = ddm(64.79, *DDM_S[s], k_sep[s], gT[s]); r = rim(344.68, *RIM_S[s], k_sep[s], gT[s])
    print(f'  {s:4}  DDM {d[0]:8.2f} (TV {d[1]*100:3.0f}%)  RIM {r[0]:8.2f}  P/TBV {ptbv(PT_S[s], .114, .032)*344.68:8.2f}')
pub = [693.01, 564.39, 538.04, 1188.87, 636.28, 1142.00]
print('  blend sep con métodos publicados: %.2f (publicado 836.60)' % sum(w * v for w, v in zip(W, pub)))
alt = [ddm(64.79, *DDM_S['base'], .114, .032)[0], rim(344.68, *RIM_S['base'], .114, .032)[0],
       ptbv(.16, .114, .032) * 344.68, 1188.87, 636.28, 1142.00]
print('  blend sep con DDM/RIM/PTBV de este script: %.2f' % sum(w * v for w, v in zip(W, alt)))

# ---------- 2) Datos 3T26 (millones de USD) ----------
q = ['4T25', '1T26', '2T26', '3T26']
rev = [13454, 17227, 20338, 18679]
exp_ = [9722, 10426, 11673, 11308]
prov = [-2123, 315, 102, 368]           # 4T25: liberación al pasar Apple Card a held for sale
ni = [4617, 5630, 6628, 5294]
pref = [233, 227, 229, 172]
eps = [14.01, 17.55, 20.98, 17.01]
comp_ = [18906 - 14241, 5412, 6104, 5122]
rote_q = [.171, .213, .255, .205]       # oficiales (presentaciones)
bb = [3000, 5000, 4000, 3000]; dv = [1240, 1380, 1360, 1490]
nic = [a - b for a, b in zip(ni, pref)]
avg_tce = [n * 4 / r for n, r in zip(nic[:3], rote_q[:3])] + [100121]   # 3T26 oficial (10-Q)
EPS0 = round(sum(eps), 2)
print('\nTTM rev', sum(rev), 'gastos', sum(exp_), 'efic %.1f%%' % (100 * sum(exp_) / sum(rev)), 'prov', sum(prov),
      'NI', sum(ni), 'NI común', sum(nic), 'EPS', EPS0)
print('ROTCE TTM %.1f%% (NI común / TCE promedio) | prom 8 trimestres 4T24-3T26 %.1f%%' % (
      100 * sum(nic) / (sum(avg_tce) / 4), 100 * sum([.155, .180, .136, .152] + rote_q) / 8))
print('comp/ingresos netos de provisión 3T26 %.1f%%; comp/ingresos TTM %.1f%%' % (
      100 * 5122 / (18679 - 368), 100 * sum(comp_) / sum(rev)))
print('Capital devuelto TTM', sum(bb) + sum(dv), '| payout total %.1f%% | div %.1f%% | 3T26 %.1f%%' % (
      100 * (sum(bb) + sum(dv)) / sum(nic), 100 * sum(dv) / sum(nic), 100 * (bb[3] + dv[3]) / nic[3]))
print('CET1 Std %.2f%% (req 11.4%%) colchón %.2f pts = $%.1fB | Adv %.2f%% (req 10.5%%)' % (
      100 * 101441 / 815793, 100 * 101441 / 815793 - 11.4, (101441 / 815793 - .114) * 815.793, 100 * 101441 / 746474))
print('ROTCE ciclo: prom 2021-2025 sin 2023 = %.1f%%; con 2023 = %.1f%%; meta 15-17%%' % (
      (24.3 + 11.0 + 13.5 + 16.0) / 4, (24.3 + 11.0 + 8.1 + 13.5 + 16.0) / 5))
print('Trading GS 3T26 %d (+%.0f%%) | MS %d' % (3471 + 6441, 100 * ((3471 + 6441) / (3493 + 3736) - 1), 2011 + 5799))

Rf, beta, ERP = .04859, 1.27, .05
print('COE CAPM %.2f%% -> 11.2%%' % (100 * (Rf + beta * ERP)))
P = 865.82; TBV = 341.43
k = {'bear': .122, 'base': .112, 'bull': .102}
nov = valuar(P=P, TBV=TBV, EPS0=EPS0, EPSfwd=74.25, k=k,
             peers={'MS': (181.44, 53.96, 13.67), 'JPM': (334.49, 112.64, 25.57)},
             hist=[(385.77, 292.52), (572.62, 316.02), (879.00, 335.49)], cons=1031.00, label='3T26 (nov-2026)')
print(f'\nBlend nov vs sep: {nov["blend"]:.2f} vs 836.60 ({100*(nov["blend"]/836.60-1):+.1f}%)')
print('Consenso upside %.1f%% | P/TBV %.2fx | P/E TTM %.1fx | P/E FY27E %.1fx' % (
      100 * (1031 / P - 1), P / TBV, P / EPS0, P / 74.25))
print('peers: MS P/TBV %.2fx P/E %.1fx | JPM %.2fx %.1fx | BAC %.2fx %.1fx' % (
      181.44 / 53.96, 181.44 / 13.67, 334.49 / 112.64, 334.49 / 25.57, 49.42 / 29.14, 49.42 / 5.19))

print('\nGrilla RIM Base (COE x g)')
for kk in [.092, .102, .112, .122, .132]:
    print(f'  {kk*100:.1f}%', [round(rim(TBV, .18, .16, .05, .06, kk, g)[0], 2) for g in [.022, .027, .032, .037, .042]])

print('\nFootball:', [(round(nov['D']['bear'][0], 2), round(nov['D']['bull'][0], 2)),
                      (round(nov['R']['bear'][0], 2), round(nov['R']['bull'][0], 2)),
                      (round(nov['J']['bear'] * TBV, 2), round(nov['J']['bull'] * TBV, 2)),
                      (round(nov['comp'][1], 2), round(nov['comp'][2], 2)),
                      (round(min(nov['rev'][0]) * TBV, 2), round(max(nov['rev'][0]) * TBV, 2)), (730, 1250)])
