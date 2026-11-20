from config.reglas import IVA_FRONTERA
from entidades.base import EntidadBase


class CarritoVenta(EntidadBase):
    def __init__(self):
        self._items = {}
        self._nombre_cliente = "Mostrador"

    @property
    def items(self):
        return self._items

    @property
    def nombre_cliente(self):
        return self._nombre_cliente

    @nombre_cliente.setter
    def nombre_cliente(self, valor):
        texto = str(valor or "").strip()
        self._nombre_cliente = texto.title()[:50] if texto else "Mostrador"

    def agregar_producto(self, producto, cantidad=1):
        cant = int(self.validar_positivo(cantidad, "cantidad"))
        if producto.codigo in self._items:
            self._items[producto.codigo]["cantidad"] += cant
        else:
            self._items[producto.codigo] = {"producto": producto, "cantidad": cant}

    def quitar_producto(self, codigo):
        self._items.pop(codigo, None)

    def vaciar(self):
        self._items.clear()
        self._nombre_cliente = "Mostrador"

    def calcular_subtotal(self):
        return round(sum(i["producto"].precio * i["cantidad"] for i in self._items.values()), 2)

    def calcular_iva(self):
        return round(self.calcular_subtotal() * IVA_FRONTERA, 2)

    def calcular_total(self):
        return round(self.calcular_subtotal() + self.calcular_iva(), 2)