// netlify/functions/log-user.js
// Registra usuarios de Google que ingresan a la pagina
// Requiere configurar las variables de entorno en Netlify:
//   GOOGLE_SHEETS_ID: ID de tu Google Sheet (parte de la URL)
//   GOOGLE_SERVICE_ACCOUNT_EMAIL: email de la cuenta de servicio
//   GOOGLE_PRIVATE_KEY: clave privada de la cuenta de servicio (con \n como saltos)

exports.handler = async function(event, context) {
  // CORS headers
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'POST, OPTIONS'
  };

  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 200, headers, body: '' };
  }

  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, headers, body: 'Method Not Allowed' };
  }

  try {
    const { email, name, uid, loginTime } = JSON.parse(event.body || '{}');

    if (!email) {
      return { statusCode: 400, headers, body: JSON.stringify({ error: 'Email requerido' }) };
    }

    const sheetId = process.env.GOOGLE_SHEETS_ID;
    const serviceEmail = process.env.GOOGLE_SERVICE_ACCOUNT_EMAIL;
    const privateKey = (process.env.GOOGLE_PRIVATE_KEY || '').replace(/\\n/g, '\n');

    if (!sheetId || !serviceEmail || !privateKey) {
      console.log('Variables de entorno no configuradas, saltando registro');
      return {
        statusCode: 200,
        headers,
        body: JSON.stringify({ success: true, message: 'Variables no configuradas' })
      };
    }

    // Obtener token de Google
    const jwt = require('jsonwebtoken');
    const now = Math.floor(Date.now() / 1000);
    const payload = {
      iss: serviceEmail,
      scope: 'https://www.googleapis.com/auth/spreadsheets',
      aud: 'https://oauth2.googleapis.com/token',
      exp: now + 3600,
      iat: now
    };

    const token = jwt.sign(payload, privateKey, { algorithm: 'RS256' });

    // Obtener access token
    const tokenRes = await fetch('https://oauth2.googleapis.com/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: `grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer&assertion=${token}`
    });
    const tokenData = await tokenRes.json();
    const accessToken = tokenData.access_token;

    if (!accessToken) {
      throw new Error('No se pudo obtener access token: ' + JSON.stringify(tokenData));
    }

    // Agregar fila a Google Sheets
    const fechaArgentina = new Date(loginTime || Date.now())
      .toLocaleString('es-AR', { timeZone: 'America/Argentina/Buenos_Aires' });

    const appendRes = await fetch(
      `https://sheets.googleapis.com/v4/spreadsheets/${sheetId}/values/Usuarios!A:E:append?valueInputOption=USER_ENTERED`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          values: [[fechaArgentina, email, name || '', uid || '', 'Google']]
        })
      }
    );

    if (!appendRes.ok) {
      const errText = await appendRes.text();
      throw new Error('Error en Sheets API: ' + errText);
    }

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({ success: true })
    };

  } catch (err) {
    console.error('Error en log-user:', err);
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ error: err.message })
    };
  }
};
