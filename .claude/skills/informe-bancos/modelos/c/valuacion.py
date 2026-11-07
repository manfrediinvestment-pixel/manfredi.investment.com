"""Valuación de C (Citigroup) — informe-bancos, actualización 3T 2026 (7-nov-2026).

Correr:  python valuacion.py
Reproduce el blend publicado en informes/c.html. Mismo modelo que modelos/bac/valuacion.py
(DDM de payout total y RIM con trayectorias lineales año 1 -> año 5, terminal de Gordon sobre el
último flujo).

check_version_anterior(): con los supuestos de sep-2026 (EPS limpio 9.89, TBVPS 100.89, COE 10.5%)
este modelo da DDM base $133.58 (publicado $132.61, +0.7%) y RIM base $121.93 (publicado $122.95,
-0.8%). La estructura es la misma (el "% del valor desde el terminal" coincide en los seis
escenarios: 63/70/77 y -63/14/44), pero los valores de sep no se guardaron con script y no cierran
al centavo con ninguna variante probada. El blend de sep sí se reproduce: $132.52 vs $132.53.

Fuentes: 8-K del 13-oct-2026 (comunicado Ex. 99.1 y suplemento financiero Ex. 99.2), 10-Q del 3T26
presentado el 5-nov-2026 (CET1/RWA definitivos y XBRL), 10-K 2025 (XBRL), transcripción oficial de
la conference call del 13-oct-2026, stockanalysis.com (consenso, beta) y Yahoo Finance (precios).
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
    return bv0 + pv + tv, tv / (bv0 + pv + tv)

# ---------------- Datos del trimestre (millones de USD salvo indicación) ----------------
P = 119.05            # cierre 6-nov-2026 (Yahoo)
TBV = 101.59          # TBVPS 30-sep-2026 (suplemento, pág. 23)
Rf, beta, ERP = .0486, 1.15, .05   # UST 10Y cierre 6-nov; beta 5Y stockanalysis
coe = Rf + beta * ERP
print('COE bruto %.2f%%' % (coe * 100))
k = {'bear': .116, 'base': .106, 'bull': .096}

q = ['4T25', '1T26', '2T26', '3T26']
eps = [1.19, 3.06, 3.15, 2.85]; notable_eps = [0.62, 0, 0, 0]          # Rusia 4T25
ni = [2471, 5785, 5831, 5245]; pref = [284, 305, 338, 353]
notable_ni = [1123, 0, 0, 0]
nii = [15665, 15741, 17125, 16982]; nir = [4206, 8892, 7641, 6863]
exp_ = [13840, 14311, 14215, 13952]; prov = [2220, 2805, 2522, 2586]
avg_tce = [170442, 169246, 169055, 168693]
bb = [4500, 6300, 4000, 3000]      # 4T25 = 13,250 (10-K) - 8,750 (9M25, 10-Q)
dv = [1093, 1053, 1051, 1142]      # 9M26 = 3,246 (10-Q); 4T25 por roll de utilidades retenidas
EPS_rep = round(sum(eps), 2); EPS0 = round(sum(eps) + sum(notable_eps), 2)
nic = [a - b for a, b in zip(ni, pref)]
print('EPS TTM rep', EPS_rep, 'sin ítems notables', EPS0)
print('NI TTM', sum(ni), 'NI común', sum(nic), 'rev', sum(nii) + sum(nir), 'NII', sum(nii), 'NIR', sum(nir),
      'gastos', sum(exp_), 'efic %.1f' % (100 * sum(exp_) / (sum(nii) + sum(nir))),
      'efic sin notable %.1f' % (100 * sum(exp_) / (sum(nii) + sum(nir) + 1173)), 'prov', sum(prov))
rot_rep = sum(nic) / (sum(avg_tce) / 4); rot_adj = (sum(nic) + sum(notable_ni)) / (sum(avg_tce) / 4)
print('ROTCE TTM rep %.1f%% sin notable %.1f%%' % (rot_rep * 100, rot_adj * 100))
ret = sum(bb) + sum(dv)
print('capital devuelto TTM', ret, 'payout total / NI común %.1f%%, sin notable %.1f%%, div %.1f%%'
      % (100 * ret / sum(nic), 100 * ret / (sum(nic) + 1123), 100 * sum(dv) / sum(nic)))
print('CET1 colchón 3T26 (10-Q 12.77%% vs 11.6%%) $B %.1f; vs 12.1%% (ene-2028) $B %.1f'
      % ((.1277 - .116) * 1232.261, (.1277 - .121) * 1232.261))

# ---------------- Método 1: DDM de payout total ----------------
D = {'bear': ddm(EPS0, .02, .02, .50, .42, k['bear'], .025),
     'base': ddm(EPS0, .11, .07, 1.00, .68, k['base'], .035),
     'bull': ddm(EPS0, .16, .10, 1.10, .80, k['bull'], .040)}
for s in D: print('DDM', s, round(D[s][0], 2), 'TV%', round(D[s][1] * 100))

# ---------------- Método 2: RIM ----------------
RA = {'bear': (.080, .070, .03, .02, .025), 'base': (.115, .125, .06, .07, .032), 'bull': (.130, .150, .09, .12, .038)}
R = {s: rim(TBV, a[0], a[1], a[2], a[3], k[s], a[4]) for s, a in RA.items()}
for s in R: print('RIM', s, round(R[s][0], 2), 'TV%', round(R[s][1] * 100))

# ---------------- Método 3: P/TBV justificado ----------------
J = {}
for s in RA:
    r, g = RA[s][1], RA[s][4]; m = (r - g) / (k[s] - g); J[s] = (m, m * TBV)
    print('PTBV', s, round(m, 3), round(m * TBV, 2))
mk = P / TBV
print('P/TBV mercado %.3f -> ROTCE implícito %.2f%%' % (mk, (mk * (k['base'] - .032) + .032) * 100))

# ---------------- Método 4: comparables (cierres 6-nov-2026) ----------------
peers = {'JPM': (334.49, 112.64, 25.57), 'BAC': (49.42, 29.14, 5.19), 'WFC': (83.94, 44.46, 8.01)}
EPS27 = 13.06
ptbv = [p / t for p, t, e in peers.values()]; pe = [p / e for p, t, e in peers.values()]
for n, (p, t, e) in peers.items(): print(n, 'P/TBV %.2f P/E27 %.2f' % (p / t, p / e))
a1 = sum(ptbv) / 3; a2 = sum(pe) / 3; c1 = a1 * TBV; c2 = a2 * EPS27; comp = (c1 + c2) / 2
print('comps P/TBV %.3f -> %.2f | P/E %.3f -> %.2f | prom %.2f | C propio P/TBV %.2f P/E27 %.2f'
      % (a1, c1, a2, c2, comp, P / TBV, P / EPS27))
print('sin JPM P/TBV %.3f -> %.2f' % ((ptbv[1] + ptbv[2]) / 2, (ptbv[1] + ptbv[2]) / 2 * TBV))

# ---------------- Método 5: reversión (cierres sin ajustar / TBVPS oficial del 4T) ----------------
hist = [(51.44, 86.19), (70.39, 89.34), (116.69, 97.06)]
mult = [p / t for p, t in hist]
print('rev mults', [round(x, 3) for x in mult], [round(x * TBV, 2) for x in mult])
rev = sum(mult) / 3 * TBV; print('rev prom %.3f -> %.2f' % (sum(mult) / 3, rev))

# ---------------- Método 6: consenso ----------------
cons = 150.60

W = [.1, .1, .1, .2, .3, .2]
V = [D['base'][0], R['base'][0], J['base'][1], comp, rev, cons]
blend = sum(w * v for w, v in zip(W, V))
print('BLEND %.2f gap %.1f%%' % (blend, 100 * (blend / P - 1)))
for n, v in zip(['DDM', 'RIM', 'PTBV', 'comps', 'rev', 'cons'], V): print('  %-5s %.2f vs mkt %+.1f%%' % (n, v, 100 * (v / P - 1)))
ev = .25 * (D['bear'][0] + R['bear'][0]) / 2 + .45 * (D['base'][0] + R['base'][0]) / 2 + .30 * (D['bull'][0] + R['bull'][0]) / 2
print('valor esperado prob. %.2f' % ev)
print('blend sin consenso (pesos reescalados) %.2f' % (sum(w * v for w, v in zip(W[:5], V[:5])) / .8))
print('grilla RIM base (COE x g):')
for kk in [.086, .096, .106, .116, .126]:
    print(' ', kk, [round(rim(TBV, .115, .125, .06, .07, kk, g)[0], 2) for g in [.022, .027, .032, .037, .042]])

def check_version_anterior():
    print('sep-2026 DDM', [round(ddm(9.89, *a)[0], 2) for a in [(.02, .02, .50, .42, .115, .025), (.11, .07, 1.0, .68, .105, .035), (.16, .10, 1.10, .80, .095, .04)]], 'publicado [48.00, 132.61, 223.26]')
    print('sep-2026 RIM', [round(rim(100.89, *a)[0], 2) for a in [(.08, .07, .03, .02, .115, .025), (.11, .12, .06, .08, .105, .032), (.13, .15, .09, .12, .095, .038)]], 'publicado [51.91, 122.95, 216.63]')
    Vs = [132.61, 122.95, 121.62, 188.35, 87.00, 155.20]
    print('sep-2026 blend %.2f (publicado 132.53)' % sum(w * v for w, v in zip(W, Vs)))
check_version_anterior()
