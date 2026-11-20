from mysql.connector import Error
from config.database import transaccion
from entidades.base import ValidacionError
from entidades.empleado import Empleado
from repositorios.empleado_repositorio import EmpleadoRepositorio
from servicios.auth_servicio import AuthServicio


class EmpleadoServicio:

    def crear_empleado(self, nombre, apell1, apell2, rfc, tel, correo, contra, rol):
        if len(str(contra or "").strip()) < 4:
            return False, "La contraseña debe tener al menos 4 caracteres."
        try:
            hash_pwd = AuthServicio.hashear_contrasena(contra)
            nuevo_emp = Empleado(
                num=None,
                nombre_pila=nombre,
                prim_apell=apell1,
                seg_apell=apell2,
                rfc=rfc,
                telefono=tel,
                correo=correo,
                contrasena=hash_pwd,
                rol_codigo=rol
            )
            with transaccion() as cursor:
                repo = EmpleadoRepositorio(cursor)
                repo.crear(nuevo_emp)
            return True, "Cuenta creada correctamente."
        except ValidacionError as e:
            return False, str(e)
        except Error as e:
            return False, f"Error de base de datos al crear cuenta: {e.msg}"

    def desactivar_cuenta(self, num_empleado):
        if int(num_empleado) == 1:
            return False
        try:
            with transaccion() as cursor:
                repo = EmpleadoRepositorio(cursor)
                return repo.desactivar(num_empleado)
        except Error:
            return False

    def listar_empleados(self):
        with transaccion(dictionary=True) as cursor:
            repo = EmpleadoRepositorio(cursor)
            return repo.listar_todos()