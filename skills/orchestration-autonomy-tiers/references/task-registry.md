# Registro vivo de tareas → nivel de autonomía

`task_type` = la clave estable que va al ledger de medición. Sembrar con las
tareas más frecuentes del equipo (evidencia: git log + crons + tickets),
clasificadas con las 4 preguntas de riesgo, al **nivel honesto de hoy** (como ya
se operan). El **techo** es determinista por riesgo. La columna *validación* =
corridas en el ledger que respaldan ese nivel — parte de 0: el nivel inicial es
**baseline por juicio**, y el ledger lo confirmará o corregirá con datos reales.
Actualiza esta tabla cuando una tarea se promueva/demueva.

Leyenda touch: 🟢 infra interna · 🟡 producción propia · 🔴 cliente/externo/fiscal/familia.

## Top tareas frecuentes (starter)

| task_type | Reversible | Touch | Techo | Hoy | Validación | Regla que lo fija |
|---|---|---|---|---|---|---|
| `content_publish` | parcial | 🔴 ext/marca | **T1** | T1 | 0 — baseline | publicación externa = freno; confirm go-live |
| `social_amplification` | no | 🔴 ext/marca | **T1** | T1 | 0 — baseline | posted=posted + riesgo de marca; confirm antes de publicar a redes |
| `agent_skill_authoring` | sí | 🟢 | **T2** | T1 | 0 — baseline | interno+reversible, pero pasa gate harness + política antes de confiar |
| `crawler_report` | sí | 🟢 | **T2** | T2 | 0 — baseline | read+report, sin mutación |
| `msg_campaign_send` (WhatsApp/CRM) | no | 🔴 cliente + plataforma | **T1** | T0 | 0 — baseline | irreversible + cliente + reglas de plataforma (ventana 24h, opt-out); jamás auto |
| `client_report_export` | sí | 🔴 cliente(read) | **T2** | T1 | 0 — baseline | genera reporte (no muta cliente), pero suele entregarse al cliente → confirm |
| `lead_osint_research` | sí | 🟢 | **T2** | T2 | 0 — baseline | lectura de datos ya recolectados; sin side-effects externos |
| `invoice_emit` (fiscal) | no | 🔴 fiscal | **T1** | T0 | 0 — baseline | emisión fiscal irreversible; gate anti-emisión-errónea; jamás auto |
| `infra_container_restart` | sí | 🟢 | **T2** | T2 | 0 — baseline | "exited → start sin confirm". No-destructivo, data persistente |
| `backup_job` | sí (additivo) | 🟢 | **T2** | T2 | 0 — baseline | cron; no-destructivo |

**Verificación de coherencia (sembrado):** ninguna tarea está hoy por encima de
su techo. Las irreversibles/sensibles (`msg_campaign_send`, `invoice_emit`)
arrancan en T0 con techo T1 — nunca llegan a auto.

## Otras tareas candidatas (ejemplos)

| task_type | Reversible | Touch | Techo | Hoy sugerido | Nota |
|---|---|---|---|---|---|
| `lead_outreach_send` (invites LinkedIn) | no | 🔴 externo | T1 | T1 | cuida rate limits y anti-ban; CAPTCHA → stop |
| `lead_scrape` (Google/LinkedIn vivo) | no (ban) | 🔴 externo | T1 | T1 | rotación de proxies/IP; CAPTCHA → parar 24h |
| `workflow_deploy` (n8n/similar) | sí (backup JSON) | 🟡 | T1 | T1 | deactivate→PUT→activate; restart afecta TODO |
| `service_deploy` (prod) | sí (rollback) | 🟡 | T2* | T1 | *T2 solo si rollback automático probado |
| `dns_zone_edit` | no (puede wipear) | 🔴 prod | T1 | T0 | backup + verificar registros previos |
| `client_ops` (cualquier mutación en sistema de cliente) | varía | 🔴 cliente | T1 | T0 | cliente activo; siempre confirm |
| `db_backup` | sí (additivo) | 🟢 | T2 | T2 | cron; no-destructivo |
| `container_stop`/`prune`/`rm` | no | varía | T1 | T0 | keyword destructivo → siempre confirm |

## Cómo crece este registro (CPMAI iterativo)

1. Tarea nueva → entra en **T0** por default (no probada = mínima autonomía).
2. Cada corrida limpia (success + E2E + sin nonconformity) registrada en el
   ledger suma a su racha.
3. Al llegar a N corridas limpias (T0→T1=3, T1→T2=5) y si no excede su techo de
   riesgo → el `stats` la **sugiere** para promoción. El usuario decide; al
   promover, anota aquí fecha y racha.
4. Una nonconformity → democión un nivel + `override_log.md` + resetea racha.
5. Revisión en la auditoría trimestral: ¿qué se promovió, qué se demovió, qué
   task_type nuevo apareció sin clasificar?

## Notas de coherencia con reglas existentes

- Si ya tienes una **matriz de auto-resolución de alertas** (p. ej. "container
  exited → start sin confirm", "cliente afectado → siempre confirm"), esa matriz
  es, de facto, una tabla de tiers para alertas. Este registro la **generaliza a
  todas las tareas**.
- El **techo de riesgo** implementa "outward-facing/destructivo → siempre
  confirm": esas tareas nunca cruzan a T2 por más costumbre.
- La **democión por nonconformity** implementa la idea de un kill-switch, pero
  granular (por tarea) en vez de matar todo el orquestador.
