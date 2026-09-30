import json, re, sys
M = json.load(open('model.json'))
MINUS = '−'
def get(path):
    v = M
    for p in path.split('.'):
        if isinstance(v, list): v = v[int(p)]
        else: v = v[p]
    return v
def sgn(v, s): return (MINUS + s.lstrip('-')) if v < 0 else s
def fmt(v, f):
    if f == '' : return str(v)
    if f == 'usd2': return sgn(v, '$'+f'{abs(v):,.2f}') if v<0 else '$'+f'{v:,.2f}'
    if f == 'usd0': return '$'+f'{v:,.0f}'
    if f in ('f0','f1','f2','f3'):
        s = f'{abs(v):,.{int(f[1])}f}'; return (MINUS+s) if v < 0 and float(s.replace(',',''))!=0 else s
    if f in ('x1','x2'): return f'{v:.{int(f[1])}f}x'
    if f in ('pct0','pct1','pct2'):
        s = f'{abs(v):.{int(f[3])}f}%'; return (MINUS+s) if v < 0 and float(s[:-1])!=0 else s
    if f in ('spct0','spct1','spct2'):
        s = f'{abs(v):.{int(f[4])}f}%'
        return (MINUS+s) if v < 0 and float(s[:-1])!=0 else ('+'+s if float(s[:-1])!=0 else s)
    if f in ('spp0',):  # puntos con signo, entero
        s=f'{abs(v):.0f}'; return (MINUS+s) if v<0 and s!='0' else ('+'+s if s!='0' else '0')
    if f == 'a1': return f'{abs(v):.1f}'
    if f == 'a0': return f'{abs(v):,.0f}'
    if f == 'js2': return f'{v:.2f}'
    if f == 'js1': return f'{v:.1f}'
    raise ValueError(f)
def sub(m):
    return fmt(get(m.group(1).strip()), m.group(2) or '')
src = open(sys.argv[1], encoding='utf-8').read()
out = re.sub(r'\{\{([^|}]+)\|?([^}]*)\}\}', sub, src)
assert '{{' not in out
open(sys.argv[2], 'w', encoding='utf-8', newline='\n').write(out)
print('ok', len(out))
