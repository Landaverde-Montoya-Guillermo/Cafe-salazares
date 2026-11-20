import os
import datetime
from fpdf import FPDF
from config.negocio import INFO_CAFETERIA
from interfaz.estilos import Color


class GeneradorDocumentos:
    """Genera tickets de venta y reportes administrativos en PDF dentro de documentos/salida/."""

    DIRECTORIO = os.path.join("documentos", "salida")

    def __init__(self):
        os.makedirs(self.DIRECTORIO, exist_ok=True)

    def _ruta(self, nombre_archivo):
        return os.path.join(self.DIRECTORIO, nombre_archivo)

    def ticket_venta(self, folio, carrito, metodo_desc, empleado, cambio=0.0):
        """Muestra resumen en consola y exporta el ticket térmico en PDF."""
        ahora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        # Configurar PDF formato ticket térmico (80mm ancho)
        pdf = FPDF(orientation="P", unit="mm", format=(80, 180))
        pdf.set_auto_page_break(auto=True, margin=8)
        pdf.add_page()
        pdf.set_margins(5, 5, 5)

        # Encabezado Cafetería
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 5, INFO_CAFETERIA["nombre"], new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.set_font("Helvetica", "", 7)
        pdf.cell(0, 4, INFO_CAFETERIA["eslogan"], new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.cell(0, 4, INFO_CAFETERIA["direccion"], new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.cell(0, 4, f"RFC: {INFO_CAFETERIA['rfc']} | Tel: {INFO_CAFETERIA['telefono']}", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.ln(2)
        pdf.cell(0, 0, "", "T", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

        # Datos de la venta
        pdf.set_font("Helvetica", "B", 8)
        pdf.cell(0, 4, f"TICKET #: {folio}", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 7)
        pdf.cell(0, 4, f"Fecha: {ahora}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 4, f"Atendio: {empleado.nombre_completo}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 4, f"Cliente: {carrito.nombre_cliente}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)
        pdf.cell(0, 0, "", "T", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

        # Tabla de productos
        pdf.set_font("Helvetica", "B", 7)
        pdf.cell(36, 4, "PRODUCTO")
        pdf.cell(8, 4, "PZS", align="R")
        pdf.cell(12, 4, "PREC", align="R")
        pdf.cell(14, 4, "TOT", align="R", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 7)

        for item in carrito.items.values():
            prod = item["producto"]
            cant = item["cantidad"]
            tot = prod.precio * cant
            nombre_corto = prod.nombre[:20]
            pdf.cell(36, 4, nombre_corto)
            pdf.cell(8, 4, str(cant), align="R")
            pdf.cell(12, 4, f"${prod.precio:.2f}", align="R")
            pdf.cell(14, 4, f"${tot:.2f}", align="R", new_x="LMARGIN", new_y="NEXT")

        pdf.ln(2)
        pdf.cell(0, 0, "", "T", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

        # Totales
        sub = carrito.calcular_subtotal()
        iva = carrito.calcular_iva()
        tot = carrito.calcular_total()

        pdf.cell(56, 4, "Subtotal:", align="R")
        pdf.cell(14, 4, f"${sub:.2f}", align="R", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(56, 4, "IVA (8%):", align="R")
        pdf.cell(14, 4, f"${iva:.2f}", align="R", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "B", 8)
        pdf.cell(56, 5, "TOTAL:", align="R")
        pdf.cell(14, 5, f"${tot:.2f}", align="R", new_x="LMARGIN", new_y="NEXT")

        pdf.ln(2)
        pdf.set_font("Helvetica", "", 7)
        pdf.cell(0, 4, f"Metodo de pago: {metodo_desc}", new_x="LMARGIN", new_y="NEXT")
        if metodo_desc == "Efectivo" and cambio > 0:
            pdf.cell(0, 4, f"Cambio entregado: ${cambio:.2f}", new_x="LMARGIN", new_y="NEXT")
        if metodo_desc == "Transferencia SPEI":
            pdf.cell(0, 4, f"CLABE: {INFO_CAFETERIA['clabe_transferencia']}", new_x="LMARGIN", new_y="NEXT")
            pdf.cell(0, 4, f"Banco: {INFO_CAFETERIA['banco']}", new_x="LMARGIN", new_y="NEXT")

        pdf.ln(3)
        pdf.set_font("Helvetica", "I", 7)
        pdf.cell(0, 4, "Gracias por su visita!", new_x="LMARGIN", new_y="NEXT", align="C")

        ruta = self._ruta(f"Ticket_Venta_{folio}.pdf")
        pdf.output(ruta)
        print(Color.ok(f"Ticket PDF guardado: {ruta}"))

    def reporte_generico(self, nombre_archivo, titulo, columnas, filas,
                         subtitulo="", encabezado_extra=""):
        """Exporta el reporte administrativo en PDF si el usuario lo confirma."""
        print(Color.info(f"\nDeseas exportar el reporte a PDF? ({nombre_archivo}.pdf)"))
        print(Color.aviso("  [S] Si exportar     [cualquier tecla] No exportar"))
        respuesta = input("  > ").strip().upper()
        if respuesta != "S":
            return

        ahora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        pdf = FPDF(orientation="L", unit="mm", format="Letter")
        pdf.add_page()

        # Encabezado
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 7, f"{INFO_CAFETERIA['nombre']} - {titulo}", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 9)
        if subtitulo:
            pdf.cell(0, 5, f"Detalle: {subtitulo}", new_x="LMARGIN", new_y="NEXT")
        if encabezado_extra:
            pdf.cell(0, 5, encabezado_extra, new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 5, f"Generado: {ahora}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)

        # Normalizar filas
        if filas and isinstance(filas[0], dict):
            filas_limpias = [[str(f.get(c, "")) for c in columnas] for f in filas]
        else:
            filas_limpias = [[str(c2) for c2 in fila] for fila in filas]

        ancho_disponible = pdf.w - 20
        ancho_col = ancho_disponible / max(1, len(columnas))

        # Cabecera de tabla
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_fill_color(130, 80, 40)
        pdf.set_text_color(255, 255, 255)
        for col in columnas:
            pdf.cell(ancho_col, 7, str(col)[:25], border=1, align="C", fill=True)
        pdf.ln()

        # Filas de tabla
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(0, 0, 0)
        if not filas_limpias:
            pdf.cell(ancho_disponible, 7, "(Sin registros)", border=1, align="C", new_x="LMARGIN", new_y="NEXT")
        else:
            for fila in filas_limpias:
                for i in range(len(columnas)):
                    val = fila[i] if i < len(fila) else ""
                    pdf.cell(ancho_col, 6, str(val)[:28], border=1, align="C")
                pdf.ln()

        ruta = self._ruta(f"{nombre_archivo}.pdf")
        pdf.output(ruta)
        print(Color.ok(f"Reporte PDF guardado: {ruta}"))