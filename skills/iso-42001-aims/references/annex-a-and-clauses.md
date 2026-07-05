# ISO/IEC 42001:2023 — Cláusulas 4-10 + Annex A (scaffold de trabajo)

> ⚠ **§7 — Esto es un SCAFFOLD, no el estándar.** El texto autoritativo y los IDs
> exactos de los controles viven en el estándar comprado ISO/IEC 42001:2023.
> Úsalo para estructurar el trabajo y conversar con el cliente; **verifica cada
> ID/título de control contra el documento real antes de entregar o de armar la
> Statement of Applicability final.** No presentes estos números como verbatim
> del estándar si no los confirmaste.

## Cláusulas de requisitos (4-10) — qué exige cada una

Las cláusulas 4-10 son los **requisitos certificables** (lo que el auditor
verifica). Siguen el ciclo PDCA de Annex SL, idéntico en estructura a ISO 27001/
9001.

| Cláusula | Tema | Qué debe existir (evidencia que busca el auditor) |
|---|---|---|
| **4** Context of the organization | Contexto + alcance | Issues internos/externos, partes interesadas y sus necesidades, **alcance del AIMS** documentado, el AIMS establecido |
| **5** Leadership | Liderazgo | **AI policy** aprobada por dirección, roles/responsabilidades/autoridades asignados, compromiso demostrable |
| **6** Planning | Planeación | Acciones para riesgos y oportunidades, **AI risk assessment + AI impact assessment** (A.5), objetivos del AIMS, planes de cambio |
| **7** Support | Soporte | Recursos, competencias, awareness, comunicación, **información documentada** (control de documentos) |
| **8** Operation | Operación | Control operacional del **ciclo de vida de IA**, ejecución del risk treatment, gestión de impactos |
| **9** Performance evaluation | Evaluación | Monitoreo/medición, análisis, **internal audit**, **management review** |
| **10** Improvement | Mejora | **Nonconformity** + acción correctiva, mejora continua |

Notas operativas:
- Cláusula 6 es donde vive el **risk assessment** Y el **AI impact assessment**
  (distinto del 27001: 42001 exige evaluar el impacto sobre **individuos y
  sociedad**, no solo sobre la organización).
- Cláusula 9 (internal audit + management review) es lo que muchos clientes
  olvidan: la gobernanza necesita un **ciclo de revisión por dirección**, no solo
  controles técnicos.

## Annex A — áreas de control (para la Statement of Applicability)

El Annex A lista **objetivos de control y controles** de referencia (~38
controles en ~9 áreas, **A.2–A.10**). En la SoA, para cada control declaras:
*aplicable / no aplicable*, justificación, y estado de implementación.

| Área | Tema | Foco del control |
|---|---|---|
| **A.2** | Policies related to AI | Existencia, aprobación, revisión y comunicación de políticas de IA |
| **A.3** | Internal organization | Roles, responsabilidades, reporte de inquietudes (concerns) |
| **A.4** | Resources for AI systems | Datos, herramientas, cómputo, recursos humanos, documentación de recursos |
| **A.5** | Assessing impacts of AI systems | **AI impact assessment**: a individuos, grupos y sociedad; consecuencias potenciales |
| **A.6** | AI system life cycle | Objetivos responsables de diseño, desarrollo, verificación, deployment, operación, **Model Cards**, retiro |
| **A.7** | Data for AI systems | Provenance, calidad, preparación, governance de datos a lo largo del ciclo |
| **A.8** | Information for interested parties | Transparencia: documentación e info para usuarios/afectados del sistema de IA |
| **A.9** | Use of AI systems | Uso responsable conforme a intended use; uso no permitido |
| **A.10** | Third-party & customer relationships | Asignar responsabilidades en la cadena de suministro de IA (proveedores de modelo, datos, customers) |

> Los títulos de área son estables y útiles para estructurar; **los controles
> individuales dentro de cada área (p.ej. "A.6.2.x") cámbialos solo tras
> verificar contra el estándar.**

## Cómo mapear A.x a las 6 fases CPMAI (resumen accionable)

- **A.5 (impact)** → Fase I, junto al Go/No-Go. ¿A quién afecta y cómo?
- **A.7 (data)** → Fases II-III (el 80% del esfuerzo CPMAI).
- **A.6 (life cycle)** → Fases IV-VI + Model Cards.
- **A.9 (use)** → Fase VI: el sistema se usa solo para su intended use.
- **A.8 (info to parties)** → transversal: transparencia al usuario final.
- **A.10 (third-party)** → quién responde por el foundation model (ver
  `control-translation.md`).
- **A.2-A.4 (policies/org/resources)** → nivel organización, no por proyecto.

## Secuencia de un engagement de certificación (para roadmap de cliente)

1. **Gap assessment** — estado actual vs cláusulas 4-10 + Annex A. Entregable:
   reporte de gaps priorizado.
2. **Scope + AI policy + roles** (Cláusula 4-5).
3. **Risk + impact assessment** (Cláusula 6 + A.5) → **Statement of
   Applicability**.
4. **Implementar controles** (Annex A aplicables) + documentar (Cláusula 7-8).
5. **Internal audit + management review** (Cláusula 9). Correr el AIMS ≥3-6
   meses con evidencia.
6. **Stage 1 audit** (revisión documental) → **Stage 2 audit** (implementación)
   por *certification body* acreditado → **certificado**.

"Conforme/listo-para-auditoría" se alcanza en el paso 5. **Certificado** solo
tras el paso 6.
