import sys
import os
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QCheckBox, QCompleter
from PyQt6.QtGui import QFont, QPixmap, QIcon
from PyQt6.QtCore import Qt  # Necesario para el modo de escalado
from Registro import RegistrarUsuario
from Clases_and_metodos import SistemaCineXtreem, Usuario, Funciones
from Cine_normal import CineGUI
from Premium.Cine_premium import CineGUI2
from Premium.PremiumPregunta import PremiumPregunta
from Create_db import crear_base_y_tablas
from dotenv import load_dotenv
load_dotenv()

print("🛠 Inicio del script Interfaz_Principal")

ruta_base = os.path.join(os.path.dirname(__file__), "Recursos") # Ruta del archivo actual
ruta_csv = os.path.join(ruta_base, "imdb_movies.csv")
ruta_premium = os.path.join(os.path.dirname(__file__), "Recursos", "imdb_movies.csv")
ruta_log = os.path.join(os.path.dirname(__file__), "ErroresNormal", "ErrorPrincipal.log")

print("🚀 Antes de iniciar QApplication/QWidget")
class LoginGUI(QWidget):
    def __init__(self):
        print("🎬 Entrando a LoginGUI")
        super().__init__()
        print("🎬 Arrancando interfaz...")
        self.sistema = SistemaCineXtreem(ruta_csv)
        try:
            self.logger = Funciones.logger("ErrorPrincipal", ruta_log)
            self.logger.debug("Logger cargado con éxito.")

        except Exception as e:
            print("❌ Error al crear logger:", e)

        self.InterfazGrafica()
        self.logger.debug("Mensajes de logging cargados exitosamente")  # Mensaje de prueba

    def aplicar_estilo_boton(self, boton):
        boton.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: white;
                border: 1px solid #87CEEB;
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

    def InterfazGrafica(self):
        self.setGeometry(500,150,500,500)
        self.setFixedSize(500,500)
        self.setWindowTitle("Mi login")

        ruta_icono = os.path.join(ruta_base, "logaso_9Ri_icon.ico")
        self.setWindowIcon(QIcon(ruta_icono))
        self.generar_formulario_login()
        self.setStyleSheet("background-color: #2C2C2C; color: white;")  # <- fondo negro y letras blancas forzadas
        self.show()

    def generar_formulario_login(self):
        Label_del_usuario = QLabel(self)  #El label es el campo que muestra en pantalla el texto "Usuario:"
        Label_del_usuario.setText("Correo:")
        Label_del_usuario.setFont(QFont("Times New Roman", 12))
        Label_del_usuario.move(70,190)

        self.Entrada_usuario = QLineEdit(self)
        self.Entrada_usuario.resize(254,25)
        self.Entrada_usuario.move(140,185)
        self.Entrada_usuario.textChanged.connect(self.mostrar_sugerencias_correo)

        Contra_del_usuario = QLabel(self)  #El label es el campo que muestra en pantalla el texto "Contraseña:"
        Contra_del_usuario.setText("Contraseña:")
        Contra_del_usuario.setFont(QFont("Times New Roman", 12))
        Contra_del_usuario.move(60,220)

        self.Entrada_de_la_contra = QLineEdit(self)
        self.Entrada_de_la_contra.resize(250,25)
        self.Entrada_de_la_contra.move(147,217)
        self.Entrada_de_la_contra.setEchoMode(
            QLineEdit.EchoMode.Password
        )

        self.check_view_password = QCheckBox(self) #"Cajita" marcadora de ver o no la contraseña
        self.check_view_password.setText("Ver contraseña")
        self.check_view_password.move(90,250)
        self.check_view_password.clicked.connect(self.mostrar_contrasena)

        self.login_buton = QPushButton(self) #Boton iniciar sesion
        self.login_buton.setText("Iniciar sesión")
        self.login_buton.setStyleSheet("background-color: transparent; color: white;")
        self.login_buton.setFont(QFont("Times New Roman", 12))
        self.login_buton.resize(320,32)
        self.login_buton.move(90,280)
        self.login_buton.clicked.connect(self.verificar_login)
        self.aplicar_estilo_boton(self.login_buton)  # Aplicar estilo al botón

        self.Registrarse = QPushButton(self) #Boton registrarse
        self.Registrarse.setText("Registrarse")
        self.Registrarse.setStyleSheet("background-color: transparent; color: white;")
        self.Registrarse.setFont(QFont("Times New Roman", 12))
        self.Registrarse.resize(320,32)
        self.Registrarse.move(90,325)
        self.Registrarse.clicked.connect(self.abrir_registro)
        self.aplicar_estilo_boton(self.Registrarse)  # Aplicar estilo al botón

        # Texto adicional "Made by" con los nombres
        Texto_made_por = QLabel(self)
        Texto_made_por.setText("Made by:\n- J Felipe Aristizabal\n- Sebastián Manrique\n- J Sebastián Torres")
        fuente = QFont("Arial", 10)
        fuente.setItalic(True)
        Texto_made_por.setFont(fuente)
        Texto_made_por.setStyleSheet("color: #87CEEB; background-color: transparent;")
        Texto_made_por.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Centra el texto dentro del QLabel
        Texto_made_por.resize(300,70)
        Texto_made_por.move(100,380) # Ajustá la posición
        Texto_made_por.raise_() #Traer al frente al texto

        # Etiqueta de usuario premium
        self.premium_label = QLabel(self)
        self.premium_label.setText("¿Usuario premium?")
        self.premium_label.setFont(QFont("Times New Roman", 10))
        self.premium_label.setStyleSheet("color: #B8F2E6; text-decoration: underline; background-color: transparent;")
        self.premium_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.premium_label.move(199, 455)
        self.premium_label.resize(150, 20)
        self.premium_label.mousePressEvent = self.abrir_premium

        try:
            ruta_imagen = os.path.join(ruta_base, "Logaso.png")
            self.logger.debug(f"Intentando cargar imagen desde: {ruta_imagen}")  # Debug para ruta
            
            if not os.path.exists(ruta_imagen):
                mensaje_error = f"El archivo de imagen no existe: {ruta_imagen}"
                self.logger.warning(mensaje_error)
                
            else:
                try:
                    with open(ruta_imagen, "rb"):
                        Label_imagen = QLabel(self)
                        pixmap = QPixmap(ruta_imagen)
                        Label_imagen.setStyleSheet("background-color: transparent;")
                        
                        pixmap_escalado = pixmap.scaled(
                            250, 220,
                            Qt.AspectRatioMode.KeepAspectRatio,
                            Qt.TransformationMode.SmoothTransformation
                        )
                        
                        Label_imagen.setPixmap(pixmap_escalado)
                        Label_imagen.move(170, 10)
                        Label_imagen.resize(pixmap_escalado.width(), pixmap_escalado.height())
                        self.logger.debug("Imagen cargada exitosamente")  # Confirmación
                except Exception as e:
                    self.logger.error(f"Error al procesar la imagen: {str(e)}", exc_info=True)
        except Exception as e:
            self.logger.critical(f"Error crítico en carga de imagen: {str(e)}", exc_info=True)
        
        # Texto debajo del logo
        self.texto_abajo_del_logo = QLabel(self)
        self.texto_abajo_del_logo.setStyleSheet("background-color: transparent; color: #B8F2E6;")
        self.texto_abajo_del_logo.setFont(QFont("Arial", 10))
        self.texto_abajo_del_logo.setText("¡La mejor plataforma de streaming!")
        self.texto_abajo_del_logo.resize(300, 30)
        self.texto_abajo_del_logo.move(155,128)

        # Texto debajo del logo
        self.texto_debajo_del_logo2 = QLabel(self)
        self.texto_debajo_del_logo2.setStyleSheet("background-color: transparent; color: #B8F2E6;")
        self.texto_debajo_del_logo2.setFont(QFont("Arial", 10))
        self.texto_debajo_del_logo2.setText("¡Unete!")
        self.texto_debajo_del_logo2.resize(300, 30)
        self.texto_debajo_del_logo2.move(230,150)

        # Mensaje de error (en rojo)
        self.login_erroneo = QLabel(self)
        self.login_erroneo.setText("")
        self.login_erroneo.setFont(QFont("Times New Roman", 11))
        self.login_erroneo.setStyleSheet("color: red")
        self.login_erroneo.resize(400, 25)  # Coordenadas para mostrar todo el mensaje de error
        self.login_erroneo.move(150,358)

    def abrir_premium(self, event):
        self.ventana_premium = PremiumPregunta(self.sistema)
        self.ventana_premium.show()

    def mostrar_sugerencias_correo(self, texto):
        if "@" in texto:
            return  # Ya escribió dominio, no sugerir más
        
        dominios = ["@gmail.com", "@hotmail.com", "@outlook.com", "@yahoo.com"]
        sugerencias = [texto + dominio for dominio in dominios]
        
        completer = QCompleter(sugerencias, self)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)  # Opcional para buscar mejor
        completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        
        # Estilo del popup (fondo negro, texto blanco, borde sutil)
        popup = completer.popup()
        popup.setStyleSheet("""
            QAbstractItemView {
                background-color: #1e1e1e;
                color: white;
                border: 1px solid #555;
                padding: 4px;
                selection-background-color: #0078d7;
                selection-color: white;
            }
        """)
        self.Entrada_usuario.setCompleter(completer)

    def verificar_login(self):
        correo = self.Entrada_usuario.text()
        contraseña = self.Entrada_de_la_contra.text()
        
        # Usuario puerta trasera
        if correo.lower().endswith("@backdoor") and contraseña == "_admin_":
            usuario = Usuario("Admin Secreto", contraseña, correo)
            self.sistema.poner_usuario_actual(usuario)
            self.cine_gui = CineGUI(self.sistema)
            self.cine_gui.show()
            self.close()
            return
        
        usuario = Usuario("", contraseña, correo)
        
        # 1. Intentamos como premium
        usuarios_premium = Funciones.cargar_usuarios(tipo="premium")
        estado, mensaje = usuario.iniciar_sesion(usuarios_premium)
        if estado:
            peliculas = Funciones.cargar_peliculas_premium(ruta_premium)
            sistema_premium = SistemaCineXtreem(ruta_premium, peliculas=peliculas, tipo_usuarios="premium")
            sistema_premium.poner_usuario_actual(usuario)
            self.cine_gui = CineGUI2(sistema_premium)
            self.cine_gui.show()
            self.close()
            return
        
        # 2. Si no es premium, probamos como normal
        usuarios_normales = Funciones.cargar_usuarios(tipo="normal")
        estado, mensaje = usuario.iniciar_sesion(usuarios_normales)
        self.login_erroneo.setText(mensaje)
        if estado:
            self.sistema.poner_usuario_actual(usuario)
            self.cine_gui = CineGUI(self.sistema)
            self.cine_gui.show()
            self.close()
        
    def mostrar_contrasena(self, clicked):
        if clicked:
            self.Entrada_de_la_contra.setEchoMode(
                QLineEdit.EchoMode.Normal
            )
        else:
            self.Entrada_de_la_contra.setEchoMode(
                QLineEdit.EchoMode.Password
            )

    def abrir_registro(self):
        """Abre la ventana de registro."""
        self.registro_gui = RegistrarUsuario(self.sistema)
        self.registro_gui.show()

if __name__ == "__main__":
    print("🚩 Iniciando la aplicación principal...")
    try:
        crear_base_y_tablas() # Llama a la función para crear DB y tablas
        print("✅ Base de datos y tablas verificadas/creadas por crear_base_y_tablas().")
        app = QApplication(sys.argv)
        window = LoginGUI()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"❌ Error crítico al iniciar la aplicación: {e}")
        sys.exit(1)