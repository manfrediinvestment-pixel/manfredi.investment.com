# Extrae EPS core y GAAP (trimestre, acumulado) del encabezado de cada comunicado de resultados.
import re, glob, json
out = {}
def vals_after(lines, i, n=2):
    v = re.findall(r'\$ ?\(?([0-9]+\.[0-9]{2})', lines[i])
    j = i + 1
    while len(v) < n and j < i + 8:
        v += re.findall(r'\$ ?\(?([0-9]+\.[0-9]{2})', lines[j]); j += 1
    return v[:n]
for f in sorted(glob.glob('*kxexhibit991.txt')):
    m = re.search(r'q(\d)(20\d\d)8', f)
    q, y = int(m.group(1)), int(m.group(2))
    L = open(f, encoding='utf-8').read().split('\n')[:120]
    core = gaap = None
    for i, l in enumerate(L):
        s = l.strip().rstrip('|').strip()
        if core is None and re.match(r'^Core EPS\b', s) and 'growth' not in s and 'change' not in s.lower():
            core = vals_after(L, i)
        if gaap is None and re.match(r'^EPS\b', s) and 'growth' not in s and 'change' not in s.lower():
            gaap = vals_after(L, i)
    out[f'{y}Q{q}'] = dict(core=core, gaap=gaap, f=f)
for k in sorted(out): print(k, out[k]['core'], out[k]['gaap'])
json.dump(out, open('eps_raw.json', 'w'), indent=1)
