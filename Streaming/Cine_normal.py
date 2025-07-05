from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QListWidget, QLineEdit, QDialog, QSlider, QMessageBox
from PyQt6.QtGui import QPixmap, QIcon, QFont, QFontDatabase, QMouseEvent
from PyQt6.QtCore import Qt, QTimer, QTime
from Clases_and_metodos import Funciones
import os

# Obtener la ruta del archivo de fuente
ruta_base = os.path.join(os.path.dirname(__file__), "Recursos")

class CineGUI(QWidget):
    def __init__(self, sistema):
        super().__init__()
        self.sistema = sistema
        self.tiempo_inicio = QTime.currentTime()  # Guarda el momento de inicio
        self.tiempo_transcurrido = 0  # En segundos
        self.tiempo_estimado = self.calcular_tiempo_estimado() #promedio historico
        self.mapping_peliculas = {}
        self.initUI()
        self.iniciar_contador()

    def calcular_tiempo_estimado(self):
        """Calcula el tiempo estimado basado en el historial"""
        if not self.sistema.usuario_actual or not hasattr(self.sistema.usuario_actual, "Tiempo_total_sesion_en_Segs"):
            return 60 * 5  # 5 minutos esperados (por defecto) si no hay historial
        
        if not self.sistema.usuario_actual.Tiempo_total_sesion_enSegs:
            return 60 * 5
        
        # Calcula el promedio de las últimas 5 sesiones
        ultimas_sesiones = self.sistema.usuario_actual.Tiempo_total_sesion_enSegs[-5:]
        return sum(ultimas_sesiones) / len(ultimas_sesiones)

    def iniciar_contador(self):
        self.timer_tiempo = QTimer(self)
        self.timer_tiempo.timeout.connect(self.actualizar_tiempo)
        self.timer_tiempo.start(1000)  # Actualizar cada segundo
    
    def actualizar_tiempo(self):
        self.tiempo_transcurrido += 1
        tiempo_str = QTime(0, 0).addSecs(self.tiempo_transcurrido).toString("hh:mm:ss")
        self.label_tiempo.setText(f"Tiempo en plataforma: {tiempo_str}")
        
        # Opcional: Actualizar tiempo estimado (ejemplo: 2x el tiempo transcurrido)
        tiempo_estimado_str = QTime(0, 0).addSecs(int(self.tiempo_estimado)).toString("hh:mm:ss")
        self.label_tiempo_estimado.setText(f"⏱ Sesión estimada: {tiempo_estimado_str}")

    def aplicar_estilo_boton(self, boton):
        boton.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: white;
                border: 1px solid #5B9BD5;
                border-radius: 6px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #4e4e4e;
            }
            QPushButton:disabled {
                background-color: #555;
                color: gray;
                border: 1px solid #444;
            }
        """)

    def initUI(self):
        self.setWindowTitle("Interfaz Cine 🎬")
        icon_path = os.path.join(ruta_base, "logaso_9Ri_icon.ico")
        self.setWindowIcon(QIcon(icon_path))
        self.setStyleSheet("background-color: #2C2C2C;")
        self.setFixedSize(685, 500)  # Tamaño fijo para diseño manual

        # Buscar película (entrada)
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Buscar película...")
        self.search_input.setStyleSheet("background-color: #3a3a3a; color: white; border: 1px solid #5B9BD5; border-radius: 6px; padding: 6px;")
        self.search_input.move(300, 45)
        self.search_input.resize(250, 30)
        self.search_input.textChanged.connect(self.buscar_pelicula)

        # Lista de películas (a la derecha)
        self.lista_peliculas = QListWidget(self)
        self.lista_peliculas.setStyleSheet("QListWidget { color: white; }")
        self.lista_peliculas.move(300, 95)
        self.lista_peliculas.resize(370, 295)
        self.cargar_peliculas()

        # Imagen debajo de los botones
        self.label_imagen = QLabel(self)
        self.label_imagen.setStyleSheet("background-color: transparent;")
        ruta_imagen = os.path.join(ruta_base, "Logaso.png")
        if os.path.exists(ruta_imagen):
            pixmap = QPixmap(ruta_imagen)
            pixmap = pixmap.scaled(200, 180, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.label_imagen.setPixmap(pixmap)
            self.label_imagen.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_imagen.move(52, 335)
        self.label_imagen.resize(200, 120)

        # Etiqueta permanente de bienvenida
        self.label_bienvenida = QLabel(self)
        self.label_bienvenida.setStyleSheet("background-color: transparent; color: white;")
        self.label_bienvenida.setText(f"Bienvenido, {self.sistema.usuario_actual.nombre} \U0001F44B")
        self.label_bienvenida.setFont(QFont("Arial", 12))
        self.label_bienvenida.move(35, 55)
        self.label_bienvenida.resize(300, 30)

        # Botones a la izquierda
        self.btn_ver = QPushButton("🎬 Ver película", self)
        self.btn_ver.move(37, 110)
        self.btn_ver.resize(220, 30)
        self.btn_ver.clicked.connect(self.ver_pelicula)
        self.aplicar_estilo_boton(self.btn_ver)

        self.btn_guardar = QPushButton("📌 Ver más tarde", self)
        self.btn_guardar.move(37, 150)
        self.btn_guardar.resize(220, 30)
        self.btn_guardar.clicked.connect(self.guardar_ver_mas_tarde)
        self.aplicar_estilo_boton(self.btn_guardar)

        self.btn_favorita = QPushButton("💖 Tus Favoritas", self)
        self.btn_favorita.move(37, 190)
        self.btn_favorita.resize(220, 30)
        self.btn_favorita.clicked.connect(self.marcar_favorita)
        self.aplicar_estilo_boton(self.btn_favorita)

        self.btn_ver_lista = QPushButton("📜 Listado de 'Ver Mas tarde' ", self)
        self.btn_ver_lista.move(37, 230)
        self.btn_ver_lista.resize(220, 30)
        self.btn_ver_lista.clicked.connect(self.mostrar_ver_mas_tarde)
        self.aplicar_estilo_boton(self.btn_ver_lista)

        self.btn_ver_favoritas = QPushButton("🌟 Listado de favoritas", self)
        self.btn_ver_favoritas.move(37, 270)
        self.btn_ver_favoritas.resize(220, 30)
        self.btn_ver_favoritas.clicked.connect(self.mostrar_favoritas)
        self.aplicar_estilo_boton(self.btn_ver_favoritas)

        self.btn_volver = QPushButton("🔙 Volver", self)
        self.btn_volver.move(37, 310)
        self.btn_volver.resize(220, 30)
        self.btn_volver.clicked.connect(self.volver_inicio)
        self.btn_volver.setVisible(False)
        self.aplicar_estilo_boton(self.btn_volver)

        # Etiqueta de tiempo real
        self.label_tiempo = QLabel(self)
        self.label_tiempo.setStyleSheet("color: #B8F2E6; font-size: 10px;")
        self.label_tiempo.move(10, 10)  # Esquina superior izquierda
        self.label_tiempo.resize(300, 15)

        # Etiqueta de tiempo estimado
        self.label_tiempo_estimado = QLabel(self)
        self.label_tiempo_estimado.setStyleSheet("color: #B8F2E6; font-size: 10px;")
        self.label_tiempo_estimado.move(10, 30)  # Debajo de la anterior
        self.label_tiempo_estimado.resize(300, 15)

        #Derechos reservados mensaje
        self.derechos_reservados = QLabel(self)
        self.derechos_reservados.setStyleSheet("background-color: transparent; color: white;")
        self.derechos_reservados.setText("© 2025 CineXtreem: Todos los Derechos Reservados")
        self.derechos_reservados.setFont(QFont("Arial", 8))
        self.derechos_reservados.move(220, 470)
        self.derechos_reservados.resize(265, 22)

        # Texto debajo del logo
        self.texto_abajo_del_logo = QLabel(self)
        self.texto_abajo_del_logo.setStyleSheet("background-color: transparent;")
        self.texto_abajo_del_logo.setText("¡La mejor plataforma de streaming!")
        
        # Cargar la fuente manualmente
        ruta_fuente1 = os.path.join(ruta_base, "print_clearly_tt.ttf")
        font_id = QFontDatabase.addApplicationFont(ruta_fuente1)
        
        if font_id != -1:
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            fuente = QFont(font_family, 12)
            fuente.setItalic(False)
            self.texto_abajo_del_logo.setFont(fuente)
        else:
            print("Error al cargar la fuente")
            
        self.texto_abajo_del_logo.move(55, 405)
        self.texto_abajo_del_logo.resize(200, 20)
        self.texto_abajo_del_logo.setStyleSheet("color: #B8F2E6;")

        # Mensaje de acciones
        self.label = QLabel("", self)
        self.label.setStyleSheet("background-color: transparent;")
        self.label.setWordWrap(True)
        self.label.setStyleSheet("color: #B8F2E6;")

        # Cargar la fuente manualmente
        ruta_fuente2= os.path.join(ruta_base, "Gravity-Regular.otf")
        font_id = QFontDatabase.addApplicationFont(ruta_fuente2)
        if font_id != -1:
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            fuente = QFont(font_family, 9)
            fuente.setItalic(False)
            self.label.setFont(fuente)
        else:
            print("Error al cargar la fuente")

        self.label.move(370, 400)
        self.label.resize(240, 30)

    def cargar_peliculas(self):
        peliculas = self.sistema.ver_recomendaciones()
        self.lista_peliculas.clear()
        self.mapping_peliculas.clear()
        for pelicula in peliculas:
            self.mapping_peliculas[pelicula.id_pelicula] = pelicula
            self.lista_peliculas.addItem(f"{pelicula.id_pelicula}. {pelicula.titulo}, Calificación: {pelicula.puntaje}")

    def buscar_pelicula(self):
        texto = self.search_input.text()
        peliculas = self.sistema.buscar_pelicula(texto)
        self.lista_peliculas.clear()
        self.mapping_peliculas.clear()
        for pelicula in peliculas:
            self.mapping_peliculas[pelicula.id_pelicula] = pelicula
            self.lista_peliculas.addItem(f"{pelicula.id_pelicula}. {pelicula.titulo}, Calificación: {pelicula.puntaje}")

    def obtener_pelicula_seleccionada(self):
        item = self.lista_peliculas.currentItem()
        if not item:
            self.label.setText("⚠ Selecciona una película primero.")
            return None
        id_pelicula = int(item.text().split(".")[0])
        return self.mapping_peliculas.get(id_pelicula)

    def ver_pelicula(self):
        pelicula = self.obtener_pelicula_seleccionada()
        if not pelicula:
            return
        estado, mensaje = self.sistema.ver_pelicula(pelicula.id_pelicula)
        self.label.setText(mensaje)

        if estado:
            ventana = VentanaReproduccion(f"{pelicula.titulo} ({pelicula.año})")
            ventana.exec()

    def guardar_ver_mas_tarde(self):
        pelicula = self.obtener_pelicula_seleccionada()
        if not pelicula:
            return
        estado, mensaje = self.sistema.agregar_a_lista(pelicula.id_pelicula)
        self.label.setText(mensaje)

    def marcar_favorita(self):
        pelicula = self.obtener_pelicula_seleccionada()
        if not pelicula:
            return
        estado, mensaje = self.sistema.marcar_como_favorita(pelicula.id_pelicula)
        self.label.setText(mensaje)

    def mostrar_ver_mas_tarde(self):
        estado, lista = self.sistema.ver_mi_lista()
        self.lista_peliculas.clear()
        self.lista_peliculas.addItems(lista if estado else [lista])
        self.label.setText("¡Este es tu listado de peliculas!\U0001FAE1")
        self.btn_volver.setVisible(True)
        self.toggle_botones(False)

    def mostrar_favoritas(self):
        estado, lista = self.sistema.ver_favoritas()
        if not lista:
            lista = ["⚠ No tienes películas favoritas aún."]
        self.lista_peliculas.clear()
        self.lista_peliculas.addItems(lista if estado else [lista])
        self.label.setText("Lista de favoritas mostrada con éxito \U0001F601")
        self.btn_volver.setVisible(True)
        self.toggle_botones(False)

    def volver_inicio(self):
        self.lista_peliculas.clear()
        self.cargar_peliculas()
        self.label.setText("")
        self.btn_volver.setVisible(False)
        self.toggle_botones(True)

    def toggle_botones(self, estado):
        botones = [
            self.btn_ver, self.btn_guardar,
            self.btn_favorita, self.btn_ver_favoritas,
            self.btn_ver_lista
    ]
        for boton in botones:
            boton.setEnabled(estado)
            if estado:
                self.aplicar_estilo_boton(boton)
            else:
                boton.setStyleSheet("""
                    QPushButton {
                        background-color: #555;
                        color: gray;
                        border: 1px solid #444;
                        border-radius: 6px;
                        padding: 6px;
                    }
                """)

    def closeEvent(self, event):
        """Se llama al cerrar la aplicación"""

        if self.sistema.usuario_actual:
            # 1. Registrar la sesión en el objeto usuario_actual
            self.sistema.usuario_actual.registrar_sesion(self.tiempo_transcurrido)

            # 2. Cargar todos los usuarios existentes de la base de datos
            usuarios = Funciones.cargar_usuarios(tipo=self.sistema.tipo_usuarios)

            # 3. Actualizar el historial de sesiones del usuario actual en el diccionario 'usuarios' cargado
            correo_actual = self.sistema.usuario_actual.correo
            if correo_actual in usuarios:
                # Actualiza solo el historial de sesiones del usuario actual
                usuarios[correo_actual]["Tiempo_total_sesion_enSegs"] = getattr(
                    self.sistema.usuario_actual, "Tiempo_total_sesion_enSegs", []
                )
                # Asegurarse de que el 'correo' esté presente en el diccionario del usuario
                # Esto es una medida de seguridad extra, por si el diccionario cargado no lo tuviera
                if 'correo' not in usuarios[correo_actual]:
                    usuarios[correo_actual]['correo'] = correo_actual
            else:
                # Si por alguna razón el usuario actual no está en el diccionario cargado,
                # lo agregamos completamente para evitar problemas al guardar.
                print(f"❌ ADVERTENCIA: Usuario actual '{correo_actual}' no encontrado en el diccionario cargado. Agregándolo...")
                usuarios[correo_actual] = {
                    "nombre": self.sistema.usuario_actual.nombre,
                    "correo": self.sistema.usuario_actual.correo, # Aseguramos que 'correo' esté aquí
                    "contraseña": self.sistema.usuario_actual.contraseña,
                    "tipo": self.sistema.usuario_actual.tipo,
                    "mi_lista": self.sistema.usuario_actual.mi_lista,
                    "favoritas": self.sistema.usuario_actual.favoritas,
                    "Tiempo_total_sesion_enSegs": self.sistema.usuario_actual.Tiempo_total_sesion_enSegs,
                }


            # 4. Iterar sobre todos los usuarios en el diccionario 'usuarios' antes de guardar
            #    para asegurar que cada diccionario individual tenga la clave 'correo'.
            #    Esto es para protegerte de datos inconsistentes de cargas anteriores o registros viejos.
            usuarios_a_guardar = {}
            for email_key, user_data_dict in usuarios.items():
                if 'correo' not in user_data_dict:
                    # Si un diccionario de usuario no tiene 'correo', lo añadimos usando la clave del diccionario principal
                    user_data_dict['correo'] = email_key
                    print(f"DEBUG: Añadiendo 'correo' faltante a {email_key} antes de guardar.")
                usuarios_a_guardar[email_key] = user_data_dict # Reconstruimos el diccionario

            # 5. Guardar el diccionario de usuarios (que ahora está sanitizado)
            try:
                Funciones.guardar_usuarios(usuarios_a_guardar, tipo=self.sistema.tipo_usuarios)
                print("✅ Usuarios guardados al cerrar la interfaz.")
            except Exception as e:
                # Muestra un error crítico si el guardado falla
                print(f"❌ Error al guardar usuarios al cerrar la interfaz: {e}")
                QMessageBox.critical(self, "Error al guardar", f"No se pudieron guardar los datos: {e}")

        # Tus mensajes QMessageBox que quieres mantener (están fuera del 'if usuario_actual' para que siempre se muestren)
        QMessageBox.information(self, "Cierre de sesión", "🎬 ¡Gracias por usar CineXtreem!")
        event.accept() # Acepta el evento de cierre para que la ventana se cierre.

class VentanaReproduccion(QDialog):
    def __init__(self, nombre_pelicula, duracion=120):
        super().__init__()

        self.setWindowTitle("🎬 Reproducción en curso")
        self.setFixedSize(400, 210)
        self.setStyleSheet("background-color: #1e1e1e; color: white;")
        self.setModal(True)

        icon_path = os.path.join(os.path.dirname(__file__), "logaso_9Ri_icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.duracion = duracion
        self.segundo_actual = 0
        self.usando_slider = False
        self.pausado = False

        # -------- Etiqueta de título --------
        self.label = QLabel(f"Estás viendo: {nombre_pelicula}", self)
        self.label.setStyleSheet("color: #B8F2E6; font-size: 14px;")
        self.label.resize(380, 30)
        self.label.move(10, 10)

        # -------- Slider de reproducción --------
        self.slider = QSlider(Qt.Orientation.Horizontal, self)
        self.slider.setRange(0, self.duracion)
        self.slider.setValue(0)
        self.slider.setStyleSheet("""
            QSlider::groove:horizontal {
                background: #444;
                height: 8px;
            }
            QSlider::handle:horizontal {
                background: #B8F2E6;
                border: 1px solid white;
                width: 14px;
                margin: -4px 0;
                border-radius: 7px;
            }
        """)
        self.slider.resize(360, 20)
        self.slider.move(20, 60)

        # -------- Etiqueta del tiempo --------
        self.label_tiempo = QLabel("00:00 / 02:00", self)
        self.label_tiempo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_tiempo.resize(380, 30)
        self.label_tiempo.move(10, 90)

        # -------- Botón Pausar/Reanudar --------
        self.boton_pausa = QPushButton("⏸ Pausar", self)
        self.boton_pausa.resize(120, 40)
        self.boton_pausa.move(140, 140)
        self.boton_pausa.clicked.connect(self.toggle_pausa)

        # -------- Timer que actualiza cada segundo --------
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.avanzar_reproduccion)
        self.timer.start(1000)

        # -------- Conexiones del slider --------
        self.slider.sliderPressed.connect(self.detener_tiempo)
        self.slider.sliderReleased.connect(self.reanudar_tiempo)
        self.slider.valueChanged.connect(self.actualizar_posicion)
        self.slider.mousePressEvent = self.ir_a_posicion_click

    # ---------- MÉTODOS ----------

    def avanzar_reproduccion(self):
        if not self.usando_slider and not self.pausado and self.segundo_actual < self.duracion:
            self.segundo_actual += 1
            self.slider.setValue(self.segundo_actual)
            self.actualizar_tiempo()

        if self.segundo_actual >= self.duracion:
            self.timer.stop()
            self.accept()

    def actualizar_tiempo(self):
        actual = self.formatear_tiempo(self.segundo_actual)
        total = self.formatear_tiempo(self.duracion)
        self.label_tiempo.setText(f"{actual} / {total}")

    def formatear_tiempo(self, segundos):
        minutos = segundos // 60
        segundos = segundos % 60
        return f"{minutos:02}:{segundos:02}"

    def detener_tiempo(self):
        self.usando_slider = True

    def reanudar_tiempo(self):
        self.usando_slider = False

    def actualizar_posicion(self, valor):
        if self.usando_slider:
            self.segundo_actual = valor
            self.actualizar_tiempo()

    def toggle_pausa(self):
        self.pausado = not self.pausado
        self.boton_pausa.setText("▶ Reanudar" if self.pausado else "⏸ Pausar")

    def ir_a_posicion_click(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            slider_width = self.slider.width()
            x = event.position().x()
            nuevo_valor = int((x / slider_width) * self.duracion)
            self.segundo_actual = nuevo_valor
            self.slider.setValue(nuevo_valor)
            self.actualizar_tiempo()
