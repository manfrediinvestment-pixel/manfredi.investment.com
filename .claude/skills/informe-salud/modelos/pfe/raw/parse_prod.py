# Lee las tablas "PFIZER INC. - REVENUES" de los comunicados de resultados (Exhibit 99 de los 8-K, ya pasados a texto)
# y guarda, por tabla, los números de cada fila (US$ millones; los guiones se descartan). Orden: mundial actual, mundial año
# anterior, EE.UU. actual, EE.UU. anterior, internacional actual, internacional anterior (si los hay) -> prod.json.
import re, json, os, glob
os.chdir(os.path.dirname(os.path.abspath(__file__)))
NUM = re.compile(r'\(?\$?\s*\d[\d,]*\)?')
def tables(path):
    s = open(path, encoding='utf-8').read()
    out = {}
    for m in re.finditer(r'PFIZER INC\. - REVENUES\s*\n\s*([A-Z\-]+(?: [A-Z\-]+)? 20\d\d) and (20\d\d)', s):
        key = m.group(1).strip()
        end = s.find('PFIZER INC', m.end())
        body = s[m.end(): end if end > 0 else None]
        rows, pending = {}, None
        for ln in body.split('\n'):
            lab = ln.split('|')[0].strip()
            rest = '|'.join(ln.split('|')[1:]) if lab else ln
            nums = []
            for c in [c.strip() for c in rest.split('|')]:
                c2 = c.replace('$', '').strip()
                if re.fullmatch(r'\(?\d[\d,]*\)?', c2): nums.append(int(c2.strip('()').replace(',', '')) * (-1 if c2.startswith('(') else 1))
            if lab and not re.fullmatch(r'[\d\W]*', lab) and lab != '(MILLIONS)':
                lab = re.sub(r'\((?:[a-z]|\d)\)$', '', lab).strip()
                if len(nums) >= 2: rows[lab] = nums; pending = None
                else: pending = lab
            elif pending and len(nums) >= 2:
                rows[pending] = nums; pending = None
        out[key] = rows
    return out
res = {}
for f in sorted(glob.glob('*ex99*.txt') + glob.glob('*exh99*.txt') + glob.glob('rel/rel_*.txt')):
    t = tables(f)
    if t: res[os.path.basename(f)] = t
json.dump(res, open('prod.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
for f, t in res.items(): print(f, {k: len(v) for k, v in t.items()})
