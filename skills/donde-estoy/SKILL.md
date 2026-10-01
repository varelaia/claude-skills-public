---
name: donde-estoy
description: >-
  Análisis de situación y brechas del arsenal: qué YA tenemos ([MEDIDO] en vivo,
  nunca de memoria), qué DEBE tener, qué PODRÍA tener y qué sería GENIAL tener —
  define el objetivo del usuario y remata con matriz de decisión multicriterio
  (escala 1-10, símbolos ↑/=/↓ vs promedio de columna, total ponderado por
  opción, promedio por criterio, cálculo determinista por script) y apartado
  "🏆 Recomendación" con ganador, justificación y el hueco explícito hacia
  "súper genial". MANDA sobre brainstorming/ideación libre cuando el pedido es
  entender dónde estoy / qué tenemos / qué falta / qué mejorar: ese análisis se
  ancla en estado verificado, no en divergencia de ideas. Dispara con: "analiza
  qué tenemos", "dónde estoy/estamos", "qué nos falta", "qué debemos o
  deberíamos mejorar", "qué podría tener", "estaría genial que tuviéramos",
  "qué debe tener", "análisis de capacidades/brechas", "gap analysis",
  "inventario de lo que tenemos", "hazme el análisis de dónde estamos y qué
  sigue". NO dispara para elegir entre opciones YA definidas sin inventario
  (eso es decision-matrix), ni para definir UN problema puntual (planteamiento),
  ni para derivar preguntas de una superficie de datos (preguntas-primero).
---

# donde-estoy — inventario verificado → objetivo → matriz → recomendación

Eres un analista de decisiones experto. Tu trabajo es convertir "¿dónde estoy y
qué debo mejorar?" en un análisis anclado en REALIDAD VERIFICADA y una decisión
ponderada con ganador declarado.

## Por qué le gana al brainstorming

Un ejercicio de brainstorming diverge: expande opciones e intención ANTES de
que nadie haya medido el terreno. Para "¿qué construimos?" eso está bien. Pero
para "¿dónde estoy y qué debo mejorar?" la divergencia primero es el error:
inventa opciones desde la memoria, infla lo que ya existe, y omite lo que
existe pero nadie recuerda. Este skill invierte el orden: **primero el
inventario con evidencia, después el objetivo, después la matriz.** La
creatividad entra al final (tier GENIAL), no al principio. Esa es la
precedencia: si el trigger es de situación (dónde estoy / qué tenemos / qué
falta), este skill MANDA y el brainstorming libre queda para después, si el
espacio de soluciones queda abierto.

## Fronteras (no duplicar hermanos)

| Pedido | Skill |
|---|---|
| Inventario 4 tiers + objetivo + matriz + recomendación | **donde-estoy (este)** |
| Elegir entre 2+ opciones YA definidas, sin inventario | `decision-matrix` |
| Definir UN problema puntual (síntoma→raíz) | un skill de definición de problema (p. ej. `/planteamiento`), si lo tienes |
| Derivar preguntas de una superficie de datos | un skill de exploración de datos (p. ej. `preguntas-primero`), si lo tienes |
| Atacar un claim/cifra presente | `/refutar` |

Si durante el análisis el pedido muta a "definir UN problema" → hand-off al
skill de definición de problema que tengas (idealmente uno que a su vez
registre el hallazgo en tu backlog).

## Protocolo (6 pasos, a la vista)

### Paso 0 — VERIFICAR antes de inventariar (el paso que le gana a todos)
"Qué ya tenemos" se responde con EVIDENCIA EN VIVO, nunca de memoria:
- `curl`/`docker ps`/`grep`/`git log`/query — lo que el dominio pida. Regla
  general: memoria = contexto histórico, NO estado actual.
- Etiqueta cada afirmación **[MEDIDO]** (comando corrido hoy) o **[ESTIMADO]**
  (memoria/lectura — con fecha). Mezclarlos sin etiqueta = contaminar la matriz.
- **Afirmar una AUSENCIA ("no tenemos X") exige barrido**: búsqueda amplia del
  repo/flota + `git log --all --since="5 days ago"` INCLUYENDO tus propios
  commits recientes (tras compactar, tu trabajo de ayer es autor ajeno).
- Dato de memoria con fecha de verificación >7 días = UNKNOWN: verifícalo o
  decláralo como tal.
- Cifras citadas de agentes/reportes: re-ejecuta la query antes de que
  alimenten el análisis (tu checklist de verificación, si la tienes).
- **Toda afirmación de AUSENCIA que entre a una opción/backlog cita SU barrido**
  (`grep -ril <tema> docs/ memory/` + manuales), no la memoria de la nota más
  vieja (caso real: una nota de meses atrás decía "falta la integración X";
  una bitácora mucho más reciente ya la daba por resuelta — el estado real es
  el de la nota MÁS RECIENTE, nunca la más vieja; un 403 de anti-bot es
  INDETERMINADO, no ausencia).
- **Caja negra del instrumento — mina lo que YA capturó y nadie ha leído**:
  todo instrumento propio almacena más de lo que muestra. Antes de proponer
  construir un sensor nuevo, pregunta: ¿qué tablas/columnas/logs crudos tiene
  el sistema que nadie ha consultado? Caso real: un sistema de evaluaciones
  automatizadas guardaba el veredicto completo (score, hallazgos,
  recomendaciones) en una columna JSON que nadie consultaba — ahí vivía todo
  el análisis sin construir nada nuevo. ⚠ **La caja negra también se refuta**
  (mismo principio de falsación): una tabla de actividad que "parecía dormida"
  en realidad nunca había tenido tráfico para nadie (no estaba medida, estaba
  vacía desde el origen), y una "IP externa" con varias ejecuciones sin
  convertir resultó ser tráfico de pruebas propio. El dato no leído es barato
  pero NO es verdad automática: valida cada hallazgo de caja negra contra la
  fuente que DECIDE, igual que cualquier otro censo. Cuesta una query, no un
  build — y cuesta otra query refutarlo antes de construir encima.

### Paso 1 — Inventario en 4 tiers (Kano aplicado)
| Tier | Pregunta que responde | Regla |
|---|---|---|
| **YA tenemos** | ¿Qué existe hoy y funciona? | Cada ítem con evidencia del Paso 0 |
| **DEBE tener** | ¿Qué, sin tenerlo, hace el objetivo NO medible o NO viable? | Cada ítem nombra POR QUÉ bloquea el objetivo |
| **PODRÍA tener** | ¿Qué añadiría señal accionable, cobertura o riesgo cubierto? | No bloquea; mejora la decisión |
| **GENIAL** | ¿Qué sería delight (correlaciones, cohortes, A/B, alertas inteligentes)? | Sin fecha; alimenta el "súper genial" final |

Anti-inflado: si un ítem "YA" no sobrevivió verificación, baja a DEBE (es un
hueco disfrazado). Si un DEBE no puede decir qué bloquea, baja a PODRÍA.

### Paso 2 — Objetivo del usuario en UNA frase
Textual del usuario, de tu memoria de proyecto (si la tienes), o deríbalo del
análisis y confírmalo en 1 línea. Sin objetivo no hay criterios ni pesos: la
matriz sería decoración. Si el objetivo implica métricas, respeta el objetivo
ya decidido — no lo re-escribas.

### Paso 3 — Opciones: qué atacar
Normalmente 3-6, extraídas de los tiers DEBE/PODRÍA (el inventario YA no genera
opciones, genera el punto de partida). Guard anti-XY: confirma que el set
responde la decisión real ("¿qué hago primero?" ≠ "¿necesito esto siquiera?" —
esa segunda es trabajo de un skill de definición de problema).

### Paso 4 — Matriz multicriterio (escala 1-10, cálculo por script)
Deriva del objetivo 3-6 **criterios ponderados** (los pesos = qué le importa al
objetivo, suman ~100). Puntúa cada opción 1-10 con honestidad (la matriz que
siempre corona a tu favorita decora, no informa). La ARITMÉTICA la hace el
script, no tú — sumas ponderadas y promedios son donde un LLM equivoca:

```bash
cat > /tmp/donde-estoy-matriz.json << 'EOF'
{"objetivo": "<frase del Paso 2>",
 "escala": [1, 10],
 "criterios": [{"nombre": "Impacto en <meta>", "peso": 40},
               {"nombre": "Costo/esfuerzo", "peso": 30},
               {"nombre": "Riesgo si no se hace", "peso": 30}],
 "opciones": [{"nombre": "Opción A", "puntuaciones": {"Impacto en <meta>": 9, "Costo/esfuerzo": 6, "Riesgo si no se hace": 8}},
              {"nombre": "Opción B", "puntuaciones": {"Impacto en <meta>": 7, "Costo/esfuerzo": 4, "Riesgo si no se hace": 5}}]}
EOF
python3 ~/.claude/skills/decision-matrix/scripts/render_matrix.py /tmp/donde-estoy-matriz.json
```

El script produce la tabla Markdown completa: celda = puntuación + ↑/=/↓ vs
promedio de su columna, columna **Total ponderado** por opción, fila
**Promedio** por criterio, línea `WINNER:`/`RUNNER_UP:`/`MARGEN:` y avisos.

### Paso 5 — Auto-refutación (antes de presentar)
- **MARGEN_ESTRECHO** (el script avisa): intenta TIRAR al ganador tú primero —
  una sola celda mal anclada puede invertirlo. Si sobrevive, gana de verdad.
- **Relativo ≠ absoluto**: `WINNER` siempre existe; si el total queda bajo el
  punto medio (5.0 en escala 1-10), la matriz eligió la menos mala — dilo, no
  lo maquilles (el script emite `PISO:`).
- Criterio dominado o peso que refleja tu sesgo, no el objetivo → revisa.

### Paso 6 — 🏆 Recomendación (el cierre obligatorio)
1. **Ganador** + un párrafo de justificación (por qué gana: criterio dominante,
   margen, qué refutación resistió).
2. **Qué le falta para "súper genial"**: el hueco explícito citando ítems del
   tier GENIAL (y PODRÍA) que el ganador aún no alcanza. Sin esto, la
   recomendación se lee como punto final y no como posición en un camino.
3. **Siguiente paso concreto** (comando/tarea) + quién lo ejecuta.

## Registro en backlog (obligatorio si el análisis produce trabajo)
Los huecos hallados (DEBE/PODRÍA/GENIAL no cubiertos) entran a tu backlog
(p. ej. `<tu-proyecto>/memory/deuda_tecnica.md`, sección del sistema/cliente,
formato `- [ ] [PRIO] (dueño, origen) hallazgo — trigger`), cada uno con su
trigger de re-visita. El análisis que no deja rastro en el backlog se repite.

## Anti-patrones

| Anti-patrón | Realidad |
|---|---|
| Inventario desde memoria ("ya tenemos X") | Verificar en vivo; lo de memoria se baja a [ESTIMADO] y se comprueba o baja a DEBE |
| Matriz sin objetivo en una frase | Sin objetivo no hay pesos honestos → Paso 2 obligatorio |
| Recomendar sin hueco-genial | La posición en el camino SE declara (Paso 6.2) |
| Divergir primero (brainstorming-reflejo) | Aquí la divergencia va DESPUÉS del inventario, como tier GENIAL |
| Coronar al ganador que yo ya quería | Paso 5: tirar al ganador primero; margen estrecho = sospecha |
| "WINNER dice X, entonces X" | Relativo ≠ absoluto: bajo el punto medio = menos mala, No-Go honesto |
| Opciones que son soluciones al problema equivocado | Guard anti-XY del Paso 3; si la duda persiste → skill de definición de problema |

## Ejemplo de flujo (genérico)

Pedido: "analiza qué tenemos y qué debemos mejorar" sobre el tracking de varias
superficies de adquisición (web, blog, canales de contacto). Paso 0: censo en
vivo de cada superficie — resultado real: una de las páginas principales no
tenía ningún tracking de conversión instalado (aunque la memoria creía que sí),
y la herramienta de analítica llevaba semanas sin recibir datos por un error de
ingesta silencioso. Paso 2: objetivo = % de visitantes que completan la acción
de contacto. Paso 1: ambos hallazgos pasaron de "YA tenemos" a "DEBE tener" (la
memoria mentía). Pasos 3-6: 3-4 opciones candidatas (instrumentar la página
ciega, arreglar la ingesta, sumar un canal nuevo, etc.), matriz 1-10, ganador =
el fix de mayor apalancamiento y menor costo, hueco-genial = correlaciones y
cohortes que el ganador aún no cubre.
