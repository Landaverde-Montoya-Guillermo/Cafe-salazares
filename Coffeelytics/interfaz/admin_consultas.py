import datetime
from typing import Any
from interfaz.estilos import Color
from consola_ui import (
    limpiar_pantalla, pausar, seleccionar_con_flechas,
    imprimir_encabezado_sesion, imprimir_tabla,
    pedir_entero_positivo, pedir_fecha,
    _ancho, _prefijo, OperacionCancelada
)


class AdminConsultas:
    def __init__(self, usuario, reporte_srv, empleado_srv, producto_srv, reportes):
        self.usuario = usuario
        self.reporte_srv = reporte_srv
        self.empleado_srv = empleado_srv
        self.producto_srv = producto_srv
        self.reportes = reportes

    def menu(self):
        opciones = [
            "C1 - Detalle de venta por folio",
            "C2 - Detalle de compra por folio",
            "C3 - Mermas",
            "C4 - Ventas por empleado y fecha",
            "C5 - Insumos de la receta de un producto",
            "<< Volver al Menu Admin",
        ]
        while True:
            enc = imprimir_encabezado_sesion(
                self.usuario,
                breadcrumb=["Inicio", "Panel Admin", "Consultas y Reportes"]
            )
            idx = seleccionar_con_flechas("CONSULTAS Y REPORTES", opciones, enc)
            if idx == 0:
                self._consulta_1()
            elif idx == 1:
                self._consulta_2()
            elif idx == 2:
                self._consulta_3()
            elif idx == 3:
                self._consulta_4()
            elif idx == 4:
                self._consulta_5()
            elif idx == 5:
                return

    def _consulta_1(self):
        while True:
            limpiar_pantalla()
            print(imprimir_encabezado_sesion(
                self.usuario,
                breadcrumb=["Inicio", "Panel Admin", "Consultas", "C1 - Detalle Venta"]
            ))
            print(f"\n  {Color.titulo('C1 - DETALLE DE VENTA')}\n")
            try:
                ventas = self.reporte_srv.listar_ventas_recientes(30)
                if ventas:
                    cols = ["Folio", "Fecha", "Barista", "Cliente", "Metodo", "Total"]
                    filas = [(v["folio"], v["fecha"], v["barista"], v["cliente"],
                              v["metodo"], f"${v['total']:.2f}") for v in ventas]
                    imprimir_tabla("Ventas recientes (ultimas 30)", cols, filas)
                folio = pedir_entero_positivo(prompt="Numero de folio de venta", ejemplo="1")
                enc_venta, lineas = self.reporte_srv.consulta_1_detalle_venta(folio)
                if not enc_venta:
                    raise ValueError("Venta no encontrada.")

                limpiar_pantalla()
                print(imprimir_encabezado_sesion(
                    self.usuario,
                    breadcrumb=["Inicio", "Panel Admin", "Consultas", f"Venta #{folio}"]
                ))
                pfx = _prefijo(_ancho())
                print(f"\n{pfx}  {Color.titulo('DETALLE VENTA #' + str(folio))}\n")
                print(f"{pfx}  Fecha:        {enc_venta['fecha']}")
                print(f"{pfx}  Cliente:      {enc_venta['nombreCliente']}")
                print(f"{pfx}  Empleado:     {enc_venta['empleado']}")
                print(f"{pfx}  Metodo pago:  {enc_venta['metodoPago']}")
                print(f"{pfx}  Total:        {Color.CARAMELO}${enc_venta['total']:.2f}{Color.RESET}")
                if lineas:
                    cols = ["Codigo", "Producto", "Precio", "Cant.", "Subtotal", "IVA", "Total"]
                    filas = [(l["codigo"], l["nombre"], f"${l['precio']:.2f}",
                              l["cantidad"], f"${l['subtotal']:.2f}",
                              f"${l['totalIVA']:.2f}", f"${l['total']:.2f}") for l in lineas]
                    imprimir_tabla("Productos vendidos", cols, filas)
                    self.reportes.reporte_generico(
                        f"Reporte_C1_Venta_{folio}",
                        "DETALLE VENTA",
                        ["Codigo", "Producto", "Precio", "Cant.", "Subtotal", "IVA", "Total"],
                        [[l["codigo"], l["nombre"], f"${l['precio']:.2f}", l["cantidad"],
                          f"${l['subtotal']:.2f}", f"${l['totalIVA']:.2f}", f"${l['total']:.2f}"]
                         for l in lineas],
                        subtitulo=f"Folio #{folio}",
                        encabezado_extra=f"Cliente: {enc_venta['nombreCliente']}  Empleado: {enc_venta['empleado']}"
                    )
                else:
                    print(Color.aviso("Esta venta no tiene productos registrados. No se genero reporte."))
                pausar()
                return
            except OperacionCancelada:
                return
            except Exception as error:
                print(Color.error(str(error)))
                pausar()

    def _consulta_2(self):
        while True:
            limpiar_pantalla()
            print(imprimir_encabezado_sesion(
                self.usuario,
                breadcrumb=["Inicio", "Panel Admin", "Consultas", "C2 - Detalle Compra"]
            ))
            print(f"\n  {Color.titulo('C2 - DETALLE DE COMPRA')}\n")
            try:
                folio = pedir_entero_positivo(prompt="Numero de folio de compra", ejemplo="1")
                enc_compra, lineas = self.reporte_srv.consulta_2_detalle_compra(folio)
                if not enc_compra:
                    raise ValueError("Compra no encontrada.")
                limpiar_pantalla()
                print(imprimir_encabezado_sesion(
                    self.usuario,
                    breadcrumb=["Inicio", "Panel Admin", "Consultas", f"Compra #{folio}"]
                ))
                pfx = _prefijo(_ancho())
                print(f"\n{pfx}  {Color.titulo('DETALLE COMPRA #' + str(folio))}\n")
                print(f"{pfx}  Fecha:      {enc_compra['fecha']}")
                print(f"{pfx}  Proveedor:  {enc_compra['proveedor']}  ({enc_compra['ciudad']})")
                print(f"{pfx}  Total:      {Color.CARAMELO}${enc_compra['total']:.2f}{Color.RESET}")
                if lineas:
                    cols = ["Codigo", "Insumo", "Precio U.", "Cant.", "Subtotal", "IVA", "Total"]
                    filas = [(l["codigo"], l["nombre"], f"${l['precio']:.2f}",
                              l["cantidad"], f"${l['subtotal']:.2f}",
                              f"${l['totalIVA']:.2f}", f"${l['total']:.2f}") for l in lineas]
                    imprimir_tabla("Insumos comprados", cols, filas)
                self.reportes.reporte_generico(
                    f"Reporte_C2_Compra_{folio}",
                    "DETALLE COMPRA",
                    ["Codigo", "Insumo", "Precio U.", "Cant.", "Subtotal", "IVA", "Total"],
                    [[l["codigo"], l["nombre"], f"${l['precio']:.2f}", l["cantidad"],
                      f"${l['subtotal']:.2f}", f"${l['totalIVA']:.2f}", f"${l['total']:.2f}"]
                     for l in (lineas or [])],
                    subtitulo=f"Folio #{folio}",
                    encabezado_extra=f"Proveedor: {enc_compra['proveedor']}  Ciudad: {enc_compra['ciudad']}"
                )
                pausar()
                return
            except OperacionCancelada:
                return
            except Exception as error:
                print(Color.error(str(error)))
                pausar()

    def _consulta_3(self):
        enc = imprimir_encabezado_sesion(
            self.usuario,
            breadcrumb=["Inicio", "Panel Admin", "Consultas", "C3 - Mermas"]
        )
        opts = [
            "Ver mermas de los ultimos 7 dias",
            "Buscar merma por folio",
            "<< Cancelar y regresar",
        ]
        idx = seleccionar_con_flechas("C3 - MERMAS", opts, enc)
        if idx == 2:
            return

        cols = ["Folio", "Fecha", "Insumo", "Cantidad", "Tipo", "Motivo"]

        if idx == 0:
            mermas = self.reporte_srv.consulta_3_mermas_semana()
            filas = []
            for m in mermas:
                filas.append((m["codigo"], m["fecha"], m["insumo"], m["cantidad"],
                               m["tipo_merma"], m["motivo"]))
            limpiar_pantalla()
            print(imprimir_encabezado_sesion(
                self.usuario,
                breadcrumb=["Inicio", "Panel Admin", "Consultas", "C3 - Mermas 7 dias"]
            ))
            imprimir_tabla("C3 - MERMAS ULTIMOS 7 DIAS", cols, filas)
            self.reportes.reporte_generico(
                "Reporte_C3_Mermas_Semana",
                "MERMAS ULTIMOS 7 DIAS",
                cols, filas,
                subtitulo=datetime.datetime.now().strftime("%d/%m/%Y")
            )
            pausar()

        elif idx == 1:
            while True:
                limpiar_pantalla()
                print(imprimir_encabezado_sesion(
                    self.usuario,
                    breadcrumb=["Inicio", "Panel Admin", "Consultas", "C3 - Merma por folio"]
                ))
                try:
                    folio = pedir_entero_positivo(prompt="Numero de folio de merma", ejemplo="3")
                    merma = self.reporte_srv.consulta_3_merma_por_folio(folio)
                    if not merma:
                        raise ValueError(f"No se encontro la merma con folio {folio}.")
                    limpiar_pantalla()
                    print(imprimir_encabezado_sesion(
                        self.usuario,
                        breadcrumb=["Inicio", "Panel Admin", "Consultas", f"C3 - Merma #{folio}"]
                    ))
                    filas = [(merma["codigo"], merma["fecha"], merma["insumo"], merma["cantidad"],
                              merma["tipo_merma"], merma["motivo"])]
                    imprimir_tabla(f"C3 - MERMA #{folio}", cols, filas)
                    self.reportes.reporte_generico(
                        f"Reporte_C3_Merma_{folio}",
                        "DETALLE MERMA",
                        cols, filas,
                        subtitulo=f"Folio #{folio}"
                    )
                    pausar()
                    return
                except OperacionCancelada:
                    return
                except Exception as error:
                    print(Color.error(str(error)))
                    pausar()

    def _consulta_4(self):
        while True:
            limpiar_pantalla()
            try:
                empleados = self.empleado_srv.listar_empleados()
                if not empleados:
                    print(Color.aviso("No hay empleados."))
                    pausar()
                    return
                enc = imprimir_encabezado_sesion(
                    self.usuario,
                    breadcrumb=["Inicio", "Panel Admin", "Consultas", "C4 - Ventas por empleado"]
                )
                opts = [f"{e['num']:>4}  {e['nombre']:<30} {e['rol']}"
                        for e in empleados] + ["<< Cancelar y regresar"]
                idx = seleccionar_con_flechas("C4 - Selecciona empleado", opts, enc)
                if idx == len(empleados):
                    return
                emp = empleados[idx]
                limpiar_pantalla()
                print(imprimir_encabezado_sesion(
                    self.usuario,
                    breadcrumb=["Inicio", "Panel Admin", "Consultas", "C4", emp["nombre"]]
                ))
                pfx = _prefijo(_ancho())
                print(f"\n{pfx}  {Color.titulo('C4 - VENTAS POR EMPLEADO Y FECHA')}")
                print(f"{pfx}  Empleado: {Color.CARAMELO}{emp['nombre']}{Color.RESET}\n")
                while True:
                    try:
                        fecha = pedir_fecha()
                        break
                    except ValueError as error:
                        print(Color.error(str(error)))
                        pausar()
                ventas = self.reporte_srv.consulta_4_ventas_por_empleado_fecha(emp["num"], fecha)
                cols = ["Folio", "Fecha", "Cliente", "Metodo", "Total"]
                filas = [(v["folio"], v["fecha"], v["nombreCliente"], v["metodoPago"],
                          f"${v['total']:.2f}") for v in ventas]
                limpiar_pantalla()
                print(imprimir_encabezado_sesion(
                    self.usuario,
                    breadcrumb=["Inicio", "Panel Admin", "Consultas", "C4", emp["nombre"], fecha]
                ))
                imprimir_tabla(f"C4 - VENTAS DE {emp['nombre']} EL {fecha}", cols, filas)
                self.reportes.reporte_generico(
                    f"Reporte_C4_{emp['num']}_{fecha.replace('-', '')}",
                    "VENTAS POR EMPLEADO",
                    cols, filas,
                    subtitulo=f"{emp['nombre']} | {fecha}"
                )
                pausar()
                return
            except OperacionCancelada:
                return
            except Exception as error:
                print(Color.error(str(error)))
                pausar()

    def _consulta_5(self):
        productos: Any = self.producto_srv.listar_todos_productos()
        if not productos:
            print(Color.aviso(texto="No hay productos."))
            pausar()
            return
        enc: str = imprimir_encabezado_sesion(
            empleado=self.usuario,
            breadcrumb=["Inicio", "Panel Admin", "Consultas", "C5 - Receta"]
        )
        opts: list[str] = [f"{p['codigo']:<10} {p['nombre']:<30} {p['categoria']}"
                for p in productos] + ["<< Cancelar y regresar"]
        idx = seleccionar_con_flechas("C5 - Insumos de la receta - Selecciona producto", opts, enc)
        if idx == len(productos):
            return
        prod = productos[idx]
        receta = self.reporte_srv.consulta_5_insumos_receta(prod["codigo"])
        cols = ["Codigo", "Insumo", "Requerido", "Stock Actual", "Unidad"]
        filas = [(r["insumo_codigo"], r["nombre"], r["requerido"],
                  r["stockActual"], r["abreviatura"]) for r in receta]
        limpiar_pantalla()
        print(imprimir_encabezado_sesion(
            self.usuario,
            breadcrumb=["Inicio", "Panel Admin", "Consultas", "C5", prod["nombre"]]
        ))
        imprimir_tabla(f"C5 - RECETA: {prod['nombre']}", cols, filas)
        self.reportes.reporte_generico(
            f"Reporte_C5_Receta_{prod['codigo']}",
            "INSUMOS DE RECETA",
            cols, filas,
            subtitulo=prod["nombre"]
        )
        pausar()
