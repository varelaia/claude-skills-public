---
name: refutar
description: Use when about to accept, build on, plan on top of, or report a claim — especially an empirical assertion ("X% de…", "N casos", "tardó Z días"), a figure from an agent/forensics/report, a "ya funciona / está listo / está live", or when asked "¿es cierto?" / "verifica esto". Triggers when a stated number or "it works" is the PREMISE of the work you're about to do. The trap it catches: inheriting the claim and appending a verification caveat at the end instead of refuting it first.
---

# Refutar — falsación popperiana operacional

## Principio
Una afirmación no se acepta porque puedas confirmarla, sino porque **sobrevivió a un intento serio de refutarla**. Verificar y refutar son asimétricos: mil observaciones a favor no la prueban; **un** contraejemplo la mata. Tu trabajo aquí no es evaluar con neutralidad — es **destruir el claim**. Solo si fallas en refutarlo, sobrevive (provisionalmente).

## La regla de hierro (esto es lo que casi siempre falla)
**La refutación es un GATE, no un caveat.** Si vas a construir/planear/reportar SOBRE un claim, el intento de refutarlo va PRIMERO y BLOQUEA lo demás. Está prohibido:
- "Voy a redactarlo directo" y luego añadir al final "ojo, no verifiqué los números".
- Construir las fases / derivar metas / estimar esfuerzo a partir de la cifra y *después* sugerir validarla.
- Tratar el §7 como nota al pie. Un caveat al final NO cuenta como refutación.

Si no puedes nombrar el experimento que mataría el claim **y ya lo corriste**, el claim no está verificado — está *no-refutado-por-pereza*, y NO se construye encima. (Esto aplica a lo que se construye **irreversiblemente** sobre el claim — ver Paso 0; un borrador reversible que el usuario revisará no se bloquea: se entrega con la cifra marcada.)

## Paso 0 — Tier de riesgo (antes que nada)
La intensidad de la refutación es **proporcional a lo que se construye encima.** ¿La acción downstream es **irreversible/externa** (enviar, desplegar, commitear la cifra, emitir un CFDI, prometer al cliente) o **reversible/interna con el usuario como gate** (un borrador que él revisa, copy ajustable, brainstorm, placeholder)?
- **Reversible + el usuario revisa antes del paso irreversible** → NO corras un experimento crucial como precondición. **Entrega lo que pidió** y marca cada cifra heredada inline como `[a validar antes de enviar/desplegar]`. Exige refutación recién cuando el número vaya a TOCAR algo irreversible.
- **Irreversible / externa / apuestas tu output a la cifra** → gate completo (Paso 1→3).

NUNCA sustituyas el entregable que el usuario pidió por tu propio reframe cuando el único problema son cifras no-validadas que puedes marcar con bandera. Sobre-refutar un borrador reversible quema su tiempo y desobedece la petición.

## Paso 1 — Clasifica el claim (define qué lo mata)
| Tipo de claim | El experimento que lo REFUTARÍA |
|---|---|
| Empírico / cifra ("73% de…", "2,100 casos") | re-correr la query/conteo en vivo; revisar el denominador y si N se concentra en 1-2 casos (→ outlier, no sistémico) |
| De sistema ("funciona / está live / está listo") | el comando E2E que daría no-2xx: booking real→DB, mensaje real por el canal, `curl` de la ruta exacta |
| De agente / reporte (cifra que otro agente afirmó) | pedir la query+output verbatim+timestamp y **re-ejecutarla** (no leer su resumen) — §7 |
| De fuente / dato factual ("el estudio dice…") | ir a la fuente primaria y buscar el dato que la contradice; ¿correlación presentada como causa? |
| Causal ("X mejoró por Y") | buscar el **confound**: ¿qué otra cosa cambió a la vez? comparar a igual carga / día-sobre-día |
| Juicio de valor / diseño / negocio ("outbound > inbound", "se ve mejor") | **NO-FALSABLE** → no es trabajo del refutador. Decláralo y devuelve el claim. No inventes una refutación empírica de algo que no es empírico. |

## Paso 2 — Nombra el experimento crucial y córrelo ANTES de construir
Escribe explícitamente "esto se refutaría si: ___". Córrelo (query / curl / fuente / búsqueda del contraejemplo). Solo con el resultado en mano procede.

## Paso 3 — Sesgo a refutar
Arranca asumiendo **REFUTADO**. El claim debe *ganarse* la supervivencia. Un verificador neutral confirma de más; ese sesgo es justo el valor que aportas. Busca activamente el dato/comando que lo tira, no el que lo apoya.

## Quine-Duhem
Cuando algo falla, una observación refuta un *bloque* de supuestos, no uno solo. Reporta **cuál hipótesis cayó** (¿el código? ¿el mount stale? ¿el DNS? ¿el denominador?), no "es falso" a secas. Si no puedes aislarla, dilo.

## Output — preséntalo SIEMPRE así (humano y escaneable, NO un log de máquina)

Nada de un bloque plano `CAMPO: valor`. El veredicto va PRIMERO (es el bottom line), el claim se cita, y cada parte vive en su propia sección con título y emoji. Plantilla:

```
🔬 REFUTACIÓN — <tema en una línea>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<badge> VEREDICTO:  <REFUTADO | SOBREVIVE (provisional) | NO-FALSABLE | NO-VERIFICABLE AÚN>
        <tipo de claim: empírico · sistema · agente · fuente · causal>

📌 El claim
   "<verbatim, entre comillas>"

🔪 Cómo intenté matarlo
   <el experimento crucial: qué observación/comando/dato lo mataría>
   → ¿Corrido? <sí/no>. <resultado VERBATIM: la cifra, el output, el contraejemplo>

🧩 Qué cayó   (solo si REFUTADO)
   <Quine-Duhem: cuál hipótesis del bloque cayó — no "es falso" a secas>
```

**Badges:** ❌ REFUTADO · ✅ SOBREVIVE (provisional) · ⚖️ NO-FALSABLE · ⏳ NO-VERIFICABLE AÚN

**Reglas de presentación:**
- El **veredicto y su badge van arriba** — no lo entierres bajo la explicación.
- "Cómo intenté matarlo" **obliga** a traer el resultado **verbatim** (la cifra, el output, el contraejemplo), nunca un "ya lo verifiqué" pelón.
- ✅ **SOBREVIVE es siempre provisional**: ganó ESTE round, no es verdad definitiva. Dilo.
- ⚖️ Si **NO-FALSABLE**: omite "Qué cayó" y di en una línea por qué no es empírico (juicio de valor/diseño/negocio) — devuelve el claim, no inventes refutación.
- Cada sección en **pocas líneas**: esto se lee en 20 segundos. Si tienes varios sub-claims, repite el bloque (uno por claim), no los amontones.

## Red flags — PARA, estás heredando el claim
- "Voy a redactarlo/planearlo directo" (sobre una cifra sin verificar)
- Pusiste la verificación como caveat al final en vez de gate al inicio
- Derivaste metas/esfuerzo/fases de un número que no re-corriste
- Citaste la cifra de otro agente sin re-ejecutar su query (cascada §7)
- Tratas de "refutar" un juicio de valor en vez de marcarlo NO-FALSABLE
- Buscaste evidencia que CONFIRMA en vez del comando que REFUTA

## Rationalizaciones (de baselines reales)
| Excusa | Realidad |
|---|---|
| "El claim viene de nuestro propio forensics/analytics" | El origen no lo verifica. Re-corre la query. La cifra propia es la que más ha fallado aquí (§7). |
| "Añadí una nota de que hay que verificar" | Un caveat no es una refutación. El gate va ANTES y bloquea el build. |
| "Es solo un plan/borrador, los números son placeholder" | Depende del Paso 0: si la acción downstream es **irreversible**, el plan ya está moldeado por el número (metas, fases, esfuerzo) → refuta primero. Si es **reversible y el usuario lo revisa**, entrégalo con la cifra marcada `[a validar]` — no lo bloquees. |
| "N=2,100 suena sistémico" | ¿Denominador? ¿Concentrado en 1-2 casos? N grande sin baseline puede ser un outlier. |
| "La latencia bajó tras el deploy, el cache funciona" | Confound. ¿Qué más cambió (tráfico, hora)? Compara a igual carga. |
| "Me pidieron construir, no verificar" | Construir sobre un claim ES aceptarlo. La petición de construir no exime de refutarlo primero. |
| "El regex/grep da 0 ocurrencias del tic, ya quedó arreglado" | Un keyword-check solo ve el patrón de AYER. Si el sistema (un LLM, un generador) puede mutar a un molde nuevo, tu detector quedará ciego a él y dará 0 falso. Caso real (cicleo de cierre en un bot): maté "Quedamos…"→creció "Me quedo con…"→lo maté→creció "abre-con-número 6/6" que el regex no buscaba. Para "¿ya no se cicla / converge?" mide la **convergencia NUEVA** (diversidad estructural, oído humano, juez-LLM de similitud), no la ausencia de la frase vieja. |
| "La métrica subió/bajó N vs ayer (reporte de tendencia)" | **Discontinuidad de medición.** ¿Cambió el CÓDIGO de la métrica entre los dos puntos? Un fix de una métrica inflada produce un delta día-sobre-día FALSO de una sola vez (el "ayer" se midió con método viejo, el "hoy" con método nuevo). Caso real: reporte diario "Citación 9 (-26 vs ayer)" = el 35 de ayer era pre-fix (crudo + bot mal clasificado), el 9 de hoy post-fix (deduplicado) → citación REAL plana en baseline. Antes de reaccionar al delta: `git log` de la métrica + re-contar AMBOS días con el MISMO método (log vivo) + comparar contra baseline. |
