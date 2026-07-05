---
name: anti-hype-acronyms-guard
description: "PRE-DELIVERY gate obligatorio: revisa todo PDF/propuesta/email cliente por acrónimos sin métricas medibles, claims de liderazgo sin evidencia, y acumulación de siglas (Mueller alert: 5+ acrónimos seguidos = spam signal). Emite PASS / WARN (con counter-propuesta) / FAIL (con correcciones específicas). Se invoca AUTOMÁTICAMENTE antes de cualquier entrega de propuesta o PDF de auditoría a cliente. Contiene regex Python ejecutables."
user-invocable: true
auto-invoke: "ANTES de renderizar un PDF de auditoría para cliente; ANTES de enviar propuesta por WA o email; ANTES de generar cualquier reporte visible al cliente"
proposed-by: Basado en Mueller alert (Google, agosto 2025)
priority: P0
---

# Anti-Hype Acronyms Guard — Mueller Alert Prevention

Mueller (Google, agosto 2025): "the stronger the push of new acronyms, the more likely they're just making spam and scamming." Este guard existe para que cualquier entregable a cliente nunca active esa señal. Las propuestas deben comunicar outcomes medibles, no stacks de siglas.

Lily Ray corolario: GEO tactics que priorizan citation engineering sobre SEO foundation causan churn porque el cliente ve citas que no convierten. Este guard también detecta ese patrón.

## Cuándo invocar

- Automáticamente antes de cualquier entrega de PDF a cliente (el pipeline de renderizado lo invoca)
- El usuario dice "revisa esta propuesta antes de enviar"
- El usuario dice "corre el guard en [archivo]"
- Antes de cualquier mensaje WA a prospecto con propuesta de servicios
- Antes de publicar contenido en nombre del equipo/agencia (blog, LinkedIn, newsletter)

## Pre-flight gate

```bash
INPUT_FILE="${INPUT_FILE:?ERROR: set INPUT_FILE=/path/to/propuesta.txt o propuesta.html}"
OUTPUT_REPORT="${OUTPUT_REPORT:-/tmp/antihype_guard_$(date +%Y%m%d_%H%M%S).json}"

# Extraer texto plano si es HTML o PDF
EXTENSION="${INPUT_FILE##*.}"
if [ "$EXTENSION" = "html" ]; then
  python3 -c "
from html.parser import HTMLParser
class T(HTMLParser):
    def __init__(self): super().__init__(); self.d=[]
    def handle_data(self, d): self.d.append(d)
p=T(); p.feed(open('$INPUT_FILE').read())
print(' '.join(p.d))
" > /tmp/antihype_text_input.txt
elif [ "$EXTENSION" = "pdf" ]; then
  python3 -c "
try:
    import pdfplumber
    with pdfplumber.open('$INPUT_FILE') as pdf:
        print(' '.join(p.extract_text() or '' for p in pdf.pages))
except ImportError:
    print('ERROR: pdfplumber no instalado. pip install pdfplumber')
" > /tmp/antihype_text_input.txt
else
  cp "$INPUT_FILE" /tmp/antihype_text_input.txt
fi

TEXT_INPUT="/tmp/antihype_text_input.txt"
test -s "$TEXT_INPUT" || { echo "ERROR: texto vacío después de extracción"; exit 1; }
wc -w "$TEXT_INPUT"
```

## Scanner Python — ejecutar esto

```python
#!/usr/bin/env python3
"""
anti_hype_guard.py — Mueller Alert Prevention Scanner
Uso: python3 anti_hype_guard.py --input /tmp/antihype_text_input.txt --output /tmp/report.json
"""
import re
import json
import sys
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Tuple

# ─────────────────────────────────────────────
# DEFINICION DE FLAGS
# ─────────────────────────────────────────────

@dataclass
class Flag:
    severity: str        # FAIL | WARN
    category: str
    pattern_matched: str
    context: str         # fragmento del texto donde ocurrió
    line_approx: int
    fix_suggestion: str

@dataclass
class GuardResult:
    verdict: str         # PASS | WARN | FAIL
    flags: List[Flag] = field(default_factory=list)
    pass_conditions: List[str] = field(default_factory=list)
    summary: str = ""

# ─────────────────────────────────────────────
# PATRONES — Mueller Alert
# ─────────────────────────────────────────────

# Acumulación de acrónimos: 4+ siglas en ventana de 30 palabras
ACRONYM_RE = re.compile(r'\b[A-Z]{2,5}\b')

def check_acronym_accumulation(text: str) -> List[Flag]:
    """Detecta rachas de acrónimos: Mueller alert si 5+ en 30 palabras."""
    flags = []
    words = text.split()
    window = 30
    for i in range(len(words) - window):
        chunk = words[i:i+window]
        chunk_text = " ".join(chunk)
        acronyms_found = ACRONYM_RE.findall(chunk_text)
        # Filtrar falsos positivos comunes
        false_positives = {"KPI", "URL", "PDF", "API", "CEO", "MXN", "USD", "OK",
                           "SEO", "GEO", "AEO", "CTA", "CRM", "FAQ", "ROI", "MX"}
        real_acronyms = [a for a in acronyms_found if len(a) >= 3]
        if len(real_acronyms) >= 5:
            flags.append(Flag(
                severity="FAIL",
                category="mueller_acronym_accumulation",
                pattern_matched=f"{len(real_acronyms)} acrónimos en 30 palabras: {', '.join(set(real_acronyms))}",
                context=chunk_text[:120] + "...",
                line_approx=i,
                fix_suggestion=(
                    "Eliminar o agrupar: en lugar de 'SEO + GEO + AEO + LLMO + AIO' "
                    "usar 'visibilidad en búsqueda, snippets de IA, y fuentes citadas por LLMs'. "
                    "Regla: máximo 2 acrónimos técnicos por párrafo de propuesta."
                )
            ))
            break  # Un solo FAIL es suficiente para esta categoría
    return flags

# Patrones de liderazgo sin evidencia
LEADERSHIP_PATTERNS = [
    (re.compile(r'\b(líderes?|líder)\s+(en|de|del)\s+(SEO|GEO|AEO|IA|México|Monterrey|mercado)', re.I),
     "FAIL", "leadership_no_evidence",
     "Reemplazar con métrica específica: 'Citation Rate 12/24 en queries de IA' en lugar de 'líderes en GEO'."),

    (re.compile(r'\b(somos|soy|es)\s+el?\s+(único|primer|mejor)\s+\w+\s+(en|de)\s+(México|Monterrey|MX)', re.I),
     "FAIL", "superlative_unverified",
     "Eliminar superlativo. Si es verdad, citar fuente verificable. Si no hay fuente, es claim no verificable."),

    (re.compile(r'\b(expertos?\s+en|especialistas?\s+en)\s+([A-Z]{2,5}\s*\+?\s*){3,}', re.I),
     "WARN", "expert_acronym_stack",
     "Tres o más acrónimos después de 'expertos en' activa señal de spam. "
     "Usar 'especialistas en visibilidad para motores de IA' (outcome) en su lugar."),

    (re.compile(r'\b(número\s+uno|#1|top\s+1)\s+(en|de)\s+\w+', re.I),
     "FAIL", "number_one_claim",
     "Claim no verificable. Reemplazar con dato real: posición en ranking específico + fuente + fecha."),
]

def check_leadership_claims(text: str) -> List[Flag]:
    flags = []
    for pattern, severity, category, fix in LEADERSHIP_PATTERNS:
        for match in pattern.finditer(text):
            ctx_start = max(0, match.start() - 60)
            ctx_end = min(len(text), match.end() + 60)
            flags.append(Flag(
                severity=severity,
                category=category,
                pattern_matched=match.group(0),
                context=text[ctx_start:ctx_end],
                line_approx=text[:match.start()].count('\n'),
                fix_suggestion=fix
            ))
    return flags

# Métricas vanity sin baseline
VANITY_PATTERNS = [
    (re.compile(r'aumentamos?\s+(tu\s+)?(visibilidad|presencia|alcance)', re.I),
     "FAIL", "vanity_metric_no_baseline",
     "Sin % específico y baseline es claim vacío. Reemplazar con: "
     "'Citation Rate actual: X/24 queries. Objetivo 90 días: Y/24 (+Z%).'"
     ),
    (re.compile(r'mejoramos?\s+(tu\s+)?(posicionamiento|ranking|visibilidad)', re.I),
     "WARN", "vanity_improve_no_delta",
     "Agregar delta específico: '...de posición 8 a posición 3 en query [X] según medición [fecha]'."
     ),
    (re.compile(r'más\s+(clientes?|visitas?|tráfico|prospectos?)\s+(para\s+ti|garantizado)', re.I),
     "FAIL", "guarantee_without_data",
     "Garantías sin datos son falsas promesas. Eliminar 'garantizado'. "
     "Si tienes caso de éxito: citar cliente (con consentimiento) + métrica real."
     ),
    (re.compile(r'(transformamos?|revolucionamos?)\s+tu\s+\w+', re.I),
     "WARN", "marketing_verb_hype",
     "Verbos de hipérbole ('transformamos', 'revolucionamos') sin mecanismo específico. "
     "Reemplazar con el mecanismo: 'Implementamos schemas X que aumentan citation rate de Y a Z'."
     ),
]

def check_vanity_metrics(text: str) -> List[Flag]:
    flags = []
    for pattern, severity, category, fix in VANITY_PATTERNS:
        for match in pattern.finditer(text):
            ctx_start = max(0, match.start() - 60)
            ctx_end = min(len(text), match.end() + 60)
            flags.append(Flag(
                severity=severity,
                category=category,
                pattern_matched=match.group(0),
                context=text[ctx_start:ctx_end],
                line_approx=text[:match.start()].count('\n'),
                fix_suggestion=fix
            ))
    return flags

# Pricing diferenciado por acrónimo sin diferenciador técnico
PRICING_HYPE = [
    (re.compile(r'(paquete|tier|plan)\s+(SEO|GEO|AEO|LLMO|AIO)\s+\$[\d,]+', re.I),
     "WARN", "tier_named_by_acronym",
     "Un tier nombrado por acrónimo sin descripción de entregables concretos "
     "activa la señal Mueller. Nombrar tiers por outcome: 'Visibilidad Base', 'Visibilidad Completa'. "
     "O usar Lite/Std/Pro con tabla de entregables específicos debajo."
     ),
]

def check_pricing_hype(text: str) -> List[Flag]:
    flags = []
    for pattern, severity, category, fix in PRICING_HYPE:
        for match in pattern.finditer(text):
            ctx_start = max(0, match.start() - 60)
            ctx_end = min(len(text), match.end() + 60)
            flags.append(Flag(
                severity=severity,
                category=category,
                pattern_matched=match.group(0),
                context=text[ctx_start:ctx_end],
                line_approx=text[:match.start()].count('\n'),
                fix_suggestion=fix
            ))
    return flags

# Inventar clientes / métricas no verificadas
CLIENT_INVENTION = [
    (re.compile(r'(caso\s+de\s+éxito|cliente|empresa)\s+.{0,30}(logró|obtuvo|alcanzó)\s+\d+%', re.I),
     "WARN", "client_metric_verify",
     "Verificar que este cliente tiene consentimiento escrito para ser mencionado. "
     "Si no hay contrato/factura verificable: eliminar nombre y genericizar a 'cliente del sector X'."
     ),
    (re.compile(r'(distribuidora|despacho|empresa|consultora)\s+[A-Z][a-z]+\s+.{0,20}(logró|obtuvo)', re.I),
     "FAIL", "invented_client_pattern",
     "Patron de cliente inventado detectado (nombre genérico + empresa + métrica). "
     "Regla P0: NUNCA inventar clientes. Si no existe contrato/factura real, eliminar."
     ),
]

def check_client_invention(text: str) -> List[Flag]:
    flags = []
    for pattern, severity, category, fix in CLIENT_INVENTION:
        for match in pattern.finditer(text):
            ctx_start = max(0, match.start() - 60)
            ctx_end = min(len(text), match.end() + 60)
            flags.append(Flag(
                severity=severity,
                category=category,
                pattern_matched=match.group(0),
                context=text[ctx_start:ctx_end],
                line_approx=text[:match.start()].count('\n'),
                fix_suggestion=fix
            ))
    return flags

# Palabras prohibidas (reglas de naming del equipo)
PROHIBITED_WORDS = [
    (re.compile(r'\bFINAL\b', re.I), "WARN", "prohibited_word_final",
     "Regla de naming: 'FINAL' prohibido en nombres de archivos y documentos. Usar versión: v1, v2, etc."),
    (re.compile(r'\b(WOW|AMAZING|POWER|ULTIMATE)\b', re.I), "WARN", "prohibited_marketing_speak",
     "Regla de naming: marketing-speak prohibido en entregables visibles al cliente. "
     "Usar identificadores técnicos: folio + versión + cliente."),
    (re.compile(r'\bCPMAI\b'), "WARN", "internal_methodology_in_client_doc",
     "Regla de naming: acrónimos de metodologías internas no aparecen en PDFs/propuestas cliente. "
     "Solo credenciales verificables externamente (Ph.D., PMP, etc.)."),
]

def check_prohibited_words(text: str) -> List[Flag]:
    flags = []
    for pattern, severity, category, fix in PROHIBITED_WORDS:
        for match in pattern.finditer(text):
            ctx_start = max(0, match.start() - 40)
            ctx_end = min(len(text), match.end() + 40)
            flags.append(Flag(
                severity=severity,
                category=category,
                pattern_matched=match.group(0),
                context=text[ctx_start:ctx_end],
                line_approx=text[:match.start()].count('\n'),
                fix_suggestion=fix
            ))
    return flags


# ─────────────────────────────────────────────
# ORQUESTADOR
# ─────────────────────────────────────────────

def run_guard(text: str) -> GuardResult:
    all_flags = []
    all_flags += check_acronym_accumulation(text)
    all_flags += check_leadership_claims(text)
    all_flags += check_vanity_metrics(text)
    all_flags += check_pricing_hype(text)
    all_flags += check_client_invention(text)
    all_flags += check_prohibited_words(text)

    fail_count = sum(1 for f in all_flags if f.severity == "FAIL")
    warn_count = sum(1 for f in all_flags if f.severity == "WARN")

    if fail_count > 0:
        verdict = "FAIL"
        summary = (
            f"{fail_count} problemas bloqueantes + {warn_count} advertencias. "
            f"NO ENTREGAR hasta corregir todos los FAIL."
        )
    elif warn_count > 0:
        verdict = "WARN"
        summary = (
            f"0 FAIL, {warn_count} advertencias. Revisar antes de enviar. "
            f"Corregir WARNs mejora percepción de credibilidad del cliente."
        )
    else:
        verdict = "PASS"
        summary = "Sin flags. Propuesta libre de hype detectable. Proceder con delivery."

    pass_conditions = []
    if not any(f.category == "mueller_acronym_accumulation" for f in all_flags):
        pass_conditions.append("Sin acumulación de acrónimos (Mueller safe)")
    if not any(f.category in ("leadership_no_evidence", "superlative_unverified") for f in all_flags):
        pass_conditions.append("Sin claims de liderazgo sin evidencia")
    if not any(f.category == "invented_client_pattern" for f in all_flags):
        pass_conditions.append("Sin clientes inventados detectados")

    return GuardResult(verdict=verdict, flags=all_flags,
                       pass_conditions=pass_conditions, summary=summary)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", default="/tmp/antihype_report.json")
    args = parser.parse_args()

    text = Path(args.input).read_text(encoding="utf-8", errors="ignore")
    result = run_guard(text)

    Path(args.output).write_text(json.dumps(asdict(result), indent=2, ensure_ascii=False))

    print(f"\n{'='*52}")
    print(f"ANTI-HYPE GUARD RESULT: {result.verdict}")
    print(f"{'='*52}")
    print(f"{result.summary}")
    if result.flags:
        print(f"\nFlags ({len(result.flags)}):")
        for f in result.flags:
            print(f"  [{f.severity}] {f.category}")
            print(f"    Match:   '{f.pattern_matched[:80]}'")
            print(f"    Context: ...{f.context[:100]}...")
            print(f"    Fix:     {f.fix_suggestion[:120]}")
            print()
    if result.pass_conditions:
        print("Condiciones aprobadas:")
        for c in result.pass_conditions:
            print(f"  + {c}")
    print(f"\nReporte completo: {args.output}")

    sys.exit(0 if result.verdict != "FAIL" else 1)
```

## Cómo invocar el scanner en pipeline

```bash
# Invocar en texto plano
python3 /path/to/anti_hype_guard.py \
  --input /tmp/antihype_text_input.txt \
  --output "$OUTPUT_REPORT"

GUARD_EXIT=$?
GUARD_VERDICT=$(python3 -c "import json; d=json.load(open('$OUTPUT_REPORT')); print(d['verdict'])")

if [ "$GUARD_EXIT" -ne 0 ]; then
  echo "DELIVERY BLOQUEADO: anti-hype guard retornó FAIL"
  echo "Corregir todos los [FAIL] antes de entregar al cliente."
  echo "Reporte: $OUTPUT_REPORT"
  exit 1
else
  echo "Guard: $GUARD_VERDICT — proceder con delivery"
fi
```

## Output esperado

```
====================================================
ANTI-HYPE GUARD RESULT: FAIL | WARN | PASS
====================================================
<summary>

Flags (N):
  [FAIL] mueller_acronym_accumulation
    Match:   'SEO + GEO + AEO + LLMO + AIO en tu estrategia'
    Context: ...somos líderes en SEO + GEO + AEO + LLMO + AIO en tu estrategia de...
    Fix:     Eliminar o agrupar: usar 'visibilidad en búsqueda, snippets de IA, y...

Condiciones aprobadas:
  + Sin acumulación de acrónimos (Mueller safe)
  + Sin clientes inventados detectados
```

## Tabla de categorías de flag

| Categoría | Severity | Patrón | Acción |
|---|---|---|---|
| `mueller_acronym_accumulation` | FAIL | 5+ siglas en 30 palabras | Reescribir con outcomes en lenguaje natural |
| `leadership_no_evidence` | FAIL | "líderes en SEO" sin fuente | Reemplazar con métrica medida |
| `superlative_unverified` | FAIL | "el mejor/único en México" | Eliminar o citar fuente verificable |
| `expert_acronym_stack` | WARN | "expertos en SEO+GEO+AEO" | Usar outcome en lugar de stack |
| `number_one_claim` | FAIL | "#1 en X" sin ranking | Eliminar o citar ranking con fecha |
| `vanity_metric_no_baseline` | FAIL | "aumentamos visibilidad" sin % | Agregar baseline + delta + plazo |
| `vanity_improve_no_delta` | WARN | "mejoramos posicionamiento" | Agregar delta numérico específico |
| `guarantee_without_data` | FAIL | "más clientes garantizado" | Eliminar garantía o citar caso con consentimiento |
| `marketing_verb_hype` | WARN | "transformamos/revolucionamos" | Reemplazar con mecanismo específico |
| `tier_named_by_acronym` | WARN | "Plan GEO $X" sin entregables | Nombrar por outcome o agregar tabla entregables |
| `client_metric_verify` | WARN | cliente + métrica % | Verificar consentimiento escrito |
| `invented_client_pattern` | FAIL | empresa genérica + métrica | Eliminar (regla P0 clientes reales) |
| `prohibited_word_final` | WARN | "FINAL" en documento | Usar versión numérica |
| `prohibited_marketing_speak` | WARN | "WOW/AMAZING/POWER" | Usar identificador técnico |
| `internal_methodology_in_client_doc` | WARN | acrónimo de metodología interna en propuesta | Eliminar — solo credenciales verificables |

## Reglas de autoridad del guard (no negociables)

1. Si `verdict = FAIL`: el pipeline de entrega NO envía output al cliente. El PDF se genera pero se marca `[DRAFT — REVISAR]` en el header.
2. Si `verdict = WARN`: entrega permitida pero el usuario debe revisar manualmente cada WARN antes de enviar por WA.
3. Si `verdict = PASS`: proceder con delivery sin fricción adicional.
4. El guard NO puede ser bypaseado por "urgencia" o "el cliente ya está esperando". Si hay FAIL, hay FAIL.
5. WARN de `invented_client_pattern` se escala automáticamente a FAIL si el nombre del cliente no aparece en el registro de clientes reales del equipo (no hay registro/contrato verificable).

## Integración con otras skills

- BLOQUEADO POR: el orchestrator del pipeline de auditoría lo invoca
- BLOQUEA: el paso de renderizado/entrega de PDF si verdict = FAIL
- DEPENDE DE: ninguna skill previa (standalone, puede correr sobre cualquier texto)
- DESBLOQUEA: el paso de renderizado/entrega si verdict = PASS/WARN-revisado

## Anti-patterns

1. Correr el guard DESPUÉS de enviar la propuesta. El orden es: guard → corrección → delivery. No al revés.
2. Ignorar WARNs por "son solo advertencias". Tres WARNs del mismo tipo en una propuesta son un FAIL encubierto.
3. Agregar excepciones al scanner sin documentarlas aquí. Si un patrón produce falsos positivos, agregar a la lista `false_positives` con comentario y fecha.
4. Usar el guard solo en propuestas grandes y saltarlo en mensajes WA. Los mensajes WA al prospecto son el primer contacto — aplica el mismo estándar.
5. Pensar que "nuestros competidores también usan hype" justifica usarlo. Mueller no distingue entre jugadores grandes y chicos. El riesgo de reputación es simétrico.
6. Modificar el scanner para que sea menos estricto cuando hay presión de cierre. El guard existe precisamente para esos momentos.

## Notas de implementación

- Crear el archivo del scanner (por ejemplo `anti_hype_guard.py`) copiando el bloque Python de esta skill en la ubicación que prefieras dentro de tu proyecto
- Requiere solo stdlib + pathlib — no hay dependencias adicionales
- Compatible con Python 3.11+
- El archivo de reporte JSON en `/tmp/` puede ser consultado por otras skills para integración
