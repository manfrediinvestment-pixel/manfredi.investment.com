# Recalcula los resultados publicados del Método 1 de septiembre con una calibración dada y los compara.
import json, sys, sep_params as S, sotp
X = json.load(open(sys.argv[1] if len(sys.argv) > 1 else 'calib_sep.json'))
def fv(p): return sotp.run(p)['fv']
def sc(**kw):
    p = S.scen('base', X); renewal = kw.pop('renewal', False); p.update(kw)
    if renewal: p['renewal'] = True
    return p
P = S.PUB
rows = [('Base', P['fv'], fv(sc())), ('Bear', P['bear'], fv(S.scen('bear', X))), ('Bull', P['bull'], fv(S.scen('bull', X))),
        ('Fechas más tardías', P['late'], fv(sc(dara_loe_us=2032, dara_loe_row=2034, trem_loe=2033, erl_loe=2041, spr_loe=2040, cap_loe=2040))),
        ('Erosión lenta', P['slow'], fv(sc(bio_e=[0.70, 0.45]))), ('Sin fase 3', P['no_ph3'], fv(sc(ph3_n=0))),
        ('Renovación', P['renewal'], fv(sc(renewal=True))), ('Beta propia', P['own_beta'], fv(sc(wacc_im=0.073, wacc_mt=0.073)))]
for n, a, b in rows: print(f'{n:20s} pub {a:8.2f} rec {b:8.2f} {100*(b/a-1):+6.1f}%')
