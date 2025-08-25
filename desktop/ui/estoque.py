from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout

class EstoqueWindow(QWidget):
    def __init__(self, user=None):
        super().__init__()
        self.user = user

        layout = QVBoxLayout()
        layout.addWidget(QLabel("📂 Controle de Estoque"))
        self.setLayout(layout)