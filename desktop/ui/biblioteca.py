from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from desktop.models import database

class BibliotecaWindow(QWidget):
    def __init__(self, user=None):
        super().__init__()
        self.user = user
        layout = QVBoxLayout()
        layout.addWidget(QLabel("📚 Biblioteca de Recursos"))
        self.setLayout(layout)
