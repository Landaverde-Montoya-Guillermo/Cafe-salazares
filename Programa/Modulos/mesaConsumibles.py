from datetime import datetime

class DespachoConsumibles:
    def __init__(self, id_despacho: int, empleado: Empleado, insumo, cantidad: float):
        self.id_despacho = id_despacho
        self.empleado = empleado  # Barista/Cajero que abre el empaque
        self.insumo = insumo      # Insumo consumible 
        self.cantidad = cantidad  # Cantidad de paquetes abiertos
        self.fecha = datetime.now()

    def __str__(self):
        return f"Despacho[{self.id_despacho}]: {self.cantidad} pza(s) de {self.insumo.nombre_insumo} sacadas por {self.empleado.nombre}"