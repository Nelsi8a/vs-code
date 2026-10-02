"""Calculadora Rosa y Lila: GUI Kivy con historial, teclado y control de división entre cero."""

from __future__ import annotations

import logging
import re

from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.core.clipboard import Clipboard
from kivy.core.text import Label as EtiquetaNucleo
from kivy.core.window import Window
from kivy.graphics import Color, Line, Rectangle, RoundedRectangle
from kivy.graphics.texture import Texture
from kivy.logger import Logger
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import ButtonBehavior
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.utils import get_color_from_hex

# Cifras significativas con las que se muestra un resultado y tamanos de la pantalla.
CIFRAS = 15
DECIMALES_MAX = 12
TAMANOS_PANTALLA = (32, 28, 24, 21, 18, 16, 14, 12)
PREFIJO_MAX = 48

FUENTE = "Roboto"

# Medidas de la interfaz; el teclado se ajusta al alto que sobre de la ventana.
MARGEN = dp(20)
ESPACIO = dp(14)
ALTO_CABECERA = dp(78)
ALTO_PANTALLA = dp(104)
ALTO_AYUDA = dp(42)
SEPARACION_TECLADO = dp(10)
ALTO_BOTON_MINIMO = dp(48)

PALETA = {
    "fondo_inicio": "#FFF1F7",
    "fondo_medio": "#F3E8FF",
    "fondo_fin": "#E9DEFF",
    "texto": "#4D3158",
    "titulo": "#71356F",
    "subtitulo": "#97789E",
    "insignia_texto": "#9B3F91",
    "insignia_fondo": "#FFFBFF",
    "insignia_borde": "#E5C8E8",
    "panel_fondo": "#FFFCFF",
    "panel_borde": "#E7CDEB",
    "etiqueta_pantalla": "#A077A5",
    "pantalla": "#54275D",
    "mensaje": "#8A6B91",
    "error": "#B62E6C",
}

# Colores de cada familia de boton (normal, al pasar el raton, al pulsar, borde y letra).
ESTILOS_BOTON = {
    "digito": dict(fondo="#FFFFFF", hover="#FFF7FC", presionado="#F0DDF4", borde="#DFC8E5",
                   texto="#5B3164", tam=19, radio=17),
    "operacion": dict(fondo="#EAD7FA", hover="#DFC0F4", presionado="#CBA0E4", borde="#D2ADE8",
                      texto="#7C3698", tam=23, radio=17),
    "limpiar": dict(fondo="#FFD9E7", hover="#FFC6DB", presionado="#FFB4D0", borde="#F2AEC8",
                    texto="#A52E67", tam=19, radio=17),
    "igual": dict(fondo="#C25ABE", hover="#AE44A6", presionado="#8E3390", borde=None,
                  texto="#FFFFFF", tam=25, radio=17, brillo=True),
    "historial": dict(fondo="#F0DEFA", hover="#E4C7F6", presionado="#D9B2EF", borde="#D2ADE8",
                      texto="#7C3698", tam=15, radio=14),
    "borrar": dict(fondo="#FFD9E7", hover="#FFC6DB", presionado="#FFB4D0", borde="#F2AEC8",
                   texto="#A52E67", tam=15, radio=17),
    "entrada": dict(fondo="#FFFFFF", hover="#FDF2FB", presionado="#F6E6F8", borde="#EBD8F0",
                    texto="#54275D", tam=16, radio=12),
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


def rgba(hex_color, alfa=1.0):
    """Convierte "#RRGGBB" en una tupla RGBA de Kivy."""
    color = get_color_from_hex(hex_color)
    return (color[0], color[1], color[2], alfa)


_MEDIDAS = {}
_TEXTURA_DEGRADADO = None


def ancho_texto(texto, tam):
    """Mide en pixeles el ancho de un texto con la misma fuente de la pantalla."""
    clave = (texto, round(tam, 2))
    if clave not in _MEDIDAS:
        if len(_MEDIDAS) > 4000:
            _MEDIDAS.clear()
        medidor = EtiquetaNucleo(text=texto, font_size=tam, bold=True, font_name=FUENTE)
        medidor.refresh()
        _MEDIDAS[clave] = medidor.width
    return _MEDIDAS[clave]


def degradado_textura():
    """Crea (una sola vez) la textura del degradado diagonal rosa y lila."""
    global _TEXTURA_DEGRADADO
    if _TEXTURA_DEGRADADO is not None:
        return _TEXTURA_DEGRADADO

    ancho = alto = 96
    inicio = [componente for componente in get_color_from_hex(PALETA["fondo_inicio"])[:3]]
    medio = [componente for componente in get_color_from_hex(PALETA["fondo_medio"])[:3]]
    final = [componente for componente in get_color_from_hex(PALETA["fondo_fin"])[:3]]

    datos = bytearray(ancho * alto * 4)
    for y in range(alto):
        for x in range(ancho):
            t = (x / (ancho - 1) + (1 - y / (alto - 1))) / 2
            if t <= 0.55:
                f = t / 0.55
                color = [inicio[i] + (medio[i] - inicio[i]) * f for i in range(3)]
            else:
                f = (t - 0.55) / 0.45
                color = [medio[i] + (final[i] - medio[i]) * f for i in range(3)]
            indice = (y * ancho + x) * 4
            for i in range(3):
                datos[indice + i] = int(round(color[i] * 255))
            datos[indice + 3] = 255

    textura = Texture.create(size=(ancho, alto))
    textura.blit_buffer(bytes(datos), colorfmt="rgba", bufferfmt="ubyte")
    textura.mag_filter = "linear"
    textura.min_filter = "linear"
    _TEXTURA_DEGRADADO = textura
    return textura


def texto_alineado(texto, color, tam, alineacion="left", negrita=False, alto=None):
    """Label de una linea cuyo salto de linea sigue el ancho disponible."""
    etiqueta = Label(
        text=texto,
        color=color,
        font_size=tam,
        font_name=FUENTE,
        bold=negrita,
        halign=alineacion,
        valign="middle",
        size_hint_y=None,
        height=alto if alto is not None else tam * 1.6,
    )
    etiqueta.bind(width=lambda w, v: setattr(w, "text_size", (v, None)))
    return etiqueta


class FondoDegradado(FloatLayout):
    """Capa base: pinta el degradado que cubre toda la ventana."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self._fondo = Rectangle(texture=degradado_textura(), pos=self.pos, size=self.size)
        self.bind(pos=self._ajustar_fondo, size=self._ajustar_fondo)

    def _ajustar_fondo(self, *_args):
        self._fondo.pos = self.pos
        self._fondo.size = self.size


class PanelRedondeado(BoxLayout):
    """Tarjeta con esquinas redondeadas, relleno translucido y borde fino."""

    def __init__(self, radio=22, relleno=(1, 1, 1, 0.9), borde=None, **kwargs):
        self.radio = radio
        super().__init__(**kwargs)
        with self.canvas.before:
            self._color = Color(*relleno)
            self._figura = RoundedRectangle(radius=[radio])
            if borde is not None:
                self._color_borde = Color(*borde)
                self._linea = Line(width=1.2)
        self.bind(pos=self._redibujar, size=self._redibujar)
        self._redibujar()

    def _redibujar(self, *_args):
        self._figura.pos = self.pos
        self._figura.size = self.size
        if hasattr(self, "_linea"):
            self._linea.rounded_rectangle = (self.x, self.y, self.width, self.height, self.radio)


class Boton(ButtonBehavior, Label):
    """Boton redondeado con los colores de su familia y reacción al ratón."""

    def __init__(self, texto="", estilo="digito", descripcion=None, **kwargs):
        self.estilo = estilo
        self.descripcion = descripcion if descripcion is not None else texto
        self.al_pedir_tooltip = None
        self.al_ocultar_tooltip = None
        super().__init__(**kwargs)

        config = ESTILOS_BOTON[estilo]
        self.radio = config["radio"]
        self.text = texto
        self.color = rgba(config["texto"])
        self.font_name = FUENTE
        self.font_size = sp(config["tam"])
        self.bold = True

        with self.canvas.before:
            self._color = Color(*rgba(config["fondo"]))
            self._figura = RoundedRectangle(radius=[self.radio])
            if config.get("brillo"):
                self._color_brillo = Color(1, 1, 1, 0.16)
                self._brillo = RoundedRectangle(radius=[max(self.radio - 3, 2)])
            if config.get("borde"):
                self._color_borde = Color(*rgba(config["borde"]))
                self._linea = Line(width=1.2)

        self._resplandor = False
        self._evento = None
        self.bind(pos=self._redibujar, size=self._redibujar, state=self.pintar,
                  disabled=self._al_desactivarse)
        self._redibujar()
        self.pintar()

    # ---------- dibujado ----------
    def _redibujar(self, *_args):
        self._figura.pos = self.pos
        self._figura.size = self.size
        if hasattr(self, "_brillo"):
            self._brillo.pos = (self.x + dp(3), self.y + dp(3))
            self._brillo.size = (max(self.width - dp(6), 1), max(self.height - dp(6), 1))
        if hasattr(self, "_linea"):
            self._linea.rounded_rectangle = (self.x, self.y, self.width, self.height, self.radio)

    def pintar(self, *_args):
        config = ESTILOS_BOTON[self.estilo]
        if self.state == "down":
            self._color.rgba = rgba(config["presionado"])
        elif self._resplandor:
            self._color.rgba = rgba(config["hover"])
        else:
            self._color.rgba = rgba(config["fondo"])

    def _al_desactivarse(self, _boton, valor):
        self.opacity = 0.45 if valor else 1

    def iluminar(self, dentro):
        """Enciende el color de hover cuando el raton entra o sale del boton."""
        if dentro != self._resplandor:
            self._resplandor = dentro
            self.pintar()

    # ---------- pulsacion larga ----------
    def on_press(self):
        if self.al_ocultar_tooltip:
            self.al_ocultar_tooltip()
        if self.al_pedir_tooltip:
            self._evento = Clock.schedule_once(lambda _dt: self.al_pedir_tooltip(self), 0.45)

    def on_release(self):
        if self._evento is not None:
            self._evento.cancel()
            self._evento = None


class Pantalla(Label):
    """Resultado en curso: reduce la letra para que el numero completo quepa siempre."""

    def __init__(self, **kwargs):
        self.al_copiar = kwargs.pop("al_copiar", None)
        super().__init__(**kwargs)
        self.color = rgba(PALETA["pantalla"])
        self.font_name = FUENTE
        self.bold = True
        self.halign = "right"
        self.valign = "middle"
        self.size_hint_y = None
        self.font_size = sp(TAMANOS_PANTALLA[0])
        self._ajustando = False
        self._ultimo_toque = 0.0
        self.bind(width=self._sincronizar_ancho, texture_size=self.ajustar_fuente)
        self._sincronizar_ancho()
        self.ajustar_fuente()

    def _sincronizar_ancho(self, *_args):
        self.text_size = (self.width, None)

    def ajustar_fuente(self, *_args):
        if self._ajustando or not self.width:
            return
        self._ajustando = True
        try:
            texto = self.text or ""
            disponible = self.width - dp(6)
            elegido = TAMANOS_PANTALLA[-1]
            for tam in TAMANOS_PANTALLA:
                if ancho_texto(texto, sp(tam)) <= disponible:
                    elegido = tam
                    break
            if self.font_size != sp(elegido):
                self.font_size = sp(elegido)
        finally:
            self._ajustando = False

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return super().on_touch_down(touch)

        ahora = Clock.get_time()
        if ahora - self._ultimo_toque < 0.4:
            self._ultimo_toque = 0.0
            if self.al_copiar and self.text:
                self.al_copiar(self.text)
        else:
            self._ultimo_toque = ahora
        return True


class HistorialPopup(ModalView):
    """Ventana con las operaciones realizadas; al elegir una se recupera su resultado."""

    def __init__(self, al_elegir, al_borrar, **kwargs):
        super().__init__(size_hint=(0.9, 0.66), auto_dismiss=True, **kwargs)
        self.al_elegir = al_elegir
        self.al_borrar = al_borrar
        self.panel = PanelRedondeado(
            orientation="vertical",
            spacing=dp(12),
            padding=[dp(20), dp(18), dp(20), dp(18)],
            radio=dp(24),
            relleno=rgba(PALETA["fondo_medio"], 0.99),
            borde=rgba("#DCC6EA"),
        )
        self.add_widget(self.panel)
        self.bind(pos=self._ajustar_panel, size=self._ajustar_panel)
        self._ajustar_panel()

        titulo = texto_alineado("Historial", rgba(PALETA["titulo"]), sp(22), negrita=True, alto=dp(34))
        self.lista = PanelRedondeado(
            orientation="vertical",
            size_hint_y=1,
            padding=dp(8),
            radio=dp(18),
            relleno=rgba("#FFFFFF", 0.94),
            borde=rgba(PALETA["panel_borde"]),
        )
        self.desplazable = ScrollView(do_scroll_x=False, bar_width=dp(6), bar_color=rgba("#D9B9E6"))
        self.contenedor = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(6))
        self.desplazable.add_widget(self.contenedor)
        self.lista.add_widget(self.desplazable)

        botones = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(44), spacing=dp(10))
        self.boton_borrar = Boton("Borrar historial", estilo="borrar")
        self.boton_borrar.bind(on_release=lambda *_: self.borrar())
        boton_cerrar = Boton("Cerrar", estilo="historial")
        boton_cerrar.bind(on_release=lambda *_: self.dismiss())
        botones.add_widget(self.boton_borrar)
        botones.add_widget(Widget())
        botones.add_widget(boton_cerrar)

        self.panel.add_widget(titulo)
        self.panel.add_widget(self.lista)
        self.panel.add_widget(botones)

        self.mostrar_vacio()

    def _ajustar_panel(self, *_args):
        self.panel.pos = self.pos
        self.panel.size = self.size

    def mostrar_vacio(self):
        self.contenedor.clear_widgets()
        vacio = texto_alineado("Sin operaciones todavía", rgba(PALETA["subtitulo"]), sp(15),
                               alineacion="center", alto=dp(40))
        self.contenedor.add_widget(vacio)
        self.contenedor.height = dp(40)
        self.boton_borrar.disabled = True

    def actualizar(self, historial):
        if not historial:
            self.mostrar_vacio()
            return

        self.contenedor.clear_widgets()
        self.boton_borrar.disabled = False
        for entrada in reversed(historial):
            boton = Boton(entrada, estilo="entrada", size_hint_y=None, height=dp(44),
                          halign="left", valign="middle")
            boton.bind(width=lambda w, v: setattr(w, "text_size", (v - dp(24), None)))
            resultado = entrada.rsplit("=", 1)[-1].strip()
            boton.bind(on_release=lambda _b, r=resultado: self.elegir(r))
            self.contenedor.add_widget(boton)

        hijos = self.contenedor.children
        self.contenedor.height = sum(hijo.height for hijo in hijos) + self.contenedor.spacing * (len(hijos) - 1)

    def elegir(self, resultado):
        if resultado:
            self.al_elegir(resultado)

    def borrar(self):
        self.al_borrar()
        self.mostrar_vacio()


class Calculadora(FondoDegradado):
    """Interfaz completa de la calculadora rosa y lila."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.botones = {}
        self._botones_visibles = []
        self.historial = []
        self.ventana_historial = None
        self.reiniciar_pantalla = False

        self.operando = None
        self.operador = None
        self.prefijo = ""
        self.pendiente_porcentaje = False
        self.porcentaje_valor = 0.0
        self.error = False

        self.contenido = BoxLayout(orientation="vertical", spacing=ESPACIO,
                                   padding=[MARGEN, dp(18), MARGEN, dp(18)])
        self.add_widget(self.contenido)
        self.bind(pos=self._ajustar_hijos, size=self._ajustar_hijos)

        self._crear_tooltip()
        self.crear_interfaz()
        self._ajustar_hijos()

        Window.bind(on_key_down=self._al_pulsar_tecla)
        Window.bind(mouse_pos=self._al_mover_raton)

    # ---------- construccion ----------
    def crear_interfaz(self):
        self.contenido.add_widget(self.crear_cabecera())
        self.contenido.add_widget(self.crear_pantalla())
        self.contenido.add_widget(Widget())
        self.contenido.add_widget(self.crear_teclado())
        self.contenido.add_widget(self.crear_ayuda())

    def crear_cabecera(self):
        cabecera = BoxLayout(orientation="horizontal", size_hint_y=None, height=ALTO_CABECERA,
                             spacing=dp(8))

        textos = BoxLayout(orientation="vertical", spacing=dp(0))
        textos.add_widget(texto_alineado("Calculadora", rgba(PALETA["titulo"]), sp(28),
                                          negrita=True, alto=dp(42)))
        textos.add_widget(texto_alineado("Suma, resta, multiplica y divide", rgba(PALETA["subtitulo"]),
                                          sp(13), alto=dp(22)))

        insignia = PanelRedondeado(orientation="horizontal", size_hint=(None, None),
                                   size=(dp(118), dp(30)), pos_hint={"center_y": 0.5},
                                   padding=[dp(6), 0], radio=dp(15),
                                   relleno=rgba(PALETA["insignia_fondo"], 0.8),
                                   borde=rgba(PALETA["insignia_borde"]))
        insignia.add_widget(Label(text="0–9  +  -  ×  ÷", color=rgba(PALETA["insignia_texto"]),
                                  font_size=sp(12), font_name=FUENTE, bold=True,
                                  halign="center", valign="middle"))

        self.boton_historial = Boton("Historial", estilo="historial", size_hint_x=None, width=dp(92),
                                     size_hint_y=None, height=dp(36), pos_hint={"center_y": 0.5})
        self.boton_historial.descripcion = "Ver las operaciones realizadas"
        self.boton_historial.al_ocultar_tooltip = self.ocultar_tooltip
        self.boton_historial.bind(on_release=lambda *_: self.abrir_historial())
        self._botones_visibles.append(self.boton_historial)

        acciones = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(36),
                             pos_hint={"center_y": 0.5}, spacing=dp(8))
        acciones.add_widget(insignia)
        acciones.add_widget(self.boton_historial)

        cabecera.add_widget(textos)
        cabecera.add_widget(acciones)
        return cabecera

    def crear_pantalla(self):
        panel = PanelRedondeado(orientation="vertical", size_hint_y=None, height=ALTO_PANTALLA,
                                spacing=dp(2), padding=[dp(18), dp(10), dp(18), dp(8)], radio=dp(22),
                                relleno=rgba(PALETA["panel_fondo"], 0.9),
                                borde=rgba(PALETA["panel_borde"]))

        etiqueta = texto_alineado("PANTALLA", rgba(PALETA["etiqueta_pantalla"]), sp(11),
                                  negrita=True, alto=dp(15))

        self.pantalla = Pantalla(text="0", height=dp(46), al_copiar=self.al_copiar)

        self.mensaje = Label(text="", color=rgba(PALETA["mensaje"]), font_size=sp(12), font_name=FUENTE,
                             halign="right", valign="middle", size_hint_y=None, height=dp(21),
                             shorten=True, shorten_from="right")
        self.mensaje.bind(width=lambda w, v: setattr(w, "text_size", (v, None)))

        panel.add_widget(etiqueta)
        panel.add_widget(self.pantalla)
        panel.add_widget(self.mensaje)
        return panel

    def crear_teclado(self):
        self.teclado = GridLayout(cols=4, spacing=SEPARACION_TECLADO, size_hint_y=None, height=dp(280))
        self._botones_teclado = []

        for _fila, _columna, texto, estilo, _span in TECLADO:
            boton = Boton(texto, estilo=estilo or "digito", size_hint_y=None, height=dp(56),
                          descripcion=self.descripcion(texto))
            boton.al_pedir_tooltip = self.pedir_tooltip
            boton.al_ocultar_tooltip = self.ocultar_tooltip
            boton.bind(on_release=lambda _b, t=texto: self.pulsar(t))
            self.teclado.add_widget(boton)
            self.botones[texto] = boton
            self._botones_visibles.append(boton)
            self._botones_teclado.append(boton)

        return self.teclado

    def crear_ayuda(self):
        return texto_alineado(
            "Teclado: 0–9  ·  + − * /  ·  Enter =  ·  Esc = C  ·  Retroceso borra"
            "\nDoble clic en la pantalla: copiar el número",
            rgba(PALETA["subtitulo"]), sp(12), alineacion="center", alto=ALTO_AYUDA,
        )

    def _crear_tooltip(self):
        self.tooltip = Label(text="", color=rgba("#FFFFFF"), font_size=sp(13), font_name=FUENTE,
                             bold=True, size_hint=(None, None), opacity=0, disabled=True)
        with self.tooltip.canvas.before:
            Color(*rgba(PALETA["texto"], 0.94))
            self.tooltip_figura = RoundedRectangle(radius=[dp(9)])
        self.tooltip.bind(pos=self._dibujar_tooltip, size=self._dibujar_tooltip,
                          texture_size=self._dibujar_tooltip)
        self.add_widget(self.tooltip)

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

    # ---------- tooltip ----------
    def pedir_tooltip(self, boton):
        texto = boton.descripcion
        if not texto or texto == boton.text:
            return
        self.tooltip.text = texto
        self.tooltip.texture_update()
        self.tooltip.size = (self.tooltip.texture_size[0] + dp(20), self.tooltip.texture_size[1] + dp(8))
        x = boton.center_x - self.tooltip.width / 2
        x = max(dp(6), min(x, self.width - self.tooltip.width - dp(6)))
        y = boton.top + dp(6)
        if y + self.tooltip.height > self.height - dp(6):
            y = boton.y - self.tooltip.height - dp(6)
        self.tooltip.pos = (x, max(y, dp(6)))
        Animation.cancel_all(self.tooltip)
        Animation(opacity=1, d=0.12).start(self.tooltip)

    def ocultar_tooltip(self, *_args):
        if self.tooltip is not None and self.tooltip.opacity:
            Animation.cancel_all(self.tooltip)
            Animation(opacity=0, d=0.1).start(self.tooltip)

    def _dibujar_tooltip(self, *_args):
        self.tooltip_figura.pos = self.tooltip.pos
        self.tooltip_figura.size = self.tooltip.size

    # ---------- pulsaciones ----------
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

        actual = self.pantalla.text or "0"

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

        self.operando = self.a_numero(self.pantalla.text)
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
        b = self.a_numero(self.pantalla.text)
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
        valor = self.pantalla.text or "0"
        if valor in ("0", "0.", "-", "-0", "-0."):
            self.escribir("0")
            return
        self.prefijo = ""
        self.pendiente_porcentaje = False
        self.escribir(valor[1:] if valor.startswith("-") else "-" + valor)

    def porcentaje(self):
        valor = self.a_numero(self.pantalla.text)
        if self.operador is not None and self.operando is not None:
            base = abs(self.operando)
            self.porcentaje_valor = valor
            self.pendiente_porcentaje = True
            # 200 + 10% = 220 · 200 − 10% = 180 · 500 × 10% = 50 · 500 ÷ 10% = 5000
            if self.operador in ("+", "−"):
                self.escribir(self.formatear(base * valor / 100))
            else:
                self.escribir(self.formatear(valor / 100))
        else:
            self.pendiente_porcentaje = False
            self.escribir(self.formatear(valor / 100))

    def cuadrado(self):
        valor = self.a_numero(self.pantalla.text)
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

    # ---------- pantalla y mensajes ----------
    def escribir(self, texto):
        self.error = False
        self.pantalla.text = texto
        self.pantalla.ajustar_fuente()

    def mostrar_mensaje(self, texto, error=False):
        self.error = bool(error)
        self.mensaje.text = texto
        self.mensaje.color = rgba(PALETA["error"] if error else PALETA["mensaje"])
        self.mensaje.bold = bool(error)

    def al_copiar(self, texto):
        Clipboard.copy(texto)
        self.mostrar_mensaje("Número copiado al portapapeles")

    # ---------- operaciones ----------
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

    # ---------- historial ----------
    def registrar(self, entrada):
        self.historial.append(entrada)
        if self.ventana_historial is not None:
            self.ventana_historial.actualizar(self.historial)

    def abrir_historial(self):
        if self.ventana_historial is None:
            self.ventana_historial = HistorialPopup(al_elegir=self.usar_resultado,
                                                     al_borrar=self.borrar_historial)
            self.ventana_historial.bind(on_pre_open=self._abrir_historial)
        self.ventana_historial.actualizar(self.historial)
        if not self.ventana_historial.parent:
            self.ventana_historial.open(self.contenido)

    def _abrir_historial(self, _modal):
        self.ventana_historial.actualizar(self.historial)

    def borrar_historial(self):
        self.historial.clear()
        self.mostrar_mensaje("Historial borrado")

    # ---------- teclado fisico ----------
    def _al_pulsar_tecla(self, _ventana, tecla, _scancode, _codepoint, modificadores):
        if modificadores and any(m in ("ctrl", "alt", "meta") for m in modificadores):
            return

        if tecla in ("enter", "numpadenter", "return"):
            self.pulsar("=")
        elif tecla == "escape":
            self.pulsar("C")
        elif tecla in ("backspace", "delete"):
            self.borrar_ultimo()
        elif tecla in "+-*/":
            self.pulsar({"+": "+", "-": "−", "*": "×", "/": "÷"}[tecla])
        elif tecla in (",", "."):
            self.pulsar(".")
        elif tecla == "%":
            self.pulsar("%")
        elif tecla in ("x", "X"):
            self.pulsar("x²")
        elif tecla in DIGITOS:
            self.pulsar(tecla)

    def borrar_ultimo(self):
        if self.error:
            self.pulsar("C")
            return

        texto = self.pantalla.text or "0"
        if texto in ("0", "0.", "-", "-0"):
            self.pulsar("C")
            return

        self.reiniciar_pantalla = False
        self.prefijo = ""
        self.pendiente_porcentaje = False
        self.escribir(texto[:-1] or "0")

    # ---------- raton y ajuste de la ventana ----------
    def _al_mover_raton(self, _ventana, posicion):
        fuera = posicion[0] < 0 or posicion[1] < 0
        for boton in self._botones_visibles:
            boton.iluminar(False if fuera else boton.collide_point(*posicion))

    def _ajustar_hijos(self, *_args):
        self.contenido.pos = self.pos
        self.contenido.size = self.size
        self._ajustar_teclado()

    def _ajustar_teclado(self):
        """Reparte el alto sobrante entre los cinco renglones del teclado."""
        if not hasattr(self, "teclado"):
            return
        fijo = (ALTO_CABECERA + ALTO_PANTALLA + ALTO_AYUDA + 4 * ESPACIO + 2 * MARGEN
                + 4 * SEPARACION_TECLADO)
        alto = max(5 * ALTO_BOTON_MINIMO, self.height - fijo)
        boton_alto = (alto - 4 * SEPARACION_TECLADO) / 5
        self.teclado.height = 5 * boton_alto + 4 * SEPARACION_TECLADO
        for boton in self._botones_teclado:
            boton.height = boton_alto

    def on_touch_down(self, touch):
        self.ocultar_tooltip()
        return super().on_touch_down(touch)


class CalculadoraApp(App):
    def build(self):
        # Kivy exige fijar los dos mínimos; en la primera asignación avisa porque
        # el otro todavía vale cero, así que ese aviso se silencia a propósito.
        nivel = Logger.level
        Logger.setLevel(logging.ERROR)
        Window.minimum_width = 470
        Window.minimum_height = 600
        Logger.setLevel(nivel)
        Window.size = (490, 680)
        Window.clearcolor = rgba(PALETA["fondo_medio"])
        self.title = "Calculadora Rosa y Lila"
        return Calculadora()


def main():
    CalculadoraApp().run()


if __name__ == "__main__":
    main()