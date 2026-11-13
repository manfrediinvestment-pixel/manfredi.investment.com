# Supuestos del Método 1 de la edición de septiembre (datos al 2T 2026, valuación al 30-sep-2026).
# Lo publicado en jnj.html (tabla de supuestos y texto de la Sección 13) va tal cual. Lo que el HTML no publica
# (nivel 2026 de cada producto, año del pico de cada rampa, cola de erosión después del año 2, crecimiento de
# Darzalex en el resto del mundo entre 2030 y su LOE, crecimiento de los productos del grupo "otros", rampa de la
# fase 3, forma de la desaceleración de MedTech) se calibró contra los componentes publicados — ver calib_sep.py y README.md.
import copy

# Niveles 2026 de septiembre: primer semestre 2026 real + segundo semestre 2025 x (1S26/1S25) (10-K 2025 y 10-Q 2T26),
# en US$ miles de millones. Caplyta (comprada en abril de 2025, sin primer semestre comparable): 2 x 1S26 x 1.05.
LVL_SEP = dict(dara26=17.305, trem26=8.794, ste26=2.588, erl26=4.138, imb26=2.461, car26=2.929, spr26=2.431,
               cap26=1.325, onc26=3.014, ico26=0.10, ima26=0.20, mat26=21.1)

BASE = dict(
    stub=0.25, tax=0.175, shares=2.4401, liab=28.278 + 1.785 + 5.5 + 0.9, acq=4.835,
    wacc_im=0.0757, wacc_mt=0.0831,
    cm={2026: 0.431, 2030: 0.431}, rd={2026: 0.192, 2030: 0.18},
    dara_g={2027: 0.11, 2028: 0.08, 2029: 0.04, 2030: 0.02}, dara_us=0.57, dara_loe_us=2029, dara_loe_row=2031,
    bio_e=[0.59, 0.28], sm_e=[0.25, 0.12], bio_tail=0.15, sm_tail=0.15, loe_lag=1,
    trem_pk=13.0, trem_pky=2030, trem_loe=2031,
    onc_pk=7.6, onc_pky=2031, onc_loe=2034,
    ico_pk=5.0, ico_pky=2032, ico_loe=2041,
    ima_pk=2.0, ima_pky=2031, ima_loe=2037,
    erl_loe=2032, ira_erl=0.08, spr_loe=2033, car_loe=2034, cap_loe=2029, imb_loe=2032, imb_d=0.12, oth_g=0.05,
    mat_g=-0.07,
    ph3_n=5.5, ph3_pk=2.0, ph3_pos=0.524, ph3_l=2029, ph3_ry=5,
    plat_share=0.40, plat_year=2040, plat_g=0.02,
    mt26=35.65, mt_g={2027: 0.045, 2029: 0.045, 2034: 0.03, 2035: 0.03}, mt_m={2026: 0.143, 2030: 0.158}, mt_perp=0.025,
    **LVL_SEP)

# Formas calibradas (calib_sep.py -> calib_sep.json; copiadas acá para que el modelo no dependa del optimizador)
CAL = {"bio_tail": 0.207993, "sm_tail": 0.256659, "trem_pky": 2030.176778, "onc_pky": 2030.51324, "ico_pky": 2032.082977, "ima_pky": 2028.777169, "oth_g": 0.109357, "ph3_ry": 6.998666, "dara_g_late": -0.022797, "dara_scale": 1.000358, "mt_decel_start": 2029.116258, "oth_gy": 2031.644544}

def apply(p, X=None):
    X = CAL if X is None else X
    for k, v in X.items():
        if k == 'dara_g_late': p['dara_g'] = dict(p['dara_g']); p['dara_g'][2030] = v
        elif k == 'mt_decel_start': p['mt_g'] = {2027: 0.045, round(v): 0.045, 2034: 0.03, 2035: 0.03} if round(v) < 2034 else p['mt_g']
        elif k == 'oth_gy': p['oth_gy'] = round(v)
        elif k == 'dara_scale': p['dara26'] = LVL_SEP['dara26'] * v
        else: p[k] = v
    return p

def scen(name, X=None):
    p = copy.deepcopy(BASE)
    if name == 'bear':
        p.update(wacc_im=0.0832, wacc_mt=0.0906, cm={2026: 0.431, 2030: 0.411}, rd={2026: 0.192, 2030: 0.19},
                 dara_g={2027: 0.08, 2028: 0.05, 2029: 0.01, 2030: 0.0}, trem_pk=11.0, ico_pk=3.0, ima_pk=1.2,
                 onc_pk=5.5, mat_g=-0.10, ph3_pk=1.5)
    if name == 'bull':
        p.update(wacc_im=0.0682, wacc_mt=0.0756, cm={2026: 0.431, 2030: 0.446}, rd={2026: 0.192, 2030: 0.175},
                 dara_g={2027: 0.13, 2028: 0.10, 2029: 0.06, 2030: 0.03}, dara_loe_us=2032, dara_loe_row=2034,
                 bio_e=[0.70, 0.45], trem_pk=14.5, trem_loe=2033, ico_pk=8.0, ima_pk=3.0, onc_pk=9.5, onc_loe=2036,
                 erl_loe=2041, spr_loe=2040, cap_loe=2040, mat_g=-0.045, ph3_pk=2.5)
    p = apply(p, X)
    if name == 'bear': p['dara_g'] = {2027: 0.08, 2028: 0.05, 2029: 0.01, 2030: 0.0}
    if name == 'bull': p['dara_g'] = {2027: 0.13, 2028: 0.10, 2029: 0.06, 2030: 0.03}
    return p

# Componentes publicados (caso Base, US$ miles de millones) y otros resultados del Método 1 de septiembre
PUB = dict(mat=57.8, dara=41.4, trem=27.7, onc=19.1, plat=17.5, ico=15.4, ph3=13.3, oth=44.7, acq=4.8, rd=-79.6,
           im_ev=162.3, mt_ev=112.2, liab=36.5, eq=238.1, fv=97.56, mt_tv_share=61.5,
           im_rev_2030=76.2, im_rev_2035=39.5, rev_2027=107.7,
           bear=68.30, bull=163.58, late=113.18, slow=100.47, no_ph3=92.18, renewal=146.36, own_beta=108.61,
           im_ps=57.68, mt_ps=39.87, ev_w=110.05,
           im_rev_bear=(66.2, 29.7), im_rev_bull=(94.7, 78.3))
