class Nodo:
    def __init__(self, vuelo):
        self.vuelo = vuelo
        self.siguiente = None
        self.anterior = None

class ListaDoblementeEnlazada:
    def __init__(self):
        self.cabeza = None
        self.cola = None
        self._longitud = 0

    def obtener_primero(self):
        return self.cabeza.vuelo if self.cabeza else None

    def obtener_ultimo(self):
        return self.cola.vuelo if self.cola else None

    def insertar_al_frente(self, vuelo):
        nuevo_nodo = Nodo(vuelo)
        if not self.cabeza:
            self.cabeza = self.cola = nuevo_nodo
        else:
            nuevo_nodo.siguiente = self.cabeza
            self.cabeza.anterior = nuevo_nodo
            self.cabeza = nuevo_nodo
        self._longitud += 1

    def insertar_al_final(self, vuelo):
        nuevo_nodo = Nodo(vuelo)
        if not self.cola:
            self.cabeza = self.cola = nuevo_nodo
        else:
            nuevo_nodo.anterior = self.cola
            self.cola.siguiente = nuevo_nodo
            self.cola = nuevo_nodo
        self._longitud += 1

    def longitud(self):
        return self._longitud

    def insertar_en_posicion(self, vuelo, posicion):
        """Inserta un vuelo en una posición específica (ej: índice 2)."""
        if posicion < 0 or posicion > self._longitud:
            raise IndexError("Posición fuera de rango")
        if posicion == 0:
            self.insertar_al_frente(vuelo)
        elif posicion == self._longitud:
            self.insertar_al_final(vuelo)
        else:
            nuevo_nodo = Nodo(vuelo)
            actual = self.cabeza
            for _ in range(posicion - 1):
                actual = actual.siguiente
            nuevo_nodo.siguiente = actual.siguiente
            nuevo_nodo.anterior = actual
            actual.siguiente.anterior = nuevo_nodo
            actual.siguiente = nuevo_nodo
            self._longitud += 1

    def extraer_de_posicion(self, posicion):
        """Remueve y retorna el vuelo en la posición dada (ej: cancelación)."""
        if posicion < 0 or posicion >= self._longitud:
            raise IndexError("Posición fuera de rango")
        if posicion == 0:
            vuelo = self.cabeza.vuelo
            self.cabeza = self.cabeza.siguiente
            if self.cabeza:
                self.cabeza.anterior = None
            else:
                self.cola = None
        elif posicion == self._longitud - 1:
            vuelo = self.cola.vuelo
            self.cola = self.cola.anterior
            if self.cola:
                self.cola.siguiente = None
            else:
                self.cabeza = None
        else:
            actual = self.cabeza
            for _ in range(posicion):
                actual = actual.siguiente
            vuelo = actual.vuelo
            actual.anterior.siguiente = actual.siguiente
            actual.siguiente.anterior = actual.anterior
        self._longitud -= 1
        return vuelo