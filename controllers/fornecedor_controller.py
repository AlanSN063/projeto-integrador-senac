from controllers.cadastro_controller import CadastroController
from models.fornecedor_model import FornecedorModel

class FornecedorController(CadastroController):
    def __init__(self): super().__init__(FornecedorModel())
