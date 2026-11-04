---
name: e2e
description: >-
  Gate E2E de SALIDA del embudo (sprint, paso 6, Definition of Done): verificación
  end-to-end por tipo de tarea (deploy/infra, API, bot de mensajería, cambio de BD,
  workflow, code fix) que toca el TRUTH-MAKER y no un proxy — fila en la BD, no "200 OK";
  el handler en el log, no "el workflow se activó" — con control NEGATIVO cuando la falla
  sería silenciosa o cara. Dispara con "/e2e", "verifica end-to-end", "¿ya quedó?",
  "antes de declarar listo", o cuando sprint llega a la fase DONE. Gate DURO: nunca
  declarar "listo" sin él; si solo puedes tocar el proxy, reporta "no verificado,
  last-known". DISTINTO de refutar (ataca el CLAIM de éxito después; e2e verifica el
  FLUJO).
---

# /e2e — verificación end-to-end antes de declarar "listo"

Corre la verificación end-to-end para la tarea indicada.

## Principio rector: prueba el TRUTH-MAKER, no un proxy (anti-Gettier)

Antes de declarar "listo", pregúntate: **¿estoy verificando el *truth-maker* (el
mecanismo que hace cierto el claim) o un *proxy* correlacionado con él?** "Corrió / se
ve bien / CI verde / grep 0 / el demo pasó" es una creencia **verdadera y justificada**,
NO conocimiento: la justificación no rastrea el mecanismo y puede pasar por la razón
equivocada (verdad por suerte = trampa Gettier). Cada check de abajo existe para tocar el
truth-maker, no la superficie: reserva → **fila en la BD**, no "200 OK"; mensaje → **el
handler correcto lo procesó en el log**, no "el workflow se activó"; la cita agendada por
la IA → **medida de verdad**, no "se ve bonito". Pega más fuerte en **código vibecoded**
(un LLM lo escribió, tú no lo entiendes, y "se ve bien" es justo el proxy más seductor).
Si solo puedes tocar el proxy, di **"no verificado, last-known"**, no "listo".

### El verde debe ser APTO: control negativo

Tocar el truth-maker no basta si el verde **pasa por suerte**. Un test que también
pasaría con el código ROTO no prueba nada (accuracy sin aptness = un "test Gettier").
**Cuando la falla sería silenciosa o cara, corre un control NEGATIVO**: rompe a
propósito (quita el fix, mete el input malo) y confirma que el check **FALLA**. Solo así
el verde está *causado por* la corrección y no por coincidencia. Ejemplos: validar un
cambio de locking corriendo SIN el lock → debe PERDER; probar un detector con el caso
que NO debe matchear. **No es mutation-testing de todo el repo**: es UN control negativo
donde el riesgo lo amerita. Esto vive en el razonamiento, no en un hook: juzgar si un
verde es apto es juicio, no señal de comando.

## Checklist por tipo de tarea

### Deploy / infra
```bash
curl -s -o /dev/null -w "%{http_code}" https://<endpoint>            # debe ser 2xx
ssh <servidor> "docker inspect --format='{{.State.Health.Status}}' <contenedor>"  # debe ser "healthy"
ssh <servidor> "docker logs --tail 5 <contenedor> 2>&1" | grep -i error           # debe estar vacío
```

### API
Manda una petición REAL con datos reales. Verifica que el JSON de respuesta trae los
campos y valores esperados, no solo que el status sea 2xx.

### Bot de mensajería (Telegram, WhatsApp, etc.)
Manda un mensaje real por el canal. Verifica que la respuesta llega. Revisa el log del
webhook: el handler correcto lo procesó.

### Cambio de base de datos
```sql
SELECT count(*) FROM <tabla> WHERE <condición>;  -- ANTES y DESPUÉS
```

### Workflow (n8n o similar)
Manda un mensaje real por el canal y luego verifica la última ejecución:
```bash
# La última ejecución debe tener node_count > 0 y duración plausible (no un no-op instantáneo)
curl -s -H "Authorization: Bearer <token>" "https://<n8n-host>/api/v1/executions?workflowId=<id>&limit=1"
```

### Code fix
1. Reproduce las condiciones originales del bug.
2. Confirma que el bug ya no ocurre.
3. Verifica que la funcionalidad adyacente sigue funcionando.

## Reporte

Reporta los resultados como tabla pass/fail. **NO declares "listo" si algún check
falla.** Si rompiste algo nuevo, revierte y arregla limpio: no parches encima, porque tu
modelo mental del sistema estaba mal.
