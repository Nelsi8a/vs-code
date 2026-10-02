"""Calculadora Rosa y Lila: GUI PySide6 con menús, historial, teclado y control de división entre cero."""

from __future__ import annotations

import re
import sys

import PySide6
from PySide6.QtCore import Qt, Signal, qVersion
from PySide6.QtGui import QAction, QActionGroup, QFont, QFontMetrics, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

VERSION = "1.0"
VERSION_MOTOR = PySide6.__version__
VERSION_QT = qVersion()
AUTOR = "Nelsi Rocio Ochoa Mamani"

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

            QMenuBar {
                background-color: #F3E8FF;
                color: #4D3158;
                font-size: 14px;
            }

            QMenuBar::item {
                background: transparent;
                border-radius: 9px;
                padding: 6px 13px;
            }

            QMenuBar::item:selected {
                background-color: #E7C4F2;
            }

            QMenuBar::item:pressed {
                background-color: #D8AEE8;
            }

            QMenu {
                background-color: #FFFFFF;
                border: 1px solid #DFC8E5;
                padding: 6px;
            }

            QMenu::item {
                padding: 7px 30px 7px 24px;
                border-radius: 9px;
            }

            QMenu::item:selected {
                background-color: #F1D9F4;
                color: #4D3158;
            }

            QMenu::item:disabled {
                color: #B9A7BE;
            }

            QMenu::separator {
                height: 1px;
                background-color: #EBDDF0;
                margin: 5px 10px;
            }

            QStatusBar {
                background-color: #F3E8FF;
                color: #6B4B70;
                font-size: 12px;
            }

            QStatusBar::item {
                border: none;
            }

            QLabel#contador {
                color: #9B3F91;
                font-size: 12px;
                font-weight: 600;
            }

            QToolTip {
                background-color: #FFFFFF;
                color: #4D3158;
                border: 1px solid #DFC8E5;
                border-radius: 8px;
                padding: 5px;
            }

            QDialog#dialogoHistorial,
            QDialog#dialogoAyuda,
            QDialog#dialogoAcerca {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #FFF1F7,
                    stop: 0.55 #F3E8FF,
                    stop: 1 #E9DEFF
                );
            }

            QLabel#tituloDialogo {
                color: #71356F;
                font-size: 22px;
                font-weight: 700;
            }

            QLabel#columna {
                color: #8A6B91;
                font-size: 11px;
                font-weight: 700;
            }

            QLabel#atajo {
                color: #54275D;
                font-size: 15px;
                font-family: "Consolas", monospace;
            }

            QLabel#ficha {
                color: #674A70;
                font-size: 15px;
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

# Atajos que se listan en el diálogo de ayuda.
ATAJOS = [
    ("Cifras 0-9", "0 1 2 3 4 5 6 7 8 9"),
    ("Suma, resta, producto y división", "+  −  *  /"),
    ("Coma decimal", ",  o  ."),
    ("Calcular", "Enter"),
    ("Borrar todo", "Esc  o  botón C"),
    ("Borrar el último carácter", "Retroceso  o  Suprimir"),
    ("Elevar al cuadrado", "x  o  X"),
    ("Porcentaje", "%"),
    ("Copiar el resultado", "Ctrl + C"),
    ("Copiar todo el historial", "Ctrl + Mayús + C"),
    ("Seleccionar el resultado", "Ctrl + A"),
    ("Abrir el historial", "F9  o  Ctrl + H"),
    ("Nueva operación", "Ctrl + N"),
    ("Ayuda de atajos", "F1"),
]


def limpiar_texto(texto):
    return (texto or "0").strip().replace(",", ".").replace("−", "-")


class HistorialDialog(QDialog):
    """Ventana con las operaciones realizadas; al elegir una se recupera su resultado."""

    resultado_elegido = Signal(str)

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setObjectName("dialogoHistorial")
        self.setWindowTitle("Historial de operaciones")
        self.setStyleSheet(ESTILO)
        self.setMinimumSize(420, 460)

        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(28, 24, 28, 24)
        raiz.setSpacing(16)

        titulo = QLabel("Historial")
        titulo.setObjectName("tituloDialogo")

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
        self.boton_borrar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.boton_borrar.setToolTip("Eliminar todas las operaciones guardadas")
        self.boton_borrar.clicked.connect(self.borrar)

        boton_cerrar = QPushButton("Cerrar")
        boton_cerrar.setCursor(Qt.CursorShape.PointingHandCursor)
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
        vacio.setFlags(Qt.ItemFlag.NoItemFlags)
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
            item.setData(Qt.ItemDataRole.UserRole, entrada.rsplit("=", 1)[-1].strip())
            self.lista.addItem(item)

    def elegir(self, item: QListWidgetItem) -> None:
        resultado = item.data(Qt.ItemDataRole.UserRole)
        if resultado:
            self.resultado_elegido.emit(str(resultado))

    def borrar(self) -> None:
        ventana = self.parent()
        if ventana is not None and hasattr(ventana, "historial"):
            ventana.historial.clear()
            ventana.actualizar_contador()
        self.mostrar_vacio()


class DialogoAyuda(QDialog):
    """Listado de los atajos de teclado y del ratón."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("dialogoAyuda")
        self.setWindowTitle("Atajos de teclado")
        self.setStyleSheet(ESTILO)
        self.setMinimumSize(560, 520)

        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(28, 24, 28, 24)
        raiz.setSpacing(16)

        titulo = QLabel("Atajos")
        titulo.setObjectName("tituloDialogo")

        texto = QLabel("Estos atajos funcionan con la ventana de la calculadora enfocada.")
        texto.setObjectName("subtitulo")
        texto.setWordWrap(True)

        tabla = QGridLayout()
        tabla.setHorizontalSpacing(20)
        tabla.setVerticalSpacing(9)

        encabezado_accion = QLabel("ACCIÓN")
        encabezado_accion.setObjectName("columna")
        encabezado_atajo = QLabel("ATAJO")
        encabezado_atajo.setObjectName("columna")
        tabla.addWidget(encabezado_accion, 0, 0)
        tabla.addWidget(encabezado_atajo, 0, 1)

        for fila, (accion, atajo) in enumerate(ATAJOS, start=1):
            etiqueta = QLabel(accion)
            etiqueta.setObjectName("ficha")
            etiqueta.setWordWrap(True)
            etiqueta.setAlignment(
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
            )
            tecla = QLabel(atajo)
            tecla.setObjectName("atajo")
            tecla.setWordWrap(True)
            tecla.setAlignment(
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
            )
            tabla.addWidget(etiqueta, fila, 0)
            tabla.addWidget(tecla, fila, 1)

        tabla.setColumnStretch(0, 3)
        tabla.setColumnStretch(1, 2)

        botones = QHBoxLayout()
        cerrar = QPushButton("Cerrar")
        cerrar.setCursor(Qt.CursorShape.PointingHandCursor)
        cerrar.clicked.connect(self.close)
        botones.addStretch()
        botones.addWidget(cerrar)

        raiz.addWidget(titulo)
        raiz.addWidget(texto)
        raiz.addLayout(tabla, 1)
        raiz.addLayout(botones)


class DialogoAcerca(QDialog):
    """Ficha de la aplicación."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("dialogoAcerca")
        self.setWindowTitle("Acerca de la calculadora")
        self.setStyleSheet(ESTILO)
        self.setMinimumSize(480, 340)

        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(30, 26, 30, 26)
        raiz.setSpacing(14)

        marca = QLabel("GLOW BELLEZA")
        marca.setObjectName("insignia")
        marca.setAlignment(Qt.AlignmentFlag.AlignCenter)

        titulo = QLabel("Calculadora Rosa y Lila")
        titulo.setObjectName("titulo")
        titulo.setWordWrap(True)
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        descripcion = QLabel(
            "Calculadora de escritorio con historial, teclado completo y control "
            "de división entre cero.\n\n"
            f"Versión {VERSION} · PySide6 {VERSION_MOTOR} · Qt {VERSION_QT}"
        )
        descripcion.setObjectName("ficha")
        descripcion.setWordWrap(True)
        descripcion.setAlignment(Qt.AlignmentFlag.AlignCenter)

        autor = QLabel(f"Autor: {AUTOR}")
        autor.setObjectName("ficha")
        autor.setWordWrap(True)
        autor.setAlignment(Qt.AlignmentFlag.AlignCenter)

        nota = QLabel("Hecha con PySide6 (Qt para Python).")
        nota.setObjectName("subtitulo")
        nota.setWordWrap(True)
        nota.setAlignment(Qt.AlignmentFlag.AlignCenter)

        botones = QHBoxLayout()
        cerrar = QPushButton("Cerrar")
        cerrar.setObjectName("igual")
        cerrar.setCursor(Qt.CursorShape.PointingHandCursor)
        cerrar.clicked.connect(self.accept)
        botones.addStretch()
        botones.addWidget(cerrar)
        botones.addStretch()

        raiz.addWidget(marca)
        raiz.addWidget(titulo)
        raiz.addWidget(descripcion)
        raiz.addWidget(autor)
        raiz.addWidget(nota)
        raiz.addStretch()
        raiz.addLayout(botones)


class Calculadora(QMainWindow):
    def __init__(self):
        super().__init__()

        self.botones = {}
        self.historial = []
        self.ventana_historial = None
        self.ventana_ayuda = None
        self.ventana_acerca = None
        self.reiniciar_pantalla = False

        self.operando = None
        self.operador = None
        self.prefijo = ""
        self.pendiente_porcentaje = False
        self.porcentaje_valor = 0.0
        self.error = False

        self.setWindowTitle("Calculadora Rosa y Lila")
        self.setMinimumSize(470, 620)
        self.resize(490, 680)

        self.aplicar_estilo()
        self.crear_menus()
        self.crear_interfaz()
        self.crear_barra_estado()
        self.activar_menu_contextual()

    def aplicar_estilo(self):
        self.setStyleSheet(ESTILO)

    # -------------------------------------------------------------------- menús
    def crear_menus(self):
        barra = self.menuBar()
        barra.setNativeMenuBar(False)

        # --- Calculadora
        calculadora = barra.addMenu("&Calculadora")

        nuevo = QAction("&Nueva operación", self)
        nuevo.setShortcut(QKeySequence.StandardKey.New)
        nuevo.setToolTip("Borra la pantalla y empieza de cero")
        nuevo.triggered.connect(self.limpiar)
        calculadora.addAction(nuevo)

        cuadrada = QAction("Elevar al &cuadrado", self)
        cuadrada.setShortcut(QKeySequence("Ctrl+D"))
        cuadrada.setToolTip("Eleva al cuadrado el número de la pantalla")
        cuadrada.triggered.connect(lambda: self.pulsar("x²"))
        calculadora.addAction(cuadrada)

        porcentaje = QAction("&Porcentaje", self)
        porcentaje.setShortcut(QKeySequence("Ctrl+P"))
        porcentaje.setToolTip("Porcentaje del operando actual")
        porcentaje.triggered.connect(lambda: self.pulsar("%"))
        calculadora.addAction(porcentaje)

        signo = QAction("Cambiar el &signo", self)
        signo.setShortcut(QKeySequence("Ctrl+Shift+M"))
        signo.triggered.connect(lambda: self.pulsar("±"))
        calculadora.addAction(signo)

        calcular = QAction("&Calcular", self)
        calcular.setShortcut(QKeySequence("Ctrl+="))
        calcular.setToolTip("Equivale a pulsar =")
        calcular.triggered.connect(lambda: self.pulsar("="))
        calculadora.addAction(calcular)

        self.accion_borrar = QAction("&Borrar historial", self)
        self.accion_borrar.setShortcut(QKeySequence("Ctrl+Shift+L"))
        self.accion_borrar.triggered.connect(self.borrar_historial)
        calculadora.addAction(self.accion_borrar)

        calculadora.addSeparator()

        salir = QAction("&Salir", self)
        salir.setShortcut(QKeySequence("Ctrl+Q"))
        salir.triggered.connect(self.close)
        calculadora.addAction(salir)

        # --- Editar
        editar = barra.addMenu("&Editar")

        copiar = QAction("&Copiar resultado", self)
        copiar.setShortcut(QKeySequence.StandardKey.Copy)
        copiar.triggered.connect(self.copiar_resultado)
        editar.addAction(copiar)

        copiar_historial = QAction("Copiar &historial", self)
        copiar_historial.setShortcut(QKeySequence("Ctrl+Shift+C"))
        copiar_historial.triggered.connect(self.copiar_historial)
        editar.addAction(copiar_historial)

        editar.addSeparator()

        seleccionar = QAction("&Seleccionar todo", self)
        seleccionar.setShortcut(QKeySequence.StandardKey.SelectAll)
        seleccionar.triggered.connect(lambda: self.pantalla.selectAll())
        editar.addAction(seleccionar)

        # --- Ver
        ver = barra.addMenu("&Ver")

        historial = QAction("&Historial de operaciones", self)
        historial.setShortcut(QKeySequence("F9"))
        historial.setCheckable(True)
        historial.toggled.connect(self.al_toggle_historial)
        ver.addAction(historial)
        self.accion_historial = historial

        historial_alt = QAction(self)
        historial_alt.setShortcut(QKeySequence("Ctrl+H"))
        historial_alt.triggered.connect(self.abrir_historial)
        self.addAction(historial_alt)

        ver.addSeparator()

        grupo = QActionGroup(self)
        grupo.setExclusive(True)
        encender = QAction("Pantalla &encendida", self)
        apagar = QAction("Pantalla a&pagada", self)
        for accion in (encender, apagar):
            accion.setCheckable(True)
            grupo.addAction(accion)
            ver.addAction(accion)
        encender.toggled.connect(lambda estado: self.al_toggle_encendido(estado))
        apagar.toggled.connect(lambda estado: self.al_toggle_encendido(not estado))
        encender.setChecked(True)

        ver.addSeparator()

        # --- Ayuda
        ayuda = barra.addMenu("A&yuda")

        ayuda_atajos = QAction("&Atajos de teclado", self)
        ayuda_atajos.setShortcut(QKeySequence.StandardKey.HelpContents)
        ayuda_atajos.triggered.connect(self.abrir_ayuda)
        ayuda.addAction(ayuda_atajos)

        ayuda.addSeparator()

        informacion = QAction(AUTOR, self)
        informacion.setToolTip("Información del autor de la aplicación")
        informacion.triggered.connect(self.abrir_acerca)
        ayuda.addAction(informacion)

        ayuda.addSeparator()

        acerca = QAction("&Acerca de la calculadora", self)
        acerca.setShortcut(QKeySequence("F12"))
        acerca.triggered.connect(self.abrir_acerca)
        ayuda.addAction(acerca)

    def activar_menu_contextual(self):
        for objetivo in (self.centralWidget(), self.pantalla):
            objetivo.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            objetivo.customContextMenuRequested.connect(self.mostrar_menu_contextual)

    def mostrar_menu_contextual(self, posicion):
        menu = QMenu(self)
        menu.addAction("Copiar resultado", self.copiar_resultado)
        menu.addAction("Copiar historial", self.copiar_historial)
        menu.addSeparator()
        menu.addAction("Historial de operaciones", self.abrir_historial)
        menu.addAction("Borrar historial", self.borrar_historial)
        menu.addSeparator()
        menu.addAction("Atajos de teclado", self.abrir_ayuda)
        menu.addSeparator()
        menu.addAction(AUTOR, self.abrir_acerca)
        menu.exec(self.mapToGlobal(posicion))

    def crear_barra_estado(self):
        self.etiqueta_autor = QLabel(AUTOR)
        self.etiqueta_autor.setObjectName("contador")
        self.etiqueta_autor.setToolTip("Autora de la aplicación")
        self.statusBar().addPermanentWidget(self.etiqueta_autor)

        self.etiqueta_contador = QLabel("0 operaciones")
        self.etiqueta_contador.setObjectName("contador")
        self.statusBar().addPermanentWidget(self.etiqueta_contador)
        self.statusBar().showMessage("Listo · F1 muestra los atajos")
        self.actualizar_contador()

    def actualizar_contador(self):
        total = len(self.historial)
        self.etiqueta_contador.setText(
            "%d operacion%s" % (total, "" if total == 1 else "es")
        )
        self.accion_borrar.setEnabled(total > 0)

    # -------------------------------------------------------------------- vistas
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
        self.boton_historial.setCursor(Qt.CursorShape.PointingHandCursor)
        self.boton_historial.setToolTip("Ver las operaciones realizadas (F9)")
        self.boton_historial.setAccessibleName("Abrir historial")
        self.boton_historial.clicked.connect(self.abrir_historial)

        textos.addWidget(titulo)
        textos.addWidget(subtitulo)

        cabecera.addLayout(textos)
        cabecera.addStretch()
        cabecera.addWidget(insignia, 0, Qt.AlignmentFlag.AlignVCenter)
        cabecera.addSpacing(10)
        cabecera.addWidget(self.boton_historial, 0, Qt.AlignmentFlag.AlignVCenter)

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
        self.pantalla.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        self.pantalla.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.pantalla.setCursorPosition(0)
        self.pantalla.setToolTip("Resultado y operandos en curso (puedes copiarlo)")
        self.pantalla.setAccessibleName("Pantalla de resultados")
        self.pantalla.setProperty("tam", str(TAMANOS_PANTALLA[0]))
        self.pantalla.textChanged.connect(self.ajustar_fuente_pantalla)

        self.mensaje = QLabel("")
        self.mensaje.setObjectName("mensaje")
        self.mensaje.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        self.mensaje.setWordWrap(True)
        self.mensaje.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        interior.addWidget(etiqueta_pantalla)
        interior.addWidget(self.pantalla)
        interior.addWidget(self.mensaje)

        raiz.addLayout(self.crear_teclado())
        raiz.addStretch(1)

        ayuda = QLabel("Teclado: 0–9  ·  + − * /  ·  Enter =  ·  Esc = C  ·  Retroceso borra")
        ayuda.setObjectName("subtitulo")
        ayuda.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        ayuda.setWordWrap(True)
        raiz.addWidget(ayuda)

    def crear_teclado(self):
        teclado = QGridLayout()
        teclado.setSpacing(12)

        for _fila, _columna, texto, estilo, span in TECLADO:
            boton = QPushButton(texto)
            if estilo:
                boton.setObjectName(estilo)
            boton.setCursor(Qt.CursorShape.PointingHandCursor)
            boton.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            boton.setToolTip(self.descripcion(texto))
            boton.setAccessibleName(texto)
            boton.clicked.connect(lambda _checked=False, t=texto: self.pulsar(t))
            teclado.addWidget(boton, _fila, _columna, 1, span)
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

    # -------------------------------------------------------------------- claves
    def copiar_resultado(self):
        texto = self.pantalla.text()
        QApplication.clipboard().setText(texto)
        self.statusBar().showMessage("Resultado copiado: %s" % texto, 4000)

    def copiar_historial(self):
        if not self.historial:
            self.statusBar().showMessage("No hay operaciones para copiar", 4000)
            return
        QApplication.clipboard().setText("\n".join(self.historial))
        self.statusBar().showMessage("Historial copiado (%d operaciones)" % len(self.historial), 4000)

    def borrar_historial(self):
        self.historial.clear()
        self.actualizar_contador()
        if self.ventana_historial is not None:
            self.ventana_historial.actualizar(self.historial)
        self.statusBar().showMessage("Historial vaciado", 4000)

    def al_toggle_historial(self, activo):
        if activo:
            self.abrir_historial()
        elif self.ventana_historial is not None:
            self.ventana_historial.close()

    def al_toggle_encendido(self, encendido):
        if not hasattr(self, "pantalla"):
            return
        if encendido:
            self.pantalla.setStyleSheet("")
        else:
            self.pantalla.setStyleSheet("color: #B9A7BE;")
        self.pantalla.style().unpolish(self.pantalla)
        self.pantalla.style().polish(self.pantalla)
        self.pantalla.update()
        self.ajustar_fuente_pantalla()
        self.statusBar().showMessage(
            "Pantalla encendida" if encendido else "Pantalla apagada", 3000
        )

    def abrir_ayuda(self):
        if self.ventana_ayuda is None:
            self.ventana_ayuda = DialogoAyuda(self)
        self.ventana_ayuda.show()
        self.ventana_ayuda.raise_()
        self.ventana_ayuda.activateWindow()

    def abrir_acerca(self):
        if self.ventana_acerca is None:
            self.ventana_acerca = DialogoAcerca(self)
        self.ventana_acerca.show()
        self.ventana_acerca.raise_()
        self.ventana_acerca.activateWindow()

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

    # --------------------------------------------------------- pantalla y estado
    def escribir(self, texto):
        self.error = False
        self.pantalla.setText(texto)
        self.pantalla.setCursorPosition(len(texto))
        self.ajustar_fuente_pantalla()

    def ajustar_fuente_pantalla(self):
        """Reduce la letra de la pantalla para que el numero completo quepa siempre."""
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
        if texto:
            self.statusBar().showMessage(texto, 6000)

    # --------------------------------------------------------------- operaciones
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

    # ------------------------------------------------------------------ historial
    def registrar(self, entrada):
        self.historial.append(entrada)
        self.actualizar_contador()
        if self.ventana_historial is not None and self.ventana_historial.isVisible():
            self.ventana_historial.actualizar(self.historial)

    def abrir_historial(self):
        if self.ventana_historial is None:
            self.ventana_historial = HistorialDialog(self)
            self.ventana_historial.resultado_elegido.connect(self.usar_resultado)
            self.ventana_historial.finished.connect(self.al_cerrar_historial)
        self.ventana_historial.actualizar(self.historial)
        self.ventana_historial.show()
        self.ventana_historial.raise_()
        self.ventana_historial.activateWindow()

    def al_cerrar_historial(self, _resultado=0):
        if self.accion_historial.isChecked():
            self.accion_historial.setChecked(False)

    # ------------------------------------------------------------------- teclado
    def keyPressEvent(self, evento):
        tecla = evento.text()
        codigo = evento.key()

        if codigo in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.pulsar("=")
        elif codigo == Qt.Key.Key_Escape:
            self.pulsar("C")
        elif codigo in (Qt.Key.Key_Backspace, Qt.Key.Key_Delete):
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
    app.setApplicationVersion(VERSION)
    ventana = Calculadora()
    ventana.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
