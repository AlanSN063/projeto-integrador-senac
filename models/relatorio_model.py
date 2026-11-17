
from conexao import conectar
from psycopg2.extras import RealDictCursor


class RelatorioModel:
    """Consultas para os relatórios do controle de estoque."""

    def _consultar(self, consulta, parametros=None):
        conexao = conectar()

        try:
            with conexao.cursor(
                cursor_factory=RealDictCursor
            ) as cursor:

                cursor.execute(
                    consulta,
                    parametros or ()
                )

                return cursor.fetchall()

        finally:
            conexao.close()

    # ==========================================
    # ESTOQUE ATUAL
    # ==========================================

    def estoque_atual(self):
        consulta = """
            SELECT
                p.codigo,
                p.nome AS produto,
                c.nome AS categoria,
                COALESCE(SUM(
                    CASE
                        WHEN m.tipo = 'ENTRADA'
                            THEN i.quantidade

                        WHEN m.tipo = 'SAIDA'
                            THEN -i.quantidade

                        ELSE 0
                    END
                ), 0)::integer AS estoque_atual,

                p.estoque_minimo

            FROM produto p

            LEFT JOIN categoria_produto c
                ON c.id = p.categoria_id

            LEFT JOIN item_movimentacao i
                ON i.produto_id = p.id

            LEFT JOIN movimentacao_estoque m
                ON m.id = i.movimentacao_id

            WHERE p.ativo = TRUE

            GROUP BY
                p.id,
                p.codigo,
                p.nome,
                c.nome,
                p.estoque_minimo

            ORDER BY p.nome
        """

        return self._consultar(consulta)

    # ==========================================
    # ESTOQUE BAIXO
    # ==========================================

    def estoque_baixo(self):
        consulta = """
            SELECT
                p.codigo,
                p.nome AS produto,
                c.nome AS categoria,

                COALESCE(SUM(
                    CASE
                        WHEN m.tipo = 'ENTRADA'
                            THEN i.quantidade

                        WHEN m.tipo = 'SAIDA'
                            THEN -i.quantidade

                        ELSE 0
                    END
                ), 0)::integer AS estoque_atual,

                p.estoque_minimo

            FROM produto p

            LEFT JOIN categoria_produto c
                ON c.id = p.categoria_id

            LEFT JOIN item_movimentacao i
                ON i.produto_id = p.id

            LEFT JOIN movimentacao_estoque m
                ON m.id = i.movimentacao_id

            WHERE p.ativo = TRUE

            GROUP BY
                p.id,
                p.codigo,
                p.nome,
                c.nome,
                p.estoque_minimo

            HAVING COALESCE(SUM(
                CASE
                    WHEN m.tipo = 'ENTRADA'
                        THEN i.quantidade

                    WHEN m.tipo = 'SAIDA'
                        THEN -i.quantidade

                    ELSE 0
                END
            ), 0) <= p.estoque_minimo

            ORDER BY estoque_atual ASC, p.nome
        """

        return self._consultar(consulta)

    # ==========================================
    # HISTÓRICO DE MOVIMENTAÇÕES
    # ==========================================

    def movimentacoes(self):
        consulta = """
            SELECT
                m.data_movimentacao,
                m.tipo,
                m.motivo,
                p.nome AS produto,
                i.quantidade,
                u.nome AS usuario

            FROM movimentacao_estoque m

            INNER JOIN usuario u
                ON u.id = m.usuario_id

            INNER JOIN item_movimentacao i
                ON i.movimentacao_id = m.id

            INNER JOIN produto p
                ON p.id = i.produto_id

            ORDER BY
                m.data_movimentacao DESC,
                m.id DESC,
                p.nome
        """

        return self._consultar(consulta)

    # ==========================================
    # ESTOQUE POR CATEGORIA
    # ==========================================

    def estoque_por_categoria(self):
        consulta = """
            WITH saldo_produtos AS (
                SELECT
                    p.id,
                    p.categoria_id,

                    COALESCE(SUM(
                        CASE
                            WHEN m.tipo = 'ENTRADA'
                                THEN i.quantidade

                            WHEN m.tipo = 'SAIDA'
                                THEN -i.quantidade

                            ELSE 0
                        END
                    ), 0)::integer AS estoque_atual

                FROM produto p

                LEFT JOIN item_movimentacao i
                    ON i.produto_id = p.id

                LEFT JOIN movimentacao_estoque m
                    ON m.id = i.movimentacao_id

                WHERE p.ativo = TRUE

                GROUP BY p.id, p.categoria_id
            )

            SELECT
                c.nome AS categoria,

                COUNT(sp.id)::integer AS total_produtos,

                COALESCE(
                    SUM(sp.estoque_atual), 0
                )::integer AS total_unidades

            FROM categoria_produto c

            LEFT JOIN saldo_produtos sp
                ON sp.categoria_id = c.id

            GROUP BY c.id, c.nome

            ORDER BY c.nome
        """

        return self._consultar(consulta)

    # ==========================================
    # SELEÇÃO DO RELATÓRIO
    # ==========================================

    def gerar(self, tipo):

        relatorios = {
            "estoque_atual": self.estoque_atual,
            "estoque_baixo": self.estoque_baixo,
            "movimentacoes": self.movimentacoes,
            "categorias": self.estoque_por_categoria
        }

        if tipo not in relatorios:
            raise ValueError(
                "Tipo de relatório inválido."
            )

        return relatorios[tipo]()
