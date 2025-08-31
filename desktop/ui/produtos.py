from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog, QFormLayout,
    QLineEdit, QMessageBox, QComboBox, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from desktop.models import database
from datetime import datetime, date

class ProdutosWindow(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.conn = database.get_connection()
        self.cursor = self.conn.cursor()

        self.setWindowTitle("Gestão de Produtos")
        self.setGeometry(200, 100, 1200, 700)

        # -------- TEMA / CORES --------
        self.setStyleSheet("""
            QWidget { background-color: #f0f8ff; font-size: 14px; }
            QTableWidget { background-color: #ffffff; alternate-background-color: #f9f9f9; selection-background-color: #4caf50; selection-color: #ffffff; border: 1px solid #cccccc; }
            QPushButton { background-color: #4caf50; color: white; font-weight: bold; padding: 6px 12px; border-radius: 6px; }
            QPushButton:hover { background-color: #45a049; }
        """)

        self.init_ui()
        self.load_products()

    def init_ui(self):
        layout = QVBoxLayout()

        # ---------- HEADER ----------
        header_layout = QHBoxLayout()
        lbl_title = QLabel("Produtos")
        lbl_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #007acc;")
        header_layout.addWidget(lbl_title)
        header_layout.addStretch()
        self.btn_add = QPushButton("+ Adicionar Produto")
        self.btn_add.clicked.connect(self.open_form_add)
        header_layout.addWidget(self.btn_add)
        layout.addLayout(header_layout)

        # ---------- TABELA ----------
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nome", "Marca", "Código de Barras", "Preço", "Quantidade", "Validade", "Status", "Ações"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table)

        # ---------- SEÇÃO EXTRA ----------
        bottom_layout = QHBoxLayout()

        # --- Controle de Estoque ---
        self.box_estoque = QFrame()
        self.box_estoque.setStyleSheet("background:#fff8dc; border:2px solid #d2b48c; border-radius:8px;")
        estoque_layout = QVBoxLayout()
        self.lbl_entradas = QLabel("📥 Entradas: 0")
        self.lbl_saidas = QLabel("📤 Saídas: 0")
        self.lbl_estoque_atual = QLabel("📦 Estoque atual: 0")
        estoque_layout.addWidget(self.lbl_entradas)
        estoque_layout.addWidget(self.lbl_saidas)
        estoque_layout.addWidget(self.lbl_estoque_atual)
        self.box_estoque.setLayout(estoque_layout)
        bottom_layout.addWidget(self.box_estoque, 1)

        # --- Dashboard ---
        self.box_dashboard = QFrame()
        self.box_dashboard.setStyleSheet("background:#eef7ff; border:2px solid #007acc; border-radius:8px;")
        dash_layout = QVBoxLayout()
        self.lbl_total_produtos = QLabel("📦 Total Produtos: 0")
        self.lbl_produtos_parados = QLabel("🛑 Produtos Parados: 0")
        self.lbl_produtos_validos = QLabel("✅ Produtos Válidos: 0")
        self.lbl_produtos_vencidos = QLabel("⚠️ Produtos Vencidos: 0")
        dash_layout.addWidget(self.lbl_total_produtos)
        dash_layout.addWidget(self.lbl_produtos_parados)
        dash_layout.addWidget(self.lbl_produtos_validos)
        dash_layout.addWidget(self.lbl_produtos_vencidos)
        self.box_dashboard.setLayout(dash_layout)
        bottom_layout.addWidget(self.box_dashboard, 1)

        layout.addLayout(bottom_layout)
        self.setLayout(layout)

    # ---------------- FUNÇÕES ----------------
    def load_products(self):
        self.table.setRowCount(0)
        self.cursor.execute("""
            SELECT id, nome, marca, codigo_barras, preco, quantidade, data_vencimento, status
            FROM produto WHERE user_id=?
        """, (self.user['id'],))
        rows = self.cursor.fetchall()
        for row_data in rows:
            row = self.table.rowCount()
            self.table.insertRow(row)
            for col, data in enumerate(row_data):
                if col == 6 and data:  # data_vencimento
                    try:
                        dt = datetime.strptime(data, "%Y-%m-%d").strftime("%d/%m/%Y")
                        data = dt
                    except:
                        pass
                self.table.setItem(row, col, QTableWidgetItem(str(data)))
            
            # Botões de ação
            btn_view = QPushButton("👁")
            btn_view.setStyleSheet("background-color: #ff9800; color: white;")
            btn_edit = QPushButton("Edit")
            btn_edit.setStyleSheet("background-color: #2196f3; color: white;")
            btn_delete = QPushButton("🗑️")
            btn_delete.setStyleSheet("background-color: #f44336; color: white;")
            btn_view.clicked.connect(lambda _, r=row_data: self.view_product(r))
            btn_edit.clicked.connect(lambda _, r=row_data: self.open_form_edit(r))
            btn_delete.clicked.connect(lambda _, r=row_data: self.delete_product(r[0]))
            action_layout = QHBoxLayout()
            action_layout.setContentsMargins(0, 0, 0, 0)
            action_layout.setSpacing(5)
            action_layout.addWidget(btn_view)
            action_layout.addWidget(btn_edit)
            action_layout.addWidget(btn_delete)
            action_widget = QWidget()
            action_widget.setLayout(action_layout)
            self.table.setCellWidget(row, 8, action_widget)

        self.update_dashboard(rows)

    def update_dashboard(self, rows=None):
        if rows is None:
            self.cursor.execute("SELECT id, status, data_vencimento, quantidade FROM produto WHERE user_id=?", (self.user['id'],))
            rows = self.cursor.fetchall()

        total = len(rows)
        parados = sum(1 for r in rows if r[1] == "PARADO")
        validos = sum(1 for r in rows if r[1] == "ATIVO")

        vencidos = 0
        estoque_total = 0
        for r in rows:
            estoque_total += r[3] if len(r) > 3 else 0
            data_venc = r[2]
            if data_venc:
                try:
                    dt = datetime.strptime(data_venc, "%Y-%m-%d").date()
                    if dt < date.today():
                        vencidos += 1
                except ValueError:
                    pass

        self.lbl_total_produtos.setText(f"📦 Total Produtos: {total}")
        self.lbl_produtos_parados.setText(f"🛑 Produtos Parados: {parados}")
        self.lbl_produtos_validos.setText(f"✅ Produtos Válidos: {validos}")
        self.lbl_produtos_vencidos.setText(f"⚠️ Produtos Vencidos: {vencidos}")
        self.lbl_estoque_atual.setText(f"📦 Estoque atual: {estoque_total}")

    # ---------------- FORMULÁRIO ----------------
    def open_form_add(self):
        self.open_form()

    def open_form_edit(self, product):
        self.open_form(product)

    def open_form(self, product=None):
        dialog = QDialog(self)
        dialog.setWindowTitle("Formulário Produto")
        form_layout = QFormLayout()

        input_nome = QLineEdit(); input_nome.setText(product[1] if product else "")
        input_marca = QLineEdit(); input_marca.setText(product[2] if product else "")
        input_cod = QLineEdit(); input_cod.setText(product[3] if product else "")
        input_preco = QLineEdit(); input_preco.setText(str(product[4]) if product else "")
        input_quant = QLineEdit(); input_quant.setText(str(product[5]) if product else "0")
        input_validade = QLineEdit(); input_validade.setText(product[6] if product else "")
        input_status = QComboBox(); input_status.addItems(["ATIVO","PARADO","VENCIDO"])
        if product: input_status.setCurrentText(product[7])

        form_layout.addRow("Nome:", input_nome)
        form_layout.addRow("Marca:", input_marca)
        form_layout.addRow("Preço:", input_preco)
        form_layout.addRow("Quantidade:", input_quant)
        form_layout.addRow("Validade (DD/MM/YYYY):", input_validade)
        form_layout.addRow("Status:", input_status)
        form_layout.addRow("Código de Barras:", input_cod)

        btn_save = QPushButton("Salvar")
        form_layout.addWidget(btn_save)
        dialog.setLayout(form_layout)

        def salvar():
            nome, marca, cod, preco, quant, validade, status = (
                input_nome.text(), input_marca.text(), input_cod.text(),
                input_preco.text(), input_quant.text(), input_validade.text(), input_status.currentText()
            )
            if product:  # editar
                self.cursor.execute("""
                    UPDATE produto SET nome=?, marca=?, codigo_barras=?, preco=?, quantidade=?, data_vencimento=?, status=? WHERE id=? AND user_id=?
                """, (nome, marca, cod, preco, quant, validade, status, product[0], self.user['id']))
            else:  # adicionar
                self.cursor.execute("""
                    INSERT INTO produto (user_id, nome, marca, codigo_barras, preco, quantidade, data_vencimento, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (self.user['id'], nome, marca, cod, preco, quant, validade, status))
            self.conn.commit()
            self.load_products()
            dialog.accept()

        btn_save.clicked.connect(salvar)
        dialog.exec_()

    # ---------------- AÇÕES ----------------
    def view_product(self, product):
        dialog = QDialog(self)
        dialog.setWindowTitle("Visualizar Produto")
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
        lbl_title = QLabel(f"{product[1]}")
        lbl_title.setObjectName("title")
        lbl_title.setProperty("class", "title")
        card_layout.addWidget(lbl_title)

        # Campos
        card_layout.addWidget(QLabel(f"\nMarca: {product[2]}"))
        card_layout.addWidget(QLabel(f"\nPreço: {product[4]}"))
        card_layout.addWidget(QLabel(f"\nQuantidade: {product[5]}"))
        card_layout.addWidget(QLabel(f"\nValidade: {product[6]}"))
        card_layout.addWidget(QLabel(f"\nStatus: {product[7]}"))
        card_layout.addWidget(QLabel(f"\nCódigo de Barras: {product[3]}"))

        card.setLayout(card_layout)
        layout.addWidget(card)

        # Botão fechar
        btn_close = QPushButton("Fechar")
        btn_close.setStyleSheet("background:#f44336; font-weight:bold;")
        btn_close.clicked.connect(dialog.close)
        layout.addWidget(btn_close, alignment=Qt.AlignRight)

        dialog.setLayout(layout)
        dialog.exec_()

    def delete_product(self, product_id):
        confirm = QMessageBox.question(
            self, "Confirmar",
            "Deseja realmente remover?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            self.cursor.execute("DELETE FROM produto WHERE id=? AND user_id=?", (product_id, self.user['id']))
            self.conn.commit()
            self.load_products()
