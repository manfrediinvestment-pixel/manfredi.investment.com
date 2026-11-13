# Extrae ventas mundiales (WW) por producto/franquicia de las tablas "Segment sales" del Exhibit 99.2 de cada 8-K.
# Uso: python parse_prod.py  -> prod.json {accesión: {periodo: {PRODUCTO: [actual, año anterior]}}}
# El nombre es la celda anterior a "US"; los valores, las dos celdas después de "WW" ("—" = 0, producto sin año anterior).
import re, glob, json
def num(x):
    x = x.replace('$', '').replace(',', '').strip()
    return float(x) if re.fullmatch(r'-?\d+(\.\d+)?', x) else None
out = {}
for f in sorted(glob.glob('*exhibit992_flat.txt')):
    s = open(f, encoding='utf-8').read()
    res = {}
    for blk in s.split('Segment sales')[1:]:
        m = re.search(r'(FIRST QUARTER|SECOND QUARTER|THIRD QUARTER|FOURTH QUARTER|SIX MONTHS|NINE MONTHS|TWELVE MONTHS)', blk[:300])
        if not m: continue
        d = res.setdefault(m.group(1), {})
        toks = [t.strip() for t in blk.split('|')]
        for i, t in enumerate(toks):
            if t != 'US' or i == 0: continue
            name = re.sub(r'\(\d\)', '', toks[i - 1]).replace('\n', ' ').strip()
            if not name or name == '$' or 'INNOVATIVE MEDICINE SEGMENT' in name or 'MEDTECH SEGMENT' in name and 'TOTAL' not in name:
                continue
            j = toks.index('WW', i)
            vals = [x for x in toks[j + 1:j + 4] if x != '$']
            cur, prev = num(vals[0]), num(vals[1])
            if cur is None: continue
            d.setdefault(name.upper(), [cur, prev if prev is not None else 0.0])
    out[f.split('_')[0]] = res
json.dump(out, open('prod.json', 'w'), indent=1)
for k, v in out.items(): print(k, {p: len(x) for p, x in v.items()})
