"""Adaptador de evaluación (Parte B, sección 1).

Expone cargar(ruta), buscar(termino, modo), ranking(k) y
sugerir(termino, max_dist=2) sobre un único motor. En E1 solo funcionan
los modos "lineal" y "avl"; el resto se marca como no implementado.
"""

import sys
from pathlib import Path

_RAIZ = Path(__file__).resolve().parent.parent
if str(_RAIZ) not in sys.path:
    sys.path.insert(0, str(_RAIZ))

from src.motor import MotorBusqueda  # noqa: E402

_motor = MotorBusqueda()


def cargar(ruta):
    """Reconstruye el estado desde el CSV; si falla conserva el anterior."""
    _motor.reiniciar_corpus(ruta)


def buscar(termino, modo):
    """list[str] con IDs ordenados. Modos E1: 'lineal' y 'avl'."""
    return _motor.buscar(termino, modo)


def ranking(k):
    raise NotImplementedError("ranking(k) se implementa en E2.")


def sugerir(termino, max_dist=2):
    raise NotImplementedError("sugerir() se implementa en E3.")
