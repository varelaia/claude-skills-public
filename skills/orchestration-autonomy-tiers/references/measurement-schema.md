# Esquema de medición unificado

> Si hoy solo mides la capa autónoma (alert/worker) y tu lector de KPIs sufre
> *schema drift* entre registros viejos y nuevos (p. ej. campos renombrados,
> `KeyError` al leer), este esquema es el destino al que migrar: medir **los 3
> niveles** (T0/T1/T2), no solo el autónomo.

## Un registro por tarea orquestada (cualquier tier)

Append-only JSONL. Una línea por tarea con side-effects, sin importar el nivel.

```json
{
  "ts": "2026-06-14T12:00:00-06:00",
  "session": "<id de sesión>",
  "task_type": "container_restart",       // clave estable; ver task-registry.md
  "tier": "T2",                            // T0 manual | T1 semi-auto | T2 auto
  "agent": "orchestrator-1",              // qué agente/orquestador ejecutó
  "outcome": "success",                    // success | rework | fail
  "e2e_passed": true,                      // ¿pasó la verificación E2E del tipo de tarea?
  "confirmed_by": null,                    // "<usuario>" si T1/T0 con gate humano; null si T2
  "reversible": true,
  "touched": "infra_interna",             // infra_interna | produccion | cliente | externo | fiscal
  "tokens": 4200,                          // si disponible
  "duration_s": 18,                        // si disponible
  "nonconformity": false,                  // true → genera entrada en override_log.md
  "notes": ""
}
```

**Compatibilidad hacia atrás:** el lector debe tolerar registros legacy. Patrón
para no repetir el crash:
```python
tier   = r.get("tier")  or _infer_tier_from_legacy(r)   # nunca r["x"] directo
target = r.get("target") or r.get("agent") or "unknown"
```

## KPIs derivados (lo que reporta el stats arreglado)

| KPI | Cómo se calcula | Umbral / acción (ISO §9→§10) |
|---|---|---|
| Success-first-time por tier | `success_e2e / total` por tier | < 0.8 en T2 → revisar; demociones |
| Rework rate | `rework / total` | sube → tarea mal-asignada o agente equivocado |
| Wrong-tier events | `fail & tier==T2 & reversible==false` | > 0 → nonconformity + democión forzada |
| Right-agent-first-time | tareas sin re-delegación / total | < 0.8 → mal match patrón↔agente |
| Autonomía neta | promociones − demociones (ventana) | negativa sostenida → calidad cayendo |
| Costo/tarea por tier | media `tokens` por tier | T2 > T1 → algo está mal (auto debería ser barato) |

## Lógica de promoción/democión (motor del "se gana con datos")

```
por cada task_type:
  corridas_limpias = racha de outcome=success & e2e_passed=true & nonconformity=false
                     en el tier actual
  si corridas_limpias >= N(tier_actual) y no excede el techo de riesgo:
      promover un nivel (T0→T1→T2), resetear racha
  si cualquier registro con nonconformity=true:
      demover un nivel, escribir override_log.md, resetear racha
N sugerido: T0→T1 = 3 ; T1→T2 = 5 (más alto = más conservador)
techo: irreversible o touched∈{cliente,externo,fiscal} → máx T1
```

## Ventana de medición honesta (gotcha heredado)

Igual que en los reportes de crawlers (Regla AEO): **no midas a 24h** lo que
ocurre en ciclos de días. Para "autonomía neta" y "success-first-time" usa
ventana ≥ 7-30 días según frecuencia del task_type. Una racha de 1 día no gana
promoción; una falla aislada en una tarea madura no debe borrar meses de track
record (pero sí dispara democión + revisión — la democión es barata de revertir).

## Dónde vive (ejemplo de implementación)

Ledger: un JSONL append-only en tu ruta de logs (p. ej.
`~/.claude/logs/orchestration_ledger.jsonl`). Herramienta: un script CLI que
envuelva este esquema (E2E verificado).

```bash
# registrar una tarea al cerrarla (cualquier agente/orquestador)
python3 orchestration_ledger.py log \
    --task container_restart --tier T2 --outcome success --e2e \
    --touched infra_interna --reversible yes --agent orchestrator-1

# ver KPIs por tier + sugerencias de promoción/democión
python3 orchestration_ledger.py stats [--days N]
```

Reporta: éxito-1ra/rework/fail por tier, wrong-tier events, nonconformities
(→ `override_log.md`), y por `task_type` la racha limpia + sugerencia
promo/democión (el usuario decide, igual que un kill-switch). La promoción
respeta el **techo de riesgo** (irreversible/cliente/externo/fiscal → máx T1).

Si convive con un stats legacy de la capa autónoma, arréglale el crash por
schema drift (`KeyError` por campos renombrados) — ese stats mide la capa
autónoma, el ledger mide los 3 niveles.
