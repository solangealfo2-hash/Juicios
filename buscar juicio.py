#!/usr/bin/env python3
"""
Buscador de causas judiciales a partir de juicios.json.

Uso:
    python3 buscar_juicio.py 514
    python3 buscar_juicio.py "casa popular"
    python3 buscar_juicio.py 143 2022
"""

import json
import sys
import unicodedata
from pathlib import Path

DATA_FILE = Path(__file__).parent / "juicios.json"


def normalizar(texto: str) -> str:
    """Minúsculas y sin acentos, para comparar sin importar tildes/mayúsculas."""
    texto = texto.lower()
    texto = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in texto if not unicodedata.combining(c))


def cargar_juicios():
    with open(DATA_FILE, encoding="utf-8") as f:
        return json.load(f)


def buscar_juicio(termino: str, juicios=None):
    """
    Busca por:
    - número exacto de causa (ej. '514')
    - número + año (ej. '514 2018')
    - texto contenido en la carátula (ej. 'casa popular', nombre de una parte)
    Devuelve la lista de coincidencias.
    """
    if juicios is None:
        juicios = cargar_juicios()

    partes = termino.strip().split()
    resultados = []

    # Caso: número + año
    if len(partes) == 2 and all(p.isdigit() for p in partes):
        numero, anio = partes
        resultados = [
            j for j in juicios if j["numero"] == numero and j["anio"] == anio
        ]
        if resultados:
            return resultados

    # Caso: solo número
    if termino.strip().isdigit():
        resultados = [j for j in juicios if j["numero"] == termino.strip()]
        if resultados:
            return resultados

    # Caso: texto libre en la carátula (o circunscripción)
    termino_norm = normalizar(termino)
    resultados = [
        j
        for j in juicios
        if termino_norm in normalizar(j["caratula"])
        or termino_norm in normalizar(j["circunscripcion"])
    ]
    return resultados


def mostrar(juicio: dict):
    print("-" * 60)
    print(f"Carátula:        {juicio['caratula']}")
    print(f"Nº / Año:        {juicio['numero']} / {juicio['anio']}")
    print(f"Circunscripción: {juicio['circunscripcion']}")
    print(f"Estado:          {juicio['estado']}")


def main():
    if len(sys.argv) < 2:
        print("Uso: python3 buscar_juicio.py <número | 'número año' | texto de la carátula>")
        sys.exit(1)

    termino = " ".join(sys.argv[1:])
    resultados = buscar_juicio(termino)

    if not resultados:
        print(f"No se encontraron causas para: {termino}")
        sys.exit(0)

    print(f"{len(resultados)} resultado(s) para: {termino}")
    for j in resultados:
        mostrar(j)


if __name__ == "__main__":
    main()
