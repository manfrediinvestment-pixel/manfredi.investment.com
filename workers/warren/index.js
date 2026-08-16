// workers/warren/index.js
// Backend de Warren IA como Cloudflare Worker (antes vivia en
// netlify/functions/warren.js, que en realidad nunca corria en produccion --
// el sitio se sirve por Cloudflare Pages, no Netlify. Ver .claude/plans/
// stateful-roaming-ladybug.md para el contexto completo del rediseño).

const ADMIN_EMAILS = ['nachito2502@gmail.com'];
const MEMBERSHIPS_BASE = 'https://manfredi-memberships.nachito2502.workers.dev';
const MERCADOS_BASE = 'https://manfredi-mercados.nachito2502.workers.dev';
const NOTICIAS_BASE = 'https://manfredi-noticias.nachito2502.workers.dev';

const MODEL_HAIKU = 'claude-haiku-4-5';
const MODEL_SONNET = 'claude-sonnet-5';
const MAX_TOOL_ITERATIONS = 4;

const CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
};
const JSON_HEADERS = { ...CORS_HEADERS, 'Content-Type': 'application/json' };

// ─── Historial de conversaciones (barra estilo ChatGPT/Gemini, solo Socios) ─
// Guardado en WARREN_KV, dos claves por usuario:
//   convos:{email}      -> array liviano [{id,title,updatedAt}], para la lista
//   convo:{email}:{id}  -> conversacion completa {id,title,createdAt,updatedAt,messages}
// El titulo se autogenera truncando el primer mensaje del usuario -- sin
// llamada extra a un LLM, cero costo de API por el simple hecho de guardar.
const CONVO_LIST_CAP = 100;   // conversaciones guardadas por usuario, las mas viejas se descartan
const CONVO_MSG_CAP = 60;     // mensajes por conversacion guardada
const CONVO_TITLE_LEN = 60;

function convoAutoTitle(messages) {
    const firstUser = (messages || []).find(m => m.role === 'user' && typeof m.content === 'string');
    if (!firstUser) return 'Conversación';
    const text = firstUser.content.trim();
    return text.length > CONVO_TITLE_LEN ? text.slice(0, CONVO_TITLE_LEN) + '…' : text;
}

async function handleConversationsList(request, env) {
    const url = new URL(request.url);
    const email = (url.searchParams.get('email') || '').toLowerCase();
    if (!email) return new Response(JSON.stringify({ error: 'Email requerido' }), { status: 400, headers: JSON_HEADERS });
    const listRaw = await env.WARREN_KV.get('convos:' + email);
    return new Response(JSON.stringify({ conversations: listRaw ? JSON.parse(listRaw) : [] }), { headers: JSON_HEADERS });
}

async function handleConversationGet(request, env) {
    const url = new URL(request.url);
    const email = (url.searchParams.get('email') || '').toLowerCase();
    const id = url.searchParams.get('id') || '';
    if (!email || !id) return new Response(JSON.stringify({ error: 'Email e id requeridos' }), { status: 400, headers: JSON_HEADERS });
    const raw = await env.WARREN_KV.get('convo:' + email + ':' + id);
    if (!raw) return new Response(JSON.stringify({ error: 'No encontrada' }), { status: 404, headers: JSON_HEADERS });
    return new Response(raw, { headers: JSON_HEADERS });
}

async function handleConversationSave(request, env) {
    const body = await request.json();
    const email = (body.email || '').toLowerCase();
    const messages = body.messages;
    if (!email || !Array.isArray(messages) || !messages.length) {
        return new Response(JSON.stringify({ error: 'Email y messages requeridos' }), { status: 400, headers: JSON_HEADERS });
    }
    const now = Date.now();
    let id = body.id || null;
    let createdAt = now, existingTitle = null;
    if (id) {
        const existingRaw = await env.WARREN_KV.get('convo:' + email + ':' + id);
        if (existingRaw) {
            const existing = JSON.parse(existingRaw);
            createdAt = existing.createdAt || now;
            existingTitle = existing.title || null;
        } else {
            id = null; // id vencido/de otro usuario -- se trata como conversacion nueva
        }
    }
    if (!id) id = now.toString(36) + Math.random().toString(36).slice(2, 8);
    const title = body.title || existingTitle || convoAutoTitle(messages);
    const convo = { id, title, createdAt, updatedAt: now, messages: messages.slice(-CONVO_MSG_CAP) };
    await env.WARREN_KV.put('convo:' + email + ':' + id, JSON.stringify(convo));

    const listRaw = await env.WARREN_KV.get('convos:' + email);
    let list = listRaw ? JSON.parse(listRaw) : [];
    list = list.filter(c => c.id !== id);
    list.unshift({ id, title, updatedAt: now });
    if (list.length > CONVO_LIST_CAP) {
        const dropped = list.slice(CONVO_LIST_CAP);
        list = list.slice(0, CONVO_LIST_CAP);
        await Promise.all(dropped.map(c => env.WARREN_KV.delete('convo:' + email + ':' + c.id)));
    }
    await env.WARREN_KV.put('convos:' + email, JSON.stringify(list));

    return new Response(JSON.stringify({ id, title }), { headers: JSON_HEADERS });
}

async function handleConversationDelete(request, env) {
    const body = await request.json();
    const email = (body.email || '').toLowerCase();
    const id = body.id;
    if (!email || !id) return new Response(JSON.stringify({ error: 'Email e id requeridos' }), { status: 400, headers: JSON_HEADERS });
    await env.WARREN_KV.delete('convo:' + email + ':' + id);
    const listRaw = await env.WARREN_KV.get('convos:' + email);
    const list = (listRaw ? JSON.parse(listRaw) : []).filter(c => c.id !== id);
    await env.WARREN_KV.put('convos:' + email, JSON.stringify(list));
    return new Response(JSON.stringify({ ok: true }), { headers: JSON_HEADERS });
}

// ─── Heuristica de ruteo de modelo ─────────────────────────────────────────
// Sin llamada extra a un LLM clasificador: el ahorro de no rutear bien es
// centavos, no vale la latencia/costo de un paso de clasificacion aparte.
// Arranca en Haiku salvo que el mensaje matchee patrones de analisis
// profundo; si en el loop se termina llamando alguna tool, el resto de la
// conversacion (la sintesis con datos reales) escala a Sonnet porque ahi es
// donde mas importa la calidad de razonamiento.
// Nota: preguntas puntuales de un solo dato (precio de un ticker, cotizacion
// del dolar hoy, titulares del dia) quedan afuera a proposito -- son lookups
// que get_market_data/get_news resuelven solos, no necesitan la sintesis de
// Sonnet. Los botones de sugerencia del chat estan diseñados para caer aca.
const DEEP_ANALYSIS_RE = /(anali[sz]|dcf|valuaci[oó]n|comparables|m[uú]ltiplos|tesis de inversi[oó]n|sector(es)?|sobrepondera|construime|arm[aá] (una |un )?cartera|portafolio|earnings|balance|resultados trimestrales|riesgos clave|red flags?|mercado argentino)/i;

function chooseInitialModel(lastUserText) {
    if (!lastUserText) return MODEL_HAIKU;
    if (lastUserText.length > 220) return MODEL_SONNET;
    if (DEEP_ANALYSIS_RE.test(lastUserText)) return MODEL_SONNET;
    return MODEL_HAIKU;
}

// ─── Definicion de tools ────────────────────────────────────────────────────
function buildTools() {
    return [
        {
            name: 'get_market_data',
            description: 'Devuelve precio en vivo, variacion del dia y (si aplica) ROE/P-E/dividend yield para un ticker en las categorias propias de Manfredi Investment (acciones y CEDEARs argentinos, acciones USA, bonos soberanos AR, cripto). Llamala SIEMPRE antes de afirmar un precio, variacion o metrica fundamental de una empresa. Si el ticker existe en mas de una categoria (ej. CEDEAR y accion USA), devuelve todas las coincidencias con su moneda -- no asumas cual es.',
            input_schema: {
                type: 'object',
                properties: {
                    symbol: { type: 'string', description: 'Ticker en mayusculas, ej. AAPL, GGAL, MELI, BTC' }
                },
                required: ['symbol']
            }
        },
        {
            name: 'get_price_history',
            description: 'Devuelve el historico de cierres diarios de un ticker ya trackeado por Manfredi Investment (misma cobertura que get_market_data). Usala para graficos de evolucion o para calcular tendencia/variacion en una ventana de dias.',
            input_schema: {
                type: 'object',
                properties: {
                    symbol: { type: 'string', description: 'Ticker en mayusculas' },
                    days: { type: 'integer', description: 'Cantidad de dias habiles hacia atras (5 a 180). Default 30.' }
                },
                required: ['symbol']
            }
        },
        {
            name: 'get_news',
            description: 'Devuelve titulares recientes de mercado argentino y Wall Street (Ambito, Cronista, Bloomberg Linea, Yahoo Finance, Investing.com, Seeking Alpha, The Economist). Usala para preguntas de coyuntura/macro o cuando el usuario pida "que esta pasando" con un tema. Podes pasar una palabra clave para filtrar.',
            input_schema: {
                type: 'object',
                properties: {
                    query: { type: 'string', description: 'Palabra clave opcional para filtrar titulares (ej. nombre de empresa, "tasas", "dolar")' }
                }
            }
        },
        {
            // Variante basica (no la _20260209 con filtrado dinamico): esa version
            // solo la soportan Opus/Sonnet 4.6+, y el router puede arrancar en
            // Haiku 4.5 -- se usa la basica para que funcione en cualquiera de
            // los dos modelos sin tener que cambiar el set de tools a mitad del loop.
            type: 'web_search_20250305',
            name: 'web_search',
            max_uses: 3
        }
    ];
}

async function toolGetMarketData(input, env) {
    const symbol = String((input && input.symbol) || '').toUpperCase().trim();
    if (!symbol) return { error: 'symbol requerido' };
    let data;
    try {
        const res = await env.MERCADOS.fetch(MERCADOS_BASE + '/mercados', { signal: AbortSignal.timeout(9000) });
        console.error('[warren] toolGetMarketData status:', res.status);
        if (!res.ok) return { error: 'No se pudo obtener datos de mercado en este momento.' };
        data = await res.json();
        console.error('[warren] toolGetMarketData categorias keys:', Object.keys((data && data.categorias) || {}));
    } catch (e) {
        console.error('[warren] toolGetMarketData fetch error:', e && e.name, e && e.message, e && e.stack);
        return { error: 'No se pudo conectar con la fuente de datos de mercado.' };
    }
    const matches = [];
    const categorias = (data && data.categorias) || {};
    for (const cat of Object.keys(categorias)) {
        const block = categorias[cat] || {};
        const item = (block.items || []).find(it => it.symbol === symbol);
        if (item) matches.push({ category: cat, currency: block.currency, price: item.price, changePct: item.change, name: item.name });
    }
    if (!matches.length) {
        return { error: `${symbol} no esta trackeado en los datos propios de Manfredi Investment. Si el usuario necesita este dato, usa web_search o decile que no lo podes confirmar con una fuente propia.` };
    }
    let fundamentals = null;
    try {
        const fRes = await env.MERCADOS.fetch(MERCADOS_BASE + '/fundamentals?symbol=' + encodeURIComponent(symbol), { signal: AbortSignal.timeout(9000) });
        if (fRes.ok) {
            const fd = await fRes.json();
            if (!fd.error) fundamentals = fd;
        }
    } catch (e) { /* fundamentals es best-effort, seguimos sin el */ }
    return { symbol, updated: data.updated, matches, fundamentals };
}

async function toolGetPriceHistory(input, env) {
    const symbol = String((input && input.symbol) || '').toUpperCase().trim();
    if (!symbol) return { error: 'symbol requerido' };
    const days = Math.min(180, Math.max(5, parseInt((input && input.days), 10) || 30));
    let mdata;
    try {
        const mres = await env.MERCADOS.fetch(MERCADOS_BASE + '/mercados', { signal: AbortSignal.timeout(9000) });
        if (!mres.ok) return { error: 'No se pudo resolver la categoria del activo.' };
        mdata = await mres.json();
    } catch (e) {
        return { error: 'No se pudo conectar con la fuente de datos de mercado.' };
    }
    let category = null;
    const categorias = (mdata && mdata.categorias) || {};
    for (const cat of Object.keys(categorias)) {
        if ((categorias[cat].items || []).some(it => it.symbol === symbol)) { category = cat; break; }
    }
    if (!category) {
        return { error: `${symbol} no esta trackeado en los datos propios de Manfredi Investment.` };
    }
    try {
        const hres = await env.MERCADOS.fetch(MERCADOS_BASE + '/historico?category=' + encodeURIComponent(category) + '&symbol=' + encodeURIComponent(symbol) + '&n=' + days, { signal: AbortSignal.timeout(9000) });
        const hdata = await hres.json();
        if (!hres.ok || hdata.error) return { error: hdata.error || 'No se pudo obtener el historico.' };
        return { symbol, category, days, closes: hdata.closes, min: hdata.min, max: hdata.max };
    } catch (e) {
        return { error: 'No se pudo obtener el historico.' };
    }
}

async function toolGetNews(input, env) {
    const query = String((input && input.query) || '').toLowerCase().trim();
    let data;
    try {
        const res = await env.NOTICIAS.fetch(NOTICIAS_BASE + '/noticias', { signal: AbortSignal.timeout(9000) });
        if (!res.ok) return { error: 'No se pudieron obtener noticias en este momento.' };
        data = await res.json();
    } catch (e) {
        return { error: 'No se pudo conectar con la fuente de noticias.' };
    }
    let items = [].concat(data.argentina || [], data.wallstreet || []);
    if (query) {
        items = items.filter(it => (it.titulo + ' ' + (it.resumen || '')).toLowerCase().includes(query));
    }
    items = items.slice(0, 8);
    return { updated: data.updated, items };
}

async function executeTool(name, input, env) {
    if (name === 'get_market_data') return toolGetMarketData(input, env);
    if (name === 'get_price_history') return toolGetPriceHistory(input, env);
    if (name === 'get_news') return toolGetNews(input, env);
    return { error: 'Tool desconocida: ' + name };
}

// ─── Llamada a la API de Anthropic ──────────────────────────────────────────
async function callClaude(apiKey, model, systemPrompt, messages, tools) {
    const requestBody = {
        model,
        // Sonnet 5 piensa (thinking) por defecto y max_tokens es el techo de
        // pensamiento + texto visible juntos -- con 1536 el thinking se comia
        // todo el presupuesto en respuestas complejas (analisis con varias
        // tools) y no dejaba nada para el texto, cortando en seco con
        // stop_reason "max_tokens" y respuesta vacia. Confirmado en pruebas.
        max_tokens: 4096,
        system: [{ type: 'text', text: systemPrompt, cache_control: { type: 'ephemeral' } }],
        messages
    };
    if (tools && tools.length) requestBody.tools = tools;
    // effort medio: recorta directamente cuanto piensa antes de responder (en
    // vez de solo darle mas techo a max_tokens). Solo Sonnet 5 lo soporta --
    // Haiku 4.5 devuelve 400 "This model does not support the effort parameter"
    // si se lo mandamos (confirmado en pruebas).
    if (model === MODEL_SONNET) requestBody.output_config = { effort: 'medium' };

    const response = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'x-api-key': apiKey,
            'anthropic-version': '2023-06-01'
        },
        body: JSON.stringify(requestBody)
    });

    if (!response.ok) {
        const errText = await response.text();
        console.error('Anthropic API error:', response.status, errText);
        throw new Error('anthropic_api_error');
    }
    return response.json();
}

function extractText(content) {
    return (content || [])
        .filter(b => b.type === 'text')
        .map(b => b.text)
        .join('\n')
        .trim();
}

export default {
    async fetch(request, env) {
        if (request.method === 'OPTIONS') {
            return new Response(null, { status: 204, headers: CORS_HEADERS });
        }

        const url = new URL(request.url);
        try {
            if (request.method === 'GET' && url.pathname === '/conversations') return await handleConversationsList(request, env);
            if (request.method === 'GET' && url.pathname === '/conversation') return await handleConversationGet(request, env);
            if (request.method === 'POST' && url.pathname === '/conversation/save') return await handleConversationSave(request, env);
            if (request.method === 'POST' && url.pathname === '/conversation/delete') return await handleConversationDelete(request, env);
        } catch (err) {
            return new Response(JSON.stringify({ error: err.message }), { status: 500, headers: JSON_HEADERS });
        }

        if (request.method !== 'POST') {
            return new Response('Method Not Allowed', { status: 405, headers: CORS_HEADERS });
        }

        const ANTHROPIC_API_KEY = env.ANTHROPIC_API_KEY;
        if (!ANTHROPIC_API_KEY) {
            console.error('ERROR: ANTHROPIC_API_KEY no encontrada');
            return new Response(JSON.stringify({ response: 'Error de configuracion: API key no encontrada.' }), { headers: JSON_HEADERS });
        }

        try {
            const body = await request.json();
            const { messages, systemPrompt, email, enableTools } = body;
            const isAdmin = email && ADMIN_EMAILS.includes(email.toLowerCase());

            // Verificar consultas disponibles (admin no tiene limite). Si el
            // worker de membresias esta caido/no responde, dejamos pasar la
            // consulta en vez de romper toda la respuesta de Warren por eso --
            // el peor caso es no descontar una consulta, no un error generico.
            if (email && !isAdmin) {
                try {
                    const consultasRes = await env.MEMBERSHIPS.fetch(`${MEMBERSHIPS_BASE}/consultas?email=${encodeURIComponent(email)}`);
                    const consultasData = await consultasRes.json();
                    if (consultasData.consultas === 0) {
                        return new Response(JSON.stringify({ response: 'Agotaste tus 100 consultas del mes. Se renuevan el 1 del proximo mes.', limitAlcanzado: true }), { headers: JSON_HEADERS });
                    }
                } catch (e) {
                    console.error('[warren] chequeo de consultas fallo, dejamos pasar:', e && e.message);
                }
            }

            const tools = enableTools ? buildTools() : null;
            const claudeMessages = messages.map(m => ({
                role: m.role === 'assistant' ? 'assistant' : 'user',
                content: m.content
            }));

            const lastUserMsg = [...claudeMessages].reverse().find(m => m.role === 'user');
            let model = chooseInitialModel(lastUserMsg && typeof lastUserMsg.content === 'string' ? lastUserMsg.content : '');

            let finalText = 'No pude procesar tu consulta. Intenta de nuevo.';
            let iterations = 0;
            let usedTool = false;
            let hitIterationLimit = false;
            const trace = [];

            while (iterations < MAX_TOOL_ITERATIONS) {
                iterations++;
                const data = await callClaude(ANTHROPIC_API_KEY, model, systemPrompt || 'Sos Warren, asesor financiero de Manfredi Investment.', claudeMessages, tools);
                const toolCallsThisTurn = (data.content || []).filter(b => b.type === 'tool_use').map(b => ({ name: b.name, input: b.input }));
                trace.push({ iteration: iterations, model, stop_reason: data.stop_reason, tools: toolCallsThisTurn, text: extractText(data.content) });

                // Claude a veces manda texto explicativo junto con el tool_use --
                // lo guardamos como mejor respuesta disponible por si se agota el
                // limite de iteraciones antes de terminar.
                const partialText = extractText(data.content);
                if (partialText) finalText = partialText;

                if (data.stop_reason !== 'tool_use') {
                    break;
                }
                if (iterations >= MAX_TOOL_ITERATIONS) {
                    hitIterationLimit = true;
                    break;
                }

                // Se pidio usar una tool: ejecutarla y, de aca en mas, escalar a Sonnet
                // para la sintesis final -- es donde mas importa la calidad.
                usedTool = true;
                model = MODEL_SONNET;

                claudeMessages.push({ role: 'assistant', content: data.content });
                const toolUseBlocks = (data.content || []).filter(b => b.type === 'tool_use');
                const toolResults = [];
                for (const block of toolUseBlocks) {
                    let result;
                    try {
                        result = await executeTool(block.name, block.input, env);
                    } catch (e) {
                        result = { error: 'Error interno ejecutando la herramienta.' };
                    }
                    toolResults.push({
                        type: 'tool_result',
                        tool_use_id: block.id,
                        content: JSON.stringify(result),
                        is_error: !!(result && result.error)
                    });
                }
                claudeMessages.push({ role: 'user', content: toolResults });
            }

            if (hitIterationLimit && finalText === 'No pude procesar tu consulta. Intenta de nuevo.') {
                // Se agoto el presupuesto de vueltas de tools sin que Claude escribiera
                // texto explicativo en ninguna -- pasa con pedidos que requieren mas
                // llamadas de las que cubrimos (ej. datos historicos multi-anio que
                // nuestras tools no tienen). Mejor avisar esto que devolver el generico.
                finalText = 'Esta consulta necesita más pasos de investigación de los que puedo hacer en una sola respuesta ahora mismo (probablemente datos históricos que mis fuentes no cubren directo). Probá pedirme algo más acotado -- por ejemplo el precio y las métricas actuales, o un aspecto puntual -- y lo resuelvo sin problema.';
            }

            // Restar 1 consulta despues de una respuesta exitosa (unico punto de
            // descuento -- el frontend no resta por su cuenta).
            if (email && !isAdmin) {
                try {
                    const restarRes = await env.MEMBERSHIPS.fetch(`${MEMBERSHIPS_BASE}/restar-consulta`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ email })
                    });
                    const restarBody = await restarRes.text();
                    console.error('[warren] restar-consulta status:', restarRes.status, 'body:', restarBody);
                } catch (e) {
                    console.error('[warren] restar-consulta fetch error:', e && e.name, e && e.message);
                }
            }

            // El trace queda solo en logs (observabilidad) -- no se lo mandamos
            // al cliente, es info interna de que tools se llamaron y por que.
            console.error('[warren] trace:', JSON.stringify(trace));

            return new Response(JSON.stringify({ response: finalText, model, usedTool }), { headers: JSON_HEADERS });

        } catch (err) {
            console.error('Warren worker error:', err);
            return new Response(JSON.stringify({ response: 'Hubo un error inesperado. Por favor intenta nuevamente.' }), { headers: JSON_HEADERS });
        }
    }
};
