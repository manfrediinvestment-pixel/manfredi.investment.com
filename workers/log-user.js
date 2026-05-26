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

          // Ruta para marcar usuario como miembro
          if (new URL(request.url).pathname === '/marcar-miembro') {export default {
        async fetch(request, env) {
                  const headers = {
                              'Access-Control-Allow-Origin': '*',
                              'Access-Control-Allow-Headers': 'Content-Type',
                              'Access-Control-Allow-Methods': 'POST, OPTIONS'
                  };

          if (request.method === 'OPTIONS') return new Response('', { headers });
                  if (request.method !== 'POST') return new Response('Method Not Allowed', { status: 405, headers });
                  const pathname = new URL(request.url).pathname;

          // Ruta para marcar usuario como miembro
          if (new URL(request.url).pathname === '/marcar-miembro') {
                      const { email } = await request.json();
                      if (!email) return new Response(JSON.stringify({ error: 'Email requerido' }), { status: 400, headers });

                    // Reusar lógica de autenticación Google
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

                    // Obtener sheetId numérico de la hoja "Usuarios"
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
                                  // Obtener total de filas para saber en qué fila quedó
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

                    return new Response(JSON.stringify({ success: true }), { headers });
          }

          // Ruta principal POST / (registrar nuevo usuario)
          try {
                      const { email, name, uid, loginTime } = await request.json();
                      if (!email) return new Response(JSON.stringify({ error: 'Email requerido' }), { status: 400, headers });

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

                    // PASO A: Insertar fila vacía en posición 2
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

                    // PASO B: Escribir los datos en la fila 2 recién creada
                    await fetch(
                                  `https://sheets.googleapis.com/v4/spreadsheets/${sheetId}/values/Usuarios!A2:E2?valueInputOption=USER_ENTERED`,
                          {
                                          method: 'PUT',
                                          headers: { 'Authorization': `Bearer ${access_token}`, 'Content-Type': 'application/json' },
                                          body: JSON.stringify({ values: [[fecha, email, name || '', uid || '', 'Google']] })
                          }
                                );

                    // Email de bienvenida (fire-and-forget)
                    fetch('https://api.resend.com/emails', {
                                  method: 'POST',
                                  headers: {
                                                  'Authorization': `Bearer ${env.RESEND_API_KEY}`,
                                                  'Content-Type': 'application/json'
                                  },
                                  body: JSON.stringify({
                                                  from: 'Manfredi Investment <hola@manfredinvestment.com>',
                                                  to: email,
                                                  subject: 'Bienvenido a Manfredi Investment',
                                                  html: `<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head><body style="margin:0;padding:0;background-color:#0a0e1a;font-family:'Helvetica Neue',Arial,sans-serif;"><table width="100%" cellpadding="0" cellspacing="0" style="background-color:#0a0e1a;padding:40px 20px;"><tr><td align="center"><table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background-color:#111827;border:1px solid #B8943F;border-radius:8px;overflow:hidden;"><tr><td style="background-color:#0d1424;padding:32px 40px;border-bottom:1px solid #B8943F;"><table cellpadding="0" cellspacing="0"><tr><td style="background-color:#B8943F;width:40px;height:40px;border-radius:4px;text-align:center;vertical-align:middle;"><span style="color:#0a0e1a;font-weight:700;font-size:16px;line-height:40px;">MI</span></td><td style="padding-left:12px;vertical-align:middle;"><span style="color:#ffffff;font-size:18px;font-weight:600;letter-spacing:0.5px;">Manfredi Investment</span><br><span style="color:#B8943F;font-size:11px;letter-spacing:2px;text-transform:uppercase;">Research &amp; Markets</span></td></tr></table></td></tr><tr><td style="padding:40px;"><h1 style="color:#ffffff;font-size:24px;font-weight:600;margin:0 0 16px 0;">Bienvenido a Manfredi Investment</h1><p style="color:#9ca3af;font-size:15px;line-height:1.6;margin:0 0 24px 0;">Su cuenta ha sido creada exitosamente. A partir de ahora tiene acceso a análisis de mercados argentinos y de Wall Street, reportes diarios y datos en tiempo real.</p><table cellpadding="0" cellspacing="0" style="background-color:#0d1424;border:1px solid #1e2d4a;border-radius:6px;width:100%;margin-bottom:32px;"><tr><td style="padding:24px;"><p style="color:#B8943F;font-size:11px;letter-spacing:2px;text-transform:uppercase;margin:0 0 16px 0;">Acceso gratuito incluye</p><table cellpadding="0" cellspacing="0"><tr><td style="padding:6px 0;color:#d1d5db;font-size:14px;">&#10003; &nbsp;Reportes diarios de Argentina y Wall Street</td></tr><tr><td style="padding:6px 0;color:#d1d5db;font-size:14px;">&#10003; &nbsp;Datos de mercado en tiempo real</td></tr><tr><td style="padding:6px 0;color:#d1d5db;font-size:14px;">&#10003; &nbsp;Cursos de educación financiera</td></tr></table></td></tr></table><table cellpadding="0" cellspacing="0" style="background-color:#0d1424;border:1px solid #B8943F;border-radius:6px;width:100%;margin-bottom:32px;"><tr><td style="padding:24px;"><p style="color:#B8943F;font-size:11px;letter-spacing:2px;text-transform:uppercase;margin:0 0 12px 0;">Membresía Premium — $10 USD / mes</p><table cellpadding="0" cellspacing="0"><tr><td style="padding:5px 0;color:#d1d5db;font-size:14px;">&#9733; &nbsp;Informes de análisis en profundidad</td></tr><tr><td style="padding:5px 0;color:#d1d5db;font-size:14px;">&#9733; &nbsp;Warren IA — Asesor financiero con inteligencia artificial</td></tr><tr><td style="padding:5px 0;color:#d1d5db;font-size:14px;">&#9733; &nbsp;Seguimiento de inversiones con métricas avanzadas</td></tr></table><table cellpadding="0" cellspacing="0" style="margin-top:20px;"><tr><td style="background-color:#B8943F;border-radius:4px;padding:12px 28px;text-align:center;"><a href="https://manfredinvestment.com" style="color:#0a0e1a;font-size:14px;font-weight:700;text-decoration:none;letter-spacing:0.5px;">Obtener acceso Premium</a></td></tr></table></td></tr></table><p style="color:#6b7280;font-size:13px;line-height:1.6;margin:0;">Este mensaje fue enviado porque se registró en Manfredi Investment. Si no reconoce esta acción, puede ignorar este correo.</p></td></tr><tr><td style="background-color:#0d1424;padding:20px 40px;border-top:1px solid #1e2d4a;text-align:center;"><p style="color:#4b5563;font-size:12px;margin:0;">© 2026 Manfredi Investment · Buenos Aires, Argentina</p></td></tr></table></td></tr></table></body></html>`
                                  })
                    }).catch(err => console.error('Error enviando email bienvenida:', err));

                    return new Response(JSON.stringify({ success: true }), { headers });
          } catch (err) {
                      return new Response(JSON.stringify({ error: err.message }), { status: 500, headers });
          }
        }
};
