# Motor de la suma de partes por producto + rNPV de LLY (Método 1 del marco informe-salud, Módulo A).
# Flujos anuales 2026-2045 a mitad de año, descontados a la fecha de valuación (de 2026 cuenta solo el 4T).
# Cada producto aporta ingresos x (margen de contribución - capex/ingresos); la I+D de toda la compañía se resta
# una sola vez como línea corporativa (después de impuestos). Ver README.md.
YEARS = list(range(2026, 2046))

def lin(y, pts):
    ks = sorted(pts)
    if y <= ks[0]: return pts[ks[0]]
    if y >= ks[-1]: return pts[ks[-1]]
    for a, b in zip(ks, ks[1:]):
        if a <= y <= b: return pts[a] + (pts[b] - pts[a]) * (y - a) / (b - a)

def erode(path, loe_first, e, tail):
    """path: dict año->ingreso pre-LOE. loe_first = primer año con erosión. e = [caída acumulada año1, año2],
    después del año 2 cae `tail` por año."""
    out = {}
    base = None
    for y in YEARS:
        if y < loe_first:
            out[y] = path(y)
        else:
            if base is None: base = path(loe_first - 1)
            k = y - loe_first
            if k == 0: out[y] = base * (1 - e[0])
            elif k == 1: out[y] = base * (1 - e[1])
            else: out[y] = base * (1 - e[1]) * (1 - tail) ** (k - 1)
    return out

def run(p):
    """p: diccionario de supuestos de un escenario. Devuelve componentes (VP, US$ miles de millones) y series."""
    w = p['wacc']
    def t(y): return 0.125 if y == p['y0'] else (y - p['y0'] - 1) + p['stub'] + 0.5
    def wt(y): return p['stub'] if y == p['y0'] else 1.0
    def df(y): return (1 + w) ** -t(y)
    cm = {y: lin(y, p['cm']) for y in YEARS}
    cx = {y: lin(y, p['capex']) for y in YEARS}
    rd = {y: lin(y, p['rd']) for y in YEARS}
    R = {}
    # Tirzepatida
    R['tirz'] = erode(lambda y: lin(y, p['tirz_path']), p['tirz_loe'], p['tirz_e'], p['tirz_tail'])
    if p.get('renewal'):   # escenario de renovación: incretinas sin erosión después de 2035, +2% anual
        pass
    # Foundayo
    R['found'] = erode(lambda y: lin(y, p['found_path']), p['found_loe'], [p['found_e1'], 1 - (1 - p['found_e1']) * (1 - p['found_tail'])], p['found_tail'])
    # Retatrutida (incremental, ajustada por probabilidad)
    reta = erode(lambda y: lin(y, p['reta_path']), p['reta_loe'], p['tirz_e'], p['tirz_tail'])
    R['reta'] = {y: v * p['reta_pos'] for y, v in reta.items()}
    if p.get('renewal'):
        for k in ('tirz', 'found', 'reta'):
            for y in YEARS:
                if y > 2035: R[k][y] = R[k][2035] * 1.02 ** (y - 2035)
    # Legados
    R['legacy'] = {y: sum(lin(y, p['leg'][k]) for k in p['leg']) for y in YEARS}
    # Resto del portafolio
    r, rest = p['rest0'], {}
    for y in YEARS:
        if y > p['y0']:
            g = p['rest_g1'] if y <= 2030 else (p['rest_g2'] if y <= 2034 else p['rest_g3'])
            r *= 1 + g
        rest[y] = r
    R['rest'] = rest
    # Fase 3 interno (5 activos, pico supuesto, probabilidad)
    R['ph3'] = {y: p['ph3_n'] * p['ph3_peak'] * p['ph3_pos'] * lin(y, p['ph3_ramp']) for y in YEARS}
    tot = {y: sum(R[k][y] for k in R) for y in YEARS}
    prem = {'tirz': p['tirz_prem']}
    C = {}
    for k in R:
        C[k] = sum(R[k][y] * (cm[y] + prem.get(k, 0) - cx[y]) * wt(y) * df(y) for y in YEARS)
    rdl = {y: -tot[y] * rd[y] * (1 - p['tax']) for y in YEARS}
    C['rd'] = sum(rdl[y] * wt(y) * df(y) for y in YEARS)
    fcf = {y: sum(R[k][y] * (cm[y] + prem.get(k, 0) - cx[y]) for k in R) + rdl[y] for y in YEARS}
    if p.get('renewal'):
        g = 0.02; ylast = YEARS[-1]
        C['tv'] = fcf[ylast] * (1 + g) / (w - g) * df(ylast)
        C['platform'] = 0.0
    else:
        C['platform'] = p['plat_share'] * fcf[p['plat_year']] * (1 + p['plat_g']) / (w - p['plat_g']) * df(p['plat_year'])
    C['acq'] = p['acq']
    ev = sum(C.values())
    eq = ev - p['net_debt']
    return dict(C=C, ev=ev, eq=eq, fv=eq / p['shares'], R=R, tot=tot, fcf=fcf,
                fcfm={y: fcf[y] / tot[y] for y in YEARS})
