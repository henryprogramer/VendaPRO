import sqlite3
from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QDateEdit, QDialog,
    QFormLayout, QComboBox, QMessageBox, QFrame
)
from PyQt5.QtCore import Qt, QDate
from models import database

class FuncionariosWindow(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.user_id = self.user['id']
        self.conn = database.get_connection()
        self.cursor = self.conn.cursor()

        self.setWindowTitle("Gestão de Funcionários")
        self.setGeometry(200, 100, 1200, 700)

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
        self.load_funcionarios()

    def init_ui(self):
        layout = QVBoxLayout()

        # ---------- HEADER ----------
        header_layout = QHBoxLayout()
        lbl_title = QLabel("Funcionários")
        lbl_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #007acc;")
        header_layout.addWidget(lbl_title)
        header_layout.addStretch()
        self.btn_add = QPushButton("+ Adicionar Funcionário")
        self.btn_add.clicked.connect(lambda: self.open_form())
        header_layout.addWidget(self.btn_add)
        layout.addLayout(header_layout)

        # ---------- TABELA ----------
        self.table = QTableWidget()
        self.table.setColumnCount(6 + 1)  # +1 para ações
        self.table.setHorizontalHeaderLabels([
            "ID", "Nome", "Email", "Telefone", "Data de Nascimento", "Cargo", "Ações"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table)

        self.setLayout(layout)

    # ---------------- FUNÇÕES ----------------
    def load_funcionarios(self):
        self.table.setRowCount(0)
        self.cursor.execute("""
            SELECT id, nome, email, telefone, data_nascimento, cargo
            FROM funcionario WHERE user_id=?
        """, (self.user_id,))
        for row_data in self.cursor.fetchall():
            row = self.table.rowCount()
            self.table.insertRow(row)
            for col, data in enumerate(row_data):
                if col == 4 and data:  # Formata a data
                    partes = data.split("-") if "-" in data else data.split("/")
                    if len(partes) == 3:
                        if "-" in data:  # YYYY-MM-DD → DD/MM/YYYY
                            data = f"{partes[2]}/{partes[1]}/{partes[0]}"
                self.table.setItem(row, col, QTableWidgetItem(str(data)))

            # Botões de ação
        for row_data in self.cursor.fetchall():
            row = self.table.rowCount()
            self.table.insertRow(row)
            for col, data in enumerate(row_data):
                if col == 4 and data:  # Formata a data
                    partes = data.split("-") if "-" in data else data.split("/")
                    if len(partes) == 3:
                        if "-" in data:  # YYYY-MM-DD → DD/MM/YYYY
                            data = f"{partes[2]}/{partes[1]}/{partes[0]}"
                self.table.setItem(row, col, QTableWidgetItem(str(data)))
        
            # Botões de ação
            btn_view = QPushButton("👁️") 
            btn_edit = QPushButton("Edit")
            btn_delete = QPushButton("🗑️")
            
            btn_view.setStyleSheet("background:#ff9800; color:white;")
            btn_edit.setStyleSheet("background:#2196f3; color:white;")
            btn_delete.setStyleSheet("background:#f44336; color:white;")
            
            # Cria cópia do row_data para cada botão
            current_data = list(row_data)
        
            btn_edit.clicked.connect(lambda _, r=current_data: self.open_form(r))
            btn_delete.clicked.connect(lambda _, r=current_data: self.delete_funcionario(r[0]))
            btn_view.clicked.connect(lambda _, r=current_data: self.view_funcionario(r))
            
            # Layout horizontal para os 3 botões
            action_layout = QHBoxLayout()
            action_layout.setContentsMargins(0, 0, 0, 0)
            action_layout.setSpacing(4)
            action_layout.addWidget(btn_view)
            action_layout.addWidget(btn_edit)
            action_layout.addWidget(btn_delete)
            
            action_widget = QWidget()
            action_widget.setLayout(action_layout)
            self.table.setCellWidget(row, 6, action_widget)

    # ---------------- FORMULÁRIO ----------------
    def open_form(self, funcionario=None):
        dialog = QDialog(self)
        dialog.setWindowTitle("Formulário Funcionário")
        form_layout = QFormLayout()

        input_nome = QLineEdit(); input_nome.setText(funcionario[1] if funcionario else "")
        input_email = QLineEdit(); input_email.setText(funcionario[2] if funcionario else "")
        input_tel = QLineEdit(); input_tel.setText(funcionario[3] if funcionario else "")
        input_data = QDateEdit(); input_data.setDisplayFormat("dd/MM/yyyy")
        if funcionario:
            partes = funcionario[4].split("/") if "/" in funcionario[4] else funcionario[4].split("-")
            if len(partes) == 3:
                input_data.setDate(QDate(int(partes[2]), int(partes[1]), int(partes[0])))
        else:
            input_data.setDate(QDate.currentDate())
        input_cargo = QLineEdit(); input_cargo.setText(funcionario[5] if funcionario else "")

        form_layout.addRow("Nome:", input_nome)
        form_layout.addRow("Email:", input_email)
        form_layout.addRow("Telefone:", input_tel)
        form_layout.addRow("Data Nascimento:", input_data)
        form_layout.addRow("Cargo:", input_cargo)

        btn_save = QPushButton("Salvar")
        form_layout.addWidget(btn_save)
        dialog.setLayout(form_layout)

        def salvar():
            nome, email, tel, data, cargo = (
                input_nome.text(), input_email.text(), input_tel.text(),
                input_data.date().toString("dd/MM/yyyy"), input_cargo.text()
            )
            if funcionario:  # editar
                self.cursor.execute("""
                    UPDATE funcionario SET nome=?, email=?, telefone=?, data_nascimento=?, cargo=? 
                    WHERE id=? AND user_id=?
                """, (nome, email, tel, data, cargo, funcionario[0], self.user_id))
            else:  # adicionar
                self.cursor.execute("""
                    INSERT INTO funcionario (user_id, nome, email, telefone, data_nascimento, cargo) 
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (self.user_id, nome, email, tel, data, cargo))
            self.conn.commit()
            self.load_funcionarios()
            dialog.accept()

        btn_save.clicked.connect(salvar)
        dialog.exec_()

    def view_funcionario(self, funcionario):
        dialog = QDialog(self)
        dialog.setWindowTitle("Visualizar Funcionário")
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
        lbl_title = QLabel(f"{funcionario[1]}")
        lbl_title.setObjectName("title")
        lbl_title.setProperty("class", "title")
        card_layout.addWidget(lbl_title)

        # Campos
        card_layout.addWidget(QLabel(f"Email: {funcionario[2]}"))
        card_layout.addWidget(QLabel(f"Telefone: {funcionario[3]}"))
        card_layout.addWidget(QLabel(f"Nascimento: {funcionario[4]}"))
        card_layout.addWidget(QLabel(f"Cargo: {funcionario[5]}"))

        card.setLayout(card_layout)
        layout.addWidget(card)

        # Botão fechar
        btn_close = QPushButton("Fechar")
        btn_close.setStyleSheet("background:#f44336; font-weight:bold;")
        btn_close.clicked.connect(dialog.close)
        layout.addWidget(btn_close, alignment=Qt.AlignRight)

        dialog.setLayout(layout)
        dialog.exec_()

    # ---------------- DELETE ----------------
    def delete_funcionario(self, funcionario_id):
        confirm = QMessageBox.question(
            self, "Confirmar", "Deseja realmente remover?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            self.cursor.execute("DELETE FROM funcionario WHERE id=? AND user_id=?", (funcionario_id, self.user_id))
            self.conn.commit()
            self.load_funcionarios()
