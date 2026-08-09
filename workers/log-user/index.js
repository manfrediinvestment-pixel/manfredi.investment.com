export default {
        async fetch(request, env) {
                  const headers = {
                              'Access-Control-Allow-Origin': '*',
                              'Access-Control-Allow-Headers': 'Content-Type',
                              'Access-Control-Allow-Methods': 'POST, OPTIONS'
                  };

          if (request.method === 'OPTIONS') return new Response('', { headers });
                  if (request.method !== 'POST') return new Response('Method Not Allowed', { status: 405, headers });
                  const pathname = new URL(request.url).pathname;

          // Ruta para avisar por mail a todos los usuarios registrados de un informe nuevo
          if (pathname === '/avisar-informe') {
              return await avisarInforme(request, env, headers);
          }

          // Ruta para marcar usuario como miembro
          if (new URL(request.url).pathname === '/marcar-miembro') {
                      const { email, accion, monto } = await request.json();
                      if (!email) return new Response(JSON.stringify({ error: 'Email requerido' }), { status: 400, headers });

                    // Reusar lÃ³gica de autenticaciÃ³n Google
                    const privateKey = env.GOOGLE_PRIVATE_KEY.replace(/\\n/g, '\n');
                      const serviceEmail = env.GOOGLE_SERVICE_ACCOUNT_EMAIL;
                      const sheetId = env.GOOGLE_SHEETS_ID;

                    const now = Math.floor(Date.now() / 1000);
                      const jwtHeader = btoa(JSON.stringify({ alg: 'RS256', typ: 'JWT' })).replace(/=/g,'').replace(/\+/g,'-').replace(/\//g,'_');
                      const jwtPayload = btoa(JSON.stringify({
                                    iss: serviceEmail,
                                    scope: 'https://www.googleapis.com/auth/spreadsheets',
                                    aud: 'https://oauth2.googleapis.com/token',
                                    exp: now + 3600,
                                    iat: now
                      })).replace(/=/g,'').replace(/\+/g,'-').replace(/\//g,'_');

                    const pemBody = privateKey.replace(/-----BEGIN PRIVATE KEY-----|-----END PRIVATE KEY-----|\n/g, '');
                      const binaryKey = Uint8Array.from(atob(pemBody), c => c.charCodeAt(0));
                      const cryptoKey = await crypto.subtle.importKey('pkcs8', binaryKey.buffer, { name: 'RSASSA-PKCS1-v1_5', hash: 'SHA-256' }, false, ['sign']);
                      const sigBuffer = await crypto.subtle.sign('RSASSA-PKCS1-v1_5', cryptoKey, new TextEncoder().encode(`${jwtHeader}.${jwtPayload}`));
                      const sig = btoa(String.fromCharCode(...new Uint8Array(sigBuffer))).replace(/=/g,'').replace(/\+/g,'-').replace(/\//g,'_');
                      const jwt = `${jwtHeader}.${jwtPayload}.${sig}`;

                    const tokenRes = await fetch('https://oauth2.googleapis.com/token', {
                                  method: 'POST',
                                  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                                  body: `grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer&assertion=${jwt}`
                    });
                      const { access_token } = await tokenRes.json();

                    // Obtener sheetId numÃ©rico de la hoja "Usuarios"
                    const sheetMetaRes = await fetch(
                                  `https://sheets.googleapis.com/v4/spreadsheets/${sheetId}?fields=sheets.properties`,
                          { headers: { 'Authorization': `Bearer ${access_token}` } }
                                );
                      const sheetMeta = await sheetMetaRes.json();
                      let usuariosSheetId = 0;
                      if (sheetMeta.sheets) {
                                    for (const sheet of sheetMeta.sheets) {
                                                    if (sheet.properties && sheet.properties.title === 'Usuarios') {
                                                                      usuariosSheetId = sheet.properties.sheetId;
                                                                      break;
                                                    }
                                    }
                      }

                    if (accion !== 'cancelacion') {
                    // Buscar fila por email
                    const searchRes = await fetch(
                                  `https://sheets.googleapis.com/v4/spreadsheets/${sheetId}/values/Usuarios!A:B`,
                          { headers: { 'Authorization': `Bearer ${access_token}` } }
                                );
                      const searchData = await searchRes.json();
                      const rows = searchData.values || [];
                      let rowIndex = -1;
                      for (let i = 1; i < rows.length; i++) {
                                    if (rows[i][1] && rows[i][1].toLowerCase() === email.toLowerCase()) {
                                                    rowIndex = i + 1; // 1-based
                                      break;
                                    }
                      }

                    if (rowIndex === -1) {
                                  // Usuario no encontrado, agregar fila nueva con miembro
                        await fetch(
                                        `https://sheets.googleapis.com/v4/spreadsheets/${sheetId}/values/Usuarios!A:F:append?valueInputOption=USER_ENTERED`,
                              {
                                                method: 'POST',
                                                headers: { 'Authorization': `Bearer ${access_token}`, 'Content-Type': 'application/json' },
                                                body: JSON.stringify({ values: [[new Date().toLocaleString('es-AR', { timeZone: 'America/Argentina/Buenos_Aires' }), email, '', '', 'Google', 'miembro']] })
                              }
                                      );
                                  // Obtener total de filas para saber en quÃ© fila quedÃ³
                        const afterAppendRes = await fetch(
                                        `https://sheets.googleapis.com/v4/spreadsheets/${sheetId}/values/Usuarios!A:A`,
                              { headers: { 'Authorization': `Bearer ${access_token}` } }
                                      );
                                  const afterAppendData = await afterAppendRes.json();
                                  rowIndex = (afterAppendData.values || []).length;
                    } else {
                                  // Actualizar columna F de la fila encontrada
                        await fetch(
                                        `https://sheets.googleapis.com/v4/spreadsheets/${sheetId}/values/Usuarios!F${rowIndex}?valueInputOption=USER_ENTERED`,
                              {
                                                method: 'PUT',
                                                headers: { 'Authorization': `Bearer ${access_token}`, 'Content-Type': 'application/json' },
                                                body: JSON.stringify({ values: [['miembro']] })
                              }
                                      );
                    }

                    // Pintar la fila de verde
                    await fetch(
                                  `https://sheets.googleapis.com/v4/spreadsheets/${sheetId}:batchUpdate`,
                          {
                                          method: 'POST',
                                          headers: { 'Authorization': `Bearer ${access_token}`, 'Content-Type': 'application/json' },
                                          body: JSON.stringify({
                                                            requests: [{
                                                                                repeatCell: {
                                                                                                      range: {
                                                                                                                              sheetId: usuariosSheetId,
                                                                                                                              startRowIndex: rowIndex - 1,
                                                                                                                              endRowIndex: rowIndex,
                                                                                                                              startColumnIndex: 0,
                                                                                                                              endColumnIndex: 6
                                                                                                            },
                                                                                                      cell: {
                                                                                                                              userEnteredFormat: {
                                                                                                                                                        backgroundColor: {
                                                                                                                                                                                    red: 0.204,
                                                                                                                                                                                    green: 0.659,
                                                                                                                                                                                    blue: 0.325
                                                                                                                                                              }
                                                                                                                                    }
                                                                                                            },
                                                                                                      fields: 'userEnteredFormat.backgroundColor'
                                                                                }
                                                            }]
                                          })
                          }
                                );
                    }

                    // Sección aparte con los que se suscriben a la membresía paga
                    // (independiente de la hoja Usuarios, que es de altas de cuenta).
                    await upsertMiembroRow(sheetId, access_token, { email, accion: accion || 'alta', monto });

                    return new Response(JSON.stringify({ success: true }), { headers });
          }

          // Ruta principal POST / (registrar nuevo usuario)
          try {
                      const { email, name, uid, loginTime, tipo } = await request.json();
                      if (!email) return new Response(JSON.stringify({ error: 'Email requerido' }), { status: 400, headers });
                      const esSoloAvisos = tipo === 'notificaciones';
                      const fuente = esSoloAvisos ? 'Notificaciones (email)' : 'Google';

                    const privateKey = env.GOOGLE_PRIVATE_KEY.replace(/\\n/g, '\n');
                      const serviceEmail = env.GOOGLE_SERVICE_ACCOUNT_EMAIL;
                      const sheetId = env.GOOGLE_SHEETS_ID;

                    // Firmar JWT con Web Crypto API
                    const now = Math.floor(Date.now() / 1000);
                      const jwtHeader = btoa(JSON.stringify({ alg: 'RS256', typ: 'JWT' })).replace(/=/g,'').replace(/\+/g,'-').replace(/\//g,'_');
                      const jwtPayload = btoa(JSON.stringify({
                                    iss: serviceEmail,
                                    scope: 'https://www.googleapis.com/auth/spreadsheets',
                                    aud: 'https://oauth2.googleapis.com/token',
                                    exp: now + 3600,
                                    iat: now
                      })).replace(/=/g,'').replace(/\+/g,'-').replace(/\//g,'_');

                    const pemBody = privateKey.replace(/-----BEGIN PRIVATE KEY-----|-----END PRIVATE KEY-----|\n/g, '');
                      const binaryKey = Uint8Array.from(atob(pemBody), c => c.charCodeAt(0));
                      const cryptoKey = await crypto.subtle.importKey(
                                    'pkcs8', binaryKey.buffer,
                            { name: 'RSASSA-PKCS1-v1_5', hash: 'SHA-256' },
                                    false, ['sign']
                                  );

                    const sigBuffer = await crypto.subtle.sign(
                                  'RSASSA-PKCS1-v1_5',
                                  cryptoKey,
                                  new TextEncoder().encode(`${jwtHeader}.${jwtPayload}`)
                                );
                      const sig = btoa(String.fromCharCode(...new Uint8Array(sigBuffer))).replace(/=/g,'').replace(/\+/g,'-').replace(/\//g,'_');
                      const jwt = `${jwtHeader}.${jwtPayload}.${sig}`;

                    // Obtener access token
                    const tokenRes = await fetch('https://oauth2.googleapis.com/token', {
                                  method: 'POST',
                                  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                                  body: `grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer&assertion=${jwt}`
                    });
                      const { access_token } = await tokenRes.json();
                      if (!access_token) throw new Error('No se pudo obtener access token');

                    // Registrar en Google Sheets: insertar en fila 2 (empuja las existentes hacia abajo)
                    const fecha = new Date(loginTime || Date.now()).toLocaleString('es-AR', { timeZone: 'America/Argentina/Buenos_Aires' });

                    // PASO A: Insertar fila vacÃ­a en posiciÃ³n 2
                    await fetch(
                                  `https://sheets.googleapis.com/v4/spreadsheets/${sheetId}:batchUpdate`,
                          {
                                          method: 'POST',
                                          headers: { 'Authorization': `Bearer ${access_token}`, 'Content-Type': 'application/json' },
                                          body: JSON.stringify({
                                                            requests: [{
                                                                                insertDimension: {
                                                                                                      range: {
                                                                                                                              sheetId: 0,
                                                                                                                              dimension: 'ROWS',
                                                                                                                              startIndex: 1,
                                                                                                                              endIndex: 2
                                                                                                            },
                                                                                                      inheritFromBefore: false
                                                                                }
                                                            }]
                                          })
                          }
                                );

                    // PASO B: Escribir los datos en la fila 2 reciÃ©n creada
                    await fetch(
                                  `https://sheets.googleapis.com/v4/spreadsheets/${sheetId}/values/Usuarios!A2:E2?valueInputOption=USER_ENTERED`,
                          {
                                          method: 'PUT',
                                          headers: { 'Authorization': `Bearer ${access_token}`, 'Content-Type': 'application/json' },
                                          body: JSON.stringify({ values: [[fecha, email, name || '', uid || '', fuente]] })
                          }
                                );

                    // Email de bienvenida (fire-and-forget): solo para altas de cuenta,
                    // no para quienes solo se suscriben a avisos (no crearon cuenta)
                    if (!esSoloAvisos) fetch('https://api.resend.com/emails', {
                                  method: 'POST',
                                  headers: {
                                                  'Authorization': `Bearer ${env.RESEND_API_KEY}`,
                                                  'Content-Type': 'application/json'
                                  },
                                  body: JSON.stringify({
                                                  from: 'Manfredi Investment <hola@manfredinvestment.com>',
                                                  to: email,
                                                  subject: 'Bienvenido a Manfredi Investment',
                                                  html: `<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head><body style="margin:0;padding:0;background-color:#0a0e1a;font-family:'Helvetica Neue',Arial,sans-serif;"><table width="100%" cellpadding="0" cellspacing="0" style="background-color:#0a0e1a;padding:40px 20px;"><tr><td align="center"><table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background-color:#111827;border:1px solid #B8943F;border-radius:8px;overflow:hidden;"><tr><td style="background-color:#0d1424;padding:32px 40px;border-bottom:1px solid #B8943F;"><table cellpadding="0" cellspacing="0"><tr><td style="background-color:#B8943F;width:40px;height:40px;border-radius:4px;text-align:center;vertical-align:middle;"><span style="color:#0a0e1a;font-weight:700;font-size:16px;line-height:40px;">MI</span></td><td style="padding-left:12px;vertical-align:middle;"><span style="color:#ffffff;font-size:18px;font-weight:600;letter-spacing:0.5px;">Manfredi Investment</span><br><span style="color:#B8943F;font-size:11px;letter-spacing:2px;text-transform:uppercase;">Research &amp; Markets</span></td></tr></table></td></tr><tr><td style="padding:40px;"><h1 style="color:#ffffff;font-size:24px;font-weight:600;margin:0 0 16px 0;">Bienvenido a Manfredi Investment</h1><p style="color:#9ca3af;font-size:15px;line-height:1.6;margin:0 0 24px 0;">Su cuenta ha sido creada exitosamente. A partir de ahora tiene acceso a anÃ¡lisis de mercados argentinos y de Wall Street, reportes diarios y datos en tiempo real.</p><table cellpadding="0" cellspacing="0" style="background-color:#0d1424;border:1px solid #1e2d4a;border-radius:6px;width:100%;margin-bottom:32px;"><tr><td style="padding:24px;"><p style="color:#B8943F;font-size:11px;letter-spacing:2px;text-transform:uppercase;margin:0 0 16px 0;">Acceso gratuito incluye</p><table cellpadding="0" cellspacing="0"><tr><td style="padding:6px 0;color:#d1d5db;font-size:14px;">&#10003; &nbsp;Reportes diarios de Argentina y Wall Street</td></tr><tr><td style="padding:6px 0;color:#d1d5db;font-size:14px;">&#10003; &nbsp;Datos de mercado en tiempo real</td></tr><tr><td style="padding:6px 0;color:#d1d5db;font-size:14px;">&#10003; &nbsp;Cursos de educaciÃ³n financiera</td></tr></table></td></tr></table><table cellpadding="0" cellspacing="0" style="background-color:#0d1424;border:1px solid #B8943F;border-radius:6px;width:100%;margin-bottom:32px;"><tr><td style="padding:24px;"><p style="color:#B8943F;font-size:11px;letter-spacing:2px;text-transform:uppercase;margin:0 0 12px 0;">MembresÃ­a Premium â $15 USD / mes</p><table cellpadding="0" cellspacing="0"><tr><td style="padding:5px 0;color:#d1d5db;font-size:14px;">&#9733; &nbsp;Informes de anÃ¡lisis en profundidad</td></tr><tr><td style="padding:5px 0;color:#d1d5db;font-size:14px;">&#9733; &nbsp;Warren IA â Asesor financiero con inteligencia artificial</td></tr><tr><td style="padding:5px 0;color:#d1d5db;font-size:14px;">&#9733; &nbsp;Seguimiento de inversiones con mÃ©tricas avanzadas</td></tr></table><table cellpadding="0" cellspacing="0" style="margin-top:20px;"><tr><td style="background-color:#B8943F;border-radius:4px;padding:12px 28px;text-align:center;"><a href="https://manfredinvestment.com" style="color:#0a0e1a;font-size:14px;font-weight:700;text-decoration:none;letter-spacing:0.5px;">Obtener acceso Premium</a></td></tr></table></td></tr></table><p style="color:#6b7280;font-size:13px;line-height:1.6;margin:0;">Este mensaje fue enviado porque se registrÃ³ en Manfredi Investment. Si no reconoce esta acciÃ³n, puede ignorar este correo.</p></td></tr><tr><td style="background-color:#0d1424;padding:20px 40px;border-top:1px solid #1e2d4a;text-align:center;"><p style="color:#4b5563;font-size:12px;margin:0;">Â© 2026 Manfredi Investment Â· Rosario, Argentina</p></td></tr></table></td></tr></table></body></html>`
                                  })
                    }).catch(err => console.error('Error enviando email bienvenida:', err));

                    return new Response(JSON.stringify({ success: true }), { headers });
          } catch (err) {
                      return new Response(JSON.stringify({ error: err.message }), { status: 500, headers });
          }
        }
};

// ─── Hoja "Miembros": socios de la membresía paga, separada de "Usuarios" ──
// (que es de altas de cuenta, gratis o no). Se crea sola la primera vez que
// hace falta. Columnas: Fecha alta | Email | Monto ARS | Última renovación |
// Vence | Estado.

// ─── Hoja "Miembros": socios de la membresía paga, separada de "Usuarios" ──
// (que es de altas de cuenta, gratis o no). Se crea sola la primera vez que
// hace falta. Columnas: Fecha alta | Email | Monto ARS | Última renovación |
// Vence | Estado.
async function ensureMiembrosSheet(sheetId, accessToken) {
    const metaRes = await fetch(
        `https://sheets.googleapis.com/v4/spreadsheets/${sheetId}?fields=sheets.properties`,
        { headers: { 'Authorization': `Bearer ${accessToken}` } }
    );
    const meta = await metaRes.json();
    console.error('[log-user] sheets meta status:', metaRes.status, 'titles:', (meta.sheets || []).map(s => s.properties && s.properties.title));
    const existing = (meta.sheets || []).find(s => s.properties && s.properties.title === 'Miembros');
    if (existing) return existing.properties.sheetId;

    const addRes = await fetch(
        `https://sheets.googleapis.com/v4/spreadsheets/${sheetId}:batchUpdate`,
        {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${accessToken}`, 'Content-Type': 'application/json' },
            body: JSON.stringify({ requests: [{ addSheet: { properties: { title: 'Miembros' } } }] })
        }
    );
    const addData = await addRes.json();
    console.error('[log-user] addSheet status:', addRes.status, 'body:', JSON.stringify(addData));
    const newSheetId = addData.replies[0].addSheet.properties.sheetId;

    const headerRes = await fetch(
        `https://sheets.googleapis.com/v4/spreadsheets/${sheetId}/values/Miembros!A1:F1?valueInputOption=USER_ENTERED`,
        {
            method: 'PUT',
            headers: { 'Authorization': `Bearer ${accessToken}`, 'Content-Type': 'application/json' },
            body: JSON.stringify({ values: [['Fecha alta', 'Email', 'Monto ARS', 'Última renovación', 'Vence', 'Estado']] })
        }
    );
    console.error('[log-user] header write status:', headerRes.status);

    return newSheetId;
}

async function upsertMiembroRow(sheetId, accessToken, { email, accion, monto }) {
    console.error('[log-user] upsertMiembroRow', email, accion, monto);
    await ensureMiembrosSheet(sheetId, accessToken);
    const fechaHoy = new Date().toLocaleString('es-AR', { timeZone: 'America/Argentina/Buenos_Aires' });
    const vence = new Date(Date.now() + 2678400000).toLocaleString('es-AR', { timeZone: 'America/Argentina/Buenos_Aires' });
    const montoStr = monto != null ? String(monto) : '';

    const searchRes = await fetch(
        `https://sheets.googleapis.com/v4/spreadsheets/${sheetId}/values/Miembros!A:F`,
        { headers: { 'Authorization': `Bearer ${accessToken}` } }
    );
    const searchData = await searchRes.json();
    const rows = searchData.values || [];
    let rowIndex = -1;
    for (let i = 1; i < rows.length; i++) {
        if (rows[i][1] && rows[i][1].toLowerCase() === email.toLowerCase()) { rowIndex = i + 1; break; }
    }
    console.error('[log-user] Miembros search status:', searchRes.status, 'rowIndex:', rowIndex, 'totalRows:', rows.length);

    if (accion === 'cancelacion') {
        if (rowIndex === -1) return; // nunca estuvo en la hoja, nada que cancelar
        const cancelRes = await fetch(
            `https://sheets.googleapis.com/v4/spreadsheets/${sheetId}/values/Miembros!F${rowIndex}?valueInputOption=USER_ENTERED`,
            {
                method: 'PUT',
                headers: { 'Authorization': `Bearer ${accessToken}`, 'Content-Type': 'application/json' },
                body: JSON.stringify({ values: [['Cancelada']] })
            }
        );
        console.error('[log-user] Miembros cancelacion write status:', cancelRes.status);
        return;
    }

    if (rowIndex === -1) {
        // Alta nueva (o una renovación que por algún motivo no tenía fila -- se
        // trata igual, con fecha de alta = hoy).
        const appendRes = await fetch(
            `https://sheets.googleapis.com/v4/spreadsheets/${sheetId}/values/Miembros!A:F:append?valueInputOption=USER_ENTERED`,
            {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${accessToken}`, 'Content-Type': 'application/json' },
                body: JSON.stringify({ values: [[fechaHoy, email, montoStr, fechaHoy, vence, 'Activo']] })
            }
        );
        const appendData = await appendRes.json();
        console.error('[log-user] Miembros append status:', appendRes.status, 'body:', JSON.stringify(appendData));
        return;
    }

    // Renovación: se actualiza monto / última renovación / vence / estado,
    // se deja la fecha de alta original de la columna A sin tocar.
    await fetch(
        `https://sheets.googleapis.com/v4/spreadsheets/${sheetId}/values/Miembros!C${rowIndex}:F${rowIndex}?valueInputOption=USER_ENTERED`,
        {
            method: 'PUT',
            headers: { 'Authorization': `Bearer ${accessToken}`, 'Content-Type': 'application/json' },
            body: JSON.stringify({ values: [[montoStr, fechaHoy, vence, 'Activo']] })
        }
    );
}

// ─── Ruta "/avisar-informe": manda por mail (Resend) el aviso de un informe ──
// nuevo a todos los emails de la hoja "Usuarios". Protegida con ADMIN_KEY
// (header x-admin-key) porque el worker es publico y esto le pega a toda la
// base de usuarios. Soporta dryRun para contar destinatarios sin enviar, y
// paginacion (offset/limit) porque una sola invocacion del worker tiene un
// tope de subrequests -- si hay muchos usuarios, se llama varias veces
// pasando el offset que devuelve la llamada anterior.
async function avisarInforme(request, env, corsHeaders) {
    const headers = { ...corsHeaders, 'Content-Type': 'application/json' };

    if (env.ADMIN_KEY && request.headers.get('x-admin-key') !== env.ADMIN_KEY) {
        return new Response(JSON.stringify({ error: 'No autorizado' }), { status: 401, headers });
    }

    let body;
    try {
        body = await request.json();
    } catch {
        return new Response(JSON.stringify({ error: 'Body invalido' }), { status: 400, headers });
    }

    const { title, intro, sections = [], ctaUrl = 'https://manfredinvestment.com/#informes',
        ctaLabel = 'Leer el informe completo — gratis', subject, dryRun = false,
        offset = 0, limit = 40, emails: emailsOverride } = body;

    if (!title || !intro || !subject) {
        return new Response(JSON.stringify({ error: 'Faltan campos: subject, title e intro son requeridos' }), { status: 400, headers });
    }

    let emailsUnicos;
    if (Array.isArray(emailsOverride) && emailsOverride.length) {
        // Reintento dirigido a direcciones puntuales (ej. las que fallaron por
        // rate-limit en una tanda anterior) sin volver a pegarle a toda la hoja.
        emailsUnicos = [...new Set(emailsOverride.map(e => (e || '').trim().toLowerCase()).filter(Boolean))];
    } else {
        const accessToken = await getGoogleAccessToken(env);
        const sheetId = env.GOOGLE_SHEETS_ID;
        const searchRes = await fetch(
            `https://sheets.googleapis.com/v4/spreadsheets/${sheetId}/values/Usuarios!B:B`,
            { headers: { 'Authorization': `Bearer ${accessToken}` } }
        );
        const searchData = await searchRes.json();
        const rows = searchData.values || [];
        emailsUnicos = [...new Set(
            rows.slice(1)
                .map(r => (r[0] || '').trim().toLowerCase())
                .filter(Boolean)
        )];
    }

    if (dryRun) {
        return new Response(JSON.stringify({ ok: true, destinatarios: emailsUnicos.length }), { status: 200, headers });
    }

    const lote = emailsUnicos.slice(offset, offset + limit);
    const html = htmlInformeNuevo({ title, intro, sections, ctaUrl, ctaLabel });

    // Envio secuencial con una pequena pausa entre cada uno -- mandar los 40
    // en paralelo pego contra el rate-limit de Resend (429s).
    const resultados = [];
    for (const email of lote) {
        try {
            const res = await fetch('https://api.resend.com/emails', {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${env.RESEND_API_KEY}`, 'Content-Type': 'application/json' },
                body: JSON.stringify({ from: 'Manfredi Investment <hola@manfredinvestment.com>', to: email, subject, html })
            });
            resultados.push({ email, ok: res.ok, status: res.status });
        } catch (err) {
            resultados.push({ email, ok: false, error: String(err) });
        }
        await new Promise(r => setTimeout(r, 550));
    }

    const enviados = resultados.filter(r => r.ok).length;
    const fallidos = resultados.filter(r => !r.ok);
    const nextOffset = offset + limit < emailsUnicos.length ? offset + limit : null;

    return new Response(JSON.stringify({
        ok: true,
        totalDestinatarios: emailsUnicos.length,
        enviados,
        fallidos,
        nextOffset
    }), { status: 200, headers });
}

async function getGoogleAccessToken(env) {
    const privateKey = env.GOOGLE_PRIVATE_KEY.replace(/\\n/g, '\n');
    const serviceEmail = env.GOOGLE_SERVICE_ACCOUNT_EMAIL;

    const now = Math.floor(Date.now() / 1000);
    const jwtHeader = btoa(JSON.stringify({ alg: 'RS256', typ: 'JWT' })).replace(/=/g, '').replace(/\+/g, '-').replace(/\//g, '_');
    const jwtPayload = btoa(JSON.stringify({
        iss: serviceEmail,
        scope: 'https://www.googleapis.com/auth/spreadsheets',
        aud: 'https://oauth2.googleapis.com/token',
        exp: now + 3600,
        iat: now
    })).replace(/=/g, '').replace(/\+/g, '-').replace(/\//g, '_');

    const pemBody = privateKey.replace(/-----BEGIN PRIVATE KEY-----|-----END PRIVATE KEY-----|\n/g, '');
    const binaryKey = Uint8Array.from(atob(pemBody), c => c.charCodeAt(0));
    const cryptoKey = await crypto.subtle.importKey('pkcs8', binaryKey.buffer, { name: 'RSASSA-PKCS1-v1_5', hash: 'SHA-256' }, false, ['sign']);
    const sigBuffer = await crypto.subtle.sign('RSASSA-PKCS1-v1_5', cryptoKey, new TextEncoder().encode(`${jwtHeader}.${jwtPayload}`));
    const sig = btoa(String.fromCharCode(...new Uint8Array(sigBuffer))).replace(/=/g, '').replace(/\+/g, '-').replace(/\//g, '_');
    const jwt = `${jwtHeader}.${jwtPayload}.${sig}`;

    const tokenRes = await fetch('https://oauth2.googleapis.com/token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer&assertion=${jwt}`
    });
    const { access_token } = await tokenRes.json();
    if (!access_token) throw new Error('No se pudo obtener access token de Google');
    return access_token;
}

// Mismo template/paleta que scripts/email-informe-nuevo.html, parametrizado
// para poder reusarlo en cada informe nuevo (no solo el de esta semana).
function htmlInformeNuevo({ title, intro, sections, ctaUrl, ctaLabel }) {
    const filas = sections.map((s, i) => {
        const num = String(i + 1).padStart(2, '0');
        const borde = i < sections.length - 1 ? 'border-bottom:1px solid #253052;' : '';
        return `<tr><td style="padding:8px 0;color:#E7EAF3;font-size:14px;${borde}"><span style="color:#EFC468;font-weight:700;">${num}</span>&nbsp; &middot; &nbsp;${s}</td></tr>`;
    }).join('');

    const bloqueSecciones = sections.length ? `
    <table cellpadding="0" cellspacing="0" style="background-color:#111a30;border:1px solid #2b3757;border-radius:6px;width:100%;margin-bottom:28px;">
      <tr><td style="padding:24px;">
        <p style="color:#EFC468;font-size:11px;letter-spacing:2px;text-transform:uppercase;margin:0 0 16px 0;">En este informe</p>
        <table cellpadding="0" cellspacing="0" style="width:100%;">${filas}</table>
      </td></tr>
    </table>` : '';

    return `<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head><body style="margin:0;padding:0;background-color:#0a0e1a;font-family:'Helvetica Neue',Arial,sans-serif;"><table width="100%" cellpadding="0" cellspacing="0" style="background-color:#0a0e1a;background-image:radial-gradient(120% 140% at 50% -10%, #182a4a 0%, #0a0e1a 55%);padding:40px 20px;"><tr><td align="center"><table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background-color:#131b30;background-image:linear-gradient(180deg,#161f38 0%,#0f1526 100%);border:1px solid #D9A73B;border-radius:10px;overflow:hidden;box-shadow:0 24px 60px rgba(0,0,0,0.45);">
  <tr><td style="background-color:#0d1424;background-image:linear-gradient(180deg,#111b32 0%,#0c111f 100%);padding:32px 40px;border-bottom:1px solid #D9A73B;">
    <table cellpadding="0" cellspacing="0"><tr>
      <td style="background-color:#D9A73B;background-image:linear-gradient(135deg,#F6D488 0%,#D9A73B 55%,#B9822C 100%);width:40px;height:40px;border-radius:6px;text-align:center;vertical-align:middle;box-shadow:0 4px 16px rgba(217,167,59,0.4);"><span style="color:#1a1206;font-weight:800;font-size:16px;line-height:40px;">MI</span></td>
      <td style="padding-left:12px;vertical-align:middle;"><span style="color:#ffffff;font-size:18px;font-weight:600;letter-spacing:0.5px;">Manfredi Investment</span><br><span style="color:#EFC468;font-size:11px;letter-spacing:2px;text-transform:uppercase;">Research &amp; Markets</span></td>
    </tr></table>
  </td></tr>
  <tr><td style="padding:40px;">
    <p style="color:#EFC468;font-size:11px;letter-spacing:2px;text-transform:uppercase;margin:0 0 12px 0;">Informe nuevo disponible</p>
    <h1 style="color:#ffffff;font-size:23px;font-weight:600;line-height:1.35;margin:0 0 14px 0;">${title}</h1>
    <p style="color:#CBD2E3;font-size:15px;line-height:1.6;margin:0 0 28px 0;">${intro}</p>
    ${bloqueSecciones}
    <table cellpadding="0" cellspacing="0" style="width:100%;margin-bottom:28px;">
      <tr><td align="center" style="background-color:#D9A73B;background-image:linear-gradient(135deg,#F8DA96 0%,#DDAB40 45%,#B9822C 100%);border-radius:7px;padding:15px 30px;border-top:1px solid rgba(255,255,255,0.55);box-shadow:0 10px 30px rgba(217,167,59,0.45);">
        <a href="${ctaUrl}" style="color:#1a1206;font-size:15px;font-weight:800;text-decoration:none;letter-spacing:0.6px;">${ctaLabel}</a>
      </td></tr>
    </table>
    <p style="color:#8D96B2;font-size:13px;line-height:1.6;margin:0;">Recibís este mail porque tenés una cuenta en Manfredi Investment. Si no querés recibir avisos de informes nuevos, respondé este correo y te sacamos de la lista.</p>
  </td></tr>
  <tr><td style="background-color:#0d1424;padding:20px 40px;border-top:1px solid #2b3757;text-align:center;">
    <p style="color:#5B6482;font-size:12px;margin:0;">© 2026 Manfredi Investment · Buenos Aires, Argentina</p>
  </td></tr>
</table></td></tr></table></body></html>`;
}
