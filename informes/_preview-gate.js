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
      "@media(max-width:720px){.mig-cta{padding:32px 20px 28px;}.mig-cta__title{font-size:20px;}}"
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
