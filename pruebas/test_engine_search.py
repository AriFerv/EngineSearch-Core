"""Pruebas de aceptación de E1: T01-T08 y T14-T16 (Parte B, sección 10).

Cada clase indica la prueba T y los requisitos RT que comprueba.
Ejecutar desde la raíz del proyecto:
    python -m unittest discover -s pruebas -v
"""

import math
import random
import sys
import tempfile
import unittest
from pathlib import Path

PRUEBAS = Path(__file__).resolve().parent
RAIZ = PRUEBAS.parent
for ruta in (str(RAIZ), str(PRUEBAS)):
    if ruta not in sys.path:
        sys.path.insert(0, ruta)

import interfaz_evaluacion as adaptador  # noqa: E402
from src.avl import ArbolAVL  # noqa: E402
from src.carga import cargar_documentos  # noqa: E402
from src.indice import buscar_lineal, construir_indice  # noqa: E402
from src.motor import MotorBusqueda  # noqa: E402
from src.normalizacion import normalizar, tokenizar  # noqa: E402

REFERENCIA = RAIZ / "datos" / "documentos_referencia.csv"
EXTRA = RAIZ / "datos" / "corpus_extra.csv"
INVALIDOS = RAIZ / "datos" / "invalidos"


class BaseConCSV(unittest.TestCase):
    """Utilidades: motor con el corpus de referencia y CSV temporales."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.motor = MotorBusqueda()
        self.motor.reiniciar_corpus(REFERENCIA)

    def csv_temporal(self, contenido, nombre="temporal.csv"):
        ruta = Path(self._tmp.name) / nombre
        if isinstance(contenido, str):
            contenido = contenido.encode("utf-8")
        ruta.write_bytes(contenido)
        return ruta

    def assert_modos(self, termino, esperado, motor=None):
        """Lineal y AVL deben dar exactamente la lista esperada."""
        motor = motor or self.motor
        self.assertEqual(motor.buscar(termino, "lineal"), esperado)
        self.assertEqual(motor.buscar(termino, "avl"), esperado)


class T01CorpusReferencia(BaseConCSV):
    """T01 (RT03): se aceptan D01 a D06; 6 IDs únicos."""

    def test_seis_documentos_unicos(self):
        docs = cargar_documentos(REFERENCIA)
        ids = [d.doc_id for d in docs]
        self.assertEqual(ids, ["D01", "D02", "D03", "D04", "D05", "D06"])
        self.assertEqual(len(set(ids)), 6)
        self.assertEqual(self.motor.resumen()["documentos"], 6)

    def test_corpus_extra_valido(self):
        motor = MotorBusqueda()
        motor.reiniciar_corpus(EXTRA)
        self.assertIn("m01", motor.ids_documentos())
        self.assertIn("M01", motor.ids_documentos())

    def test_posteo_sin_repetidos(self):
        # "python" aparece dos veces en D01: el ID va una sola vez.
        frecuencia, ids = construir_indice(
            cargar_documentos(REFERENCIA))["python"]
        self.assertEqual((frecuencia, ids), (2, ["D01"]))


class T02ConsultaBusca(BaseConCSV):
    """T02 (RT03, RT04, RT07): busca -> [D01, D02, D03] en lineal y AVL."""

    def test_busca(self):
        self.assert_modos("busca", ["D01", "D02", "D03"])

    def test_adaptador(self):
        adaptador.cargar(REFERENCIA)
        for modo in ("lineal", "avl"):
            self.assertEqual(adaptador.buscar("busca", modo),
                             ["D01", "D02", "D03"])

    def test_avl_igual_a_lineal_en_todo_el_vocabulario(self):
        for ruta in (REFERENCIA, EXTRA):
            motor = MotorBusqueda()
            motor.reiniciar_corpus(ruta)
            for termino in motor.vocabulario():
                self.assertEqual(motor.buscar(termino, "avl"),
                                 motor.buscar(termino, "lineal"), termino)
                self.assertEqual(motor.buscar(termino, "avl"),
                                 motor.indice[termino][1], termino)


class T03ConsultaPalabras(BaseConCSV):
    """T03 (RT02, RT03): palabras -> [D02, D03, D05, D06], frecuencia 4."""

    def test_palabras(self):
        self.assert_modos("palabras", ["D02", "D03", "D05", "D06"])
        self.assertEqual(self.motor.frecuencia("palabras"), 4)


class T04ConsultaPython(BaseConCSV):
    """T04 (RT03): python -> [D01], frecuencia total 2."""

    def test_python(self):
        self.assert_modos("python", ["D01"])
        self.assertEqual(self.motor.frecuencia("python"), 2)


class T05Inexistente(BaseConCSV):
    """T05 (RT04, RT07): palabra ausente -> [] (sin Bloom todavía)."""

    def test_ausente_es_lista_vacia(self):
        for termino in ("inexistente", "zzz", "pythom"):
            self.assert_modos(termino, [])
        self.assertEqual(self.motor.frecuencia("inexistente"), 0)

    def test_ausente_no_modifica_el_arbol(self):
        antes = self.motor.arbol.preorden()
        self.motor.buscar("inexistente", "avl")
        self.assertEqual(self.motor.arbol.preorden(), antes)


class T06MayusculasYAcentos(BaseConCSV):
    """T06 (RT01, RT02): mayúsculas se unifican; los acentos se conservan."""

    def test_mayusculas(self):
        self.assertEqual(normalizar("PYTHON"), normalizar("python"))
        self.assert_modos("PYTHON", ["D01"])
        self.assert_modos("PyThOn", ["D01"])

    def test_acentos_distintos(self):
        self.assertNotEqual(normalizar("canción"), normalizar("cancion"))
        motor = MotorBusqueda()
        motor.reiniciar_corpus(EXTRA)
        self.assert_modos("canción", ["M01"], motor)
        self.assert_modos("cancion", ["M02"], motor)
        self.assert_modos("CANCIÓN", ["M01"], motor)

    def test_nfkc(self):
        self.assertEqual(normalizar("ﬁnal"), "final")
        motor = MotorBusqueda()
        motor.reiniciar_corpus(EXTRA)
        self.assert_modos("final", ["M08"], motor)

    def test_normalizar_idempotente(self):
        for texto in ("İstanbul", "ÑANDÚ", "ß", "ﬁ"):
            self.assertEqual(normalizar(normalizar(texto)),
                             normalizar(texto))

    def test_tokenizar(self):
        self.assertEqual(tokenizar("Año 2026: guion_bajo!"),
                         ["año", "2026", "guion", "bajo"])
        self.assertEqual(tokenizar("---"), [])
        self.assertEqual(tokenizar("la la la"), ["la", "la", "la"])

    def test_no_hay_stopwords(self):
        self.assert_modos("la", ["D06"])
        self.assert_modos("un", ["D02", "D03"])


class T07CSVInvalido(BaseConCSV):
    """T07 (RT05): IDs repetidos y CSV corrupto, sin carga parcial."""

    def test_todo_invalido_se_rechaza_con_mensaje(self):
        archivos = sorted(INVALIDOS.glob("*.csv"))
        self.assertGreaterEqual(len(archivos), 2)
        for archivo in archivos:
            with self.subTest(archivo=archivo.name):
                with self.assertRaises(ValueError) as ctx:
                    MotorBusqueda().reiniciar_corpus(archivo)
                self.assertTrue(str(ctx.exception).strip())

    def test_diagnostico_de_duplicado(self):
        with self.assertRaises(ValueError) as ctx:
            cargar_documentos(INVALIDOS / "ids_duplicados.csv")
        mensaje = str(ctx.exception)
        self.assertIn("duplicado", mensaje)
        self.assertIn("D01", mensaje)
        self.assertIn("Línea 4", mensaje)

    def test_error_conserva_el_corpus_previo(self):
        antes = self.motor.resumen()
        arbol_antes = self.motor.arbol
        for archivo in sorted(INVALIDOS.glob("*.csv")):
            with self.assertRaises(ValueError):
                self.motor.reiniciar_corpus(archivo)
        with self.assertRaises(ValueError):
            self.motor.reiniciar_corpus(RAIZ / "no_existe.csv")
        self.assertEqual(self.motor.resumen(), antes)
        self.assertIs(self.motor.arbol, arbol_antes)
        self.assert_modos("busca", ["D01", "D02", "D03"])

    def test_el_id_distingue_mayusculas(self):
        ruta = self.csv_temporal("doc_id,title,body\nA,uno,x\na,dos,y\n")
        motor = MotorBusqueda()
        motor.reiniciar_corpus(ruta)
        self.assertEqual(motor.ids_documentos(), ["A", "a"])

    def test_id_unico_tras_trim(self):
        ruta = self.csv_temporal("doc_id,title,body\nA,uno,x\n A ,dos,y\n")
        with self.assertRaises(ValueError):
            MotorBusqueda().reiniciar_corpus(ruta)

    def test_acepta_bom_y_comillas(self):
        ruta = self.csv_temporal(
            '﻿doc_id,title,body\nA,"uno, dos","línea\nsiguiente"\n')
        motor = MotorBusqueda()
        motor.reiniciar_corpus(ruta)
        self.assert_modos("siguiente", ["A"], motor)

    def test_adaptador_conserva_corpus(self):
        adaptador.cargar(REFERENCIA)
        with self.assertRaises(ValueError):
            adaptador.cargar(INVALIDOS / "ids_duplicados.csv")
        self.assertEqual(adaptador.buscar("python", "avl"), ["D01"])


class T08RotacionesAVL(unittest.TestCase):
    """T08 (RT06-RT09): LL, RR, LR, RL; balance y recorrido correctos."""

    CASOS = {"LL": [30, 20, 10], "RR": [10, 20, 30],
             "LR": [30, 10, 20], "RL": [10, 30, 20]}

    def test_cuatro_rotaciones(self):
        for caso, claves in self.CASOS.items():
            with self.subTest(caso=caso):
                arbol = ArbolAVL()
                for clave in claves:
                    arbol.insertar(clave, [f"D{clave}"])
                self.assertEqual(arbol.rotaciones, [caso])
                self.assertEqual(arbol.clave_raiz, 20)
                self.assertEqual(arbol.preorden(), [20, 10, 30])
                self.assertEqual(arbol.inorder(), [10, 20, 30])
                self.assertEqual(arbol.altura, 2)
                self.assertTrue(arbol.verificar())

    def test_insertar_actualiza_sin_duplicar(self):
        arbol = ArbolAVL()
        arbol.insertar("a", ["D01"])
        arbol.insertar("a", ["D01", "D02"])
        self.assertEqual(len(arbol), 1)
        self.assertEqual(arbol.buscar("a"), ["D01", "D02"])
        self.assertEqual(arbol.inorder(), ["a"])

    def test_buscar_ausente_y_no_altera(self):
        arbol = ArbolAVL()
        for clave in "mfzab":
            arbol.insertar(clave, [clave.upper()])
        forma = arbol.preorden()
        self.assertEqual(arbol.buscar("q"), [])
        self.assertEqual(ArbolAVL().buscar("q"), [])
        self.assertEqual(arbol.preorden(), forma)

    def test_orden_ascendente_cumple_cota_de_altura(self):
        arbol = ArbolAVL()
        n = 1000
        for i in range(n):
            arbol.insertar(i, [str(i)])
            self.assertTrue(arbol.verificar())
        self.assertEqual(arbol.inorder(), list(range(n)))
        self.assertLessEqual(arbol.altura, 1.44 * math.log2(n + 2))

    def test_inserciones_aleatorias(self):
        azar = random.Random(2026)
        vistas = set()
        for _ in range(200):
            claves = azar.sample(range(500), 60)
            arbol = ArbolAVL()
            for clave in claves:
                arbol.insertar(clave, [str(clave)])
                self.assertTrue(arbol.verificar())
            self.assertEqual(arbol.inorder(), sorted(claves))
            vistas.update(arbol.rotaciones)
        self.assertEqual(vistas, {"LL", "RR", "LR", "RL"})

    def test_verificar_detecta_arboles_danados(self):
        arbol = ArbolAVL()
        for clave in (20, 10, 30):
            arbol.insertar(clave, [])
        raiz = arbol._raiz
        raiz.altura = 7                      # altura incoherente
        self.assertFalse(arbol.verificar())
        raiz.altura = 2
        raiz.izq.clave = 25                  # rompe el orden BST
        self.assertFalse(arbol.verificar())
        raiz.izq.clave = 10
        # Cadena 30 -> 40 -> 50 a la derecha con alturas coherentes:
        # BST y alturas correctas, pero balance de la raíz = -2.
        n40, n50 = type(raiz)(40, []), type(raiz)(50, [])
        raiz.der.der = n40
        n40.der = n50
        n40.altura, raiz.der.altura, raiz.altura = 2, 3, 4
        self.assertFalse(arbol.verificar())

    def test_vocabulario_del_corpus(self):
        for ruta in (REFERENCIA, EXTRA):
            motor = MotorBusqueda()
            motor.reiniciar_corpus(ruta)
            self.assertEqual(motor.arbol.inorder(), sorted(motor.indice))
            self.assertEqual(len(motor.arbol), len(motor.indice))
            self.assertTrue(motor.arbol.verificar())


class T14ReinicioConOtroCorpus(BaseConCSV):
    """T14 (RT05): reiniciar con otro corpus no deja residuos."""

    def test_sin_terminos_ni_ids_residuales(self):
        ruta = self.csv_temporal(
            "doc_id,title,body\nX01,Gato negro,El gato duerme.\n")
        self.motor.reiniciar_corpus(ruta)
        self.assertEqual(self.motor.ids_documentos(), ["X01"])
        self.assertEqual(self.motor.vocabulario(),
                         ["duerme", "el", "gato", "negro"])
        self.assertEqual(self.motor.arbol.inorder(),
                         ["duerme", "el", "gato", "negro"])
        for termino in ("python", "busca", "palabras", "avl"):
            self.assert_modos(termino, [])
        self.assert_modos("gato", ["X01"])

    def test_instancias_aisladas(self):
        otro = MotorBusqueda()
        otro.reiniciar_corpus(EXTRA)
        self.assert_modos("busca", ["D01", "D02", "D03"])
        self.assert_modos("busca", [], otro)

    def test_adaptador_reinicia(self):
        adaptador.cargar(REFERENCIA)
        adaptador.cargar(EXTRA)
        self.assertEqual(adaptador.buscar("busca", "lineal"), [])
        self.assertEqual(adaptador.buscar("busca", "avl"), [])
        adaptador.cargar(REFERENCIA)
        self.assertEqual(adaptador.buscar("busca", "avl"),
                         ["D01", "D02", "D03"])


class T15CorpusVacioOSinTokens(BaseConCSV):
    """T15 (RT05): corpus vacío o sin tokens -> rechazo seguro."""

    def casos(self):
        return {
            "archivo vacío": self.csv_temporal(b"", "vacio.csv"),
            "solo encabezado": self.csv_temporal(
                "doc_id,title,body\n", "encabezado.csv"),
            "sin tokens": INVALIDOS / "sin_tokens.csv",
            "solo espacios": self.csv_temporal("  \n\n", "espacios.csv"),
        }

    def test_rechazo_con_motivo_y_sin_perder_estado(self):
        for nombre, ruta in self.casos().items():
            with self.subTest(caso=nombre):
                with self.assertRaises(ValueError) as ctx:
                    self.motor.reiniciar_corpus(ruta)
                self.assertTrue(str(ctx.exception).strip())
                self.assert_modos("python", ["D01"])

    def test_motor_nuevo_sigue_sin_corpus(self):
        motor = MotorBusqueda()
        with self.assertRaises(ValueError):
            motor.reiniciar_corpus(INVALIDOS / "sin_tokens.csv")
        self.assertFalse(motor.cargado)
        with self.assertRaises(ValueError):
            motor.buscar("python", "avl")


class T16ConsultaInvalida(BaseConCSV):
    """T16 (RT01, RT02): consulta vacía o de dos palabras -> error claro."""

    def test_consultas_invalidas(self):
        for consulta in ("", "   ", "dos palabras", "!!!", "_", None, 7):
            for modo in ("lineal", "avl"):
                with self.subTest(consulta=consulta, modo=modo):
                    with self.assertRaises(ValueError) as ctx:
                        self.motor.buscar(consulta, modo)
                    self.assertTrue(str(ctx.exception).strip())

    def test_el_motor_sigue_funcionando(self):
        with self.assertRaises(ValueError):
            self.motor.buscar("dos palabras", "avl")
        self.assert_modos("python", ["D01"])

    def test_adaptador_modos(self):
        adaptador.cargar(REFERENCIA)
        with self.assertRaises(ValueError):
            adaptador.buscar("", "avl")
        with self.assertRaises(ValueError):
            adaptador.buscar("python", "inexistente")
        with self.assertRaises(NotImplementedError):
            adaptador.buscar("python", "hash")
        with self.assertRaises(NotImplementedError):
            adaptador.ranking(3)
        with self.assertRaises(NotImplementedError):
            adaptador.sugerir("pythom")

    def test_lineal_independiente_del_indice(self):
        docs = cargar_documentos(REFERENCIA)
        self.assertEqual(buscar_lineal(docs, "Python"), ["D01"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
