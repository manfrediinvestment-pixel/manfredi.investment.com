# Actualiza solo el sparkline de la tarjeta de UNH en index.html con model.json['spark'] (7 cierres mensuales).
# Misma fórmula que index_add.py. No toca nada más de la home.
import json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[5].as_posix()   # raíz del repo
M = json.load(open('model.json'))
sp = M['spark']; lo, hi = min(sp), max(sp)
pts = ' '.join(f'{i*15},{round(34 - (v-lo)/(hi-lo)*28)}' for i, v in enumerate(sp))
p = ROOT + '/index.html'
s = open(p, encoding='utf-8', newline='').read()
pat = re.compile(r'(<span class="pick-ticker">UNH</span>.*?<polyline points=")([^"]+)(")', re.S)
assert len(pat.findall(s)) == 1, 'tarjeta UNH'
s2 = pat.sub(lambda m: m.group(1) + pts + m.group(3), s, count=1)
open(p, 'w', encoding='utf-8', newline='').write(s2)
print('sparkline', sp, pts)
