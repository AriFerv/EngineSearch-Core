# EngineSearch-Core — Entrega E1 (ICC006 Análisis de Algoritmos)

- Equipo: Individual
- Alumno: Ari Gabriel Fernandez Villarreal (matrícula M045944)
- Repositorio: https://github.com/AriFerv/EngineSearch-Core 
- Entrega del proyecto: E1

## Requisitos

- Python 3.10 o superior (probado con 3.13).
- Sin dependencias externas: solo biblioteca estándar.
- No necesita internet. Todo se lee de archivos locales.

## Comandos

Ejecutar siempre desde la carpeta raíz del proyecto. En Windows use `py` en lugar de `python`.

```
python -m src.main                       # consola interactiva
python -m src.main --demo                # demostración mínima de E1
python -m src.main datos/corpus_extra.csv  # consola con otro corpus
python -m unittest discover -s pruebas -v  # pruebas T01-T08 y T14-T16
```

Comandos de la consola: `cargar <ruta>`, `buscar <palabra>`, `resumen`,
`avl`, `demo`, `ayuda`, `salir`.

## Estructura

```
datos/documentos_referencia.csv   corpus oficial D01-D06
datos/corpus_extra.csv            corpus adicional (acentos, NFKC, comillas)
datos/invalidos/                  CSV inválidos para T07 y T15
src/normalizacion.py              normalizar y tokenizar (RT01, RT02)
src/carga.py                      lectura y validación del CSV (contrato)
src/indice.py                     índice invertido y búsqueda lineal (RT03, RT04)
src/avl.py                        árbol AVL propio (RT06-RT09)
src/motor.py                      estado del corpus y reinicio atómico (RT05)
src/main.py                       consola
pruebas/interfaz_evaluacion.py    adaptador: cargar, buscar, ranking, sugerir
pruebas/test_engine_search.py     pruebas
evidencias/                       E1_Evidencias_arifernandez.pdf
bitacora.md                       bitacora_contribuciones.md
```

## Alcance de E1

Incluido: carga y validación de CSV, normalización NFKC + casefold,
tokenización, índice invertido, búsqueda lineal, búsqueda con AVL y
reinicio atómico del corpus.

| Prueba | Qué comprueba | Clase en `test_engine_search.py` |
|--------|---------------|----------------------------------|
| T01 | seis documentos, IDs únicos | `T01CorpusReferencia` |
| T02 | `busca` → D01, D02, D03 en lineal y AVL | `T02ConsultaBusca` |
| T03 | `palabras` → D02, D03, D05, D06; frecuencia 4 | `T03ConsultaPalabras` |
| T04 | `python` → D01; frecuencia 2 | `T04ConsultaPython` |
| T05 | consulta ausente → lista vacía (sin Bloom) | `T05Inexistente` |
| T06 | mayúsculas se unifican, acentos se conservan | `T06MayusculasYAcentos` |
| T07 | IDs repetidos y CSV corrupto, sin carga parcial | `T07CSVInvalido` |
| T08 | rotaciones LL, RR, LR, RL; balance e in-order | `T08RotacionesAVL` |
| T14 | reinicio sin residuos | `T14ReinicioConOtroCorpus` |
| T15 | corpus vacío o sin tokens | `T15CorpusVacioOSinTokens` |
| T16 | consulta vacía o de dos palabras | `T16ConsultaInvalida` |

## Decisiones

- Encabezados exactos `doc_id,title,body`. Se tolera el BOM de UTF-8 que
  agrega Excel; cualquier otro byte no UTF-8 se rechaza.
- `doc_id` se recorta con `strip`, no puede estar vacío y es único
  distinguiendo mayúsculas (`A` y `a` son distintos).
- `title` no puede estar vacío tras `strip`; `body` sí puede.
- Las líneas completamente en blanco se ignoran; una fila con más o menos
  de tres columnas se rechaza indicando la línea.
- Frecuencia total = apariciones en título y cuerpo de todos los
  documentos; el posteo lista cada `doc_id` una sola vez, ordenado.
- La búsqueda exacta acepta una sola palabra tras normalizar; una
  palabra ausente devuelve `[]`.
- Un corpus que no produce ningún token se rechaza.
- `reiniciar_corpus` valida y construye todo en variables locales y publica
  el estado nuevo en una sola asignación; si falla, el corpus anterior
  queda intacto.
