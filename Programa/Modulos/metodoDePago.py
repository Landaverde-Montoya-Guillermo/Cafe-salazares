class MetodoPago:
    def __init__(self, codigo: int, descripcion: str):
        self.codigo = codigo
        self.descripcion = descripcion  # Ej. "Efectivo", "Tarjeta de Débito", "Transferencia SPEI"

    def __str__(self):
        return f"MetodoPago[{self.codigo}]: {self.descripcion}"