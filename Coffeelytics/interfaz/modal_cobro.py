from config.negocio import INFO_CAFETERIA
from interfaz.estilos import Color
from consola_ui import (
    limpiar_pantalla, pausar, seleccionar_con_flechas,
    imprimir_encabezado_sesion, pedir_nombre_cliente,
    pedir_monto_efectivo, _imprimir_guia, _input_centrado,
    _ancho, _prefijo, OperacionCancelada
)


class ModalCobro:
    def __init__(self, usuario, carrito, venta_servicio, reportes):
        self.usuario = usuario
        self.carrito = carrito
        self.venta_servicio = venta_servicio
        self.reportes = reportes

    def procesar(self):
        """Procesa el pago y delega al servicio el guardado. Devuelve True si se cobro."""
        limpiar_pantalla()
        enc = imprimir_encabezado_sesion(
            self.usuario,
            breadcrumb=["Inicio", "Panel Barista", "Carrito", "Cobro"]
        )
        print(enc)
        pfx = _prefijo(_ancho())
        total_venta = self.carrito.calcular_total()
        print(f"\n{pfx}  Total a cobrar: {Color.CARAMELO}{Color.BOLD}${total_venta:.2f}{Color.RESET}\n")

        self.carrito.nombre_cliente = pedir_nombre_cliente()

        metodos = [("EFEC", "Efectivo"), ("TARJ", "Tarjeta bancaria"), ("SPEI", "Transferencia SPEI")]
        enc2 = imprimir_encabezado_sesion(
            self.usuario,
            breadcrumb=["Inicio", "Panel Barista", "Carrito", "Cobro", "Metodo de pago"]
        )
        idx_m = seleccionar_con_flechas("Metodo de pago", [m[1] for m in metodos], enc2)
        cod_pago, desc_pago = metodos[idx_m]

        cambio = 0.0
        if cod_pago == "EFEC":
            limpiar_pantalla()
            print(imprimir_encabezado_sesion(
                self.usuario,
                breadcrumb=["Inicio", "Panel Barista", "Cobro", "Efectivo"]
            ))
            print(f"\n{pfx}  Total: {Color.CARAMELO}{Color.BOLD}${total_venta:.2f}{Color.RESET}")
            try:
                _, cambio = pedir_monto_efectivo(total_venta)
            except OperacionCancelada:
                return False
        elif cod_pago == "TARJ":
            _imprimir_guia(
                "Pago con tarjeta bancaria en terminal POS",
                "Pasa la tarjeta en el lector POS y presiona ENTER para confirmar",
                "ENTER",
                "El sistema registra el pago con metodo TARJ sin datos de la tarjeta."
            )
            _input_centrado("Presiona ENTER cuando el cobro en terminal sea confirmado")
        elif cod_pago == "SPEI":
            _imprimir_guia(
                "Pago por Transferencia SPEI",
                "El cliente transfiere a la CLABE indicada y presiona ENTER para confirmar",
                "ENTER",
                f"CLABE: {INFO_CAFETERIA['clabe_transferencia']}  Banco: {INFO_CAFETERIA['banco']}"
            )
            print(f"{pfx}  {Color.CARAMELO}CLABE: {INFO_CAFETERIA['clabe_transferencia']}  "
                  f"Banco: {INFO_CAFETERIA['banco']}{Color.RESET}")
            _input_centrado("Presiona ENTER cuando recibas la confirmacion de la transferencia")

        ok, msg, folio = self.venta_servicio.registrar_venta(self.carrito, cod_pago, self.usuario.num)
        if ok:
            print(Color.ok(msg))
            self.reportes.ticket_venta(folio, self.carrito, desc_pago, self.usuario, cambio)
            self.carrito.vaciar()
            pausar()
            return True
        else:
            print(Color.error(msg))
            pausar()
            return False