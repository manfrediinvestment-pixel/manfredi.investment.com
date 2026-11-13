# Calibra las formas que el HTML de septiembre no publica (nivel 2026 de tirzepatida y del resto, rampas de Foundayo,
# retatrutida y fase 3, cola de erosión, factor de legados) contra lo que sí publica: componentes del caso Base,
# ingresos 2030/2031, margen de FCF 2030, franquicia de incretinas 2030/2035 y fair value Base.
# Solo se corre a mano; el resultado se copia a sep_params.CAL.
import json, copy
from scipy.optimize import least_squares
from sotp import run
import sep_params as S
T = dict(tirz=243.7, rest=69.0, reta=48.8, platform=41.5, found=37.4, legacy=26.7, ph3=24.4, rd=-117.7)
NAMES = ['rest0', 'rest_g3', 'found_2027', 'found_peak_year', 'found_tail', 'reta_2028', 'reta_peak_year', 'tirz_tail',
         'ph3_start', 'ph3_peak_year', 'legacy_k', 'tirz_2026']
def raw(): p = copy.deepcopy(S.BASE); return p
def resid(x):
    r = run(S.apply(raw(), dict(zip(NAMES, x)))); C = r['C']; out = [(C[k] - v) / abs(v) for k, v in T.items()]
    out += [(r['tot'][2030] - 115.5) / 115.5 * 3, (r['tot'][2031] - 119.1) / 119.1 * 3, (r['fcfm'][2030] - 0.381) * 10,
            (sum(r['R'][k][2030] for k in ('tirz', 'found', 'reta')) - 85) / 85,
            (sum(r['R'][k][2035] for k in ('tirz', 'found', 'reta')) - 98) / 98, (r['fv'] - 386.44) / 386.44 * 5]
    return out
if __name__ == '__main__':
    x0 = [12.0, -0.03, 3.0, 2031.0, 0.30, 2.0, 2033.0, 0.25, 2027.5, 2033.0, 1.0, 57.0]
    lb = [9.0, -0.25, 0.5, 2029.0, 0.05, 0.3, 2030.5, 0.05, 2026.5, 2030.0, 0.6, 52.0]
    ub = [14.0, 0.03, 8.0, 2034.0, 0.70, 8.0, 2036.0, 0.60, 2030.0, 2038.0, 1.5, 62.0]
    s = least_squares(resid, x0, bounds=(lb, ub))
    X = dict(zip(NAMES, [float(v) for v in s.x])); json.dump(X, open('calib_sep.json', 'w'), indent=1); print(json.dumps(X, indent=1))
