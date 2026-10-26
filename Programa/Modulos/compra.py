from datetime import datetime

class Proveedor:
    def __init__(self, codigo_proveedor: int, nombre: str, telefono: str, calle: str, colonia: str, numero: str):
        self.codigo_proveedor = codigo_proveedor
        self.nombre = nombre
        self.telefono = telefono
        self.calle = calle
        self.colonia = colonia
        self.numero = numero

    def __str__(self):
        return f"Proveedor[{self.codigo_proveedor}]: {self.nombre}"


class DetalleCompra:
    def __init__(self, insumo, cantidad_comprada: float, precio_unitario_compra: float):
        self.insumo = insumo  # Objeto de la clase Insumo
        self.cantidad_comprada = cantidad_comprada
        self.precio_unitario_compra = precio_unitario_compra
        self.importe = cantidad_comprada * precio_unitario_compra


class Compra:
    def __init__(self, codigo_compra: int, proveedor: Proveedor, empleado: Empleado, codigo_metodo_pago: int, factura=None):
        self.codigo_compra = codigo_compra
        self.fecha = datetime.now()
        self.proveedor = proveedor
        self.empleado = empleado
        self.codigo_metodo_pago = codigo_metodo_pago
        self.factura = factura
        self.detalles = []  # Lista de DetalleCompra
        self.monto = 0.0

    def agregar_insumo(self, insumo, cantidad: float, precio_unitario: float):
        detalle = DetalleCompra(insumo, cantidad, precio_unitario)
        self.detalles.append(detalle)
        self.monto += detalle.importe

    def __str__(self):
        return f"Compra[{self.codigo_compra}]: Prov: {self.proveedor.nombre} | Monto: ${self.monto:.2f}"