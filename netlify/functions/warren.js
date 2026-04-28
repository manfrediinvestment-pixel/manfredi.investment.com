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

        const ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY;
        if (!ANTHROPIC_API_KEY) {
                    console.error('ERROR: ANTHROPIC_API_KEY no encontrada');
                    return {
                                    statusCode: 200,
                                    headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
                                    body: JSON.stringify({ response: 'Error de configuracion: API key no encontrada.' })
                    };
        }

        try {
                    const body = JSON.parse(event.body);
                    const { messages, systemPrompt, email } = body;

            // CAMBIO 2 — Verificar consultas disponibles antes de llamar a Anthropic
            if (email) {
                            const consultasRes = await fetch(`https://manfredi-memberships.nachito2502.workers.dev/consultas?email=${encodeURIComponent(email)}`);
                            const consultasData = await consultasRes.json();
                            if (consultasData.consultas === 0) {
                                                return {
                                                                        statusCode: 200,
                                                                        headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
                                                                        body: JSON.stringify({ response: 'Agotaste tus 50 consultas del mes. Se renuevan el 1 del próximo mes.', limitAlcanzado: true })
                                                };
                            }
            }

            const requestBody = {
                            model: 'claude-haiku-4-5',
                            max_tokens: 1024,
                            system: systemPrompt || 'Sos Warren, asesor financiero de Manfredi Investment.',
                            messages: messages.map(m => ({
                                                role: m.role === 'assistant' ? 'assistant' : 'user',
                                                content: m.content
                            }))
            };

            const response = await fetch('https://api.anthropic.com/v1/messages', {
                            method: 'POST',
                            headers: {
                                                'Content-Type': 'application/json',
                                                'x-api-key': ANTHROPIC_API_KEY,
                                                'anthropic-version': '2023-06-01'
                            },
                            body: JSON.stringify(requestBody)
            });

            if (!response.ok) {
                            const errText = await response.text();
                            console.error('Anthropic API error:', response.status, errText);
                            return {
                                                statusCode: 200,
                                                headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
                                                body: JSON.stringify({ response: 'Error al conectar con el servicio de IA. Intenta de nuevo.' })
                            };
            }

            const data = await response.json();
                    const reply = data.content && data.content[0] && data.content[0].text
                        ? data.content[0].text
                                    : 'No pude procesar tu consulta. Intenta de nuevo.';

            // Restar 1 consulta después de respuesta exitosa
            if (email) {
                            await fetch('https://manfredi-memberships.nachito2502.workers.dev/restar-consulta', {
                                                method: 'POST',
                                                headers: { 'Content-Type': 'application/json' },
                                                body: JSON.stringify({ email })
                            });
            }

            return {
                            statusCode: 200,
                            headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
                            body: JSON.stringify({ response: reply })
            };

        } catch (err) {
                    console.error('Warren function error:', err);
                    return {
                                    statusCode: 200,
                                    headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
                                    body: JSON.stringify({ response: 'Hubo un error inesperado. Por favor intenta nuevamente.' })
                    };
        }
};
