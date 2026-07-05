# ISO 42001 sobre AWS — Implementación de referencia (cloud-native)

> Este es el blueprint AWS **completo y fiel al documento fuente**. Es UNA
> implementación de referencia, válida cuando el cliente corre en AWS. Para
> servidores self-hosted + APIs de modelo y para clientes no-AWS, traduce con
> `control-translation.md`. El núcleo certificable son las cláusulas y el Annex
> A, no los nombres de servicio.

## 1. Fundamento: integración y responsabilidad compartida

ISO/IEC 42001:2023 mueve a la **gobernanza sistémica** de IA. Por su estructura
armonizada **Annex SL**, integra nativamente con **ISO 27001** (seguridad) e
**ISO 9001** (calidad): el AIMS **extiende** registros de activos y workflows de
control de cambios existentes, eliminando fragmentación y "audit fatigue".

**AWS Shared Responsibility Model for AI** — define la frontera:

| AWS (proveedor) | Cliente (gobernanza/operación) |
|---|---|
| Seguridad física e infraestructura de los servicios de IA | **Data governance**: calidad, provenance, `DataSensitivityTier` |
| Integridad del foundation model (Bedrock, Amazon Q Business) | **Model configuration**: intended use, hyperparameters, guardrails |
| Evidencia de tercero: certificación ISO 42001 vía **AWS Artifact** (Bedrock, Q Business, Textract, Transcribe) | **Risk assessment**: impact assessments (A.5), monitoreo de bias/drift/degradación |

**Risk transfer:** usar servicios certificados ISO 42001 transfiere a AWS el
riesgo de infra y de integridad del base-model. PERO AWS solo garantiza la
disponibilidad del API — el cliente sigue siendo el único responsable de que el
**output** cumpla con políticas éticas y mandatos como el EU AI Act.

## 2. Cláusula 4 — Contexto y alcance técnico

Definir alcance es el primer requisito del AIMS. Evita *shadow AI*.

**Inventario y scoping de activos:**
- **AWS Organizations + Control Tower**: agrupar workloads de IA en cuentas
  dedicadas (Dev/Staging/Prod) → guardrails por Organizational Unit (OU).
- **AWS Resource Explorer**: descubrimiento automático de activos de IA
  cross-account/region.
- **AWS Config**: historial continuo de configuración de todos los recursos de
  IA (sin blind spots de auditoría).

```bash
# Descubrir endpoints SageMaker y agentes Bedrock en un scope
aws resource-explorer-2 search \
  --query-string "service:sagemaker type:endpoint OR service:bedrock type:agent"
```

**Tags obligatorios** (gobernanza metadata-driven): `AISystemName`, `RiskTier`
(Minimal/Limited/High/Prohibited), `AIOwner`, `LifecycleStage`,
`DataSensitivityTier` (ligado a Amazon Macie), `ComplianceFramework`
(ISO42001, EU_AI_Act). El *under-scoping* (excluir experimentación interna o
APIs de terceros) distorsiona el perfil de riesgo; el descubrimiento automático
vía Config lo previene.

## 3. Cláusula 5 — Liderazgo y enforcement de política

Compromiso de liderazgo operacionalizado en guardrails técnicos ("compliance by
design"):
- **Service Control Policies (SCPs)**: restringir despliegues a regiones
  aprobadas, bloquear servicios no conformes.
- **IAM Identity Center + Permission Boundaries**: separación de deberes. Un
  data scientist puede entrenar pero NO desplegar a producción.
- **Amazon Bedrock Guardrails + Automated Reasoning**: más allá del filtrado
  probabilístico (PII redaction, topic blocking), **Automated Reasoning** usa
  verificación formal para *probar matemáticamente* que una respuesta cumple
  conocimiento de dominio y reglas de política — caza errores factuales que los
  filtros estándar no ven.

## 4. Cláusula 6 — Risk management y threat modeling

Flujo de gestión de riesgo (multi-stage lifecycle):
1. **Identify AI Systems** — SageMaker AI, EMR, API Gateway: inventariar
   endpoints y pipelines de datos.
2. **Identify Risks** — bias, drift, exposición de datos (SageMaker AI, S3).
3. **Analyze & Evaluate** — likelihood/impacto con **MITRE ATLAS** (técnicas
   adversariales de ML).
4. **Compare** — vs **Risk Appetite & Thresholds** (CloudWatch Alarms flag
   desviaciones del baseline).
5. **Apply Controls (SoA)** — IAM, AWS KMS, Amazon Macie, Bedrock Guardrails.
6. **Continuous Monitoring** — SageMaker Model Monitor, AWS Glue Data Quality,
   CloudTrail.
7. **Feedback Loop** — SageMaker Ground Truth + CloudWatch Evidently
   (human-in-the-loop).

**Functional vs infrastructure risk:** firewalls no bastan. Un modelo puede ser
infra-seguro pero compliance-roto por bias discriminatorio. **SageMaker Clarify**
para riesgos funcionales.

## 5. Cláusula 8 — Controles de ciclo de vida (Annex A.6)

- **Orchestration gates**: AWS CodePipeline + SageMaker Pipelines fuerzan
  aprobaciones "Gate". Ningún modelo a producción sin evaluación de bias
  automatizada + sign-off manual en el **SageMaker Model Registry**.
- **Model Cards** obligatorias: provenance del training, intended use, límites.
- **Agentic AI**: **Amazon Bedrock AgentCore** gobierna *permitted tool scope*,
  *autonomy boundaries* y *reasoning traces*.
- **Shadow Testing**: SageMaker Shadow Testing valida versiones nuevas contra
  tráfico real sin impactar usuarios.
- **Dataset provenance**: AWS Glue Data Quality + SageMaker Data Wrangler mitigan
  "garbage in, garbage out" en el origen.

## 6. Cláusula 9 — Performance evaluation y monitoreo automatizado

| Categoría | Métrica | Implementación AWS | Acción |
|---|---|---|---|
| Model quality | Data/Model Drift (PSI < 0.25) | SageMaker Model Monitor | Retraining; avisar owner |
| Accuracy | vs Baseline | SageMaker AI Evaluation | Rollback si cae bajo umbral |
| Generative safety | Hallucination rate (< 5%) | Bedrock Guardrails / CloudWatch | Revisar prompts / guardrails |
| Fairness | Bias deviation | SageMaker Clarify (scheduled) | Fairness review; update risk register |
| Security | Acceso no autorizado | GuardDuty / CloudTrail | Tolerancia cero: aislar; IR |

La detección automática de drift vuelve la gobernanza una ventaja **proactiva**.

## 7. Cláusula 10 — Incident management y mejora continua

- Categorías de incidente de IA (fairness, transparencia) gestionadas vía **AWS
  Systems Manager Incident Manager** → coordina respuesta técnica + legal,
  satisface el requisito de "serious incident" del EU AI Act (planes + plazos).
- **Remediación automatizada con AWS Step Functions**: rollback automático de
  modelo ante alarma de drift; deshabilitar endpoint que cruce umbral de
  safety/bias.
- **Audit trail tamper-evident**: CloudTrail + AWS Config → root cause
  post-incidente verificable (qué cambió y cómo respondió el AIMS).

## Conclusión

Esta arquitectura AWS embebe la gobernanza en el tejido del cloud, mapeando
servicios a las cláusulas del estándar para un AIMS sostenible, auditable y
resiliente.
