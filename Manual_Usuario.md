<h1 align="center">Sistema Acadêmico Colaborativo (PIM II)</h1>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/C-Standard-lightgrey.svg" alt="C">
  <img src="https://img.shields.io/badge/Status-Concluído-success.svg" alt="Status">
</p>

<p align="center">
  <strong>Integração de Backend em C e Frontend em Python para gestão acadêmica.</strong>
</p>

---

## 📖 Sobre o Projeto

Este projeto foi desenvolvido como parte do **PIM II** (Projeto Integrado Multidisciplinar). O objetivo é criar um sistema funcional que une a eficiência da linguagem **C** (para rotinas administrativas) com a interatividade do **Python** (para a interface do usuário).

### ⚙️ Arquitetura Híbrida
O sistema não usa banco de dados SQL. Ele opera com uma **Base de Dados em CSV**.

| Componente | Linguagem | Função |
| :--- | :---: | :--- |
| **Backend Admin** | **C** | Cadastro rápido de usuários e limpeza de dados (CLI). |
| **Interface Visual** | **Python** | Login, gráficos, lançamento de notas e I.A. (GUI). |
| **Banco de Dados** | **CSV** | Arquivos de texto compartilhados que guardam todas as informações. |

---

## 🚀 Como Funciona?

O sistema segue o fluxo **Ler ➔ Editar ➔ Salvar**.

1.  O programa carrega os arquivos `.csv` da pasta `dados_confidenciais` para a memória RAM.
2.  O usuário faz alterações (lança nota, cadastra aluno).
3.  O programa apaga o arquivo antigo e reescreve a versão atualizada.

> ⚠️ **Aviso Importante:** Não rode os dois programas (C e Python) ao mesmo tempo para evitar conflito na gravação dos arquivos.

---

## 🛠️ Instalação e Execução

Siga o passo a passo abaixo para rodar o projeto na sua máquina.

### 1. Preparar o Ambiente
Crie uma pasta para o projeto e, dentro dela, crie a estrutura de pastas obrigatória:

```text
PROJETO_PIM/
│
├── output/
│   └── dados_confidenciais/  <-- (Aqui ficarão os CSVs gerados)
│
├── Interface_PIMII.py
├── Sistema_cadastro.c
└── UNIP.jpg (Opcional: Imagem de fundo)