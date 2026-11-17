# Marco de análisis

## Métricas que importan (en orden)

| Métrica | Por qué | Dónde se ve |
|---------|---------|-------------|
| Retención a 3s / "tasa de gancho" | Si el gancho falla, nada más importa | TikTok Studio (curva), IG Insights ("Tiempo de reproducción") |
| % visto completo / tiempo medio | Señal principal del algoritmo | TikTok: "vio el video completo"; IG: duración media vs. duración |
| Compartidos | Alcance fuera de seguidores | IG y TikTok |
| Guardados | Valor percibido (clave en finanzas: se guarda lo educativo) | IG y TikTok |
| Seguidores ganados por pieza | Crecimiento real | IG Insights por reel, TikTok Studio |
| Clics al link / visitas al perfil | Conversión a la membresía | IG "Visitas al perfil", link en bio |
| Vistas | Resultado, no causa. Se usa normalizado | Grilla |
| Likes / comentarios | Lo que menos predice. Comentarios = ideas de próximos videos | — |

Ratios útiles:
- **Guardados / vistas ×1000** y **compartidos / vistas ×1000**, para comparar piezas de distinto alcance.
- **Seguidores / 1000 vistas**, para saber qué convierte y no solo qué entretiene.

## Normalización

Todo se compara contra la **mediana de la propia cuenta** en los últimos 30 posts
(mediana, no promedio: un viral rompe el promedio).

- Índice = vistas de la pieza / mediana.
- ≥ 2,0 → ganadora · 0,5 a 2,0 → normal · ≤ 0,5 → perdedora.
- Las piezas de < 48h no se clasifican todavía.

## Etiquetas por pieza

Cada pieza en `historial.md` y en los snapshots lleva:

- **formato**: cámara-a-cámara · voz en off + pantalla · motion graphics · carrusel · story · mixto
- **tema**: ticker (cuál) · macro AR · macro EE.UU./Fed · finanzas personales · educación bolsa · producto (Portfolio/Warren/informes) · noticia
- **gancho**: tipo según `ganchos-guiones.md` (número, contraste, error, pregunta, promesa, polémica, lista, historia)
- **duración** (s) · **cámara** sí/no · **CTA**: seguir / guardar / comentar / link / ninguno
- **oportunidad**: ¿salió pegado a un evento (balance, dato INDEC, Fed)? sí/no

## Formato del snapshot

`metricas/AAAA-MM-DD-<red>.md`:

```
# <red> — AAAA-MM-DD
Fuente: chrome | capturas del user | csv | web pública
Seguidores: N (Δ vs. snapshot anterior)
Mediana vistas últimos 30: N

| fecha | link | formato | tema | gancho | dur | vistas | idx | guard | comp | seg+ | % completo |
|-------|------|---------|------|--------|-----|--------|-----|-------|------|------|------------|
```

## Diagnóstico (modo Auditoría)

Salida en este orden, corta:

1. **Estado** en 3 líneas: seguidores, tendencia, mediana, mejor pieza del período.
2. **Qué funciona**: etiquetas sobrerrepresentadas en las ganadoras, con evidencia (qué piezas).
3. **Qué no funciona**: igual con las perdedoras.
4. **Brecha con la competencia**: qué hacen ellos que acá no.
5. **3 acciones** concretas para las próximas 2 semanas, cada una con la métrica que la valida.

## Competencia (modo Competencia)

Por cuenta: tamaño, frecuencia, formato dominante, duración típica, uso de
cámara, top 3 y bottom 3 contra su mediana y el gancho textual de cada top.
Cerrá con una tabla **"robar / evitar"**: patrones que aparecen en 2+ cuentas.
Nunca copiar guiones textuales: se toma la estructura, no el contenido.
