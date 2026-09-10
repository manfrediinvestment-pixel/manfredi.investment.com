/* ============================================================================
   Vista previa de informes para no-miembros
   ----------------------------------------------------------------------------
   Los informes de la sección Inversiones dejan de estar bloqueados: cualquiera
   puede abrir la portada + UNA sección completa del informe: la Sección 03
   ("Modelo de Negocio y Segmentos"), que en todos los informes trae al menos
   un gráfico. Las Secciones 01 y 02 se ocultan; de la Sección 04 en adelante
   el contenido se difumina y aparece una tarjeta de membresía.
   (Para mostrar otra sección, cambiar SHOW_ID abajo.)

   Miembro = localStorage['mi_member_token'] presente (mismo criterio que la
   home). Un miembro ve el informe completo, sin cambios.

   Escape hatch para revisión: agregar ?preview=full a la URL fuerza el informe
   completo aunque no haya sesión.
   ========================================================================== */
(function () {
  "use strict";

  function isMember() {
    try {
      if (new URLSearchParams(location.search).get("preview") === "full") return true;
      return !!localStorage.getItem("mi_member_token");
    } catch (e) {
      return false;
    }
  }

  if (isMember()) return;

  function pad2(n) { return (n < 10 ? "0" : "") + n; }

  function run() {
    var wrap = document.querySelector(".wrap");
    var disclosure = document.querySelector(".disclosure");

    // Única sección visible sin membresía. La 03 ("Modelo de Negocio y
    // Segmentos") siempre trae al menos un gráfico; cambiar acá para mostrar otra.
    var SHOW_ID = "s03";
    var showSec = document.getElementById(SHOW_ID);
    var firstSec = document.getElementById("s01");
    if (!wrap || !disclosure || !showSec || !firstSec) return; // estructura inesperada: informe abierto
    var showNum = parseInt(SHOW_ID.slice(1), 10);
    var afterSec = document.getElementById("s" + pad2(showNum + 1)); // primera sección difuminada

    // --- estilos -------------------------------------------------------------
    var css = document.createElement("style");
    css.textContent = [
      ".mig-notice{border:1px solid var(--line);border-left:3px solid var(--blue);",
      "background:var(--blue-pale);padding:12px 16px;margin:26px 0 4px;",
      "font-family:var(--mono);font-size:11.5px;line-height:1.6;color:var(--navy2);}",
      ".mig-notice strong{color:var(--navy-dark);}",

      ".mig-lock{position:relative;max-height:430px;overflow:hidden;",
      "filter:blur(5px);opacity:.55;pointer-events:none;user-select:none;",
      "-webkit-mask-image:linear-gradient(180deg,#000 0%,#000 20%,transparent 88%);",
      "mask-image:linear-gradient(180deg,#000 0%,#000 20%,transparent 88%);}",

      ".mig-cta{position:relative;z-index:2;margin:-72px 0 46px;",
      "border:1px solid var(--navy-dark);background:#fff;",
      "box-shadow:0 24px 60px -28px rgba(11,31,58,.45);",
      "padding:40px 34px 34px;text-align:center;}",
      ".mig-cta__mark{width:40px;height:40px;border:1.5px solid var(--navy-dark);",
      "display:flex;align-items:center;justify-content:center;margin:0 auto 18px;",
      "font-family:var(--serif);font-weight:700;color:var(--navy-dark);font-size:17px;}",
      ".mig-cta__kicker{font-family:var(--mono);font-size:10px;letter-spacing:.16em;",
      "text-transform:uppercase;color:var(--muted);margin-bottom:10px;}",
      ".mig-cta__title{font-family:var(--serif);font-size:23px;font-weight:600;",
      "color:var(--navy2);margin:0 0 12px;line-height:1.3;}",
      ".mig-cta__text{font-size:14px;color:var(--text);line-height:1.7;",
      "max-width:52ch;margin:0 auto 22px;}",
      ".mig-cta__price{font-family:var(--mono);margin-bottom:20px;}",
      ".mig-cta__amt{font-size:22px;font-weight:600;color:var(--navy-dark);}",
      ".mig-cta__per{font-size:12px;color:var(--muted);margin-left:8px;}",
      ".mig-cta__btn{display:inline-block;background:var(--navy-dark);color:#fff;",
      "font-family:var(--sans);font-weight:600;font-size:14px;text-decoration:none;",
      "padding:13px 30px;border:1px solid var(--navy-dark);transition:background .15s;}",
      ".mig-cta__btn:hover{background:var(--navy2);}",
      ".mig-cta__login{font-family:var(--mono);font-size:11px;color:var(--muted);",
      "margin:16px 0 0;}",
      ".mig-cta__login a{color:var(--blue);}",
      "@media(max-width:720px){.mig-cta{padding:32px 20px 28px;}.mig-cta__title{font-size:20px;}}",

      /* --- fair value + barra de veredicto difuminados en la portada --- */
      ".mig-fvlock .fv-value{filter:blur(7px);-webkit-user-select:none;user-select:none;pointer-events:none;}",
      ".mig-fvlock .fv-gap{filter:blur(6px);-webkit-user-select:none;user-select:none;pointer-events:none;}",
      ".mig-verdlock .verdict-stance{filter:blur(4.5px);-webkit-user-select:none;user-select:none;pointer-events:none;}",
      ".mig-verdlock{border-left:4px solid var(--line);}",
      ".mig-verdlock.mig-verdlock--pos{border-left-color:var(--green);}",
      ".mig-verdlock.mig-verdlock--neg{border-left-color:var(--red);}",

      ".mig-sig{display:inline-block;margin-top:9px;font-family:var(--mono);font-size:9.5px;",
      "letter-spacing:.08em;text-transform:uppercase;padding:4px 9px;border:1px solid var(--line);}",
      ".mig-sig--pos{color:var(--green);border-color:var(--green);background:rgba(26,122,84,.08);}",
      ".mig-sig--neg{color:var(--red);border-color:var(--red);background:rgba(168,41,31,.09);}",
      ".mig-sig--neutral{color:var(--muted);background:#f4f6f9;}"
    ].join("");
    document.head.appendChild(css);

    // --- aviso de vista previa (arriba, antes del índice) -------------------
    var total = document.querySelectorAll(".secnum").length || 14;
    var showTitle = showSec.textContent.replace(/^\s*\d+\s*[—–-]\s*/, "").trim();
    var toc = wrap.querySelector(".toc");
    var notice = document.createElement("div");
    notice.className = "mig-notice";
    notice.innerHTML =
      "<strong>Vista previa gratuita.</strong> Est&aacute;s viendo la portada y una secci&oacute;n " +
      "completa del informe &mdash; " + showTitle + ", con gr&aacute;ficos. Las otras " + (total - 1) +
      " secciones &mdash; estados financieros, flujo de caja, comparables, el modelo proyectado y la " +
      "valuaci&oacute;n con el fair value &mdash; requieren membres&iacute;a.";
    if (toc) wrap.insertBefore(notice, toc);
    else wrap.insertBefore(notice, firstSec);

    // --- difuminar el fair value y la barra de veredicto de la portada -----
    // El monto exacto queda ilegible; el color de la señal (verde = fair
    // value por encima del precio, rojo = por debajo) sigue a la vista.
    var fvBlock = wrap.querySelector(".fv-block");
    var verdictBar = wrap.querySelector(".verdict-bar");
    var gapEl = wrap.querySelector(".fv-gap");
    var sign = "neutral";
    if (gapEl && gapEl.classList.contains("pos")) sign = "pos";
    else if (gapEl && gapEl.classList.contains("neg")) sign = "neg";

    if (fvBlock) {
      fvBlock.classList.add("mig-fvlock");
      var sig = document.createElement("div");
      sig.className = "mig-sig mig-sig--" + sign;
      sig.textContent =
        sign === "pos" ? "Fair value ▲ por encima del precio · monto con membresía" :
        sign === "neg" ? "Fair value ▼ por debajo del precio · monto con membresía" :
                         "Fair value en revisión · monto con membresía";
      (gapEl && gapEl.parentNode === fvBlock ? gapEl : fvBlock.lastChild).after(sig);
    }
    if (verdictBar) {
      verdictBar.classList.add("mig-verdlock");
      if (sign !== "neutral") verdictBar.classList.add("mig-verdlock--" + sign);
    }

    // --- ocultar las secciones previas a la elegida (01 y 02) ------------
    var hidePre = document.createElement("div");
    hidePre.hidden = true;
    hidePre.setAttribute("aria-hidden", "true");
    firstSec.parentNode.insertBefore(hidePre, firstSec);
    var p = firstSec;
    while (p && p !== showSec) {
      var pnext = p.nextSibling;
      hidePre.appendChild(p);
      p = pnext;
    }

    // --- difuminar desde la sección siguiente hasta el disclosure -------
    if (afterSec) {
      var lock = document.createElement("div");
      lock.className = "mig-lock";
      lock.setAttribute("aria-hidden", "true");
      afterSec.parentNode.insertBefore(lock, afterSec);
      var node = afterSec;
      while (node && node !== disclosure) {
        var next = node.nextSibling;
        lock.appendChild(node);
        node = next;
      }
    }

    // --- tarjeta de membresía --------------------------------------------------
    var cta = document.createElement("div");
    cta.className = "mig-cta";
    cta.setAttribute("role", "region");
    cta.setAttribute("aria-label", "Contenido para miembros");
    cta.innerHTML =
      '<div class="mig-cta__mark">MI</div>' +
      '<div class="mig-cta__kicker">Manfredi Investment &middot; Membres&iacute;a</div>' +
      '<h3 class="mig-cta__title">El resto del informe es para miembros</h3>' +
      '<p class="mig-cta__text">Segu&iacute; leyendo las ' + (total - 1) + ' secciones restantes: estados financieros l&iacute;nea por l&iacute;nea, ' +
      'deuda y balance, flujo de caja, comparables de industria, registro de riesgos, catalizadores, el modelo ' +
      'proyectado y la valuaci&oacute;n &mdash; cuatro metodolog&iacute;as y el fair value.</p>' +
      '<div class="mig-cta__price"><span class="mig-cta__amt">USD 15</span><span class="mig-cta__per">/ mes &middot; cancel&aacute;s cuando quieras</span></div>' +
      '<a class="mig-cta__btn" href="/#membresia">Hacerme miembro &rarr;</a>' +
      '<p class="mig-cta__login">&iquest;Ya sos miembro? <a href="/">Inici&aacute; sesi&oacute;n en el inicio</a></p>';

    disclosure.parentNode.insertBefore(cta, disclosure);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", run);
  } else {
    run();
  }
})();
