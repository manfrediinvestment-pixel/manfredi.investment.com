# Actualiza informes/dis.html (edición sep-2026, 3T FY26) a la edición nov-2026 (4T FY26 + año completo) sin rediseñar:
# misma estructura de 14 secciones, mismas tablas y gráficos, mismo estilo (decimales con coma). Toda cifra derivada sale de
# resultados.json (valuacion.py). Se corre UNA vez sobre la versión de septiembre (falla si no encuentra los bloques).
import json, re, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
R = json.load(open(HERE/'resultados.json', encoding='utf-8'))
F = ROOT/'informes'/'dis.html'
s = open(F, encoding='utf-8').read()

def es(v, d=2):
    t = f'{abs(v):,.{d}f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
    return ('−' if v < 0 and float(f'{abs(v):.{d}f}') != 0 else '') + t
def usd(v, d=2): return ('−$' if v < 0 else '$') + es(abs(v), d)
def pct(v, d=1): return ('+' if v > 0 else '') + es(v, d) + '%'
def x(v, d=1): return es(v, d) + 'x'
g = R
PR = usd(g['price']); BL = usd(g['blend'])

def between(a, b, new, keep_b=True):
    global s
    i = s.index(a); j = s.index(b, i)
    s = s[:i] + new + (s[j:] if keep_b else s[j+len(b):])
def rep(a, b):
    global s
    assert s.count(a) == 1, ('no único', a[:80], s.count(a))
    s = s.replace(a, b)

# ---------------- cabecera, meta y portada ----------------
rep('.verdict-note{color:#5d646f !important;}', '.verdict-note{color:var(--muted) !important;}')
rep("""el conglomerado de medios cotiza a ~15x utilidad ajustada forward mientras la rentabilidad de streaming se inflexiona, ESPN migra a directo-al-consumidor, D'Amaro asume como CEO y el capex de parques sigu""",
    f"""cierre del año fiscal 2026 de 53 semanas, dividendo +33%, recompras de US$9.000 millones, fin del dato de rentabilidad del streaming y ahorro de US$3.000 millones; cotiza a ~{es(g['pe_ntm'],1)}x la utilidad ajustada del año fiscal 2027 mientras el capex de parques sigu""")
between('<div class="doctype">', '</div>\n</div>', '<div class="doctype">Equity Research · Informe Institucional<br>Datos al 4T y año fiscal 2026 (cerrado 3-oct-2026, 53 semanas; reporte y 10-K del 17-nov-2026) · Precio al 20 nov 2026')
between('<div class="fv-value">', '<div class="verdict-note">', f"""<div class="fv-value">{BL}</div>
        <div class="fv-gap {'pos' if g['blend'] > g['price'] else 'neg'}">vs. {PR} mercado · {pct(g['blend_gap'])}</div>
      </div>
    </div>
    <div class="verdict-bar">
      <div class="verdict-stance">POSTURA DEL ANÁLISIS: <strong>NEUTRAL, LEVEMENTE POR DEBAJO DEL PRECIO</strong> — el blend ponderado de cinco métodos ({BL}) queda {pct(g['blend_gap'])} contra el precio de mercado. Los métodos que no usan el precio de Disney —DCF Base ({usd(g['dcf_base'])}), suma de partes por segmento ({usd(g['sotp_base'])}) y comparables ({usd(g['comp'])})— promedian {usd(g['indep'])}; los anclados al mercado —reversión en ventana limpia ({usd(g['rev'])}) y consenso de Wall Street ({usd(g['cons'])})—, {usd(g['anch'])}. Contra la edición de septiembre (publicada como promedio simple, $106,28 con la acción a $104,16) el fair value sube y la acción sube más ({pct(g['price_chg'])}). Se valuó a Disney con la misma vara que a Netflix, Comcast y el resto de las compañías de medios y plataformas de esta cobertura (ver Sección 13).</div>
      """)
between('<div class="thesis-block">', '<p class="footnote">Cifras fundamentales', f"""<div class="thesis-block">
        El 17 de noviembre de 2026, Disney reportó su cuarto trimestre y el año fiscal 2026 completo (cerrado el 3-oct-2026,
        un año de 53 semanas): ingresos de US$102.344 millones ({pct(g['fy_rev_g'])}), utilidad operativa de segmentos de
        US$19.728 millones ({pct(g['fy_segoi_g'])}) y utilidad diluida por acción ajustada de US$7,02 ({pct(g['fy_eps_g'])}; {pct(g['fy_eps_g_ex53'])}
        sin la semana extra, por encima de la guía de ~12%). El cuarto trimestre trajo ingresos de US$25.947 millones
        ({pct(g['q4_rev_g'])}, con ~8 puntos de la semana 53) y un streaming (Disney+/Hulu SVOD) con margen de 11,5% en el año.
        Disney anunció un dividendo de US$2,00 para el año fiscal 2027 (+33%), recompras de ~US$9.000 millones, un plan de
        ahorro de ~US$3.000 millones anuales hacia el año fiscal 2029 y una guía de crecimiento de doble dígito del EPS
        ajustado sin la semana 53; a la vez, <strong>deja de publicar la utilidad operativa del streaming</strong> desde el
        año fiscal 2027. A {PR} la acción cotiza a ~{es(g['pe_ntm'],1)}x la utilidad ajustada de consenso del año fiscal 2027
        (US${es(g['c27'])}) y ~{es(g['pe_c28'],1)}x la de 2028. Este informe recorre el negocio completo y cierra, en la Sección 13,
        con cinco metodologías de valuación ponderadas con la regla de la casa: el blend da <strong>{BL}</strong>, {pct(g['blend_gap'])}
        contra el precio.
      </div>
    </div>
    <div class="statsrow">
      <div class="statcell"><div class="k">Ingresos FY2026 (53 sem.)</div><div class="v">$102,34B</div></div>
      <div class="statcell"><div class="k">Var. ingresos (4T)</div><div class="v pos">{pct(g['q4_rev_g'],0)}</div></div>
      <div class="statcell"><div class="k">Margen op. de segmentos FY2026</div><div class="v">{es(g['fy_seg_m'],1)}%</div></div>
      <div class="statcell"><div class="k">Deuda neta</div><div class="v neg">&minus;${es(g['nd'],1)}B</div></div>
    </div>
  </div>
  """)
between('<p class="footnote">Cifras fundamentales', '<div class="toc">', f"""<p class="footnote">Cifras fundamentales: SEC EDGAR (8-K del 17-nov-2026 con la carta a accionistas del 4T fiscal 2026; 10-K del año fiscal 2026 presentado el mismo día; 8-K ítem 7.01 del 17-nov-2026 con el cambio de reporte por segmento; 10-Q del 1T al 3T fiscal 2026). Disney tiene año fiscal cerrado a fines de septiembre o principios de octubre; el año fiscal 2026 tuvo 53 semanas (la semana extra cayó en el 4T, de julio a principios de octubre de 2026). Precio de mercado: Yahoo Finance, cierre del viernes 20 de noviembre de 2026 ({PR}). Rango de 52 semanas: US$92,19 &ndash; US$123,37. Edición anterior: datos al 3T fiscal 2026 y precio del 8 de septiembre de 2026 (US$104,16). Este documento es 100% analítico — no constituye una recomendación de compra, venta ni mantenimiento. Ver disclosure completo al pie.</p>

  """)

# ---------------- 01 ----------------
between('<!-- 01 -->', '<!-- 02 -->', f"""<!-- 01 -->
  <p class="secnum" id="s01">01 — Resumen Ejecutivo</p>
  <h2>Un año récord con una semana de regalo, más caja para el accionista y menos datos sobre el streaming</h2>
  <p>
    Disney reportó el 17 de noviembre de 2026 su cuarto trimestre fiscal y el año fiscal 2026 completo (cerrado el 3 de
    octubre de 2026). El año tuvo 53 semanas, y la semana extra cayó en el cuarto trimestre: sumó ~US$1.600 millones de
    ingresos, ~US$490 millones de utilidad operativa de segmentos y ~US$0,17 de utilidad por acción ajustada. Con todo,
    los ingresos fueron de US$102.344 millones ({pct(g['fy_rev_g'])}), la utilidad operativa de segmentos de US$19.728 millones
    ({pct(g['fy_segoi_g'])}; ~+10% sin la semana 53) y la utilidad diluida ajustada de US$7,02 ({pct(g['fy_eps_g'])}). Sin la semana extra
    el EPS ajustado fue de US$6,85, +{es(g['fy_eps_g_ex53'],1)}%, por encima de la guía de "~12%" que la compañía repitió todo el año. La
    utilidad GAAP por acción cayó a US$5,63 desde US$6,85 porque el año fiscal 2025 había tenido un beneficio impositivo de
    US$3.277 millones por la reclasificación de Hulu y el 2026 cargó deterioros de A+E (US$1.012 millones) y cargos
    impositivos no-caja por las operaciones de Fubo y la NFL (US$422 millones).
  </p>
  <p>
    El cuarto trimestre confirmó las tres inflexiones que el informe de septiembre describía. <strong>El streaming</strong>
    (Disney+/Hulu SVOD) ganó US$824 millones en el trimestre (US$160 millones de la semana extra) y US$2.568 millones en el
    año, un margen de 11,5% (US$1.302 millones en el año fiscal 2025). <strong>Experiences</strong> tuvo récord de ingresos (US$10.105
    millones, +15%; ~+8% sin la semana extra) y de utilidad operativa (US$2.250 millones, +20%), con huéspedes globales
    +4% sin la semana 53 y la asistencia a los parques de EE.UU. +3%, todavía con menos visitantes internacionales.
    <strong>ESPN</strong> sumó US$1.393 millones de utilidad operativa (+53%, con la semana 53 y la NFL Network), en un
    trimestre de récords de audiencia del fútbol americano.
  </p>
  <p>
    Lo nuevo para el accionista: un <strong>dividendo de US$2,00 para el año fiscal 2027</strong> (+33% sobre los US$1,50 de
    2026), en dos cuotas de US$1,00 (enero y julio de 2027); recompras de ~US$9.000 millones (las mismas que en 2026); un
    programa de eficiencia que ahora apunta a ~US$3.000 millones de ahorro anual de gastos operativos hacia el año fiscal
    2029; y la venta del 50% de A+E a Hearst por ~US$1.300 millones, cerrada el 30 de septiembre. La guía del año fiscal
    2027 promete crecimiento de doble dígito del EPS ajustado sin la semana 53, ~8% de utilidad operativa de segmentos,
    ~US$11.000 millones de flujo de caja libre (con capex de ~US$9.000 millones y gasto de contenido de ~US$26.000 millones,
    +9%), y concentra el crecimiento en el primer semestre. La contracara: <strong>Disney deja de publicar la utilidad
    operativa del streaming</strong> desde el primer trimestre fiscal 2027 —justo cuando el dato se volvió bueno— y pasa
    Consumer Products de Experiences a Entertainment, lo que cambia la lectura de los dos segmentos.
  </p>
  <p>
    La tensión de la tesis sigue estando en el precio. A {PR} —13% por encima del precio de la edición anterior y cerca
    del máximo de 52 semanas (US$123,37)— la acción cotiza a ~{es(g['pe_ntm'],1)}x la utilidad ajustada de consenso del año fiscal
    2027 (US${es(g['c27'])}) y ~{es(g['pe_c28'],1)}x la de 2028 (US${es(g['c28'])}). La Sección 13 confronta ese precio con cinco metodologías
    —DCF en tres escenarios, suma de partes por segmento, comparables, reversión histórica en ventana limpia y consenso de
    Wall Street— que, ponderadas con la regla de la casa (en septiembre el informe todavía usaba un promedio simple), dan
    <strong>{BL} por acción</strong>, {pct(g['blend_gap'])} contra el precio: el negocio mejoró, pero el precio subió más que el valor.
  </p>

  """)

# ---------------- 02 (solo el dato del recuadro y el gráfico) ----------------
rep("""El dato que mejor resume la última fase de la transición no es el precio de la acción —que a fines de fiscal 2025
    cerró cerca de US$99,50, casi plano respecto de un año antes— sino la rentabilidad del streaming.""",
    """El dato que mejor resume la última fase de la transición no es el precio de la acción —que a fines del año fiscal 2025
    cerró en US$113,47 y un año después, a fines del año fiscal 2026, en US$102,19— sino la rentabilidad del streaming.""")
rep("""alcanzó un margen operativo de 12,9% en el tercer trimestre fiscal 2026. Después de acumular más de US$11.000
    millones de pérdidas operativas de streaming entre 2020 y 2023, la parte del negocio que iba a "matar" a la
    televisión de cable finalmente aporta caja.""",
    """ganó US$2.568 millones en el año fiscal 2026 (11,5% de margen, contra US$1.302 millones en 2025). Después de acumular
    más de US$11.000 millones de pérdidas operativas de streaming entre 2020 y 2023, la parte del negocio que iba a
    "matar" a la televisión de cable finalmente aporta caja; desde el año fiscal 2027 Disney deja de publicar ese dato.""")
rep('<p class="chartcap">Ingresos anuales reportados, FY2019&ndash;FY2025, y TTM al cierre del 3T fiscal 2026. Fuente: SEC EDGAR (10-K/10-Q), concepto XBRL Revenues.</p>',
    '<p class="chartcap">Ingresos anuales reportados, FY2019&ndash;FY2026 (el FY2026 tuvo 53 semanas: ~US$1.600 millones de la semana extra). Fuente: SEC EDGAR (10-K), concepto XBRL Revenues.</p>')
rep("""de un objetivo de US$3.000 millones en fiscal 2025 a "al menos US$9.000 millones" en fiscal 2026.""",
    """de US$3.500 millones en fiscal 2025 a US$9.000 millones en fiscal 2026, y ~US$9.000 millones guiados para 2027.""")

# ---------------- 03 ----------------
seg = g['seg']
between('    Desde el año fiscal 2024, Disney reporta tres segmentos operativos.', '<!-- 04 -->', f"""    Desde el año fiscal 2024, Disney reporta tres segmentos operativos. <strong>Entertainment</strong> agrupa los
    estudios de cine y televisión, las redes lineales de entretenimiento (ABC, cable de entretenimiento), los servicios
    de TV en vivo por internet (Hulu Live TV y Fubo) y el streaming Disney+/Hulu. <strong>Sports</strong> es esencialmente
    ESPN: redes lineales de deportes, el servicio directo-al-consumidor de ESPN, la NFL Network (desde enero de 2026) y las
    señales internacionales. <strong>Experiences</strong> reúne parques temáticos y resorts (domésticos e internacionales),
    Disney Cruise Line y, hasta el año fiscal 2026, el negocio de licencias y productos de consumo. <strong>Desde el primer
    trimestre fiscal 2027</strong> las licencias de mercadería y la editorial pasan a Entertainment (solo la venta directa
    de mercadería queda en Experiences) y Entertainment deja de incluir la participación en ganancias de asociadas.
  </p>
  <div class="table-scroll"><table>
    <tr><th>Segmento (año fiscal 2026, 53 semanas)</th><th class="right-al">Ingresos</th><th class="right-al">% del total</th><th class="right-al">Utilidad op. de segmento</th><th class="right-al">Margen op.</th></tr>
    <tr><td class="label">Experiences (parques, cruceros, productos)</td><td class="right-al">$39.566M</td><td class="right-al">{es(g['seg_exp_share_rev'],1)}%</td><td class="right-al">$11.191M</td><td class="right-al">{es(seg['exp']['m'],1)}%</td></tr>
    <tr><td class="label">Entertainment (estudios, lineal, Disney+/Hulu)</td><td class="right-al">$46.562M</td><td class="right-al">{es(g['seg_ent_share_rev'],1)}%</td><td class="right-al">$5.443M</td><td class="right-al">{es(seg['ent']['m'],1)}%</td></tr>
    <tr><td class="label">Sports (ESPN, lineal + directo-al-consumidor)</td><td class="right-al">$18.632M</td><td class="right-al">{es(g['seg_spo_share_rev'],1)}%</td><td class="right-al">$3.094M</td><td class="right-al">{es(seg['spo']['m'],1)}%</td></tr>
    <tr class="total"><td class="label">Total segmentos (antes de eliminaciones y corporativo)</td><td class="right-al">${es(g['seg_rev_tot']*1000,0)}M</td><td class="right-al">100%</td><td class="right-al">$19.728M</td><td class="right-al">{es(g['seg_oi_tot']/g['seg_rev_tot']*100,1)}%</td></tr>
  </table></div>
  <p class="footnote">Año fiscal 2026 tal como se reportó (53 semanas; la semana extra sumó US$580 / US$810 / US$290 millones de ingresos y US$180 / US$230 / US$80 millones de utilidad a Experiences / Entertainment / Sports). Los ingresos totales de la compañía (US$102.344 millones) son menores a la suma de segmentos por eliminaciones intersegmento de US$2.416 millones; los gastos corporativos y no asignados (US$1.461 millones), la amortización de intangibles de adquisiciones (US$1.284 millones), la pérdida de la asociación en India (US$158 millones), los cargos de reestructuración y deterioro (US$1.456 millones) y los intereses se restan por debajo de la utilidad operativa de segmentos. <strong>Con el reporte nuevo</strong> (8-K del 17-nov-2026), el año fiscal 2026 recalculado queda: Experiences US$35.855 millones de ingresos y US$8.859 millones de utilidad; Entertainment US$50.273 millones y US$7.367 millones (suma US$2.332 millones de Consumer Products y resta US$408 millones de participación en ganancias); Sports sin cambios. Fuente: 10-K y comunicados de Disney.</p>
  <div class="chartbox">
    <canvas id="segmentChart" height="240"></canvas>
    <p class="chartcap">Utilidad operativa de segmento, año fiscal 2026 tal como se reportó. Experiences aporta {es(g['seg_exp_share_oi'],0)}% de la utilidad operativa de segmentos con {es(g['seg_exp_share_rev'],0)}% de los ingresos; con el reporte nuevo (Consumer Products en Entertainment) aportaría 45%.</p>
  </div>
  <p>
    El corte por segmento explica por qué un flujo de caja descontado consolidado es un instrumento romo para valuar a
    Disney: mezcla, en un mismo flujo, un negocio de parques de ~28% de margen operativo, un negocio de entretenimiento de
    ~12% de margen que combina streaming en expansión con redes lineales en declive, y un ESPN de ~17% de margen en plena
    transición de lo lineal a lo digital. Por eso la Sección 13 incorpora, además del DCF, una suma de partes por segmento.
    El cambio de reporte del año fiscal 2027 mueve US$2.332 millones de utilidad de licencias (un negocio de margen muy
    alto) de Experiences a Entertainment: Experiences queda como un negocio puro de parques, cruceros y venta directa, con
    margen de ~25%, y Entertainment sube a ~15%. Nada cambia en la utilidad total; cambia qué segmento "se ve" mejor. Para
    comparar con septiembre, este informe sigue usando la apertura vieja en la suma de partes y muestra el resultado con
    la nueva (Sección 13).
  </p>

  """)

# ---------------- 04 ----------------
between('<!-- 04 -->', '<!-- 05 -->', f"""<!-- 04 -->
  <p class="secnum" id="s04">04 — Desarrollos Recientes y Perspectiva</p>
  <h2>Cinco frentes que definen la lectura del mercado sobre Disney al cierre del año fiscal 2026</h2>
  <h3>Capital al accionista: dividendo +33%, recompras de US$9.000 millones y un plan de ahorro de US$3.000 millones</h3>
  <p>
    El directorio declaró un dividendo de US$2,00 por acción para el año fiscal 2027, en dos cuotas de US$1,00 (22 de enero
    de 2027, registro el 16 de diciembre de 2026; y 13 de julio de 2027), contra US$1,50 en 2026. En 2026 Disney recompró
    US$9.000 millones de acciones (US$1.800 millones en el cuarto trimestre) y devolvió US$11.600 millones en total; para
    2027 apunta a otros ~US$9.000 millones. El programa de eficiencia que en agosto estaba "a mitad de camino" ahora tiene
    número: ~US$3.000 millones de ahorro anual de gastos operativos hacia el año fiscal 2029, que se usarán "principalmente
    para financiar crecimiento", con una parte que debería llegar a la utilidad con el tiempo.
  </p>
  <h3>Streaming: margen de 11,5% en el año, y el fin del dato separado</h3>
  <p>
    El streaming de entretenimiento (Disney+/Hulu SVOD) facturó US$6.050 millones en el cuarto trimestre (+19%; ~9 puntos de
    la semana 53), con ingresos por suscripción +22% —10 puntos por más suscriptores, 9 por la semana extra y 2 por precio—
    y publicidad +6% (con tarifas 6% más bajas, la misma debilidad que la compañía había advertido en agosto). La utilidad
    fue de US$824 millones (13,6% de margen; US$160 millones de la semana extra) y la del año, US$2.568 millones (11,5%). Desde
    el primer trimestre fiscal 2027 <strong>Disney deja de publicar la utilidad del streaming</strong>: dice que ya no
    refleja cómo gestiona Entertainment, que pasará a mostrar ingresos por SVOD, contenido y propiedad intelectual, y redes
    lineales y TV en vivo. Para el inversor es menos visibilidad sobre la variable que más movió la acción en dos años, y
    la compañía anticipa más gasto de contenido y marketing en 2027. En diciembre termina la unificación de Disney+ y Hulu
    en una sola aplicación y empieza el contenido de creadores vía un acuerdo con TikTok.
  </p>
  <h3>ESPN: récords de audiencia, NFL Network adentro y el primer Super Bowl en 2027</h3>
  <p>
    La utilidad de Sports creció 53% en el cuarto trimestre (US$1.393 millones) y 7% en el año (US$3.094 millones), con la
    semana 53 y la operación con la NFL (que le dio a la liga 10% de ESPN a cambio de NFL Network, RedZone y NFL Fantasy)
    sumando 11 puntos al crecimiento de los ingresos del trimestre. Monday Night Football tuvo sus mejores semanas 1 y 2 de
    la historia, ESPN extendió la exclusividad del College Football Playoff ampliado a 24 equipos y transmitirá el Super
    Bowl LXI en febrero de 2027. Para 2027 la guía es de crecimiento de "un dígito alto" reportado (doble dígito sin la
    semana 53), con caída en el primer trimestre por el calendario de los partidos del playoff universitario.
  </p>
  <h3>Experiences y el consumidor de EE.UU.</h3>
  <p>
    Experiences cerró el año con US$11.191 millones de utilidad (+12%; +10% sin la semana extra) y un cuarto trimestre récord:
    los parques de EE.UU. crecieron 19% en ingresos y 36% en utilidad (15 puntos de la semana 53), con asistencia +3% sin la
    semana extra y gasto por visitante +4%; los internacionales cedieron utilidad (−7%) porque Hong Kong y Shanghái
    empeoraron, algo que la compañía espera que siga en 2027, mientras Disneyland Paris crece con World of Frozen. Los
    cruceros (Disney Destiny y Disney Adventure) sumaron 11 puntos al crecimiento de resorts y vacaciones. Para 2027 la guía
    de Experiences es "un dígito alto" sin la semana 53, con crecimiento en el primer semestre y utilidad plana en el segundo
    (se comparan los lanzamientos de cruceros, World of Frozen y el reintegro de aranceles del 3T fiscal 2026).
  </p>
  <p>
    <strong>El consumidor de EE.UU. al cierre de este informe</strong> (bloque compartido con el informe de Walmart): las
    ventas minoristas de octubre subieron 0,2% contra septiembre y 6,8% interanual (Census, 17 de noviembre), con las ventas
    "de control" en +0,6%; la confianza de la Universidad de Michigan subió a 51,0 en la lectura preliminar de noviembre
    (48,0 en octubre), un nivel históricamente bajo, con expectativas de inflación a un año de 4,3%; el IPC de octubre subió
    0,4% mensual; el diésel promedió US$5,94 el galón en la semana al 16 de noviembre, US$2,07 más que un año antes; la NRF
    espera ventas navideñas de +4,2%, mitad volumen y mitad precio; y en aranceles los de la ley IEEPA se devuelven desde
    abril, mientras siguen vigentes los de las Secciones 232 y 301. Disney describe el entorno macro de 2026 como
    "desafiante" y su guía de 2027 asume que no se deteriora; Walmart, que lo mide en el changuito, dice que gana
    participación en todos los niveles de ingreso, liderada por los hogares de ingresos altos —el mismo cliente que
    sostiene el gasto por visitante en los parques—.
  </p>
  <h3>Portafolio, liderazgo y taquilla</h3>
  <p>
    El 30 de septiembre de 2026 Disney cerró la venta de su 50% de A+E Global Media a Hearst por ~US$1.300 millones (A+E
    aportaba ~US$390 millones de participación en ganancias por año). En septiembre nombró a Karandeep Anand como primer
    director de tecnología del grupo y a Adam Smith como presidente de Direct-to-Consumer de Disney Entertainment. Bob Iger
    se retira el 31 de diciembre de 2026. En taquilla, <em>Toy Story 5</em> sostuvo el trimestre y el reestreno de
    <em>Avengers: Endgame</em> anticipó <em>Avengers: Doomsday</em> (18 de diciembre de 2026), el estreno más importante del
    año fiscal 2027; <em>Frozen 3</em> y <em>Lilo &amp; Stitch 2</em> llegan en 2028.
  </p>

  """)

# ---------------- 05 ----------------
q3, q4, fy = g['q3'], g['q4'], g['fy']
between('<!-- 05 -->', '<!-- 06 -->', f"""<!-- 05 -->
  <p class="secnum" id="s05">05 — Estados Financieros</p>
  <h2>Los últimos dos trimestres y el año fiscal 2026, línea por línea</h2>
  <p>
    El tercer trimestre fiscal (abril a junio) fue el de mayor margen del año; el cuarto (julio a principios de octubre)
    creció mucho más en ingresos (+{es(g['q4_rev_g'],1)}%) y en utilidad de segmentos (+{es(g['q4_segoi_g'],1)}%) porque tuvo catorce semanas
    contra trece y se comparaba contra un cuarto trimestre de 2025 débil (US$3.480 millones de utilidad de segmentos). Sin la
    semana extra, la utilidad de segmentos del cuarto trimestre fue de US$4.480 millones (+29%). La utilidad neta y la
    utilidad por acción GAAP de Disney siguen siendo difíciles de leer por las partidas no recurrentes —beneficios
    impositivos por Hulu en 2025, deterioros de A+E, cargos no-caja por Fubo y la NFL, amortización de intangibles de la
    compra de Fox—, por eso este informe, igual que la compañía y el consenso, trabaja con la <strong>utilidad diluida por
    acción ajustada</strong>.
  </p>
  <div class="table-scroll"><table>
    <tr><th>Métrica</th><th class="right-al">3T fiscal 2026 (jun-26)</th><th class="right-al">4T fiscal 2026 (oct-26, 14 sem.)</th><th class="right-al">Año fiscal 2026 (53 sem.)</th></tr>
    <tr><td class="label">Ingresos totales</td><td class="right-al">$25,25B</td><td class="right-al">$25,95B</td><td class="right-al">$102,34B</td></tr>
    <tr><td class="label">Var. interanual</td><td class="right-al pos">+6,8%</td><td class="right-al pos">{pct(g['q4_rev_g'])}</td><td class="right-al pos">{pct(g['fy_rev_g'])}</td></tr>
    <tr><td class="label">Utilidad operativa de segmentos</td><td class="right-al">$5,56B</td><td class="right-al">$4,97B</td><td class="right-al">$19,73B</td></tr>
    <tr><td class="label">Margen operativo de segmentos</td><td class="right-al">{es(g['q3_seg_m'],1)}%</td><td class="right-al">{es(g['q4_seg_m'],1)}%</td><td class="right-al">{es(g['fy_seg_m'],1)}%</td></tr>
    <tr><td class="label">Utilidad antes de impuestos</td><td class="right-al">$3,65B</td><td class="right-al">$3,51B</td><td class="right-al">$14,21B</td></tr>
    <tr><td class="label">Utilidad neta atribuible a Disney</td><td class="right-al">$2,64B</td><td class="right-al">$2,61B</td><td class="right-al">$9,90B</td></tr>
    <tr><td class="label">EPS diluido GAAP</td><td class="right-al">$1,51</td><td class="right-al">$1,51</td><td class="right-al">$5,63<sup>1</sup></td></tr>
    <tr><td class="label">EPS diluido ajustado</td><td class="right-al">$2,06</td><td class="right-al">$1,77</td><td class="right-al">$7,02</td></tr>
    <tr><td class="label">EPS ajustado sin la semana 53</td><td class="right-al">&mdash;</td><td class="right-al">$1,59</td><td class="right-al">$6,85</td></tr>
    <tr><td class="label">Acciones diluidas (millones)</td><td class="right-al">1.743</td><td class="right-al">1.731</td><td class="right-al">1.759</td></tr>
  </table></div>
  <p class="footnote">Fuente: 8-K y 10-K del 17-nov-2026, 10-Q del 3T fiscal 2026 y comunicados de Disney. EPS ajustado por trimestre del año fiscal 2026: US$1,63 / US$1,57 / US$2,06 / US$1,77 (la edición de septiembre mostraba el del 2T en US$1,86 "por diferencia": era un error de cálculo, porque nueve meses de US$5,25 menos US$1,63 y US$2,06 dan US$1,56; el comunicado del 6-may-2026 informó US$1,57). <sup>1</sup>El EPS GAAP del año excluye de la utilidad ajustada: reestructuración y deterioros (US$0,65, incluido el deterioro de A+E de US$1.012 millones), amortización de intangibles de adquisiciones (US$0,50) y cargos impositivos no-caja por Fubo y la NFL (US$0,23). En el año fiscal 2025 el EPS GAAP (US$6,85) incluía un beneficio de US$1,55 por Hulu y US$0,56 por la resolución de un asunto impositivo.</p>
  <p>
    Dos lecturas. Primero, la calidad del crecimiento: sin la semana extra la utilidad de segmentos creció ~10% en el año
    con ingresos que crecieron ~6%, y el apalancamiento vino del streaming (US$1.266 millones más de utilidad) y de
    Experiences; las redes lineales siguieron en declive. Segundo, la guía de 2027: ~8% de crecimiento de la utilidad de
    segmentos sin la semana 53 y con el reporte nuevo (sin la participación en ganancias de A+E), con la mayor parte del
    crecimiento en el primer semestre —el primer trimestre fiscal 2027 debería dar ~US$5.400 millones— y un cuarto
    trimestre que compara contra la semana extra.
  </p>
  <div class="chartbox">
    <canvas id="marginChart" height="260"></canvas>
    <p class="chartcap">Margen operativo de segmentos por trimestre fiscal, últimos 8 trimestres (1T fiscal 2025&ndash;4T fiscal 2026; el 4T fiscal 2026 tuvo 14 semanas). El primer trimestre fiscal (calendario oct&ndash;dic) es estacionalmente fuerte por la temporada de fiestas en parques; el cuarto (jul&ndash;sep) el más débil. Fuente: comunicados de Disney y SEC EDGAR.</p>
  </div>

  """)

# ---------------- 06 ----------------
between('<!-- 06 -->', '<!-- 07 -->', f"""<!-- 06 -->
  <p class="secnum" id="s06">06 — Deuda y Balance</p>
  <h2>Deuda neta de ~US${es(g['nd']*1000,0)} millones, US$3.000 millones menos que en junio</h2>
  <div class="table-scroll"><table>
    <tr><th>Métrica (al 3 oct 2026)</th><th class="right-al">Valor</th></tr>
    <tr><td class="label">Efectivo y equivalentes</td><td class="right-al">$6.679M</td></tr>
    <tr><td class="label">Deuda de corto plazo (porción corriente)</td><td class="right-al">$7.331M</td></tr>
    <tr><td class="label">Deuda de largo plazo</td><td class="right-al">$37.142M</td></tr>
    <tr><td class="label">Deuda bruta total</td><td class="right-al">${es(g['debt']*1000,0)}M</td></tr>
    <tr class="total"><td class="label">Deuda neta</td><td class="right-al neg">&minus;${es(g['nd']*1000,0)}M</td></tr>
    <tr><td class="label">Patrimonio neto atribuible a Disney</td><td class="right-al">$111.600M</td></tr>
    <tr><td class="label">Participaciones no controlantes (valor libro)</td><td class="right-al">$7.105M</td></tr>
    <tr><td class="label">Goodwill + intangibles netos</td><td class="right-al">${es(g['gw_int']*1000,0)}M</td></tr>
  </table></div>
  <p class="footnote">Fuente: balance del 8-K / 10-K del 17-nov-2026. El goodwill (US$74.700 millones) proviene mayormente de la adquisición de 21st Century Fox en 2019. Las participaciones no controlantes subieron de US$4.743 a US$7.105 millones en el año por el 10% de ESPN que recibió la NFL y el ~30% de Fubo que quedó en manos de terceros.</p>
  <p>
    Disney cerró el año fiscal con deuda neta de US${es(g['nd']*1000,0)} millones —deuda bruta de US${es(g['debt']*1000,0)} millones contra
    US$6.679 millones de caja, que incluye el cobro de A+E—. Sobre la utilidad operativa de segmentos del año (US$19.728 millones)
    son {es(g['nd_segoi'],1)}x; sobre una aproximación de EBITDA (utilidad de segmentos más depreciación y amortización, ~US$25.300
    millones), {es(g['nd_ebitda'],1)}x. El gasto neto de intereses fue de US$1.157 millones. No es un balance en estrés: Disney tiene
    grado de inversión y prioriza recompras por sobre el desendeudamiento. Pero la deuda <strong>sí importa para la
    valuación</strong>: como el equity es el residuo después de pagar a los acreedores, amplifica en términos porcentuales
    cualquier diferencia operativa razonable entre los escenarios del DCF. Por eso la dispersión entre el Bear
    ({usd(g['dcf_bear'])}) y el Bull ({usd(g['dcf_bull'])}) de la Sección 13 es mucho más amplia que la de una compañía con caja neta.
  </p>

  """)

# ---------------- 07 ----------------
between('<!-- 07 -->', '<!-- 08 -->', f"""<!-- 07 -->
  <p class="secnum" id="s07">07 — Flujo de Caja y Capital Allocation</p>
  <h2>US$10.572 millones de flujo libre en 2026 y una guía de ~US$11.000 millones para 2027</h2>
  <div class="table-scroll"><table>
    <tr><th>Métrica</th><th class="right-al">4T FY25</th><th class="right-al">1T FY26</th><th class="right-al">2T FY26</th><th class="right-al">3T FY26</th><th class="right-al">4T FY26</th></tr>
    <tr><td class="label">Flujo de caja operativo (OCF)</td><td class="right-al">$4,47B</td><td class="right-al">$0,74B</td><td class="right-al">$6,91B</td><td class="right-al">$4,87B</td><td class="right-al">$6,76B</td></tr>
    <tr><td class="label">Capex (parques, resorts, propiedad)</td><td class="right-al">$1,92B</td><td class="right-al">$3,01B</td><td class="right-al">$1,97B</td><td class="right-al">$1,79B</td><td class="right-al">$1,92B</td></tr>
    <tr><td class="label">Flujo de caja libre (FCF)</td><td class="right-al">$2,56B</td><td class="right-al neg">&minus;$2,28B</td><td class="right-al">$4,94B</td><td class="right-al">$3,07B</td><td class="right-al">$4,84B</td></tr>
  </table></div>
  <p class="footnote">FCF definido por la compañía como OCF menos inversiones en parques, resorts y otra propiedad (capex). Año fiscal 2026: OCF US$19.270 millones, capex US$8.698 millones, FCF US$10.572 millones (2025: US$18.101 / US$8.024 / US$10.077 millones). Fuente: comunicados de Disney (4T fiscal 2026 y anteriores). El 1T fiscal 2026 está deprimido por el pago, en octubre de 2025, de impuestos federales y de California de los ejercicios 2025 y parte de 2024 que se habían diferido por los incendios de California.</p>
  <div class="chartbox">
    <canvas id="fcfChart" height="260"></canvas>
    <p class="chartcap">Flujo de caja libre trimestral, últimos cinco trimestres fiscales. El 1T fiscal 2026 fue negativo por el pago diferido de impuestos y el pico de capex de cruceros; el 4T fiscal 2026 (14 semanas) fue el más fuerte.</p>
  </div>
  <p>
    El flujo libre del año fue de US$10.572 millones (+5%), con un flujo operativo de US$19.270 millones —en línea con la guía
    de "al menos US$19.000 millones" de agosto— a pesar del pago diferido de impuestos. Para 2027 la compañía guía ~US$20.000
    millones de flujo operativo y ~US$9.000 millones de capex: ~US$11.000 millones de flujo libre, con un gasto de contenido
    en efectivo de ~US$26.000 millones (+9%, por derechos deportivos, programación internacional y el calendario de
    producción de películas). La conversión del flujo libre sobre la utilidad ajustada fue de {es(g['fcf_conv'],0)}%.
  </p>
  <p>
    En retorno de capital, 2026 fue el año de la aceleración: US$9.000 millones de recompras (contra US$3.500 millones en
    2025) y US$2.634 millones de dividendos, US$11.600 millones en total, {es(g['payout_fcf'],0)}% del flujo libre del año (la
    diferencia salió de la venta de A+E y de deuda de corto plazo). Para 2027: dividendo de US$2,00 (+33%; rendimiento de
    {es(g['div_yield'],1)}% al precio de corte) y ~US$9.000 millones de recompras, otra vez por encima del flujo libre guiado si se suman
    los dos. Las acciones en circulación bajaron a 1.708 millones al 11 de noviembre de 2026, desde ~1.800 millones un año antes.
  </p>

  """)

# ---------------- 08 ----------------
pe = {k: v['pe'] for k, v in g['peers'].items()}
between('<!-- 08 -->', '<!-- 09 -->', f"""<!-- 08 -->
  <p class="secnum" id="s08">08 — Comparables de Industria</p>
  <h2>DIS frente a la plataforma de streaming pura, el conglomerado con parques y el especialista en vivo</h2>
  <p>
    Disney no tiene un comparable perfecto que cotice en bolsa —es simultáneamente el mayor operador de parques
    temáticos del mundo, un estudio de cine y televisión de primer nivel, el dueño de ESPN y una de las tres o cuatro
    plataformas de streaming de escala global—. El panel combina a <strong>Netflix</strong> (la plataforma de suscripción
    digital pura), <strong>Comcast</strong> (el comparable estructural más cercano: parques Universal, NBCUniversal, Peacock
    y banda ancha) y <strong>Fox Corp.</strong> (deportes y noticias en vivo). <strong>Warner Bros. Discovery</strong>, que en
    septiembre se excluía por la adquisición pendiente, dejó de cotizar: Paramount Skydance cerró la compra el 6 de octubre
    de 2026.
  </p>
  <div class="table-scroll"><table>
    <tr><th>Ticker</th><th class="right-al">P/E próximos 12 meses</th><th class="right-al">Precio</th><th class="right-al">Contexto</th></tr>
    <tr class="total"><td class="label">DIS</td><td class="right-al">{x(g['pe_ntm'])}</td><td class="right-al">{PR}</td><td class="right-al">Sobre EPS ajustado FY2027E US${es(g['c27'])}</td></tr>
    <tr><td class="label">NFLX</td><td class="right-al">{x(pe['NFLX'])}</td><td class="right-al">{usd(g['peers']['NFLX']['px'])}</td><td class="right-al">Streaming puro; prima del panel</td></tr>
    <tr><td class="label">FOXA</td><td class="right-al">{x(pe['FOXA'])}</td><td class="right-al">{usd(g['peers']['FOXA']['px'])}</td><td class="right-al">Deportes + noticias en vivo</td></tr>
    <tr><td class="label">CMCSA</td><td class="right-al">{x(pe['CMCSA'])}</td><td class="right-al">{usd(g['peers']['CMCSA']['px'])}</td><td class="right-al">Cable + parques + Peacock; piso del panel</td></tr>
  </table></div>
  <p class="footnote">P/E calculado por este informe (no el "forward P/E" de un proveedor): precio de cierre del 20-nov-2026 (Yahoo Finance) sobre el EPS ajustado de consenso de los próximos cuatro trimestres de S&amp;P Global (stockanalysis.com, 21-nov-2026) — dos trimestres de consenso más la parte del año fiscal que completa cuatro (Fox, que cierra su año en junio: los tres trimestres que faltan del año fiscal 2027, sin el 1T de US$2,54 de año electoral, más un cuarto del 2028). Disney tiene los cuatro trimestres del año fiscal 2027 por reportar: su EPS de los próximos 12 meses es el consenso del año (US${es(g['c27'])}). En septiembre el P/E de FOXA era una aproximación sin verificar; ahora está calculado. WBD ya no cotiza.</p>
  <div class="chartbox">
    <canvas id="compsChart" height="240"></canvas>
    <p class="chartcap">P/E sobre el EPS de consenso de los próximos 12 meses. Disney cotiza en un punto intermedio: con prima frente a Comcast y Fox, con descuento frente a Netflix.</p>
  </div>
  <h3>Netflix (NFLX) — la plataforma de streaming pura, sin activos físicos que diluyan el múltiplo</h3>
  <p>
    Netflix es el comparable de la parte del negocio de Disney que más está cambiando, pero también el menos parecido en
    estructura: no tiene parques, ni redes lineales, ni estudios con taquilla irregular, ni deuda apalancada relevante. Su
    acción cayó fuerte desde agosto (cerró a US$56,73 el 20 de noviembre, cerca de su mínimo de 52 semanas) y cotiza a
    {x(pe['NFLX'])}: el descuento de Disney contra Netflix se achicó de ~5 puntos de múltiplo en septiembre a menos de uno.
  </p>
  <h3>Comcast (CMCSA) — el espejo más cercano: parques, estudio, streaming y cable, todo junto</h3>
  <p>
    Comcast es el que más se parece a Disney en la mezcla de negocios: los parques Universal (competidor directo de
    Experiences, con Epic Universe abierto desde 2025), NBCUniversal, Peacock —muy por debajo de la escala de Disney+— y un
    negocio de banda ancha que pierde clientes. Cotiza al múltiplo más bajo del panel ({x(pe['CMCSA'])}), reflejo del declive del
    cable y de las dudas sobre Peacock. Aplicar su múltiplo a Disney da el piso del rango de comparables.
  </p>
  <h3>Fox Corp. (FOXA) — deportes y noticias en vivo, sin la carga del streaming de entretenimiento</h3>
  <p>
    Fox quedó con la parte de contenido "en vivo" que Disney no compró en 2019 —deportes (incluida una porción de la NFL) y
    noticias por cable—. Es un negocio generador de caja, sin la inversión en streaming de entretenimiento a escala, y su
    año fiscal 2027 incluye el beneficio publicitario de las elecciones de medio término de noviembre de 2026 (de ahí el
    US$2,54 de su primer trimestre). Cotiza a {x(pe['FOXA'])}.
  </p>
  <p class="pull">
    Disney cotiza entre el conglomerado de medios con parques (Comcast, {x(pe['CMCSA'])}) y la plataforma de suscripción pura
    (Netflix, {x(pe['NFLX'])}), ahora mucho más cerca de Netflix que en septiembre —porque Disney subió y Netflix cayó—. La
    dispersión de precios implícitos de este panel —de ~{usd(g['comp_low'],0)} con el múltiplo de Comcast a ~{usd(g['comp_high'],0)} con el de Netflix—
    sigue siendo la consecuencia de que Disney no tiene un comparable verdaderamente parecido cotizando en bolsa, y es la
    razón por la que la Sección 13 complementa los comparables con la suma de partes por segmento.
  </p>

  """)

# ---------------- 09 (ajustes) ----------------
rep('<div class="govcell"><div class="k">Bob Iger</div><div class="v">Asesor senior</div><div class="sub">Miembro del directorio y asesor senior hasta su retiro formal el 31-dic-2026. Compensación FY2025: US$45,8M (+11,5%).</div></div>',
    '<div class="govcell"><div class="k">Bob Iger</div><div class="v">Asesor senior</div><div class="sub">Miembro del directorio y asesor senior hasta su retiro formal el 31-dic-2026. Compensación FY2025: US$45,8M (+11,5%).</div></div>')
rep("""viajes). El paquete de compensación de D'Amaro como CEO se detallará en el próximo proxy.""",
    """viajes). El paquete de compensación de D'Amaro como CEO se detallará en el proxy de 2027. En septiembre de 2026 el
    equipo sumó a Karandeep Anand como primer director de tecnología del grupo y a Adam Smith al frente del streaming
    de Disney Entertainment, y la carta del 4T fiscal 2026 ya la firman D'Amaro y el CFO Hugh Johnston.""")

# ---------------- 10 ----------------
between('    <tr><td class="label">Retornos del ciclo de capex de Experiences</td>', '  </table></div>\n\n  <!-- 11 -->', f"""    <tr><td class="label">Retornos del ciclo de capex de Experiences</td><td class="label">Capex de US$8.698 millones en 2026 y ~US$9.000 millones guiados para 2027, dentro de un plan de ~US$60.000 millones para Experiences. La tesis Base asume que esos proyectos generan los retornos de doble dígito que promete management; si decepcionan (consumidor más débil, sobrecosto de cruceros, Asia), el flujo libre no crece al ritmo esperado.</td><td class="right-al">Alta</td></tr>
    <tr><td class="label">Menos visibilidad del streaming</td><td class="label">Desde el año fiscal 2027 Disney deja de publicar la utilidad del streaming (US$2.568 millones y 11,5% de margen en 2026) y anticipa más gasto de contenido y marketing. Si el margen se estanca, el mercado no lo va a ver directo sino en la utilidad de Entertainment, mezclado con las redes lineales en declive.</td><td class="right-al">Media-Alta</td></tr>
    <tr><td class="label">Declive estructural de las redes lineales</td><td class="label">Las redes lineales de entretenimiento siguen en declive secular; ESPN transita de lo lineal a lo directo-al-consumidor con riesgo de canibalizar su base de afiliados de cable, todavía la más rentable. Con el reporte nuevo, las redes lineales y la TV en vivo (Hulu Live, Fubo) se muestran juntas.</td><td class="right-al">Alta</td></tr>
    <tr><td class="label">Consumidor de EE.UU. y parques</td><td class="label">Confianza de la U. Michigan en 51,0 (nov-2026, preliminar), IPC firme y diésel a US$5,94 el galón: la asistencia a los parques de EE.UU. creció 3% sin la semana extra y todavía con menos visitantes internacionales; Hong Kong y Shanghái empeoraron y la compañía espera que siga en 2027. La guía de 2027 asume que el entorno macro no se deteriora.</td><td class="right-al">Media</td></tr>
    <tr><td class="label">Apalancamiento del balance</td><td class="label">Deuda neta de ~US${es(g['nd']*1000,0)} millones ({es(g['nd_segoi'],1)}x la utilidad operativa de segmentos). No es un riesgo de crédito, pero amplifica la dispersión entre Bear y Bull de la valuación; las recompras y el dividendo de 2027 suman más que el flujo libre guiado.</td><td class="right-al">Media</td></tr>
    <tr><td class="label">Inflación de costos de derechos deportivos</td><td class="label">Gasto de contenido de ~US$26.000 millones en 2027 (+9%), con más derechos deportivos (College Football Playoff ampliado, NFL, NBA). Si los derechos crecen más rápido que los ingresos por suscripción y afiliación, el margen de Sports se comprime.</td><td class="right-al">Media</td></tr>
    <tr><td class="label">Comparación contra la semana 53 y fases del año</td><td class="label">La semana extra sumó US$0,17 al EPS de 2026 y US$490 millones a la utilidad de segmentos; la guía de 2027 concentra el crecimiento en el primer semestre y prevé utilidad plana en Experiences y Sports en el segundo. Un primer semestre flojo dejaría poco margen para cumplir el "doble dígito".</td><td class="right-al">Media</td></tr>
    <tr><td class="label">Taquilla irregular de estudios</td><td class="label">El año fiscal 2027 depende en buena parte de <em>Avengers: Doomsday</em> (18-dic-2026). La parte de estudios del negocio sigue siendo volátil trimestre a trimestre.</td><td class="right-al">Media-Baja</td></tr>
    <tr><td class="label">Regulatorio y comercial (aranceles)</td><td class="label">El reintegro de aranceles de ~US$100 millones del 3T fiscal 2026 en Experiences no se repite en 2027 (la compañía lo menciona en la guía). Siguen vigentes los aranceles de las Secciones 232 y 301 sobre mercadería importada.</td><td class="right-al">Baja</td></tr>
""")

# ---------------- 11 ----------------
between('    <tr><td class="label">Otoño boreal 2026</td>', '  </table></div>\n\n  <!-- 12 -->', """    <tr><td class="label">Dic 2026</td><td class="label">Experiencia unificada de Disney+ y Hulu en una sola aplicación (con TV en vivo); llegada del contenido de creadores vía el acuerdo con TikTok.</td></tr>
    <tr><td class="label">18 dic 2026</td><td class="label">Estreno de <em>Avengers: Doomsday</em>, el título más importante del año fiscal 2027 para taquilla, Disney+ y productos de consumo.</td></tr>
    <tr><td class="label">31 dic 2026</td><td class="label">Retiro formal de Bob Iger. Josh D'Amaro queda plenamente al mando.</td></tr>
    <tr><td class="label">22 ene 2027</td><td class="label">Pago de la primera cuota de US$1,00 del dividendo de US$2,00 del año fiscal 2027 (registro el 16-dic-2026).</td></tr>
    <tr><td class="label">~Feb 2027</td><td class="label">Reporte del 1T fiscal 2027 —el primero con el reporte nuevo y sin la utilidad del streaming—; guía de ~US$5.400 millones de utilidad operativa de segmentos. Super Bowl LXI en ESPN/ABC el mismo mes.</td></tr>
    <tr><td class="label">2027</td><td class="label">Avance del plan de ahorro de ~US$3.000 millones anuales hacia el año fiscal 2029; botadura del crucero Disney Believe a fines de 2027.</td></tr>
    <tr><td class="label">En curso, sin fecha fija</td><td class="label">Consumidor de EE.UU. (temporada navideña, confianza, combustible) y demanda en los parques de Asia; ritmo de recompras (~US$9.000 millones guiados).</td></tr>
""")

# ---------------- 12 ----------------
between('<!-- 12 -->', '<!-- 13 -->', f"""<!-- 12 -->
  <p class="secnum" id="s12">12 — Modelo Financiero Proyectado y Momentum de Estimados</p>
  <h2>Qué espera el consenso: +{es(g['c27_g_ex53'],0)}% de utilidad ajustada en 2027 sin la semana extra y +{es(g['c28_g'],0)}% en 2028</h2>
  <p>
    El consenso de S&amp;P Global espera una utilidad ajustada por acción de US${es(g['c27'])} para el año fiscal 2027 ({pct(g['c27_g'])}
    contra los US$7,02 reportados; {pct(g['c27_g_ex53'])} contra los US$6,85 sin la semana 53, en línea con la guía de "doble dígito") y de
    US${es(g['c28'])} para 2028 ({pct(g['c28_g'])}), apoyado en el compounding de Experiences, el ahorro de costos y la caída del conteo de
    acciones por recompras.
  </p>
  <div class="table-scroll"><table>
    <tr><th>Métrica</th><th class="right-al">FY2026 (real, 53 sem.)</th><th class="right-al">FY2027E</th><th class="right-al">FY2028E</th></tr>
    <tr><td class="label">EPS diluido ajustado</td><td class="right-al">$7,02 ($6,85 sin la semana 53)</td><td class="right-al">${es(g['c27'])} (consenso)</td><td class="right-al">${es(g['c28'])} (consenso)</td></tr>
    <tr><td class="label">Var. YoY EPS ajustado</td><td class="right-al pos">{pct(g['fy_eps_g'])}</td><td class="right-al pos">{pct(g['c27_g'])}<sup>1</sup></td><td class="right-al pos">{pct(g['c28_g'])}</td></tr>
    <tr><td class="label">Próximos dos trimestres (consenso)</td><td class="right-al">&mdash;</td><td class="right-al">1T ${es(g['q_cons']['q1'])} · 2T ${es(g['q_cons']['q2'])}</td><td class="right-al">&mdash;</td></tr>
  </table></div>
  <p class="footnote">Fuente: S&amp;P Global vía stockanalysis.com (21-nov-2026; {g['c27_n']:.0f} analistas para el FY2027) y carta a accionistas del 4T fiscal 2026. <sup>1</sup>Contra el EPS reportado de 2026, que incluye ~US$0,17 de la semana 53; sin ella, {pct(g['c27_g_ex53'])}. La edición de septiembre tomaba el consenso de GuruFocus, Erste Group y stockanalysis; esta usa una sola fuente, la misma que el informe de Walmart.</p>
  <h3>La guía del año fiscal 2027</h3>
  <div class="table-scroll"><table>
    <tr><th>Métrica</th><th class="right-al">Guía de la compañía</th></tr>
    <tr><td class="label">EPS ajustado</td><td class="right-al">Doble dígito sin la semana 53</td></tr>
    <tr><td class="label">Utilidad operativa de segmentos (sin semana 53, reporte nuevo)</td><td class="right-al">~+8%</td></tr>
    <tr><td class="label">Experiences / Entertainment / Sports</td><td class="right-al">Un dígito alto / un dígito alto / doble dígito</td></tr>
    <tr><td class="label">1T fiscal 2027: utilidad operativa de segmentos</td><td class="right-al">~$5.400M</td></tr>
    <tr><td class="label">Flujo operativo / capex / flujo libre</td><td class="right-al">~$20.000M / ~$9.000M / ~$11.000M</td></tr>
    <tr><td class="label">Gasto de contenido en efectivo</td><td class="right-al">~$26.000M (+9%)</td></tr>
    <tr><td class="label">Recompras / dividendo</td><td class="right-al">~$9.000M / $2,00 por acción</td></tr>
    <tr><td class="label">Tasa impositiva / amortización de adquisiciones</td><td class="right-al">"Low 20s" / ~$1.200M</td></tr>
  </table></div>
  <p class="footnote">Fuente: carta a accionistas del 4T fiscal 2026 (17-nov-2026), páginas 11-12. La guía asume que el entorno macroeconómico global no se deteriora en forma material durante el año fiscal 2027. Sports reportado: un dígito alto.</p>
  <h3>Precio objetivo del consenso: {usd(g['cons'])}, {pct(g['cons_gap'])} sobre el mercado</h3>
  <p>
    El precio objetivo promedio de {g['cons_n']:.0f} analistas es de <strong>{usd(g['cons'])}</strong> (mediana {usd(g['cons_med'])}; rango
    {usd(g['cons_low'],0)}&ndash;{usd(g['cons_high'],0)}), {pct(g['cons_gap'])} sobre el precio de corte, con {g['cons_sb']:.0f} recomendaciones de compra fuerte, {g['cons_b']:.0f}
    de compra, {g['cons_h']:.0f} neutrales y {g['cons_ss']:.0f} de venta fuerte (S&amp;P Global, 19-nov-2026). En septiembre el promedio era de US$127,61 y quedaba
    22% arriba del precio: la acción se acercó al consenso. Igual que en la cobertura de Netflix, un consenso por encima del
    precio no es por sí mismo evidencia de que la acción esté barata.
  </p>
  <div class="chartbox">
    <canvas id="revisionChart" height="230"></canvas>
    <p class="chartcap">Utilidad diluida por acción ajustada: FY2024 a FY2026 reales (el FY2026 con la semana 53) y FY2027E y FY2028E de consenso.</p>
  </div>

  """)

# ---------------- 13 ----------------
sc = g['sc']; d = g['dcf_base_detail']; win = g['rev_window']
def drow(lbl, vals, total=False):
    return f'<tr{" class=\"total\"" if total else ""}><td class="label">{lbl}</td>' + ''.join(f'<td class="right-al">{v}</td>' for v in vals) + '</tr>'
grid_rows = '\n'.join(f'    <tr><td class="axis">{es(w,1)}%</td>' + ''.join(f'<td class="right-al{" base-cell" if (i == 2 and j == 2) else ""}">{usd(g["grid"][i][j])}</td>' for j in range(5)) + '</tr>' for i, w in enumerate(g['grid_w']))
between('<!-- 13 -->', '<!-- 14 -->', f"""<!-- 13 -->
  <p class="secnum" id="s13">13 — Valuación: Cinco Métodos y el Fair Value</p>
  <h2>Cuánto vale la acción, mirado desde cinco ángulos: el valor sube, el precio sube más</h2>
  <p>
    Calculamos el valor razonable con cinco enfoques —flujo de caja descontado (tres escenarios), suma de partes por
    segmento, múltiplos de comparables, reversión a la media histórica propia en ventana limpia y consenso de analistas— y
    los combinamos con los <strong>pesos de la casa</strong>: 15% intrínseco (repartido 7,5% en el DCF y 7,5% en la suma de
    partes), 25% comparables, 35% reversión y 25% consenso. La edición de septiembre promediaba los cinco en partes
    iguales (US$106,28); con la regla ponderada, esos mismos cinco valores habrían dado <strong>{usd(g['sep_blend_w'])}</strong>. La
    reversión y el consenso parten de cómo el mercado viene valuando a Disney y juntos pesan 60%; el DCF, la suma de partes
    y los comparables no usan el precio ni el múltiplo de Disney en ningún paso. La síntesis muestra el promedio de cada
    grupo.
  </p>

  <h3>Método 1 — Flujo de caja descontado (DCF), tres escenarios</h3>
  <p>
    El modelo es el mismo de septiembre —dos etapas, cinco años explícitos y valor terminal por crecimiento perpetuo, sobre
    el flujo operativo más intereses después de impuestos menos capex—, reconstruido con un script: con interpolación
    lineal entre el año 1 y el año 5 reproduce el Base publicado (US$102,32) y la grilla 5&times;5 con diferencias de hasta
    US$0,22. Ahora corre un año más adelante: el año 1 es el <strong>año fiscal 2027</strong>, anclado en la guía de la
    compañía (flujo operativo de ~US$20.000 millones y capex de ~US$9.000 millones; ya no hace falta normalizar el pago
    impositivo de los incendios), y el año 5 es el 2031, con el mismo crecimiento implícito del flujo operativo que cada
    escenario tenía en septiembre. Se suman los intereses netos del año fiscal 2026 después de impuestos (US$1.157 millones
    &times; 79% = US${es(g['intr']*1000,0)} millones; septiembre usaba ~US$717 millones), se restan la deuda neta (US${es(g['nd']*1000,0)} millones) y
    las participaciones no controlantes a valor libro (US$7.105 millones) y se divide por 1.708 millones de acciones (al
    11-nov-2026).
  </p>
  <p>
    El WACC del caso Base usa una tasa libre de riesgo de {es(g['rf'],3)}% (Treasury a 10 años, cierre del 20-nov-2026), el mismo
    beta de 1,30 de septiembre (stockanalysis reporta {es(g['beta_sa'],2)}: con ese beta el Base daría {usd(g['dcf_beta_sa'])}) y una prima de
    riesgo de 5,0%, la fija del marco (con la prima implícita de Damodaran al 1-nov-2026, {es(g['erp_dam'],2)}%, daría
    {usd(g['dcf_erp_dam'])}): costo de equity de {es(g['ke'],2)}%. Con un costo de deuda de {es(g['kd'],2)}% después de impuestos y una
    ponderación de mercado de {es(100-g['wd'],1)}% equity / {es(g['wd'],1)}% deuda, el <strong>WACC del Base es {es(g['wacc'],2)}%</strong>
    ({es(sc['bear']['w'],2)}% en el Bear, {es(sc['bull']['w'],2)}% en el Bull).
  </p>
  <div class="table-scroll"><table>
    <tr><th>Supuesto</th><th class="right-al">Bear</th><th class="right-al">Base</th><th class="right-al">Bull</th></tr>
    {drow('Flujo de caja operativo, FY2027 &rarr; FY2031', [f"${es(sc[k]['o1'],1)}B &rarr; ${es(sc[k]['o5'],1)}B" for k in ('bear','base','bull')])}
    {drow('Crecimiento anual implícito del OCF (el de septiembre)', [f"~{es(sc[k]['gr'],1)}%" for k in ('bear','base','bull')])}
    {drow('Capex, FY2027 &rarr; FY2031', [f"${es(sc[k]['c1'],1)}B &rarr; ${es(sc[k]['c5'],1)}B" for k in ('bear','base','bull')])}
    {drow('WACC', [f"{es(sc[k]['w'],2)}%" for k in ('bear','base','bull')])}
    {drow('Crecimiento terminal', [f"{es(sc[k]['g'],1)}%" for k in ('bear','base','bull')])}
    {drow('% del EV desde valor terminal', [f"{es(g['dcf_'+k+'_tv'],0)}%" for k in ('bear','base','bull')])}
    {drow('Fair value por acción', [usd(g['dcf_'+k]) for k in ('bear','base','bull')], total=True)}
    {drow('Septiembre (precio $104,16)', ['$50,25', '$102,32', '$167,93'])}
  </table></div>
  <p>
    El <strong>Bear</strong> asume que la mejora del streaming se estanca, que la debilidad del consumidor en parques se
    extiende y que el capex no baja de ~US$9.000 millones; el <strong>Base</strong>, que el flujo operativo crece ~{es(sc['base']['gr'],1)}% por
    año (streaming con más margen, compounding de Experiences, el ahorro de US$3.000 millones) y que el capex se normaliza
    hacia US$8.000 millones cuando terminan los cruceros; el <strong>Bull</strong>, una convergencia más rápida del streaming
    hacia los márgenes de Netflix y un capex que normaliza antes. El Base da <strong>{usd(g['dcf_base'])}</strong> ({pct(g['dcf_gap'])} contra
    el precio), con {es(g['dcf_base_tv'],0)}% del valor en la perpetuidad; el valor esperado ponderado (25/45/30) es {usd(g['dcf_pw'])}. El
    Base sube {usd(g['dcf_base']-102.32)} contra septiembre: el año 1 avanza al 2027 y la deuda neta bajó US$3.000 millones, mientras
    la tasa libre de riesgo y el flujo guiado (más bajo que el sendero de septiembre por el mayor gasto de contenido) restan.
    <strong>DCF inverso:</strong> con el resto del Base igual, el precio de {PR} exige un WACC de {es(g['impl_wacc'],2)}% o un flujo
    operativo que crezca {es(g['impl_o_cagr'],1)}% por año hasta US${es(g['impl_o5'],1)} mil millones en 2031.
  </p>
  <h3>Sensibilidad del caso Base: WACC &times; crecimiento terminal</h3>
  <p>
    Con {es(g['dcf_base_tv'],0)}% del valor de empresa en la perpetuidad, mostramos cómo se mueve el Base variando solo el WACC y el
    crecimiento terminal. La celda marcada es el caso Base ({usd(g['dcf_base'])}, WACC {es(g['wacc'],1)}%, g 3,0%).
  </p>
  <div class="table-scroll"><table class="sens-table">
    <tr><th>WACC \\ g terminal</th><th class="right-al">2,0%</th><th class="right-al">2,5%</th><th class="right-al">3,0%</th><th class="right-al">3,5%</th><th class="right-al">4,0%</th></tr>
{grid_rows}
  </table></div>
  <p class="footnote">Grilla propia: recalcula el DCF completo del caso Base (script en el repositorio del research desk) para cada combinación; la celda marcada reproduce el fair value del Método 1. La reconstrucción del DCF de septiembre usa interpolación lineal del flujo operativo y del capex entre el año 1 y el año 5 y despeja el interés después de impuestos (US$717 millones) para reproducir el Base publicado; con eso, la grilla publicada en septiembre se reproduce con diferencias de hasta US$0,22, el Bear con US$0,32 y el Bull con US$0,99 (el informe no publicaba los años intermedios).</p>

  <h3>Método 2 — Múltiplos de comparables (25%)</h3>
  <p>
    Aplicamos el P/E promedio de Netflix, Comcast y Fox —calculado con el precio de cada uno y el consenso de sus próximos
    cuatro trimestres, nunca con el múltiplo de Disney— a la utilidad ajustada de consenso de Disney para los próximos 12
    meses (el año fiscal 2027, US${es(g['c27'])}).
  </p>
  <div class="table-scroll"><table>
    <tr><th>Múltiplo P/E aplicado</th><th class="right-al">Precio implícito</th></tr>
    <tr><td class="label">{x(pe['CMCSA'])} (piso del panel, CMCSA)</td><td class="right-al">{usd(g['comp_low'])}</td></tr>
    <tr><td class="label">{x(pe['FOXA'])} (FOXA)</td><td class="right-al">{usd(pe['FOXA']*g['c27'])}</td></tr>
    <tr class="total"><td class="label">{x(g['peer_pe_avg'])} (promedio de CMCSA, FOXA, NFLX)</td><td class="right-al">{usd(g['comp'])}</td></tr>
    <tr><td class="label">{x(pe['NFLX'])} (techo del panel, NFLX)</td><td class="right-al">{usd(g['comp_high'])}</td></tr>
  </table></div>
  <p>
    Tomamos <strong>{usd(g['comp'])}</strong> (el promedio de los tres) como resultado, contra US$95,36 en septiembre: el EPS sube de
    los US$6,91 que el consenso esperaba para 2026 a US${es(g['c27'])} de 2027, pero el múltiplo promedio del panel baja de 13,8x a
    {x(g['peer_pe_avg'])} porque Netflix pasó de ~20x a {x(pe['NFLX'])}. Sin Netflix el método daría {usd(g['comp_xnflx'])}. La dispersión —de
    {usd(g['comp_low'],0)} a {usd(g['comp_high'],0)}— sigue siendo enorme: Disney no tiene un comparable de negocio parecido cotizando en bolsa.
  </p>

  <h3>Método 3 — Sum-of-the-parts por segmento (7,5%)</h3>
  <p>
    Como los tres segmentos tienen rentabilidades y perfiles de crecimiento muy distintos (Sección 03), valuamos cada uno
    con su propio múltiplo sobre la utilidad operativa del año fiscal 2026 —los mismos múltiplos de septiembre: Experiences
    14x (rango 12x&ndash;16x), Entertainment 11x (9x&ndash;13x), Sports 10x (8x&ndash;12x)— y restamos los gastos corporativos
    capitalizados a 10x. Dos ajustes para no inflar la base: se saca la semana 53 de cada segmento y, en Entertainment, la
    participación en ganancias de asociadas (US$408 millones, casi toda de A+E, que se vendió y cuya caja ya está en la
    deuda neta).
  </p>
  <div class="table-scroll"><table>
    <tr><th>Segmento</th><th class="right-al">Utilidad op. FY2026 ajustada</th><th class="right-al">Múltiplo</th><th class="right-al">Valor de empresa</th></tr>
    <tr><td class="label">Experiences</td><td class="right-al">${es(seg['exp']['adj']*1000,0)}M</td><td class="right-al">14x</td><td class="right-al">${es(g['sotp_exp_ev'],1)}B</td></tr>
    <tr><td class="label">Entertainment</td><td class="right-al">${es(seg['ent']['adj']*1000,0)}M</td><td class="right-al">11x</td><td class="right-al">${es(g['sotp_ent_ev'],1)}B</td></tr>
    <tr><td class="label">Sports</td><td class="right-al">${es(seg['spo']['adj']*1000,0)}M</td><td class="right-al">10x</td><td class="right-al">${es(g['sotp_spo_ev'],1)}B</td></tr>
    <tr><td class="label">Corporativo y no asignado</td><td class="right-al">&minus;$1.461M</td><td class="right-al">10x</td><td class="right-al">&minus;${es(-g['sotp_corp_ev'],1)}B</td></tr>
    <tr class="total"><td class="label">Valor de empresa (SOTP)</td><td class="right-al"></td><td class="right-al"></td><td class="right-al">${es(g['sotp_ev'],1)}B</td></tr>
    <tr><td class="label">&minus; Deuda neta</td><td class="right-al"></td><td class="right-al"></td><td class="right-al">&minus;${es(g['nd'],1)}B</td></tr>
    <tr><td class="label">&minus; Participaciones no controlantes (valor libro)</td><td class="right-al"></td><td class="right-al"></td><td class="right-al">&minus;${es(g['nci'],1)}B</td></tr>
    <tr class="total"><td class="label">Valor del equity &rarr; por acción (1.708M)</td><td class="right-al"></td><td class="right-al"></td><td class="right-al">${es(g['sotp_eq'],1)}B &rarr; {usd(g['sotp_base'])}</td></tr>
  </table></div>
  <p>
    El resultado es <strong>{usd(g['sotp_base'])} por acción</strong> (rango {usd(g['sotp_low'])} a {usd(g['sotp_high'])}), contra US$98,01 en septiembre:
    sube por la utilidad de un año completo y por la deuda neta más baja. Experiences explica {es(g['sotp_exp_share'],0)}% del valor de los
    segmentos. Con la apertura nueva (Consumer Products en Entertainment) y los mismos múltiplos daría {usd(g['sotp_recast'])}: mover
    US$2.332 millones de utilidad de licencias del múltiplo de 14x al de 11x baja el valor, no porque cambie el negocio sino
    porque cambia dónde se lo cuenta —por eso este informe mantiene la apertura vieja para comparar con septiembre—. Las
    participaciones no controlantes se restan a valor libro (US$7.105 millones): el 28% de ESPN en manos de Hearst y la NFL
    vale más que eso, así que restar el valor libro deja el método con un sesgo leve al alza (la edición de septiembre lo describía al revés).
  </p>

  <h3>Método 4 — Reversión a la media histórica propia (ventana limpia, 35%)</h3>
  <p>
    El historial largo de P/E de Disney sigue siendo inservible (promedios de 5 años de 50x&ndash;56x y de 10 años de
    32x&ndash;48x, contaminados por la pandemia y las pérdidas del streaming). En septiembre la ventana limpia se resolvió
    con un múltiplo aproximado de ~17x sobre cierres de trimestre estimados; esta edición la reconstruye con datos: el
    precio de cierre de cada uno de los últimos cuatro trimestres fiscales (Yahoo Finance) dividido por el EPS ajustado de
    los cuatro trimestres terminados en esa fecha (comunicados de Disney), sin la semana 53 en el último.
  </p>
  <div class="table-scroll"><table>
    <tr><th>Cierre de trimestre fiscal</th><th class="right-al">Precio</th><th class="right-al">EPS ajustado 12 meses</th><th class="right-al">P/E</th></tr>
""" + '\n'.join(f'    <tr><td class="label">{w["date"][8:10]}-{["","ene","feb","mar","abr","may","jun","jul","ago","sep","oct","nov","dic"][int(w["date"][5:7])]}-{w["date"][:4]}</td><td class="right-al">{usd(w["px"])}</td><td class="right-al">{usd(w["ttm"])}</td><td class="right-al">{x(w["pe"])}</td></tr>' for w in win) + f"""
    <tr class="total"><td class="label">Ventana limpia: promedio &rarr; sobre EPS ajustado de 12 meses sin la semana 53 (US$6,85)</td><td class="right-al"></td><td class="right-al"></td><td class="right-al">{x(g['pe_rev'])} &rarr; {usd(g['rev'])}</td></tr>
  </table></div>
  <p class="footnote">EPS ajustado por trimestre: FY2025 US$1,76 / US$1,45 / US$1,61 / US$1,11; FY2026 US$1,63 / US$1,57 / US$2,06 / US$1,77 (US$0,18 de la semana 53 en el 4T). Septiembre usaba "~US$99,50" como cierre del año fiscal 2025: el cierre real del 26-sep-2025 fue de US$113,47. Con el EPS reportado de 2026 (US$7,02, con la semana extra) la lectura daría {usd(g['rev_with53'])}; con el mismo múltiplo sobre el consenso de los próximos 12 meses, {usd(g['rev_ntm'])}.</p>
  <p>
    El resultado es <strong>{usd(g['rev'])}</strong> ({pct(g['rev_gap'])}), con un rango de {usd(g['rev_low'])} a {usd(g['rev_high'])} entre el cierre más barato y el más
    caro de la ventana. El múltiplo bajó de 19,6x a fines de 2025 a ~15x en 2026 aunque la utilidad creció: la acción se
    re-valuó hacia abajo mientras ejecutaba el plan, y recién en octubre y noviembre recuperó terreno.
  </p>

  <h3>Método 5 — Consenso de Wall Street (25%)</h3>
  <div class="table-scroll"><table>
    <tr><th>Métrica</th><th class="right-al">Valor</th></tr>
    <tr><td class="label">Analistas / calificación consenso</td><td class="right-al">{g['cons_n']:.0f} / Buy</td></tr>
    <tr class="total"><td class="label">Precio objetivo promedio (12 meses)</td><td class="right-al">{usd(g['cons'])}</td></tr>
    <tr><td class="label">Mediana / rango</td><td class="right-al">{usd(g['cons_med'])} / {usd(g['cons_low'])} &ndash; {usd(g['cons_high'])}</td></tr>
    <tr><td class="label">Upside implícito sobre el precio de mercado</td><td class="right-al pos">{pct(g['cons_gap'])}</td></tr>
  </table></div>
  <p class="footnote">Fuente: stockanalysis.com (S&amp;P Global), actualizado al 19-nov-2026, la misma fuente y el mismo día de consulta que el informe de Walmart. En septiembre: US$127,61 (barchart / GuruFocus / ChartMill).</p>

  <h3>Síntesis: el blend ponderado</h3>
  <div class="table-scroll"><table>
    <tr><th>Método</th><th>Tipo</th><th class="right-al">Fair value</th><th class="right-al">Peso</th><th class="right-al">Aporte</th></tr>
    <tr><td class="label">Método 1 — DCF Base</td><td class="label">Independiente del precio</td><td class="right-al">{usd(g['dcf_base'])}</td><td class="right-al">7,5%</td><td class="right-al">{usd(g['contrib_dcf'])}</td></tr>
    <tr><td class="label">Método 3 — Sum-of-the-parts por segmento</td><td class="label">Independiente del precio</td><td class="right-al">{usd(g['sotp_base'])}</td><td class="right-al">7,5%</td><td class="right-al">{usd(g['contrib_sotp'])}</td></tr>
    <tr><td class="label">Método 2 — Comparables (CMCSA/FOXA/NFLX)</td><td class="label">Independiente del precio</td><td class="right-al">{usd(g['comp'])}</td><td class="right-al">25%</td><td class="right-al">{usd(g['contrib_comp'])}</td></tr>
    <tr><td class="label">Método 4 — Reversión (ventana limpia)</td><td class="label">Anclado al mercado</td><td class="right-al">{usd(g['rev'])}</td><td class="right-al">35%</td><td class="right-al">{usd(g['contrib_rev'])}</td></tr>
    <tr><td class="label">Método 5 — Consenso Wall Street</td><td class="label">Anclado al mercado</td><td class="right-al">{usd(g['cons'])}</td><td class="right-al">25%</td><td class="right-al">{usd(g['contrib_cons'])}</td></tr>
    <tr><td class="label">Promedio ponderado de los independientes del precio (40% del peso)</td><td class="label"></td><td class="right-al">{usd(g['indep'])}</td><td class="right-al"></td><td class="right-al">{pct((g['indep']/g['price']-1)*100)} vs. mercado</td></tr>
    <tr><td class="label">Promedio ponderado de los anclados al mercado (60% del peso)</td><td class="label"></td><td class="right-al">{usd(g['anch'])}</td><td class="right-al"></td><td class="right-al">{pct((g['anch']/g['price']-1)*100)} vs. mercado</td></tr>
    <tr class="total"><td class="label">Blend ponderado — fair value final</td><td class="label"></td><td class="right-al">{BL}</td><td class="right-al">100%</td><td class="right-al">{pct(g['blend_gap'])} vs. mercado</td></tr>
  </table></div>
  <p class="footnote">Aportes = fair value &times; peso; el blend es la suma: {' + '.join(es(g['contrib_'+k]) for k in ('dcf','sotp','comp','rev','cons'))} = {es(g['blend'])}. Como referencia, el promedio simple de los cinco (la regla que usaba septiembre) daría {usd(g['blend_simple'])}; el valor esperado ponderado por probabilidad de los tres escenarios del DCF (25/45/30), {usd(g['dcf_pw'])}.</p>
  <h3>Antes &rarr; ahora: qué cambió desde la edición de septiembre</h3>
  <div class="table-scroll"><table>
    <tr><th>Método</th><th class="right-al">Sep-2026 (3T FY26)</th><th class="right-al">Nov-2026 (4T FY26)</th><th class="right-al">Cambio</th><th class="right-al">Aporte al cambio del blend</th></tr>
    <tr><td class="label">DCF Base</td><td class="right-al">$102,32</td><td class="right-al">{usd(g['dcf_base'])}</td><td class="right-al">{usd(g['chg_dcf'])}</td><td class="right-al">{usd(g['chg_contrib_dcf'])}</td></tr>
    <tr><td class="label">Suma de partes</td><td class="right-al">$98,01</td><td class="right-al">{usd(g['sotp_base'])}</td><td class="right-al">{usd(g['chg_sotp'])}</td><td class="right-al">{usd(g['chg_contrib_sotp'])}</td></tr>
    <tr><td class="label">Comparables</td><td class="right-al">$95,36</td><td class="right-al">{usd(g['comp'])}</td><td class="right-al">{usd(g['chg_comp'])}</td><td class="right-al">{usd(g['chg_contrib_comp'])}</td></tr>
    <tr><td class="label">Reversión</td><td class="right-al">$108,12</td><td class="right-al">{usd(g['rev'])}</td><td class="right-al">{usd(g['chg_rev'])}</td><td class="right-al">{usd(g['chg_contrib_rev'])}</td></tr>
    <tr><td class="label">Consenso</td><td class="right-al">$127,61</td><td class="right-al">{usd(g['cons'])}</td><td class="right-al">{usd(g['chg_cons'])}</td><td class="right-al">{usd(g['chg_contrib_cons'])}</td></tr>
    <tr class="total"><td class="label">Blend ponderado (septiembre recalculado con la regla vigente)</td><td class="right-al">{usd(g['sep_blend_w'])}</td><td class="right-al">{BL}</td><td class="right-al">{usd(g['blend_chg_vs_w'])} ({pct(g['blend_chg_pct_w'])})</td><td class="right-al">{usd(g['blend_chg_vs_w'])}</td></tr>
    <tr><td class="label">Blend publicado en septiembre (promedio simple)</td><td class="right-al">$106,28</td><td class="right-al">{BL}</td><td class="right-al">{usd(g['blend_chg_vs_pub'])}</td><td class="right-al"></td></tr>
    <tr><td class="label">Precio de referencia</td><td class="right-al">$104,16</td><td class="right-al">{PR}</td><td class="right-al">{pct(g['price_chg'])}</td><td class="right-al"></td></tr>
    <tr><td class="label">Fair value contra el precio</td><td class="right-al">+2,0% (publicado) / {pct(g['sep_blend_w_gap'])} (ponderado)</td><td class="right-al">{pct(g['blend_gap'])}</td><td class="right-al"></td><td class="right-al"></td></tr>
  </table></div>
  <div class="chartbox">
    <canvas id="footballChart" height="290"></canvas>
    <p class="chartcap">"Football field" de valuación — rango bajo/alto de cada metodología. La línea roja marca el precio de mercado ({usd(g['price'],0)}); la azul, el blend propio ({usd(g['blend'],0)}); la dorada, el consenso de Wall Street ({usd(g['cons'],0)}).</p>
  </div>
  <p>
    El blend de <strong>{BL}</strong> queda {pct(g['blend_gap'])} contra el precio de {PR}. Los métodos que no usan el precio de Disney
    promedian {usd(g['indep'])} ({pct((g['indep']/g['price']-1)*100)}): con un costo de capital de CAPM, valuando cada segmento por separado o
    contra lo que el mercado paga por sus pares, Disney vale menos que su precio. Los anclados al mercado promedian
    {usd(g['anch'])}: el consenso queda arriba y su propio múltiplo reciente, levemente abajo. La postura es <strong>neutral,
    levemente por debajo del precio</strong> (en septiembre: neutral, prácticamente en línea). El negocio mejoró en todo lo
    que importa —streaming rentable, Experiences récord, ESPN con audiencias récord, más caja para el accionista—, y el
    fair value subió {pct(g['blend_chg_pct_w'])} contra la versión ponderada de septiembre; pero la acción subió {pct(g['price_chg'])}, a ~{es(g['pe_ntm'],1)}x el
    EPS de 2027, y la compañía va a mostrar menos de su motor más visible. Para que haya un upside sustancial tiene que
    cumplirse lo que asume el consenso: el "doble dígito" de 2027 sin la semana extra y un múltiplo que vuelva hacia el de
    fines de 2025.
  </p>

  """)

# ---------------- 14 ----------------
between('<!-- 14 -->', '<div class="disclosure">', f"""<!-- 14 -->
  <p class="secnum" id="s14">14 — Limitaciones del Modelo</p>
  <h2>Qué asume este análisis, y dónde puede fallar</h2>
  <div class="watermark-block">
    <p style="margin-bottom:0;">
      Entre {es(g['dcf_bear_tv'],0)}% y {es(g['dcf_bull_tv'],0)}% del valor de empresa de los tres escenarios del DCF proviene del valor terminal: el modelo
      es, por construcción, sensible a supuestos de largo plazo. El DCF de septiembre no publicaba los años intermedios: la
      reconstrucción con interpolación lineal reproduce el Base al centavo y la grilla con diferencias de hasta US$0,22, y esta
      edición mantiene esa convención (flujos a fin de año, año 1 = año fiscal 2027 completo aunque la valuación es del
      21-nov-2026, lo que la hace levemente conservadora). El beta de 1,30 está por debajo del {es(g['beta_sa'],2)} de stockanalysis (con
      ese beta el Base daría {usd(g['dcf_beta_sa'])}); la prima de riesgo de 5,0% es la fija del marco (con la implícita de Damodaran,
      {usd(g['dcf_erp_dam'])}). La deuda neta de ~US${es(g['nd']*1000,0)} millones apalanca el equity: por eso el rango Bear&ndash;Bull del DCF
      ({usd(g['dcf_bear'],0)} a {usd(g['dcf_bull'],0)}) es mucho más amplio que el de una cobertura con balance sano. La suma de partes usa
      múltiplos de segmento elegidos con juicio, resta las participaciones no controlantes a valor libro y mantiene la apertura
      de segmentos vieja; con la nueva daría {usd(g['sotp_recast'])}. Desde el año fiscal 2027 Disney no publica la utilidad del
      streaming, así que la próxima edición no podrá separar su margen. El panel de comparables tiene tres empresas y ninguna
      es equivalente a Disney; Netflix cayó fuerte entre ediciones y eso solo movió el promedio del panel. La reversión usa
      cuatro cierres trimestrales (EPS realizado, no el consenso de cada fecha). La utilidad GAAP de Disney está distorsionada
      por partidas no recurrentes, por lo que el informe trabaja con la utilidad ajustada —que incorpora juicios de la
      compañía sobre qué excluir—. El 10-K del año fiscal 2026 se presentó el 17-nov-2026, junto con el comunicado.
    </p>
  </div>

  """)

# ---------------- disclosure ----------------
between('    Documento elaborado a partir de fuentes públicas: SEC EDGAR', '    <br><br>', """    Documento elaborado a partir de fuentes públicas: SEC EDGAR (8-K del 17-nov-2026 con la carta del 4T fiscal 2026, 10-K del
    año fiscal 2026 presentado el 17-nov-2026, 8-K ítem 7.01 del 17-nov-2026 con el cambio de reporte por segmento, 10-Q del
    1T al 3T fiscal 2026 y comunicados del 2-feb, 6-may y 5-ago-2026, XBRL companyfacts API, CIK 0001744489), Yahoo Finance
    (precios y rendimiento del Treasury a 10 años), stockanalysis.com / S&amp;P Global (consenso de EPS y precios objetivo,
    beta), Census Bureau (ventas minoristas), Universidad de Michigan (confianza del consumidor), BLS (IPC), EIA (diésel),
    NRF (pronóstico de la temporada navideña), Damodaran Online (prima de riesgo implícita), financecharts.com,
    fullratio.com, ycharts (P/E históricos de largo plazo), Variety, CNBC, The Hollywood Reporter, Deadline, The Wrap
    (sucesión de CEO y compensación ejecutiva), y análisis de ownership institucional de Disney. Cifras fundamentales con
    fecha de corte en el 10-K del año fiscal cerrado el 3 de octubre de 2026; precios de mercado al cierre del 20 de
    noviembre de 2026; desarrollos corporativos con fecha de corte del 21 de noviembre de 2026.
""")

# ---------------- gráficos ----------------
rep("labels:['FY2019','FY2020','FY2021','FY2022','FY2023','FY2024','FY2025','TTM'],\n      values:[69.57,65.39,67.42,82.72,88.90,91.36,94.43,98.86],",
    "labels:['FY2019','FY2020','FY2021','FY2022','FY2023','FY2024','FY2025','FY2026'],\n      values:[69.57,65.39,67.42,82.72,88.90,91.36,94.43,102.34],")
rep("values:[10.819,4.807,2.612],", "values:[11.191,5.443,3.094],")
rep("""labels:["4T'24","1T'25","2T'25","3T'25","4T'25","1T'26","2T'26","3T'26"],""", """labels:["1T'25","2T'25","3T'25","4T'25","1T'26","2T'26","3T'26","4T'26"],""")
rep("values:[16.2,20.5,18.8,19.3,15.5,17.7,18.3,22.0]", f"values:[20.5,18.8,19.3,15.5,17.7,18.3,22.0,{g['q4_seg_m']:.1f}]")
rep("labels:['3T FY25','4T FY25','1T FY26','2T FY26','3T FY26'],\n      values:[1.89,2.56,-2.28,4.94,3.07],",
    "labels:['4T FY25','1T FY26','2T FY26','3T FY26','4T FY26'],\n      values:[2.56,-2.28,4.94,3.07,4.84],")
rep("colors:[PALETTE.blueLight,PALETTE.blueLight,PALETTE.red,PALETTE.navy2,PALETTE.navy],\n      valueFmt:function(v){ return (v<0?'−$':'$')",
    "colors:[PALETTE.blueLight,PALETTE.red,PALETTE.blueLight,PALETTE.navy2,PALETTE.navy],\n      valueFmt:function(v){ return (v<0?'−$':'$')")
rep("values:[20.3,15.1,14.0,7.5],", f"values:[{pe['NFLX']:.2f},{g['pe_ntm']:.2f},{pe['FOXA']:.2f},{pe['CMCSA']:.2f}],")
rep("""      labels:['DCF (Bear → Bull)','Comparables (piso → techo panel)','Sum-of-the-parts (bajo → alto)'],
      ranges:[[50.25,167.93],[51.83,140.27],[76.10,119.92]],
      colors:[PALETTE.blue,PALETTE.navy2,PALETTE.blueLight],
      refLines:[{value:104.16,color:PALETTE.red,label:'Mercado $104'},{value:106.28,color:PALETTE.navy,label:'Blend $106'},{value:127.61,color:PALETTE.gold,label:'Consenso $128'}],""",
    f"""      labels:['DCF (Bear → Bull)','Sum-of-the-parts (bajo → alto)','Comparables (piso → techo panel)','Reversión (ventana limpia)','Consenso (rango)'],
      ranges:[[{g['dcf_bear']:.2f},{g['dcf_bull']:.2f}],[{g['sotp_low']:.2f},{g['sotp_high']:.2f}],[{g['comp_low']:.2f},{g['comp_high']:.2f}],[{g['rev_low']:.2f},{g['rev_high']:.2f}],[{g['cons_low']:.2f},{g['cons_high']:.2f}]],
      colors:[PALETTE.blue,PALETTE.blueLight,PALETTE.navy2,PALETTE.pale,PALETTE.gold],
      refLines:[{{value:{g['price']:.2f},color:PALETTE.red,label:'Mercado ${g['price']:.0f}'}},{{value:{g['blend']:.2f},color:PALETTE.navy,label:'Blend ${g['blend']:.0f}'}},{{value:{g['cons']:.2f},color:PALETTE.gold,label:'Consenso ${g['cons']:.0f}'}}],""")
rep("labels:['FY2024','FY2025','FY2026E','FY2027E'],\n      values:[4.97,5.93,6.91,7.47],\n      colors:[PALETTE.blueLight,PALETTE.blue,PALETTE.navy2,PALETTE.navy],",
    f"labels:['FY2024','FY2025','FY2026','FY2027E','FY2028E'],\n      values:[4.97,5.93,7.02,{g['c27']:.2f},{g['c28']:.2f}],\n      colors:[PALETTE.pale,PALETTE.blueLight,PALETTE.navy,PALETTE.blue,PALETTE.blueLight],")

open(F, 'w', encoding='utf-8', newline='\n').write(s)
print('ok', len(s))
