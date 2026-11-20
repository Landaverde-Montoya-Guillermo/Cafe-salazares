from interfaz.estilos import Color
from consola_ui import (
    limpiar_pantalla, pausar, seleccionar_con_flechas,
    imprimir_encabezado_sesion, imprimir_tabla,
    pedir_cantidad_carrito, OperacionCancelada
)


class BaristaCatalogo:
    def __init__(self, usuario, producto_srv, carrito):
        self.usuario = usuario
        self.producto_srv = producto_srv
        self.carrito = carrito

    def catalogo_productos(self):
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
            self.listar_productos_categoria(categorias[idx])

    def listar_productos_categoria(self, cat):
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
            self.previsualizar_y_agregar(productos[idx])

    def previsualizar_y_agregar(self, producto):
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

        receta = self.producto_srv.obtener_receta(producto.codigo)
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
        self.carrito.agregar_producto(producto, cant)
        print(Color.ok(f"{cant}x {producto.nombre} agregado al carrito."))
        pausar()
