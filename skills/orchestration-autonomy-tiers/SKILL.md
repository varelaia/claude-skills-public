---
name: orchestration-autonomy-tiers
description: >-
  Marco de decisión para asignar a CUALQUIER tarea su nivel de autonomía
  (T0 manual / T1 semi-auto / T2 auto) según riesgo/impacto, y qué medir en cada
  nivel. La autonomía NO es global: depende de la tarea, y se GANA con datos —
  una tarea sube de manual→semi→auto al acumular corridas E2E limpias y baja ante
  una falla (CPMAI iterativo + ISO 42001 A.6 autonomy boundaries / Cláusula 9).
  Es el "cómo decido + cómo mido" operativo, complemento del "por qué"
  (`cpmai-orchestration-doctrine`). Invocar/consultar cuando: vayas a automatizar
  o semi-automatizar una tarea y haya que decidir su nivel; al evaluar si una
  tarea ya se ganó más autonomía; al diseñar/medir orquestación; cuando el usuario
  pregunte "¿esto puede ir solo o lo confirmo?"; o ante una decisión de
  auto-resolver vs confirmar. Incluye registro de tareas de ejemplo clasificadas
  y el esquema de medición unificado.
---

# Niveles de autonomía por tarea (orchestration autonomy tiers)

La autonomía no es un interruptor global. **Cada tarea tiene su nivel correcto**,
y ese nivel se decide por riesgo/impacto y se **gana con track record medido** —
no se asume. Este es el marco para decidirlo y medirlo. El "por qué" de cada
decisión vive en `cpmai-orchestration-doctrine`; aquí está el "cómo".

## Los 3 niveles

| Nivel | Quién decide / ejecuta | Cuándo aplica |
|---|---|---|
| **T0 — Manual** | El humano decide y ejecuta; el agente solo **propone/asiste** | Irreversible + cara al cliente, o tarea **nueva/no probada** |
| **T1 — Semi-auto** | El agente ejecuta hasta un **gate**; el humano confirma el paso con consecuencia; el agente completa y reporta | Hay un paso consecuente pero el resto es mecánico; o tarea repetible aún **no del todo confiable** |
| **T2 — Auto** | El agente decide y ejecuta **sin confirm**; reporta después | **No-destructivo, reversible, interno, probado** |

## Cómo decidir el nivel (4 preguntas de riesgo)

Hazte estas 4 — cada una ancla a un principio CPMAI/ISO. La **más restrictiva
gana** (si una sola empuja a T0, es T0):

1. **¿Es reversible?** ¿Se puede deshacer sin daño? → *Irreversible empuja a T0.*
   (ISO §6 risk appetite. Ej. emitir CFDI real, mandar WhatsApp, borrar datos.)
2. **¿A quién toca?** ¿Cliente / producción / dato real, o solo infra interna de
   pruebas? → *Cliente/prod empuja a T0–T1.* (ISO **A.5 impact assessment**.)
3. **¿Está probada?** ¿Pasó E2E limpio ≥N veces, o es nueva/cambió? → *Nueva
   empuja a T0.* (CPMAI: pilot antes de confiar; la confianza se gana con datos.)
4. **¿Vale automatizarla?** ¿Frecuencia/volumen recurrente que justifique el
   costo de construir la automatización? → *Baja frecuencia = déjala manual, no
   sobre-ingenierices.* (CPMAI Business Feasibility; gate harness: multi-agente
   ~15× tokens.)

**Reglas duras que cortan por encima del scoring** (siempre, sin importar lo demás):
- Keyword destructivo (`delete/drop/force/wipe/prune/rm`) → **nunca T2** (confirm
  obligatorio). 
- Acción **externa/irreversible** (publicar a cliente/canal, deploy a prod de
  cliente, edición DNS, emisión fiscal) → **nunca T2** (freno duro).
- Si una cifra de agente alimenta la decisión → **re-validar en vivo (§7)** antes
  de cualquier nivel; cifra sin verificar baja la tarea a T0.

## La autonomía se GANA (promoción/democión por datos)

Esto es lo que vuelve el marco vivo, no una tabla estática (CPMAI iterativo +
ISO §9→§10):

- **Promoción T0→T1→T2:** una tarea sube de nivel cuando acumula **≥N corridas
  E2E limpias** consecutivas a su nivel actual (sugerido N=5; ajústalo por riesgo:
  más alto para tareas cara-al-cliente). La confianza es un *output medido*, no
  un supuesto.
- **Democión inmediata:** **una sola** falla con consecuencia (nonconformity)
  baja la tarea un nivel **y** genera entrada en `override_log.md` (ISO §10). Se
  re-gana la autonomía repitiendo el conteo limpio.
- **Techo por riesgo:** las tareas irreversibles/cara-al-cliente tienen **techo
  T1** — jamás llegan a T2 por más track record (el riesgo no se amortiza con
  costumbre).

## Qué se mide en cada nivel (spec del registro)

Toda tarea orquestada —manual, semi o auto— escribe **una línea** al registro
unificado (esquema en `references/measurement-schema.md`). Mínimo:

```
task_type · tier (T0/T1/T2) · outcome (success|rework|fail) · e2e_passed (bool)
· confirmed_by (humano, si T1) · tokens · duration_s · ts · session
```

**KPIs de orquestación (ISO Cláusula 9 — lo que hoy NO se mide):**
- **Success-first-time por tier** — ¿salió bien a la primera? (rework = señal de
  tarea mal-asignada de nivel o de agente equivocado).
- **Wrong-tier events** — una T2 que causó problema = debió ser T1 →
  nonconformity → democión + override_log.
- **Right-agent-first-time** — ¿se delegó al agente correcto? (re-delegación =
  mal match patrón↔agente).
- **Promociones/demociones** — la flota debería *ganar* autonomía neta con el
  tiempo si la calidad sube; demociones en aumento = problema.
- **Costo:** tokens/tarea por tier (T2 debería ser el más barato; si no, algo
  está mal).

## Registro de tareas de ejemplo (starter — ver reference para la tabla completa)

| Tarea | Reversible | Toca | Probada | Nivel hoy | Por qué |
|---|---|---|---|---|---|
| Restart container (data persistente) | sí | infra interna | sí | **T2** | reversible, no-destructivo; data persistente sobrevive |
| Research / OSINT de leads (read-only) | sí | nada externo | sí | **T2** | solo lectura, sin side-effects |
| Deploy de servicio a prod (cliente) | sí (rollback) | cliente | sí | **T1** | producto de cliente; confirm el deploy, resto mecánico |
| Edición de zona DNS | no (puede wipear) | producción | — | **T0** | backup obligatorio + verificación manual |
| Campaña WhatsApp a cliente (envío) | no (enviado=enviado) | cliente + Meta rules | — | **T0** | irreversible + cara al cliente; techo T1 máximo |
| Emitir factura fiscal (CFDI) | no (SAT real) | fiscal cliente | — | **T0** | irreversible fiscal; jamás T2 |
| Publicar blog + redes sociales | no (externo) | externo/marca | sí | **T1** | freno duro de publicación externa; confirm antes |

Las **tareas más frecuentes** + candidatas y la lógica de promoción:
`references/task-registry.md`.

## Cuándo NO aplicar este marco

Para una pregunta trivial o una respuesta conversacional, no clasifiques nada —
responde directo. El marco es para **tareas con side-effects** (algo cambia en
infra, datos, cliente o canal externo). Clasificar una charla es ruido, y el
ruido viola el propio principio de iteración limpia.

## Relacionado

- `cpmai-orchestration-doctrine` — el "por qué" de cada decisión (frases CPMAI/
  ISO quotable). Este marco es su brazo operativo.
- `references/measurement-schema.md` — esquema exacto del registro unificado
  (blanco para reparar/unificar la plomería de medición, hoy rota: el
  `orchestrator_usage.jsonl` mide solo la capa autónoma y su stats crashea por
  schema drift).
- `references/task-registry.md` — clasificación viva de las tareas.
