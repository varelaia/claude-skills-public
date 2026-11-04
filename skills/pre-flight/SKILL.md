---
name: pre-flight
description: >-
  Gate PRE-FLIGHT del embudo (sprint, paso 3): antes de tocar nada, verifica EN VIVO los
  supuestos técnicos sobre el sistema real — Ubicación, Tráfico, Propiedad, Método de
  deploy, Plan de rollback, Radio de daño — con comandos, no de memoria. Dispara con
  "/pre-flight", "verifica los supuestos antes", "checa dónde vive el código / cómo se
  despliega", o cuando sprint llega a la fase PRE-FLIGHT. Separa "creí que" de "verifiqué
  que". DISTINTO de premortem (imagina la falla FUTURA; pre-flight verifica el ESTADO
  ACTUAL) y de e2e (verifica el DONE al final; pre-flight verifica el terreno al inicio).
  Si alguna respuesta es "no estoy seguro", investiga antes de proceder.
---

# /pre-flight — verificar los supuestos antes de tocar nada

Antes de hacer cambios, verifica estos supuestos para la tarea indicada. Cada punto se
contesta con una **medición en vivo**, no con lo que recuerdas del sistema. Sin esto, el
premortem y el build razonan sobre un sistema imaginario.

## Checklist de supuestos

1. **Ubicación**: "El código que voy a cambiar está en ___"
   - Verifica: `wc -l <archivo>` en el host, o
     `ssh <servidor> "docker exec <contenedor> wc -l <archivo>"` si corre en contenedor.
   - Costo de asumirlo mal: editar código en el lugar equivocado (una copia, un
     bind-mount viejo, otro branch) y "desplegar" un cambio que nunca corre.

2. **Tráfico**: "Las peticiones llegan a este handler vía ___"
   - Verifica: registro del webhook, labels del reverse proxy, config de rutas.
   - Costo de asumirlo mal: el webhook apunta a otro lado y arreglas un handler que
     nadie invoca.

3. **Propiedad**: "Este componente es nuestro / de terceros"
   - Si es de terceros: lee su documentación ANTES de asumir su comportamiento.
   - Costo de asumirlo mal: `httpx` no se comporta como `requests`; el fork de
     `gunicorn` no comparte estado; Traefik v3 cambió la sintaxis de v2.

4. **Método de deploy**: "Los cambios surten efecto mediante ___"
   - bind mount → reiniciar el contenedor.
   - `COPY` en la imagen → reconstruir imagen + reiniciar.
   - Workflow (p. ej. n8n) → desactivar + actualizar + activar + reiniciar los workers.
   - Costo de asumirlo mal: reiniciar y creer que desplegaste cuando la imagen sigue
     con el código viejo.

5. **Plan de rollback**: "Si esto rompe algo, voy a ___"
   - Defínelo ANTES de ejecutar, no después.

6. **Radio de daño**: "Este cambio afecta a ___"
   - Lista TODOS los servicios, bots y clientes impactados.
   - Si afecta a más de un cliente: precaución extra (ventana, aviso, respaldo).

## Regla

Contesta cada punto explícitamente. Si CUALQUIER respuesta es "no estoy seguro",
investiga antes de proceder.
