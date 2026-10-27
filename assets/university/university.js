/* Pestaña University: progreso de cada curso en su tarjeta (lecciones aprobadas
   según los quizzes, guardadas por miQuizRecordResult), perfil del test marcado
   en la escala, y gráficos de los cursos con colores del sitio oscuro.
   assets/university/university.css */
(function () {
  var LECCIONES = ['L0', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'L7'];
  var PERFILES = ['Conservador', 'Moderado-Conservador', 'Moderado', 'Moderado-Agresivo', 'Agresivo'];

  function progreso(curso) {
    if (typeof miCourseProgressSummary !== 'function') return null;
    try { return miCourseProgressSummary(curso, LECCIONES); } catch (e) { return null; }
  }

  function pintarCursos() {
    var total = 0, listos = 0;
    document.querySelectorAll('#university .uv-c[data-uv]').forEach(function (card) {
      var s = progreso(card.getAttribute('data-uv'));
      if (!s) return;
      var hechas = s.lessonsDone + (s.finalPassed ? 1 : 0);
      var pct = Math.round(hechas / (s.lessonsTotal + 1) * 100);
      var st = s.finalPassed ? 'listo' : hechas > 0 ? 'curso' : 'nuevo';
      card.setAttribute('data-st', st);
      card.querySelector('[data-uv-bar]').style.width = pct + '%';
      card.querySelector('[data-uv-est]').textContent =
        st === 'listo' ? 'Diploma listo' : st === 'curso' ? s.lessonsDone + ' de ' + s.lessonsTotal : 'Sin empezar';
      card.querySelector('[data-uv-cta]').textContent =
        st === 'listo' ? 'Repasar' : st === 'curso' ? 'Seguir' : 'Empezar';
      total += s.lessonsDone; if (s.finalPassed) listos++;
    });
    var el = document.getElementById('uvTotal');
    if (el) el.innerHTML = total
      ? '<b>' + total + '</b> de 32 lecciones aprobadas' + (listos ? ' · <b>' + listos + '</b> ' + (listos === 1 ? 'diploma' : 'diplomas') : '')
      : '';
  }

  function pintarPerfil(p) {
    if (!p) { try { p = JSON.parse(localStorage.getItem('mi_quiz_profile')); } catch (e) { p = null; } }
    var med = document.getElementById('uvMedidor');
    if (!med || !p || typeof p.tier !== 'number') return;
    med.classList.add('has');
    med.style.setProperty('--rot', (-72 + 36 * p.tier) + 'deg');
    med.querySelectorAll('.uv-g__s').forEach(function (s) {
      s.classList.toggle('on', +s.getAttribute('data-t') === p.tier);
    });
    var res = document.getElementById('uvMedidorRes');
    if (res) res.innerHTML = '<small>Tu perfil</small><span>' + (p.name || PERFILES[p.tier]) + '</span>';
    var cta = document.querySelector('[data-uv-test-cta]');
    if (cta) cta.innerHTML = 'Repetir el test &rarr;';
  }

  // gráficos de los cursos: texto blanco, grilla tenue y la paleta azul/índigo
  // original (vive dentro de cada curso) traducida a champagne/azul/verde
  var PALETA = {
    '#1a56db': '#f2c94c', 'rgba(26,86,219,0.15)': 'rgba(242,201,76,.16)',
    '#6366f1': '#7fb0ff', 'rgba(99,102,241,0.15)': 'rgba(127,176,255,.16)',
    '#16a34a': '#56c793', 'rgba(22,163,74,0.15)': 'rgba(86,199,147,.16)',
    '#b45309': '#e8a25a', 'rgba(180,83,9,0.15)': 'rgba(232,162,90,.16)',
    '#dc2626': '#f07b70', 'rgba(220,38,38,0.15)': 'rgba(240,123,112,.16)',
    '#1e40af': '#5b8def', 'rgba(30,64,175,0.15)': 'rgba(91,141,239,.16)',
    '#888780': '#c9d6e8', 'rgba(136,135,128,0.15)': 'rgba(201,214,232,.14)'
  };
  var CLAVES = ['backgroundColor', 'borderColor', 'pointBackgroundColor', 'pointBorderColor', 'hoverBackgroundColor', 'hoverBorderColor'];
  function traducir(c) {
    if (Array.isArray(c)) return c.map(traducir);
    if (typeof c !== 'string') return c;
    return PALETA[c.toLowerCase().replace(/\s+/g, '')] || c;
  }
  function temaGraficos() {
    var C = window.Chart;
    if (!C || !C.defaults || C._uv) return;
    C._uv = true;
    C.defaults.color = '#f3f6fb';
    C.defaults.borderColor = 'rgba(214,226,244,.1)';
    C.defaults.font.family = "'IBM Plex Sans', system-ui, sans-serif";
    C.register({
      id: 'uvPaleta',
      beforeInit: function (chart) {
        if (!chart.canvas || !chart.canvas.closest('.course-modal')) return;
        (chart.config.data.datasets || []).forEach(function (ds) {
          CLAVES.forEach(function (k) { if (ds[k]) ds[k] = traducir(ds[k]); });
        });
      }
    });
  }

  // el progreso cambia al corregir un quiz y al cerrar un curso
  function engancharse() {
    if (typeof window.quizGrade === 'function' && !window.quizGrade._uv) {
      var corregir = window.quizGrade;
      window.quizGrade = function () { var r = corregir.apply(this, arguments); pintarCursos(); return r; };
      window.quizGrade._uv = true;
    }
    // Chart.js puede cargarse (o recargarse) después: el tema se aplica al abrir un curso
    if (typeof window.openCourse === 'function' && !window.openCourse._uv) {
      var abrir = window.openCourse;
      window.openCourse = function () { temaGraficos(); return abrir.apply(this, arguments); };
      window.openCourse._uv = true;
    }
    if (typeof window.closeCourse === 'function' && !window.closeCourse._uv) {
      var cerrar = window.closeCourse;
      window.closeCourse = function () { var r = cerrar.apply(this, arguments); pintarCursos(); return r; };
      window.closeCourse._uv = true;
    }
  }

  // entrada escalonada la primera vez que se ve la pestaña
  function entrada() {
    var sec = document.getElementById('university');
    if (!sec || !('IntersectionObserver' in window)) return;
    var io = new IntersectionObserver(function (es) {
      if (es.some(function (e) { return e.isIntersecting; })) { sec.classList.add('uv-in'); io.disconnect(); }
    });
    io.observe(sec);
  }

  function init() {
    temaGraficos(); engancharse(); pintarCursos(); pintarPerfil(); entrada();
    window.addEventListener('mi:quiz-completed', function (e) { pintarPerfil(e.detail); });
    window.addEventListener('storage', function () { pintarCursos(); pintarPerfil(); });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
