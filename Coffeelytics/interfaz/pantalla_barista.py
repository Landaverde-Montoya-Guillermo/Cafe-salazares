from interfaz.estilos import Color
from consola_ui import (
    limpiar_pantalla, pausar, seleccionar_con_flechas,
    imprimir_encabezado_sesion, imprimir_tabla,
    pedir_numero_positivo, pedir_motivo, pedir_cantidad_carrito,
    _ancho, _prefijo, OperacionCancelada
)
from entidades.carrito_venta import CarritoVenta
from interfaz.modal_cobro import ModalCobro


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
                self._catalogo_productos(carrito)
            elif idx == 1:
                self._gestionar_carrito(carrito)
            elif idx == 2:
                self._registrar_merma()
            elif idx == 3:
                self._surtir_mesa()
            elif idx == 4:
                if self._desactivar_mi_cuenta():
                    return
            elif idx == 5:
                return

    def _catalogo_productos(self, carrito):
        while True:
            categorias = self.producto_srv.obtener_categorias_con_conteo()
            if not categorias:
                print(Color.aviso("No hay categorias disponibles."))
                pausar()
                return
            opciones_cat = [
                f"{c['nombre']:<24}  Disponibles: {c['disponibles']}/{c['total']}"
                for c in categorias
            ] + ["<< Volver al Menu Barista"]
            enc = imprimir_encabezado_sesion(
                self.usuario,
                breadcrumb=["Inicio", "Panel Barista", "Catalogo"]
            )
            idx = seleccionar_con_flechas("CATALOGO - Selecciona categoria", opciones_cat, enc)
            if idx == len(categorias):
                return
            self._listar_productos_categoria(categorias[idx], carrito)

    def _listar_productos_categoria(self, cat, carrito):
        while True:
            productos = self.producto_srv.obtener_productos_por_categoria(cat["codigo"])
            if not productos:
                print(Color.aviso("Esta categoria no tiene productos."))
                pausar()
                return
            etiquetas = []
            for p in productos:
                disp = f"{Color.VERDE_OK}[Disponible]{Color.RESET}" if p.esta_disponible() \
                       else f"{Color.ROJO_ALT}[No disponible]{Color.RESET}"
                etiquetas.append(f"{p.nombre:<30}  ${p.precio:>6.2f}  {disp}")
            etiquetas.append("<< Volver al Catalogo")
            enc = imprimir_encabezado_sesion(
                self.usuario,
                breadcrumb=["Inicio", "Panel Barista", "Catalogo", cat["nombre"]]
            )
            idx = seleccionar_con_flechas(f"CATEGORIA: {cat['nombre']}", etiquetas, enc)
            if idx == len(productos):
                return
            self._previsualizar_y_agregar(productos[idx], carrito)

    def _previsualizar_y_agregar(self, producto, carrito):
        limpiar_pantalla()
        enc = imprimir_encabezado_sesion(
            self.usuario,
            breadcrumb=["Inicio", "Panel Barista", "Catalogo", "Producto"]
        )
        print(enc)
        print(f"\n  {Color.titulo(producto.nombre)}")
        print(f"  Precio: {Color.CARAMELO}${producto.precio:.2f}{Color.RESET}")
        est = f"{Color.VERDE_OK}Disponible{Color.RESET}" if producto.esta_disponible() \
              else f"{Color.ROJO_ALT}No disponible{Color.RESET}"
        print(f"  Estatus: {est}")

        receta = self.producto_srv.obtener_receta_producto(producto.codigo)
        if receta:
            cols = ["Insumo", "Requerido", "Stock Actual", "Unidad"]
            filas = [(r["nombre"], r["requerido"], r["stockActual"], r["abreviatura"])
                     for r in receta]
            imprimir_tabla("Receta / Insumos en vivo", cols, filas)
        else:
            print(Color.info("Este producto no tiene receta registrada."))

        if not producto.esta_disponible():
            print(Color.aviso("Producto no disponible. No se puede agregar al carrito."))
            pausar()
            return

        try:
            cant = pedir_cantidad_carrito(producto.nombre)
        except OperacionCancelada:
            return
        carrito.agregar_producto(producto, cant)
        print(Color.ok(f"{cant}x {producto.nombre} agregado al carrito."))
        pausar()

    def _gestionar_carrito(self, carrito):
        while True:
            limpiar_pantalla()
            enc = imprimir_encabezado_sesion(
                self.usuario,
                breadcrumb=["Inicio", "Panel Barista", "Carrito"]
            )
            print(enc)
            if not carrito.items:
                print(Color.aviso("\n  El carrito esta vacio."))
                pausar()
                return
            cols = ["Codigo", "Producto", "Precio", "Cant.", "Total"]
            filas = []
            for item in carrito.items.values():
                p = item["producto"]
                filas.append((p.codigo, p.nombre, f"${p.precio:.2f}",
                              item["cantidad"], f"${p.precio * item['cantidad']:.2f}"))
            imprimir_tabla("CARRITO ACTUAL", cols, filas)
            sub = carrito.calcular_subtotal()
            iva = carrito.calcular_iva()
            tot = carrito.calcular_total()
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
                modal = ModalCobro(self.usuario, carrito, self.venta_srv, self.reportes)
                if modal.procesar():
                    return
            elif idx == 1:
                self._quitar_del_carrito(carrito)
            elif idx == 2:
                carrito.vaciar()
                print(Color.ok("Carrito vaciado."))
                pausar()
                return
            elif idx == 3:
                return

    def _quitar_del_carrito(self, carrito):
        codigos = list(carrito.items.keys())
        nombres = [f"{carrito.items[c]['producto'].nombre} x{carrito.items[c]['cantidad']}"
                   for c in codigos] + ["<< Cancelar"]
        enc = imprimir_encabezado_sesion(
            self.usuario,
            breadcrumb=["Inicio", "Panel Barista", "Carrito", "Quitar producto"]
        )
        idx = seleccionar_con_flechas("Selecciona producto a quitar", nombres, enc)
        if idx < len(codigos):
            nombre_p = carrito.items[codigos[idx]]["producto"].nombre
            carrito.quitar_producto(codigos[idx])
            print(Color.ok(f"'{nombre_p}' eliminado del carrito."))
            pausar()

    def _registrar_merma(self):
        insumos = self.inventario_srv.listar_todos_insumos()
        tipos_merma = self.merma_srv.listar_tipos_merma()
        if not insumos or not tipos_merma:
            print(Color.aviso("No hay insumos o tipos de merma registrados."))
            pausar()
            return

        enc = imprimir_encabezado_sesion(
            self.usuario,
            breadcrumb=["Inicio", "Panel Barista", "Registrar Merma", "Selecciona insumo"]
        )
        opts_i = [f"{i['codigo']:<12} {i['nombre']:<30} Stock: {i['stockActual']} {i['abreviatura']}"
                  for i in insumos] + ["<< Cancelar y regresar"]
        idx_i = seleccionar_con_flechas("REGISTRAR MERMA - Selecciona insumo", opts_i, enc)
        if idx_i == len(insumos):
            return
        ins = insumos[idx_i]

        enc = imprimir_encabezado_sesion(
            self.usuario,
            breadcrumb=["Inicio", "Panel Barista", "Registrar Merma", "Tipo de merma"]
        )
        opts_t = [t["nombre"] for t in tipos_merma] + ["<< Cancelar y regresar"]
        idx_t = seleccionar_con_flechas("Tipo de merma", opts_t, enc)
        if idx_t == len(tipos_merma):
            return
        tipo = tipos_merma[idx_t]

        limpiar_pantalla()
        print(imprimir_encabezado_sesion(
            self.usuario,
            breadcrumb=["Inicio", "Panel Barista", "Registrar Merma"]
        ))
        pfx = _prefijo(_ancho())
        print(f"\n{pfx}  {Color.titulo('REGISTRAR MERMA')}")
        print(f"{pfx}  Insumo: {Color.CARAMELO}{ins['nombre']}{Color.RESET}  "
              f"Stock actual: {ins['stockActual']} {ins['abreviatura']}")
        print(f"{pfx}  Tipo:   {Color.CARAMELO}{tipo['nombre']}{Color.RESET}\n")

        try:
            cantidad = pedir_numero_positivo(
                prompt="Cantidad a dar de baja",
                unidad=ins["abreviatura"],
                ejemplo=f"{min(1, float(ins['stockActual'])):.1f}",
                stock_max=float(ins["stockActual"]),
                nombre_campo="cantidad de merma"
            )
            motivo = pedir_motivo(ejemplo="Derrame accidental en barra")
        except OperacionCancelada:
            print(Color.aviso("Operacion cancelada. No se registro la merma."))
            pausar()
            return

        ok, msg = self.merma_srv.registrar_merma(ins["codigo"], tipo["codigo"], cantidad, motivo)
        print(Color.ok(msg) if ok else Color.error(msg))
        pausar()

    def _surtir_mesa(self):
        insumos = self.inventario_srv.listar_todos_insumos()
        if not insumos:
            print(Color.aviso("No hay insumos registrados."))
            pausar()
            return
        enc = imprimir_encabezado_sesion(
            self.usuario,
            breadcrumb=["Inicio", "Panel Barista", "Surtir Mesa"]
        )
        opts = [f"{i['codigo']:<12} {i['nombre']:<30} Stock: {i['stockActual']} {i['abreviatura']}"
                for i in insumos] + ["<< Cancelar y regresar"]
        idx = seleccionar_con_flechas("SURTIR MESA - Selecciona insumo", opts, enc)
        if idx == len(insumos):
            return
        ins = insumos[idx]

        limpiar_pantalla()
        print(imprimir_encabezado_sesion(
            self.usuario,
            breadcrumb=["Inicio", "Panel Barista", "Surtir Mesa", ins["nombre"]]
        ))
        pfx = _prefijo(_ancho())
        print(f"\n{pfx}  {Color.titulo('SURTIR MESA DE CONSUMIBLES')}")
        print(f"{pfx}  Insumo: {Color.CARAMELO}{ins['nombre']}{Color.RESET}  "
              f"Stock disponible: {ins['stockActual']} {ins['abreviatura']}\n")

        try:
            cantidad = pedir_numero_positivo(
                prompt="Cantidad a surtir",
                unidad=ins["abreviatura"],
                ejemplo="50",
                stock_max=float(ins["stockActual"]),
                nombre_campo="cantidad a surtir"
            )
        except OperacionCancelada:
            print(Color.aviso("Operacion cancelada. No se surtio la mesa."))
            pausar()
            return

        ok, msg = self.despacho_srv.surtir_mesa_consumibles(ins["codigo"], cantidad)
        print(Color.ok(msg) if ok else Color.error(msg))
        pausar()

    def _desactivar_mi_cuenta(self):
        limpiar_pantalla()
        print(imprimir_encabezado_sesion(
            self.usuario,
            breadcrumb=["Inicio", "Panel Barista", "Mi Cuenta"]
        ))
        print(Color.aviso("\n  ATENCION: Esta accion desactivara tu cuenta y cerrara la sesion."))
        enc = imprimir_encabezado_sesion(
            self.usuario,
            breadcrumb=["Inicio", "Panel Barista", "Mi Cuenta", "Desactivar"]
        )
        opts = ["Confirmar - desactivar mi cuenta", "<< Cancelar - no desactivar mi cuenta"]
        idx = seleccionar_con_flechas("Desactivar cuenta propia", opts, enc)
        if idx == 0:
            ok = self.empleado_srv.desactivar_cuenta(self.usuario.num)
            if ok:
                print(Color.ok("Cuenta desactivada. Sesion cerrada."))
                pausar()
                return True
            else:
                print(Color.error("No se pudo desactivar la cuenta."))
                pausar()
        return False