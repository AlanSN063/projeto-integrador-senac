from controllers.cadastro_controller import CadastroController
from models.categoria_produto_model import CategoriaProdutoModel

class CategoriaController(CadastroController):
    def __init__(self): super().__init__(CategoriaProdutoModel())
