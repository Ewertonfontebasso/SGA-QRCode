import sqlite3
import os

def cadastrar_novo_usuario(id_user, nome, nivel, senha):
    caminho_banco = os.path.join(os.path.dirname(__file__), 'banco_ativos.db')
    conn = sqlite3.connect(caminho_banco)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO usuarios (id_usuario, nome_exibicao, nivel, senha)
            VALUES (?, ?, ?, ?)
        """, (id_user, nome, nivel, senha))
        
        conn.commit()
        print(f"✅ Usuário '{nome}' cadastrado com sucesso!")
        print(f"ID: {id_user} | Senha: {senha}")
    
    except sqlite3.IntegrityError:
        print(f"❌ Erro: O ID '{id_user}' já está em uso.")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    print("--- Cadastro de Novo Usuário SGA ---")
    
    # Você pode alterar esses dados para criar quem você quiser
    novo_id = input("Digite o ID (ex: 987654321): ")
    novo_nome = input("Digite o Nome de Exibição: ")
    novo_nivel = input("Digite o Nível (ex: Admin, Técnico, Supervisor): ")
    nova_senha = input("Digite a Senha: ")

    cadastrar_novo_usuario(novo_id, novo_nome, novo_nivel, nova_senha)