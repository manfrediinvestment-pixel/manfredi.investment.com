# Conecta ABBV en index.html (panel Defensivos): reemplaza la tarjeta "Próximamente" por una tarjeta activa con
# sparkline de 7 cierres mensuales (model.json["spark"]), logo y botón con miGateAnalysis, igual a las vecinas
# (LLY, JNJ, PG, UNH, WMT, KO, PEP). Acento "neutral": postura neutral, con sesgo cauteloso (como BRK.B y SAP).
# NO toca el contador "N de 10 con informe completo" (lo maneja la integración de los tres informes).
# NO se corre en la rama del informe: se corre en la integración (feat/defensivos-10-de-10).
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4].as_posix()
M = json.load(open(HERE / 'model.json', encoding='utf-8'))
p = ROOT + '/index.html'
s = open(p, encoding='utf-8').read()
sp = M['spark']; lo, hi = min(sp), max(sp)
pts = ' '.join(f'{i*15},{round(34 - (v-lo)/(hi-lo)*28)}' for i, v in enumerate(sp))
LOGO = """<img class="pick-logo" src="assets/logos/abbv.png" alt="" width="40" height="40" loading="lazy" onerror="this.outerHTML='&lt;svg class=&quot;pick-logo pick-logo--mi&quot; aria-hidden=&quot;true&quot;&gt;&lt;use href=&quot;#miMark&quot;/&gt;&lt;/svg&gt;'">"""
soon = f"""            <div class="pick-card pick-card--soon">
              <div class="pick-accent soon"></div>
              {LOGO}
              <div class="pick-info">
                <div class="pick-row1"><span class="pick-ticker">ABBV</span><span class="pick-tag pick-tag-us">USA &middot; Salud</span></div>
                <div class="pick-name">AbbVie Inc.</div>
              </div>
              <div class="pick-sparkline" style="width:90px;height:40px;"></div>
              <div class="pick-right"><span class="pick-sentiment soon">Próximamente</span></div>
            </div>
"""
card = f"""            <div class="pick-card">
              <div class="pick-accent neutral"></div>
              {LOGO}
              <div class="pick-info">
                <div class="pick-row1"><span class="pick-ticker">ABBV</span><span class="pick-tag pick-tag-us">USA &middot; Salud</span></div>
                <div class="pick-name">AbbVie Inc.</div>
              </div>
              <div class="pick-sparkline"><svg width="90" height="40" viewBox="0 0 90 40"><polyline points="{pts}" fill="none" stroke="var(--yellow)" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/></svg></div>
              <div class="pick-right"><a href="informes/abbv.html" class="pick-btn" target="_blank" rel="noopener" onclick="return miGateAnalysis(event,'ABBV')">Ver análisis &rarr;</a></div>
            </div>
"""
i = s.index('data-sector-panel="defensivos"')
assert s.count(soon) == 1, 'tarjeta ABBV Próximamente'
j = s.index(soon)
assert j > i, 'la tarjeta tiene que estar en el panel Defensivos'
s = s[:j] + card + s[j + len(soon):]
open(p, 'w', encoding='utf-8', newline='').write(s)
print('sparkline', M['spark_months'], sp, pts)
