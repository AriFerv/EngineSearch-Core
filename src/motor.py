"""Motor de búsqueda de E1: corpus, índice invertido, lineal y AVL.

Todo el estado vive en una única tupla _Estado. reiniciar_corpus (RT05)
construye un estado nuevo completo en variables locales y solo al final lo
publica con UNA asignación; si algo falla antes, self._estado no se toca y
el corpus anterior queda íntegro (T07, T14, T15).
"""

from typing import NamedTuple

from .avl import ArbolAVL
from .carga import cargar_documentos
from .indice import buscar_lineal, construir_indice, validar_consulta

MODOS_E1 = ("lineal", "avl")
MODOS_E2 = ("hash", "bloom_hash")


class _Estado(NamedTuple):
    ruta: str
    documentos: tuple
    indice: dict
    arbol: ArbolAVL


class MotorBusqueda:
    """Cada instancia tiene su propio estado, aislado de las demás."""

    def __init__(self):
        self._estado = None

    @property
    def cargado(self):
        return self._estado is not None

    def _requerir_estado(self):
        if self._estado is None:
            raise ValueError(
                "No hay ningún corpus cargado; use reiniciar_corpus(ruta)."
            )
        return self._estado

    # RT05 -----------------------------------------------------------
    def reiniciar_corpus(self, ruta):
        """Carga atómica: reconstruye todo o conserva el corpus previo."""
        documentos = cargar_documentos(ruta)
        indice = construir_indice(documentos)
        if not indice:
            raise ValueError(
                "El corpus no produce ningún token (solo letras o dígitos "
                "cuentan); se rechaza."
            )
        arbol = ArbolAVL()
        for termino, (_, ids) in indice.items():
            arbol.insertar(termino, ids)
        if not arbol.verificar():
            raise RuntimeError("El AVL construido viola sus invariantes.")
        self._estado = _Estado(str(ruta), tuple(documentos), indice, arbol)

    # Búsqueda -------------------------------------------------------
    def buscar(self, termino, modo="avl"):
        """IDs ordenados que contienen el término, según el modo."""
        if modo in MODOS_E2:
            raise NotImplementedError(
                f"El modo '{modo}' se implementa a partir de E2."
            )
        if modo not in MODOS_E1:
            raise ValueError(
                f"Modo desconocido '{modo}'. Modos: lineal, avl, hash, "
                "bloom_hash."
            )
        estado = self._requerir_estado()
        token = validar_consulta(termino)
        if modo == "lineal":
            return buscar_lineal(estado.documentos, token)
        return estado.arbol.buscar(token)

    def buscar_avl_con_traza(self, termino):
        """(IDs, camino de claves visitadas) usando solo el AVL."""
        estado = self._requerir_estado()
        return estado.arbol.buscar_con_traza(validar_consulta(termino))

    # Consulta de estado ---------------------------------------------
    def frecuencia(self, termino):
        """Frecuencia total del término en el corpus (0 si no existe)."""
        estado = self._requerir_estado()
        token = validar_consulta(termino)
        return estado.indice.get(token, (0, []))[0]

    def vocabulario(self):
        """Términos distintos en orden lexicográfico."""
        return list(self._requerir_estado().indice)

    @property
    def indice(self):
        """Índice invertido de referencia (no modificar)."""
        return self._requerir_estado().indice

    @property
    def arbol(self):
        """El AVL del corpus actual (para diagnóstico y pruebas)."""
        return self._requerir_estado().arbol

    def ids_documentos(self):
        return [doc.doc_id for doc in self._requerir_estado().documentos]

    def resumen(self):
        estado = self._requerir_estado()
        return {
            "ruta": estado.ruta,
            "documentos": len(estado.documentos),
            "vocabulario": len(estado.indice),
            "altura_avl": estado.arbol.altura,
        }
