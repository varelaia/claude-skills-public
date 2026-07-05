# Traducción de controles — AWS → stack self-hosted

El blueprint AWS usa servicios gestionados. La **función de gobernanza** es la
misma en cualquier stack; cambia la herramienta. Esta tabla traduce cada
mecanismo AWS a (a) un stack self-hosted de referencia (Docker/Traefik/Postgres/
n8n + APIs OpenAI/Gemini) y (b) un equivalente genérico self-hosted. Usa la
columna que aplique al cliente.

## Por qué esto importa (honestidad de responsabilidad)

En AWS, parte del riesgo se "transfiere" al proveedor. En self-hosted
**no hay a quién transferir la infra** — tú eres el proveedor. Y cuando se usa
una **API de modelo** (OpenAI, Gemini, Anthropic, etc.),
la integridad del foundation model la gobierna **ese proveedor**, así que la
evidencia de tercero sale de **su** portal de compliance (OpenAI/Anthropic/
Google), NO de AWS Artifact. Documenta esto en la SoA.

## Tabla maestra de traducción

| Función de gobernanza | AWS (referencia) | Stack self-hosted | Notas |
|---|---|---|---|
| Inventario de activos de IA | Resource Explorer + Config | Registro propio: tabla `ai_systems` en Postgres + `inventory.json` | Una fila por cada bot, agente de IA y sistema interno |
| Aislamiento de entornos | Organizations + Control Tower (OUs) | Separación por servidor + redes Docker + entornos (dev/prod) | Requisito básico de hardening de red |
| Historial de configuración | AWS Config | `docker inspect` snapshots + git de compose/configs + `git log` | Versionar compose y `.env.example` (NUNCA secretos) |
| Policy-as-code / enforcement | Service Control Policies | CI gates + hooks pre-commit + IAM de servidores | Hooks pre-commit para bloquear secretos antes del commit |
| Separación de deberes | IAM Identity Center + permission boundaries | Usuarios SSH por rol + permisos de deploy restringidos | Quien entrena/edita ≠ quien hace deploy a prod |
| Guardrails de contenido | Bedrock Guardrails + Automated Reasoning | Guardrails de prompt + filtros de output + sanitización de URLs generadas | El LLM nunca controla URLs; strip + whitelist por código |
| Clasificación de datos | Amazon Macie | Script de clasificación + `DataSensitivityTier` por tabla/dataset | Marcar PII (pacientes, biometría, datos sensibles) explícito |
| Cifrado | AWS KMS | TLS (Traefik v2.11) + cifrado en reposo de DB + secrets en `os.environ` | Nunca hardcodear tokens (regla dura) |
| Detección de drift/quality | SageMaker Model Monitor / Clarify | Job de evaluación programado (cron + flock) que loguea métricas a Postgres/JSONL | Cron duration < interval + `flock` (evitar solapamiento de jobs) |
| Monitoreo de seguridad | GuardDuty / CloudTrail | Logs nginx + auditoría de procesos/zombies + alert_queue + bots de monitoreo | Un canal de alerta por dominio/servicio |
| Audit trail tamper-evident | CloudTrail + Config | Logs append-only (JSONL) + git inmutable + `evidence_log_path + sha256` | Hash sha256 sobre evidencia (anti-fabricación) |
| Gates de deploy con sign-off | CodePipeline + Model Registry | Checks de deploy + pruebas e2e + sign-off humano antes de prod | E2E obligatorio antes de marcar "done" |
| Versionado/registro de modelos | SageMaker Model Registry | Tabla de versiones + Model Card en repo por sistema | Ver plantilla Model Card en deliverables |
| Remediación automatizada | Step Functions (rollback/disable) | Script de rollback (`docker compose` a tag previo) + kill-switch | Define por política qué se auto-resuelve vs qué requiere confirmación |
| Incident response de IA | Systems Manager Incident Manager | Runbook + log de overrides + escalamiento al responsable/on-call | Plazos EU AI Act si aplica al cliente |
| Human-in-the-loop / feedback | Ground Truth + Evidently | Revisión humana (gates de visión/contenido) | Reasoning traces de agentes = logs de tool-use |

## Foundation model: de quién es la responsabilidad

La columna "Sistema" es un ejemplo; sustituye por tus sistemas reales.

| Tipo de sistema (ejemplo) | Modelo / proveedor | Quién gobierna integridad del modelo | Evidencia de tercero a citar |
|---|---|---|---|
| Bot/asistente de voz | OpenAI Realtime + Whisper + TTS | OpenAI | OpenAI trust/compliance portal |
| Fallback de voz | OpenRouter (varía) | El proveedor ruteado | Verificar por modelo concreto |
| Bots de mensajería | Gemini / OpenAI / Anthropic | Cada proveedor | Portal del proveedor usado |
| Biometría (self-hosted) | Modelo de visión local (ONNX) | **Tú** (modelo local) | N/A — generas la evidencia tú |
| Agentes internos | Anthropic | Anthropic | Anthropic trust center |

**Implicación para la SoA:** para los modelos via API, el control de "integridad
del base model" se marca como *gestionado por el proveedor + verificación de su
atestación*. Para modelos self-hosted (p.ej. un modelo de visión local), tú asumes el
control completo: bias testing, versionado y provenance del modelo son
responsabilidad propia.

## Anti-patrón

No copies nombres de servicio AWS a un entregable de cliente no-AWS ("usa Bedrock
Guardrails") — traduce a la función ("guardrails de output: filtro de PII +
whitelist de URLs por código"). El auditor evalúa que el **control existe y
funciona**, no la marca de la herramienta.
