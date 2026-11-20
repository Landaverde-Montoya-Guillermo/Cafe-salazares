from interfaz.estilos import Color
from consola_ui import (
    pausar, seleccionar_con_flechas,
    imprimir_encabezado_sesion, imprimir_tabla,
    _ancho, _prefijo, limpiar_pantalla
)
from interfaz.modal_cobro import ModalCobro


class BaristaCarrito:
    def __init__(self, usuario, venta_srv, carrito, reportes):
        self.usuario = usuario
        self.venta_srv = venta_srv
        self.carrito = carrito
        self.reportes = reportes

    def gestionar_carrito(self):
        while True:
            limpiar_pantalla()
            enc = imprimir_encabezado_sesion(
                self.usuario,
                breadcrumb=["Inicio", "Panel Barista", "Carrito"]
            )
            print(enc)
            if not self.carrito.items:
                print(Color.aviso("\n  El carrito esta vacio."))
                pausar()
                return
            cols = ["Codigo", "Producto", "Precio", "Cant.", "Total"]
            filas = []
            for item in self.carrito.items.values():
                p = item["producto"]
                filas.append((p.codigo, p.nombre, f"${p.precio:.2f}",
                              item["cantidad"], f"${p.precio * item['cantidad']:.2f}"))
            imprimir_tabla("CARRITO ACTUAL", cols, filas)
            sub = self.carrito.calcular_subtotal()
            iva = self.carrito.calcular_iva()
            tot = self.carrito.calcular_total()
            pfx = _prefijo(_ancho())
            print(f"\n{pfx}  Subtotal: {Color.CREMA}${sub:.2f}{Color.RESET}  "
                  f"IVA 8%: {Color.CREMA}${iva:.2f}{Color.RESET}  "
                  f"TOTAL: {Color.CARAMELO}{Color.BOLD}${tot:.2f}{Color.RESET}")

            opts = [
                "Cobrar (procesar pago)",
                "Quitar producto del carrito",
                "Vaciar carrito",
                "<< Volver sin cobrar",
            ]
            enc2 = imprimir_encabezado_sesion(
                self.usuario,
                breadcrumb=["Inicio", "Panel Barista", "Carrito"]
            )
            idx = seleccionar_con_flechas("Que deseas hacer?", opts, enc2)
            if idx == 0:
                modal = ModalCobro(self.usuario, self.carrito, self.venta_srv, self.reportes)
                if modal.procesar():
                    return
            elif idx == 1:
                self._quitar_del_carrito()
            elif idx == 2:
                self.carrito.vaciar()
                print(Color.ok("Carrito vaciado."))
                pausar()
                return
            elif idx == 3:
                return

    def _quitar_del_carrito(self):
        codigos = list(self.carrito.items.keys())
        nombres = [
            f"{self.carrito.items[c]['producto'].nombre} x{self.carrito.items[c]['cantidad']}"
            for c in codigos
        ] + ["<< Cancelar"]
        enc = imprimir_encabezado_sesion(
            self.usuario,
            breadcrumb=["Inicio", "Panel Barista", "Carrito", "Quitar producto"]
        )
        idx = seleccionar_con_flechas("Selecciona producto a quitar", nombres, enc)
        if idx < len(codigos):
            nombre_p = self.carrito.items[codigos[idx]]["producto"].nombre
            self.carrito.quitar_producto(codigos[idx])
            print(Color.ok(f"'{nombre_p}' eliminado del carrito."))
            pausar()
