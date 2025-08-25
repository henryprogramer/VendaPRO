# desktop/ui/painel.py
from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QGridLayout,
    QFrame, QSizePolicy, QTableWidget, QTableWidgetItem,
    QHeaderView, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QColor


class ExpandableCard(QFrame):
    expanded_card = None  # controla qual card está expandido

    def __init__(self, title, content_widget=None, color="#2E86C1"):
        super().__init__()
        self.title = title
        self.color = color
        self.is_expanded = False
        self.default_height = 140
        self.expanded_height = 300  # agora expande mais

        self.setFrameShape(QFrame.StyledPanel)
        self.set_default_style()

        # sombra
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(shadow)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(5)

        # cabeçalho clicável
        self.header = QLabel(title)
        self.header.setStyleSheet(f"color: {self.color}; font-size: 18px; font-weight: bold;")
        self.header.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.header)

        # conteúdo
        self.content_area = QWidget()
        self.content_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.content_layout = QVBoxLayout(self.content_area)
        if content_widget:
            self.content_layout.addWidget(content_widget)
        self.main_layout.addWidget(self.content_area)
        self.content_area.setVisible(False)

        # animação de altura
        self.animation = QPropertyAnimation(self, b"maximumHeight")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.InOutCubic)

        # clique
        self.header.mousePressEvent = self.toggle

    def set_default_style(self):
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 10px;
                border: 2px solid {self.color};
            }}
            QLabel {{
                font-size: 16px;
            }}
        """)

    def set_expanded_style(self):
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {self.color};
                border-radius: 10px;
                border: 2px solid {self.color};
            }}
            QLabel {{
                font-size: 16px;
                color: white;
            }}
        """)

    def toggle(self, event):
        parent = self.parentWidget()

        if ExpandableCard.expanded_card and ExpandableCard.expanded_card != self:
            ExpandableCard.expanded_card.collapse()

        if self.is_expanded:
            self.collapse()
            ExpandableCard.expanded_card = None
        else:
            self.expand()
            ExpandableCard.expanded_card = self

        if parent:
            parent.updateLayout()

    def expand(self):
        self.is_expanded = True
        self.content_area.setVisible(True)
        self.set_expanded_style()
        self.animate_height(self.expanded_height)

    def collapse(self):
        self.is_expanded = False
        self.content_area.setVisible(False)
        self.set_default_style()
        self.animate_height(self.default_height)

    def animate_height(self, target_height):
        self.animation.stop()
        self.animation.setStartValue(self.height())
        self.animation.setEndValue(target_height)
        self.animation.start()


class PainelWindow(QWidget):
    def __init__(self, user=None):
        super().__init__()
        self.user = user

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # grid para cards do topo
        self.grid = QGridLayout()
        self.grid.setSpacing(15)

        # exemplo de tabelas dentro dos cards
        vendas_table = self.create_table(["ID", "Cliente", "Valor"], [
            ["1", "João", "R$ 120,00"],
            ["2", "Maria", "R$ 350,00"],
            ["3", "Pedro", "R$ 99,90"],
            ["4", "Ana", "R$ 500,00"],
        ])

        clientes_table = self.create_table(["ID", "Nome", "Status"], [
            ["1", "João", "Ativo"],
            ["2", "Maria", "Inativo"],
            ["3", "Carlos", "Ativo"],
        ])

        estoque_table = self.create_table(["Produto", "Qtd", "Estoque Mínimo"], [
            ["Mouse", "50", "10"],
            ["Teclado", "20", "5"],
            ["Monitor", "8", "2"],
        ])

        financeiro_table = self.create_table(["Mês", "Receita", "Despesa"], [
            ["Agosto", "R$ 5.000", "R$ 2.500"],
            ["Setembro", "R$ 7.200", "R$ 3.100"],
            ["Outubro", "R$ 6.800", "R$ 3.400"],
        ])

        # cards principais
        self.cards = [
            ExpandableCard("📊 Vendas Recentes", vendas_table, "#2E86C1"),
            ExpandableCard("👥 Clientes", clientes_table, "#28B463"),
            ExpandableCard("📦 Estoque", estoque_table, "#CA6F1E"),
            ExpandableCard("💰 Financeiro", financeiro_table, "#884EA0"),
        ]

        # coloca cards em 2 colunas
        row, col = 0, 0
        for card in self.cards:
            self.grid.addWidget(card, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1

        layout.addLayout(self.grid)
        
    def get_vendas(self):
        import models.database as db
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, cliente_id, total FROM vendas WHERE usuario_id=?", (self.user_id,))
        data = cursor.fetchall()
        conn.close()
        return [[str(row["id"]), str(row["cliente_id"]), str(row["total"])] for row in data]

    def updateLayout(self):
        """Atualiza layout quando algum card expande"""
        for card in self.cards:
            if card.is_expanded:
                card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            else:
                card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                card.setMaximumHeight(card.default_height)
        self.updateGeometry()

    def create_table(self, headers, data):
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setRowCount(len(data))

        for i, row in enumerate(data):
            for j, val in enumerate(row):
                table.setItem(i, j, QTableWidgetItem(val))

        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setAlternatingRowColors(True)
        table.setStyleSheet("""
            QTableWidget {
                border: none;
                border-radius: 6px;
                background: #fdfdfd;
                alternate-background-color: #f5f5f5;
            }
            QHeaderView::section {
                background: #2E4053;
                color: white;
                font-weight: bold;
                border: none;
                padding: 6px;
            }
        """)
        return table
