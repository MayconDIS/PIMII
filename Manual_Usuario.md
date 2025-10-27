# Sistema Acadêmico (PIM II)

Este projeto é um Sistema Acadêmico desenvolvido como parte do PIM II (Projeto Integrado Multidisciplinar). Ele utiliza Python com a biblioteca Tkinter para criar uma interface gráfica (GUI) que permite gerenciar notas de alunos em diversas disciplinas, com diferentes níveis de acesso para Administradores, Professores e Alunos.

## ✨ Funcionalidades

* **Interface Gráfica Amigável:** Construída com Tkinter para fácil interação.
* **Login Seguro:** Sistema de autenticação com três níveis de acesso:
    * **Administrador:** Controle total sobre dados e usuários.
    * **Professor:** Acesso restrito à sua disciplina e visualização geral.
    * **Aluno:** Acesso apenas aos seus próprios dados e funcionalidades específicas.
* **Cadastro de Usuários:**
    * Alunos podem se autocadastrar.
    * Administradores podem cadastrar novos professores.
* **Gerenciamento de Dados via CSV:**
    * Carrega dados de alunos a partir de arquivos `.csv`.
    * Salva credenciais, mapeamentos e notas em arquivos `.csv` separados.
    * Estrutura de pastas organizada (`output/` e `output/dados_confidenciais/`).
* **Gerenciamento de Notas:**
    * Administradores podem lançar/editar notas em qualquer disciplina.
    * Professores podem lançar/editar notas apenas em sua disciplina designada.
* **Visualização de Dados:**
    * Tabela principal com visualização adaptada ao nível de acesso.
    * Janela detalhada para visualização de todas as notas (Admin/Aluno) ou nota específica (Professor).
* **Gráficos de Desempenho:** Geração de gráficos de barras (usando Matplotlib) para visualizar o desempenho de um aluno nas disciplinas.
* **Disciplina Flexível:** O sistema suporta 5 disciplinas, sendo a última ("Extra" por padrão) renomeável pelo Administrador durante o cadastro de um professor para ela.
* **Feedback Inteligente (I.A.):** Recurso exclusivo para alunos que fornece mensagens motivacionais com base em seu desempenho.

## 🛠️ Tecnologias Utilizadas

* **Python 3:** Linguagem de programação principal.
* **Tkinter:** Biblioteca padrão do Python para criação de interfaces gráficas.
* **Matplotlib:** Biblioteca para geração de gráficos.
* **Pillow (PIL):** Biblioteca para manipulação de imagens (usada na imagem flutuante do login).
* **Módulo CSV:** Para leitura e escrita de arquivos de dados.

## ⚙️ Pré-requisitos

* Python 3 instalado em seu sistema.
* Pip (gerenciador de pacotes Python, geralmente incluído com Python).

## 🚀 Instalação e Configuração

1.  **Clone o Repositório:**
    ```bash
    git clone <URL_DO_SEU_REPOSITORIO>
    cd PIMII # Ou o nome da pasta do seu projeto
    ```
2.  **Instale as Dependências:**
    ```bash
    pip install Pillow matplotlib
    ```
3.  **Crie a Estrutura de Pastas:**
    * No diretório principal do projeto, crie uma pasta chamada `output`.
    * Dentro da pasta `output`, crie outra pasta chamada `dados_confidenciais`.
    * (Opcional) Coloque uma imagem `UNIP.jpg` na pasta principal do projeto se desejar a imagem flutuante no login.

4.  **(Importante) Arquivos CSV Iniciais:** O programa criará os arquivos CSV necessários (`alunos.csv`, `credenciais_*.csv`, etc.) na primeira execução ou quando os dados forem salvos. Se você já tiver arquivos de versões anteriores, **apague-os** antes de executar esta versão para garantir a compatibilidade com a estrutura atual (5 disciplinas, nomes de exibição, etc.).

## ▶️ Executando a Aplicação

1.  Abra seu terminal ou prompt de comando.
2.  Navegue até o diretório principal do projeto (onde está o `Interface_PIMII.py`).
3.  Execute o comando:
    ```bash
    python Interface_PIMII.py
    ```
4.  A janela de login será exibida.

## 📖 Como Usar

Consulte o arquivo `Manual_Usuario.md` (***Sugestão:*** *Copie o manual que geramos para um arquivo com este nome no seu repositório*) para um guia detalhado passo a passo sobre todas as funcionalidades, incluindo:

1.  Como fazer login com diferentes perfis (o login padrão do admin é `admin`/`admin123`).
2.  Como cadastrar novos alunos e professores.
3.  Como carregar o arquivo CSV de alunos.
4.  Como lançar e visualizar notas.
5.  Como gerar e interpretar os gráficos.
6.  Como usar o recurso de I.A. (para alunos).
7.  Como renomear a disciplina "Extra".

## 📁 Estrutura de Arquivos de Dados

O sistema armazena seus dados nos seguintes arquivos CSV:

* `output/alunos.csv`: Dados acadêmicos (Nome, RA, Email, Notas, Média).
* `output/dados_confidenciais/credenciais_alunos.csv`: Logins e senhas dos alunos.
* `output/dados_confidenciais/credenciais_professores.csv`: Logins e senhas dos professores.
* `output/dados_confidenciais/professores.csv`: Mapeamento de login de professor para disciplina interna.
* `output/dados_confidenciais/disciplinas_nomes.csv`: Mapeamento de nomes internos de disciplinas para nomes de exibição.

**⚠️ Atenção:** As senhas nos arquivos `credenciais_*.csv` são armazenadas em **texto puro**. Em um ambiente real, isso seria uma falha de segurança. Para este projeto acadêmico, certifique-se de que a pasta `dados_confidenciais` não seja compartilhada indevidamente.

---
