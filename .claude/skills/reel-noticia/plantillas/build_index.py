"""Arma index.html a partir de la lista de escenas (id, segundo en que entra).

Para resincronizar con la voz: cambiar los segundos de SCENES (y END) y correr
    python -I build_index.py
Cada escena dura hasta que entra la siguiente + 0,34 s (el solape de la transición).
"""
import pathlib

SCENES = [
    ("golpe", 0),
    ("ranking", 2.96),
    ("ventas", 6.96),
    ("gasto", 9.96),
    ("panaderia", 19.76),
    ("ironia", 29.76),
    ("nube", 38.96),
    ("informe", 44.46),
    ("final", 52.46),
    ("comenta", 61.46),
    ("logo", 67.06),
]
END = 70.6
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
    # golpe: el chip cae, pega y se parte; la regla de años frena en 2004
    ("swoosh-b", "golpe", 1.80, 0.30, {}),
    ("impact-bass-1", "golpe", 1.92, 0.60, {"dur": 1.4}),
    ("crack-a", "golpe", 1.97, 0.55, {}),
    ("click", "golpe", 2.75, 0.35, {}),
    # ranking: barras que llegan, la de 2026 cae y golpea, contador y "borrados"
    ("pop", "ranking", 0.90, 0.28, {}),
    ("pop", "ranking", 2.00, 0.28, {}),
    ("impact-bass-1", "ranking", 2.18, 0.42, {"dur": 1.0}),
    ("pop", "ranking", 2.30, 0.32, {}),
    ("typing", "ranking", 3.25, 0.45, {"skip": 0.44, "dur": 0.45}),
    ("ping", "ranking", 3.45, 0.32, {}),
    # ventas: +25%, entra el chip roto, aparece el "?"
    ("pop", "ventas", 0.95, 0.32, {}),
    ("swoosh-b", "ventas", 1.80, 0.22, {}),
    ("pop", "ventas", 2.45, 0.38, {}),
    # gasto: ventas ok, salen los billetes, caen los racks, golpe del contador, x2,1
    ("pop", "gasto", 0.92, 0.28, {}),
    ("swoosh-c", "gasto", 2.05, 0.32, {}),
    ("impact-bass-1", "gasto", 3.34, 0.16, {"dur": 0.5}),
    ("impact-bass-1", "gasto", 3.56, 0.13, {"dur": 0.5}),
    ("impact-bass-1", "gasto", 3.78, 0.17, {"dur": 0.5}),
    ("impact-bass-1", "gasto", 4.00, 0.13, {"dur": 0.5}),
    ("impact-bass-1", "gasto", 4.22, 0.16, {"dur": 0.5}),
    ("impact-bass-1", "gasto", 5.90, 0.55, {"dur": 1.4}),
    ("pop", "gasto", 8.45, 0.35, {}),
    # panadería: cartel, panes, hornos pesados, la caja y el golpe del -9.065
    ("click", "panaderia", 0.53, 0.38, {}),
    ("pop", "panaderia", 1.35, 0.22, {}),
    ("pop", "panaderia", 1.79, 0.20, {}),
    ("pop", "panaderia", 2.23, 0.22, {}),
    ("impact-bass-1", "panaderia", 3.35, 0.24, {"dur": 0.6}),
    ("impact-bass-1", "panaderia", 3.75, 0.22, {"dur": 0.6}),
    ("swoosh-b", "panaderia", 4.75, 0.24, {}),
    ("ping", "panaderia", 6.27, 0.30, {}),
    ("click", "panaderia", 7.95, 0.35, {}),
    ("impact-bass-1", "panaderia", 8.94, 0.58, {"dur": 1.4}),
    # ironía: el cohete llega, despega (crece), el otro cae y choca
    ("swoosh-b", "ironia", 2.05, 0.22, {}),
    ("pop", "ironia", 2.62, 0.24, {}),
    ("pop", "ironia", 3.22, 0.24, {}),
    ("whoosh-cinematic", "ironia", 4.85, 0.40, {}),
    ("swoosh-c", "ironia", 7.85, 0.34, {}),
    ("impact-bass-1", "ironia", 8.00, 0.58, {"dur": 1.4}),
    ("crack-b", "ironia", 8.00, 0.45, {}),
    # nube: entra la nube, +103%, los hornos sacan pan
    ("swoosh-b", "nube", 0.90, 0.22, {}),
    ("sparkle", "nube", 2.58, 0.28, {}),
    ("pop", "nube", 4.45, 0.22, {}),
    ("pop", "nube", 4.81, 0.20, {}),
    # informe: la tarjeta entra, aterriza el valor justo, el precio toca la línea dorada
    ("swoosh-a", "informe", 0.95, 0.30, {}),
    ("pop", "informe", 3.42, 0.34, {}),
    ("impact-bass-2", "informe", 6.90, 0.42, {}),
    ("sparkle", "informe", 6.92, 0.30, {}),
    # final: tarjeta tachada, tarjeta roja que golpea, tres toques del cursor
    ("swoosh-b", "final", 1.55, 0.22, {}),
    ("click", "final", 2.27, 0.22, {}),
    ("impact-bass-1", "final", 3.62, 0.45, {"dur": 1.2}),
    ("click", "final", 5.62, 0.45, {}),
    ("click", "final", 6.37, 0.45, {}),
    ("click", "final", 7.22, 0.45, {}),
    # comenta: tipea G-O-O-G-L-E, enviar, corazón, llega el mensaje
    ("key-press", "comenta", 1.81, 0.50, {}),
    ("key-press", "comenta", 1.90, 0.42, {}),
    ("key-press", "comenta", 1.99, 0.50, {}),
    ("key-press", "comenta", 2.08, 0.44, {}),
    ("key-press", "comenta", 2.17, 0.50, {}),
    ("key-press", "comenta", 2.26, 0.46, {}),
    ("click", "comenta", 2.73, 0.48, {}),
    ("pop", "comenta", 3.12, 0.30, {}),
    ("notification", "comenta", 3.52, 0.34, {}),
    # logo: el golpe con crecida llega cuando aterriza el emblema
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
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
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
