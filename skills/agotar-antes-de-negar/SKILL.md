---
name: agotar-antes-de-negar
description: >-
  Use ANTES de declarar que algo "no existe / no es posible / no está disponible" —
  especialmente una capacidad técnica (modelo, endpoint, flag, feature) — y SIEMPRE
  que el usuario dispute esa negación con conocimiento directo (documentación propia,
  experiencia previa, "sé que sí"). Triggers: vas a decir "no se puede", "no existe",
  "no está disponible", "confirmado que no", o el usuario ya te contradijo una vez
  sobre una negación tuya. El trap que cazó esto: declarar una ausencia "verificada"
  tras UN solo método de prueba (una búsqueda, un endpoint, un nombre), con lenguaje
  de certeza ("confirmado", "conclusión funcional"), cuando quedaban métodos sin
  probar — y el usuario tenía razón las 3 veces que insistió (s-2026-10-25,
  Grok Imagine en OpenRouter: existía, el error fue mío en 3 capas distintas).
---

# Agotar antes de negar

## Principio
Una negación ("esto no existe / no se puede / no está disponible") exige el MISMO
rigor que una afirmación positiva — normalmente más, porque es más fácil fallar por
omisión (no probé la forma correcta) que por comisión (inventé un dato). "Lo busqué
y no lo encontré" no es lo mismo que "no existe". Son afirmaciones distintas y solo
la primera es la que de verdad verificaste.

## La regla de hierro
**Antes de declarar una ausencia con lenguaje de certeza, agota ≥2 métodos de
verificación independientes — no la misma búsqueda con más confianza.** Métodos
independientes de verdad (no variaciones del mismo):
1. Catálogo/metadata oficial de la fuente (ej. listado de modelos) — pero solo
   prueba lo que ese catálogo decide registrar, no todas las formas de accederlo.
2. Llamada real (POST/GET) con el nombre/parámetro más probable — pero un nombre
   equivocado da un falso negativo indistinguible de "no existe".
3. **Endpoint o forma de acceso alternativa** — el mismo recurso puede estar vivo
   por una ruta y muerto por otra (s-2026-10-25: `chat/completions` con
   `modalities` devolvía 404 "sin endpoints"; `/images/generations` con el mismo
   modelo devolvió 200 y una imagen real).
4. Documentación propia/del usuario y una búsqueda web fresca — si el usuario
   dice "está documentado en X", leer X ANTES de reafirmar la negación, no después.

Declarar cierre tras UN solo método — aunque ese método sea datos estructurados
reales (ej. metadata de API) — es la falla. Los datos eran reales; la generalización
("esto prueba que NO existe NINGUNA forma de usarlo") fue el error, no el dato.

## La señal que vale más que tu propia verificación
**Cuando alguien con conocimiento directo (documentación que ya leyó, experiencia
previa, acceso que tú no tienes) disputa tu negación — eso es evidencia, no ruido.**
No lo proceses como "insistencia a ignorar con más cortesía". Procésalo como: *mi
método de verificación tiene un hueco que no he encontrado todavía*. Sube el nivel
de búsqueda (prueba el método 3 y 4 de la lista) en vez de repetir el método 1-2 con
mejor redacción. Si el usuario insiste una SEGUNDA vez tras tu "verificación en
vivo" — para ahí. Eso ya no es tozudez suya, es información que no estás usando.

## Lenguaje: cierra solo lo que de verdad cerraste
- ❌ "Confirmado que no existe" / "Conclusión funcional: no es posible" — tras un
  solo método, esto afirma más de lo que probaste.
- ✅ "No lo encontré probando [métodos 1 y 2] — todavía no probé [3 y 4]."
- ✅ "Esto confirma que [la ruta A] no lo sirve. No confirma que ninguna ruta lo sirva."
Un catálogo/metadata que dice "esto solo da texto" describe UN modo de acceso, no
el universo de modos de acceso. No conviertas "no por este camino" en "no existe".

## Caso de origen (s-2026-10-25, Varela Insights / generación de imágenes)
Usuario pidió usar Grok vía OpenRouter. Claude dijo "no tiene modelo de imagen"
(memoria de 5 semanas + búsqueda por substring `'image'` que no capturaba
`'imagine'` — bug silencioso). Usuario insistió 3 veces. Cada vez Claude SÍ
investigó más (buena fe, no pereza) pero cerró con certeza prematura:
1ª negación: búsqueda de catálogo con bug de substring → "no existe".
2ª negación: nombres de modelo adivinados (`grok-imagine-2.0`, `-q`, etc., todos
  incorrectos) + metadata `output_modalities` de TODO el catálogo (dato real) →
  "confirmado, dato estructurado, no por falta de investigación" — pero nunca
  probó el endpoint `/images/generations`, solo `/chat/completions`.
3ª insistencia del usuario → WebSearch reveló el nombre real
  (`grok-imagine-image-quality`) → probado en `/images/generations` → HTTP 200,
  imagen real generada. **Existía. El usuario tenía razón las 3 veces.**
Lección adicional: aun así, ese endpoint NO preservó la identidad de la persona
en la foto de referencia (prueba real lo reveló) — la capacidad tenía un límite
real, solo que no era el límite que Claude había declarado.
