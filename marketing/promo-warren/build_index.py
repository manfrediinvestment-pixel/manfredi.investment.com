"""Arma index.html a partir de la lista de escenas (id, segundo en que entra).

Para resincronizar con la voz: cambiar los segundos de SCENES (y END) y correr
    python -I build_index.py
Cada escena dura hasta que entra la siguiente + 0,34 s (el solape de la transición).
"""
import pathlib

SCENES = [
    ("gancho", 0),
    ("pregunta", 6.0),
    ("contexto", 12.0),
    ("revelacion", 22.0),   # entra sin latigazo: el botón de Warren crece y se vuelve el fondo
    ("respuesta", 27.0),
    ("real", 42.0),
    ("comenta", 54.0),
    ("logo", 63.0),
]
END = 66.0
NOWHIP = {"revelacion"}  # escenas que no entran con latigazo
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
    # gancho: golpe de entrada, logos que llegan, choque y cartel
    ("impact-bass-1", "gancho", 0.02, 0.55, {"dur": 1.2}),
    ("whoosh-cinematic", "gancho", 0.45, 0.30, {"dur": 1.2, "skip": 2.0}),
] + [("pop", "gancho", 0.25 + i * 0.07, 0.16, {}) for i in range(6)] + [
    ("swoosh-c", "gancho", 2.95, 0.36, {}),
    ("impact-bass-2", "gancho", 3.04, 0.55, {}),
    ("crack-a", "gancho", 3.05, 0.40, {}),
    ("impact-bass-1", "gancho", 3.43, 0.55, {"dur": 1.3}),
    ("sparkle", "gancho", 3.1, 0.28, {}),
    # pregunta: tecleo, enviar, respuesta de golpe, cartel
] + [("key-press", "pregunta", 0.35 + i * 0.038, 0.30 if i % 2 else 0.38, {}) for i in range(0, 40, 3)] + [
    ("click", "pregunta", 1.94, 0.42, {}),
    ("pop", "pregunta", 2.97, 0.32, {}),
    ("impact-bass-1", "pregunta", 3.7, 0.58, {"dur": 1.3}),
    ("pop", "pregunta", 4.65, 0.22, {}),
    # contexto: cada casillero cae (golpe), se agrieta (vidrio) y se rompe al final
] + [("impact-bass-1", "contexto", t + 0.36, 0.24, {"dur": 0.6}) for t in (0.45, 2.3, 3.95, 5.75)] + [
    ("crack-a", "contexto", t + 0.62, 0.42, {}) for t in (0.45, 2.3, 3.95, 5.75)] + [
    ("pop", "contexto", t + 0.7, 0.18, {}) for t in (0.45, 2.3, 3.95, 5.75)] + [
    ("crack-b", "contexto", 7.6, 0.45, {"dur": 1.6}),
    ("impact-bass-1", "contexto", 7.95, 0.55, {"dur": 1.2}),
    ("swoosh-a", "contexto", 9.05, 0.36, {}),
    ("sparkle", "contexto", 9.2, 0.28, {}),
    ("whoosh-cinematic", "contexto", 10.0, 0.40, {"dur": 3.0}),
    # revelación: las mitades vuelven, clic por cable, tecla por cada ✓
    ("sparkle", "revelacion", 0.45, 0.30, {}),
    ("swoosh-b", "revelacion", 0.75, 0.22, {}),
] + [("click", "revelacion", t + 0.26, 0.42, {}) for t in (1.55, 1.95, 2.35, 2.75)] + [
    ("key-press", "revelacion", t + 0.3, 0.48, {}) for t in (1.55, 1.95, 2.35, 2.75)] + [
    ("impact-bass-2", "revelacion", 3.4, 0.36, {}),
    ("sparkle", "revelacion", 3.42, 0.24, {}),
    # respuesta: tecleo, enviar, ráfaga de ✓, golpes cortos en cada dato, remate
] + [("key-press", "respuesta", 0.3 + i * 0.028, 0.28 if i % 2 else 0.36, {}) for i in range(0, 40, 4)] + [
    ("click", "respuesta", 1.45, 0.42, {}),
] + [("key-press", "respuesta", t + 0.18, 0.46, {}) for t in (1.68, 1.8, 1.92, 2.04)] + [
    ("swoosh-b", "respuesta", 2.3, 0.20, {}),
    ("impact-bass-1", "respuesta", 3.65, 0.48, {"dur": 1.0}),
    ("pop", "respuesta", 3.8, 0.26, {}),
    ("impact-bass-1", "respuesta", 4.35, 0.34, {"dur": 0.8}),
    ("sparkle", "respuesta", 4.65, 0.22, {}),
] + [("pop", "respuesta", 4.9 + i * 0.14, 0.14, {}) for i in range(6)] + [
    ("impact-bass-1", "respuesta", 5.75, 0.28, {"dur": 0.7}),
] + [("pop", "respuesta", 6.5 + i * 0.14, 0.13, {}) for i in range(5)] + [
    ("click", "respuesta", 7.1, 0.28, {}),
    ("ping", "respuesta", 7.32, 0.26, {}),
] + [("pop", "respuesta", 8.0 + i * 0.16, 0.18, {}) for i in range(3)] + [
    ("impact-bass-1", "respuesta", 8.65, 0.28, {"dur": 0.7}),
] + [("click", "respuesta", 9.35 + i * 0.12, 0.22, {}) for i in range(4)] + [
    ("impact-bass-2", "respuesta", 11.0, 0.48, {}),
    ("impact-bass-1", "respuesta", 11.0, 0.30, {"dur": 1.2}),
    # informe real: tapa, se abre la ventana, scroll, cartel
    ("swoosh-b", "real", 0.25, 0.24, {}),
    ("swoosh-c", "real", 1.6, 0.30, {}),
    ("typing", "real", 2.3, 0.18, {"dur": 1.4}),
    ("ping", "real", 8.6, 0.30, {}),
    ("impact-bass-1", "real", 9.2, 0.55, {"dur": 1.2}),
    ("pop", "real", 10.35, 0.32, {}),
    # comenta: F-I-N-A-N-Z-A-S, enviar, corazón, llega el mensaje, el código
] + [("key-press", "comenta", 1.31 + i * 0.09, 0.50 if i % 2 == 0 else 0.42, {}) for i in range(8)] + [
    ("click", "comenta", 2.57, 0.48, {}),
    ("pop", "comenta", 2.97, 0.30, {}),
    ("notification", "comenta", 3.4, 0.34, {}),
    ("pop", "comenta", 3.9, 0.30, {}),
    ("click", "comenta", 4.6, 0.30, {}),
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
    k = 0
    for i in range(1, len(SCENES)):
        if SCENES[i][0] in NOWHIP:
            continue
        f = WHOOSHES[k % len(WHOOSHES)]
        k += 1
        cues.append((f, SCENES[i][1] + WHIP / 2, WHOOSH_VOL[f], {}))   # pico en el cuadro más rápido del latigazo
    for f, sc, t, v, x in SFX:
        cues.append((f, start[sc] + t, v, x))
    tags, ends = [], []  # ends[k] = segundo en que se libera la pista 30+k
    for n, (f, t, v, x) in enumerate(sorted(cues, key=lambda c: c[1])):
        skip = x.get("skip", 0)  # segundos recortados del inicio del archivo
        st = round(max(0.0, t - (PEAK[f] - skip) + 1 / 30), 3)
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
    if i + 1 < len(SCENES):
        nxt = SCENES[i + 1][1] + (0 if SCENES[i + 1][0] in NOWHIP else 0.34)
    else:
        nxt = END
    dur = round(nxt - st, 2)
    hosts.append(
        f'      <div id="{sid}" class="scene" data-composition-id="{sid}" data-composition-src="compositions/{sid}.html"\n'
        f'        data-start="{st}" data-duration="{dur}" data-track-index="{i + 1}" data-track-kind="graphics" data-width="1080" data-height="1920"></div>'
    )
    z.append(f"#{sid} {{ z-index: {len(SCENES) - i}; }}")
sets = "\n".join(f'      tl.set("#{s}", {{ y: 1920 }}, 0);' for s, _ in SCENES[1:] if s not in NOWHIP)
whips = "\n".join(f'      whip("#{SCENES[i][0]}", "#{SCENES[i + 1][0]}", {SCENES[i + 1][1]});' for i in range(len(SCENES) - 1) if SCENES[i + 1][0] not in NOWHIP)

SFX_TAGS, N_SFX = sfx_tags()
html = f"""<!doctype html>
<html lang="es" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="assets/gsap.min.js"></script>
    <link rel="stylesheet" href="assets/brand.css" />
    <script src="assets/brand.js"></script>
    <script src="assets/ctx.js"></script>
    <script src="assets/ai-logos.js"></script>
    <script src="assets/warren-doc.js"></script>
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
