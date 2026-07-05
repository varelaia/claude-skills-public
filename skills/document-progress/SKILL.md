---
name: document-progress
description: >-
  Cierra y documenta una sesión de trabajo sustancial en una sola pasada:
  bitácora (MEMORY.md + topic file), Trinity de manuales (TÉCNICO + OPERATIVO +
  USUARIO en tu directorio de docs), actualización condicional de agente/skill,
  y commit. Dispara SOLO por petición manual explícita del usuario — frases como
  "documenta avances", "documenta esto", "cierra documentación", "genera los
  manuales", "deja la bitácora y los 3 manuales", "trinity de esta sesión".
  Úsalo cuando hubo un avance real (deploy, fix verificado, incidente resuelto,
  feature, hallazgo de auditoría) que merece quedar registrado para sesiones
  futuras. NO lo uses para checkpoints rápidos entre tareas (usa comandos más
  ligeros de changelog) ni para cerrar la sesión entera con backup+CRM (usa un
  comando de cierre de sesión dedicado). Si el usuario solo dice "guarda" o "haz
  commit" sin pedir documentación, tampoco apliques esto.
---

# document-progress

Documenta un avance sustancial de forma completa y consistente: **bitácora +
Trinity de manuales + update de agente/skill + commit**, en una sola pasada y
sin que el usuario tenga que recordarte cada pieza.

## Por qué existe

El usuario documenta cada avance importante con un patrón fijo (lo verás
replicado en MEMORY.md como "Trinity manuales"). Hacerlo a mano se olvida pasos:
se queda la bitácora sin el manual de usuario, o el manual sin el puntero en
MEMORY.md, o se documenta en la memoria de sesión algo que **nunca quedó
commiteado en disco** (memoria de sesión ≠ commit en disco). Este skill
fuerza el flujo completo y verifica que quedó en disco antes de declararlo hecho.

## Lo que orquesta vs lo que crea

- **Reusa tu comando de changelog de sesión** como fuente de datos (commits, archivos, decisiones del día).
- **Reusa tu comando de creación de topics de memoria** cuando el avance acumuló >5 hechos sobre un tema sin archivo propio.
- **Crea él mismo el Trinity** (3 manuales nuevos) — los comandos de actualización de manuales solo *anexan* a un manual existente, no crean los 3. Los templates están en `assets/`.

## ⚠ Paso 0.0 — Gate de right-size (NO todo avance = Trinity)

**Antes de generar 3 manuales, refuta la premisa "esto amerita Trinity".** Corre la
evidencia dura (Paso 0.4) PRIMERO y mira **qué cambió en disco**:

- Si el avance es **técnico/operativo con sistema que documentar + cliente** (deploy, fix,
  adapter, infra, entregable de cliente) → **Trinity completo**, sigue normal.
- Si el avance es **de comportamiento / meta / disciplina / una RESTA** (decidir NO construir,
  un compromiso de cómo trabajo, una lección sin sistema ni cliente) → el artefacto correcto es
  una **feedback memory** (Paso 1), **NO un Trinity**. 3 manuales sobre "me comprometí a X" =
  exactamente la *doc-que-nadie-lee*. El "usuario" de un manual USUARIO no puede ser el propio
  modelo. Caso disparador: hilo "arquitectura 4-capas" cuyo producto fue **cero archivos**
  (refutar+premortem mataron todo lo propuesto) — forzar Trinity habría sido la basura que el
  hilo entero combatió. Right-size = memory + puntero + (si reveló gotcha) patch de skill + marker.

Regla: **cero archivos de código/infra cambiados + avance conductual ⇒ NO Trinity.** Declara el
right-size explícito en el cierre y deja el marker con `"manuals":0`.

## Paso 0 — Recolectar inputs (NO inventar)

Antes de escribir nada, reúne y confirma con el usuario lo mínimo:

1. **NOMBRE** del avance en MAYÚSCULAS_SNAKE (ej. `DEPLOY_PIPELINE_FIX`). Si el usuario no lo da, propón uno derivado del trabajo y confírmalo.
2. **Sesión** (identificador que uses, p. ej. `sNNN`) y **fecha local** (hoy). Convierte a la zona horaria del usuario siempre, nunca UTC al usuario.
3. **Cliente / proyecto / VPS / container** afectado.
4. **Evidencia dura** — corre, no asumas:
   ```bash
   # Desde la raíz de tu repositorio principal:
   git log --oneline --since="today 00:00"
   git status --porcelain
   git diff --stat
   ```
   Para el changelog completo del día, invoca tu comando de changelog de sesión y usa su salida.
5. **Resultado E2E verbatim** — el output real del curl/query/docker que prueba
   que el avance funciona. Si no lo tienes, **córrelo ahora** o dilo explícito en
   el manual ("no verificado en vivo, último estado conocido <fecha>"). Nunca
   escribas "funcionó" sin evidencia.

> Si una cifra viene de otro agente, re-valídala en vivo antes de escribirla
> (no confíes en cifras heredadas sin re-verificación).

## Paso 1 — Bitácora

1. **Puntero en MEMORY.md** — una línea, <200 chars, formato de los existentes:
   ```
   - [Título](archivo.md) — gancho de una frase
   ```
   Va en `~/.claude/projects/<tu-proyecto>/memory/MEMORY.md`
   (índice de auto-memoria) y/o `<repo>/memory/MEMORY.md` según dónde viva el detalle.
   El detalle largo NUNCA va en MEMORY.md — solo el puntero.

2. **Topic file (condicional)** — si el avance acumuló **>5 hechos** sobre un
   tema que aún no tiene archivo de memoria, invoca tu comando de creación de
   topics de memoria. Si el tema ya tiene archivo, **actualiza ese**, no dupliques.

## Paso 2 — Trinity de manuales (SOLO si el Gate 0.0 dijo Trinity)

⚠ Aplica **solo si el Paso 0.0 clasificó el avance como técnico/operativo**. Si fue
**conductual / meta / una resta** → ya quedó en la memory (Paso 1); **NO generes manuales**
(forzarlos = la muda #1, doc-que-nadie-lee). Para avances técnicos, usa Trinity
completo (no escalado por tamaño *dentro de lo técnico*). Genera los tres
en tu directorio de manuales (p. ej. `docs/manuales-tecnicos/`):

```
<NOMBRE>_<fecha>_MANUAL_TECNICO.md
<NOMBRE>_<fecha>_MANUAL_OPERATIVO.md
<NOMBRE>_<fecha>_MANUAL_USUARIO.md
```

Usa los templates de `assets/` (`TEMPLATE_TECNICO.md`, `TEMPLATE_OPERATIVO.md`,
`TEMPLATE_USUARIO.md`) como esqueleto, pero adáptalos al contenido real — no son
formularios rígidos. Las proporciones canónicas: TÉCNICO ~150-200 líneas (con
sección de **verificación verbatim** y **deuda técnica**), OPERATIVO ~80-100
líneas (runbook con ramas de decisión + "errores a NO cometer"), USUARIO ~40-50
líneas (lenguaje llano, sin jerga, 20s de lectura).

El de USUARIO es el que más se olvida y el que más sirve para hablar con el
cliente final: que de verdad no tenga paths ni comandos.

## Paso 3 — Actualizar agente / skill (regla dura, no "si aplica")

No es un juicio vago. Aplica este criterio:

- **Actualiza un agente** SOLO si el avance produjo una **regla generalizable**
  reutilizable en sesiones futuras (el patrón "Regla NNN" que ya usan tus agentes
  existentes). Edita el `.md` del agente en `~/.claude/agents/` y añade la regla.
- **Actualiza un skill** SOLO si la ejecución reveló que un skill existente tiene
  un paso faltante, incorrecto o un gotcha nuevo. Parchea ese skill.
- **Crea un skill nuevo** solo si el usuario lo pide explícitamente — no por iniciativa.
- **Si nada de lo anterior aplica**, decláralo explícito en tu reporte final:
  *"Sin cambios a agente/skill: <por qué>"*. El silencio se lee como olvido.

Si tocas un skill, recuerda la regla de salud de skills: un skill activo debe
estar referenciado por ≥1 agente (mantén tu propio `SKILLS_POLICY.md` o
equivalente si lo tienes).

## Paso 4 — Commit

Mensaje en el estilo que ya usa el repo, p. ej.:
```
<tipo> <fecha>: <NOMBRE> — bitácora + trinity manuales + <agente/skill si aplica>
```
NUNCA `git add -A` / `git add .` (puede arrastrar secrets). Añade explícitamente
los archivos que generaste/tocaste.

## Verificación antes de declarar "documentado" (gate obligatorio)

No declares hecho hasta confirmar **en disco**, no en tu memoria de sesión:

```bash
N="<NOMBRE>"; F="<fecha>"
REPO="<path-a-tu-repo>"                    # raíz del repositorio principal
MANUALES="<tu-directorio-de-manuales>"     # p. ej. docs/manuales-tecnicos
MEMORY="<ruta-a-tu/MEMORY.md>"             # p. ej. ~/.claude/projects/<proyecto>/memory/MEMORY.md
ls -la "$REPO/$MANUALES/${N}_${F}_MANUAL_{TECNICO,OPERATIVO,USUARIO}.md"
grep -l "$N" "$MEMORY"
git -C "$REPO" log --oneline -1
```

Deben existir los 3 manuales, aparecer el puntero en MEMORY.md, y verse el commit.
Si falta cualquiera → vuelve al paso correspondiente.

## Paso 5 — Marcar la ejecución (para no duplicar al cerrar la sesión)

El comando de cierre de sesión suele rehacer trinity + reflexión + commit.
Para que NO los duplique cuando este skill ya corrió hoy, deja un marcador
determinístico al terminar (una línea JSON por avance documentado):

```bash
mkdir -p "$HOME/.claude/logs"
printf '{"date":"%s","nombre":"%s","manuals":3,"commit":"%s","agent_skill":"%s"}\n' \
  "$(date +%F)" "<NOMBRE>" \
  "$(git -C <path-a-tu-repo> rev-parse --short HEAD)" \
  "<agente/skill tocado o 'ninguno'>" \
  >> "$HOME/.claude/logs/document_progress_runs.jsonl"
```

Tu comando de cierre de sesión puede leer este log para hoy y saltar la
re-documentación de los avances aquí listados (solo referenciarlos). Si lo
implementas con un marker type, te bastará un log compartido como este.

## Cierre

Resumen de 4 líneas: qué quedó documentado, dónde, estado de agente/skill
(cambio o "sin cambios + por qué"), y confirmación de que el marcador quedó escrito.
