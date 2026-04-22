from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
import random
import qrcode
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'sga_projeto_univesp_2026'

# --- FUNÇÕES AUXILIARES ---

def conectar_banco():
    caminho_banco = os.path.join(os.path.dirname(__file__), 'banco_ativos.db')
    return sqlite3.connect(caminho_banco)

def obter_usuario_logado():
    if 'user_id' in session:
        return {
            "nome": session.get('user_nome'),
            "nivel": session.get('user_nivel')
        }
    return None

def gerar_id_unico():
    while True:
        novo_id = str(random.randint(10000, 99999))
        conn = conectar_banco()
        cursor = conn.cursor()
        cursor.execute("SELECT id_ativo FROM ativos WHERE id_ativo = ?", (novo_id,))
        existe = cursor.fetchone()
        conn.close()
        if not existe:
            return novo_id

# --- ROTAS ---

@app.route('/')
@app.route('/index')
def index():
    user = obter_usuario_logado()
    if not user:
        return redirect(url_for('login')) # BLOQUEIO
    return render_template('index.html', user_nome=user['nome'], user_nivel=user['nivel'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form.get('id_usuario')
        senha = request.form.get('senha')

        conn = conectar_banco()
        cursor = conn.cursor()
        cursor.execute("SELECT id_usuario, nome_exibicao, nivel FROM usuarios WHERE id_usuario = ? AND senha = ?", (user_id, senha))
        usuario = cursor.fetchone()
        conn.close()

        if usuario:
            session['user_id'] = usuario[0]
            session['user_nome'] = usuario[1]
            session['user_nivel'] = usuario[2]
            return redirect(url_for('index'))
        else:
            return render_template('login.html', erro="ID ou Senha incorretos!")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/consult', methods=['POST'])
def consult():
    # Proteção rápida mesmo em rotas de processamento
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    id_buscado = request.form.get('id_busca')
    return redirect(url_for('consult_get', id_ativo=id_buscado))

@app.route('/consult/<id_ativo>')
def consult_get(id_ativo):
    user = obter_usuario_logado()
    if not user:
        return redirect(url_for('login')) # BLOQUEIO

    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("SELECT id_ativo, nome, data_atualizacao, resumo FROM ativos WHERE id_ativo = ?", (id_ativo,))
    resultado = cursor.fetchone()
    conn.close()

    if resultado:
        return render_template('consult.html', 
                               user_nome=user['nome'], 
                               user_nivel=user['nivel'],
                               id_ativo=resultado[0], 
                               nome=resultado[1], 
                               data=resultado[2], 
                               resumo=resultado[3])
    return redirect('/index?erro=inexistente')

@app.route('/newAsset', methods=['GET', 'POST'])
def newAsset():
    user = obter_usuario_logado()
    if not user:
        return redirect(url_for('login')) # BLOQUEIO
    
    if request.method == 'POST':
        nome = request.form.get('equipamento')
        descricao = request.form.get('descricao')
        data_formatada = request.form.get('data_escondida')
        id_gerado = gerar_id_unico()

        pasta_qr = os.path.join('static', 'qrcodes')
        if not os.path.exists(pasta_qr):
            os.makedirs(pasta_qr)
        
        caminho_qr = f'static/qrcodes/qr_{id_gerado}.png'
        img = qrcode.make(id_gerado)
        img.save(caminho_qr)

        conn = conectar_banco()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO ativos (id_ativo, nome, data_atualizacao, resumo) VALUES (?, ?, ?, ?)",
                       (id_gerado, nome, data_formatada, descricao))
        conn.commit()
        conn.close()

        return render_template('newAsset.html', 
                               user_nome=user['nome'], 
                               user_nivel=user['nivel'],
                               sucesso=True, 
                               id_ativo=id_gerado, 
                               qr_code=caminho_qr,
                               nome=nome,
                               data=data_formatada,
                               descricao=descricao)

    return render_template('newAsset.html', user_nome=user['nome'], user_nivel=user['nivel'], sucesso=False)

@app.route('/newUpdate/<id_ativo>')
def newUpdate(id_ativo):
    user = obter_usuario_logado()
    if not user:
        return redirect(url_for('login')) # BLOQUEIO

    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("SELECT nome FROM ativos WHERE id_ativo = ?", (id_ativo,))
    ativo = cursor.fetchone()
    conn.close()
    
    if ativo:
        return render_template('newUpdate.html', 
                               user_nome=user['nome'], 
                               user_nivel=user['nivel'], 
                               id_ativo=id_ativo, 
                               nome=ativo[0])
    return redirect('/index?erro=inexistente')

@app.route('/saveUpdate', methods=['POST'])
def saveUpdate():
    if 'user_id' not in session:
        return redirect(url_for('login')) # BLOQUEIO

    id_ativo = request.form.get('id_ativo')
    nova_data = request.form.get('data_escondida')
    novo_texto = request.form.get('resumo_atualizacao')

    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("SELECT resumo FROM ativos WHERE id_ativo = ?", (id_ativo,))
    resultado = cursor.fetchone()
    resumo_antigo = resultado[0] if resultado[0] else ""
    historico_atualizado = f"{nova_data}\n{novo_texto}\n\n{resumo_antigo}"
    cursor.execute("UPDATE ativos SET resumo = ?, data_atualizacao = ? WHERE id_ativo = ?", 
                    (historico_atualizado, nova_data, id_ativo))
    conn.commit()
    conn.close()
    
    return redirect(url_for('consult_get', id_ativo=id_ativo))

@app.after_request
def add_header(response):
    """
    Adiciona cabeçalhos para impedir que o navegador armazene cache das páginas.
    Isso garante que, ao deslogar, o usuário não consiga voltar e ver os dados.
    """
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response
if __name__ == '__main__':
    app.run(debug=True)