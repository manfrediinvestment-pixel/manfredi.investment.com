"""Arma index.html a partir de la lista de escenas (id, segundo en que entra).

Para resincronizar con la voz: cambiar los segundos de SCENES (y END) y correr
    python -I build_index.py
Cada escena dura hasta que entra la siguiente + 0,34 s (el solape de la transición).
"""
import pathlib

SCENES = [
    ("golpe", 0),
    ("esperado", 4.6),
    ("pregunta", 10.0),
    ("recompras", 14.2),
    ("campo", 21.2),
    ("siembra", 30.1),
    ("silo", 39.7),
    ("informe", 47.2),
    ("final", 55.6),
    ("comenta", 63.8),
    ("logo", 69.4),
]
END = 72.9
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
    # golpe: el contador aterriza, la placa cae y pega cuando la acción pasa a rojo
    ("pop", "golpe", 1.45, 0.30, {}),
    ("swoosh-b", "golpe", 2.55, 0.28, {}),
    ("impact-bass-1", "golpe", 2.90, 0.60, {"dur": 1.4}),
    # esperado: barra de lo esperado, lo que dio cae y golpea, badge
    ("pop", "esperado", 0.60, 0.26, {}),
    ("swoosh-b", "esperado", 3.05, 0.24, {}),
    ("impact-bass-1", "esperado", 3.30, 0.48, {"dur": 1.0}),
    ("pop", "esperado", 4.15, 0.34, {}),
    # pregunta: renglones, lupa, cae el "?"
    ("pop", "pregunta", 0.45, 0.18, {}),
    ("pop", "pregunta", 0.61, 0.18, {}),
    ("pop", "pregunta", 0.77, 0.18, {}),
    ("pop", "pregunta", 0.93, 0.22, {}),
    ("swoosh-c", "pregunta", 1.75, 0.28, {}),
    ("impact-bass-1", "pregunta", 3.28, 0.42, {"dur": 1.0}),
    # recompras: barras que crecen, la última se desploma, -84%
    ("pop", "recompras", 0.60, 0.20, {}),
    ("pop", "recompras", 0.82, 0.20, {}),
    ("pop", "recompras", 1.04, 0.20, {}),
    ("pop", "recompras", 1.26, 0.22, {}),
    ("impact-bass-1", "recompras", 3.82, 0.60, {"dur": 1.4}),
    ("crack-a", "recompras", 3.84, 0.45, {}),
    ("pop", "recompras", 5.00, 0.36, {}),
    # campo: cartel clavado, nubes, brotes, la cosecha
    ("impact-bass-1", "campo", 0.57, 0.24, {"dur": 0.6}),
    ("swoosh-b", "campo", 1.40, 0.24, {}),
    ("sparkle", "campo", 2.70, 0.22, {}),
    ("pop", "campo", 2.75, 0.14, {}),
    ("pop", "campo", 3.11, 0.14, {}),
    ("pop", "campo", 3.47, 0.14, {}),
    ("pop", "campo", 3.83, 0.14, {}),
    ("pop", "campo", 4.19, 0.14, {}),
    ("swoosh-a", "campo", 5.70, 0.24, {}),
    ("pop", "campo", 7.25, 0.36, {}),
    ("sparkle", "campo", 7.12, 0.26, {}),
    # siembra: opción 1, barras, el x3 golpea, sello CARO, semillas, cita
    ("swoosh-b", "siembra", 0.70, 0.22, {}),
    ("pop", "siembra", 3.15, 0.24, {}),
    ("pop", "siembra", 4.15, 0.24, {}),
    ("impact-bass-1", "siembra", 5.10, 0.45, {"dur": 1.0}),
    ("impact-bass-1", "siembra", 5.88, 0.40, {"dur": 1.0}),
    ("crack-a", "siembra", 5.88, 0.30, {}),
    ("swoosh-c", "siembra", 6.55, 0.26, {}),
    ("pop", "siembra", 7.50, 0.16, {}),
    ("pop", "siembra", 7.65, 0.16, {}),
    ("pop", "siembra", 7.80, 0.18, {}),
    ("swoosh-a", "siembra", 7.35, 0.20, {}),
    # silo: entra, cae el grano, el número llega, se tacha la sequía, brota
    ("swoosh-b", "silo", 0.20, 0.22, {}),
    ("typing", "silo", 1.20, 0.22, {"skip": 0.30, "dur": 1.2}),
    ("ping", "silo", 3.02, 0.30, {}),
    ("click", "silo", 4.32, 0.38, {}),
    ("pop", "silo", 4.85, 0.30, {}),
    ("pop", "silo", 5.55, 0.24, {}),
    ("pop", "silo", 5.73, 0.24, {}),
    # informe: tarjeta, valor justo, la brecha
    ("swoosh-a", "informe", 0.45, 0.28, {}),
    ("pop", "informe", 2.62, 0.34, {}),
    ("impact-bass-2", "informe", 4.90, 0.42, {}),
    ("sparkle", "informe", 4.62, 0.24, {}),
    # final: tachado, tarjeta roja, tres toques
    ("swoosh-b", "final", 0.55, 0.22, {}),
    ("click", "final", 1.37, 0.24, {}),
    ("impact-bass-1", "final", 2.07, 0.45, {"dur": 1.2}),
    ("click", "final", 4.42, 0.45, {}),
    ("click", "final", 5.17, 0.45, {}),
    ("click", "final", 6.32, 0.45, {}),
    # comenta: J-P-M-O-R-G-A-N, enviar, corazón, mensaje
    ("key-press", "comenta", 1.81, 0.5, {}),
    ("key-press", "comenta", 1.88, 0.46, {}),
    ("key-press", "comenta", 1.95, 0.5, {}),
    ("key-press", "comenta", 2.02, 0.46, {}),
    ("key-press", "comenta", 2.09, 0.5, {}),
    ("key-press", "comenta", 2.16, 0.46, {}),
    ("key-press", "comenta", 2.23, 0.5, {}),
    ("key-press", "comenta", 2.30, 0.46, {}),
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
