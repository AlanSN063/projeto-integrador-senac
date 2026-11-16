import customtkinter as ctk
from tkinter import messagebox


class MovimentacoesView(ctk.CTkFrame):
    """Cadastro e histórico de entradas e saídas do estoque."""

    MOTIVOS = {
        "ENTRADA": ["COMPRA", "DEVOLUCAO", "AJUSTE"],
        "SAIDA": ["USO_OS", "VENDA", "PERDA", "AJUSTE"],
    }

    def __init__(self, master, produtos=None, fornecedores=None, ordens=None,
                 historico=None, on_salvar=None, on_listar=None,
                 on_carregar_auxiliares=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.produtos = produtos or []
        self.fornecedores = fornecedores or []
        self.ordens = ordens or []
        self.historico = historico or []
        self.on_salvar = on_salvar or (lambda dados: False)
        self.on_listar = on_listar
        self.on_carregar_auxiliares = on_carregar_auxiliares
        self.itens = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            self, text="Movimentações de estoque",
            font=("Poppins", 24, "bold")
        ).grid(row=0, column=0, sticky="w", padx=22, pady=(22, 4))

        ctk.CTkLabel(
            self, text="Registre entradas, saídas e consulte o histórico.",
            font=("Roboto", 13), text_color="gray"
        ).grid(row=1, column=0, sticky="w", padx=22, pady=(0, 14))

        corpo = ctk.CTkFrame(self, fg_color="transparent")
        corpo.grid(row=2, column=0, sticky="nsew", padx=22, pady=(0, 20))
        corpo.grid_columnconfigure(0, weight=1)
        corpo.grid_rowconfigure(1, weight=1)

        self._criar_formulario(corpo)
        self._criar_historico(corpo)
        self._renderizar_itens()
        self._renderizar_historico(self.historico)

    def _criar_formulario(self, master):
        form = ctk.CTkFrame(master, corner_radius=10)
        form.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        for col in range(4):
            form.grid_columnconfigure(col, weight=1)

        ctk.CTkLabel(form, text="Nova movimentação",
                     font=("Poppins", 17, "bold")).grid(
            row=0, column=0, columnspan=4, sticky="w", padx=16, pady=(14, 8)
        )

        ctk.CTkLabel(form, text="Tipo").grid(row=1, column=0, sticky="w", padx=12)
        self.tipo = ctk.CTkOptionMenu(
            form, values=["ENTRADA", "SAIDA"], command=self._tipo_alterado
        )
        self.tipo.grid(row=2, column=0, sticky="ew", padx=10, pady=(3, 10))

        ctk.CTkLabel(form, text="Motivo").grid(row=1, column=1, sticky="w", padx=12)
        self.motivo = ctk.CTkOptionMenu(
            form, values=self.MOTIVOS["ENTRADA"]
        )
        self.motivo.grid(row=2, column=1, sticky="ew", padx=10, pady=(3, 10))

        ctk.CTkLabel(form, text="Fornecedor (opcional)").grid(
            row=1, column=2, sticky="w", padx=12
        )
        self.fornecedor = ctk.CTkOptionMenu(
            form, values=self._opcoes_fornecedores()
        )
        self.fornecedor.grid(row=2, column=2, sticky="ew", padx=10, pady=(3, 10))

        ctk.CTkLabel(form, text="Ordem de serviço (para USO_OS)").grid(
            row=1, column=3, sticky="w", padx=12
        )
        self.ordem = ctk.CTkOptionMenu(
            form, values=self._opcoes_ordens()
        )
        self.ordem.grid(row=2, column=3, sticky="ew", padx=10, pady=(3, 10))

        ctk.CTkLabel(form, text="Produto").grid(row=3, column=0, sticky="w", padx=12)
        self.produto = ctk.CTkOptionMenu(
            form, values=self._opcoes_produtos()
        )
        self.produto.grid(row=4, column=0, sticky="ew", padx=10, pady=(3, 10))

        ctk.CTkLabel(form, text="Quantidade").grid(row=3, column=1, sticky="w", padx=12)
        self.quantidade = ctk.CTkEntry(form, placeholder_text="Ex.: 5")
        self.quantidade.grid(row=4, column=1, sticky="ew", padx=10, pady=(3, 10))

        ctk.CTkLabel(form, text="Valor unitário").grid(row=3, column=2, sticky="w", padx=12)
        self.valor = ctk.CTkEntry(form, placeholder_text="Ex.: 25,90")
        self.valor.grid(row=4, column=2, sticky="ew", padx=10, pady=(3, 10))

        ctk.CTkButton(
            form, text="Adicionar item", command=self._adicionar_item
        ).grid(row=4, column=3, sticky="ew", padx=10, pady=(3, 10))

        self.itens_frame = ctk.CTkFrame(form, fg_color="transparent")
        self.itens_frame.grid(
            row=5, column=0, columnspan=4, sticky="ew", padx=12, pady=4
        )
        self.itens_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(form, text="Observação").grid(
            row=6, column=0, sticky="w", padx=12
        )
        self.observacao = ctk.CTkEntry(
            form, placeholder_text="Observações opcionais"
        )
        self.observacao.grid(
            row=7, column=0, columnspan=3, sticky="ew",
            padx=10, pady=(3, 10)
        )

        botoes = ctk.CTkFrame(form, fg_color="transparent")
        botoes.grid(row=7, column=3, sticky="e", padx=10, pady=(3, 10))
        ctk.CTkButton(
            botoes, text="Registrar movimentação",
            command=self._salvar
        ).pack(side="left", padx=3)
        ctk.CTkButton(
            botoes, text="Limpar", fg_color="gray",
            command=self._limpar
        ).pack(side="left", padx=3)

    def _criar_historico(self, master):
        painel = ctk.CTkFrame(master, corner_radius=10)
        painel.grid(row=1, column=0, sticky="nsew")
        painel.grid_columnconfigure(0, weight=1)
        painel.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            painel, text="Histórico de movimentações",
            font=("Poppins", 17, "bold")
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(14, 8))

        busca_frame = ctk.CTkFrame(painel, fg_color="transparent")
        busca_frame.grid(row=1, column=0, sticky="ew", padx=14, pady=(0, 8))
        busca_frame.grid_columnconfigure(0, weight=1)
        self.busca = ctk.CTkEntry(
            busca_frame, placeholder_text="Pesquisar por tipo, motivo, produto, fornecedor ou OS"
        )
        self.busca.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.busca.bind("<Return>", lambda _e: self._buscar())
        ctk.CTkButton(
            busca_frame, text="Pesquisar", width=100,
            command=self._buscar
        ).grid(row=0, column=1)

        self.historico_frame = ctk.CTkScrollableFrame(
            painel, fg_color="transparent"
        )
        self.historico_frame.grid(
            row=2, column=0, sticky="nsew", padx=12, pady=(0, 12)
        )
        self.historico_frame.grid_columnconfigure(0, weight=1)

    def _opcoes_produtos(self):
        return [
            f'{p["id"]} | {p["codigo"]} | {p["nome"]} (saldo: {p["estoque_atual"]})'
            for p in self.produtos
        ] or ["Nenhum produto ativo"]

    def _opcoes_fornecedores(self):
        return [""] + [
            f'{f["id"]} | {f["razao_social"]}' for f in self.fornecedores
        ]

    def _opcoes_ordens(self):
        return [""] + [
            f'{o["id"]} | {o["numero"]} | {o["cliente_nome"]}'
            for o in self.ordens
        ]

    def _tipo_alterado(self, tipo):
        motivos = self.MOTIVOS[tipo]
        self.motivo.configure(values=motivos)
        self.motivo.set(motivos[0])
        if tipo == "SAIDA":
            self.fornecedor.set("")

    def _adicionar_item(self):
        produto_texto = self.produto.get()
        if produto_texto.startswith("Nenhum"):
            messagebox.showwarning("Produto", "Não há produtos ativos cadastrados.", parent=self)
            return
        try:
            produto_id = int(produto_texto.split("|", 1)[0].strip())
            quantidade = int(self.quantidade.get().strip())
            valor = float(self.valor.get().strip().replace(",", "."))
            if quantidade <= 0 or valor < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Dados inválidos",
                "Informe uma quantidade maior que zero e um valor unitário não negativo.",
                parent=self
            )
            return

        if any(item["produto_id"] == produto_id for item in self.itens):
            messagebox.showwarning(
                "Produto repetido", "Esse produto já foi adicionado.", parent=self
            )
            return

        produto = next(p for p in self.produtos if p["id"] == produto_id)
        self.itens.append({
            "produto_id": produto_id,
            "nome": produto["nome"],
            "quantidade": quantidade,
            "valor_unitario": valor,
        })
        self.quantidade.delete(0, "end")
        self.valor.delete(0, "end")
        self._renderizar_itens()

    def _renderizar_itens(self):
        for widget in self.itens_frame.winfo_children():
            widget.destroy()
        if not self.itens:
            ctk.CTkLabel(
                self.itens_frame, text="Nenhum produto adicionado.",
                text_color="gray"
            ).grid(row=0, column=0, sticky="w", pady=5)
            return

        for indice, item in enumerate(self.itens):
            linha = ctk.CTkFrame(self.itens_frame, corner_radius=6)
            linha.grid(row=indice, column=0, sticky="ew", pady=3)
            linha.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(
                linha,
                text=f'{item["nome"]} — Qtd.: {item["quantidade"]} — '
                     f'Unit.: R$ {item["valor_unitario"]:.2f}'
            ).grid(row=0, column=0, sticky="w", padx=8, pady=6)
            ctk.CTkButton(
                linha, text="Remover", width=75, height=26,
                fg_color="#B91C1C",
                command=lambda i=indice: self._remover_item(i)
            ).grid(row=0, column=1, padx=6, pady=4)

    def _remover_item(self, indice):
        self.itens.pop(indice)
        self._renderizar_itens()

    def _salvar(self):
        if not self.itens:
            messagebox.showwarning(
                "Movimentação", "Adicione pelo menos um produto.", parent=self
            )
            return

        tipo = self.tipo.get()
        motivo = self.motivo.get()
        fornecedor_texto = self.fornecedor.get()
        ordem_texto = self.ordem.get()

        fornecedor_id = (
            int(fornecedor_texto.split("|", 1)[0].strip())
            if fornecedor_texto else None
        )
        ordem_id = (
            int(ordem_texto.split("|", 1)[0].strip())
            if ordem_texto else None
        )

        if tipo == "SAIDA":
            fornecedor_id = None
        if motivo == "USO_OS" and not ordem_id:
            messagebox.showwarning(
                "Ordem de serviço",
                "Selecione uma ordem de serviço para motivo USO_OS.",
                parent=self
            )
            return
        if motivo != "USO_OS":
            ordem_id = None

        dados = {
            "tipo": tipo,
            "motivo": motivo,
            "fornecedor_id": fornecedor_id,
            "ordem_servico_id": ordem_id,
            "observacao": self.observacao.get().strip(),
            "itens": [
                {
                    "produto_id": item["produto_id"],
                    "quantidade": item["quantidade"],
                    "valor_unitario": item["valor_unitario"],
                }
                for item in self.itens
            ],
        }

        try:
            resultado = self.on_salvar(dados)
            if resultado:
                messagebox.showinfo(
                    "Movimentações",
                    f"Movimentação registrada com sucesso! ID: {resultado}",
                    parent=self
                )
                self._limpar()
                self.atualizar()
            else:
                messagebox.showerror(
                    "Movimentações",
                    "Não foi possível registrar a movimentação.",
                    parent=self
                )
        except Exception as exc:
            messagebox.showerror(
                "Erro ao registrar movimentação", str(exc), parent=self
            )

    def _limpar(self):
        self.itens.clear()
        self.observacao.delete(0, "end")
        self._renderizar_itens()

    def _buscar(self):
        if self.on_listar:
            try:
                self.historico = self.on_listar(self.busca.get().strip() or None)
                self._renderizar_historico(self.historico)
            except Exception as exc:
                messagebox.showerror("Erro", str(exc), parent=self)

    def atualizar(self):
        if self.on_carregar_auxiliares:
            dados = self.on_carregar_auxiliares()
            self.produtos = dados["produtos"]
            self.fornecedores = dados["fornecedores"]
            self.ordens = dados["ordens"]
            self.produto.configure(values=self._opcoes_produtos())
            self.fornecedor.configure(values=self._opcoes_fornecedores())
            self.ordem.configure(values=self._opcoes_ordens())
        if self.on_listar:
            self.historico = self.on_listar(None)
            self._renderizar_historico(self.historico)

    def _renderizar_historico(self, registros):
        for widget in self.historico_frame.winfo_children():
            widget.destroy()
        if not registros:
            ctk.CTkLabel(
                self.historico_frame, text="Nenhuma movimentação encontrada.",
                text_color="gray"
            ).grid(row=0, column=0, pady=18)
            return

        for indice, registro in enumerate(registros):
            data = registro["data_movimentacao"]
            data_texto = data.strftime("%d/%m/%Y %H:%M") if hasattr(data, "strftime") else str(data)
            texto = (
                f'#{registro["id"]} | {registro["tipo"]} - {registro["motivo"]} | '
                f'{data_texto}\n'
                f'Produtos: {registro["itens"] or "—"}\n'
                f'Usuário: {registro["usuario_nome"]} | '
                f'Fornecedor: {registro["fornecedor_nome"] or "—"} | '
                f'OS: {registro["ordem_numero"] or "—"}'
            )
            card = ctk.CTkFrame(self.historico_frame, corner_radius=7)
            card.grid(row=indice, column=0, sticky="ew", pady=4)
            card.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(
                card, text=texto, justify="left", anchor="w",
                wraplength=900
            ).grid(row=0, column=0, sticky="ew", padx=10, pady=8)
