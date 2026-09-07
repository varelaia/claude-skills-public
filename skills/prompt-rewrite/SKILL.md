---
name: prompt-rewrite
description: "Reescritura disciplinada de system prompts en producción que fallan. INVOCAR cuando: bot/asistente ignora reglas del prompt, responde seco/genérico, alucina memoria o datos que no existen, prompt creció >12K chars, user reporta 'no tiene personalidad' / 'inventa cosas' / 'no me hace caso' / 'no me recuerda'. Para LLMs chat (Claude/GPT) y voz Realtime. Proceso: captura datos reales del fallo + crítica experta vía codemaster + reescritura con XML semántico + dialog pair few-shots + sentinel NONE para memoria + addenda condicionales + deploy con 4 capas de persistencia (disco/imagen/restore/git tag) + validación E2E con reproducción del usuario."
user-invocable: true
---

# Prompt Rewrite — Reescritura disciplinada de prompts en producción

**Cuándo usar este skill:**
- Modelo en producción ignora reglas del prompt (responde seco/genérico)
- Modelo alucina memoria/datos que no existen
- Prompt creció orgánicamente >12K chars y la adherencia degradó
- User reporta "no tiene personalidad", "no me hace caso", "inventa cosas"
- Antes de "sumar más reglas" — agregar SIEMPRE empeora un prompt malo

**No usar para:**
- Crear prompt desde cero (otro flujo)
- Bugs de código que NO son del prompt (logs muestran error técnico)
- Tweaks menores de tono — usar Edit directo

## Proceso (5 fases obligatorias)

### Fase 1 — Capturar datos REALES de fallo (no especulación)

```bash
# Para asistentes de voz: leer el último transcript desde tu almacenamiento
sqlite3 /path/to/voice.db "SELECT id,duration_s,summary,transcript FROM calls ORDER BY id DESC LIMIT 2"

# Para chatbots: revisar logs últimos N mensajes
docker logs <container> --since 1h | grep -E 'user|assistant' | tail -50

# Para n8n: revisar ejecuciones recientes
curl -s --http1.1 -H "X-N8N-API-KEY: $KEY" "$N8N/api/v1/executions?workflowId=$WF&limit=5"
```

**Documentar 3 cosas concretas (no genéricas):**
1. Input exacto del user
2. Output exacto del modelo (palabras literales)
3. Comportamiento esperado vs real

Si no tienes los 3 → STOP, captura más datos antes de tocar el prompt.

### Fase 2 — Medir el prompt actual

```bash
# Extraer SYSTEM_PROMPT del código
python3 -c "
import re
content = open('PATH_TO_FILE').read()
m = re.search(r'SYSTEM_PROMPT[_A-Z]*\s*=\s*[\"\\\'][\"\\\'][\"\\\'](.*?)[\"\\\'][\"\\\'][\"\\\']', content, re.DOTALL)
if m:
    p = m.group(1)
    print(f'CHARS: {len(p)}')
    print(f'WORDS: {len(p.split())}')
    print(f'LINES: {len(p.splitlines())}')
    open('/tmp/prompt_actual.txt','w').write(p)
"
```

**Métricas red flag:**
- `>12,000 chars` → degradación de adherencia confirmada (OpenAI Realtime sweet spot: <8K)
- `>5,000 palabras` → modelo dropea instrucciones del medio
- Ratio `NUNCA:SIEMPRE > 3:1` → modelo en estado de inhibición
- Ejemplos `Caller: "X" → "Y"` en prosa → tokenizer NO los reconoce como dialog pair
- Mismo ejemplo repetido 2-3 veces en secciones distintas → modelo lo trata como template literal rígido

### Fase 3 — Crítica experta (delegar a codemaster)

```python
Agent({
    "subagent_type": "codemaster",
    "description": "Critica prompt produccion",
    "prompt": """
    Eres experto en prompt engineering para [LLM_TARGET — ej: OpenAI Realtime, Claude Sonnet, GPT-5].

    Contexto del problema concreto (NO especulación — datos reales):
    [PEGAR LOS 3 EJEMPLOS CAPTURADOS EN FASE 1]

    Datos del prompt:
    - Archivo: /tmp/prompt_actual.txt
    - [METRICAS DE FASE 2]
    - Modelo: [...]
    - Idioma: [...]
    - Casos de uso: [...]

    Entrega análisis estructurado:
    1. Top 5 problemas REALES con citas literales del prompt (líneas/secciones)
    2. ¿Por qué el modelo ignora la regla X? (position bias, dilution, contradicciones)
    3. Reescritura propuesta — esqueleto recortado <8K chars con estructura jerárquica
    4. Errores específicos en few-shots (formato, generalización, repetición)
    5. State-of-the-art comparativo (anti-patrones + best practices oficiales)

    LEE PRIMERO /tmp/prompt_actual.txt. Sé brutal. Máx 1500 palabras.
    """
})
```

Si la crítica del agente no cita líneas literales del prompt → pedir de nuevo. Crítica genérica = inútil.

### Fase 4 — Reescritura V3 con 7 principios estructurales

**Aplicar TODOS — son ortogonales y se refuerzan:**

#### 1. Reglas duras al INICIO (top-of-mind)
Las primeras ~600 tokens tienen máxima adherencia. Pon ahí 3-5 reglas no negociables, cada una con UNA línea de "qué hacer" + 1 línea de "por qué importa".

```
🔑 5 REGLAS DURAS (no negociables)

R1 — [Comportamiento crítico]: [acción esperada]. [Razón en 1 línea].
R2 — ...
```

#### 2. Contexto dinámico con XML tags semánticos
El modelo respeta tags estructurados. Inyecta SIEMPRE los slots, con sentinel `NONE` cuando vacíos:

```
<caller>nombre={X}, label={Y}, vip={true|false}, hora={CST}</caller>
<memoria_previa>NONE</memoria_previa>   <!-- o lista real -->
<modo>inbound | outbound | nocturno</modo>
```

**El sentinel `NONE` literal es CRÍTICO** — el modelo distingue "vacío" de "ausencia". Sin sentinel inventa contenido para llenar el slot mental.

#### 3. Few-shots como dialog pairs (no prosa)
```
❌ MAL (modelo lo lee como narrativa):
- Caller: "X" → "Y"

✅ BIEN (tokenizer reconoce dialog pair):
<turn><user>X</user><asistente>Y</asistente></turn>
```

#### 4. 3-5 variantes por categoría conductual
Un solo ejemplo NO generaliza. Si el caller real dice "soy TU hija" pero el ejemplo es "soy SU hija", el match falla → fallback a default frío. Necesitas 3-5 variantes paralelas del mismo patrón.

```
### Categoría: afecto familiar humorístico
<turn><user>soy tu hija favorita</user><asistente>...</asistente></turn>
<turn><user>soy su hija favorita</user><asistente>...</asistente></turn>
<turn><user>habla la nuera</user><asistente>...</asistente></turn>
<turn><user>soy su mamá</user><asistente>...</asistente></turn>
<turn><user>habla el compadre</user><asistente>...</asistente></turn>
```

#### 5. Addenda condicionales (no inline)
Bloques aplicables solo a ciertos contextos (modo nocturno, tipo de caller, modo outbound) → mover a constantes separadas e inyectar SOLO cuando aplican.

```python
ADDENDUM_NOCTURNO = """<addendum_modo_nocturno>...</addendum_modo_nocturno>"""
ADDENDUM_VIP = """<addendum_caller_vip>...</addendum_caller_vip>"""

# En entrypoint:
if night: extra += ADDENDUM_NOCTURNO
if is_vip: extra += ADDENDUM_VIP
```

Reduce el prompt base 30-50% y elimina ruido para casos donde no aplica.

#### 6. Tools como tabla simple
```
| Tool | Usar cuando | NO usar cuando |
|---|---|---|
| take_message | caller explicó motivo Y le diste 1 valor | aún no entiendes qué quiere |
```

NO escribir párrafos descriptivos por tool — el modelo no los procesa bien.

#### 7. Audio cues prosódicos (solo voz)
Para modelos de voz Realtime: `[pausa breve]`, `[tono cálido]`, `[con sonrisa en la voz]`. Funcionan literalmente.

### Fase 5 — Deploy con 4 capas de persistencia

```bash
# 1. Restore point en el servidor (ajusta host/path a tu setup)
ssh <tu-host> "cp /opt/svc/file.py /opt/svc/file.py.restore-pre-vN-$(date +%Y%m%d-%H%M)"

# 2. Copia + verify md5
scp local.py <tu-host>:/tmp/
ssh <tu-host> "md5sum /tmp/file.py" # match local

# 3. Swap + py_compile + redeploy
ssh <tu-host> "cp /tmp/file.py /opt/svc/file.py && python3 -m py_compile /opt/svc/file.py && cd /opt/svc && bash redeploy.sh"

# 4. Git commit + tag (4a capa: GitHub remoto)
git add path/to/prompt.py
git commit -m "svc vN.X: prompt rewrite — XX% smaller + structured semantics

Resuelve bugs reportados:
- Bug 1: [...]
- Bug 2: [...]

Restore: /opt/svc/file.py.restore-pre-vN-...
SHA: $(sha256sum)"

git tag -a svc-vN.X -m "..."
git push origin <branch>
git push origin svc-vN.X
```

### Fase 6 — Validación E2E (NO opcional)

```bash
# Verificar SHA disco==container
ssh <tu-host> "sha256sum /opt/svc/file.py | cut -c1-16; docker exec svc sha256sum /app/file.py | cut -c1-16"

# Verificar worker registered + sin errores
ssh <tu-host> "docker ps --filter name=svc --format '{{.Status}}'; docker logs svc --tail 30 | grep -E 'ERROR|Traceback'"
```

**Después pedir al usuario que reproduzca el flujo original que falló** — si no hay reproducción real, no hay fix verificado.

## Métricas de éxito

| Métrica | Antes | Target después |
|---|---|---|
| Total prompt chars | medir | <8K (Realtime) o <12K (chat) |
| Words count | medir | -70% mínimo |
| NUNCA:SIEMPRE ratio | medir | <3:1 |
| Few-shots por categoría | medir | 3-5 variantes |
| Sentinel NONE en slots vacíos | rara vez | SIEMPRE |
| Addenda condicionales | inline | extraídos |

## Anti-patrones del proceso

- **Tweakear sin medir**: agregar 2 reglas más a un prompt de 35K chars no arregla nada.
- **Crítica genérica**: "es muy largo" sin citar líneas específicas no sirve.
- **Skip de fase 1**: reescribir sin datos reales = inventar problemas.
- **Skip restore point**: rollback sin restore point = pérdida de trabajo previo.
- **Deploy sin reproducción E2E**: "compila bien" ≠ "funciona en producción".

## Caso de referencia (ejemplo representativo)

Un asistente de voz en producción, tras la reescritura:
- 35,867 → 8,277 chars (-77%)
- 5,685 → 1,041 palabras (-82%)
- Bugs resueltos: bot seco / alucinación de memoria / sin actitud
- Tag git: `<asistente>-prompt-v2`
- Restore: `<path>/agent.py.restore-pre-rewrite-*`
- Crítica del experto: 5 problemas con citas literales, 4-6h estimado, impacto medible

## Tools / agents que usa este skill

- `codemaster` — crítica experta del prompt (KB 2.3GB en prompts/system prompts)
- Bash + SSH — captura de datos producción + deploy
- Python regex — extracción y medición del prompt
- Git — commit + tag para 4a capa de persistencia
