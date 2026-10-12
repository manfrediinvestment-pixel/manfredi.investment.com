---
name: revisar-analisis
description: "Use when the user asks to review the pieces that guest analysts sent to the 'Análisis e informes' section of manfredinvestment.com — 'revisá los análisis', 'hay análisis para revisar', 'revisá lo que mandaron los analistas', 'revisá el informe de [autor]'. Reads every pending submission (PDF or text) end to end, checks it against the section's hard rules (no personalized buy/sell advice from non-advisors, no selling courses/signals/paid groups, only allowed links, no guaranteed returns, no plagiarism), verifies the key numbers against primary sources, grades quality, and writes one revision.json per submission with a verdict (publicar / cambios / rechazar), a traffic-light checklist with page references and a ready-to-send message to the author. The verdicts show up in the creator Panel ('Análisis por revisar'), where the user only approves or rejects. Runs locally in Claude Code: zero API cost."
metadata:
  version: 0.1.0
---

# Revisar análisis de autores invitados — Manfredi Investment

El usuario (Ignacio, el creador del sitio) **no quiere leer cada análisis uno por uno**.
Vos lo leés entero, lo controlás y le dejás un veredicto claro en el Panel. Él mira el
semáforo, abre el PDF solo si algo le llama la atención y toca **Aprobar** o **Rechazar**.

Nunca publicás ni rechazás vos: **la decisión final es siempre del usuario**.

## 1. De dónde salen los envíos

Cada envío es una carpeta con `envio.json` (lo que completó el autor en el portal de carga)
y el archivo (`analisis.pdf`) si es PDF:

```
revision/<origen>/<id>/
  envio.json      ← datos del envío (ver esquema abajo)
  analisis.pdf    ← solo si formato = "pdf"
  tapa.jpg        ← página 1 del PDF (la genera el portal)
  revision.json   ← LO QUE ESCRIBÍS VOS
```

- `revision/prueba/` tiene 3 envíos de prueba (uno bueno, uno con cambios, uno para
  rechazar). Sirven para probar la skill y son los que se ven en el Panel en local.
- `revision/pendientes/` es donde van a caer los envíos reales. **Todavía no existe el
  portal de carga** (worker + R2): cuando exista, el paso 0 de esta skill es bajar los
  pendientes del worker a esta carpeta y el paso 6 es subir las revisiones. Hasta
  entonces, si el usuario te pasa un PDF a mano, creá la carpeta vos con su `envio.json`.

Revisá **solo** los envíos que no tienen `revision.json`, salvo que el usuario pida
revisar de nuevo uno puntual.

### envio.json

```json
{
  "id": "2026-10-12-romero-elecciones",
  "autor": { "slug": "lucia-romero", "nombre": "Lucía Romero", "email": "…", "rol": "Politóloga (UBA)",
             "pais": "AR", "asesor": false, "links": { "linkedin": "…", "newsletter": "…" } },
  "titulo": "…", "categoria": "macro|acciones|bonos|politica|trading", "resumen": "2 líneas",
  "activos": ["AL30", "GD30"], "formato": "pdf|texto", "cuerpo": "solo si formato = texto",
  "paginas": 12, "enviado": "2026-10-12T10:42:00-03:00",
  "declaraciones": { "autoria": true, "sinRecomendaciones": true, "posiciones": "Tengo GD30" }
}
```

`asesor: true` solo si el autor acreditó matrícula vigente (CNV en Argentina, CNMV en
España, etc.). Por defecto es `false`.

## 2. Leer el análisis entero

- PDF: leelo con Read **página por página** (de a 20 páginas máximo por llamada). No
  alcanza con la tapa y el resumen: los problemas suelen estar en el medio o en la última
  página ("contactame", "link en bio", "precio objetivo").
- Texto: el campo `cuerpo`.
- Anotá el número de página de cada cosa que marques. En texto usá el subtítulo más cercano.

## 3. Reglas duras (cualquier "mal" = no se publica así)

Las fijó el usuario el 09-oct-2026. Son las que hacen que la sección sea segura y seria.

| # | Regla | Qué buscar | Estado |
|---|---|---|---|
| R1 | **Sin recomendaciones personalizadas** si `asesor = false` | "comprá", "conviene comprar/vender", "hay que entrar", "yo me posicionaría", precio objetivo presentado como orden, "stop en X" dirigido al lector, carteras sugeridas con % | `ojo` si es una frase reformulable; `mal` si todo el texto es una recomendación |
| R2 | **Nada de venta** | cursos, mentorías, señales pagas, grupos VIP de Telegram/WhatsApp/Discord, links de referido a brokers, cupones, "escribime por privado para más" | `mal` siempre |
| R3 | **Solo links permitidos** | LinkedIn, redes, lugar de trabajo. Newsletter **gratis** de análisis: `ojo` (decide el usuario, todavía no lo definió). Cualquier otro link comercial: `mal` | |
| R4 | **Sin promesas de rentabilidad** | "rendimiento asegurado", "no puede bajar", "x2 seguro", "sin riesgo" | `mal` |
| R5 | **Autoría propia** | Buscá en la web 2 o 3 frases distintivas entre comillas. Si aparecen en otro sitio sin cita: `mal` (plagio). Gráficos o tablas de terceros sin fuente: `ojo` | |
| R6 | **Sin ataques personales ni información privilegiada** | insultos a personas, datos no públicos de empresas, rumores presentados como hechos | `mal` |
| R7 | **Declaración de posiciones** | si menciona activos y `declaraciones.posiciones` está vacío | `ojo` |

**Reformular no es censurar**: si una frase rompe R1, proponé en el mensaje al autor la
versión en lenguaje de análisis ("conviene comprar GD30" → "el GD30 ofrece más valor
relativo que el AL30 en este escenario"). La opinión del autor se respeta.

## 4. Datos y calidad

**Cifras clave** (las 3 a 6 que sostienen la tesis: riesgo país, reservas, inflación,
tasas, precios, ratios, resultados electorales). Verificá cada una con WebSearch/WebFetch
contra la fuente primaria (BCRA, INDEC, Ministerio de Economía, BYMA, balances de la
empresa, JP Morgan para el EMBI, justicia electoral) **a la fecha que dice el autor**.

- Coincide (tolerancia de redondeo o de un par de días): `ok`.
- Distinto pero explicable (otra fecha, otra serie): `ojo`, decí cuál es el dato correcto y la fuente.
- Mal o inventado: `ojo` si no cambia la conclusión, `mal` si la tesis se apoya en ese número.
- No se puede verificar (dato propio del autor, encuesta privada): `ojo` con "pedir fuente".

Usá el mismo rigor que en los informes del sitio: recalculá con Python si hay cuentas
(spreads, TIR, variaciones, ROE real). No a ojo.

**Calidad** (no bloquea, pero suma o resta puntaje):
- Tesis clara en la primera página. Datos con fecha y fuente.
- El título y el resumen dicen lo mismo que el texto. El resumen entra en 2 líneas.
- La `categoria` es la correcta.
- Ortografía y redacción: marcá solo errores que se noten, no estilo.
- Extensión razonable: un PDF de 2 páginas sin datos es flojo; uno de 40 sin conclusión también.

## 5. Veredicto

- `publicar`: ningún `mal` y como mucho detalles menores de `ojo` que no hace falta tocar.
- `cambios`: hay `ojo` que el autor tiene que corregir (o un `mal` de R1 reformulable).
- `rechazar`: cualquier `mal` de R2, R4, R5 o R6, o un texto que es entero una recomendación.

`puntaje` de 0 a 100 = solo calidad del análisis (datos, claridad, profundidad),
independiente de las reglas. Sirve para que el usuario ordene qué publicar primero.

### revision.json (lo que lee el Panel)

```json
{
  "veredicto": "publicar|cambios|rechazar",
  "puntaje": 82,
  "resumen": "Una o dos oraciones para el usuario: de qué trata y si está para publicar.",
  "checks": [
    { "estado": "ok|ojo|mal", "regla": "R1|R2|…|datos|calidad", "titulo": "Corto, sin punto final",
      "detalle": "Qué pasa y qué hacer", "pagina": 4 }
  ],
  "datos": [
    { "dato": "Riesgo país 620 pb (03-oct)", "estado": "ok|ojo|mal", "fuente": "https://…", "nota": "JP Morgan EMBI: 618 pb" }
  ],
  "mensajeAutor": "Mensaje listo para mandar al autor si hay cambios o rechazo. Vacío si es publicar.",
  "revisadoEn": "2026-10-12T15:30:00-03:00",
  "revisor": "skill revisar-analisis 0.1.0"
}
```

Reglas para escribir el revision.json:
- **Primero los `mal`, después los `ojo`, al final los `ok`.** Los `ok` van igual: le dan
  tranquilidad al usuario de que se revisó ("Sin venta de cursos ni links comerciales").
- `titulo` corto (máx. ~60 caracteres), `detalle` concreto con la cita textual entre comillas.
- `mensajeAutor`: en el registro del autor (si `pais` = "ES" usá tú y "podrás"; si es de
  Argentina, voseo), cordial, en el orden de importancia, con la reformulación propuesta.
  Firmado "Ignacio · Manfredi Investment". Nunca menciones que lo revisó una IA.
- Fechas ISO con zona horaria de Buenos Aires (-03:00).

## 6. Cerrar

1. Validá cada revision.json con `python -m json.tool` y reescribí
   `revision/<origen>/index.json` = `{"origen": "<origen>", "envios": [ids con envio.json]}`
   (el Panel en local lee ese índice; el server estático no lista carpetas).
2. Si el portal ya existe: subí las revisiones al worker (pendiente de construir).
3. Abrí el Panel en local para ver cómo quedó:
   `python -m http.server 8800` en la raíz del repo y
   `http://127.0.0.1:8800/?revision=prueba#panel` (en local muestra `revision/prueba`
   sin necesidad de iniciar sesión).
4. Contale al usuario en 3 o 4 líneas: cuántos revisaste, cuáles están para publicar,
   cuáles necesitan cambios y si hay alguno para rechazar, con el motivo en una frase.
   **No** le repitas los checklists: están en el Panel.
