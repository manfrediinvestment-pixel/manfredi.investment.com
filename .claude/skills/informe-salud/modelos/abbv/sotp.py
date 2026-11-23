# Motor de la suma de partes por producto + rNPV de ABBV (Método 1 del marco informe-salud, Módulo A).
# Flujos anuales 2026-2045 a mitad de año, descontados al 30-sep-2026 (de 2026 cuenta solo el 4T).
# Cada producto aporta ingresos x (margen de contribución - capex/ingresos); la I+D de toda la compañía se resta
# una sola vez como línea corporativa (después de impuestos). Las franquicias sin LOE clásica (Botox y estética)
# reciben un valor terminal propio, en línea separada; la "plataforma" de I+D también va en línea separada.
YEARS = list(range(2026, 2046))


def lin(y, pts):
    ks = sorted(pts)
    if y <= ks[0]: return pts[ks[0]]
    if y >= ks[-1]: return pts[ks[-1]]
    for a, b in zip(ks, ks[1:]):
        if a <= y <= b: return pts[a] + (pts[b] - pts[a]) * (y - a) / (b - a)


def grow(level26, g):
    """level26 = ingreso anualizado 2026; g = dict año->crecimiento (se interpola y se mantiene el último)."""
    out, v = {}, level26
    for y in YEARS:
        if y > 2026: v *= 1 + lin(y, g)
        out[y] = v
    return out


def erode(path, loe_first, curve, tail):
    """path: dict año->ingreso sin LOE. loe_first = primer año con erosión. curve = caída acumulada contra el
    último año sin erosión, año por año; después de la curva cae `tail` por año."""
    out, base = {}, None
    for y in YEARS:
        if y < loe_first:
            out[y] = path[y]
        else:
            if base is None: base = path[loe_first - 1]
            k = y - loe_first
            if k < len(curve): out[y] = base * (1 - curve[k])
            else: out[y] = base * (1 - curve[-1]) * (1 - tail) ** (k - len(curve) + 1)
    return out


def ramp(peak, launch, peak_year, loe_first, curve, tail, pos):
    """Activo del pipeline: lanzamiento lineal hasta el pico, meseta, erosión; todo x probabilidad."""
    path = {}
    for y in YEARS:
        if y < launch: path[y] = 0.0
        elif y >= peak_year: path[y] = peak
        else: path[y] = peak * (y - launch + 1) / (peak_year - launch + 1)
    out = erode(path, loe_first, curve, tail)
    return {y: v * pos for y, v in out.items()}


def run(p):
    """p: supuestos de un escenario (ver model.py). Devuelve componentes (VP, US$ miles de millones) y series."""
    w = p['wacc']
    def t(y): return 0.125 if y == 2026 else (y - 2027) + 0.25 + 0.5
    def wt(y): return 0.25 if y == 2026 else 1.0
    def df(y): return (1 + w) ** -t(y)
    cm = {y: lin(y, p['cm']) for y in YEARS}
    cx = {y: lin(y, p['capex']) for y in YEARS}
    rd = {y: lin(y, p['rd']) for y in YEARS}
    R = {}
    for k, spec in p['prod'].items():
        path = grow(spec['l26'], spec['g'])
        for y, f in spec.get('adj', {}).items():          # recortes de precio (IRA) desde el año y
            for yy in YEARS:
                if yy >= y: path[yy] *= 1 + f
        if spec.get('loe'):
            if p.get('renewal') and k in p.get('renew_keys', ()):
                last = spec['loe'] - 1
                for yy in YEARS:
                    if yy > last: path[yy] = path[last] * 1.02 ** (yy - last)
                R[k] = path
            else:
                R[k] = erode(path, spec['loe'], spec['curve'], spec['tail'])
        else:
            R[k] = path
    for k, a in p['pipe'].items():
        pos = a['pos'] if k != p.get('pos_key') or p.get('pos_override') is None else p['pos_override']
        R['pipe_' + k] = ramp(a['peak'], a['launch'], a['peak_year'], a['loe'], a['curve'], a['tail'], pos)
    tot = {y: sum(R[k][y] for k in R) for y in YEARS}
    def contrib(k, y): return R[k][y] * (cm[y] - cx[y])
    C = {k: sum(contrib(k, y) * wt(y) * df(y) for y in YEARS) for k in R}
    rdl = {y: -tot[y] * rd[y] * (1 - p['tax']) for y in YEARS}
    C['rd'] = sum(rdl[y] * wt(y) * df(y) for y in YEARS)
    fcf = {y: sum(contrib(k, y) for k in R) + rdl[y] for y in YEARS}
    ylast = YEARS[-1]
    # Franquicias sin LOE clásica: valor terminal propio sobre su flujo de 2045, neto de la I+D proporcional
    nl = [k for k in p['prod'] if not p['prod'][k].get('loe') and p['prod'][k].get('terminal')]
    f_nl = {y: sum(R[k][y] for k in nl) * (cm[y] - cx[y] - rd[y] * (1 - p['tax'])) for y in YEARS}
    g_nl = p['g_noloe']
    if p.get('renewal'):
        C['tv'] = fcf[ylast] * (1 + 0.02) / (w - 0.02) * df(ylast)
        C['noloe_tv'] = 0.0
        C['platform'] = 0.0
    else:
        C['noloe_tv'] = f_nl[ylast] * (1 + g_nl) / (w - g_nl) * df(ylast)
        base_plat = fcf[p['plat_year']] - f_nl[p['plat_year']]
        C['platform'] = p['plat_share'] * base_plat * (1 + p['plat_g']) / (w - p['plat_g']) * df(p['plat_year'])
    ev = sum(C.values())
    eq = ev - p['net_debt'] - p['contingent']
    return dict(C=C, ev=ev, eq=eq, fv=eq / p['shares'], R=R, tot=tot, fcf=fcf,
                fcfm={y: fcf[y] / tot[y] for y in YEARS})
