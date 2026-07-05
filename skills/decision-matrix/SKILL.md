---
name: decision-matrix
description: >-
  Construye una matriz de decisión multicriterio en Markdown para elegir entre
  varias opciones evaluadas contra criterios ponderados. Cada celda muestra una
  puntuación (escala 1-5) y un símbolo ↑/=/↓ que indica si está por encima, igual
  o por debajo del promedio de su columna; agrega una columna "Total ponderado"
  por opción, una fila "Promedio" por criterio, y un apartado "🏆 Recomendación"
  que justifica al ganador. Dispara cuando el usuario pide "matriz de decisión",
  "matriz multicriterio", "ayúdame a decidir entre X, Y, Z", "compara estas
  opciones con criterios", "tabla de decisión ponderada", "evalúa opciones contra
  criterios", "¿cuál conviene más?", "matriz de criterios", o cuando enfrenta una
  decisión entre 2+ alternativas y menciona factores/criterios a sopesar — aunque
  no diga literalmente "matriz". Dispara TAMBIÉN cuando se comparan PROBLEMAS o
  SOLUCIONES entre sí: "compara estos problemas", "cuál problema atacar primero",
  "compara estas soluciones", "qué solución es mejor", "evalúa estos enfoques/
  approaches/alternativas", "cuál arreglo conviene", "prioriza estos problemas por
  impacto" — siempre que haya 2+ candidatos a sopesar contra factores. Úsalo
  también para decisiones de negocio, proveedores, arquitectura, contratación,
  pricing, troubleshooting (qué causa raíz perseguir) o cualquier elección
  estructurada. NO lo uses para preguntas de una sola respuesta sin alternativas,
  ni para priorizar tareas (eso es otra cosa), ni cuando el usuario solo pide un pro/
  contra simple sin ponderación.
---

# Matriz de decisión multicriterio

Eres un analista de decisiones experto. Tu trabajo es convertir una decisión
difusa ("¿qué conviene más?") en una matriz multicriterio honesta, calculada sin
errores de aritmética, con una recomendación justificada.

## Por qué este flujo

Dos riesgos arruinan una matriz de decisión:

1. **Aritmética equivocada** — las sumas ponderadas y los promedios de columna son
   fáciles de calcular mal a mano. Por eso el cálculo lo hace un script
   determinista (`scripts/render_matrix.py`), no tú a ojo.
2. **Sesgo de confirmación** — es tentador inflar la opción que ya prefieres. Una
   matriz que siempre "gana" la opción que querías desde el principio no informa,
   decora. Tu valor está en puntuar honesto, incluso cuando el número derrumba la
   opción favorita.

Tú aportas el juicio (criterios, pesos, puntuaciones, recomendación); el script
aporta los números.

## Flujo (intake híbrido: infiere → confirma → calcula)

### Paso 1 — Identifica el objetivo
Lee la petición y extrae la decisión real en una frase:
"Elegir [entre qué opciones] para [qué fin], priorizando [qué importa]".
Si la decisión no está clara, eso sí pregúntalo antes de seguir.

Las "opciones" son cualquier conjunto de candidatos a sopesar: productos,
proveedores, arquitecturas — pero también **problemas** (cuál atacar primero),
**soluciones/enfoques** (qué arreglo conviene) o **causas raíz** (cuál perseguir).
La mecánica es la misma; solo cambia qué nombras en la columna "Opción" y qué
criterios eliges (p. ej. para problemas: impacto, frecuencia, costo de no
arreglar, esfuerzo del fix).

### Paso 2 — Propón el borrador (infiere) y CONFÍRMALO
Antes de calcular nada, infiere y muestra en formato corto (lectura de 20s):

- **Opciones** a comparar (2+).
- **Criterios** relevantes (típicamente 3-6) — los factores que de verdad mueven
  esta decisión, no relleno.
- **Pesos** en % que **sumen 100** — refleja qué importa más. Justifica cada peso
  en media línea.

Muéstralo y espera el visto bueno del usuario ("ok", "dale", o ajustes). Si pide
cambios (otro criterio, otro peso, otra opción), incorpóralos. **No pases al Paso 3
sin confirmación** — los pesos cambian el resultado y son la decisión más
subjetiva de todo el ejercicio; merece su luz verde.

Si el usuario ya te dio criterios/pesos/opciones explícitos, no los re-preguntes:
confírmalos en una línea y sigue.

### Paso 3 — Puntúa honesto (escala 1-5)
Asigna a cada opción una puntuación 1-5 por criterio. **Reglas de honestidad:**

- Puntúa por evidencia/razonamiento, no por preferencia. Si no tienes datos para
  un criterio, di el supuesto explícitamente ("asumo X porque…") y márcalo débil.
- No ancles todo cerca de la opción favorita. Usa el rango completo 1-5 cuando los
  hechos lo justifican; las diferencias reales deben verse.
- Está perfectamente bien que la matriz haga perder la opción que parecía obvia —
  ese es exactamente el tipo de hallazgo que hace útil el ejercicio. Repórtalo sin
  suavizar (la honestidad es el punto: si la opción favorita gana 0/6 escenarios,
  dilo).

### Paso 4 — Calcula con el script
Arma el JSON y pásalo al script. **No calcules los totales ni los promedios a
mano.**

```bash
python3 ~/.claude/skills/decision-matrix/scripts/render_matrix.py /tmp/matriz.json
```

(O por stdin: `cat /tmp/matriz.json | python3 .../render_matrix.py`.)

Schema del JSON:

```json
{
  "objetivo": "Elegir CRM para la agencia priorizando costo y rapidez de adopción",
  "criterios": [
    {"nombre": "Costo mensual", "peso": 30},
    {"nombre": "Curva de adopción", "peso": 25},
    {"nombre": "Integraciones", "peso": 25},
    {"nombre": "Soporte en español", "peso": 20}
  ],
  "opciones": [
    {"nombre": "HighLevel", "puntuaciones": {"Costo mensual": 3, "Curva de adopción": 4, "Integraciones": 5, "Soporte en español": 4}},
    {"nombre": "Kommo",     "puntuaciones": {"Costo mensual": 4, "Curva de adopción": 3, "Integraciones": 4, "Soporte en español": 5}}
  ]
}
```

El script imprime la tabla Markdown ya formateada (celdas con ↑/=/↓, columna
**Total ponderado**, fila **Promedio**) y una línea `WINNER:` con el ganador,
`RUNNER_UP:` y `MARGEN:`. Si los pesos no suman 100 o hay puntuaciones fuera de
rango, imprime `AVISO:` — corrígelo o explícalo.

### Paso 5 — Presenta + 🏆 Recomendación
Muestra la tabla tal cual la devuelve el script. Debajo, escribe el apartado:

```markdown
## 🏆 Recomendación

[Opción ganadora] obtiene el total ponderado más alto ([X.XX]). [Un párrafo: por
qué gana — qué criterios de alto peso domina, dónde cede frente al segundo lugar,
y qué tan ajustado es el margen. Si el margen es estrecho (< ~0.3), dilo: la
decisión es sensible a los pesos y vale revisarlos. Si la matriz contradice la
intuición inicial, nómbralo explícitamente.]
```

La recomendación sigue al número (gana el `WINNER:` del script), pero tu párrafo
debe ser honesto sobre cuán robusta es esa victoria — un margen de 0.05 no es lo
mismo que uno de 1.2.

## Formato de salida (referencia)

```markdown
**Objetivo:** Elegir CRM para la agencia…

| Opción | Costo mensual (30%) | Curva de adopción (25%) | … | **Total ponderado** |
|---|---|---|---|---|
| HighLevel | 3 ↓ | 4 ↑ | … | **3.95** |
| Kommo | 4 ↑ | 3 ↓ | … | **4.05** |
| **Promedio** | _3.50_ | _3.50_ | _…_ | — |

_Escala 1-5. Símbolo ↑/=/↓ = puntuación vs. promedio de su columna._

## 🏆 Recomendación
…
```

## Notas

- **Honestidad > narrativa cómoda.** Si el usuario tiene una opción favorita y la
  matriz dice otra cosa, ese es el resultado valioso. No reverse-engineer los
  pesos para que gane la preferida.
- Mantén 3-6 criterios. Más de ~7 diluye y nadie distingue los pesos.
- Si una decisión tiene un criterio eliminatorio (un must-have binario que una
  opción no cumple), dilo aparte: la matriz pondera, no veta. Una opción puede
  ganar en puntos y aun así quedar descartada por no cumplir un requisito duro.
