"""Salida de consola para la CLI (capa de presentacion).

Centraliza la salida al usuario. A diferencia del resto del proyecto, aqui
se usa ``print`` deliberadamente: es la interfaz con la persona que ejecuta
los scripts (no es logging). Se evitan emojis para compatibilidad con la
consola de Windows.
"""

from __future__ import annotations


def heading(text: str) -> None:
    print(f"\n=== {text} ===")


def info(text: str) -> None:
    print(text)


def success(text: str) -> None:
    print(f"[OK] {text}")


def warn(text: str) -> None:
    print(f"[!] {text}")


def error(text: str) -> None:
    print(f"[ERROR] {text}")


def say(speaker: str, text: str) -> None:
    print(f"\n{speaker}: {text}\n")
