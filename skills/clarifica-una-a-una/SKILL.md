---
name: clarifica-una-a-una
description: >-
  Antes de implementar, construir o crear cualquier cosa, clarifica los
  requisitos haciendo preguntas de opción múltiple UNA A LA VEZ (formato
  ADHD-friendly de 20 segundos), usando el widget AskUserQuestion con una sola
  pregunta por llamada. Dispara de DOS formas: (1) MANUAL cuando el usuario lo pide
  explícito — "pregúntame primero", "una pregunta a la vez", "clarifícame antes
  de implementar", "modo entrevista", "no asumas, pregunta", "hazme preguntas de
  opción múltiple"; y (2) AUTO cuando el usuario pide construir/implementar/crear/
  diseñar/armar algo y la petición tiene ambigüedades críticas que cambiarían lo
  que entregas (alcance, formato, destino, stack, defaults riesgosos). NO lo uses
  para tareas triviales de un solo paso sin ambigüedad, ni para preguntas de pura
  información ("qué hora es", "cómo está X"), ni cuando el usuario ya dio specs
  completas o dijo explícitamente "no preguntes, solo hazlo". REGLA DE DISPARO
  REFORZADA (2026-06-09): SIEMPRE que al ir a construir/implementar/crear/diseñar
  quede CUALQUIER pregunta o tema sin clarificar que cambie el entregable, INVOCA
  este skill antes de tocar nada — no improvises supuestos sueltos. Sigue
  preguntando una a una hasta tener claridad; luego muestra un resumen de 20
  segundos e IMPLEMENTA de inmediato sin esperar "ok" (excepto si la primera
  acción es destructiva o externa irreversible → ahí sí confirmas).
---

# clarifica-una-a-una

Clarifica antes de construir. Una pregunta de opción múltiple a la vez. Esperas
la respuesta. Sigues con la siguiente. Hasta tener claridad. Recién entonces
implementas.

## Por qué existe

El usuario procesa mejor en bloques de ~20 segundos. Un muro de 6 preguntas
abiertas lo agota y se pierde detalle; una pregunta de opción múltiple con 3-4
opciones concretas se contesta de un clic y mantiene el hilo. El costo de una
pregunta mal entendida es alto: implementar la cosa equivocada quema tokens,
tiempo y, en producción, afecta usuarios reales (cifras y premisas falsas
invalidan planes completos). Una buena pregunta barata ahora evita un rework caro
después.

Este skill convierte la disciplina de "pre-flight de supuestos" en un ritmo
conversacional que el usuario puede sostener.

## El ritmo (regla central)

```
1. PARA antes de implementar
2. Detecta las ambigüedades que REALMENTE cambian el entregable
3. Pregunta UNA sola → con AskUserQuestion (un solo elemento en el array)
4. Espera la respuesta
5. ¿Queda alguna ambigüedad crítica? → vuelve al paso 3
6. ¿Ya hay claridad? → resumen 20-seg + IMPLEMENTA de inmediato (sin esperar "ok")
7. EXCEPCIÓN freno: si la primera acción es destructiva o externa irreversible
   (mandar algo a un cliente, borrar/sobrescribir, deploy a prod de cliente) →
   ahí SÍ esperas confirmación explícita antes de ejecutar
```

La disciplina que importa: **una pregunta por turno**. No batches. Nunca metas
varias preguntas en el mismo `AskUserQuestion`. El widget permite hasta 4
preguntas a la vez — aquí siempre mandas exactamente una. El "una a la vez" es el
punto entero del skill; perderlo lo rompe.

## Cómo preguntar

Usa el tool **AskUserQuestion** con el array `questions` conteniendo **un solo
objeto**:

- `header`: etiqueta corta (≤12 chars) — ej. "Alcance", "Formato", "Stack".
- `question`: la pregunta, clara y específica, una sola.
- `options`: 2 a 4 opciones **concretas y mutuamente excluyentes**. El widget
  agrega "Other" automáticamente para texto libre (esa es tu quinta opción "e" de
  facto — no necesitas crearla).
- Si tienes una recomendación honesta, ponla **primera** y agrégale
  "(Recomendado)" a la etiqueta. No recomiendes por inercia; solo cuando de
  verdad hay un default sensato.

Mantén etiquetas y descripciones cortas — 20 segundos de lectura total. Cada
opción se entiende sin pensar.

**Traduce a resultados, no a mecanismos.** El usuario es el operador/dueño, no el
ingeniero. Si la decisión es técnica, las opciones NO deben
usar jerga interna (`LIMIT 500`, `pHash`, `moiré`, nombres de funciones) — el
usuario no puede elegir entre cosas que no entiende. Frasea cada opción por el
**resultado que le importa**: "que el número sea correcto", "que deje de marcar
casos falsos", "que cace el fraude que se escapa". Si el usuario responde "no me
quedó claro" / "nada de esto se entiende" → la causa casi siempre es jerga:
reformula en lenguaje llano con ejemplos concretos, y agrega una opción de escape
"explícame primero en simple". El "una a la vez" no sirve si la pregunta no se
entiende.

### Qué SÍ preguntar

Solo lo que cambia el entregable y no puedes inferir con confianza:
- **Alcance** — ¿toda la cosa o solo una parte? ¿incluye X?
- **Formato/salida** — ¿PDF, HTML, script, página? ¿dónde vive?
- **Destino** — ¿qué VPS, qué container, qué dominio?
- **Stack/método** — ¿reusar lo existente o algo nuevo?
- **Defaults riesgosos** — cuando asumir mal es caro o irreversible.
- **Trade-offs reales** — rápido-y-sucio vs robusto, etc.

### Qué NO preguntar

- Cosas que el código, el repo, la memoria o `git` ya responden — léelo tú.
- Convenciones ya establecidas en el proyecto (naming, timezone, puertos,
  forma de leer tokens). Aplícalas, no preguntes.
- Detalles triviales con un default obvio — elígelo y menciónalo de pasada.
- Preguntas de relleno para parecer minucioso. Cada pregunta cuesta atención;
  gástala solo donde mueve la aguja.

Si no queda **ninguna** ambigüedad crítica, no preguntes — salta directo al
resumen o a implementar.

## Trigger automático

**Regla reforzada:** SIEMPRE que vayas a
construir/implementar/crear/diseñar algo y quede **CUALQUIER** pregunta o tema sin
clarificar que cambie el entregable, **invoca este skill ANTES de tocar nada**. No
improvises supuestos sueltos sobre alcance/destino/formato/método cuando podrías
preguntar. Si detectas ≥1 ambigüedad crítica → primera pregunta, una a la vez.

Cuando el usuario pide construir/implementar/crear algo sin specs completas, activa
este ritmo **antes** de escribir código o tocar infra. No anuncies un proceso
largo; simplemente lanza la primera pregunta relevante. Si en realidad no hay
ambigüedad (la petición es clara y de bajo riesgo), no fuerces preguntas — procede
y, si acaso, menciona los defaults que asumiste.

Excepción dura: si el usuario dice "no preguntes, solo hazlo" / "ya sabes" / "tú
decide" → respeta eso, asume defaults razonables, impleméntalos y reporta qué
asumiste. La instrucción explícita del usuario gana sobre este skill.

## Cierre: resumen → implementa directo (sin "ok")

Cuando ya no quedan ambigüedades, **NO esperes confirmación** — el "ok" final
estorba. El resumen es un aviso de arranque, no una puerta. Flujo:

1. Muestra un resumen de 20 segundos de lo decidido. Formato ADHD-friendly:

```
🎯 Voy a construir: <una línea>
   • Alcance: <…>
   • Formato/destino: <…>
   • Método: <…>
   • Asumo por default: <lo no preguntado>

Arranco ahora. (avísame solo si algo de esto no era lo que querías)
```

2. **Implementa de inmediato** siguiendo las reglas del proyecto (E2E antes de
   declarar "listo", verificación en vivo, etc.). No hay paso de espera.

### Freno duro (la ÚNICA excepción que conserva confirmación)

Si la **primera acción** que vas a ejecutar es **destructiva o externa
irreversible**, el resumen SÍ termina pidiendo luz verde y esperas:

- Mandar/publicar algo a un cliente o canal externo (WhatsApp, email, redes).
- Borrar, sobrescribir o `rm`/`prune`/`drop` cualquier dato.
- Deploy a producción de un **cliente** (no a tu propia infra de pruebas).
- Cualquier cosa cubierta por las reglas globales de "confirmar outward-facing".

En ese caso el cierre dice: `⚠️ Esto es <destructivo/externo>. Confirmo y
ejecuto cuando me digas.` — y ahí sí esperas. En TODO lo demás, arrancas solo.

El resumen sigue cerrando el loop (el usuario ve qué entendiste), pero ya no te
detiene salvo en lo que de verdad puede doler.

## Ejemplo de un turno

Usuario: "arma un dashboard para ver los pedidos recientes"

Tú (primera pregunta, una sola):

> AskUserQuestion →
> header: "Alcance"
> question: "¿Qué debe mostrar el dashboard en v1?"
> options:
>   a) Solo pedidos de hoy (tiempo real) — (Recomendado) arranque simple
>   b) Histórico con filtro por fecha y categoría
>   c) Histórico + alertas (pedidos retrasados o anómalos)
> (Other queda disponible para "e" libre)

Esperas la respuesta. Según conteste, la siguiente pregunta podría ser destino
(¿subdominio nuevo o ruta en el dashboard existente?), luego stack, etc. Una a la
vez, hasta que el resumen 20-seg quede obvio.

## Notas

- Este skill es **proceso**, no implementación. Una vez con luz verde, encadena
  con los skills/reglas que correspondan a la tarea real.
- Complementa una verificación técnica de supuestos (pre-flight) pero es más
  conversacional y centrado en decisiones de producto/alcance.
- Si una respuesta abre una ambigüedad nueva, está bien — pregúntala. El loop es
  dinámico, no un cuestionario fijo.
