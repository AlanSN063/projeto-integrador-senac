from getpass import getpass
from conexao import conectar
from models.usuario_model import UsuarioModel


def main():
    nome = input("Nome do usuário: ").strip()
    login = input("Login: ").strip()
    senha = getpass("Senha: ")
    confirmar = getpass("Confirme a senha: ")
    if not nome or not login or not senha:
        print("Todos os campos são obrigatórios."); return
    if senha != confirmar:
        print("As senhas não conferem."); return
    # Verifica se a migração foi executada e grava a senha com hash PBKDF2.
    try:
        novo_id = UsuarioModel().criar_usuario(nome, login, senha, "ADMINISTRADOR")
        print(f"Usuário administrador criado. ID: {novo_id}")
    except Exception as exc:
        print(f"Não foi possível criar o usuário: {exc}")

if __name__ == "__main__":
    main()
