"""Arma index.html a partir de la lista de escenas (id, segundo en que entra).

Para resincronizar con la voz: cambiar los segundos de SCENES (y END) y correr
    python -I build_index.py
Cada escena dura hasta que entra la siguiente + 0,34 s (el solape de la transición).
"""
import pathlib

SCENES = [
    ("gancho", 0),
    ("contexto", 5.0),
    ("revelacion", 12.8),   # entra sin latigazo: el botón de Warren crece y se vuelve el fondo
    ("respuesta", 18.4),
    ("contraste", 44.0),
    ("informes", 50.0),
    ("comenta", 57.8),
    ("logo", 65.9),
]
END = 69.4
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
    # gancho: aparece la respuesta de dos líneas de golpe; "¿Eso es todo?" cae seco
    ("click", "gancho", 1.95, 0.25, {}),
    ("typing", "gancho", 2.75, 0.30, {"skip": 0.44, "dur": 0.6}),
    ("pop", "gancho", 3.42, 0.30, {}),
    ("impact-bass-1", "gancho", 3.94, 0.62, {"dur": 1.3}),
    # contexto: el chat se encoge, caen los cuatro casilleros con su ✗, entra el botón dorado y crece
    ("swoosh-b", "contexto", 1.55, 0.20, {}),
] + [("impact-bass-1", "contexto", t + 0.36, 0.20, {"dur": 0.5}) for t in (2.85, 3.95, 5.05, 6.1)] + [
    ("pop", "contexto", t + 0.55, 0.26, {}) for t in (2.85, 3.95, 5.05, 6.1)] + [
    ("swoosh-a", "contexto", 6.85, 0.36, {}),
    ("sparkle", "contexto", 7.0, 0.30, {}),
    ("whoosh-cinematic", "contexto", 7.8, 0.40, {"dur": 3.0}),
    # revelación: avatar, casilleros que llegan, cada cable que se enchufa (clic) y cada ✓ (tecla)
    ("sparkle", "revelacion", 0.5, 0.30, {}),
    ("swoosh-b", "revelacion", 1.15, 0.20, {}),
] + [("click", "revelacion", t + 0.28, 0.42, {}) for t in (2.9, 3.3, 3.7, 4.1)] + [
    ("key-press", "revelacion", t + 0.32, 0.48, {}) for t in (2.9, 3.3, 3.7, 4.1)] + [
    ("impact-bass-2", "revelacion", 4.75, 0.36, {}),
    ("sparkle", "revelacion", 4.77, 0.24, {}),
    # respuesta: tecleo de la pregunta, enviar, cada ✓ de lo que leyó, golpes en el valor justo y el remate
] + [("key-press", "respuesta", 0.45 + i * 0.045, 0.30 if i % 2 else 0.38, {}) for i in range(0, 40, 3)] + [
    ("click", "respuesta", 2.32, 0.45, {}),
    ("pop", "respuesta", 2.5, 0.24, {}),
] + [("key-press", "respuesta", t + 0.22, 0.50, {}) for t in (2.9, 3.25, 3.6, 3.95)] + [
    ("swoosh-b", "respuesta", 4.3, 0.20, {}),
    ("impact-bass-1", "respuesta", 6.42, 0.52, {"dur": 1.2}),
    ("pop", "respuesta", 7.2, 0.22, {}),
    ("pop", "respuesta", 7.35, 0.30, {}),
] + [("swoosh-b", "respuesta", t + 0.3, 0.13, {}) for t in (7.9, 11.0, 14.6, 17.8, 20.4)] + [
    ("pop", "respuesta", 8.55, 0.20, {}),
    ("pop", "respuesta", 8.9, 0.20, {}),
    ("impact-bass-1", "respuesta", 9.45, 0.40, {"dur": 1.0}),
    ("sparkle", "respuesta", 10.25, 0.24, {}),
] + [("pop", "respuesta", 11.65 + i * 0.36, 0.16, {}) for i in range(6)] + [
    ("impact-bass-1", "respuesta", 13.55, 0.28, {"dur": 0.8}),
] + [("pop", "respuesta", 15.35 + i * 0.3, 0.14, {}) for i in range(5)] + [
    ("click", "respuesta", 16.9, 0.30, {}),
    ("ping", "respuesta", 17.2, 0.28, {}),
] + [("pop", "respuesta", 18.45 + i * 0.4, 0.20, {}) for i in range(3)] + [
    ("impact-bass-1", "respuesta", 19.75, 0.28, {"dur": 0.8}),
] + [("click", "respuesta", 21.0 + i * 0.3, 0.24, {}) for i in range(4)] + [
    ("impact-bass-2", "respuesta", 22.76, 0.48, {}),
    ("impact-bass-1", "respuesta", 22.76, 0.30, {"dur": 1.2}),
    # contraste: entran las dos ventanas, el "vs" y el contador de palabras
    ("swoosh-b", "contraste", 0.3, 0.20, {}),
    ("pop", "contraste", 0.85, 0.24, {}),
    ("swoosh-b", "contraste", 1.65, 0.20, {}),
    ("pop", "contraste", 1.95, 0.30, {}),
    ("ping", "contraste", 3.3, 0.30, {}),
    # informes: lluvia de lomos, "casi 50" con golpe, el de GOOGL pasa al atril
] + [("impact-bass-1", "informes", 0.89 + i * 0.05, 0.13 + 0.04 * (i % 2), {"dur": 0.4}) for i in range(0, 49, 6)] + [
    ("impact-bass-1", "informes", 3.4, 0.50, {"dur": 1.2}),
    ("click", "informes", 4.35, 0.30, {}),
    ("swoosh-c", "informes", 5.0, 0.28, {}),
    ("sparkle", "informes", 5.1, 0.24, {}),
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
