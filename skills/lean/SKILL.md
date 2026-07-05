---
name: lean
description: >-
  Aplica Lean (eliminar muda/desperdicio) a vibecoding + infra: PREVIENE acumulación al
  construir (reuse-before-create, YAGNI, right-size, delete-as-feature) y BARRE lo ya acumulado
  (imágenes/volúmenes/logs Docker, disco/logs/cron Linux, código/deps muertos, sprawl de docs y
  contexto) con detección read-only + remediación SIEMPRE confirm-gated (nunca auto-destructivo).
  Trigger: el usuario pide "limpiar/reducir bloat", "esto se está acumulando", "hazlo lean", disco
  llenándose, "demasiados procesos/datos", housekeeping, o ANTES de declarar un build hecho.
  NO duplica un chequeo de salud/status — éste ataca DESPERDICIO.
---

# lean — eliminar muda en vibecoding + infra

## Principio (Lean / TPS, Ohno 1988)
**Lean = maximizar valor, eliminar muda (desperdicio).** La **resta es un entregable**, no una pérdida.
El desperdicio #1 aquí es **sobreproducción**: generar el artefacto pesado por default (código
especulativo, deps que no uso, docs que nadie lee, manuales en cada cierre). Encadena con
un gate de feedback antes de construir — el gate decide SI construir; este skill decide cuánto, y limpia lo que ya sobra.

## Las 7 mudas → cómo se ven en NUESTRO trabajo (checklist mental)
(Lean Software Development, Poppendieck 2003 · Google SRE "toil")
1. **Sobreproducción / extra features** → código/feature no pedido (YAGNI lo mata).
2. **Inventario / partially-done** → ramas/PRs sin mergear, código sin desplegar.
3. **Sobre-procesamiento** → más ceremonia/precisión que el valor (over-engineering en avance trivial).
4. **Esperas / handoffs** → pasos bloqueados, syncs redundantes.
5. **Task-switching** → contexto disperso (también del LLM: "context rot").
6. **Defectos** → rework por no verificar (lo ataca `/refutar` + `/premortem`).
7. **Relearning** → re-descubrir lo ya sabido (memory mal indexada).
+ **Toil (SRE)**: trabajo manual·repetitivo·automatizable·sin valor perdurable·que escala lineal → automatizar o eliminar la fuente.

---

## MODO 1 — PREVENIR (al construir, antes de declarar hecho)
Checklist de 20 segundos. Cada "no" es muda evitada:
- [ ] **Reuse-before-create** — ¿ya existe esta función/archivo/script? Reusar > crear (DRY, Pragmatic Programmer 1999). El LLM tiende a crear nuevo en vez de reusar (GitClear: copy-paste 8.3%→12.3% 2021-24; *evidencia mixta, ver §7*).
- [ ] **YAGNI** — ¿lo necesito AHORA o "por si acaso"? Sin demanda real → no se construye (Beck/Fowler).
- [ ] **Right-size el artefacto** — ¿el output pesado (manual, reporte, dashboard) lo va a leer alguien? Si no → memory/una línea. (Ver gate 0.0 de `document-progress`.)
- [ ] **Cero deps especulativas** — ¿la librería existe y la uso? Verificar antes de instalar (slopsquatting: LLMs alucinan 5.2-21.7% de nombres de paquete — USENIX 2025).
- [ ] **Delete-as-a-feature** — ¿qué puedo BORRAR al cerrar esto? Negative-LOC es valor.
- [ ] **Doc solo el "por qué"** — no dupliques en prosa lo que el código ya dice (sprawl + se pone stale).
- [ ] **Rule of Three** — no abstraigas hasta la 3ª repetición (Sandi Metz: "duplicación > la abstracción equivocada").

## MODO 2 — BARRER (auditoría de acumulación, read-only → propone, NO ejecuta)
⚠ **GATE DURO:** detectar es autónomo; **remediar destructivo (prune/rm/autoremove/vacuum/-delete) JAMÁS sin
confirm del usuario** (regla global: disco>85% → sugerir, NO `rm`/`prune` solo). Presenta el comando
exacto, el usuario aprueba. En SSH remoto usa `timeout` para no colgar la sesión.
- **Auto-identifica el host** (`hostname`/`hostname -I` en CADA probe) — nunca atribuyas muda por orden de salida (experiencia de campo: es fácil reportar la muda del host equivocado).
- **2 ejes SEPARADOS, no los confundas:** presión de disco (`df %`, urgencia solo >80%) vs reclamable (muda, valor). **Sin presión + host de cliente → acción mínima o diferir** ("no hacer nada" > "sweep pesado" en un host de cliente sin presión; la cantidad reclamada NO manda, el riesgo/toil sí).
- **Completitud de flota:** barre todos tus hosts; si uno no resuelve en `~/.ssh/config`, **decláralo INALCANZABLE — no fabriques su estado ni intentes acceso no configurado** (§7).
- **Mide la muda EN VIVO, no la deduzcas de la regla/política/doc.** La norma dice *dónde debería* estar la muda ("este host solo corre X", "los servicios internos van aparte"); la realidad diverge (experiencia de campo: aserté "poca superficie de crons en un host" sin leer el crontab → tenía 36, varios outbound a usuarios). Lee el estado (`crontab -l`/`df`/`docker`), no el "debería" (verificación en vivo + §7).

### Docker  (`ssh tu-host 'timeout 20 docker system df -v'`)
| Muda | Detección (read-only) | Remediación | ¿Destructivo? |
|---|---|---|---|
| Imágenes dangling | `docker images -f dangling=true` | `docker image prune` | SAFE |
| Containers exited | `docker ps -a -f status=exited` | `docker container prune` | leve (pierde capa rw) |
| **Volúmenes sin uso** (asesino silencioso de disco) | `docker volume ls -f dangling=true` | `docker volume prune` | **DESTRUCTIVO — borra DATA. CONFIRM.** |
| Build cache | `docker system df` (fila BUILD CACHE) | `docker builder prune` | safe-ish (rebuild lento) |
| **Logs json-file sin rotar** (unbounded por default) | `du -sh /var/lib/docker/containers/*/*-json.log` | `daemon.json`/compose `max-size:10m,max-file:3` + recrear | config safe |
- ⚠ **`docker system prune -a --volumes` puede WIPEAR DB. NUNCA en cron, NUNCA sin confirm.** Imágenes en uso por un cliente → confirm (cliente afectado = mayor umbral de revisión).
- ⚠ **El RESUMEN `docker system df` SOBRE-REPORTA "RECLAIMABLE" de imágenes — bug confirmado `moby/moby#51775`** (regresión Docker 29.0/API≥1.52, fix en 29.4.1; en un host dijo "12.34 GB 100% reclamable" con TODAS las imgs en uso). La señal REAL = `docker system df -v` columna **CONTAINERS** (≥1 = en uso). Para build cache, el reclaimable del resumen **SUB-cuenta** (solo privado; `docker builder du` = privado+compartido, `moby/moby#48523`) → prune libera ≥ esa cifra. NO confíes en el % del resumen.
- **Prevenir > limpiar (build cache):** se re-acumula (caso real: 18 GB en 925 capas). En hosts afectados, capa en la fuente: BuildKit GC (`daemon.json` `builder.gc` — **verifica versión + config actual ANTES**, no copy-paste) o `builder prune` periódico. ⚠ editar daemon + `restart docker` = client-facing → **confirm**.
- **🧹 SOP `docker builder prune` en host de CLIENTE** (verificado vs Docker docs: NO toca containers vivos / imágenes en uso / volúmenes / bind mounts / datos): (1) pre-flight `free -m` (headroom RAM); (2) `timeout 300 docker builder prune -f` (conservador: `--filter "type!=exec.cachemount"` si dudas de cache mounts — borrarlos afecta velocidad, no correctitud); (3) **NUNCA cancelar / Ctrl-C** — interrumpirlo CUELGA dockerd y exige `restart` = rebota TODOS los containers del cliente (`moby/buildkit#4399`); (4) `df -h /` antes y después para el reclaim real. ⚠ **NO** confundir con `system prune -a --volumes` (ese SÍ borra data). Sigue confirm-gated.

### Linux / disco / logs  (`ssh tu-host 'df -h / && du -sh /var/* | sort -rh | head'`)
| Muda | Detección | Remediación | ¿Destructivo? |
|---|---|---|---|
| apt cache | `du -sh /var/cache/apt` | `apt-get clean` | leve (re-descargable) |
| deps huérfanas | `apt-get autoremove --dry-run` | `apt-get autoremove` | **CONFIRM (borra paquetes)** |
| kernels viejos | `dpkg -l 'linux-image-*'\|grep ^ii` | `autoremove --purge` | **CONFIRM — nunca el `uname -r` actual** |
| journald | `journalctl --disk-usage` | `--rotate && --vacuum-size=500M`; durable: `journald.conf.d SystemMaxUse=` | **CONFIRM** (valores de ejemplo, dimensiona al disco) |
| logs app | `logrotate -d` (debug, no rota) | entry en `/etc/logrotate.d/` (`maxsize`,`rotate`,`compress`,`copytruncate`) | config safe |
| `.jsonl`/`.log` append-forever | `find /path -name '*.log' -mtime +30` | `find … -mtime +30 -delete` (corre SIN `-delete` 1º) | **CONFIRM** |
| cron solapado (dur > intervalo) | `time script` vs intervalo | wrap `flock -n /var/lock/x.lock` | safe |

### Código / deps muertos
| Muda | Detección | Counter |
|---|---|---|
| Código muerto | `vulture .` (Py) · `npx knip` (TS, unused exports/files) | borrar |
| Clones / copy-paste | `jscpd ./src` · churn `git log --numstat` | DRY / reuse |
| Deps sin uso | `deptry .` (Py) · `depcheck`/`knip` (JS) | quitar + pin |

### Docs / contexto / proceso
- **Doc sprawl** → manuales/reportes que nadie lee. Detección: ¿se referenció en 30d? Counter: borrar/fusionar.
- **Context rot** → `CLAUDE.md`/`.md` inflados degradan AL PROPIO agente (Chroma 2025; "lost in the middle" Liu 2023). "Más reglas ≠ mejor": podar. Just-in-time > front-load.
- **Proceso** → syncs/pasos redundantes en runbooks. Counter: saltar pasos cuyo input no cambió. **PERO** gates de seguridad/persistencia = músculo, no se tocan.
- **Zombie sano (automatización viva sin valor)** → un cron/job que corre PERFECTO (loguea, envía 3/3, status OK) pero produce **cero valor** — ej. un cliente de reportes diarios: útil las primeras 26 corridas, luego **14 días seguidos mandando audio vacío** a 3 personas; una auditoría de zombies lo marcaba `OK` porque su definición de zombie = roto (archivo faltante/log muerto/endpoint 404), NO "vivo pero inútil". Counter: **revisión humana periódica** de los crons *outbound-a-humanos* (briefs/reports/digests) — "¿esto sigue sirviendo?". Ojo: **vacío/0 puede ser silencio CORRECTO**, no muerte (una alerta "0 hoy" un día sin incidentes; un bot silenciado en horario laboral) → distínguelo con **baseline**, no por el valor crudo. ❌ **NO** detector keyword de "output vacío" (whack-a-mole: ≥4 frases ya — "0 groups"/"minimal"/"No messages"/numérico "0 logins"/sin-log — caza el molde de ayer, ciego al siguiente; mismo anti-patrón que fiscalizar solo el cierre/síntoma). ❌ **NO** flag genérico "output idéntico N días" (falso-positivo estructural: para healthchecks el output idéntico ES salud). ❌ **NO** añadir un vigía reflejo nuevo por cada falso negativo. Automatizar solo al **3er caso** (Rule of Three) y con la señal correcta (payload trivial en crons outbound-tagged), no antes.

---

## Errores a NO cometer
- ❌ Ejecutar `prune`/`rm`/`autoremove`/`vacuum`/`-delete` autónomo. SIEMPRE confirm.
- ❌ Cortar músculo: backup auto-memory, audit de secrets, healthchecks, gates de verificación NO son muda.
- ❌ Que el propio output de este skill sea sobreproducción: reporta el barrido en una tabla escaneable, no un manual.
- ❌ Confundir con `/status` (salud/up-down) — éste ataca DESPERDICIO/acumulación.
- ❌ `du`/`ncdu` recursivo sin acotar sobre dirs gigantes (regla OOM CLAUDE.md): `| head`, `timeout`.

## §7 — Honestidad de la evidencia
- 7 mudas (Poppendieck 2003), toil (Google SRE book), YAGNI/DRY/Rule-of-Three (Beck·Pragmatic Programmer 1999·Sandi Metz 2016): **canónicos verificados**.
- Slopsquatting 5.2-21.7% (USENIX 2025, arxiv 2406.10279) · context-rot (trychroma 2025) · "lost in the middle" (arxiv 2307.03172): **verificados**.
- GitClear copy-paste/churn: primario, **pero la evidencia de "IA duplica más" es MIXTA** (otro estudio halló lo contrario) → no sobre-afirmar.
- DORA −1.5%/−7.2% throughput/stability: **secundario** (cita del PDF, no landing). "Pinboard negative-LOC" quote: **[unverified]**.

## Referencias
Skills hermanos: `document-progress` (right-size de docs), `/refutar` y `/premortem` (falsación de supuestos).
