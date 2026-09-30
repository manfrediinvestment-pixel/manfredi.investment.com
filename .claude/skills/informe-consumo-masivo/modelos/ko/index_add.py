# Conecta KO en index.html (panel Defensivos): tarjeta activa con sparkline de 7 cierres mensuales y contador 5 de 10.
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[5].as_posix()   # raíz del repo
M = json.load(open('model.json'))
p = ROOT + '/index.html'
s = open(p, encoding='utf-8').read()
sp = M['spark']; lo, hi = min(sp), max(sp)
pts = ' '.join(f'{i*15},{round(34 - (v-lo)/(hi-lo)*28)}' for i, v in enumerate(sp))
LOGO = """<img class="pick-logo" src="assets/logos/ko.png" alt="" width="40" height="40" loading="lazy" onerror="this.outerHTML='&lt;svg class=&quot;pick-logo pick-logo--mi&quot; aria-hidden=&quot;true&quot;&gt;&lt;use href=&quot;#miMark&quot;/&gt;&lt;/svg&gt;'">"""
soon = f"""            <div class="pick-card pick-card--soon">
              <div class="pick-accent soon"></div>
              {LOGO}
              <div class="pick-info">
                <div class="pick-row1"><span class="pick-ticker">KO</span><span class="pick-tag pick-tag-us">USA &middot; Consumo</span></div>
                <div class="pick-name">The Coca-Cola Company</div>
              </div>
              <div class="pick-sparkline" style="width:90px;height:40px;"></div>
              <div class="pick-right"><span class="pick-sentiment soon">Próximamente</span></div>
            </div>
"""
card = f"""            <div class="pick-card">
              <div class="pick-accent neutral"></div>
              {LOGO}
              <div class="pick-info">
                <div class="pick-row1"><span class="pick-ticker">KO</span><span class="pick-tag pick-tag-us">USA &middot; Consumo</span></div>
                <div class="pick-name">The Coca-Cola Company</div>
              </div>
              <div class="pick-sparkline"><svg width="90" height="40" viewBox="0 0 90 40"><polyline points="{pts}" fill="none" stroke="var(--yellow)" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/></svg></div>
              <div class="pick-right"><a href="informes/ko.html" class="pick-btn" target="_blank" rel="noopener" onclick="return miGateAnalysis(event,'KO')">Ver análisis &rarr;</a></div>
            </div>
"""
assert s.count(soon) == 1, 'tarjeta KO Próximamente'
s = s.replace(soon, card)   # en el mismo lugar: queda después de UNH, como las demás activas
old = '<div class="inv-panel-progress">4 de 10 con informe completo</div>'
assert s.count(old) == 1
s = s.replace(old, '<div class="inv-panel-progress">5 de 10 con informe completo</div>')
open(p, 'w', encoding='utf-8', newline='\r\n').write(s)   # el index.html del working tree usa CRLF
print('sparkline', sp, pts)
