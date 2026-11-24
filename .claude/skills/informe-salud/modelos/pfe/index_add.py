# Conecta PFE en index.html (panel Defensivos): reemplaza la tarjeta "Próximamente" de PFE por una tarjeta activa, en el
# mismo lugar, con sparkline de 7 cierres mensuales, acento según la postura del modelo y botón con miGateAnalysis.
# NO toca el contador "N de 10 con informe completo" (lo ajusta la integración de defensivos).
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4].as_posix()
M = json.load(open(HERE / 'model.json', encoding='utf-8'))
p = ROOT + '/index.html'
s = open(p, encoding='utf-8', newline='').read()   # conserva los fines de línea del archivo (CRLF)
NL = chr(13) + chr(10) if chr(13) + chr(10) in s else chr(10)
sp = M['spark']; lo, hi = min(sp), max(sp)
pts = ' '.join(f'{i*15},{round(34 - (v-lo)/(hi-lo)*28)}' for i, v in enumerate(sp))
LOGO = """<img class="pick-logo" src="assets/logos/pfe.png" alt="" width="40" height="40" loading="lazy" onerror="this.outerHTML='&lt;svg class=&quot;pick-logo pick-logo--mi&quot; aria-hidden=&quot;true&quot;&gt;&lt;use href=&quot;#miMark&quot;/&gt;&lt;/svg&gt;'">"""
soon = f"""            <div class="pick-card pick-card--soon">
              <div class="pick-accent soon"></div>
              {LOGO}
              <div class="pick-info">
                <div class="pick-row1"><span class="pick-ticker">PFE</span><span class="pick-tag pick-tag-us">USA &middot; Salud</span></div>
                <div class="pick-name">Pfizer Inc.</div>
              </div>
              <div class="pick-sparkline" style="width:90px;height:40px;"></div>
              <div class="pick-right"><span class="pick-sentiment soon">Próximamente</span></div>
            </div>
"""
card = f"""            <div class="pick-card">
              <div class="pick-accent {M['card_accent']}"></div>
              {LOGO}
              <div class="pick-info">
                <div class="pick-row1"><span class="pick-ticker">PFE</span><span class="pick-tag pick-tag-us">USA &middot; Salud</span></div>
                <div class="pick-name">Pfizer Inc.</div>
              </div>
              <div class="pick-sparkline"><svg width="90" height="40" viewBox="0 0 90 40"><polyline points="{pts}" fill="none" stroke="var(--yellow)" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/></svg></div>
              <div class="pick-right"><a href="informes/pfe.html" class="pick-btn" target="_blank" rel="noopener" onclick="return miGateAnalysis(event,'PFE')">Ver análisis &rarr;</a></div>
            </div>
"""
soon, card = soon.replace(chr(10), NL), card.replace(chr(10), NL)
i = s.index('data-sector-panel="defensivos"')
assert s.count(soon) == 1 and s.index(soon) > i, 'tarjeta PFE Próximamente en el panel Defensivos'
s = s.replace(soon, card)
open(p, 'w', encoding='utf-8', newline='').write(s)
print('PFE activa · acento', M['card_accent'], '· sparkline', sp, pts)
