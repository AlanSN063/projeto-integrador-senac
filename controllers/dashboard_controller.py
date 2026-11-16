from conexao import conectar


class DashboardController:
    def resumo(self):
        conexao = conectar()
        try:
            with conexao.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM produto WHERE ativo = TRUE")
                produtos = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM fornecedor")
                fornecedores = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM ordem_servico")
                ordens = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM movimentacao_estoque")
                movimentacoes = cursor.fetchone()[0]
            return {"Produtos": produtos, "Fornecedores": fornecedores,
                    "Ordens de Serviço": ordens, "Movimentações": movimentacoes}
        finally:
            conexao.close()

    def movimentacoes_recentes(self, limite=8):
        conexao = conectar()
        try:
            with conexao.cursor() as cursor:
                cursor.execute("""
                    SELECT to_char(m.data_movimentacao, 'DD/MM/YYYY HH24:MI'),
                           m.tipo, COALESCE(string_agg(p.nome, ', ' ORDER BY p.nome), '—'),
                           CASE WHEN m.tipo = 'ENTRADA' THEN '+' ELSE '-' END ||
                           COALESCE(SUM(i.quantidade), 0)::text
                    FROM movimentacao_estoque m
                    LEFT JOIN item_movimentacao i ON i.movimentacao_id = m.id
                    LEFT JOIN produto p ON p.id = i.produto_id
                    GROUP BY m.id
                    ORDER BY m.data_movimentacao DESC
                    LIMIT %s
                """, (limite,))
                return cursor.fetchall()
        finally:
            conexao.close()

    def estoque_por_categoria(self):
        conexao = conectar()
        try:
            with conexao.cursor() as cursor:
                cursor.execute("""
                    SELECT c.nome, COALESCE(SUM(
                        CASE WHEN m.tipo = 'ENTRADA' THEN i.quantidade
                             WHEN m.tipo = 'SAIDA' THEN -i.quantidade ELSE 0 END
                    ), 0)::integer AS saldo
                    FROM categoria_produto c
                    LEFT JOIN produto p ON p.categoria_id = c.id
                    LEFT JOIN item_movimentacao i ON i.produto_id = p.id
                    LEFT JOIN movimentacao_estoque m ON m.id = i.movimentacao_id
                    GROUP BY c.id, c.nome ORDER BY c.nome
                """)
                dados = cursor.fetchall()
            total = sum(max(0, linha[1]) for linha in dados)
            return [(nome, max(0, saldo), (max(0, saldo) / total if total else 0))
                    for nome, saldo in dados]
        finally:
            conexao.close()
