# ANTES DE QUALQUER COISA, INSTALE
- #### Git -> https://git-scm.com/install/windows
- #### Python -> https://www.python.org/downloads/
- #### Pip -> https://pypi.org/project/pip/#files
- #### Habilite a execução de Scripts
    - 1: Inicie o Powershell como administrador
    - 2: Digite o seguinte comando "Set-ExecutionPolicy Unrestricted" e pressione enter.
    - 3: Digite S (ou Y)

## PASSOS DE INSTALAÇÃO

### Passo 1: Clonar o repositório.
- 1: Escolha uma pasta no explorador de arquivos e inicie o **cmd** a partir dela.
- 2: Digite o comando "git clone https://github.com/Braian-paC/DiscoveringMath"
### Passo 2: Criar um ambiente virtual.
- Ainda no terminal, crie uma venv digitando "python -m venv venv"
- Agora, inicie o ambiente virtual: "./.venv/Scripts/activate"
### Passo 3: Instale as dependências.
- Cole o comando "pip install -r requirements.txt" para instalar todas as bibliotecas necessárias.
### Passo 4: Configure as variáveis do ambiente.
- Crie um arquivo .env na raiz do projeto e cole a chave da OpenAI da seguinte maneira:
- OPENAI_API_KEY=sua_chave_aqui
### Passo 5: Rode o projeto.
- python scripts/main.py
