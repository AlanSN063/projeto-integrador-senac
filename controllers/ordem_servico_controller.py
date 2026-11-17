from datetime import date
from tkinter import messagebox
from conexao import conectar
from models.ordem_servico_model import OrdemServicoModel
from views.detalhes_ordem_view import DetalhesOrdemView
from views.formulario_ordem_view import FormularioOrdemView


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
        FormularioOrdemView(self.master, on_salvar=self._cadastrar)

    def _cadastrar(self, dados):
        try:
            self.model.cadastrar(**dados, data_abertura=date.today())
            self.on_change()
            messagebox.showinfo("Ordens de serviço", "Ordem cadastrada com sucesso.", parent=self.master)
            return True
        except Exception as exc:
            messagebox.showerror("Erro", f"Não foi possível cadastrar a OS.\n{exc}", parent=self.master)
            return False

    def visualizar(self, numero):
        try:
            registro = self._buscar(numero)
            if not registro:
                messagebox.showwarning("Ordem não encontrada",
                    f"A ordem {numero} não foi encontrada.", parent=self.master)
                return
            DetalhesOrdemView(self.master, registro)
        except Exception as exc:
            messagebox.showerror("Erro ao consultar OS", str(exc), parent=self.master)

    def editar(self, numero):
        try:
            registro = self._buscar(numero)
            if not registro:
                messagebox.showwarning("OS não encontrada", f"A ordem {numero} não foi encontrada.", parent=self.master)
                return
            FormularioOrdemView(self.master, registro=registro,
                               on_salvar=lambda dados: self._atualizar(registro["id"], dados))
        except Exception as exc:
            messagebox.showerror("Erro ao consultar OS", str(exc), parent=self.master)

    def _atualizar(self, registro_id, dados):
        try:
            self.model.atualizar(registro_id, **dados)
            self.on_change()
            messagebox.showinfo("Ordens de serviço", "Ordem atualizada com sucesso.", parent=self.master)
            return True
        except Exception as exc:
            messagebox.showerror("Erro", f"Não foi possível atualizar a OS.\n{exc}", parent=self.master)
            return False

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
