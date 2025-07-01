from PyQt6.QtWidgets import (QDialog, QLabel,
QPushButton, QLineEdit)

from PyQt6.QtGui import QFont, QIcon, QPixmap
from Clases_and_metodos import Usuario, Funciones
from PyQt6.QtCore import Qt  # Necesario para el modo de escalado
import os

ruta_recursos = os.path.join(os.path.dirname(__file__), "Recursos") # Ruta del archivo
ruta_log = os.path.join(os.path.dirname(__file__), "ErroresNormal", "ErrorRegistro.log")

class RegistrarUsuario(QDialog):
    def __init__(self, sistema, tipo="normal"):
        super().__init__()
        self.sistema = sistema
        self.tipo = tipo
        self.logger = Funciones.logger("ErrorRegistro", ruta_log)
        self.setModal(True)
        self.generar_formulario()
        self.logger.debug("Mensajes de logging cargados")  # Mensaje de prueba

    def generar_formulario(self):
        self.setGeometry(500,150,500,500)
        self.setFixedSize(500,500)
        self.setWindowTitle("Ventana de Registro")

        icon_path = os.path.join(ruta_recursos, "logaso_9Ri_icon.ico")
        self.setWindowIcon(QIcon(icon_path))
        self.setStyleSheet("background-color: #2C2C2C; color: white;")  # <- fondo negro y letras blancas forzadas

        Label_de_usuario = QLabel(self) #Mostrar "usuario"
        Label_de_usuario.setText("Usuario:") 
        Label_de_usuario.setFont(QFont("Times New Roman", 12))
        Label_de_usuario.move(67,155)

        self.entrada_usuario = QLineEdit(self) #Cajita de texto
        self.entrada_usuario.resize(282,25)
        self.entrada_usuario.move(140,152)

        Label_de_correo = QLabel(self) #Mostrar "Correo"
        Label_de_correo.setText("Correo:")
        Label_de_correo.setFont(QFont("Times New Roman", 12))
        Label_de_correo.move(70,187)

        self.entrada_correo = QLineEdit(self) #Cajita de texto
        self.entrada_correo.resize(282,25)
        self.entrada_correo.move(140,184)

        Label_de_contraseña1 = QLabel(self) #Mostrar "contraseña"
        Label_de_contraseña1.setText("Contraseña:")
        Label_de_contraseña1.setFont(QFont("Times New Roman", 12))
        Label_de_contraseña1.move(60,220)

        self.entrada_contraseña1 = QLineEdit(self) #Cajita de texto de la contraseña
        self.entrada_contraseña1.resize(276,25)
        self.entrada_contraseña1.move(145,217)
        self.entrada_contraseña1.setEchoMode(
            QLineEdit.EchoMode.Password
        )

        Label_de_contraseña2 = QLabel(self) #Mostrar "Confirmar contraseña"
        Label_de_contraseña2.setText("Confirmar contraseña:")
        Label_de_contraseña2.setFont(QFont("Times New Roman", 12))
        Label_de_contraseña2.move(22,253)

        self.entrada_contraseña2 = QLineEdit(self) #Cajita de texto de la confirmación
        self.entrada_contraseña2.resize(250,25)
        self.entrada_contraseña2.move(170,250)
        self.entrada_contraseña2.setEchoMode(
            QLineEdit.EchoMode.Password
        )

        btn_registrar = QPushButton(self) #Boton clickeable para crear la cuenta con lo anterior preguntado
        btn_registrar.setText("Crear cuenta")
        btn_registrar.setFont(QFont("Times New Roman", 12))
        btn_registrar.resize(150,30)
        btn_registrar.move(170,300)
        btn_registrar.clicked.connect(self.registrar_usuario)

        btn_cancelar_registro = QPushButton(self) #Boton para cancelar la operación
        btn_cancelar_registro.setText("Cancelar")
        btn_cancelar_registro.setFont(QFont("Times New Roman", 12))
        btn_cancelar_registro.resize(150,30)
        btn_cancelar_registro.move(170,340)
        btn_cancelar_registro.clicked.connect(self.cancelar_registro)

        #frase motivadora pa q se registren
        Texto_motivador = QLabel(self)
        Texto_motivador.setText("Empieza ahora. Tu próxima gran experiencia está a un clic. \U0001F4AF")
        fuente_motivadora = QFont("Times New Roman", 10)
        fuente_motivadora.setItalic(True)
        Texto_motivador.setFont(fuente_motivadora)
        Texto_motivador.setStyleSheet("color: #87CEEB; background-color: transparent;")
        Texto_motivador.setAlignment(Qt.AlignmentFlag.AlignCenter)
        Texto_motivador.resize(400, 40)  # Ajustá el ancho según la ventana
        Texto_motivador.move(50, 385)   # Ajustá la posición según el diseño de la interfaz

        # Mensaje de error del login (en rojo)
        self.login_erroneo = QLabel(self)
        self.login_erroneo.setText("")
        self.login_erroneo.setFont(QFont("Times New Roman", 10))
        self.login_erroneo.setStyleSheet("color: red")
        self.login_erroneo.resize(400, 30)  # Agrandar el tamaño para mostrar todo el mensaje
        self.login_erroneo.move(90,275)

        try:
            ruta_imagen = os.path.join(ruta_recursos, "Logaso.png")
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

    #Acá en registrar_usuario no pusimos logging.
    #--------------------------------------------
    #Esto porque queremos que el usuario se de cuenta de que le faltan rellenar campos.
    #------------------------------------------------------------------------------------
    #Si se pone logging, el usuario no ve el error y no sabe que le falta rellenar campos.

    def registrar_usuario(self):
        correo = self.entrada_correo.text()
        nombre = self.entrada_usuario.text()
        contraseña1 = self.entrada_contraseña1.text()
        contraseña2 = self.entrada_contraseña2.text()
        
        if not correo or not nombre or not contraseña1 or not contraseña2:
            self.login_erroneo.setText("Todos los campos son obligatorios.")
            return
        
        if contraseña1 != contraseña2:
            self.login_erroneo.setText("Las contraseñas no coinciden.")
            return
        
        usuario = Usuario(nombre, contraseña1, correo)
        
        try:
            # cargar usuarios según el tipo
            usuarios = Funciones.cargar_usuarios(tipo=self.tipo)
            
            estado, mensaje = usuario.registrar_usuario(usuarios, tipo=self.tipo)
            
            # guardar usuarios según el tipo
            if estado:
                Funciones.guardar_usuarios(usuarios, tipo=self.tipo)
        except Exception as e:
            self.login_erroneo.setText(f"Error interno del programa: {e}")
            return
        self.login_erroneo.setText(mensaje)
        if estado:
            self.close()

    def cancelar_registro(self):
        self.close()



