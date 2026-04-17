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

@app.route('/consult', methods=['POST'])
def consult():
    id_buscado = request.form.get('id_busca')
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("SELECT id_ativo, nome, data_atualizacao, resumo FROM ativos WHERE id_ativo = ?", (id_buscado,))
    resultado = cursor.fetchone()
    conn.close()

    if resultado:
        return render_template('consult.html', 
                               id_ativo=resultado[0], 
                               nome=resultado[1], 
                               data=resultado[2], 
                               resumo=resultado[3])
    else:
        return redirect('/index?erro=inexistente')

@app.route('/newAsset', methods=['GET', 'POST'])
def newAsset():
    if request.method == 'POST':
        nome = request.form.get('equipamento')
        descricao = request.form.get('descricao')
        data_formatada = request.form.get('data_escondida')

        id_gerado = gerar_id_unico()

        # Garante que a pasta de QR Codes existe
        pasta_qr = os.path.join('static', 'qrcodes')
        if not os.path.exists(pasta_qr):
            os.makedirs(pasta_qr)
        
        caminho_qr = f'static/qrcodes/qr_{id_gerado}.png'
        img = qrcode.make(id_gerado)
        img.save(caminho_qr)

        # Salva no Banco
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

@app.route('/login')
def login(): 
    return render_template('login.html')

@app.route('/newUpdate')
def newUpdate(): 
    return render_template('newUpdate.html')

# O app.run SEMPRE deve ser a última coisa do arquivo
if __name__ == '__main__':
    app.run(debug=True)