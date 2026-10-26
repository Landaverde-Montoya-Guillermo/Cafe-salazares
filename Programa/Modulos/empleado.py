class Rol:
    def __init__(self, codigo: int, tipo_rol: str, descripcion: str = ""):
        self.codigo = codigo
        self.tipo_rol = tipo_rol  # Ej. "Administrador", "Barista", "Cajero"
        self.descripcion = descripcion

    def __str__(self):
        return f"Rol[{self.codigo}]: {self.tipo_rol}"
    
class Empleado:
    def __init__(self, num_empleado: int, nombre: str, prim_apell: str, 
                 seg_apell: str, rfc: str, telefono: str, codigo_rol: str):
        self.num_empleado = num_empleado
        self.nombre = nombre
        self.prim_apell = prim_apell
        self.seg_apell = seg_apell
        self.rfc = rfc
        self.telefono = telefono
        self.codigo_rol = codigo_rol

    @property
    def nombre_completo(self) -> str:
        segundo = f" {self.seg_apell}" if self.seg_apell else ""
        return f"{self.nombre} {self.prim_apell}{segundo}"

    def __str__(self):
        return f"Empleado[{self.num_empleado}]: {self.nombre_completo}"