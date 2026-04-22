import sqlite3
import os

def adicionar_coluna_senha():
    caminho_banco = os.path.join(os.path.dirname(__file__), 'banco_ativos.db')
    conn = sqlite3.connect(caminho_banco)
    cursor = conn.cursor()

    try:
        # 1. Adiciona a coluna senha na tabela usuarios
        cursor.execute("ALTER TABLE usuarios ADD COLUMN senha TEXT;")
        print("Coluna 'senha' adicionada com sucesso!")
        
        # 2. Define uma senha padrão para o seu usuário de teste
        # Ajuste o ID '123456789' se o seu for diferente
        cursor.execute("UPDATE usuarios SET senha = '123' WHERE id_usuario = '123456789';")
        print("Senha padrão '123' definida para o usuário 123456789.")
        
        conn.commit()
    except sqlite3.OperationalError:
        print("Aviso: A coluna 'senha' já existe ou a tabela não foi encontrada.")
    finally:
        conn.close()

if __name__ == '__main__':
    adicionar_coluna_senha()