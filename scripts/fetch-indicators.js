const https = require('https');
const fs = require('fs');
const path = require('path');

const API_KEY = process.env.AV_API_KEY;
if (!API_KEY) {
  console.error('AV_API_KEY no definida');
  process.exit(1);
}

// Lee los tickers desde el JSON que el Action va a pasarle
const tickers = JSON.parse(process.env.MI_TICKERS || '[]');
if (!tickers.length) {
  console.error('No hay tickers');
  process.exit(1);
}

const outDir = path.join(__dirname, '..', 'data', 'indicators');
fs.mkdirSync(outDir, { recursive: true });

function get(url) {
  return new Promise((resolve, reject) => {
    https.get(url, res => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => {
        try { resolve(JSON.parse(data)); }
        catch(e) { reject(e); }
      });
    }).on('error', reject);
  });
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

async function fetchTicker(ticker) {
  const base = `https://www.alphavantage.co/query?apikey=${API_KEY}`;
  try {
    // RSI
    const rsiData = await get(`${base}&function=RSI&symbol=${ticker}&interval=daily&time_period=14&series_type=close`);
    await sleep(12000); // respeta límite 5 req/min plan gratuito

    // MACD
    const macdData = await get(`${base}&function=MACD&symbol=${ticker}&interval=daily&series_type=close`);
    await sleep(12000);

    // ADX
    const adxData = await get(`${base}&function=ADX&symbol=${ticker}&interval=daily&time_period=14`);
    await sleep(12000);

    // EMA 20, 50, 200 + precio
    const ema20Data = await get(`${base}&function=EMA&symbol=${ticker}&interval=daily&time_period=20&series_type=close`);
    await sleep(12000);
    const ema50Data = await get(`${base}&function=EMA&symbol=${ticker}&interval=daily&time_period=50&series_type=close`);
    await sleep(12000);
    const ema200Data = await get(`${base}&function=EMA&symbol=${ticker}&interval=daily&time_period=200&series_type=close`);
    await sleep(12000);
    const priceData = await get(`${base}&function=GLOBAL_QUOTE&symbol=${ticker}`);
    await sleep(12000);

    // Extraer último valor de cada indicador
    const rsiVals  = rsiData['Technical Analysis: RSI']  || {};
    const macdVals = macdData['Technical Analysis: MACD'] || {};
    const adxVals  = adxData['Technical Analysis: ADX']  || {};
    const ema20Vals  = ema20Data['Technical Analysis: EMA']  || {};
    const ema50Vals  = ema50Data['Technical Analysis: EMA']  || {};
    const ema200Vals = ema200Data['Technical Analysis: EMA'] || {};

    const rsiDate   = Object.keys(rsiVals)[0];
    const macdDate  = Object.keys(macdVals)[0];
    const adxDate   = Object.keys(adxVals)[0];
    const ema20Date  = Object.keys(ema20Vals)[0];
    const ema50Date  = Object.keys(ema50Vals)[0];
    const ema200Date = Object.keys(ema200Vals)[0];
    const price = parseFloat(priceData['Global Quote']?.['05. price'] || 0);

    if (!rsiDate || !macdDate || !adxDate) {
      console.warn(`[${ticker}] Datos incompletos — saltando`);
      return;
    }

    const result = {
      ticker,
      updated: new Date().toISOString().split('T')[0],
      rsi:  parseFloat(rsiVals[rsiDate]['RSI']),
      macd: parseFloat(macdVals[macdDate]['MACD']),
      macd_signal: parseFloat(macdVals[macdDate]['MACD_Signal']),
      adx:  parseFloat(adxVals[adxDate]['ADX']),
      ema: {
        price,
        ema20:  parseFloat(ema20Vals[ema20Date]?.['EMA']  || 0),
        ema50:  parseFloat(ema50Vals[ema50Date]?.['EMA']  || 0),
        ema200: parseFloat(ema200Vals[ema200Date]?.['EMA'] || 0)
      }
    };

    const outPath = path.join(outDir, `${ticker}.json`);
    fs.writeFileSync(outPath, JSON.stringify(result, null, 2));
    console.log(`✅ ${ticker} → ${outPath}`);

  } catch(e) {
    console.warn(`[${ticker}] Error:`, e.message);
  }
}

(async () => {
  for (const ticker of tickers) {
    await fetchTicker(ticker);
  }
  console.log('Listo.');
})();
