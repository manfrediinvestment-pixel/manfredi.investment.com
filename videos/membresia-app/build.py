"""Video "Manfredi Pro en la app" — v2 (1920x1080, se renderiza en 4K a 60 fps).

Un celular realista en el centro recorre Manfredi Pro con datos REALES de los informes publicados:
  intro → Informes (tocás Apple, el celular gira y se ve el informe ORIGINAL como en la compu)
  → Warren IA compara Apple vs Microsoft (respuesta larga) → se pide un informe de Boeing → cierre.
A los costados, simétricos: izquierda = la sección, derecha = lo que podés hacer (íconos).
El fondo (aurora que se mueve + polvo dorado) es UNA composición para todo el video: los cortes no se notan.

    python -I build.py      -> index.html + compositions/*.html
Render 4K:  npx hyperframes render --resolution landscape-4k --fps 60 --quality high -o output/...
"""
import pathlib
import random

ROOT = pathlib.Path(__file__).parent
MP_PATH = (ROOT / "assets" / "mppath.txt").read_text(encoding="utf-8").strip()  # ícono de Mercado Pago (Simple Icons)

# (id, segundo de entrada). Cortes secos: en el cuadro del corte el celular está idéntico en las dos escenas.
SCENES = [("intro", 0), ("informes", 4.6), ("warren", 18.6), ("pedido", 36.6), ("cierre", 47.2)]
END = 54.2

SW, SH = 374, 814                                     # pantalla del celular (px CSS)
TAB_IC = {
    "Informes": '<path d="M7 3h7l5 5v13H7z"/><path d="M14 3v5h5"/><path d="M10 13h6M10 17h6"/>',
    "Warren IA": '<path d="M4 5h16v11H10l-6 4z"/><path d="M9 10.5h6"/>',
    "Pedidos": '<circle cx="12" cy="12" r="9"/><path d="M12 8v8M8 12h8"/>',
}
TAB_X = lambda i: round(i * 116.67 + 4.33, 2)         # left de la pastilla activa
TAB_CX = lambda i: round(12 + i * 116.67 + 58.33, 1)  # centro de cada pestaña
TAB_CY = SH - 30 - 37

ICON = {  # íconos de línea (24x24) para "lo que podés hacer"
    "doc": '<path d="M7 3h7l5 5v13H7z"/><path d="M14 3v5h5"/><path d="M10 13h6M10 17h6"/>',
    "target": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.4"/>',
    "chart": '<path d="M4 20V11M10 20V5M16 20v-6M3 20h18"/>',
    "shield": '<path d="M12 3l7 3v6c0 4.5-3 7.6-7 9-4-1.4-7-4.5-7-9V6z"/><path d="M9 12l2 2 4-4"/>',
    "compare": '<path d="M5 8h13l-3-3"/><path d="M19 16H6l3 3"/>',
    "tag": '<path d="M3 12l9-9h8v8l-9 9z"/><circle cx="16" cy="8" r="1.5"/>',
    "alert": '<path d="M12 3l10 18H2z"/><path d="M12 10v5M12 18v.4"/>',
    "pie": '<path d="M12 3v9h9"/><path d="M21 12a9 9 0 1 1-9-9"/>',
    "search": '<circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/>',
    "plus": '<circle cx="12" cy="12" r="9"/><path d="M12 8v8M8 12h8"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2.5"/><path d="M3.5 7l8.5 6 8.5-6"/>',
}
GDEF = ('<svg width="0" height="0" style="position:absolute"><defs><linearGradient id="gg" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0" stop-color="#fbecc4"/><stop offset=".55" stop-color="#f2c94c"/><stop offset="1" stop-color="#c99a2e"/></linearGradient></defs></svg>')


def fmt_ar(v, dec):
    s = f"{v:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def phone(inner, tab, pid, chrome=True, extra=""):
    tabs = "".join(
        f'<div class="tab" id="{pid}-t{i}" style="color:{"#f2c94c" if i == tab else "#ead9a4"}"><svg viewBox="0 0 24 24">{TAB_IC[n]}</svg>{n}</div>'
        for i, n in enumerate(TAB_IC))
    ch = f'''
          <div class="ahead" id="{pid}-head"><div class="brand"><img src="assets/img/emblem.svg" alt="">Manfredi <em>Investment</em></div><div class="av">IM</div></div>
          <div class="view" id="{pid}-view">{inner}</div>
          <div class="tabs" id="{pid}-tabs"><div class="pill" id="{pid}-pill" style="left:{TAB_X(0)}px"></div>{tabs}</div>''' if chrome else inner
    return f'''
      <div class="cshadow" id="{pid}-cs"></div>
      <div class="pw">
      <div class="phone" id="{pid}-phone">
        <i class="pbtn a"></i><i class="pbtn v1"></i><i class="pbtn v2"></i><i class="pbtn p"></i>
        <div class="bezel"></div>
        <div class="screen" id="{pid}-screen">
          <div class="app"></div>{ch}
          <div class="sbar" id="{pid}-sbar"><span>9:41</span><span class="ic"><b style="height:5px"></b><b style="height:8px"></b><b style="height:11px"></b><b style="height:14px"></b><span class="bat"></span></span></div>
          <div class="island"></div>
          <div class="homeind" id="{pid}-home"></div>
          <div class="touch" id="{pid}-touch"></div>{extra}
        </div>
        <div class="glare"><i id="{pid}-glare"></i></div>
      </div>
      </div>'''


def side_l(pid, kick, l1, l2, desc):
    return f'''
      <div class="side side-l" id="{pid}-sl">
        <div class="kick" id="{pid}-k">{kick}<i></i></div>
        <div class="ttl"><span class="ln" id="{pid}-l1">{l1}</span><span class="ln" id="{pid}-l2"><em>{l2}</em></span></div>
        <div class="rule" id="{pid}-rl"></div>
        <div class="desc" id="{pid}-ds">{desc}</div>
      </div>'''


def side_r(pid, acts, kick="Lo que podés hacer"):
    lis = "".join(f'''
          <li class="act" id="{pid}-a{i}"><span class="tile" id="{pid}-ti{i}"><svg viewBox="0 0 24 24">{ICON[ic]}</svg></span>
            <div><div class="t" id="{pid}-at{i}">{t}</div><div class="s" id="{pid}-as{i}">{s}</div></div></li>''' for i, (ic, t, s) in enumerate(acts))
    return f'''
      <div class="side side-r" id="{pid}-sr">
        <div class="kick" id="{pid}-kr"><i></i>{kick}</div>
        <ul class="acts">{lis}
        </ul>
      </div>'''


COMMON_JS = r'''
      function sidesIn(t0) {
        tl.fromTo("#@@-k", { opacity: 0, x: -40 }, { opacity: 1, x: 0, duration: 0.6, ease: "expo.out" }, t0);
        tl.fromTo(["#@@-l1", "#@@-l2"], { opacity: 0, yPercent: 60, filter: "blur(16px)" },
          { opacity: 1, yPercent: 0, filter: "blur(0px)", duration: 0.75, ease: "expo.out", stagger: 0.09 }, t0 + 0.05);
        tl.fromTo("#@@-rl", { scaleX: 0 }, { scaleX: 1, duration: 0.8, ease: "expo.inOut" }, t0 + 0.25);
        tl.fromTo("#@@-ds", { opacity: 0, y: 24 }, { opacity: 1, y: 0, duration: 0.6, ease: "expo.out" }, t0 + 0.4);
        tl.fromTo("#@@-kr", { opacity: 0, x: 40 }, { opacity: 1, x: 0, duration: 0.6, ease: "expo.out" }, t0 + 0.1);
      }
      function actsIn(t0, step) {
        R.querySelectorAll("#@@-sr .act").forEach((li, i) => {
          const t = t0 + i * step;
          tl.fromTo(li.querySelector(".tile"), { opacity: 0, scale: 0.4, rotation: -14 }, { opacity: 1, scale: 1, rotation: 0, duration: 0.7, ease: "back.out(2.2)" }, t);
          tl.fromTo(li.querySelector(".t"), { opacity: 0, x: 46, filter: "blur(8px)" }, { opacity: 1, x: 0, filter: "blur(0px)", duration: 0.6, ease: "expo.out" }, t + 0.08);
          tl.fromTo(li.querySelector(".s"), { opacity: 0, x: 30 }, { opacity: 1, x: 0, duration: 0.6, ease: "expo.out" }, t + 0.16);
        });
      }
      function sidesOut(t) {
        tl.to(["#@@-sl", "#@@-sr"], { y: -170, opacity: 0, filter: "blur(18px)", duration: 0.32, ease: "power3.in" }, t);
      }
      function pageIn(sel, t) { tl.fromTo(sel, { x: 374 }, { x: 0, duration: 0.65, ease: "expo.out" }, t); }
      function pageOut(sel, t) { tl.to(sel, { x: -374, opacity: 0.2, duration: 0.3, ease: "power3.in" }, t); }
      function tap(x, y, t) {
        const el = "#@@-touch";
        tl.set(el, { x: x, y: y }, t - 0.3);
        tl.fromTo(el, { opacity: 0, scale: 1.5 }, { opacity: 1, scale: 1, duration: 0.22, ease: "power2.out", immediateRender: false }, t - 0.26);
        tl.to(el, { scale: 0.78, duration: 0.08, ease: "power2.in" }, t - 0.04);
        tl.to(el, { scale: 1.4, opacity: 0, duration: 0.34, ease: "power2.out" }, t + 0.05);
      }
      function at(sel) {  // centro de un elemento en coordenadas de la pantalla (sin transforms)
        let el = R.querySelector(sel), x = el.offsetWidth / 2, y = el.offsetHeight / 2;
        const scr = R.querySelector("#@@-screen");
        while (el && el !== scr) { x += el.offsetLeft; y += el.offsetTop; el = el.offsetParent; }
        return [x, y];
      }
      const pillEl = R.querySelector("#@@-pill");
      if (pillEl) tl.set(pillEl, { x: TABX[TAB0] - TABX[0] }, 0);
      function tabTo(i, t) {
        tl.to("#@@-pill", { x: TABX[i] - TABX[0], duration: 0.45, ease: "back.out(1.6)" }, t);
        R.querySelectorAll("#@@-tabs .tab").forEach((tb, k) => tl.to(tb, { color: k === i ? "#f2c94c" : "#ead9a4", duration: 0.2, ease: "none" }, t + 0.05));
      }
      function drift(deg, from, to) {  // giro 3D suave que vuelve a 0 (el corte con la escena siguiente no se nota)
        const a = from || 0, b = to || DUR, h = (b - a) / 2;
        tl.fromTo("#@@-phone", { rotationY: 0, y: 0 }, { rotationY: deg, y: -12, duration: h, ease: "sine.inOut", transformPerspective: 2200 }, a);
        tl.to("#@@-phone", { rotationY: 0, y: 0, duration: h, ease: "sine.inOut" }, a + h);
        tl.fromTo("#@@-glare", { x: 0 }, { x: deg > 0 ? 300 : 140, duration: h, ease: "sine.inOut" }, a);
        tl.to("#@@-glare", { x: 0, duration: h, ease: "sine.inOut" }, a + h);
      }
'''


def scene(sid, dur, body, js, css="", tab0=0):
    return f'''<template id="{sid}-template">
  <div id="root" data-composition-id="{sid}" data-start="0" data-duration="{dur}" data-width="1920" data-height="1080">
    <style>
      #root {{ position: relative; width: 1920px; height: 1080px; overflow: hidden; }}
      {css}
    </style>
    {GDEF}
    <div class="halo"></div>
{body}
    <script>
      (function () {{
      const R = document.querySelector('[data-composition-id="{sid}"]');
      const tl = gsap.timeline({{ paused: true }});
      const TAB0 = {tab0};
      const DUR = {dur};
      const TABX = [{TAB_X(0)}, {TAB_X(1)}, {TAB_X(2)}];
{COMMON_JS.replace('@@', sid)}
{js}
      window.__timelines["{sid}"] = tl;
      }})();
    </script>
  </div>
</template>
'''


def dur_of(sid):
    i = [s for s, _ in SCENES].index(sid)
    return round((SCENES[i + 1][1] if i + 1 < len(SCENES) else END) - SCENES[i][1], 2)


# ═════════════════════════════════ FONDO (todo el video) ═════════════════════════════════
random.seed(7)
dust = []
for i in range(46):
    x, y, r = random.uniform(40, 1880), random.uniform(40, 1040), random.choice([1.6, 2, 2.4, 3, 3.6])
    o = random.uniform(.18, .55)
    dust.append((i, x, y, r, o, random.uniform(-70, -150), random.uniform(-30, 30), random.uniform(1.6, 3.4)))
dust_html = "".join(f'<i class="dust" id="fondo-d{i}" style="left:{x:.0f}px;top:{y:.0f}px;width:{r}px;height:{r}px;opacity:{o:.2f};box-shadow:0 0 {r * 4:.0f}px rgba(247,220,138,.6)"></i>'
                    for i, x, y, r, o, *_ in dust)
fondo_body = f'''
    <div class="f-base"></div>
    <div class="blob b1" id="fondo-b1"></div><div class="blob b2" id="fondo-b2"></div><div class="blob b3" id="fondo-b3"></div>
    <div class="f-grid"></div>
    {dust_html}
    <div class="f-vig"></div><div class="f-grain"></div>'''
fondo_js = '''
      tl.fromTo("#fondo-b1", { x: 0, y: 0, scale: 1 }, { x: 260, y: 140, scale: 1.15, duration: DUR, ease: "sine.inOut" }, 0);
      tl.fromTo("#fondo-b2", { x: 0, y: 0, scale: 1 }, { x: -300, y: 180, scale: 0.92, duration: DUR, ease: "sine.inOut" }, 0);
      tl.fromTo("#fondo-b3", { x: 0, y: 0, scale: 1 }, { x: 220, y: -120, scale: 1.12, duration: DUR, ease: "sine.inOut" }, 0);
''' + "".join(f'      tl.fromTo("#fondo-d{i}", {{ x: 0, y: 0 }}, {{ x: {dx:.0f}, y: {dy:.0f}, duration: DUR, ease: "none" }}, 0);\n'
              f'      tl.fromTo("#fondo-d{i}", {{ scale: 1 }}, {{ scale: 0.4, duration: {p:.2f}, ease: "sine.inOut", yoyo: true, repeat: {int(END / p)} }}, {i * 0.07:.2f});\n'
              for i, x, y, r, o, dy, dx, p in dust)


def fondo_scene():
    return f'''<template id="fondo-template">
  <div id="root" data-composition-id="fondo" data-start="0" data-duration="{END}" data-width="1920" data-height="1080">
    <style>#root {{ position: relative; width: 1920px; height: 1080px; overflow: hidden; }}</style>
{fondo_body}
    <script>
      (function () {{
      const tl = gsap.timeline({{ paused: true }});
      const DUR = {END};
{fondo_js}
      window.__timelines["fondo"] = tl;
      }})();
    </script>
  </div>
</template>
'''


# ═════════════════════════════════ INTRO ═════════════════════════════════
intro_screen = f'''
          <div id="intro-home" style="position:absolute;inset:0;background:
            radial-gradient(70% 40% at 30% 18%, rgba(242,201,76,.24), transparent 70%),
            radial-gradient(80% 50% at 90% 70%, rgba(64,128,232,.38), transparent 70%),
            linear-gradient(180deg,#14305a,#0a1630 60%,#071022);">
            <div style="position:absolute;top:118px;width:100%;text-align:center;font:400 100px/1 'DM Serif';color:#f6f8fc;letter-spacing:-.02em">9:41</div>
            <div style="position:absolute;top:228px;width:100%;text-align:center;font:500 17px/1 'Instrument';color:#ead9a4">Martes 3 de noviembre</div>
            <div id="intro-icon" style="position:absolute;left:148px;top:520px;width:78px;height:78px;border-radius:20px;overflow:hidden;
              background:linear-gradient(160deg,#18305c,#0a1430);box-shadow:inset 0 0 0 1px rgba(242,201,76,.4),0 18px 40px -12px rgba(0,0,0,.7);
              display:flex;align-items:center;justify-content:center"><img src="assets/img/emblem.svg" style="width:58px;height:58px" alt=""></div>
            <div style="position:absolute;top:610px;width:100%;text-align:center;font:500 14px/1 'Instrument';color:#f6f8fc">Manfredi</div>
          </div>
          <div id="intro-launch" style="position:absolute;left:148px;top:520px;width:78px;height:78px;border-radius:20px;opacity:0;
            background:linear-gradient(180deg,#0d1c37,#091428 60%,#070f1e)"></div>
          <div id="intro-splash" style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:18px;opacity:0">
            <img src="assets/img/emblem.svg" style="width:116px;height:116px" alt="">
            <div style="font:400 31px/1 'DM Serif';color:#f6f8fc">Manfredi <em style="font-family:'Newsreader';color:#f7dc8a">Investment</em></div>
          </div>
          <div id="intro-chrome" style="position:absolute;inset:0;opacity:0">
            <div class="ahead"><div class="brand"><img src="assets/img/emblem.svg" alt="">Manfredi <em>Investment</em></div><div class="av">IM</div></div>
            <div class="tabs" id="intro-tabs"><div class="pill" style="left:{TAB_X(0)}px"></div>''' + "".join(
    f'<div class="tab" style="color:{"#f2c94c" if i == 0 else "#ead9a4"}"><svg viewBox="0 0 24 24">{TAB_IC[n]}</svg>{n}</div>' for i, n in enumerate(TAB_IC)) + '''</div>
          </div>'''

intro_body = phone(intro_screen, 0, "intro", chrome=False) + '''
      <div class="side side-l" id="intro-sl">
        <div class="kick" id="intro-k">Membresía<i></i></div>
        <div class="ttl"><span class="ln" id="intro-l1">Manfredi</span><span class="ln" id="intro-l2"><em>Pro.</em></span></div>
      </div>
      <div class="side side-r" id="intro-sr">
        <div class="kick" id="intro-kr"><i></i>Todo en tu celular</div>
        <div class="ttl" style="font-size:96px"><span class="ln" id="intro-r1">Todo el análisis,</span><span class="ln" id="intro-r2"><em>en tu bolsillo.</em></span></div>
      </div>'''

intro_js = '''
      // cuadro 0 = portada nítida; se asienta enseguida
      tl.fromTo("#intro-phone", { y: 70, rotationX: 16, scale: 0.95 }, { y: 0, rotationX: 0, scale: 1, duration: 1.2, ease: "expo.out", transformPerspective: 1800 }, 0);
      tl.fromTo(["#intro-k", "#intro-l1", "#intro-l2"], { y: 18 }, { y: 0, duration: 1.0, ease: "expo.out", stagger: 0.08 }, 0);
      tl.fromTo(["#intro-kr", "#intro-r1", "#intro-r2"], { y: 18 }, { y: 0, duration: 1.0, ease: "expo.out", stagger: 0.08 }, 0);
      tl.fromTo("#intro-glare", { x: 0 }, { x: 260, duration: 2.2, ease: "sine.inOut" }, 0);
      tl.fromTo("#intro-icon", { scale: 1 }, { scale: 1.08, duration: 0.5, ease: "sine.inOut", yoyo: true, repeat: 1 }, 0.4);
      tap(187, 559, 1.5);
      tl.to("#intro-icon", { scale: 0.86, duration: 0.08, ease: "power2.in" }, 1.46);
      tl.set("#intro-launch", { opacity: 1 }, 1.58);
      tl.fromTo("#intro-launch", { scale: 1, borderRadius: 20 }, { scale: 13, borderRadius: 4, duration: 0.5, ease: "expo.inOut" }, 1.58);
      tl.fromTo("#intro-splash", { opacity: 0, scale: 0.85 }, { opacity: 1, scale: 1, duration: 0.45, ease: "expo.out" }, 1.98);
      tl.to("#intro-splash", { opacity: 0, scale: 1.06, filter: "blur(8px)", duration: 0.35, ease: "power2.in" }, 2.85);
      tl.to("#intro-chrome", { opacity: 1, duration: 0.3, ease: "power2.out" }, 3.05);
      tl.fromTo("#intro-tabs", { y: 120 }, { y: 0, duration: 0.6, ease: "expo.out" }, 3.05);
      tl.to("#intro-glare", { x: 0, duration: 1.4, ease: "sine.inOut" }, 2.6);
      sidesOut(3.95);
'''

# ═════════════════════════════════ INFORMES ═════════════════════════════════
# biblioteca en vertical → tocás Apple → el celular gira y muestra el informe ORIGINAL (captura real de
# informes/aapl.html a 1080 px de ancho, x3): tapa + segmentos + síntesis de valuación.
COVERS = [("aapl", "AAPL", "Apple", "Tecnología", "#6ea0ff"), ("msft", "MSFT", "Microsoft", "Tecnología", "#6ea0ff"),
          ("nvda", "NVDA", "NVIDIA", "Semiconductores", "#a98bd6"), ("googl", "GOOGL", "Alphabet", "Tecnología", "#6ea0ff"),
          ("mu", "MU", "Micron", "Semiconductores", "#a98bd6"), ("jpm", "JPM", "JPMorgan", "Bancos", "#10B981")]
covers_html = "".join(f'''
                <div class="cov" id="informes-cv{i}">
                  <div class="row"><img src="assets/img/mono-{f}.png" alt=""><span class="no">N° {i + 1:02d}</span></div>
                  <div class="tk">{t}</div><div class="nm">{n}</div>
                  <div class="sec"><i style="background:{c}"></i>{sct}</div>
                </div>''' for i, (f, t, n, sct, c) in enumerate(COVERS))

LW, LH = SH, SW                       # pantalla en horizontal: 814 x 374
BAR = 40                              # barra de la app arriba del informe
IMG_W, IMG_H = 3240, 9780             # captura x3 del informe (1080 px CSS de ancho)
K = LW / (IMG_W / 3)                  # escala del informe dentro del celular
IMG_SH = IMG_H / IMG_W * LW           # alto de la imagen en px de pantalla
VIS = LH - BAR
REP = lambda y_css: -round(min(y_css * K, IMG_SH - VIS), 1)   # scroll a una altura del informe (px CSS del informe)

informes_page = f'''
            <div class="pg" id="informes-lib">
              <h4>Informes <em>Pro</em></h4>
              <div class="sub">+50 informes de distintos sectores y regiones</div>
              <div class="srch"><svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/></svg>Buscar empresa o ticker…</div>
              <div class="covs">{covers_html}
              </div>
            </div>'''
informes_land = f'''
          <div id="informes-land">
            <div class="lbar"><span class="lb-back">‹ Informes</span><span class="lb-t">Apple Inc. <em>· Informe institucional</em></span><span class="lb-tk">AAPL</span></div>
            <div class="lview"><img id="informes-doc" src="assets/img/aapl-informe.jpg" alt=""><i class="lscroll" id="informes-sc"></i></div>
          </div>'''

informes_css = f'''
      .srch {{ display:flex; align-items:center; gap:8px; height:38px; border-radius:12px; padding:0 12px; margin-bottom:12px; box-shadow:inset 0 0 0 1px rgba(226,234,245,.16);
        background:rgba(255,255,255,.04); font:500 13px/1 "Instrument"; color:#ead9a4; }}
      .srch svg {{ width:16px; height:16px; fill:none; stroke:#ead9a4; stroke-width:2; }}
      .covs {{ display:grid; grid-template-columns:1fr 1fr; gap:10px; }}
      .cov {{ height:128px; border-radius:15px; padding:12px; display:flex; flex-direction:column; box-shadow:inset 0 0 0 1px rgba(226,234,245,.15), 0 14px 26px -16px rgba(0,0,0,.8);
        background:radial-gradient(90% 70% at 100% 0%, rgba(242,201,76,.12), transparent 60%), linear-gradient(160deg,#18305c,#0a1430); }}
      .cov img {{ height:26px; width:auto; max-width:70px; object-fit:contain; }}
      .cov .no {{ font:600 9.5px/1 "Plex Mono"; color:#ead9a4; letter-spacing:.08em; }}
      .cov .tk {{ margin-top:auto; font:700 11px/1 "Plex Mono"; color:#f7dc8a; letter-spacing:.1em; }}
      .cov .nm {{ font:400 21px/1.1 "DM Serif"; color:#f6f8fc; margin-top:3px; }}
      .cov .sec {{ display:flex; align-items:center; gap:6px; margin-top:6px; font:600 10px/1 "Instrument"; color:#ead9a4; }}
      .cov .sec i {{ width:7px; height:7px; border-radius:50%; display:block; }}
      #informes-land {{ position:absolute; left:{(SW - LW) / 2}px; top:{(SH - LH) / 2}px; width:{LW}px; height:{LH}px; transform:rotate(90deg); z-index:20; overflow:hidden; background:#fff; }}
      .lbar {{ position:absolute; left:0; right:0; top:0; height:{BAR}px; display:flex; align-items:center; justify-content:space-between; padding:0 22px 0 58px;
        background:linear-gradient(180deg,#0f2142,#0a1730); font:600 12.5px/1 "Instrument"; color:#f6f8fc; z-index:2; }}
      .lb-back {{ color:#f2c94c; }} .lb-t em {{ font-family:"Newsreader"; font-style:italic; font-weight:400; color:#ead9a4; font-size:13.5px; }}
      .lb-tk {{ font:700 10.5px/1 "Plex Mono"; letter-spacing:.1em; color:#0a1322; background:#f2c94c; padding:5px 8px; border-radius:6px; }}
      .lview {{ position:absolute; left:0; right:0; top:{BAR}px; bottom:0; overflow:hidden; background:#fff; }}
      #informes-doc {{ position:absolute; left:0; top:0; width:{LW}px; height:auto; display:block; }}
      .lscroll {{ position:absolute; right:3px; top:4px; width:4px; height:46px; border-radius:2px; background:rgba(10,19,34,.35); }}
'''

informes_body = phone(informes_page, 0, "informes", extra=informes_land) + side_l(
    "informes", "<b>01</b> · Informes", "Informes", "a fondo.", "+50 informes de distintos sectores y regiones.") + side_r(
    "informes", [("doc", "Leer el informe completo", "14 secciones, como un analista"), ("target", "Ver el fair value", "4 métodos, un solo número"),
                 ("chart", "Entender los números", "Datos oficiales de la SEC"), ("shield", "Conocer los riesgos", "Y los catalizadores que vienen")])

ROT = 1.82   # escala del celular en horizontal
STOPS = [(4.6, 430, 1.2), (6.2, 1060, 1.1), (7.6, 1500, 0.8), (8.8, 2010, 0.9), (10.0, 2470, 0.9), (11.2, 2820, 0.8)]
scroll_js = "".join(f'      tl.to("#informes-doc", {{ y: {REP(y)}, duration: {d}, ease: "power2.inOut" }}, {t});\n'
                    f'      tl.to("#informes-sc", {{ y: {round(min(1, y * K / (IMG_SH - VIS)) * (VIS - 54), 1)}, duration: {d}, ease: "power2.inOut" }}, {t});\n'
                    for t, y, d in STOPS)
informes_js = f'''
      pageIn("#informes-lib", 0.02);
      sidesIn(0.1);
      actsIn(0.55, 0.32);
      tl.set("#informes-land", {{ opacity: 0 }}, 0);
      for (let i = 0; i < 6; i++) tl.fromTo("#informes-cv" + i, {{ opacity: 0, y: 30, scale: 0.94 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.5, ease: "expo.out" }}, 0.35 + i * 0.08);
      tl.fromTo("#informes-phone", {{ rotationY: 0 }}, {{ rotationY: -6, duration: 1.3, ease: "sine.inOut", transformPerspective: 2200 }}, 0);
      tl.to("#informes-phone", {{ rotationY: 0, duration: 1.0, ease: "sine.inOut" }}, 1.3);
      // toca Apple
      tap(...at("#informes-cv0"), 2.55);
      tl.to("#informes-cv0", {{ scale: 0.95, duration: 0.08, ease: "power2.in" }}, 2.51);
      tl.to("#informes-cv0", {{ scale: 1.04, duration: 0.25, ease: "power2.out" }}, 2.6);
      sidesOut(2.7);
      // el celular gira a horizontal y se agranda: se abre el informe original, como en la compu
      tl.to("#informes-phone", {{ rotation: -90, scale: {ROT}, duration: 1.0, ease: "expo.inOut" }}, 2.85);
      tl.to("#informes-cs", {{ opacity: 0, duration: 0.4, ease: "power2.out" }}, 2.85);
      tl.to(["#informes-head", "#informes-view", "#informes-tabs", "#informes-sbar", "#informes-home"], {{ opacity: 0, duration: 0.3, ease: "power2.in" }}, 2.95);
      tl.fromTo("#informes-land", {{ opacity: 0, scale: 0.9 }}, {{ opacity: 1, scale: 1, duration: 0.55, ease: "expo.out", immediateRender: false }}, 3.3);
      tl.fromTo("#informes-glare", {{ x: 0 }}, {{ x: 280, duration: 1.4, ease: "sine.inOut" }}, 2.85);
      // recorre el informe: tapa → resumen → segmentos y gráfico → valuación
      tl.set(["#informes-doc", "#informes-sc"], {{ y: 0 }}, 0);
{scroll_js}
      // vuelve a vertical, de nuevo en la biblioteca
      tl.to("#informes-land", {{ opacity: 0, duration: 0.3, ease: "power2.in" }}, 12.15);
      tl.to("#informes-phone", {{ rotation: 0, scale: 1, duration: 0.9, ease: "expo.inOut" }}, 12.2);
      tl.to("#informes-glare", {{ x: 0, duration: 0.9, ease: "sine.inOut" }}, 12.2);
      tl.to("#informes-cs", {{ opacity: 1, duration: 0.4, ease: "power2.out" }}, 12.8);
      tl.to(["#informes-head", "#informes-view", "#informes-tabs", "#informes-sbar", "#informes-home"], {{ opacity: 1, duration: 0.35, ease: "power2.out" }}, 12.6);
      tl.to("#informes-cv0", {{ scale: 1, duration: 0.3, ease: "power2.out" }}, 12.6);
      // a Warren IA
      tap({TAB_CX(1)}, {TAB_CY}, 13.35);
      tabTo(1, 13.4);
      pageOut("#informes-lib", 13.65);
'''

# ═════════════════════════════════ WARREN (Apple vs Microsoft) ═════════════════════════════════
# informes/aapl.html (4T FY2026, publicado 3-nov-2026) e informes/msft.html (1T FY2027): los dos en main.
Q = "¿Me conviene invertir en Apple o en Microsoft?"


def words(t, cls=""):
    return " ".join(f'<span class="tk w{(" " + cls) if cls else ""}">{w}</span>' for w in t.split())


def hl(txt, cls):  # número resaltado como un solo token
    return f'<b class="tk w {cls}">{txt}</b>'


def co_card(logo, name, pill, pill_cls, lines):
    lis = "".join(f'<li>{l}</li>' for l in lines)
    return f'''<div class="co tk">
        <div class="coh"><span class="lg2"><img src="{logo}" alt=""></span><b>{name}</b><span class="cp {pill_cls}">{pill}</span></div>
        <ul>{lis}</ul></div>'''


answer = f'''
      <p>{words("No te puedo decir cuál comprar, pero sí cómo se comparan según nuestros informes:")}</p>
      {co_card("assets/img/apple.svg", "Apple", "EXIGENTE", "red", [
          words("Fair value US$ 263,56 vs. US$ 338,32 →") + " " + hl("−22,1%", "r"),
          words("Año fiscal récord: US$ 478.800 M (+15%) y EPS +20%."),
          words("Ojo: la guía baja el margen bruto a 45%-46% (desde 48,8%).")])}
      {co_card("assets/img/mono-msft.png", "Microsoft", "CONSTRUCTIVA", "gold", [
          words("Fair value US$ 540,66 vs. US$ 507,12 →") + " " + hl("+6,6%", "g"),
          words("1T FY27: ventas US$ 92.300 M (+18,8%) y Azure +48%."),
          words("Ojo: el capex del año fiscal 2027 deja el flujo de caja libre en negativo.")])}
      <div class="tbl tk">
        <div class="tr th"><span>Lado a lado</span><span>AAPL</span><span>MSFT</span></div>
        <div class="tr"><span>Vs. fair value</span><span class="r">−22,1%</span><span class="g">+6,6%</span></div>
        <div class="tr"><span>Ventas último trim.</span><span>+11,7%</span><span>+18,8%</span></div>
        <div class="tr"><span>Tiene que salir bien</span><span>Margen</span><span>IA</span></div>
      </div>
      <p><b class="tk w y">En</b> <b class="tk w y">síntesis:</b> {words("según nuestros informes, Microsoft cotiza por debajo de su valor justo y Apple por encima. La decisión depende de tu perfil y de tu horizonte.")}</p>
      <p class="disc">{words("Precios a la fecha de cada informe. Análisis informativo, no es una recomendación de inversión.")}</p>'''

warren_page = f'''
            <div class="pg" id="warren-pg" style="padding:6px 16px 0">
              <div class="row" style="padding:2px 4px 12px;border-bottom:1px solid rgba(226,234,245,.08)">
                <div style="display:flex;align-items:center;gap:10px">
                  <div style="width:38px;height:38px;border-radius:50%;background:linear-gradient(160deg,#f7dc8a,#d8a93a);display:flex;align-items:center;justify-content:center;font:italic 400 22px/1 'DM Serif';color:#0a1322;box-shadow:0 0 22px rgba(242,201,76,.35)">W</div>
                  <div><div style="font:400 21px/1 'DM Serif';color:#f6f8fc">Warren <em style="color:#f7dc8a">IA</em></div><div style="font:500 11.5px/1 'Instrument';color:#ead9a4;margin-top:4px">Lee los informes de Manfredi</div></div>
                </div>
                <span style="font:600 10px/1 'Plex Mono';color:#ead9a4;letter-spacing:.08em">96/100</span>
              </div>
              <div id="warren-scroll">
                <div id="warren-chat">
                  <div id="warren-q">{Q}</div>
                  <div class="stp" id="warren-s0"><i></i>Leyendo el informe de Apple</div>
                  <div class="stp" id="warren-s1"><i></i>Leyendo el informe de Microsoft</div>
                  <div class="stp" id="warren-s2"><i></i>Comparando valuación y riesgos</div>
                  <div id="warren-a">{answer}</div>
                </div>
              </div>
            </div>
            <div id="warren-in" style="position:absolute;left:14px;right:14px;bottom:8px;height:48px;border-radius:24px;box-shadow:inset 0 0 0 1px rgba(226,234,245,.18);background:rgba(10,20,38,.97);display:flex;align-items:center;padding:0 6px 0 16px;gap:8px;z-index:3">
              <div style="flex:1;font:500 13.5px/1 'Instrument';color:#f6f8fc;white-space:nowrap;overflow:hidden"><span id="warren-typed"></span><span id="warren-caret" style="display:inline-block;width:1.5px;height:16px;background:#f2c94c;vertical-align:middle;margin-left:1px"></span><span id="warren-ph" style="color:#ead9a4">Preguntale a Warren…</span></div>
              <div id="warren-send" style="width:36px;height:36px;border-radius:50%;background:#f2c94c;display:flex;align-items:center;justify-content:center"><svg viewBox="0 0 24 24" style="width:18px;height:18px" fill="none" stroke="#0a1322" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M12 19V5M5 12l7-7 7 7"/></svg></div>
            </div>'''

warren_css = '''
      #warren-scroll { position:absolute; left:16px; right:16px; top:64px; bottom:64px; overflow:hidden; }
      #warren-chat { position:absolute; left:0; right:0; top:0; padding-bottom:14px; }
      #warren-q { margin:12px 0 0 auto; max-width:250px; width:fit-content; padding:11px 14px; border-radius:18px 18px 4px 18px;
        background:linear-gradient(180deg,#f7dc8a,#e2b94f); font:500 14px/1.35 "Instrument"; color:#0a1322; }
      .stp { margin-top:10px; display:flex; align-items:center; gap:8px; font:600 11px/1 "Plex Mono"; letter-spacing:.03em; color:#ead9a4; }
      .stp i { width:14px; height:14px; border-radius:50%; border:2px solid rgba(242,201,76,.25); border-top-color:#f2c94c; display:block; flex:none; }
      .stp.ok i { border-color:#10B981; background:#10B981; }
      #warren-a { margin-top:12px; padding:13px 14px; border-radius:18px 18px 18px 4px; box-shadow:inset 0 0 0 1px rgba(226,234,245,.16); background:rgba(18,35,62,.9);
        font:400 13px/1.5 "Instrument"; color:#f6f8fc; }
      #warren-a p { margin:0 0 10px; } #warren-a p:last-child { margin:0; }
      #warren-a .w { opacity:0; }
      #warren-a .r { color:#f87171; font-weight:700; } #warren-a .g { color:#34d399; font-weight:700; }
      #warren-a b.y { color:#f7dc8a; }
      .co { margin:0 0 10px; border-radius:12px; padding:10px 11px; box-shadow:inset 0 0 0 1px rgba(226,234,245,.12); background:rgba(255,255,255,.03); }
      .coh { display:flex; align-items:center; gap:8px; margin-bottom:6px; }
      .coh b { font:400 17px/1 "DM Serif"; color:#f6f8fc; flex:1; }
      .lg2 { width:24px; height:24px; border-radius:7px; background:#0a1322; display:flex; align-items:center; justify-content:center; box-shadow:inset 0 0 0 1px rgba(226,234,245,.18); }
      .lg2 img { width:14px; height:14px; object-fit:contain; }
      .cp { font:700 9px/1 "Plex Mono"; letter-spacing:.08em; padding:5px 7px; border-radius:6px; }
      .cp.red { color:#fca5a5; background:rgba(239,68,68,.14); } .cp.gold { color:#f7dc8a; background:rgba(242,201,76,.14); }
      .co ul { margin:0; padding-left:14px; } .co li { margin:3px 0; font-size:12.5px; line-height:1.42; }
      .co li::marker { color:#f2c94c; }
      .tbl { margin:0 0 10px; border-radius:12px; overflow:hidden; box-shadow:inset 0 0 0 1px rgba(226,234,245,.14); font:600 11.5px/1 "Instrument"; }
      .tr { display:grid; grid-template-columns:1.5fr 1fr 1fr; padding:8px 10px; border-top:1px solid rgba(226,234,245,.08); }
      .tr span:not(:first-child) { text-align:right; font-family:"Plex Mono"; font-weight:700; }
      .tr.th { border-top:0; background:rgba(242,201,76,.10); color:#f7dc8a; font:700 10px/1 "Plex Mono"; letter-spacing:.08em; text-transform:uppercase; }
      .disc { font-size:10.5px !important; line-height:1.4 !important; color:#ead9a4; }
'''

warren_body = phone(warren_page, 1, "warren") + side_l(
    "warren", "<b>02</b> · Warren IA", "Warren", "IA.", "Tu analista personal: 100 consultas por mes.") + side_r(
    "warren", [("compare", "Comparar empresas", "Apple vs. Microsoft, lado a lado"), ("tag", "Saber si algo está caro", "Contra nuestro fair value"),
               ("alert", "Ver los riesgos", "Lo que tiene que salir bien"), ("pie", "Analizar tu portafolio", "Con tus posiciones reales")])

warren_js = '''
      drift(6);
      pageIn("#warren-pg", 0.02);
      tl.fromTo("#warren-in", { y: 90 }, { y: 0, duration: 0.6, ease: "expo.out" }, 0.1);
      sidesIn(0.1);
      actsIn(0.55, 0.36);
      const Q = ''' + repr(Q) + ''';
      const typed = R.querySelector("#warren-typed"), ph = R.querySelector("#warren-ph"), caret = R.querySelector("#warren-caret");
      tl.fromTo("#warren-q", { opacity: 0, y: 24, scale: 0.9 }, { opacity: 1, y: 0, scale: 1, duration: 0.4, ease: "back.out(2)", transformOrigin: "100% 100%" }, 2.55);
      const STEP_T = [2.95, 3.55, 4.15];
      STEP_T.forEach((t, i) => tl.fromTo("#warren-s" + i, { opacity: 0, x: -10 }, { opacity: 1, x: 0, duration: 0.3, ease: "power2.out" }, t));
      tl.fromTo("#warren-a", { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: 0.35, ease: "power2.out" }, 4.85);
      const TK = Array.from(R.querySelectorAll("#warren-a .tk"));
      const chat = R.querySelector("#warren-chat"), VIS = R.querySelector("#warren-scroll").offsetHeight;
      const T0 = 5.0, T1 = 14.6;
      const cost = TK.map((el) => (el.classList.contains("w") ? 1 : 6));
      const total = cost.reduce((a, b) => a + b, 0);
      let acc = 0;
      const times = cost.map((c) => { const t = T0 + (acc / total) * (T1 - T0); acc += c; return t; });
      // fondo de cada token; una tarjeta de empresa "termina" en su encabezado (sus renglones se escriben después)
      const bottoms = TK.map((el) => { let y = el.classList.contains("co") ? 38 : el.offsetHeight, e = el; while (e && e !== chat) { y += e.offsetTop; e = e.offsetParent; } return y; });
      TK.forEach((el, i) => {
        if (el.classList.contains("w")) tl.fromTo(el, { opacity: 0 }, { opacity: 1, duration: 0.1, ease: "none" }, times[i]);
        else tl.fromTo(el, { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: 0.35, ease: "expo.out" }, times[i]);
      });
      const qBottom = R.querySelector("#warren-s2").offsetTop + 30;
      const ansEl = R.querySelector("#warren-a"), A_BOT = ansEl.offsetTop + ansEl.offsetHeight;
      function target(t) {
        let b = t < 2.5 ? 0 : qBottom;
        for (let i = 0; i < TK.length; i++) { if (times[i] <= t) b = Math.max(b, bottoms[i]); else break; }
        return -Math.max(0, b + 16 - VIS);
      }
      MF.clock(tl, DUR, (t) => {
        const k = Math.max(0, Math.min(Q.length, Math.floor((t - 0.55) / 1.75 * Q.length)));
        const sent = t >= 2.5;
        typed.textContent = sent ? "" : Q.slice(0, k);
        ph.style.display = (k === 0 || sent) ? "inline" : "none";
        caret.style.opacity = (Math.floor(t * 2.2) % 2 === 0 && !sent) ? 1 : 0;
        STEP_T.forEach((st, i) => {
          const el = R.querySelector("#warren-s" + i), done = t >= st + 0.55;
          el.classList.toggle("ok", done);
          el.querySelector("i").style.transform = done ? "none" : "rotate(" + (t * 520) + "deg)";
        });
        // la burbuja crece a medida que Warren escribe (recorte desde abajo)
        let rb = 0; for (let i = 0; i < TK.length; i++) { if (times[i] <= t + 0.05) rb = Math.max(rb, bottoms[i]); else break; }
        const cut = Math.max(0, A_BOT - (rb + 14));
        ansEl.style.clipPath = "inset(0 0 " + cut.toFixed(1) + "px 0 round 18px 18px 18px 4px)";
        let y = 0; for (let j = 0; j < 8; j++) y += target(t - j * 0.05); y /= 8;
        chat.style.transform = "translateY(" + y.toFixed(1) + "px)";
      });
      tap(...at("#warren-send"), 2.45);
      tap(''' + str(TAB_CX(2)) + ''', ''' + str(TAB_CY) + ''', 17.2);
      tabTo(2, 17.25);
      pageOut("#warren-pg", 17.55);
      tl.to("#warren-in", { y: 90, duration: 0.3, ease: "power3.in" }, 17.55);
      sidesOut(17.55);
'''

# ═════════════════════════════════ PEDIDO (Boeing) ═════════════════════════════════
pedido_page = '''
            <div class="pg" id="pedido-pg">
              <h4>Pedí un <em>informe</em></h4>
              <div class="sub">1 por mes con tu membresía · te queda 1</div>
              <div class="srch on" id="pedido-srch"><svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/></svg><span id="pedido-typed"></span><span id="pedido-caret" class="caret"></span><span id="pedido-ph">Buscar empresa o ticker…</span></div>
              <div class="res" id="pedido-res">
                <div class="ri"><span class="lg3"><img src="assets/img/boeing.svg" alt=""></span><span class="rt">BA</span><span class="rn">The Boeing Company</span></div>
                <div class="rempty">Todavía no tenemos informe de <b>BOEING</b>.<span class="cta" id="pedido-cta">Pedilo con tu membresía →</span></div>
              </div>
              <div class="frm" id="pedido-frm">
                <div class="row" style="justify-content:flex-start;gap:12px">
                  <span class="lg3 big"><img src="assets/img/boeing.svg" alt=""></span>
                  <div><div style="font:400 23px/1 'DM Serif';color:#f6f8fc">The Boeing <em style="color:#f7dc8a">Company</em></div><div style="font:600 10.5px/1 'Plex Mono';color:#ead9a4;margin-top:6px;letter-spacing:.06em">BA · NYSE · AEROESPACIAL</div></div>
                </div>
                <div class="fl"><span>Informe completo</span><b>14 secciones + fair value</b></div>
                <div class="fl"><span>Entrega</span><b>48 hs como máximo</b></div>
                <div class="fl"><span>Pedidos este mes</span><b>1 de 1</b></div>
                <div class="pbtn2" id="pedido-btn"><span id="pedido-bt">Pedir informe</span></div>
              </div>
              <div class="ok" id="pedido-ok">
                <div class="okc" id="pedido-okc"><svg viewBox="0 0 24 24" fill="none" stroke="#06261b" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg></div>
                <div class="okt">¡Listo! Recibimos tu pedido de <b>BA</b>.</div>
                <div class="oks">Lo vas a tener en un <b>máximo de 48 hs</b> y te avisamos por mail.</div>
                <div class="okl"><span class="on"><i></i>Pedido</span><span id="pedido-p1"><i id="pedido-p1i"></i>En análisis</span><span><i></i>Publicado</span></div>
              </div>
            </div>'''

pedido_css = '''
      .srch { display:flex; align-items:center; gap:8px; height:42px; border-radius:12px; padding:0 12px; box-shadow:inset 0 0 0 1px rgba(226,234,245,.16);
        background:rgba(255,255,255,.04); font:500 14px/1 "Instrument"; color:#f6f8fc; }
      .srch.on { box-shadow:inset 0 0 0 1px rgba(242,201,76,.6), 0 0 0 3px rgba(242,201,76,.10); }
      .srch svg { width:16px; height:16px; fill:none; stroke:#ead9a4; stroke-width:2; flex:none; }
      #pedido-ph { color:#ead9a4; } .caret { display:inline-block; width:1.5px; height:17px; background:#f2c94c; margin-left:-6px; }
      .res { margin-top:8px; border-radius:14px; overflow:hidden; box-shadow:inset 0 0 0 1px rgba(226,234,245,.14); background:#0e1d36; }
      .ri { display:flex; align-items:center; gap:10px; padding:11px 12px; border-bottom:1px solid rgba(226,234,245,.08); }
      .rt { font:700 13px/1 "Plex Mono"; color:#f7dc8a; } .rn { font:500 13px/1 "Instrument"; color:#f6f8fc; flex:1; }
      .lg3 { width:30px; height:30px; border-radius:8px; background:#1d4fa3; display:flex; align-items:center; justify-content:center; flex:none; }
      .lg3 img { width:20px; height:20px; } .lg3.big { width:48px; height:48px; border-radius:12px; } .lg3.big img { width:32px; height:32px; }
      .rempty { padding:12px; font:500 12.5px/1.45 "Instrument"; color:#f6f8fc; display:flex; flex-direction:column; gap:10px; }
      .rempty b { font-family:"Plex Mono"; color:#f7dc8a; }
      .cta { align-self:flex-start; padding:9px 14px; border-radius:999px; background:linear-gradient(180deg,#f7dc8a,#d8a93a); color:#0a1322; font:600 12.5px/1 "Instrument"; }
      .frm { position:absolute; left:20px; right:20px; top:96px; border-radius:18px; padding:16px; box-shadow:inset 0 0 0 1px rgba(242,201,76,.38);
        background:radial-gradient(100% 60% at 100% 0%, rgba(242,201,76,.12), transparent 60%), linear-gradient(170deg,#1a3360,#0a1530); }
      .fl { display:flex; justify-content:space-between; align-items:center; padding:12px 0; border-top:1px solid rgba(226,234,245,.10); margin-top:12px; font:500 12.5px/1 "Instrument"; color:#ead9a4; }
      .fl + .fl { margin-top:0; } .fl b { font:600 12.5px/1 "Instrument"; color:#f6f8fc; }
      .pbtn2 { margin-top:12px; height:50px; border-radius:25px; background:linear-gradient(180deg,#f7dc8a,#d8a93a); display:flex; align-items:center; justify-content:center; font:600 15px/1 "Instrument"; color:#0a1322; }
      .ok { position:absolute; left:20px; right:20px; top:96px; border-radius:18px; padding:22px 18px; text-align:center; box-shadow:inset 0 0 0 1px rgba(16,185,129,.42);
        background:radial-gradient(100% 70% at 50% 0%, rgba(16,185,129,.16), transparent 65%), linear-gradient(170deg,#12304a,#0a1530); }
      .okc { width:64px; height:64px; margin:0 auto 14px; border-radius:50%; background:#10B981; display:flex; align-items:center; justify-content:center; box-shadow:0 0 40px rgba(16,185,129,.55); }
      .okc svg { width:32px; height:32px; }
      .okt { font:400 22px/1.15 "DM Serif"; color:#f6f8fc; } .okt b { font-family:"Plex Mono"; font-weight:700; color:#f7dc8a; font-size:18px; }
      .oks { margin-top:10px; font:500 13px/1.45 "Instrument"; color:#f6f8fc; } .oks b { color:#34d399; }
      .okl { margin-top:18px; display:flex; justify-content:space-between; position:relative; }
      .okl::before { content:""; position:absolute; left:18px; right:18px; top:6px; height:2px; background:rgba(226,234,245,.14); }
      .okl span { position:relative; display:flex; flex-direction:column; align-items:center; gap:7px; font:600 10.5px/1 "Plex Mono"; letter-spacing:.04em; color:#ead9a4; width:33%; }
      .okl i { width:14px; height:14px; border-radius:50%; background:#0a1530; border:2px solid rgba(226,234,245,.3); display:block; }
      .okl span.on { color:#34d399; } .okl span.on i { background:#10B981; border-color:#10B981; }
'''

pedido_body = phone(pedido_page, 2, "pedido") + side_l(
    "pedido", "<b>03</b> · Pedidos", "Pedí tu", "informe.", "1 por mes, de la empresa que quieras.") + side_r(
    "pedido", [("search", "Buscar cualquier empresa", "Las que cotizan en bolsa"), ("plus", "Pedir el informe", "Con un toque, incluido en Pro"),
               ("clock", "Tenerlo en 48 hs", "Como máximo"), ("mail", "Recibir el aviso", "Te llega por mail")])

pedido_js = '''
      drift(-6);
      pageIn("#pedido-pg", 0.02);
      sidesIn(0.1);
      actsIn(0.55, 0.36);
      tl.fromTo("#pedido-frm", { opacity: 0, y: 500 }, { opacity: 1, y: 0, duration: 0.6, ease: "expo.out", immediateRender: true }, 3.15);
      tl.fromTo("#pedido-ok", { opacity: 0, scale: 0.9 }, { opacity: 1, scale: 1, duration: 0.5, ease: "back.out(1.8)", immediateRender: true }, 6.2);
      const W = "Boeing";
      const typed = R.querySelector("#pedido-typed"), ph = R.querySelector("#pedido-ph"), caret = R.querySelector("#pedido-caret");
      MF.clock(tl, DUR, (t) => {
        const k = Math.max(0, Math.min(W.length, Math.floor((t - 0.8) / 0.9 * W.length)));
        typed.textContent = W.slice(0, k);
        ph.style.display = k === 0 ? "inline" : "none";
        caret.style.marginLeft = k === 0 ? "-6px" : "1px";
        caret.style.opacity = (Math.floor(t * 2.2) % 2 === 0 && t < 3.1) ? 1 : 0;
        R.querySelector("#pedido-bt").textContent = t >= 5.75 && t < 6.25 ? "Enviando…" : "Pedir informe";
      });
      tl.fromTo("#pedido-res", { opacity: 0, y: -8 }, { opacity: 1, y: 0, duration: 0.35, ease: "expo.out" }, 1.85);
      tl.fromTo("#pedido-cta", { boxShadow: "0 0 0 rgba(242,201,76,0)" }, { boxShadow: "0 0 26px rgba(242,201,76,.6)", duration: 0.4, ease: "sine.inOut", yoyo: true, repeat: 1 }, 2.15);
      tap(...at("#pedido-cta"), 2.9);
      tl.to("#pedido-cta", { scale: 0.94, duration: 0.08, ease: "power2.in" }, 2.86);
      tl.to(["#pedido-res", "#pedido-srch"], { opacity: 0, y: -20, duration: 0.3, ease: "power2.in" }, 3.1);
      tap(...at("#pedido-btn"), 5.7);
      tl.to("#pedido-btn", { scale: 0.95, duration: 0.08, ease: "power2.in" }, 5.66);
      tl.to("#pedido-btn", { scale: 1, duration: 0.2, ease: "power2.out" }, 5.76);
      tl.to("#pedido-frm", { opacity: 0, scale: 0.92, duration: 0.3, ease: "power2.in" }, 6.0);
      tl.fromTo("#pedido-okc", { scale: 0, rotation: -60 }, { scale: 1, rotation: 0, duration: 0.6, ease: "back.out(2.6)" }, 6.35);
      tl.to("#pedido-p1", { color: "#34d399", duration: 0.3 }, 7.6);
      tl.to("#pedido-p1i", { backgroundColor: "#0a1530", borderColor: "#10B981", duration: 0.3 }, 7.6);
      pageOut("#pedido-pg", 9.95);
      sidesOut(9.95);
'''

# ═════════════════════════════════ CIERRE ═════════════════════════════════
cierre_css = '''
      #cierre-card { position:absolute; left:400px; top:250px; width:1120px; height:540px; border-radius:34px; padding:60px 66px; display:flex; flex-direction:column;
        box-shadow:inset 0 0 0 1px rgba(242,201,76,.5), inset 0 1px 0 rgba(255,255,255,.08), 0 60px 120px -30px rgba(0,0,0,.85), 0 0 120px -20px rgba(242,201,76,.35);
        background:radial-gradient(110% 60% at 50% 0%, rgba(242,201,76,.16), transparent 62%), linear-gradient(180deg, rgba(25,45,78,.85), rgba(10,20,38,.95)); }
      .cc-top { display:flex; justify-content:space-between; align-items:center; }
      .cc-n { font:400 100px/1 "DM Serif"; color:#f6f8fc; letter-spacing:-.025em; white-space:nowrap; }
      .cc-n em { font-style:italic; background:linear-gradient(180deg,#fbecc4,#f2c94c 52%,#b98a28); -webkit-background-clip:text; background-clip:text; color:transparent; padding-right:.08em; }
      .cc-p { display:flex; align-items:baseline; gap:12px; white-space:nowrap; }
      .cc-p .cur { font:600 22px/1 "Plex Mono"; letter-spacing:.14em; color:#ead9a4; align-self:flex-start; margin-top:12px; }
      .cc-p .amt { font:400 116px/1 "DM Serif"; color:#f7dc8a; }
      .cc-p .per { font:italic 400 36px/1 "Newsreader"; color:#f3e3bd; }
      .cc-g { margin-top:auto; display:grid; grid-template-columns:1fr 1fr; gap:24px 40px; padding-top:36px; border-top:1px solid rgba(226,234,245,.14); }
      .cc-g div { display:flex; align-items:center; gap:16px; font:600 29px/1.1 "Instrument"; color:#f6f8fc; white-space:nowrap; }
      .cc-g .tile { width:54px; height:54px; border-radius:16px; }
      .cc-g .tile svg { width:26px; height:26px; }
      #cierre-logo { position:absolute; left:0; right:0; top:0; height:1080px; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:28px; }
      #cierre-logo .wm { font:400 96px/1 "DM Serif"; color:#f6f8fc; letter-spacing:-.025em; }
      #cierre-logo .wm em { font-style:italic; color:#f7dc8a; }
      #cierre-logo .url { font:600 26px/1 "Plex Mono"; letter-spacing:.14em; color:#ead9a4; }
      .mp { display:inline-flex; align-items:center; gap:12px; height:58px; padding:0 22px 0 14px; border-radius:999px; background:#fff; font:700 25px/1 "Plex Sans"; color:#2d3277; }
      .mp b { color:#00b1ea; } .mp svg { width:42px; height:42px; }
      .mprow { display:flex; align-items:center; gap:18px; font:500 26px/1 "Instrument"; color:#f6f8fc; }
'''
mp_svg = f'<svg viewBox="0 0 24 24"><path fill="#00b1ea" d="{MP_PATH}"/></svg>'
FEATS_PRO = [("doc", "Informes institucionales"), ("compare", "Warren IA: 100 consultas"), ("plus", "1 informe a pedido por mes"), ("pie", "Chats Pro con Ignacio")]
cierre_body = phone("", 2, "cierre") + f'''
      <div id="cierre-card">
        <div class="cc-top"><div class="cc-n" id="cierre-n">Manfredi <em>Pro</em></div>
          <div class="cc-p" id="cierre-p"><span class="cur">USD</span><span class="amt">15</span><span class="per">por mes</span></div></div>
        <div class="cc-g">{"".join(f'<div id="cierre-f{i}"><span class="tile"><svg viewBox="0 0 24 24">{ICON[ic]}</svg></span>{f}</div>' for i, (ic, f) in enumerate(FEATS_PRO))}</div>
      </div>
      <div id="cierre-logo">
        <img id="cierre-em" src="assets/img/emblem.svg" style="width:156px;height:156px" alt="">
        <div class="wm" id="cierre-wm">Manfredi <em>Investment</em></div>
        <div class="url" id="cierre-url">MANFREDINVESTMENT.COM</div>
        <div class="mprow" id="cierre-mp"><span class="mp">{mp_svg}mercado <b>pago</b></span>Suscribite con Mercado Pago</div>
      </div>'''

cierre_js = '''
      tl.to("#cierre-phone", { scale: 0.7, opacity: 0, filter: "blur(12px)", duration: 0.6, ease: "power3.in" }, 0.05);
      tl.to("#cierre-cs", { opacity: 0, duration: 0.4 }, 0.05);
      tl.fromTo("#cierre-card", { opacity: 0, y: 280, rotationX: -22, transformPerspective: 1600 }, { opacity: 1, y: 0, rotationX: 0, duration: 0.9, ease: "expo.out" }, 0.45);
      tl.fromTo(["#cierre-n", "#cierre-p"], { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.6, ease: "expo.out", stagger: 0.12 }, 0.75);
      for (let i = 0; i < 4; i++) tl.fromTo("#cierre-f" + i, { opacity: 0, x: 40 }, { opacity: 1, x: 0, duration: 0.5, ease: "expo.out" }, 1.1 + i * 0.14);
      tl.to("#cierre-card", { y: -14, duration: 1.6, ease: "sine.inOut" }, 1.4);
      tl.to("#cierre-card", { opacity: 0, y: -170, filter: "blur(16px)", duration: 0.4, ease: "power3.in" }, 3.2);
      tl.fromTo("#cierre-em", { opacity: 0, scale: 0.4, rotation: -30 }, { opacity: 1, scale: 1, rotation: 0, duration: 0.8, ease: "back.out(1.8)" }, 3.55);
      tl.fromTo("#cierre-wm", { opacity: 0, y: 40, filter: "blur(10px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 0.6, ease: "expo.out" }, 3.75);
      tl.fromTo("#cierre-url", { opacity: 0, scale: 1.25 }, { opacity: 1, scale: 1, duration: 0.8, ease: "expo.out" }, 3.95);
      tl.fromTo("#cierre-mp", { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.5, ease: "expo.out" }, 4.2);
'''

SCN = {
    "intro": (intro_body, intro_js, "", 0),
    "informes": (informes_body, informes_js, informes_css, 0),
    "warren": (warren_body, warren_js, warren_css, 1),
    "pedido": (pedido_body, pedido_js, pedido_css, 2),
    "cierre": (cierre_body, cierre_js, cierre_css, 2),
}
(ROOT / "compositions").mkdir(exist_ok=True)
for old in (ROOT / "compositions").glob("*.html"):
    old.unlink()
(ROOT / "compositions" / "fondo.html").write_text(fondo_scene(), encoding="utf-8")
for sid, (body, js, css, t0) in SCN.items():
    (ROOT / "compositions" / f"{sid}.html").write_text(scene(sid, dur_of(sid), body, js, css, t0), encoding="utf-8")

# ═════════════════════════════════ SONIDO ═════════════════════════════════
PEAK = {"swoosh-a": 0.291, "swoosh-b": 0.042, "swoosh-c": 1.312, "pop": 0.120, "click": 0.073, "ping": 0.324,
        "sparkle": 0.027, "notification": 0.229, "typing": 0.457, "whoosh-cinematic": 2.503, "impact-bass-1": 0.073}
DUR = {"swoosh-a": 0.92, "swoosh-b": 0.7, "swoosh-c": 2.0, "pop": 0.6, "click": 0.37, "ping": 1.2, "sparkle": 1.6,
       "notification": 1.4, "typing": 1.6, "whoosh-cinematic": 4.0, "impact-bass-1": 1.4}
SFX = [  # (archivo, escena, segundo local del cuadro de la acción, volumen, extra)
    ("swoosh-b", "intro", 0.05, 0.25, {}), ("click", "intro", 1.5, 0.5, {}), ("swoosh-c", "intro", 1.62, 0.28, {}),
    ("sparkle", "intro", 2.0, 0.3, {}), ("swoosh-a", "intro", 4.05, 0.35, {}),
    ("pop", "informes", 0.6, 0.2, {}), ("pop", "informes", 0.92, 0.2, {}), ("pop", "informes", 1.24, 0.2, {}), ("pop", "informes", 1.56, 0.2, {}),
    ("click", "informes", 2.55, 0.5, {}), ("whoosh-cinematic", "informes", 3.3, 0.32, {}),
    ("swoosh-b", "informes", 4.65, 0.16, {}), ("swoosh-b", "informes", 6.25, 0.16, {}), ("swoosh-b", "informes", 7.65, 0.2, {}),
    ("swoosh-b", "informes", 8.85, 0.16, {}), ("swoosh-b", "informes", 10.05, 0.2, {}), ("ping", "informes", 10.9, 0.22, {}),
    ("swoosh-c", "informes", 12.4, 0.26, {}),
    ("click", "informes", 13.35, 0.5, {}), ("swoosh-a", "informes", 13.75, 0.35, {}),
    ("pop", "warren", 0.6, 0.2, {}), ("pop", "warren", 0.96, 0.2, {}), ("pop", "warren", 1.32, 0.2, {}), ("pop", "warren", 1.68, 0.2, {}),
    ("typing", "warren", 0.95, 0.35, {"dur": 1.4}),
    ("click", "warren", 2.45, 0.45, {}), ("pop", "warren", 2.58, 0.3, {}),
    ("pop", "warren", 3.5, 0.16, {}), ("pop", "warren", 4.1, 0.16, {}), ("pop", "warren", 4.7, 0.16, {}),
    ("notification", "warren", 4.9, 0.3, {}),
    ("click", "warren", 17.2, 0.5, {}), ("swoosh-a", "warren", 17.65, 0.35, {}),
    ("pop", "pedido", 0.6, 0.2, {}), ("pop", "pedido", 0.96, 0.2, {}), ("pop", "pedido", 1.32, 0.2, {}), ("pop", "pedido", 1.68, 0.2, {}),
    ("typing", "pedido", 1.05, 0.3, {"dur": 0.9}),
    ("click", "pedido", 2.9, 0.5, {}), ("swoosh-b", "pedido", 3.2, 0.3, {}),
    ("click", "pedido", 5.7, 0.5, {}), ("sparkle", "pedido", 6.4, 0.4, {}), ("notification", "pedido", 6.45, 0.3, {}),
    ("swoosh-a", "pedido", 10.05, 0.35, {}),
    ("whoosh-cinematic", "cierre", 0.7, 0.3, {}), ("swoosh-b", "cierre", 3.3, 0.3, {}),
    ("impact-bass-1", "cierre", 3.7, 0.45, {}), ("sparkle", "cierre", 4.0, 0.3, {}),
]


def sfx_tags():
    start = dict(SCENES)
    tags, ends = [], []
    for n, (f, sc, t, v, x) in enumerate(sorted(SFX, key=lambda c: start[c[1]] + c[2])):
        st = round(max(0.0, start[sc] + t - PEAK[f] + 1 / 60), 3)
        dur = round(min(x.get("dur", 99), DUR[f], END - st), 3)
        k = next((i for i, e in enumerate(ends) if e <= st), None)
        if k is None:
            ends.append(0)
            k = len(ends) - 1
        ends[k] = st + dur
        tags.append(f'      <audio id="sfx-{n:02d}" src="assets/sfx/{f}.mp3" data-start="{st}" data-duration="{dur}" data-volume="{v}" data-track-index="{30 + k}"></audio>')
    return "\n".join(tags)


hosts = "\n".join(
    f'      <div id="{sid}" class="scene" data-composition-id="{sid}" data-composition-src="compositions/{sid}.html" '
    f'data-start="{st}" data-duration="{dur_of(sid)}" data-track-index="{i + 1}" data-track-kind="graphics" data-width="1920" data-height="1080"></div>'
    for i, (sid, st) in enumerate(SCENES))

index = f"""<!doctype html>
<html lang="es">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <link rel="stylesheet" href="assets/app.css" />
    <script src="assets/brand.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: 1920px; height: 1080px; overflow: hidden; background: #060d1a; }}
      #root {{ position: relative; width: 100%; height: 100%; overflow: hidden; }}
      .scene {{ position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; z-index: 2; }}
      #fondo {{ z-index: 1; }}
    </style>
  </head>
  <body>
    <!-- Generado por build.py: no editar a mano. -->
    <div id="root" data-composition-id="main" data-start="0" data-duration="{END}" data-width="1920" data-height="1080">
      <div id="fondo" class="scene" data-composition-id="fondo" data-composition-src="compositions/fondo.html" data-start="0" data-duration="{END}" data-track-index="0" data-track-kind="graphics" data-width="1920" data-height="1080"></div>
{hosts}
      <audio id="music" src="assets/sfx/music-bed.mp3" data-start="0" data-duration="{END}" data-volume="0.32" data-track-index="20"></audio>
{sfx_tags()}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
(ROOT / "index.html").write_text(index, encoding="utf-8")
print(f"index.html: {len(SCENES)} escenas + fondo, {len(SFX)} efectos, {END} s")
