# Conecta WMT en index.html (panel Defensivos): tarjeta activa con sparkline de 7 cierres mensuales y contador +1.
# Mismo formato que las tarjetas activas (LLY, JNJ, PG, UNH). Acento "down": postura neutral con sesgo bajista (como ARM).
import json, re
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4].as_posix()
M = json.load(open(HERE/'model.json'))
p = ROOT + '/index.html'
s = open(p, encoding='utf-8').read()
sp = M['spark']; lo, hi = min(sp), max(sp)
pts = ' '.join(f'{i*15},{round(34 - (v-lo)/(hi-lo)*28)}' for i, v in enumerate(sp))
LOGO = """<img class="pick-logo" src="assets/logos/wmt.png" alt="" width="40" height="40" loading="lazy" onerror="this.outerHTML='&lt;svg class=&quot;pick-logo pick-logo--mi&quot; aria-hidden=&quot;true&quot;&gt;&lt;use href=&quot;#miMark&quot;/&gt;&lt;/svg&gt;'">"""
soon = f"""            <div class="pick-card pick-card--soon">
              <div class="pick-accent soon"></div>
              {LOGO}
              <div class="pick-info">
                <div class="pick-row1"><span class="pick-ticker">WMT</span><span class="pick-tag pick-tag-us">USA &middot; Consumo</span></div>
                <div class="pick-name">Walmart Inc.</div>
              </div>
              <div class="pick-sparkline" style="width:90px;height:40px;"></div>
              <div class="pick-right"><span class="pick-sentiment soon">Próximamente</span></div>
            </div>
"""
card = f"""            <div class="pick-card">
              <div class="pick-accent down"></div>
              {LOGO}
              <div class="pick-info">
                <div class="pick-row1"><span class="pick-ticker">WMT</span><span class="pick-tag pick-tag-us">USA &middot; Consumo</span></div>
                <div class="pick-name">Walmart Inc.</div>
              </div>
              <div class="pick-sparkline"><svg width="90" height="40" viewBox="0 0 90 40"><polyline points="{pts}" fill="none" stroke="var(--yellow)" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/></svg></div>
              <div class="pick-right"><a href="informes/wmt.html" class="pick-btn" target="_blank" rel="noopener" onclick="return miGateAnalysis(event,'WMT')">Ver análisis &rarr;</a></div>
            </div>
"""
assert s.count(soon) == 1, 'tarjeta WMT Próximamente'
s = s.replace(soon, '')
# la tarjeta activa va después de la última activa del panel (UNH)
anchor = """onclick="return miGateAnalysis(event,'UNH')">Ver análisis &rarr;</a></div>
            </div>
"""
assert s.count(anchor) == 1
s = s.replace(anchor, anchor + card)
# contador del panel Defensivos: se lee el número actual y se suma 1
i = s.index('data-sector-panel="defensivos"')
m = re.compile(r'<div class="inv-panel-progress">(\d+) de 10 con informe completo</div>').search(s, i)
assert m and m.start() - i < 300
n = int(m.group(1)) + 1
s = s[:m.start()] + f'<div class="inv-panel-progress">{n} de 10 con informe completo</div>' + s[m.end():]
open(p, 'w', encoding='utf-8', newline='').write(s)
print('sparkline', sp, pts, '| contador', n)
