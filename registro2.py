"""Glow Belleza | Registro de productos: interfaz Toga (BeeWare).

Puerto de registro.py (PyQt5) a la libreria Toga 0.5.
"""

from __future__ import annotations

import math

import toga
from toga.style import Pack

# Paleta de colores (equivalente al QSS de la version PyQt5).
FONDO_PAGINA = "#FFF5FA"
PANEL = "#FFFFFF"
PANEL_BORDE = "#EACCEB"
MARCA = "#A0449D"
TITULO = "#6B287F"
SUBTITULO = "#755E7D"
SECCION = "#6B287F"
AYUDA = "#8B728F"
CONTADOR = "#A0449D"
ESTADO = "#387B5A"
ESTADO_FONDO = "#EAF8F0"
ESTADO_ERROR = "#B42318"
ESTADO_ERROR_FONDO = "#FFF0F0"
DISTINTIVO = "#8A368D"
DISTINTIVO_FONDO = "#F5E4FA"
DISTINTIVO_BORDE = "#E6C7EB"
TEXTO = "#43284D"
TEXTO_LISTADO = "#4B2F55"
PRIMARIO = "#B552B2"
SUAVE = "#F5E4FA"
SUAVE_TEXTO = "#79328A"
PELIGRO = "#A73A57"
PELIGRO_FONDO = "#FFF0F3"


def caja(children=None, *, direction="column", gap=8, margin=0,
         flex=None, width=None, height=None, background_color=None,
         align_items=None, justify_content=None, **extra):
    """Crea un toga.Box con un estilo Pack a partir de argumentos opcionales."""
    propiedades = {"direction": direction, "gap": gap, "margin": margin}
    if flex is not None:
        propiedades["flex"] = flex
    if width is not None:
        propiedades["width"] = width
    if height is not None:
        propiedades["height"] = height
    if background_color is not None:
        propiedades["background_color"] = background_color
    if align_items is not None:
        propiedades["align_items"] = align_items
    if justify_content is not None:
        propiedades["justify_content"] = justify_content
    propiedades.update(extra)
    return toga.Box(children=children or [], style=Pack(**propiedades))


def etiqueta(texto, *, size=14, color=TEXTO, bold=False, **extra):
    """Crea un toga.Label con estilo tipografico y opciones adicionales."""
    estilo = {"font_size": size, "color": color,
              "font_weight": "bold" if bold else "normal"}
    estilo.update(extra)
    return toga.Label(texto, style=Pack(**estilo))


def fila(etiqueta_texto, widget):
    """Fila tipo QFormLayout: etiqueta de ancho fijo a la izquierda del campo."""
    titulo = toga.Label(
        etiqueta_texto,
        style=Pack(width=180, margin_right=12, margin_top=6, color=TEXTO),
    )
    return caja([titulo, widget], direction="row", gap=0, margin_bottom=6)


class DialogoRegistro(toga.Window):
    """Ventana secundaria equivalente a DialogoRegistro (QDialog)."""

    def __init__(self, app_registro, on_result=None):
        super().__init__(
            title="Registrar producto de belleza",
            size=(860, 700),
            resizable=True,
            closable=True,
            minimizable=False,
            on_close=self._al_cerrar_ventana,
        )
        self._app_registro = app_registro
        self._al_resultado = on_result
        self._notificado = False
        self.producto_registrado = None
        self.content = self._construir_formulario()

    # ------------------------------------------------------------------- cierre
    def _al_cerrar_ventana(self, window, **kwargs):
        self._notificar_resultado()
        return True

    def _notificar_resultado(self):
        if self._notificado:
            return
        self._notificado = True
        if self._al_resultado is not None:
            self._al_resultado(self)

    def _cerrar(self):
        self._notificar_resultado()
        self.close()

    # ------------------------------------------------------------------ vista
    def _construir_formulario(self):
        marca = etiqueta("GLOW BELLEZA", size=15, color=MARCA, bold=True,
                         margin_bottom=4)
        titulo = etiqueta("Nuevo producto", size=34, color=TITULO, bold=True,
                          margin_bottom=4)
        instruccion = etiqueta(
            "Completa la información para agregarlo al inventario.",
            size=15, color=SUBTITULO, margin_bottom=10,
        )
        textos = caja([marca, titulo, instruccion], gap=0)
        distintivo = etiqueta(
            "FORMULARIO DE PRODUCTO", size=10, color=DISTINTIVO, bold=True,
            background_color=DISTINTIVO_FONDO, margin=(4, 9),
        )
        cabecera = caja(
            [textos, caja([], flex=1), distintivo],
            direction="row", gap=0, margin_bottom=10,
            align_items="start",
        )

        self.nombre = toga.TextInput(placeholder="Ejemplo: Crema hidratante Glow",
                                     style=Pack(flex=1))
        self.codigo = toga.TextInput(placeholder="Ejemplo: GB-001",
                                     style=Pack(flex=1))
        self.marca_producto = toga.TextInput(placeholder="Ejemplo: Glow Beauty",
                                             style=Pack(flex=1))
        self.categoria = toga.Selection(
            items=[
                "Cuidado facial",
                "Maquillaje",
                "Cuidado corporal",
                "Cabello",
                "Perfumería",
                "Accesorios",
            ],
            value="Cuidado facial",
            style=Pack(flex=1),
        )
        self.precio = toga.TextInput(placeholder="Ejemplo: 24990 o 24990.50",
                                     style=Pack(flex=1))
        self.cantidad = toga.TextInput(placeholder="Ejemplo: 25",
                                       style=Pack(flex=1))
        self.tipo_piel = toga.Selection(
            items=[
                "Todos los tipos",
                "Piel normal",
                "Piel seca",
                "Piel grasa",
                "Piel mixta",
                "Piel sensible",
            ],
            value="Todos los tipos",
            style=Pack(flex=1),
        )
        self.comentarios = toga.MultilineTextInput(
            placeholder="Escribe detalles del producto, presentación o indicaciones...",
            style=Pack(flex=1, height=70),
        )

        formulario = caja(
            [
                fila("Nombre del producto *", self.nombre),
                fila("Código *", self.codigo),
                fila("Marca *", self.marca_producto),
                fila("Categoría *", self.categoria),
                fila("Precio *", self.precio),
                fila("Cantidad *", self.cantidad),
                fila("Tipo de piel *", self.tipo_piel),
                fila("Comentarios", self.comentarios),
            ],
            gap=0, margin_bottom=8,
        )

        self.estado = toga.Selection(
            items=["Activo", "Inactivo"],
            value="Activo",
            style=Pack(width=200),
        )
        self.nuevo = toga.Switch("Nuevo", value=False)
        self.oferta = toga.Switch("Oferta", value=False)
        self.recomendado = toga.Switch("Recomendado", value=False)
        etiquetas = caja(
            [self.nuevo, self.oferta, self.recomendado],
            direction="row", gap=16, margin_bottom=8,
        )
        extras = caja(
            [
                caja(
                    [etiqueta("Estado *", size=14), self.estado],
                    direction="row", gap=12, align_items="center",
                ),
                caja(
                    [etiqueta("Etiquetas", size=14), etiquetas],
                    direction="row", gap=12, align_items="center",
                ),
            ],
            gap=8, margin_bottom=8,
        )

        self.mensaje = etiqueta("Los campos con * son obligatorios.", size=12,
                                color=AYUDA, margin_bottom=8)
        guardar = toga.Button("Guardar", on_press=self.guardar_producto,
                              style=Pack(width=110, margin_right=10))
        limpiar = toga.Button("Limpiar", on_press=self.limpiar_formulario,
                              style=Pack(width=110, margin_right=10))
        salir = toga.Button("Salir", on_press=self.rechazar,
                            style=Pack(width=110))
        botones = caja([guardar, limpiar, salir], direction="row", gap=0)

        cuerpo = caja(
            [cabecera, formulario, extras, self.mensaje, botones],
            gap=0, margin=(24, 30),
            background_color=FONDO_PAGINA,
        )
        return toga.ScrollContainer(content=cuerpo, horizontal=False,
                                    vertical=True)

    # ---------------------------------------------------------------- acciones
    def rechazar(self, widget=None, **kwargs):
        self.producto_registrado = None
        self._cerrar()

    def limpiar_formulario(self, widget=None, **kwargs):
        self.nombre.value = ""
        self.codigo.value = ""
        self.marca_producto.value = ""
        self.precio.value = ""
        self.cantidad.value = ""
        self.comentarios.value = ""
        self.categoria.value = "Cuidado facial"
        self.tipo_piel.value = "Todos los tipos"
        self.estado.value = "Activo"
        self.nuevo.value = False
        self.oferta.value = False
        self.recomendado.value = False
        self._cambiar_estilo_mensaje(error=False)
        self.mensaje.text = "Los campos con * son obligatorios."

    # -------------------------------------------------------------- validacion
    def _cambiar_estilo_mensaje(self, error):
        self.mensaje.style = Pack(
            font_size=12,
            color=ESTADO_ERROR if error else ESTADO,
            background_color=ESTADO_ERROR_FONDO if error else ESTADO_FONDO,
            margin=(6, 10),
            margin_bottom=8,
        )

    def mostrar_error(self, texto):
        self._cambiar_estilo_mensaje(error=True)
        self.mensaje.text = texto

    def guardar_producto(self, widget=None, **kwargs):
        nombre = self.nombre.value.strip()
        codigo = self.codigo.value.strip()
        marca = self.marca_producto.value.strip()
        precio_texto = self.precio.value.strip().replace(",", ".")
        cantidad_texto = self.cantidad.value.strip()

        if not all([nombre, codigo, marca, precio_texto, cantidad_texto]):
            self.mostrar_error("Completa todos los campos obligatorios.")
            return

        try:
            precio = float(precio_texto)
        except ValueError:
            self.mostrar_error("El precio debe contener un valor numérico.")
            return

        try:
            cantidad = int(cantidad_texto)
        except ValueError:
            self.mostrar_error("La cantidad debe ser un número entero.")
            return

        if math.isnan(precio) or math.isinf(precio) or precio <= 0:
            self.mostrar_error("El precio debe ser un número mayor que cero.")
            return

        if cantidad < 0:
            self.mostrar_error("La cantidad no puede ser menor que cero.")
            return

        productos = getattr(self._app_registro, "productos", [])
        if any(p["codigo"].lower() == codigo.lower() for p in productos):
            self.mostrar_error("Ya existe un producto registrado con este código.")
            return

        etiquetas = []
        if self.nuevo.value:
            etiquetas.append("Nuevo")
        if self.oferta.value:
            etiquetas.append("Oferta")
        if self.recomendado.value:
            etiquetas.append("Recomendado")

        self.producto_registrado = {
            "nombre": nombre,
            "codigo": codigo,
            "marca": marca,
            "categoria": self.categoria.value,
            "precio": precio,
            "cantidad": cantidad,
            "tipo_piel": self.tipo_piel.value,
            "estado": self.estado.value,
            "etiquetas": etiquetas,
            "comentarios": self.comentarios.value.strip(),
        }
        self._cerrar()


class AplicacionRegistro(toga.App):
    """Aplicacion principal equivalente a VentanaPrincipal (QMainWindow)."""

    def startup(self):
        self.productos = []
        self.registro_visible = False
        self.dialogo_registro = None

        self.main_window = toga.MainWindow(
            title="Glow Belleza | Bienvenida", size=(980, 720)
        )
        self.main_window.content = self._vista_bienvenida()
        self.main_window.show()

    # ------------------------------------------------------------------ vistas
    def _vista_bienvenida(self):
        marca = etiqueta("GLOW BELLEZA", size=15, color=MARCA, bold=True,
                         margin_bottom=4)
        titulo = etiqueta("¡Bienvenida a tu nueva rutina de belleza!", size=34,
                          color=TITULO, bold=True, margin_bottom=6)
        subtitulo = etiqueta(
            "Organiza tu inventario de productos de forma sencilla, elegante y rápida.",
            size=15, color=SUBTITULO, margin_bottom=12,
        )

        encabezado = etiqueta("Todo lo que necesitas en un solo lugar", size=18,
                              color=SECCION, bold=True, margin_bottom=6)
        descripcion = toga.MultilineTextInput(
            value=(
                "Registra nombre, código, marca, categoría, precio y cantidad.\n\n"
                "Clasifica cada producto por tipo de piel, estado y etiquetas "
                "especiales.\n\n"
                "Consulta tus productos guardados desde una vista clara y organizada."
            ),
            readonly=True,
            style=Pack(flex=1, height=150, margin_bottom=10),
        )
        ingresar = toga.Button("Ingresar al registro", on_press=self.mostrar_registro,
                               style=Pack(flex=1, margin_right=6))
        salir = toga.Button("Salir", on_press=self.salir,
                            style=Pack(flex=1, margin_left=6))
        botones = caja([ingresar, salir], direction="row", gap=0)

        panel = caja([encabezado, descripcion, botones], gap=8, margin=24,
                     background_color=PANEL)
        contenido = caja([marca, titulo, subtitulo, panel], gap=6,
                         margin=(48, 80), background_color=FONDO_PAGINA)
        return toga.ScrollContainer(content=contenido, horizontal=False,
                                    vertical=True)

    def _vista_registro(self):
        marca = etiqueta("GLOW BELLEZA", size=15, color=MARCA, bold=True,
                         margin_bottom=2)
        titulo = etiqueta("Registro de productos", size=34, color=TITULO,
                          bold=True, margin_bottom=2)
        subtitulo = etiqueta("Consulta y organiza tu inventario de belleza.",
                             size=15, color=SUBTITULO)
        textos = caja([marca, titulo, subtitulo], gap=0)
        registrar = toga.Button("Registrar producto", on_press=self.abrir_registro,
                                style=Pack(width=180))
        cabecera = caja([textos, caja([], flex=1), registrar],
                        direction="row", gap=0, margin_bottom=10,
                        align_items="start")

        self.mensaje_registro = etiqueta("", size=12, color=ESTADO,
                                         background_color=ESTADO_FONDO,
                                         margin=(6, 10), margin_bottom=10)

        seccion = etiqueta("Productos registrados", size=18, color=SECCION,
                           bold=True, margin_bottom=6)
        self.listado_productos = toga.MultilineTextInput(
            readonly=True, style=Pack(flex=1, margin_bottom=10)
        )

        self.contador_productos = etiqueta("", size=14, color=CONTADOR, bold=True)
        volver = toga.Button("Volver al inicio", on_press=self.mostrar_bienvenida,
                             style=Pack(width=160, margin_right=10))
        salir = toga.Button("Salir", on_press=self.salir, style=Pack(width=110))
        pie = caja(
            [self.contador_productos, caja([], flex=1), volver, salir],
            direction="row", gap=0, align_items="center",
        )

        pagina = caja([cabecera, self.mensaje_registro, seccion,
                       self.listado_productos, pie],
                      gap=0, margin=(40, 52), background_color=FONDO_PAGINA)
        return pagina

    def mostrar_bienvenida(self, widget=None, **kwargs):
        self.registro_visible = False
        self.main_window.title = "Glow Belleza | Bienvenida"
        self.main_window.content = self._vista_bienvenida()

    def mostrar_registro(self, widget=None, **kwargs):
        self.registro_visible = True
        self.main_window.title = "Glow Belleza | Productos"
        self.main_window.content = self._vista_registro()
        self.actualizar_listado(
            "Ingresa un nuevo producto para comenzar tu registro."
        )

    def salir(self, widget=None, **kwargs):
        self.request_exit()

    # ---------------------------------------------------------------- acciones
    def abrir_registro(self, widget=None, **kwargs):
        if self.dialogo_registro is not None:
            self.dialogo_registro.close()
            self.dialogo_registro = None

        dialogo = DialogoRegistro(self, on_result=self._al_terminar_registro)
        self.dialogo_registro = dialogo
        dialogo.show()

    def _al_terminar_registro(self, dialogo):
        self.dialogo_registro = None
        if dialogo.producto_registrado is not None:
            self.productos.append(dialogo.producto_registrado)
            if self.registro_visible:
                self.actualizar_listado(
                    "Producto \u00ab%s\u00bb guardado correctamente."
                    % dialogo.producto_registrado["nombre"]
                )

    def actualizar_listado(self, mensaje):
        total = len(self.productos)
        total_texto = "producto" if total == 1 else "productos"
        self.contador_productos.text = (
            "%d %s guardado%s" % (total, total_texto, "" if total == 1 else "s")
        )
        self.mensaje_registro.text = mensaje

        if not self.productos:
            self.listado_productos.value = (
                "Todavía no hay productos registrados.\n\n"
                "Pulsa \u00abRegistrar producto\u00bb para crear el primero."
            )
            return

        bloques = []
        for indice, producto in enumerate(self.productos, start=1):
            etiquetas = (", ".join(producto["etiquetas"])
                         if producto["etiquetas"] else "Sin etiquetas")
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
                + "-" * 72
            )

        self.listado_productos.value = "\n\n".join(bloques)


def main():
    return AplicacionRegistro(
        "Glow Belleza", "org.glowbelleza.registro"
    ).main_loop()


if __name__ == "__main__":
    main()
