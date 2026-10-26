from datetime import datetime

class TipoMerma:
    def __init__(self, codigo: int, nombre: str):
        self.codigo = codigo
        self.nombre = nombre  # Ej. "Caducidad", "Derrame", "Mala preparación"

    def __str__(self):
        return f"TipoMerma[{self.codigo}]: {self.nombre}"


class Merma:
    def __init__(self, codigo_merma: int, insumo, tipo_merma: TipoMerma, cantidad: float, motivo: str):
        self.codigo_merma = codigo_merma
        self.fecha = datetime.now()
        self.insumo = insumo  # Objeto Insumo afectado
        self.tipo_merma = tipo_merma  # Objeto TipoMerma
        self.cantidad = cantidad
        self.motivo = motivo

    def __str__(self):
        return f"Merma[{self.codigo_merma}]: {self.insumo.nombre_insumo} | Cantidad: {self.cantidad} ({self.tipo_merma.nombre})"