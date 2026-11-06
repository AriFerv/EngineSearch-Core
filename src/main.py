"""Consola de EngineSearch-Core (E1).

Uso, desde la carpeta raíz del proyecto:
    python -m src.main                 consola interactiva (corpus de ref.)
    python -m src.main ruta.csv        consola con otro corpus
    python -m src.main --demo          demostración mínima de E1
"""

import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from src.indice import validar_consulta
    from src.motor import MotorBusqueda
else:
    from .indice import validar_consulta
    from .motor import MotorBusqueda

RAIZ = Path(__file__).resolve().parent.parent
RUTA_REFERENCIA = RAIZ / "datos" / "documentos_referencia.csv"
RUTA_INVALIDA = RAIZ / "datos" / "invalidos" / "ids_duplicados.csv"

AYUDA = """Comandos:
  cargar <ruta.csv>   carga un corpus (si falla, se conserva el anterior)
  buscar <palabra>    busca con el método lineal y con el AVL y los compara
  resumen             documentos, términos y altura del AVL
  avl                 muestra la raíz y los primeros términos en orden
  demo                ejecuta la demostración mínima de E1
  ayuda               muestra este texto
  salir               termina el programa"""


def cargar(motor, ruta):
    """Carga un corpus e informa el resultado; devuelve True si tuvo éxito."""
    try:
        motor.reiniciar_corpus(ruta)
    except ValueError as exc:
        print(f"[ERROR] No se cargó el corpus: {exc}")
        if motor.cargado:
            r = motor.resumen()
            print(f"        Se conserva el corpus anterior: "
                  f"{r['documentos']} documentos, {r['vocabulario']} "
                  "términos.")
        return False
    r = motor.resumen()
    print(f"[OK] Corpus cargado: {r['documentos']} documentos, "
          f"{r['vocabulario']} términos distintos, altura AVL = "
          f"{r['altura_avl']}.")
    return True


def buscar(motor, texto):
    """Busca con ambos métodos y muestra cuánto trabajó cada uno."""
    try:
        token = validar_consulta(texto)
        ids_lineal = motor.buscar(texto, "lineal")
        ids_avl, camino = motor.buscar_avl_con_traza(texto)
    except ValueError as exc:
        print(f"[CONSULTA INVÁLIDA] {exc}")
        return
    r = motor.resumen()
    print(f"Consulta {texto!r} -> palabra normalizada {token!r}")
    print(f"  Lineal: {ids_lineal}   (recorrió los {r['documentos']} "
          "documentos completos)")
    print(f"  AVL   : {ids_avl}   (visitó {len(camino)} de "
          f"{r['vocabulario']} términos)")
    print(f"  Camino en el AVL: {' -> '.join(camino)}")
    if not ids_avl:
        print("  La palabra no está en el corpus: lista vacía (no es error).")
    if ids_lineal == ids_avl:
        print("  [OK] Ambos métodos devuelven la misma lista.")
    else:
        print("  [FALLA] Los métodos NO coinciden; hay un defecto.")


def mostrar_avl(motor):
    arbol = motor.arbol
    vocab = arbol.inorder()
    print(f"Raíz: {arbol.clave_raiz!r}   altura: {arbol.altura}   "
          f"términos: {len(arbol)}   invariantes AVL: "
          f"{'OK' if arbol.verificar() else 'FALLA'}")
    print(f"Primeros términos (in-order): {vocab[:15]}")


def demo(motor):
    """Demostración mínima pedida para E1 (Parte C, sección 3)."""
    print("=== DEMOSTRACIÓN E1 ===")
    print("\n1) Cargar el corpus de referencia")
    cargar(motor, RUTA_REFERENCIA)
    pasos = (("2) Buscar 'busca'", "busca"),
             ("3) Buscar 'python'", "python"),
             ("4) Consulta ausente", "inexistente"),
             ("5) Consulta inválida (dos palabras)", "dos palabras"))
    for titulo, consulta in pasos:
        print(f"\n{titulo}")
        buscar(motor, consulta)
    print("\n6) Error de archivo (IDs duplicados) con corpus ya cargado")
    cargar(motor, RUTA_INVALIDA)
    buscar(motor, "busca")
    print("\n7) ¿Por qué el índice evita revisar todos los documentos?")
    print("  Sin índice, cada consulta recorre y tokeniza todos los\n"
          "  documentos: Θ(T) con T tokens en el corpus.\n"
          "  Con el índice invertido la preparación se paga una sola vez\n"
          "  al cargar; después cada consulta localiza el término en el\n"
          "  AVL con O(log V) comparaciones y lee su lista de posteo,\n"
          "  sin abrir ningún documento.")


def repl(motor):
    print("EngineSearch-Core E1. Escriba 'ayuda' para ver los comandos.")
    while True:
        try:
            linea = input("engine> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if not linea:
            continue
        comando, _, resto = linea.partition(" ")
        comando = comando.lower()
        resto = resto.strip().strip('"')
        if comando in ("salir", "exit", "quit"):
            return
        if comando == "ayuda":
            print(AYUDA)
        elif comando == "cargar":
            cargar(motor, resto)
        elif comando == "buscar":
            buscar(motor, resto)
        elif comando == "resumen" and motor.cargado:
            print(motor.resumen())
        elif comando == "avl" and motor.cargado:
            mostrar_avl(motor)
        elif comando == "demo":
            demo(motor)
        elif comando in ("resumen", "avl"):
            print("[ERROR] No hay ningún corpus cargado.")
        else:
            print(f"Comando desconocido: {comando!r}. Escriba 'ayuda'.")


def _configurar_salida():
    """Evita errores de codificación en consolas que no usan UTF-8."""
    for flujo in (sys.stdout, sys.stderr):
        try:
            flujo.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    _configurar_salida()
    motor = MotorBusqueda()
    if "--demo" in argv:
        demo(motor)
        return 0
    rutas = [a for a in argv if not a.startswith("--")]
    cargar(motor, rutas[0] if rutas else RUTA_REFERENCIA)
    repl(motor)
    return 0


if __name__ == "__main__":
    sys.exit(main())
