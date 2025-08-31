from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QComboBox, QMessageBox, QFrame, QInputDialog, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from desktop.models import database
import datetime

class CaixaWindow(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.conn = database.get_connection()
        self.cursor = self.conn.cursor()

        # estado da venda
        self.carrinho = []
        self.total_carrinho = 0.0
        self.total_final = 0.0
        self.produto_atual = None

        # janela
        self.setWindowTitle("Caixa - VendaPRO")
        self.setGeometry(100, 50, 1200, 700)
        self.setStyleSheet("background-color: #f0f2f5;")
        self.init_ui()

    def init_ui(self):
        # layout principal
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(10)

        # Botão Abrir Caixa (visual destacado)
        self.btn_abrir_caixa = QPushButton("🔓 Abrir Caixa")
        self.btn_abrir_caixa.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.btn_abrir_caixa.setFont(QFont("Arial", 20, QFont.Bold))
        self.btn_abrir_caixa.setStyleSheet("""
            QPushButton {
                background-color: #0066cc; color: white; font-weight: bold;
                padding: 30px; border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #004c99;
            }
        """)
        self.btn_abrir_caixa.clicked.connect(self.abrir_caixa)
        self.layout.addWidget(self.btn_abrir_caixa, alignment=Qt.AlignCenter)

        self.setLayout(self.layout)

    # ---------- AÇÕES DO CAIXA ----------
    def abrir_caixa(self):
        # pede senha (usa campo 'password' do usuário)
        senha, ok = QInputDialog.getText(self, "Senha", "Digite sua senha:", QLineEdit.Password)
        if not ok:
            return
        if senha != self.user.get('password', ''):
            QMessageBox.warning(self, "Erro", "Senha incorreta!")
            return

        # limpa layout atual
        for i in reversed(range(self.layout.count())):
            item = self.layout.itemAt(i)
            if item.widget():
                item.widget().setParent(None)

        # botão iniciar venda
        btn_iniciar_venda = QPushButton("🛒 Iniciar Venda")
        btn_iniciar_venda.setStyleSheet("""
            QPushButton {
                background-color: #28a745; color: white; font-weight: bold;
                padding: 10px; border-radius: 8px;
            }
            QPushButton:hover { background-color: #218838; }
        """)
        btn_iniciar_venda.clicked.connect(self.iniciar_venda)
        self.layout.addWidget(btn_iniciar_venda, alignment=Qt.AlignLeft)

        # botão relatório (placeholder)
        btn_relatorio = QPushButton("📄 Relatório de Fluxo de Caixa")
        btn_relatorio.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8; color: white; font-weight: bold;
                padding: 10px; border-radius: 8px;
            }
            QPushButton:hover { background-color: #117a8b; }
        """)
        btn_relatorio.clicked.connect(lambda: QMessageBox.information(self, "Relatório", "Relatório não implementado ainda."))
        self.layout.addWidget(btn_relatorio, alignment=Qt.AlignLeft)

        QMessageBox.information(self, "Sucesso", "Caixa aberto com sucesso!")

    def fechar_caixa(self):
        # limpa layout e restaura botão Abrir Caixa
        for i in reversed(range(self.layout.count())):
            item = self.layout.itemAt(i)
            if item.widget():
                item.widget().setParent(None)
        self.layout.addWidget(self.btn_abrir_caixa, alignment=Qt.AlignCenter)
        QMessageBox.information(self, "Fechado", "Caixa fechado com sucesso!")

    # ---------- INICIAR VENDA (layout de venda) ----------
    def iniciar_venda(self):
        # limpa layout
        for i in reversed(range(self.layout.count())):
            item = self.layout.itemAt(i)
            if item.widget():
                item.widget().setParent(None)

        main_layout = QHBoxLayout()
        main_layout.setSpacing(15)

        # LADO ESQUERDO: busca, cálculo e tabela de produtos
        left_layout = QVBoxLayout()
        left_layout.setSpacing(15)

        # Botão Fechar Caixa na tela de vendas
        self.btn_fechar_caixa = QPushButton("🔒 Fechar Caixa")
        self.btn_fechar_caixa.setStyleSheet("""
            QPushButton {
                background-color: #f44336; color: white; font-weight: bold;
                padding: 8px; border-radius: 8px;
            }
            QPushButton:hover { background-color: #ff4336; }
        """)
        self.btn_fechar_caixa.clicked.connect(self.fechar_caixa)
        left_layout.addWidget(self.btn_fechar_caixa, alignment=Qt.AlignLeft)

        # Card busca (topo-esquerdo)
        card_busca = QFrame()
        card_busca.setStyleSheet("background-color: #ffffff; border-radius: 10px; padding: 10px;")
        card_busca.setFrameShape(QFrame.StyledPanel)
        layout_busca = QVBoxLayout()
        layout_busca.setSpacing(8)

        self.input_busca = QLineEdit()
        self.input_busca.setPlaceholderText("Digite nome ou código de barras")
        self.input_busca.setStyleSheet("padding: 6px; border-radius: 6px; border: 1px solid #ccc;")
        btn_buscar = QPushButton("🔍 Buscar")
        btn_buscar.setStyleSheet("""
            QPushButton {
                background-color: #ffc107; color: black; font-weight: bold;
                padding: 6px; border-radius: 6px;
            }
            QPushButton:hover { background-color: #e0a800; }
        """)
        btn_buscar.clicked.connect(self.buscar_produto)

        layout_busca.addWidget(self.input_busca)
        layout_busca.addWidget(btn_buscar)

        self.lbl_produto = QLabel("Produto não selecionado")
        self.lbl_produto.setFont(QFont("Arial", 12))
        layout_busca.addWidget(self.lbl_produto)

        self.btn_adicionar = QPushButton("Adicionar ao Carrinho")
        self.btn_adicionar.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8; color: white; font-weight: bold;
                padding: 8px; border-radius: 6px;
            }
            QPushButton:hover { background-color: #117a8b; }
        """)
        self.btn_adicionar.clicked.connect(self.adicionar_carrinho)
        self.btn_adicionar.setEnabled(False)
        layout_busca.addWidget(self.btn_adicionar)

        card_busca.setLayout(layout_busca)
        left_layout.addWidget(card_busca)

        # Pressionar Enter busca + adiciona
        self.input_busca.returnPressed.connect(self.buscar_e_adicionar)

        # Card cálculo da venda (abaixo do card busca)
        card_calc = QFrame()
        card_calc.setStyleSheet("background-color: #ffffff; border-radius: 10px; padding: 10px;")
        card_calc.setFrameShape(QFrame.StyledPanel)
        layout_calc = QVBoxLayout()
        layout_calc.setSpacing(8)

        self.combo_pagamento = QComboBox()
        self.combo_pagamento.addItems(["DINHEIRO", "PIX", "CARTÃO"])
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(["À VISTA", "A PRAZO"])

        self.input_desconto = QLineEdit("0")
        self.input_pago = QLineEdit("0")

        # Conecta mudanças para atualizar total/troco em tempo real
        self.input_desconto.textChanged.connect(self.atualizar_total)
        self.input_pago.textChanged.connect(self.atualizar_total)
        self.combo_tipo.currentIndexChanged.connect(self.atualizar_total)

        layout_calc.addWidget(QLabel("Forma de Pagamento:"))
        layout_calc.addWidget(self.combo_pagamento)
        layout_calc.addWidget(QLabel("Tipo de Pagamento:"))
        layout_calc.addWidget(self.combo_tipo)
        layout_calc.addWidget(QLabel("Desconto (R$):"))
        layout_calc.addWidget(self.input_desconto)
        layout_calc.addWidget(QLabel("Valor Pago pelo Cliente:"))
        layout_calc.addWidget(self.input_pago)

        self.lbl_final_total = QLabel("Total Final: R$ 0,00")
        self.lbl_final_total.setFont(QFont("Arial", 12, QFont.Bold))
        self.lbl_troco = QLabel("Troco: R$ 0,00")
        self.lbl_troco.setFont(QFont("Arial", 12))
        layout_calc.addWidget(self.lbl_final_total)
        layout_calc.addWidget(self.lbl_troco)

        self.btn_finalizar = QPushButton("💰 Finalizar Venda")
        self.btn_finalizar.setStyleSheet("""
            QPushButton {
                background-color: #dc3545; color: white; font-weight: bold;
                padding: 8px; border-radius: 8px;
            }
            QPushButton:hover { background-color: #bd2130; }
        """)
        self.btn_finalizar.clicked.connect(self.finalizar_venda)
        layout_calc.addWidget(self.btn_finalizar)

        card_calc.setLayout(layout_calc)
        left_layout.addWidget(card_calc)

        # Card tabela de produtos (abaixo do cálculo)
        card_tabela = QFrame()
        card_tabela.setStyleSheet("background-color: #ffffff; border-radius: 10px; padding: 10px;")
        layout_tabela = QVBoxLayout()
        self.table_produtos = QTableWidget()
        # agora mostramos quantidade também
        self.table_produtos.setColumnCount(4)
        self.table_produtos.setHorizontalHeaderLabels(["Produto", "Código", "Preço", "Qtd"])
        self.table_produtos.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout_tabela.addWidget(self.table_produtos)
        card_tabela.setLayout(layout_tabela)
        left_layout.addWidget(card_tabela)

        main_layout.addLayout(left_layout, 3)

        # LADO DIREITO: Carrinho
        card_carrinho = QFrame()
        card_carrinho.setStyleSheet("background-color: #ffffff; border-radius: 10px; padding: 10px;")
        layout_carrinho = QVBoxLayout()
        self.table_carrinho = QTableWidget()
        self.table_carrinho.setColumnCount(4)
        self.table_carrinho.setHorizontalHeaderLabels(["Produto", "Preço Unit.", "Qtd", "Total"])
        self.table_carrinho.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout_carrinho.addWidget(self.table_carrinho)

        self.lbl_total = QLabel("Total: R$ 0,00")
        self.lbl_total.setFont(QFont("Arial", 12, QFont.Bold))
        layout_carrinho.addWidget(self.lbl_total)

        card_carrinho.setLayout(layout_carrinho)
        main_layout.addWidget(card_carrinho, 1)

        # adiciona tudo ao layout principal
        self.layout.addLayout(main_layout)

        # carrega produtos do banco
        self.carregar_produtos()

    # ---------- Funções auxiliares ----------
    def buscar_e_adicionar(self):
        self.buscar_produto()
        if self.produto_atual:
            self.adicionar_carrinho()

    def carregar_produtos(self):
        """Carrega produtos com quantidade atual da tabela produto."""
        self.table_produtos.setRowCount(0)
        self.cursor.execute("SELECT * FROM produto WHERE user_id=?", (self.user['id'],))
        for p in self.cursor.fetchall():
            r = self.table_produtos.rowCount()
            self.table_produtos.insertRow(r)
            nome = p['nome']
            codigo = p.get('codigo_barras') or ""
            preco = p['preco'] or 0.0
            quantidade = p.get('quantidade') or 0
            self.table_produtos.setItem(r, 0, QTableWidgetItem(nome))
            self.table_produtos.setItem(r, 1, QTableWidgetItem(codigo))
            self.table_produtos.setItem(r, 2, QTableWidgetItem(f"R$ {preco:.2f}"))
            self.table_produtos.setItem(r, 3, QTableWidgetItem(str(quantidade)))

    def buscar_produto(self):
        termo = self.input_busca.text().strip()
        if not termo:
            QMessageBox.information(self, "Busca", "Digite um nome ou código.")
            return
        self.cursor.execute("""
            SELECT * FROM produto WHERE user_id=? AND (nome=? OR codigo_barras=?)
        """, (self.user['id'], termo, termo))
        result = self.cursor.fetchone()
        if result:
            self.produto_atual = dict(result)
            qtd_disp = int(result.get('quantidade') or 0)
            self.lbl_produto.setText(f"{result['nome']} - R$ {result['preco']:.2f}  (Qtd: {qtd_disp})")
            # se estoque == 0, não permite adicionar
            self.btn_adicionar.setEnabled(qtd_disp > 0)
        else:
            self.produto_atual = None
            self.lbl_produto.setText("Produto não encontrado")
            self.btn_adicionar.setEnabled(False)

    def adicionar_carrinho(self):
        if not self.produto_atual:
            return
        # valida estoque disponível
        qtd_disp = int(self.produto_atual.get('quantidade') or 0)
        # verifica se já existe no carrinho
        for item in self.carrinho:
            if item["produto_id"] == self.produto_atual["id"]:
                if item["quantidade"] + 1 > qtd_disp:
                    QMessageBox.warning(self, "Estoque", "Quantidade disponível insuficiente.")
                    return
                item["quantidade"] += 1
                break
        else:
            if qtd_disp <= 0:
                QMessageBox.warning(self, "Estoque", "Produto sem estoque disponível!")
                return
            self.carrinho.append({
                "produto_id": self.produto_atual["id"],
                "nome": self.produto_atual["nome"],
                "preco": float(self.produto_atual.get("preco") or 0.0),
                "quantidade": 1
            })

        # atualiza carrinho e limpa busca
        self.atualizar_carrinho()
        self.input_busca.clear()
        self.produto_atual = None
        self.lbl_produto.setText("Produto não selecionado")
        self.btn_adicionar.setEnabled(False)

    def atualizar_carrinho(self):
        self.table_carrinho.setRowCount(0)
        total = 0.0
        for item in self.carrinho:
            r = self.table_carrinho.rowCount()
            self.table_carrinho.insertRow(r)
            self.table_carrinho.setItem(r, 0, QTableWidgetItem(item["nome"]))
            self.table_carrinho.setItem(r, 1, QTableWidgetItem(f"R$ {item['preco']:.2f}"))
            self.table_carrinho.setItem(r, 2, QTableWidgetItem(str(item["quantidade"])))
            total_item = item["preco"] * item["quantidade"]
            self.table_carrinho.setItem(r, 3, QTableWidgetItem(f"R$ {total_item:.2f}"))
            total += total_item
        self.total_carrinho = total
        self.lbl_total.setText(f"Total: R$ {total:.2f}")
        self.atualizar_total()
        # atualiza tabela de produtos (exibe qtd atual)
        self.carregar_produtos()

    def atualizar_total(self):
        # calcula total_final e troco em tempo real
        try:
            desconto = float(self.input_desconto.text() or 0)
        except ValueError:
            desconto = 0.0
        try:
            pago = float(self.input_pago.text() or 0)
        except ValueError:
            pago = 0.0
        tipo = self.combo_tipo.currentText() if hasattr(self, "combo_tipo") else "À VISTA"
        total_final = max(self.total_carrinho - desconto, 0.0)
        if tipo == "A PRAZO":
            total_final *= 1.10  # juros exemplo 10%
        self.total_final = total_final
        self.lbl_final_total.setText(f"Total Final: R$ {total_final:.2f}")
        troco = max(pago - total_final, 0.0)
        self.lbl_troco.setText(f"Troco: R$ {troco:.2f}")

    def finalizar_venda(self):
        if not self.carrinho:
            QMessageBox.warning(self, "Erro", "Carrinho vazio")
            return

        # recalcula (para garantir)
        self.atualizar_total()
        total_final = self.total_final
        forma_pag = self.combo_pagamento.currentText()
        hoje = datetime.date.today().strftime("%Y-%m-%d")

        # registra venda
        self.cursor.execute("INSERT INTO vendas (user_id, data, total) VALUES (?, ?, ?)",
                            (self.user['id'], hoje, total_final))
        venda_id = self.cursor.lastrowid

        # atualiza estoque e registra movimento
        for item in self.carrinho:
            # diminui quantidade do produto
            self.cursor.execute("""
                UPDATE produto SET quantidade = quantidade - ? WHERE id=? AND user_id=?
            """, (item["quantidade"], item["produto_id"], self.user['id']))

            # registra movimento de estoque
            self.cursor.execute("""
                INSERT INTO estoque_movimento (produto_id, tipo, quantidade, data_movimento)
                VALUES (?, 'SAÍDA', ?, ?)
            """, (item["produto_id"], item["quantidade"], hoje))

        # registra entrada no caixa
        self.cursor.execute("""
            INSERT INTO caixa (user_id, data, entrada, saida, saldo)
            VALUES (?, ?, ?, 0, ?)
        """, (self.user['id'], hoje, total_final, total_final))

        self.conn.commit()

        QMessageBox.information(self, "Venda Finalizada", f"Venda ID {venda_id} registrada com sucesso!")

        # limpa carrinho e atualiza telas
        self.carrinho = []
        self.atualizar_carrinho()
        self.input_busca.clear()
        self.produto_atual = None
        self.lbl_produto.setText("Produto não selecionado")
        self.carregar_produtos()