import sys
from PySide6.QtWidgets import QApplication, QStyle
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile


class Bienvenida:
    def __init__(self):
        print("SE EJECUTÓ MI MAIN.PY")
        archivo = QFile("welcome.ui")
        archivo.open(QFile.OpenModeFlag.ReadOnly)
        self.ventana = QUiLoader().load(archivo)
        archivo.close()

        self.contador = 0
        self.titulo_base = self.ventana.windowTitle()  
        self.ventana.lblContador.setText("Saludos: 0")

        # ícono estándar del sistema, como en la clase 7
        icono = self.ventana.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation)
        self.ventana.setWindowIcon(icono)

        self.ventana.btnSaludar.clicked.connect(self.saludar)
        self.ventana.txtNombre.returnPressed.connect(self.saludar)
        self.ventana.btnLimpiar.clicked.connect(self.limpiar)

    def saludar(self):
        print("Se presionó Saludar")
        nombre = self.ventana.txtNombre.text().strip()
        if not nombre:
            self.ventana.lblResultado.setText("Primero escribe tu nombre")
            self.ventana.txtNombre.setFocus()
            return
        self.contador += 1
        print("Contador actual:", self.contador)
        self.ventana.lblResultado.setText(f"¡Hola, {nombre}! Bienvenido(a) a la Agenda de Contactos.")
        self.ventana.lblContador.setText(f"Saludos: {self.contador}")
        self.ventana.setWindowTitle(f"{self.titulo_base} · {self.contador} saludo(s)")  # título dinámico

    def limpiar(self):
        self.ventana.lblResultado.setText("Aquí aparecerá el saludo")


app = QApplication(sys.argv)
app_bienvenida = Bienvenida()
app_bienvenida.ventana.show()
sys.exit(app.exec())