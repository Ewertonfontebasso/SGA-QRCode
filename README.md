# SGA - Sistema de Gestão de Ativos via QR Code

### 🎓 Projeto Integrador - UNIVESP (Engenharia de Computação)

O **SGA** é uma solução desenvolvida para otimizar o inventário e a manutenção de ativos. Através da tecnologia de **QR Code**, o sistema permite o cadastro de equipamentos, geração automática de etiquetas e consulta instantânea do histórico de manutenção via câmera do celular ou computador.

---

## 🛠️ Tecnologias Utilizadas
- **Back-end:** Python 3 + Flask
- **Front-end:** HTML5, CSS3 e JavaScript (Vanilla)
- **Banco de Dados:** SQLite3
- **Bibliotecas Principais:**
  - `qrcode` (Geração das etiquetas)
  - `Pillow` (Processamento de imagem)
  - `Html5-QRCode` (Leitura via câmera direto no navegador)

---

## 👤 Credenciais para Teste (Login)
Para acessar o sistema e testar as funcionalidades, utilize um dos perfis abaixo:

| Perfil | ID de Usuário | Senha |
| :--- | :--- | :--- |
| **Administrador** | `123456789` | `admin123` |
| **Supervisor** | `111111111` | `teste123` |
| **Técnico** | `222222222` | `teste123` |

---

## ⚙️ Como Instalar e Executar
Siga os passos abaixo para rodar o projeto localmente:

1. **Ative o ambiente virtual:**
   ```powershell
   .\venv\Scripts\Activate.ps1

    Instale as dependências:
    Bash

    pip install flask qrcode pillow

    Inicie o servidor:
    Bash

    python app.py

    Acesse no navegador: http://localhost:5000

📷 Como testar o Scanner no Celular (Rede Local)

Para que a câmera funcione em ambiente de teste (HTTP), siga este procedimento:

    Conecte o celular e o PC no mesmo Wi-Fi.

    No celular, acesse o sistema pelo IP do seu computador (Ex: http://192.168.1.20:5000).

    Habilitar Câmera no Chrome (Android):

        No navegador do celular, digite: chrome://flags

        Pesquise por: #unsafely-treat-insecure-origin-as-secure

        Mude para Enabled.

        Digite o endereço do PC no campo de texto: http://192.168.1.20:5000

        Clique em Relaunch.

    Agora, ao clicar em "Escanear QR CODE" no celular, a câmera será ativada.

🔍 Massa de Dados para Busca Direta

Caso queira testar a pesquisa manual sem escanear, utilize estes códigos:

    11504 (Conversor de Mídia)

    44012 (Roteador Mikrotik CCR1036)

📂 Estrutura de Pastas
Plaintext

SGA-QRCode/
├── app.py
├── banco_ativos.db
├── static/
│   ├── css/
│   ├── img/
│   └── qrcodes/
└── templates/