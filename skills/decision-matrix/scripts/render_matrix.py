#!/usr/bin/env python3
"""
render_matrix.py — Renderiza una matriz de decisión multicriterio en Markdown.

Toma un JSON (stdin o archivo) con objetivo, criterios ponderados y opciones con
puntuaciones 1-5, y produce:
  - Tabla Markdown: cada celda = puntuación + símbolo ↑/=/↓ (vs promedio de su columna)
  - Columna final "Total ponderado" = Σ(puntuación × peso)
  - Fila final "Promedio" = promedio simple por criterio
  - Línea WINNER para que el modelo redacte la recomendación

Por qué un script: las sumas ponderadas y los promedios de columna son aritmética
que un LLM equivoca con facilidad. Aquí el cálculo es determinista; el juicio
(elegir criterios, pesos y puntuaciones) se queda en el modelo.

Uso:
    python3 render_matrix.py datos.json
    cat datos.json | python3 render_matrix.py

Schema del JSON de entrada:
{
  "objetivo": "Frase del objetivo a decidir",
  "criterios": [
    {"nombre": "Costo", "peso": 30},
    {"nombre": "Velocidad de implementación", "peso": 25}
  ],
  "opciones": [
    {"nombre": "Opción A", "puntuaciones": {"Costo": 4, "Velocidad de implementación": 3}},
    {"nombre": "Opción B", "puntuaciones": {"Costo": 2, "Velocidad de implementación": 5}}
  ]
}

Reglas:
  - Pesos en porcentaje; idealmente suman 100. Si no, el script lo AVISA y normaliza
    para el cálculo (sin alterar el JSON), para que la comparación sea justa.
  - Puntuaciones esperadas 1-5 (enteras o decimales). Fuera de rango → aviso.
"""
import json
import sys

ESCALA_MIN, ESCALA_MAX = 1, 5
EPS = 1e-9


def cargar(args):
    if len(args) > 1:
        with open(args[1], "r", encoding="utf-8") as fh:
            return json.load(fh)
    data = sys.stdin.read()
    if not data.strip():
        sys.exit("ERROR: no se recibió JSON (ni archivo ni stdin).")
    return json.loads(data)


def simbolo(valor, promedio):
    if abs(valor - promedio) < 1e-6:
        return "="
    return "↑" if valor > promedio else "↓"


def main():
    d = cargar(sys.argv)
    avisos = []

    objetivo = d.get("objetivo", "").strip()
    criterios = d.get("criterios", [])
    opciones = d.get("opciones", [])

    if not criterios:
        sys.exit("ERROR: faltan 'criterios'.")
    if not opciones:
        sys.exit("ERROR: faltan 'opciones'.")

    nombres_crit = [c["nombre"] for c in criterios]
    pesos = {c["nombre"]: float(c["peso"]) for c in criterios}

    suma_pesos = sum(pesos.values())
    if abs(suma_pesos - 100) > 0.5:
        avisos.append(
            f"Los pesos suman {suma_pesos:g}%, no 100%. Se normalizan para el cálculo."
        )
    factor = 100.0 / suma_pesos if suma_pesos else 1.0
    pesos_norm = {k: v * factor for k, v in pesos.items()}

    # Validar puntuaciones y rango
    for op in opciones:
        for crit in nombres_crit:
            if crit not in op.get("puntuaciones", {}):
                sys.exit(f"ERROR: a '{op['nombre']}' le falta puntuación para '{crit}'.")
            val = float(op["puntuaciones"][crit])
            if val < ESCALA_MIN - EPS or val > ESCALA_MAX + EPS:
                avisos.append(
                    f"'{op['nombre']}' / '{crit}' = {val:g} está fuera de la escala {ESCALA_MIN}-{ESCALA_MAX}."
                )

    # Promedio por columna (promedio simple entre opciones)
    promedios = {}
    for crit in nombres_crit:
        vals = [float(op["puntuaciones"][crit]) for op in opciones]
        promedios[crit] = sum(vals) / len(vals)

    # Total ponderado por opción
    totales = {}
    for op in opciones:
        total = sum(
            float(op["puntuaciones"][crit]) * pesos_norm[crit] / 100.0
            for crit in nombres_crit
        )
        totales[op["nombre"]] = total

    # --- Render Markdown ---
    out = []
    if objetivo:
        out.append(f"**Objetivo:** {objetivo}\n")

    encabezado = ["Opción"] + [f"{c} ({pesos[c]:g}%)" for c in nombres_crit] + ["**Total ponderado**"]
    out.append("| " + " | ".join(encabezado) + " |")
    out.append("|" + "|".join(["---"] * len(encabezado)) + "|")

    # Ordenar opciones por total descendente para lectura rápida
    opciones_ord = sorted(opciones, key=lambda o: totales[o["nombre"]], reverse=True)
    for op in opciones_ord:
        fila = [op["nombre"]]
        for crit in nombres_crit:
            val = float(op["puntuaciones"][crit])
            val_str = f"{val:g}"
            fila.append(f"{val_str} {simbolo(val, promedios[crit])}")
        fila.append(f"**{totales[op['nombre']]:.2f}**")
        out.append("| " + " | ".join(fila) + " |")

    # Fila promedio simple por criterio
    fila_prom = ["**Promedio**"]
    for crit in nombres_crit:
        fila_prom.append(f"_{promedios[crit]:.2f}_")
    fila_prom.append("—")
    out.append("| " + " | ".join(fila_prom) + " |")

    print("\n".join(out))
    print()
    print(f"_Escala {ESCALA_MIN}-{ESCALA_MAX}. Símbolo ↑/=/↓ = puntuación vs. promedio de su columna._")

    # Línea(s) máquina para que el modelo redacte la 🏆 Recomendación
    ganador = max(totales, key=totales.get)
    ordenado = sorted(totales.items(), key=lambda kv: kv[1], reverse=True)
    print()
    print(f"WINNER: {ganador} ({totales[ganador]:.2f})")
    if len(ordenado) > 1:
        segundo, val2 = ordenado[1]
        margen = totales[ganador] - val2
        print(f"RUNNER_UP: {segundo} ({val2:.2f}) | MARGEN: {margen:.2f}")
    if avisos:
        print()
        for a in avisos:
            print(f"AVISO: {a}")


if __name__ == "__main__":
    main()
