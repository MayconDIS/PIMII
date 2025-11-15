Sistema Acadêmico (PIM II)
Este projeto é um Sistema de Gerenciamento Acadêmico (SGA) desenvolvido para o PIM II. O sistema é composto por dois módulos principais que operam sobre o mesmo conjunto de arquivos CSV:

Interface Gráfica (Python/Tkinter): A aplicação principal usada por Alunos, Professores e Administradores para login, gerenciamento de notas e visualização de dados.

Utilitário de Cadastro (C): Uma ferramenta de linha de comando (CLI) usada por Administradores para cadastrar ou excluir usuários (Alunos e Professores).

Arquitetura do Sistema
Este projeto não utiliza um banco de dados tradicional. Em vez disso, todo o estado do sistema (usuários, senhas, notas) é armazenado em arquivos CSV localizados na pasta output/dados_confidenciais/.

Ambos os programas (Python e C) leem e escrevem diretamente nesses arquivos.

Interface Gráfica (Interface_PIMII.py)

Usada por: Alunos, Professores e Administradores.

Acessa: alunos.csv, credenciais_alunos.csv, credenciais_professores.csv, professores.csv.

Funções: Login, visualização, lançamento de notas, gerenciamento de usuários.

Utilitário de Terminal (Sistema_cadastro.c)

Usado por: Apenas Administradores.

Acessa: credenciais_alunos.csv, credenciais_professores.csv, professores.csv.

Funções: Cadastro e exclusão de usuários (Alunos e Professores).

Funcionalidades Principais
Interface Gráfica (GUI):

Login de 3 Níveis: Acesso separado para Admin, Professor e Aluno.

Visão Adaptativa: Alunos veem apenas suas notas; Professores veem todos os alunos, mas apenas as notas da sua disciplina.

Lançamento de Notas: Professores e Admins podem lançar e alterar notas.

Gráficos de Desempenho: Geração de gráficos (Matplotlib) para análise visual das notas do aluno.

"I.A." Motivacional: Um pop-up para alunos que analisa a nota mais alta e mais baixa e oferece uma mensagem de incentivo.

Gerenciamento de Usuários (Admin): O Admin pode excluir alunos (por RA) ou professores (por Login) diretamente da interface.

Utilitário de Terminal (CLI):

Cadastro de Usuários: Permite ao Admin (com senha) cadastrar novos Alunos ou Professores.

Exclusão de Usuários: Permite ao Admin (com senha) excluir Alunos ou Professores.

Gerenciamento de Dados:

Lógica "Ler/Reescrever": Para evitar corrupção, os programas leem os CSVs, alteram os dados na memória e reescrevem o arquivo inteiro, garantindo a integridade.

Disciplina "Extra" Dinâmica: A 5ª disciplina ("Extra") só aparece na interface se um professor for atribuído a ela.

Tecnologias Utilizadas
Python 3: Linguagem principal da aplicação GUI.

Tkinter: Biblioteca nativa do Python para a interface gráfica.

Linguagem C: Para o módulo CLI de cadastro (Sistema_cadastro.c).

Matplotlib: Para geração de gráficos de notas.

Pillow (PIL): Para manipulação da imagem de fundo da tela de login.

Instalação e Configuração
Siga estes passos para configurar o ambiente e executar o projeto.

1. Clone o Repositório
Bash

git clone https://github.com/SEU-USUARIO/SEU-REPOSITORIO.git
cd SEU-REPOSITORIO
2. Instale as Dependências (Python)
A aplicação Python requer as bibliotecas matplotlib e pillow.

Bash

pip install matplotlib pillow
3. Crie a Estrutura de Pastas
O programa precisa de uma estrutura de pastas específica para salvar os arquivos CSV. Você deve criar as pastas output e dados_confidenciais manualmente.

A estrutura final deve ser:

Plaintext

SEU-REPOSITORIO/
|
+-- output/
|   |
|   +-- dados_confidenciais/
|       |
|       +-- (Esta pasta armazenará os CSVs de usuários e notas)
|
+-- Interface_PIMII.py
+-- Sistema_cadastro.c
+-- Manual_Usuario.md
+-- UNIP.jpg              (Opcional, imagem para a tela de login)
4. Compile o Módulo (C)
O arquivo Sistema_cadastro.c precisa ser compilado para se tornar um executável.

Pré-requisito: Você precisa de um compilador C, como o gcc (popular no Windows via MinGW).

Bash

# 1. Compile o arquivo .c e nomeie o executável
gcc Sistema_cadastro.c -o Sistema_cadastro.exe

# 2. Mova o executável para a pasta 'output'
# (No Windows)
move Sistema_cadastro.exe output\
# (No Linux/macOS)
# mv Sistema_cadastro.exe output/
Executando a Aplicação
Você pode executar qualquer um dos dois módulos.

Aviso: Não execute os dois programas (Python e C) ao mesmo tempo. Como eles modificam os mesmos arquivos, isso pode causar perda de dados ou corromper os CSVs.

Módulo Principal (GUI - Python)
Este é o programa principal para Alunos, Professores e Admins.

Bash

python Interface_PIMII.py
Módulo de Cadastro (CLI - C)
Este utilitário é usado apenas pelo Admin para criar ou excluir contas.

Bash

# 1. Navegue até a pasta 'output' onde o .exe está
cd output

# 2. Execute o programa
# (No Windows)
.\Sistema_cadastro.exe
# (No Linux/macOS)
# ./Sistema_cadastro.exe
Credenciais Padrão
Para acessar como Administrador (necessário para cadastrar professores ou excluir usuários):

Usuário: admin

Senha: admin123
