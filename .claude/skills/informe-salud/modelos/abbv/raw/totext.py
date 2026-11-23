# Convierte los .htm bajados de EDGAR a texto plano (una celda de tabla separada por " | ").
import re, glob, html, os
for f in glob.glob('*.htm'):
    out = f[:-4] + '.txt'
    if os.path.exists(out): continue
    s = open(f, encoding='utf-8', errors='ignore').read()
    s = re.sub(r'(?is)<(script|style).*?</\1>', '', s)
    s = re.sub(r'(?is)<ix:header>.*?</ix:header>', '', s)
    s = re.sub(r'(?i)</t[dh]>', ' | ', s)
    s = re.sub(r'(?i)</(p|div|tr|br|li|h\d)>|<br\s*/?>', '\n', s)
    s = re.sub(r'<[^>]+>', '', s)
    s = html.unescape(s).replace('\xa0', ' ')
    s = re.sub(r'[ \t]+', ' ', s)
    s = re.sub(r'( \| ){2,}', ' | ', s)
    s = re.sub(r'\n\s*\n+', '\n', s)
    open(out, 'w', encoding='utf-8').write(s)
    print(out, len(s))
