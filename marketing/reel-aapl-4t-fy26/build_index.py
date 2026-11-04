"""Arma index.html a partir de la lista de escenas (id, segundo en que entra).

Para resincronizar con la voz: cambiar los segundos de SCENES (y END) y correr
    python -I build_index.py
Cada escena dura hasta que entra la siguiente + 0,34 s (el solape de la transición).
"""
import pathlib

SCENES = [
    ("golpe", 0),
    ("reaccion", 3.3),
    ("pregunta", 7.9),
    ("causa", 12.5),
    ("heladeria", 23.1),
    ("ironia", 35.0),
    ("cola", 41.8),
    ("informe", 46.2),
    ("final", 53.8),
    ("comenta", 62.0),
    ("logo", 67.6),
]
END = 71.1
WHIP = 0.3  # duración de la transición latigazo vertical


# ---------------------------------------------------------------------------
# SONIDO. Cada efecto tiene una causa en pantalla. El tiempo es el del CUADRO
# donde pasa la acción (segundos locales de la escena); el script resta el pico
# del archivo para que el golpe suene 1 cuadro después de verse.
# (archivo, escena, segundo_local, volumen, extra)
# ---------------------------------------------------------------------------
PEAK = {  # segundo del pico de cada archivo (npx hyperframes audio --only moments)
    "swoosh-a": 0.291, "swoosh-b": 0.042, "swoosh-c": 1.312, "crack-a": 0.028, "crack-b": 1.017,
    "impact-bass-1": 0.073, "impact-bass-2": 1.986, "pop": 0.120, "click": 0.073, "key-press": 0.076,
    "ping": 0.324, "sparkle": 0.027, "notification": 0.229, "typing": 0.457, "whoosh-cinematic": 2.503,
}
SFX = [
    # golpe: el récord aterriza; el chip de Apple cae, pega y se parte
    ("pop", "golpe", 1.50, 0.30, {}),
    ("swoosh-b", "golpe", 2.38, 0.30, {}),
    ("impact-bass-1", "golpe", 2.50, 0.60, {"dur": 1.4}),
    ("crack-a", "golpe", 2.55, 0.55, {}),
    # reacción: entran las 5 en verde, Apple cae en rojo, contador y "borrados"
    ("pop", "reaccion", 0.45, 0.16, {}),
    ("pop", "reaccion", 0.69, 0.16, {}),
    ("pop", "reaccion", 0.93, 0.16, {}),
    ("impact-bass-1", "reaccion", 1.32, 0.45, {"dur": 1.0}),
    ("pop", "reaccion", 1.50, 0.30, {}),
    ("ping", "reaccion", 3.10, 0.30, {}),
    ("typing", "reaccion", 3.40, 0.45, {"skip": 0.44, "dur": 0.45}),
    ("pop", "reaccion", 3.70, 0.28, {}),
    # pregunta: +11,7%, le ganó al consenso, entra el chip roto, "?"
    ("pop", "pregunta", 0.95, 0.32, {}),
    ("pop", "pregunta", 1.50, 0.26, {}),
    ("swoosh-b", "pregunta", 2.40, 0.22, {}),
    ("pop", "pregunta", 3.15, 0.38, {}),
    # causa: la guía cae y golpea; módulos de memoria en serie; inventario x2,5
    ("swoosh-b", "causa", 4.55, 0.22, {}),
    ("impact-bass-1", "causa", 4.91, 0.55, {"dur": 1.4}),
    ("pop", "causa", 5.15, 0.30, {}),
    ("impact-bass-1", "causa", 7.04, 0.16, {"dur": 0.5}),
    ("impact-bass-1", "causa", 7.26, 0.13, {"dur": 0.5}),
    ("impact-bass-1", "causa", 7.48, 0.17, {"dur": 0.5}),
    ("impact-bass-1", "causa", 7.70, 0.13, {"dur": 0.5}),
    ("pop", "causa", 7.90, 0.22, {}),
    ("impact-bass-1", "causa", 9.70, 0.40, {"dur": 1.0}),
    ("pop", "causa", 9.75, 0.30, {}),
    # heladería: toldo, cartel, freezer pesado, gustos, crema y cucuruchos, la cuenta y el golpe del -$3,30
    ("impact-bass-1", "heladeria", 0.48, 0.24, {"dur": 0.6}),
    ("click", "heladeria", 0.72, 0.38, {}),
    ("impact-bass-1", "heladeria", 1.17, 0.30, {"dur": 0.7}),
    ("pop", "heladeria", 1.30, 0.18, {}),
    ("pop", "heladeria", 1.42, 0.16, {}),
    ("pop", "heladeria", 1.54, 0.18, {}),
    ("pop", "heladeria", 1.66, 0.16, {}),
    ("pop", "heladeria", 2.75, 0.24, {}),
    ("impact-bass-1", "heladeria", 3.83, 0.22, {"dur": 0.6}),
    ("impact-bass-1", "heladeria", 4.68, 0.22, {"dur": 0.6}),
    ("ping", "heladeria", 5.45, 0.28, {}),
    ("swoosh-b", "heladeria", 6.60, 0.24, {}),
    ("ping", "heladeria", 7.30, 0.26, {}),
    ("click", "heladeria", 9.05, 0.35, {}),
    ("impact-bass-1", "heladeria", 10.37, 0.58, {"dur": 1.4}),
    # ironía: flecha que baja, flecha que sube, el P/E cae encima
    ("swoosh-c", "ironia", 2.55, 0.26, {}),
    ("pop", "ironia", 3.45, 0.26, {}),
    ("swoosh-c", "ironia", 4.10, 0.26, {}),
    ("pop", "ironia", 5.00, 0.26, {}),
    ("impact-bass-1", "ironia", 5.69, 0.50, {"dur": 1.2}),
    # cola: +17,5% y la Mac
    ("pop", "cola", 2.50, 0.30, {}),
    ("pop", "cola", 3.10, 0.24, {}),
    # informe: la tarjeta entra, aterriza el valor justo, el corchete mide la distancia
    ("swoosh-a", "informe", 0.30, 0.30, {}),
    ("pop", "informe", 2.80, 0.34, {}),
    ("impact-bass-2", "informe", 5.95, 0.42, {}),
    ("sparkle", "informe", 5.97, 0.30, {}),
    # final: tarjeta tachada, tarjeta roja que golpea, tres toques del cursor
    ("swoosh-b", "final", 1.55, 0.22, {}),
    ("click", "final", 2.27, 0.22, {}),
    ("impact-bass-1", "final", 3.62, 0.45, {"dur": 1.2}),
    ("click", "final", 5.62, 0.45, {}),
    ("click", "final", 6.37, 0.45, {}),
    ("click", "final", 7.22, 0.45, {}),
    # comenta: tipea A-P-P-L-E, enviar, corazón, llega el mensaje
    ("key-press", "comenta", 1.81, 0.50, {}),
    ("key-press", "comenta", 1.90, 0.42, {}),
    ("key-press", "comenta", 1.99, 0.50, {}),
    ("key-press", "comenta", 2.08, 0.44, {}),
    ("key-press", "comenta", 2.17, 0.50, {}),
    ("click", "comenta", 2.73, 0.48, {}),
    ("pop", "comenta", 3.12, 0.30, {}),
    ("notification", "comenta", 3.52, 0.34, {}),
    # logo
    ("impact-bass-2", "logo", 0.55, 0.40, {}),
]
DUR = {  # duración de cada archivo (s)
    "swoosh-a": 0.92, "swoosh-b": 0.70, "swoosh-c": 1.85, "crack-a": 0.81, "crack-b": 3.48,
    "impact-bass-1": 2.12, "impact-bass-2": 2.59, "pop": 0.72, "click": 0.37, "key-press": 0.40,
    "ping": 1.32, "sparkle": 1.80, "notification": 2.46, "typing": 1.50, "whoosh-cinematic": 5.54,
}
WHOOSHES = ["swoosh-a", "swoosh-c", "swoosh-b"]  # rotan en cada transición
WHOOSH_VOL = {"swoosh-a": 0.42, "swoosh-b": 0.50, "swoosh-c": 0.34}

def sfx_tags():
    start = dict(SCENES)
    cues = []
    for i in range(1, len(SCENES)):
        f = WHOOSHES[(i - 1) % len(WHOOSHES)]
        cues.append((f, SCENES[i][1] + WHIP / 2, WHOOSH_VOL[f], {}))   # pico en el cuadro más rápido del latigazo
    for f, sc, t, v, x in SFX:
        cues.append((f, start[sc] + t, v, x))
    tags, ends = [], []  # ends[k] = segundo en que se libera la pista 30+k
    for n, (f, t, v, x) in enumerate(sorted(cues, key=lambda c: c[1])):
        skip = x.get("skip", 0)  # segundos recortados del inicio del archivo
        st = round(max(0.0, t - (PEAK[f] - skip) + 1 / 60), 3)
        dur = round(min(x.get("dur", 99), DUR[f] - skip, END - st), 3)
        k = next((i for i, e in enumerate(ends) if e <= st), None)
        if k is None:
            ends.append(0)
            k = len(ends) - 1
        ends[k] = st + dur
        attrs = f'id="sfx-{n:02d}" src="assets/sfx/{f}.mp3" data-start="{st}" data-duration="{dur}" data-volume="{v}" data-track-index="{30 + k}"'
        if skip:
            attrs += f' data-media-start="{skip}"'
        tags.append(f"      <audio {attrs}></audio>")
    return "\n".join(tags), len(tags)

hosts, z = [], []
for i, (sid, st) in enumerate(SCENES):
    nxt = SCENES[i + 1][1] + 0.34 if i + 1 < len(SCENES) else END
    dur = round(nxt - st, 2)
    hosts.append(
        f'      <div id="{sid}" class="scene" data-composition-id="{sid}" data-composition-src="compositions/{sid}.html"\n'
        f'        data-start="{st}" data-duration="{dur}" data-track-index="{i + 1}" data-track-kind="graphics" data-width="1080" data-height="1920"></div>'
    )
    z.append(f"#{sid} {{ z-index: {len(SCENES) - i}; }}")
sets = "\n".join(f'      tl.set("#{s}", {{ y: 1920 }}, 0);' for s, _ in SCENES[1:])
whips = "\n".join(f'      whip("#{SCENES[i][0]}", "#{SCENES[i + 1][0]}", {SCENES[i + 1][1]});' for i in range(len(SCENES) - 1))

SFX_TAGS, N_SFX = sfx_tags()
html = f"""<!doctype html>
<html lang="es" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="assets/gsap.min.js"></script>
    <link rel="stylesheet" href="assets/brand.css" />
    <script src="assets/brand.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #060d1a; }}
      #root {{ position: relative; width: 100%; height: 100%; overflow: hidden; }}
      .scene {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; }}
      {" ".join(z)}
    </style>
  </head>
  <body>
    <!-- Generado por build_index.py: no editar a mano. Guion en GUION.md. -->
    <div id="root" data-composition-id="main" data-start="0" data-duration="{END}" data-width="1080" data-height="1920"
      data-motion-blur="on" data-motion-blur-shutter="300">
{chr(10).join(hosts)}
{SFX_TAGS}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      // latigazo vertical: toda la escena sube y la siguiente entra pegada desde abajo, borde duro
      function whip(outSel, inSel, at) {{
        tl.fromTo(outSel, {{ y: 0 }}, {{ y: -1920, duration: {WHIP}, ease: "expo.inOut" }}, at);
        tl.fromTo(inSel, {{ y: 1920 }}, {{ y: 0, duration: {WHIP}, ease: "expo.inOut" }}, at);
      }}
{sets}
{whips}
      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>
"""
pathlib.Path(__file__).with_name("index.html").write_text(html, encoding="utf-8")
print(f"index.html: {len(SCENES)} escenas, {N_SFX} efectos de sonido, {END} s")
