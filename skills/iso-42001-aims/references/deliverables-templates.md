# Plantillas de entregables — AIMS ISO 42001

Plantillas listas para llenar. Encajan con el estilo de entregables que el agente
CPMAI ya produce (workbook, propuesta, Go/No-Go). Destino: chat (markdown),
la carpeta de documentación del proyecto, o PDF si va a cliente final.

---

## 1. AIMS Scope Statement (Cláusula 4)

```markdown
# Alcance del AI Management System — <Organización>
**Fecha:** <ISO>  · **Versión:** v1  · **Owner:** <nombre>

## Sistemas de IA dentro del alcance
| AISystemName | Descripción | RiskTier | AIOwner | LifecycleStage | DataSensitivityTier |
|---|---|---|---|---|---|
| ... | ... | High/Limited/Minimal | ... | Prod/Dev | PII/Sensible/Público |

## Fuera de alcance (con justificación)
- <sistema> — <por qué se excluye>

## Interfaces y dependencias
- Proveedores de modelo (APIs): <OpenAI/Gemini/...> — ver A.10
- Sistemas integrados: <CRM, WhatsApp, etc.>

## Partes interesadas y sus necesidades (Cláusula 4.2)
| Parte interesada | Necesidad/expectativa | ¿Regulatoria? |
|---|---|---|
| Usuarios finales | ... | ... |
| Reguladores | EU AI Act / LFPDPPP / ... | sí |
```

---

## 2. AI Policy (Cláusula 5 / A.2)

```markdown
# Política de IA — <Organización>
1. **Propósito y principios** — uso responsable, alineado a <valores/Trustworthy AI>.
2. **Intended use permitido** — qué SÍ. **Usos prohibidos** — qué NO.
3. **Roles** — quién aprueba, quién entrena, quién despliega (separación de deberes).
4. **Gestión de riesgo e impacto** — todo sistema pasa risk + impact assessment.
5. **Datos** — provenance, calidad, privacidad, clasificación obligatoria.
6. **Transparencia** — qué se comunica a usuarios/afectados.
7. **Monitoreo e incidentes** — umbrales, respuesta, mejora continua.
8. **Revisión** — esta política se revisa cada <N> meses por dirección.
Aprobada por: <dirección> · Fecha · Próxima revisión.
```

---

## 3. AI Risk Register (Cláusula 6)

```markdown
| ID | Sistema | Riesgo | Categoría (bias/drift/seguridad/privacidad/abuso) | Vector adversarial (MITRE ATLAS) | Likelihood | Impacto | Risk score | ¿> appetite? | Control(es) (ref Annex A) | Owner | Estado |
|----|---------|--------|---|---|---|---|---|---|---|---|---|
| R-01 | Bot de soporte | Alucinación da info falsa al usuario | safety | — | M | A | Alto | sí | Guardrail output + HITL | ... | abierto |
```
Regla §7: N=1 incidente NO se extrapola a "el sistema" sin baseline del resto.

---

## 4. Statement of Applicability (SoA) — Annex A

```markdown
# Statement of Applicability — <Organización>  (verificar IDs vs estándar)
| Área/Control | ¿Aplicable? | Justificación | Implementado | Evidencia |
|---|---|---|---|---|
| A.2 Policies | Sí | toda org necesita política de IA | Sí | doc AI Policy v1 |
| A.5 Impact assessment | Sí | sistemas afectan a personas | Parcial | 2/4 sistemas evaluados |
| A.6 Life cycle | Sí | ... | Sí | Model Cards + gates |
| A.7 Data | Sí | ... | Parcial | clasificación pendiente |
| A.10 Third-party | Sí | usa APIs de modelo | Sí | atestaciones proveedor |
| <control> | No | <no usa ese tipo de sistema> | N/A | — |
```

---

## 5. Model Card (A.6)

```markdown
# Model Card — <AISystemName>  · v<n> · <fecha>
- **Intended use:** <para qué SÍ> · **Out-of-scope:** <para qué NO>
- **Modelo/proveedor:** <OpenAI / Anthropic / modelo local / ...>
- **Datos de entrenamiento / provenance:** <fuente, fechas, licencia, sesgos conocidos>
- **Métricas de desempeño:** <accuracy/precision/recall/F1 + umbral de negocio>
- **Evaluación de fairness/bias:** <subgrupos probados, resultados>
- **Límites y modos de fallo conocidos:** <...>
- **Monitoreo en producción:** <métrica → umbral → acción>
- **Responsable (AIOwner):** <...>
```

---

## 6. Gap Assessment Report (arranque de engagement)

```markdown
# Gap Assessment ISO 42001 — <Organización> · <fecha>
## Resumen ejecutivo
<madurez actual: X% de cláusulas/controles con evidencia. Top 3 gaps.>

## Hallazgos por cláusula (4-10)
| Cláusula | Estado (Ausente/Parcial/Listo) | Evidencia hallada | Gap | Prioridad |
|---|---|---|---|---|

## Hallazgos por área Annex A (A.2-A.10)
| Área | Estado | Gap | Esfuerzo estimado |
|---|---|---|---|

## Roadmap a certificación (fases 1-6, ver annex-a-and-clauses.md)
| Fase | Entregable | Duración estimada | Dependencias |
```

---

## 7. Governance Go/No-Go Gate (integra con Go/No-Go CPMAI Fase I)

```markdown
# Governance Gate — <Proyecto>
## Insumos
- [ ] Go/No-Go CPMAI: 3 pilares de feasibility (Business/Data/Implementation)
- [ ] **AI impact assessment (A.5)** completado
- [ ] RiskTier asignado (¿es High/Prohibited bajo EU AI Act?)
- [ ] Controles mínimos del Annex A aplicables identificados
- [ ] Foundation model: responsabilidad y evidencia de proveedor claras (A.10)
## Decisión
**GO** solo si feasibility valida Y el impact assessment no arroja riesgo
inaceptable sin mitigación. Si RiskTier=Prohibited → **Kill**. Si riesgo alto
mitigable → **GO condicionado** a controles X antes de prod.
```

---

## 8. AI Incident Response Plan (Cláusula 10)

```markdown
# Plan de Respuesta a Incidentes de IA — <Organización>
## Categorías (propias de IA, además de seguridad clásica)
- Fairness violation · Hallucination dañina · Drift fuera de umbral · Fuga de
  datos via modelo · Uso fuera de intended use · Comportamiento de agente fuera
  de autonomy boundaries
## Flujo
1. Detección (alarma de umbral / reporte humano) → 2. Triage + clasificación →
3. Contención (rollback de modelo / deshabilitar endpoint) → 4. Notificación
   (incl. **serious incident al regulador** si EU AI Act aplica, con plazo) →
5. Root cause (audit trail) → 6. Acción correctiva (nonconformity) → 7. Lección
   a la mejora continua.
## Tiempos objetivo
| Severidad | Contención | Notificación |
|---|---|---|
| Crítica | <T> | <plazo regulatorio> |
```
