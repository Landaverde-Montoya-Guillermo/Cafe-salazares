from datetime import datetime
from decimal import Decimal
from mysql.connector import Error
from config.database import transaccion
from config.reglas import IVA_FRONTERA
from entidades.base import StockInsuficienteError
from repositorios.venta_repositorios import VentaRepositorio
from repositorios.producto_repositorio import ProductoRepositorio
from repositorios.insumo_repositorio import InsumoRepositorio
from servicios.inventario_servicio import InventarioServicio


class VentaServicio:

    def registrar_venta(self, carrito, metodo_pago_cod, num_empleado):
        if not carrito.items:
            return False, "El carrito está vacío.", None

        try:
            with transaccion(dictionary=True) as cursor:
                venta_repo = VentaRepositorio(cursor)
                prod_repo = ProductoRepositorio(cursor)
                insumo_repo = InsumoRepositorio(cursor)

                # 1. Calcular demanda total de insumos del carrito y validar stock antes de vender
                consumo_total = {}
                for item in carrito.items.values():
                    prod = item["producto"]
                    cant = Decimal(str(item["cantidad"]))
                    receta = prod_repo.obtener_receta(prod.codigo)
                    for ing in receta:
                        cod_ins = ing["insumo_codigo"]
                        req = Decimal(str(ing["requerido"])) * cant
                        consumo_total[cod_ins] = consumo_total.get(cod_ins, Decimal("0")) + req

                for cod_ins, req_total in consumo_total.items():
                    ins_db = insumo_repo.obtener_por_codigo(cod_ins)
                    if not ins_db:
                        raise StockInsuficienteError(f"El insumo {cod_ins} no existe en inventario.")
                    stock_actual = Decimal(str(ins_db["stockActual"]))
                    if stock_actual < req_total:
                        raise StockInsuficienteError(
                            f"Stock insuficiente de '{ins_db['nombre']}': "
                            f"disponible {stock_actual}, requerido {req_total}."
                        )

                # 2. Insertar encabezado de venta
                fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                total_venta = carrito.calcular_total()
                folio = venta_repo.insertar_encabezado(
                    fecha_actual, carrito.nombre_cliente, total_venta,
                    metodo_pago_cod, num_empleado
                )

                # 3. Insertar líneas de detalle en prod_venta
                for item in carrito.items.values():
                    prod = item["producto"]
                    cant = item["cantidad"]
                    sub = round(prod.precio * cant, 2)
                    iva = round(sub * IVA_FRONTERA, 2)
                    tot_linea = round(sub + iva, 2)
                    venta_repo.insertar_linea(
                        folio, prod.codigo, cant, prod.precio, sub, iva, tot_linea
                    )

                # 4. Descontar stock real de insumos
                for cod_ins, req_total in consumo_total.items():
                    ins_db = insumo_repo.obtener_por_codigo(cod_ins)
                    nuevo_stock = Decimal(str(ins_db["stockActual"])) - req_total
                    insumo_repo.actualizar_stock(cod_ins, nuevo_stock)

                # 5. Sincronizar estatus de productos
                InventarioServicio.sincronizar_estatus_productos(cursor)

            return True, f"Venta #{folio} registrada.", folio
        except StockInsuficienteError as e:
            return False, str(e), None
        except Error as e:
            return False, f"Error en venta: {str(e)}", None