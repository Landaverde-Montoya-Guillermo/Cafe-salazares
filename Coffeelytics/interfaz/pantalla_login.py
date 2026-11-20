from interfaz.estilos import Color
from consola_ui import (
    limpiar_pantalla, pausar, imprimir_encabezado_sesion,
    pedir_contrasena, imprimir_caja_credenciales, imprimir_banner,
    _imprimir_guia, _input_centrado, _ancho, _prefijo
)


class PantallaLogin:
    def __init__(self, auth_servicio):
        self.auth_servicio = auth_servicio

    def mostrar(self):
        intentos = 0
        mensaje = ""
        while True:
            limpiar_pantalla()
            imprimir_banner()
            imprimir_caja_credenciales()
            print()
            enc = imprimir_encabezado_sesion(None, breadcrumb=["Inicio", "Inicio de Sesion"])
            print(enc)
            if mensaje:
                pfx = _prefijo(_ancho())
                print(f"\n{pfx}  {mensaje}\n")

            _imprimir_guia(
                "Correo electronico registrado en el sistema",
                "usuario@dominio.com (sin espacios)",
                "admin@coffeelytics.com",
                "Las credenciales se verifican contra la base de datos MySQL."
            )
            correo = _input_centrado("Correo electronico")
            if correo.strip().lower() in ("salir", "0"):
                return None

            correo = correo.strip().lower()
            contra = pedir_contrasena("Contrasena: ")

            empleado = self.auth_servicio.iniciar_sesion(correo, contra)
            if empleado:
                return empleado

            intentos += 1
            mensaje = Color.error(f"Credenciales incorrectas o cuenta inactiva. Intento {intentos}/3.")
            if intentos >= 3:
                limpiar_pantalla()
                print(Color.error("Demasiados intentos fallidos. El sistema se cerrara."))
                pausar()
                return None