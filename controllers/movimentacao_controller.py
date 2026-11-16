from decimal import Decimal, InvalidOperation

from models.movimentacao_model import MovimentacaoModel


class MovimentacaoController:
    MOTIVOS = {
        "ENTRADA": ("COMPRA", "DEVOLUCAO", "AJUSTE"),
        "SAIDA": ("USO_OS", "VENDA", "PERDA", "AJUSTE"),
    }

    def __init__(self, model=None):
        self.model = model or MovimentacaoModel()

    def listar(self, termo=None):
        return self.model.listar_historico(termo)

    def listar_produtos(self):
        return self.model.listar_produtos_com_estoque()

    def listar_fornecedores(self):
        return self.model.listar_fornecedores()

    def listar_ordens_servico(self):
        return self.model.listar_ordens_servico()

    def cadastrar(self, usuario_id, dados):
        if not usuario_id:
            raise ValueError("Não foi possível identificar o usuário logado.")

        tipo = (dados.get("tipo") or "").strip().upper()
        motivo = (dados.get("motivo") or "").strip().upper()

        if tipo not in self.MOTIVOS:
            raise ValueError("Selecione um tipo de movimentação válido.")
        if motivo not in self.MOTIVOS[tipo]:
            raise ValueError("O motivo não é permitido para o tipo selecionado.")

        fornecedor_id = dados.get("fornecedor_id") or None
        ordem_servico_id = dados.get("ordem_servico_id") or None

        if tipo == "SAIDA":
            fornecedor_id = None
        if motivo == "USO_OS" and not ordem_servico_id:
            raise ValueError("Selecione a ordem de serviço para a saída por uso em OS.")
        if motivo != "USO_OS":
            ordem_servico_id = None

        itens_recebidos = dados.get("itens") or []
        if not itens_recebidos:
            raise ValueError("Adicione pelo menos um produto.")

        itens = []
        produtos_repetidos = set()

        for item in itens_recebidos:
            try:
                produto_id = int(item.get("produto_id"))
                quantidade = int(item.get("quantidade"))
                valor = Decimal(str(item.get("valor_unitario")).replace(",", "."))
            except (TypeError, ValueError, InvalidOperation):
                raise ValueError("Produto, quantidade e valor unitário devem ser válidos.")

            if produto_id in produtos_repetidos:
                raise ValueError("Não repita o mesmo produto na movimentação.")
            produtos_repetidos.add(produto_id)

            if quantidade <= 0:
                raise ValueError("A quantidade deve ser maior que zero.")
            if not valor.is_finite() or valor < 0:
                raise ValueError("O valor unitário não pode ser negativo.")

            itens.append({
                "produto_id": produto_id,
                "quantidade": quantidade,
                "valor_unitario": valor,
            })

        observacao = (dados.get("observacao") or "").strip() or None

        return self.model.cadastrar(
            usuario_id=int(usuario_id),
            tipo=tipo,
            motivo=motivo,
            itens=itens,
            fornecedor_id=int(fornecedor_id) if fornecedor_id else None,
            ordem_servico_id=int(ordem_servico_id) if ordem_servico_id else None,
            observacao=observacao,
        )
