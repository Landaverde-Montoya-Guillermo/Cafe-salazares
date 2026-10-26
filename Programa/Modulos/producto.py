class Producto:
    def __init__(self, codigo: str, nombre_producto: str, precio_venta: float):
        self.codigo = codigo
        self.nombre_producto = nombre_producto
        self.precio_venta = precio_venta
        self.receta = []  # Lista de tuplas/objetos: (Insumo, cantidad_requerida, unidad_medicion)

    def agregar_insumo_a_receta(self, insumo, cantidad: float, unidad_medicion: str):
        self.receta.append({
            "insumo": insumo,
            "cantidad": cantidad,
            "unidad_medicion": unidad_medicion
        })

    def __str__(self):
        return f"Producto[{self.codigo}]: {self.nombre_producto} | Precio: ${self.precio_venta:.2f}"