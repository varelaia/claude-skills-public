---
name: planteamiento
description: >-
  Use BEFORE writing a spec, building, deciding, or starting a fix on any NON-TRIVIAL
  work — to define the problem and its ROOT CAUSE before solving. Triggers on intent to
  fix/build/decide on a non-trivial task ("voy a arreglar/construir", "el problema es",
  "algo no funciona", "hay que resolver", "necesito que X"), on bugs/incidents, and on
  client problems or decisions with a disyuntiva. The trap it catches: jumping from a
  SYMPTOM straight to a spec or a solution without verifying it is the RIGHT problem and
  what its root cause is (the GPS-fleet trap — a 5-phase plan built on an N=1 outlier).
  NOT for trivial mechanical work (typo/rename/dep-bump/format), pure informational
  questions, or when the user said "solo hazlo / sin más vueltas". DISTINCT from /refutar
  (kills a claim/figure), /premortem (future failure of a SOLUTION), and
  clarifica-una-a-una (requirements of the DELIVERABLE) — planteamiento defines the
  PROBLEM itself. Operacionaliza CPMAI Fase I (Business Understanding).
---

# Planteamiento del Problema — gate de entrada

Define el problema y su raíz ANTES de escribir la especificación o de construir.
Complemento de la verificación end-to-end, pero al frente del embudo: la verificación
E2E confirma que la solución funciona; esto verifica que el problema esté bien definido.
Produce un **artefacto visible** que el usuario aprueba antes de avanzar.

## Cuándo aplica
OBLIGATORIO en trabajo no trivial: feature/proyecto nuevo · fix no trivial / incidente ·
problema o decisión de cliente · "algo no funciona".

**Skip-list (EXENTO):** edición mecánica / typo / rename / dep-bump / formato · pregunta
puramente informativa · el usuario dijo "solo hazlo / sin más vueltas". Si aplica skip,
dilo en una línea y procede.

## Los 7 campos (llénalos en orden, a la vista)
1. **Síntoma observado** — el hecho, con EVIDENCIA verificada en vivo (comando/dato), NO de memoria.
2. **Estado actual vs estado deseado** — la brecha concreta.
3. **Causa raíz (5-Whys)** — encadena: síntoma → ¿por qué? → … → raíz. Para cuando el "por qué"
   ya no tiene respuesta verificable.
4. **Enunciado formal** — *"El estado es X porque Y; evidencia Z; la raíz es W."*
5. **Hipótesis falsable + métrica** — qué predices y cómo se mediría que es falsa.
6. **Denominador absoluto + baseline del KPI** — toda cifra agregada exige su denominador
   (un share/% sobre universo chico = nada). Nombra el número base actual de la métrica que
   moverías.
7. **Delimitación** — qué NO es el problema (guard anti-XY: ¿el usuario pide Y porque cree que
   resuelve X? ¿es X el problema real?).

## Después de los 7 campos: refutar el ENUNCIADO
Corre `/refutar` sobre el **enunciado del problema** (campo 4), NO sobre cifras sueltas.
¿Sobrevive? ¿O el enunciado sigue siendo un síntoma disfrazado de raíz?

## Criterio Go / No-Go
- **GO** si: el planteamiento nombra **palanca movible + denominador absoluto + baseline de KPI**
  Y el enunciado sobrevive `/refutar`.
- **No-Go** si falta cualquiera → reformular antes de especificar. NO se construye sobre un
  problema mal definido.
- Si **N=1** → reformular como **caso aislado**, NUNCA extrapolar a "el sistema" sin baseline
  del resto (toda cifra citada de memoria o de un incidente previo se re-valida en vivo antes
  de extrapolar).

## Ejemplo ILUSTRATIVO (caso compuesto de flota — debe dar No-Go)
> ⚠ Caso compuesto para ilustrar la mecánica del gate, NO cifras verificadas. Al usar el
> gate de verdad, re-corre tú las cifras en vivo.
- Síntoma: "el agente reporta 2,100 registros sin GPS en el último mes".
- Campo 6 (denominador): ¿2,100 sobre cuántos registros totales? **No verificado.**
- `/refutar` del enunciado "la flota tiene un problema sistémico de GPS": query directa →
  99% GPS OK; **un solo vehículo = único outlier (N=1)**.
- **Veredicto: No-Go.** El "problema sistémico" era un síntoma de un outlier individual. El
  plan de 5 fases / 12-14h se habría evitado. Reformular: "ese vehículo reporta 100% GPS
  NULL — ¿por qué SOLO ese?" (caso aislado).
