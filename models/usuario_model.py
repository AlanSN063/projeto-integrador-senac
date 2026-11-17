import hashlib
import hmac
import os

from psycopg2.extras import RealDictCursor
from conexao import conectar
from models.base_model import BaseModel


class UsuarioModel(BaseModel):
    tabela = "usuario"
    campos = ("nome", "login", "cargo", "ativo", "senha_hash")


    def listar(self):
        conexao = conectar()

        try:
            with conexao.cursor(
                cursor_factory=RealDictCursor
            ) as cursor:

                cursor.execute("""
                    SELECT id, nome, login, cargo, ativo
                    FROM usuario
                    ORDER BY id
                """)

                return cursor.fetchall()

        finally:
            conexao.close()


    @staticmethod
    def gerar_hash(senha):
        salt = os.urandom(16)
        chave = hashlib.pbkdf2_hmac("sha256", senha.encode("utf-8"), salt, 310000)
        return f"pbkdf2_sha256$310000${salt.hex()}${chave.hex()}"

    @staticmethod
    def verificar_senha(senha, senha_hash):
        try:
            algoritmo, iteracoes, salt_hex, hash_hex = senha_hash.split("$")
            if algoritmo != "pbkdf2_sha256":
                return False
            calculado = hashlib.pbkdf2_hmac(
                "sha256", senha.encode("utf-8"), bytes.fromhex(salt_hex), int(iteracoes)
            )
            return hmac.compare_digest(calculado.hex(), hash_hex)
        except (AttributeError, ValueError):
            return False

    def autenticar(self, login, senha):
        conexao = conectar()
        try:
            with conexao.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    "SELECT id, nome, login, cargo, ativo, senha_hash FROM usuario WHERE login = %s",
                    (login,)
                )
                usuario = cursor.fetchone()
            if not usuario or not usuario["ativo"] or not usuario.get("senha_hash"):
                return None
            if self.verificar_senha(senha, usuario["senha_hash"]):
                usuario.pop("senha_hash", None)
                return dict(usuario)
            return None
        finally:
            conexao.close()

    def criar_usuario(self, nome, login, senha, cargo="OPERADOR"):
        return self.cadastrar(
            nome=nome.strip(), login=login.strip(), cargo=cargo,
            ativo=True, senha_hash=self.gerar_hash(senha)
        )
