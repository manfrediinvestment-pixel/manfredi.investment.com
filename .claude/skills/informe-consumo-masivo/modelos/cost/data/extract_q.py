# Imprime, de cada comunicado trimestral (8-K ítem 2.02, anexo 99.1), las líneas del estado de resultados del trimestre
# y la tabla de ventas comparables. Insumo de Q en model.py (se copian a mano y model.py las verifica contra el anual).
import glob, re
ITEMS = ['Net sales', 'Membership fees', 'Total revenue', 'Merchandise costs', 'Selling, general and administrative',
         'Operating income', 'NET INCOME', 'Diluted']
for f in sorted(glob.glob('ex/*_8-K_cost*ex991*.txt')):
    s = open(f, encoding='utf-8').read()
    if 'OPERATING RESULTS' not in s.upper(): continue
    t = s[s.find('CONSOLIDATED STATEMENTS OF INCOME'):]
    row = {}
    for it in ITEMS:
        m = re.search(r'\n' + re.escape(it) + r'[^\n|]*\|([^\n]*)', t)
        if m: row[it] = [x for x in re.findall(r'[\d,.]+', m.group(1)) if x not in ('.',)][:2]
    hdr = re.search(r'operating results for the ([^,]+?) ended ([A-Za-z]+ \d+, \d{4})', s)
    comps = re.search(r'Comparable sales for the.*?Total Company[^\n]*', s, re.S)
    print(f[3:13], hdr.group(1) if hdr else '', hdr.group(2) if hdr else '')
    for k, v in row.items(): print('   ', k, v)
    if comps: print('   ', re.sub(r'\s*\|\s*', ' ', comps.group(0)).replace('\n', ' ')[:600])
