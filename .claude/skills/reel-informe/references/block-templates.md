# Templates de código — copiar y adaptar

Estos son los esqueletos exactos ya probados en el episodio piloto de NVDA
(`marketing/reel-informe-nvda/`). Para el cuerpo de cada bloque (gráfico de barras,
cards, lista de riesgo, comparación en dos actos), **copiá el composition file
correspondiente** de `marketing/reel-informe-nvda/compositions/` — ver la tabla del
"Menú de bloques" en `SKILL.md`. Esta página cubre lo que NO vive en un composition
file propio: el esqueleto de bumper compartido por los cinco bloques, el banner
persistente y el cierre de marca, que viven en `index.html`.

## 1 — Esqueleto de bumper + header + cámara (compartido por todos los bloques)

Cada composition file de bloque (`frame2-*.html` a `frame6-*.html`) empieza con este
mismo patrón — numeral gigante con glow, título que hace waterfall palabra por
palabra, se encoge a un header fijo arriba a la izquierda, mientras la cámara hace un
push-in continuo de fondo. Parametrizá `N` (el número del bloque), `TITLE_WORDS` (el
título en mayúsculas, una palabra por `<span>`) y `HEADER_TEXT` (el título en formato
oración).

```html
<!-- dentro de <style> del composition file -->
[data-composition-id="frameN-..."] .world { position: absolute; inset: 0; transform-origin: 50% 42%; }

[data-composition-id="frameN-..."] .bumper-group {
  position: absolute; left: 0; right: 0; top: 560px; text-align: center; transform-origin: 50% 0%;
}
[data-composition-id="frameN-..."] .glow-numeral {
  position: absolute; left: 50%; top: 40px; width: 900px; height: 900px;
  transform: translate(-50%, 0) scale(.85); border-radius: 50%; opacity: 0;
  background: radial-gradient(circle, rgba(242,201,76,.55) 0%, rgba(242,201,76,0) 68%);
  filter: blur(2px);
}
[data-composition-id="frameN-..."] .numeral {
  font-family: 'DM Serif Display', Georgia, serif; font-size: 420px; line-height: 1; color: #FFE28A;
  text-shadow: 0 0 34px rgba(242,201,76,.65), 0 0 70px rgba(242,201,76,.3);
  transform: scale(0); opacity: 0;
}
/* Bloque de riesgo: reemplazar #FFE28A/rgba(242,201,76,*) por #FFC98A/rgba(255,165,61,*) en numeral y glow */

[data-composition-id="frameN-..."] .bumper-title {
  margin: 96px auto 0; max-width: 920px; font-family: 'IBM Plex Mono', monospace; font-weight: 600;
  font-size: 42px; letter-spacing: .07em; text-transform: uppercase; color: #FFFFFF; line-height: 1.3;
}
[data-composition-id="frameN-..."] .bumper-title span { display: inline-block; opacity: 0; }
[data-composition-id="frameN-..."] .bumper-rule {
  width: 120px; height: 4px; margin: 26px auto 0; background: #F2C94C;
  box-shadow: 0 0 24px rgba(242,201,76,.7); transform: scaleX(0); transform-origin: 50% 50%;
}

[data-composition-id="frameN-..."] .header {
  position: absolute; left: 64px; top: 108px; display: flex; align-items: baseline; gap: 18px; opacity: 0;
}
[data-composition-id="frameN-..."] .header .hn {
  font-family: 'DM Serif Display', Georgia, serif; font-size: 64px; color: #FFE28A;
  text-shadow: 0 0 30px rgba(242,201,76,.5);
}
[data-composition-id="frameN-..."] .header .ht {
  font-family: 'IBM Plex Mono', monospace; font-weight: 600; font-size: 30px;
  letter-spacing: .1em; text-transform: uppercase; color: #FFFFFF;
}
```

```html
<!-- markup, dentro del .world -->
<div class="bumper-group" id="bumper-group">
  <div class="glow-numeral" id="glow-numeral"></div>
  <div class="numeral" id="numeral">N</div>
  <div class="bumper-title" id="bumper-title">
    <span>PALABRA1</span>&nbsp;<span>PALABRA2</span>&nbsp;<span>PALABRA3</span>
  </div>
  <div class="bumper-rule" id="bumper-rule"></div>
</div>

<div class="header" id="header">
  <span class="hn">N</span><span class="ht">Título en formato oración</span>
</div>
```

```js
// dentro del <script>, tl ya es el gsap.timeline() de la escena
var root = '[data-composition-id="frameN-..."] ';

// Cámara: push-in continuo toda la escena (10s)
tl.fromTo(root + '.world', { scale: 1 }, { scale: 1.055, duration: 10, ease: 'none' }, 0);

// Numeral + glow, un solo beat
tl.fromTo(root + '#glow-numeral', { opacity: 0, scale: .82 }, { opacity: .5, scale: 1, duration: .8, ease: 'power2.out' }, 0);
tl.fromTo(root + '#numeral', { scale: 0, opacity: 0 }, { scale: 1, opacity: 1, duration: .6, ease: 'back.out(1.4)' }, 0.05);

// Título: waterfall por palabra — OJO: &nbsp; entre <span> NO cuenta para :nth-child.
// Con 3 palabras los índices son 1, 2, 3 (no 1, 3, 5).
var bWords = gsap.utils.toArray(document.querySelectorAll(root + '.bumper-title span'));
var bStarts = [0.42, 0.57, 0.72]; // sumar ~0.12-0.15s por palabra extra si el título tiene 4
bWords.forEach(function(w, i){
  tl.set(w, { opacity: 1, y: 45 }, bStarts[i]);
  tl.to(w, { y: 0, duration: .16, ease: 'power4.out' }, bStarts[i]);
});
tl.fromTo(root + '#bumper-rule', { scaleX: 0 }, { scaleX: 1, duration: .5, ease: 'power3.out' }, bStarts[bStarts.length-1] + .28);

// Glow del numeral: bounded idle breathe (nunca yoyo infinito)
(function(){
  var glow = document.querySelector(root + '#glow-numeral');
  var phase = { p: 0 };
  tl.to(phase, {
    p: Math.PI * 2 * 1.6, duration: 2.6, ease: 'none',
    onUpdate: function(){
      var s = Math.sin(phase.p);
      glow.style.opacity = String(.5 + s * .04);
      glow.style.transform = 'translate(-50%, 0) scale(' + (1 + s * .02) + ')';
    }
  }, 0.85);
})();

// Bumper se encoge y se convierte en el header fijo — arrancar ~1.55-1.7s
// (más tarde cuanto más largo el título, para que el usuario alcance a leerlo)
tl.to(root + '#bumper-group', { scale: .17, y: -540, duration: .65, ease: 'power3.inOut' }, 1.65);
tl.to(root + '#bumper-group', { opacity: 0, duration: .25, ease: 'power2.in' }, 2.05);
tl.fromTo(root + '#header', { opacity: 0 }, { opacity: 1, duration: .35, ease: 'power2.out' }, 2.05);

// El contenido del bloque (chart/cards/lista/comparación) arranca ~1.75-2.2s en adelante
```

**Regla de `margin-top` del `.bumper-title` según cantidad de palabras** (evita el bug
de `content_overlap` numeral-vs-título): con `margin: 96px auto 0; max-width: 920px;
font-size: 42px;` aguanta hasta 4 palabras sin overlap ni overflow — es el valor
default, no lo bajes.

## 2 — Banner de marca persistente (root-level, en `index.html`)

Va UNA vez en `index.html`, no en cada composition file — cubre todos los bloques de
análisis por encima (`data-track-index="20"`), y nunca durante el cierre de marca.

```html
<!-- dentro del <style> de index.html -->
@font-face {
  font-family: "DM Serif Display";
  font-style: normal;
  font-weight: 400;
  src: url("assets/fonts/dm-serif-display.woff2") format("woff2");
}

#brand-banner-slot { position: absolute; inset: 0; pointer-events: none; z-index: 50; }
#brand-banner {
  position: absolute; left: 0; right: 0; bottom: 0; height: 104px;
  display: flex; align-items: center; justify-content: center; gap: 20px;
  background: rgba(5, 8, 16, 0.85);
  border-top: 1px solid rgba(242, 201, 76, 0.35);
  box-shadow: 0 -14px 46px rgba(0, 0, 0, 0.5);
  opacity: 0;
}
#brand-banner img { width: 54px; height: 54px; border-radius: 10px; box-shadow: 0 0 22px rgba(242, 201, 76, 0.25); }
#brand-banner .bb-word { font-family: "DM Serif Display", Georgia, serif; font-size: 32px; color: #ffffff; }
#brand-banner .bb-dot { width: 6px; height: 6px; border-radius: 50%; background: #f2c94c; box-shadow: 0 0 10px rgba(242, 201, 76, 0.8); }
#brand-banner .bb-link { font-family: "IBM Plex Mono", monospace; font-weight: 600; font-size: 24px; letter-spacing: 0.02em; color: #f2c94c; }
```

```html
<!-- dentro de #root, como hermano de los slots de frame -->
<div id="brand-banner-slot" class="clip" data-start="0" data-duration="55.5" data-track-index="20">
  <div id="brand-banner">
    <img src="assets/img/logo-source.png" alt="Manfredi Investment" />
    <div class="bb-word">Manfredi Investment</div>
    <div class="bb-dot"></div>
    <div class="bb-link">manfredinvestment.com</div>
  </div>
</div>
```

```js
// dentro del <script> de index.html, en el timeline "main"
tl.fromTo(
  "#brand-banner",
  { opacity: 0, y: 18 },
  { opacity: 1, y: 0, duration: 0.6, ease: "power2.out" },
  0.15,
);
```

`data-duration="55.5"` es el ejemplo de NVDA (5 bloques de 10s + 5.5s de preview) —
ajustalo a la suma real de preview + bloques del episodio nuevo. Nunca lo extiendas
sobre el cierre de marca.

## 3 — Cierre de marca (root-level, en `index.html`)

No se reconstruye — se monta el mp4 ya aprobado (ver tabla de assets en `SKILL.md`)
como host media, con audio en un `<audio>` separado (el `<video>` va `muted`).

```html
<video
  id="el-frame8-video"
  class="clip"
  src="assets/video/outro-manfredi-brand.mp4"
  data-start="55.5"
  data-duration="5"
  data-track-index="1"
  muted
  playsinline
  style="position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; object-fit: cover"
></video>
<audio
  id="el-frame8-audio"
  class="clip"
  src="assets/video/outro-manfredi-brand.mp4"
  data-start="55.5"
  data-duration="5"
  data-track-index="10"
></audio>
```

`data-start="55.5"` = duración total de preview + bloques de análisis del episodio
nuevo (ajustar). Si ya está wireado el Frame 7 (cámara del usuario), sumarle también
esos segundos.

## 4 — Contador con prefijo/sufijo (hero stat de cada bloque)

Patrón usado en los cinco heroes (`$81.6B`, `2.6%`, `~$20B`, `$15.9B`, `$307.23`):

```html
<div class="hero-stat" id="hero-stat"><span class="pre">$</span>0<span class="suffix">B</span></div>
```

```js
var counter = document.querySelector(root + '#hero-stat');
var textNode = counter.childNodes[1]; // [span.pre, textNode("0"), span.suffix] — el textNode del medio
var state = { value: 0 };
tl.to(state, {
  value: TARGET, duration: 1.5, ease: 'power3.out',
  onUpdate: function(){ textNode.nodeValue = state.value.toFixed(DECIMALS); } // 0 para enteros, 1-2 para decimales
}, START_AT);
tl.fromTo(counter, { scale: START_SCALE, opacity: 0 }, { scale: 1, opacity: 1, duration: 1.5, ease: 'power3.out' }, START_AT);
```

`childNodes[1]` asume exactamente un `<span class="pre">` antes del texto — si no hay
prefijo, es `childNodes[0]`. Contá los nodos hijos reales antes de copiar este patrón,
no asumas el índice.
