from PyQt6.QtWidgets import QPushButton, QLabel, QDialog
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from Premium.RegistroPremium import RegistrarUsuario

class PremiumPregunta(QDialog):
    def __init__(self, sistema):
        super().__init__()
        self.sistema = sistema
        self.setModal(True)
        self.initUI()

    def initUI(self):
        self.setGeometry(500, 150, 400, 200)
        self.setFixedSize(400, 200)
        self.setWindowTitle("Registro de Usuario Premium")
        self.setStyleSheet("background-color: #2C2C2C; color: #B8F2E6;")

        label = QLabel("¿Deseas registrarte como usuario premium?", self)
        label.setFont(QFont("Times New Roman", 12))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.resize(380, 50)
        label.move(10, 30)

        btn_registrar = QPushButton("Sí, registrarme \U0001F60E", self)
        btn_registrar.setFont(QFont("Times New Roman", 11))
        btn_registrar.resize(150, 32)
        btn_registrar.move(50, 100)
        btn_registrar.clicked.connect(self.abrir_registro_premium)

        btn_cancelar = QPushButton("Cancelar \U0001FAE4", self)
        btn_cancelar.setFont(QFont("Times New Roman", 11))
        btn_cancelar.resize(150, 32)
        btn_cancelar.move(200, 100)
        btn_cancelar.clicked.connect(self.close)
        
    def abrir_registro_premium(self):
        self.registro = RegistrarUsuario(self.sistema, tipo="premium")
        self.registro.show()
        self.close()


