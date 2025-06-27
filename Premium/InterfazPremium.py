from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QListWidget, QLineEdit, QMessageBox
from PyQt6.QtGui import QPixmap, QIcon, QFont, QFontDatabase
from PyQt6.QtCore import Qt, QTimer, QTime
import os
from Interfaz_Cine import VentanaReproduccion
from Clases_and_metodos import Funciones

# Obtener la ruta del archivo de fuente
ruta_base = os.path.join(os.path.dirname(__file__), "Recursos")

class CineGUI2(QWidget):
    def __init__(self, sistema):
        super().__init__()
        self.sistema = sistema
        self.tiempo_inicio = QTime.currentTime()  # Guarda el momento de inicio
        self.tiempo_transcurrido = 0  # En segundos
        self.tiempo_estimado = self.calcular_tiempo_estimado()
        self.mapping_peliculas = {}
        self.InitUI2()
        self.iniciar_contador()

    def calcular_tiempo_estimado(self):
        """Calcula el tiempo estimado basado en el historial"""
        if not self.sistema.usuario_actual or not hasattr(self.sistema.usuario_actual, "historial_sesiones"):
            return 60 * 15  # 15 minutos por defecto si no hay historial
        
        if not self.sistema.usuario_actual.historial_sesiones:
            return 60 * 15
        
        # Calcula el promedio de las últimas 5 sesiones
        ultimas_sesiones = self.sistema.usuario_actual.historial_sesiones[-5:]
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
                border: 1px solid #B8F2E6;
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

    def InitUI2(self):
        self.setWindowTitle("Interfaz Cine Premium🎬")
        icon_path = os.path.join(ruta_base, "logaso_9Ri_icon.ico")
        self.setWindowIcon(QIcon(icon_path))
        self.setStyleSheet("background-color: #2C2C2C;")
        self.setFixedSize(685, 500)  # Tamaño fijo para diseño manual

        # Buscar película (entrada)
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Buscar película...")
        self.search_input.move(300, 45)
        self.search_input.resize(250, 30)
        self.search_input.textChanged.connect(self.buscar_pelicula)

        # Lista de películas (a la derecha)
        self.lista_peliculas = QListWidget(self)
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
        self.label_bienvenida.move(35, 43)
        self.label_bienvenida.resize(300, 30)

        # Botones a la izquierda
        self.btn_ver = QPushButton("🎬 Ver película", self)
        self.btn_ver.move(37, 100)
        self.btn_ver.resize(220, 30)
        self.btn_ver.clicked.connect(self.ver_pelicula)
        self.aplicar_estilo_boton(self.btn_ver)

        self.btn_guardar = QPushButton("📌 Ver más tarde", self)
        self.btn_guardar.move(37, 140)
        self.btn_guardar.resize(220, 30)
        self.btn_guardar.clicked.connect(self.guardar_ver_mas_tarde)
        self.aplicar_estilo_boton(self.btn_guardar)

        self.btn_favorita = QPushButton("💖 Tus Favoritas", self)
        self.btn_favorita.move(37, 180)
        self.btn_favorita.resize(220, 30)
        self.btn_favorita.clicked.connect(self.marcar_favorita)
        self.aplicar_estilo_boton(self.btn_favorita)

        self.btn_ver_lista = QPushButton("📜 Listado de 'Ver Mas tarde' ", self)
        self.btn_ver_lista.move(37, 220)
        self.btn_ver_lista.resize(220, 30)
        self.btn_ver_lista.clicked.connect(self.mostrar_ver_mas_tarde)
        self.aplicar_estilo_boton(self.btn_ver_lista)

        self.btn_ver_favoritas = QPushButton("🌟 Listado de favoritas", self)
        self.btn_ver_favoritas.move(37, 260)
        self.btn_ver_favoritas.resize(220, 30)
        self.btn_ver_favoritas.clicked.connect(self.mostrar_favoritas)
        self.aplicar_estilo_boton(self.btn_ver_favoritas)

        self.btn_volver = QPushButton("🔙 Volver", self)
        self.btn_volver.move(37, 300)
        self.btn_volver.resize(220, 30)
        self.btn_volver.clicked.connect(self.volver_inicio)
        self.btn_volver.setVisible(False)
        self.aplicar_estilo_boton(self.btn_volver)

        # Etiqueta de tiempo real
        self.label_tiempo = QLabel(self)
        self.label_tiempo.setStyleSheet("color: #B8F2E6; font-size: 10px;")
        self.label_tiempo.move(10, 10)  # Esquina superior izquierda
        self.label_tiempo.resize(300, 20)

        # Etiqueta de tiempo estimado
        self.label_tiempo_estimado = QLabel(self)
        self.label_tiempo_estimado.setStyleSheet("color: #B8F2E6; font-size: 10px;")
        self.label_tiempo_estimado.move(10, 30)  # Debajo de la anterior
        self.label_tiempo_estimado.resize(300, 20)

        #Derechos reservados mensaje
        self.derechos_reservados = QLabel(self)
        self.derechos_reservados.setStyleSheet("background-color: transparent; color: white;")
        self.derechos_reservados.setText("© 2025 CineXtreem: Todos los Derechos Reservados")
        self.derechos_reservados.setFont(QFont("Arial", 8))
        self.derechos_reservados.move(220, 470)
        self.derechos_reservados.resize(265, 22)

        # Texto debajo del logo
        self.texto_abajo_del_logo = QLabel(self)
        self.texto_abajo_del_logo.setStyleSheet("background-color: transparent; color: #B8F2E6;")
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
        for pelicula in peliculas[:100]:
            self.mapping_peliculas[pelicula.id_pelicula] = pelicula
            self.lista_peliculas.addItem(
                f"{pelicula.id_pelicula}. {pelicula.titulo}, Calificación: {pelicula.puntaje}"
            )

    def buscar_pelicula(self):
        texto = self.search_input.text()
        peliculas = self.sistema.buscar_pelicula(texto)
        self.lista_peliculas.clear()
        self.mapping_peliculas.clear()

        for pelicula in peliculas[:100]:
            self.mapping_peliculas[pelicula.id_pelicula] = pelicula
            self.lista_peliculas.addItem(
                f"{pelicula.id_pelicula}. {pelicula.titulo}, Calificación: {pelicula.puntaje}"
            )
            if len(peliculas) > 100:
                self.label.setText("Mostrando solo los primeros 100 resultados.")
            else:
                self.label.setText("")

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
            self.sistema.usuario_actual.registrar_sesion(self.tiempo_transcurrido)
            
            usuarios = Funciones.cargar_usuarios(tipo=self.sistema.tipo_usuarios)
            
            if self.sistema.usuario_actual.correo in usuarios:
                usuarios[self.sistema.usuario_actual.correo]["historial_sesiones"] = getattr(
                    self.sistema.usuario_actual, "historial_sesiones", []
                )
                Funciones.guardar_usuarios(usuarios, tipo=self.sistema.tipo_usuarios)
        QMessageBox.information(self, "Cierre de sesión", "🎬 ¡Gracias por usar CineXtreem!")
        event.accept()