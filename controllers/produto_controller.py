from decimal import Decimal, InvalidOperation
from models.produto_model import ProdutoModel
from models.categoria_produto_model import CategoriaProdutoModel


class ProdutoController:
    def __init__(self, produto_model=None, categoria_model=None):
        self.produtos = produto_model or ProdutoModel()
        self.categorias = categoria_model or CategoriaProdutoModel()

    def listar(self, termo=None):
        return self.produtos.listar_com_estoque(termo or None)

    def listar_categorias(self):
        return [item["nome"] for item in self.categorias.listar()]

    def salvar(self, dados):
        nome = (dados.get("nome") or "").strip()
        codigo = (dados.get("codigo") or "").strip()
        categoria = (dados.get("categoria") or "").strip()
        marca = (dados.get("marca") or "").strip() or None
        if not nome or not codigo or not categoria:
            raise ValueError("Nome, código e categoria são obrigatórios.")
        categoria_id = self.produtos.buscar_categoria_id(categoria)
        if not categoria_id:
            raise ValueError("Selecione uma categoria cadastrada.")
        try:
            preco = Decimal(str(dados.get("preco_venda")).replace(",", "."))
            estoque_minimo = int(dados.get("estoque_minimo"))
        except (InvalidOperation, TypeError, ValueError):
            raise ValueError("Preço e estoque mínimo devem ser numéricos.")
        if preco < 0 or estoque_minimo < 0:
            raise ValueError("Preço e estoque mínimo não podem ser negativos.")
        return self.produtos.cadastrar(
            categoria_id=categoria_id, codigo=codigo, nome=nome, marca=marca,
            preco_venda=preco, estoque_minimo=estoque_minimo, ativo=True
        )
