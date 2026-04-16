# Adicione 'redirect' e 'url_for' nesta linha
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)


# Função auxiliar para conectar no banco
def conectar_banco():
    caminho_banco = os.path.join(os.path.dirname(__file__), 'banco_ativos.db')
    return sqlite3.connect(caminho_banco)

@app.route('/')
@app.route('/index')
def index():
    # ID de teste que criamos no banco
    ID_LOGADO = '123456789'
    
    conexao = sqlite3.connect('banco_ativos.db')
    cursor = conexao.cursor()
    
    # Busca nome e nível baseados no ID de 9 dígitos
    cursor.execute("SELECT nome_exibicao, nivel FROM usuarios WHERE id_usuario = ?", (ID_LOGADO,))
    usuario = cursor.fetchone()
    conexao.close()

    if usuario:
        return render_template('index.html', user_nome=usuario[0], user_nivel=usuario[1])
    return render_template('index.html', user_nome="Convidado", user_nivel="N/A")

@app.route('/consult', methods=['POST'])
def consult():
    id_buscado = request.form.get('id_busca')

    # Busca no SQLite em vez do dicionário
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("SELECT id_ativo, nome, data_atualizacao, resumo FROM ativos WHERE id_ativo = ?", (id_buscado,))
    resultado = cursor.fetchone()
    conn.close()

    if resultado:
        # Retorna os dados do banco para o seu HTML
        return render_template('consult.html', 
                               id_ativo=resultado[0], 
                               nome=resultado[1], 
                               data=resultado[2], 
                               resumo=resultado[3])
    else:
        return redirect('/index?erro=inexistente')

# Outras rotas (mantenha como estão)
@app.route('/login')
def login(): return render_template('login.html')

@app.route('/newAsset')
def newAsset(): return render_template('newAsset.html')

@app.route('/newUpdate')
def newUpdate(): return render_template('newUpdate.html')

if __name__ == '__main__':
    app.run(debug=True)