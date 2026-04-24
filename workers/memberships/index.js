// workers/memberships/index.js
// Worker de Cloudflare para manejo de membresías con Mercado Pago

const CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Content-Type': 'application/json',
};

export default {
    async fetch(request, env) {
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

            if (path === '/webhook' && request.method === 'POST') {
                      return await procesarWebhook(request, env);
            }

            if (path === '/verificar-membresia' && request.method === 'GET') {
                      return await verificarMembresia(request, env);
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

// ─── RUTA 1: POST /crear-preferencia ─────────────────────────────────────────
async function crearPreferencia(request, env) {
    const MP_ACCESS_TOKEN = env.MP_ACCESS_TOKEN;
    const SITE_URL = env.SITE_URL;

  if (!MP_ACCESS_TOKEN) {
        return new Response(
                JSON.stringify({ error: 'MP_ACCESS_TOKEN no configurado' }),
          { status: 500, headers: CORS_HEADERS }
              );
  }

  // 1. Obtener cotización del dólar blue desde DolarAPI
  let precioPesos;
    try {
          const dolarResp = await fetch('https://dolarapi.com/v1/dolares/blue');
          if (!dolarResp.ok) throw new Error('Error al consultar DolarAPI');
          const dolarData = await dolarResp.json();
          const cotizacionVenta = dolarData.venta;
          // $10 USD al tipo de cambio blue
      precioPesos = Math.round(10 * cotizacionVenta);
    } catch (err) {
          console.error('DolarAPI error:', err);
          return new Response(
                  JSON.stringify({ error: 'No se pudo obtener la cotización del dólar blue' }),
            { status: 502, headers: CORS_HEADERS }
                );
    }

  // 2. Crear preferencia de pago en Mercado Pago Checkout Pro
  const preferencia = {
        items: [
          {
                    title: 'Membresía Manfredi Investment',
                    description: 'Acceso completo a reportes y Warren IA',
                    quantity: 1,
                    currency_id: 'ARS',
                    unit_price: precioPesos,
          }
              ],
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
                cotizacion_blue: Math.round(precioPesos / 10),
        }),
    { status: 200, headers: CORS_HEADERS }
      );
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

  // Mercado Pago envía notificaciones de tipo "payment"
  const tipo = body.type || body.topic;
    const pagoId = body.data?.id || body.id;

  if (tipo !== 'payment' || !pagoId) {
        // Notificación de otro tipo, ignorar silenciosamente
      return new Response(JSON.stringify({ ok: true }), { status: 200, headers: CORS_HEADERS });
  }

  // Consultar el estado del pago a la API de Mercado Pago
  let pagoData;
    try {
          const pagoResp = await fetch(`https://api.mercadopago.com/v1/payments/${pagoId}`, {
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

  // Obtener el email del pagador
  const email = pagoData.payer?.email;
    if (!email) {
          console.error('Pago aprobado sin email de pagador:', pagoId);
          return new Response(
                  JSON.stringify({ error: 'No se encontró el email del pagador' }),
            { status: 422, headers: CORS_HEADERS }
                );
    }

  // Guardar en KV: email -> "true"
  await env.MEMBERS.put(email.toLowerCase(), 'true');
    console.log(`Membresía activada para: ${email}`);

  return new Response(
        JSON.stringify({ ok: true, email: email }),
    { status: 200, headers: CORS_HEADERS }
      );
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
