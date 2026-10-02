"""Calculadora Rosa y Lila: GUI wxPython con historial, teclado y control de división entre cero."""

from __future__ import annotations

import re
import sys

import wx

# Cifras significativas con las que se muestra un resultado y tamanos de la pantalla.
# wxFont mide en puntos, no en pixeles: los valores salen del diseno original (px * 0.75).
CIFRAS = 15
DECIMALES_MAX = 12
TAMANOS_PANTALLA = (24, 21, 18, 16, 14, 12, 10, 9)
PREFIJO_MAX = 48
FAMILIA = "Segoe UI"

# Paleta: wxPython no usa hojas de estilo, asi que los colores viven aqui.
TONOS = {
    "fondo_inicio": "#FFF1F7",
    "fondo_fin": "#E9DEFF",
    "tinta": "#4D3158",
    "titulo": "#71356F",
    "subtitulo": "#97789E",
    "insignia_texto": "#9B3F91",
    "insignia_fondo": "#FBF1FC",
    "insignia_borde": "#E5C8E8",
    "pantalla_caja": "#FCF7FD",
    "pantalla_borde": "#E7CDEB",
    "pantalla_texto": "#54275D",
    "etiqueta_pantalla": "#A077A5",
    "mensaje": "#8A6B91",
    "mensaje_error": "#B62E6C",
    "historial_texto": "#54275D",
    "historial_fondo": "#FCF7FD",
    "historial_borde": "#E7CDEB",
}

# Aspecto de cada tipo de boton del teclado (tamanos de fuente en puntos, alto en pixeles).
ASPECTOS = {
    "": {
        "fondo": "#FFFFFF",
        "borde": "#DFC8E5",
        "texto": "#5B3164",
        "tam": 14,
        "alto": 48,
        "radio": 17,
    },
    "operacion": {
        "fondo": "#EAD7FA",
        "borde": "#D2ADE8",
        "texto": "#7C3698",
        "tam": 17,
        "alto": 48,
        "radio": 17,
    },
    "limpiar": {
        "fondo": "#FFD9E7",
        "borde": "#F2AEC8",
        "texto": "#A52E67",
        "tam": 14,
        "alto": 48,
        "radio": 17,
    },
    "igual": {
        "fondo": "#E674BE",
        "borde": "#E674BE",
        "texto": "#FFFFFF",
        "tam": 19,
        "alto": 48,
        "radio": 17,
        "degradado": ("#E674BE", "#A149C6"),
    },
    "historial": {
        "fondo": "#F0DEFA",
        "borde": "#D2ADE8",
        "texto": "#7C3698",
        "tam": 11,
        "alto": 38,
        "radio": 12,
    },
    "borrar": {
        "fondo": "#FFD9E7",
        "borde": "#F2AEC8",
        "texto": "#A52E67",
        "tam": 11,
        "alto": 40,
        "radio": 12,
    },
}

# Disposición del teclado: (renglón, columna, texto, nombre de estilo, columnas que ocupa)
TECLADO = [
    (0, 0, "7", "", 1),
    (0, 1, "8", "", 1),
    (0, 2, "9", "", 1),
    (0, 3, "÷", "operacion", 1),
    (1, 0, "4", "", 1),
    (1, 1, "5", "", 1),
    (1, 2, "6", "", 1),
    (1, 3, "×", "operacion", 1),
    (2, 0, "1", "", 1),
    (2, 1, "2", "", 1),
    (2, 2, "3", "", 1),
    (2, 3, "−", "operacion", 1),
    (3, 0, "±", "operacion", 1),
    (3, 1, "%", "operacion", 1),
    (3, 2, "x²", "operacion", 1),
    (3, 3, "+", "operacion", 1),
    (4, 0, "C", "limpiar", 1),
    (4, 1, "0", "", 1),
    (4, 2, ".", "", 1),
    (4, 3, "=", "igual", 1),
]

NOMBRES_OPERACION = {"+": "Suma", "−": "Resta", "×": "Multiplicación", "÷": "División"}
SIMBOLO_A_LLAVE = {"+": "+", "−": "-", "×": "*", "÷": "/"}
DIGITOS = "0123456789"
PATRON_NUMERO = re.compile(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?")


def limpiar_texto(texto):
    return (texto or "0").strip().replace(",", ".").replace("−", "-")


def fuente(tam, peso=wx.FONTWEIGHT_NORMAL):
    info = wx.FontInfo(tam)
    info.FaceName(FAMILIA)
    info.Weight(peso)
    return wx.Font(info)


def aclarar(color, factor):
    return wx.Colour(
        min(255, int(color.Red() + (255 - color.Red()) * factor)),
        min(255, int(color.Green() + (255 - color.Green()) * factor)),
        min(255, int(color.Blue() + (255 - color.Blue()) * factor)),
    )


def oscurecer(color, factor):
    return wx.Colour(
        int(color.Red() * (1 - factor)),
        int(color.Green() * (1 - factor)),
        int(color.Blue() * (1 - factor)),
    )


class FondoDegradado(wx.Panel):
    """Panel que pinta el fondo con degradado de la ventana."""

    def __init__(self, parent):
        super().__init__(parent, style=wx.FULL_REPAINT_ON_RESIZE)
        self.inicio = wx.Colour(TONOS["fondo_inicio"])
        self.fin = wx.Colour(TONOS["fondo_fin"])
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.Bind(wx.EVT_PAINT, self.al_pintar)

    def al_pintar(self, evento):
        dc = wx.PaintDC(self)
        dc.SetPen(wx.Pen(self.fin))
        dc.SetBrush(wx.Brush(self.fin))
        area = wx.Rect(0, 0, *self.GetClientSize())
        dc.DrawRectangle(area)
        try:
            dc.GradientFillLinear(area, self.inicio, self.fin, wx.DOWN)
        except (AttributeError, NotImplementedError, TypeError):
            pass


class PanelRedondeado(wx.Panel):
    """Tarjeta con esquinas redondeadas (pantalla, insignias, listas)."""

    def __init__(self, parent, radio=18, relleno=None, borde=None):
        super().__init__(parent, style=wx.FULL_REPAINT_ON_RESIZE)
        self.radio = radio
        self.relleno = wx.Colour(relleno or TONOS["pantalla_caja"])
        self.borde = wx.Colour(borde or TONOS["pantalla_borde"])
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.Bind(wx.EVT_PAINT, self.al_pintar)

    def al_pintar(self, evento):
        dc = wx.PaintDC(self)
        dc.SetPen(wx.Pen(self.borde, 1))
        dc.SetBrush(wx.Brush(self.relleno))
        dc.DrawRoundedRectangle(0, 0, *self.GetClientSize(), self.radio)


class EtiquetaRedondeada(PanelRedondeado):
    """Insignia con texto centrado."""

    def __init__(self, parent, texto, tam=12, relleno=None, borde=None, tinta=None):
        super().__init__(
            parent,
            radio=14,
            relleno=relleno or TONOS["insignia_fondo"],
            borde=borde or TONOS["insignia_borde"],
        )
        self.texto = texto
        self.fuente_texto = fuente(tam)
        self.tinta = wx.Colour(tinta or TONOS["insignia_texto"])
        dc = wx.ClientDC(self)
        dc.SetFont(self.fuente_texto)
        ancho, alto = dc.GetTextExtent(texto)
        self.SetMinSize((ancho + 24, alto + 14))
        self.Bind(wx.EVT_PAINT, self.al_pintar)

    def al_pintar(self, evento):
        super().al_pintar(evento)
        dc = wx.PaintDC(self)
        dc.SetFont(self.fuente_texto)
        dc.SetTextForeground(self.tinta)
        dc.DrawLabel(self.texto, wx.Rect(0, 0, *self.GetClientSize()),
                     wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL)


class BotonRedondeado(wx.Window):
    """Boton con esquinas redondeadas pintado a mano.

    En Windows los wx.Button nativos ignoran DoPaint, asi que se dibuja aqui
    y se reenvia un wx.EVT_BUTTON normal para no cambiar la forma de usar la app.
    """

    def __init__(self, parent, etiqueta, estilo=""):
        super().__init__(parent, style=wx.FULL_REPAINT_ON_RESIZE)
        self.aspecto = ASPECTOS.get(estilo, ASPECTOS[""])
        self.etiqueta = etiqueta
        self.radio = self.aspecto["radio"]
        self.degradado = self.aspecto.get("degradado")
        self.fondo = wx.Colour(self.aspecto["fondo"])
        self.borde = wx.Colour(self.aspecto["borde"])
        self.tinta = wx.Colour(self.aspecto["texto"])
        self.fuente_texto = fuente(self.aspecto["tam"], wx.FONTWEIGHT_BOLD)
        self.habilitado = True
        self.encima = False
        self.presionado = False

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.SetFont(self.fuente_texto)
        self.SetCursor(wx.Cursor(wx.CURSOR_HAND))

        dc = wx.ClientDC(self)
        dc.SetFont(self.fuente_texto)
        ancho, alto = dc.GetTextExtent(etiqueta)
        self.SetMinSize((ancho + 30, self.aspecto["alto"]))

        self.Bind(wx.EVT_PAINT, self.al_pintar)
        self.Bind(wx.EVT_LEFT_DOWN, self.al_presionar)
        self.Bind(wx.EVT_LEFT_UP, self.al_soltar)
        self.Bind(wx.EVT_MOUSE_CAPTURE_LOST, self.al_soltar_captura)
        self.Bind(wx.EVT_ENTER_WINDOW, self.al_entrar)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.al_salir)

    # ------------------------------------------------------------ estado visible
    def habilitar(self, valor=True):
        self.habilitado = bool(valor)
        self.SetCursor(wx.Cursor(wx.CURSOR_HAND if self.habilitado else wx.CURSOR_ARROW))
        self.Refresh()

    def colores(self):
        if not self.habilitado:
            return wx.Colour("#F3EDF5"), wx.Colour("#E4DCE6"), wx.Colour("#A99FAB"), None
        if self.presionado:
            fondo = oscurecer(self.fondo, 0.12)
            borde = oscurecer(self.borde, 0.12)
        elif self.encima:
            fondo = aclarar(self.fondo, 0.35)
            borde = aclarar(self.borde, 0.35)
        else:
            fondo, borde = self.fondo, self.borde
        if self.degradado:
            inicio, fin = self.degradado
            if self.presionado:
                degradado = (oscurecer(wx.Colour(inicio), 0.12), oscurecer(wx.Colour(fin), 0.12))
            else:
                degradado = (wx.Colour(inicio), wx.Colour(fin))
            return fondo, borde, self.tinta, degradado
        return fondo, borde, self.tinta, None

    # ------------------------------------------------------------------ pintado
    def al_pintar(self, evento):
        fondo, borde, tinta, degradado = self.colores()
        dc = wx.PaintDC(self)
        dc.SetPen(wx.Pen(borde, 1))
        dc.SetBrush(wx.Brush(fondo))
        dc.DrawRoundedRectangle(0, 0, *self.GetClientSize(), self.radio)
        if degradado is not None:
            try:
                dc.GradientFillLinear(
                    wx.Rect(0, 0, *self.GetClientSize()), degradado[0], degradado[1], wx.RIGHT
                )
            except (AttributeError, NotImplementedError, TypeError):
                pass
        dc.SetFont(self.fuente_texto)
        dc.SetTextForeground(tinta)
        dc.DrawLabel(self.etiqueta, wx.Rect(0, 0, *self.GetClientSize()),
                     wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL)

    # ------------------------------------------------------------------ raton
    def al_presionar(self, evento):
        if not self.habilitado:
            return
        self.presionado = True
        self.CaptureMouse()
        self.Refresh()

    def al_soltar(self, evento):
        if not self.presionado:
            return
        self.presionado = False
        dentro = self.contiene(evento.GetPosition())
        self.ReleaseMouse()
        if dentro and self.habilitado:
            self.lanzar_evento()
        self.Refresh()

    def al_soltar_captura(self, evento):
        self.presionado = False
        self.Refresh()

    def al_entrar(self, evento):
        self.encima = True
        self.Refresh()

    def al_salir(self, evento):
        self.encima = False
        self.presionado = False
        self.Refresh()

    def contiene(self, punto):
        ancho, alto = self.GetClientSize()
        return 0 <= punto.x < ancho and 0 <= punto.y < alto

    def lanzar_evento(self):
        evento = wx.CommandEvent(wx.EVT_BUTTON.typeId, self.GetId())
        evento.SetEventObject(self)
        evento.SetString(self.etiqueta)
        wx.PostEvent(self, evento)


class HistorialDialog(wx.Dialog):
    """Ventana con las operaciones realizadas; al elegir una se recupera su resultado."""

    def __init__(self, parent, titulo="Historial de operaciones") -> None:
        super().__init__(parent, title=titulo, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.al_elegir = None
        self.resultados = []
        self.crear_interfaz()
        self.SetMinSize((420, 460))
        self.actualizar(getattr(parent, "historial", []))

    def crear_interfaz(self) -> None:
        fondo = FondoDegradado(self)
        raiz = wx.BoxSizer(wx.VERTICAL)

        titulo = wx.StaticText(fondo, label="Historial")
        titulo.SetForegroundColour(wx.Colour(TONOS["titulo"]))
        titulo.SetFont(fuente(17, wx.FONTWEIGHT_BOLD))
        raiz.Add(titulo, 0, wx.LEFT | wx.TOP, 28)
        raiz.Add((-1, 6), 0)

        self.lista = wx.ListBox(fondo, style=wx.LB_SINGLE)
        self.lista.SetBackgroundColour(wx.Colour(TONOS["historial_fondo"]))
        self.lista.SetForegroundColour(wx.Colour(TONOS["historial_texto"]))
        self.lista.SetFont(fuente(12))
        self.lista.SetToolTip("Elige una operación para usar su resultado")
        self.lista.Bind(wx.EVT_LISTBOX, self.elegir)
        raiz.Add(self.lista, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 28)

        raiz.Add((-1, 12), 0)

        botones = wx.BoxSizer(wx.HORIZONTAL)
        self.boton_borrar = BotonRedondeado(fondo, "Borrar historial", "borrar")
        self.boton_borrar.SetToolTip("Eliminar todas las operaciones guardadas")
        self.boton_borrar.Bind(wx.EVT_BUTTON, self.borrar)

        cerrar = BotonRedondeado(fondo, "Cerrar", "")
        cerrar.SetToolTip("Cerrar el historial")
        cerrar.Bind(wx.EVT_BUTTON, lambda evento: self.EndModal(wx.ID_CANCEL))

        botones.Add(self.boton_borrar, 0)
        botones.AddStretchSpacer()
        botones.Add(cerrar, 0)
        raiz.Add(botones, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 28)

        fondo.SetSizer(raiz)

    def mostrar_vacio(self) -> None:
        self.lista.Set(["Sin operaciones todavía"])
        self.resultados = []
        self.boton_borrar.habilitar(False)

    def actualizar(self, historial) -> None:
        if not historial:
            self.mostrar_vacio()
            return

        self.lista.Set(list(reversed(historial)))
        self.resultados = [entrada.rsplit("=", 1)[-1].strip() for entrada in reversed(historial)]
        self.boton_borrar.habilitar(True)

    def elegir(self, evento) -> None:
        indice = self.lista.GetSelection()
        if indice == wx.NOT_FOUND or indice >= len(self.resultados):
            return
        resultado = self.resultados[indice]
        if resultado and callable(self.al_elegir):
            self.al_elegir(resultado)

    def borrar(self, evento) -> None:
        padre = self.GetParent()
        historial = getattr(padre, "historial", None)
        if historial is not None:
            historial.clear()
        self.mostrar_vacio()


class Calculadora(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Calculadora Rosa y Lila")

        self.botones = {}
        self.historial = []
        self.ventana_historial = None
        self.reiniciar_pantalla = False

        self.operando = None
        self.operador = None
        self.prefijo = ""
        self.pendiente_porcentaje = False
        self.porcentaje_valor = 0.0
        self.error = False

        self.SetMinSize((480, 610))
        self.SetSize((490, 650))

        self.crear_interfaz()

        self.Bind(wx.EVT_CHAR_HOOK, self.al_tecla)
        self.Bind(wx.EVT_SIZE, self.al_redimensionar)
        self.Bind(wx.EVT_CLOSE, lambda evento: self.Destroy())

    # ---------------------------------------------------------------- interfaz
    def crear_interfaz(self):
        self.fondo = FondoDegradado(self)
        raiz = wx.BoxSizer(wx.VERTICAL)
        self.fondo.SetSizer(raiz)

        raiz.Add(self.crear_cabecera(), 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 30)
        raiz.Add((-1, 18), 0)

        raiz.Add(self.crear_pantalla(), 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 30)
        raiz.Add((-1, 18), 0)

        raiz.Add(self.crear_teclado(), 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 30)
        raiz.AddStretchSpacer()

        ayuda = wx.StaticText(self.fondo, label="Teclado: 0-9  ·  + − * /  ·  Enter =  ·  Esc = C  ·  Retroceso borra")
        ayuda.SetForegroundColour(wx.Colour(TONOS["subtitulo"]))
        ayuda.SetFont(fuente(10))
        ayuda.Wrap(400)
        raiz.Add(ayuda, 0, wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT | wx.BOTTOM, 30)

    def crear_cabecera(self):
        cabecera = wx.FlexGridSizer(1, 3, 12, 12)
        cabecera.AddGrowableCol(0, 1)

        textos = wx.BoxSizer(wx.VERTICAL)
        titulo = wx.StaticText(self.fondo, label="Calculadora")
        titulo.SetForegroundColour(wx.Colour(TONOS["titulo"]))
        titulo.SetFont(fuente(22, wx.FONTWEIGHT_BOLD))
        subtitulo = wx.StaticText(self.fondo, label="Suma, resta, multiplica y divide")
        subtitulo.SetForegroundColour(wx.Colour(TONOS["subtitulo"]))
        subtitulo.SetFont(fuente(10))
        textos.Add(titulo)
        textos.Add(subtitulo)

        insignia = EtiquetaRedondeada(self.fondo, "0-9  +  -  ×  ÷")

        self.boton_historial = BotonRedondeado(self.fondo, "Historial", "historial")
        self.boton_historial.SetToolTip("Ver las operaciones realizadas")
        self.boton_historial.Bind(wx.EVT_BUTTON, self.abrir_historial)

        cabecera.Add(textos, 0, wx.ALIGN_CENTER_VERTICAL)
        cabecera.Add(insignia, 0, wx.ALIGN_CENTER_VERTICAL)
        cabecera.Add(self.boton_historial, 0, wx.ALIGN_CENTER_VERTICAL)
        return cabecera

    def crear_pantalla(self):
        contenedor = PanelRedondeado(self.fondo, radio=22)
        interior = wx.BoxSizer(wx.VERTICAL)
        contenedor.SetSizer(interior)

        etiqueta = wx.StaticText(contenedor, label="PANTALLA")
        etiqueta.SetForegroundColour(wx.Colour(TONOS["etiqueta_pantalla"]))
        etiqueta.SetFont(fuente(8, wx.FONTWEIGHT_BOLD))
        interior.Add(etiqueta, 0, wx.LEFT | wx.RIGHT | wx.TOP, 22)

        self.pantalla = wx.TextCtrl(
            contenedor, value="0", style=wx.TE_READONLY | wx.TE_RIGHT | wx.TE_BESTWRAP
        )
        self.pantalla.SetBackgroundColour(wx.Colour(TONOS["pantalla_caja"]))
        self.pantalla.SetForegroundColour(wx.Colour(TONOS["pantalla_texto"]))
        self.pantalla.SetFont(fuente(TAMANOS_PANTALLA[0]))
        self.pantalla.SetToolTip("Resultado y operandos en curso (puedes copiarlo)")
        self.pantalla.SetMinSize((-1, 46))
        self.pantalla.Bind(wx.EVT_TEXT, self.ajustar_fuente_pantalla)
        interior.Add(self.pantalla, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 18)

        self.mensaje = wx.StaticText(contenedor, label="")
        self.mensaje.SetForegroundColour(wx.Colour(TONOS["mensaje"]))
        self.mensaje.SetFont(fuente(9))
        self.mensaje.SetMinSize((-1, 20))
        interior.Add(self.mensaje, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 14)

        return contenedor

    def crear_teclado(self):
        teclado = wx.FlexGridSizer(5, 4, 12, 12)
        teclado.AddGrowableCol(0, 1)
        teclado.AddGrowableCol(1, 1)
        teclado.AddGrowableCol(2, 1)
        teclado.AddGrowableCol(3, 1)

        for _fila, _columna, texto, estilo, _span in TECLADO:
            boton = BotonRedondeado(self.fondo, texto, estilo)
            boton.SetToolTip(self.descripcion(texto))
            boton.Bind(wx.EVT_BUTTON, lambda evento, t=texto: self.pulsar(t))
            teclado.Add(boton, 0, wx.EXPAND)
            self.botones[texto] = boton

        for fila in range(5):
            teclado.AddGrowableRow(fila, 1)

        return teclado

    @staticmethod
    def descripcion(texto):
        textos = {
            "C": "Borrar la pantalla",
            "=": "Calcular el resultado",
            "±": "Cambiar el signo",
            "%": "Porcentaje del operando (sin operador: dividir entre cien)",
            "x²": "Elevar al cuadrado",
        }
        return textos.get(texto, texto)

    # ---------------------------------------------------------------- pulsaciones
    def pulsar(self, texto):
        if texto in ("+", "−", "×", "÷"):
            self.elegir_operador(texto)
        elif texto == "=":
            self.calcular()
        elif texto == "C":
            self.limpiar()
        elif texto == "±":
            self.cambiar_signo()
        elif texto == "%":
            self.porcentaje()
        elif texto == "x²":
            self.cuadrado()
        else:
            self.ingresar(texto)

    def ingresar(self, texto):
        if self.error:
            self.limpiar()

        if self.reiniciar_pantalla:
            self.reiniciar_pantalla = False
            self.escribir("0." if texto == "." else texto)
            return

        # Cualquier cifra escrita invalida la expresión encadenada anterior.
        self.prefijo = ""
        self.pendiente_porcentaje = False

        actual = self.pantalla.GetValue() or "0"

        if texto == ".":
            if "." in actual:
                return
            nuevo = "-0." if actual == "-" else ("0." if actual == "" else actual + ".")
        elif actual == "-":
            nuevo = "-" + texto
        elif actual == "0":
            nuevo = texto
        elif actual == "-0":
            nuevo = "-" + texto
        else:
            nuevo = actual + texto

        if len(nuevo.lstrip("-").replace(".", "")) > CIFRAS:
            return

        self.escribir(nuevo)

    def elegir_operador(self, op):
        if self.operador is not None and not self.reiniciar_pantalla:
            if not self.calcular():
                return

        self.operando = self.a_numero(self.pantalla.GetValue())
        self.operador = op
        self.reiniciar_pantalla = True
        self.pendiente_porcentaje = False
        self.mostrar_mensaje(f"{self.prefijo}{self.formatear(self.operando)} {op}")

    def calcular(self):
        if self.operador is None or self.operando is None:
            self.mostrar_mensaje("Primero elige un operador")
            return False

        op = self.operador
        a = self.operando
        b = self.a_numero(self.pantalla.GetValue())
        porcentaje = self.pendiente_porcentaje
        self.pendiente_porcentaje = False

        try:
            resultado = self.aplicar(op, a, b)
        except ZeroDivisionError:
            self.fallo("No se puede dividir entre cero")
            return False

        if resultado != resultado or abs(resultado) == float("inf"):
            self.fallo("El resultado es demasiado grande")
            return False

        ta = self.formatear(a)
        tb = f"{self.formatear(self.porcentaje_valor)}%" if porcentaje else self.formatear(b)
        tr = self.formatear(resultado)
        izquierda = f"{ta} {op} {tb}"
        expresion = f"{self.prefijo}{izquierda} = {tr}"

        self.prefijo = f"({self.prefijo}{izquierda}) + "
        if len(self.prefijo) > PREFIJO_MAX:
            self.prefijo = ""

        self.reiniciar_estado()
        self.reiniciar_pantalla = True
        self.escribir(tr)
        self.registrar(f"{NOMBRES_OPERACION[op]}: {expresion}")
        self.mostrar_mensaje(expresion)
        return True

    def fallo(self, mensaje):
        self.reiniciar_estado()
        self.reiniciar_pantalla = True
        self.prefijo = ""
        self.pendiente_porcentaje = False
        self.escribir("0")
        self.mostrar_mensaje(mensaje, True)

    def reiniciar_estado(self):
        self.operando = None
        self.operador = None

    def limpiar(self):
        self.reiniciar_estado()
        self.reiniciar_pantalla = False
        self.prefijo = ""
        self.pendiente_porcentaje = False
        self.escribir("0")
        self.mostrar_mensaje("")

    def cambiar_signo(self):
        valor = self.pantalla.GetValue() or "0"
        if valor in ("0", "0.", "-", "-0", "-0."):
            self.escribir("0")
            return
        self.prefijo = ""
        self.pendiente_porcentaje = False
        self.escribir(valor[1:] if valor.startswith("-") else "-" + valor)

    def porcentaje(self):
        valor = self.a_numero(self.pantalla.GetValue())
        if self.operador is not None and self.operando is not None:
            base = abs(self.operando)
            self.porcentaje_valor = valor
            self.pendiente_porcentaje = True
            # 200 + 10% = 220 · 200 - 10% = 180 · 500 × 10% = 50 · 500 ÷ 10% = 5000
            if self.operador in ("+", "−"):
                self.escribir(self.formatear(base * valor / 100))
            else:
                self.escribir(self.formatear(valor / 100))
        else:
            self.pendiente_porcentaje = False
            self.escribir(self.formatear(valor / 100))

    def cuadrado(self):
        valor = self.a_numero(self.pantalla.GetValue())
        resultado = valor * valor
        if resultado != resultado or abs(resultado) == float("inf"):
            self.mostrar_mensaje("El resultado es demasiado grande", True)
            return
        tv = self.formatear(valor)
        tr = self.formatear(resultado)
        self.prefijo = f"({tv}²) + "
        self.pendiente_porcentaje = False
        self.escribir(tr)
        self.registrar(f"Cuadrado: {tv} ^ 2 = {tr}")
        self.mostrar_mensaje(f"{tv}² = {tr}")

    def usar_resultado(self, valor):
        if not self.es_numero(valor):
            return
        self.reiniciar_estado()
        self.reiniciar_pantalla = True
        self.prefijo = ""
        self.pendiente_porcentaje = False
        self.escribir(valor)
        self.mostrar_mensaje("Resultado recuperado del historial")

    # ---------------------------------------------------------------- pantalla
    def escribir(self, texto):
        self.error = False
        self.pantalla.SetValue(texto)
        self.pantalla.SetInsertionPointEnd()
        self.ajustar_fuente_pantalla()

    def ajustar_fuente_pantalla(self, evento=None):
        """Reduce la letra de la pantalla para que el numero completo quepa siempre."""
        if not hasattr(self, "pantalla"):
            return

        ancho = self.pantalla.GetClientSize().width
        if ancho < 60:
            return

        texto = self.pantalla.GetValue() or ""
        dc = wx.ClientDC(self.pantalla)
        elegido = TAMANOS_PANTALLA[-1]
        for tam in TAMANOS_PANTALLA:
            dc.SetFont(fuente(tam))
            if dc.GetTextExtent(texto)[0] <= ancho - 6:
                elegido = tam
                break

        actual = self.pantalla.GetFont().GetPointSize()
        if actual != elegido:
            self.pantalla.SetFont(fuente(elegido))

    def al_redimensionar(self, evento):
        self.ajustar_fuente_pantalla()
        evento.Skip()

    def mostrar_mensaje(self, texto, error=False):
        self.error = bool(error)
        self.mensaje.SetLabel(texto)
        self.mensaje.SetForegroundColour(
            wx.Colour(TONOS["mensaje_error"] if error else TONOS["mensaje"])
        )
        self.mensaje.SetFont(fuente(9, wx.FONTWEIGHT_BOLD if error else wx.FONTWEIGHT_NORMAL))
        self.mensaje.Refresh()
        self.Layout()

    # ---------------------------------------------------------------- operaciones
    @staticmethod
    def aplicar(op, a, b):
        llave = SIMBOLO_A_LLAVE.get(op, op)
        if llave == "+":
            return a + b
        if llave == "-":
            return a - b
        if llave == "*":
            return a * b
        if llave == "/":
            if b == 0:
                raise ZeroDivisionError("No se puede dividir entre cero")
            return a / b
        raise ValueError(f"Operador desconocido: {op}")

    @staticmethod
    def es_numero(texto):
        return PATRON_NUMERO.fullmatch(limpiar_texto(texto)) is not None

    @staticmethod
    def a_numero(texto):
        limpio = limpiar_texto(texto)
        if not PATRON_NUMERO.fullmatch(limpio):
            return 0.0
        try:
            return float(limpio)
        except ValueError:
            return 0.0

    @staticmethod
    def formatear(numero):
        """Devuelve el numero en decimal plano (nunca notacion cientifica ilegible)."""
        if numero != numero:
            return "NaN"
        if numero == float("inf"):
            return "∞"
        if numero == float("-inf"):
            return "-∞"
        if numero == 0:
            return "0"

        negativo = numero < 0
        valor = abs(numero)
        digitos = len(str(int(valor)))

        if digitos > CIFRAS:
            mantisa, exponente = f"{valor:.{CIFRAS - 1}e}".split("e")
            mantisa = mantisa.rstrip("0").rstrip(".")
            return f"{'-' if negativo else ''}{mantisa}e{exponente}"

        decimales = min(DECIMALES_MAX, CIFRAS - digitos)
        texto = f"{valor:.{decimales}f}"
        if "." in texto:
            texto = texto.rstrip("0").rstrip(".")
        return f"{'-' if negativo else ''}{texto or '0'}"

    # ---------------------------------------------------------------- historial
    def registrar(self, entrada):
        self.historial.append(entrada)
        if self.ventana_historial is not None and self.ventana_historial.IsShown():
            self.ventana_historial.actualizar(self.historial)

    def abrir_historial(self, evento=None):
        if self.ventana_historial is None:
            self.ventana_historial = HistorialDialog(self)
            self.ventana_historial.al_elegir = self.usar_resultado
        self.ventana_historial.actualizar(self.historial)
        self.ventana_historial.Show()
        self.ventana_historial.Raise()

    # ---------------------------------------------------------------- teclado fisico
    def al_tecla(self, evento):
        codigo = evento.GetKeyCode()
        tecla = evento.GetUnicodeKey()

        if codigo in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
            self.pulsar("=")
        elif codigo == wx.WXK_ESCAPE:
            self.pulsar("C")
        elif codigo in (wx.WXK_BACK, wx.WXK_DELETE):
            self.borrar_ultimo()
        elif tecla in "+-*/":
            self.pulsar({"+": "+", "-": "−", "*": "×", "/": "÷"}[tecla])
        elif tecla == ",":
            self.pulsar(".")
        elif tecla == "%":
            self.pulsar("%")
        elif tecla in ("x", "X"):
            self.pulsar("x²")
        elif tecla in DIGITOS:
            self.pulsar(tecla)
        else:
            evento.Skip()

    def borrar_ultimo(self):
        if self.error:
            self.pulsar("C")
            return

        texto = self.pantalla.GetValue() or "0"
        if texto in ("0", "0.", "-", "-0"):
            self.pulsar("C")
            return

        self.reiniciar_pantalla = False
        self.prefijo = ""
        self.pendiente_porcentaje = False
        self.escribir(texto[:-1] or "0")


def main():
    app = wx.App(False)
    app.SetAppName("Calculadora Rosa y Lila")
    ventana = Calculadora()
    ventana.Show()
    app.MainLoop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
