// workers/memberships/index.js
// Worker de Cloudflare para manejo de membresías con Mercado Pago

const CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Content-Type': 'application/json',
};

export default {
    async fetch(request, env, ctx) {
          const url = new URL(request.url);
          const path = url.pathname;

      // Manejar preflight CORS
      if (request.method === 'OPTIONS') {
              return new Response(null, { status: 204, headers: CORS_HEADERS });
      }

      try {
              if (path === '/crear-preferencia' && request.method === 'POST') {
                        return await crearPreferencia(request, env);
              }

            if (path === '/crear-suscripcion' && request.method === 'POST') {
                      return await crearSuscripcion(request, env);
            }

            if (path === '/cancelar-suscripcion' && request.method === 'POST') {
                      return await cancelarSuscripcion(request, env);
            }

            if (path === '/mi-suscripcion' && request.method === 'GET') {
                      return await miSuscripcion(request, env);
            }

            if (path === '/webhook' && request.method === 'POST') {
                      return await procesarWebhook(request, env);
            }

            if (path === '/verificar-membresia' && request.method === 'GET') {
                      return await verificarMembresia(request, env);
            }

            if (path === '/pedir-informe' && request.method === 'POST') {
                      return await pedirInforme(request, env, ctx);
            }
            if (path === '/mi-pedido' && request.method === 'GET') {
                      return await miPedido(request, env);
            }
            if (path === '/creador/pedidos' && request.method === 'GET') {
                      return await creadorPedidos(request, env);
            }
            if (path === '/creador/pedido' && request.method === 'POST') {
                      return await creadorActualizar(request, env, ctx);
            }
            if (path === '/creador/resumen' && request.method === 'GET') {
                      return await creadorResumen(request, env);
            }

                        // GET /consultas?email=xxx — devuelve consultas restantes del mes
            if (url.pathname === '/consultas' && request.method === 'GET') {
                const email = url.searchParams.get('email');
                if (!email) {
                    return new Response(JSON.stringify({ error: 'Email requerido' }), { status: 400, headers: CORS_HEADERS });
                }
                const key = email + ':consultas';
                const resetKey = email + ':reset';
                const ahora = new Date();
                const mesActual = ahora.getFullYear() + '-' + String(ahora.getMonth() + 1).padStart(2, '0');
                const mesGuardado = await env.MEMBERS.get(resetKey);
                let consultas;
                if (mesGuardado !== mesActual) {
                    // Reset automático de mes
                    consultas = 100;
                    await env.MEMBERS.put(key, '100');
                    await env.MEMBERS.put(resetKey, mesActual);
                } else {
                    const val = await env.MEMBERS.get(key);
                    consultas = val !== null ? parseInt(val) : 100;
                    if (val === null) {
                        await env.MEMBERS.put(key, '100');
                        await env.MEMBERS.put(resetKey, mesActual);
                    }
                }
                return new Response(JSON.stringify({ consultas, reset: mesActual }), { status: 200, headers: CORS_HEADERS });
            }

            // POST /restar-consulta — resta 1 consulta al usuario
            if (url.pathname === '/restar-consulta' && request.method === 'POST') {
                const body = await request.json();
                const email = body.email;
                if (!email) {
                    return new Response(JSON.stringify({ error: 'Email requerido' }), { status: 400, headers: CORS_HEADERS });
                }
                const key = email + ':consultas';
                const val = await env.MEMBERS.get(key);
                const consultas = val !== null ? parseInt(val) : 100;
                if (consultas <= 0) {
                    return new Response(JSON.stringify({ error: 'No quedan consultas disponibles', consultas: 0 }), { status: 429, headers: CORS_HEADERS });
                }
                const nuevas = consultas - 1;
                await env.MEMBERS.put(key, String(nuevas));
                return new Response(JSON.stringify({ ok: true, consultas: nuevas }), { status: 200, headers: CORS_HEADERS });
            }

return new Response(
                      JSON.stringify({ error: 'Ruta no encontrada' }),
              { status: 404, headers: CORS_HEADERS }
                    );

      } catch (err) {
              console.error('Worker error:', err);
              return new Response(
                        JSON.stringify({ error: 'Error interno del servidor' }),
                { status: 500, headers: CORS_HEADERS }
                      );
      }
    }
};

// Meses prepagos permitidos y códigos de descuento activos (% off sobre el
// total del plan). Todo pago único -- sin recurrencia -- así que el
// descuento nunca se "arrastra" a un cobro futuro.
const PLANES_MESES_VALIDOS = [1, 3, 6, 12];
const CODIGOS_DESCUENTO = {
    'MANFREDI30': 0.30,
};

// ─── RUTA 1: POST /crear-preferencia ─────────────────────────────────────────
// Pago único (no recurrente) por un bloque prepago de N meses de membresía.
// Usada para planes de 3/6/12 meses y para aplicar códigos de descuento --
// la suscripción mensual con auto-renovación sigue yendo por /crear-suscripcion.
async function crearPreferencia(request, env) {
    const MP_ACCESS_TOKEN = env.MP_ACCESS_TOKEN;
    const SITE_URL = env.SITE_URL;

  if (!MP_ACCESS_TOKEN) {
        return new Response(
                JSON.stringify({ error: 'MP_ACCESS_TOKEN no configurado' }),
          { status: 500, headers: CORS_HEADERS }
              );
  }

  let email, meses, codigo;
    try {
          const body = await request.json();
          email = body.email;
          meses = parseInt(body.meses, 10) || 1;
          codigo = (body.codigo || '').trim().toUpperCase();
    } catch { /* body vacío o inválido */ }

  if (!email) {
        return new Response(JSON.stringify({ error: 'Email requerido -- hay que iniciar sesión antes de pagar' }), { status: 400, headers: CORS_HEADERS });
  }
  if (!PLANES_MESES_VALIDOS.includes(meses)) {
        return new Response(JSON.stringify({ error: 'Plan inválido' }), { status: 400, headers: CORS_HEADERS });
  }

  // El % de descuento SIEMPRE se resuelve acá adentro a partir del código
  // recibido -- nunca se confía en un monto o porcentaje mandado por el
  // cliente.
  let descuento = 0;
    if (codigo) {
          if (!CODIGOS_DESCUENTO[codigo]) {
                  return new Response(JSON.stringify({ error: 'Código de descuento inválido' }), { status: 400, headers: CORS_HEADERS });
          }
          descuento = CODIGOS_DESCUENTO[codigo];
    }

  const precioUsdBase = 15 * meses;
    const precioUsdFinal = Math.round(precioUsdBase * (1 - descuento) * 100) / 100;

  // 1. Obtener cotización del dólar blue desde DolarAPI
  let precioPesos;
    try {
          const dolarResp = await fetch('https://dolarapi.com/v1/dolares/blue');
          if (!dolarResp.ok) throw new Error('Error al consultar DolarAPI');
          const dolarData = await dolarResp.json();
          const cotizacionVenta = dolarData.venta;
      precioPesos = Math.round(precioUsdFinal * cotizacionVenta);
    } catch (err) {
          console.error('DolarAPI error:', err);
          return new Response(
                  JSON.stringify({ error: 'No se pudo obtener la cotización del dólar blue' }),
            { status: 502, headers: CORS_HEADERS }
                );
    }

  const tituloMeses = meses === 1 ? '1 mes' : `${meses} meses`;

  // 2. Crear preferencia de pago en Mercado Pago Checkout Pro
  const preferencia = {
        items: [
          {
                    title: `Membresía Manfredi Investment · ${tituloMeses}`,
                    description: codigo
                        ? `Acceso completo a reportes y Warren IA -- código ${codigo} aplicado`
                        : 'Acceso completo a reportes y Warren IA',
                    quantity: 1,
                    currency_id: 'ARS',
                    unit_price: precioPesos,
          }
              ],
        payer: { email },
        metadata: { email: email.toLowerCase(), meses, codigo: codigo || null },
        back_urls: {
                success: `${SITE_URL}?pago=exitoso`,
                failure: `${SITE_URL}?pago=fallido`,
                pending: `${SITE_URL}?pago=pendiente`,
        },
        auto_return: 'approved',
        notification_url: `https://manfredi-memberships.nachito2502.workers.dev/webhook`,
        payment_methods: {
                excluded_payment_types: [],
                installments: 1,
        },
  };

  let mpResp;
    try {
          mpResp = await fetch('https://api.mercadopago.com/checkout/preferences', {
                  method: 'POST',
                  headers: {
                            'Authorization': `Bearer ${MP_ACCESS_TOKEN}`,
                            'Content-Type': 'application/json',
                  },
                  body: JSON.stringify(preferencia),
          });
    } catch (err) {
          console.error('MercadoPago fetch error:', err);
          return new Response(
                  JSON.stringify({ error: 'Error al conectar con Mercado Pago' }),
            { status: 502, headers: CORS_HEADERS }
                );
    }

  if (!mpResp.ok) {
        const errText = await mpResp.text();
        console.error('MercadoPago API error:', mpResp.status, errText);
        return new Response(
                JSON.stringify({ error: 'Error en la API de Mercado Pago', detalle: errText }),
          { status: 502, headers: CORS_HEADERS }
              );
  }

  const mpData = await mpResp.json();

  return new Response(
        JSON.stringify({
                init_point: mpData.init_point,
                precio_pesos: precioPesos,
                precio_usd: precioUsdFinal,
                meses,
                descuento_aplicado: descuento,
                cotizacion_blue: Math.round(precioPesos / precioUsdFinal),
        }),
    { status: 200, headers: CORS_HEADERS }
      );
}

// ─── RUTA 1b: POST /crear-suscripcion ──────────────────────────────────────────
// Suscripción recurrente real via Preapproval de Mercado Pago (a diferencia de
// crear-preferencia, que es un cobro único). El monto en pesos queda fijo desde
// el momento de la suscripción -- MP no lo reajusta solo con el dólar. Para
// subir el precio de los socios NUEVOS alcanza con cambiar el "15" de abajo;
// los que ya estén suscriptos siguen pagando el monto que autorizaron hasta
// que cancelen y se vuelvan a suscribir.
async function crearSuscripcion(request, env) {
    const MP_ACCESS_TOKEN = env.MP_ACCESS_TOKEN;
    const SITE_URL = env.SITE_URL;

    if (!MP_ACCESS_TOKEN) {
        return new Response(JSON.stringify({ error: 'MP_ACCESS_TOKEN no configurado' }), { status: 500, headers: CORS_HEADERS });
    }

    let email;
    try {
        const body = await request.json();
        email = body.email;
    } catch { /* body vacío o inválido, email queda undefined */ }
    if (!email) {
        return new Response(JSON.stringify({ error: 'Email requerido -- hay que iniciar sesión antes de suscribirse' }), { status: 400, headers: CORS_HEADERS });
    }

    let precioPesos;
    try {
        const dolarResp = await fetch('https://dolarapi.com/v1/dolares/blue');
        if (!dolarResp.ok) throw new Error('Error al consultar DolarAPI');
        const dolarData = await dolarResp.json();
        precioPesos = Math.round(15 * dolarData.venta);
    } catch (err) {
        console.error('DolarAPI error:', err);
        return new Response(JSON.stringify({ error: 'No se pudo obtener la cotización del dólar blue' }), { status: 502, headers: CORS_HEADERS });
    }

    const preapproval = {
        reason: 'Membresía Manfredi Investment',
        external_reference: email.toLowerCase(),
        payer_email: email,
        back_url: `${SITE_URL}?suscripcion=exitosa`,
        status: 'pending',
        auto_recurring: {
            frequency: 1,
            frequency_type: 'months',
            transaction_amount: precioPesos,
            currency_id: 'ARS'
        }
    };

    let mpResp;
    try {
        mpResp = await fetch('https://api.mercadopago.com/preapproval', {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${MP_ACCESS_TOKEN}`, 'Content-Type': 'application/json' },
            body: JSON.stringify(preapproval)
        });
    } catch (err) {
        console.error('MercadoPago fetch error (preapproval):', err);
        return new Response(JSON.stringify({ error: 'Error al conectar con Mercado Pago' }), { status: 502, headers: CORS_HEADERS });
    }

    if (!mpResp.ok) {
        const errText = await mpResp.text();
        console.error('MercadoPago API error (preapproval):', mpResp.status, errText);
        return new Response(JSON.stringify({ error: 'Error en la API de Mercado Pago', detalle: errText }), { status: 502, headers: CORS_HEADERS });
    }

    const mpData = await mpResp.json();

    return new Response(
        JSON.stringify({
            init_point: mpData.init_point,
            precio_pesos: precioPesos,
            preapproval_id: mpData.id,
            cotizacion_blue: Math.round(precioPesos / 15),
        }),
        { status: 200, headers: CORS_HEADERS }
    );
}

// ─── RUTA 1c: POST /cancelar-suscripcion ───────────────────────────────────────
async function cancelarSuscripcion(request, env) {
    let email;
    try {
        const body = await request.json();
        email = body.email;
    } catch { /* email queda undefined */ }
    if (!email) {
        return new Response(JSON.stringify({ error: 'Email requerido' }), { status: 400, headers: CORS_HEADERS });
    }
    email = email.toLowerCase();

    const preapprovalId = await env.MEMBERS.get(email + ':preapproval_id');
    if (!preapprovalId) {
        return new Response(JSON.stringify({ error: 'No se encontró una suscripción activa para este email' }), { status: 404, headers: CORS_HEADERS });
    }

    let cancelRes;
    try {
        cancelRes = await fetch(`https://api.mercadopago.com/preapproval/${preapprovalId}`, {
            method: 'PUT',
            headers: { 'Authorization': `Bearer ${env.MP_ACCESS_TOKEN}`, 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: 'cancelled' })
        });
    } catch (err) {
        console.error('Error cancelando preapproval en MP:', err);
        return new Response(JSON.stringify({ error: 'No se pudo cancelar la suscripción en Mercado Pago' }), { status: 502, headers: CORS_HEADERS });
    }
    if (!cancelRes.ok) {
        const errText = await cancelRes.text();
        console.error('MercadoPago API error (cancel preapproval):', cancelRes.status, errText);
        return new Response(JSON.stringify({ error: 'Error en la API de Mercado Pago', detalle: errText }), { status: 502, headers: CORS_HEADERS });
    }

    // No revocamos el acceso ya mismo -- el usuario ya pagó este período, así
    // que sigue teniendo acceso hasta que expire el TTL de 31 días seteado en
    // el último cobro aprobado (activarMembresia). Solo cortamos la
    // recurrencia borrando el preapproval_id, así no se genera el próximo cobro.
    await env.MEMBERS.delete(email + ':preapproval_id');

    env.LOGUSER.fetch('https://log-user/marcar-miembro', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, accion: 'cancelacion' })
    }).catch(err => console.error('Error marcando cancelación en Sheets:', err));

    return new Response(JSON.stringify({ ok: true }), { status: 200, headers: CORS_HEADERS });
}

// ─── RUTA 1d: GET /mi-suscripcion?email=xxx ────────────────────────────────────
// Le dice al frontend si este email tiene una suscripción recurrente activa,
// para decidir si mostrar el botón de "Cancelar membresía".
async function miSuscripcion(request, env) {
    const url = new URL(request.url);
    const email = url.searchParams.get('email');
    if (!email) {
        return new Response(JSON.stringify({ error: 'Parámetro email requerido' }), { status: 400, headers: CORS_HEADERS });
    }
    const preapprovalId = await env.MEMBERS.get(email.toLowerCase() + ':preapproval_id');
    return new Response(JSON.stringify({ tieneSuscripcion: !!preapprovalId }), { status: 200, headers: CORS_HEADERS });
}

// Marca a un email como miembro activo (KV con TTL de 31 días -- cada cobro
// recurrente exitoso vuelve a llamar esto y refresca el TTL, así que mientras
// los cobros mensuales sigan aprobándose el acceso nunca llega a vencer).
// esNueva=true dispara el mail de bienvenida completo; en una renovación
// mensual normal no lo mandamos de nuevo para no ser spam.
async function activarMembresia(email, env, { esNueva, monto, preapprovalId, meses } = {}) {
    email = email.toLowerCase();
    // 31 días por mes pagado -- un prepago de 6 meses, por ejemplo, extiende
    // el TTL a 186 días en vez de los 31 días de una renovación mensual.
    const ttlDias = 31 * (meses && meses > 0 ? meses : 1);
    await env.MEMBERS.put(email, 'true', { expirationTtl: ttlDias * 86400 });
    if (preapprovalId) await env.MEMBERS.put(email + ':preapproval_id', preapprovalId);

    env.LOGUSER.fetch('https://log-user/marcar-miembro', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, accion: esNueva ? 'alta' : 'renovacion', monto })
    }).catch(err => console.error('Error marcando miembro en Sheets:', err));

    if (!esNueva) {
        console.log(`Membresía renovada para: ${email}`);
        return;
    }

    // Notificación a Nacho (solo en altas nuevas, no en cada renovación mensual)
    fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${env.RESEND_API_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        from: 'Manfredi Investment <hola@manfredinvestment.com>',
        to: 'nachito2502@gmail.com',
        subject: '💰 Nuevo miembro en Manfredi Investment',
        html: `<h2>Nuevo miembro registrado</h2><p><strong>Email:</strong> ${email}</p><p><strong>Fecha:</strong> ${new Date().toLocaleString('es-AR', { timeZone: 'America/Argentina/Buenos_Aires' })}</p>`
      })
    }).catch(err => console.error('Error enviando email:', err));

      // Email al pagador con confirmación de membresía (fire-and-forget)
      fetch('https://api.resend.com/emails', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${env.RESEND_API_KEY}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          from: 'Manfredi Investment <hola@manfredinvestment.com>',
          to: email,
          subject: '¡Bienvenido a Manfredi Investment Premium!',
          html: `<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head><body style="margin:0;padding:0;background-color:#0a0e1a;font-family:'Helvetica Neue',Arial,sans-serif;"><table width="100%" cellpadding="0" cellspacing="0" style="background-color:#0a0e1a;padding:40px 20px;"><tr><td align="center"><table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background-color:#111827;border:1px solid #B8943F;border-radius:8px;overflow:hidden;"><tr><td style="background-color:#0d1424;padding:32px 40px;border-bottom:1px solid #B8943F;"><table cellpadding="0" cellspacing="0"><tr><td style="background-color:#B8943F;width:40px;height:40px;border-radius:4px;text-align:center;vertical-align:middle;"><span style="color:#0a0e1a;font-weight:700;font-size:16px;line-height:40px;">MI</span></td><td style="padding-left:12px;vertical-align:middle;"><span style="color:#ffffff;font-size:18px;font-weight:600;letter-spacing:0.5px;">Manfredi Investment</span><br><span style="color:#B8943F;font-size:11px;letter-spacing:2px;text-transform:uppercase;">Research &amp; Markets</span></td></tr></table></td></tr><tr><td style="padding:40px;"><p style="color:#B8943F;font-size:11px;letter-spacing:2px;text-transform:uppercase;margin:0 0 12px 0;">Membresía activada</p><h1 style="color:#ffffff;font-size:24px;font-weight:600;margin:0 0 16px 0;">Su acceso Premium está activo</h1><p style="color:#9ca3af;font-size:15px;line-height:1.6;margin:0 0 32px 0;">Su pago fue procesado exitosamente. A partir de este momento tiene acceso completo a todas las funcionalidades de Manfredi Investment.</p><table cellpadding="0" cellspacing="0" style="background-color:#0d1424;border:1px solid #B8943F;border-radius:6px;width:100%;margin-bottom:32px;"><tr><td style="padding:24px;"><p style="color:#B8943F;font-size:11px;letter-spacing:2px;text-transform:uppercase;margin:0 0 16px 0;">Su membresía incluye</p><table cellpadding="0" cellspacing="0"><tr><td style="padding:7px 0;color:#d1d5db;font-size:14px;">&#10003; &nbsp;Informes de análisis en profundidad</td></tr><tr><td style="padding:7px 0;color:#d1d5db;font-size:14px;">&#10003; &nbsp;Warren IA — Asesor financiero con inteligencia artificial</td></tr><tr><td style="padding:7px 0;color:#d1d5db;font-size:14px;">&#10003; &nbsp;Seguimiento de inversiones con métricas avanzadas</td></tr><tr><td style="padding:7px 0;color:#d1d5db;font-size:14px;">&#10003; &nbsp;Reportes diarios prioritarios</td></tr></table></td></tr></table><table cellpadding="0" cellspacing="0" style="width:100%;margin-bottom:32px;"><tr><td align="center" style="background-color:#B8943F;border-radius:4px;padding:14px 28px;"><a href="https://manfredinvestment.com" style="color:#0a0e1a;font-size:15px;font-weight:700;text-decoration:none;letter-spacing:0.5px;">Acceder a la plataforma</a></td></tr></table><table cellpadding="0" cellspacing="0" style="background-color:#0d1424;border:1px solid #1e2d4a;border-radius:6px;width:100%;margin-bottom:32px;"><tr><td style="padding:20px 24px;"><p style="color:#6b7280;font-size:12px;margin:0 0 4px 0;text-transform:uppercase;letter-spacing:1px;">Detalle del pago</p><p style="color:#d1d5db;font-size:13px;margin:0;">Membresía mensual · Renovación automática</p></td></tr></table><p style="color:#6b7280;font-size:13px;line-height:1.6;margin:0;">Podés cancelar cuando quieras desde tu cuenta en la plataforma. Ante cualquier consulta puede responder este correo o contactarnos directamente.</p></td></tr><tr><td style="background-color:#0d1424;padding:20px 40px;border-top:1px solid #1e2d4a;text-align:center;"><p style="color:#4b5563;font-size:12px;margin:0;">© 2026 Manfredi Investment · Buenos Aires, Argentina</p></td></tr></table></td></tr></table></body></html>`
        })
      }).catch(err => console.error('Error enviando email membresía:', err));
    console.log(`Membresía activada para: ${email}`);
}

// ─── RUTA 2: POST /webhook ────────────────────────────────────────────────────
async function procesarWebhook(request, env) {
    let body;
    try {
          body = await request.json();
    } catch {
          return new Response(
                  JSON.stringify({ error: 'Body inválido' }),
            { status: 400, headers: CORS_HEADERS }
                );
    }

  // Validar firma de Mercado Pago
  const xSignature = request.headers.get('x-signature');
  const xRequestId = request.headers.get('x-request-id');
  const urlParams = new URL(request.url).searchParams;
  const dataId = urlParams.get('data.id') || (body.data && body.data.id) || body.id || '';

  if (xSignature && env.MP_WEBHOOK_SECRET) {
    const parts = xSignature.split(',');
    let ts = '', v1 = '';
    parts.forEach(part => {
      const [key, val] = part.trim().split('=');
      if (key === 'ts') ts = val;
      if (key === 'v1') v1 = val;
    });
    const manifest = `id:${dataId};request-id:${xRequestId};ts:${ts};`;
    const encoder = new TextEncoder();
    const keyData = encoder.encode(env.MP_WEBHOOK_SECRET);
    const msgData = encoder.encode(manifest);
    const cryptoKey = await crypto.subtle.importKey('raw', keyData, { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
    const signature = await crypto.subtle.sign('HMAC', cryptoKey, msgData);
    const hashArray = Array.from(new Uint8Array(signature));
    const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
    if (hashHex !== v1) {
      return new Response(JSON.stringify({ error: 'Firma inválida' }), { status: 401, headers: CORS_HEADERS });
    }
  }

  const tipo = body.type || body.topic;
  const notifId = body.data?.id || body.id;
  console.error('[memberships] webhook recibido, tipo:', tipo, 'id:', notifId);

  if (tipo === 'subscription_preapproval') {
    return await procesarNotifPreapproval(notifId, env);
  }

  if (tipo === 'subscription_authorized_payment') {
    return await procesarNotifCobroRecurrente(notifId, env);
  }

  if (tipo !== 'payment' || !notifId) {
        // Notificación de otro tipo, ignorar silenciosamente
      return new Response(JSON.stringify({ ok: true }), { status: 200, headers: CORS_HEADERS });
  }

  // Consultar el estado del pago a la API de Mercado Pago (cobro único, flujo
  // viejo de crear-preferencia -- se deja andando por compatibilidad).
  let pagoData;
    try {
          const pagoResp = await fetch(`https://api.mercadopago.com/v1/payments/${notifId}`, {
                  headers: { 'Authorization': `Bearer ${env.MP_ACCESS_TOKEN}` },
          });
          if (!pagoResp.ok) throw new Error(`MP status ${pagoResp.status}`);
          pagoData = await pagoResp.json();
    } catch (err) {
          console.error('Error consultando pago MP:', err);
          return new Response(
                  JSON.stringify({ error: 'No se pudo verificar el pago' }),
            { status: 502, headers: CORS_HEADERS }
                );
    }

  // Solo procesar pagos aprobados
  if (pagoData.status !== 'approved') {
        return new Response(JSON.stringify({ ok: true, estado: pagoData.status }), { status: 200, headers: CORS_HEADERS });
  }

  // Obtener el email del pagador -- preferimos el que mandamos nosotros en
  // metadata al crear la preferencia (payer.email a veces no vuelve completo
  // según el método de pago usado, ej. algunos medios en efectivo).
  const email = pagoData.metadata?.email || pagoData.payer?.email;
    if (!email) {
          console.error('Pago aprobado sin email de pagador:', notifId);
          return new Response(
                  JSON.stringify({ error: 'No se encontró el email del pagador' }),
            { status: 422, headers: CORS_HEADERS }
                );
    }

  const meses = pagoData.metadata?.meses || 1;
    const yaEraMiembro = (await env.MEMBERS.get(email.toLowerCase())) === 'true';
    await activarMembresia(email, env, { esNueva: !yaEraMiembro, monto: pagoData.transaction_amount, meses });

  return new Response(
        JSON.stringify({ ok: true, email: email.toLowerCase() }),
    { status: 200, headers: CORS_HEADERS }
      );
}

// Notificación "subscription_preapproval": se creó, autorizó, pausó o
// canceló una suscripción. El id que llega es el id del preapproval mismo.
async function procesarNotifPreapproval(preapprovalId, env) {
    if (!preapprovalId) return new Response(JSON.stringify({ ok: true }), { status: 200, headers: CORS_HEADERS });

    let preData;
    try {
        const res = await fetch(`https://api.mercadopago.com/preapproval/${preapprovalId}`, {
            headers: { 'Authorization': `Bearer ${env.MP_ACCESS_TOKEN}` }
        });
        if (!res.ok) throw new Error(`MP status ${res.status}`);
        preData = await res.json();
        console.error('[memberships] preapproval', preapprovalId, 'status:', preData.status, 'payer:', preData.payer_email);
    } catch (err) {
        console.error('Error consultando preapproval MP:', err);
        return new Response(JSON.stringify({ error: 'No se pudo verificar la suscripción' }), { status: 502, headers: CORS_HEADERS });
    }

    // payer_email suele venir vacío una vez autorizado el preapproval (aunque
    // se haya mandado en la creación) -- confirmado probando contra la API
    // real. external_reference es propio nuestro (lo seteamos en
    // crearSuscripcion como el email en minúsculas) y sí sobrevive, así que
    // es la fuente confiable.
    const email = preData.external_reference || preData.payer_email || preData.payerEmail;
    if (!email) {
        console.error('Preapproval sin email resoluble (ni external_reference ni payer_email):', preapprovalId);
        return new Response(JSON.stringify({ ok: true }), { status: 200, headers: CORS_HEADERS });
    }

    if (preData.status === 'authorized') {
        // Si ya era miembro activo, esto es una renovación mensual (llega vía
        // subscription_authorized_payment), no un alta -- no hay que remandar
        // el mail de bienvenida cada mes.
        const yaEraMiembro = (await env.MEMBERS.get(email.toLowerCase())) === 'true';
        await activarMembresia(email, env, {
            esNueva: !yaEraMiembro,
            monto: preData.auto_recurring?.transaction_amount,
            preapprovalId
        });
    } else if (preData.status === 'cancelled') {
        // Cancelación voluntaria (o disparada por cancelarSuscripcion): dejamos
        // que el acceso siga vivo hasta que expire el TTL del último período
        // pagado -- solo cortamos la recurrencia para que no se genere el
        // próximo cobro. Ver mismo criterio en cancelarSuscripcion().
        await env.MEMBERS.delete(email.toLowerCase() + ':preapproval_id');
        env.LOGUSER.fetch('https://log-user/marcar-miembro', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: email.toLowerCase(), accion: 'cancelacion' })
        }).catch(err => console.error('Error marcando cancelación en Sheets:', err));
        console.log(`Membresía dada de baja (${preData.status}) para: ${email}`);
    } else if (preData.status === 'paused') {
        // Pausa (típicamente por fallas de cobro, no por acción del usuario):
        // acá sí cortamos el acceso ya mismo porque no hay un período pagado
        // que respetar.
        await env.MEMBERS.delete(email.toLowerCase());
        await env.MEMBERS.delete(email.toLowerCase() + ':preapproval_id');
        env.LOGUSER.fetch('https://log-user/marcar-miembro', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: email.toLowerCase(), accion: 'cancelacion' })
        }).catch(err => console.error('Error marcando cancelación en Sheets:', err));
        console.log(`Membresía dada de baja (${preData.status}) para: ${email}`);
    }

    return new Response(JSON.stringify({ ok: true, email: email.toLowerCase(), estado: preData.status }), { status: 200, headers: CORS_HEADERS });
}

// Notificación "subscription_authorized_payment": se procesó un cobro
// recurrente (mensual). No confiamos en el campo de estado de este recurso
// puntual -- resolvemos el preapproval asociado y usamos SU estado (que sí
// está documentado y es la fuente de verdad) para decidir si renovar.
async function procesarNotifCobroRecurrente(cobroId, env) {
    if (!cobroId) return new Response(JSON.stringify({ ok: true }), { status: 200, headers: CORS_HEADERS });

    let cobroData;
    try {
        const res = await fetch(`https://api.mercadopago.com/authorized_payments/${cobroId}`, {
            headers: { 'Authorization': `Bearer ${env.MP_ACCESS_TOKEN}` }
        });
        if (!res.ok) throw new Error(`MP status ${res.status}`);
        cobroData = await res.json();
        console.error('[memberships] authorized_payment', cobroId, JSON.stringify(cobroData));
    } catch (err) {
        console.error('Error consultando authorized_payment MP:', err);
        return new Response(JSON.stringify({ error: 'No se pudo verificar el cobro recurrente' }), { status: 502, headers: CORS_HEADERS });
    }

    const preapprovalId = cobroData.preapproval_id;
    if (!preapprovalId) {
        console.error('authorized_payment sin preapproval_id:', cobroId);
        return new Response(JSON.stringify({ ok: true }), { status: 200, headers: CORS_HEADERS });
    }

    return await procesarNotifPreapproval(preapprovalId, env);
}

// ─── RUTA 3: GET /verificar-membresia?email=xxx ───────────────────────────────
async function verificarMembresia(request, env) {
    const url = new URL(request.url);
    const email = url.searchParams.get('email');

  if (!email) {
        return new Response(
                JSON.stringify({ error: 'Parámetro email requerido' }),
          { status: 400, headers: CORS_HEADERS }
              );
  }

  const valor = await env.MEMBERS.get(email.toLowerCase());
    const esMiembro = valor === 'true';

  return new Response(
        JSON.stringify({ miembro: esMiembro }),
    { status: 200, headers: CORS_HEADERS }
      );
}

// ─── Rol "creador" + pedidos de informes ──────────────────────────────────────
// Los creadores (hoy solo Nacho) ven y gestionan los pedidos de los socios.
// La identidad sale SIEMPRE del ID token de Firebase (header Authorization),
// nunca de un email mandado en el body -- si no, cualquiera podria leer los
// pedidos o gastar el cupo de otro socio.
const CREADORES = ['nachito2502@gmail.com'];
const FIREBASE_PROJECT = 'manfrediinvestment-989c8';
const PLAZO_HORAS = 48;
const json = (obj, status = 200) => new Response(JSON.stringify(obj), { status, headers: CORS_HEADERS });

let _jwksCache = { keys: null, exp: 0 };
async function firebaseKeys() {
    if (_jwksCache.keys && Date.now() < _jwksCache.exp) return _jwksCache.keys;
    const r = await fetch('https://www.googleapis.com/service_accounts/v1/jwk/securetoken@system.gserviceaccount.com');
    const { keys } = await r.json();
    const m = /max-age=(\d+)/.exec(r.headers.get('cache-control') || '');
    _jwksCache = { keys, exp: Date.now() + (m ? +m[1] : 3600) * 1000 };
    return keys;
}
function b64urlBytes(s) {
    s = s.replace(/-/g, '+').replace(/_/g, '/'); while (s.length % 4) s += '=';
    return Uint8Array.from(atob(s), c => c.charCodeAt(0));
}
// Devuelve { email, nombre } si el token es valido; null si no.
async function usuarioDelToken(request) {
    const auth = request.headers.get('Authorization') || '';
    const token = auth.startsWith('Bearer ') ? auth.slice(7) : '';
    const parts = token.split('.');
    if (parts.length !== 3) return null;
    try {
        const header = JSON.parse(new TextDecoder().decode(b64urlBytes(parts[0])));
        const p = JSON.parse(new TextDecoder().decode(b64urlBytes(parts[1])));
        const now = Math.floor(Date.now() / 1000);
        if (header.alg !== 'RS256' || p.aud !== FIREBASE_PROJECT || p.iss !== 'https://securetoken.google.com/' + FIREBASE_PROJECT) return null;
        if (!p.exp || p.exp < now || !p.email || p.email_verified === false) return null;
        const jwk = (await firebaseKeys()).find(k => k.kid === header.kid);
        if (!jwk) return null;
        const key = await crypto.subtle.importKey('jwk', jwk, { name: 'RSASSA-PKCS1-v1_5', hash: 'SHA-256' }, false, ['verify']);
        const ok = await crypto.subtle.verify('RSASSA-PKCS1-v1_5', key, b64urlBytes(parts[2]), new TextEncoder().encode(parts[0] + '.' + parts[1]));
        return ok ? { email: String(p.email).toLowerCase(), nombre: p.name || '' } : null;
    } catch (e) { return null; }
}
const esCreador = email => CREADORES.includes(email);
const mesART = () => new Date().toLocaleDateString('en-CA', { timeZone: 'America/Argentina/Buenos_Aires' }).slice(0, 7);
const fechaART = iso => new Date(iso).toLocaleString('es-AR', { timeZone: 'America/Argentina/Buenos_Aires', day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit', hourCycle: 'h23' }) + ' hs';
function esc(s) { return String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c])); }
async function mail(env, to, subject, html, extra = {}) {
    try {
        await fetch('https://api.resend.com/emails', {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${env.RESEND_API_KEY}`, 'Content-Type': 'application/json' },
            body: JSON.stringify({ from: 'Manfredi Investment <hola@manfredinvestment.com>', to, subject, html, ...extra })
        });
    } catch (err) { console.error('Error enviando email:', err); }
}
// Cada pedido vive en `pedido:<id>` (valor JSON + el mismo objeto como metadata,
// asi el listado del creador sale de un solo list() sin N lecturas). El cupo
// mensual del socio es `email:pedido:YYYY-MM` -> id del pedido.
async function guardarPedido(env, p) {
    await env.MEMBERS.put('pedido:' + p.id, JSON.stringify(p), { metadata: p });
}

// POST /pedir-informe  { ticker }  -- socio (o creador) logueado
async function pedirInforme(request, env, ctx) {
    const u = await usuarioDelToken(request);
    if (!u) return json({ error: 'Iniciá sesión para pedir un informe' }, 401);
    const body = await request.json().catch(() => ({}));
    const ticker = String(body.ticker || '').trim().toUpperCase().slice(0, 12);
    if (!ticker || !/^[A-Z0-9.\- ]+$/.test(ticker)) return json({ error: 'Ticker inválido' }, 400);

    const creador = esCreador(u.email);
    if (!creador && (await env.MEMBERS.get(u.email)) !== 'true') return json({ error: 'Solo para socios' }, 403);

    const cupoKey = `${u.email}:pedido:${mesART()}`;
    const previoId = await env.MEMBERS.get(cupoKey);
    if (previoId && !creador) {
        const previo = JSON.parse((await env.MEMBERS.get('pedido:' + previoId)) || '{}');
        return json({ error: 'Ya usaste tu pedido de este mes', pedido: previo }, 429);
    }

    const ahora = new Date();
    const p = {
        id: ahora.getTime().toString(36) + Math.random().toString(36).slice(2, 6),
        ticker, email: u.email, nombre: u.nombre.slice(0, 60),
        creado: ahora.toISOString(),
        vence: new Date(ahora.getTime() + PLAZO_HORAS * 3600e3).toISOString(),
        estado: 'pendiente', url: ''
    };
    await guardarPedido(env, p);
    if (!creador) await env.MEMBERS.put(cupoKey, p.id, { expirationTtl: 60 * 60 * 24 * 45 });

    const aviso = mail(env, CREADORES, `📊 Pedido de informe: ${ticker} (vence ${fechaART(p.vence)})`,
        `<h2>Nuevo pedido de informe</h2><p><strong>Ticker:</strong> ${esc(ticker)}</p><p><strong>Socio:</strong> ${esc(u.nombre)} &lt;${esc(u.email)}&gt;</p><p><strong>Plazo máximo:</strong> ${fechaART(p.vence)} (${PLAZO_HORAS} hs)</p><p>Lo gestionás desde el Panel de creador en la sección Informes.</p>`,
        { reply_to: u.email });
    if (ctx && ctx.waitUntil) ctx.waitUntil(aviso);
    return json({ ok: true, pedido: p, plazoHoras: PLAZO_HORAS });
}

// GET /mi-pedido -- el pedido del mes del socio logueado (para mostrar su estado)
async function miPedido(request, env) {
    const u = await usuarioDelToken(request);
    if (!u) return json({ error: 'No autenticado' }, 401);
    const id = await env.MEMBERS.get(`${u.email}:pedido:${mesART()}`);
    const p = id ? JSON.parse((await env.MEMBERS.get('pedido:' + id)) || 'null') : null;
    return json({ pedido: p, creador: esCreador(u.email), plazoHoras: PLAZO_HORAS });
}

// GET /creador/pedidos -- todos los pedidos (solo creadores)
async function creadorPedidos(request, env) {
    const u = await usuarioDelToken(request);
    if (!u) return json({ error: 'No autenticado' }, 401);
    if (!esCreador(u.email)) return json({ error: 'Solo para creadores' }, 403);
    const pedidos = [];
    let cursor;
    do {
        const r = await env.MEMBERS.list({ prefix: 'pedido:', cursor });
        r.keys.forEach(k => { if (k.metadata) pedidos.push(k.metadata); });
        cursor = r.list_complete ? null : r.cursor;
    } while (cursor);
    pedidos.sort((a, b) => b.creado.localeCompare(a.creado));
    return json({ pedidos, plazoHoras: PLAZO_HORAS });
}

// POST /creador/pedido  { id, estado, url? } -- cambia el estado; 'hecho' avisa al socio
async function creadorActualizar(request, env, ctx) {
    const u = await usuarioDelToken(request);
    if (!u) return json({ error: 'No autenticado' }, 401);
    if (!esCreador(u.email)) return json({ error: 'Solo para creadores' }, 403);
    const body = await request.json().catch(() => ({}));
    const raw = await env.MEMBERS.get('pedido:' + String(body.id || ''));
    if (!raw) return json({ error: 'Pedido no encontrado' }, 404);
    const p = JSON.parse(raw);

    if (body.estado === 'borrar') {
        await env.MEMBERS.delete('pedido:' + p.id);
        return json({ ok: true, borrado: p.id });
    }
    if (!['pendiente', 'en_proceso', 'hecho', 'rechazado'].includes(body.estado)) return json({ error: 'Estado inválido' }, 400);
    const url = String(body.url || '').trim();
    if (body.estado === 'hecho' && url && !/^https:\/\/(www\.)?manfredinvestment\.com\//.test(url)) return json({ error: 'El link tiene que ser de manfredinvestment.com' }, 400);

    const avisar = body.estado === 'hecho' && p.estado !== 'hecho' && p.email !== u.email;
    p.estado = body.estado;
    if (url) p.url = url;
    p.actualizado = new Date().toISOString();
    if (p.estado === 'hecho') p.hecho = p.actualizado;
    await guardarPedido(env, p);

    if (avisar) {
        const link = p.url || 'https://manfredinvestment.com/#inversiones';
        const envio = mail(env, p.email, `Tu informe de ${p.ticker} ya está publicado`,
            `<div style="font-family:Arial,sans-serif;background:#0a0e1a;padding:32px"><div style="max-width:560px;margin:0 auto;background:#111827;border:1px solid #B8943F;border-radius:8px;padding:32px"><p style="color:#B8943F;font-size:11px;letter-spacing:2px;text-transform:uppercase;margin:0 0 12px">Tu pedido de informe</p><h1 style="color:#fff;font-size:22px;margin:0 0 14px">El informe de ${esc(p.ticker)} ya está online</h1><p style="color:#9ca3af;font-size:15px;line-height:1.6;margin:0 0 24px">Hola${p.nombre ? ' ' + esc(p.nombre.split(' ')[0]) : ''}, terminamos el informe institucional que pediste: tesis, estados financieros, valuación y fair value.</p><a href="${esc(link)}" style="display:inline-block;background:#B8943F;color:#0a0e1a;font-weight:700;text-decoration:none;padding:13px 26px;border-radius:4px">Leer el informe</a><p style="color:#6b7280;font-size:12px;margin:28px 0 0">Tu próximo pedido se habilita el 1° del mes que viene.</p></div></div>`);
        if (ctx && ctx.waitUntil) ctx.waitUntil(envio);
    }
    return json({ ok: true, pedido: p });
}

// GET /creador/resumen -- datos del negocio para el Panel de creador (solo creadores).
// Todo sale de lo que este worker ya maneja: KV de socios + API de Mercado Pago.
async function creadorResumen(request, env) {
    const u = await usuarioDelToken(request);
    if (!u) return json({ error: 'No autenticado' }, 401);
    if (!esCreador(u.email)) return json({ error: 'Solo para creadores' }, 403);

    const keys = [];
    let cursor;
    do {
        const r = await env.MEMBERS.list({ cursor });
        keys.push(...r.keys);
        cursor = r.list_complete ? null : r.cursor;
    } while (cursor);

    // Socio activo = clave `email` (sin ':'); su TTL es el vencimiento del periodo pago.
    const conRecurrente = new Set(keys.filter(k => k.name.endsWith(':preapproval_id')).map(k => k.name.slice(0, -15)));
    const socios = keys.filter(k => !k.name.includes(':') && k.name.includes('@')).map(k => ({
        email: k.name,
        vence: k.expiration ? new Date(k.expiration * 1000).toISOString() : null,
        recurrente: conRecurrente.has(k.name)
    }));
    const pedidos = keys.filter(k => k.name.startsWith('pedido:') && k.metadata).map(k => k.metadata);

    // Warren: `email:consultas` guarda las RESTANTES del mes (arranca en 100) y `email:reset` el mes.
    const mesWarren = new Date().getFullYear() + '-' + String(new Date().getMonth() + 1).padStart(2, '0');
    const emailsWarren = keys.filter(k => k.name.endsWith(':consultas')).map(k => k.name.slice(0, -10)).slice(0, 400);
    const warren = (await Promise.all(emailsWarren.map(async email => {
        const [rest, mes] = await Promise.all([env.MEMBERS.get(email + ':consultas'), env.MEMBERS.get(email + ':reset')]);
        return { email, usadas: mes === mesWarren ? Math.max(0, 100 - parseInt(rest || '100', 10)) : 0, mes };
    }))).filter(w => w.usadas > 0).sort((a, b) => b.usadas - a.usadas);

    const errores = {};
    let pagos = [], suscripciones = [];
    if (env.MP_ACCESS_TOKEN) {
        const mp = path => fetch('https://api.mercadopago.com' + path, { headers: { Authorization: 'Bearer ' + env.MP_ACCESS_TOKEN } }).then(r => r.ok ? r.json() : Promise.reject(new Error('MP ' + r.status)));
        try {
            for (let offset = 0; offset < 500; offset += 100) {
                const d = await mp(`/v1/payments/search?sort=date_created&criteria=desc&range=date_created&begin_date=NOW-180DAYS&end_date=NOW&limit=100&offset=${offset}`);
                (d.results || []).forEach(p => pagos.push({
                    fecha: p.date_approved || p.date_created, estado: p.status, detalle: p.status_detail,
                    monto: p.transaction_amount, moneda: p.currency_id,
                    email: (p.metadata && p.metadata.email) || p.external_reference || (p.payer && p.payer.email) || '',
                    concepto: p.description || '', meses: p.metadata && p.metadata.meses, codigo: p.metadata && p.metadata.codigo
                }));
                if (!d.results || d.results.length < 100) break;
            }
        } catch (e) { errores.pagos = e.message; }
        try {
            const d = await mp('/preapproval/search?limit=100&offset=0');
            suscripciones = (d.results || []).map(s => ({
                email: s.external_reference || s.payer_email || '', estado: s.status,
                monto: s.auto_recurring && s.auto_recurring.transaction_amount, moneda: s.auto_recurring && s.auto_recurring.currency_id,
                creado: s.date_created, proximo: s.next_payment_date
            }));
        } catch (e) { errores.suscripciones = e.message; }
    } else {
        errores.pagos = errores.suscripciones = 'MP_ACCESS_TOKEN no configurado';
    }

    return json({ generado: new Date().toISOString(), socios, pedidos, warren, pagos, suscripciones, errores });
}
