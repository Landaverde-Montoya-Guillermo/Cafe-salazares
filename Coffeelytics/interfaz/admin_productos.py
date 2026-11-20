from interfaz.estilos import Color
from consola_ui import (
    limpiar_pantalla, pausar, seleccionar_con_flechas,
    imprimir_encabezado_sesion, imprimir_tabla,
    pedir_codigo, pedir_nombre_propio, pedir_precio,
    pedir_numero_positivo,
    _ancho, _prefijo, OperacionCancelada
)


class AdminProductos:
    def __init__(self, usuario, producto_srv, inventario_srv):
        self.usuario = usuario
        self.producto_srv = producto_srv
        self.inventario_srv = inventario_srv

    def configurar_receta(self, prod_codigo, prod_nombre):
        while True:
            limpiar_pantalla()
            encabezado = imprimir_encabezado_sesion(
                self.usuario,
                breadcrumb=["Inicio", "Panel Admin", "Alta de Producto", f"Receta: {prod_nombre}"]
            )
            print(encabezado)

            receta_actual = self.producto_srv.obtener_receta(prod_codigo)
            filas_receta = []
            for r in receta_actual:
                fila = [r["insumo_codigo"], r["nombre"], f"{r['cantidad']} {r['unidad_medida']}"]
                filas_receta.append(fila)
            imprimir_tabla(f"Insumos actuales de '{prod_nombre}' ({prod_codigo})",
                           ["Codigo", "Insumo", "Cantidad por unidad"], filas_receta)

            insumos = self.inventario_srv.listar_todos_insumos()
            if not insumos:
                print(Color.aviso("No hay insumos registrados en el inventario."))
                pausar()
                break

            opciones = []
            for ins in insumos:
                linea = f"{ins['codigo']:<12} {ins['nombre']:<30} Stock: {ins['stockActual']} {ins['abreviatura']}"
                opciones.append(linea)
            opciones.append("[OK] Finalizar y guardar receta")

            idx = seleccionar_con_flechas(
                f"Selecciona un insumo para agregar a '{prod_nombre}'",
                opciones,
                encabezado_extra=encabezado
            )

            if idx == len(opciones) - 1:
                if not receta_actual:
                    print(Color.aviso("Debes agregar al menos un insumo a la receta antes de finalizar."))
                    pausar()
                    continue
                print(Color.ok(f"Receta de '{prod_nombre}' guardada con {len(receta_actual)} insumo(s)."))
                pausar()
                break

            ins_sel = insumos[idx]
            try:
                cant = pedir_numero_positivo(
                    prompt=f"Cantidad de {ins_sel['nombre']} por cada '{prod_nombre}'",
                    unidad=ins_sel["abreviatura"],
                    ejemplo="250",
                    nombre_campo="cantidad requerida"
                )
                ok, msg = self.producto_srv.registrar_insumo_en_receta(prod_codigo, ins_sel["codigo"], cant)
                print(Color.ok(msg) if ok else Color.error(msg))
                pausar()
            except OperacionCancelada:
                continue

    def asignar_insumo_receta(self):
        productos = self.producto_srv.listar_todos_productos()
        insumos = self.inventario_srv.listar_todos_insumos()
        if not productos or not insumos:
            print(Color.aviso("No hay productos o insumos suficientes."))
            pausar()
            return

        while True:
            enc = imprimir_encabezado_sesion(
                self.usuario,
                breadcrumb=["Inicio", "Panel Admin", "Asignar Insumo a Receta", "Producto"]
            )
            opts = [f"{p['codigo']:<10} {p['nombre']:<30} ${p['precio']:.2f}  {p['categoria']}"
                    for p in productos] + ["<< Finalizar y regresar"]
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
                continue

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
                continue

            ok, msg = self.producto_srv.registrar_insumo_en_receta(prod["codigo"], ins["codigo"], cantidad)
            print(Color.ok(msg) if ok else Color.error(msg))
            pausar()

    def alta_producto(self):
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
            codigo = pedir_codigo(prompt="Codigo del producto", longitud_max=4, ejemplo="P099")
            nombre = pedir_nombre_propio(prompt="Nombre del producto", ejemplo="Moka Navideno")
            precio = pedir_precio(ejemplo="65.00")
        except OperacionCancelada:
            print(Color.aviso("Operacion cancelada. No se creo el producto."))
            pausar()
            return

        ok, msg = self.producto_srv.crear_producto_menu(codigo, nombre, precio, cat["codigo"])
        if not ok:
            print(Color.error(msg))
            pausar()
            return
        print(Color.ok(msg))
        print(Color.info("Ahora puedes asignar los insumos de la receta."))
        self.configurar_receta(codigo.upper(), nombre)
