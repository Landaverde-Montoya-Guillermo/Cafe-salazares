from interfaz.estilos import Color
from consola_ui import (
    limpiar_pantalla, pausar, seleccionar_con_flechas,
    imprimir_encabezado_sesion,
    pedir_numero_positivo, pedir_motivo,
    _ancho, _prefijo, OperacionCancelada
)


class BaristaOperaciones:
    def __init__(self, usuario, inventario_srv, despacho_srv, empleado_srv, merma_srv):
        self.usuario = usuario
        self.inventario_srv = inventario_srv
        self.despacho_srv = despacho_srv
        self.empleado_srv = empleado_srv
        self.merma_srv = merma_srv

    def registrar_merma(self):
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

    def surtir_mesa(self):
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

    def desactivar_mi_cuenta(self):
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
