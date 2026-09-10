/* ============================================================================
   Vista previa de informes para no-miembros
   ----------------------------------------------------------------------------
   Los informes de la sección Inversiones dejan de estar bloqueados: cualquiera
   puede abrirlos y leer la portada + el Resumen Ejecutivo (Sección 01). Desde
   la Sección 02 en adelante el contenido se difumina y aparece una tarjeta de
   membresía.

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

  function run() {
    var wrap = document.querySelector(".wrap");
    var start = document.getElementById("s02");
    var disclosure = document.querySelector(".disclosure");
    if (!wrap || !start) return; // estructura inesperada: dejamos el informe abierto

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
    var toc = wrap.querySelector(".toc");
    var notice = document.createElement("div");
    notice.className = "mig-notice";
    notice.innerHTML =
      "<strong>Vista previa gratuita.</strong> Estás viendo la portada y la Secci&oacute;n 01 (Resumen Ejecutivo). " +
      "Las " + (total - 1) + " secciones restantes &mdash; incluida la valuaci&oacute;n con el fair value &mdash; requieren membres&iacute;a.";
    if (toc) wrap.insertBefore(notice, toc);
    else wrap.insertBefore(notice, start);

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

    // --- difuminar de la Sección 02 en adelante ----------------------------
    var lock = document.createElement("div");
    lock.className = "mig-lock";
    lock.setAttribute("aria-hidden", "true");
    start.parentNode.insertBefore(lock, start);

    var node = start;
    while (node && node !== disclosure) {
      var next = node.nextSibling;
      lock.appendChild(node);
      node = next;
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

    if (disclosure) disclosure.parentNode.insertBefore(cta, disclosure);
    else lock.parentNode.appendChild(cta);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", run);
  } else {
    run();
  }
})();
