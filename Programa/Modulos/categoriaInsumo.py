class CategoriaInsumo:
    def __init__(self, codigo_cat_insumo: int, nombre: str):
        self.codigo_cat_insumo = codigo_cat_insumo
        self.nombre = nombre  # Ej. "Lácteos", "Granos de Café", "Jarabes/Siropes", "Empaques/Consumibles"

    def __str__(self):
        return f"CategoriaInsumo[{self.codigo_cat_insumo}]: {self.nombre}"