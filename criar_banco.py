import sqlite3

# Conecta ao banco (se não existir, ele cria o arquivo)
conexao = sqlite3.connect('banco_ativos.db')
cursor = conexao.cursor()

# Cria a tabela de equipamentos
cursor.execute('''
    CREATE TABLE IF NOT EXISTS ativos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        data_atualizacao TEXT,
        resumo TEXT
    )
''')

# Insere um dado de teste para termos o que ver
cursor.execute('''
    INSERT INTO ativos (nome, data_atualizacao, resumo)
    VALUES ('Caixa de Emenda Óptica CEO-12', '12/03/2026', 'Manutenção preventiva realizada. Tudo OK.')
''')

conexao.commit()
conexao.close()
print("Banco de dados e tabela criados com sucesso!")
