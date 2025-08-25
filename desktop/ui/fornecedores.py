from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout

class FornecedoresWindow(QWidget):
    def __init__(self, user=None):
        super().__init__()
        self.user = user

        layout = QVBoxLayout()
        layout.addWidget(QLabel("🚚 Gestão de Fornecedores"))
        self.setLayout(layout)
