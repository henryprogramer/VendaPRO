# desktop/main.py
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QSizePolicy, QFrame
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VendaPRO - Desktop")
        self.setGeometry(100, 100, 1400, 800)

        # Layout principal
        central_widget = QWidget()
        central_layout = QVBoxLayout()
        central_widget.setLayout(central_layout)
        self.setCentralWidget(central_widget)

        # ========== CABEÇALHO ==========
        header = QFrame()
        header.setFrameShape(QFrame.StyledPanel)
        header.setFixedHeight(60)
        header.setStyleSheet("background-color: #052c93; color: white;")
        header_layout = QHBoxLayout()
        header.setLayout(header_layout)

        # Botão ativar/desativar menu
        self.btn_toggle_menu = QPushButton("☰")
        self.btn_toggle_menu.setFixedSize(40, 40)
        self.btn_toggle_menu.clicked.connect(self.toggle_menu)
        header_layout.addWidget(self.btn_toggle_menu, alignment=Qt.AlignLeft)

        # Logo e nome do sistema
        logo_label = QLabel()
        logo_pix = QPixmap("desktop/assets/icons/logo.png")  # coloque seu logo aqui
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
        perfil_label = QLabel("Usuário: Admin")
        header_layout.addWidget(perfil_label, alignment=Qt.AlignRight)

        # ========== CORPO ==========
        body = QHBoxLayout()

        # --- MENU LATERAL ---
        self.menu_widget = QFrame()
        self.menu_widget.setFrameShape(QFrame.StyledPanel)
        self.menu_widget.setFixedWidth(200)
        self.menu_widget.setStyleSheet("background-color: #052c93; color: white;")
        menu_layout = QVBoxLayout()
        self.menu_widget.setLayout(menu_layout)

        self.btn_dashboard = QPushButton("Dashboard")
        self.btn_caixa = QPushButton("Caixa")
        self.btn_clientes = QPushButton("Clientes")
        self.btn_produtos = QPushButton("Produtos")
        self.btn_estoque = QPushButton("Estoque")
        self.btn_fornecedores = QPushButton("Fornecedores")
        self.btn_vendas = QPushButton("Vendas")
        self.btn_delivery = QPushButton("Delivery")
        self.btn_arquivos = QPushButton("Arquivos")

        for btn in [self.btn_dashboard, self.btn_caixa, self.btn_clientes, self.btn_produtos,
                    self.btn_estoque, self.btn_fornecedores, self.btn_vendas, self.btn_delivery,
                    self.btn_arquivos]:
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            menu_layout.addWidget(btn)
        menu_layout.addStretch()

        # --- CONTEÚDO PRINCIPAL ---
        self.content_widget = QStackedWidget()
        self.content_widget.addWidget(QLabel("Bem-vindo ao VendaPRO"))  # Tela inicial placeholder

        # --- APARTE LATERAL (DIREITA) ---
        aside = QFrame()
        aside.setFrameShape(QFrame.StyledPanel)
        aside.setFixedWidth(200)
        aside.setStyleSheet("background-color: #052c93; color: white;")
        aside_layout = QVBoxLayout()
        aside.setLayout(aside_layout)

        lbl_social = QLabel("Redes Sociais")
        aside_layout.addWidget(lbl_social)
        for name in ["Instagram", "Facebook", "WhatsApp"]:
            btn = QPushButton(name)
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
        footer.setStyleSheet("background-color: #052c93; color: white;")
        footer_layout = QHBoxLayout()
        footer.setLayout(footer_layout)
        footer_label = QLabel("© 2025 VendaPRO. Todos os direitos reservados.")
        footer_layout.addWidget(footer_label, alignment=Qt.AlignCenter)

        # Monta layout central
        central_layout.addWidget(header)
        central_layout.addLayout(body)
        central_layout.addWidget(footer)

        # Conecta botões do menu
        self.btn_dashboard.clicked.connect(lambda: self.mudar_area("Dashboard"))
        self.btn_caixa.clicked.connect(lambda: self.mudar_area("Caixa"))
        self.btn_clientes.clicked.connect(lambda: self.mudar_area("Clientes"))
        self.btn_produtos.clicked.connect(lambda: self.mudar_area("Produtos"))
        self.btn_estoque.clicked.connect(lambda: self.mudar_area("Estoque"))
        self.btn_fornecedores.clicked.connect(lambda: self.mudar_area("Fornecedores"))
        self.btn_vendas.clicked.connect(lambda: self.mudar_area("Vendas"))
        self.btn_delivery.clicked.connect(lambda: self.mudar_area("Delivery"))
        self.btn_arquivos.clicked.connect(lambda: self.mudar_area("Arquivos"))

    # Alterna visibilidade do menu lateral
    def toggle_menu(self):
        if self.menu_widget.isVisible():
            self.menu_widget.hide()
        else:
            self.menu_widget.show()

    # Troca conteúdo principal
    def mudar_area(self, nome):
        self.content_widget.addWidget(QLabel(f"Tela: {nome}"))
        self.content_widget.setCurrentIndex(self.content_widget.count() - 1)

    # Mostra conteúdo de redes sociais no conteúdo principal
    def show_social(self, rede):
        self.content_widget.addWidget(QLabel(f"Conteúdo de {rede}"))
        self.content_widget.setCurrentIndex(self.content_widget.count() - 1)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
