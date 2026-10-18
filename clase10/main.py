import sys
from PySide6.QtWidgets import QApplication, QTableWidgetItem, QMessageBox
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile

# datos de ejemplo: una lista de tuplas (nombre, teléfono, edad)
CONTACTOS = [
    ("Ana Rojas", "70012345", 21),
    ("Luis Pérez", "71122334", 9),
    ("María Flores", "72233445", 34),
]


def cargar_ui(ruta):
    archivo = QFile(ruta)
    archivo.open(QFile.OpenModeFlag.ReadOnly)
    ventana = QUiLoader().load(archivo)
    archivo.close()
    return ventana


def actualizar_total():
    ventana.lblTotal.setText(f"Contactos: {tabla.rowCount()}")


def cargar_datos():
    for nombre, telefono, edad in CONTACTOS:
        fila = tabla.rowCount()          # la próxima fila libre
        tabla.insertRow(fila)
        tabla.setItem(fila, 0, QTableWidgetItem(nombre))
        tabla.setItem(fila, 1, QTableWidgetItem(telefono))
        tabla.setItem(fila, 2, QTableWidgetItem(str(edad)))
    actualizar_total()


def agregar_fila():
    fila = tabla.rowCount()
    tabla.insertRow(fila)
    tabla.setItem(fila, 0, QTableWidgetItem("Nuevo contacto"))
    tabla.setItem(fila, 1, QTableWidgetItem(""))
    tabla.setItem(fila, 2, QTableWidgetItem("0"))
    tabla.setCurrentCell(fila, 0)        # selecciona la fila nueva
    tabla.editItem(tabla.item(fila, 0))  # y abre la celda para escribir
    actualizar_total()





def eliminar_fila():
    seleccionadas = tabla.selectionModel().selectedRows()

    if not seleccionadas:
        QMessageBox.warning(
            ventana,
            "Eliminar fila",
            "Primero selecciona una fila."
        )
        return

    fila = seleccionadas[0].row()
    tabla.removeRow(fila)
    actualizar_total()





    

app = QApplication(sys.argv)
ventana = cargar_ui("contactos.ui")
tabla = ventana.tblContactos
tabla.setSelectionBehavior(
    tabla.SelectionBehavior.SelectRows
)
tabla.setSelectionMode(
    tabla.SelectionMode.SingleSelection
)

ventana.btnAgregar.clicked.connect(agregar_fila)
ventana.btnEliminar.clicked.connect(eliminar_fila)

cargar_datos()
ventana.show()
sys.exit(app.exec())