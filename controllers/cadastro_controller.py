class CadastroController:
    """Controller CRUD genérico para modelos derivados de BaseModel."""
    def __init__(self, model):
        self.model = model

    def listar(self): return self.model.listar()
    def buscar(self, registro_id): return self.model.buscar_por_id(registro_id)
    def cadastrar(self, **dados): return self.model.cadastrar(**dados)
    def atualizar(self, registro_id, **dados): return self.model.atualizar(registro_id, **dados)
    def excluir(self, registro_id): return self.model.deletar(registro_id)
