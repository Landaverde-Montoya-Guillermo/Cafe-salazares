class Estante:
    def __init__(self, codigo_almacen: int, secciones: str, capacidad: float):
        self.codigo_almacen = codigo_almacen
        self.secciones = secciones  # Ej. "Sección A - Refrigerados", "Estante 2 - Secos"
        self.capacidad = capacidad  # Capacidad máxima (en kg, litros o volumen)

    def __str__(self):
        return f"Estante[{self.codigo_almacen}]: {self.secciones} (Capacidad: {self.capacidad})"