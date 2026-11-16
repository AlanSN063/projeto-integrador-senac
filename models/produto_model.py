from conexao import conectar
from psycopg2.extras import RealDictCursor
from models.base_model import BaseModel


class ProdutoModel(BaseModel):
    tabela = "produto"
    campos = ("categoria_id", "codigo", "nome", "marca", "preco_venda", "estoque_minimo", "ativo")

    def listar_com_estoque(self, termo=None):
        conexao = conectar()
        try:
            with conexao.cursor(cursor_factory=RealDictCursor) as cursor:
                consulta = """
                    SELECT p.id, p.codigo, p.nome, p.marca, p.preco_venda,
                           p.estoque_minimo, p.ativo, c.nome AS categoria,
                           COALESCE(SUM(CASE WHEN m.tipo = 'ENTRADA' THEN i.quantidade
                                             WHEN m.tipo = 'SAIDA' THEN -i.quantidade
                                             ELSE 0 END), 0)::integer AS estoque_atual
                    FROM produto p
                    JOIN categoria_produto c ON c.id = p.categoria_id
                    LEFT JOIN item_movimentacao i ON i.produto_id = p.id
                    LEFT JOIN movimentacao_estoque m ON m.id = i.movimentacao_id
                    WHERE (%s IS NULL OR p.nome ILIKE %s OR p.codigo ILIKE %s)
                    GROUP BY p.id, c.nome
                    ORDER BY p.nome
                """
                cursor.execute(consulta, (termo, f"%{termo}%" if termo else None, f"%{termo}%" if termo else None))
                return cursor.fetchall()
        finally:
            conexao.close()

    def buscar_categoria_id(self, nome):
        conexao = conectar()
        try:
            with conexao.cursor() as cursor:
                cursor.execute("SELECT id FROM categoria_produto WHERE nome = %s", (nome,))
                linha = cursor.fetchone()
                return linha[0] if linha else None
        finally:
            conexao.close()
