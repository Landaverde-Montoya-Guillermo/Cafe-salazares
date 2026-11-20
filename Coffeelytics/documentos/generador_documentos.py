import os
import datetime
from fpdf import FPDF
from config.negocio import INFO_CAFETERIA
from interfaz.estilos import Color
from consola_ui import imprimir_tabla


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
        pdf.cell(0, 5, INFO_CAFETERIA["nombre"], ln=True, align="C")
        pdf.set_font("Helvetica", "", 7)
        pdf.cell(0, 4, INFO_CAFETERIA["eslogan"], ln=True, align="C")
        pdf.cell(0, 4, INFO_CAFETERIA["direccion"], ln=True, align="C")
        pdf.cell(0, 4, f"RFC: {INFO_CAFETERIA['rfc']} | Tel: {INFO_CAFETERIA['telefono']}", ln=True, align="C")
        pdf.ln(2)
        pdf.cell(0, 0, "", "T", ln=True)
        pdf.ln(2)

        # Datos de la venta
        pdf.set_font("Helvetica", "B", 8)
        pdf.cell(0, 4, f"TICKET #: {folio}", ln=True)
        pdf.set_font("Helvetica", "", 7)
        pdf.cell(0, 4, f"Fecha: {ahora}", ln=True)
        pdf.cell(0, 4, f"Atendio: {empleado.nombre_completo}", ln=True)
        pdf.cell(0, 4, f"Cliente: {carrito.nombre_cliente}", ln=True)
        pdf.ln(2)
        pdf.cell(0, 0, "", "T", ln=True)
        pdf.ln(2)

        # Tabla de productos
        pdf.set_font("Helvetica", "B", 7)
        pdf.cell(36, 4, "PRODUCTO")
        pdf.cell(8, 4, "PZS", align="R")
        pdf.cell(12, 4, "PREC", align="R")
        pdf.cell(14, 4, "TOT", align="R", ln=True)
        pdf.set_font("Helvetica", "", 7)

        for item in carrito.items.values():
            prod = item["producto"]
            cant = item["cantidad"]
            tot = prod.precio * cant
            nombre_corto = prod.nombre[:20]
            pdf.cell(36, 4, nombre_corto)
            pdf.cell(8, 4, str(cant), align="R")
            pdf.cell(12, 4, f"${prod.precio:.2f}", align="R")
            pdf.cell(14, 4, f"${tot:.2f}", align="R", ln=True)

        pdf.ln(2)
        pdf.cell(0, 0, "", "T", ln=True)
        pdf.ln(2)

        # Totales
        sub = carrito.calcular_subtotal()
        iva = carrito.calcular_iva()
        tot = carrito.calcular_total()

        pdf.cell(56, 4, "Subtotal:", align="R")
        pdf.cell(14, 4, f"${sub:.2f}", align="R", ln=True)
        pdf.cell(56, 4, "IVA (8%):", align="R")
        pdf.cell(14, 4, f"${iva:.2f}", align="R", ln=True)
        pdf.set_font("Helvetica", "B", 8)
        pdf.cell(56, 5, "TOTAL:", align="R")
        pdf.cell(14, 5, f"${tot:.2f}", align="R", ln=True)

        pdf.ln(2)
        pdf.set_font("Helvetica", "", 7)
        pdf.cell(0, 4, f"Metodo de pago: {metodo_desc}", ln=True)
        if metodo_desc == "Efectivo" and cambio > 0:
            pdf.cell(0, 4, f"Cambio entregado: ${cambio:.2f}", ln=True)
        if metodo_desc == "Transferencia SPEI":
            pdf.cell(0, 4, f"CLABE: {INFO_CAFETERIA['clabe_transferencia']}", ln=True)
            pdf.cell(0, 4, f"Banco: {INFO_CAFETERIA['banco']}", ln=True)

        pdf.ln(3)
        pdf.set_font("Helvetica", "I", 7)
        pdf.cell(0, 4, "Gracias por su visita!", ln=True, align="C")

        ruta = self._ruta(f"Ticket_Venta_{folio}.pdf")
        pdf.output(ruta)
        print(Color.ok(f"Ticket PDF guardado: {ruta}"))

    def reporte_generico(self, nombre_archivo, titulo, columnas, filas,
                         subtitulo="", encabezado_extra=""):
        """Muestra la tabla en consola y exporta el reporte administrativo en PDF."""
        imprimir_tabla(titulo if not subtitulo else f"{titulo} - {subtitulo}", columnas, filas)

        ahora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        pdf = FPDF(orientation="L", unit="mm", format="Letter")
        pdf.add_page()

        # Encabezado
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 7, f"{INFO_CAFETERIA['nombre']} - {titulo}", ln=True)
        pdf.set_font("Helvetica", "", 9)
        if subtitulo:
            pdf.cell(0, 5, f"Detalle: {subtitulo}", ln=True)
        if encabezado_extra:
            pdf.cell(0, 5, encabezado_extra, ln=True)
        pdf.cell(0, 5, f"Generado: {ahora}", ln=True)
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
            pdf.cell(ancho_disponible, 7, "(Sin registros)", border=1, align="C", ln=True)
        else:
            for fila in filas_limpias:
                for i in range(len(columnas)):
                    val = fila[i] if i < len(fila) else ""
                    pdf.cell(ancho_col, 6, str(val)[:28], border=1, align="C")
                pdf.ln()

        ruta = self._ruta(f"{nombre_archivo}.pdf")
        pdf.output(ruta)
        print(Color.ok(f"Reporte PDF guardado: {ruta}"))