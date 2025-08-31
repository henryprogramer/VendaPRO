from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog, QFormLayout,
    QLineEdit, QMessageBox, QComboBox, QFrame
)
from PyQt5.QtCore import Qt
from desktop.models import database

class ClientesWindow(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.conn = database.get_connection()
        self.cursor = self.conn.cursor()

        self.setWindowTitle("Gestão de Clientes")
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
        self.load_clients()

    def init_ui(self):
        layout = QVBoxLayout()

        # ---------- HEADER ----------
        header_layout = QHBoxLayout()
        lbl_title = QLabel("Clientes")
        lbl_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #007acc;")
        header_layout.addWidget(lbl_title)
        header_layout.addStretch()
        self.btn_add = QPushButton("+ Adicionar Cliente")
        self.btn_add.clicked.connect(self.open_form_add)
        header_layout.addWidget(self.btn_add)
        layout.addLayout(header_layout)

        # ---------- TABELA ----------
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nome", "Email", "Telefone",
            "CPF", "Status", "Data Prospecção", "Ações"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table)

        # ---------- SEÇÃO EXTRA ----------
        bottom_layout = QHBoxLayout()

        # --- LIVRO ABERTO (Contas + Dashboard) ---
        book_layout = QHBoxLayout()

        # Página esquerda = Contas
        self.page_left = QFrame()
        self.page_left.setStyleSheet("background:#fff8dc; border:2px solid #d2b48c; border-radius:8px;")
        contas_layout = QVBoxLayout()
        contas_title = QLabel("📖 Contas do Cliente")
        contas_title.setStyleSheet("font-size:16px; font-weight:bold; margin-bottom:8px;")
        self.lbl_compras = QLabel("🛒 Compras: 0")
        self.lbl_dividas = QLabel("💸 Dívidas: R$ 0,00")
        self.lbl_total = QLabel("💰 Total gasto: R$ 0,00")
        contas_layout.addWidget(contas_title)
        contas_layout.addWidget(self.lbl_compras)
        contas_layout.addWidget(self.lbl_dividas)
        contas_layout.addWidget(self.lbl_total)
        self.page_left.setLayout(contas_layout)

        # Página direita = Dashboard
        self.page_right = QFrame()
        self.page_right.setStyleSheet("background:#eef7ff; border:2px solid #007acc; border-radius:8px;")
        dash_layout = QVBoxLayout()
        dash_title = QLabel("📊 Dashboard")
        dash_title.setStyleSheet("font-size:16px; font-weight:bold; margin-bottom:8px;")
        self.lbl_total_clientes = QLabel("👥 Total Clientes: 0")
        self.lbl_ativos = QLabel("✅ Ativos: 0")
        self.lbl_inativos = QLabel("❌ Inativos: 0")
        self.lbl_recent = QLabel("📅 Prospects recentes: 0")
        dash_layout.addWidget(dash_title)
        dash_layout.addWidget(self.lbl_total_clientes)
        dash_layout.addWidget(self.lbl_ativos)
        dash_layout.addWidget(self.lbl_inativos)
        dash_layout.addWidget(self.lbl_recent)
        self.page_right.setLayout(dash_layout)

        book_layout.addWidget(self.page_left, 1)
        book_layout.addWidget(self.page_right, 1)

        bottom_layout.addLayout(book_layout)
        layout.addLayout(bottom_layout)

        self.setLayout(layout)

    # ---------------- FUNÇÕES ----------------
    def load_clients(self):
        self.table.setRowCount(0)
        self.cursor.execute("""
            SELECT id, nome, email, telefone, cpf, status, data_prospeccao 
            FROM cliente WHERE user_id=?
        """, (self.user['id'],))
        for row_data in self.cursor.fetchall():
            row = self.table.rowCount()
            self.table.insertRow(row)
            for col, data in enumerate(row_data):
                self.table.setItem(row, col, QTableWidgetItem(str(data)))

            # Botões de ação
            btn_view = QPushButton("👁")
            btn_edit = QPushButton("Edit")
            btn_delete = QPushButton("🗑️")

            btn_view.setStyleSheet("background:#ff9800; color:white;")
            btn_edit.setStyleSheet("background:#2196f3; color:white;")
            btn_delete.setStyleSheet("background:#f44336; color:white;")

            btn_view.clicked.connect(lambda _, r=row_data: self.view_client(r))
            btn_edit.clicked.connect(lambda _, r=row_data: self.open_form_edit(r))
            btn_delete.clicked.connect(lambda _, r=row_data: self.delete_client(r[0]))

            action_layout = QHBoxLayout()
            action_layout.setContentsMargins(0, 0, 0, 0)  # remove margens
            action_layout.setSpacing(4)
            action_layout.addWidget(btn_view)
            action_layout.addWidget(btn_edit)
            action_layout.addWidget(btn_delete)

            action_widget = QWidget()
            action_widget.setLayout(action_layout)
            self.table.setCellWidget(row, 7, action_widget)

        self.update_dashboard()

    def update_dashboard(self):
        self.cursor.execute("""
            SELECT COUNT(*),
                   SUM(CASE WHEN status='ATIVO' THEN 1 ELSE 0 END),
                   SUM(CASE WHEN status='INATIVO' THEN 1 ELSE 0 END)
            FROM cliente WHERE user_id=?
        """, (self.user['id'],))
        total, ativos, inativos = self.cursor.fetchone()
        self.lbl_total_clientes.setText(f"👥 Total Clientes: {total}")
        self.lbl_ativos.setText(f"✅ Ativos: {ativos or 0}")
        self.lbl_inativos.setText(f"❌ Inativos: {inativos or 0}")

        # Prospects recentes (últimos 30 dias)
        self.cursor.execute("""
            SELECT COUNT(*) FROM cliente 
            WHERE user_id=? AND data_prospeccao >= date('now','-30 day')
        """, (self.user['id'],))
        recentes = self.cursor.fetchone()[0]
        self.lbl_recent.setText(f"📅 Prospects recentes: {recentes}")

    # ---------------- FORMULÁRIO ----------------
    def open_form_add(self):
        self.open_form()

    def open_form_edit(self, client):
        self.open_form(client)

    def open_form(self, client=None):
        dialog = QDialog(self)
        dialog.setWindowTitle("Formulário Cliente")
        form_layout = QFormLayout()

        input_nome = QLineEdit(); input_nome.setText(client[1] if client else "")
        input_email = QLineEdit(); input_email.setText(client[2] if client else "")
        input_tel = QLineEdit(); input_tel.setText(client[3] if client else "")
        input_cpf = QLineEdit(); input_cpf.setText(client[4] if client else "")
        input_status = QComboBox(); input_status.addItems(["ATIVO", "INATIVO"])
        if client: input_status.setCurrentText(client[5])

        form_layout.addRow("Nome:", input_nome)
        form_layout.addRow("Email:", input_email)
        form_layout.addRow("Telefone:", input_tel)
        form_layout.addRow("CPF:", input_cpf)
        form_layout.addRow("Status:", input_status)

        btn_save = QPushButton("Salvar")
        form_layout.addWidget(btn_save)
        dialog.setLayout(form_layout)

        def salvar():
            nome, email, tel, cpf, status = (
                input_nome.text(), input_email.text(), input_tel.text(),
                input_cpf.text(), input_status.currentText()
            )
            if client:  # editar
                self.cursor.execute("""
                    UPDATE cliente SET nome=?, email=?, telefone=?, cpf=?, status=? 
                    WHERE id=? AND user_id=?
                """, (nome, email, tel, cpf, status, client[0], self.user['id']))
            else:  # adicionar
                self.cursor.execute("""
                    INSERT INTO cliente (user_id, nome, email, telefone, cpf, status, data_prospeccao) 
                    VALUES (?, ?, ?, ?, ?, ?, date('now'))
                """, (self.user['id'], nome, email, tel, cpf, status))
            self.conn.commit()
            self.load_clients()
            dialog.accept()

        btn_save.clicked.connect(salvar)
        dialog.exec_()
    def view_client(self, client):
        dialog = QDialog(self)
        dialog.setWindowTitle("Visualizar Cliente")
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
        lbl_title = QLabel(f"{client[1]}")
        lbl_title.setObjectName("title")
        lbl_title.setProperty("class", "title")
        card_layout.addWidget(lbl_title)

        # Campos
        card_layout.addWidget(QLabel(f"Email: {client[2]}"))
        card_layout.addWidget(QLabel(f"Telefone: {client[3]}"))

        card.setLayout(card_layout)
        layout.addWidget(card)

        # Botão fechar
        btn_close = QPushButton("Fechar")
        btn_close.setStyleSheet("background:#f44336; font-weight:bold;")
        btn_close.clicked.connect(dialog.close)
        layout.addWidget(btn_close, alignment=Qt.AlignRight)

        dialog.setLayout(layout)
        dialog.exec_()

    def delete_client(self, client_id):
        confirm = QMessageBox.question(
            self, "Confirmar", "Deseja realmente remover?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            self.cursor.execute("DELETE FROM cliente WHERE id=? AND user_id=?", (client_id, self.user['id']))
            self.conn.commit()
            self.load_clients()
