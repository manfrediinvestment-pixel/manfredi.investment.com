# Calibra las formas que el informe de septiembre no publicó contra los componentes que sí publicó (caso Base).
# Se corre a mano: python calib_sep.py -> calib_sep.json (y se copia a sep_params.CAL).
import json, copy
import numpy as np
from scipy.optimize import least_squares
import sep_params as S, sotp

NAMES = ['bio_tail', 'sm_tail', 'trem_pky', 'onc_pky', 'ico_pky', 'ima_pky', 'oth_g', 'ph3_ry', 'dara_g_late',
         'dara_scale', 'mt_decel_start', 'oth_gy']
X0 = [0.15, 0.15, 2030, 2031, 2032, 2031, 0.05, 5, 0.02, 1.0, 2029.5, 2030]
LO = [0.0, 0.0, 2027.5, 2028, 2028, 2028, 0.0, 2, -0.03, 0.97, 2029.0, 2027]
HI = [0.45, 0.45, 2031, 2034, 2036, 2034, 0.15, 9, 0.06, 1.03, 2033.0, 2034]
P = S.PUB

def comp(x):
    X = dict(zip(NAMES, x))
    p = S.scen('base', X)
    r = sotp.run(p)
    C = r['im']['C']
    res = [(C[k] - P[k]) / 2.0 for k in ('mat', 'dara', 'trem', 'onc', 'plat', 'ico', 'ph3', 'oth', 'rd')]
    res += [(r['mt']['ev'] - P['mt_ev']) / 2.0, (r['mt']['tv_share'] * 100 - P['mt_tv_share']) / 1.0,
            (r['im']['tot'][2030] - P['im_rev_2030']) / 1.0, (r['im']['tot'][2035] - P['im_rev_2035']) / 1.0,
            (r['im']['tot'][2027] + r['mt']['rev'][2027] - P['rev_2027']) / 1.0,
            (r['fv'] - P['fv']) / 0.25]
    pl = S.scen('base', X); pl.update(dara_loe_us=2032, dara_loe_row=2034, trem_loe=2033, erl_loe=2041, spr_loe=2040, cap_loe=2040)
    res += [(sotp.run(pl)['fv'] - P['late']) / 2.0]
    return np.array(res), r

if __name__ == '__main__':
    sol = least_squares(lambda x: comp(x)[0], X0, bounds=(LO, HI), diff_step=1e-3)
    X = dict(zip(NAMES, [float(v) for v in sol.x]))
    res, r = comp(sol.x)
    json.dump(X, open('calib_sep.json', 'w'), indent=1)
    print(json.dumps(X, indent=1))
    print({k: round(v, 2) for k, v in r['im']['C'].items()}, 'MT', round(r['mt']['ev'], 2), round(r['mt']['tv_share'], 3), 'fv', round(r['fv'], 2))
    print('IM', round(r['im']['tot'][2030], 2), round(r['im']['tot'][2035], 2), 'rev27', round(r['im']['tot'][2027] + r['mt']['rev'][2027], 2))
