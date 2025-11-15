<h1 align="center"> Sistema Acadêmico (PIM II) </h1>

<p align="center"> Um sistema de gerenciamento de notas com interface gráfica em Python (Tkinter) e um módulo de cadastro em C. </p>

<p align="center"> <img alt="Linguagem Principal" src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&style=for-the-badge"> <img alt="Módulo Secundário" src="https://img.shields.io/badge/Linguagem-C-lightgrey?logo=c&style=for-the-badge"> <img alt="Interface" src="https://img.shields.io/badge/UI-Tkinter-orange?style=for-the-badge"> </p>

<p align="center">

</p>

Sobre o Projeto
Este projeto é um Sistema de Gerenciamento Acadêmico (SGA) desenvolvido como parte do Projeto Integrado Multidisciplinar (PIM II). O objetivo é demonstrar a integração de diferentes tecnologias e paradigmas de programação para criar uma aplicação funcional.

O sistema é dividido em duas partes principais que operam sobre o mesmo conjunto de dados:

<table width="100%"> <tr valign="top"> <td width="50%" align="center"> <h3>1. Interface Principal (Python)</h3> <p>Uma aplicação de desktop com interface gráfica (GUI) feita em <b>Python</b> e <b>Tkinter</b>. É por aqui que Alunos, Professores e Administradores interagem com o sistema para ver notas, lançar notas e gerenciar usuários.</p> </td> <td width="50%" align="center"> <h3>2. Utilitário de Cadastro (C)</h3> <p>Um programa de linha de comando (CLI) feito em <b>C</b>. Este módulo é uma ferramenta administrativa (protegida por senha) usada especificamente para criar ou excluir contas de usuários (alunos e professores) no sistema.</p> </td> </tr> </table>

Como Funciona? A Arquitetura
Este projeto utiliza uma abordagem de "CSV como Banco de Dados". Em vez de um servidor de banco de dados complexo (como MySQL ou PostgreSQL), todas as informações — notas dos alunos, credenciais de login e mapeamento de professores — são armazenadas em arquivos .csv simples na pasta output/dados_confidenciais/.

Ambos os programas (Python e C) foram ensinados a ler e escrever diretamente nesses arquivos.

Snippet de código

graph TD
    subgraph Usuários
        U_Aluno[Aluno]
        U_Prof[Professor]
        U_Admin[Admin]
    end

    subgraph Aplicações
        App_Py[<b>Interface_PIMII.py</b><br>(GUI em Python/Tkinter)]
        App_C[<b>Sistema_cadastro.exe</b><br>(CLI em C)]
    end

    subgraph "Banco de Dados (Arquivos CSV)"
        CSV1[alunos.csv]
        CSV2[credenciais_alunos.csv]
        CSV3[credenciais_professores.csv]
        CSV4[professores.csv]
    end

    U_Aluno & U_Prof --> App_Py
    U_Admin --> App_Py
    U_Admin --> App_C

    App_Py <--> CSV1
    App_Py <--> CSV2
    App_Py <--> CSV3
    App_Py <--> CSV4

    App_C <--> CSV2
    App_C <--> CSV3
    App_C <--> CSV4
A Lógica de Leitura/Reescrita
Para garantir a integridade dos dados e evitar linhas em branco ou erros, o sistema usa uma lógica de "Ler, Modificar e Reescrever":

Ler: O programa (C ou Python) lê o arquivo CSV inteiro para a memória.

Modificar: A alteração (adicionar um usuário, lançar uma nota, excluir uma linha) é feita na memória.

Reescrever: O programa então apaga o arquivo CSV antigo e reescreve seu conteúdo inteiro a partir da memória.

<div style="background-color: #fff8c5; border-left: 5px solid #ffc107; padding: 10px 15px; margin-bottom: 15px; font-family: sans-serif;"> <strong>Importante:</strong> Por causa dessa lógica, <b>não execute os dois programas (Python e C) ao mesmo tempo</b>. Se ambos tentarem reescrever o mesmo arquivo simultaneamente, um deles terá seus dados perdidos. </div>

Funcionalidades por Nível de Acesso
O sistema possui três níveis de permissão. Clique para expandir:

<details> <summary><strong>Nível 1: Aluno (Visão Pessoal)</strong></summary> <ul> <li>Faz login com seu usuário (gerado no cadastro) e senha.</li> <li>Pode visualizar <strong>apenas suas próprias notas</strong>.</li> <li>Pode gerar um gráfico de desempenho <strong>apenas de suas próprias notas</strong>.</li> <li>Pode ver a lista de professores e suas respectivas disciplinas.</li> <li>Tem acesso a uma função "I.A." que oferece uma mensagem motivacional com base na sua maior e menor nota.</li> </ul> </details>

<details> <summary><strong>Nível 2: Professor (Visão Restrita)</strong></summary> <ul> <li>Faz login com seu usuário e senha.</li> <li>Pode visualizar todos os alunos, mas só vê as notas da <strong>disciplina que ele leciona</strong> (outras notas aparecem como "---").</li> <li>Pode <strong>lançar ou alterar notas</strong> apenas para a sua disciplina.</li> <li>Pode ver notas e gráficos de qualquer aluno, mas apenas os dados da sua disciplina.</li> </ul> </details>

<details> <summary><strong>Nível 3: Administrador (Acesso Total)</strong></summary> <ul> <li>Faz login com as credenciais <code>admin</code>.</li> <li>Pode carregar qualquer arquivo <code>alunos.csv</code>.</li> <li>Pode <strong>lançar ou alterar notas</strong> para <strong>qualquer aluno em qualquer disciplina</strong>.</li> <li>Pode ver notas e gráficos de todos os alunos sem restrições.</li> <li>Pode <strong>excluir alunos</strong> (buscando por RA) ou <strong>professores</strong> (buscando por Login) diretamente pela interface.</li> <li>É o único que pode usar o módulo em C ou as funções de cadastro de professor na GUI.</li> </ul> </details>

Guia de Instalação (Passo a Passo)
<ol> <li> <strong>Clone o Repositório</strong> <pre><code class="lang-bash">git clone https://github.com/SEU-USUARIO/SEU-REPOSITORIO.git cd SEU-REPOSITORIO</code></pre> </li>

<li> <strong>Instale as Dependências (Python)</strong> <p>A aplicação Python requer as bibliotecas <code>matplotlib</code> e <code>pillow</code>.</p> <pre><code class="lang-bash">pip install matplotlib pillow</code></pre> </li>

<li> <strong>Crie a Estrutura de Pastas</strong> <p>O programa <strong>precisa</strong> de uma estrutura de pastas específica para salvar os arquivos CSV. Você deve criar as pastas <code>output</code> e <code>dados_confidenciais</code> manualmente.</p> <pre><code>SEU-REPOSITORIO/ | +-- output/ | | | +-- dados_confidenciais/ | | | +-- (Esta pasta armazenará os CSVs) | +-- Interface_PIMII.py +-- Sistema_cadastro.c +-- UNIP.jpg (Opcional) </code></pre> </li>

<li> <strong>Compile o Módulo (C)</strong> <p>O arquivo <code>Sistema_cadastro.c</code> precisa ser compilado para se tornar um executável. (Requer um compilador C como <code>gcc</code>).</p> <pre><code class="lang-bash"># 1. Compile o arquivo .c e nomeie o executável gcc Sistema_cadastro.c -o Sistema_cadastro.exe

2. Mova o executável para a pasta 'output'
(No Windows)
move Sistema_cadastro.exe output\

(No Linux/macOS)
mv Sistema_cadastro.exe output/
</code></pre>

</li> </ol>

Como Executar
<table width="100%"> <tr valign="top"> <td width="50%"> <h3>Módulo Principal (GUI - Python)</h3> <p>Este é o programa principal para Alunos, Professores e Admins.</p> <pre><code class="lang-bash">python Interface_PIMII.py</code></pre> </td> <td width="50%"> <h3>Módulo de Cadastro (CLI - C)</h3> <p>Este utilitário é usado <strong>apenas pelo Admin</strong>.</p> <pre><code class="lang-bash"># 1. Navegue até a pasta 'output' cd output

2. Execute o programa
(No Windows)
.\Sistema_cadastro.exe

(No Linux/macOS)
./Sistema_cadastro.exe</code></pre>
</td>
</tr> </table>

Login Padrão
<div style="background-color: #f0f6ff; border: 1px solid #c8e1ff; padding: 15px; border-radius: 5px; font-family: sans-serif;"> Para acessar como Administrador (necessário para cadastrar professores ou excluir usuários): <ul> <li><strong>Usuário:</strong> <code>admin</code></li> <li><strong>Senha:</strong> <code>admin123</code></li> </ul> </div>
