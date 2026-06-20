"""Logging centralizado.

Regla del proyecto: usar SIEMPRE ``get_logger(__name__)``; nunca
``logging.getLogger`` ni ``print()`` directamente.
"""

from __future__ import annotations

import logging
import os
import sys

_CONFIGURED = False
_LOG_FORMAT = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"
_DATE_FORMAT = "%H:%M:%S"


def _configure_root() -> None:
    """Configura el logger raiz una sola vez (idempotente)."""
    global _CONFIGURED
    if _CONFIGURED:
        return

    level_name = os.environ.get("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    handler = logging.StreamHandler(stream=sys.stderr)
    handler.setFormatter(logging.Formatter(fmt=_LOG_FORMAT, datefmt=_DATE_FORMAT))

    root = logging.getLogger()
    root.setLevel(level)
    # Evita handlers duplicados si algo ya configuro el root.
    if not root.handlers:
        root.addHandler(handler)

    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """Devuelve un logger configurado para el modulo dado.

    Args:
        name: Normalmente ``__name__`` del modulo llamante.

    Returns:
        Logger listo para usar con formato y nivel del proyecto.
    """
    _configure_root()
    return logging.getLogger(name)
