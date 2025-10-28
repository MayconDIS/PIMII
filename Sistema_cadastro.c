// Sistema_cadastro.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h> // Para tolower
#include <time.h>  // Para fallback de login
#include <direct.h> // Para _mkdir (Windows)

// --- DEFINIÇÕES DE CAMINHO ATUALIZADAS ---
#define BASE_DIR "C:\\Users\\mayco\\Documents\\GitHub\\PIMII\\output\\" // Adapte se necessário
#define CONFIDENTIAL_DIR BASE_DIR "dados_confidenciais\\"
#define OUTPUT_DIR BASE_DIR

#define ARQ_ALUNOS OUTPUT_DIR "alunos.csv"
#define ARQ_CREDS_ALUNOS CONFIDENTIAL_DIR "credenciais_alunos.csv"
#define ARQ_CREDS_PROFS CONFIDENTIAL_DIR "credenciais_professores.csv"
#define ARQ_MAP_PROFS CONFIDENTIAL_DIR "professores.csv"
#define ARQ_NOMES_DISC CONFIDENTIAL_DIR "disciplinas_nomes.csv"
// --- FIM DAS DEFINIÇÕES DE CAMINHO ---

#define MAX_NOME 100
#define MAX_RA 20
#define MAX_EMAIL 100
#define MAX_LOGIN 40
#define MAX_SENHA 40
#define MAX_DISCIPLINA 50
#define NUM_DISCIPLINAS 5 // LingEstC, Python, EngSoft, APS, Extra
#define MAX_LINHA_CSV 512
#define MAX_PROFESSORES 50
#define MAX_ALUNOS 500 // Limite de linhas de alunos/credenciais em memória

// --- ESTRUTURAS DE DADOS ---
typedef struct {
    char nome[MAX_NOME];
    char ra[MAX_RA];
    char email[MAX_EMAIL];
} AlunoInfo;

typedef struct {
    char login[MAX_LOGIN];
    char senha[MAX_SENHA];
} Credencial;

typedef struct {
    char login[MAX_LOGIN];
    char disciplina_interna[MAX_DISCIPLINA];
} ProfessorMap;

typedef struct {
    char interno[MAX_DISCIPLINA];
    char display[MAX_DISCIPLINA];
} NomeDisciplina;
// --- FIM DAS ESTRUTURAS ---

// --- GLOBAIS ---
const char* LISTA_DISCIPLINAS[NUM_DISCIPLINAS] = {
    "LingEstC", "Python", "EngSoft", "APS", "Extra"
};
NomeDisciplina DISPLAY_NAMES[NUM_DISCIPLINAS];
const char* ADMIN_PASSWORD = "admin123";
ProfessorMap todos_mapeamentos[MAX_PROFESSORES];
int num_mapeamentos_lidos = 0;

// Arrays para armazenar linhas dos arquivos lidos
char linhas_alunos[MAX_ALUNOS][MAX_LINHA_CSV];
int num_linhas_alunos = 0;
char linhas_creds_alunos[MAX_ALUNOS][MAX_LINHA_CSV]; // Reutilizando MAX_ALUNOS
int num_linhas_creds_alunos = 0;
char linhas_creds_profs[MAX_PROFESSORES][MAX_LINHA_CSV]; // Reutilizando MAX_PROFESSORES
int num_linhas_creds_profs = 0;
// --- FIM GLOBAIS ---

// --- FUNÇÕES UTILITÁRIAS ---
void limpar_string(char *str) {
    str[strcspn(str, "\r\n")] = '\0';
}

void limpar_buffer() {
    int c;
    while ((c = getchar()) != '\n' && c != EOF);
}

void str_tolower(char *str) {
    for (int i = 0; str[i]; i++) {
        str[i] = tolower(str[i]);
    }
}

int verificar_criar_diretorios() {
    _mkdir(OUTPUT_DIR);
    _mkdir(CONFIDENTIAL_DIR);
    FILE *f_out = fopen(ARQ_ALUNOS, "a");
    FILE *f_conf = fopen(ARQ_CREDS_ALUNOS, "a");
    if (!f_out || !f_conf) {
        printf("\n[ERRO] Nao foi possivel acessar/criar diretorios de output.\n");
        if (f_out) fclose(f_out);
        if (f_conf) fclose(f_conf);
        return 0;
    }
    if (f_out) fclose(f_out);
    if (f_conf) fclose(f_conf);
    return 1;
}
// --- FIM FUNÇÕES UTILITÁRIAS ---

// --- FUNÇÕES DE NOMES DE DISCIPLINA ---
void salvar_nomes_disciplinas() {
    _mkdir(CONFIDENTIAL_DIR);
    FILE *f = fopen(ARQ_NOMES_DISC, "w");
    if (!f) {
        printf("[AVISO] Nao foi possivel salvar nomes de disciplinas em '%s'.\n", ARQ_NOMES_DISC);
        return;
    }
    fprintf(f, "InternalName,DisplayName\n");
    for (int i = 0; i < NUM_DISCIPLINAS; i++) {
        fprintf(f, "%s,%s\n", DISPLAY_NAMES[i].interno, DISPLAY_NAMES[i].display);
    }
    fclose(f);
}

void carregar_nomes_disciplinas() {
    for (int i = 0; i < NUM_DISCIPLINAS; i++) {
        strncpy(DISPLAY_NAMES[i].interno, LISTA_DISCIPLINAS[i], MAX_DISCIPLINA - 1);
        DISPLAY_NAMES[i].interno[MAX_DISCIPLINA - 1] = '\0';
        strncpy(DISPLAY_NAMES[i].display, LISTA_DISCIPLINAS[i], MAX_DISCIPLINA - 1);
        DISPLAY_NAMES[i].display[MAX_DISCIPLINA - 1] = '\0';
    }
    FILE *f = fopen(ARQ_NOMES_DISC, "r");
    if (!f) {
        printf("Arquivo '%s' nao encontrado. Criando com nomes padrao.\n", ARQ_NOMES_DISC);
        salvar_nomes_disciplinas();
        return;
    }
    char linha[MAX_LINHA_CSV];
    if(fgets(linha, sizeof(linha), f) == NULL) {
        printf("[AVISO] Arquivo '%s' parece estar vazio ou erro na leitura do cabecalho.\n", ARQ_NOMES_DISC);
        fclose(f);
        salvar_nomes_disciplinas();
        return;
    }
    while (fgets(linha, sizeof(linha), f)) {
        limpar_string(linha);
        char *interno_csv = strtok(linha, ",");
        char *display_csv = strtok(NULL, ",");
        if (interno_csv && display_csv) {
            for (int i = 0; i < NUM_DISCIPLINAS; i++) {
                if (strcmp(interno_csv, DISPLAY_NAMES[i].interno) == 0) {
                    strncpy(DISPLAY_NAMES[i].display, display_csv, MAX_DISCIPLINA - 1);
                     DISPLAY_NAMES[i].display[MAX_DISCIPLINA - 1] = '\0';
                    break;
                }
            }
        }
    }
    fclose(f);
    printf("Nomes de disciplinas carregados de '%s'.\n", ARQ_NOMES_DISC);
}
// --- FIM FUNÇÕES NOMES DISCIPLINA ---

// --- FUNÇÕES DE LEITURA/ESCRITA GENÉRICAS (MODO REESCRITA) ---
// Lê todas as linhas de um arquivo CSV para um array de strings
int ler_linhas_arquivo(const char *caminho, char linhas[][MAX_LINHA_CSV], int max_linhas) {
    int count = 0;
    FILE *f = fopen(caminho, "r");
    if (!f) {
        // Arquivo não existe ou não pode ser lido, retorna 0 linhas
        return 0;
    }
    while (fgets(linhas[count], MAX_LINHA_CSV, f) && count < max_linhas) {
        limpar_string(linhas[count]); // Remove \n lido por fgets
        // Opcional: Ignorar linhas completamente vazias durante a leitura
        if (strlen(linhas[count]) > 0) {
             count++;
        }
    }
    fclose(f);
    return count;
}

// Salva todas as linhas de um array de strings para um arquivo CSV (sobrescreve)
int salvar_linhas_arquivo(const char *caminho, char linhas[][MAX_LINHA_CSV], int num_linhas) {
    FILE *f = fopen(caminho, "w"); // Modo escrita (sobrescreve)
    if (!f) {
        printf("\n[ERRO] Nao foi possivel abrir '%s' para escrita.\n", caminho);
        return 0; // Falha
    }
    for (int i = 0; i < num_linhas; i++) {
        fprintf(f, "%s\n", linhas[i]); // Adiciona \n ao salvar cada linha
    }
    fclose(f);
    return 1; // Sucesso
}
// --- FIM FUNÇÕES LEITURA/ESCRITA GENÉRICAS ---

// --- FUNÇÕES DE MAPEAMENTO DE PROFESSORES (Usam leitura/escrita genérica agora) ---
void ler_mapeamentos_professores() {
    num_mapeamentos_lidos = 0;
    // Buffer temporário para ler linhas
    char linhas_map[MAX_PROFESSORES][MAX_LINHA_CSV];
    int total_linhas = ler_linhas_arquivo(ARQ_MAP_PROFS, linhas_map, MAX_PROFESSORES);

    // Ignora cabeçalho (linha 0) se existir
    int inicio = (total_linhas > 0 && strstr(linhas_map[0], "Login") != NULL) ? 1 : 0;

    for(int i = inicio; i < total_linhas && num_mapeamentos_lidos < MAX_PROFESSORES; i++) {
         // Faz uma cópia da linha para strtok não modificar o original no array
        char linha_copia[MAX_LINHA_CSV];
        strncpy(linha_copia, linhas_map[i], MAX_LINHA_CSV -1);
        linha_copia[MAX_LINHA_CSV-1] = '\0';

        char *login_csv = strtok(linha_copia, ",");
        char *disciplina_csv = strtok(NULL, ",");

        if (login_csv && disciplina_csv) {
            strncpy(todos_mapeamentos[num_mapeamentos_lidos].login, login_csv, MAX_LOGIN - 1);
            todos_mapeamentos[num_mapeamentos_lidos].login[MAX_LOGIN - 1] = '\0';
            strncpy(todos_mapeamentos[num_mapeamentos_lidos].disciplina_interna, disciplina_csv, MAX_DISCIPLINA - 1);
            todos_mapeamentos[num_mapeamentos_lidos].disciplina_interna[MAX_DISCIPLINA - 1] = '\0';
            num_mapeamentos_lidos++;
        }
    }
    printf("Carregados %d mapeamentos de professores de '%s'.\n", num_mapeamentos_lidos, ARQ_MAP_PROFS);
}

void salvar_todos_mapeamentos_professores() {
    _mkdir(CONFIDENTIAL_DIR);
    // Buffer temporário para formatar linhas
    char linhas_map_salvar[MAX_PROFESSORES + 1][MAX_LINHA_CSV]; // +1 para cabeçalho
    int total_linhas_salvar = 0;

    // Adiciona cabeçalho
    snprintf(linhas_map_salvar[total_linhas_salvar], MAX_LINHA_CSV, "Login,Disciplina");
    total_linhas_salvar++;

    // Adiciona dados
    for (int i = 0; i < num_mapeamentos_lidos && total_linhas_salvar <= MAX_PROFESSORES; i++) {
        snprintf(linhas_map_salvar[total_linhas_salvar], MAX_LINHA_CSV, "%s,%s",
                 todos_mapeamentos[i].login, todos_mapeamentos[i].disciplina_interna);
        total_linhas_salvar++;
    }

    if(salvar_linhas_arquivo(ARQ_MAP_PROFS, linhas_map_salvar, total_linhas_salvar)){
         printf("[SUCESSO] Mapeamentos de professores salvos em '%s'.\n", ARQ_MAP_PROFS);
    }
}
// --- FIM FUNÇÕES DE MAPEAMENTO ---

// --- FUNÇÕES DE CADASTRO ATUALIZADA (lógica Ler/Adicionar/Reescrever) ---
void cadastrar_aluno() {
    AlunoInfo aluno_info;
    Credencial aluno_cred;

    printf("\n=== Cadastro de Novo Aluno ===\n");

    printf("Nome Completo: ");
    if (fgets(aluno_info.nome, sizeof(aluno_info.nome), stdin) == NULL) return;
    limpar_string(aluno_info.nome);
    if (strlen(aluno_info.nome) == 0) { printf("Nome vazio. Cancelado.\n"); return; }

    printf("RA (Registro Academico): ");
    if (fgets(aluno_info.ra, sizeof(aluno_info.ra), stdin) == NULL) return;
    limpar_string(aluno_info.ra);
    if (strlen(aluno_info.ra) == 0) { printf("RA vazio. Cancelado.\n"); return; }

    char nome_temp[MAX_NOME];
    strncpy(nome_temp, aluno_info.nome, MAX_NOME);
    char *primeiro_nome = strtok(nome_temp, " ");
    if (primeiro_nome) {
        snprintf(aluno_cred.login, sizeof(aluno_cred.login), "%s", primeiro_nome);
        str_tolower(aluno_cred.login);
    } else {
        snprintf(aluno_cred.login, sizeof(aluno_cred.login), "aluno%ld", (long)time(NULL));
    }
    printf("Login gerado: %s\n", aluno_cred.login);

    printf("Senha para o login '%s': ", aluno_cred.login);
    if (fgets(aluno_cred.senha, sizeof(aluno_cred.senha), stdin) == NULL) return;
    limpar_string(aluno_cred.senha);
    if (strlen(aluno_cred.senha) == 0) { printf("Senha vazia. Cancelado.\n"); return; }

    printf("Email (deixe em branco para %s@unip.com): ", aluno_cred.login);
    if (fgets(aluno_info.email, sizeof(aluno_info.email), stdin) == NULL) return;
    limpar_string(aluno_info.email);
    if (strlen(aluno_info.email) == 0) {
        snprintf(aluno_info.email, sizeof(aluno_info.email), "%s@unip.com", aluno_cred.login);
        printf("Email definido como: %s\n", aluno_info.email);
    }

    // --- Salvar credenciais (Ler/Adicionar/Reescrever) ---
    _mkdir(CONFIDENTIAL_DIR);
    num_linhas_creds_alunos = ler_linhas_arquivo(ARQ_CREDS_ALUNOS, linhas_creds_alunos, MAX_ALUNOS);

    if (num_linhas_creds_alunos < MAX_ALUNOS) {
        // Formata a nova linha
        snprintf(linhas_creds_alunos[num_linhas_creds_alunos], MAX_LINHA_CSV, "%s,%s",
                 aluno_cred.login, aluno_cred.senha);
        num_linhas_creds_alunos++; // Incrementa o contador

        // Garante cabeçalho se for a primeira linha (ou se não foi lido)
        if (num_linhas_creds_alunos == 1 || strstr(linhas_creds_alunos[0], "Login") == NULL) {
             // Move a linha adicionada para o índice 1 e insere cabeçalho no 0
            if (num_linhas_creds_alunos == 1) { // Só tinha 1 linha (a nova)
                 strncpy(linhas_creds_alunos[1], linhas_creds_alunos[0], MAX_LINHA_CSV);
            } else { // Se leu algo antes mas não tinha cabeçalho, shift + insert (raro)
                for(int i = num_linhas_creds_alunos -1; i > 0; i--) {
                     strncpy(linhas_creds_alunos[i], linhas_creds_alunos[i-1], MAX_LINHA_CSV);
                }
            }
             snprintf(linhas_creds_alunos[0], MAX_LINHA_CSV, "Login,Senha");
             num_linhas_creds_alunos = (num_linhas_creds_alunos == 1) ? 2 : num_linhas_creds_alunos; // Ajusta contagem se inseriu cabeçalho
        }

        // Reescreve o arquivo
        if (salvar_linhas_arquivo(ARQ_CREDS_ALUNOS, linhas_creds_alunos, num_linhas_creds_alunos)) {
            printf("[SUCESSO] Credenciais salvas em '%s'.\n", ARQ_CREDS_ALUNOS);
        }
    } else {
        printf("[ERRO] Limite maximo de alunos (%d) atingido no arquivo de credenciais.\n", MAX_ALUNOS);
    }

    // --- Salvar dados academicos (Ler/Adicionar/Reescrever) ---
    _mkdir(OUTPUT_DIR);
    num_linhas_alunos = ler_linhas_arquivo(ARQ_ALUNOS, linhas_alunos, MAX_ALUNOS);

    if (num_linhas_alunos < MAX_ALUNOS) {
         // Formata a nova linha de dados
        char nova_linha_aluno[MAX_LINHA_CSV];
        char buffer_notas[MAX_LINHA_CSV] = ""; // Buffer para concatenar notas
        for (int i = 0; i < NUM_DISCIPLINAS; i++) {
             strcat(buffer_notas, ",0.00");
        }
        strcat(buffer_notas, ",0.00"); // Media Geral

        snprintf(nova_linha_aluno, MAX_LINHA_CSV, "%s,%s,%s%s",
                 aluno_info.nome, aluno_info.ra, aluno_info.email, buffer_notas);

        // Adiciona a nova linha ao array
        strncpy(linhas_alunos[num_linhas_alunos], nova_linha_aluno, MAX_LINHA_CSV - 1);
        linhas_alunos[num_linhas_alunos][MAX_LINHA_CSV-1] = '\0';
        num_linhas_alunos++;

        // Garante cabeçalho
         if (num_linhas_alunos == 1 || strstr(linhas_alunos[0], "Nome,RA,Email") == NULL) {
             if (num_linhas_alunos == 1) {
                 strncpy(linhas_alunos[1], linhas_alunos[0], MAX_LINHA_CSV);
             } else {
                 for(int i = num_linhas_alunos -1; i > 0; i--) {
                     strncpy(linhas_alunos[i], linhas_alunos[i-1], MAX_LINHA_CSV);
                 }
             }
             // Cria cabeçalho dinâmico
             char cabecalho[MAX_LINHA_CSV] = "Nome,RA,Email";
             for (int i = 0; i < NUM_DISCIPLINAS; i++) {
                 strcat(cabecalho, ",");
                 strcat(cabecalho, LISTA_DISCIPLINAS[i]);
             }
             strcat(cabecalho, ",Media Geral");
             snprintf(linhas_alunos[0], MAX_LINHA_CSV, "%s", cabecalho);
             num_linhas_alunos = (num_linhas_alunos == 1) ? 2 : num_linhas_alunos;
         }

        // Reescreve o arquivo
        if (salvar_linhas_arquivo(ARQ_ALUNOS, linhas_alunos, num_linhas_alunos)) {
            printf("[SUCESSO] Dados academicos salvos em '%s'.\n", ARQ_ALUNOS);
        }
    } else {
         printf("[ERRO] Limite maximo de alunos (%d) atingido no arquivo de dados.\n", MAX_ALUNOS);
    }
}

// --- FUNÇÃO ATUALIZADA (usa lógica Ler/Adicionar/Reescrever para credenciais) ---
void cadastrar_professor() {
    Credencial prof_cred;
    ProfessorMap novo_map;
    int disciplina_idx = -1;
    char disciplina_display_escolhida[MAX_DISCIPLINA];
    int mapeamento_existente_idx = -1;
    int substituir_disciplina = 0;

    printf("\n=== Cadastro de Novo Professor ===\n");

    printf("Login do Professor: ");
    if (fgets(prof_cred.login, sizeof(prof_cred.login), stdin) == NULL) return;
    limpar_string(prof_cred.login);
    str_tolower(prof_cred.login);
    if (strlen(prof_cred.login) == 0) { printf("Login vazio. Cancelado.\n"); return; }

    printf("Senha para o login '%s': ", prof_cred.login);
    if (fgets(prof_cred.senha, sizeof(prof_cred.senha), stdin) == NULL) return;
    limpar_string(prof_cred.senha);
    if (strlen(prof_cred.senha) == 0) { printf("Senha vazia. Cancelado.\n"); return; }

    printf("Disciplinas disponiveis:\n");
    for (int i = 0; i < NUM_DISCIPLINAS; i++) {
        printf("  %d. %s\n", i + 1, DISPLAY_NAMES[i].display);
    }
    printf("Escolha o numero da disciplina: ");
    int escolha_num;
    if (scanf("%d", &escolha_num) != 1) {
        printf("Entrada invalida. Cancelado.\n");
        limpar_buffer();
        return;
    }
    limpar_buffer(); // Limpa após scanf

    if (escolha_num < 1 || escolha_num > NUM_DISCIPLINAS) {
         printf("Escolha invalida. Cancelado.\n");
         return;
    }
    disciplina_idx = escolha_num - 1;

    strncpy(novo_map.login, prof_cred.login, MAX_LOGIN -1);
    novo_map.login[MAX_LOGIN-1] = '\0';
    strncpy(novo_map.disciplina_interna, DISPLAY_NAMES[disciplina_idx].interno, MAX_DISCIPLINA -1);
    novo_map.disciplina_interna[MAX_DISCIPLINA-1] = '\0';
    strncpy(disciplina_display_escolhida, DISPLAY_NAMES[disciplina_idx].display, MAX_DISCIPLINA -1);
    disciplina_display_escolhida[MAX_DISCIPLINA-1] = '\0';

    if (strcmp(novo_map.disciplina_interna, "Extra") == 0) {
        printf("Voce escolheu a disciplina '%s'.\n", disciplina_display_escolhida);
        printf("Digite um novo nome para ela (ou deixe em branco para manter): ");
        char novo_nome[MAX_DISCIPLINA];
        if (fgets(novo_nome, sizeof(novo_nome), stdin) != NULL) {
            limpar_string(novo_nome);
            if (strlen(novo_nome) > 0) {
                strncpy(DISPLAY_NAMES[disciplina_idx].display, novo_nome, MAX_DISCIPLINA - 1);
                 DISPLAY_NAMES[disciplina_idx].display[MAX_DISCIPLINA - 1] = '\0';
                salvar_nomes_disciplinas();
                printf("Disciplina 'Extra' renomeada para '%s'.\n", novo_nome);
                 strncpy(disciplina_display_escolhida, novo_nome, MAX_DISCIPLINA -1);
                 disciplina_display_escolhida[MAX_DISCIPLINA-1] = '\0';
            }
        }
    }

    ler_mapeamentos_professores(); // Mapeamentos já usam ler/reescrever

    for(int i = 0; i < num_mapeamentos_lidos; i++) {
        // ... (lógica de verificação de substituição - mantenha como antes) ...
         if (strcmp(todos_mapeamentos[i].disciplina_interna, novo_map.disciplina_interna) == 0 &&
            strcmp(todos_mapeamentos[i].login, novo_map.login) != 0)
        {
            printf("AVISO: A disciplina '%s' ja eh lecionada por '%s'.\n",
                   disciplina_display_escolhida, todos_mapeamentos[i].login);
            printf("Deseja substituir '%s' por '%s' nesta disciplina? (s/n): ",
                   todos_mapeamentos[i].login, novo_map.login);
            char resp[3];
            if (fgets(resp, sizeof(resp), stdin) != NULL) {
                limpar_string(resp);
                if (tolower(resp[0]) == 's') {
                    mapeamento_existente_idx = i;
                    substituir_disciplina = 1;
                    break;
                } else {
                    printf("Cadastro cancelado.\n"); return;
                }
            } else { return; }
        }
        else if (strcmp(todos_mapeamentos[i].login, novo_map.login) == 0 &&
                 strcmp(todos_mapeamentos[i].disciplina_interna, novo_map.disciplina_interna) != 0)
        {
             mapeamento_existente_idx = i;
             substituir_disciplina = 0;
             break;
        }
        else if (strcmp(todos_mapeamentos[i].login, novo_map.login) == 0 &&
                 strcmp(todos_mapeamentos[i].disciplina_interna, novo_map.disciplina_interna) == 0)
        {
             printf("Este professor ja esta cadastrado para esta disciplina.\n"); return;
        }
    }

    if (mapeamento_existente_idx != -1) {
        // ... (lógica de atualização do array todos_mapeamentos - mantenha como antes) ...
         char login_antigo[MAX_LOGIN];
        if (substituir_disciplina) {
             strncpy(login_antigo, todos_mapeamentos[mapeamento_existente_idx].login, MAX_LOGIN -1);
             login_antigo[MAX_LOGIN - 1] = '\0';
        }
        strncpy(todos_mapeamentos[mapeamento_existente_idx].login, novo_map.login, MAX_LOGIN -1);
        strncpy(todos_mapeamentos[mapeamento_existente_idx].disciplina_interna, novo_map.disciplina_interna, MAX_DISCIPLINA -1);
         todos_mapeamentos[mapeamento_existente_idx].login[MAX_LOGIN - 1] = '\0';
         todos_mapeamentos[mapeamento_existente_idx].disciplina_interna[MAX_DISCIPLINA - 1] = '\0';
         if(substituir_disciplina) {
             printf("Professor '%s' substituido por '%s' para a disciplina '%s'.\n", login_antigo, novo_map.login, disciplina_display_escolhida);
         } else {
             printf("Disciplina do professor '%s' atualizada para '%s'.\n", novo_map.login, disciplina_display_escolhida);
         }

    } else if (num_mapeamentos_lidos < MAX_PROFESSORES) {
        todos_mapeamentos[num_mapeamentos_lidos] = novo_map;
        num_mapeamentos_lidos++;
        printf("Novo mapeamento adicionado: Professor '%s' para disciplina '%s'.\n", novo_map.login, disciplina_display_escolhida);
    } else {
        printf("[ERRO] Limite maximo de professores (%d) atingido. Nao foi possivel adicionar.\n", MAX_PROFESSORES);
        return;
    }
    salvar_todos_mapeamentos_professores(); // Salva mapeamentos (sobrescreve)

    // --- Salvar credenciais do professor (Ler/Adicionar/Reescrever) ---
    _mkdir(CONFIDENTIAL_DIR);
    num_linhas_creds_profs = ler_linhas_arquivo(ARQ_CREDS_PROFS, linhas_creds_profs, MAX_PROFESSORES);

     if (num_linhas_creds_profs < MAX_PROFESSORES) {
        // Formata a nova linha
        snprintf(linhas_creds_profs[num_linhas_creds_profs], MAX_LINHA_CSV, "%s,%s",
                 prof_cred.login, prof_cred.senha);
        num_linhas_creds_profs++;

        // Garante cabeçalho
        if (num_linhas_creds_profs == 1 || strstr(linhas_creds_profs[0], "Login") == NULL) {
            if (num_linhas_creds_profs == 1) {
                 strncpy(linhas_creds_profs[1], linhas_creds_profs[0], MAX_LINHA_CSV);
            } else {
                for(int i = num_linhas_creds_profs -1; i > 0; i--) {
                     strncpy(linhas_creds_profs[i], linhas_creds_profs[i-1], MAX_LINHA_CSV);
                }
            }
             snprintf(linhas_creds_profs[0], MAX_LINHA_CSV, "Login,Senha");
             num_linhas_creds_profs = (num_linhas_creds_profs == 1) ? 2 : num_linhas_creds_profs;
        }

        // Reescreve o arquivo
        if (salvar_linhas_arquivo(ARQ_CREDS_PROFS, linhas_creds_profs, num_linhas_creds_profs)) {
            printf("[SUCESSO] Credenciais do professor salvas em '%s'.\n", ARQ_CREDS_PROFS);
        }
    } else {
        printf("[ERRO] Limite maximo de professores (%d) atingido no arquivo de credenciais.\n", MAX_PROFESSORES);
    }
}
// --- FIM FUNÇÕES CADASTRO ---

// --- FUNÇÃO MAIN ---
int main() {
    if (!verificar_criar_diretorios()) {
        printf("Pressione Enter para sair...\n");
        getchar();
        return 1;
    }
    carregar_nomes_disciplinas();

    int escolha;
    do {
        printf("\n--- Sistema de Cadastro (C) ---\n");
        printf("1. Cadastrar Novo Aluno\n");
        printf("2. Cadastrar Novo Professor (Requer Senha Admin)\n");
        printf("3. Sair\n");
        printf("Escolha uma opcao: ");

        if (scanf("%d", &escolha) != 1) {
            printf("\nOpcao invalida. Digite um numero.\n");
            limpar_buffer();
            escolha = 0;
            continue;
        }
        limpar_buffer(); // Limpa após ler escolha

        switch (escolha) {
            case 1:
                cadastrar_aluno();
                break;
            case 2:
                printf("Digite a senha de administrador: ");
                char senha_admin_digitada[MAX_SENHA];
                if (fgets(senha_admin_digitada, sizeof(senha_admin_digitada), stdin) != NULL) {
                    limpar_string(senha_admin_digitada);
                    if (strcmp(senha_admin_digitada, ADMIN_PASSWORD) == 0) {
                        cadastrar_professor();
                    } else {
                        printf("Senha de administrador incorreta.\n");
                    }
                } else {
                    printf("Erro ao ler senha.\n");
                }
                break;
            case 3:
                printf("Saindo...\n");
                break;
            default:
                printf("Opcao invalida.\n");
        }
    } while (escolha != 3);

    return 0;
}
// --- FIM FUNÇÃO MAIN ---