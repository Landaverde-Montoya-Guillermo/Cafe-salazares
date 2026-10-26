from datetime import datetime

class DetalleVenta:
    def __init__(self, producto, cantidad: int, precio_unitario_venta: float):
        self.producto = producto
        self.cantidad = cantidad
        self.precio_unitario_venta = precio_unitario_venta
        self.subtotal = cantidad * precio_unitario_venta

class Venta:
    def __init__(self, codigo_venta: int, num_empleado: int, codigo_metodo_pago: int):
        self.codigo_venta = codigo_venta
        self.fecha_hora = datetime.now()
        self.num_empleado = num_empleado
        self.codigo_metodo_pago = codigo_metodo_pago
        self.detalles = []  # Lista de DetalleVenta
        self.total = 0.0

    def agregar_producto(self, producto, cantidad: int):
        detalle = DetalleVenta(producto, cantidad, producto.precio_venta)
        self.detalles.append(detalle)
        self.total += detalle.subtotal

    def __str__(self):
        return f"Venta[{self.codigo_venta}]: Total ${self.total:.2f} ({len(self.detalles)} ítems)"