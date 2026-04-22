from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
import random
import qrcode
from datetime import datetime

app = Flask(__name__)

# --- FUNÇÕES AUXILIARES ---

def conectar_banco():
    caminho_banco = os.path.join(os.path.dirname(__file__), 'banco_ativos.db')
    return sqlite3.connect(caminho_banco)

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
    ID_LOGADO = '123456789'
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("SELECT nome_exibicao, nivel FROM usuarios WHERE id_usuario = ?", (ID_LOGADO,))
    usuario = cursor.fetchone()
    conn.close()

    if usuario:
        return render_template('index.html', user_nome=usuario[0], user_nivel=usuario[1])
    return render_template('index.html', user_nome="Convidado", user_nivel="N/A")

# Rota de Consulta (Via formulário POST)
@app.route('/consult', methods=['POST'])
def consult():
    id_buscado = request.form.get('id_busca')
    return redirect(url_for('consult_get', id_ativo=id_buscado))

# Rota de exibição dos detalhes (GET)
@app.route('/consult/<id_ativo>')
def consult_get(id_ativo):
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("SELECT id_ativo, nome, data_atualizacao, resumo FROM ativos WHERE id_ativo = ?", (id_ativo,))
    resultado = cursor.fetchone()
    conn.close()

    if resultado:
        return render_template('consult.html', 
                               id_ativo=resultado[0], 
                               nome=resultado[1], 
                               data=resultado[2], 
                               resumo=resultado[3])
    return redirect('/index?erro=inexistente')

@app.route('/newAsset', methods=['GET', 'POST'])
def newAsset():
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
                               sucesso=True, 
                               id_ativo=id_gerado, 
                               qr_code=caminho_qr,
                               nome=nome,
                               data=data_formatada,
                               descricao=descricao)

    return render_template('newAsset.html', sucesso=False)

# Rota para abrir a tela de atualização carregando os dados do ativo
@app.route('/newUpdate/<id_ativo>')
def newUpdate(id_ativo):
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("SELECT nome FROM ativos WHERE id_ativo = ?", (id_ativo,))
    ativo = cursor.fetchone()
    conn.close()
    
    if ativo:
        return render_template('newUpdate.html', id_ativo=id_ativo, nome=ativo[0])
    return redirect('/index?erro=inexistente')

# Rota que processa o salvamento do histórico acumulativo
@app.route('/saveUpdate', methods=['POST'])
def saveUpdate():
    id_ativo = request.form.get('id_ativo')
    nova_data = request.form.get('data_escondida')
    novo_texto = request.form.get('resumo_atualizacao')

    conn = conectar_banco()
    cursor = conn.cursor()
    
    # 1. Busca o histórico antigo
    cursor.execute("SELECT resumo FROM ativos WHERE id_ativo = ?", (id_ativo,))
    resultado = cursor.fetchone()
    resumo_antigo = resultado[0] if resultado[0] else ""

    # 2. Cria o novo bloco de texto (Nova info no TOPO)
    historico_atualizado = f"{nova_data}\n{novo_texto}\n\n{resumo_antigo}"

    # 3. Faz o Update no banco
    cursor.execute("UPDATE ativos SET resumo = ?, data_atualizacao = ? WHERE id_ativo = ?", 
                   (historico_atualizado, nova_data, id_ativo))
    
    conn.commit()
    conn.close()
    
    # Redireciona para a tela de consulta para ver o histórico novo
    return redirect(url_for('consult_get', id_ativo=id_ativo))

@app.route('/login')
def login(): 
    return render_template('login.html')

# --- FINALIZAÇÃO ---

if __name__ == '__main__':
    app.run(debug=True)