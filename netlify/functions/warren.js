exports.handler = async function(event, context) {
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS'
      },
      body: ''
    };
  }

  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, body: 'Method Not Allowed' };
  }

  const GEMINI_API_KEY = process.env.GEMINI_API_KEY;
  if (!GEMINI_API_KEY) {
    console.error('ERROR: GEMINI_API_KEY no encontrada');
    return {
      statusCode: 200,
      headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
      body: JSON.stringify({ response: 'Error de configuración.' })
    };
  }

  try {
    const body = JSON.parse(event.body);
    const { messages, systemPrompt } = body;

    const geminiMessages = messages.map(m => ({
      role: m.role === 'assistant' ? 'model' : 'user',
      parts: [{ text: m.content }]
    }));

    const requestBody = {
      system_instruction: {
        parts: [{ text: systemPrompt || 'Sos Warren, asesor financiero de Manfredi Investment.' }]
      },
      contents: geminiMessages,
      generationConfig: {
        temperature: 0.7,
        maxOutputTokens: 2048
      }
    };

    // Lista de modelos a probar en orden
    const models = [
      'gemini-2.0-flash-lite',
      'gemini-2.0-flash',
      'gemini-1.5-flash',
      'gemini-1.5-flash-8b'
    ];

    let lastError = '';
    for (const model of models) {
      const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${GEMINI_API_KEY}`;
      console.log(`Intentando modelo: ${model}`);

      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody)
      });

      const responseText = await response.text();
      console.log(`${model} status: ${response.status}`);

      if (response.ok) {
        const data = JSON.parse(responseText);
        const text = data.candidates?.[0]?.content?.parts?.[0]?.text || 'Sin respuesta.';
        console.log(`Éxito con modelo: ${model}`);
        return {
          statusCode: 200,
          headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
          body: JSON.stringify({ response: text })
        };
      } else {
        lastError = responseText.substring(0, 200);
        console.error(`${model} falló:`, lastError);
      }
    }

    // Si todos fallaron
    console.error('Todos los modelos fallaron. Último error:', lastError);
    return {
      statusCode: 200,
      headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
      body: JSON.stringify({ response: 'El servicio no está disponible en este momento. Por favor intentá más tarde.' })
    };

  } catch (error) {
    console.error('Error en la función:', error.message);
    return {
      statusCode: 200,
      headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
      body: JSON.stringify({ response: 'Ocurrió un error inesperado. Intentá nuevamente.' })
    };
  }
};
