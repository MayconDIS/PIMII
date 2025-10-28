// Sistema_cadastro.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <time.h>

#if defined(_WIN32) || defined(_WIN64)
    #include <direct.h> // _mkdir
    #define MKDIR(path) _mkdir(path)
#else
    #include <sys/stat.h>
    #include <sys/types.h>
    #define MKDIR(path) mkdir((path), 0755)
#endif

// --- CONFIGURAÇÃO DE CAMINHOS (ajuste se necessário) ---
#define BASE_DIR "C:\\Users\\mayco\\Documents\\GitHub\\PIMII\\output\\"  // ajuste conforme necessidade
#define CONFIDENTIAL_DIR BASE_DIR "dados_confidenciais\\"
#define OUTPUT_DIR BASE_DIR

#define ARQ_ALUNOS OUTPUT_DIR "alunos.csv"
#define ARQ_CREDS_ALUNOS CONFIDENTIAL_DIR "credenciais_alunos.csv"
#define ARQ_CREDS_PROFS CONFIDENTIAL_DIR "credenciais_professores.csv"
#define ARQ_MAP_PROFS CONFIDENTIAL_DIR "professores.csv"
#define ARQ_NOMES_DISC CONFIDENTIAL_DIR "disciplinas_nomes.csv"

// --- LIMITES ---
#define MAX_NOME 100
#define MAX_RA 20
#define MAX_EMAIL 100
#define MAX_LOGIN 40
#define MAX_SENHA 40
#define MAX_DISCIPLINA 50
#define NUM_DISCIPLINAS 5
#define MAX_LINHA_CSV 512
#define MAX_PROFESSORES 50
#define MAX_ALUNOS 500

// --- ESTRUTURAS ---
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

// --- GLOBAIS ---
const char* LISTA_DISCIPLINAS[NUM_DISCIPLINAS] = {
    "LingEstC", "Python", "EngSoft", "APS", "Extra"
};
NomeDisciplina DISPLAY_NAMES[NUM_DISCIPLINAS];
const char* ADMIN_PASSWORD = "admin123";

ProfessorMap todos_mapeamentos[MAX_PROFESSORES];
int num_mapeamentos_lidos = 0;

// Buffers para linhas em memória
char linhas_alunos[MAX_ALUNOS + 5][MAX_LINHA_CSV];
int num_linhas_alunos = 0;
char linhas_creds_alunos[MAX_ALUNOS + 5][MAX_LINHA_CSV];
int num_linhas_creds_alunos = 0;
char linhas_creds_profs[MAX_PROFESSORES + 5][MAX_LINHA_CSV];
int num_linhas_creds_profs = 0;

// --- UTILITÁRIOS ---

// --- INÍCIO: limpar_string ---
void limpar_string(char *str) {
    str[strcspn(str, "\r\n")] = '\0';
}
// --- FIM: limpar_string ---

// --- INÍCIO: limpar_buffer ---
void limpar_buffer() {
    int c;
    while ((c = getchar()) != '\n' && c != EOF);
}
// --- FIM: limpar_buffer ---

// --- INÍCIO: str_tolower ---
void str_tolower(char *str) {
    for (int i = 0; str[i]; i++) str[i] = (char)tolower((unsigned char)str[i]);
}
// --- FIM: str_tolower ---

// --- INÍCIO: verificar_criar_diretorios ---
int verificar_criar_diretorios() {
    if (MKDIR(OUTPUT_DIR) != 0) {
        // Pode retornar !=0 se já existir; ignoramos erro simples
    }
    if (MKDIR(CONFIDENTIAL_DIR) != 0) {
        // idem
    }
    // Testa abertura de arquivos (cria se não existirem)
    FILE *f_out = fopen(ARQ_ALUNOS, "a");
    FILE *f_conf = fopen(ARQ_CREDS_ALUNOS, "a");
    if (!f_out || !f_conf) {
        printf("\n[ERRO] Nao foi possivel acessar/criar diretorios de output.\n");
        if (f_out) fclose(f_out);
        if (f_conf) fclose(f_conf);
        return 0;
    }
    fclose(f_out);
    fclose(f_conf);
    return 1;
}
// --- FIM: verificar_criar_diretorios ---

// --- Nomes de disciplinas ---

// --- INÍCIO: salvar_nomes_disciplinas ---
void salvar_nomes_disciplinas() {
    MKDIR(CONFIDENTIAL_DIR);
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
// --- FIM: salvar_nomes_disciplinas ---

// --- INÍCIO: carregar_nomes_disciplinas ---
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
    // Consome cabeçalho se presente
    if (fgets(linha, sizeof(linha), f) == NULL) {
        fclose(f);
        salvar_nomes_disciplinas();
        return;
    }
    while (fgets(linha, sizeof(linha), f)) {
        limpar_string(linha);
        if (strlen(linha) == 0) continue;
        char linha_copy[MAX_LINHA_CSV];
        strncpy(linha_copy, linha, MAX_LINHA_CSV - 1);
        linha_copy[MAX_LINHA_CSV - 1] = '\0';
        char *interno_csv = strtok(linha_copy, ",");
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
// --- FIM: carregar_nomes_disciplinas ---

// --- Leitura/Escrita genérica de linhas (retorna numero de linhas lidas) ---

// --- INÍCIO: ler_linhas_arquivo ---
int ler_linhas_arquivo(const char *caminho, char linhas[][MAX_LINHA_CSV], int max_linhas) {
    int count = 0;
    FILE *f = fopen(caminho, "r");
    if (!f) return 0;
    while (count < max_linhas && fgets(linhas[count], MAX_LINHA_CSV, f)) {
        limpar_string(linhas[count]);
        if (strlen(linhas[count]) == 0) continue; // ignora linhas vazias
        count++;
    }
    fclose(f);
    return count;
}
// --- FIM: ler_linhas_arquivo ---

// --- INÍCIO: salvar_linhas_arquivo ---
int salvar_linhas_arquivo(const char *caminho, char linhas[][MAX_LINHA_CSV], int num_linhas) {
    FILE *f = fopen(caminho, "w");
    if (!f) {
        printf("\n[ERRO] Nao foi possivel abrir '%s' para escrita.\n", caminho);
        return 0;
    }
    for (int i = 0; i < num_linhas; i++) {
        fprintf(f, "%s\n", linhas[i]);
    }
    fclose(f);
    return 1;
}
// --- FIM: salvar_linhas_arquivo ---

// Garante cabeçalho no array (insere no índice 0 se faltante).
// --- INÍCIO: garantir_cabecalho ---
void garantir_cabecalho(char linhas[][MAX_LINHA_CSV], int *p_num_linhas, const char* cabecalho, int max_total) {
    if (*p_num_linhas == 0) {
        if (max_total < 2) return;
        // insere cabecalho e mantém espaço para ao menos 1 dado
        strncpy(linhas[0], cabecalho, MAX_LINHA_CSV - 1);
        linhas[0][MAX_LINHA_CSV - 1] = '\0';
        *p_num_linhas = 1;
    } else {
        if (strstr(linhas[0], cabecalho) == NULL) {
            // shift para a direita para inserir cabeçalho se couber
            if (*p_num_linhas + 1 > max_total) {
                // nao tem espaço para inserir cabecalho, aborta (raro)
                return;
            }
            for (int i = *p_num_linhas; i > 0; i--) {
                strncpy(linhas[i], linhas[i-1], MAX_LINHA_CSV - 1);
                linhas[i][MAX_LINHA_CSV - 1] = '\0';
            }
            strncpy(linhas[0], cabecalho, MAX_LINHA_CSV - 1);
            linhas[0][MAX_LINHA_CSV - 1] = '\0';
            (*p_num_linhas)++;
        }
    }
}
// --- FIM: garantir_cabecalho ---

// --- Mapeamento de professores ---

// --- INÍCIO: ler_mapeamentos_professores ---
void ler_mapeamentos_professores() {
    num_mapeamentos_lidos = 0;
    char linhas_map[MAX_PROFESSORES + 5][MAX_LINHA_CSV];
    int total_linhas = ler_linhas_arquivo(ARQ_MAP_PROFS, linhas_map, MAX_PROFESSORES);

    int inicio = (total_linhas > 0 && strstr(linhas_map[0], "Login") != NULL) ? 1 : 0;

    for (int i = inicio; i < total_linhas && num_mapeamentos_lidos < MAX_PROFESSORES; i++) {
        char copia[MAX_LINHA_CSV];
        strncpy(copia, linhas_map[i], MAX_LINHA_CSV - 1);
        copia[MAX_LINHA_CSV - 1] = '\0';
        char *login = strtok(copia, ",");
        char *disc = strtok(NULL, ",");
        if (login && disc) {
            strncpy(todos_mapeamentos[num_mapeamentos_lidos].login, login, MAX_LOGIN - 1);
            todos_mapeamentos[num_mapeamentos_lidos].login[MAX_LOGIN - 1] = '\0';
            strncpy(todos_mapeamentos[num_mapeamentos_lidos].disciplina_interna, disc, MAX_DISCIPLINA - 1);
            todos_mapeamentos[num_mapeamentos_lidos].disciplina_interna[MAX_DISCIPLINA - 1] = '\0';
            num_mapeamentos_lidos++;
        }
    }
    printf("Carregados %d mapeamentos de professores de '%s'.\n", num_mapeamentos_lidos, ARQ_MAP_PROFS);
}
// --- FIM: ler_mapeamentos_professores ---

// --- INÍCIO: salvar_todos_mapeamentos_professores ---
void salvar_todos_mapeamentos_professores() {
    MKDIR(CONFIDENTIAL_DIR);
    char linhas_map[MAX_PROFESSORES + 5][MAX_LINHA_CSV];
    int total = 0;
    snprintf(linhas_map[total++], MAX_LINHA_CSV, "Login,Disciplina");
    for (int i = 0; i < num_mapeamentos_lidos && total < MAX_PROFESSORES; i++) {
        snprintf(linhas_map[total++], MAX_LINHA_CSV, "%s,%s", todos_mapeamentos[i].login, todos_mapeamentos[i].disciplina_interna);
    }
    if (salvar_linhas_arquivo(ARQ_MAP_PROFS, linhas_map, total)) {
        printf("[SUCESSO] Mapeamentos de professores salvos em '%s'.\n", ARQ_MAP_PROFS);
    }
}
// --- FIM: salvar_todos_mapeamentos_professores ---

// --- CADASTROS ---

// --- INÍCIO: cadastrar_aluno ---
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
    strncpy(nome_temp, aluno_info.nome, sizeof(nome_temp) - 1);
    nome_temp[sizeof(nome_temp)-1] = '\0';
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

    // Salvar credenciais de alunos
    MKDIR(CONFIDENTIAL_DIR);
    num_linhas_creds_alunos = ler_linhas_arquivo(ARQ_CREDS_ALUNOS, linhas_creds_alunos, MAX_ALUNOS);
    // Formata nova linha
    if (num_linhas_creds_alunos < MAX_ALUNOS) {
        snprintf(linhas_creds_alunos[num_linhas_creds_alunos], MAX_LINHA_CSV, "%s,%s", aluno_cred.login, aluno_cred.senha);
        num_linhas_creds_alunos++;
        // Garante cabeçalho
        garantir_cabecalho(linhas_creds_alunos, &num_linhas_creds_alunos, "Login,Senha", MAX_ALUNOS);
        if (salvar_linhas_arquivo(ARQ_CREDS_ALUNOS, linhas_creds_alunos, num_linhas_creds_alunos)) {
            printf("[SUCESSO] Credenciais salvas em '%s'.\n", ARQ_CREDS_ALUNOS);
        }
    } else {
        printf("[ERRO] Limite maximo de alunos (%d) atingido no arquivo de credenciais.\n", MAX_ALUNOS);
    }

    // Salvar dados academicos (alunos)
    MKDIR(OUTPUT_DIR);
    num_linhas_alunos = ler_linhas_arquivo(ARQ_ALUNOS, linhas_alunos, MAX_ALUNOS);
    if (num_linhas_alunos < MAX_ALUNOS) {
        char nova_linha_aluno[MAX_LINHA_CSV];
        // Constrói string de notas iniciais com segurança
        char buffer_notas[MAX_LINHA_CSV];
        buffer_notas[0] = '\0';
        for (int i = 0; i < NUM_DISCIPLINAS; i++) {
            // cada nota tem formato ,0.00 (4 chars + comma)
            strncat(buffer_notas, ",0.00", sizeof(buffer_notas) - strlen(buffer_notas) - 1);
        }
        strncat(buffer_notas, ",0.00", sizeof(buffer_notas) - strlen(buffer_notas) - 1); // Media Geral

        snprintf(nova_linha_aluno, sizeof(nova_linha_aluno), "%s,%s,%s%s",
                 aluno_info.nome, aluno_info.ra, aluno_info.email, buffer_notas);

        // adiciona
        strncpy(linhas_alunos[num_linhas_alunos], nova_linha_aluno, MAX_LINHA_CSV - 1);
        linhas_alunos[num_linhas_alunos][MAX_LINHA_CSV - 1] = '\0';
        num_linhas_alunos++;

        // Garante cabeçalho dinâmico
        char cabecalho[MAX_LINHA_CSV] = "Nome,RA,Email";
        for (int i = 0; i < NUM_DISCIPLINAS; i++) {
            strncat(cabecalho, ",", sizeof(cabecalho) - strlen(cabecalho) - 1);
            strncat(cabecalho, LISTA_DISCIPLINAS[i], sizeof(cabecalho) - strlen(cabecalho) - 1);
        }
        strncat(cabecalho, ",Media Geral", sizeof(cabecalho) - strlen(cabecalho) - 1);
        garantir_cabecalho(linhas_alunos, &num_linhas_alunos, cabecalho, MAX_ALUNOS);

        if (salvar_linhas_arquivo(ARQ_ALUNOS, linhas_alunos, num_linhas_alunos)) {
            printf("[SUCESSO] Dados academicos salvos em '%s'.\n", ARQ_ALUNOS);
        }
    } else {
        printf("[ERRO] Limite maximo de alunos (%d) atingido no arquivo de dados.\n", MAX_ALUNOS);
    }
}
// --- FIM: cadastrar_aluno ---

// --- INÍCIO: cadastrar_professor ---
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
    limpar_buffer();

    if (escolha_num < 1 || escolha_num > NUM_DISCIPLINAS) {
        printf("Escolha invalida. Cancelado.\n");
        return;
    }
    disciplina_idx = escolha_num - 1;

    strncpy(novo_map.login, prof_cred.login, MAX_LOGIN - 1);
    novo_map.login[MAX_LOGIN - 1] = '\0';
    strncpy(novo_map.disciplina_interna, DISPLAY_NAMES[disciplina_idx].interno, MAX_DISCIPLINA - 1);
    novo_map.disciplina_interna[MAX_DISCIPLINA - 1] = '\0';
    strncpy(disciplina_display_escolhida, DISPLAY_NAMES[disciplina_idx].display, MAX_DISCIPLINA - 1);
    disciplina_display_escolhida[MAX_DISCIPLINA - 1] = '\0';

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
                strncpy(disciplina_display_escolhida, novo_nome, MAX_DISCIPLINA - 1);
                disciplina_display_escolhida[MAX_DISCIPLINA - 1] = '\0';
                printf("Disciplina 'Extra' renomeada para '%s'.\n", novo_nome);
            }
        }
    }

    // carregar mapeamentos atuais
    ler_mapeamentos_professores();

    for (int i = 0; i < num_mapeamentos_lidos; i++) {
        if (strcmp(todos_mapeamentos[i].disciplina_interna, novo_map.disciplina_interna) == 0 &&
            strcmp(todos_mapeamentos[i].login, novo_map.login) != 0)
        {
            printf("AVISO: A disciplina '%s' ja eh lecionada por '%s'.\n",
                   disciplina_display_escolhida, todos_mapeamentos[i].login);
            printf("Deseja substituir '%s' por '%s' nesta disciplina? (s/n): ",
                   todos_mapeamentos[i].login, novo_map.login);
            char resp[8];
            if (fgets(resp, sizeof(resp), stdin) != NULL) {
                limpar_string(resp);
                if (tolower(resp[0]) == 's') {
                    mapeamento_existente_idx = i;
                    substituir_disciplina = 1;
                    break;
                } else {
                    printf("Cadastro cancelado.\n");
                    return;
                }
            } else return;
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
            printf("Este professor ja esta cadastrado para esta disciplina.\n");
            return;
        }
    }

    if (mapeamento_existente_idx != -1) {
        char login_antigo[MAX_LOGIN];
        if (substituir_disciplina) {
            strncpy(login_antigo, todos_mapeamentos[mapeamento_existente_idx].login, MAX_LOGIN - 1);
            login_antigo[MAX_LOGIN - 1] = '\0';
        }
        strncpy(todos_mapeamentos[mapeamento_existente_idx].login, novo_map.login, MAX_LOGIN - 1);
        strncpy(todos_mapeamentos[mapeamento_existente_idx].disciplina_interna, novo_map.disciplina_interna, MAX_DISCIPLINA - 1);
        todos_mapeamentos[mapeamento_existente_idx].login[MAX_LOGIN - 1] = '\0';
        todos_mapeamentos[mapeamento_existente_idx].disciplina_interna[MAX_DISCIPLINA - 1] = '\0';
        if (substituir_disciplina) {
            printf("Professor '%s' substituido por '%s' para a disciplina '%s'.\n", login_antigo, novo_map.login, disciplina_display_escolhida);
        } else {
            printf("Disciplina do professor '%s' atualizada para '%s'.\n", novo_map.login, disciplina_display_escolhida);
        }
    } else if (num_mapeamentos_lidos < MAX_PROFESSORES) {
        todos_mapeamentos[num_mapeamentos_lidos++] = novo_map;
        printf("Novo mapeamento adicionado: Professor '%s' para disciplina '%s'.\n", novo_map.login, disciplina_display_escolhida);
    } else {
        printf("[ERRO] Limite maximo de professores (%d) atingido. Nao foi possivel adicionar.\n", MAX_PROFESSORES);
        return;
    }

    salvar_todos_mapeamentos_professores();

    // Salvar credenciais professor
    MKDIR(CONFIDENTIAL_DIR);
    num_linhas_creds_profs = ler_linhas_arquivo(ARQ_CREDS_PROFS, linhas_creds_profs, MAX_PROFESSORES);
    if (num_linhas_creds_profs < MAX_PROFESSORES) {
        snprintf(linhas_creds_profs[num_linhas_creds_profs], MAX_LINHA_CSV, "%s,%s", prof_cred.login, prof_cred.senha);
        num_linhas_creds_profs++;
        garantir_cabecalho(linhas_creds_profs, &num_linhas_creds_profs, "Login,Senha", MAX_PROFESSORES);
        if (salvar_linhas_arquivo(ARQ_CREDS_PROFS, linhas_creds_profs, num_linhas_creds_profs)) {
            printf("[SUCESSO] Credenciais do professor salvas em '%s'.\n", ARQ_CREDS_PROFS);
        }
    } else {
        printf("[ERRO] Limite maximo de professores (%d) atingido no arquivo de credenciais.\n", MAX_PROFESSORES);
    }
}
// --- FIM: cadastrar_professor ---

// --- MAIN ---

// --- INÍCIO: main ---
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
        limpar_buffer();

        switch (escolha) {
            case 1:
                cadastrar_aluno();
                break;
            case 2:
            {
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
            }
            case 3:
                printf("Saindo...\n");
                break;
            default:
                printf("Opcao invalida.\n");
        }
    } while (escolha != 3);

    return 0;
}
// --- FIM: main ---