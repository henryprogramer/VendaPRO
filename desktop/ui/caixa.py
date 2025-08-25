from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout

class CaixaWindow(QWidget):
    def __init__(self, user=None):
        super().__init__()
        self.user = user              # dicionário completo
        self.user_id = user["id"] if user else None
        self.username = user["username"] if user else "Admin"

        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"💵 Módulo de Caixa - Usuário ID: {self.user_id}"))
        self.setLayout(layout)
