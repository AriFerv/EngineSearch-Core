"""Normalización y tokenización de texto (RT01 y RT02).

Reglas del contrato (Parte B, sección 4):
  * normalizar aplica Unicode NFKC y casefold. NO quita acentos:
    "canción" y "cancion" siguen siendo palabras distintas.
  * tokenizar devuelve las secuencias maximales de letras o dígitos
    Unicode. El guion bajo separa palabras y no se eliminan stopwords.
"""

import re
import unicodedata

# \w incluye letras, dígitos y "_"; con [^\W_] nos quedamos con
# letras/dígitos Unicode y el guion bajo funciona como separador.
_PATRON_TOKEN = re.compile(r"[^\W_]+")


def normalizar(texto):
    """Devuelve el texto en NFKC y casefold (RT01).

    Se aplica NFKC otra vez después del casefold porque casefold puede
    producir secuencias que no están compuestas; así normalizar es
    idempotente: normalizar(normalizar(x)) == normalizar(x).
    """
    if not isinstance(texto, str):
        raise ValueError("El texto a normalizar debe ser una cadena.")
    compuesto = unicodedata.normalize("NFKC", texto)
    return unicodedata.normalize("NFKC", compuesto.casefold())


def tokenizar(texto):
    """Lista de tokens (letras/dígitos Unicode) del texto normalizado (RT02).

    Conserva repeticiones y el orden de aparición; la frecuencia total de
    un término se obtiene contando estos tokens.
    """
    return _PATRON_TOKEN.findall(normalizar(texto))
