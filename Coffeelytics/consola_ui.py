import os
import sys
import shutil
import getpass
import datetime

from interfaz.estilos import Color
from config.negocio import INFO_CAFETERIA, LINEAS_BANNER_GRANDE


# ── EXCEPCION DE CANCELACION ─────────────────────────────────────────────────

class OperacionCancelada(Exception):
    """Se lanza cuando el usuario escribe 0 o CANCELAR en cualquier campo."""
    pass


# ── ANCHO RESPONSIVO ─────────────────────────────────────────────────────────

ANCHO_MAXIMO_UI = 132

def _ancho():
    """Devuelve el ancho util de la terminal, acotado a ANCHO_MAXIMO_UI."""
    cols = shutil.get_terminal_size(fallback=(80, 24)).columns
    return min(cols, ANCHO_MAXIMO_UI)

def _margen(ancho_caja):
    """Calcula el margen izquierdo para centrar horizontalmente una caja."""
    cols = shutil.get_terminal_size(fallback=(80, 24)).columns
    return max(0, (cols - ancho_caja) // 2)

def _prefijo(ancho_caja):
    """Devuelve la cadena de espacios para centrar horizontalmente."""
    return " " * _margen(ancho_caja)


# ── SOPORTE ANSI EN WINDOWS ──────────────────────────────────────────────────

def habilitar_ansi_windows():
    """Activa los codigos ANSI en la consola de Windows (cmd/PowerShell)."""
    if sys.platform == "win32":
        os.system("")


# ── PANTALLA ─────────────────────────────────────────────────────────────────

def limpiar_pantalla():
    os.system("cls" if sys.platform == "win32" else "clear")


def pausar(mensaje="  Presiona ENTER para continuar..."):
    ancho = _ancho()
    pfx   = _prefijo(ancho)
    print(f"\n{pfx}{Color.GRIS}{mensaje}{Color.RESET}")
    try:
        input()
    except (EOFError, KeyboardInterrupt):
        pass


# ── LECTURA DE TECLAS (MULTIPLATAFORMA) ──────────────────────────────────────

def _es_tty():
    return sys.stdin.isatty()


def leer_tecla():
    """
    Lee una tecla sin ENTER. Devuelve:
      'ARRIBA', 'ABAJO', 'IZQUIERDA', 'DERECHA', 'ENTER', 'ESC' o el caracter leido.
    """
    if not _es_tty():
        return "ENTER"

    if sys.platform == "win32":
        import msvcrt
        ch = msvcrt.getch()
        if ch in (b'\xe0', b'\x00'):
            ch2 = msvcrt.getch()
            if ch2 == b'H':
                return "ARRIBA"
            if ch2 == b'P':
                return "ABAJO"
            if ch2 == b'K':
                return "IZQUIERDA"
            if ch2 == b'M':
                return "DERECHA"
            return ""
        if ch in (b'\r', b'\n'):
            return "ENTER"
        if ch == b'\x1b':
            return "ESC"
        decoded = ch.decode("utf-8", errors="replace")
        if decoded in ("w", "W"):
            return "ARRIBA"
        if decoded in ("s", "S"):
            return "ABAJO"
        return decoded
    else:
        import termios
        import tty
        import select
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            if ch == "\x1b":
                rlist, _, _ = select.select([sys.stdin], [], [], 0.05)
                if not rlist:
                    return "ESC"
                ch2 = sys.stdin.read(1)
                if ch2 in ("[", "O"):
                    ch3 = sys.stdin.read(1)
                    if ch3 == "A":
                        return "ARRIBA"
                    if ch3 == "B":
                        return "ABAJO"
                    if ch3 == "D":
                        return "IZQUIERDA"
                    if ch3 == "C":
                        return "DERECHA"
                return ""
            if ch in ("\r", "\n"):
                return "ENTER"
            if ch in ("w", "W"):
                return "ARRIBA"
            if ch in ("s", "S"):
                return "ABAJO"
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)


# ── SELECTOR INTERACTIVO CON FLECHAS ─────────────────────────────────────────

def seleccionar_con_flechas(titulo, opciones, encabezado_extra=""):
    """Muestra un menu vertical navegable con flechas ARRIBA/ABAJO y ENTER."""
    if not opciones:
        return 0

    ancho = _ancho()
    pfx   = _prefijo(ancho)
    sep   = pfx + Color.DIM + "─" * ancho + Color.RESET

    if not _es_tty():
        limpiar_pantalla()
        if encabezado_extra:
            print(encabezado_extra)
        print(sep)
        titulo_fmt = f" {titulo} "
        pad = max(0, (ancho - len(titulo_fmt)) // 2)
        print(f"{pfx}{' ' * pad}{Color.BOLD}{Color.CARAMELO}{titulo_fmt}{Color.RESET}")
        print(sep)
        for i, op in enumerate(opciones, 1):
            print(f"{pfx}  {Color.CARAMELO}{i:2}.{Color.RESET} {op}")
        print()
        while True:
            try:
                raw = input(f"{pfx}{Color.CIAN}  Numero de opcion: {Color.RESET}").strip()
                n = int(raw)
                if 1 <= n <= len(opciones):
                    return n - 1
            except (ValueError, EOFError):
                pass
            print(Color.error("Numero invalido."))

    sel   = 0
    total = len(opciones)
    ultima_es_volver = any(kw in opciones[-1].lower()
                           for kw in ["volver", "cancelar", "salir", "<<"])

    while True:
        limpiar_pantalla()
        if encabezado_extra:
            print(encabezado_extra)
        print(sep)
        titulo_fmt = f" {titulo} "
        pad = max(0, (ancho - len(titulo_fmt)) // 2)
        print(f"{pfx}{' ' * pad}{Color.BOLD}{Color.CARAMELO}{titulo_fmt}{Color.RESET}")
        print(sep)

        for i, op in enumerate(opciones):
            es_volver = (ultima_es_volver and i == total - 1)
            if i == sel:
                if es_volver:
                    relleno = max(0, ancho - 8 - len(op))
                    linea = f"{pfx}  {Color.BG_OSCURO}{Color.AMARILLO}{Color.BOLD} [<<] {op}{' ' * relleno} {Color.RESET}"
                else:
                    relleno = max(0, ancho - 8 - len(op))
                    linea = f"{pfx}  {Color.BG_CAFE}{Color.CREMA}{Color.BOLD} [>>] {op}{' ' * relleno} {Color.RESET}"
                print(linea)
            else:
                if es_volver:
                    print(f"{pfx}  {Color.AMARILLO}  [<<] {op}{Color.RESET}")
                else:
                    print(f"{pfx}  {Color.CREMA}  [  ] {op}{Color.RESET}")
            if i < total - 1:
                print(f"{pfx}  {Color.DIM}{'─' * (ancho - 4)}{Color.RESET}")

        print(f"\n{pfx}{Color.DIM}  [^] Arriba   [v] Abajo   [ENTER] Seleccionar   [ESC] Volver{Color.RESET}")

        tecla = leer_tecla()
        if tecla == "ARRIBA":
            sel = (sel - 1) % total
        elif tecla == "ABAJO":
            sel = (sel + 1) % total
        elif tecla == "ENTER":
            return sel
        elif tecla == "ESC":
            return total - 1


# ── BREADCRUMB (RASTRO DE UBICACION) ─────────────────────────────────────────

def imprimir_breadcrumb(ruta):
    ancho = _ancho()
    pfx   = _prefijo(ancho)
    texto = " > ".join(ruta)
    linea = f"  Ubicacion: {Color.CARAMELO}{texto}{Color.RESET}"
    sep   = pfx + Color.DIM + "─" * ancho + Color.RESET
    print(sep)
    print(f"{pfx}{Color.DIM}{linea}{Color.RESET}")
    print(sep)


# ── ENCABEZADO DE SESION ─────────────────────────────────────────────────────

def imprimir_encabezado_sesion(empleado, breadcrumb=None):
    ancho = _ancho()
    pfx   = _prefijo(ancho)
    ahora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    if empleado is None:
        nom = "---"
        etiqueta_rol = "---"
    else:
        nom = empleado.nombre_completo
        if empleado.es_admin():
            if empleado.num == 1:
                etiqueta_rol = f"{Color.CARAMELO}[ADMIN PRINCIPAL]{Color.RESET}"
            else:
                etiqueta_rol = f"{Color.AMARILLO}[ADMIN SECUNDARIO]{Color.RESET}"
        else:
            etiqueta_rol = f"{Color.VERDE_OK}[{empleado.rol_nombre}]{Color.RESET}"

    linea = (f"{pfx}  {Color.BG_CAFE}{Color.CREMA}{Color.BOLD}  COFFEELYTICS  {Color.RESET}"
             f"  {Color.CARAMELO}{nom}{Color.RESET}  {etiqueta_rol}"
             f"  {Color.DIM}{ahora}{Color.RESET}")

    if breadcrumb:
        texto_bc = " > ".join(breadcrumb)
        sep = pfx + Color.DIM + "─" * ancho + Color.RESET
        bc  = f"{pfx}{Color.DIM}  Ubicacion: {Color.CARAMELO}{texto_bc}{Color.RESET}"
        return f"{linea}\n{sep}\n{bc}\n{sep}"
    return linea


# ── BANNER DE INICIO ─────────────────────────────────────────────────────────

def imprimir_banner():
    ancho_banner = 90
    pfx = _prefijo(ancho_banner)
    print()
    for linea in LINEAS_BANNER_GRANDE:
        print(pfx + linea)
    print()


# ── CAJA DE CREDENCIALES DE PRUEBA ───────────────────────────────────────────

def imprimir_caja_credenciales():
    ancho = _ancho()
    lineas_contenido = [
        ("titulo",  "Cuentas de acceso para pruebas"),
        ("sep",     ""),
        ("item",    "Admin Principal (Acceso Total):  admin@coffeelytics.com   /  admin123"),
        ("item",    "Barista (Operacion POS):          barista@coffeelytics.com /  barista123"),
        ("sep",     ""),
        ("nota",    "[!] Los nuevos administradores creados tendran rol de"),
        ("nota",    "    Administrador Secundario (privilegios operativos limitados)."),
    ]
    max_txt  = max(len(l[1]) for l in lineas_contenido if l[0] != "sep") + 4
    caja_w   = min(max_txt + 4, ancho - 4)
    pad_ext  = max(0, (ancho - caja_w) // 2)
    pfx      = " " * pad_ext

    borde_top = pfx + Color.CARAMELO + "┌" + "─" * (caja_w - 2) + "┐" + Color.RESET
    borde_bot = pfx + Color.CARAMELO + "└" + "─" * (caja_w - 2) + "┘" + Color.RESET
    vbar      = Color.CARAMELO + "│" + Color.RESET

    print(borde_top)
    for tipo, texto in lineas_contenido:
        if tipo == "sep":
            inner = Color.DIM + "─" * (caja_w - 2) + Color.RESET
            print(pfx + vbar + inner + vbar)
            continue
        interior = caja_w - 4
        if tipo == "titulo":
            txt_col = Color.BOLD + Color.CARAMELO + texto.center(interior) + Color.RESET
        elif tipo == "item":
            txt_col = Color.CREMA + f" {texto:<{interior - 1}}" + Color.RESET
        else:
            txt_col = Color.AMARILLO + f" {texto:<{interior - 1}}" + Color.RESET
        print(pfx + vbar + "  " + txt_col + "  " + vbar)
    print(borde_bot)


# ── TABLA UNICODE CON CUADRICULA COMPLETA ────────────────────────────────────

def imprimir_tabla(titulo, columnas, filas, ancho_min=12):
    ancho = _ancho()
    pfx   = _prefijo(ancho)

    if filas and isinstance(filas[0], dict):
        filas = [[str(f.get(c, "")) for c in columnas] for f in filas]
    else:
        filas = [[str(c2) for c2 in fila] for fila in filas]

    anchos = [max(ancho_min, len(str(col))) for col in columnas]
    for fila in filas:
        for i, celda in enumerate(fila):
            if i < len(anchos):
                anchos[i] = max(anchos[i], len(str(celda)))

    disponible = ancho - len(pfx) - 2
    total_tabla = sum(a + 5 for a in anchos) + 1
    if total_tabla > disponible and len(anchos) > 1:
        exceso = total_tabla - disponible
        for _ in range(exceso):
            idx_max = anchos.index(max(anchos))
            if anchos[idx_max] > ancho_min + 1:
                anchos[idx_max] -= 1

    sep_top = pfx + "  ╔" + "╤".join("═" * (a + 4) for a in anchos) + "╗"
    sep_hdr = pfx + "  ╠" + "╪".join("═" * (a + 4) for a in anchos) + "╣"
    sep_mid = pfx + "  ├" + "┼".join("─" * (a + 4) for a in anchos) + "┤"
    sep_bot = pfx + "  ╚" + "╧".join("═" * (a + 4) for a in anchos) + "╝"

    def fila_str(celdas, color_celdas=Color.RESET):
        partes = []
        for i, celda in enumerate(celdas):
            a   = anchos[i] if i < len(anchos) else ancho_min
            txt = str(celda)
            if len(txt) > a:
                txt = txt[:a - 1] + "~"
            partes.append(f"  {color_celdas}{txt:<{a}}{Color.RESET}  ")
        return pfx + "  ║" + "│".join(partes) + "║"

    print(f"\n{pfx}  {Color.titulo(titulo)}")
    print(sep_top)
    print(fila_str(columnas, Color.CARAMELO + Color.BOLD))
    print(sep_hdr)
    if not filas:
        print(fila_str(["(Sin registros)"] + [""] * (len(columnas) - 1)))
    else:
        for idx, fila in enumerate(filas):
            fila_norm = list(fila) + [""] * (len(columnas) - len(fila))
            color = Color.CREMA if idx % 2 == 0 else Color.GRIS
            print(fila_str(fila_norm[:len(columnas)], color))
            if idx < len(filas) - 1:
                print(sep_mid)
    print(sep_bot)


# ── ENTRADA DE CONTRASENA OCULTA ─────────────────────────────────────────────

def pedir_contrasena(prompt="  Contrasena: "):
    ancho = _ancho()
    pfx   = _prefijo(ancho)
    if sys.platform == "win32":
        import msvcrt
        print(pfx + prompt, end="", flush=True)
        chars = []
        while True:
            ch = msvcrt.getch()
            if ch in (b'\r', b'\n'):
                print()
                break
            elif ch == b'\x08':
                if chars:
                    chars.pop()
                    print("\b \b", end="", flush=True)
            elif ch == b'\x03':
                raise KeyboardInterrupt
            else:
                chars.append(ch.decode("utf-8", errors="replace"))
                print("*", end="", flush=True)
        return "".join(chars)
    else:
        return getpass.getpass(pfx + prompt)


# ── FUNCIONES DE ENTRADA VALIDADA CON NORMALIZACION ──────────────────────────

def _imprimir_guia(que, formato, ejemplo, accion=""):
    ancho    = _ancho()
    caja_w   = min(70, ancho - 4)
    pad_caja = max(0, (ancho - caja_w) // 2)
    p        = " " * pad_caja
    sep_in   = p + Color.DIM + "─" * caja_w + Color.RESET
    print(sep_in)
    print(f"{p}  {Color.CIAN}[>>] Dato:    {Color.RESET}{que}")
    print(f"{p}  {Color.CIAN}     Formato: {Color.RESET}{formato}")
    print(f"{p}  {Color.CIAN}     Ejemplo: {Color.RESET}{Color.CARAMELO}{ejemplo}{Color.RESET}")
    if accion:
        print(f"{p}  {Color.CIAN}     Accion:  {Color.RESET}{Color.DIM}{accion}{Color.RESET}")
    print(f"{p}  {Color.DIM}Escribe 0 o CANCELAR para abortar y volver atras sin guardar.{Color.RESET}")
    print(sep_in)


def _verificar_cancelacion(val):
    normalizado = val.strip().upper()
    if normalizado in ("0", "CANCELAR"):
        raise OperacionCancelada("Operacion cancelada por el usuario.")


def _input_centrado(prompt):
    ancho = _ancho()
    pfx   = _prefijo(ancho)
    print(f"{pfx}  {Color.CIAN}{prompt}: {Color.RESET}", end="")
    return input().strip()


def pedir_correo(prompt="Correo electronico", obligatorio=True):
    _imprimir_guia(
        "Correo electronico del usuario",
        "usuario@dominio.com  (sin espacios, con @ y punto en dominio)",
        "ejemplo@coffeelytics.com",
        "Se convierte automaticamente a minusculas."
    )
    while True:
        raw = _input_centrado(prompt)
        _verificar_cancelacion(raw)
        val = raw.lower()
        if not obligatorio and val == "":
            return val
        if "@" in val and "." in val.split("@")[-1] and " " not in val:
            return val
        print(Color.error("Formato invalido. Debe contener '@' y dominio con punto. Sin espacios."))


def pedir_codigo(prompt="Codigo", longitud_max=10, ejemplo="INS008"):
    _imprimir_guia(
        f"Codigo identificador (maximo {longitud_max} caracteres alfanumericos)",
        f"Solo letras y numeros, sin espacios, maximo {longitud_max} chars",
        ejemplo,
        "Se convierte automaticamente a MAYUSCULAS."
    )
    while True:
        raw = _input_centrado(prompt)
        _verificar_cancelacion(raw)
        val = raw.upper()
        if val and len(val) <= longitud_max and val.replace("-", "").replace("_", "").isalnum():
            return val
        print(Color.error(
            f"Codigo invalido. Solo letras y numeros, sin espacios, maximo {longitud_max} caracteres."))


def pedir_nombre_propio(prompt="Nombre", max_len=50, ejemplo="Juan Perez"):
    _imprimir_guia(
        "Nombre propio (persona, producto o insumo)",
        f"Texto libre, maximo {max_len} caracteres",
        ejemplo,
        "Se ajusta automaticamente a Formato Titulo: 'juan perez' -> 'Juan Perez'."
    )
    while True:
        raw = _input_centrado(prompt)
        _verificar_cancelacion(raw)
        val = raw.title()
        if val and len(val) <= max_len:
            return val
        if not val:
            print(Color.error("El nombre no puede estar vacio."))
        else:
            print(Color.error(f"El nombre no puede superar {max_len} caracteres."))


def pedir_rfc(prompt="RFC"):
    _imprimir_guia(
        "RFC de persona fisica o moral",
        "12 o 13 caracteres alfanumericos (sin espacios ni guiones)",
        "COF260101TJ8  o  VECJ880326XXX",
        "Se convierte automaticamente a MAYUSCULAS."
    )
    while True:
        raw = _input_centrado(prompt)
        _verificar_cancelacion(raw)
        val = raw.upper().replace("-", "").replace(" ", "")
        if 12 <= len(val) <= 13 and val.isalnum():
            return val
        print(Color.error("RFC invalido. Debe tener 12 o 13 caracteres alfanumericos sin espacios."))


def pedir_telefono(prompt="Telefono"):
    _imprimir_guia(
        "Numero de telefono de 10 digitos",
        "Solo digitos numericos, exactamente 10",
        "6641234567",
        "Se valida que sea exactamente 10 digitos."
    )
    while True:
        raw = _input_centrado(prompt)
        _verificar_cancelacion(raw)
        val = raw.replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
        if val.isdigit() and len(val) == 10:
            return val
        print(Color.error("Telefono invalido. Debe tener exactamente 10 digitos numericos."))


def pedir_numero_positivo(prompt="Cantidad", unidad="", ejemplo="1000",
                          stock_max=None, nombre_campo="cantidad"):
    desc_stock = f"  No puede exceder el stock disponible ({stock_max} {unidad})." \
                 if stock_max is not None else ""
    _imprimir_guia(
        f"{nombre_campo.capitalize()} numerica mayor a cero",
        f"Numero entero o decimal positivo{' en ' + unidad if unidad else ''}",
        ejemplo,
        f"Se registra en la base de datos inmediatamente al confirmar.{desc_stock}"
    )
    while True:
        raw = _input_centrado(f"{prompt}{' (' + unidad + ')' if unidad else ''}")
        _verificar_cancelacion(raw)
        try:
            val = float(raw)
            if val <= 0:
                raise ValueError
            if stock_max is not None and val > float(stock_max):
                print(Color.error(
                    f"La cantidad ({val}) supera el stock disponible ({stock_max} {unidad})."))
                continue
            return val
        except ValueError:
            print(Color.error(
                f"Valor invalido. Ingresa un numero positivo{' mayor a 0' if not raw else ''}."))


def pedir_precio(prompt="Precio unitario ($MXN)", ejemplo="0.85"):
    _imprimir_guia(
        "Precio en pesos mexicanos (MXN)",
        "Numero decimal positivo con hasta 2 decimales",
        ejemplo,
        "El sistema calculara IVA 8% (proveedor frontera) o 16% (interior) automaticamente."
    )
    while True:
        raw = _input_centrado(f"{prompt} $")
        _verificar_cancelacion(raw)
        try:
            val = float(raw)
            if val > 0:
                return val
            raise ValueError
        except ValueError:
            print(Color.error("Precio invalido. Ingresa un numero mayor a 0 (ej. 0.85 o 150)."))


def pedir_motivo(prompt="Motivo", ejemplo="Derrame accidental en barra"):
    _imprimir_guia(
        "Motivo o descripcion de la incidencia",
        "Texto libre, maximo 300 caracteres",
        ejemplo,
        "La primera letra se convierte automaticamente a mayuscula."
    )
    while True:
        raw = _input_centrado(prompt)
        _verificar_cancelacion(raw)
        val = raw.capitalize()
        if val and len(val) <= 300:
            return val
        if not val:
            print(Color.error("El motivo no puede estar vacio."))
        else:
            print(Color.error("El motivo no puede superar 300 caracteres."))


def pedir_fecha(prompt="Fecha (YYYY-MM-DD)"):
    _imprimir_guia(
        "Fecha en formato ISO 8601",
        "YYYY-MM-DD  (anio 4 digitos, mes 2, dia 2)",
        datetime.datetime.now().strftime("%Y-%m-%d"),
        "El sistema buscara todas las ventas de ese empleado en esa fecha exacta."
    )
    while True:
        raw = _input_centrado(prompt)
        _verificar_cancelacion(raw)
        try:
            datetime.datetime.strptime(raw, "%Y-%m-%d")
            return raw
        except ValueError:
            print(Color.error("Formato invalido. Usa YYYY-MM-DD (ej. 2024-12-25)."))


def pedir_entero_positivo(prompt="Folio", ejemplo="5"):
    _imprimir_guia(
        "Numero entero positivo",
        "Solo digitos, sin puntos ni comas",
        ejemplo,
        "El sistema buscara el registro con ese folio en la base de datos."
    )
    while True:
        raw = _input_centrado(prompt)
        _verificar_cancelacion(raw)
        if raw.isdigit() and int(raw) > 0:
            return int(raw)
        print(Color.error("Folio invalido. Ingresa un numero entero positivo."))


def pedir_nombre_cliente():
    _imprimir_guia(
        "Nombre del cliente para el ticket",
        "Texto libre, maximo 50 caracteres. ENTER para 'Mostrador'",
        "Maria Garcia",
        "Se ajusta a Formato Titulo. Aparece impreso en el ticket de venta."
    )
    raw = _input_centrado("Nombre del cliente (ENTER = Mostrador)")
    if not raw:
        return "Mostrador"
    if raw.strip().upper() in ("0", "CANCELAR"):
        return "Mostrador"
    return raw.title()[:50]


def pedir_monto_efectivo(total):
    _imprimir_guia(
        "Monto en efectivo entregado por el cliente",
        f"Numero mayor o igual al total: ${total:.2f}",
        f"{total:.2f}  o  200.00",
        f"El sistema calculara el cambio automaticamente: cambio = monto - ${total:.2f}."
    )
    while True:
        raw = _input_centrado("Monto recibido $")
        _verificar_cancelacion(raw)
        try:
            val = float(raw)
            if val >= total:
                cambio = round(val - total, 2)
                print(Color.ok(f"Cambio: ${cambio:.2f}"))
                return val, cambio
            print(Color.error(f"Monto insuficiente. El total es ${total:.2f}."))
        except ValueError:
            print(Color.error("Ingresa una cantidad numerica valida (ej. 200 o 150.50)."))


def pedir_cantidad_carrito(nombre_producto):
    _imprimir_guia(
        f"Cantidad de '{nombre_producto}' a agregar al pedido",
        "Numero entero positivo (minimo 1)",
        "1  o  2",
        "Se suma al carrito activo. Puedes agregar mas unidades del mismo producto."
    )
    raw = _input_centrado("Cantidad (ENTER = 1)")
    if raw == "" or raw.strip().upper() in ("0", "CANCELAR"):
        return 1
    try:
        cant = int(raw)
        if cant > 0:
            return cant
    except ValueError:
        pass
    return 1