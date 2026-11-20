from interfaz.estilos import Color
from consola_ui import (
    limpiar_pantalla, pausar, seleccionar_con_flechas,
    imprimir_encabezado_sesion, imprimir_tabla,
    pedir_codigo, pedir_nombre_propio,
    pedir_numero_positivo, pedir_precio,
    _imprimir_guia, _input_centrado, _ancho, _prefijo, OperacionCancelada
)


class AdminInventario:
    def __init__(self, usuario, inventario_srv, compra_srv, reportes):
        self.usuario = usuario
        self.inventario_srv = inventario_srv
        self.compra_srv = compra_srv
        self.reportes = reportes

    def alertas_stock(self):
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

    def registrar_compra(self):
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

    def registrar_insumo(self):
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
