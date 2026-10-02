"""Calculadora Rosa y Lila: GUI PyQt5 con historial, teclado y control de división entre cero."""

from __future__ import annotations

import re
import sys

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QFontMetrics
from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

# Cifras significativas con las que se muestra un resultado y tamanos de la pantalla.
CIFRAS = 15
DECIMALES_MAX = 12
TAMANOS_PANTALLA = (32, 28, 24, 21, 18, 16, 14, 12)
PREFIJO_MAX = 48

REGLAS_FUENTE = "\n".join(
    f'            QLineEdit#pantalla[tam="{t}"] {{ font-size: {t}px; }}'
    for t in TAMANOS_PANTALLA
)

ESTILO = """
            QMainWindow {
                background-color: #F6EEFC;
            }

            QWidget {
                color: #4D3158;
                font-family: "Segoe UI", sans-serif;
            }

            QWidget#fondo {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #FFF1F7,
                    stop: 0.55 #F3E8FF,
                    stop: 1 #E9DEFF
                );
            }

            QLabel#titulo {
                color: #71356F;
                font-size: 30px;
                font-weight: 700;
            }

            QLabel#subtitulo {
                color: #97789E;
                font-size: 14px;
            }

            QLabel#insignia {
                color: #9B3F91;
                background-color: rgba(255, 255, 255, 190);
                border: 1px solid #E5C8E8;
                border-radius: 14px;
                padding: 7px 12px;
                font-size: 12px;
                font-weight: 600;
            }

            QWidget#pantallaContenedor {
                background-color: rgba(255, 255, 255, 220);
                border: 1px solid #E7CDEB;
                border-radius: 22px;
            }

            QLabel#etiquetaPantalla {
                color: #A077A5;
                font-size: 11px;
                font-weight: 700;
            }

            QLineEdit#pantalla {
                color: #54275D;
                background-color: transparent;
                border: none;
                padding: 8px 4px;
                selection-background-color: #D98FD7;
                selection-color: white;
            }

            QLabel#mensaje {
                color: #8A6B91;
                font-size: 12px;
                min-height: 18px;
            }

            QLabel#mensaje[error="true"] {
                color: #B62E6C;
                font-weight: 600;
            }

            QPushButton {
                min-height: 48px;
                color: #5B3164;
                background-color: #FFFFFF;
                border: 1px solid #DFC8E5;
                border-radius: 17px;
                font-size: 19px;
                font-weight: 700;
            }

            QPushButton:hover {
                background-color: #FFF7FC;
                border-color: #CB83C8;
            }

            QPushButton:pressed {
                background-color: #F0DDF4;
                border-color: #A94FA6;
            }

            QPushButton#operacion {
                color: #7C3698;
                background-color: #EAD7FA;
                border-color: #D2ADE8;
                font-size: 23px;
            }

            QPushButton#operacion:hover {
                background-color: #DFC0F4;
            }

            QPushButton#historial {
                color: #7C3698;
                background-color: #F0DEFA;
                border-color: #D2ADE8;
                font-size: 15px;
                min-height: 38px;
                padding: 0 16px;
            }

            QPushButton#historial:hover {
                background-color: #E4C7F6;
                border-color: #B87FD1;
            }

            QDialog#historialDialogo {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #FFF1F7,
                    stop: 0.55 #F3E8FF,
                    stop: 1 #E9DEFF
                );
            }

            QLabel#historialTitulo {
                color: #71356F;
                font-size: 22px;
                font-weight: 700;
            }

            QListWidget#listaHistorial {
                background-color: rgba(255, 255, 255, 220);
                border: 1px solid #E7CDEB;
                border-radius: 18px;
                color: #54275D;
                font-size: 16px;
                padding: 6px;
            }

            QListWidget#listaHistorial::item {
                padding: 7px;
                border-radius: 10px;
            }

            QListWidget#listaHistorial::item:selected {
                background-color: #E7C4F2;
                color: #4D3158;
            }

            QPushButton#borrarHistorial {
                color: #A52E67;
                background-color: #FFD9E7;
                border-color: #F2AEC8;
                font-size: 15px;
            }

            QPushButton#borrarHistorial:hover {
                background-color: #FFC6DB;
            }

            QPushButton#limpiar {
                color: #A52E67;
                background-color: #FFD9E7;
                border-color: #F2AEC8;
            }

            QPushButton#limpiar:hover {
                background-color: #FFC6DB;
            }

            QPushButton#igual {
                color: white;
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #E674BE,
                    stop: 1 #A149C6
                );
                border: none;
                font-size: 25px;
            }

            QPushButton#igual:hover {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #D95CAA,
                    stop: 1 #8734B1
                );
            }
        """ + REGLAS_FUENTE

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


class HistorialDialog(QDialog):
    """Ventana con las operaciones realizadas; al elegir una se recupera su resultado."""

    resultado_elegido = pyqtSignal(str)

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setObjectName("historialDialogo")
        self.setWindowTitle("Historial de operaciones")
        self.setStyleSheet(ESTILO)
        self.setMinimumSize(420, 460)

        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(28, 24, 28, 24)
        raiz.setSpacing(16)

        titulo = QLabel("Historial")
        titulo.setObjectName("historialTitulo")

        self.lista = QListWidget()
        self.lista.setObjectName("listaHistorial")
        self.lista.setAlternatingRowColors(False)
        self.lista.setToolTip("Haz clic en una operación para usar su resultado")
        self.lista.setWordWrap(True)
        self.lista.itemClicked.connect(self.elegir)

        botones = QHBoxLayout()
        botones.setSpacing(10)

        self.boton_borrar = QPushButton("Borrar historial")
        self.boton_borrar.setObjectName("borrarHistorial")
        self.boton_borrar.setCursor(Qt.PointingHandCursor)
        self.boton_borrar.setToolTip("Eliminar todas las operaciones guardadas")
        self.boton_borrar.clicked.connect(self.borrar)

        boton_cerrar = QPushButton("Cerrar")
        boton_cerrar.setCursor(Qt.PointingHandCursor)
        boton_cerrar.clicked.connect(self.close)

        botones.addWidget(self.boton_borrar)
        botones.addStretch()
        botones.addWidget(boton_cerrar)

        raiz.addWidget(titulo)
        raiz.addWidget(self.lista, 1)
        raiz.addLayout(botones)

    def mostrar_vacio(self) -> None:
        self.lista.clear()
        vacio = QListWidgetItem("Sin operaciones todavía")
        vacio.setFlags(Qt.NoItemFlags)
        self.lista.addItem(vacio)
        self.boton_borrar.setEnabled(False)

    def actualizar(self, historial: list[str]) -> None:
        if not historial:
            self.mostrar_vacio()
            return

        self.lista.clear()
        self.boton_borrar.setEnabled(True)
        for entrada in reversed(historial):
            item = QListWidgetItem(entrada)
            item.setData(Qt.UserRole, entrada.rsplit("=", 1)[-1].strip())
            self.lista.addItem(item)

    def elegir(self, item: QListWidgetItem) -> None:
        resultado = item.data(Qt.UserRole)
        if resultado:
            self.resultado_elegido.emit(str(resultado))

    def borrar(self) -> None:
        ventana = self.parent()
        if ventana is not None and hasattr(ventana, "historial"):
            ventana.historial.clear()
        self.mostrar_vacio()


class Calculadora(QMainWindow):
    def __init__(self):
        super().__init__()

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

        self.setWindowTitle("Calculadora Rosa y Lila")
        self.setMinimumSize(470, 620)
        self.resize(490, 650)

        self.aplicar_estilo()
        self.crear_interfaz()

    def aplicar_estilo(self):
        self.setStyleSheet(ESTILO)

    def crear_interfaz(self):
        fondo = QWidget()
        fondo.setObjectName("fondo")
        self.setCentralWidget(fondo)

        raiz = QVBoxLayout(fondo)
        raiz.setContentsMargins(30, 26, 30, 30)
        raiz.setSpacing(18)

        cabecera = QHBoxLayout()
        textos = QVBoxLayout()
        textos.setSpacing(1)

        titulo = QLabel("Calculadora")
        titulo.setObjectName("titulo")

        subtitulo = QLabel("Suma, resta, multiplica y divide")
        subtitulo.setObjectName("subtitulo")

        insignia = QLabel("0–9  +  -  ×  ÷")
        insignia.setObjectName("insignia")

        self.boton_historial = QPushButton("Historial")
        self.boton_historial.setObjectName("historial")
        self.boton_historial.setCursor(Qt.PointingHandCursor)
        self.boton_historial.setToolTip("Ver las operaciones realizadas")
        self.boton_historial.setAccessibleName("Abrir historial")
        self.boton_historial.clicked.connect(self.abrir_historial)

        textos.addWidget(titulo)
        textos.addWidget(subtitulo)

        cabecera.addLayout(textos)
        cabecera.addStretch()
        cabecera.addWidget(insignia, 0, Qt.AlignVCenter)
        cabecera.addSpacing(10)
        cabecera.addWidget(
            self.boton_historial,
            0,
            Qt.AlignVCenter
        )

        raiz.addLayout(cabecera)

        contenedor_pantalla = QWidget()
        contenedor_pantalla.setObjectName("pantallaContenedor")
        raiz.addWidget(contenedor_pantalla)

        interior = QVBoxLayout(contenedor_pantalla)
        interior.setContentsMargins(22, 14, 22, 14)
        interior.setSpacing(4)

        etiqueta_pantalla = QLabel("PANTALLA")
        etiqueta_pantalla.setObjectName("etiquetaPantalla")

        self.pantalla = QLineEdit("0")
        self.pantalla.setObjectName("pantalla")
        self.pantalla.setReadOnly(True)
        self.pantalla.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.pantalla.setFocusPolicy(Qt.NoFocus)
        self.pantalla.setCursorPosition(0)
        self.pantalla.setToolTip("Resultado y operandos en curso (puedes copiarlo)")
        self.pantalla.setAccessibleName("Pantalla de resultados")
        self.pantalla.setProperty("tam", str(TAMANOS_PANTALLA[0]))
        self.pantalla.textChanged.connect(self.ajustar_fuente_pantalla)

        self.mensaje = QLabel("")
        self.mensaje.setObjectName("mensaje")
        self.mensaje.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.mensaje.setWordWrap(True)
        self.mensaje.setFocusPolicy(Qt.NoFocus)

        interior.addWidget(etiqueta_pantalla)
        interior.addWidget(self.pantalla)
        interior.addWidget(self.mensaje)

        raiz.addLayout(self.crear_teclado())
        raiz.addStretch(1)

        ayuda = QLabel("Teclado: 0–9  ·  + − * /  ·  Enter =  ·  Esc = C  ·  Retroceso borra")
        ayuda.setObjectName("subtitulo")
        ayuda.setAlignment(Qt.AlignHCenter)
        ayuda.setWordWrap(True)
        raiz.addWidget(ayuda)

    def crear_teclado(self):
        teclado = QGridLayout()
        teclado.setSpacing(12)

        for fila, columna, texto, estilo, span in TECLADO:
            boton = QPushButton(texto)
            if estilo:
                boton.setObjectName(estilo)
            boton.setCursor(Qt.PointingHandCursor)
            boton.setFocusPolicy(Qt.NoFocus)
            boton.setToolTip(self.descripcion(texto))
            boton.setAccessibleName(texto)
            boton.clicked.connect(lambda _checked=False, t=texto: self.pulsar(t))
            teclado.addWidget(boton, fila, columna, 1, span)
            self.botones[texto] = boton

        for columna in range(4):
            teclado.setColumnStretch(columna, 1)
        for fila in range(5):
            teclado.setRowStretch(fila, 1)

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

        actual = self.pantalla.text() or "0"

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

        self.operando = self.a_numero(self.pantalla.text())
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
        b = self.a_numero(self.pantalla.text())
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
        valor = self.pantalla.text() or "0"
        if valor in ("0", "0.", "-", "-0", "-0."):
            self.escribir("0")
            return
        self.prefijo = ""
        self.pendiente_porcentaje = False
        self.escribir(valor[1:] if valor.startswith("-") else "-" + valor)

    def porcentaje(self):
        valor = self.a_numero(self.pantalla.text())
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
        valor = self.a_numero(self.pantalla.text())
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
        self.pantalla.setText(texto)
        self.pantalla.setCursorPosition(len(texto))
        self.ajustar_fuente_pantalla()

    def ajustar_fuente_pantalla(self):
        """Reduce la letra de la pantalla para que el número completo quepa siempre."""
        ancho = self.pantalla.contentsRect().width()
        if ancho < 60:
            return

        texto = self.pantalla.text() or ""
        elegido = TAMANOS_PANTALLA[-1]
        for tam in TAMANOS_PANTALLA:
            fuente = QFont(self.pantalla.font())
            fuente.setPixelSize(tam)
            if QFontMetrics(fuente).horizontalAdvance(texto) <= ancho - 4:
                elegido = tam
                break

        if str(self.pantalla.property("tam") or "") != str(elegido):
            self.pantalla.setProperty("tam", str(elegido))
            self.pantalla.style().unpolish(self.pantalla)
            self.pantalla.style().polish(self.pantalla)

    def resizeEvent(self, evento):
        super().resizeEvent(evento)
        self.ajustar_fuente_pantalla()

    def mostrar_mensaje(self, texto, error=False):
        self.error = bool(error)
        self.mensaje.setText(texto)
        self.mensaje.setProperty("error", "true" if error else "false")
        self.mensaje.style().unpolish(self.mensaje)
        self.mensaje.style().polish(self.mensaje)

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
        if self.ventana_historial is not None and self.ventana_historial.isVisible():
            self.ventana_historial.actualizar(self.historial)

    def abrir_historial(self):
        if self.ventana_historial is None:
            self.ventana_historial = HistorialDialog(self)
            self.ventana_historial.resultado_elegido.connect(self.usar_resultado)
        self.ventana_historial.actualizar(self.historial)
        self.ventana_historial.show()
        self.ventana_historial.raise_()
        self.ventana_historial.activateWindow()

    # ---------- teclado físico ----------
    def keyPressEvent(self, evento):
        tecla = evento.text()
        codigo = evento.key()

        if codigo in (Qt.Key_Return, Qt.Key_Enter):
            self.pulsar("=")
        elif codigo == Qt.Key_Escape:
            self.pulsar("C")
        elif codigo in (Qt.Key_Backspace, Qt.Key_Delete):
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
            super().keyPressEvent(evento)

    def borrar_ultimo(self):
        if self.error:
            self.pulsar("C")
            return

        texto = self.pantalla.text() or "0"
        if texto in ("0", "0.", "-", "-0"):
            self.pulsar("C")
            return

        self.reiniciar_pantalla = False
        self.prefijo = ""
        self.pendiente_porcentaje = False
        self.escribir(texto[:-1] or "0")


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Calculadora Rosa y Lila")
    ventana = Calculadora()
    ventana.show()
    return app.exec_()


if __name__ == "__main__":
    raise SystemExit(main())