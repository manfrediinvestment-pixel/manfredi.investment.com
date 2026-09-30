# Extrae de cada comunicado trimestral (ex/*earningsrelease*) las ventas comparables sin combustible, tráfico,
# ticket y aporte del e-commerce de Walmart U.S. y Sam's Club, más los titulares (e-commerce, publicidad,
# membresías, EPS ajustado). Imprime todo para cargarlo a mano en model.py con la fuente al lado.
import glob, re
def flat(s): return re.sub(r'\s*\n\s*(?=\|)', ' ', s)   # une "Comp sales (ex. fuel)2\n | 2.6%"
for f in sorted(glob.glob('ex/*earningsrelease*.txt')):
    s = flat(open(f, encoding='utf-8').read())
    q = re.search(r'fy(\d\d)q(\d)', f); print(f'=== {q.group(2)}T FY{q.group(1)}  ({f[3:13]})')
    for seg, nxt in (('Walmart U.S. | Q', 'Walmart International | Q'), ('Sam.s Club U.S. | Q', '\n\n')):
        m = re.search(seg + r'.*?(?=' + nxt + ')', s, re.S)
        if not m: m = re.search(seg + r'.{0,900}', s, re.S)
        blk = m.group(0) if m else ''
        out = []
        for k in ('Net sales \|', r'Net sales \(ex\. fuel\) \|', r'Comp sales \(ex\. fuel\)\d? \|', 'Comp sales', 'Transactions \|', 'Average [Tt]icket \|', 'eCommerce contribution to comp \|', 'Operating [Ii]ncome \|'):
            mm = re.search(k + r'[^\n]*', blk)
            if mm: out.append(re.sub(r'\s*\|\s*', ' | ', mm.group(0))[:80])
        print(' ', seg[:12], out)
    for pat in (r'eCommerce[^.\n]{0,40}(?:up|grew|increased)[^.\n]{0,80}', r'[Aa]dvertising[^.\n]{0,60}(?:up|grew)[^.\n]{0,60}',
                r'Membership (?:fee )?(?:and other )?(?:income|revenue)[^.\n]{0,80}', r'Adjusted EPS\d? of \$[\d.]+', r'GAAP EPS of \$[\d.]+',
                r'Walmart Connect[^.\n]{0,80}', r'Walmart\+[^.\n]{0,80}', r'renewal[^.\n]{0,80}', r'profitab[^.\n]{0,100}'):
        for mm in re.findall(pat, s)[:3]: print('   ·', mm.strip()[:160])
