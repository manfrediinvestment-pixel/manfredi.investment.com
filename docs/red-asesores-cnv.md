# Red de Asesores: marco CNV y modelo de cobro

Relevamiento actualizado al 08-oct-2026 sobre el texto vigente de las Normas CNV (N.T. 2013 y mod.). No reemplaza la opinión de un abogado de mercado de capitales.

## El modelo planteado

1. Asesores registrados en la CNV consiguen clientes dentro de la plataforma.
2. Cada asesor tiene una sección privada por cliente: cartera cargada a mano o desde el PDF de tenencias del broker, más herramientas de análisis.
3. Manfredi cobra una licencia anual por el uso de la plataforma.
4. Manfredi cobra un porcentaje de la mensualidad que el asesor le cobra a cada cliente.
5. No hay custodia de activos.

## Qué dice la norma, pieza por pieza

### Software (puntos 2 y 3): no requiere registro
Una herramienta para que un asesor registrado vea y analice carteras, cobrada como licencia, no es asesoramiento, intermediación, gestión de órdenes ni administración de carteras. Sigue siendo así mientras Manfredi no recomiende inversiones, no reciba órdenes y no toque fondos.

### Conseguir clientes para los asesores (punto 1): es una actividad regulada
- **Agente Productor (Título VII, Cap. V, art. 2):** "el AP podrá captar clientes para los AN, ALyC y/o AAGI" con los que tenga convenio. Captar clientes para agentes es la actividad típica del AP, y para hacerla hay que estar inscripto.
- **Publicidad a través de terceros (RG 1048/2025, art. 7° bis):** los agentes pueden difundir sus servicios a través de terceros, pero el acuerdo "podrá celebrarse únicamente" con: (1) sujetos registrados ante la CNV que asesoren, administren, intermedien o negocien, y PSAV; o (2) entidades financieras, Proveedores de Servicios de Pago y Plataformas de Financiamiento MiPyME. Una plataforma sin registro no está en esa lista.

### Porcentaje de la mensualidad del asesor (punto 4): el punto más delicado
Cobrar un porcentaje de lo que paga cada cliente que llegó por la plataforma es retribución por captación. Si Manfredi no está registrado, eso es hacer la actividad de un AP sin inscripción (Ley 26.831, art. 117 inc. c, y régimen sancionatorio del art. 132).

Si Manfredi estuviera registrado como AP, la norma lo contempla: el art. 8° del Cap. V obliga al AP a informar la "modalidad de retribución" y, cada trimestre, las retribuciones de clientes y las "comisiones percibidas de los Agentes" con los que tiene convenio.

### Sin custodia (punto 5): necesario pero no suficiente
Ni el AP (art. 4 b y c) ni el AAGI (art. 3) pueden recibir ni custodiar fondos o valores de clientes, así que no custodiar está bien. Pero eso no cambia el análisis de los puntos 1 y 4.

Si la plataforma cobra la mensualidad al cliente y le transfiere su parte al asesor, conviene hacerlo a través de un procesador de pagos regulado (Mercado Pago, Stripe u otro PSP) con división de cobro, y no con una cuenta propia de Manfredi.

## Tres caminos

### A. Software puro (sin registro de Manfredi)
- Licencia anual + **cargo fijo por cliente activo en la consola**, igual para todos y sin relación con lo que cobra el asesor.
- Directorio de asesores neutral: sin rankings pagos y sin que Manfredi asigne o recomiende un asesor según el perfil del cliente.
- Contras: no podés cobrar un porcentaje de la mensualidad. El directorio queda en zona gris frente al art. 7° bis, así que conviene una consulta legal y, si es posible, una consulta formal a la CNV.

### B. Manfredi como Agente Productor persona jurídica
- Se inscribe una sociedad como AP con convenio con uno o más ALyC, AN o AAGI. El capítulo no fija patrimonio mínimo ni objeto exclusivo. Pide estatuto, accionistas, administradores, idoneidad, antecedentes penales y declaraciones juradas de lavado. El trámite oficial figura en 20 días desde la documentación completa.
- Permite captar clientes y cobrar comisión de forma legal.
- Límite: el AP capta para **los agentes con los que tiene convenio**, no para cualquier asesor independiente. Sirve si los asesores de la red operan bajo esos mismos ALyC o AAGI.

### C. Manfredi crea un AAGI y los asesores son sus Agentes Productores
- AAGI (Título VII, Cap. IV): solo **SA o SAS**, con **objeto social exclusivo**, **patrimonio neto mínimo de 65.350 UVA** (actualizable por CER), Responsable de Cumplimiento Regulatorio y Control Interno, idoneidad y declaraciones juradas.
- Puede cobrar honorarios a los clientes (art. 15) y vincular a los asesores como AP (Cap. V, art. 2). Así el reparto de la mensualidad pasa a ser legal y declarado.
- El objeto exclusivo obliga a usar una **sociedad separada** del medio y del sitio web.
- Es el camino que más se parece al modelo planteado, y también el más caro: capital, cumplimiento, sujeto obligado ante la UIF y controles.

**Recomendación:** lanzar con A, construir tracción y armar C en paralelo si el negocio lo justifica.

## Obligaciones en cualquier camino
- **Datos personales (Ley 25.326):** consentimiento de cada cliente, política de privacidad, inscripción de la base ante la AAIP y contrato con cada asesor (Manfredi como encargado del tratamiento).
- **Verificación de registro:** comprobar idoneidad y categoría de cada asesor en el registro de la CNV antes de habilitar la consola, y volver a revisarla periódicamente.
- **Análisis publicados:** las opiniones generales y los reportes, aun con recomendación de compra o venta, no son asesoramiento porque no consideran el perfil del cliente (Título XII, Cap. III, Sec. III, art. 3°).
- **Términos y condiciones:** el asesor es el único responsable de su asesoramiento; Manfredi provee software.
- **Defensa del consumidor (Ley 24.240)** frente a los clientes finales.

## Fuentes
- Agente Productor, texto vigente (Título VII, Cap. V): https://www.argentina.gob.ar/normativa/recurso/219405/texact-TituloVII-CapV/htm
- AAGI, texto vigente (Título VII, Cap. IV): https://www.argentina.gob.ar/normativa/recurso/219405/texact-TituloVII-CapIV/htm
- RG 1048/2025, texto original: https://www.argentina.gob.ar/normativa/nacional/norma-408249/texto
- CNV sobre la RG 1048: https://www.argentina.gob.ar/noticias/resolucion-final-canales-de-publicidad-captacion-de-ordenes-y-referenciamiento-de-clientes
- Inscripción AP persona humana: https://www.argentina.gob.ar/servicio/inscribirse-como-agente-productor-persona-humana
- Inscripción AP persona jurídica: https://www.argentina.gob.ar/servicio/inscribirse-como-agente-productor-persona-juridica-ap-pj
- Inscripción AAGI: https://www.argentina.gob.ar/servicio/inscribirse-como-agente-asesor-global-de-inversion-aagi
- Norma sobre qué no es asesoramiento: https://www.boletinoficial.gob.ar/pdf/aviso/primera/307566/20250808
- Alerta CNV sobre membresías con carteras recomendadas: https://www.cnv.gov.ar/DESCARGAS/alertas/blob/E1DEA762-EE32-449E-8530-69AC2DAD5782
