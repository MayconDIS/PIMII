# Sistema Acadêmico (PIM II)

Este projeto é um Sistema Acadêmico desenvolvido como parte do PIM II (Projeto Integrado Multidisciplinar). Ele utiliza Python com a biblioteca Tkinter para criar a interface gráfica (GUI) e C para um módulo de cadastro/exclusão via terminal (CLI). O sistema permite gerenciar notas de alunos com diferentes níveis de acesso: Administrador, Professor e Aluno.

## ✨ Funcionalidades

* **Interface de Janela Única:** O programa Python (GUI) utiliza uma única janela que se transforma da tela de login para a interface principal, evitando pop-ups e problemas de foco.
* **Módulo Duplo (Python GUI + C CLI):**
    * **Python (GUI):** Interface gráfica completa para login, consulta de dados, lançamento de notas, geração de gráficos e gerenciamento de usuários.
    * **C (CLI):** Módulo de terminal (`Sistema_cadastro.exe`) para cadastro e exclusão de Alunos e Professores, acessível apenas pelo Admin.
* **Gestão de Usuários e Autenticação:**
    * Autenticação de três níveis (Admin, Professor, Aluno).
    * Credenciais de Professores e Alunos são 100% carregadas dinamicamente dos arquivos CSV.
    * Cadastro de Alunos (via GUI) com geração automática de login.
    * Cadastro de Professores (via GUI ou CLI, restrito ao Admin).
    * **Exclusão de Usuários (Admin):** Funcionalidade segura (via GUI ou CLI) para remover Alunos (por RA) ou Professores (por Login) de todos os arquivos de dados.
* **Gerenciamento de Dados via CSV:**
    * **Lógica de "Ler/Reescrever":** Ambos os módulos C e Python leem os arquivos CSV, removem linhas em branco e reescrevem o arquivo de forma limpa a cada salvamento, garantindo a integridade dos dados.
    * **Estrutura de Pastas Segura:** Todos os arquivos de dados (incluindo `alunos.csv`, credenciais e mapeamentos) são salvos na pasta `output/dados_confidenciais/`.
* **Gestão Acadêmica e Visualização:**
    * Lançamento de notas (Admin/Professor) com persistência imediata.
    * Visualização de dados adaptativa: Alunos veem apenas seus dados; Professores veem apenas as notas de sua disciplina.
    * **Coluna "Extra" Oculta:** A 5ª disciplina ("Extra") só é exibida na interface (tabela, notas, gráficos) se um professor estiver ativamente atribuído a ela.
    * Geração de gráficos de desempenho (Matplotlib) e análise motivacional por "I.A." (para Alunos).

## 🛠️ Tecnologias Utilizadas

* **Python 3:** Linguagem principal da aplicação GUI.
* **Tkinter:** Biblioteca padrão do Python para a interface gráfica.
* **Linguagem C:** Para um módulo CLI de cadastro e exclusão (`Sistema_cadastro.c`).
* **Matplotlib:** Para geração de gráficos.
* **Pillow (PIL):** Para manipulação de imagens (imagem de login).
* **Módulo CSV (Python) e stdio.h (C):** Para leitura e escrita de arquivos de dados.

## ⚙️ Pré-requisitos

* Python 3 instalado em seu sistema.
* Pip (gerenciador de pacotes Python).
* Um compilador C (como `gcc` via MinGW no Windows) para compilar o módulo C.

## 🚀 Instalação e Configuração

1.  **Clone o Repositório:**
    ```bash
    git clone [https://github.com/SEU-USUARIO/SEU-REPOSITORIO.git](https://github.com/SEU-USUARIO/SEU-REPOSITORIO.git)
    cd SEU-REPOSITORIO
    ```
2.  **Instale as Dependências Python:**
    ```bash
    pip install Pillow matplotlib
    ```
3.  **Crie a Estrutura de Pastas:**
    * No diretório principal do projeto, crie uma pasta chamada `output`.
    * Dentro da pasta `output`, crie outra pasta chamada `dados_confidenciais`.
    * (Opcional) Coloque uma imagem `UNIP.jpg` na pasta principal do projeto.

4.  **Compile o Módulo C (Obrigatório para o CLI):**
    * Abra um terminal que tenha o compilador C (como `gcc`) no seu PATH.
    * Navegue até a pasta do projeto.
    * Compile o arquivo `Sistema_cadastro.c`:
        ```bash
        gcc Sistema_cadastro.c -o Sistema_cadastro.exe
        ```
    * Mova o `Sistema_cadastro.exe` gerado para dentro da pasta `output`:
        ```bash
        move Sistema_cadastro.exe output\
        ```
5.  **(Importante) Arquivos CSV:** Os programas gerenciarão os arquivos CSV automaticamente. O módulo Python (`Interface_PIMII.py`) criará `disciplinas_nomes.csv` na primeira execução, que é necessário para o módulo C funcionar.

## ▶️ Executando a Aplicação

Você pode executar qualquer um dos dois módulos (mas não ao mesmo tempo, para evitar conflitos de arquivo).

**Módulo GUI (Python):**
```bash
python Interface_PIMII.py
