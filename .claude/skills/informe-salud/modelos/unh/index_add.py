# Conecta UNH en index.html (panel Defensivos): tarjeta activa con sparkline de 7 cierres mensuales y contador 4 de 10.
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[5].as_posix()   # raíz del repo
M = json.load(open('model.json'))
p = ROOT + '/index.html'
s = open(p, encoding='utf-8').read()
sp = M['spark']; lo, hi = min(sp), max(sp)
pts = ' '.join(f'{i*15},{round(34 - (v-lo)/(hi-lo)*28)}' for i, v in enumerate(sp))
LOGO = """<img class="pick-logo" src="assets/logos/unh.png" alt="" width="40" height="40" loading="lazy" onerror="this.outerHTML='&lt;svg class=&quot;pick-logo pick-logo--mi&quot; aria-hidden=&quot;true&quot;&gt;&lt;use href=&quot;#miMark&quot;/&gt;&lt;/svg&gt;'">"""
soon = f"""            <div class="pick-card pick-card--soon">
              <div class="pick-accent soon"></div>
              {LOGO}
              <div class="pick-info">
                <div class="pick-row1"><span class="pick-ticker">UNH</span><span class="pick-tag pick-tag-us">USA &middot; Salud</span></div>
                <div class="pick-name">UnitedHealth Group Incorporated</div>
              </div>
              <div class="pick-sparkline" style="width:90px;height:40px;"></div>
              <div class="pick-right"><span class="pick-sentiment soon">Próximamente</span></div>
            </div>
"""
card = f"""            <div class="pick-card">
              <div class="pick-accent neutral"></div>
              {LOGO}
              <div class="pick-info">
                <div class="pick-row1"><span class="pick-ticker">UNH</span><span class="pick-tag pick-tag-us">USA &middot; Salud</span></div>
                <div class="pick-name">UnitedHealth Group Incorporated</div>
              </div>
              <div class="pick-sparkline"><svg width="90" height="40" viewBox="0 0 90 40"><polyline points="{pts}" fill="none" stroke="var(--yellow)" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/></svg></div>
              <div class="pick-right"><a href="informes/unh.html" class="pick-btn" target="_blank" rel="noopener" onclick="return miGateAnalysis(event,'UNH')">Ver análisis &rarr;</a></div>
            </div>
"""
assert s.count(soon) == 1, 'tarjeta UNH Próximamente'
s = s.replace(soon, '')
anchor = """onclick="return miGateAnalysis(event,'PG')">Ver análisis &rarr;</a></div>
            </div>
"""
assert s.count(anchor) == 1
s = s.replace(anchor, anchor + card)
old = '<div class="inv-panel-progress">3 de 10 con informe completo</div>'
assert s.count(old) == 1
s = s.replace(old, '<div class="inv-panel-progress">4 de 10 con informe completo</div>')
open(p, 'w', encoding='utf-8', newline='').write(s)
print('sparkline', sp, pts)
