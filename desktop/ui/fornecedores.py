from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog, QFormLayout,
    QLineEdit, QMessageBox, QComboBox, QFrame
)
from PyQt5.QtCore import Qt
from desktop.models import database

class FornecedoresWindow(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.conn = database.get_connection()
        self.cursor = self.conn.cursor()

        self.setWindowTitle("Gestão de Fornecedores")
        self.setGeometry(200, 100, 1000, 600)

        # -------- TEMA / CORES --------
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f8ff;
                font-size: 14px;
            }
            QTableWidget {
                background-color: #ffffff;
                alternate-background-color: #f9f9f9;
                selection-background-color: #4caf50;
                selection-color: #ffffff;
                border: 1px solid #cccccc;
            }
            QPushButton {
                background-color: #4caf50;
                color: white;
                font-weight: bold;
                padding: 6px 12px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        self.init_ui()
        self.load_fornecedores()

    def init_ui(self):
        layout = QVBoxLayout()

        # ---------- HEADER ----------
        header_layout = QHBoxLayout()
        lbl_title = QLabel("Fornecedores")
        lbl_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #007acc;")
        header_layout.addWidget(lbl_title)
        header_layout.addStretch()
        self.btn_add = QPushButton("+ Adicionar Fornecedor")
        self.btn_add.clicked.connect(self.open_form_add)
        header_layout.addWidget(self.btn_add)
        layout.addLayout(header_layout)

        # ---------- TABELA ----------
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nome", "Contato", "Ações"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table)

        # ---------- DASHBOARD ----------
        dash_layout = QHBoxLayout()
        self.page_right = QFrame()
        self.page_right.setStyleSheet("background:#eef7ff; border:2px solid #007acc; border-radius:8px;")
        right_layout = QVBoxLayout()
        dash_title = QLabel("📊 Dashboard Fornecedores")
        dash_title.setStyleSheet("font-size:16px; font-weight:bold; margin-bottom:8px;")
        self.lbl_total = QLabel("🏢 Total Fornecedores: 0")
        right_layout.addWidget(dash_title)
        right_layout.addWidget(self.lbl_total)
        self.page_right.setLayout(right_layout)
        dash_layout.addWidget(self.page_right, 1)
        layout.addLayout(dash_layout)

        self.setLayout(layout)

    # ---------------- FUNÇÕES ----------------
    def load_fornecedores(self):
        self.table.setRowCount(0)
        self.cursor.execute("""
            SELECT id, nome, contato 
            FROM fornecedor WHERE user_id=?
        """, (self.user['id'],))
        for row_data in self.cursor.fetchall():
            row = self.table.rowCount()
            self.table.insertRow(row)
            for col, data in enumerate(row_data):
                self.table.setItem(row, col, QTableWidgetItem(str(data)))

            # Botões de ação
            btn_view = QPushButton("👁️") 
            btn_edit = QPushButton("Edit")
            btn_delete = QPushButton("🗑️")

            btn_view.setStyleSheet("background:#ff9800; color:white;")
            btn_edit.setStyleSheet("background:#2196f3; color:white;")
            btn_delete.setStyleSheet("background:#f44336; color:white;")

            # Conecta as funções
            btn_edit.clicked.connect(lambda _, r=row_data: self.open_form(r))
            btn_delete.clicked.connect(lambda _, r=row_data: self.delete_fornecedor(r[0]))
            btn_view.clicked.connect(lambda _, r=row_data: self.view_fornecedor(r))

            # Layout horizontal para os 3 botões
            action_layout = QHBoxLayout()
            action_layout.setContentsMargins(0, 0, 0, 0)
            action_layout.setSpacing(4)
            action_layout.addWidget(btn_view)
            action_layout.addWidget(btn_edit)
            action_layout.addWidget(btn_delete)

            action_widget = QWidget()
            action_widget.setLayout(action_layout)
            self.table.setCellWidget(row, 3, action_widget)  # agora certo na coluna "Ações"

        self.update_dashboard()

    def update_dashboard(self):
        self.cursor.execute("SELECT COUNT(*) FROM fornecedor WHERE user_id=?", (self.user['id'],))
        total = self.cursor.fetchone()[0]
        self.lbl_total.setText(f"🏢 Total Fornecedores: {total}")

    def view_fornecedor(self, fornecedor):
        dialog = QDialog(self)
        dialog.setWindowTitle("Visualizar Fornecedor")
        dialog.setMinimumWidth(400)

        layout = QVBoxLayout()

        # Card container
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: #ffffff;
                border: 2px solid #007acc;
                border-radius: 8px;
                padding: 12px;
            }
            QLabel {
                font-size: 14px;
                margin: 4px 0;
            }
            QLabel.title {
                font-size: 16px;
                font-weight: bold;
                color: #007acc;
                margin-bottom: 8px;
            }
        """)
        card_layout = QVBoxLayout()

        # Título
        lbl_title = QLabel(f"{fornecedor[1]}")
        lbl_title.setObjectName("title")
        lbl_title.setProperty("class", "title")
        card_layout.addWidget(lbl_title)

        # Campos
        card_layout.addWidget(QLabel(f"Contato: {fornecedor[2]}"))

        card.setLayout(card_layout)
        layout.addWidget(card)

        # Botão fechar
        btn_close = QPushButton("Fechar")
        btn_close.setStyleSheet("background:#f44336; font-weight:bold;")
        btn_close.clicked.connect(dialog.close)
        layout.addWidget(btn_close, alignment=Qt.AlignRight)

        dialog.setLayout(layout)
        dialog.exec_()


    # ---------------- FORMULÁRIO ----------------
    def open_form_add(self):
        self.open_form()

    def open_form_edit(self, fornecedor):
        self.open_form(fornecedor)

    def open_form(self, fornecedor=None):
        dialog = QDialog(self)
        dialog.setWindowTitle("Formulário Fornecedor")
        form_layout = QFormLayout()

        input_nome = QLineEdit(); input_nome.setPlaceholderText("Nome do fornecedor")
        input_nome.setText(fornecedor[1] if fornecedor else "")
        input_contato = QLineEdit(); input_contato.setPlaceholderText("Contato (telefone/email)")
        input_contato.setText(fornecedor[2] if fornecedor else "")

        form_layout.addRow("Nome:", input_nome)
        form_layout.addRow("Contato:", input_contato)

        btn_save = QPushButton("Salvar")
        form_layout.addWidget(btn_save)
        dialog.setLayout(form_layout)

        def salvar():
            nome, contato = input_nome.text(), input_contato.text()
            if fornecedor:  # editar
                self.cursor.execute("""
                    UPDATE fornecedor SET nome=?, contato=? 
                    WHERE id=? AND user_id=?
                """, (nome, contato, fornecedor[0], self.user['id']))
            else:  # adicionar
                self.cursor.execute("""
                    INSERT INTO fornecedor (user_id, nome, contato) 
                    VALUES (?, ?, ?)
                """, (self.user['id'], nome, contato))
            self.conn.commit()
            self.load_fornecedores()
            dialog.accept()

        btn_save.clicked.connect(salvar)
        dialog.exec_()

    def delete_fornecedor(self, fornecedor_id):
        confirm = QMessageBox.question(
            self, "Confirmar", "Deseja realmente remover?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            self.cursor.execute("DELETE FROM fornecedor WHERE id=? AND user_id=?", (fornecedor_id, self.user['id']))
            self.conn.commit()
            self.load_fornecedores()
