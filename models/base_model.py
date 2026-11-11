from psycopg2 import sql
from psycopg2.extras import RealDictCursor

from conexao import conectar


class BaseModel:

    tabela = None
    campos = ()

    def __init__(self):
        if not self.tabela:
            raise ValueError("A tabela não foi definida")

    # CREATE - Inserir Registro
    def cadastrar(self, **dados):
        self.validar_campos(dados)
        conexao = conectar()

        try:
            with conexao, conexao.cursor() as cursor:
                colunas = list(dados.keys())
                valores = list(dados.values())

                comando = sql.SQL(
                    "INSERT INTO {} ({}) VALUES ({}) RETURNING id"
                ).format(
                    sql.Identifier(self.tabela),
                    sql.SQL(", ").join(map(sql.Identifier, colunas)),
                    sql.SQL(",").join(sql.Placeholder() for _ in valores),
                )

                cursor.execute(comando, valores)
                return cursor.fetchone()[0]  # Retorna o ID do registro inserido
        finally:
            conexao.close()

    # READ - Listar Todos os registros
    def listar(self):
        conexao = conectar()

        try:
            with conexao, conexao.cursor(cursor_factory=RealDictCursor) as cursor:
                comando = sql.SQL("SELECT * FROM {} ORDER BY id").format(
                    sql.Identifier(self.tabela)
                )
                cursor.execute(comando)
                return cursor.fetchall()
        finally:
            conexao.close()

    # READ - Buscar Registro por ID
    def buscar_por_id(self, id):
        conexao = conectar()

        try:
            with conexao, conexao.cursor(cursor_factory=RealDictCursor) as cursor:
                comando = sql.SQL("SELECT * FROM {} WHERE id = %s").format(
                    sql.Identifier(self.tabela)
                )
                cursor.execute(comando, (id,))
                return cursor.fetchone()
        finally:
            conexao.close()

    # UPDATE - Atualizar Registro
    def atualizar(self, id, **dados):
        if not dados:
            raise ValueError("Nenhum dado fornecido para atualização")

        self.validar_campos(dados)
        conexao = conectar()

        try:
            with conexao, conexao.cursor() as cursor:
                colunas = list(dados.keys())
                valores = list(dados.values())

                atualizacoes = sql.SQL(", ").join(
                    sql.SQL("{} = {}").format(sql.Identifier(coluna), sql.Placeholder())
                    for coluna in colunas
                )

                comando = sql.SQL("UPDATE {} SET {} WHERE id = %s").format(
                    sql.Identifier(self.tabela), atualizacoes
                )

                cursor.execute(comando, valores + [id])
                return cursor.rowcount  # Retorna o número de registros atualizados
        finally:
            conexao.close()

    # DELETE - Deletar Registro
    def deletar(self, id):
        conexao = conectar()

        try:
            with conexao, conexao.cursor() as cursor:
                comando = sql.SQL("DELETE FROM {} WHERE id = %s").format(
                    sql.Identifier(self.tabela)
                )
                cursor.execute(comando, (id,))
                return cursor.rowcount  # Retorna o número de registros deletados
        finally:
            conexao.close()

    def validar_campos(self, dados):
        if not dados:
            raise ValueError("Nenhum dado fornecido para validação")

        for campo in dados:
            if campo not in self.campos:
                raise ValueError(f"Campo inválido: {campo}")