"""Glow Belleza | Registro de productos con wxPython.

Puerto de registro.py (PyQt5) a la libreria wxPython 4.3.
"""

from __future__ import annotations

import math

import wx

# Paleta (equivalente al QSS de la version PyQt5).
FONDO_VENTANA = "#FFF8FC"
FONDO_PAGINA_INICIO = "#FFF5FA"
FONDO_PAGINA_FIN = "#FFFFFF"
FONDO_DIALOGO_INICIO = "#FFF8FC"
PANEL = "#FFFFFF"
PANEL_BORDE = "#EACCEB"
PANEL_MEDIO = "#F7ECFF"
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
TEXTO = "#43284D"
TEXTO_LISTADO = "#4B2F55"
TEXTO_DESCRIPCION = "#674A70"
PRIMARIO_FIN = "#A64BC1"
PRIMARIO_TEXTO = "#FFFFFF"
SUAVE_FONDO = "#F5E4FA"
SUAVE_TEXTO = "#79328A"
PELIGRO_FONDO = "#FFF0F3"
PELIGRO_TEXTO = "#A73A57"


def color(hexadecimal):
    """Convierte "#RRGGBB" en un wx.Colour."""
    valor = hexadecimal.lstrip("#")
    return wx.Colour(
        int(valor[0:2], 16), int(valor[2:4], 16), int(valor[4:6], 16)
    )


def fuente(tamano, negrita=False, monoespaciada=False):
    """Crea un wx.Font con Segoe UI (o Consolas) del tamano indicado."""
    info = wx.FontInfo(tamano).FaceName("Consolas" if monoespaciada else "Segoe UI")
    if negrita:
        info = info.Bold()
    return wx.Font(info)


def boton(parent, texto, manejador, fondo=None, texto_color=None, negrita=True):
    """Crea un wx.Button con colores y tipografia, enlazado a su manejador."""
    control = wx.Button(parent, label=texto)
    control.SetFont(fuente(14, negrita=negrita))
    if fondo:
        control.SetBackgroundColour(color(fondo))
    if texto_color:
        control.SetForegroundColour(color(texto_color))
    control.Bind(wx.EVT_BUTTON, manejador)
    return control


class PanelDegradado(wx.Panel):
    """Panel que pinta un degradado diagonal (equivalente al QSS qlineargradient)."""

    def __init__(self, parent, inicio, fin):
        super().__init__(parent)
        self._inicio = color(inicio)
        self._fin = color(fin)
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.Bind(wx.EVT_PAINT, self._al_pintar)

    def _al_pintar(self, evento):
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        if gc is None:
            return
        ancho, alto = self.GetClientSize()
        if ancho <= 0 or alto <= 0:
            return
        pincel = gc.CreateLinearGradientBrush(0, 0, ancho, alto, self._inicio, self._fin)
        gc.SetBrush(pincel)
        gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawRectangle(0, 0, ancho, alto)


class PanelRedondeado(wx.Panel):
    """Panel con fondo de esquinas redondeadas y borde opcional."""

    def __init__(self, parent, relleno, fondo, borde=None, radio=24):
        super().__init__(parent)
        self._relleno = color(relleno)
        self._fondo = color(fondo)
        self._borde = color(borde) if borde else None
        self._radio = radio
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.Bind(wx.EVT_PAINT, self._al_pintar)

    def _al_pintar(self, evento):
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        if gc is None:
            return
        ancho, alto = self.GetClientSize()
        if ancho <= 0 or alto <= 0:
            return
        gc.SetBrush(wx.Brush(self._fondo))
        gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawRectangle(0, 0, ancho, alto)
        gc.SetBrush(wx.Brush(self._relleno))
        if self._borde is not None:
            gc.SetPen(wx.Pen(self._borde, 1))
        else:
            gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawRoundedRectangle(0, 0, ancho, alto, self._radio)


class DialogoRegistro(wx.Dialog):
    """Ventana secundaria equivalente a DialogoRegistro (QDialog)."""

    def __init__(self, parent, al_terminar=None):
        super().__init__(
            parent,
            title="Registrar producto de belleza",
            size=(860, 760),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )
        self.SetMinSize((800, 700))
        self.SetBackgroundColour(color(FONDO_DIALOGO_INICIO))
        self._al_terminar = al_terminar
        self._terminado = False
        self.producto_registrado = None
        self._construir_formulario()
        self.Bind(wx.EVT_CLOSE, self._al_cerrar_ventana)

    # ------------------------------------------------------------------- cierre
    def _al_cerrar_ventana(self, evento):
        self._notificar_resultado()
        evento.Skip()

    def _notificar_resultado(self):
        if self._terminado:
            return
        self._terminado = True
        if self._al_terminar is not None:
            self._al_terminar(self)

    def _cerrar(self):
        self._notificar_resultado()
        self.Close()

    # ------------------------------------------------------------------ vista
    def _construir_formulario(self):
        self._cuerpo = wx.ScrolledWindow(self, style=wx.VSCROLL)
        self._cuerpo.SetBackgroundColour(color(FONDO_DIALOGO_INICIO))
        self._cuerpo.SetScrollRate(0, 15)
        raiz = wx.BoxSizer(wx.VERTICAL)
        margen = 30

        marca = wx.StaticText(self._cuerpo, label="GLOW BELLEZA")
        marca.SetFont(fuente(15, negrita=True))
        marca.SetForegroundColour(color(MARCA))
        titulo = wx.StaticText(self._cuerpo, label="Nuevo producto")
        titulo.SetFont(fuente(34, negrita=True))
        titulo.SetForegroundColour(color(TITULO))
        instruccion = wx.StaticText(
            self._cuerpo,
            label="Completa la información para agregarlo al inventario.",
        )
        instruccion.SetFont(fuente(15))
        instruccion.SetForegroundColour(color(SUBTITULO))
        textos = wx.BoxSizer(wx.VERTICAL)
        textos.Add(marca, 0)
        textos.Add(titulo, 0, wx.TOP, 2)
        textos.Add(instruccion, 0, wx.TOP, 4)

        distintivo = wx.StaticText(self._cuerpo, label="FORMULARIO DE PRODUCTO")
        distintivo.SetFont(fuente(10, negrita=True))
        distintivo.SetForegroundColour(color(DISTINTIVO))
        cabecera = wx.BoxSizer(wx.HORIZONTAL)
        cabecera.Add(textos, 1, wx.ALIGN_TOP)
        cabecera.Add(distintivo, 0, wx.ALIGN_TOP)
        raiz.Add(cabecera, 0, wx.EXPAND | wx.ALL, margen)

        formulario = wx.FlexGridSizer(cols=2, vgap=7, hgap=14)
        formulario.AddGrowableCol(1, 1)

        self.nombre = self._campo(formulario, "Nombre del producto *",
                                  wx.TextCtrl(self._cuerpo))
        self.nombre.SetHint("Ejemplo: Crema hidratante Glow")
        self.codigo = self._campo(formulario, "Código *", wx.TextCtrl(self._cuerpo))
        self.codigo.SetHint("Ejemplo: GB-001")
        self.marca_producto = self._campo(formulario, "Marca *", wx.TextCtrl(self._cuerpo))
        self.marca_producto.SetHint("Ejemplo: Glow Beauty")

        self.categoria = wx.ComboBox(self._cuerpo,
            choices=[
                "Cuidado facial",
                "Maquillaje",
                "Cuidado corporal",
                "Cabello",
                "Perfumería",
                "Accesorios",
            ],
            style=wx.CB_READONLY,
        )
        self.categoria.SetSelection(0)
        self._campo(formulario, "Categoría *", self.categoria)

        self.precio = self._campo(formulario, "Precio *", wx.TextCtrl(self._cuerpo))
        self.precio.SetHint("Ejemplo: 24990 o 24990.50")
        self.cantidad = self._campo(formulario, "Cantidad *", wx.TextCtrl(self._cuerpo))
        self.cantidad.SetHint("Ejemplo: 25")

        self.tipo_piel = wx.ComboBox(self._cuerpo,
            choices=[
                "Todos los tipos",
                "Piel normal",
                "Piel seca",
                "Piel grasa",
                "Piel mixta",
                "Piel sensible",
            ],
            style=wx.CB_READONLY,
        )
        self.tipo_piel.SetSelection(0)
        self._campo(formulario, "Tipo de piel *", self.tipo_piel)

        self.comentarios = wx.TextCtrl(self._cuerpo, style=wx.TE_MULTILINE, size=(-1, 70))
        self.comentarios.SetHint(
            "Escribe detalles del producto, presentación o indicaciones..."
        )
        self._campo(formulario, "Comentarios", self.comentarios)

        raiz.Add(formulario, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, margen)

        extras = wx.FlexGridSizer(cols=2, vgap=8, hgap=14)
        extras.AddGrowableCol(1, 1)
        estado_texto = wx.StaticText(self._cuerpo, label="Estado *")
        estado = wx.BoxSizer(wx.HORIZONTAL)
        self.estado_activo = wx.RadioButton(self._cuerpo, label="Activo",
                                            style=wx.RB_GROUP)
        self.estado_activo.SetValue(True)
        self.estado_inactivo = wx.RadioButton(self._cuerpo, label="Inactivo")
        estado.Add(self.estado_activo, 0, wx.ALIGN_CENTER_VERTICAL)
        estado.Add(self.estado_inactivo, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 18)
        extras.Add(estado_texto, 0, wx.ALIGN_CENTER_VERTICAL)
        extras.Add(estado, 1, wx.EXPAND)

        etiquetas_texto = wx.StaticText(self._cuerpo, label="Etiquetas")
        self.nuevo = wx.CheckBox(self._cuerpo, label="Nuevo")
        self.oferta = wx.CheckBox(self._cuerpo, label="Oferta")
        self.recomendado = wx.CheckBox(self._cuerpo, label="Recomendado")
        etiquetas = wx.BoxSizer(wx.HORIZONTAL)
        for casilla in (self.nuevo, self.oferta, self.recomendado):
            etiquetas.Add(casilla, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 18)
        extras.Add(etiquetas_texto, 0, wx.ALIGN_CENTER_VERTICAL)
        extras.Add(etiquetas, 1, wx.EXPAND)
        raiz.Add(extras, 0, wx.EXPAND | wx.ALL, margen)

        self.mensaje_panel = wx.Panel(self._cuerpo)
        self.mensaje_panel.SetBackgroundColour(color(FONDO_DIALOGO_INICIO))
        mensaje_sizer = wx.BoxSizer(wx.VERTICAL)
        self.mensaje = wx.StaticText(
            self.mensaje_panel, label="Los campos con * son obligatorios."
        )
        self.mensaje.SetFont(fuente(12))
        self.mensaje.SetForegroundColour(color(AYUDA))
        mensaje_sizer.Add(self.mensaje, 0, wx.ALL, 8)
        self.mensaje_panel.SetSizer(mensaje_sizer)
        raiz.Add(self.mensaje_panel, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, margen)

        guardar = boton(self._cuerpo, "Guardar", self.guardar_producto,
                        fondo=PRIMARIO_FIN, texto_color=PRIMARIO_TEXTO)
        limpiar = boton(self._cuerpo, "Limpiar", self.limpiar_formulario,
                        fondo=SUAVE_FONDO, texto_color=SUAVE_TEXTO)
        salir = boton(self._cuerpo, "Salir", self.rechazar,
                      fondo=PELIGRO_FONDO, texto_color=PELIGRO_TEXTO)
        botones = wx.BoxSizer(wx.HORIZONTAL)
        botones.AddStretchSpacer(1)
        botones.Add(guardar, 0, wx.LEFT, 10)
        botones.Add(limpiar, 0, wx.LEFT, 10)
        botones.Add(salir, 0, wx.LEFT, 10)
        raiz.Add(botones, 0, wx.EXPAND | wx.ALL, margen)

        self._cuerpo.SetSizer(raiz)
        self._cuerpo.FitInside()
        contenedor = wx.BoxSizer(wx.VERTICAL)
        contenedor.Add(self._cuerpo, 1, wx.EXPAND)
        self.SetSizer(contenedor)
        self.Layout()
        self.nombre.SetFocus()

    def _campo(self, formulario, texto, control):
        etiqueta = wx.StaticText(self._cuerpo, label=texto)
        etiqueta.SetForegroundColour(color(TEXTO))
        formulario.Add(etiqueta, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        formulario.Add(control, 1, wx.EXPAND)
        return control

    # ---------------------------------------------------------------- acciones
    def rechazar(self, evento=None):
        self.producto_registrado = None
        self._cerrar()

    def limpiar_formulario(self, evento=None):
        self.nombre.SetValue("")
        self.codigo.SetValue("")
        self.marca_producto.SetValue("")
        self.precio.SetValue("")
        self.cantidad.SetValue("")
        self.comentarios.SetValue("")
        self.categoria.SetSelection(0)
        self.tipo_piel.SetSelection(0)
        self.estado_activo.SetValue(True)
        self.nuevo.SetValue(False)
        self.oferta.SetValue(False)
        self.recomendado.SetValue(False)
        self._cambiar_estilo_mensaje(error=False)
        self.mensaje.SetLabel("Los campos con * son obligatorios.")

    # -------------------------------------------------------------- validacion
    def _cambiar_estilo_mensaje(self, error):
        self.mensaje.SetForegroundColour(color(ESTADO_ERROR if error else AYUDA))
        self.mensaje_panel.SetBackgroundColour(
            color(ESTADO_ERROR_FONDO if error else FONDO_DIALOGO_INICIO)
        )
        self.mensaje_panel.Refresh()
        self.Layout()

    def mostrar_error(self, texto):
        self._cambiar_estilo_mensaje(error=True)
        self.mensaje.SetLabel(texto)

    def guardar_producto(self, evento=None):
        nombre = self.nombre.GetValue().strip()
        codigo = self.codigo.GetValue().strip()
        marca = self.marca_producto.GetValue().strip()
        precio_texto = self.precio.GetValue().strip().replace(",", ".")
        cantidad_texto = self.cantidad.GetValue().strip()

        if not all([nombre, codigo, marca, precio_texto, cantidad_texto]):
            self.mostrar_error("Completa todos los campos obligatorios.")
            self.nombre.SetFocus()
            return

        try:
            precio = float(precio_texto)
        except ValueError:
            self.mostrar_error("El precio debe contener un valor numérico.")
            self.precio.SetFocus()
            return

        try:
            cantidad = int(cantidad_texto)
        except ValueError:
            self.mostrar_error("La cantidad debe ser un número entero.")
            self.cantidad.SetFocus()
            return

        if math.isnan(precio) or math.isinf(precio) or precio <= 0:
            self.mostrar_error("El precio debe ser un número mayor que cero.")
            self.precio.SetFocus()
            return

        if cantidad < 0:
            self.mostrar_error("La cantidad no puede ser menor que cero.")
            self.cantidad.SetFocus()
            return

        padre = self.GetParent()
        productos = getattr(padre, "productos", []) if padre is not None else []
        if any(p["codigo"].lower() == codigo.lower() for p in productos):
            self.mostrar_error("Ya existe un producto registrado con este código.")
            self.codigo.SetFocus()
            return

        etiquetas = []
        if self.nuevo.GetValue():
            etiquetas.append("Nuevo")
        if self.oferta.GetValue():
            etiquetas.append("Oferta")
        if self.recomendado.GetValue():
            etiquetas.append("Recomendado")

        self.producto_registrado = {
            "nombre": nombre,
            "codigo": codigo,
            "marca": marca,
            "categoria": self.categoria.GetStringSelection(),
            "precio": precio,
            "cantidad": cantidad,
            "tipo_piel": self.tipo_piel.GetStringSelection(),
            "estado": "Activo" if self.estado_activo.GetValue() else "Inactivo",
            "etiquetas": etiquetas,
            "comentarios": self.comentarios.GetValue().strip(),
        }
        self._cerrar()


class VentanaPrincipal(wx.Frame):
    """Ventana principal equivalente a VentanaPrincipal (QMainWindow)."""

    def __init__(self):
        super().__init__(
            None,
            title="Glow Belleza | Registro de productos",
            size=(980, 720),
        )
        self.SetMinSize((820, 620))
        self.SetBackgroundColour(color(FONDO_VENTANA))
        self.productos = []
        self.registro_visible = False
        self.dialogo_registro = None
        self._vista = None
        self.mostrar_bienvenida()
        self.Centre()

    # ------------------------------------------------------------------ vistas
    def _cambiar_vista(self, constructor):
        anterior = self._vista
        self._vista = constructor()
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._vista, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.Layout()
        if anterior is not None:
            anterior.Destroy()

    def _texto(self, parent, texto, tamano, color_hex, negrita=False,
               monoespaciada=False, alineacion=0):
        etiqueta = wx.StaticText(parent, label=texto, style=alineacion)
        etiqueta.SetFont(fuente(tamano, negrita=negrita,
                                monoespaciada=monoespaciada))
        etiqueta.SetForegroundColour(color(color_hex))
        return etiqueta

    def _construir_bienvenida(self):
        pagina = PanelDegradado(self, FONDO_PAGINA_INICIO, FONDO_PAGINA_FIN)
        raiz = wx.BoxSizer(wx.VERTICAL)
        margen = 80

        raiz.AddStretchSpacer(1)
        raiz.Add(self._texto(pagina, "GLOW BELLEZA", 15, MARCA, negrita=True),
                 0, wx.LEFT | wx.RIGHT, margen)
        raiz.Add(
            self._texto(pagina, "¡Bienvenida a tu nueva rutina de belleza!",
                        34, TITULO, negrita=True),
            0, wx.LEFT | wx.RIGHT | wx.TOP, margen,
        )
        raiz.Add(
            self._texto(pagina,
                        "Organiza tu inventario de productos de forma sencilla, "
                        "elegante y rápida.",
                        15, SUBTITULO),
            0, wx.LEFT | wx.RIGHT | wx.TOP, margen,
        )

        panel = PanelRedondeado(pagina, PANEL, PANEL_MEDIO,
                                 borde=PANEL_BORDE, radio=24)
        panel_sizer = wx.BoxSizer(wx.VERTICAL)
        encabezado = self._texto(panel, "Todo lo que necesitas en un solo lugar",
                                 18, SECCION, negrita=True)
        panel_sizer.Add(encabezado, 0, wx.ALL, 24)

        descripcion = self._texto(
            panel,
            "Registra nombre, código, marca, categoría, precio y cantidad.\n"
            "Clasifica cada producto por tipo de piel, estado y etiquetas "
            "especiales.\n"
            "Consulta tus productos guardados desde una vista clara y organizada.",
            15, TEXTO_DESCRIPCION, alineacion=wx.ALIGN_CENTRE_HORIZONTAL,
        )
        panel_sizer.Add(descripcion, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 24)

        ingresar = boton(panel, "Ingresar al registro", self.mostrar_registro,
                         fondo=PRIMARIO_FIN, texto_color=PRIMARIO_TEXTO)
        salir = boton(panel, "Salir", self.salir,
                      fondo=PELIGRO_FONDO, texto_color=PELIGRO_TEXTO)
        botones = wx.BoxSizer(wx.HORIZONTAL)
        botones.Add(ingresar, 1, wx.RIGHT, 8)
        botones.Add(salir, 1)
        panel_sizer.Add(botones, 0, wx.EXPAND | wx.ALL, 24)
        panel.SetSizer(panel_sizer)

        raiz.Add(panel, 0, wx.EXPAND | wx.ALL, margen)
        raiz.AddSpacer(60)
        pagina.SetSizer(raiz)
        return pagina

    def _construir_registro(self):
        pagina = PanelDegradado(self, FONDO_PAGINA_INICIO, FONDO_PAGINA_FIN)
        raiz = wx.BoxSizer(wx.VERTICAL)
        margen = 52

        marca = self._texto(pagina, "GLOW BELLEZA", 15, MARCA, negrita=True)
        titulo = self._texto(pagina, "Registro de productos", 34, TITULO,
                             negrita=True)
        subtitulo = self._texto(pagina, "Consulta y organiza tu inventario de "
                                         "belleza.", 15, SUBTITULO)
        textos = wx.BoxSizer(wx.VERTICAL)
        textos.Add(marca, 0)
        textos.Add(titulo, 0, wx.TOP, 2)
        textos.Add(subtitulo, 0, wx.TOP, 2)

        registrar = boton(pagina, "Registrar producto", self.abrir_registro,
                          fondo=PRIMARIO_FIN, texto_color=PRIMARIO_TEXTO)
        cabecera = wx.BoxSizer(wx.HORIZONTAL)
        cabecera.Add(textos, 1, wx.ALIGN_TOP)
        cabecera.Add(registrar, 0, wx.ALIGN_TOP)
        raiz.Add(cabecera, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, margen)

        self.mensaje_registro_panel = wx.Panel(pagina)
        self.mensaje_registro_panel.SetBackgroundColour(color(ESTADO_FONDO))
        self.mensaje_registro = self._texto(
            self.mensaje_registro_panel, "", 12, ESTADO)
        mensaje_sizer = wx.BoxSizer(wx.VERTICAL)
        mensaje_sizer.Add(self.mensaje_registro, 0, wx.ALL, 8)
        self.mensaje_registro_panel.SetSizer(mensaje_sizer)
        raiz.Add(self.mensaje_registro_panel, 0,
                 wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, margen)

        seccion = self._texto(pagina, "Productos registrados", 18, SECCION,
                              negrita=True)
        raiz.Add(seccion, 0, wx.LEFT | wx.RIGHT | wx.TOP, margen)

        self.listado_productos = wx.TextCtrl(
            pagina, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.BORDER_SIMPLE)
        self.listado_productos.SetFont(fuente(13, monoespaciada=True))
        self.listado_productos.SetForegroundColour(color(TEXTO_LISTADO))
        self.listado_productos.SetBackgroundColour(color(PANEL))
        raiz.Add(self.listado_productos, 1,
                 wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, margen)

        self.contador_productos = self._texto(pagina, "", 14, CONTADOR,
                                              negrita=True)
        volver = boton(pagina, "Volver al inicio", self.mostrar_bienvenida,
                       fondo=SUAVE_FONDO, texto_color=SUAVE_TEXTO)
        salir = boton(pagina, "Salir", self.salir,
                      fondo=PELIGRO_FONDO, texto_color=PELIGRO_TEXTO)
        pie = wx.BoxSizer(wx.HORIZONTAL)
        pie.Add(self.contador_productos, 0, wx.ALIGN_CENTER_VERTICAL)
        pie.AddStretchSpacer(1)
        pie.Add(volver, 0, wx.RIGHT, 10)
        pie.Add(salir, 0)
        raiz.Add(pie, 0, wx.EXPAND | wx.ALL, margen)

        pagina.SetSizer(raiz)
        return pagina

    def mostrar_bienvenida(self, evento=None):
        self.registro_visible = False
        self.SetTitle("Glow Belleza | Bienvenida")
        self._cambiar_vista(self._construir_bienvenida)

    def mostrar_registro(self, evento=None):
        self.registro_visible = True
        self.SetTitle("Glow Belleza | Productos")
        self._cambiar_vista(self._construir_registro)
        self.actualizar_listado(
            "Ingresa un nuevo producto para comenzar tu registro."
        )

    def salir(self, evento=None):
        self.Close()

    # ---------------------------------------------------------------- acciones
    def abrir_registro(self, evento=None):
        if self.dialogo_registro is not None:
            self.dialogo_registro.Destroy()
            self.dialogo_registro = None

        dialogo = DialogoRegistro(self, al_terminar=self._al_terminar_registro)
        self.dialogo_registro = dialogo
        dialogo.Show()
        dialogo.Raise()

    def _al_terminar_registro(self, dialogo):
        self.dialogo_registro = None
        if dialogo.producto_registrado is not None:
            self.productos.append(dialogo.producto_registrado)
            if self.registro_visible:
                self.actualizar_listado(
                    "Producto «%s» guardado correctamente."
                    % dialogo.producto_registrado["nombre"]
                )

    def actualizar_listado(self, mensaje):
        total = len(self.productos)
        total_texto = "producto" if total == 1 else "productos"
        self.contador_productos.SetLabel(
            "%d %s guardado%s" % (total, total_texto, "" if total == 1 else "s")
        )
        self.mensaje_registro.SetLabel(mensaje)
        self.mensaje_registro_panel.Layout()

        if not self.productos:
            self.listado_productos.SetValue(
                "Todavía no hay productos registrados.\n\n"
                "Pulsa «Registrar producto» para crear el primero."
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

        self.listado_productos.SetValue("\n\n".join(bloques))


def main():
    aplicacion = wx.App(False)
    ventana = VentanaPrincipal()
    ventana.Show()
    aplicacion.MainLoop()


if __name__ == "__main__":
    main()
