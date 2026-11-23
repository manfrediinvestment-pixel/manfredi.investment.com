# Conecta COST en index.html (panel Defensivos): reemplaza la tarjeta "Próximamente" de COST por la tarjeta activa, en el
# mismo lugar, con sparkline de 7 cierres mensuales (may-2026 a oct-2026 + 20-nov-2026) y acento según la postura del modelo
# ("down" = neutral con sesgo bajista, como WMT). NO toca el contador "N de 10": lo actualiza la integración.
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4].as_posix()
M = json.load(open(HERE/'model.json'))
p = ROOT + '/index.html'
s = open(p, encoding='utf-8', newline='').read()        # conserva los finales de línea del archivo (CRLF)
NL = chr(13) + chr(10) if chr(13) + chr(10) in s else chr(10)
sp = M['spark']; lo, hi = min(sp), max(sp)
pts = ' '.join(f'{i*15},{round(34 - (v-lo)/(hi-lo)*28)}' for i, v in enumerate(sp))
LOGO = """<img class="pick-logo" src="assets/logos/cost.png" alt="" width="40" height="40" loading="lazy" onerror="this.outerHTML='&lt;svg class=&quot;pick-logo pick-logo--mi&quot; aria-hidden=&quot;true&quot;&gt;&lt;use href=&quot;#miMark&quot;/&gt;&lt;/svg&gt;'">"""
soon = f"""            <div class="pick-card pick-card--soon">
              <div class="pick-accent soon"></div>
              {LOGO}
              <div class="pick-info">
                <div class="pick-row1"><span class="pick-ticker">COST</span><span class="pick-tag pick-tag-us">USA &middot; Consumo</span></div>
                <div class="pick-name">Costco Wholesale Corporation</div>
              </div>
              <div class="pick-sparkline" style="width:90px;height:40px;"></div>
              <div class="pick-right"><span class="pick-sentiment soon">Próximamente</span></div>
            </div>
"""
card = f"""            <div class="pick-card">
              <div class="pick-accent {M['stance_accent']}"></div>
              {LOGO}
              <div class="pick-info">
                <div class="pick-row1"><span class="pick-ticker">COST</span><span class="pick-tag pick-tag-us">USA &middot; Consumo</span></div>
                <div class="pick-name">Costco Wholesale Corporation</div>
              </div>
              <div class="pick-sparkline"><svg width="90" height="40" viewBox="0 0 90 40"><polyline points="{pts}" fill="none" stroke="var(--yellow)" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/></svg></div>
              <div class="pick-right"><a href="informes/cost.html" class="pick-btn" target="_blank" rel="noopener" onclick="return miGateAnalysis(event,'COST')">Ver análisis &rarr;</a></div>
            </div>
"""
assert M['stance_accent'] == 'down'
soon = soon.replace('\n', NL); card = card.replace('\n', NL)
assert s.count(soon) == 1, 'tarjeta COST Próximamente (¿ya se conectó?)'
i = s.index('data-sector-panel="defensivos"'); j = s.index(soon)
assert j > i, 'la tarjeta de COST no está en el panel Defensivos'
s = s.replace(soon, card)
open(p, 'w', encoding='utf-8', newline='').write(s)
print('sparkline', sp, pts)
