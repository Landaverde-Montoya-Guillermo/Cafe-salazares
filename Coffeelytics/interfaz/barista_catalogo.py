from decimal import Decimal, ROUND_FLOOR

from interfaz.estilos import Color
from consola_ui import (
    limpiar_pantalla, pausar, seleccionar_con_flechas,
    imprimir_encabezado_sesion, imprimir_tabla,
    pedir_cantidad_carrito, OperacionCancelada
)


class BaristaCatalogo:
    def __init__(self, usuario, producto_srv, carrito, carrito_ui):
        self.usuario = usuario
        self.producto_srv = producto_srv
        self.carrito = carrito
        self.carrito_ui = carrito_ui

    def catalogo_productos(self):
        while True:
            categorias = self.producto_srv.obtener_categorias_con_conteo()
            if not categorias:
                print(Color.aviso("No hay categorias disponibles."))
            opciones_cat = [
                f"{c['nombre']:<24}  Disponibles: {c['disponibles']}/{c['total']}"
                for c in categorias
            ] + [
                f"Ver / gestionar carrito ({len(self.carrito.items)} productos)",
                "<< Volver al Menu Barista",
            ]
            enc = imprimir_encabezado_sesion(
                self.usuario,
                breadcrumb=["Inicio", "Panel Barista", "Nueva Venta", "Catalogo"]
            )
            idx = seleccionar_con_flechas("CATALOGO - Selecciona categoria", opciones_cat, enc)
            if idx == len(categorias):
                self.carrito_ui.gestionar_carrito()
                continue
            if idx == len(categorias) + 1:
                return
            self.listar_productos_categoria(categorias[idx])

    def listar_productos_categoria(self, cat):
        while True:
            productos = self.producto_srv.obtener_productos_por_categoria(cat["codigo"])
            if not productos:
                print(Color.aviso("No hay productos activos con receta en esta categoria."))
                pausar()
                return
            etiquetas = []
            for p in productos:
                disp = f"{Color.VERDE_OK}[Disponible]{Color.RESET}" if p.esta_disponible() \
                       else f"{Color.ROJO_ALT}[No disponible]{Color.RESET}"
                etiquetas.append(f"{p.nombre:<30}  ${p.precio:>6.2f}  {disp}")
            etiquetas.extend([
                f"Ver / gestionar carrito ({len(self.carrito.items)} productos)",
                "<< Volver al Catalogo",
            ])
            enc = imprimir_encabezado_sesion(
                self.usuario,
                breadcrumb=[
                    "Inicio", "Panel Barista", "Nueva Venta",
                    "Catalogo", cat["nombre"]
                ]
            )
            idx = seleccionar_con_flechas(f"CATEGORIA: {cat['nombre']}", etiquetas, enc)
            if idx == len(productos):
                self.carrito_ui.gestionar_carrito()
                continue
            if idx == len(productos) + 1:
                return
            self.previsualizar_y_agregar(productos[idx])

    def _obtener_insumos_apartados(self):
        apartados = {}
        for item in self.carrito.items.values():
            receta = self.producto_srv.obtener_receta(item["producto"].codigo)
            for ingrediente in receta:
                codigo = ingrediente["insumo_codigo"]
                cantidad = Decimal(str(ingrediente["requerido"]))
                cantidad = cantidad * Decimal(str(item["cantidad"]))
                apartados[codigo] = apartados.get(codigo, Decimal("0")) + cantidad
        return apartados

    def _validar_stock_disponible(self, producto, receta, cantidad):
        apartados = self._obtener_insumos_apartados()
        maximo_posible = None
        insumo_limitante = ""

        for ingrediente in receta:
            requerido = Decimal(str(ingrediente["requerido"]))
            if requerido <= 0:
                raise ValueError(
                    f"La receta de '{producto.nombre}' tiene una cantidad invalida."
                )

            codigo = ingrediente["insumo_codigo"]
            stock = Decimal(str(ingrediente["stockActual"]))
            disponible = stock - apartados.get(codigo, Decimal("0"))
            if disponible < 0:
                disponible = Decimal("0")

            maximo_insumo = int(
                (disponible / requerido).to_integral_value(rounding=ROUND_FLOOR)
            )
            if maximo_posible is None or maximo_insumo < maximo_posible:
                maximo_posible = maximo_insumo
                insumo_limitante = ingrediente["nombre"]

        if maximo_posible is not None and cantidad > maximo_posible:
            return False, (
                f"Stock insuficiente de '{insumo_limitante}'. "
                f"Puedes agregar como maximo {maximo_posible} unidad(es) adicionales "
                f"de '{producto.nombre}' con el stock disponible."
            )
        return True, ""

    def previsualizar_y_agregar(self, producto):
        while True:
            limpiar_pantalla()
            try:
                if not self.producto_srv.es_producto_vendible(producto.codigo):
                    print(Color.aviso(
                        "El producto ya no esta activo o no tiene insumos en su receta."
                    ))
                    pausar()
                    return

                enc = imprimir_encabezado_sesion(
                    self.usuario,
                    breadcrumb=[
                        "Inicio", "Panel Barista", "Nueva Venta",
                        "Catalogo", "Producto"
                    ]
                )
                print(enc)
                print(f"\n  {Color.titulo(producto.nombre)}")
                print(f"  Precio: {Color.CARAMELO}${producto.precio:.2f}{Color.RESET}")
                est = f"{Color.VERDE_OK}Disponible{Color.RESET}" if producto.esta_disponible() \
                      else f"{Color.ROJO_ALT}No disponible{Color.RESET}"
                print(f"  Estatus: {est}")

                receta = self.producto_srv.obtener_receta(producto.codigo)
                cols = ["Insumo", "Requerido", "Stock Actual", "Unidad"]
                filas = [(r["nombre"], r["requerido"], r["stockActual"], r["abreviatura"])
                         for r in receta]
                imprimir_tabla("Receta / Insumos en vivo", cols, filas)

                if not producto.esta_disponible():
                    print(Color.aviso("Producto no disponible. No se puede agregar al carrito."))
                    pausar()
                    return

                while True:
                    try:
                        cant = pedir_cantidad_carrito(producto.nombre)
                    except ValueError as error:
                        print(Color.error(str(error)))
                        pausar()
                        continue
                    receta_actual = self.producto_srv.obtener_receta(producto.codigo)
                    if not receta_actual:
                        print(Color.error(
                            "El producto ya no tiene insumos registrados en su receta."
                        ))
                        pausar()
                        return
                    hay_stock, mensaje = self._validar_stock_disponible(
                        producto, receta_actual, cant
                    )
                    if not hay_stock:
                        print(Color.error(mensaje))
                        pausar()
                        continue

                    self.carrito.agregar_producto(producto, cant)
                    print(Color.ok(f"{cant}x {producto.nombre} agregado al carrito."))
                    pausar()
                    return
            except OperacionCancelada:
                print(Color.aviso("Operacion cancelada. No se agrego el producto al carrito."))
                pausar()
                return
            except Exception as error:
                print(Color.error(str(error)))
                pausar()
                continue
