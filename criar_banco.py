import sqlite3

def criar():
    conexao = sqlite3.connect('banco_ativos.db')
    cursor = conexao.cursor()

    # Mantendo sua tabela de ativos (com os códigos de 5 dígitos)
    cursor.execute('DROP TABLE IF EXISTS ativos')
    cursor.execute('''
        CREATE TABLE ativos (
            id_ativo TEXT PRIMARY KEY,
            nome TEXT NOT NULL,
            data_atualizacao TEXT,
            resumo TEXT
        )
    ''')

    # Criando a tabela de usuários com ID de 9 dígitos e senha
    cursor.execute('DROP TABLE IF EXISTS usuarios')
    cursor.execute('''
        CREATE TABLE usuarios (
            id_usuario TEXT PRIMARY KEY, -- ID de 9 dígitos
            nome_exibicao TEXT NOT NULL,
            senha TEXT NOT NULL,          -- No futuro usaremos hash, por enquanto texto puro
            nivel TEXT NOT NULL
        )
    ''')

    # Inserindo seu usuário (Exemplo de ID com 9 dígitos)
    cursor.execute('''
        INSERT INTO usuarios (id_usuario, nome_exibicao, senha, nivel)
        VALUES ('123456789', 'Ewerton Eng', 'admin123', 'Administrador')
    ''')

    # Re-inserindo os ativos de teste
    ativos_exemplo = [
        ('44012', 'Roteador Mikrotik CCR1036', '15/04/2026', 'Uplink 10Gbps OK.'),
        ('88291', 'Switch HP 1920G 24p', '14/04/2026', 'VLAN Gerência rack A3.'),
        ('11504', 'Conversor de Mídia', '10/04/2026', 'Redundância ativa.')
    ]
    cursor.executemany('INSERT INTO ativos VALUES (?,?,?,?)', ativos_exemplo)

    conexao.commit()
    conexao.close()
    print("✅ Banco atualizado: Usuários (9 dígitos) e Ativos (5 dígitos) prontos!")

if __name__ == '__main__':
    criar()