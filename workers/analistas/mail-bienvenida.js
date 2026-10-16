// workers/analistas/mail-bienvenida.js — mail que recibe un autor cuando lo habilitás en el Panel.
//
// Armado con tablas y estilos en línea (Gmail no lee <style> de forma confiable ni SVG).
// Sin texto gris: blanco para leer, champagne para etiquetas y acentos, líneas finas para ordenar.
// Vista previa: node workers/analistas/mail-bienvenida.preview.mjs > salida.html

const SITIO = 'https://manfredinvestment.com';
const BLANCO = '#f3f6fb', CHAMPAGNE = '#e9d3a0', CLARO = '#f3e3bd', ORO = '#d8b66e';
const LINEA = '#26355a', FONDO = '#050912', PAPEL = '#0b1222';
const SANS = "Arial,Helvetica,sans-serif", SERIF = "Georgia,'Times New Roman',serif";

const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const etiqueta = t => `<p style="margin:0;font-family:${SANS};font-size:10px;font-weight:bold;letter-spacing:3px;text-transform:uppercase;color:${CHAMPAGNE};">${t}</p>`;
const filete = (ancho = 36) => `<table role="presentation" cellpadding="0" cellspacing="0"><tr><td width="${ancho}" height="1" style="background:${ORO};font-size:1px;line-height:1px;">&nbsp;</td></tr></table>`;

function fecha(iso) {
  const d = iso ? new Date(iso) : new Date();
  return d.toLocaleDateString('es-AR', { timeZone: 'America/Argentina/Buenos_Aires', day: '2-digit', month: '2-digit', year: 'numeric' }).replace(/\//g, ' · ');
}
function iniciales(nombre) {
  const p = String(nombre || '').trim().split(/\s+/).filter(Boolean);
  return ((p[0] || '')[0] || '').toUpperCase() + ((p.length > 1 ? p[p.length - 1][0] : '') || '').toUpperCase();
}

// a = perfil guardado en meta/habilitados.json (nombre, rol, habilitadoEn, registro?)
export function mailBienvenida(email, a) {
  const nombre = a.nombre || '';
  const pila = esc(nombre.split(' ')[0]);
  const reg = a.registro;
  const asunto = 'Tu firma, en Manfredi Investment';

  const paso = (n, titulo, texto) => `
    <tr><td style="padding:18px 0;border-top:1px solid ${LINEA};">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr>
        <td width="46" valign="top" style="font-family:${SERIF};font-size:20px;line-height:1.2;color:${ORO};">${n}</td>
        <td valign="top">
          <p style="margin:0;font-family:${SANS};font-size:15px;font-weight:bold;color:${BLANCO};">${titulo}</p>
          <p style="margin:6px 0 0;font-family:${SANS};font-size:14px;line-height:1.6;color:${BLANCO};">${texto}</p>
        </td>
      </tr></table>
    </td></tr>`;
  const regla = texto => `
    <tr><td width="22" valign="top" style="padding:7px 0;font-family:${SANS};font-size:14px;line-height:1.6;color:${ORO};">—</td>
      <td valign="top" style="padding:7px 0;font-family:${SANS};font-size:14px;line-height:1.6;color:${BLANCO};">${texto}</td></tr>`;
  const dato = (rotulo, valor, ancho) => `
    <td width="${ancho}" valign="top" style="padding:14px 16px;">
      ${etiqueta(rotulo)}
      <p style="margin:6px 0 0;font-family:${SANS};font-size:13px;line-height:1.4;color:${BLANCO};word-break:break-all;">${valor}</p>
    </td>`;

  const html = `<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light only">
<title>${asunto}</title>
<style>@media (max-width:480px){.px{padding-left:20px!important;padding-right:20px!important}}</style>
</head>
<body style="margin:0;padding:0;background:${FONDO};">
<div style="display:none;max-height:0;overflow:hidden;">Desde hoy publicás en Análisis e informes. Te cuento cómo empezar.</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:${FONDO};">
<tr><td align="center" style="padding:28px 12px;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:600px;background:${PAPEL};border:1px solid ${LINEA};border-radius:14px;overflow:hidden;">

<!-- Filete dorado -->
<tr><td height="1" bgcolor="${ORO}" style="background:${ORO};background-image:linear-gradient(90deg,#0b1222,#c9a24f 20%,#efd9a4 50%,#c9a24f 80%,#0b1222);font-size:1px;line-height:1px;">&nbsp;</td></tr>

<!-- Encabezado y portada -->
<tr><td class="px" bgcolor="${PAPEL}" style="background:${PAPEL};background-image:linear-gradient(170deg,#070c19 0%,#0f1b36 62%,#16274a 100%);padding:26px 34px 40px;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr>
    <td><table role="presentation" cellpadding="0" cellspacing="0"><tr>
      <td><img src="${SITIO}/assets/img/logo-mark-512.png" width="40" height="40" alt="Manfredi Investment" style="display:block;border:0;width:40px;height:40px;"></td>
      <td style="padding-left:12px;font-family:${SANS};font-size:11px;font-weight:bold;letter-spacing:3px;color:${CHAMPAGNE};">MANFREDI INVESTMENT</td>
    </tr></table></td>
    <td align="right" style="font-family:${SANS};font-size:10px;letter-spacing:3px;color:${CHAMPAGNE};">AUTORES INVITADOS</td>
  </tr></table>

  <p style="margin:52px 0 0;font-family:${SANS};font-size:10px;font-weight:bold;letter-spacing:4px;color:${CHAMPAGNE};">CARTA DE BIENVENIDA</p>
  <p style="margin:14px 0 0;font-family:${SERIF};font-size:32px;line-height:1.15;color:${BLANCO};">Tu firma,<br><i style="color:${CLARO};">en Manfredi.</i></p>
  <div style="margin:22px 0 0;">${filete(44)}</div>
  <p style="margin:20px 0 0;font-family:${SERIF};font-size:17px;line-height:1.6;color:${BLANCO};">Hola ${pila}: desde hoy publicás en la sección <b style="color:${CLARO};font-weight:normal;font-style:italic;">Análisis e informes</b>.</p>
</td></tr>

<!-- Credencial -->
<tr><td class="px" style="padding:30px 34px 6px;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border:1px solid ${LINEA};border-radius:12px;background:#0d1730;">
    <tr><td style="padding:20px 16px 18px;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr>
        <td width="56" valign="middle">
          <table role="presentation" cellpadding="0" cellspacing="0"><tr><td width="44" height="44" align="center" valign="middle" style="border:1px solid ${ORO};border-radius:22px;font-family:${SERIF};font-size:16px;letter-spacing:1px;color:${CLARO};">${esc(iniciales(nombre))}</td></tr></table>
        </td>
        <td valign="middle">
          <p style="margin:0;font-family:${SERIF};font-size:20px;line-height:1.25;color:${BLANCO};">${esc(nombre)}</p>
          ${a.rol ? `<p style="margin:4px 0 0;font-family:${SANS};font-size:13px;line-height:1.4;color:${BLANCO};">${esc(a.rol)}</p>` : ''}
        </td>
        <td align="right" valign="top" style="font-family:${SANS};font-size:10px;font-weight:bold;letter-spacing:2px;color:${ORO};white-space:nowrap;">&#10022; AUTOR</td>
      </tr></table>
    </td></tr>
    <tr><td height="1" style="background:${LINEA};font-size:1px;line-height:1px;">&nbsp;</td></tr>
    <tr><td>
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr>
        ${dato('Habilitado', fecha(a.habilitadoEn), '34%')}
        <td width="1" style="background:${LINEA};font-size:1px;">&nbsp;</td>
        ${reg
          ? dato('Matrícula', esc(reg.organismo) + ' · ' + esc(reg.numero), '66%')
          : dato('Cuenta', esc(email), '66%')}
      </tr></table>
    </td></tr>
  </table>
</td></tr>

<!-- Carta -->
<tr><td class="px" style="padding:30px 34px 4px;font-family:${SERIF};font-size:17px;line-height:1.7;color:${BLANCO};">
  <p style="margin:0 0 16px;">Manfredi Investment nació para leer el mercado con la profundidad de un profesional y contarlo claro. Abrir la sección a autores invitados es el paso que sigue: más miradas, más temas, el mismo rigor.</p>
  <p style="margin:0;">No la abrimos a cualquiera. Habilitamos a pocos, uno por uno, y vos estás en ese grupo. Lo que publiques sale con tu nombre y tu perfil, para que tu trabajo llegue a quien lo tiene que leer.</p>
</td></tr>

<!-- Pasos -->
<tr><td class="px" style="padding:34px 34px 0;">
  ${etiqueta('Cómo publicar')}
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin-top:14px;">
    ${paso('01', 'Entrá con este mail', `Iniciá sesión con <b style="color:${CLARO};">${esc(email)}</b>, con Google o con mail y contraseña. Tiene que ser exactamente este.`)}
    ${paso('02', 'Abrí Mi espacio de autor', 'Está junto a las pestañas de Noticias. Primero completá tu perfil: foto, bio y links.')}
    ${paso('03', 'Subí tu análisis', 'En PDF o como texto, con un resumen de dos líneas. Lo revisamos y te avisamos por mail cuando sale publicado o si hace falta un ajuste.')}
  </table>
</td></tr>

<!-- Botón -->
<tr><td class="px" style="padding:12px 34px 6px;">
  <table role="presentation" cellpadding="0" cellspacing="0"><tr>
    <td style="border:1px solid ${ORO};border-radius:8px;background:#101c38;">
      <a href="${SITIO}/#autor" style="display:inline-block;padding:12px 22px;font-family:${SANS};font-size:13px;font-weight:bold;letter-spacing:1px;color:${CLARO};text-decoration:none;">Ir a Mi espacio de autor &nbsp;&rarr;</a>
    </td>
  </tr></table>
</td></tr>

<!-- Reglas -->
<tr><td class="px" style="padding:36px 34px 0;">
  ${etiqueta('Las reglas del juego')}
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin-top:12px;">
    ${regla('Cada análisis lleva tu nombre y suma a tu perfil público, que podés compartir.')}
    ${regla('Podés linkear tu LinkedIn, tus redes o el lugar donde trabajás.')}
    ${reg
      ? regla(`Con tu matrícula (${esc(reg.organismo)} ${esc(reg.numero)}) podés dar recomendaciones generales, con tu propio aviso de riesgo.`)
      : regla('Nada de recomendaciones de compra o venta: análisis, datos y opinión fundada.')}
    ${regla('Sin promesas de rentabilidad, venta de cursos o señales, ni información privilegiada.')}
    ${regla('Si querés retirar un análisis, lo bajamos dentro de los 5 días hábiles.')}
  </table>
  <p style="margin:14px 0 0;font-family:${SANS};font-size:13px;"><a href="${SITIO}/terminos-autores.html" style="color:${CLARO};text-decoration:underline;">Leer los Términos de colaboración</a></p>
</td></tr>

<!-- Firma -->
<tr><td class="px" style="padding:40px 34px 36px;">
  ${filete(44)}
  <p style="margin:20px 0 0;font-family:${SERIF};font-size:17px;font-style:italic;color:${BLANCO};">Te damos la bienvenida,</p>
  <p style="margin:8px 0 0;font-family:${SERIF};font-size:22px;color:${CLARO};">Ignacio</p>
  <p style="margin:4px 0 0;font-family:${SANS};font-size:10px;font-weight:bold;letter-spacing:3px;color:${CHAMPAGNE};">FUNDADOR · MANFREDI INVESTMENT</p>
</td></tr>

<!-- Pie -->
<tr><td class="px" style="padding:20px 34px 24px;border-top:1px solid ${LINEA};">
  <p style="margin:0;font-family:${SANS};font-size:12px;line-height:1.6;color:${BLANCO};">Recibís este mail porque habilitamos <span style="color:${CLARO};">${esc(email)}</span> como autor invitado.</p>
  <p style="margin:10px 0 0;"><a href="${SITIO}" style="font-family:${SANS};font-size:11px;letter-spacing:2px;color:${CHAMPAGNE};text-decoration:none;">MANFREDINVESTMENT.COM</a></p>
</td></tr>

</table>
</td></tr>
</table>
</body>
</html>`;
  return { asunto, html };
}
