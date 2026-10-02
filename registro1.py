import math
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QWidget, QMainWindow, QDialog,
    QLabel, QPushButton, QLineEdit, QTextEdit,
    QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout,
    QCheckBox, QRadioButton, QComboBox
)

ESTILO = """
QWidget {
    font-family: "Segoe UI", sans-serif;
    font-size: 14px;
    color: #43284D;
}

QMainWindow {
    background-color: #FFF8FC;
}

QWidget#pagina {
    background: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 1,
        stop: 0 #FFF5FA,
        stop: 0.55 #F7ECFF,
        stop: 1 #FFFFFF
    );
}

QWidget#panel {
    background-color: #FFFFFF;
    border: 1px solid #EACCEB;
    border-radius: 24px;
}

QLabel#marca {
    color: #A0449D;
    font-size: 15px;
    font-weight: 700;
}

QLabel#titulo {
    color: #6B287F;
    font-size: 34px;
    font-weight: 700;
}

QLabel#subtitulo {
    color: #755E7D;
    font-size: 15px;
}

QLabel#seccion {
    color: #6B287F;
    font-size: 18px;
    font-weight: 700;
}

QLabel#ayuda {
    color: #8B728F;
    font-size: 12px;
}

QLabel#contador {
    color: #A0449D;
    font-weight: 700;
}

QLabel#estado {
    color: #387B5A;
    font-weight: 600;
    padding: 8px 12px;
    background-color: #EAF8F0;
    border-radius: 10px;
}

QLabel#estadoError {
    color: #B42318;
    font-weight: 600;
    padding: 8px 12px;
    background-color: #FFF0F0;
    border-radius: 10px;
}

QLabel#distintivo {
    color: #8A368D;
    background-color: #F5E4FA;
    border: 1px solid #E6C7EB;
    border-radius: 9px;
    padding: 4px 9px;
    font-size: 10px;
    font-weight: 700;
}

QTextEdit#listado {
    background-color: #FFFFFF;
    border: 1px solid #EACCEB;
    border-radius: 18px;
    padding: 14px;
    color: #4B2F55;
    font-family: "Consolas", monospace;
    font-size: 13px;
}

QTextEdit#descripcion {
    background-color: #FDF7FE;
    border: 1px solid #F0D8F3;
    border-radius: 16px;
}

QLineEdit, QTextEdit, QComboBox {
    background-color: #FFFFFF;
    border: 1px solid #DFC6E2;
    border-radius: 12px;
    padding: 9px 12px;
    selection-background-color: #D98BD7;
    selection-color: #FFFFFF;
}

QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
    border: 2px solid #C465C1;
    padding: 8px 11px;
}

QComboBox {
    min-height: 22px;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox QAbstractItemView {
    background-color: #FFFFFF;
    border: 1px solid #DFC6E2;
    selection-background-color: #F1D9F4;
    selection-color: #54215F;
    padding: 6px;
}

QCheckBox, QRadioButton {
    spacing: 8px;
    color: #5C3D64;
}

QCheckBox::indicator, QRadioButton::indicator {
    width: 18px;
    height: 18px;
}

QCheckBox::indicator {
    border: 2px solid #C89ECD;
    border-radius: 5px;
    background-color: #FFFFFF;
}

QCheckBox::indicator:checked {
    background-color: #B552B2;
    border-color: #B552B2;
}

QRadioButton::indicator {
    border: 2px solid #C89ECD;
    border-radius: 9px;
    background-color: #FFFFFF;
}

QRadioButton::indicator:checked {
    background-color: #B552B2;
    border: 5px solid #F1D3F1;
}

QPushButton {
    min-height: 22px;
    background-color: #FFFFFF;
    border: 1px solid #DDB8DF;
    border-radius: 14px;
    padding: 10px 18px;
    color: #6B287F;
    font-weight: 700;
}

QPushButton:hover {
    background-color: #FBF0FC;
    border-color: #C06AC0;
}

QPushButton#primario {
    background: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 0,
        stop: 0 #D96BCB,
        stop: 1 #A64BC1
    );
    color: #FFFFFF;
    border: none;
}

QPushButton#primario:hover {
    background: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 0,
        stop: 0 #C956BD,
        stop: 1 #8D36A8
    );
}

QPushButton#suave {
    background-color: #F5E4FA;
    color: #79328A;
}

QPushButton#peligro {
    background-color: #FFF0F3;
    color: #A73A57;
    border-color: #F0C5CF;
}

QDialog#dialogoRegistro QPushButton {
    min-height: 18px;
    padding: 7px 14px;
    border-radius: 11px;
    font-size: 13px;
}

QDialog#dialogoRegistro {
    background: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 1,
        stop: 0 #FFF8FC,
        stop: 1 #F6EAFF
    );
}
"""


class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(" Registro de productos")
        self.setWindowFlags(
            self.windowFlags()
            | Qt.WindowTitleHint
            | Qt.WindowSystemMenuHint
            | Qt.WindowMinimizeButtonHint
            | Qt.WindowMaximizeButtonHint
            | Qt.WindowCloseButtonHint
        )
        self.setMinimumSize(820, 620)
        self.resize(980, 720)
        self.productos = []
        self.registro_visible = False
        self.dialogo_registro = None
        self.setStyleSheet(ESTILO)
        self.mostrar_bienvenida()

    # ------------------------------------------------------------------ vistas
    def mostrar_bienvenida(self):
        self.registro_visible = False
        self.setWindowTitle(" Bienvenida")

        pagina = QWidget()
        pagina.setObjectName("pagina")
        raiz = QVBoxLayout(pagina)
        raiz.setContentsMargins(80, 48, 80, 48)
        raiz.setSpacing(18)

        marca = QLabel("GLOW BELLEZA")
        marca.setObjectName("marca")

        titulo = QLabel("¡Bienvenida a tu nueva rutina de belleza!")
        titulo.setObjectName("titulo")
        titulo.setWordWrap(True)

        subtitulo = QLabel(
            "Organiza tu inventario de productos de forma sencilla, elegante y rápida."
        )
        subtitulo.setObjectName("subtitulo")
        subtitulo.setWordWrap(True)

        panel = QWidget()
        panel.setObjectName("panel")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(38, 30, 38, 30)
        panel_layout.setSpacing(14)

        encabezado = QLabel("Todo lo que necesitas en un solo lugar")
        encabezado.setObjectName("seccion")

        descripcion = QTextEdit()
        descripcion.setObjectName("descripcion")
        descripcion.setReadOnly(True)
        descripcion.setFrameShape(QTextEdit.NoFrame)
        descripcion.setMinimumHeight(150)
        descripcion.setHtml(
            "<div style=\"color:#674A70; font-family:'Segoe UI'; font-size:15px; "
            "line-height:150%; text-align:center;\">"
            "<p><b>Registra</b> nombre, código, marca, categoría, precio y cantidad.</p>"
            "<p>Clasifica cada producto por tipo de piel, estado y etiquetas especiales.</p>"
            "<p>Consulta tus productos guardados desde una vista clara y organizada.</p>"
            "</div>"
        )

        botones = QHBoxLayout()
        ingresar = QPushButton("Ingresar al registro")
        ingresar.setObjectName("primario")
        ingresar.clicked.connect(self.mostrar_registro)
        salir = QPushButton("Salir")
        salir.setObjectName("peligro")
        salir.clicked.connect(self.close)
        botones.addWidget(ingresar)
        botones.addWidget(salir)

        panel_layout.addWidget(encabezado)
        panel_layout.addWidget(descripcion)
        panel_layout.addLayout(botones)

        raiz.addStretch()
        raiz.addWidget(marca)
        raiz.addWidget(titulo)
        raiz.addWidget(subtitulo)
        raiz.addSpacing(12)
        raiz.addWidget(panel)
        raiz.addStretch()

        self.setCentralWidget(pagina)

    def mostrar_registro(self):
        self.registro_visible = True
        self.setWindowTitle("Glow Belleza | Productos")

        pagina = QWidget()
        pagina.setObjectName("pagina")
        raiz = QVBoxLayout(pagina)
        raiz.setContentsMargins(52, 40, 52, 40)
        raiz.setSpacing(16)

        cabecera = QHBoxLayout()
        textos = QVBoxLayout()
        marca = QLabel("GLOW BELLEZA")
        marca.setObjectName("marca")
        titulo = QLabel("Registro de productos")
        titulo.setObjectName("titulo")
        subtitulo = QLabel("Consulta y organiza tu inventario de belleza.")
        subtitulo.setObjectName("subtitulo")
        textos.addWidget(marca)
        textos.addWidget(titulo)
        textos.addWidget(subtitulo)

        registrar = QPushButton("Registrar producto")
        registrar.setObjectName("primario")
        registrar.clicked.connect(self.abrir_registro)

        cabecera.addLayout(textos)
        cabecera.addStretch()
        cabecera.addWidget(registrar)
        raiz.addLayout(cabecera)

        self.mensaje_registro = QLabel()
        self.mensaje_registro.setObjectName("estado")
        self.mensaje_registro.setWordWrap(True)
        raiz.addWidget(self.mensaje_registro)

        seccion = QLabel("Productos registrados")
        seccion.setObjectName("seccion")
        raiz.addWidget(seccion)

        self.listado_productos = QTextEdit()
        self.listado_productos.setObjectName("listado")
        self.listado_productos.setReadOnly(True)
        raiz.addWidget(self.listado_productos, 1)

        pie = QHBoxLayout()
        self.contador_productos = QLabel()
        self.contador_productos.setObjectName("contador")
        volver = QPushButton("Volver al inicio")
        volver.setObjectName("suave")
        volver.clicked.connect(self.mostrar_bienvenida)
        salir = QPushButton("Salir")
        salir.setObjectName("peligro")
        salir.clicked.connect(self.close)
        pie.addWidget(self.contador_productos)
        pie.addStretch()
        pie.addWidget(volver)
        pie.addWidget(salir)
        raiz.addLayout(pie)

        self.setCentralWidget(pagina)
        self.actualizar_listado("Ingresa un nuevo producto para comenzar tu registro.")

    # ---------------------------------------------------------------- acciones
    def abrir_registro(self):
        if self.dialogo_registro is not None:
            self.dialogo_registro.close()

        dialogo = DialogoRegistro(self)
        self.dialogo_registro = dialogo
        dialogo.finished.connect(self._al_terminar_registro)
        dialogo.show()
        dialogo.raise_()
        dialogo.activateWindow()

    def _al_terminar_registro(self, resultado):
        dialogo = self.dialogo_registro
        self.dialogo_registro = None
        if dialogo is None:
            return
        if resultado == QDialog.Accepted and dialogo.producto_registrado is not None:
            self.productos.append(dialogo.producto_registrado)
            self.actualizar_listado(
                "Producto «%s» guardado correctamente." % dialogo.producto_registrado["nombre"]
            )

    def actualizar_listado(self, mensaje):
        total = len(self.productos)
        total_texto = "producto" if total == 1 else "productos"
        self.contador_productos.setText(
            "%d %s guardado%s" % (total, total_texto, "" if total == 1 else "s")
        )
        self.mensaje_registro.setText(mensaje)

        if not self.productos:
            self.listado_productos.setPlainText(
                "Todavía no hay productos registrados.\n\n"
                "Pulsa «Registrar producto» para crear el primero."
            )
            return

        bloques = []
        for indice, producto in enumerate(self.productos, start=1):
            etiquetas = ", ".join(producto["etiquetas"]) if producto["etiquetas"] else "Sin etiquetas"
            comentarios = producto["comentarios"].replace("\n", " | ") or "Sin comentarios"
            bloques.append(
                "PRODUCTO %02d\n"
                "Nombre: %s   |   Código: %s\n"
                "Marca: %s   |   Categoría: %s\n"
                "Precio: $%.2f   |   Cantidad: %d   |   Tipo de piel: %s\n"
                "Estado: %s   |   Etiquetas: %s\n"
                "Comentarios: %s\n"
                % (
                    indice,
                    producto["nombre"],
                    producto["codigo"],
                    producto["marca"],
                    producto["categoria"],
                    producto["precio"],
                    producto["cantidad"],
                    producto["tipo_piel"],
                    producto["estado"],
                    etiquetas,
                    comentarios,
                )
                + "─" * 72
            )

        self.listado_productos.setPlainText("\n\n".join(bloques))


class DialogoRegistro(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("dialogoRegistro")
        self.setWindowTitle("Registrar producto de belleza")
        self.setWindowFlags(
            Qt.Window
            | Qt.WindowTitleHint
            | Qt.WindowSystemMenuHint
            | Qt.WindowMinimizeButtonHint
            | Qt.WindowMaximizeButtonHint
            | Qt.WindowCloseButtonHint
        )
        self.setMinimumSize(800, 650)
        self.resize(860, 700)
        self.producto_registrado = None

        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(30, 20, 30, 20)
        raiz.setSpacing(10)

        cabecera = QHBoxLayout()
        textos = QVBoxLayout()
        marca = QLabel("GLOW BELLEZA")
        marca.setObjectName("marca")
        titulo = QLabel("Nuevo producto")
        titulo.setObjectName("titulo")
        instruccion = QLabel("Completa la información para agregarlo al inventario.")
        instruccion.setObjectName("subtitulo")
        instruccion.setWordWrap(True)
        textos.addWidget(marca)
        textos.addWidget(titulo)
        textos.addWidget(instruccion)
        distintivo = QLabel("FORMULARIO DE PRODUCTO")
        distintivo.setObjectName("distintivo")
        cabecera.addLayout(textos)
        cabecera.addStretch()
        cabecera.addWidget(distintivo, 0, Qt.AlignTop)
        raiz.addLayout(cabecera)

        formulario = QFormLayout()
        formulario.setContentsMargins(14, 2, 14, 2)
        formulario.setHorizontalSpacing(14)
        formulario.setVerticalSpacing(7)

        self.nombre = QLineEdit()
        self.nombre.setPlaceholderText("Ejemplo: Crema hidratante Glow")
        self.codigo = QLineEdit()
        self.codigo.setPlaceholderText("Ejemplo: GB-001")
        self.marca = QLineEdit()
        self.marca.setPlaceholderText("Ejemplo: Glow Beauty")
        self.categoria = QComboBox()
        self.categoria.addItems([
            "Cuidado facial",
            "Maquillaje",
            "Cuidado corporal",
            "Cabello",
            "Perfumería",
            "Accesorios",
        ])
        self.precio = QLineEdit()
        self.precio.setPlaceholderText("Ejemplo: 24990 o 24990.50")
        self.cantidad = QLineEdit()
        self.cantidad.setPlaceholderText("Ejemplo: 25")
        self.tipo_piel = QComboBox()
        self.tipo_piel.addItems([
            "Todos los tipos",
            "Piel normal",
            "Piel seca",
            "Piel grasa",
            "Piel mixta",
            "Piel sensible",
        ])
        self.comentarios = QTextEdit()
        self.comentarios.setPlaceholderText(
            "Escribe detalles del producto, presentación o indicaciones..."
        )
        self.comentarios.setMinimumHeight(62)
        self.comentarios.setMaximumHeight(90)

        formulario.addRow("Nombre del producto *", self.nombre)
        formulario.addRow("Código *", self.codigo)
        formulario.addRow("Marca *", self.marca)
        formulario.addRow("Categoría *", self.categoria)
        formulario.addRow("Precio *", self.precio)
        formulario.addRow("Cantidad *", self.cantidad)
        formulario.addRow("Tipo de piel *", self.tipo_piel)
        formulario.addRow("Comentarios", self.comentarios)
        raiz.addLayout(formulario)

        extras = QGridLayout()
        extras.setContentsMargins(14, 2, 14, 2)
        extras.setHorizontalSpacing(18)
        extras.setVerticalSpacing(6)
        extras.setColumnStretch(4, 1)

        estado_texto = QLabel("Estado *")
        etiquetas_texto = QLabel("Etiquetas")
        self.estado_activo = QRadioButton("Activo")
        self.estado_inactivo = QRadioButton("Inactivo")
        self.estado_activo.setChecked(True)
        self.nuevo = QCheckBox("Nuevo")
        self.oferta = QCheckBox("Oferta")
        self.recomendado = QCheckBox("Recomendado")

        extras.addWidget(estado_texto, 0, 0)
        extras.addWidget(self.estado_activo, 0, 1)
        extras.addWidget(self.estado_inactivo, 0, 2)
        extras.addWidget(etiquetas_texto, 1, 0)
        extras.addWidget(self.nuevo, 1, 1)
        extras.addWidget(self.oferta, 1, 2)
        extras.addWidget(self.recomendado, 1, 3)
        raiz.addLayout(extras)

        acciones = QVBoxLayout()
        acciones.setSpacing(10)
        self.mensaje = QLabel("Los campos con * son obligatorios.")
        self.mensaje.setObjectName("ayuda")
        self.mensaje.setWordWrap(True)
        acciones.addWidget(self.mensaje)

        botones = QHBoxLayout()
        botones.setSpacing(10)
        guardar = QPushButton("Guardar")
        guardar.setObjectName("primario")
        guardar.setMinimumWidth(110)
        guardar.clicked.connect(self.guardar_producto)
        limpiar = QPushButton("Limpiar")
        limpiar.setObjectName("suave")
        limpiar.clicked.connect(self.limpiar_formulario)
        salir = QPushButton("Salir")
        salir.setObjectName("peligro")
        salir.clicked.connect(self.close)

        botones.addStretch()
        botones.addWidget(guardar)
        botones.addWidget(limpiar)
        botones.addWidget(salir)
        acciones.addLayout(botones)
        raiz.addLayout(acciones)
        raiz.addStretch()

        self.nombre.setFocus()

    # ---------------------------------------------------------------- helpers
    def _cambiar_estilo_mensaje(self, nombre_objeto):
        """Qt no reaplica el QSS al cambiar objectName sin un repolish."""
        self.mensaje.setObjectName(nombre_objeto)
        self.mensaje.style().unpolish(self.mensaje)
        self.mensaje.style().polish(self.mensaje)
        self.mensaje.update()

    def mostrar_error(self, texto):
        self.mensaje.setText(texto)
        self._cambiar_estilo_mensaje("estadoError")

    def limpiar_formulario(self):
        self.nombre.clear()
        self.codigo.clear()
        self.marca.clear()
        self.precio.clear()
        self.cantidad.clear()
        self.comentarios.clear()
        self.categoria.setCurrentIndex(0)
        self.tipo_piel.setCurrentIndex(0)
        self.estado_activo.setChecked(True)
        self.nuevo.setChecked(False)
        self.oferta.setChecked(False)
        self.recomendado.setChecked(False)
        self.mensaje.setText("Los campos con * son obligatorios.")
        self._cambiar_estilo_mensaje("ayuda")
        self.nombre.setFocus()

    # -------------------------------------------------------------- validacion
    def guardar_producto(self):
        nombre = self.nombre.text().strip()
        codigo = self.codigo.text().strip()
        marca = self.marca.text().strip()
        precio_texto = self.precio.text().strip().replace(",", ".")
        cantidad_texto = self.cantidad.text().strip()

        if not all([nombre, codigo, marca, precio_texto, cantidad_texto]):
            self.mostrar_error("Completa todos los campos obligatorios.")
            self.nombre.setFocus()
            return

        try:
            precio = float(precio_texto)
        except ValueError:
            self.mostrar_error("El precio debe contener un valor numérico.")
            self.precio.setFocus()
            return

        try:
            cantidad = int(cantidad_texto)
        except ValueError:
            self.mostrar_error("La cantidad debe ser un número entero.")
            self.cantidad.setFocus()
            return

        if math.isnan(precio) or math.isinf(precio) or precio <= 0:
            self.mostrar_error("El precio debe ser un número mayor que cero.")
            self.precio.setFocus()
            return

        if cantidad < 0:
            self.mostrar_error("La cantidad no puede ser menor que cero.")
            self.cantidad.setFocus()
            return

        parent = self.parent()
        productos = parent.productos if parent is not None and hasattr(parent, "productos") else []
        if any(p["codigo"].lower() == codigo.lower() for p in productos):
            self.mostrar_error("Ya existe un producto registrado con este código.")
            self.codigo.setFocus()
            return

        etiquetas = []
        if self.nuevo.isChecked():
            etiquetas.append("Nuevo")
        if self.oferta.isChecked():
            etiquetas.append("Oferta")
        if self.recomendado.isChecked():
            etiquetas.append("Recomendado")

        self.producto_registrado = {
            "nombre": nombre,
            "codigo": codigo,
            "marca": marca,
            "categoria": self.categoria.currentText(),
            "precio": precio,
            "cantidad": cantidad,
            "tipo_piel": self.tipo_piel.currentText(),
            "estado": "Activo" if self.estado_activo.isChecked() else "Inactivo",
            "etiquetas": etiquetas,
            "comentarios": self.comentarios.toPlainText().strip(),
        }
        self.accept()


def main():
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()