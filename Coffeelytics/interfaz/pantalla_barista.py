from consola_ui import (
    seleccionar_con_flechas,
    imprimir_encabezado_sesion,
)
from entidades.carrito_venta import CarritoVenta
from interfaz.barista_catalogo import BaristaCatalogo
from interfaz.barista_carrito import BaristaCarrito
from interfaz.barista_operaciones import BaristaOperaciones


class PantallaBarista:
    def __init__(self, usuario, servicios, reportes):
        self.usuario = usuario
        self.producto_srv = servicios["producto"]
        self.venta_srv = servicios["venta"]
        self.inventario_srv = servicios["inventario"]
        self.merma_srv = servicios["merma"]
        self.despacho_srv = servicios["despacho"]
        self.empleado_srv = servicios["empleado"]
        self.reportes = reportes

    def mostrar(self):
        carrito = CarritoVenta()
        catalogo_ui = BaristaCatalogo(self.usuario, self.producto_srv, carrito)
        carrito_ui = BaristaCarrito(self.usuario, self.venta_srv, carrito, self.reportes)
        operaciones_ui = BaristaOperaciones(
            self.usuario,
            self.inventario_srv,
            self.despacho_srv,
            self.empleado_srv,
            self.merma_srv,
        )
        opciones = [
            "Nueva venta - Catalogo de productos",
            "Ver / gestionar carrito",
            "Registrar merma",
            "Surtir mesa de consumibles",
            "Mi cuenta (desactivar)",
            "<< Cerrar sesion y volver al Inicio",
        ]
        while True:
            enc = imprimir_encabezado_sesion(
                self.usuario,
                breadcrumb=["Inicio", "Panel Barista"]
            )
            idx = seleccionar_con_flechas("MENU BARISTA", opciones, enc)
            if idx == 0:
                catalogo_ui.catalogo_productos()
            elif idx == 1:
                carrito_ui.gestionar_carrito()
            elif idx == 2:
                operaciones_ui.registrar_merma()
            elif idx == 3:
                operaciones_ui.surtir_mesa()
            elif idx == 4:
                if operaciones_ui.desactivar_mi_cuenta():
                    return
            elif idx == 5:
                return
