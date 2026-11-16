from datetime import date
from tkinter import messagebox, simpledialog
from conexao import conectar
from models.ordem_servico_model import OrdemServicoModel


class OrdemServicoController:
    STATUS_EXIBICAO = {"ABERTA": "Aberta", "EM_EXECUCAO": "Em Andamento",
                       "CONCLUIDA": "Concluída", "CANCELADA": "Cancelada"}
    STATUS_BANCO = {v: k for k, v in STATUS_EXIBICAO.items()}

    def __init__(self, master=None, model=None, on_change=None):
        self.master = master
        self.model = model or OrdemServicoModel()
        self.on_change = on_change or (lambda: None)

    def listar(self):
        registros = self.model.listar()
        return [(r["numero"], r["cliente_nome"], r["placa_veiculo"],
                 r["data_abertura"].strftime("%d/%m/%Y"),
                 self.STATUS_EXIBICAO.get(r["status"], r["status"])) for r in registros]

    def nova_ordem(self):
        numero = simpledialog.askstring("Nova Ordem", "Número da OS:", parent=self.master)
        if not numero: return
        cliente = simpledialog.askstring("Nova Ordem", "Nome do cliente:", parent=self.master)
        if not cliente: return
        placa = simpledialog.askstring("Nova Ordem", "Placa do veículo:", parent=self.master)
        if not placa: return
        descricao = simpledialog.askstring("Nova Ordem", "Descrição do serviço:", parent=self.master)
        if not descricao: return
        try:
            self.model.cadastrar(numero=numero.strip(), cliente_nome=cliente.strip(),
                placa_veiculo=placa.strip().upper(), descricao_servico=descricao.strip(),
                status="ABERTA", data_abertura=date.today())
            messagebox.showinfo("Ordens de serviço", "Ordem cadastrada com sucesso.", parent=self.master)
            self.on_change()
        except Exception as exc:
            messagebox.showerror("Erro", f"Não foi possível cadastrar a OS.\n{exc}", parent=self.master)

    def visualizar(self, numero):
        registro = self._buscar(numero)
        if registro:
            texto = (f"Número: {registro['numero']}\nCliente: {registro['cliente_nome']}\n"
                     f"Placa: {registro['placa_veiculo']}\nServiço: {registro['descricao_servico']}\n"
                     f"Status: {self.STATUS_EXIBICAO.get(registro['status'], registro['status'])}\n"
                     f"Abertura: {registro['data_abertura']:%d/%m/%Y}")
            messagebox.showinfo("Detalhes da OS", texto, parent=self.master)

    def editar(self, numero):
        registro = self._buscar(numero)
        if not registro: return
        atual = self.STATUS_EXIBICAO.get(registro["status"], "Aberta")
        status = simpledialog.askstring("Editar OS",
            "Novo status (Aberta, Em Andamento, Concluída ou Cancelada):",
            initialvalue=atual, parent=self.master)
        if not status: return
        status = status.strip().title()
        if status not in self.STATUS_BANCO:
            messagebox.showerror("Status inválido", "Informe um dos status apresentados.", parent=self.master)
            return
        try:
            self.model.atualizar(registro["id"], status=self.STATUS_BANCO[status])
            messagebox.showinfo("Ordens de serviço", "Status atualizado.", parent=self.master)
            self.on_change()
        except Exception as exc:
            messagebox.showerror("Erro", str(exc), parent=self.master)

    def excluir(self, numero):
        registro = self._buscar(numero)
        if not registro: return
        if messagebox.askyesno("Excluir OS", f"Deseja excluir a ordem {numero}?", parent=self.master):
            try:
                self.model.deletar(registro["id"])
                self.on_change()
            except Exception as exc:
                messagebox.showerror("Erro", f"Não foi possível excluir.\n{exc}", parent=self.master)

    def _buscar(self, numero):
        conexao = conectar()
        try:
            with conexao.cursor() as cursor:
                cursor.execute("SELECT * FROM ordem_servico WHERE numero = %s", (numero,))
                linha = cursor.fetchone()
                if not linha: return None
                colunas = [d[0] for d in cursor.description]
                return dict(zip(colunas, linha))
        finally:
            conexao.close()
