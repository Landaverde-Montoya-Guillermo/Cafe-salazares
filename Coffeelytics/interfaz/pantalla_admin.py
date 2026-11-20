import datetime
from interfaz.estilos import Color
from consola_ui import (
    limpiar_pantalla, pausar, seleccionar_con_flechas,
    imprimir_encabezado_sesion, imprimir_tabla,
    pedir_correo, pedir_codigo, pedir_nombre_propio, pedir_rfc,
    pedir_telefono, pedir_numero_positivo, pedir_precio,
    pedir_fecha, pedir_entero_positivo,
    _imprimir_guia, _input_centrado, _ancho, _prefijo, OperacionCancelada
)


def _es_admin_principal(usuario):
    """True solo para la cuenta fundadora num==1."""
    return usuario is not None and usuario.es_admin() and usuario.num == 1


def _acceso_denegado():
    print(Color.aviso("Acceso restringido: requiere privilegios de Administrador Principal."))
    pausar()
    return False


class PantallaAdmin:
    def __init__(self, usuario, servicios, reportes):
        self.usuario = usuario
        self.inventario_srv = servicios["inventario"]
        self.reporte_srv = servicios["reporte"]
        self.compra_srv = servicios["compra"]
        self.producto_srv = servicios["producto"]
        self.empleado_srv = servicios["empleado"]
        self.reportes = reportes

    def mostrar(self):
        es_principal = _es_admin_principal(self.usuario)
        marca = "" if es_principal else "  [Solo Admin Principal]"
        opciones = [
            "Alertas de stock bajo",
            f"Resumen financiero{marca}",
            "Registrar compra a proveedor",
            "Registrar nuevo insumo",
            f"Asignar insumo a receta de producto{marca}",
            f"Alta de nuevo producto / bebida festiva{marca}",
            "Consultas de reportes (exportar .txt)",
            "Gestion de empleados (CRUD)",
            "<< Cerrar sesion y volver al Inicio",
        ]
        while True:
            enc = imprimir_encabezado_sesion(
                self.usuario,
                breadcrumb=["Inicio", "Panel Admin"]
            )
            idx = seleccionar_con_flechas("MENU ADMINISTRADOR", opciones, enc)
            if idx == 0:
                self._alertas_stock()
            elif idx == 1:
                if not es_principal:
                    _acceso_denegado()
                else:
                    self._resumen_financiero()
            elif idx == 2:
                self._registrar_compra()
            elif idx == 3:
                self._registrar_insumo()
            elif idx == 4:
                if not es_principal:
                    _acceso_denegado()
                else:
                    self._asignar_insumo_receta()
            elif idx == 5:
                if not es_principal:
                    _acceso_denegado()
                else:
                    self._alta_producto()
            elif idx == 6:
                self._menu_consultas()
            elif idx == 7:
                self._gestion_empleados()
            elif idx == 8:
                return

    def _alertas_stock(self):
        alertas = self.inventario_srv.obtener_alertas_stock_bajo()
        cols = ["Codigo", "Insumo", "Stock", "Min", "Unidad", "Proveedor", "Telefono", "Ciudad"]
        filas = [(a["codigo"], a["nombre"], a["stockActual"], a["stockMin"],
                  a["abreviatura"], a["proveedor"], a["telefono"], a["ciudad"])
                 for a in alertas]
        limpiar_pantalla()
        print(imprimir_encabezado_sesion(
            self.usuario,
            breadcrumb=["Inicio", "Panel Admin", "Alertas de Stock"]
        ))
        if not alertas:
            print(Color.ok("\n  Todos los insumos tienen stock suficiente."))
        else:
            print(Color.aviso(f"\n  {len(alertas)} insumo(s) con stock bajo:\n"))
            imprimir_tabla("ALERTAS DE STOCK BAJO", cols, filas)
        pausar()

    def _resumen_financiero(self):
        periodos = ["HOY", "SEMANA", "MES", "ANIO"]
        descs = ["Hoy", "Esta semana", "Este mes", "Este anio"]
        enc = imprimir_encabezado_sesion(
            self.usuario,
            breadcrumb=["Inicio", "Panel Admin", "Resumen Financiero"]
        )
        opts = descs + ["<< Volver al Menu Admin"]
        idx = seleccionar_con_flechas("RESUMEN FINANCIERO - Periodo", opts, enc)
        if idx == len(periodos):
            return
        periodo = periodos[idx]
        datos = self.reporte_srv.obtener_resumen_financiero(periodo)
        limpiar_pantalla()
        print(imprimir_encabezado_sesion(
            self.usuario,
            breadcrumb=["Inicio", "Panel Admin", "Resumen Financiero", descs[idx]]
        ))
        ancho_ui = _ancho()
        pfx = _prefijo(ancho_ui)
        sep = pfx + Color.aplicar(Color.CARAMELO, "═" * min(56, ancho_ui - 4))
        print(f"\n{sep}")
        print(f"{pfx}  {Color.titulo('RESUMEN FINANCIERO')}  [{descs[idx].upper()}]")
        print(sep)
        print(f"{pfx}  Ventas realizadas:  {Color.CARAMELO}{datos['num_ventas']}{Color.RESET}")
        print(f"{pfx}  Ingresos totales:   {Color.VERDE_OK}${datos['ingresos']:,.2f}{Color.RESET}")
        print(f"{pfx}  Gastos en insumos:  {Color.ROJO_ALT}${datos['gastos_insumos']:,.2f}{Color.RESET}")
        color_gan = Color.VERDE_OK if datos['ganancia_bruta'] >= 0 else Color.ROJO_ALT
        print(f"{pfx}  Ganancia bruta:     {Color.BOLD}{color_gan}${datos['ganancia_bruta']:,.2f}{Color.RESET}")
        print(sep)
        pausar()

    def _registrar_compra(self):
        proveedores = self.compra_srv.listar_proveedores()
        insumos = self.inventario_srv.listar_todos_insumos()
        if not proveedores or not insumos:
            print(Color.aviso("No hay proveedores o insumos registrados."))
            pausar()
            return

        enc = imprimir_encabezado_sesion(
            self.usuario,
            breadcrumb=["Inicio", "Panel Admin", "Registrar Compra", "Proveedor"]
        )
        opts = [f"{p['codigo']:<10} {p['nombre']:<30} {p['ciudad']}"
                for p in proveedores] + ["<< Cancelar y regresar"]
        idx = seleccionar_con_flechas("REGISTRAR COMPRA - Selecciona proveedor", opts, enc)
        if idx == len(proveedores):
            return
        prov = proveedores[idx]

        enc = imprimir_encabezado_sesion(
            self.usuario,
            breadcrumb=["Inicio", "Panel Admin", "Registrar Compra", "Insumo"]
        )
        opts2 = [f"{i['codigo']:<12} {i['nombre']:<30} Stock: {i['stockActual']} {i['abreviatura']}"
                 for i in insumos] + ["<< Cancelar y regresar"]
        idx2 = seleccionar_con_flechas("Selecciona insumo a comprar", opts2, enc)
        if idx2 == len(insumos):
            return
        ins = insumos[idx2]

        limpiar_pantalla()
        print(imprimir_encabezado_sesion(
            self.usuario,
            breadcrumb=["Inicio", "Panel Admin", "Registrar Compra", "Datos"]
        ))
        pfx = _prefijo(_ancho())
        print(f"\n{pfx}  {Color.titulo('REGISTRAR COMPRA A PROVEEDOR')}")
        print(f"{pfx}  Proveedor: {Color.CARAMELO}{prov['nombre']}{Color.RESET}  "
              f"Ciudad: {prov['ciudad']}")
        print(f"{pfx}  Insumo:    {Color.CARAMELO}{ins['nombre']}{Color.RESET}\n")
        print(Color.info("El IVA se calculara automaticamente: 8% si el proveedor es de frontera, "
                         "16% si es del interior del pais."))
        print()

        try:
            cantidad = pedir_numero_positivo(
                prompt="Cantidad comprada",
                unidad=ins["abreviatura"],
                ejemplo="1000",
                nombre_campo="cantidad"
            )
            precio_unit = pedir_precio(ejemplo="0.85")
        except OperacionCancelada:
            print(Color.aviso("Operacion cancelada. No se registro la compra."))
            pausar()
            return

        # Regla delegada al servicio
        tasa, sub, iva_v, total = self.compra_srv.calcular_totales_previos(
            prov.get("ciudad", ""), cantidad, precio_unit
        )
        print(f"\n{pfx}  Subtotal: ${sub:.2f}  IVA ({int(tasa*100)}%): ${iva_v:.2f}  "
              f"Total: {Color.CARAMELO}${total:.2f}{Color.RESET}")

        metodos = [("EFEC", "Efectivo"), ("TARJ", "Tarjeta"), ("SPEI", "Transferencia SPEI")]
        enc3 = imprimir_encabezado_sesion(
            self.usuario,
            breadcrumb=["Inicio", "Panel Admin", "Registrar Compra", "Metodo de pago"]
        )
        idx_m = seleccionar_con_flechas("Metodo de pago al proveedor", [m[1] for m in metodos], enc3)
        cod_pago = metodos[idx_m][0]

        ok, msg = self.compra_srv.registrar_compra_proveedor(
            prov["codigo"], ins["codigo"], cantidad, precio_unit,
            cod_pago, self.usuario.num
        )
        print(Color.ok(msg) if ok else Color.error(msg))
        pausar()

    def _registrar_insumo(self):
        limpiar_pantalla()
        print(imprimir_encabezado_sesion(
            self.usuario,
            breadcrumb=["Inicio", "Panel Admin", "Registrar Insumo"]
        ))
        pfx = _prefijo(_ancho())
        print(f"\n{pfx}  {Color.titulo('REGISTRAR NUEVO INSUMO EN ALMACEN')}\n")
        print(Color.info("Completa los siguientes datos para dar de alta el insumo en el inventario."))
        print()

        try:
            codigo = pedir_codigo(prompt="Codigo del insumo", longitud_max=6, ejemplo="INS008")
            nombre = pedir_nombre_propio(prompt="Nombre del insumo", ejemplo="Leche Entera")
            stock_ini = pedir_numero_positivo(prompt="Stock inicial", unidad="", ejemplo="500",
                                              nombre_campo="stock inicial")
            stock_min = pedir_numero_positivo(prompt="Stock minimo de alerta", unidad="",
                                              ejemplo="100", nombre_campo="stock minimo")

            _imprimir_guia(
                "Seccion del almacen donde se guarda el insumo",
                "Texto libre, maximo 30 caracteres",
                "Refrigeracion  o  Bodega seca",
                "Permite ubicar fisicamente el insumo en almacen."
            )
            raw_sec = _input_centrado("Seccion de almacen")
            if raw_sec.strip().upper() in ("0", "CANCELAR"):
                raise OperacionCancelada()
            seccion = raw_sec.strip().title() or "General"

            _imprimir_guia(
                "Codigo de unidad de medida",
                "Codigo corto en mayusculas registrado en la BD",
                "KG  o  LT  o  PZ  o  ML",
                "Debe coincidir con un codigo existente en la tabla unidad_medida."
            )
            raw_uni = _input_centrado("Codigo de unidad (ej. KG, LT, PZ)")
            if raw_uni.strip().upper() in ("0", "CANCELAR"):
                raise OperacionCancelada()
            unidad = raw_uni.strip().upper() or "KG"

            _imprimir_guia(
                "Estante o ubicacion exacta dentro de la seccion",
                "Texto libre, maximo 20 caracteres",
                "Estante-A3  o  Frio-2",
                "Referencia visual para el personal de almacen."
            )
            raw_est = _input_centrado("Estante / ubicacion")
            if raw_est.strip().upper() in ("0", "CANCELAR"):
                raise OperacionCancelada()
            estante = raw_est.strip() or "General"

            _imprimir_guia(
                "Categoria del insumo en el almacen",
                "Codigo de categoria registrado en la BD",
                "CAFE  o  LACTE  o  ENDULZANTE  o  CONSUMIB",
                "Debe coincidir con un codigo existente en categoria_insumo."
            )
            raw_cat = _input_centrado("Categoria de insumo")
            if raw_cat.strip().upper() in ("0", "CANCELAR"):
                raise OperacionCancelada()
            cat_ins = raw_cat.strip().upper() or "CAFE"

        except OperacionCancelada:
            print(Color.aviso("Operacion cancelada. No se registro el insumo."))
            pausar()
            return

        ok, msg = self.inventario_srv.registrar_insumo(
            codigo, nombre, stock_ini, stock_min, seccion, unidad, estante, cat_ins
        )
        print(Color.ok(msg) if ok else Color.error(msg))
        pausar()

    def _asignar_insumo_receta(self):
        productos = self.producto_srv.listar_todos_productos()
        insumos = self.inventario_srv.listar_todos_insumos()
        if not productos or not insumos:
            print(Color.aviso("No hay productos o insumos suficientes."))
            pausar()
            return

        enc = imprimir_encabezado_sesion(
            self.usuario,
            breadcrumb=["Inicio", "Panel Admin", "Asignar Insumo a Receta", "Producto"]
        )
        opts = [f"{p['codigo']:<10} {p['nombre']:<30} ${p['precio']:.2f}  {p['categoria']}"
                for p in productos] + ["<< Cancelar y regresar"]
        idx = seleccionar_con_flechas("ASIGNAR INSUMO A RECETA - Producto", opts, enc)
        if idx == len(productos):
            return
        prod = productos[idx]

        enc2 = imprimir_encabezado_sesion(
            self.usuario,
            breadcrumb=["Inicio", "Panel Admin", "Asignar Insumo a Receta", "Insumo"]
        )
        opts2 = [f"{i['codigo']:<12} {i['nombre']:<30} Stock: {i['stockActual']} {i['abreviatura']}"
                 for i in insumos] + ["<< Cancelar y regresar"]
        idx2 = seleccionar_con_flechas("Selecciona insumo a asignar a la receta", opts2, enc2)
        if idx2 == len(insumos):
            return
        ins = insumos[idx2]

        limpiar_pantalla()
        print(imprimir_encabezado_sesion(
            self.usuario,
            breadcrumb=["Inicio", "Panel Admin", "Asignar Insumo a Receta", "Cantidad"]
        ))
        pfx = _prefijo(_ancho())
        print(f"\n{pfx}  {Color.titulo('ASIGNAR INSUMO A RECETA')}")
        print(f"{pfx}  Producto: {Color.CARAMELO}{prod['nombre']}{Color.RESET}")
        print(f"{pfx}  Insumo:   {Color.CARAMELO}{ins['nombre']}{Color.RESET}  ({ins['abreviatura']})\n")
        print(Color.info("La cantidad indica cuanto de este insumo se consume por UNIDAD vendida del producto."))
        print()

        try:
            cantidad = pedir_numero_positivo(
                prompt="Cantidad requerida por unidad de producto",
                unidad=ins["abreviatura"],
                ejemplo="250",
                nombre_campo="cantidad en receta"
            )
        except OperacionCancelada:
            print(Color.aviso("Operacion cancelada. No se modifico la receta."))
            pausar()
            return

        ok, msg = self.producto_srv.registrar_insumo_en_receta(prod["codigo"], ins["codigo"], cantidad)
        print(Color.ok(msg) if ok else Color.error(msg))
        pausar()

    def _alta_producto(self):
        categorias = self.producto_srv.obtener_categorias_con_conteo()
        if not categorias:
            print(Color.aviso("No hay categorias disponibles."))
            pausar()
            return

        enc = imprimir_encabezado_sesion(
            self.usuario,
            breadcrumb=["Inicio", "Panel Admin", "Alta de Producto", "Categoria"]
        )
        opts = [f"{c['codigo']:<10} {c['nombre']}" for c in categorias] + ["<< Cancelar y regresar"]
        idx = seleccionar_con_flechas("ALTA DE PRODUCTO - Selecciona categoria", opts, enc)
        if idx == len(categorias):
            return
        cat = categorias[idx]

        limpiar_pantalla()
        print(imprimir_encabezado_sesion(
            self.usuario,
            breadcrumb=["Inicio", "Panel Admin", "Alta de Producto", "Datos"]
        ))
        pfx = _prefijo(_ancho())
        print(f"\n{pfx}  {Color.titulo('ALTA DE NUEVO PRODUCTO / BEBIDA FESTIVA')}")
        print(f"{pfx}  Categoria: {Color.CARAMELO}{cat['nombre']}{Color.RESET}\n")
        print(Color.info("El producto quedara con estatus Activo. Para que sea vendible debe tener receta asignada."))
        print()

        try:
            codigo = pedir_codigo(prompt="Codigo del producto", longitud_max=6, ejemplo="P099")
            nombre = pedir_nombre_propio(prompt="Nombre del producto", ejemplo="Moka Navideno")
            precio = pedir_precio(ejemplo="65.00")
        except OperacionCancelada:
            print(Color.aviso("Operacion cancelada. No se creo el producto."))
            pausar()
            return

        ok, msg = self.producto_srv.crear_producto_menu(codigo, nombre, precio, cat["codigo"])
        print(Color.ok(msg) if ok else Color.error(msg))
        pausar()

    def _menu_consultas(self):
        opciones = [
            "C1 - Detalle de venta por folio",
            "C2 - Detalle de compra por folio",
            "C3 - Mermas de los ultimos 7 dias",
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
        limpiar_pantalla()
        print(imprimir_encabezado_sesion(
            self.usuario,
            breadcrumb=["Inicio", "Panel Admin", "Consultas", "C1 - Detalle Venta"]
        ))
        print(f"\n  {Color.titulo('C1 - DETALLE DE VENTA')}\n")
        ventas = self.reporte_srv.listar_ventas_recientes(30)
        if ventas:
            cols = ["Folio", "Fecha", "Barista", "Cliente", "Metodo", "Total"]
            filas = [(v["folio"], v["fecha"], v["barista"], v["cliente"],
                      v["metodo"], f"${v['total']:.2f}") for v in ventas]
            imprimir_tabla("Ventas recientes (ultimas 30)", cols, filas)
        try:
            folio = pedir_entero_positivo(prompt="Numero de folio de venta", ejemplo="1")
        except OperacionCancelada:
            return
        enc_venta, lineas = self.reporte_srv.consulta_1_detalle_venta(folio)
        if not enc_venta:
            print(Color.aviso("Venta no encontrada."))
            pausar()
            return
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
             for l in (lineas or [])],
            subtitulo=f"Folio #{folio}",
            encabezado_extra=f"Cliente: {enc_venta['nombreCliente']}  Empleado: {enc_venta['empleado']}"
        )
        pausar()

    def _consulta_2(self):
        limpiar_pantalla()
        print(imprimir_encabezado_sesion(
            self.usuario,
            breadcrumb=["Inicio", "Panel Admin", "Consultas", "C2 - Detalle Compra"]
        ))
        print(f"\n  {Color.titulo('C2 - DETALLE DE COMPRA')}\n")
        try:
            folio = pedir_entero_positivo(prompt="Numero de folio de compra", ejemplo="1")
        except OperacionCancelada:
            return
        enc_compra, lineas = self.reporte_srv.consulta_2_detalle_compra(folio)
        if not enc_compra:
            print(Color.aviso("Compra no encontrada."))
            pausar()
            return
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

    def _consulta_3(self):
        mermas = self.reporte_srv.consulta_3_mermas_semana()
        cols = ["Folio", "Fecha", "Insumo", "Cantidad", "Tipo", "Motivo"]
        filas = [(m["codigo"], m["fecha"], m["insumo"], m["cantidad"],
                  m["tipo_merma"], m["motivo"]) for m in mermas]
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

    def _consulta_4(self):
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
        try:
            fecha = pedir_fecha()
        except OperacionCancelada:
            return
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

    def _consulta_5(self):
        productos = self.producto_srv.listar_todos_productos()
        if not productos:
            print(Color.aviso("No hay productos."))
            pausar()
            return
        enc = imprimir_encabezado_sesion(
            self.usuario,
            breadcrumb=["Inicio", "Panel Admin", "Consultas", "C5 - Receta"]
        )
        opts = [f"{p['codigo']:<10} {p['nombre']:<30} {p['categoria']}"
                for p in productos] + ["<< Cancelar y regresar"]
        idx = seleccionar_con_flechas("C5 - Insumos de la receta - Selecciona producto", opts, enc)
        if idx == len(productos):
            return
        prod = productos[idx]
        receta = self.reporte_srv.consulta_5_insumos_receta(prod["codigo"])
        cols = ["Codigo", "Insumo", "Requerido", "Stock Actual", "Unidad"]
        filas = [(r["codigo"], r["nombre"], r["requerido"],
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

    def _gestion_empleados(self):
        es_principal = _es_admin_principal(self.usuario)
        if es_principal:
            opciones = [
                "Listar todos los empleados",
                "Dar de alta nuevo empleado",
                "Desactivar cuenta de empleado",
                "<< Volver al Menu Admin",
            ]
        else:
            opciones = [
                "Listar todos los empleados",
                "Dar de alta nuevo Barista",
                "<< Volver al Menu Admin",
            ]
        while True:
            enc = imprimir_encabezado_sesion(
                self.usuario,
                breadcrumb=["Inicio", "Panel Admin", "Gestion de Empleados"]
            )
            idx = seleccionar_con_flechas("GESTION DE EMPLEADOS", opciones, enc)
            if es_principal:
                if idx == 0:
                    self._listar_empleados()
                elif idx == 1:
                    self._crear_empleado()
                elif idx == 2:
                    self._desactivar_empleado()
                elif idx == 3:
                    return
            else:
                if idx == 0:
                    self._listar_empleados()
                elif idx == 1:
                    self._crear_empleado(forzar_barista=True)
                elif idx == 2:
                    return

    def _listar_empleados(self):
        empleados = self.empleado_srv.listar_empleados()
        cols = ["#", "Nombre", "Correo", "Rol", "Activo"]
        filas = [(e["num"], e["nombre"], e["correo"], e["rol"],
                  "SI" if e["activo"] else "NO") for e in empleados]
        limpiar_pantalla()
        print(imprimir_encabezado_sesion(
            self.usuario,
            breadcrumb=["Inicio", "Panel Admin", "Gestion de Empleados", "Listar"]
        ))
        imprimir_tabla("EMPLEADOS REGISTRADOS", cols, filas)
        pausar()

    def _crear_empleado(self, forzar_barista=False):
        es_principal = _es_admin_principal(self.usuario)
        if not es_principal:
            forzar_barista = True

        limpiar_pantalla()
        print(imprimir_encabezado_sesion(
            self.usuario,
            breadcrumb=["Inicio", "Panel Admin", "Gestion de Empleados", "Alta Empleado"]
        ))
        pfx = _prefijo(_ancho())
        print(f"\n{pfx}  {Color.titulo('ALTA DE NUEVO EMPLEADO')}\n")
        print(Color.info("Completa los datos del nuevo colaborador."))
        if forzar_barista:
            print(Color.aviso("[!] Como Admin Secundario solo puedes crear cuentas de Barista."))
        print()

        try:
            nombre = pedir_nombre_propio(prompt="Nombre(s)", ejemplo="Maria")
            apell1 = pedir_nombre_propio(prompt="Primer apellido", ejemplo="Garcia")

            _imprimir_guia(
                "Segundo apellido del empleado (opcional)",
                "Texto libre, maximo 50 caracteres. ENTER para omitir.",
                "Lopez",
                "Se ajusta a Formato Titulo."
            )
            raw_a2 = _input_centrado("Segundo apellido (ENTER si no aplica)")
            if raw_a2.strip().upper() in ("0", "CANCELAR"):
                raise OperacionCancelada()
            apell2 = raw_a2.strip().title()

            rfc = pedir_rfc()
            tel = pedir_telefono()
            correo = pedir_correo()

            _imprimir_guia(
                "Contrasena inicial de acceso",
                "Minimo 4 caracteres, sin espacios",
                "cof2024",
                "El empleado podra usarla de inmediato al iniciar sesion."
            )
            raw_contra = _input_centrado("Contrasena inicial (minimo 4 chars)")
            if raw_contra.strip().upper() in ("0", "CANCELAR"):
                raise OperacionCancelada()
            contra = raw_contra.strip()
            if len(contra) < 4:
                print(Color.error("Contrasena demasiado corta. Debe tener al menos 4 caracteres."))
                pausar()
                return

        except OperacionCancelada:
            print(Color.aviso("Operacion cancelada. No se creo el empleado."))
            pausar()
            return

        if forzar_barista:
            rol = "BARI"
            print(Color.info("Rol asignado automaticamente: Barista."))
        else:
            enc = imprimir_encabezado_sesion(
                self.usuario,
                breadcrumb=["Inicio", "Panel Admin", "Gestion de Empleados", "Alta", "Rol"]
            )
            opts = ["Barista", "Administrador Secundario", "<< Cancelar"]
            idx = seleccionar_con_flechas("Rol del nuevo empleado", opts, enc)
            if idx == 2:
                return
            rol = "BARI" if idx == 0 else "ADMN"

        ok, msg = self.empleado_srv.crear_empleado(nombre, apell1, apell2, rfc, tel, correo, contra, rol)
        print(Color.ok(msg) if ok else Color.error(msg))
        pausar()

    def _desactivar_empleado(self):
        empleados = self.empleado_srv.listar_empleados()
        candidatos = [e for e in empleados
                      if e["activo"] and e["num"] != 1 and e["num"] != self.usuario.num]
        if not candidatos:
            print(Color.aviso("No hay cuentas desactivables disponibles."))
            print(Color.info("Nota: La cuenta Admin Principal (num=1) no puede desactivarse."))
            pausar()
            return
        enc = imprimir_encabezado_sesion(
            self.usuario,
            breadcrumb=["Inicio", "Panel Admin", "Gestion de Empleados", "Desactivar"]
        )
        opts = [f"{e['num']:>4}  {e['nombre']:<30} {e['rol']}  {'Activo' if e['activo'] else 'Inactivo'}"
                for e in candidatos] + ["<< Cancelar y regresar"]
        idx = seleccionar_con_flechas("Selecciona cuenta a desactivar", opts, enc)
        if idx == len(candidatos):
            return
        emp = candidatos[idx]
        enc2 = imprimir_encabezado_sesion(
            self.usuario,
            breadcrumb=["Inicio", "Panel Admin", "Gestion de Empleados", "Confirmar desactivacion"]
        )
        opts2 = [f"Confirmar - desactivar a {emp['nombre']}", f"<< Cancelar - no desactivar a {emp['nombre']}"]
        idx2 = seleccionar_con_flechas("Confirmar desactivacion", opts2, enc2)
        if idx2 == 0:
            ok = self.empleado_srv.desactivar_cuenta(emp["num"])
            print(Color.ok(f"Cuenta de {emp['nombre']} desactivada.") if ok
                  else Color.error("No se pudo desactivar la cuenta."))
            pausar()