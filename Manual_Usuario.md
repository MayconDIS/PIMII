<h1 align="center">
  Sistema Acadêmico (PIM II)
</h1>

<p align="center">
  Um sistema de gerenciamento de notas com interface gráfica em Python (Tkinter) e um módulo de cadastro em C.
</p>

<p align="center">
  <img alt="Linguagem Principal" src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&style=for-the-badge">
  <img alt="Módulo Secundário" src="https://img.shields.io/badge/Linguagem-C-lightgrey?logo=c&style=for-the-badge">
  <img alt="Interface" src="https://img.shields.io/badge/UI-Tkinter-orange?style=for-the-badge">
</p>

---

## 💻 Sobre o Projeto

Este projeto é um Sistema de Gerenciamento Acadêmico (SGA) desenvolvido como parte do Projeto Integrado Multidisciplinar (PIM II). O objetivo é demonstrar a integração de diferentes tecnologias e paradigmas de programação para criar uma aplicação funcional.

O sistema é dividido em duas partes principais que operam sobre o mesmo conjunto de dados:

<table width="100%">
  <tr valign="top">
    <td width="50%" align="center">
      <h3>1. Interface Principal (Python)</h3>
      <p>Uma aplicação de desktop com interface gráfica (GUI) feita em <b>Python</b> e <b>Tkinter</b>. É por aqui que Alunos, Professores e Administradores interagem com o sistema para ver notas, lançar notas e gerenciar usuários.</p>
    </td>
    <td width="50%" align="center">
      <h3>2. Utilitário de Cadastro (C)</h3>
      <p>Um programa de linha de comando (CLI) feito em <b>C</b>. Este módulo é uma ferramenta administrativa (protegida por senha) usada especificamente para criar ou excluir contas de usuários (alunos e professores) no sistema.</p>
    </td>
  </tr>
</table>

---

## 🏛️ Como Funciona? A Arquitetura

Este projeto utiliza uma abordagem de **"CSV como Banco de Dados"**. Em vez de um servidor de banco de dados complexo (como MySQL ou PostgreSQL), todas as informações — notas dos alunos, credenciais de login e mapeamento de professores — são armazenadas em arquivos `.csv` simples na pasta `output/dados_confidenciais/`.

Ambos os programas (Python e C) foram ensinados a ler e escrever diretamente nesses arquivos.

```mermaid
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