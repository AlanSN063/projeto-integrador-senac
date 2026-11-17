"""Formulário de cadastro e edição de OS em uma janela CustomTkinter."""
import re
import customtkinter as ctk
from tkinter import messagebox
from .theme import COLORS


class FormularioOrdemView(ctk.CTkToplevel):
    STATUS = {
        "Aberta": "ABERTA",
        "Em andamento": "EM_EXECUCAO",
        "Concluída": "CONCLUIDA",
        "Cancelada": "CANCELADA",
    }

    def __init__(self, master, on_salvar, registro=None):
        super().__init__(master)
        self.registro = registro
        self.on_salvar = on_salvar
        self.editando = registro is not None
        self.title("Editar ordem de serviço" if self.editando else "Nova ordem de serviço")
        self.geometry("790x660")
        self.minsize(640, 570)
        self.configure(fg_color=COLORS["background"])
        self.transient(master)
        self.protocol("WM_DELETE_WINDOW", self.destroy)

        self.update_idletasks()
        largura, altura = 790, 660
        x = max(0, master.winfo_rootx() + (master.winfo_width() - largura) // 2)
        y = max(0, master.winfo_rooty() + (master.winfo_height() - altura) // 2)
        self.geometry(f"{largura}x{altura}+{x}+{y}")

        topo = ctk.CTkFrame(self, fg_color=COLORS["white"], corner_radius=0)
        topo.pack(fill="x")
        titulo = "Editar ordem de serviço" if self.editando else "Nova ordem de serviço"
        ctk.CTkLabel(topo, text=titulo, font=("Poppins", 23, "bold"),
                     text_color=COLORS["text"], anchor="w").pack(fill="x", padx=30, pady=(23, 2))
        subtitulo = ("Atualize os dados e acompanhe o andamento do serviço."
                     if self.editando else "Preencha os dados para registrar uma nova ordem.")
        ctk.CTkLabel(topo, text=subtitulo, font=("Roboto", 13),
                     text_color=COLORS["muted"], anchor="w").pack(fill="x", padx=30, pady=(0, 22))

        corpo = ctk.CTkScrollableFrame(self, fg_color="transparent")
        corpo.pack(fill="both", expand=True, padx=20, pady=(18, 12))
        cartao = ctk.CTkFrame(corpo, fg_color=COLORS["white"], corner_radius=12,
                              border_width=1, border_color=COLORS["border"])
        cartao.pack(fill="x", padx=2, pady=2)
        ctk.CTkLabel(cartao, text="Informações da ordem", font=("Poppins", 16, "bold"),
                     text_color=COLORS["text"], anchor="w").pack(fill="x", padx=22, pady=(22, 15))

        grade = ctk.CTkFrame(cartao, fg_color="transparent")
        grade.pack(fill="x", padx=22)
        grade.grid_columnconfigure((0, 1), weight=1, uniform="colunas")

        self.numero = self._campo(grade, "Número da OS *", 0, 0, "Ex.: OS-ALN-005")
        self.cliente = self._campo(grade, "Cliente *", 0, 1, "Nome completo do cliente")
        self.placa = self._campo(grade, "Placa do veículo *", 1, 0, "Ex.: ABC1D23")

        status_bloco = ctk.CTkFrame(grade, fg_color="transparent")
        status_bloco.grid(row=1, column=1, sticky="ew", padx=5, pady=(0, 15))
        ctk.CTkLabel(status_bloco, text="Status", font=("Roboto", 12, "bold"),
                     text_color=COLORS["text"], anchor="w").pack(fill="x", pady=(0, 6))
        self.status = ctk.CTkOptionMenu(
            status_bloco, values=list(self.STATUS), height=39,
            fg_color=COLORS["graphite"], button_color=COLORS["graphite"],
            button_hover_color=COLORS["charcoal"],
            font=("Roboto", 13), dropdown_font=("Roboto", 13))
        self.status.pack(fill="x")
        self.status.set("Aberta")
        if not self.editando:
            self.status.configure(state="disabled")

        ctk.CTkLabel(cartao, text="Descrição do serviço *", font=("Roboto", 12, "bold"),
                     text_color=COLORS["text"], anchor="w").pack(fill="x", padx=27, pady=(3, 6))
        self.descricao = ctk.CTkTextbox(cartao, height=132, border_width=1,
                                        border_color=COLORS["border"],
                                        fg_color="#FAFAFA", font=("Roboto", 13), wrap="word")
        self.descricao.pack(fill="x", padx=27, pady=(0, 12))
        ctk.CTkLabel(cartao, text="* Campos obrigatórios", text_color=COLORS["muted"],
                     font=("Roboto", 11), anchor="w").pack(fill="x", padx=27, pady=(0, 20))

        if registro:
            self._preencher(self.numero, registro.get("numero"))
            self._preencher(self.cliente, registro.get("cliente_nome"))
            self._preencher(self.placa, registro.get("placa_veiculo"))
            self.descricao.insert("1.0", str(registro.get("descricao_servico") or ""))
            status_atual = registro.get("status")
            self.status.set(next((nome for nome, codigo in self.STATUS.items()
                                  if codigo == status_atual), "Aberta"))

        rodape = ctk.CTkFrame(self, fg_color=COLORS["white"], corner_radius=0)
        rodape.pack(fill="x")
        ctk.CTkButton(rodape, text="Salvar alterações" if self.editando else "Cadastrar ordem",
                      width=175, height=41, font=("Roboto", 13, "bold"),
                      fg_color=COLORS["red"], hover_color=COLORS["dark_red"],
                      command=self._salvar).pack(side="right", padx=(8, 25), pady=17)
        ctk.CTkButton(rodape, text="Cancelar", width=115, height=41,
                      fg_color=COLORS["soft_gray"], hover_color=COLORS["border"],
                      text_color=COLORS["text"], command=self.destroy).pack(side="right", pady=17)

        self.bind("<Escape>", lambda _: self.destroy())
        self.after(100, self._ativar)

    @staticmethod
    def _campo(parent, titulo, linha, coluna, dica):
        bloco = ctk.CTkFrame(parent, fg_color="transparent")
        bloco.grid(row=linha, column=coluna, sticky="ew", padx=5, pady=(0, 15))
        ctk.CTkLabel(bloco, text=titulo, font=("Roboto", 12, "bold"),
                     text_color=COLORS["text"], anchor="w").pack(fill="x", pady=(0, 6))
        entrada = ctk.CTkEntry(bloco, height=39, placeholder_text=dica,
                               fg_color="#FAFAFA", border_color=COLORS["border"],
                               font=("Roboto", 13))
        entrada.pack(fill="x")
        return entrada

    @staticmethod
    def _preencher(campo, valor):
        campo.insert(0, str(valor or ""))

    def _salvar(self):
        numero = self.numero.get().strip()
        cliente = self.cliente.get().strip()
        placa = self.placa.get().strip().upper().replace("-", "")
        descricao = self.descricao.get("1.0", "end-1c").strip()
        if not all((numero, cliente, placa, descricao)):
            messagebox.showwarning("Dados obrigatórios", "Preencha todos os campos obrigatórios.", parent=self)
            return
        if len(numero) > 50 or len(cliente) > 150:
            messagebox.showwarning("Campo muito longo", "Verifique o tamanho do número da OS e do nome do cliente.", parent=self)
            return
        if not re.fullmatch(r"[A-Z]{3}[0-9][A-Z0-9][0-9]{2}", placa):
            messagebox.showwarning("Placa inválida", "Informe uma placa brasileira válida no formato ABC1234 ou ABC1D23.", parent=self)
            return
        dados = {"numero": numero, "cliente_nome": cliente,
                 "placa_veiculo": placa, "descricao_servico": descricao,
                 "status": self.STATUS[self.status.get()]}
        # O controller retorna True somente após a persistência no banco.
        if self.on_salvar(dados):
            self.destroy()

    def _ativar(self):
        if self.winfo_exists():
            self.lift()
            self.grab_set()
            self.numero.focus_set()
