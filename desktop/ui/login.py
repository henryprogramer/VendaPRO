from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt
import sqlite3
from desktop.models import database

class LoginWindow(QWidget):
    def __init__(self, on_login_success=None):
        super().__init__()
        self.on_login_success = on_login_success
        self.setWindowTitle("VendaPRO - Login / Cadastro")
        self.setStyleSheet("background-color: #001c46;")
        self.setFixedSize(400, 400)

        self.mode = "login"
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(30, 30, 30, 30)
        self.layout.setSpacing(15)
        self.setLayout(self.layout)

        # Logo
        self.logo_label = QLabel()
        logo_pix = QPixmap("desktop/assets/img/logo_vendapro.png")
        self.logo_label.setPixmap(logo_pix.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.logo_label)

        # Título
        self.title_label = QLabel()
        self.title_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.title_label.setStyleSheet("color: white;")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title_label)

        # Campo usuário
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Usuário")
        self.user_input.setStyleSheet("background-color: white; color: black; padding: 5px; border-radius: 5px;")
        self.layout.addWidget(self.user_input)

        # Campo senha
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Senha")
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setStyleSheet("background-color: white; color: black; padding: 5px; border-radius: 5px;")
        self.layout.addWidget(self.pass_input)

        # Campo confirmar senha (só aparece no cadastro)
        self.confirm_input = QLineEdit()
        self.confirm_input.setPlaceholderText("Confirme a senha")
        self.confirm_input.setEchoMode(QLineEdit.Password)
        self.confirm_input.setStyleSheet("background-color: white; color: black; padding: 5px; border-radius: 5px;")
        self.layout.addWidget(self.confirm_input)
        self.confirm_input.hide()

        # Botão entrar/cadastrar
        self.btn_submit = QPushButton()
        self.btn_submit.setStyleSheet("""
            QPushButton {
                background-color: #0066cc;
                color: white;
                padding: 8px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #004c99;
            }
        """)
        self.btn_submit.clicked.connect(self.submit)
        
        # Conecta Enter dos campos ao submit
        self.user_input.returnPressed.connect(self.btn_submit.click)
        self.pass_input.returnPressed.connect(self.btn_submit.click)
        self.confirm_input.returnPressed.connect(self.btn_submit.click)

        self.layout.addWidget(self.btn_submit)

        # Alternar login/cadastro
        self.toggle_label = QLabel()
        self.toggle_label.setAlignment(Qt.AlignCenter)
        self.toggle_label.setStyleSheet("color: #66aaff; text-decoration: underline;")
        self.toggle_label.mousePressEvent = self.toggle_mode
        self.layout.addWidget(self.toggle_label)

        self.update_ui()

    def update_ui(self):
        if self.mode == "login":
            self.title_label.setText("Login - VendaPRO")
            self.btn_submit.setText("Entrar")
            self.confirm_input.hide()
            self.toggle_label.setText("Ainda não tem conta? Cadastre-se")
        else:
            self.title_label.setText("Cadastro - VendaPRO")
            self.btn_submit.setText("Cadastrar")
            self.confirm_input.show()
            self.toggle_label.setText("Já tem conta? Faça login")

    def toggle_mode(self, event):
        self.mode = "register" if self.mode == "login" else "login"
        self.update_ui()

    def submit(self):
        username = self.user_input.text().strip()
        password = self.pass_input.text().strip()
        conn = database.get_connection()
        cursor = conn.cursor()

        if self.mode == "login":
            cursor.execute("SELECT * FROM usuario WHERE username=? AND password=?", (username, password))
            user = cursor.fetchone()
            if user:
                # Converte Row para dict
                user_dict = dict(zip([c[0] for c in cursor.description], user))

                if self.on_login_success:
                    self.on_login_success(user_dict)  # passa dicionário em vez de Row
                self.close()
            else:
                QMessageBox.warning(self, "Erro", "Usuário ou senha inválidos!")
        else:
            confirm = self.confirm_input.text().strip()
            if not username or not password:
                QMessageBox.warning(self, "Erro", "Preencha todos os campos!")
                conn.close()
                return
            if password != confirm:
                QMessageBox.warning(self, "Erro", "Senhas não coincidem!")
                conn.close()
                return
            try:
                cursor.execute("INSERT INTO usuario (username, password) VALUES (?, ?)", (username, password))
                conn.commit()
                self.mode = "login"
                self.update_ui()
            except sqlite3.IntegrityError:
                QMessageBox.warning(self, "Erro", "Usuário já existe!")
        conn.close()
