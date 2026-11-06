"""Lectura y validación del CSV de documentos (Parte B, sección 2).

cargar_documentos valida TODO el archivo antes de devolver algo. Si hay
cualquier problema lanza ValueError con un diagnóstico (línea y motivo) y
no devuelve resultados parciales.
"""

import csv
import io
from typing import NamedTuple

ENCABEZADOS = ["doc_id", "title", "body"]


class Documento(NamedTuple):
    """Un registro válido del corpus."""

    doc_id: str
    title: str
    body: str


def _leer_texto(ruta):
    """Lee el archivo completo y lo decodifica como UTF-8."""
    try:
        with open(ruta, "rb") as archivo:
            crudo = archivo.read()
    except FileNotFoundError:
        raise ValueError(f"El archivo '{ruta}' no existe.") from None
    except (OSError, TypeError, ValueError) as exc:
        raise ValueError(f"No se pudo leer '{ruta}': {exc}") from exc

    if not crudo.strip():
        raise ValueError(f"El archivo '{ruta}' está vacío.")
    try:
        # utf-8-sig tolera el BOM que agrega Excel al guardar como CSV.
        return crudo.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError(
            f"'{ruta}' no es UTF-8 válido (byte {exc.start}: {exc.reason})."
        ) from exc


def cargar_documentos(ruta):
    """Devuelve la lista de Documento del CSV o lanza ValueError.

    Validaciones: encabezados exactos doc_id,title,body; tres columnas por
    fila; doc_id y title no vacíos tras strip; doc_id único (distingue
    mayúsculas); al menos un documento. Las líneas completamente en blanco
    se ignoran. La validación de "cero tokens" la hace el motor, que es
    quien tokeniza.
    """
    texto = _leer_texto(ruta)
    lector = csv.reader(io.StringIO(texto, newline=""), strict=True)
    documentos = []
    vistos = set()
    try:
        encabezado = next(lector, None)
        if encabezado != ENCABEZADOS:
            raise ValueError(
                "Encabezados inválidos: se esperaba "
                f"{','.join(ENCABEZADOS)} y se encontró {encabezado}."
            )
        for fila in lector:
            if not fila:
                continue
            linea = lector.line_num
            if len(fila) != len(ENCABEZADOS):
                raise ValueError(
                    f"Línea {linea}: se esperaban 3 columnas y hay "
                    f"{len(fila)}."
                )
            doc_id = fila[0].strip()
            titulo = fila[1]
            if not doc_id:
                raise ValueError(f"Línea {linea}: doc_id vacío.")
            if doc_id in vistos:
                raise ValueError(
                    f"Línea {linea}: doc_id duplicado '{doc_id}'."
                )
            if not titulo.strip():
                raise ValueError(f"Línea {linea}: title vacío.")
            vistos.add(doc_id)
            documentos.append(Documento(doc_id, titulo, fila[2]))
    except csv.Error as exc:
        raise ValueError(
            f"CSV mal formado cerca de la línea {lector.line_num}: {exc}."
        ) from exc

    if not documentos:
        raise ValueError("El archivo no contiene ningún documento.")
    return documentos
