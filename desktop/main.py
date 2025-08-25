import sys
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QSizePolicy, QFrame
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon

# Imports das janelas
from models import database
from ui.login import LoginWindow
from ui.painel import PainelWindow
from ui.caixa import CaixaWindow
from ui.clientes import ClientesWindow
from ui.produtos import ProdutosWindow
from ui.estoque import EstoqueWindow
from ui.fornecedores import FornecedoresWindow
from ui.vendas import VendasWindow
from ui.biblioteca import BibliotecaWindow

class MainWindow(QMainWindow):
    def __init__(self, user=None):
        super().__init__()
        self.user = user  # dicionário do login
        
        self.setWindowIcon(QIcon(QPixmap("desktop/assets/img/logo_vendapro.png")))
        self.setWindowTitle("VendaPRO - Desktop")
        self.setGeometry(100, 100, 1400, 800)

        # Dicionário de janelas (para navegação)
        self.pages = {}

        # Layout principal
        central_widget = QWidget()
        central_layout = QVBoxLayout()
        central_widget.setLayout(central_layout)
        self.setCentralWidget(central_widget)

        # ========== CABEÇALHO ==========
        header = QFrame()
        header.setFrameShape(QFrame.StyledPanel)
        header.setFixedHeight(60)
        header.setStyleSheet("background-color: #001c46; color: white;")
        header_layout = QHBoxLayout()
        header.setLayout(header_layout)

        # Botão ativar/desativar menu
        self.btn_toggle_menu = QPushButton("☰")
        self.btn_toggle_menu.setFixedSize(40, 40)
        self.btn_toggle_menu.setStyleSheet("background-color: white; color: #001c46;")
        self.btn_toggle_menu.clicked.connect(self.toggle_menu)
        header_layout.addWidget(self.btn_toggle_menu, alignment=Qt.AlignLeft)

        # Logo e nome do sistema
        logo_label = QLabel()
        logo_pix = QPixmap("desktop/assets/img/logo_vendapro.png")
        logo_pix = logo_pix.scaled(QSize(40, 40), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(logo_pix)
        system_name = QLabel("VendaPRO")
        system_name.setStyleSheet("font-size: 20px; font-weight: bold;")
        logo_layout = QHBoxLayout()
        logo_layout.addWidget(logo_label)
        logo_layout.addWidget(system_name)
        logo_layout.addStretch()
        logo_container = QWidget()
        logo_container.setLayout(logo_layout)
        header_layout.addWidget(logo_container, alignment=Qt.AlignCenter)

        # Perfil do usuário
        self.perfil_label = QLabel(f"Usuário: {self.user['username'] if self.user else 'Admin'}")
        header_layout.addWidget(self.perfil_label, alignment=Qt.AlignRight)

        # ========== CORPO ==========
        body = QHBoxLayout()

        # --- MENU LATERAL ---
        self.menu_widget = QFrame()
        self.menu_widget.setFrameShape(QFrame.StyledPanel)
        self.menu_widget.setFixedWidth(300)
        self.menu_widget.setStyleSheet("background-color: white;")
        menu_layout = QVBoxLayout()
        self.menu_widget.setLayout(menu_layout)

        # Botões do menu com ícones
        menu_items = [
            ("PAINEL", "desktop/assets/img/icon_dashboard.png"),
            ("CAIXA", "desktop/assets/img/icon_caixa.png"),
            ("CLIENTES", "desktop/assets/img/icon_clientes.png"),
            ("PRODUTOS", "desktop/assets/img/icon_produtos.png"),
            ("ESTOQUE", "desktop/assets/img/icon_estoque.png"),
            ("FORNECEDORES", "desktop/assets/img/icon_fornecedores.png"),
            ("VENDAS", "desktop/assets/img/icon_vendas.png"),
            ("DELIVERY", ""),  # placeholder
            ("BIBLIOTECA", "desktop/assets/img/icon_biblioteca.png")
        ]

        self.menu_buttons = {}
        for name, icon_path in menu_items:
            btn = QPushButton(name)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: white;
                    color: #001c46;
                    text-align: left;
                    font-weight: bold;
                    padding: 2px;
                    font-size: 20px;
                }
                QPushButton:hover {
                    background-color: #e6e6e6;
                }
            """)
            if icon_path:
                btn.setIcon(QIcon(icon_path))
                btn.setIconSize(QSize(90, 90))
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            menu_layout.addWidget(btn)
            self.menu_buttons[name] = btn
        menu_layout.addStretch()

        # --- CONTEÚDO PRINCIPAL ---
        self.content_widget = QStackedWidget()

        # Tela inicial com imagem de fundo
        self.inicio_widget = QWidget()
        inicio_layout = QVBoxLayout()
        self.inicio_widget.setLayout(inicio_layout)

        fundo_label = QLabel()
        fundo_pix = QPixmap("desktop/assets/img/img_fundo_inicio.png")
        fundo_pix = fundo_pix.scaled(800, 600, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        fundo_label.setPixmap(fundo_pix)
        fundo_label.setAlignment(Qt.AlignCenter)

        inicio_layout.addWidget(fundo_label)
        self.content_widget.addWidget(self.inicio_widget)

        # --- REGISTRO DAS PÁGINAS ---
        self.pages["PAINEL"] = PainelWindow(user=self.user)
        self.pages["CAIXA"] = CaixaWindow(user=self.user)
        self.pages["CLIENTES"] = ClientesWindow(user=self.user)
        self.pages["PRODUTOS"] = ProdutosWindow(user=self.user)
        self.pages["ESTOQUE"] = EstoqueWindow(user=self.user)
        self.pages["FORNECEDORES"] = FornecedoresWindow(user=self.user)
        self.pages["VENDAS"] = VendasWindow(user=self.user)
        self.pages["BIBLIOTECA"] = BibliotecaWindow(user=self.user)
        self.pages["DELIVERY"] = QLabel("🚚 Módulo Delivery em construção...")

        for page in self.pages.values():
            self.content_widget.addWidget(page)

        # --- APARTE LATERAL (DIREITA) ---
        aside = QFrame()
        aside.setFrameShape(QFrame.StyledPanel)
        aside.setFixedWidth(200)
        aside.setStyleSheet("background-color: #001c46; color: white;")
        aside_layout = QVBoxLayout()
        aside.setLayout(aside_layout)

        lbl_social = QLabel("Redes Sociais")
        aside_layout.addWidget(lbl_social)
        for name in ["Instagram", "Facebook", "WhatsApp"]:
            btn = QPushButton(name)
            btn.setStyleSheet("background-color: white; color: #001c46; font-weight: bold;")
            btn.clicked.connect(lambda checked, n=name: self.show_social(n))
            aside_layout.addWidget(btn)
        aside_layout.addStretch()

        # Adiciona widgets ao body
        body.addWidget(self.menu_widget)
        body.addWidget(self.content_widget, stretch=1)
        body.addWidget(aside)

        # ========== RODAPÉ ==========
        footer = QFrame()
        footer.setFrameShape(QFrame.StyledPanel)
        footer.setFixedHeight(30)
        footer.setStyleSheet("background-color: #001c46; font-weight: bold; color: white;")
        footer_layout = QHBoxLayout()
        footer.setLayout(footer_layout)
        footer_label = QLabel("© 2025 VendaPRO. Todos os direitos reservados.")
        footer_layout.addWidget(footer_label, alignment=Qt.AlignCenter)

        # Monta layout central
        central_layout.addWidget(header)
        central_layout.addLayout(body)
        central_layout.addWidget(footer)

        # Conecta botões do menu
        for name in self.menu_buttons:
            self.menu_buttons[name].clicked.connect(lambda checked, n=name: self.mudar_area(n))

    # Alterna visibilidade do menu lateral
    def toggle_menu(self):
        self.menu_widget.setVisible(not self.menu_widget.isVisible())

    # Troca conteúdo principal
    def mudar_area(self, nome):
        if nome in self.pages:
            self.content_widget.setCurrentWidget(self.pages[nome])
        else:
            self.content_widget.setCurrentWidget(self.inicio_widget)

    # Exibe alerta ou info para redes sociais
    def show_social(self, name):
        print(f"Abrindo rede social: {name}")


if __name__ == "__main__":
    database.init_db()  # inicializa o banco
    app = QApplication(sys.argv)
    
    def open_main_window(user):
        main_window = MainWindow(user=user)
        main_window.show()

    login = LoginWindow(on_login_success=open_main_window)
    login.show()
    
    sys.exit(app.exec_())