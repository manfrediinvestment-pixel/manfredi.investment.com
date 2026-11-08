"""Valuación de MS (Morgan Stanley) — informe-bancos, actualización 3T 2026 (8-nov-2026).

Correr:  python valuacion.py
Mismo modelo que modelos/gs, modelos/wfc y modelos/c (DDM de payout total y RIM con trayectorias
lineales año 1 -> año 5, terminal de Gordon sobre el último flujo). A diferencia de GS, el P/TBV
justificado de MS en sep-2026 usaba el COE y la g DE CADA ESCENARIO (Bear 12.5%/2.5%, Bull 10.5%/3.8%):
se mantiene esa convención, que reproduce los tres valores publicados al centavo.

1) check_septiembre(): con los supuestos publicados el 14-sep-2026 (P $206.58, TBVPS $53.18,
   EPS TTM $12.37, COE 11.5%) este modelo da DDM Bear $51.76 (igual al centavo), Base $121.97
   (publicado $122.31, -0.3%), Bull $201.04 (publicado $198.03, +1.5%); RIM Base $120.82 (publicado
   $119.63, +1.0%); P/TBV justificado igual al centavo en los tres escenarios. El "% del valor desde el terminal"
   del DDM coincide (63/71/76%); el del RIM publicado era sobre el valor en exceso del libro (no
   sobre el total). El blend de sep se reproduce al centavo con los valores publicados ($163.20);
   con los de este script daría $163.28 (+0.05%). Se documenta y se sigue con el modelo del panel.

2) Correcciones de datos de sep (no de método):
   - Reversión: el TBVPS OFICIAL de cierre de 2024 es $44.57 (8-K 4T24 y 4T25), no $44.87; y los
     precios de cierre de año son los del último día hábil (31-dic-2024 $125.72, 31-dic-2025
     $177.53), no los del 30-dic ($125.75 / $179.08). 2023 ($93.25 / $40.89) estaba bien.
     Reversión de sep corregida: 2.884x -> $153.37 (publicado $153.60).
   - Beta: sep usaba ~1.30 "no verificado"; el beta 5 años verificado es 1.22 -> COE 11.0%.
   - Comparables con P/E sobre EPS FY2027E (como el resto del panel), ya no FY2026E.

Fuentes: 8-K del 14-oct-2026 (Ex. 99.1 comunicado, Ex. 99.2 Financial Supplement), 10-Q del 3T26
presentado el 5-nov-2026 (CET1 $88,831M / RWA estándar $595,983M definitivos, requerimientos 11.8%,
SCB 4.3% hasta 31-dic-2027, SLR 4.8% vs 3.5%, dividendos comunes declarados), 8-K de resultados
4T23/4T24/4T25/1T26/2T26, strategic update 4T25 (ROTCE anual 2016-2025, metas). Precios: Yahoo chart
'close' (sin ajustar por dividendos) al 6-nov-2026; ^TNX 4.86%. Consenso y beta: stockanalysis.com
(S&P Global, 26 analistas, 6-nov-2026). GS/JPM: informes del panel actualizados al 3T26 (6-nov-2026).
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
    return v, tv / v, tv / (v - bv0)   # % del total y % del valor en exceso del libro

def ptbv(r, k, g): return (r - g) / (k - g)

W = [.1, .1, .1, .2, .3, .2]  # DDM, RIM, P/TBV just., comps, reversión, consenso
gT = {'bear': .025, 'base': .032, 'bull': .038}

# ---------- 1) Septiembre-2026 ----------
SEP_DDM = {'bear': (.03, .03, .40, .40), 'base': (.10, .06, .58, .66), 'bull': (.14, .08, .72, .78)}
SEP_RIM = {'bear': (.15, .13, .04, .02), 'base': (.22, .20, .10, .07), 'bull': (.25, .22, .13, .09)}
PT_S = {'bear': .13, 'base': .20, 'bull': .22}
k_sep = {'bear': .125, 'base': .115, 'bull': .105}
print('===== CHECK SEP-2026 (publicado: DDM 51.76/122.31/198.03, RIM 57.67/119.63/173.41, P/TBV 55.84/107.64/144.46) =====')
for s in k_sep:
    d = ddm(12.37, *SEP_DDM[s], k_sep[s], gT[s]); r = rim(53.18, *SEP_RIM[s], k_sep[s], gT[s])
    print(f'  {s:4}  DDM {d[0]:8.2f} (TV {d[1]*100:3.0f}%)  RIM {r[0]:8.2f} (TV total {r[1]*100:3.0f}% / exceso {r[2]*100:3.0f}%)'
          f'  P/TBV {ptbv(PT_S[s], k_sep[s], gT[s])*53.18:8.2f}')
pub = [122.31, 119.63, 107.64, 174.19, 153.60, 236.62]
print('  blend sep con métodos publicados: %.2f (publicado 163.20)' % sum(w * v for w, v in zip(W, pub)))
alt = [ddm(12.37, *SEP_DDM['base'], .115, .032)[0], rim(53.18, *SEP_RIM['base'], .115, .032)[0],
       ptbv(.20, .115, .032) * 53.18, 174.19, 153.60, 236.62]
print('  blend sep con DDM/RIM/PTBV de este script: %.2f' % sum(w * v for w, v in zip(W, alt)))
hist_ok = [(93.25, 40.89), (125.72, 44.57), (177.53, 50.00)]
m_ok = sum(p / t for p, t in hist_ok) / 3
print('  reversión sep corregida (TBVPS oficiales, cierres 31-dic): %.3fx -> %.2f (publicado 2.89x -> 153.60)' % (m_ok, m_ok * 53.18))

# ---------- 2) Datos trimestrales oficiales (millones de USD) ----------
q    = ['4T24', '1T25', '2T25', '3T25', '4T25', '1T26', '2T26', '3T26']
rev  = [16223, 17739, 16792, 18224, 17890, 20580, 21348, 20338]
nii  = [2552, 2353, 2347, 2491, 2855, 2703, 2780, 3250]
exp_ = [11202, 12060, 11974, 12196, 12112, 13471, 13902, 13712]
prov = [115, 135, 196, 0, 18, 98, 98, 148]
ni   = [3714, 4315, 3539, 4610, 4397, 5567, 5581, 4909]
pref = [150, 158, 147, 160, 147, 156, 145, 158]
eps  = [2.22, 2.60, 2.13, 2.80, 2.68, 3.43, 3.46, 3.03]
rote = [.202, .230, .182, .235, .218, .271, .266, .226]   # oficiales
roe  = [.152, .174, .139, .180, .169, .210, .207, .178]
tbv  = [44.57, 46.08, 47.25, 48.64, 50.00, 51.58, 53.18, 53.96]
bb   = [750, 1000, 1000, 1085, 1500, 1750, 1500, 1540]     # recompras ($M)
dv   = [None, None, 1478, 1592, 6147 - 4562, 1589, 1575, 1804]  # dividendos comunes declarados (XBRL)
nic = [a - b for a, b in zip(ni, pref)]
L = slice(4, 8)  # TTM = 4T25-3T26
EPS0 = round(sum(eps[L]), 2)
print('\nEficiencia trimestral', [f'{100*e/r:.1f}' for e, r in zip(exp_, rev)])
print('NII/ingresos', [f'{100*n/r:.1f}' for n, r in zip(nii, rev)])
print('TTM: ingresos %d NII %d (%.1f%%) gastos %d efic %.1f%% prov %d NI %d NIcomún %d EPS %.2f' % (
    sum(rev[L]), sum(nii[L]), 100 * sum(nii[L]) / sum(rev[L]), sum(exp_[L]), 100 * sum(exp_[L]) / sum(rev[L]),
    sum(prov[L]), sum(ni[L]), sum(nic[L]), EPS0))
avg_tce = [n * 4 / r for n, r in zip(nic, rote)]
print('ROTCE TTM %.1f%% | ROE TTM aprox %.1f%% | prom 8 trimestres %.1f%% | 9M26 oficial 25.4%%' % (
    100 * sum(nic[L]) / (sum(avg_tce[L]) / 4), 100 * sum(nic[L]) / (sum(n * 4 / r for n, r in zip(nic[L], roe[L])) / 4),
    100 * sum(rote) / 8))
print('ROTCE anual oficial: 2021 19.8 2022 15.3 2023 12.8 2024 18.8 2025 21.6 | prom 21-25 %.1f%% | prom 24-25 %.1f%% | sin 2023 %.1f%%' % (
    (19.8 + 15.3 + 12.8 + 18.8 + 21.6) / 5, (18.8 + 21.6) / 2, (19.8 + 15.3 + 18.8 + 21.6) / 4))
div_ttm = sum(dv[L]); bb_ttm = sum(bb[L])
print('Capital devuelto TTM: recompras %d + dividendos %d = %d | payout total %.1f%% | div %.1f%% | DPS pagado 4.15 / EPS %.1f%%' % (
    bb_ttm, div_ttm, bb_ttm + div_ttm, 100 * (bb_ttm + div_ttm) / sum(nic[L]), 100 * div_ttm / sum(nic[L]), 100 * 4.15 / EPS0))
print('3T26: payout total %.1f%%' % (100 * (bb[7] + dv[7]) / nic[7]))
cet1, rwa_s, rwa_a = 88831, 595983, 546181
print('CET1 Std %.2f%% (req 11.8%%) colchón %.2f pts = $%.1fB | Adv %.2f%% (req 10.0%%) colchón %.2f pts' % (
    100 * cet1 / rwa_s, 100 * cet1 / rwa_s - 11.8, (cet1 / rwa_s - .118) * rwa_s / 1000, 100 * cet1 / rwa_a, 100 * cet1 / rwa_a - 10.0))
print('TBVPS +%.1f%% interanual (3T25->3T26) | +%.1f%% en 9M (anualizado %.1f%%)' % (
    100 * (53.96 / 48.64 - 1), 100 * (53.96 / 50.00 - 1), 100 * ((53.96 / 50.00) ** (4 / 3) - 1)))
print('WM: margen 3T26 %.1f%% | 9M %.1f%% | NNA 9M %.1f | fee-based 9M %.1f' % (
    100 * 2754 / 9065, 100 * 8042 / 26440, 118.4 + 148.1 + 232.4, 53.7 + 39.1 + 80.5))
print('ISG trading 3T26 %d vs %d (%+.1f%%) | IS IB %+.1f%%' % (5799 + 2011, 4116 + 2169, 100 * ((5799 + 2011) / (4116 + 2169) - 1), 100 * (2159 / 2108 - 1)))

# ---------- 3) Valuación 3T26 ----------
Rf, beta, ERP = .0486, 1.22, .05
print('\nCOE CAPM %.2f%% -> 11.0%%' % (100 * (Rf + beta * ERP)))
k = {'bear': .12, 'base': .11, 'bull': .10}
DDM_S = {'bear': (.03, .03, .40, .40), 'base': (.085, .06, .65, .68), 'bull': (.14, .08, .72, .78)}
RIM_S = {'bear': (.15, .13, .04, .02), 'base': (.23, .20, .10, .07), 'bull': (.25, .22, .13, .09)}
P, TBV, EPSfwd, CONS = 181.44, 53.96, 13.67, 211.50
print('EPS FY27E / EPS TTM = %+.1f%%' % (100 * (EPSfwd / EPS0 - 1)))

D = {s: ddm(EPS0, *DDM_S[s], k[s], gT[s]) for s in k}
R = {s: rim(TBV, *RIM_S[s], k[s], gT[s]) for s in k}
J = {s: ptbv(PT_S[s], k[s], gT[s]) for s in k}   # COE/g de cada escenario (convención MS sep)
for s in k:
    print(f'  {s:4}  DDM {D[s][0]:8.2f} (TV {D[s][1]*100:3.0f}%)  RIM {R[s][0]:8.2f} (TV total {R[s][1]*100:3.0f}% / exceso {R[s][2]*100:3.0f}%)  P/TBV {J[s]:.3f}x {J[s]*TBV:8.2f}')
peers = {'GS': (865.82, 341.43, 74.25)}
ap = []
for n, (p, t, e) in peers.items():
    print(f'  peer {n}: P/TBV {p/t:.3f}x -> {p/t*TBV:.2f} | P/E FY27E {p/e:.3f}x -> {p/e*EPSfwd:.2f}')
    ap += [p / t * TBV, p / e * EPSfwd]
comp = sum(ap) / len(ap)
print(f'  comparables {comp:.2f}  piso {min(ap):.2f} techo {max(ap):.2f}')
mult = [p / t for p, t in hist_ok]; m3 = sum(mult) / 3; rev_v = m3 * TBV
print('  reversión', [f'{m:.3f}x={m*TBV:.2f}' for m in mult], f'prom {m3:.3f}x -> {rev_v:.2f}')
V = [D['base'][0], R['base'][0], J['base'] * TBV, comp, rev_v, CONS]
blend = sum(w * v for w, v in zip(W, V))
print('  métodos', [round(v, 2) for v in V], [f'{100*(v/P-1):+.1f}%' for v in V])
print(f'  BLEND {blend:.2f}  ({100*(blend/P-1):+.1f}% vs {P}) | vs sep 163.20: {100*(blend/163.20-1):+.1f}%')
ev = sum(w * (D[s][0] + R[s][0]) / 2 for s, w in (('bear', .25), ('base', .45), ('bull', .30)))
imp = (P / TBV) * (k['base'] - gT['base']) + gT['base']
print(f'  EV prob DDM+RIM {ev:.2f} | P/TBV mercado {P/TBV:.3f}x -> ROTCE implícito {imp*100:.2f}%')
print('  P/E TTM %.1fx | P/E FY27E %.1fx | consenso upside %+.1f%%' % (P / EPS0, P / EPSfwd, 100 * (CONS / P - 1)))
print('  SCHW ref: P/TBV 6.12x, P/E fwd 12.24x (stockanalysis) | JPM P/TBV %.2fx P/E %.1fx' % (334.49 / 112.64, 334.49 / 25.57))

# Atribución del cambio sep -> nov (paso a paso, cada uno sobre el anterior)
print('\nAtribución sep 163.20 -> nov:')
def blend_with(k_, eps0, tbv, ddm_s, rim_s, comp_, rev_, cons):
    v = [ddm(eps0, *ddm_s, k_, .032)[0], rim(tbv, *rim_s, k_, .032)[0], ptbv(.20, k_, .032) * tbv, comp_, rev_, cons]
    return sum(w * x for w, x in zip(W, v))
steps = [
    ('sep (script)', blend_with(.115, 12.37, 53.18, SEP_DDM['base'], SEP_RIM['base'], 174.19, 153.60, 236.62)),
    ('+ reversión sep corregida', blend_with(.115, 12.37, 53.18, SEP_DDM['base'], SEP_RIM['base'], 174.19, m_ok * 53.18, 236.62)),
    ('+ datos 3T26 (TBV, EPS, mult. reversión s/ TBV nuevo)', blend_with(.115, EPS0, TBV, SEP_DDM['base'], SEP_RIM['base'], 174.19, rev_v, 236.62)),
    ('+ supuestos año 1 (payout 65%, g 8.5%, ROTCE 23%)', blend_with(.115, EPS0, TBV, DDM_S['base'], RIM_S['base'], 174.19, rev_v, 236.62)),
    ('+ COE 11.0% (beta verificado 1.22)', blend_with(.11, EPS0, TBV, DDM_S['base'], RIM_S['base'], 174.19, rev_v, 236.62)),
    ('+ comparables GS 3T26 (FY27E)', blend_with(.11, EPS0, TBV, DDM_S['base'], RIM_S['base'], comp, rev_v, 236.62)),
    ('+ consenso nov $211.50', blend_with(.11, EPS0, TBV, DDM_S['base'], RIM_S['base'], comp, rev_v, CONS)),
]
for n, v in steps: print(f'  {n:55} {v:8.2f}')

print('\nGrilla RIM Base (COE x g)')
for kk in [.10, .105, .11, .115, .12]:
    print(f'  {kk*100:.1f}%', [round(rim(TBV, *RIM_S['base'], kk, g)[0], 2) for g in [.022, .027, .032, .037, .042]])

print('\nFootball:', [(round(D['bear'][0], 2), round(D['bull'][0], 2)), (round(R['bear'][0], 2), round(R['bull'][0], 2)),
                      (round(J['bear'] * TBV, 2), round(J['bull'] * TBV, 2)), (round(min(ap), 2), round(max(ap), 2)),
                      (round(min(mult) * TBV, 2), round(max(mult) * TBV, 2)), (185, 262)])
