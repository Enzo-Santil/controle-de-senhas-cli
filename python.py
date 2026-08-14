"""
Cofre de Senhas Local (CLI) - Python
"""

import sqlite3
import os

DB_NAME = "controle_senhas.db"


# ---------------- Conexão e criação do banco ---------------- #

def conectar():
    """
    Abre conexão com banco SQLite e garante que a tabela exista.
    """
    conexao = sqlite3.connect(DB_NAME)
    cursor = conexao.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS senhas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        site TEXT NOT NULL,
        login TEXT NOT NULL,
        senha TEXT NOT NULL
    )
    """)

    conexao.commit()
    return conexao


# ---------------- Funções auxiliares ---------------- #

def ler_texto(mensagem):
    """
    Lê um texto do usuário.
    """
    return input(mensagem).strip()


def ler_inteiro(mensagem):
    """
    Lê um inteiro do usuário.
    """
    try:
        return int(input(mensagem).strip())
    except ValueError:
        return None


def confirmar(mensagem):
    """
    Solicita confirmação (S/N).
    """
    resposta = input(f"{mensagem} (S/N): ").strip().lower()
    return resposta == "s"


def senha_mascarada(senha, mostrar):
    """
    Retorna a senha real ou mascarada.
    """
    return senha if mostrar else "*" * len(senha)


# ---------------- Operações CRUD ---------------- #

def cadastrar(conexao):
    """
    Cadastra uma nova credencial.
    """

    print("\n--- Cadastrar Nova Credencial ---")

    site = ler_texto("Digite o site: ")
    login = ler_texto("Digite o login: ")
    senha = ler_texto("Digite a senha: ")

    if not site or not login or not senha:
        print("[ERRO] Todos os campos são obrigatórios.")
        return

    try:
        cursor = conexao.cursor()

        cursor.execute(
            "INSERT INTO senhas (site, login, senha) VALUES (?, ?, ?)",
            (site, login, senha)
        )

        conexao.commit()

        print(
            f"[OK] Credencial cadastrada com sucesso! (ID: {cursor.lastrowid})"
        )

    except sqlite3.Error as erro:
        print(f"[ERRO] Não foi possível cadastrar: {erro}")


def listar(conexao):
    """
    Lista todas as credenciais.
    """

    print("\n--- Listar Credenciais ---")

    try:
        cursor = conexao.cursor()

        cursor.execute(
            "SELECT id, site, login, senha FROM senhas ORDER BY id"
        )

        registros = cursor.fetchall()

        if not registros:
            print("[INFO] Nenhuma credencial cadastrada.")
            return

        mostrar = confirmar("Deseja revelar as senhas?")

        print("\n")
        print(f"{'ID':<5} {'Site':<20} {'Login':<20} {'Senha'}")
        print("-" * 70)

        for id_, site, login, senha in registros:
            print(
                f"{id_:<5} "
                f"{site:<20} "
                f"{login:<20} "
                f"{senha_mascarada(senha, mostrar)}"
            )

    except sqlite3.Error as erro:
        print(f"[ERRO] Não foi possível listar: {erro}")


def atualizar(conexao):
    """
    Atualiza login e/ou senha de uma credencial.
    """

    print("\n--- Atualizar Credencial ---")

    id_ = ler_inteiro("Informe o ID da credencial: ")

    if id_ is None:
        print("[ERRO] ID inválido.")
        return

    try:
        cursor = conexao.cursor()

        cursor.execute(
            "SELECT site, login, senha FROM senhas WHERE id = ?",
            (id_,)
        )

        registro = cursor.fetchone()

        if registro is None:
            print("[ERRO] Credencial não encontrada.")
            return

        site_atual, login_atual, senha_atual = registro

        print(f"\nEditando credencial do site: {site_atual}")

        novo_login = input(
            f"Novo login (atual: {login_atual}): "
        ).strip()

        nova_senha = input(
            f"Nova senha (atual: {senha_atual}): "
        ).strip()

        if not novo_login:
            novo_login = login_atual

        if not nova_senha:
            nova_senha = senha_atual

        cursor.execute(
            """
            UPDATE senhas
            SET login = ?, senha = ?
            WHERE id = ?
            """,
            (novo_login, nova_senha, id_)
        )

        conexao.commit()

        print("[OK] Credencial atualizada com sucesso!")

    except sqlite3.Error as erro:
        print(f"[ERRO] Falha ao atualizar: {erro}")


def excluir(conexao):
    """
    Exclui uma credencial pelo ID.
    """

    print("\n--- Excluir Credencial ---")

    id_ = ler_inteiro("Informe o ID da credencial: ")

    if id_ is None:
        print("[ERRO] ID inválido.")
        return

    try:
        cursor = conexao.cursor()

        cursor.execute(
            "SELECT site, login FROM senhas WHERE id = ?",
            (id_,)
        )

        registro = cursor.fetchone()

        if registro is None:
            print("[ERRO] ID não encontrado.")
            return

        site, login = registro

        print(
            f"Credencial selecionada -> Site: {site} | Login: {login}"
        )

        if not confirmar(
            "Tem certeza que deseja excluir esta credencial?"
        ):
            print("Operação cancelada.")
            return

        cursor.execute(
            "DELETE FROM senhas WHERE id = ?",
            (id_,)
        )

        conexao.commit()

        print("[OK] Credencial excluída com sucesso!")

    except sqlite3.Error as erro:
        print(f"[ERRO] Falha ao excluir: {erro}")


# ---------------- Menu Principal ---------------- #

def menu():
    """
    Mostra o menu principal.
    """

    print("\n========== CONTROLE DE SENHAS ==========")
    print("1 - Cadastrar credencial")
    print("2 - Listar credenciais")
    print("3 - Atualizar credencial")
    print("4 - Excluir credencial")
    print("5 - Sair")

    return input("Escolha uma opção: ").strip()


def main():
    """
    Função principal.
    """

    print(f"Banco de dados: {os.path.abspath(DB_NAME)}")

    conexao = conectar()

    try:
        while True:

            opcao = menu()

            if opcao == "1":
                cadastrar(conexao)

            elif opcao == "2":
                listar(conexao)

            elif opcao == "3":
                atualizar(conexao)

            elif opcao == "4":
                excluir(conexao)

            elif opcao == "5":
                print(
                    "\nSaindo... até logo! "
                    "Suas senhas estão seguras."
                )
                break

            else:
                print(
                    "[ERRO] Opção inválida. "
                    "Escolha uma opção de 1 a 5."
                )

    finally:
        conexao.close()
        print("Conexão com o banco finalizada!")


# ---------------- Ponto de entrada ---------------- #

if __name__ == "__main__":
    main()