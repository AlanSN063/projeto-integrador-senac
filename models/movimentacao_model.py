from decimal import Decimal
from psycopg2 import sql
from psycopg2.extras import RealDictCursor

from conexao import conectar


class MovimentacaoModel:
    """Persistência das movimentações e cálculo do estoque pelo histórico."""

    TIPOS = ("ENTRADA", "SAIDA")
    MOTIVOS = {
        "ENTRADA": ("COMPRA", "DEVOLUCAO", "AJUSTE"),
        "SAIDA": ("USO_OS", "VENDA", "PERDA", "AJUSTE"),
    }

    def listar_produtos_com_estoque(self):
        conexao = conectar()
        try:
            with conexao.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT
                        p.id, p.codigo, p.nome, p.marca,
                        p.preco_venda, p.estoque_minimo,
                        COALESCE(SUM(
                            CASE
                                WHEN m.tipo = 'ENTRADA' THEN i.quantidade
                                WHEN m.tipo = 'SAIDA' THEN -i.quantidade
                                ELSE 0
                            END
                        ), 0)::integer AS estoque_atual
                    FROM produto p
                    LEFT JOIN item_movimentacao i ON i.produto_id = p.id
                    LEFT JOIN movimentacao_estoque m ON m.id = i.movimentacao_id
                    WHERE p.ativo = TRUE
                    GROUP BY p.id
                    ORDER BY p.nome
                """)
                return cursor.fetchall()
        finally:
            conexao.close()

    def listar_fornecedores(self):
        conexao = conectar()
        try:
            with conexao.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT id, razao_social
                    FROM fornecedor
                    ORDER BY razao_social
                """)
                return cursor.fetchall()
        finally:
            conexao.close()

    def listar_ordens_servico(self):
        conexao = conectar()
        try:
            with conexao.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT id, numero, cliente_nome, placa_veiculo, status
                    FROM ordem_servico
                    WHERE status IN ('ABERTA', 'EM_EXECUCAO')
                    ORDER BY data_abertura DESC, numero
                """)
                return cursor.fetchall()
        finally:
            conexao.close()

    def listar_historico(self, termo=None):
        conexao = conectar()
        try:
            with conexao.cursor(cursor_factory=RealDictCursor) as cursor:
                consulta = """
                    SELECT
                        m.id, m.tipo, m.motivo, m.data_movimentacao,
                        m.observacao, u.nome AS usuario_nome,
                        f.razao_social AS fornecedor_nome,
                        os.numero AS ordem_numero,
                        COALESCE(
                            STRING_AGG(
                                p.nome || ' (' || i.quantidade::text || ')',
                                ', ' ORDER BY p.nome
                            ),
                            ''
                        ) AS itens,
                        COALESCE(SUM(i.quantidade), 0)::integer AS quantidade_total
                    FROM movimentacao_estoque m
                    JOIN usuario u ON u.id = m.usuario_id
                    LEFT JOIN fornecedor f ON f.id = m.fornecedor_id
                    LEFT JOIN ordem_servico os ON os.id = m.ordem_servico_id
                    LEFT JOIN item_movimentacao i ON i.movimentacao_id = m.id
                    LEFT JOIN produto p ON p.id = i.produto_id
                """
                parametros = ()
                if termo:
                    consulta += """
                        WHERE
                            CAST(m.id AS TEXT) ILIKE %s
                            OR m.tipo ILIKE %s
                            OR m.motivo ILIKE %s
                            OR COALESCE(f.razao_social, '') ILIKE %s
                            OR COALESCE(os.numero, '') ILIKE %s
                            OR COALESCE(p.nome, '') ILIKE %s
                    """
                    padrao = f"%{termo}%"
                    parametros = (padrao,) * 6

                consulta += """
                    GROUP BY m.id, u.nome, f.razao_social, os.numero
                    ORDER BY m.data_movimentacao DESC, m.id DESC
                """
                cursor.execute(consulta, parametros)
                return cursor.fetchall()
        finally:
            conexao.close()

    def obter_estoque_produto(self, produto_id, cursor=None):
        """Calcula o saldo atual. Pode reutilizar cursor de uma transação."""
        comando = """
            SELECT COALESCE(SUM(
                CASE
                    WHEN m.tipo = 'ENTRADA' THEN i.quantidade
                    WHEN m.tipo = 'SAIDA' THEN -i.quantidade
                    ELSE 0
                END
            ), 0)::integer AS saldo
            FROM item_movimentacao i
            JOIN movimentacao_estoque m ON m.id = i.movimentacao_id
            WHERE i.produto_id = %s
        """
        if cursor is not None:
            cursor.execute(comando, (produto_id,))
            return cursor.fetchone()["saldo"]

        conexao = conectar()
        try:
            with conexao.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(comando, (produto_id,))
                return cur.fetchone()["saldo"]
        finally:
            conexao.close()

    def cadastrar(self, usuario_id, tipo, motivo, itens,
                  fornecedor_id=None, ordem_servico_id=None, observacao=None):
        """
        Cria cabeçalho e itens em uma única transação.
        Bloqueia as linhas dos produtos para serializar saídas concorrentes.
        """
        if not itens:
            raise ValueError("Adicione pelo menos um produto à movimentação.")

        conexao = conectar()
        try:
            with conexao:
                with conexao.cursor(cursor_factory=RealDictCursor) as cursor:
                    ids = sorted({int(item["produto_id"]) for item in itens})

                    # Todas as operações de movimentação bloqueiam os produtos
                    # em ordem crescente para reduzir risco de deadlock.
                    cursor.execute(
                        "SELECT id FROM produto WHERE id = ANY(%s) AND ativo = TRUE "
                        "ORDER BY id FOR UPDATE",
                        (ids,)
                    )
                    encontrados = {row["id"] for row in cursor.fetchall()}
                    if encontrados != set(ids):
                        raise ValueError("Um ou mais produtos não existem ou estão inativos.")

                    if tipo == "SAIDA":
                        for item in itens:
                            saldo = self.obter_estoque_produto(
                                int(item["produto_id"]), cursor
                            )
                            if int(item["quantidade"]) > saldo:
                                raise ValueError(
                                    f"Estoque insuficiente para o produto ID "
                                    f"{item['produto_id']}. Disponível: {saldo}."
                                )

                    cursor.execute("""
                        INSERT INTO movimentacao_estoque
                            (usuario_id, fornecedor_id, ordem_servico_id,
                             tipo, motivo, observacao)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        RETURNING id
                    """, (
                        usuario_id, fornecedor_id, ordem_servico_id,
                        tipo, motivo, observacao
                    ))
                    movimentacao_id = cursor.fetchone()["id"]

                    for item in itens:
                        cursor.execute("""
                            INSERT INTO item_movimentacao
                                (movimentacao_id, produto_id, quantidade, valor_unitario)
                            VALUES (%s, %s, %s, %s)
                        """, (
                            movimentacao_id,
                            int(item["produto_id"]),
                            int(item["quantidade"]),
                            Decimal(str(item["valor_unitario"]))
                        ))

                    return movimentacao_id
        finally:
            conexao.close()
