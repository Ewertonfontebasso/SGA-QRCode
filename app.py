from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
import random
import qrcode
from functools import wraps
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'sga_projeto_univesp_2026'

# --- DECORATOR DE SEGURANÇA ---

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Por favor, faça login para acessar esta página.", "danger")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- FUNÇÕES AUXILIARES ---

def conectar_banco():
    caminho_banco = os.path.join(os.path.dirname(__file__), 'banco_ativos.db')
    return sqlite3.connect(caminho_banco)

def obter_usuario_logado():
    """Retorna os dados do usuário para passar aos templates"""
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

# --- ROTAS DE ACESSO ---

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
            flash(f"Bem-vindo, {usuario[1]}!", "success")
            return redirect(url_for('index'))
        else:
            flash("ID ou Senha incorretos!", "danger")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Sessão encerrada com sucesso.", "success")
    return redirect(url_for('login'))

# --- ROTAS PROTEGIDAS (@login_required) ---

@app.route('/')
@app.route('/index')
@login_required
def index():
    user = obter_usuario_logado()
    return render_template('index.html', user_nome=user['nome'], user_nivel=user['nivel'])

@app.route('/consult', methods=['POST'])
@login_required
def consult():
    id_buscado = request.form.get('id_busca')
    
    if not id_buscado:
        flash("Introduza um ID para pesquisar.", "danger")
        return redirect(url_for('index'))

    # Validação Humana: Verifica se o código existe ANTES de redirecionar
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("SELECT id_ativo FROM ativos WHERE id_ativo = ?", (id_buscado,))
    existe = cursor.fetchone()
    conn.close()

    if existe:
        return redirect(url_for('consult_get', id_ativo=id_buscado))
    else:
        flash(f"O código {id_buscado} não foi encontrado no sistema.", "danger")
        return redirect(url_for('index'))

@app.route('/consult/<id_ativo>')
@login_required
def consult_get(id_ativo):
    user = obter_usuario_logado()
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
    
    flash("Ativo não encontrado.", "danger")
    return redirect(url_for('index'))

@app.route('/newAsset', methods=['GET', 'POST'])
@login_required
def newAsset():
    user = obter_usuario_logado()
    
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

        flash(f"Ativo {id_gerado} cadastrado com sucesso!", "success")

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
@login_required
def newUpdate(id_ativo):
    user = obter_usuario_logado()
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
    
    flash("Ativo inexistente para atualização.", "danger")
    return redirect(url_for('index'))

@app.route('/saveUpdate', methods=['POST'])
@login_required
def saveUpdate():
    id_ativo = request.form.get('id_ativo')
    nova_data = request.form.get('data_escondida')
    novo_texto = request.form.get('resumo_atualizacao')

    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("SELECT resumo FROM ativos WHERE id_ativo = ?", (id_ativo,))
    resultado = cursor.fetchone()
    
    resumo_antigo = resultado[0] if resultado and resultado[0] else ""
    historico_atualizado = f"{nova_data}\n{novo_texto}\n\n{resumo_antigo}"
    
    cursor.execute("UPDATE ativos SET resumo = ?, data_atualizacao = ? WHERE id_ativo = ?", 
                    (historico_atualizado, nova_data, id_ativo))
    conn.commit()
    conn.close()
    
    flash("Histórico de manutenção atualizado!", "success")
    return redirect(url_for('consult_get', id_ativo=id_ativo))

# --- CABEÇALHOS ANTI-CACHE ---

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

if __name__ == '__main__':
   app.run(debug=True, host='0.0.0.0', port=5000)