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
BASE_PROJECT_DIR = r"C:\Users\mayco\Documents\GitHub\PIMII"
OUTPUT_DIR = os.path.join(BASE_PROJECT_DIR, "output")

# --- NOVO CAMINHO PARA DADOS CONFIDENCIAIS ---
CONFIDENTIAL_DATA_DIR = os.path.join(OUTPUT_DIR, "dados_confidenciais")
# --- FIM DA ALTERAÇÃO ---

# --- CAMINHOS DOS ARQUIVOS ATUALIZADOS ---
ARQUIVO_CREDENCIAIS = os.path.join(CONFIDENTIAL_DATA_DIR, "credenciais_alunos.csv")
ARQUIVO_CREDENCIAIS_PROFESSORES = os.path.join(CONFIDENTIAL_DATA_DIR, "credenciais_professores.csv")
ARQUIVO_MAPEAMENTO_PROFESSORES = os.path.join(CONFIDENTIAL_DATA_DIR, "professores.csv")
ARQUIVO_NOMES_DISCIPLINAS = os.path.join(CONFIDENTIAL_DATA_DIR, "disciplinas_nomes.csv")
# --- FIM DA ATUALIZAÇÃO ---

# Arquivo de alunos permanece no output principal
DEFAULT_CSV_FILE_PATH = os.path.join(OUTPUT_DIR, "alunos.csv")
DEFAULT_CSV_FILE = "alunos.csv" # Nome base usado em cadastrar_novo_aluno
CREDENTIALS_DIR = OUTPUT_DIR # Diretório inicial para FileDialog pode ser output

BG_DARK = '#212121'
FRAME_BG = '#3A3A3A'
TEXT_FG = 'white'
BTN_ROXO_BASE = '#4A148C'
BTN_ROXO_CLARO = '#6A1B9A'
BTN_FG = 'white'
BTN_EXIT_BG = '#8B0000'
BTN_AMARELO_CADASTRO = '#CCAA00'

# =================== GLOBAIS ===================

LISTA_DISCIPLINAS = ["LingEstC", "Python", "EngSoft", "APS", "Extra"] 
DISPLAY_NAMES = {} 

dados_alunos = []
caminho_arquivo_atual = None
nivel_acesso_atual = None
usuario_logado = None
canvas_grafico = None
botao_fechar_grafico = None
janela_imagem_fundo = None

NUM_COLUNAS_ESPERADAS = 3 + len(LISTA_DISCIPLINAS) + 1 
COLUNA_MAP = {}
i = 3 
for disc in LISTA_DISCIPLINAS:
    COLUNA_MAP[disc] = i
    i += 1
COLUNA_MAP["Media Geral"] = i

CREDENCIAIS = {
    "Admin": {"admin": "admin123"},
    "Professores": {
        "pedro": "pedro123",
        "flavio": "flavio123",
        "cordeiro": "cordeiro123",
        "francisco": "francisco123"
    },
    "Alunos": {}
}

PROFESSORES_POR_DISCIPLINA = {
    "LingEstC": "pedro",
    "Python": "flavio",
    "EngSoft": "cordeiro",
    "APS": "francisco"
}

PROFESSOR_TO_COLNAME = {
    "pedro": "LingEstC",
    "flavio": "Python",
    "cordeiro": "EngSoft",
    "francisco": "APS"
}


# =================== UTILIDADES ===================

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

# --- ATUALIZADO (makedirs) ---
def salvar_nomes_disciplinas():
    """Salva o mapa de nomes de exibição (DISPLAY_NAMES) no CSV."""
    os.makedirs(CONFIDENTIAL_DATA_DIR, exist_ok=True) # <<< MUDANÇA AQUI
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

# --- ATUALIZADO (makedirs) ---
def salvar_credenciais_csv(login, senha):
    os.makedirs(CONFIDENTIAL_DATA_DIR, exist_ok=True) # <<< MUDANÇA AQUI
    try:
        adicionar_cabecalho = not os.path.exists(ARQUIVO_CREDENCIAIS) or os.path.getsize(ARQUIVO_CREDENCIAIS) == 0
        with open(ARQUIVO_CREDENCIAIS, "a", newline='', encoding='utf-8') as arq_creds:
            writer = csv.writer(arq_creds)
            if adicionar_cabecalho:
                writer.writerow(["Login", "Senha"])
            writer.writerow([login, senha])
        return True
    except Exception as e:
        messagebox.showwarning("Aviso", f"Houve erro ao salvar as credenciais: {e}")
        return False

# --- ATUALIZADO (makedirs) ---
# Nota: Esta função salva o ALUNOS.CSV, que deixamos no OUTPUT_DIR
def salvar_dados_no_csv(caminho, dados_novos, modo='a'):
    os.makedirs(OUTPUT_DIR, exist_ok=True) # <<< MANTIDO COMO OUTPUT_DIR
    cabecalho = ["Nome","RA","Email"] + LISTA_DISCIPLINAS + ["Media Geral"]
    try:
        adicionar_cabecalho = not os.path.exists(caminho) or os.path.getsize(caminho) == 0
        with open(caminho, mode=modo, newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if adicionar_cabecalho:
                writer.writerow(cabecalho)
            writer.writerow(dados_novos)
        return True
    except Exception as e:
        messagebox.showerror("Erro de Salvamento", f"Não foi possível salvar o arquivo: {e}")
        return False

def _recalcular_media_geral(aluno):
    notas = []
    for i in range(3, 3 + len(LISTA_DISCIPLINAS)):
        try:
            v = str(aluno[i]).strip()
            if v != "":
                notas.append(float(v))
        except Exception:
            pass
    
    media_idx = COLUNA_MAP["Media Geral"]
    if notas:
        media = sum(notas) / len(notas)
        aluno[media_idx] = f"{media:.2f}"
    else:
        aluno[media_idx] = "0.00"

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

# --- ATUALIZADO (makedirs) ---
def salvar_credenciais_professor_csv(login, senha):
    os.makedirs(CONFIDENTIAL_DATA_DIR, exist_ok=True) # <<< MUDANÇA AQUI
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

# --- ATUALIZADO (makedirs) ---
def salvar_mapeamento_professor_csv(login, disciplina_interna):
    os.makedirs(CONFIDENTIAL_DATA_DIR, exist_ok=True) # <<< MUDANÇA AQUI
    try:
        adicionar_cabecalho = not os.path.exists(ARQUIVO_MAPEAMENTO_PROFESSORES) or os.path.getsize(ARQUIVO_MAPEAMENTO_PROFESSORES) == 0
        with open(ARQUIVO_MAPEAMENTO_PROFESSORES, "a", newline='', encoding='utf-8') as arq_map:
            writer = csv.writer(arq_map)
            if adicionar_cabecalho:
                writer.writerow(["Login", "Disciplina"])
            writer.writerow([login, disciplina_interna])
        return True
    except Exception as e:
        messagebox.showwarning("Aviso", f"Houve erro ao salvar o mapeamento do professor: {e}")
        return False

def carregar_dados_professores():
    global CREDENCIAIS, PROFESSOR_TO_COLNAME, PROFESSORES_POR_DISCIPLINA
    
    creds_csv = carregar_credenciais_professores()
    CREDENCIAIS["Professores"].update(creds_csv)
    
    map_csv = carregar_mapeamento_professores()
    PROFESSOR_TO_COLNAME.update(map_csv)
    
    PROFESSORES_POR_DISCIPLINA.clear()
    for login, disciplina in PROFESSOR_TO_COLNAME.items():
        if disciplina in COLUNA_MAP: 
            PROFESSORES_POR_DISCIPLINA[disciplina] = login
        
    print("Dados de professores carregados e mesclados.")


# =================== JANELA FLUTUANTE (IMAGEM) ===================

def mostrar_janela_imagem_flutuante(janela_login_obj, caminho_imagem):
    """Cria e posiciona uma janela de imagem abaixo da janela de login."""
    global janela_imagem_fundo
    
    janela_login_obj.update_idletasks()
    
    pos_x_login = janela_login_obj.winfo_x()
    pos_y_login = janela_login_obj.winfo_y()
    largura_login = janela_login_obj.winfo_width()
    altura_login = janela_login_obj.winfo_height()
    
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

    # Tornando a imagem filha da janela de login, não da principal
    janela_imagem_fundo = tk.Toplevel(janela_login_obj, bg=FRAME_BG) 
    
    janela_imagem_fundo.title("Imagem Flutuante") 
    
    janela_imagem_fundo.attributes('-topmost', True) 
    
    try:
        img_pil = Image.open(caminho_imagem).convert("RGB")
        img_redimensionada = img_pil.resize((largura_img, altura_img), Image.LANCZOS)
        img_tk_local = ImageTk.PhotoImage(img_redimensionada) 
    except Exception as e:
        print(f"ERRO ao carregar imagem flutuante: {e}. Verifique o formato do arquivo.")
        janela_imagem_fundo.destroy()
        return

    frame_conteudo_img = tk.Frame(janela_imagem_fundo, bg=FRAME_BG)
    frame_conteudo_img.pack(fill=tk.BOTH, expand=True)

    label_fundo = tk.Label(frame_conteudo_img, image=img_tk_local, bg=FRAME_BG)
    label_fundo.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    
    btn_fechar_img = tk.Button(janela_imagem_fundo, text="Fechar Imagem", 
                                command=fechar_janela_imagem_fundo, 
                                bg=BTN_EXIT_BG, fg="white", font=("Arial", 10, "bold"))
    btn_fechar_img.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
    
    janela_imagem_fundo.photo_image = img_tk_local 
    
    janela_imagem_fundo.geometry(f'{largura_img}x{altura_img}+{pos_x_login}+{pos_y_login + altura_login + MARGEM_VERTICAL}') 
    janela_imagem_fundo.lift() 
    
    janela_imagem_fundo.protocol("WM_DELETE_WINDOW", fechar_janela_imagem_fundo)


def fechar_janela_imagem_fundo():
    """Fecha a janela flutuante ao fechar o login.""" 
    global janela_imagem_fundo
    if janela_imagem_fundo and janela_imagem_fundo.winfo_exists():
        janela_imagem_fundo.destroy()
        janela_imagem_fundo = None

# =================== FUNÇÕES DE DADOS E INTERFACE ===================

def selecionar_arquivo(caminho=None):
    global caminho_arquivo_atual, dados_alunos
    caminho_padrao_dados = DEFAULT_CSV_FILE_PATH # <<< USA O CAMINHO COMPLETO
    if caminho is None:
        caminho = filedialog.askopenfilename(
            title="Selecione o arquivo CSV de alunos",
            initialdir=OUTPUT_DIR, # <<< Inicia no output principal
            filetypes=[("Arquivos CSV", "*.csv"), ("Todos os arquivos", "*.*")]
        )
    if not caminho and os.path.exists(caminho_padrao_dados):
        caminho = caminho_padrao_dados
    if not caminho:
        return
    caminho_arquivo_atual = caminho
    dados_alunos.clear()
    conteudo_bruto = None
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            conteudo_bruto = f.read()
    except UnicodeDecodeError:
        try:
            with open(caminho, 'r', encoding='latin-1') as f:
                conteudo_bruto = f.read()
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível ler o arquivo: {e}")
            return
    except Exception as e:
        messagebox.showerror("Erro", f"Não foi possível ler o arquivo: {e}")
        return
    try:
        reader = csv.reader(io.StringIO(conteudo_bruto))
        todas_linhas = list(reader)
    except Exception as e:
        messagebox.showerror("Erro CSV", f"Falha ao analisar CSV: {e}")
        return
    if not todas_linhas or len(todas_linhas) == 1:
        messagebox.showwarning("Aviso", "Arquivo de dados de alunos vazio.")
        return
    dados_validos = []
    for i, linha in enumerate(todas_linhas[1:], start=1):
        if len(linha) >= NUM_COLUNAS_ESPERADAS:
            linha_usavel = linha[:NUM_COLUNAS_ESPERADAS]
            while len(linha_usavel) < NUM_COLUNAS_ESPERADAS:
                linha_usavel.append("0.00")
            _recalcular_media_geral(linha_usavel)
            dados_validos.append(linha_usavel)
        else:
            print(f"LINHA INVÁLIDA {i}: {len(linha)} colunas (Esperado >= {NUM_COLUNAS_ESPERADAS}) -> {linha}")
    if not dados_validos:
        messagebox.showerror("Erro", f"Nenhum aluno válido encontrado (não tem >= {NUM_COLUNAS_ESPERADAS} colunas por linha).")
        return
    dados_alunos = dados_validos
    mostrar_todos_alunos()

# Funções lancar_nota, mostrar_todos_alunos, obter_indice_aluno, 
# mostrar_notas, gerar_grafico, mostrar_professores, analisar_por_ia
# JÁ ESTÃO CORRETAS (usando DISPLAY_NAMES onde necessário)
# ... (código dessas funções omitido para brevidade, mantenha o seu) ...
def lancar_nota():
    if nivel_acesso_atual not in ["Admin", "Professores"]:
        messagebox.showwarning("Acesso Negado", "Apenas Administradores e Professores podem lançar notas.")
        return
    if not dados_alunos:
        messagebox.showwarning("Aviso", "Nenhum aluno carregado. Por favor, carregue o CSV primeiro.")
        return

    coluna_indice = None
    disciplina_nome_display = None # Nome de exibição

    if nivel_acesso_atual == "Admin":
        # Mapa de disciplinas (usando Nomes de Exibição)
        disciplinas_disp = {}
        for internal_name in LISTA_DISCIPLINAS:
            display_name = DISPLAY_NAMES.get(internal_name, internal_name)
            disciplinas_disp[display_name.lower()] = COLUNA_MAP[internal_name]
        
        # Adiciona apelidos
        display_ling = DISPLAY_NAMES.get("LingEstC", "LingEstC")
        disciplinas_disp[display_ling.lower()[:4]] = COLUNA_MAP.get("LingEstC") # "ling"
        
        display_eng = DISPLAY_NAMES.get("EngSoft", "EngSoft")
        disciplinas_disp[display_eng.lower()[:3]] = COLUNA_MAP.get("EngSoft") # "eng"

        # Prompt usa Nomes de Exibição
        prompt_disciplinas = ", ".join([DISPLAY_NAMES.get(d, d) for d in LISTA_DISCIPLINAS])
        escolha = simpledialog.askstring("Admin: Selecionar Disciplina",
                                         f"Digite a disciplina (ex.: {prompt_disciplinas}):", parent=janela)
        if not escolha: return
        chave = escolha.strip().lower().replace(" ", "").replace(".", "")
        coluna_indice = disciplinas_disp.get(chave, None)
        
        if coluna_indice is None:
            messagebox.showerror("Erro", "Disciplina não reconhecida.")
            return
        
        # Encontra o nome de exibição pelo índice
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
            f"PROFESSOR {usuario_logado.upper()} ({disciplina_nome_display.upper()})\n\nDigite o número do aluno (1 a {len(dados_alunos)}) para lançar nota:",
            parent=janela, minvalue=1, maxvalue=len(dados_alunos)
        )
        if num is None: return
        indice_aluno = num - 1
    except Exception:
        messagebox.showerror("Erro", "Entrada de aluno inválida.")
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
                with open(caminho_arquivo_atual, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    linhas = list(reader)
                for idx, linha in enumerate(linhas[1:], start=1):
                    if (len(linha) >= 2 and linha[1] == aluno_selecionado[1]) or (linha[0] == aluno_selecionado[0]):
                        linhas[idx] = aluno_selecionado
                        break
                with open(caminho_arquivo_atual, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerows(linhas)
            except Exception as e:
                messagebox.showwarning("Aviso", f"Nota lançada no sistema, mas houve erro ao salvar no CSV: {e}")

        mostrar_todos_alunos() # Redesenha a tabela
        messagebox.showinfo("Sucesso", f"Nota de {aluno_selecionado[0]} atualizada em {disciplina_nome_display} para {nova_nota:.2f}.")
    except ValueError:
        messagebox.showerror("Erro", "Nota inválida. Digite um número.")
        return

def mostrar_todos_alunos():
    for item in tree.get_children():
        tree.delete(item)

    alunos_a_exibir = dados_alunos
    if nivel_acesso_atual == "Alunos":
        usuario_aluno = usuario_logado
        alunos_a_exibir = []
        for aluno in dados_alunos:
            # Garante que aluno[0] existe antes de dividir
            if aluno and isinstance(aluno[0], str) and aluno[0].split():
                if aluno[0].split()[0].lower() == usuario_aluno:
                    alunos_a_exibir.append(aluno)
                    break
            else:
                print(f"Aviso: Aluno com formato inesperado encontrado: {aluno}")


    # Colunas internas
    todas_colunas_internas = ["#", "Nome", "RA", "Email"] + LISTA_DISCIPLINAS + ["Media Geral"]
    tree["columns"] = todas_colunas_internas
    tree["show"] = "headings"

    larguras_base = {
        "#": 30, "Nome": 140, "RA": 90, "Email": 160,
        "LingEstC": 90, "Python": 90, "EngSoft": 90, "APS": 90,
        "Extra": 90, "Media Geral": 90
    }

    colunas_notas = set(LISTA_DISCIPLINAS + ["Media Geral"])

    for col_interna in todas_colunas_internas:
        # Usa o nome de exibição para o cabeçalho
        display_text = DISPLAY_NAMES.get(col_interna, col_interna)
        tree.heading(col_interna, text=display_text)

        anchor_type = tk.CENTER if col_interna == "#" or col_interna in colunas_notas else tk.W
        tree.column(col_interna, width=larguras_base.get(col_interna, 80), anchor=anchor_type)

    colunas_ocultas_indices = []
    if nivel_acesso_atual == "Professores":
        disciplina_interna = PROFESSOR_TO_COLNAME.get(usuario_logado, "")

        for disc_interna in LISTA_DISCIPLINAS:
            if disc_interna != disciplina_interna:
                colunas_ocultas_indices.append(COLUNA_MAP.get(disc_interna, None))

        colunas_ocultas_indices.append(COLUNA_MAP["Media Geral"])

    for i, linha in enumerate(alunos_a_exibir):
        dados_para_tree = [i + 1]
        dados_para_tree.extend(linha)

        if nivel_acesso_atual == "Professores":
            dados_finais = list(dados_para_tree)
            for indice_csv_oculto in colunas_ocultas_indices:
                if indice_csv_oculto is not None and (indice_csv_oculto + 1) < len(dados_finais):
                    dados_finais[indice_csv_oculto + 1] = "---"
            tree.insert("", "end", values=dados_finais)
        else:
            tree.insert("", "end", values=dados_para_tree)


def obter_indice_aluno():
    if not dados_alunos:
        messagebox.showwarning("Aviso", "Nenhum aluno carregado.")
        return None
    if nivel_acesso_atual == "Alunos":
        usuario_aluno = usuario_logado
        for i, aluno in enumerate(dados_alunos):
            # Garante que aluno[0] existe antes de dividir
            if aluno and isinstance(aluno[0], str) and aluno[0].split():
                 if aluno[0].split()[0].lower() == usuario_aluno:
                    return i
            else:
                 print(f"Aviso: Aluno com formato inesperado encontrado ao obter índice: {aluno}")
        messagebox.showerror("Erro", f"Seu login ({usuario_aluno.capitalize()}) não foi encontrado na lista de alunos carregada.")
        return None
    try:
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

def mostrar_notas():
    indice = obter_indice_aluno()
    if indice is None:
        return

    aluno = dados_alunos[indice]
    nome = aluno[0]

    janela_notas = tk.Toplevel(janela)
    janela_notas.title(f"Notas de {nome}")
    janela_notas.geometry("500x300")

    texto = f"Aluno: {nome}\n\n"

    if nivel_acesso_atual == "Professores":
        disciplina_interna = PROFESSOR_TO_COLNAME.get(usuario_logado, None)
        coluna_indice = COLUNA_MAP.get(disciplina_interna, None)

        if disciplina_interna and coluna_indice is not None:
            display_name = DISPLAY_NAMES.get(disciplina_interna, disciplina_interna)
            texto += f"{display_name}: {aluno[coluna_indice]}\n"
            texto += "\n============================\n"
            texto += "(Professores visualizam apenas a\nnota de sua respectiva disciplina)"
        else:
            texto = "Erro: Professor não associado a uma disciplina."

    else: # Admin ou Aluno veem tudo
        for disc_interna in LISTA_DISCIPLINAS:
            display_name = DISPLAY_NAMES.get(disc_interna, disc_interna)
            # Verifica se o índice existe antes de acessá-lo
            col_idx = COLUNA_MAP.get(disc_interna)
            if col_idx is not None and col_idx < len(aluno):
                 texto += f"{display_name}: {aluno[col_idx]}\n"
            else:
                 texto += f"{display_name}: (Erro: dado ausente)\n"


        texto += f"\n============================\n"
        media_display = DISPLAY_NAMES.get("Media Geral", "Media Geral")
        media_idx = COLUNA_MAP.get("Media Geral")
        if media_idx is not None and media_idx < len(aluno):
             texto += f"{media_display.upper()}: {aluno[media_idx]}\n"
        else:
             texto += f"{media_display.upper()}: (Erro: dado ausente)\n"

    tk.Label(janela_notas, text=texto, font=("Arial", 11), justify=tk.LEFT, padx=20, pady=20).pack()


def gerar_grafico():
    indice = obter_indice_aluno()
    if indice is None:
        return

    global canvas_grafico, botao_fechar_grafico
    if canvas_grafico is not None:
        canvas_grafico.get_tk_widget().destroy()
        canvas_grafico = None
    if botao_fechar_grafico is not None:
        botao_fechar_grafico.destroy()
        botao_fechar_grafico = None

    aluno = dados_alunos[indice]
    nome = aluno[0]

    disciplinas_finais_internas = []
    medias_finais = []
    cores_finais = []

    todas_disciplinas_internas = LISTA_DISCIPLINAS
    todas_cores = ['#2196F3', '#FF9800', '#4CAF50', '#9C27B0', '#F44336']
    while len(todas_cores) < len(todas_disciplinas_internas):
        todas_cores.append('#'+''.join(random.choices('0123456789ABCDEF', k=6)))

    if nivel_acesso_atual == "Professores":
        disciplina_interna = PROFESSOR_TO_COLNAME.get(usuario_logado, None)
        coluna_indice = COLUNA_MAP.get(disciplina_interna, None)

        if disciplina_interna and coluna_indice is not None:
            disciplinas_finais_internas.append(disciplina_interna)
            try:
                # Verifica se o índice existe antes de acessá-lo
                if coluna_indice < len(aluno):
                    medias_finais.append(float(aluno[coluna_indice]))
                else:
                    medias_finais.append(0.0)
            except Exception:
                medias_finais.append(0.0)
            try:
                idx_cor = todas_disciplinas_internas.index(disciplina_interna)
                cores_finais.append(todas_cores[idx_cor])
            except ValueError:
                cores_finais.append(todas_cores[0])
        else:
            messagebox.showerror("Erro", "Professor não associado a uma disciplina.")
            return

    else: # Admin ou Aluno
        disciplinas_finais_internas = todas_disciplinas_internas
        cores_finais = todas_cores[:len(disciplinas_finais_internas)]

        for i in range(3, 3 + len(LISTA_DISCIPLINAS)):
            try:
                # Verifica se o índice existe antes de acessá-lo
                if i < len(aluno):
                    medias_finais.append(float(aluno[i]))
                else:
                    medias_finais.append(0.0) # Adiciona 0 se o dado estiver faltando
            except Exception:
                medias_finais.append(0.0)

    fig, ax = plt.subplots(figsize=(7,4))

    # Converte nomes internos para Nomes de Exibição para o gráfico
    disciplinas_finais_display = [DISPLAY_NAMES.get(d, d) for d in disciplinas_finais_internas]

    x = range(len(disciplinas_finais_display))
    ax.bar(x, medias_finais, width=0.6, color=cores_finais)

    ax.set_xlabel('Disciplinas')
    ax.set_ylabel('Média Final')
    ax.set_title(f'Médias Disciplinares de {nome}')
    ax.set_ylim(0, 10)
    ax.set_xticks(x)
    ax.set_xticklabels(disciplinas_finais_display) # Usa os nomes de exibição

    for i, media in enumerate(medias_finais):
        ax.text(i, media + 0.1, f'{media:.2f}', ha='center', va='bottom', fontsize=10)

    ax.grid(axis='y', linestyle='--', alpha=0.7)

    canvas_grafico = FigureCanvasTkAgg(fig, master=janela)
    canvas_grafico.draw()
    canvas_grafico.get_tk_widget().pack(pady=10, padx=10, fill=tk.BOTH, expand=False)

    def fechar():
        global canvas_grafico, botao_fechar_grafico
        if canvas_grafico is not None:
            canvas_grafico.get_tk_widget().destroy()
            canvas_grafico = None
        if botao_fechar_grafico is not None:
            botao_fechar_grafico.destroy()
            botao_fechar_grafico = None

    botao_fechar_grafico = tk.Button(janela, text="Fechar Gráfico", command=fechar, bg="red", fg="white")
    botao_fechar_grafico.pack(pady=5)


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

# =================== I.A: análise disciplinar e mensagem personalizada ===================

# --- FUNÇÃO ATUALIZADA (centralização da janela) ---
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
        # Garante que a[0] existe antes de dividir
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

    disciplinas_internas = LISTA_DISCIPLINAS
    notas = []
    for i in range(3, 3 + len(LISTA_DISCIPLINAS)):
        try:
            # Verifica se o índice existe antes de acessá-lo
            if i < len(aluno):
                notas.append(float(aluno[i]))
            else:
                notas.append(0.0) # Adiciona 0 se o dado estiver faltando
        except Exception:
            notas.append(0.0)

    # Verifica se há notas suficientes para a média
    if len(notas) != len(LISTA_DISCIPLINAS):
        media_geral = 0.0 # Define 0 se não houver todas as notas
    else:
        media_geral = sum(notas) / len(notas) if notas else 0.0

    notas_validas = [n for n in notas if n > 0.0]

    if not notas_validas:
        messagebox.showinfo("I.A", "Você ainda não possui notas lançadas para análise.")
        return

    menor_nota = min(notas_validas)
    maior_nota = max(notas_validas)

    # Encontra o índice da nota original (incluindo as zeras)
    try:
        disc_interna_fraca = disciplinas_internas[notas.index(menor_nota)]
        disc_interna_forte = disciplinas_internas[notas.index(maior_nota)]
    except ValueError:
        messagebox.showerror("Erro I.A", "Não foi possível identificar as disciplinas.")
        return


    # Converte para nomes de exibição
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

    # --- Janela de exibição ATUALIZADA ---
    j = tk.Toplevel(janela)
    j.title("Sugestão Inteligente (I.A)")
    j.config(bg=FRAME_BG)
    j.transient(janela) # Faz a janela IA depender da principal
    j.grab_set() # Torna a janela IA modal

    largura_ia = 480
    altura_ia = 220

    # Calcula posição para centralizar em relação à janela principal
    janela.update_idletasks() # Garante que as dimensões da janela principal estão atualizadas
    pos_x_janela = janela.winfo_x()
    pos_y_janela = janela.winfo_y()
    largura_janela = janela.winfo_width()
    altura_janela = janela.winfo_height()

    pos_x = pos_x_janela + (largura_janela // 2) - (largura_ia // 2)
    pos_y = pos_y_janela + (altura_janela // 2) - (altura_ia // 2)

    j.geometry(f'{largura_ia}x{altura_ia}+{pos_x}+{pos_y}')
    j.resizable(False, False) # Impede redimensionamento
    # --- Fim da atualização da janela ---

    tk.Label(j, text=titulo, bg=FRAME_BG, fg="#FFD700", font=("Arial", 13, "bold")).pack(pady=(12,6))
    tk.Message(j, text=texto, bg=FRAME_BG, fg="white", font=("Arial", 11), width=440).pack(padx=10, pady=6)

    def abrir_acao_rapida():
        # Mostra a mensagem relativa à janela IA
        messagebox.showinfo("Ação Rápida", f"Tente revisar 3 tópicos principais de {disc_display_fraca} essa semana.", parent=j)

    tk.Button(j, text="Ação Rápida", bg=BTN_ROXO_CLARO, fg="white", command=abrir_acao_rapida).pack(side=tk.LEFT, padx=20, pady=12)
    tk.Button(j, text="Fechar", bg=BTN_EXIT_BG, fg="white", command=j.destroy).pack(side=tk.RIGHT, padx=20, pady=12)

    # Define o foco inicial para o botão fechar, por exemplo
    j.focus_force()
    j.winfo_children()[-1].focus_set() # Foca no último widget adicionado (botão fechar)

# =================== LOGIN E HABILITAÇÃO DE BOTOES ===================

def verificar_credenciais(usuario, senha):
    credenciais_dinamicas_alunos = carregar_credenciais_alunos()
    CREDENCIAIS["Alunos"].update({k.lower(): v for k, v in credenciais_dinamicas_alunos.items()})
    
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

def habilitar_botoes(nivel):
    botoes_controle = {
        "csv": btn_selecionar,
        "lancar_notas": btn_lancar_notas,
        "notas": btn_ver_notas,
        "grafico": btn_gerar_grafico,
        "professores": btn_ver_professores,
        "ia": btn_ia
    }
    for btn in botoes_controle.values():
        btn.config(state=tk.DISABLED, bg=BTN_ROXO_BASE)
    botoes_controle["ia"].config(bg=BTN_ROXO_BASE, state=tk.DISABLED)

    if nivel == "Admin":
        for key in ["csv", "lancar_notas", "notas", "grafico", "professores"]:
            botoes_controle[key].config(state=tk.NORMAL, bg=BTN_ROXO_CLARO)
    elif nivel == "Professores":
        for key in ["csv", "lancar_notas", "notas", "grafico", "professores"]:
            botoes_controle[key].config(state=tk.NORMAL, bg=BTN_ROXO_CLARO)
    elif nivel == "Alunos":
        for key in ["csv", "notas", "grafico", "professores", "ia"]:
            botoes_controle[key].config(state=tk.NORMAL, bg=BTN_ROXO_CLARO)
            
    btn_sair.config(bg=BTN_EXIT_BG, state=tk.NORMAL)

def tentar_login(janela_login, user_entry, senha_entry):
    global nivel_acesso_atual, usuario_logado
    usuario = user_entry.get().strip().lower()
    senha = senha_entry.get().strip()
    nivel = verificar_credenciais(usuario, senha)
    if nivel:
        nivel_acesso_atual = nivel
        usuario_logado = usuario
        global dados_alunos
        dados_alunos = []
        for item in tree.get_children():
            tree.delete(item)
        habilitar_botoes(nivel)
        
        janela_login.grab_release() # Libera o foco
        janela_login.destroy()
        
        fechar_janela_imagem_fundo()

        # Força a janela principal a voltar ao topo após o login
        janela.attributes('-topmost', True)
        janela.update_idletasks() # Processa a mudança
        janela.attributes('-topmost', False)

        janela.title(f"Sistema Acadêmico - {nivel} Logado: {usuario.capitalize()}")
        messagebox.showinfo("Sucesso", f"Login efetuado como {nivel} ({usuario.capitalize()}).\nUse 'Selecionar Arquivo CSV' para carregar dados.")
    else:
        # Adiciona 'parent' para o messagebox ficar no topo
        messagebox.showerror("Erro de Login", "Usuário ou senha inválidos.", parent=janela_login)

def mostrar_janela_login():
    janela_login = tk.Toplevel(janela, bg=BG_DARK)
    janela_login.title("Login")
    janela_login.transient(janela)
    
    largura_login = 300
    altura_login = 230 
    
    largura_tela = janela.winfo_screenwidth()
    altura_tela = janela.winfo_screenheight()
    pos_x = (largura_tela // 2) - (largura_login // 2)
    pos_y = (altura_tela // 2) - (altura_login // 2)
    janela_login.geometry(f'{largura_login}x{altura_login}+{pos_x}+{pos_y}')
    
    # Garante que a janela de login fique no topo
    janela_login.attributes('-topmost', True)
    # Torna a janela MODAL, bloqueando a janela principal
    janela_login.grab_set() 
    
    login_frame = tk.Frame(janela_login, bg=FRAME_BG)
    login_frame.pack(padx=10, pady=10)
    login_frame.grid_columnconfigure(1, weight=1)
    
    tk.Label(login_frame, text="Usuário:", bg=FRAME_BG, fg=TEXT_FG).grid(row=0, column=0, padx=5, pady=5, sticky="w")
    user_entry = tk.Entry(login_frame)
    user_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
    
    tk.Label(login_frame, text="Senha:", bg=FRAME_BG, fg=TEXT_FG).grid(row=1, column=0, padx=5, pady=5, sticky="w")
    senha_entry = tk.Entry(login_frame, show="*")
    senha_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
    
    senha_entry.bind("<Return>", lambda event: tentar_login(janela_login, user_entry, senha_entry))
    user_entry.bind("<Return>", lambda event: senha_entry.focus_set())
    
    tk.Button(login_frame, text="Entrar", bg=BTN_ROXO_CLARO, fg="white",
              command=lambda: tentar_login(janela_login, user_entry, senha_entry)).grid(row=2, column=0, columnspan=2, pady=5, sticky="ew")
    
    tk.Button(login_frame, text="Cadastrar Aluno", bg=BTN_AMARELO_CADASTRO, fg="white",
              command=lambda: cadastrar_novo_aluno_interface(janela_login)).grid(row=3, column=0, columnspan=2, pady=5, sticky="ew")

    tk.Button(login_frame, text="Cadastrar Professor", bg=BTN_AMARELO_CADASTRO, fg=BG_DARK,
              command=lambda: iniciar_cadastro_professor(janela_login)).grid(row=4, column=0, columnspan=2, pady=5, sticky="ew")

    
    caminho_da_sua_imagem = os.path.join(BASE_PROJECT_DIR, "UNIP.jpg")
    janela.after(10, lambda: mostrar_janela_imagem_flutuante(janela_login, caminho_da_sua_imagem))
    janela_login.protocol("WM_DELETE_WINDOW", lambda: [fechar_janela_imagem_fundo(), janela.destroy()])
    user_entry.focus_set()

# --- FUNÇÃO ATUALIZADA (sem withdraw/deiconify) ---
def cadastrar_novo_aluno_interface(janela_login=None):
    global caminho_arquivo_atual
    caminho_dados_alunos = DEFAULT_CSV_FILE_PATH # <<< Usa o caminho completo
    if not os.path.exists(OUTPUT_DIR): # Verifica o diretório principal
        messagebox.showwarning("Aviso", f"O diretório '{OUTPUT_DIR}' não existe. Crie-o manualmente antes de cadastrar.")
        return
    
    parent_window = janela_login or janela

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
    
    # Cria a linha de dados (usando Nomes Internos)
    notas_vazias = ["0.00"] * len(LISTA_DISCIPLINAS)
    media_geral = "0.00"
    nova_linha_dados = [nome, ra, email] + notas_vazias + [media_geral]
    
    if salvar_dados_no_csv(caminho_dados_alunos, nova_linha_dados):
        if salvar_credenciais_csv(login, senha):
            messagebox.showinfo("Sucesso", f"Aluno '{nome}' cadastrado com sucesso! Use '{login}' para login.", parent=parent_window)

# --- FUNÇÃO ATUALIZADA (com parent=parent_window no erro) ---
def iniciar_cadastro_professor(janela_login=None):
    admin_pass_real = CREDENCIAIS.get("Admin", {}).get("admin", "admin123") 
    parent_window = janela_login or janela
    senha_admin = simpledialog.askstring("Autenticação Necessária", 
                                         "Para cadastrar um professor, digite a senha de 'admin':", 
                                         show='*', parent=parent_window)
    if senha_admin == admin_pass_real:
        cadastrar_novo_professor_interface(janela_login)
    elif senha_admin is not None:
        messagebox.showerror("Acesso Negado", "Senha de Administrador incorreta.", parent=parent_window)
    else:
        pass # Usuário cancelou

# --- FUNÇÃO ATUALIZADA (sem withdraw/deiconify) ---
def cadastrar_novo_professor_interface(janela_login=None):
    
    # Prompt usa Nomes de Exibição
    disciplinas_validas_display = [DISPLAY_NAMES.get(d, d) for d in LISTA_DISCIPLINAS]
    disciplinas_texto = ", ".join(disciplinas_validas_display)
    
    parent_window = janela_login or janela 

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
    
    # Converte o nome de exibição de volta para o nome interno
    disciplina_interna = None
    for internal, display in DISPLAY_NAMES.items():
        if disciplina_display_escolhida.strip().lower() == display.lower():
            disciplina_interna = internal
            break
        
    if disciplina_interna is None or disciplina_interna not in LISTA_DISCIPLINAS:
        messagebox.showerror("Erro", f"Disciplina inválida: '{disciplina_display_escolhida}'.\nUse uma das opções: {disciplinas_texto}", parent=parent_window)
        return
        
    # --- LÓGICA DE RENOMEAÇÃO (Início) ---
    if disciplina_interna == "Extra":
        nome_atual_extra = DISPLAY_NAMES.get("Extra", "Extra")
        novo_nome_display = simpledialog.askstring("Renomear Disciplina",
                                                   f"Você selecionou a disciplina '{nome_atual_extra}'.\n"
                                                   "Digite um novo nome para ela (ex: 'Cálculo', 'Física'):",
                                                   initialvalue=nome_atual_extra,
                                                   parent=parent_window)
        
        if novo_nome_display and novo_nome_display.strip():
            novo_nome_display = novo_nome_display.strip()
            DISPLAY_NAMES["Extra"] = novo_nome_display # Atualiza o global
            salvar_nomes_disciplinas() # Salva no CSV
            messagebox.showinfo("Disciplina Renomeada", 
                                f"A disciplina 'Extra' agora é '{novo_nome_display}'.", 
                                parent=parent_window)
            
            # Atualiza a interface principal (cabeçalhos da tabela) se já estiver logado (raro aqui)
            if nivel_acesso_atual:
                mostrar_todos_alunos()
        else:
            # Usuário cancelou a renomeação, mas continua o cadastro
            pass 
    # --- LÓGICA DE RENOMEAÇÃO (Fim) ---
        
    if disciplina_interna in PROFESSORES_POR_DISCIPLINA:
        prof_atual = PROFESSORES_POR_DISCIPLINA[disciplina_interna]
        display_name_atual = DISPLAY_NAMES.get(disciplina_interna, disciplina_interna)
        resp = messagebox.askyesno("Confirmar Substituição", 
                                   f"A disciplina {display_name_atual} já é lecionada por '{prof_atual}'.\n"
                                   f"Deseja substituir '{prof_atual}' por '{login}' nesta disciplina?",
                                   icon='warning', parent=parent_window)
        if not resp:
            messagebox.showinfo("Cancelado", "Cadastro cancelado.", parent=parent_window)
            return

    # Salva os dados (usando o NOME INTERNO)
    if salvar_credenciais_professor_csv(login, senha):
        if salvar_mapeamento_professor_csv(login, disciplina_interna):
            display_name_final = DISPLAY_NAMES.get(disciplina_interna, disciplina_interna)
            messagebox.showinfo("Sucesso", f"Professor '{login}' cadastrado com sucesso para {display_name_final}!", parent=parent_window)
            carregar_dados_professores() # Recarrega os mapeamentos
        else:
            messagebox.showerror("Erro", "Credencial salva, mas houve erro ao salvar o mapeamento da disciplina.", parent=parent_window)
    else:
        messagebox.showerror("Erro", "Houve erro ao salvar as credenciais do professor.", parent=parent_window)


# =================== INTERFACE PRINCIPAL ===================

janela = tk.Tk()
janela.title("Sistema Acadêmico - Login Necessário")
janela.config(bg=BG_DARK)

largura_tela = janela.winfo_screenwidth()
altura_tela = janela.winfo_screenheight()

largura_base_cols = 30 + 140 + 90 + 160 + 90 + 40 # #, Nome, RA, Email, Media, Scrollbar
largura_disciplinas = len(LISTA_DISCIPLINAS) * 90
largura_principal = largura_base_cols + largura_disciplinas
altura_principal = 750

largura_principal = min(largura_principal, largura_tela - 50) 

pos_x_principal = (largura_tela // 2) - (largura_principal // 2)
pos_y_principal = (altura_tela // 2) - (altura_principal // 2)

janela.geometry(f'{largura_principal}x{altura_principal}+{pos_x_principal}+{pos_y_principal}')

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
btn_selecionar.grid(row=0, column=0, padx=5)
btn_lancar_notas = tk.Button(frame_botoes, text="Lançar Notas", command=lancar_nota, bg=BTN_ROXO_CLARO, fg=BTN_FG)
btn_lancar_notas.grid(row=0, column=1, padx=5)
btn_ver_notas = tk.Button(frame_botoes, text="Ver Notas", command=mostrar_notas, bg=BTN_ROXO_CLARO, fg=BTN_FG)
btn_ver_notas.grid(row=0, column=2, padx=5)
btn_gerar_grafico = tk.Button(frame_botoes, text="Gerar Gráfico", command=gerar_grafico, bg=BTN_ROXO_CLARO, fg=BTN_FG)
btn_gerar_grafico.grid(row=0, column=3, padx=5)
btn_ver_professores = tk.Button(frame_botoes, text="Ver Professores", command=mostrar_professores, bg=BTN_ROXO_CLARO, fg=BTN_FG)
btn_ver_professores.grid(row=0, column=4, padx=5)

btn_ia = tk.Button(frame_botoes, text="I.A", command=analisar_por_ia, bg=BTN_ROXO_BASE, fg="white", font=("Arial", 10, "bold"))
btn_ia.grid(row=0, column=5, padx=5)

btn_sair = tk.Button(frame_botoes, text="Sair", command=janela.destroy, bg=BTN_EXIT_BG, fg=BTN_FG, font=("Arial", 10))
btn_sair.grid(row=0, column=6, padx=5) 

frame_tree = tk.Frame(frame_principal_interativo, bg=BG_DARK)
frame_tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

tree = ttk.Treeview(frame_tree)
tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar = ttk.Scrollbar(frame_tree, orient="vertical", command=tree.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
tree.configure(yscrollcommand=scrollbar.set)

# --- CARREGAMENTOS INICIAIS ---
carregar_nomes_disciplinas() # DEVE ser chamado primeiro
carregar_dados_professores() 
# --- FIM DOS CARREGAMENTOS ---

habilitar_botoes(None)
janela.after(100, mostrar_janela_login)
janela.mainloop()
