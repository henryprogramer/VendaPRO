from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout

class VendasWindow(QWidget):
    def __init__(self, user=None):
        super().__init__()
        self.user = user
        layout = QVBoxLayout()
        layout.addWidget(QLabel("🛒 Registro de Vendas"))
        self.setLayout(layout)
