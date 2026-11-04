---
name: spec
description: >-
  Gate SPEC del embudo (sprint, paso 2): antes de escribir CUALQUIER código, produce un
  spec de 7 campos — Qué, Por qué, Dónde, Cómo, Casos borde, Verificación, Rollback — y
  pide aprobación antes de implementar. Dispara con "/spec", "haz el spec", "especifica
  esto antes de tocar código", o cuando sprint llega a la fase SPEC. Default spec-lite (un
  markdown, una vez); sube a spec versionado (SDD pleno) solo si el build es recurrente o
  multi-sesión, hay un cliente en producción con requisito de auditoría, o 2+ personas
  tocarán el código. NO es planteamiento (define el PROBLEMA; spec define la SOLUCIÓN) ni
  clarifica-una-a-una (desambigua el ENTREGABLE; spec lo detalla ya desambiguado).
---

# /spec — definir la solución antes de tocar código

Antes de escribir CUALQUIER código, produce un spec para esta tarea:

1. **Qué**: una oración que describe qué hace este cambio.
2. **Por qué**: qué problema resuelve o qué valor agrega.
3. **Dónde**: qué archivos, contenedores o servidores se tocan.
4. **Cómo**: plan de implementación paso a paso (numerado).
5. **Casos borde**: ¿qué puede salir mal? ¿qué entradas son inesperadas?
6. **Verificación**: ¿cómo probamos que funciona? (curl, query o test ESPECÍFICO, no
   "lo probamos").
7. **Rollback**: si rompe algo, ¿cómo lo revertimos?

Escribe el spec como bloque al inicio de la tarea y **obtén la aprobación del usuario
antes de implementar**.

## Nivel del spec

- **Default: spec-lite.** Un markdown, una vez, no se versiona como artefacto vivo.
- **Sube a SDD pleno** (spec versionado = fuente de verdad que el código debe cumplir)
  SOLO si se cumple al menos uno: (a) build recurrente o multi-sesión que vivirá y
  mutará; (b) cliente en producción con requisito de auditoría; (c) dos o más personas
  tocarán el código. Si ninguno aplica, lite. El spec vivo *para todo* es ceremonia que
  grava la velocidad; su valor solo paga donde el riesgo lo justifica.

## Regla

**No omitas ninguna sección.** El spec toma 2 minutos. Arreglar una mala implementación
toma 2 horas.
