"""American Express (AXP) — modelo de valuación del informe informes/axp.html.

Marco de Visa adaptado a un emisor de circuito cerrado (pesos 15/10/25/30/20):
  M1 DCF de flujo al accionista (FCFE): utilidad neta a comunes − 10.5% x aumento de RWA, al Ke (no WACC).
     Utilidad a comunes = ingresos x margen pretax x (1 − tasa) x 98.9%;
     margen pretax = 1 − engagement − provisiones − marketing − gastos operativos (ratios sobre ingresos).
     RWA crece igual que los ingresos. Terminal = (NI5 x (1+g) − 10.5% x RWA5 x g) / (Ke − g).
     Al valor se le suma el excedente (o resta el déficit) de CET1 sobre 10.5% al inicio.
  M2 Retorno total de capital: NI a comunes x payout; terminal con payout = 1 − g/ROE sostenible.
  M3 Comparables COF 40 / V 20 / MA 20 / JPM 20 (P/E forward x EPS forward implícito de AXP en la misma fuente).
  M4 Reversión (P/E al cierre de diciembre, ventana 3 años) sobre EPS TTM.
  M5 Consenso (precio objetivo promedio).
Uso: python valuacion.py [--json]
"""
import json, sys, os

W = dict(m1=.15, m2=.10, m3=.25, m4=.30, m5=.20)
lin = lambda a, b: [a + (b - a) * i / 4 for i in range(5)]
pct = lambda xs: [x / 100 for x in xs]


def path(P, s):
    rev, out = P['rev0'], []
    for t in range(5):
        rev *= 1 + s['g'][t] / 100
        pre = 1 - (s['eng'][t] + s['prov'][t] + s['mkt_opex'][t]) / 100
        out.append(dict(rev=rev, pre=pre, ni=rev * pre * (1 - P['tax']) * P['com']))
    return out


def m1(P, s, ke=None):
    ke = s['ke'] if ke is None else ke
    g = s['gt']; rwa = P['rwa0']; pv = 0; pts = path(P, s)
    for t, p in enumerate(pts, 1):
        d = rwa * s['g'][t - 1] / 100; rwa += d
        pv += (p['ni'] - P['cet1'] * d) / (1 + ke) ** t
    pvtv = (pts[-1]['ni'] * (1 + g) - P['cet1'] * rwa * g) / (ke - g) / (1 + ke) ** 5
    return (pv + pvtv + P['cap_exc']) / P['sh'], pvtv / (pv + pvtv), pts


def m2(P, s):
    ke, g = s['ke'], s['gt']; pts = path(P, s); pv = 0
    for t, (p, po) in enumerate(zip(pts, s['payout']), 1):
        pv += p['ni'] * po / 100 / (1 + ke) ** t
    tv = pts[-1]['ni'] * (1 + g) * (1 - g / s['roe']) / (ke - g) / (1 + ke) ** 5
    return (pv + tv) / P['sh']


def run(P):
    out, sc = {}, {}
    for k, s in P['esc'].items():
        v, tvs, pts = m1(P, s)
        sc[k] = dict(m1=round(v, 2), tv_share=round(tvs * 100, 1), m2=round(m2(P, s), 2),
                     ni=[round(p['ni']) for p in pts], pretax=[round(p['pre'] * 100, 1) for p in pts])
    out['escenarios'] = sc
    b = P['esc']['base']
    out['grid'] = {}
    for kk in P['grid_ke']:
        row = []
        for gg in P['grid_g']:
            s2 = dict(b, gt=gg / 100); row.append(round(m1(P, s2, kk / 100)[0], 2))
        out['grid'][kk] = row
    out['m1_ke_visa'] = round(m1(P, b, P['ke_visa'])[0], 2)
    eps_f = P['price'] / P['pe_fwd']['AXP']
    c = {k: round(v * eps_f, 2) for k, v in P['pe_fwd'].items()}
    wpe = sum(P['wc'][k] * P['pe_fwd'][k] for k in P['wc'])
    out['comps'] = dict(c, eps_fwd=round(eps_f, 2), pe_pond=round(wpe, 2), blend=round(wpe * eps_f, 2),
                        iguales=round(sum(P['pe_fwd'][k] for k in P['wc']) / 4 * eps_f, 2))
    pes = {y: px / e for y, (px, e) in P['hist'].items()}
    out['pe_hist'] = {y: round(v, 2) for y, v in pes.items()}
    win = lambda ys: (round(sum(pes[y] for y in ys) / len(ys), 2), round(sum(pes[y] for y in ys) / len(ys) * P['eps_ttm'], 2))
    out['reversion'] = {k: win(ys) for k, ys in P['ventanas'].items()}
    vals = dict(m1=sc['base']['m1'], m2=sc['base']['m2'], m3=out['comps']['blend'], m4=out['reversion']['3a'][1], m5=P['pt_avg'])
    out['metodos'] = vals
    out['blend'] = round(sum(W[k] * vals[k] for k in W), 2)
    out['gap'] = round((out['blend'] / P['price'] - 1) * 100, 1)
    out['ev_m1'] = round(.25 * sc['bear']['m1'] + .45 * sc['base']['m1'] + .30 * sc['bull']['m1'], 2)
    # DCF inverso: crecimiento constante de ingresos 5 años que iguala el precio (resto del Base fijo)
    lo, hi = 0.0, 0.5
    for _ in range(100):
        mid = (lo + hi) / 2
        v = m1(P, dict(b, g=[mid * 100] * 5))[0]
        lo, hi = (mid, hi) if v < P['price'] else (lo, mid)
    out['dcf_inverso_g_ingresos'] = round(mid * 100, 2)
    # blend con ventana de 4 años en reversión
    out['blend_rev4'] = round(out['blend'] + W['m4'] * (out['reversion']['4a'][1] - vals['m4']), 2)
    return out


HIST = {'2021': (16.33 * 10.02, 10.02), '2022': (15.00 * 9.85, 9.85), '2023': (187.34, 11.21), '2024': (296.79, 14.01), '2025': (369.95, 15.38)}
VENT = {'3a': ['2023', '2024', '2025'], '4a': ['2022', '2023', '2024', '2025'], '5a': ['2021', '2022', '2023', '2024', '2025']}

# ---------------- Edición sep-2026 (2T 2026, precio 18-sep $311.56) ----------------
# Base: crecimiento de ingresos 8.9/8.25/7.8/7.3/6.7 (sep lo derivaba de componentes; esta trayectoria reproduce
# M1 $268.96 al centavo y la utilidad del año 5 en $17,109M vs $17,106M publicados). Bear/Bull con interpolación
# lineal: +$0.95 y +$1.46 en M1 (solo afectan el football field).
REPRO_SEP = dict(
    rev0=75950, tax=.225, com=.989, cet1=.105, rwa0=268321, cap_exc=-395, sh=679, price=311.56, ke_visa=.0881,
    esc=dict(
        base=dict(g=[8.9, 8.25, 7.8, 7.3, 6.7], eng=[44.5] * 5, prov=[6.8] * 5, mkt_opex=lin(29.5, 28.5), ke=.1026, gt=.03,
                  payout=lin(86, 90), roe=.30),
        bear=dict(g=lin(5.2, 3.5), eng=lin(44.5, 46.0), prov=lin(7.6, 8.4), mkt_opex=[29.7] * 5, ke=.1101, gt=.025,
                  payout=lin(80, 82), roe=.24),
        bull=dict(g=lin(10.8, 7.9), eng=lin(44.0, 43.0), prov=lin(6.4, 6.2), mkt_opex=lin(29.2, 27.4), ke=.0951, gt=.035,
                  payout=lin(88, 93), roe=.33),
    ),
    grid_ke=[9.26, 9.76, 10.26, 10.76, 11.26], grid_g=[2.0, 2.5, 3.0, 3.5, 4.0],
    pe_fwd=dict(AXP=16.78, COF=9.26, V=25.47, MA=26.58, JPM=14.43), wc=dict(COF=.4, V=.2, MA=.2, JPM=.2),
    hist=HIST, ventanas=VENT, eps_ttm=16.48, pt_avg=375.96,
)

# ---------------- Edición nov-2026 (3T 2026, cierre 30-sep-2026; precio 13-nov $320.60) ----------------
# Fuentes: 8-K y 10-Q del 23-oct-2026 (suplemento estadístico); Tesoro 13-nov (5.15%); stockanalysis 15-nov.
RF, BETA, ERP = 5.15, 1.08, 5.0
KE = (RF + BETA * ERP) / 100                    # 10.55%
KE_V = (RF + 0.79 * ERP) / 100                  # Ke de Visa con el mismo Rf: 9.10%
TTM = dict(  # 4T25 + 1T26 + 2T26 + 3T26
    rev=18980 + 18907 + 19637 + 20062, prov=1414 + 1251 + 1084 + 985,
    eng=(4805 + 4891 + 5051 + 5090) + (1728 + 1591 + 1755 + 1795) + (1951 + 1975 + 1949 + 2006),
    mkt=1612 + 1480 + 1650 + 1770, pretax=3090 + 3778 + 4071 + 4531, tax=628 + 807 + 961 + 819,
    ni=2462 + 2971 + 3110 + 3712,
    eps=round(15.38 + 14.22 - 11.85, 2), eps_aj=round(15.38 + 13.49 - 11.85, 2),
    recompras=5814 + 5805 - 4915, dividendos=2271 + 1916 - 1688)
CET1, RWA = 29338, 270071
NOV = dict(
    rev0=TTM['rev'], tax=.225, com=.989, cet1=.105, rwa0=RWA, cap_exc=round(CET1 - .105 * RWA), sh=674, price=320.60,
    ke_visa=KE_V,
    esc=dict(
        # Mismas trayectorias de crecimiento, engagement y marketing+opex que septiembre; provisiones re-ancladas
        # 0.3 pp abajo (TTM 6.1% vs 6.6%); payout re-anclado a la práctica real (TTM 75%, 9M ex-GBTG ~80%).
        base=dict(g=[8.9, 8.25, 7.8, 7.3, 6.7], eng=[44.5] * 5, prov=[6.5] * 5, mkt_opex=lin(29.5, 28.5), ke=round(KE, 4), gt=.03,
                  payout=lin(80, 90), roe=.30),
        bear=dict(g=lin(5.2, 3.5), eng=lin(44.5, 46.0), prov=lin(7.3, 8.1), mkt_opex=[29.7] * 5, ke=round(KE + .0075, 4),
                  gt=.025, payout=lin(74, 82), roe=.24),
        bull=dict(g=lin(10.8, 7.9), eng=lin(44.0, 43.0), prov=lin(6.1, 5.9), mkt_opex=lin(29.2, 27.4), ke=round(KE - .0075, 4),
                  gt=.035, payout=lin(82, 93), roe=.33),
    ),
    grid_ke=[9.55, 10.05, 10.55, 11.05, 11.55], grid_g=[2.0, 2.5, 3.0, 3.5, 4.0],
    pe_fwd=dict(AXP=16.52, COF=8.48, V=28.32, MA=29.74, JPM=13.81), wc=dict(COF=.4, V=.2, MA=.2, JPM=.2),
    hist=HIST, ventanas=VENT, eps_ttm=TTM['eps_aj'], pt_avg=364.79,
)

if __name__ == '__main__':
    sep, nov = run(REPRO_SEP), run(NOV)
    print('== sep ==', json.dumps(sep, ensure_ascii=False))
    print('TTM', TTM, {k: round(TTM[k] / TTM['rev'] * 100, 2) for k in ('prov', 'eng', 'mkt', 'pretax')},
          'tax', round(TTM['tax'] / TTM['pretax'] * 100, 1), 'retorno/NI', round((TTM['recompras'] + TTM['dividendos']) / TTM['ni'] * 100, 1))
    print('Ke %.2f  Ke Visa %.2f  excedente CET1 %d' % (KE * 100, KE_V * 100, NOV['cap_exc']))
    print('== nov ==', json.dumps(nov, ensure_ascii=False, indent=1))
    if '--json' in sys.argv:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resultados.json'), 'w', encoding='utf-8') as fh:
            json.dump(dict(sep=sep, nov=nov, ttm=TTM, ke=round(KE * 100, 2), ke_visa=round(KE_V * 100, 2)), fh, indent=1, ensure_ascii=False)
