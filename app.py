from flask import Flask, render_template
import sqlite3
import os  #Importar o 'os' aqui no topo

app = Flask(__name__)

# A função buscar_dados_do_banco fica aqui no meio
def buscar_dados_do_banco():

    caminho_diretorio = os.path.dirname(os.path.abspath(__file__))
    caminho_banco = os.path.join(caminho_diretorio, 'banco_ativos.db')
    
    conexao = sqlite3.connect(caminho_banco)
    cursor = conexao.cursor()
    
    try:
        cursor.execute("SELECT nome, data_atualizacao, resumo FROM ativos LIMIT 1")
        dado = cursor.fetchone()
    except sqlite3.OperationalError:
        dado = ("Tabela não encontrada", "N/A", "Rode o criar_banco.py novamente")
    
    conexao.close()
    return dado

#A rota que o navegador acessa
@app.route('/')
def home():
    dados_do_ativo = buscar_dados_do_banco()
    
    if dados_do_ativo:
        # Note que adicionamos 'id_ativo' aqui embaixo
        id_formatado = f"{1:05d}"
        return render_template('consult.html', 
                               nome=dados_do_ativo[0], 
                               data=dados_do_ativo[1], 
                               resumo=dados_do_ativo[2],
                               id_ativo=id_formatado) 
    else:
        return "Banco de dados vazio!"
@app.route('/login')
def login():
    return render_template('login.html')    

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/consult')
def consult():
    return render_template('consult.html')

@app.route('/newAsset')
def newAsset():
    return render_template('newAsset.html')

@app.route('/newUpdate')
def newUpdate():
    return render_template('newUpdate.html')                

if __name__ == "__main__":
    app.run(debug=True)

