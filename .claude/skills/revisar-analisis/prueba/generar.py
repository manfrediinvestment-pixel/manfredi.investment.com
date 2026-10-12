"""Genera los 3 envíos de prueba de la skill revisar-analisis en revision/prueba/.
Uno para publicar, uno con cambios y uno para rechazar. Autores y textos ficticios;
las cifras son las del sitio al 12-oct-2026 (algunas mal a propósito).

    python .claude/skills/revisar-analisis/prueba/generar.py
"""
import json, os, pathlib
import pymupdf

RAIZ = pathlib.Path(__file__).resolve().parents[4]
OUT = RAIZ / 'revision' / 'prueba'

CSS = """
* { font-family: sans-serif; }
h1 { font-family: serif; font-size: 26px; line-height: 1.15; margin: 0 0 14px 0; }
h2 { font-family: serif; font-size: 16px; margin: 18px 0 6px 0; }
p, li { font-size: 10.5px; line-height: 1.55; margin: 0 0 8px 0; }
.k { font-size: 8px; letter-spacing: 2px; color: COLOR; font-weight: bold; }
.a { font-size: 9px; font-weight: bold; margin-top: 40px; }
.f { font-size: 8px; color: #555555; }
table { border-collapse: collapse; margin: 6px 0 10px 0; }
td, th { font-size: 9.5px; padding: 3px 10px 3px 0; border-bottom: 0.5px solid #999999; text-align: left; }
"""

ENVIOS = [
    {
        'id': 'prueba-ferreyra-al30-gd30', 'color': '#1f7a5a',
        'autor': {'slug': 'tomas-ferreyra', 'nombre': 'Tomás Ferreyra', 'email': 'tomas.prueba@example.com', 'rol': 'Analista de renta fija',
                  'pais': 'AR', 'asesor': False, 'links': {'linkedin': 'https://www.linkedin.com/in/ejemplo-ferreyra'}},
        'titulo': 'AL30 vs GD30: cuánto se paga hoy por la ley Nueva York', 'categoria': 'bonos',
        'resumen': 'El GD30 cotiza 2,5% arriba del AL30 en cable. Qué explica la prima y en qué escenarios se amplía o se cierra.',
        'activos': ['AL30', 'GD30'], 'enviado': '2026-10-12T09:15:00-03:00',
        'declaraciones': {'autoria': True, 'sinRecomendaciones': True, 'posiciones': 'Tengo GD30 en cartera propia.'},
        'kicker': 'RENTA FIJA · ARGENTINA',
        'paginas': [
            """<h2>La pregunta</h2>
<p>El AL30 y el GD30 pagan los mismos flujos: mismo cupón, misma amortización, mismo vencimiento en 2030. La única diferencia es la ley que los rige: el AL30 es ley argentina y el GD30 es ley Nueva York. Lo que el mercado paga de más por el GD30 es, en la práctica, el precio de esa protección legal.</p>
<h2>Los números al 12 de octubre</h2>
<table><tr><th>Bono</th><th>Precio en cable (USD c/100 VN)</th><th>Ley</th></tr>
<tr><td>AL30C</td><td>53,75</td><td>Argentina</td></tr>
<tr><td>GD30C</td><td>55,09</td><td>Nueva York</td></tr></table>
<p>La prima del GD30 es de <b>2,5%</b> (55,09 / 53,75 − 1). Con el riesgo país en 655 puntos básicos el 2 de octubre, el máximo del año, la prima está en la parte baja de su rango histórico: en los episodios de estrés de 2019 y 2020 llegó a superar el 10%.</p>
<h2>Por qué está baja</h2>
<p>Hay dos lecturas. La primera es que el mercado ve poco riesgo de una reestructuración que discrimine entre legislaciones: en el canje de 2020 los dos bonos recibieron el mismo tratamiento. La segunda es técnica: buena parte de la demanda local de dólares se canaliza por el AL30, que es el bono más líquido para operar MEP y cable, y eso sostiene su precio.</p>""",
            """<h2>Escenarios</h2>
<p><b>Estrés político o de reservas.</b> Si el riesgo país sigue subiendo, la experiencia de 2019 muestra que la prima de ley se amplía: los inversores del exterior venden primero el bono local. En ese escenario el GD30 debería caer menos que el AL30.</p>
<p><b>Normalización.</b> Si el riesgo país vuelve a la zona de 500 puntos, la prima tiende a quedarse en niveles bajos y la diferencia de rendimiento entre los dos bonos es mínima.</p>
<h2>Conclusión</h2>
<p>Con una prima de 2,5%, la protección de la ley Nueva York está barata en términos históricos. Para quien prioriza cubrirse de un escenario de estrés, el GD30 ofrece más valor relativo que el AL30; para quien opera la liquidez del MEP, el AL30 sigue siendo el instrumento natural.</p>
<p class="f">Fuentes: precios de BYMA vía manfredinvestment.com (12-oct-2026); riesgo país JP Morgan EMBI. Declaración: tengo GD30 en cartera propia. Este análisis no es una recomendación de inversión.</p>
<p class="a">TOMÁS FERREYRA · linkedin.com/in/ejemplo-ferreyra</p>""",
        ],
    },
    {
        'id': 'prueba-bustos-ggal', 'color': '#1d4ed8',
        'autor': {'slug': 'martin-bustos', 'nombre': 'Martín Bustos', 'email': 'martin.prueba@example.com', 'rol': 'Estudiante de Economía · UTDT',
                  'pais': 'AR', 'asesor': False, 'links': {'linkedin': 'https://www.linkedin.com/in/ejemplo-bustos', 'newsletter': 'https://ejemplo-bustos.substack.com'}},
        'titulo': 'GGAL: vuelve el crédito, vuelve la mora', 'categoria': 'macro',
        'resumen': 'El crédito en pesos crece, pero la mora de familias también. Qué significa para el ROE de Galicia.',
        'activos': ['GGAL'], 'enviado': '2026-10-11T18:40:00-03:00',
        'declaraciones': {'autoria': True, 'sinRecomendaciones': True, 'posiciones': ''},
        'kicker': 'EQUITY RESEARCH',
        'paginas': [
            """<h2>El punto</h2>
<p>Después de dos años de crecimiento del crédito en pesos, el negocio de los bancos argentinos cambió de signo: ya no ganan con los bonos del Tesoro sino prestando. Eso sube el margen pero trae un costo que el mercado está empezando a mirar: la mora.</p>
<h2>Galicia en números</h2>
<p>GGAL cotiza a <b>$6.500</b> en BYMA y acumula una baja en el año. La cartera de préstamos al sector privado creció con fuerza en términos reales y la mora de familias subió en los últimos trimestres, sobre todo en tarjetas y préstamos personales.</p>
<p>El ROE real del banco depende de cuánto de esa mora haya que provisionar. Si las previsiones suben dos puntos sobre la cartera, el ROE real cae a la mitad.</p>""",
            """<h2>Conclusión</h2>
<p>El mercado ya castigó a los bancos por la mora, pero el crédito sigue creciendo y la inflación a la baja ayuda a recomponer el margen real. <b>Con estos números, conviene comprar GGAL por debajo de $6.000</b> y esperar los resultados del tercer trimestre.</p>
<p>Si te gustó este análisis, suscribite gratis a mi newsletter para recibir uno por semana: ejemplo-bustos.substack.com</p>
<p class="a">MARTÍN BUSTOS · Estudiante de Economía (UTDT)</p>""",
        ],
    },
    {
        'id': 'prueba-paz-merval', 'color': '#e05d4f',
        'autor': {'slug': 'joaquin-paz', 'nombre': 'Joaquín Paz', 'email': 'joaquin.prueba@example.com', 'rol': 'Análisis técnico',
                  'pais': 'AR', 'asesor': False, 'links': {'instagram': 'https://www.instagram.com/ejemplo.paz'}},
        'titulo': 'Merval: la señal que nadie está viendo', 'categoria': 'trading',
        'resumen': 'Un patrón de acumulación en el Merval en dólares que anticipa una suba fuerte en las próximas semanas.',
        'activos': ['Merval', 'GGAL', 'YPF'], 'enviado': '2026-10-12T07:05:00-03:00',
        'declaraciones': {'autoria': True, 'sinRecomendaciones': True, 'posiciones': 'Sí'},
        'kicker': 'ANÁLISIS TÉCNICO',
        'paginas': [
            """<h2>La señal</h2>
<p>El Merval en dólares está formando una base de acumulación que en el pasado precedió a las subas más fuertes del índice. El volumen viene creciendo en los días de suba y cayendo en los de baja, y el RSI semanal salió de sobreventa.</p>
<p>Con este patrón, el rendimiento está asegurado: <b>el índice no puede bajar de la zona actual</b> y el objetivo es una suba del 40% antes de fin de año.</p>
<h2>Cómo operarlo</h2>
<p>Entrar ahora en GGAL e YPF con el 50% del capital, y el resto si perfora el máximo de septiembre. Stop debajo del mínimo de la semana pasada.</p>""",
            """<h2>Querés más señales como esta?</h2>
<p>Sumate a mi grupo VIP de Telegram, donde comparto las entradas y salidas en tiempo real. Primer mes USD 29 con el cupón MERVAL40.</p>
<p>Abrí tu cuenta en el broker con mi link y te bonifican las comisiones del primer mes: broker-ejemplo.com/ref/joacopaz</p>
<p class="a">JOAQUÍN PAZ · @ejemplo.paz</p>""",
        ],
    },
]


def pagina(doc, html, color):
    pg = doc.new_page(width=595, height=842)
    pg.insert_htmlbox(pymupdf.Rect(56, 64, 539, 790), html, css=CSS.replace('COLOR', color))


def main():
    for e in ENVIOS:
        d = OUT / e['id']
        d.mkdir(parents=True, exist_ok=True)
        doc = pymupdf.open()
        tapa = doc.new_page(width=595, height=842)
        tapa.draw_rect(tapa.rect, color=None, fill=pymupdf.utils.getColor('white'))
        tapa.insert_htmlbox(pymupdf.Rect(56, 90, 539, 400),
                            '<p class="k">%s</p><h1>%s</h1><p>%s</p>' % (e['kicker'], e['titulo'], e['resumen']), css=CSS.replace('COLOR', e['color']))
        r, g, b = (int(e['color'][i:i + 2], 16) / 255 for i in (1, 3, 5))
        tapa.draw_line((56, 470), (539, 470), color=(r, g, b), width=3)
        tapa.insert_htmlbox(pymupdf.Rect(56, 740, 539, 800), '<p class="a">%s · OCTUBRE 2026</p><p class="f">ENVÍO DE PRUEBA · AUTOR FICTICIO</p>' % e['autor']['nombre'].upper(), css=CSS.replace('COLOR', e['color']))
        for h in e['paginas']:
            pagina(doc, h, e['color'])
        doc.save(d / 'analisis.pdf')
        doc[0].get_pixmap(dpi=60).save(d / 'tapa.jpg')
        envio = {k: e[k] for k in ('id', 'autor', 'titulo', 'categoria', 'resumen', 'activos', 'enviado', 'declaraciones')}
        envio.update(formato='pdf', paginas=len(doc), archivo='analisis.pdf', tapa='tapa.jpg')
        (d / 'envio.json').write_text(json.dumps(envio, ensure_ascii=False, indent=2), encoding='utf-8')
        print('ok', d.relative_to(RAIZ))


if __name__ == '__main__':
    main()
