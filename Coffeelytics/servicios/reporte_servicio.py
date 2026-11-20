from config.database import transaccion
from repositorios.consultas_repositorio import ConsultasRepositorio
from repositorios.producto_repositorio import ProductoRepositorio


class ReporteServicio:

    def obtener_resumen_financiero(self, periodo="HOY"):
        filtros = {
            "HOY":    "DATE(fecha) = CURDATE()",
            "SEMANA": "YEARWEEK(fecha, 1) = YEARWEEK(CURDATE(), 1)",
            "MES":    "MONTH(fecha) = MONTH(CURDATE()) AND YEAR(fecha) = YEAR(CURDATE())",
            "ANIO":   "YEAR(fecha) = YEAR(CURDATE())",
        }
        filtro = filtros.get(periodo, "1=1")
        with transaccion(dictionary=True) as cursor:
            repo = ConsultasRepositorio(cursor)
            ventas, compras = repo.resumen_financiero(filtro)
            ingresos = float(ventas["ingresos"])
            gastos = float(compras["gastos"])
            return {
                "num_ventas": ventas["num_ventas"],
                "ingresos": ingresos,
                "gastos_insumos": gastos,
                "ganancia_bruta": round(ingresos - gastos, 2)
            }

    def listar_ventas_recientes(self, limite=20):
        with transaccion(dictionary=True) as cursor:
            repo = ConsultasRepositorio(cursor)
            return repo.listar_ventas_recientes(limite)

    def consulta_1_detalle_venta(self, folio_venta):
        with transaccion(dictionary=True) as cursor:
            repo = ConsultasRepositorio(cursor)
            enc = repo.detalle_venta_encabezado(folio_venta)
            lineas = repo.detalle_venta_lineas(folio_venta)
            return enc, lineas

    def consulta_2_detalle_compra(self, folio_compra):
        with transaccion(dictionary=True) as cursor:
            repo = ConsultasRepositorio(cursor)
            enc = repo.detalle_compra_encabezado(folio_compra)
            lineas = repo.detalle_compra_lineas(folio_compra)
            return enc, lineas

    def consulta_3_mermas_semana(self):
        with transaccion(dictionary=True) as cursor:
            repo = ConsultasRepositorio(cursor)
            return repo.mermas_ultima_semana()

    def consulta_3_merma_por_folio(self, folio):
        with transaccion(dictionary=True) as cursor:
            repo = ConsultasRepositorio(cursor)
            return repo.merma_por_folio(folio)

    def consulta_4_ventas_por_empleado_fecha(self, num_empleado, fecha_str):
        with transaccion(dictionary=True) as cursor:
            repo = ConsultasRepositorio(cursor)
            return repo.ventas_por_empleado_fecha(num_empleado, fecha_str)

    def consulta_5_insumos_receta(self, cod_producto):
        with transaccion(dictionary=True) as cursor:
            repo = ProductoRepositorio(cursor)
            return repo.obtener_receta(cod_producto)