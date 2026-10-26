class Insumo:
    def __init__(self, codigo: str, nombre_insumo: str, stock_actual: float, 
                 stock_min: float, unidad_medida: str, codigo_cat_insumo: int, codigo_almacen: int):
        self.codigo = codigo
        self.nombre_insumo = nombre_insumo
        self.stock_actual = stock_actual
        self.stock_min = stock_min
        self.unidad_medida = unidad_medida
        self.codigo_cat_insumo = codigo_cat_insumo
        self.codigo_almacen = codigo_almacen

    def requiere_reabastecimiento(self) -> bool:
        """Retorna True si el stock actual cayó por debajo del stock mínimo."""
        return self.stock_actual <= self.stock_min

    def __str__(self):
        return f"Insumo[{self.codigo}]: {self.nombre_insumo} | Stock: {self.stock_actual} {self.unidad_medida}"