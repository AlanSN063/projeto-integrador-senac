from decimal import Decimal, InvalidOperation
from conexao import conectar


class MovimentacaoController:
    """Registra entrada/saída e atualiza o saldo por meio do histórico de itens."""
    TIPOS_MOTIVOS = {
        "ENTRADA": {"COMPRA", "DEVOLUCAO", "AJUSTE"},
        "SAIDA": {"USO_OS", "VENDA", "PERDA", "AJUSTE"},
    }

    def registrar(self, usuario_id, tipo, motivo, itens, fornecedor_id=None, ordem_servico_id=None, observacao=None):
        tipo = (tipo or "").upper()
        motivo = (motivo or "").upper()
        if tipo not in self.TIPOS_MOTIVOS or motivo not in self.TIPOS_MOTIVOS[tipo]:
            raise ValueError("Tipo ou motivo de movimentação inválido.")
        if not itens:
            raise ValueError("Adicione pelo menos um produto à movimentação.")
        if fornecedor_id and tipo != "ENTRADA":
            raise ValueError("Fornecedor só pode ser informado em entradas.")
        if (motivo == "USO_OS") != (ordem_servico_id is not None):
            raise ValueError("Saída por uso em OS exige uma ordem de serviço; outros motivos não aceitam OS.")

        conexao = conectar()
        try:
            with conexao:
                with conexao.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO movimentacao_estoque
                        (usuario_id, fornecedor_id, ordem_servico_id, tipo, motivo, observacao)
                        VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
                    """, (usuario_id, fornecedor_id, ordem_servico_id, tipo, motivo, observacao))
                    movimentacao_id = cursor.fetchone()[0]
                    for item in itens:
                        produto_id = int(item["produto_id"])
                        quantidade = int(item["quantidade"])
                        valor = Decimal(str(item.get("valor_unitario", 0)).replace(",", "."))
                        if quantidade <= 0 or valor < 0:
                            raise ValueError("Quantidade deve ser positiva e valor não pode ser negativo.")
                        if tipo == "SAIDA":
                            cursor.execute("""
                                SELECT COALESCE(SUM(CASE WHEN m.tipo = 'ENTRADA' THEN i.quantidade
                                                         WHEN m.tipo = 'SAIDA' THEN -i.quantidade ELSE 0 END), 0)
                                FROM item_movimentacao i
                                JOIN movimentacao_estoque m ON m.id = i.movimentacao_id
                                WHERE i.produto_id = %s
                            """, (produto_id,))
                            saldo = cursor.fetchone()[0]
                            if saldo < quantidade:
                                raise ValueError(f"Estoque insuficiente para o produto ID {produto_id}. Saldo: {saldo}.")
                        cursor.execute("""
                            INSERT INTO item_movimentacao
                            (movimentacao_id, produto_id, quantidade, valor_unitario)
                            VALUES (%s, %s, %s, %s)
                        """, (movimentacao_id, produto_id, quantidade, valor))
            return movimentacao_id
        finally:
            conexao.close()
