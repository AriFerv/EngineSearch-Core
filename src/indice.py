"""Índice invertido, validación de consultas y búsqueda lineal.

RT03: construir_indice crea el mapa lógico
        término -> (frecuencia_total, lista_ordenada_de_ids_sin_repetidos)
RT04: buscar_lineal recorre el corpus completo sin usar el índice, el AVL
      ni ninguna otra estructura; es la línea base y el oráculo de pruebas.
"""

from .normalizacion import tokenizar


def validar_consulta(consulta):
    """Devuelve el único token de la consulta o lanza ValueError.

    La búsqueda exacta acepta una sola palabra (después de normalizar).
    Se rechazan consultas vacías o con cero o más de un token (T16).
    """
    if not isinstance(consulta, str):
        raise ValueError("La consulta debe ser texto.")
    if not consulta.strip():
        raise ValueError("La consulta está vacía.")
    tokens = tokenizar(consulta)
    if not tokens:
        raise ValueError(
            "La consulta no contiene ninguna palabra "
            "(solo cuentan letras y dígitos)."
        )
    if len(tokens) > 1:
        raise ValueError(
            "La búsqueda exacta acepta una sola palabra; la consulta "
            f"contiene {len(tokens)}: {tokens}."
        )
    return tokens[0]


def construir_indice(documentos):
    """Construye el índice invertido (RT03).

    Costo: O(T) para recorrer los T tokens, más ordenar el vocabulario
    (O(V log V)) y cada lista de IDs.

    La frecuencia cuenta todas las apariciones (título y cuerpo, en todos
    los documentos). El posteo guarda cada doc_id UNA vez por término,
    aunque el término se repita dentro del mismo documento, y se entrega
    ordenado ascendentemente. El diccionario resultante sale ordenado por
    término.
    """
    frecuencias = {}
    posteos = {}
    for doc in documentos:
        for token in tokenizar(doc.title) + tokenizar(doc.body):
            frecuencias[token] = frecuencias.get(token, 0) + 1
            posteos.setdefault(token, set()).add(doc.doc_id)
    return {
        termino: (frecuencias[termino], sorted(posteos[termino]))
        for termino in sorted(frecuencias)
    }


def buscar_lineal(documentos, termino):
    """IDs ordenados de los documentos que contienen el término (RT04).

    Recorre y tokeniza TODOS los documentos en cada consulta: costo
    Θ(T) con T = total de tokens del corpus. No consulta ningún índice.
    """
    token = validar_consulta(termino)
    encontrados = set()
    for doc in documentos:
        if token in tokenizar(doc.title) or token in tokenizar(doc.body):
            encontrados.add(doc.doc_id)
    return sorted(encontrados)
