from datetime import datetime

class Factura:
    def __init__(self, folio_fiscal: str, monto: float, fecha: datetime = None, codigo_compra: int = None):
        self.folio_fiscal = folio_fiscal  # String largo para la clave/UUID del SAT/Factura
        self.monto = monto
        self.fecha = fecha if fecha else datetime.now()
        self.codigo_compra = codigo_compra  # Referencia a la Compra que la originó

    def __str__(self):
        return f"Factura[{self.folio_fiscal}]: Monto ${self.monto:.2f} | Fecha: {self.fecha.strftime('%Y-%m-%d')}"