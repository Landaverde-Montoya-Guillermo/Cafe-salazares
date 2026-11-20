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
        try:
            enc = imprimir_encabezado_sesion(
                self.usuario,
                breadcrumb=["Inicio", "Panel Barista", "Nueva Venta", "Carrito", "Cobro"]
            )
            print(enc)
            pfx = _prefijo(_ancho())
            total_venta = self.carrito.calcular_total()
            print(f"\n{pfx}  Total a cobrar: {Color.CARAMELO}{Color.BOLD}${total_venta:.2f}{Color.RESET}\n")

            while True:
                try:
                    nombre_cliente = pedir_nombre_cliente()
                    break
                except ValueError as error:
                    print(Color.error(str(error)))
                    pausar()

            metodos = [
                ("EFEC", "Efectivo"),
                ("TARJ", "Tarjeta bancaria"),
                ("SPEI", "Transferencia SPEI"),
            ]
            enc2 = imprimir_encabezado_sesion(
                self.usuario,
                breadcrumb=["Inicio", "Panel Barista", "Nueva Venta", "Carrito", "Cobro", "Metodo de pago"]
            )
            opciones_pago = [m[1] for m in metodos] + ["<< Cancelar cobro"]
            idx_m = seleccionar_con_flechas("Metodo de pago", opciones_pago, enc2)
            if idx_m == len(metodos):
                print(Color.aviso("Operacion cancelada. No se registro la venta."))
                pausar()
                return False
            cod_pago, desc_pago = metodos[idx_m]

            cambio = 0.0
            if cod_pago == "EFEC":
                limpiar_pantalla()
                print(imprimir_encabezado_sesion(
                    self.usuario,
                    breadcrumb=["Inicio", "Panel Barista", "Nueva Venta", "Cobro", "Efectivo"]
                ))
                print(f"\n{pfx}  Total: {Color.CARAMELO}{Color.BOLD}${total_venta:.2f}{Color.RESET}")
                while True:
                    try:
                        _, cambio = pedir_monto_efectivo(total_venta)
                        break
                    except ValueError as error:
                        print(Color.error(str(error)))
                        pausar()
            elif cod_pago == "TARJ":
                _imprimir_guia(
                    "Pago con tarjeta bancaria en terminal POS",
                    "Pasa la tarjeta en el lector POS y presiona ENTER para confirmar",
                    "ENTER",
                    "El sistema registra el pago con metodo TARJ sin datos de la tarjeta."
                )
                confirmacion = _input_centrado(
                    "Presiona ENTER cuando el cobro en terminal sea confirmado"
                )
                if confirmacion.strip().upper() in ("0", "CANCELAR"):
                    raise OperacionCancelada()
            elif cod_pago == "SPEI":
                _imprimir_guia(
                    "Pago por Transferencia SPEI",
                    "El cliente transfiere a la CLABE indicada y presiona ENTER para confirmar",
                    "ENTER",
                    f"CLABE: {INFO_CAFETERIA['clabe_transferencia']}  Banco: {INFO_CAFETERIA['banco']}"
                )
                print(f"{pfx}  {Color.CARAMELO}CLABE: {INFO_CAFETERIA['clabe_transferencia']}  "
                      f"Banco: {INFO_CAFETERIA['banco']}{Color.RESET}")
                confirmacion = _input_centrado(
                    "Presiona ENTER cuando recibas la confirmacion de la transferencia"
                )
                if confirmacion.strip().upper() in ("0", "CANCELAR"):
                    raise OperacionCancelada()
        except OperacionCancelada:
            print(Color.aviso("Operacion cancelada. No se registro la venta."))
            pausar()
            return False
        except Exception as error:
            print(Color.error(str(error)))
            pausar()
            return False

        self.carrito.nombre_cliente = nombre_cliente
        try:
            ok, msg, folio = self.venta_servicio.registrar_venta(
                self.carrito, cod_pago, self.usuario.num
            )
        except Exception as error:
            print(Color.error(str(error)))
            pausar()
            return False
        if not ok:
            print(Color.error(msg))
            pausar()
            return False

        print(Color.ok(msg))
        try:
            self.reportes.ticket_venta(
                folio, self.carrito, desc_pago, self.usuario, cambio
            )
        except Exception as error:
            print(Color.error(
                f"La venta se registro, pero no se pudo generar el ticket: {error}"
            ))
        self.carrito.vaciar()
        pausar()
        return True