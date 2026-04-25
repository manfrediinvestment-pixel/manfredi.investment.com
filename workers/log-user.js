export default {
    async fetch(request, env) {
          const headers = {
                  'Access-Control-Allow-Origin': '*',
                  'Access-Control-Allow-Headers': 'Content-Type',
                  'Access-Control-Allow-Methods': 'POST, OPTIONS'
          };

      if (request.method === 'OPTIONS') return new Response('', { headers });
          if (request.method !== 'POST') return new Response('Method Not Allowed', { status: 405, headers });

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

            // Registrar en Google Sheets
            const fecha = new Date(loginTime || Date.now()).toLocaleString('es-AR', { timeZone: 'America/Argentina/Buenos_Aires' });
              await fetch(
                        `https://sheets.googleapis.com/v4/spreadsheets/${sheetId}/values/Usuarios!A:E:append?valueInputOption=USER_ENTERED`,
                {
                            method: 'POST',
                            headers: { 'Authorization': `Bearer ${access_token}`, 'Content-Type': 'application/json' },
                            body: JSON.stringify({ values: [[fecha, email, name || '', uid || '', 'Google']] })
                }
                      );

            return new Response(JSON.stringify({ success: true }), { headers });
      } catch (err) {
              return new Response(JSON.stringify({ error: err.message }), { status: 500, headers });
      }

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

      const pemBody = privateKey.replace(/-----BEGIN PRIVATE KEY-----|-----END PRIVATE KEY-----|
/g, '');
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

      return new Response(JSON.stringify({ success: true }), { headers });
    }

    }
};
