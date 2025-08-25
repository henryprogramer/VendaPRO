from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog, QFormLayout,
    QLineEdit, QMessageBox, QComboBox, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from models import database

class ProdutosWindow(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.conn = database.get_connection()
        self.cursor = self.conn.cursor()

        self.setWindowTitle("Gestão de Produtos")
        self.setGeometry(200, 100, 1200, 700)

        self.init_ui()
        self.load_products()

    def init_ui(self):
        layout = QVBoxLayout()

        # ---------- HEADER ----------
        header_layout = QHBoxLayout()
        lbl_title = QLabel("📦 Produtos")
        lbl_title.setStyleSheet("font-size: 20px; font-weight: bold;")
        header_layout.addWidget(lbl_title)
        header_layout.addStretch()
        self.btn_add = QPushButton("➕ Adicionar Produto")
        self.btn_add.clicked.connect(self.open_form_add)
        header_layout.addWidget(self.btn_add)
        layout.addLayout(header_layout)

        # ---------- TABELA ----------
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nome", "Marca", "Código de Barras", "Preço", "Validade", "Status", "Ações"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table)

        # ---------- SEÇÃO EXTRA ----------
        bottom_layout = QHBoxLayout()

        # --- Controle de Estoque ---
        self.box_estoque = QFrame()
        self.box_estoque.setStyleSheet("background:#f2f2f2; border:1px solid #ccc;")
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
        self.box_dashboard.setStyleSheet("background:#eef7ff; border:1px solid #007acc;")
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
            SELECT id, nome, marca, codigo_barras, preco, data_vencimento, status
            FROM produto WHERE user_id=?
        """, (self.user['id'],))
        for row_data in self.cursor.fetchall():
            row = self.table.rowCount()
            self.table.insertRow(row)
            for col, data in enumerate(row_data):
                self.table.setItem(row, col, QTableWidgetItem(str(data)))
            
            # Botões de ação
            btn_view = QPushButton("👁")
            btn_edit = QPushButton("✏️")
            btn_delete = QPushButton("🗑️")
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
            self.table.setCellWidget(row, 7, action_widget)

        self.update_dashboard()

    def update_dashboard(self):
        self.cursor.execute("SELECT COUNT(*), SUM(CASE WHEN status='PARADO' THEN 1 ELSE 0 END) FROM produto WHERE user_id=?", (self.user['id'],))
        total, parados = self.cursor.fetchone()
        self.lbl_total_produtos.setText(f"📦 Total Produtos: {total}")
        self.lbl_produtos_parados.setText(f"🛑 Produtos Parados: {parados or 0}")
        # Aqui você pode calcular produtos válidos e vencidos com base na data_validade

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
        input_validade = QLineEdit(); input_validade.setText(product[5] if product else "")
        input_status = QComboBox(); input_status.addItems(["ATIVO","PARADO","VENCIDO"])
        if product: input_status.setCurrentText(product[6])

        form_layout.addRow("Nome:", input_nome)
        form_layout.addRow("Marca:", input_marca)
        form_layout.addRow("Código de Barras:", input_cod)
        form_layout.addRow("Preço:", input_preco)
        form_layout.addRow("Validade:", input_validade)
        form_layout.addRow("Status:", input_status)

        btn_save = QPushButton("Salvar")
        form_layout.addWidget(btn_save)
        dialog.setLayout(form_layout)

        def salvar():
            nome, marca, cod, preco, validade, status = (
                input_nome.text(), input_marca.text(), input_cod.text(),
                input_preco.text(), input_validade.text(), input_status.currentText()
            )
            if product:  # editar
                self.cursor.execute("""
                    UPDATE produto SET nome=?, marca=?, codigo_barras=?, preco=?, data_vencimento=?, status=? WHERE id=? AND user_id=?
                """, (nome, marca, cod, preco, validade, status, product[0], self.user['id']))
            else:  # adicionar
                self.cursor.execute("""
                    INSERT INTO produto (user_id, nome, marca, codigo_barras, preco, data_vencimento, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (self.user['id'], nome, marca, cod, preco, validade, status))
            self.conn.commit()
            self.load_products()
            dialog.accept()

        btn_save.clicked.connect(salvar)
        dialog.exec_()

    def view_product(self, product):
        QMessageBox.information(self, "Visualizar Produto", f"Nome: {product[1]}\nMarca: {product[2]}\nPreço: {product[4]}")

    def delete_product(self, product_id):
        confirm = QMessageBox.question(self, "Confirmar", "Deseja realmente remover?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            self.cursor.execute("DELETE FROM produto WHERE id=? AND user_id=?", (product_id, self.user['id']))
            self.conn.commit()
            self.load_products()
