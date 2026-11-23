# Motor de la suma de partes por producto + rNPV de PFE (Método 1 del marco informe-salud, Módulo A).
# Flujos anuales 2026-2045 a mitad de año, descontados a la fecha de valuación (de 2026 cuenta solo el 4T).
# Cada producto (y cada tramo EE.UU. / fuera de EE.UU.) aporta ingresos x (margen de contribución - capex/ingresos);
# la I+D de toda la compañía se resta una sola vez como línea corporativa (después de impuestos). Sin valor terminal
# sobre productos actuales: la "plataforma" va en línea separada, chica y explícita. Ver README.md.
YEARS = list(range(2026, 2046))
STEPS = 4   # la erosión post-LOE se integra por trimestre (permite fechas de LOE a mitad de año)

def lin(y, pts):
    ks = sorted(pts)
    if y <= ks[0]: return pts[ks[0]]
    if y >= ks[-1]: return pts[ks[-1]]
    for a, b in zip(ks, ks[1:]):
        if a <= y <= b: return pts[a] + (pts[b] - pts[a]) * (y - a) / (b - a)

def grow(v26, g):
    """Trayectoria sin LOE: nivel 2026 (año calendario) y crecimiento anual g(año) (dict año->tasa, interpolado)."""
    out, v = {}, v26
    for y in YEARS:
        if y > 2026: v *= 1 + lin(y, g)
        out[y] = v
    return out

def efactor(tau, curve):
    """Fracción de las ventas pre-LOE que queda tau años después de la LOE. curve = (caída año 1, caída acumulada año 2, cola anual)."""
    e1, e2, tail = curve
    if tau <= 0: return 1.0
    if tau <= 1: return 1 - e1
    if tau <= 2: return 1 - e2
    return (1 - e2) * (1 - tail) ** (tau - 2)

def with_loe(path, loe, curve):
    """Aplica la erosión a una trayectoria anual. loe = fecha (año con fracción, ej. 2028.25 = 1-abr-2028)."""
    if loe is None: return dict(path)
    out = {}
    for y in YEARS:
        f = sum(efactor(y + (q + 0.5) / STEPS - loe, curve) for q in range(STEPS)) / STEPS
        out[y] = path[y] * f
    return out

def ramp(launch, peak, loe, curve, yrs=5):
    """Activo del pipeline: lanza a mitad de `launch`, sube lineal hasta `peak` en `yrs` años, meseta y erosión desde `loe`."""
    pre = {y: (0.0 if y < launch else peak * min(1.0, (y - launch + 0.5) / yrs)) for y in YEARS}
    return with_loe(pre, loe, curve)

def run(p):
    """p: supuestos de un escenario. Devuelve componentes (VP, US$ miles de millones) y series."""
    w = p['wacc']
    def t(y): return 0.125 if y == 2026 else (y - 2027) + p['stub'] + 0.5
    def wt(y): return p['stub'] if y == 2026 else 1.0
    def df(y): return (1 + w) ** -t(y)
    cm = {y: lin(y, p['cm']) for y in YEARS}
    cx = {y: lin(y, p['capex']) for y in YEARS}
    rd = {y: lin(y, p['rd']) for y in YEARS}
    R, HAIR = {}, {}
    for k, seg in p['products'].items():          # productos comercializados: suma de tramos
        tot = {y: 0.0 for y in YEARS}
        for s in seg:
            path = grow(s['v26'], s['g'])
            if s.get('ira'):                       # precio negociado de Medicare: escalón desde el año indicado
                yi, cut = s['ira']
                path = {y: v * (1 - cut if y >= yi else 1) for y, v in path.items()}
            ren = p.get('renewal') and k in p['renew_keys'] and s['loe'] is not None
            ser = with_loe(path, None if ren else s['loe'], s['curve'])
            if ren:
                base = None
                for y in YEARS:
                    if y > s['loe'] and base is None: base = ser[y - 1]
                    if base is not None and y > s['loe']: ser[y] = base * 1.02 ** (y - int(s['loe']))
            for y in YEARS: tot[y] += ser[y]
        R[k] = tot
    PIPE = {}
    for a in p['pipeline']:
        ser = ramp(a['launch'], a['peak'], a['loe'], a['curve'])
        PIPE[a['key']] = {y: v * a['pos'] for y, v in ser.items()}
        HAIR[a['key']] = a.get('roy', 0.0)
    allR = dict(R); allR.update(PIPE)
    tot = {y: sum(allR[k][y] for k in allR) for y in YEARS}
    C = {}
    for k, ser in allR.items():
        C[k] = sum(ser[y] * (cm[y] - HAIR.get(k, 0.0) - cx[y]) * wt(y) * df(y) for y in YEARS)
    rdl = {y: -tot[y] * rd[y] * (1 - p['tax']) for y in YEARS}
    C['rd'] = sum(rdl[y] * wt(y) * df(y) for y in YEARS)
    fcf = {y: sum(allR[k][y] * (cm[y] - HAIR.get(k, 0.0) - cx[y]) for k in allR) + rdl[y] for y in YEARS}
    if p.get('renewal'):
        g = 0.02; yl = YEARS[-1]
        C['platform'] = fcf[yl] * (1 + g) / (w - g) * df(yl)
    else:
        C['platform'] = p['plat_share'] * max(fcf[p['plat_year']], 0.0) * (1 + p['plat_g']) / (w - p['plat_g']) * df(p['plat_year'])
    C['acq'] = p['acq']
    # CVR de Metsera: pagos por acción x acciones de Metsera x probabilidad del hito, descontados al año esperado
    C['cvr'] = -sum(m['usd'] * m['prob'] * (1 + w) ** -(m['year'] - 2026.75) for m in p['cvr'])
    ev = sum(C.values())
    eq = ev - p['net_debt']
    return dict(C=C, ev=ev, eq=eq, fv=eq / p['shares'], R=allR, tot=tot, fcf=fcf,
                fcfm={y: fcf[y] / tot[y] for y in YEARS})
