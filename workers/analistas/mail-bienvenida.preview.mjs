// Vista previa del mail de bienvenida con un autor de ejemplo.
// node workers/analistas/mail-bienvenida.preview.mjs [matricula] > salida.html
import { mailBienvenida } from './mail-bienvenida.js';
const a = { nombre: 'Martín Gómez', rol: 'Analista de renta variable', habilitadoEn: new Date().toISOString() };
if (process.argv[2] === 'matricula') a.registro = { organismo: 'CNV', categoria: 'Agente Productor', numero: '1234' };
process.stdout.write(mailBienvenida('martin.gomez@gmail.com', a).html);
