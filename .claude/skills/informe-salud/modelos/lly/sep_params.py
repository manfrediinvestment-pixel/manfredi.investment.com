# Supuestos del Método 1 de la edición de septiembre (datos al 2T 2026, valuación al 30-sep-2026).
# Lo publicado en lly.html (tabla de supuestos) va tal cual; las trayectorias que el HTML no publica (forma de la
# rampa, cola de erosión, nivel 2026) se calibraron contra los valores por componente publicados — ver README.md.
import copy
LEG = {  # Trulicity, Jardiance, Taltz, Verzenio (US$ miles de millones por año)
 'trul': {2026: 4.0, 2027: 3.4, 2028: 2.0, 2029: 1.2, 2030: 0.8, 2031: 0.5, 2032: 0.3, 2036: 0.0},
 'jard': {2026: 4.3, 2027: 4.0, 2028: 4.0, 2029: 0.3, 2045: 0.3},
 'taltz': {2026: 3.5, 2029: 3.5, 2030: 2.6, 2031: 1.6, 2032: 1.0, 2033: 0.6, 2036: 0.2, 2045: 0.0},
 'verz': {2026: 5.9, 2027: 6.1, 2028: 5.0, 2030: 5.0, 2031: 2.0, 2032: 0.6, 2033: 0.3, 2036: 0.0},
}
BASE = dict(
    y0=2026, stub=0.25, wacc=0.0822, tax=0.185, shares=0.894, net_debt=45.958, acq=17.52,
    cm={2026: 0.515, 2030: 0.55}, capex={2026: 0.12, 2030: 0.06}, rd={2026: 0.171, 2030: 0.155},
    tirz_prem=0.03,
    tirz_path={2026: 57.0, 2027: 60.5, 2030: 65.0, 2035: 65.0}, tirz_loe=2036, tirz_e=[0.225, 0.50], tirz_tail=0.25,
    found_path={2026: 0.5, 2027: 3.0, 2031: 15.0}, found_loe=2038, found_e1=0.70, found_tail=0.30,
    reta_path={2027: 0.0, 2028: 2.0, 2033: 20.0}, reta_loe=2041, reta_pos=0.906,
    leg=LEG,
    rest0=12.0, rest_g1=0.08, rest_g2=0.03, rest_g3=0.0,
    ph3_n=5, ph3_peak=3.5, ph3_pos=0.524, ph3_ramp={2027: 0.0, 2028: 0.1, 2033: 1.0},
    plat_share=0.40, plat_year=2040, plat_g=0.02,
)
# Formas calibradas (calib_sep.py -> calib_sep.json; copiadas acá para que el modelo no dependa del optimizador)
CAL = {"rest0": 14.0, "rest_g3": -0.176747, "found_2027": 0.5, "found_peak_year": 2030.998669, "found_tail": 0.7, "reta_2028": 0.574831, "reta_peak_year": 2033.230729, "tirz_tail": 0.22473, "ph3_start": 2026.5, "ph3_peak_year": 2037.720339, "legacy_k": 1.084477, "tirz_2026": 52.0}

def apply(p, X=None):
    X = X or CAL
    p['rest0'] = X['rest0']; p['rest_g3'] = X['rest_g3']; p['found_tail'] = X['found_tail']; p['tirz_tail'] = X['tirz_tail']
    pk = max(p['found_path'].values())
    p['found_path'] = {2026: p['found_path'][2026], 2027: X['found_2027'] * pk / 15.0, X['found_peak_year']: pk}
    rp = max(p['reta_path'].values())
    p['reta_path'] = {2027: 0.0, 2028: X['reta_2028'] * rp / 20.0, X['reta_peak_year']: rp}
    p['ph3_ramp'] = {X['ph3_start']: 0.0, X['ph3_peak_year']: 1.0}
    p['leg'] = {k: {y: v * X['legacy_k'] for y, v in d.items()} for k, d in p['leg'].items()}
    tp = dict(p['tirz_path']); tp[2026] = X['tirz_2026'] if p.get('sep_2026', True) else tp[2026]; p['tirz_path'] = tp
    return p

def scen(name):
    p = copy.deepcopy(BASE)
    if name == 'bear':
        p.update(wacc=0.0897, cm={2026: 0.515, 2030: 0.52}, capex={2026: 0.12, 2030: 0.07}, rd={2026: 0.171, 2030: 0.165},
                 tirz_path={2026: 57.0, 2027: 57.0, 2035: 48.0}, found_path={2026: 0.5, 2027: 2.0, 2031: 7.0},
                 reta_path={2027: 0.0, 2028: 1.0, 2033: 10.0}, rest_g1=0.05, rest_g2=0.0)
    if name == 'bull':
        p.update(wacc=0.0747, cm={2026: 0.515, 2030: 0.57}, capex={2026: 0.12, 2030: 0.055}, rd={2026: 0.171, 2030: 0.15},
                 tirz_path={2026: 57.0, 2027: 62.0, 2030: 72.0, 2038: 72.0}, tirz_loe=2039,
                 found_path={2026: 0.5, 2027: 3.5, 2031: 18.0}, found_loe=2041,
                 reta_path={2027: 0.0, 2028: 2.5, 2033: 27.0}, rest_g1=0.11, rest_g2=0.05)
    return apply(p)
