# Interface_PIMII.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import csv
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import io
import random

# =================== CONFIGS ===================
BASE_PROJECT_DIR = r"C:\Users\mayco\Documents\GitHub\PIMII" # Adapte se necessário
OUTPUT_DIR = os.path.join(BASE_PROJECT_DIR, "output")
CONFIDENTIAL_DATA_DIR = os.path.join(OUTPUT_DIR, "dados_confidenciais")

ARQUIVO_CREDENCIAIS = os.path.join(CONFIDENTIAL_DATA_DIR, "credenciais_alunos.csv")
ARQUIVO_CREDENCIAIS_PROFESSORES = os.path.join(CONFIDENTIAL_DATA_DIR, "credenciais_professores.csv")
ARQUIVO_MAPEAMENTO_PROFESSORES = os.path.join(CONFIDENTIAL_DATA_DIR, "professores.csv")
ARQUIVO_NOMES_DISCIPLINAS = os.path.join(CONFIDENTIAL_DATA_DIR, "disciplinas_nomes.csv")
DEFAULT_CSV_FILE_PATH = os.path.join(CONFIDENTIAL_DATA_DIR, "alunos.csv")
DEFAULT_CSV_FILE = "alunos.csv"
CREDENTIALS_DIR = CONFIDENTIAL_DATA_DIR 

BG_DARK = '#212121'
FRAME_BG = '#3A3A3A'
TEXT_FG = 'white'
BTN_ROXO_BASE = '#4A148C'
BTN_ROXO_CLARO = '#6A1B9A'
BTN_FG = 'white'
BTN_EXIT_BG = '#8B0000'
BTN_AMARELO_CADASTRO = '#CCAA00'

# =================== GLOBAIS (Corrigido) ===================
LISTA_DISCIPLINAS = ["LingEstC", "Python", "EngSoft", "APS", "Extra"] 
DISPLAY_NAMES = {} 

dados_alunos = []
caminho_arquivo_atual = None
nivel_acesso_atual = None
usuario_logado = None
canvas_grafico = None
botao_fechar_grafico = None
janela_imagem_fundo = None
geometria_principal = None 
geometria_login = None 
login_frame_global = None 

NUM_COLUNAS_ESPERADAS = 3 + len(LISTA_DISCIPLINAS) + 1 
COLUNA_MAP = {}
i = 3 
for disc in LISTA_DISCIPLINAS:
    COLUNA_MAP[disc] = i
    i += 1
COLUNA_MAP["Media Geral"] = i

# --- MUDANÇA: Credenciais fixas removidas ---
CREDENCIAIS = {
    "Admin": {"admin": "admin123"},
    "Professores": {},
    "Alunos": {}
}
PROFESSORES_POR_DISCIPLINA = {}
PROFESSOR_TO_COLNAME = {}
# --- FIM DA MUDANÇA ---

# --- Variáveis Globais para Widgets da Interface Principal ---
frame_principal_interativo = None
frame_botoes = None
frame_tree = None
btn_selecionar = None
btn_lancar_notas = None
btn_ver_notas = None
btn_gerar_grafico = None
btn_ver_professores = None
btn_ia = None
btn_sair = None
tree = None
scrollbar = None
# --- Fim Variáveis Globais ---

# =================== UTILIDADES ===================
# --- INÍCIO: carregar_nomes_disciplinas ---
def carregar_nomes_disciplinas():
    """Carrega os nomes de exibição das disciplinas a partir do CSV."""
    global DISPLAY_NAMES

    DISPLAY_NAMES = {}
    for disc in LISTA_DISCIPLINAS:
        DISPLAY_NAMES[disc] = disc
    DISPLAY_NAMES["Media Geral"] = "Media Geral"

    if not os.path.exists(ARQUIVO_NOMES_DISCIPLINAS):
        salvar_nomes_disciplinas()
        return

    try:
        with open(ARQUIVO_NOMES_DISCIPLINAS, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader, None)
            for linha in reader:
                if len(linha) >= 2:
                    internal_name, display_name = linha
                    if internal_name in DISPLAY_NAMES:
                        DISPLAY_NAMES[internal_name] = display_name
    except Exception as e:
        print(f"Erro ao carregar nomes de disciplinas: {e}. Usando padrões.")
        salvar_nomes_disciplinas()
# --- FIM: carregar_nomes_disciplinas ---

# --- INÍCIO: salvar_nomes_disciplinas ---
def salvar_nomes_disciplinas():
    """Salva o mapa de nomes de exibição (DISPLAY_NAMES) no CSV."""
    os.makedirs(CONFIDENTIAL_DATA_DIR, exist_ok=True)
    try:
        with open(ARQUIVO_NOMES_DISCIPLINAS, "w", newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["InternalName", "DisplayName"])
            for internal, display in DISPLAY_NAMES.items():
                if internal in LISTA_DISCIPLINAS:
                    writer.writerow([internal, display])
        return True
    except Exception as e:
        messagebox.showwarning("Aviso", f"Houve erro ao salvar os nomes das disciplinas: {e}")
        return False
# --- FIM: salvar_nomes_disciplinas ---

# --- INÍCIO: carregar_credenciais_alunos ---
def carregar_credenciais_alunos():
    novas_creds = {}
    if not os.path.exists(ARQUIVO_CREDENCIAIS):
        return novas_creds
    conteudo_bruto = None
    for encoding in ['utf-8', 'latin-1']:
        try:
            with open(ARQUIVO_CREDENCIAIS, 'r', encoding=encoding) as f:
                conteudo_bruto = f.read()
            break
        except Exception:
            continue
    if conteudo_bruto is None:
        return novas_creds
    try:
        reader = csv.reader(io.StringIO(conteudo_bruto))
        header = next(reader, None)
        for linha in reader:
            if len(linha) >= 2:
                login = linha[0].strip().lower()
                senha = linha[1].strip()
                if login and senha:
                    novas_creds[login] = senha
    except Exception:
        pass
    return novas_creds
# --- FIM: carregar_credenciais_alunos ---

# --- INÍCIO: salvar_credenciais_csv (ATUALIZADO) ---
def salvar_credenciais_csv(login, senha):
    """Lê, adiciona e reescreve o CSV de credenciais de alunos."""
    os.makedirs(CONFIDENTIAL_DATA_DIR, exist_ok=True) 
    cabecalho = ["Login", "Senha"]
    
    linhas = ler_linhas_csv(ARQUIVO_CREDENCIAIS)
    if linhas is None: return False # Erro na leitura
    
    # Adiciona a nova linha de dados
    linhas.append([login, senha])
    
    # Salva o arquivo inteiro
    return salvar_linhas_csv(ARQUIVO_CREDENCIAIS, linhas, cabecalho)
# --- FIM: salvar_credenciais_csv ---

# --- INÍCIO: salvar_dados_no_csv (ATUALIZADO) ---
def salvar_dados_no_csv(caminho, dados_novos, modo='a'): # 'modo' não é mais usado
    """Lê, adiciona e reescreve o CSV de dados de alunos."""
    os.makedirs(CONFIDENTIAL_DATA_DIR, exist_ok=True) 
    cabecalho = ["Nome","RA","Email"] + LISTA_DISCIPLINAS + ["Media Geral"]
    
    linhas = ler_linhas_csv(caminho)
    if linhas is None: return False # Erro na leitura
    
    # Adiciona a nova linha de dados
    linhas.append(dados_novos)
    
    # Salva o arquivo inteiro
    return salvar_linhas_csv(caminho, linhas, cabecalho)
# --- FIM: salvar_dados_no_csv ---

# ... (pule _recalcular_media_geral e as funções de carregar) ...

# --- INÍCIO: salvar_credenciais_professor_csv (ATUALIZADO) ---
def salvar_credenciais_professor_csv(login, senha):
    """Lê, adiciona e reescreve o CSV de credenciais de professores."""
    os.makedirs(CONFIDENTIAL_DATA_DIR, exist_ok=True) 
    cabecalho = ["Login", "Senha"]
    
    linhas = ler_linhas_csv(ARQUIVO_CREDENCIAIS_PROFESSORES)
    if linhas is None: return False # Erro na leitura
    
    # Adiciona a nova linha de dados
    linhas.append([login, senha])
    
    # Salva o arquivo inteiro
    return salvar_linhas_csv(ARQUIVO_CREDENCIAIS_PROFESSORES, linhas, cabecalho)
# --- FIM: salvar_credenciais_professor_csv ---

# --- INÍCIO: salvar_mapeamento_professor_csv (ATUALIZADO) ---
def salvar_mapeamento_professor_csv(login, disciplina_interna):
    """Lê o arquivo de mapeamento, atualiza-o e o reescreve."""
    os.makedirs(CONFIDENTIAL_DATA_DIR, exist_ok=True)
    cabecalho = ["Login", "Disciplina"]
    
    linhas = ler_linhas_csv(ARQUIVO_MAPEAMENTO_PROFESSORES)
    if linhas is None: return False # Erro na leitura
    
    # Converte linhas lidas para um dicionário para fácil manipulação
    mapeamentos = {}
    # Pula o cabeçalho se ele existir e for correto
    if linhas and linhas[0] == cabecalho:
        for row in linhas[1:]:
            if len(row) >= 2:
                mapeamentos[row[0].strip().lower()] = row[1].strip()
    else: # Sem cabeçalho ou cabeçalho incorreto
         for row in linhas:
             if len(row) >= 2:
                 # Assume que qualquer linha pode ser dado se não houver cabeçalho
                 if row[0].lower() != "login": 
                     mapeamentos[row[0].strip().lower()] = row[1].strip()

    # Atualiza o dicionário com a nova lógica
    mapeamentos[login] = disciplina_interna
    for prof_login, disc in list(mapeamentos.items()):
        if disc == disciplina_interna and prof_login != login:
            del mapeamentos[prof_login]
        if prof_login == login and disc != disciplina_interna:
             del mapeamentos[prof_login]

    # Converte o dicionário de volta para lista de linhas
    linhas_para_salvar = []
    for prof_login, disc in mapeamentos.items():
        linhas_para_salvar.append([prof_login, disc])
        
    # Salva o arquivo inteiro (sobrescrevendo)
    return salvar_linhas_csv(ARQUIVO_MAPEAMENTO_PROFESSORES, linhas_para_salvar, cabecalho)
# --- FIM: salvar_mapeamento_professor_csv ---

# --- INÍCIO: _recalcular_media_geral ---
def _recalcular_media_geral(aluno):
    notas = []
    if len(aluno) >= NUM_COLUNAS_ESPERADAS:
        for i in range(3, 3 + len(LISTA_DISCIPLINAS)):
            try:
                v = str(aluno[i]).strip()
                if v != "":
                    notas.append(float(v))
            except (ValueError, IndexError):
                pass

        media_idx = COLUNA_MAP["Media Geral"]
        if notas:
            media = sum(notas) / len(notas)
            if media_idx < len(aluno):
                 aluno[media_idx] = f"{media:.2f}"
            else:
                 while len(aluno) <= media_idx: aluno.append("0.00")
                 aluno[media_idx] = f"{media:.2f}"
        else:
            if media_idx < len(aluno):
                 aluno[media_idx] = "0.00"
            else:
                 while len(aluno) <= media_idx: aluno.append("0.00")
                 aluno[media_idx] = "0.00"
    else:
         while len(aluno) < NUM_COLUNAS_ESPERADAS:
             aluno.append("0.00")
# --- FIM: _recalcular_media_geral ---

# --- INÍCIO: carregar_credenciais_professores ---
def carregar_credenciais_professores():
    novas_creds = {}
    if not os.path.exists(ARQUIVO_CREDENCIAIS_PROFESSORES):
        return novas_creds

    conteudo_bruto = None
    for encoding in ['utf-8', 'latin-1']:
        try:
            with open(ARQUIVO_CREDENCIAIS_PROFESSORES, 'r', encoding=encoding) as f:
                conteudo_bruto = f.read()
            break
        except Exception:
            continue
    if conteudo_bruto is None:
        return novas_creds

    try:
        reader = csv.reader(io.StringIO(conteudo_bruto))
        header = next(reader, None)
        for linha in reader:
            if len(linha) >= 2:
                login = linha[0].strip().lower()
                senha = linha[1].strip()
                if login and senha:
                    novas_creds[login] = senha
    except Exception:
        pass
    return novas_creds
# --- FIM: carregar_credenciais_professores ---

# --- INÍCIO: carregar_mapeamento_professores ---
def carregar_mapeamento_professores():
    novo_map = {}
    if not os.path.exists(ARQUIVO_MAPEAMENTO_PROFESSORES):
        return novo_map

    conteudo_bruto = None
    for encoding in ['utf-8', 'latin-1']:
        try:
            with open(ARQUIVO_MAPEAMENTO_PROFESSORES, 'r', encoding=encoding) as f:
                conteudo_bruto = f.read()
            break
        except Exception:
            continue
    if conteudo_bruto is None:
        return novo_map

    try:
        reader = csv.reader(io.StringIO(conteudo_bruto))
        header = next(reader, None)
        for linha in reader:
            if len(linha) >= 2:
                login = linha[0].strip().lower()
                disciplina = linha[1].strip()
                if login and disciplina:
                    novo_map[login] = disciplina
    except Exception:
        pass
    return novo_map
# --- FIM: carregar_mapeamento_professores ---

# --- INÍCIO: salvar_credenciais_professor_csv ---
def salvar_credenciais_professor_csv(login, senha):
    os.makedirs(CONFIDENTIAL_DATA_DIR, exist_ok=True)
    try:
        adicionar_cabecalho = not os.path.exists(ARQUIVO_CREDENCIAIS_PROFESSORES) or os.path.getsize(ARQUIVO_CREDENCIAIS_PROFESSORES) == 0
        with open(ARQUIVO_CREDENCIAIS_PROFESSORES, "a", newline='', encoding='utf-8') as arq_creds:
            writer = csv.writer(arq_creds)
            if adicionar_cabecalho:
                writer.writerow(["Login", "Senha"])
            writer.writerow([login, senha])
        return True
    except Exception as e:
        messagebox.showwarning("Aviso", f"Houve erro ao salvar as credenciais do professor: {e}")
        return False
# --- FIM: salvar_credenciais_professor_csv ---

# --- INÍCIO: salvar_mapeamento_professor_csv (CORRIGIDO) ---
def salvar_mapeamento_professor_csv(login, disciplina_interna):
    """Lê o arquivo de mapeamento, atualiza-o e o reescreve."""
    os.makedirs(CONFIDENTIAL_DATA_DIR, exist_ok=True)
    try:
        # 1. Lê todos os mapeamentos existentes do arquivo
        mapeamentos = {}
        if os.path.exists(ARQUIVO_MAPEAMENTO_PROFESSORES):
             with open(ARQUIVO_MAPEAMENTO_PROFESSORES, 'r', newline='', encoding='utf-8') as f:
                 reader = csv.reader(f)
                 try:
                     header = next(reader, None) # Pula cabeçalho
                     for row in reader:
                         if len(row) >= 2:
                             mapeamentos[row[0].strip().lower()] = row[1].strip()
                 except StopIteration:
                     pass # Arquivo estava vazio ou só tinha cabeçalho

        # 2. Adiciona/Atualiza o novo mapeamento
        mapeamentos[login] = disciplina_interna

        # 3. Remove o mapeamento antigo se um professor foi substituído
        for prof_login, disc in list(mapeamentos.items()):
            if disc == disciplina_interna and prof_login != login:
                del mapeamentos[prof_login]
            # Remove o professor de qualquer outra disciplina que ele lecionava
            if prof_login == login and disc != disciplina_interna:
                 del mapeamentos[prof_login]

        # 4. Reescreve o arquivo inteiro (modo "w")
        with open(ARQUIVO_MAPEAMENTO_PROFESSORES, "w", newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Login", "Disciplina"])
            for prof_login, disc in mapeamentos.items():
                 writer.writerow([prof_login, disc])
        return True

    except Exception as e:
        messagebox.showwarning("Aviso", f"Houve erro ao salvar o mapeamento do professor: {e}")
        return False
# --- FIM: salvar_mapeamento_professor_csv ---

# --- INÍCIO: carregar_dados_professores (CORRIGIDO) ---
def carregar_dados_professores():
    global CREDENCIAIS, PROFESSOR_TO_COLNAME, PROFESSORES_POR_DISCIPLINA

    # 1. Carrega credenciais do CSV (substitui o dict global)
    creds_csv = carregar_credenciais_professores()
    CREDENCIAIS["Professores"] = creds_csv # Substitui, não atualiza

    # 2. Carrega mapeamentos do CSV (substitui o dict global)
    map_csv = carregar_mapeamento_professores()
    PROFESSOR_TO_COLNAME = map_csv # Substitui, não atualiza

    # 3. Reconstrói o dicionário INVERSO (Disciplina -> Login)
    PROFESSORES_POR_DISCIPLINA.clear()
    for login, disciplina in PROFESSOR_TO_COLNAME.items():
        if disciplina in COLUNA_MAP:
            PROFESSORES_POR_DISCIPLINA[disciplina] = login

    print("Dados de professores carregados e mesclados.")
# --- FIM: carregar_dados_professores ---

# --- INÍCIO: Novas Funções Auxiliares de Leitura/Escrita ---
def ler_linhas_csv(caminho_arquivo):
    """Lê todas as linhas de um CSV, ignorando linhas totalmente vazias."""
    if not os.path.exists(caminho_arquivo):
        return [] # Retorna lista vazia se o arquivo não existe
    
    linhas = []
    encoding_usada = 'utf-8' # Tenta utf-8 primeiro
    try:
        with open(caminho_arquivo, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if row: # Adiciona apenas se a linha não for [ ]
                    linhas.append(row)
    except UnicodeDecodeError:
        try:
            # Tenta latin-1 como fallback
            encoding_usada = 'latin-1'
            with open(caminho_arquivo, 'r', newline='', encoding='latin-1') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row: 
                        linhas.append(row)
        except Exception as e:
            messagebox.showerror("Erro de Leitura", f"Não foi possível ler {os.path.basename(caminho_arquivo)} com {encoding_usada}: {e}")
            return None # Indica erro
    except Exception as e:
         messagebox.showerror("Erro de Leitura", f"Não foi possível ler {os.path.basename(caminho_arquivo)}: {e}")
         return None # Indica erro
         
    return linhas

def salvar_linhas_csv(caminho_arquivo, linhas, cabecalho_esperado):
    """Salva uma lista de linhas em um arquivo CSV, sobrescrevendo (modo 'w')."""
    try:
        # Garante que o cabeçalho esteja presente e correto
        if not linhas or linhas[0] != cabecalho_esperado:
            # Remove cabeçalho antigo/incorreto se houver
            if linhas and len(linhas[0]) == len(cabecalho_esperado):
                linhas.pop(0)
            linhas.insert(0, cabecalho_esperado)
            
        with open(caminho_arquivo, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(linhas)
        return True
    except Exception as e:
        messagebox.showerror("Erro de Salvamento", f"Não foi possível salvar em {os.path.basename(caminho_arquivo)}: {e}")
        return False
# --- FIM: Novas Funções Auxiliares ---

# =================== JANELA FLUTUANTE (IMAGEM) ===================
# --- INÍCIO: mostrar_janela_imagem_flutuante ---
def mostrar_janela_imagem_flutuante(janela_pai, caminho_imagem):
    """Cria e posiciona uma janela de imagem abaixo da janela de login."""
    global janela_imagem_fundo
    # Aumenta o delay para garantir que a janela de login esteja 100% desenhada
    janela_pai.after(100, lambda: _posicionar_imagem_flutuante(janela_pai, caminho_imagem)) 

def _posicionar_imagem_flutuante(janela_pai, caminho_imagem):
     global janela_imagem_fundo
     try:
        if not janela_pai.winfo_exists(): return

        janela_pai.update_idletasks()
        pos_x_login = janela_pai.winfo_x()
        pos_y_login = janela_pai.winfo_y()
        largura_login = janela_pai.winfo_width()
        altura_login = janela_pai.winfo_height()

        largura_img = largura_login
        altura_img = 100
        MARGEM_VERTICAL = 40

        if janela_imagem_fundo and janela_imagem_fundo.winfo_exists():
            janela_imagem_fundo.geometry(f'{largura_img}x{altura_img}+{pos_x_login}+{pos_y_login + altura_login + MARGEM_VERTICAL}')
            janela_imagem_fundo.lift()
            janela_imagem_fundo.attributes('-topmost', True)
            return

        if not os.path.exists(caminho_imagem):
            print(f"AVISO: Imagem flutuante '{caminho_imagem}' não encontrada.")
            return

        janela_imagem_fundo = tk.Toplevel(janela_pai, bg=FRAME_BG)
        janela_imagem_fundo.title("Imagem Flutuante")
        janela_imagem_fundo.attributes('-topmost', True)
        
        # --- LINHA REMOVIDA ---
        # janela_imagem_fundo.overrideredirect(True) 
        # --- FIM DA REMOÇÃO ---

        img_pil = Image.open(caminho_imagem).convert("RGB")
        img_redimensionada = img_pil.resize((largura_img, altura_img), Image.LANCZOS)
        img_tk_local = ImageTk.PhotoImage(img_redimensionada)

        label_fundo = tk.Label(janela_imagem_fundo, image=img_tk_local, bg=FRAME_BG)
        label_fundo.pack(fill=tk.BOTH, expand=True)

        janela_imagem_fundo.photo_image = img_tk_local

        janela_imagem_fundo.geometry(f'{largura_img}x{altura_img}+{pos_x_login}+{pos_y_login + altura_login + MARGEM_VERTICAL}')
        janela_imagem_fundo.lift()

        janela_pai.bind("<Destroy>", fechar_janela_imagem_fundo, add="+")

     except Exception as e:
        print(f"ERRO ao mostrar imagem flutuante: {e}")
        if janela_imagem_fundo and janela_imagem_fundo.winfo_exists():
            janela_imagem_fundo.destroy()
        janela_imagem_fundo = None
# --- FIM: mostrar_janela_imagem_flutuante ---

# --- INÍCIO: fechar_janela_imagem_fundo ---
def fechar_janela_imagem_fundo(*args):
    """Fecha a janela flutuante."""
    global janela_imagem_fundo
    if janela_imagem_fundo and janela_imagem_fundo.winfo_exists():
        janela_imagem_fundo.destroy()
        janela_imagem_fundo = None
# --- FIM: fechar_janela_imagem_fundo ---

# =================== FUNÇÕES DE DADOS E INTERFACE ===================
# --- INÍCIO: selecionar_arquivo ---
def selecionar_arquivo(caminho=None):
    global caminho_arquivo_atual, dados_alunos
    caminho_padrao_dados = DEFAULT_CSV_FILE_PATH
    if caminho is None:
        caminho = filedialog.askopenfilename(
            title="Selecione o arquivo CSV de alunos",
            initialdir=CREDENTIALS_DIR,
            filetypes=[("Arquivos CSV", "*.csv"), ("Todos os arquivos", "*.*")]
        )
    if not caminho and not os.path.exists(caminho_padrao_dados):
         messagebox.showinfo("Informação", "Nenhum arquivo selecionado.")
         return
    elif not caminho and os.path.exists(caminho_padrao_dados):
        caminho = caminho_padrao_dados

    if not os.path.exists(caminho):
         messagebox.showerror("Erro", f"Arquivo não encontrado: {caminho}")
         return

    caminho_arquivo_atual = caminho
    dados_alunos = []
    conteudo_bruto = None
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            conteudo_bruto = f.read()
    except UnicodeDecodeError:
        try:
            with open(caminho, 'r', encoding='latin-1') as f:
                conteudo_bruto = f.read()
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível ler o arquivo (encoding latin-1): {e}")
            return
    except Exception as e:
        messagebox.showerror("Erro", f"Não foi possível abrir o arquivo: {e}")
        return

    try:
        reader = csv.reader(io.StringIO(conteudo_bruto))
        primeira_linha = next(reader, None)
        if primeira_linha is None:
             messagebox.showwarning("Aviso", "Arquivo de dados de alunos está vazio.")
             mostrar_todos_alunos()
             return

        todas_linhas = [primeira_linha] + list(reader)

    except Exception as e:
        messagebox.showerror("Erro CSV", f"Falha ao analisar CSV: {e}")
        return

    dados_validos = []
    num_colunas_cabecalho = len(todas_linhas[0]) if todas_linhas else 0

    if num_colunas_cabecalho < 3:
        messagebox.showerror("Erro de Formato", "Arquivo CSV não parece ter o formato esperado (poucas colunas no cabeçalho).")
        return

    for i, linha in enumerate(todas_linhas[1:], start=1):
        if not linha:
             print(f"AVISO: Linha {i+1} em branco ignorada.")
             continue
        linha_proc = linha[:NUM_COLUNAS_ESPERADAS]
        while len(linha_proc) < NUM_COLUNAS_ESPERADAS:
            linha_proc.append("0.00")

        _recalcular_media_geral(linha_proc)
        dados_validos.append(linha_proc)

    if not dados_validos and len(todas_linhas) > 1:
         messagebox.showwarning("Aviso", "Nenhuma linha de dados válida encontrada após o cabeçalho.")
    elif not dados_validos and len(todas_linhas) <= 1:
         messagebox.showwarning("Aviso", "Arquivo CSV contém apenas o cabeçalho ou está vazio.")

    dados_alunos = dados_validos
    mostrar_todos_alunos()
# --- FIM: selecionar_arquivo ---

# --- INÍCIO: lancar_nota ---
def lancar_nota():
    if nivel_acesso_atual not in ["Admin", "Professores"]:
        messagebox.showwarning("Acesso Negado", "Apenas Administradores e Professores podem lançar notas.")
        return
    if not dados_alunos:
        messagebox.showwarning("Aviso", "Nenhum aluno carregado. Por favor, carregue o CSV primeiro.")
        return

    coluna_indice = None
    disciplina_nome_display = None

    if nivel_acesso_atual == "Admin":
        disciplinas_disp = {}
        for internal_name in LISTA_DISCIPLINAS:
            display_name = DISPLAY_NAMES.get(internal_name, internal_name)
            disciplinas_disp[display_name.lower()] = COLUNA_MAP[internal_name]

        display_ling = DISPLAY_NAMES.get("LingEstC", "LingEstC")
        disciplinas_disp[display_ling.lower()[:4]] = COLUNA_MAP.get("LingEstC")

        display_eng = DISPLAY_NAMES.get("EngSoft", "EngSoft")
        disciplinas_disp[display_eng.lower()[:3]] = COLUNA_MAP.get("EngSoft")

        prompt_disciplinas = ", ".join([DISPLAY_NAMES.get(d, d) for d in LISTA_DISCIPLINAS])
        escolha = simpledialog.askstring("Admin: Selecionar Disciplina",
                                         f"Digite a disciplina (ex.: {prompt_disciplinas}):", parent=janela)
        if not escolha: return
        chave = escolha.strip().lower().replace(" ", "").replace(".", "")
        coluna_indice = disciplinas_disp.get(chave, None)

        if coluna_indice is None:
            messagebox.showerror("Erro", "Disciplina não reconhecida.")
            return

        for internal, idx in COLUNA_MAP.items():
            if idx == coluna_indice:
                disciplina_nome_display = DISPLAY_NAMES.get(internal, internal)
                break

    elif nivel_acesso_atual == "Professores":
        disciplina_interna = PROFESSOR_TO_COLNAME.get(usuario_logado, None)
        if disciplina_interna is None:
            messagebox.showerror("Erro", "Seu login de professor não está associado a uma disciplina.")
            return
        coluna_indice = COLUNA_MAP.get(disciplina_interna, None)
        if coluna_indice is None:
             messagebox.showerror("Erro", f"A disciplina '{disciplina_interna}' associada a você não existe mais no sistema.")
             return
        disciplina_nome_display = DISPLAY_NAMES.get(disciplina_interna, disciplina_interna)

    try:
        num = simpledialog.askinteger(
            "Lançar Nota",
            f"PROFESSOR {usuario_logado.upper()} ({disciplina_nome_display.upper()})\n\nDigite o número do aluno (1 a {len(dados_alunos)}):",
            parent=janela, minvalue=1, maxvalue=len(dados_alunos)
        )
        if num is None: return
        indice_aluno = num - 1
    except Exception:
        messagebox.showerror("Erro", "Entrada de aluno inválida.")
        return

    if not (0 <= indice_aluno < len(dados_alunos)):
         messagebox.showerror("Erro", "Número do aluno inválido.")
         return
    aluno_selecionado = dados_alunos[indice_aluno]

    try:
        nova_nota_str = simpledialog.askstring(
            "Lançar Nota",
            f"Digite a nova nota para {aluno_selecionado[0]} em {disciplina_nome_display} (Atual: {aluno_selecionado[coluna_indice]}):",
            parent=janela
        )
        if nova_nota_str is None: return
        nova_nota = float(nova_nota_str.replace(',', '.'))
        if not (0.0 <= nova_nota <= 10.0):
            messagebox.showerror("Erro", "A nota deve ser entre 0.0 e 10.0.")
            return
        aluno_selecionado[coluna_indice] = f"{nova_nota:.2f}"
        _recalcular_media_geral(aluno_selecionado)

        if caminho_arquivo_atual:
            try:
                with open(caminho_arquivo_atual, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    linhas = list(reader)

                if 0 <= indice_aluno < len(dados_alunos) and (indice_aluno + 1) < len(linhas):
                    if linhas[indice_aluno + 1][1] == aluno_selecionado[1] or linhas[indice_aluno + 1][0] == aluno_selecionado[0]:
                         linhas[indice_aluno + 1] = aluno_selecionado
                    else:
                         found = False
                         for idx, linha in enumerate(linhas[1:], start=1):
                             if (len(linha) >= 2 and linha[1] == aluno_selecionado[1]) or (linha[0] == aluno_selecionado[0]):
                                 linhas[idx] = aluno_selecionado
                                 found = True
                                 break
                         if not found:
                              raise ValueError("Aluno não encontrado no arquivo CSV para atualização.")
                else:
                     raise IndexError("Índice do aluno fora dos limites para atualização.")

                with open(caminho_arquivo_atual, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerows(linhas)

            except Exception as e:
                messagebox.showwarning("Aviso", f"Nota lançada no sistema, mas houve erro ao salvar no CSV: {e}")

        mostrar_todos_alunos()
        messagebox.showinfo("Sucesso", f"Nota de {aluno_selecionado[0]} atualizada em {disciplina_nome_display} para {nova_nota:.2f}.")
    except ValueError:
        messagebox.showerror("Erro", "Nota inválida. Digite um número.")
        return
# --- FIM: lancar_nota ---

# --- INÍCIO: mostrar_todos_alunos ---
def mostrar_todos_alunos():
    # Verifica se o widget tree existe antes de usá-lo
    if 'tree' not in globals() or tree is None: return 
    for item in tree.get_children():
        tree.delete(item)

    alunos_a_exibir = dados_alunos
    if nivel_acesso_atual == "Alunos":
        usuario_aluno = usuario_logado
        alunos_a_exibir = []
        for aluno in dados_alunos:
            if aluno and isinstance(aluno[0], str) and aluno[0].split():
                if aluno[0].split()[0].lower() == usuario_aluno:
                    alunos_a_exibir.append(aluno)
                    break
            else:
                print(f"Aviso: Aluno com formato inesperado encontrado: {aluno}")

    # --- MUDANÇA: Determina colunas visíveis ---
    # Começa com todas as colunas
    todas_colunas_internas = ["#", "Nome", "RA", "Email"] + LISTA_DISCIPLINAS + ["Media Geral"]
    # Se "Extra" não tem professor, remove da lista de colunas da tree
    if "Extra" not in PROFESSORES_POR_DISCIPLINA:
        todas_colunas_internas.remove("Extra")
    # --- FIM DA MUDANÇA ---
        
    tree["columns"] = todas_colunas_internas
    tree["show"] = "headings"

    larguras_base = {
        "#": 30, "Nome": 140, "RA": 90, "Email": 160,
        "LingEstC": 90, "Python": 90, "EngSoft": 90, "APS": 90,
        "Extra": 90, "Media Geral": 90
    }

    colunas_notas = set(LISTA_DISCIPLINAS + ["Media Geral"])

    # Loop agora usa a lista filtrada
    for col_interna in todas_colunas_internas:
        display_text = DISPLAY_NAMES.get(col_interna, col_interna)
        tree.heading(col_interna, text=display_text)
        anchor_type = tk.CENTER if col_interna == "#" or col_interna in colunas_notas else tk.W
        tree.column(col_interna, width=larguras_base.get(col_interna, 80), anchor=anchor_type)

    colunas_ocultas_indices = []
    if nivel_acesso_atual == "Professores":
        disciplina_interna = PROFESSOR_TO_COLNAME.get(usuario_logado, "")
        # Usa LISTA_DISCIPLINAS aqui para saber quais colunas de dados existem
        for disc_interna in LISTA_DISCIPLINAS: 
            if disc_interna != disciplina_interna:
                colunas_ocultas_indices.append(COLUNA_MAP.get(disc_interna, None))
        colunas_ocultas_indices.append(COLUNA_MAP["Media Geral"])

    for i, linha in enumerate(alunos_a_exibir):
        dados_para_tree = [i + 1]
        
        # --- MUDANÇA: Filtra os dados da linha para corresponder às colunas visíveis ---
        dados_aluno_filtrados = []
        # Adiciona Nome, RA, Email
        dados_aluno_filtrados.extend(linha[0:3]) 
        # Adiciona notas das disciplinas visíveis
        for disc_interna in LISTA_DISCIPLINAS:
            if disc_interna == "Extra" and "Extra" not in PROFESSORES_POR_DISCIPLINA:
                continue # Pula a coluna "Extra"
            col_idx = COLUNA_MAP.get(disc_interna)
            if col_idx is not None and col_idx < len(linha):
                dados_aluno_filtrados.append(linha[col_idx])
            else:
                dados_aluno_filtrados.append("N/A")
        # Adiciona Média Geral
        media_idx = COLUNA_MAP.get("Media Geral")
        if media_idx is not None and media_idx < len(linha):
             dados_aluno_filtrados.append(linha[media_idx])
        else:
             dados_aluno_filtrados.append("N/A")
             
        dados_para_tree.extend(dados_aluno_filtrados)
        # --- FIM DA MUDANÇA ---

        if nivel_acesso_atual == "Professores":
            dados_finais = list(dados_para_tree)
            # A lógica de ocultar "---" precisa ser re-mapeada para as colunas visíveis
            # Simplificação: A lógica de filtragem de colunas já trata isso para a tree
            # Vamos aplicar o "---" nos dados_aluno_filtrados antes de estender
            
            # --- Lógica de Ocultar Notas do Professor (Reaplicada) ---
            # (Inicia em 4 por causa de: #, Nome, RA, Email)
            idx_tree_atual = 4 
            disciplina_prof = PROFESSOR_TO_COLNAME.get(usuario_logado, "")
            
            for disc_interna in LISTA_DISCIPLINAS:
                # Se "Extra" não está visível, pula
                if disc_interna == "Extra" and "Extra" not in PROFESSORES_POR_DISCIPLINA:
                    continue
                
                if disc_interna != disciplina_prof:
                    if idx_tree_atual < len(dados_para_tree):
                        dados_para_tree[idx_tree_atual] = "---"
                
                idx_tree_atual += 1
            
            # Oculta Média Geral (última coluna)
            if idx_tree_atual < len(dados_para_tree):
                dados_para_tree[idx_tree_atual] = "---"
            # --- FIM DA LÓGICA DE OCULTAR ---
                
            tree.insert("", "end", values=dados_para_tree)
        else:
             tree.insert("", "end", values=dados_para_tree)
# --- FIM: mostrar_todos_alunos ---

# --- INÍCIO: obter_indice_aluno ---
def obter_indice_aluno():
    if not dados_alunos:
        messagebox.showwarning("Aviso", "Nenhum aluno carregado.")
        return None
    if nivel_acesso_atual == "Alunos":
        usuario_aluno = usuario_logado
        for i, aluno in enumerate(dados_alunos):
            if aluno and isinstance(aluno[0], str) and aluno[0].split():
                 if aluno[0].split()[0].lower() == usuario_aluno:
                    return i
            else:
                 print(f"Aviso: Aluno com formato inesperado encontrado ao obter índice: {aluno}")
        messagebox.showerror("Erro", f"Seu login ({usuario_aluno.capitalize()}) não foi encontrado na lista de alunos carregada.")
        return None
    try:
        if not dados_alunos:
             messagebox.showwarning("Aviso", "Nenhum aluno para selecionar.")
             return None
        num = simpledialog.askinteger(
            "Selecionar Aluno",
            f"Digite o número do aluno (1 a {len(dados_alunos)}):",
            parent=janela, minvalue=1, maxvalue=len(dados_alunos)
        )
        if num is None:
            return None
        return num - 1
    except Exception:
        messagebox.showerror("Erro", "Entrada inválida.")
        return None
# --- FIM: obter_indice_aluno ---

# --- INÍCIO: mostrar_notas ---
def mostrar_notas():
    indice = obter_indice_aluno()
    if indice is None:
        return

    if not (0 <= indice < len(dados_alunos)):
        messagebox.showerror("Erro", "Índice de aluno inválido.")
        return

    aluno = dados_alunos[indice]
    if not aluno or not isinstance(aluno[0], str):
         messagebox.showerror("Erro", f"Dados inválidos para o aluno no índice {indice+1}.")
         return
    nome = aluno[0]

    janela_notas = tk.Toplevel(janela)
    janela_notas.title(f"Notas de {nome}")
    janela_notas.geometry("500x300")

    texto = f"Aluno: {nome}\n\n"

    if nivel_acesso_atual == "Professores":
        disciplina_interna = PROFESSOR_TO_COLNAME.get(usuario_logado, None)
        coluna_indice = COLUNA_MAP.get(disciplina_interna, None)
        if disciplina_interna and coluna_indice is not None and coluna_indice < len(aluno):
            display_name = DISPLAY_NAMES.get(disciplina_interna, disciplina_interna)
            texto += f"{display_name}: {aluno[coluna_indice]}\n"
            texto += "\n============================\n"
            texto += "(Professores visualizam apenas a\nnota de sua respectiva disciplina)"
        else:
            texto = "Erro: Professor não associado a uma disciplina ou dados do aluno incompletos."
    else: # Admin ou Aluno veem tudo
        # --- MUDANÇA: Pula "Extra" se não houver professor ---
        for disc_interna in LISTA_DISCIPLINAS:
            if disc_interna == "Extra" and "Extra" not in PROFESSORES_POR_DISCIPLINA:
                continue # Pula a disciplina
            # --- FIM DA MUDANÇA ---
                
            display_name = DISPLAY_NAMES.get(disc_interna, disc_interna)
            col_idx = COLUNA_MAP.get(disc_interna)
            if col_idx is not None and col_idx < len(aluno):
                 texto += f"{display_name}: {aluno[col_idx]}\n"
            else:
                 texto += f"{display_name}: (N/A)\n"

        texto += f"\n============================\n"
        media_display = DISPLAY_NAMES.get("Media Geral", "Media Geral")
        media_idx = COLUNA_MAP.get("Media Geral")
        if media_idx is not None and media_idx < len(aluno):
             texto += f"{media_display.upper()}: {aluno[media_idx]}\n"
        else:
             texto += f"{media_display.upper()}: (N/A)\n"

    tk.Label(janela_notas, text=texto, font=("Arial", 11), justify=tk.LEFT, padx=20, pady=20).pack()
# --- FIM: mostrar_notas ---

# --- INÍCIO: gerar_grafico ---
def gerar_grafico():
    indice = obter_indice_aluno()
    if indice is None:
        return

    if not (0 <= indice < len(dados_alunos)):
        messagebox.showerror("Erro", "Índice de aluno inválido.")
        return

    global canvas_grafico, botao_fechar_grafico
    if canvas_grafico is not None:
        if canvas_grafico.get_tk_widget().winfo_exists():
            canvas_grafico.get_tk_widget().destroy()
        canvas_grafico = None
    if botao_fechar_grafico is not None:
        if botao_fechar_grafico.winfo_exists():
            botao_fechar_grafico.destroy()
        botao_fechar_grafico = None

    aluno = dados_alunos[indice]
    if not aluno or not isinstance(aluno[0], str):
         messagebox.showerror("Erro", f"Dados inválidos para o aluno no índice {indice+1}.")
         return
    nome = aluno[0]

    disciplinas_finais_internas = []
    medias_finais = []
    cores_finais = []

    # Mapa de cores baseado na LISTA_DISCIPLINAS (completa)
    todas_disciplinas_map = {d: i for i, d in enumerate(LISTA_DISCIPLINAS)}
    todas_cores = ['#2196F3', '#FF9800', '#4CAF50', '#9C27B0', '#F44336']
    while len(todas_cores) < len(LISTA_DISCIPLINAS):
        todas_cores.append('#'+''.join(random.choices('0123456789ABCDEF', k=6)))

    if nivel_acesso_atual == "Professores":
        disciplina_interna = PROFESSOR_TO_COLNAME.get(usuario_logado, None)
        coluna_indice = COLUNA_MAP.get(disciplina_interna, None)
        if disciplina_interna and coluna_indice is not None:
            disciplinas_finais_internas.append(disciplina_interna)
            try:
                if coluna_indice < len(aluno):
                    medias_finais.append(float(aluno[coluna_indice]))
                else:
                    medias_finais.append(0.0)
            except Exception:
                medias_finais.append(0.0)
            try:
                # Pega a cor do mapa completo
                idx_cor = todas_disciplinas_map.get(disciplina_interna, 0)
                cores_finais.append(todas_cores[idx_cor])
            except (ValueError, IndexError):
                cores_finais.append(todas_cores[0])
        else:
            messagebox.showerror("Erro", "Professor não associado a uma disciplina.")
            return
    else: # Admin ou Aluno
        # --- MUDANÇA: Constrói as listas apenas com disciplinas visíveis ---
        for disc_interna in LISTA_DISCIPLINAS:
            if disc_interna == "Extra" and "Extra" not in PROFESSORES_POR_DISCIPLINA:
                continue # Pula "Extra" se não tiver professor

            disciplinas_finais_internas.append(disc_interna)
            
            # Pega a nota
            col_idx = COLUNA_MAP.get(disc_interna)
            try:
                if col_idx is not None and col_idx < len(aluno):
                    medias_finais.append(float(aluno[col_idx]))
                else:
                    medias_finais.append(0.0)
            except Exception:
                medias_finais.append(0.0)
            
            # Pega a cor
            cor_idx = todas_disciplinas_map.get(disc_interna, 0)
            cores_finais.append(todas_cores[cor_idx])
        # --- FIM DA MUDANÇA ---

    fig, ax = plt.subplots(figsize=(7,4))
    disciplinas_finais_display = [DISPLAY_NAMES.get(d, d) for d in disciplinas_finais_internas]
    x = range(len(disciplinas_finais_display))
    ax.bar(x, medias_finais, width=0.6, color=cores_finais)
    ax.set_xlabel('Disciplinas')
    ax.set_ylabel('Média Final')
    ax.set_title(f'Médias Disciplinares de {nome}')
    ax.set_ylim(0, 10)
    ax.set_xticks(x)
    ax.set_xticklabels(disciplinas_finais_display)
    for i, media in enumerate(medias_finais):
        ax.text(i, media + 0.1, f'{media:.2f}', ha='center', va='bottom', fontsize=10)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    canvas_grafico = FigureCanvasTkAgg(fig, master=janela)
    canvas_grafico.draw()
    canvas_grafico.get_tk_widget().pack(pady=10, padx=10, fill=tk.BOTH, expand=False)

    def fechar():
        global canvas_grafico, botao_fechar_grafico
        if canvas_grafico is not None:
             if canvas_grafico.get_tk_widget().winfo_exists():
                canvas_grafico.get_tk_widget().destroy()
             canvas_grafico = None
        if botao_fechar_grafico is not None:
             if botao_fechar_grafico.winfo_exists():
                botao_fechar_grafico.destroy()
             botao_fechar_grafico = None

    botao_fechar_grafico = tk.Button(janela, text="Fechar Gráfico", command=fechar, bg="red", fg="white")
    botao_fechar_grafico.pack(pady=5)
# --- FIM: gerar_grafico ---

# --- INÍCIO: mostrar_professores ---
def mostrar_professores():
    janela_professores = tk.Toplevel(janela)
    janela_professores.title("Professores e Disciplinas")
    janela_professores.geometry("400x250")
    texto = "=== Professores por Disciplina ===\n\n"
    for disc_interna in LISTA_DISCIPLINAS:
        display_name = DISPLAY_NAMES.get(disc_interna, disc_interna)
        professor_login = PROFESSORES_POR_DISCIPLINA.get(disc_interna, None)
        if professor_login:
             texto += f"{display_name}: {professor_login.capitalize()}\n"
        else:
             texto += f"{display_name}: (Vago)\n"
    tk.Label(janela_professores, text=texto, font=("Arial", 12), justify=tk.LEFT, padx=20, pady=20).pack()
# --- FIM: mostrar_professores ---

# =================== I.A: análise disciplinar e mensagem personalizada ===================
# --- INÍCIO: analisar_por_ia ---
def analisar_por_ia():
    """Analisa as notas do aluno logado, identifica disciplina mais fraca/forte e mostra mensagem."""
    if nivel_acesso_atual != "Alunos":
        messagebox.showwarning("Acesso Negado", "Apenas alunos podem usar a I.A motivacional.")
        return
    if not dados_alunos:
        messagebox.showwarning("Aviso", "Nenhum aluno carregado. Carregue o CSV primeiro.")
        return

    aluno = None
    for a in dados_alunos:
        if a and isinstance(a[0], str) and a[0].split():
             primeiro_login = a[0].split()[0].lower()
             if primeiro_login == usuario_logado:
                aluno = a
                break
        else:
             print(f"Aviso: Aluno com formato inesperado encontrado na IA: {a}")
    if aluno is None:
        messagebox.showerror("Erro", "Cadastro do aluno não encontrado nos dados carregados.")
        return

    # --- MUDANÇA: Filtra as disciplinas e notas ---
    disciplinas_internas = []
    notas = []
    for disc_interna in LISTA_DISCIPLINAS:
        if disc_interna == "Extra" and "Extra" not in PROFESSORES_POR_DISCIPLINA:
            continue # Pula "Extra" se não tiver professor
        
        disciplinas_internas.append(disc_interna)
        col_idx = COLUNA_MAP.get(disc_interna)
        try:
            if col_idx is not None and col_idx < len(aluno):
                notas.append(float(aluno[col_idx]))
            else:
                notas.append(0.0)
        except Exception:
            notas.append(0.0)
    # --- FIM DA MUDANÇA ---


    if len(notas) != len(disciplinas_internas): # Verificação de segurança
        media_geral = 0.0
    else:
        # Calcula a média geral usando TODAS as notas (incluindo as invisíveis)
        media_geral_completa_notas = []
        for i in range(3, 3 + len(LISTA_DISCIPLINAS)):
             try:
                 if i < len(aluno): media_geral_completa_notas.append(float(aluno[i]))
                 else: media_geral_completa_notas.append(0.0)
             except Exception: media_geral_completa_notas.append(0.0)
        media_geral = sum(media_geral_completa_notas) / len(media_geral_completa_notas) if media_geral_completa_notas else 0.0


    notas_validas = [n for n in notas if n > 0.0] # Usa apenas notas visíveis > 0 para min/max
    if not notas_validas:
        messagebox.showinfo("I.A", "Você ainda não possui notas lançadas para análise.")
        return

    menor_nota = min(notas_validas)
    maior_nota = max(notas_validas)
    try:
        disc_interna_fraca = disciplinas_internas[notas.index(menor_nota)]
        disc_interna_forte = disciplinas_internas[notas.index(maior_nota)]
    except ValueError:
        messagebox.showerror("Erro I.A", "Não foi possível identificar as disciplinas.")
        return

    disc_display_fraca = DISPLAY_NAMES.get(disc_interna_fraca, disc_interna_fraca)
    disc_display_forte = DISPLAY_NAMES.get(disc_interna_forte, disc_interna_forte)

    motivacionais = [
        f"Não desista! Sua disciplina mais fraca é {disc_display_fraca} ({menor_nota:.2f}). "
        "Pequenas ações diárias fazem grande diferença. Tente revisar 30 minutos por dia.",
        f"Foco em {disc_display_fraca}! Identificamos {menor_nota:.2f} — organize sessões curtas de estudo e peça ajuda ao professor.",
        f"Você pode melhorar em {disc_display_fraca}. Experimente exercícios práticos e revisar os tópicos fundamentais.",
    ]
    parabens = [
        f"Parabéns! Você se destacou em {disc_display_forte} com {maior_nota:.2f}. Continue assim!",
        f"Excelente trabalho! Sua maior força é {disc_display_forte} ({maior_nota:.2f}). Mantenha esse ritmo!",
        f"Incrível desempenho em {disc_display_forte}. Isso mostra que seu esforço está dando resultado.",
    ]
    neutras = [
        f"Você está progredindo. Sua menor nota foi em {disc_display_fraca} ({menor_nota:.2f}). Ajustes pontuais vão ajudar.",
        f"Bom trabalho! Continue praticando. {disc_display_fraca} ({menor_nota:.2f}) merece atenção, mas a média geral é {media_geral:.2f}.",
        f"Está quase lá! Revise {disc_display_fraca} e consolide seus conhecimentos — sua média atual é {media_geral:.2f}.",
    ]

    if media_geral <= 5.0:
        titulo = "💡 Sugestões da I.A - Vamos melhorar!"
        texto = random.choice(motivacionais)
    elif media_geral >= 7.0:
        titulo = "🎉 Sugestões da I.A - Excelente!"
        texto = random.choice(parabens)
    else:
        titulo = "📘 Sugestões da I.A - Progresso"
        texto = random.choice(neutras)

    j = tk.Toplevel(janela)
    j.title("Sugestão Inteligente (I.A)")
    j.config(bg=FRAME_BG)
    j.transient(janela)
    j.grab_set()

    largura_ia = 480
    altura_ia = 220

    janela.update_idletasks()
    pos_x_janela = janela.winfo_x()
    pos_y_janela = janela.winfo_y()
    largura_janela = janela.winfo_width()
    altura_janela = janela.winfo_height()

    pos_x = pos_x_janela + (largura_janela // 2) - (largura_ia // 2)
    pos_y = pos_y_janela + (altura_janela // 2) - (altura_ia // 2)

    j.geometry(f'{largura_ia}x{altura_ia}+{pos_x}+{pos_y}')
    j.resizable(False, False)

    tk.Label(j, text=titulo, bg=FRAME_BG, fg="#FFD700", font=("Arial", 13, "bold")).pack(pady=(12,6))
    tk.Message(j, text=texto, bg=FRAME_BG, fg="white", font=("Arial", 11), width=440).pack(padx=10, pady=6)

    def abrir_acao_rapida():
        messagebox.showinfo("Ação Rápida", f"Tente revisar 3 tópicos principais de {disc_display_fraca} essa semana.", parent=j)

    tk.Button(j, text="Ação Rápida", bg=BTN_ROXO_CLARO, fg="white", command=abrir_acao_rapida).pack(side=tk.LEFT, padx=20, pady=12)
    tk.Button(j, text="Fechar", bg=BTN_EXIT_BG, fg="white", command=j.destroy).pack(side=tk.RIGHT, padx=20, pady=12)

    j.focus_force()
    j.winfo_children()[-1].focus_set()
# --- FIM: analisar_por_ia ---

# =================== LOGIN E HABILITAÇÃO DE BOTOES ===================
# --- INÍCIO: verificar_credenciais (CORRIGIDO) ---
def verificar_credenciais(usuario, senha):
    # Carrega dinamicamente credenciais de ALUNOS
    credenciais_dinamicas_alunos = carregar_credenciais_alunos()
    CREDENCIAIS["Alunos"].update({k.lower(): v for k, v in credenciais_dinamicas_alunos.items()})
    
    # --- MUDANÇA: Carrega dinamicamente credenciais de PROFESSORES ---
    credenciais_dinamicas_profs = carregar_credenciais_professores()
    CREDENCIAIS["Professores"].update({k.lower(): v for k, v in credenciais_dinamicas_profs.items()})
    # --- FIM DA MUDANÇA ---
    
    usuario_norm = usuario.strip().lower()

    for admin_user, admin_pass in CREDENCIAIS.get("Admin", {}).items():
        if usuario_norm == admin_user.lower() and senha == admin_pass:
            return "Admin"
    for prof_user, prof_pass in CREDENCIAIS.get("Professores", {}).items():
        if usuario_norm == prof_user.lower() and senha == prof_pass:
            return "Professores"
    for aluno_user, aluno_pass in CREDENCIAIS.get("Alunos", {}).items():
        if usuario_norm == aluno_user.lower() and senha == aluno_pass:
            return "Alunos"
    return None
# --- FIM: verificar_credenciais ---

# --- INÍCIO: habilitar_botoes ---
def habilitar_botoes(nivel):
    # Verifica se os botões já foram criados
    if 'btn_selecionar' not in globals() or btn_selecionar is None:
         return 

    botoes = {
        "csv": btn_selecionar,
        "lancar_notas": btn_lancar_notas,
        "notas": btn_ver_notas,
        "grafico": btn_gerar_grafico,
        "professores": btn_ver_professores,
        "ia": btn_ia,
        "sair": btn_sair
    }

    for btn_widget in botoes.values():
        if btn_widget is not None:
             try:
                 btn_widget.grid_forget()
             except tk.TclError: pass

    botoes_visiveis = []
    if nivel == "Admin":
        botoes_visiveis = ["csv", "lancar_notas", "notas", "grafico", "professores", "sair"]
    elif nivel == "Professores":
        botoes_visiveis = ["lancar_notas", "notas", "grafico", "professores", "sair"]
    elif nivel == "Alunos":
        botoes_visiveis = ["notas", "grafico", "professores", "ia", "sair"]
    else: # nivel is None (tela de login)
        botoes_visiveis = []

    coluna_atual = 0
    for key in botoes_visiveis:
        btn = botoes.get(key)
        if btn is not None:
            try:
                if btn.winfo_exists():
                    btn.config(state=tk.NORMAL)
                    if key == "sair":
                        btn.config(bg=BTN_EXIT_BG, fg=BTN_FG)
                    elif key == "ia":
                        btn.config(bg=BTN_ROXO_CLARO, fg=BTN_FG)
                    else:
                         btn.config(bg=BTN_ROXO_CLARO, fg=BTN_FG)
                    btn.grid(row=0, column=coluna_atual, padx=5)
                    coluna_atual += 1
            except tk.TclError:
                 pass

    for key, btn in botoes.items():
         if btn is not None:
            try:
                 if btn.winfo_exists():
                     if key not in botoes_visiveis:
                          btn.config(state=tk.DISABLED, bg=BTN_ROXO_BASE)
                          if key == "ia": btn.config(bg=BTN_ROXO_BASE)
                          if key == "sair": btn.config(bg=BTN_EXIT_BG)
                     if nivel is None and key == "sair":
                          btn.config(state=tk.DISABLED)
            except tk.TclError:
                 pass
# --- FIM: habilitar_botoes ---

# --- INÍCIO: tentar_login (CORRIGIDO) ---
def tentar_login(user_entry, senha_entry):
    global nivel_acesso_atual, usuario_logado, dados_alunos, login_frame_global

    usuario = user_entry.get().strip().lower()
    senha = senha_entry.get().strip()
    nivel = verificar_credenciais(usuario, senha)

    if nivel:
        nivel_acesso_atual = nivel
        usuario_logado = usuario
        dados_alunos = []

        if login_frame_global:
            login_frame_global.destroy()
            login_frame_global = None
        
        fechar_janela_imagem_fundo()

        # --- MUDANÇA: ORDEM INVERTIDA ---
        # 1. Constrói a interface principal AGORA
        construir_interface_principal() 

        # 2. Aplica a geometria centralizada (tamanho grande)
        if geometria_principal:
            janela.geometry(geometria_principal)
        # --- FIM DA MUDANÇA ---

        # 3. Força o Tkinter a desenhar e traz para frente
        janela.update_idletasks() 
        janela.attributes('-topmost', True)
        janela.attributes('-topmost', False)
        janela.lift()
        janela.focus_force()

        janela.title(f"Sistema Acadêmico - {nivel} Logado: {usuario.capitalize()}")

        # 4. Carrega os dados
        if nivel in ["Professores", "Alunos"]:
            if os.path.exists(DEFAULT_CSV_FILE_PATH):
                selecionar_arquivo(caminho=DEFAULT_CSV_FILE_PATH)
                messagebox.showinfo("Sucesso", f"Login efetuado como {nivel} ({usuario.capitalize()}).\n"
                                              f"Arquivo de alunos padrão '{DEFAULT_CSV_FILE}' carregado automaticamente.")
            else:
                messagebox.showwarning("Aviso", f"Login efetuado como {nivel} ({usuario.capitalize()}).\n"
                                                f"Arquivo de alunos padrão ({DEFAULT_CSV_FILE}) não encontrado. "
                                                "Peça a um Administrador para carregar um arquivo.")
                mostrar_todos_alunos()
        else: # Admin
            messagebox.showinfo("Sucesso", f"Login efetuado como {nivel} ({usuario.capitalize()}).\n"
                                          "Use 'Selecionar Arquivo CSV' para carregar dados.")
            mostrar_todos_alunos()

    else:
        messagebox.showerror("Erro de Login", "Usuário ou senha inválidos.", parent=janela)
# --- FIM: tentar_login ---

# --- INÍCIO: mostrar_janela_login (Modificado para Janela Única) ---
def mostrar_janela_login():
    global login_frame_global # Salva a referência do frame

    # Centraliza a janela (que está no tamanho de login)
    janela.geometry(geometria_login) 

    login_frame = tk.Frame(janela, bg=FRAME_BG)
    login_frame_global = login_frame
    
    # Pack com expand=True centraliza o frame
    login_frame.pack(padx=10, pady=10, expand=True) 
    login_frame.grid_columnconfigure(1, weight=1)

    tk.Label(login_frame, text="Usuário:", bg=FRAME_BG, fg=TEXT_FG).grid(row=0, column=0, padx=5, pady=5, sticky="w")
    user_entry = tk.Entry(login_frame)
    user_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    tk.Label(login_frame, text="Senha:", bg=FRAME_BG, fg=TEXT_FG).grid(row=1, column=0, padx=5, pady=5, sticky="w")
    senha_entry = tk.Entry(login_frame, show="*")
    senha_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

    senha_entry.bind("<Return>", lambda event: tentar_login(user_entry, senha_entry))
    user_entry.bind("<Return>", lambda event: senha_entry.focus_set())

    tk.Button(login_frame, text="Entrar", bg=BTN_ROXO_CLARO, fg="white",
              command=lambda: tentar_login(user_entry, senha_entry)).grid(row=2, column=0, columnspan=2, pady=5, sticky="ew")

    tk.Button(login_frame, text="Cadastrar Aluno", bg=BTN_AMARELO_CADASTRO, fg="white",
              command=lambda: cadastrar_novo_aluno_interface(janela)).grid(row=3, column=0, columnspan=2, pady=5, sticky="ew")

    tk.Button(login_frame, text="Cadastrar Professor", bg=BTN_AMARELO_CADASTRO, fg=BG_DARK,
              command=lambda: iniciar_cadastro_professor(janela)).grid(row=4, column=0, columnspan=2, pady=5, sticky="ew")

    caminho_da_sua_imagem = os.path.join(BASE_PROJECT_DIR, "UNIP.jpg")
    # Atraso para garantir que a janela 'janela' está pronta
    janela.after(100, lambda: mostrar_janela_imagem_flutuante(janela, caminho_da_sua_imagem))

    janela.protocol("WM_DELETE_WINDOW", lambda: [fechar_janela_imagem_fundo(), janela.destroy()])
    user_entry.focus_set()
# --- FIM: mostrar_janela_login ---

# --- INÍCIO: cadastrar_novo_aluno_interface ---
def cadastrar_novo_aluno_interface(parent_window=None):
    if parent_window is None: parent_window = janela
    
    global caminho_arquivo_atual
    caminho_dados_alunos = DEFAULT_CSV_FILE_PATH

    if not os.path.exists(CONFIDENTIAL_DATA_DIR):
        try:
            os.makedirs(CONFIDENTIAL_DATA_DIR, exist_ok=True)
        except Exception as e:
             messagebox.showwarning("Aviso", f"O diretório '{CONFIDENTIAL_DATA_DIR}' não existe e não pôde ser criado: {e}", parent=parent_window)
             return

    nome = simpledialog.askstring("Cadastro Aluno", "Nome Completo do Aluno:", parent=parent_window)
    if not nome:
        return

    base_login = nome.split()[0].lower()
    cred_dyn = carregar_credenciais_alunos()
    existentes = set(list(cred_dyn.keys()) + list(CREDENCIAIS.get("Alunos", {}).keys()))
    login = base_login
    suffix = 1
    while login in existentes:
        login = f"{base_login}{suffix}"
        suffix += 1

    senha = simpledialog.askstring("Cadastro Aluno", f"Crie uma Senha para o login '{login}':", show='*', parent=parent_window)
    if not senha or not senha.strip():
        return

    ra = simpledialog.askstring("Cadastro Aluno", "RA (Registro Acadêmico):", parent=parent_window)
    if not ra:
        return

    email_padrao = login + "@unip.com"
    email = simpledialog.askstring("Cadastro Aluno", f"Email (Padrão: {email_padrao}):", initialvalue=email_padrao, parent=parent_window)
    if not email:
        return

    notas_vazias = ["0.00"] * len(LISTA_DISCIPLINAS)
    media_geral = "0.00"
    nova_linha_dados = [nome, ra, email] + notas_vazias + [media_geral]

    if salvar_dados_no_csv(caminho_dados_alunos, nova_linha_dados):
        if salvar_credenciais_csv(login, senha):
            messagebox.showinfo("Sucesso", f"Aluno '{nome}' cadastrado com sucesso! Use '{login}' para login.", parent=parent_window)
# --- FIM: cadastrar_novo_aluno_interface ---

# --- INÍCIO: iniciar_cadastro_professor ---
def iniciar_cadastro_professor(parent_window=None):
    if parent_window is None: parent_window = janela

    admin_pass_real = CREDENCIAIS.get("Admin", {}).get("admin", "admin123")
    senha_admin = simpledialog.askstring("Autenticação Necessária",
                                         "Para cadastrar um professor, digite a senha de 'admin':",
                                         show='*', parent=parent_window)
    if senha_admin == admin_pass_real:
        cadastrar_novo_professor_interface(parent_window)
    elif senha_admin is not None:
        messagebox.showerror("Acesso Negado", "Senha de Administrador incorreta.", parent=parent_window)
    else:
        pass # Usuário cancelou
# --- FIM: iniciar_cadastro_professor ---

# --- INÍCIO: cadastrar_novo_professor_interface ---
def cadastrar_novo_professor_interface(parent_window=None):
    if parent_window is None: parent_window = janela

    disciplinas_validas_display = [DISPLAY_NAMES.get(d, d) for d in LISTA_DISCIPLINAS]
    disciplinas_texto = ", ".join(disciplinas_validas_display)

    login = simpledialog.askstring("Cadastro Professor (1/3)",
                                   "Digite o LOGIN do novo professor (ex: 'novoprof'):",
                                   parent=parent_window)
    if not login:
        return
    login = login.strip().lower()

    if login in CREDENCIAIS["Professores"] or login in CREDENCIAIS["Admin"] or login in CREDENCIAIS["Alunos"]:
        messagebox.showerror("Erro", f"O login '{login}' já está em uso.", parent=parent_window)
        return

    senha = simpledialog.askstring("Cadastro Professor (2/3)",
                                   f"Crie uma SENHA para o login '{login}':",
                                   show='*', parent=parent_window)
    if not senha or not senha.strip():
        return

    disciplina_display_escolhida = simpledialog.askstring("Cadastro Professor (3/3)",
                                        f"Qual DISCIPLINA '{login}' irá lecionar?\n\n"
                                        f"Opções: {disciplinas_texto}",
                                        parent=parent_window)
    if not disciplina_display_escolhida:
        return

    disciplina_interna = None
    for internal, display in DISPLAY_NAMES.items():
        if disciplina_display_escolhida.strip().lower() == display.lower():
            disciplina_interna = internal
            break

    if disciplina_interna is None or disciplina_interna not in LISTA_DISCIPLINAS:
        messagebox.showerror("Erro", f"Disciplina inválida: '{disciplina_display_escolhida}'.\nUse uma das opções: {disciplinas_texto}", parent=parent_window)
        return

    if disciplina_interna == "Extra":
        nome_atual_extra = DISPLAY_NAMES.get("Extra", "Extra")
        novo_nome_display = simpledialog.askstring("Renomear Disciplina",
                                                   f"Você selecionou a disciplina '{nome_atual_extra}'.\n"
                                                   "Digite um novo nome para ela (ex: 'Cálculo', 'Física'):",
                                                   initialvalue=nome_atual_extra,
                                                   parent=parent_window)

        if novo_nome_display and novo_nome_display.strip():
            novo_nome_display = novo_nome_display.strip()
            DISPLAY_NAMES["Extra"] = novo_nome_display
            salvar_nomes_disciplinas()
            messagebox.showinfo("Disciplina Renomeada",
                                f"A disciplina 'Extra' agora é '{novo_nome_display}'.",
                                parent=parent_window)

            if nivel_acesso_atual:
                mostrar_todos_alunos() # Redesenha a tabela principal se já estiver logado
        else:
            pass

    substituir = False
    prof_antigo = None
    if disciplina_interna in PROFESSORES_POR_DISCIPLINA:
         prof_antigo = PROFESSORES_POR_DISCIPLINA[disciplina_interna]
         if prof_antigo != login:
             display_name_atual = DISPLAY_NAMES.get(disciplina_interna, disciplina_interna)
             resp = messagebox.askyesno("Confirmar Substituição",
                                        f"A disciplina {display_name_atual} já é lecionada por '{prof_antigo}'.\n"
                                        f"Deseja substituir '{prof_antigo}' por '{login}' nesta disciplina?",
                                        icon='warning', parent=parent_window)
             if not resp:
                 messagebox.showinfo("Cancelado", "Cadastro cancelado.", parent=parent_window)
                 return
             substituir = True

    if salvar_credenciais_professor_csv(login, senha):
        if salvar_mapeamento_professor_csv(login, disciplina_interna):
            display_name_final = DISPLAY_NAMES.get(disciplina_interna, disciplina_interna)
            
            # --- MUDANÇA: Atualiza os dicts globais e redesenha a tabela ---
            PROFESSOR_TO_COLNAME[login] = disciplina_interna
            PROFESSORES_POR_DISCIPLINA[disciplina_interna] = login
            if substituir and prof_antigo and prof_antigo in PROFESSOR_TO_COLNAME:
                 del PROFESSOR_TO_COLNAME[prof_antigo]
            
            messagebox.showinfo("Sucesso", f"Professor '{login}' cadastrado com sucesso para {display_name_final}!", parent=parent_window)
            
            # Se a interface principal já existir (Admin logado), redesenha
            if 'tree' in globals() and tree is not None:
                mostrar_todos_alunos()
            # --- FIM DA MUDANÇA ---
        else:
            messagebox.showerror("Erro", "Credencial salva, mas houve erro ao salvar o mapeamento da disciplina.", parent=parent_window)
    else:
        messagebox.showerror("Erro", "Houve erro ao salvar as credenciais do professor.", parent=parent_window)
# --- FIM: cadastrar_novo_professor_interface ---

# =================== FUNÇÃO PARA CONSTRUIR INTERFACE PRINCIPAL ===================
def construir_interface_principal():
    global btn_selecionar, btn_lancar_notas, btn_ver_notas, btn_gerar_grafico
    global btn_ver_professores, btn_ia, btn_sair, tree, scrollbar
    global frame_principal_interativo, frame_botoes, frame_tree

    # Limpa a janela principal (que estava com o login)
    for widget in janela.winfo_children():
        widget.destroy()

    # Define a cor de fundo da janela principal (que pode ter sido perdida)
    janela.config(bg=BG_DARK)

    style = ttk.Style(janela)
    style.theme_use('clam')
    style.configure("Treeview", background=FRAME_BG, foreground=TEXT_FG, fieldbackground=FRAME_BG, rowheight=25)
    style.map('Treeview', background=[('selected', '#555555')])
    style.configure("Treeview.Heading", background=BG_DARK, foreground=TEXT_FG)

    frame_principal_interativo = tk.Frame(janela, bg=BG_DARK)
    frame_principal_interativo.pack(fill=tk.BOTH, expand=True)

    frame_botoes = tk.Frame(frame_principal_interativo, bg=BG_DARK)
    frame_botoes.pack(pady=10)

    btn_selecionar = tk.Button(frame_botoes, text="Selecionar Arquivo CSV", command=selecionar_arquivo, bg=BTN_ROXO_BASE, fg=BTN_FG)
    btn_lancar_notas = tk.Button(frame_botoes, text="Lançar Notas", command=lancar_nota, bg=BTN_ROXO_CLARO, fg=BTN_FG)
    btn_ver_notas = tk.Button(frame_botoes, text="Ver Notas", command=mostrar_notas, bg=BTN_ROXO_CLARO, fg=BTN_FG)
    btn_gerar_grafico = tk.Button(frame_botoes, text="Gerar Gráfico", command=gerar_grafico, bg=BTN_ROXO_CLARO, fg=BTN_FG)
    btn_ver_professores = tk.Button(frame_botoes, text="Ver Professores", command=mostrar_professores, bg=BTN_ROXO_CLARO, fg=BTN_FG)
    btn_ia = tk.Button(frame_botoes, text="I.A", command=analisar_por_ia, bg=BTN_ROXO_BASE, fg="white", font=("Arial", 10, "bold"))
    btn_sair = tk.Button(frame_botoes, text="Sair", command=janela.destroy, bg=BTN_EXIT_BG, fg=BTN_FG, font=("Arial", 10))

    frame_tree = tk.Frame(frame_principal_interativo, bg=BG_DARK)
    frame_tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    tree = ttk.Treeview(frame_tree)
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar = ttk.Scrollbar(frame_tree, orient="vertical", command=tree.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    tree.configure(yscrollcommand=scrollbar.set)

    # Habilita os botões corretos APÓS a interface ser construída
    habilitar_botoes(nivel_acesso_atual)
# --- FIM FUNÇÃO CONSTRUIR INTERFACE ---

# =================== INTERFACE PRINCIPAL ===================
janela = tk.Tk()
janela.title("Sistema Acadêmico - Login Necessário")
janela.config(bg=BG_DARK)

largura_tela = janela.winfo_screenwidth()
altura_tela = janela.winfo_screenheight()

# Geometria Principal
largura_base_cols = 30 + 140 + 90 + 160 + 90 + 40
largura_disciplinas = len(LISTA_DISCIPLINAS) * 90
largura_principal = largura_base_cols + largura_disciplinas
altura_principal = 750
largura_principal = min(largura_principal, largura_tela - 50)
pos_x_principal = (largura_tela // 2) - (largura_principal // 2)
pos_y_principal = (altura_tela // 2) - (altura_principal // 2)
geometria_principal = f'{largura_principal}x{altura_principal}+{pos_x_principal}+{pos_y_principal}'

# Geometria de Login
largura_login = 300
altura_login = 230
pos_x_login = (largura_tela // 2) - (largura_login // 2)
pos_y_login = (altura_tela // 2) - (altura_login // 2)
geometria_login = f'{largura_login}x{altura_login}+{pos_x_login}+{pos_y_login}'

# --- FIM DA INTERFACE PRINCIPAL (PARCIAL) ---

# --- ÚLTIMAS LINHAS (LÓGICA CORRIGIDA) ---
carregar_nomes_disciplinas()
carregar_dados_professores()

# 1. Aplica a geometria de LOGIN primeiro
janela.geometry(geometria_login)
# 2. Constrói a UI de Login
mostrar_janela_login()

# 3. Inicia o loop
janela.mainloop()
# --- FIM ---