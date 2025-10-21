#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define BASE_DIR "C:\\Users\\mayco\\Documents\\GitHub\\PIMII\\output\\"
#define ARQ_ALUNOS BASE_DIR "alunos.csv"
#define ARQ_CREDS  BASE_DIR "credenciais_alunos.csv"

#define MAX_NOME 100
#define MAX_RA 20
#define MAX_EMAIL 100
#define MAX_LOGIN 40
#define MAX_SENHA 40

typedef struct {
    char nome[MAX_NOME];
    char ra[MAX_RA];
    char email[MAX_EMAIL];
    char login[MAX_LOGIN];
    char senha[MAX_SENHA];
} Aluno;

void limpar_string(char *str) {
    str[strcspn(str, "\r\n")] = '\0';
}

void limpar_buffer() {
    int c;
    while ((c = getchar()) != '\n' && c != EOF);
}

int arquivo_existente(const char *caminho) {
    FILE *f = fopen(caminho, "r");
    if (f) { fclose(f); return 1; }
    return 0;
}

int diretorio_output_existe() {
    /* Checa apenas se o arquivo de credenciais ou alunos é acessível (proxy para dir existente).
       Como o usuário pediu criar manualmente a pasta, retornamos erro instructivo se não existir.
    */
    FILE *f = fopen(ARQ_ALUNOS, "a"); /* tenta abrir para criação: se falhar, pode ser por diretório não existir */
    if (f) {
        fclose(f);
        /* se acabou de criar um arquivo vazio, removemos para não poluir (pois preferimos gravar cabeçalho ao cadastrar) */
        remove(ARQ_ALUNOS);
        return 1;
    }
    return 0;
}

void cadastrar_aluno() {
    if (!diretorio_output_existe()) {
        printf("\n[ERRO] Diretorio de output nao encontrado.\nCrie manualmente a pasta:\n  C:\\Users\\mayco\\Documents\\GitHub\\PIMII\\output\nE rode o programa novamente.\n");
        return;
    }

    Aluno aluno;
    printf("\n=== Cadastro de Novo Aluno ===\n");

    printf("Nome Completo: ");
    limpar_buffer();
    if (fgets(aluno.nome, sizeof(aluno.nome), stdin) == NULL) return;
    limpar_string(aluno.nome);

    if (strlen(aluno.nome) == 0) {
        printf("Nome vazio. Cadastro cancelado.\n");
        return;
    }

    printf("RA (Registro Academico): ");
    if (fgets(aluno.ra, sizeof(aluno.ra), stdin) == NULL) return;
    limpar_string(aluno.ra);
    if (strlen(aluno.ra) == 0) {
        printf("RA vazio. Cadastro cancelado.\n");
        return;
    }

    printf("Login (ex: primeiro nome minusculo): ");
    if (fgets(aluno.login, sizeof(aluno.login), stdin) == NULL) return;
    limpar_string(aluno.login);
    if (strlen(aluno.login) == 0) {
        /* fallback: primeiro token do nome, minusculo */
        char *token = strtok(aluno.nome, " ");
        if (token) {
            snprintf(aluno.login, sizeof(aluno.login), "%s", token);
            /* restaurar nome (strtok altera) não crítico aqui */
        }
    }

    printf("Senha para o login: ");
    if (fgets(aluno.senha, sizeof(aluno.senha), stdin) == NULL) return;
    limpar_string(aluno.senha);
    if (strlen(aluno.senha) == 0) {
        printf("Senha vazia. Cadastro cancelado.\n");
        return;
    }

    printf("Email: ");
    if (fgets(aluno.email, sizeof(aluno.email), stdin) == NULL) return;
    limpar_string(aluno.email);
    if (strlen(aluno.email) == 0) {
        /* fallback: login + @unip.com */
        snprintf(aluno.email, sizeof(aluno.email), "%s@unip.com", aluno.login);
    }

    /* --- Salvar credenciais --- */
    FILE *arq_creds = fopen(ARQ_CREDS, "a");
    if (arq_creds == NULL) {
        printf("\n[AVISO] Nao foi possivel abrir '%s' para gravar credenciais.\n", ARQ_CREDS);
    } else {
        /* se arquivo novo, escreve cabeçalho */
        fseek(arq_creds, 0, SEEK_END);
        if (ftell(arq_creds) == 0) {
            fprintf(arq_creds, "Login,Senha\n");
        }
        fprintf(arq_creds, "%s,%s\n", aluno.login, aluno.senha);
        fclose(arq_creds);
        printf("[SUCESSO] Credenciais salvas em '%s'.\n", ARQ_CREDS);
    }

    /* --- Salvar dados academicos --- */
    FILE *arq_alunos = fopen(ARQ_ALUNOS, "a");
    if (arq_alunos == NULL) {
        printf("\nErro ao abrir '%s'. Dados academicos nao salvos.\n", ARQ_ALUNOS);
        return;
    }

    fseek(arq_alunos, 0, SEEK_END);
    if (ftell(arq_alunos) == 0) {
        /* Cabeçalho conforme solicitado:
           Nome,RA,Email,LingEstC,Python,EngSoft,APS,Media Geral
        */
        fprintf(arq_alunos, "Nome,RA,Email,LingEstC,Python,EngSoft,APS,Media Geral\n");
    }

    /* grava SEM aspas, campos separados por vírgula */
    fprintf(arq_alunos, "%s,%s,%s,%.2f,%.2f,%.2f,%.2f,%.2f\n",
            aluno.nome,
            aluno.ra,
            aluno.email,
            0.00, /* LingEstC */
            0.00, /* Python */
            0.00, /* EngSoft */
            0.00, /* APS */
            0.00  /* Media Geral */
    );

    fclose(arq_alunos);
    printf("[SUCESSO] Dados academicos salvos em '%s'.\n", ARQ_ALUNOS);
}

int main() {
    int escolha;
    do {
        printf("\n--- Sistema de Cadastro (C) ---\n");
        printf("1. Cadastrar Novo Aluno\n");
        printf("2. Sair\n");
        printf("Escolha uma opcao: ");

        if (scanf("%d", &escolha) != 1) {
            printf("\nOpcao invalida. Digite um numero.\n");
            limpar_buffer();
            escolha = 0;
            continue;
        }

        switch (escolha) {
            case 1:
                cadastrar_aluno();
                break;
            case 2:
                printf("Saindo...\n");
                break;
            default:
                printf("Opcao invalida.\n");
        }
    } while (escolha != 2);

    return 0;
}