from repositorios.base_repositorios import BaseRepositorio


class ConsultasRepositorio(BaseRepositorio):

    def resumen_financiero(self, filtro_sql):
        self._cursor.execute(
            f"SELECT COUNT(*) AS num_ventas, COALESCE(SUM(total),0) AS ingresos FROM venta WHERE {filtro_sql}"
        )
        ventas = self._cursor.fetchone() or {"num_ventas": 0, "ingresos": 0}
        self._cursor.execute(
            f"SELECT COALESCE(SUM(total),0) AS gastos FROM compra WHERE {filtro_sql}"
        )
        compras = self._cursor.fetchone() or {"gastos": 0}
        return ventas, compras

    def listar_ventas_recientes(self, limite=20):
        self._cursor.execute(f"""
            SELECT v.codigo AS folio,
                   DATE_FORMAT(v.fecha, '%d/%m %H:%i') AS fecha,
                   CONCAT(e.nombrePila,' ',e.primApell) AS barista,
                   v.nombreCliente                       AS cliente,
                   m.descripcion                        AS metodo,
                   v.total
            FROM venta v
            INNER JOIN empleado e    ON v.empleado   = e.num
            INNER JOIN metodo_pago m ON v.metodoPago = m.codigo
            ORDER BY v.codigo DESC
            LIMIT {int(limite)}
        """)
        return self._cursor.fetchall()

    def detalle_venta_encabezado(self, folio_venta):
        self._cursor.execute("""
            SELECT v.codigo AS folio, v.fecha, v.nombreCliente,
                   CONCAT(e.nombrePila,' ',e.primApell) AS empleado,
                   m.descripcion AS metodoPago, v.total
            FROM venta v
            INNER JOIN empleado e    ON v.empleado   = e.num
            INNER JOIN metodo_pago m ON v.metodoPago = m.codigo
            WHERE v.codigo = %s
        """, (folio_venta,))
        return self._cursor.fetchone()

    def detalle_venta_lineas(self, folio_venta):
        self._cursor.execute("""
            SELECT p.codigo, p.nombre, pv.precioUnitarioVenta AS precio,
                   pv.cantidad, pv.subtotal, pv.totalIVA, pv.total
            FROM prod_venta pv
            INNER JOIN producto p ON pv.producto = p.codigo
            WHERE pv.venta = %s
        """, (folio_venta,))
        return self._cursor.fetchall()

    def detalle_compra_encabezado(self, folio_compra):
        self._cursor.execute("""
            SELECT c.codigo AS folio, c.fecha, p.nombre AS proveedor, p.ciudad, c.total
            FROM compra c
            INNER JOIN proveedor p ON c.proveedor = p.codigo
            WHERE c.codigo = %s
        """, (folio_compra,))
        return self._cursor.fetchone()

    def detalle_compra_lineas(self, folio_compra):
        self._cursor.execute("""
            SELECT i.codigo, i.nombre, ic.precioUnitarioCom AS precio,
                   ic.cantidad, ic.subtotal, ic.totalIVA, ic.total
            FROM insum_com ic
            INNER JOIN insumo i ON ic.insumo = i.codigo
            WHERE ic.compra = %s
        """, (folio_compra,))
        return self._cursor.fetchall()

    def mermas_ultima_semana(self):
        self._cursor.execute("""
            SELECT m.codigo, m.fecha, i.nombre AS insumo,
                   CONCAT(m.cantidad,' ',u.abreviatura) AS cantidad,
                   tm.nombre AS tipo_merma, m.motivo
            FROM merma m
            INNER JOIN insumo i        ON m.insumo = i.codigo
            INNER JOIN unidad_medida u ON i.unidad = u.codigo
            INNER JOIN tipo_merma tm   ON m.tipo   = tm.codigo
            WHERE m.fecha >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
            ORDER BY m.fecha DESC, m.codigo DESC
        """)
        return self._cursor.fetchall()

    def merma_por_folio(self, folio):
        self._cursor.execute("""
            SELECT m.codigo, m.fecha, i.nombre AS insumo,
                   CONCAT(m.cantidad,' ',u.abreviatura) AS cantidad,
                   tm.nombre AS tipo_merma, m.motivo
            FROM merma m
            INNER JOIN insumo i        ON m.insumo = i.codigo
            INNER JOIN unidad_medida u ON i.unidad = u.codigo
            INNER JOIN tipo_merma tm   ON m.tipo   = tm.codigo
            WHERE m.codigo = %s
        """, (folio,))
        return self._cursor.fetchone()

    def ventas_por_empleado_fecha(self, num_empleado, fecha_str):
        self._cursor.execute("""
            SELECT v.codigo AS folio, v.fecha, v.nombreCliente,
                   m.descripcion AS metodoPago, v.total
            FROM venta v
            INNER JOIN metodo_pago m ON v.metodoPago = m.codigo
            WHERE v.empleado = %s AND DATE(v.fecha) = %s
            ORDER BY v.fecha DESC
        """, (num_empleado, fecha_str))
        return self._cursor.fetchall()