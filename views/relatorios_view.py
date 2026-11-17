"""Painel visual de relatórios, com gráficos alimentados pelas consultas existentes."""
from collections import Counter, defaultdict
from datetime import datetime
import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator
from .theme import COLORS, FONTS
from .components import PageHeader


class RelatoriosView(ctk.CTkFrame):
    RELATORIOS = {
        "Estoque atual": {"tipo": "estoque_atual", "colunas": [("codigo", "Código"), ("produto", "Produto"), ("categoria", "Categoria"), ("estoque_atual", "Estoque"), ("estoque_minimo", "Mínimo")]},
        "Estoque baixo": {"tipo": "estoque_baixo", "colunas": [("codigo", "Código"), ("produto", "Produto"), ("categoria", "Categoria"), ("estoque_atual", "Estoque atual"), ("estoque_minimo", "Estoque mínimo")]},
        "Movimentações": {"tipo": "movimentacoes", "colunas": [("data_movimentacao", "Data"), ("tipo", "Tipo"), ("motivo", "Motivo"), ("produto", "Produto"), ("quantidade", "Quantidade"), ("usuario", "Responsável")]},
        "Estoque por categoria": {"tipo": "categorias", "colunas": [("categoria", "Categoria"), ("total_produtos", "Produtos"), ("total_unidades", "Unidades")]},
    }
    RED = "#FF0000"
    DARK = "#414141"
    LIGHT = "#D9D9D9"

    def __init__(self, master, on_carregar=None, **kwargs):
        super().__init__(master, fg_color=COLORS["background"], **kwargs)
        self.on_carregar = on_carregar
        self.dados = []
        self.relatorio_atual = "Estoque atual"
        self._canvas_grafico = None
        self._figura = None
        PageHeader(self, "Relatórios", "Indicadores e gráficos do estoque",
                   "chart").pack(fill="x", padx=22, pady=(22, 12))

        corpo = ctk.CTkFrame(self, fg_color="transparent")
        corpo.pack(fill="both", expand=True, padx=22, pady=(0, 16))
        corpo.grid_columnconfigure(0, weight=1)
        corpo.grid_rowconfigure(1, weight=1)
        self._criar_filtros(corpo)

        self.rolagem = ctk.CTkScrollableFrame(
            corpo, fg_color="transparent", corner_radius=0)
        self.rolagem.grid(row=1, column=0, sticky="nsew")
        self.rolagem.grid_columnconfigure(0, weight=1)
        self.metricas_frame = ctk.CTkFrame(
            self.rolagem, fg_color="transparent")
        self.metricas_frame.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        self.metricas_frame.grid_columnconfigure(
            (0, 1, 2), weight=1, uniform="indicador")

        self.grafico_card = self._card(self.rolagem)
        self.grafico_card.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        self.grafico_card.grid_columnconfigure(0, weight=1)
        self.titulo_grafico = ctk.CTkLabel(self.grafico_card, text="Análise visual", font=(
            "Poppins", 16, "bold"), text_color=COLORS["text"])
        self.titulo_grafico.grid(
            row=0, column=0, sticky="w", padx=18, pady=(14, 3))
        self.subtitulo_grafico = ctk.CTkLabel(
            self.grafico_card, text="", font=FONTS["small"], text_color=COLORS["muted"])
        self.subtitulo_grafico.grid(row=1, column=0, sticky="w", padx=18)
        self.grafico_host = ctk.CTkFrame(
            self.grafico_card, fg_color="white", height=285)
        self.grafico_host.grid(
            row=2, column=0, sticky="ew", padx=12, pady=(8, 14))
        self.grafico_host.grid_propagate(False)
        self.grafico_host.grid_columnconfigure(0, weight=1)
        self.grafico_host.grid_rowconfigure(0, weight=1)

        self.tabela_card = self._card(self.rolagem)
        self.tabela_card.grid(row=2, column=0, sticky="ew")
        self.tabela_card.grid_columnconfigure(0, weight=1)
        header = ctk.CTkFrame(self.tabela_card, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=18, pady=(14, 8))
        header.grid_columnconfigure(0, weight=1)
        self.titulo_tabela = ctk.CTkLabel(header, text="Registros", font=(
            "Poppins", 15, "bold"), text_color=COLORS["text"])
        self.titulo_tabela.grid(row=0, column=0, sticky="w")
        self.total_registros = ctk.CTkLabel(
            header, text="", font=FONTS["small"], text_color=COLORS["muted"])
        self.total_registros.grid(row=0, column=1)
        self.tabela = ctk.CTkScrollableFrame(
            self.tabela_card, fg_color="white", height=245)
        self.tabela.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 12))
        self.feedback = ctk.CTkLabel(
            self.rolagem, text="", font=FONTS["small"], text_color=COLORS["muted"], anchor="w")
        self.feedback.grid(row=3, column=0, sticky="ew", pady=(6, 0))
        self.carregar_relatorio()

    def _card(self, parent):
        return ctk.CTkFrame(parent, fg_color=COLORS["white"], corner_radius=10, border_width=1, border_color=COLORS["border"])

    def _criar_filtros(self, parent):
        painel = self._card(parent)
        painel.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        painel.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(painel, text="Selecionar relatório", font=("Poppins", 14, "bold"), text_color=COLORS["text"]).grid(
            row=0, column=0, columnspan=3, sticky="w", padx=16, pady=(10, 4))
        self.seletor = ctk.CTkOptionMenu(painel, values=list(self.RELATORIOS), width=245, height=36, fg_color=COLORS["red"], button_color=COLORS[
                                         "dark_red"], button_hover_color=COLORS["graphite"], font=FONTS["body"], command=self._selecionar_relatorio)
        self.seletor.grid(row=1, column=0, sticky="w", padx=16, pady=(0, 12))
        self.seletor.set("Estoque atual")
        ctk.CTkButton(painel, text="Atualizar relatório", width=150, height=36, fg_color=COLORS["red"], hover_color=COLORS[
                      "dark_red"], font=FONTS["button"], command=self.carregar_relatorio).grid(row=1, column=1, padx=8, pady=(0, 12))
        ctk.CTkButton(painel, text="Limpar", width=90, height=36, fg_color=COLORS["graphite"], hover_color=COLORS[
                      "charcoal"], font=FONTS["button"], command=self.limpar).grid(row=1, column=2, padx=(6, 16), pady=(0, 12))

    def _selecionar_relatorio(self, escolha):
        self.relatorio_atual = escolha
        self.carregar_relatorio()

    def carregar_relatorio(self):
        self.relatorio_atual = self.seletor.get()
        if not self.on_carregar:
            self._mensagem(
                "Callback de relatórios não configurado.", erro=True)
            return
        try:
            tipo = self.RELATORIOS[self.relatorio_atual]["tipo"]
            self.dados = list(self.on_carregar(tipo) or [])
            self._renderizar()
            self._mensagem("Relatório atualizado com dados do banco de dados.")
        except Exception as exc:
            self.dados = []
            self._renderizar()
            self._mensagem(f"Erro ao gerar relatório: {exc}", erro=True)

    @staticmethod
    def _numero(valor):
        try:
            return float(valor or 0)
        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def _inteiro(valor):
        return f"{int(valor):,}".replace(",", ".")

    def _indicadores(self):
        tipo = self.RELATORIOS[self.relatorio_atual]["tipo"]
        if tipo in ("estoque_atual", "estoque_baixo"):
            saldo = sum(self._numero(d.get("estoque_atual"))
                        for d in self.dados)
            abaixo = sum(self._numero(d.get("estoque_atual")) <= self._numero(
                d.get("estoque_minimo")) for d in self.dados)
            return [("Produtos listados", len(self.dados)), ("Unidades em estoque", saldo), ("No mínimo ou abaixo", abaixo)]
        if tipo == "movimentacoes":
            entradas = sum(self._numero(d.get("quantidade")) for d in self.dados if str(
                d.get("tipo", "")).upper() == "ENTRADA")
            saidas = sum(self._numero(d.get("quantidade"))
                         for d in self.dados if str(d.get("tipo", "")).upper() == "SAIDA")
            return [("Itens movimentados", entradas + saidas), ("Unidades de entrada", entradas), ("Unidades de saída", saidas)]
        return [("Categorias", len(self.dados)), ("Produtos cadastrados", sum(self._numero(d.get("total_produtos")) for d in self.dados)), ("Unidades totais", sum(self._numero(d.get("total_unidades")) for d in self.dados))]

    def _renderizar(self):
        for child in self.metricas_frame.winfo_children():
            child.destroy()
        for i, (titulo, numero) in enumerate(self._indicadores()):
            cartao = self._card(self.metricas_frame)
            cartao.grid(row=0, column=i, sticky="ew", padx=(
                0 if i == 0 else 5, 0 if i == 2 else 5))
            ctk.CTkLabel(cartao, text=titulo, font=FONTS["small"], text_color=COLORS["muted"]).pack(
                anchor="w", padx=17, pady=(11, 0))
            ctk.CTkLabel(cartao, text=self._inteiro(numero), font=("Poppins", 25, "bold"),
                         text_color=self.RED if i == 2 else COLORS["text"]).pack(anchor="w", padx=17, pady=(0, 11))
        self.titulo_tabela.configure(
            text=f"Detalhamento · {self.relatorio_atual}")
        self.total_registros.configure(text=f"{len(self.dados)} registros")
        self._renderizar_grafico()
        self._renderizar_tabela()

    @staticmethod
    def _estilo_eixo(ax):
        ax.set_facecolor("#FFFFFF")
        for borda in ax.spines.values():
            borda.set_visible(False)
        ax.grid(axis="x", color="#ECECEC", linewidth=0.8)
        ax.set_axisbelow(True)
        ax.tick_params(axis="both", labelsize=9,
                       length=0, colors="#444444", pad=7)
        ax.xaxis.set_major_locator(MaxNLocator(integer=True, nbins=6))

    @staticmethod
    def _encurtar(valor, limite=30):
        texto = str(valor or "Sem identificação")
        return texto if len(texto) <= limite else texto[:limite - 1] + "…"

    def _renderizar_grafico(self):
        if self._canvas_grafico is not None:
            self._canvas_grafico.get_tk_widget().destroy()
            self._canvas_grafico = None
        if self._figura is not None:
            self._figura.clear()
            self._figura = None
        for widget in self.grafico_host.winfo_children():
            widget.destroy()
        tipo = self.RELATORIOS[self.relatorio_atual]["tipo"]
        subtitulos = {
            "estoque_atual": "Produtos com maior quantidade em estoque (até 10)",
            "estoque_baixo": "Comparação entre saldo atual e estoque mínimo (até 10)",
            "movimentacoes": "Quantidade de unidades movimentadas por dia (últimos 14 dias com registros)",
            "categorias": "Comparativo de unidades por categoria",
        }
        self.titulo_grafico.configure(text=self.relatorio_atual)
        self.subtitulo_grafico.configure(text=subtitulos[tipo])
        if not self.dados:
            ctk.CTkLabel(self.grafico_host, text="Sem dados disponíveis para gerar o gráfico.",
                         font=FONTS["body"], text_color=COLORS["muted"]).grid(row=0, column=0)
            return
        fig = Figure(figsize=(10, 2.85), dpi=100, facecolor="white")
        ax = fig.add_subplot(111)
        self._estilo_eixo(ax)
        if tipo in ("estoque_atual", "estoque_baixo"):
            valores = sorted(self.dados, key=lambda d: self._numero(
                d.get("estoque_atual")), reverse=(tipo == "estoque_atual"))[:10]
            valores.reverse()
            nomes = [self._encurtar(d.get("produto"), 27) for d in valores]
            posicoes = list(range(len(valores)))
            if tipo == "estoque_atual":
                ax.barh(posicoes, [self._numero(d.get("estoque_atual"))
                        for d in valores], color=self.RED, height=0.57)
            else:
                atuais = [self._numero(d.get("estoque_atual"))
                          for d in valores]
                minimos = [self._numero(d.get("estoque_minimo"))
                           for d in valores]
                ax.barh([i - 0.18 for i in posicoes], atuais,
                        color=self.RED, height=0.34, label="Atual")
                ax.barh([i + 0.18 for i in posicoes], minimos,
                        color=self.DARK, height=0.34, label="Mínimo")
                ax.legend(loc="lower right", frameon=False, fontsize=9)
            ax.set_yticks(posicoes, nomes)
            fig.subplots_adjust(left=0.27, right=0.97, top=0.94, bottom=0.12)
        elif tipo == "categorias":
            valores = sorted(self.dados, key=lambda d: self._numero(
                d.get("total_unidades")), reverse=True)[:12]
            valores.reverse()
            ax.barh(range(len(valores)), [self._numero(
                d.get("total_unidades")) for d in valores], color=self.RED, height=0.56)
            ax.set_yticks(range(len(valores)), [self._encurtar(
                d.get("categoria"), 26) for d in valores])
            fig.subplots_adjust(left=0.27, right=0.97, top=0.94, bottom=0.12)
        else:
            agrupados = defaultdict(lambda: {"ENTRADA": 0, "SAIDA": 0})
            for linha in self.dados:
                data = linha.get("data_movimentacao")
                if isinstance(data, datetime):
                    dia = data.date()
                elif hasattr(data, "strftime"):
                    dia = data
                else:
                    try:
                        dia = datetime.fromisoformat(str(data)).date()
                    except (ValueError, TypeError):
                        continue
                classe = str(linha.get("tipo", "")).upper()
                if classe in ("ENTRADA", "SAIDA"):
                    agrupados[dia][classe] += self._numero(
                        linha.get("quantidade"))
            dias = sorted(agrupados)[-14:]
            if not dias:
                ctk.CTkLabel(self.grafico_host, text="Não há datas válidas para o gráfico.",
                             font=FONTS["body"]).grid(row=0, column=0)
                return
            x = list(range(len(dias)))
            ax.bar([i - 0.19 for i in x], [agrupados[d]["ENTRADA"]
                   for d in dias], width=0.37, color=self.DARK, label="Entradas")
            ax.bar([i + 0.19 for i in x], [agrupados[d]["SAIDA"]
                   for d in dias], width=0.37, color=self.RED, label="Saídas")
            ax.set_xticks(x, [d.strftime("%d/%m")
                          for d in dias], rotation=35, ha="right")
            ax.yaxis.set_major_locator(MaxNLocator(integer=True, nbins=5))
            ax.legend(loc="upper right", frameon=False, fontsize=9)
            ax.grid(axis="y", color="#ECECEC", linewidth=0.8)
            ax.grid(axis="x", visible=False)
            fig.subplots_adjust(left=0.06, right=0.98, top=0.95, bottom=0.22)
        self._figura = fig
        self._canvas_grafico = FigureCanvasTkAgg(fig, master=self.grafico_host)
        self._canvas_grafico.draw()
        self._canvas_grafico.get_tk_widget().grid(row=0, column=0, sticky="nsew")

    def _renderizar_tabela(self):
        for widget in self.tabela.winfo_children():
            widget.destroy()
        colunas = self.RELATORIOS[self.relatorio_atual]["colunas"]
        for indice, (_, titulo) in enumerate(colunas):
            self.tabela.grid_columnconfigure(indice, weight=1, uniform="col")
            ctk.CTkLabel(self.tabela, text=titulo, font=("Roboto", 12, "bold"), text_color=COLORS["text"], fg_color=COLORS["table_header"], corner_radius=4, anchor="w").grid(
                row=0, column=indice, sticky="ew", padx=2, pady=3, ipady=8)
        if not self.dados:
            ctk.CTkLabel(self.tabela, text="Nenhum registro encontrado para este relatório.",
                         font=FONTS["body"], text_color=COLORS["muted"]).grid(row=1, column=0, columnspan=len(colunas), pady=24)
            return
        for linha, registro in enumerate(self.dados, start=1):
            for coluna, (chave, _) in enumerate(colunas):
                valor = registro.get(chave)
                if valor is None:
                    valor = "—"
                elif hasattr(valor, "strftime"):
                    valor = valor.strftime("%d/%m/%Y %H:%M")
                elif isinstance(valor, float):
                    valor = f"{valor:.2f}"
                ctk.CTkLabel(self.tabela, text=self._encurtar(valor, 40), font=FONTS["body"], text_color=COLORS["text"], anchor="w").grid(
                    row=linha, column=coluna, sticky="ew", padx=8, pady=7)

    def limpar(self):
        self.seletor.set("Estoque atual")
        self.relatorio_atual = "Estoque atual"
        self.dados = []
        self._renderizar()
        self._mensagem("")

    def _mensagem(self, texto, erro=False):
        self.feedback.configure(
            text=texto, text_color=COLORS["red"] if erro else COLORS["green"])
