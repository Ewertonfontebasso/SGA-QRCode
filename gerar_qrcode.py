import qrcode
import os

def gerar_codigo_ativo(id_ativo):
    #Criamos o código numérico formatado (ex: 1 vira 00001)
    codigo_numérico = f"{id_ativo:05d}"
    
    #Definimos o link que o QR Code vai abrir
    url = f"http://127.0.0.1:5000/ativo/{id_ativo}"
    
    # Configuração do desenho do QR Code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url)
    qr.make(fit=True)

    # Cria a imagem usando a biblioteca Pillow (PIL)
    img = qr.make_image(fill_color="black", back_color="white")
    
    #Garante que a pasta 'static' existe
    if not os.path.exists('static'):
        os.makedirs('static')
        
    #Salva a imagem com o nome padrão que o HTML vai buscar
    caminho_arquivo = f"static/qrcode_ativo_{id_ativo}.png"
    img.save(caminho_arquivo)
    
    print("-" * 30)
    print(f"SUCESSO NA GERAÇÃO!")
    print(f"Ativo ID: {id_ativo}")
    print(f"Código para digitação: {codigo_numérico}")
    print(f"Arquivo salvo em: {caminho_arquivo}")
    print("-" * 30)

if __name__ == "__main__":
    # Aqui você escolhe o ID que quer gerar. 
    # Como só temos um ativo no banco, vamos usar o 1.
    gerar_codigo_ativo(1)