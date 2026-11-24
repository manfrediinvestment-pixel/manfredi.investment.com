# Motor del Método 1 de JNJ (informe-salud, conglomerado): suma de partes por segmento.
#  - Innovative Medicine (Módulo A): producto por producto hasta la LOE + rNPV de la fase 3, I+D como línea corporativa,
#    línea de "plataforma" post-2040.
#  - MedTech (Módulo B): DCF con crecimiento orgánico y perpetuidad.
# Flujos anuales 2026-2045 a mitad de año, descontados a la fecha de valuación (de 2026 cuenta solo la fracción `stub`).
# Unidades: US$ miles de millones. Ver README.md.
YEARS = list(range(2026, 2046))

def lin(y, pts):
    ks = sorted(pts)
    if y <= ks[0]: return pts[ks[0]]
    if y >= ks[-1]: return pts[ks[-1]]
    for a, b in zip(ks, ks[1:]):
        if a <= y <= b: return pts[a] + (pts[b] - pts[a]) * (y - a) / (b - a)

def erode(path, first, e, tail):
    """path(y) = ingreso antes de la LOE; first = primer año con erosión; e = [nivel año 1, nivel año 2] sobre el
    último año previo; después cae `tail` por año."""
    out, base = {}, None
    for y in YEARS:
        if y < first: out[y] = path(y)
        else:
            if base is None: base = path(first - 1)
            k = y - first
            out[y] = base * (e[0] if k == 0 else e[1] * (1 - tail) ** (k - 1))
    return out

def growth_path(v0, rates, y0=2026):
    """v0 en y0 y tasas por año {año: g} (lin entre puntos)."""
    out, v = {}, v0
    for y in YEARS:
        if y > y0: v *= 1 + lin(y, rates)
        out[y] = v
    return out

def ramp(v0, peak, pk_year, y0=2026):
    return lambda y: lin(y, {y0: v0, pk_year: peak})

def im_revenue(p):
    """Ingresos de Innovative Medicine por producto/grupo (dict de dicts)."""
    R = {}
    BIO, SM = p['bio_e'], p['sm_e']
    # Darzalex: EE.UU. y resto del mundo, mismo crecimiento hasta su LOE, erosión de biológico
    dpath = growth_path(p['dara26'], p['dara_g'])
    for part, sh, loe in (('dara_us', p['dara_us'], p['dara_loe_us']), ('dara_row', 1 - p['dara_us'], p['dara_loe_row'])):
        R[part] = erode(lambda y, sh=sh: dpath[y] * sh, loe + p['loe_lag'], BIO, p['bio_tail'])
    # Tremfya: rampa hasta el pico y meseta hasta la LOE
    R['trem'] = erode(ramp(p['trem26'], p['trem_pk'], p['trem_pky']), p['trem_loe'] + p['loe_lag'], BIO, p['bio_tail'])
    # Oncología en lanzamiento (Rybrevant/Lazcluze, Tecvayli, Talvey)
    R['onc'] = erode(ramp(p['onc26'], p['onc_pk'], p['onc_pky']), p['onc_loe'] + p['loe_lag'], BIO, p['bio_tail'])
    # Icotyde (péptido oral, NDA: erosión de molécula pequeña)
    R['ico'] = erode(ramp(p['ico26'], p['ico_pk'], p['ico_pky']), p['ico_loe'] + p['loe_lag'], SM, p['sm_tail'])
    # Resto de productos con fecha: Erleada (IRA desde 2028), Spravato, Carvykti (mitad del margen), Caplyta,
    # Imaavy, Imbruvica (−12%/año), Stelara (−35%, −25%, −15%/año)
    g = p['oth_g']; gy = p.get('oth_gy', 2030)   # crecen a `oth_g` hasta `oth_gy` y después se aplanan
    def gr(y): return (1 + g) ** (min(y, gy) - 2026)
    R['erl'] = erode(lambda y: p['erl26'] * gr(y) * (1 - p['ira_erl'] if y >= 2028 else 1),
                     p['erl_loe'] + p['loe_lag'], SM, p['sm_tail'])
    R['spr'] = erode(lambda y: p['spr26'] * gr(y), p['spr_loe'] + p['loe_lag'], SM, p['sm_tail'])
    R['car'] = erode(lambda y: p['car26'] * gr(y), p['car_loe'] + p['loe_lag'], BIO, p['bio_tail'])
    R['cap'] = erode(lambda y: p['cap26'] * gr(y), p['cap_loe'] + p['loe_lag'], SM, p['sm_tail'])
    R['ima'] = erode(ramp(p['ima26'], p['ima_pk'], p['ima_pky']), p['ima_loe'] + p['loe_lag'], BIO, p['bio_tail'])
    R['imb'] = erode(lambda y: p['imb26'] * (1 - p['imb_d']) ** (y - 2026), p['imb_loe'] + p['loe_lag'], SM, p['sm_tail'])
    st = {}
    for y in YEARS:
        k = y - 2026
        st[y] = p['ste26'] * (1 if k == 0 else 0.65 if k == 1 else 0.65 * 0.75 * 0.85 ** (k - 2))
    R['ste'] = st
    # Cartera madura (Invega, hipertensión pulmonar, infecciosas, Xarelto, Simponi, Remicade, otros)
    R['mat'] = {y: p['mat26'] * (1 + p['mat_g']) ** (y - 2026) for y in YEARS}
    # Fase 3 (activos equivalentes x pico x probabilidad)
    R['ph3'] = {y: p['ph3_n'] * p['ph3_pk'] * p['ph3_pos'] * lin(y, {p['ph3_l'] - 1: 0.0, p['ph3_l'] - 1 + p['ph3_ry']: 1.0})
                for y in YEARS}
    if p.get('renewal'):   # Darzalex sin erosión después de su LOE: +2% anual
        for part in ('dara_us', 'dara_row'):
            pre = R[part][p['dara_loe_us'] + p['loe_lag'] - 1] if part == 'dara_us' else R[part][p['dara_loe_row'] + p['loe_lag'] - 1]
            ystart = (p['dara_loe_us'] if part == 'dara_us' else p['dara_loe_row']) + p['loe_lag']
            for y in YEARS:
                if y >= ystart: R[part][y] = pre * 1.02 ** (y - ystart + 1)
    return R

GROUPS = {'mat': ['mat'], 'dara': ['dara_us', 'dara_row'], 'trem': ['trem'], 'onc': ['onc'], 'ico': ['ico'], 'ph3': ['ph3'],
          'oth': ['erl', 'spr', 'car', 'ima', 'imb', 'cap', 'ste']}

def disc(p, w):
    def t(y): return p['stub'] / 2 if y == 2026 else (y - 2027) + p['stub'] + 0.5
    def wt(y): return p['stub'] if y == 2026 else 1.0
    return (lambda y: (1 + w) ** -t(y)), wt

def run_im(p):
    w = p['wacc_im']; df, wt = disc(p, w)
    R = im_revenue(p)
    tot = {y: sum(R[k][y] for k in R) for y in YEARS}
    cm = {y: lin(y, p['cm']) for y in YEARS}; rd = {y: lin(y, p['rd']) for y in YEARS}
    half = {'car': 0.5}
    cf = {k: {y: R[k][y] * cm[y] * half.get(k, 1.0) for y in YEARS} for k in R}
    C = {g: sum(cf[k][y] * wt(y) * df(y) for k in ks for y in YEARS) for g, ks in GROUPS.items()}
    rdl = {y: -tot[y] * rd[y] * (1 - p['tax']) for y in YEARS}
    C['rd'] = sum(rdl[y] * wt(y) * df(y) for y in YEARS)
    fcf = {y: sum(cf[k][y] for k in R) + rdl[y] for y in YEARS}
    if p.get('renewal'):   # renovación: valor terminal sobre el flujo de 2045 (+2%), sin línea de plataforma
        C['plat'] = fcf[YEARS[-1]] * 1.02 / (w - 0.02) * df(YEARS[-1])
    else:
        C['plat'] = p['plat_share'] * fcf[p['plat_year']] * (1 + p['plat_g']) / (w - p['plat_g']) * df(p['plat_year'])
    C['acq'] = p['acq']
    return dict(C=C, ev=sum(C.values()), R=R, tot=tot, fcf=fcf)

def run_mt(p):
    w = p['wacc_mt']; df, wt = disc(p, w)
    rev, v = {}, p['mt26']
    for y in YEARS[:10]:   # 2026-2035
        if y > 2026: v *= 1 + lin(y, p['mt_g'])
        rev[y] = v
    fm = {y: lin(y, p['mt_m']) for y in rev}
    fcf = {y: rev[y] * fm[y] for y in rev}
    pv = sum(fcf[y] * wt(y) * df(y) for y in rev)
    tv = fcf[2035] * (1 + p['mt_perp']) / (w - p['mt_perp']) * df(2035)
    return dict(ev=pv + tv, pv=pv, tv=tv, rev=rev, fcf=fcf, tv_share=tv / (pv + tv))

def run(p):
    im, mt = run_im(p), run_mt(p)
    ev = im['ev'] + mt['ev']
    eq = ev - p['liab']
    # reparto de pasivos por valor de empresa (para el peso de cada pieza en el blend)
    im_ps = (im['ev'] - p['liab'] * im['ev'] / ev) / p['shares']
    mt_ps = (mt['ev'] - p['liab'] * mt['ev'] / ev) / p['shares']
    return dict(im=im, mt=mt, ev=ev, eq=eq, fv=eq / p['shares'], im_ps=im_ps, mt_ps=mt_ps)
