class TipoMerma:
    def __init__(self, codigo: int, nombre: str):
        self.codigo = codigo
        self.nombre = nombre  # Ej. "Caducidad", "Derrame/Accidente", "Mala preparación"

    def __str__(self):
        return f"TipoMerma[{self.codigo}]: {self.nombre}"