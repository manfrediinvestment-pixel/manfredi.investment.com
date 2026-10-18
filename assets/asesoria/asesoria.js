/* Asesoría personalizada (#asesoria). Las consultas van al worker log-user
   (POST /asesoria-consulta): quedan en la hoja "Asesoria" de la planilla de
   usuarios y llegan por mail a Ignacio, con copia de confirmación al cliente. */
(function () {
  // Cuando la CNV dé el alta, cargar el número acá: cambia la sección y el
  // aviso legal del pie (sin número = "en trámite").
  var MATRICULA = '';
  var ENDPOINT = 'https://log-user.nachito2502.workers.dev/asesoria-consulta';

  var sec = document.getElementById('asesoria');
  if (!sec) return;
  var activo = !!MATRICULA;

  function set(sel, txt) { sec.querySelectorAll(sel).forEach(function (el) { el.textContent = txt; }); }
  set('[data-as="categoria"]', activo ? 'Agente Productor' : 'Agente Productor · alta en trámite');
  set('[data-as="matricula"]', activo ? 'N° ' + MATRICULA : 'En trámite');
  var legal = sec.querySelector('[data-as="legal"]');
  if (legal) legal.textContent = activo
    ? 'Ignacio Manfredi actúa como Agente Productor registrado ante la Comisión Nacional de Valores (matrícula N° ' + MATRICULA + '), vinculado a Balanz Capital Valores S.A.U. El asesoramiento se brinda según tu perfil de inversor y bajo responsabilidad del Agente Productor. Los honorarios se pactan por escrito antes de empezar. Invertir implica riesgos, incluida la posible pérdida del capital; los rendimientos pasados no garantizan resultados futuros.'
    : 'El alta de Ignacio Manfredi como Agente Productor ante la Comisión Nacional de Valores está en trámite. Hasta completar la inscripción no se brinda asesoramiento personalizado: solo registramos tu consulta y te contactamos cuando esté habilitado. Invertir implica riesgos, incluida la posible pérdida del capital.';
  var sub = sec.querySelector('[data-as="sub"]');
  if (sub && !activo) sub.textContent = 'Dejá tus datos y te escribo apenas esté habilitada la matrícula. La primera charla es sin cargo.';

  var box = sec.querySelector('.as-form'), form = box && box.querySelector('form');
  if (!form) return;
  var msg = box.querySelector('.as-msg'), btn = form.querySelector('.as-btn');

  // Si el usuario ya inició sesión, completar nombre y mail (el login es
  // asíncrono: se intenta al tocar el formulario, no al cargar).
  form.addEventListener('focusin', function () {
    var u = window._currentUser;
    if (!u) return;
    if (u.displayName && !form.nombre.value) form.nombre.value = u.displayName;
    if (u.email && !form.email.value) form.email.value = u.email;
  }, { once: true });

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    msg.textContent = ''; msg.classList.remove('is-err');
    var d = {
      nombre: form.nombre.value.trim(), email: form.email.value.trim(), whatsapp: form.whatsapp.value.trim(),
      experiencia: form.experiencia.value, monto: form.monto.value, objetivo: form.objetivo.value.trim(),
      web: form.web.value // trampa para bots, tiene que llegar vacío
    };
    if (!d.nombre || !d.email || !form.ok.checked) {
      msg.textContent = 'Completá nombre, mail y aceptá que te contactemos.'; msg.classList.add('is-err'); return;
    }
    btn.disabled = true; btn.textContent = 'Enviando…';
    fetch(ENDPOINT, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(d) })
      .then(function (r) { return r.json().catch(function () { return {}; }).then(function (j) { if (!r.ok || !j.ok) throw new Error(j.error || r.status); }); })
      .then(function () {
        box.classList.add('is-sent');
        var n = box.querySelector('[data-as="nombre"]'); if (n) n.textContent = d.nombre.split(' ')[0];
      })
      .catch(function () {
        msg.textContent = 'No se pudo enviar. Probá de nuevo o escribime a manfredi.investment@gmail.com.'; msg.classList.add('is-err');
      })
      .then(function () { btn.disabled = false; btn.textContent = 'Enviar consulta →'; });
  });
})();
