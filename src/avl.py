"""Árbol AVL propio (RT06 a RT09). No usa dict ni librerías de árboles.

Convenciones
  * altura(None) = 0 y la altura de una hoja es 1.
  * balance(nodo) = altura(izq) - altura(der).

Invariante AVL: para todo nodo, |balance| <= 1, además del orden BST
(izq < clave < der) y de que cada altura guardada sea la real.

Argumento de altura: sea N(h) el mínimo de nodos de un AVL de altura h.
Un AVL mínimo tiene un subárbol de altura h-1 y otro de h-2, así que
N(h) = N(h-1) + N(h-2) + 1, con N(1) = 1 y N(2) = 2. Eso crece como los
números de Fibonacci (N(h) >= phi^h / sqrt(5) - 1), por lo que
n >= N(h) implica h < 1.44 * log2(n + 2). Por tanto buscar e insertar
cuestan O(log V) con V términos.

Rotaciones (cada inserción hace a lo sumo una rotación simple o doble):
  LL: desbalance +2 y el hijo izquierdo pesa a la izquierda -> rot. derecha
  RR: desbalance -2 y el hijo derecho pesa a la derecha -> rot. izquierda
  LR: desbalance +2 y el hijo izquierdo pesa a la derecha ->
      rot. izquierda del hijo y luego rot. derecha
  RL: desbalance -2 y el hijo derecho pesa a la izquierda ->
      rot. derecha del hijo y luego rot. izquierda
"""


class NodoAVL:
    """Nodo con clave, posteo (lista de IDs) y altura."""

    __slots__ = ("clave", "posteo", "altura", "izq", "der")

    def __init__(self, clave, posteo):
        self.clave = clave
        self.posteo = posteo
        self.altura = 1
        self.izq = None
        self.der = None


def _altura(nodo):
    return nodo.altura if nodo is not None else 0


def _actualizar(nodo):
    nodo.altura = 1 + max(_altura(nodo.izq), _altura(nodo.der))


def _balance(nodo):
    return _altura(nodo.izq) - _altura(nodo.der)


def _rotar_derecha(y):
    """Sube el hijo izquierdo; y pasa a ser su hijo derecho."""
    x = y.izq
    y.izq = x.der
    x.der = y
    _actualizar(y)
    _actualizar(x)
    return x


def _rotar_izquierda(x):
    """Sube el hijo derecho; x pasa a ser su hijo izquierdo."""
    y = x.der
    x.der = y.izq
    y.izq = x
    _actualizar(x)
    _actualizar(y)
    return y


class ArbolAVL:
    """Mapa clave -> posteo ordenado por clave, balanceado como AVL."""

    def __init__(self):
        self._raiz = None
        self._tamano = 0
        # Bitácora de rotaciones ("LL", "RR", "LR", "RL") para las pruebas
        # y para la traza que se pide en las evidencias.
        self.rotaciones = []

    def __len__(self):
        return self._tamano

    @property
    def altura(self):
        return _altura(self._raiz)

    @property
    def clave_raiz(self):
        return self._raiz.clave if self._raiz is not None else None

    # RT06 -----------------------------------------------------------
    def insertar(self, clave, posteo):
        """Inserta la clave o actualiza su posteo sin duplicarla (RT06).

        La clave puede ser cualquier valor comparable (en el motor son
        cadenas). Guarda una copia del posteo.
        """
        self._raiz = self._insertar(self._raiz, clave, list(posteo))

    def _insertar(self, nodo, clave, posteo):
        if nodo is None:
            self._tamano += 1
            return NodoAVL(clave, posteo)
        if clave < nodo.clave:
            nodo.izq = self._insertar(nodo.izq, clave, posteo)
        elif clave > nodo.clave:
            nodo.der = self._insertar(nodo.der, clave, posteo)
        else:
            nodo.posteo = posteo
            return nodo
        return self._rebalancear(nodo)

    def _rebalancear(self, nodo):
        _actualizar(nodo)
        balance = _balance(nodo)
        if balance > 1:
            if _balance(nodo.izq) < 0:
                self.rotaciones.append("LR")
                nodo.izq = _rotar_izquierda(nodo.izq)
            else:
                self.rotaciones.append("LL")
            return _rotar_derecha(nodo)
        if balance < -1:
            if _balance(nodo.der) > 0:
                self.rotaciones.append("RL")
                nodo.der = _rotar_derecha(nodo.der)
            else:
                self.rotaciones.append("RR")
            return _rotar_izquierda(nodo)
        return nodo

    # RT07 -----------------------------------------------------------
    def buscar_con_traza(self, clave):
        """Devuelve (posteo, camino): lista vacía si no existe (RT07).

        camino es la lista de claves visitadas desde la raíz. No modifica
        el árbol. Cada paso descarta un subárbol completo, por eso el
        costo es O(altura) = O(log V).
        """
        camino = []
        nodo = self._raiz
        while nodo is not None:
            camino.append(nodo.clave)
            if clave == nodo.clave:
                return list(nodo.posteo), camino
            nodo = nodo.izq if clave < nodo.clave else nodo.der
        return [], camino

    def buscar(self, clave):
        """Posteo de la clave o lista vacía (RT07)."""
        return self.buscar_con_traza(clave)[0]

    # RT08 -----------------------------------------------------------
    def verificar(self):
        """True si se cumplen orden BST, alturas reales y balance (RT08)."""
        return self._revisar(self._raiz, None, None) is not None

    def _revisar(self, nodo, minimo, maximo):
        """Altura real del subárbol, o None si alguna regla falla."""
        if nodo is None:
            return 0
        if minimo is not None and not nodo.clave > minimo:
            return None
        if maximo is not None and not nodo.clave < maximo:
            return None
        h_izq = self._revisar(nodo.izq, minimo, nodo.clave)
        if h_izq is None:
            return None
        h_der = self._revisar(nodo.der, nodo.clave, maximo)
        if h_der is None:
            return None
        if nodo.altura != 1 + max(h_izq, h_der):
            return None
        if abs(h_izq - h_der) > 1:
            return None
        return nodo.altura

    # RT09 -----------------------------------------------------------
    def inorder(self):
        """Claves en orden lexicográfico ascendente (RT09)."""
        claves = []
        self._recorrer(self._raiz, claves, "in")
        return claves

    def preorden(self):
        """Claves en preorden (raíz, izq, der); útil para ver la forma."""
        claves = []
        self._recorrer(self._raiz, claves, "pre")
        return claves

    def _recorrer(self, nodo, salida, orden):
        if nodo is None:
            return
        if orden == "pre":
            salida.append(nodo.clave)
        self._recorrer(nodo.izq, salida, orden)
        if orden == "in":
            salida.append(nodo.clave)
        self._recorrer(nodo.der, salida, orden)
