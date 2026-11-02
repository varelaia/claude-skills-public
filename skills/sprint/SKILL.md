---
name: sprint
description: >-
  Orquesta UNA tarea de principio a fin con un embudo canónico phase-gated (estilo
  CPMAI + una capa operativa), encadenando tus gates existentes en un orden fijo:
  planteamiento (gate de entrada) → clarifica-una-a-una (si el entregable es ambiguo)
  → spec → pre-flight (verificar supuestos técnicos) → premortem (si es irreversible/
  prod) → BUILD single-agent (TDD/loop + hooks) → e2e (gate de salida, Definition of
  Done) → refutar (refutar el "ya quedó" antes de reportar) → retro (captura el
  aprendizaje). Es un CONDUCTOR delgado: no reimplementa los gates, los invoca
  (cablear, no encarnar), así que hereda cualquier mejora que les hagas. Dispara
  cuando el usuario pida "corre/arranca un sprint", "haz un sprint de X", "llévalo de
  principio a fin", "ciclo completo con gates", "del problema al done", o cuando una
  tarea NO trivial merezca pasar por todo el embudo y no solo por un gate suelto. NO
  lo uses para trabajo mecánico trivial (typo/rename/dep-bump/formato), preguntas
  puramente informativas, ni cuando el usuario solo quiera UN gate aislado (ahí invoca
  ese gate directo). DISTINTO de planteamiento (solo define el PROBLEMA), e2e (solo
  verifica el DONE) y document-progress (solo documenta al final) — sprint los ENCADENA
  para una tarea completa.
---

# /sprint — conductor del embudo canónico de la metodología

Lleva **una tarea** del problema al done verificado en una pasada, recorriendo un
**embudo canónico** phase-gated — los mismos gates, en el mismo orden, cada vez. No es
Scrum-de-ceremonia ni un "equipo Scrum" multi-agente: es la adaptación ágil correcta
para IA (CPMAI = iterativo **pero phase-gated y data-centric**). La velocidad sin gates
produce el modo de falla más caro de la IA — la *zombie sana*: se ve lista, está rota
en silencio.

> **Fuente de verdad del orden:** si mantienes un índice de metodología propio, ese
> documento manda sobre el orden y los gates. Si ese índice cambia, este skill se
> realinea a él — el índice manda, no este archivo.

**Por qué conductor delgado:** cada fase invoca un skill/agente que ya existe (reusar
antes que crear). Si mañana mejoras `e2e` o `planteamiento`, `sprint` hereda el cambio
sin tocarse. Nunca dupliques aquí la lógica de un gate.

## Cuándo aplica / cuándo NO

| Aplica | NO aplica |
|---|---|
| Feature/fix NO trivial que vale el embudo completo | Edición mecánica (typo/rename/dep-bump/formato) → hazla y ya |
| Incidente con causa raíz por investigar | Pregunta puramente informativa |
| Tarea con una disyuntiva real | El usuario quiere UN gate suelto → invoca ese gate directo |
| El usuario pide "ciclo completo / de principio a fin" | El usuario dijo "solo hazlo / sin más vueltas" → ejecuta sin cadencia |

## El artefacto: tablero del sprint (visible)

Al arrancar, crea un **todo por fase** (TaskCreate/TodoWrite) para que la cadencia sea
visible y el usuario vea el progreso. Marca `in_progress`/`completed` al cruzar cada
fase. El tablero ES el "sprint board" — una columna por fase, en el orden del embudo:

```
[ ] 1. PLAN        — planteamiento (Go/No-Go) + refutar del enunciado
[ ] 2. SPEC        — clarifica si ambiguo → spec
[ ] 3. PRE-FLIGHT  — pre-flight (verificar supuestos técnicos antes de tocar)
[ ] 4. RIESGO      — premortem (solo si irreversible/prod)
[ ] 5. BUILD       — single-agent (+worktree opcional), TDD/loop, hooks
[ ] 6. DONE        — e2e por tipo de tarea (gate duro)
[ ] 7. CIERRE      — refutar el "ya quedó / funciona" antes de reportar
[ ] 8. RETRO       — captura el aprendizaje (capa de doc, post-embudo)
```

> Fases 1–7 son el **embudo canónico** (gates de la metodología). La 8 (RETRO) es la
> **capa de documentación** que cuelga del cierre — no es un gate de problema-solución,
> pero es donde el sprint se vuelve mejora compuesta.

## Las 8 fases

### 1. PLAN — gate de ENTRADA (puede dar No-Go y parar el sprint)
Invoca **`planteamiento`**. Llena sus campos con evidencia **en vivo** (no de memoria)
y corre `refutar` sobre el enunciado.
- **No-Go** (falta palanca movible, denominador o baseline; o el enunciado es un
  síntoma disfrazado de raíz; o N=1 extrapolado a "el sistema") → **el sprint para
  aquí**. Reformula el problema o repórtalo. No se construye sobre un problema mal
  definido — ése es el punto del gate.
- **Go** → sigue. Esto cumple el gate de definición-de-problema de tus reglas base.

> Skip-list de `planteamiento`: si la tarea cae en mecánico-trivial, probablemente
> `sprint` ni debió dispararse. Si dudas, dilo en una línea y baja a BUILD.

### 2. SPEC — definir el entregable
- Si el ENTREGABLE tiene ambigüedad que cambiaría lo que entregas (alcance, formato,
  destino, stack, defaults riesgosos) → corre **`clarifica-una-a-una`** primero.
  (`planteamiento` define el PROBLEMA; clarifica define el ENTREGABLE — son distintos.)
- Luego **`spec`**: qué/por qué/dónde/cómo/edge-cases/verificación/rollback. Sin spec
  no se escribe código (regla dura).
- **Nivel del spec (trigger híbrido SDD):** por **default, `spec`-lite** (un markdown,
  una vez, no se versiona como artefacto vivo). **Sube a SDD-pleno** (spec versionado =
  fuente de verdad que el código debe cumplir, estilo Spec Kit) SOLO si se cumple ≥1:
  (a) build **recurrente/multi-sesión** que vivirá y mutará; (b) **prod con requisito
  de auditoría** (ISO-42001 / entregable gobernado); (c) **≥2 personas** tocarán el
  código. Si ninguno aplica → lite. El SDD-pleno *para todo* es ceremonia que grava
  velocidad; el valor del spec-vivo solo paga donde el stakes lo justifica.

### 3. PRE-FLIGHT — verificar los supuestos técnicos
Invoca **`pre-flight`** ANTES de tocar nada. Verifica EN VIVO los supuestos sobre el
sistema real, no de memoria: ¿el archivo está bind-mounteado o baked en la imagen?
¿la env var existe en el contenedor? ¿el endpoint responde? ¿el mount resuelve al inodo
correcto? ¿la columna/tabla existe? Es el paso que separa "creí que" de "verifiqué que".
Sin esto, el premortem y el build razonan sobre un sistema imaginario. (Distinto de
`premortem`: pre-flight verifica el ESTADO ACTUAL; premortem imagina la falla FUTURA.)

### 4. RIESGO — premortem (condicional)
Corre **`premortem`** SOLO si la tarea es irreversible o toca producción: deploy a
prod, migración de DB, merge+deploy de PR, reescritura de zona DNS/infra, dar autonomía
de escritura a un agente, o cualquier cosa destructiva. Para una tarea reversible de
bajo impacto, sáltalo (decláralo en una línea). El objetivo es cazar la falla
determinista ANTES (dep alucinada, secreto, 4xx silencioso), no dejarla a "disciplina
del modelo".

### 5. BUILD — construir (single-agent + micro-loop)
El embudo gobierna el *macro* (problema→done); aquí adentro gobierna el **micro-loop**
(estilo Software 3.0). El híbrido —gates + micro-loop— vence tanto al embudo solo como
al loop solo: los gates atrapan la falla silenciosa que el loop ignora, y el loop da la
velocidad que la ceremonia quita. Doctrina del loop:
- **Maximiza el loop Generación–Verificación.** El cuello de botella ya no es escribir
  código, es verificarlo. Optimiza por *qué tan rápido puedes verificar y corregir*, no
  por cuánto genera el modelo de una vez.
- **Tight leash / incrementos pequeños.** Diffs chicos, scope estrecho, un cambio
  verificable a la vez. **Nunca aceptes un diff que no puedas verificar** — 1000 líneas
  a ciegas es deuda silenciosa, justo el modo de falla que el gate DONE existe para cazar.
- **Autonomy slider.** Sube la autonomía SOLO cuando el verify es barato (test que
  corre, curl, query). Donde verificar es caro o el error es irreversible → leash corto,
  paso a paso. "Iron Man suit, no robot": aumenta tu juicio, no lo reemplaza.
- **Single-agent.** Multi-agente cae en eficacia en tareas chicas; el default es un
  agente hasta que haya workstreams genuinamente independientes. No spawnees un "equipo
  Scrum".
- **Worktree git opcional** SOLO si la tarea muta archivos en paralelo y chocaría con
  otro trabajo. Cuesta setup + disco; no lo uses por reflejo.
- **TDD donde haya tests:** escribe el test que falla, hazlo verde, refactoriza. Para
  ciclos largos de "tests verdes hasta pasar" usa un loop automatizado.
- **Deja trabajar a los hooks:** si tienes hooks de calidad (PreToolUse/PostToolUse,
  compilación, conteo de líneas) son tus gates deterministas — no los puentees.
- **Reglas duras de tu propio archivo de reglas que apliquen según el dominio:**
  convenciones de naming, nombres de servicio entre contenedores (no localhost),
  verificar el status de las respuestas HTTP, timezone del usuario, respaldos antes de
  editar infra. Carga la regla del dominio si tocas ese dominio.

### 6. DONE — gate de SALIDA (Definition of Done)
Invoca **`e2e`** por tipo de tarea. Esto es gate DURO: **nunca** declares "listo" sin
él (saltarlo ya costó incidentes reales en producción). Verifica el flujo real (curl
2xx, registro real, mensaje real por el canal, query DB antes/después), no el happy-path
teórico. Si rompe algo nuevo → **revierte y arregla limpio**, no parches encima (tu
modelo mental del sistema estaba mal).

### 7. CIERRE — refutar el "ya quedó" antes de reportar
Corre **`refutar`** sobre el claim de éxito ANTES de decirle al usuario que funciona.
`e2e` verifica que el flujo corre; `refutar` ataca la afirmación misma: ¿el "ya quedó"
sobrevive? ¿la cifra que vas a reportar tiene denominador? ¿probaste el camino de FALLO
o solo el happy-path? ¿una métrica derivada/panel se confundió con la fuente? Es el gate
contra la *narrativa de sesión que diverge de la realidad operativa*. Si el claim NO
sobrevive → vuelve a la fase que toque, no reportes. Solo cuando sobrevive, reporta el
done.

### 8. RETRO — capturar el aprendizaje (que no se pierda)
La retrospectiva es lo que convierte un sprint en mejora compuesta. Calibra el peso:
- **Avance sustancial** (deploy, fix verificado, incidente resuelto, feature, hallazgo)
  → ofrece **`document-progress`** (bitácora + manuales + commit). Es petición manual
  del usuario, así que **ofrécelo**, no lo dispares solo.
- **Lección reutilizable** (algo no-obvio que cambiaría cómo trabajas la próxima vez) →
  escribe UNA memoria `feedback-*` (con **Why** + **How to apply**). Tus memorias
  `feedback-*` SON retros codificadas.
- **Checkpoint ligero** entre tareas → un changelog de sesión.
- **Nada que aprender** → dilo en una línea y cierra. No inventes lecciones.

## Reglas del conductor (duras)

1. **No reimplementes un gate aquí.** Si te ves copiando los campos de `planteamiento`
   o el checklist de `e2e` dentro de este flujo, párate e invoca el skill. Cablear, no
   encarnar.
2. **Respeta los gates que paran.** PLAN puede dar No-Go; RIESGO puede pedir confirm del
   usuario antes de algo irreversible. El sprint NO los atropella por "avanzar".
3. **Single-agent hasta probar lo contrario.** Multi-agente solo con workstreams
   independientes reales; justifícalo si lo eliges.
4. **Una tarea por sprint.** Si aparecen 3 tareas, son 3 sprints (o un backlog que
   priorizas y corres en serie) — no las mezcles en un flujo.
5. **Cifras heredadas se re-validan en vivo antes de planear encima.** El sprint no
   hereda un número sin verificarlo.
6. **Gate referenciado pero NO instalado → ejecútalo inline y decláralo.** No todos los
   gates existen como skills en todo entorno. Cuando falte uno: (a) usa el skill
   instalado más cercano si lo hay (p. ej. `verification-before-completion` cubre buena
   parte de `e2e`); (b) si no, ejecuta la fase inline con su checklist mínimo; (c) **dilo
   en el tablero** — un gate ausente no se salta en silencio, porque el tablero es lo que
   le dice al usuario qué se verificó de verdad. No inventes que invocaste un skill que
   no existe.

## Ejemplo (ilustra la mecánica, no es dato verificado)

> "corre un sprint para arreglar que un servicio no envía la notificación de confirmación".
- **PLAN** `planteamiento`: síntoma verificado en vivo (registro creado pero sin
  notificación), raíz por 5-Whys → un segundo camino de creación saltó el chokepoint de
  notificación. Denominador + baseline. `refutar` del enunciado. → **Go**.
- **SPEC** sin ambigüedad de entregable (no corre clarifica). `spec`: enrutar la creación
  por el endpoint canónico; rollback = revertir el route.
- **PRE-FLIGHT** `pre-flight`: en vivo, ¿el archivo es bind-mount o baked en la imagen?
  ¿existe el chokepoint en el route canónico? ¿la env var del servicio está en el
  contenedor? Verificado antes de tocar.
- **RIESGO** toca producción → `premortem`: ¿doble notificación? scope canary = un solo
  destinatario de prueba.
- **BUILD** single-agent, sin worktree (un archivo). Edita el route. Hooks corren.
- **DONE** `e2e` de mensajería: registro de prueba real → llega la notificación por el
  canal real → se limpia la prueba. Verde.
- **CIERRE** `refutar` del "ya quedó": ¿la notificación llegó por el camino real o lo
  asumí? ¿probé el camino de fallo? El claim sobrevive → reporto.
- **RETRO** avance real → ofrece `document-progress`; memoria `feedback-*` con la lección.

## Distinto de
- **`planteamiento`** — solo la fase PLAN (define el problema). `sprint` la usa.
- **`pre-flight`** — solo verifica supuestos técnicos (fase 3). `sprint` la usa.
- **`premortem`** — solo imagina la falla futura (fase 4). `sprint` la usa.
- **`e2e`** — solo la fase DONE (verifica). `sprint` la usa.
- **`refutar`** — solo mata un claim/cifra (fase 7, y transversal). `sprint` la usa.
- **`document-progress`** — solo la fase RETRO al cierre. `sprint` la ofrece.
- **`clarifica-una-a-una`** — solo aclara el entregable dentro de SPEC.
- Un "equipo Scrum multi-agente" — `sprint` es deliberadamente single-agent.
