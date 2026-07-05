---
name: premortem
description: Use BEFORE building, shipping, deploying, or letting an agent run autonomously — when you're about to commit to a plan and want to surface how it fails BEFORE it fails. Triggers on "premortem", "qué puede salir mal", "análisis de riesgo antes de", "antes de lanzar/desplegar esto", "si esto fracasa por qué sería", or any moment you're about to vibecode/automate something whose failure would be silent, costly, or hard to undo (deploy a prod, dar autonomía a un agente, correr algo destructivo, soltar un build de IA). The trap it catches: jumping from plan to execution without imagining the failure first — and, specifically for vibecoding, leaving a deterministic failure (dep alucinada, secreto, 4xx silencioso) to "model discipline" instead of a hard gate. NOT for killing a present claim (that's /refutar) nor verifying current technical assumptions (that's /pre-flight) — premortem is about FUTURE failure of something you haven't shipped yet.
---

# Premortem — fracaso prospectivo para vibecoding

## Principio
Un premortem no pregunta "¿qué podría salir mal?" — pregunta **"ya fracasó: ¿qué pasó?"**.
La diferencia no es cosmética. Imaginar un evento como **ya ocurrido** (hindsight prospectivo,
Mitchell, Russo & Pennington 1989) sube ~**30%** la capacidad de nombrar las causas reales de un
desenlace (Gary Klein, *Performing a Project Premortem*, HBR 2007). El cerebro busca explicaciones
de un hecho consumado mejor que riesgos de un hecho hipotético. Por eso el premortem se corre
**en tiempo pasado**, antes de construir.

En **vibecoding** —tú (o un agente) dejando que el LLM conduzca el código— esto importa el doble,
porque las fallas de IA son **silenciosas y reproducibles**, no ruidosas y aleatorias:
- 62% de las apps construidas con IA embarcan vulnerabilidades críticas (OX Security 2025); 86% del
  código IA falló defensas XSS (Georgetown CSET).
- Los LLM **alucinan dependencias** (paquetes que no existen / deprecados / con CVE) y repiten el
  mismo nombre falso entre modelos → blanco de *slopsquatting*.
- La deuda de seguridad se acumula ~10× más rápido que la remediación; el refactor cayó de 25% a
  <10% de los cambios al subir la adopción de IA.
- El *knowledge cutoff* hace que el modelo sugiera versiones con CVEs posteriores a su entrenamiento.

Traducción: un build de vibecoding puede **declararse "listo", pasar a la vista, y estar roto o
inseguro sin un solo error en pantalla**. El premortem es donde lo cazas antes.

## La regla de hierro
**El premortem es un GATE de arranque, no un adorno.** Si vas a construir/desplegar/automatizar y la
falla sería silenciosa, cara o difícil de deshacer, el premortem va **ANTES** y produce un veredicto
**Go / No-Go**. Está prohibido:
- Correr el premortem *después* de desplegar ("ya quedó, ahora sí pienso qué pudo fallar").
- Listar riesgos bonitos y **no asignar a cada uno un control concreto** (un riesgo sin mitigación
  con dueño y altura es teatro).
- Mecanizar como hook un riesgo que vive en el juicio, o dejar a "disciplina del modelo" un riesgo
  que tiene señal determinista limpia (ver §Altura del control — esto es el corazón del skill).

## Cuándo SÍ correrlo (y cuándo es otro skill)
| Situación | Skill |
|---|---|
| Vas a **construir/desplegar/automatizar** algo y quieres ver el fracaso futuro | **premortem** (este) |
| Vas a darle **autonomía a un agente** / soltar un build de IA / tocar prod de cliente | **premortem** |
| Tienes un **claim/cifra presente** ("ya funciona", "73%") y vas a construir encima | `/refutar` |
| Quieres validar **supuestos técnicos actuales** antes de tocar (mounts, env, rutas) | `/pre-flight` |
| Vas a **elegir entre opciones** ponderadas | `decision-matrix` |

Premortem mira al **futuro** (¿cómo fracasa esto que aún no existe?); refutar mira al **presente**
(¿este claim es falso ahora?); pre-flight mira el **estado actual** (¿mis supuestos se sostienen?).

## El protocolo (adaptado a solo + agente, no a una sala de juntas)
Klein lo corre con un equipo en 20-30 min. En vibecoding casi siempre estás solo con el modelo, así
que el "equipo diverso" lo simulas con el **catálogo sembrado** (abajo) y, para algo grande, con
**sub-agentes adversarios** (uno por lente). Pasos:

1. **Enuncia la operación y el plan en una línea.** Qué se va a construir/desplegar y dónde.
2. **Fija el horizonte y declara la muerte.** "Son las/el [fecha + N días/semanas]. Esto **explotó
   en producción**. No es hipótesis: ya pasó." Escríbelo en pasado.
3. **Genera causas — sembradas, no en blanco.** Recorre el **catálogo de fallas de vibecoding**
   (§siguiente) y, para cada una, pregunta "¿esta es la que nos mató?". Para operaciones grandes,
   lanza sub-agentes en paralelo, cada uno con una lente (seguridad / falla-silenciosa /
   blast-radius / deps / reversibilidad) — la diversidad caza lo que una sola mirada no ve.
4. **Puntúa** cada modo de falla en la matriz (§matriz).
5. **Asigna la ALTURA del control** a cada mitigación (§altura) — el paso que distingue este skill.
6. **Veredicto Go / No-Go + plan de rollback.**

## Catálogo de fallas de vibecoding (siembra — no arranques en blanco)
No preguntes "¿qué puede salir mal?" a pelo; el valor está en recorrer los patrones REALES. Para cada
uno: ¿aplica aquí? ¿cómo nos enteraríamos? (la detección es lo crítico — estas fallas son mudas).

| # | Modo de falla | Señal de que pasó (¿cómo lo notamos?) |
|---|---|---|
| 1 | **Dependencia alucinada / slopsquat** (pkg inexistente, deprecado, con CVE) | `pip/npm install` de algo fuera del allowlist; import que no resuelve |
| 2 | **"Listo" fabricado** (declaró done sin E2E real) | ¿corrió el curl 2xx / booking real / mensaje real por el canal? si no → no está listo |
| 3 | **Cifra inventada / no re-verificada (§7)** | se construyó plan/meta encima de un N% que nadie re-corrió |
| 4 | **Fallo HTTP silencioso** (4xx/5xx que no lanza excepción) | `resp.status_code` sin checar tras cada post(); 200 asumido |
| 5 | **Secreto hardcodeado / leak** | token literal en código/commit en vez de `os.environ` |
| 6 | **Operación destructiva sin confirm** | `rm`/`prune`/`drop`/`git add -A`/`mass_edit_zone`/deploy prod cliente |
| 7 | **Fix sobre roto / spaghetti** | parche encima sin reproducir el bug ni entender el flujo (debió REVERT primero) |
| 8 | **Scope creep del agente** | tocó archivos/servicios fuera del alcance pedido |
| 9 | **Knowledge cutoff** | usó versión/API vieja, con CVE, o que ya no existe (no verificó docs) |
| 10 | **Deploy que no aplicó** (mount stale, inode, cache) | host muestra lo nuevo, el container/usuario ve lo viejo |
| 11 | **Daño al vecino** (blast radius) | el cambio tumba otro servicio (restart global, OOM a vecinos, puerto) |
| 12 | **Violación de infra/política** | SSH bidireccional (Bastion), servicio interno en VPS de cliente, naming predecible |

Añade los específicos del dominio que estés tocando (este catálogo es piso, no techo).

## Matriz de riesgo (output)
Una fila por modo de falla que SÍ aplica. La columna que más se olvida y más importa en vibecoding es
**Detección**: si no sabes cómo te enterarías, la falla es invisible = trátala como alta prioridad.

```
| # | Modo de falla | Prob. (A/M/B) | Blast radius | ¿Cómo nos enteramos? | Altura del control | Prioridad |
```

## Altura del control — el paso que hace útil al premortem (Regla 6, harness-architect)
Listar riesgos es la parte fácil. El valor está en mandar cada mitigación a **la altura correcta**.
Mecanizar lo que no debe mecanizarse es teatro de confiabilidad; dejar a "disciplina" lo que tiene
señal limpia es una fuga garantizada. Clasifica la **señal** de cada falla:

- **(a) Señal de comando/output limpia** (un `pip install X`, un `git add -A`, un `curl` que dio 5xx,
  un token literal) → **gate de bloqueo duro** (hook PreToolUse exit 2 / PostToolUse). Fiable,
  falsos-positivos casi cero. *Ej.: deps (1), secretos (5), destructivos (6), status HTTP (4).*
- **(b) Señal de lenguaje natural** ("declaró listo", "reportó estado") → **nudge suave 1×/turno**
  (Stop hook guardado por `stop_hook_active`), NUNCA bloqueo duro (fatiga de alerta lo degrada).
  *Ej.: "listo" sin E2E (2).*
- **(c) Juicio que vive en el razonamiento** ("¿esta cifra es load-bearing?", "¿el alcance es
  correcto?", "¿la arquitectura aguanta?") → **NO se hookea.** Queda como disciplina del modelo +
  skill (`/refutar`, este premortem, code review). *Ej.: §7 (3), scope (8), spaghetti (7), infra (12).*

Para cada mitigación, nombra: **qué control, de qué altura, y si ya existe** en el proyecto
(reúsalo: E2E/`verification-checklist`, `dep_gate`, `cmd_guard`, `curl_status_nudge`,
`epistemic_stop_nudge`, `sentinel`, `/refutar`, Agent Delegation Gate) o hay que crearlo.

## Rollback y Go/No-Go (cierre obligatorio)
- **Rollback:** pasos concretos para deshacer + tiempo estimado. Si no puedes enunciar el rollback,
  ese solo hecho es un hallazgo del premortem (la operación es demasiado irreversible para su riesgo).
- **Go / No-Go:** ¿backups verificados? ¿rollback probado/plausible? ¿controles P1 en su altura
  correcta ANTES de proceder? ¿detección en su lugar para las fallas silenciosas? Solo entonces: Go.

## Output — preséntalo SIEMPRE así (escaneable, no un volcado)
El veredicto va primero. Cada modo de falla P1/P2 en su fila. Las mitigaciones con altura y dueño.

```
🪦 PREMORTEM — <operación en una línea>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<badge> VEREDICTO:  GO · GO-CON-CONDICIONES · NO-GO
        Horizonte: "<fecha+N>, esto explotó en producción"

💀 Cómo murió (causas, peor primero)
   | # | Modo de falla | Prob | Blast | ¿Cómo nos enteramos? | Altura control | Prio |
   ... (solo las que aplican; Detección es obligatoria)

🛡️ Mitigaciones P1 (antes de proceder)
   1. <falla> → <control concreto> · altura <a/b/c> · <ya existe: cuál | crear>
   ...

↩️ Rollback
   - Paso 1… / Paso 2… · tiempo estimado: <X min>

✅ Go/No-Go checklist
   - [ ] Controles P1 puestos en su altura correcta
   - [ ] Detección lista para las fallas silenciosas
   - [ ] Rollback enunciado y plausible
   - [ ] Backups / confirm para lo destructivo o externo
```

**Badges:** ✅ GO · ⚠️ GO-CON-CONDICIONES (haz los P1 primero) · ⛔ NO-GO (riesgo > valor o irreversible sin rollback)

**Reglas de presentación:**
- Veredicto y badge **arriba**. Las causas en **pasado** (murió porque…), no en condicional.
- Toda falla P1/P2 trae su **Detección** y su **altura de control** — sin eso es decoración.
- Escala al riesgo: build trivial reversible → premortem de 3 líneas; deploy a prod de cliente o
  autonomía de agente → matriz completa + rollback + (si grande) sub-agentes adversarios.
- Para la versión pesada (operación de infra grande), considera el agente `systems-forensics` en
  **Pre-Mortem Mode** (trae su propia matriz + Go/No-Go).

## Red flags — PARA, estás saltando el premortem
- "Lo despliego y si algo truena lo arreglo" (sobre algo con falla silenciosa o irreversible).
- Listaste riesgos pero **ninguno tiene control con altura y dueño**.
- Pusiste un hook para vigilar un juicio (c), o dejaste a disciplina una señal limpia (a).
- No puedes enunciar el rollback → procediste igual.
- La "detección" de una falla silenciosa quedó en blanco → la diste por improbable sin base.

## Rationalizaciones (de baselines reales)
| Excusa | Realidad |
|---|---|
| "El agente probó el código, está bien" | ¿Corrió el E2E real (curl 2xx / flujo real) o se auto-declaró listo? Falla #2. |
| "Es código nuestro / interno, no hay riesgo de seguridad" | 62% del código IA embarca vulns; el origen no lo exime. Corre #1, #4, #5. |
| "Solo agregué una librería" | ¿Existe? ¿allowlist? ¿CVE? El slopsquat vive justo en ese "solo". Falla #1. |
| "Pongo un hook para que el modelo siempre verifique la cifra" | Eso es juicio (c) — no se hookea, es teatro. Va a `/refutar` + disciplina. |
| "Es reversible, no necesito rollback" | Enúncialo igual en una línea. Si no puedes, NO era tan reversible. |
| "Ya pensé los riesgos en mi cabeza" | El hindsight prospectivo (muerte declarada, en pasado) saca un 30% más. Escríbelo. |
