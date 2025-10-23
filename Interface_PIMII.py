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
ARQUIVO_CREDENCIAIS = os.path.join(OUTPUT_DIR, "credenciais_alunos.csv")
DEFAULT_CSV_FILE = "alunos.csv"
CREDENTIALS_DIR = OUTPUT_DIR

BG_DARK = '#212121'
FRAME_BG = '#3A3A3A'
TEXT_FG = 'white'
BTN_ROXO_BASE = '#4A148C'
BTN_ROXO_CLARO = '#6A1B9A'
BTN_FG = 'white'
BTN_EXIT_BG = '#8B0000'
BTN_AMARELO_CADASTRO = '#CCAA00'

# =================== GLOBAIS ===================
dados_alunos = []                 # lista de listas: cada aluno = [Nome,RA,Email,ling,py,eng,aps,media]
caminho_arquivo_atual = None
nivel_acesso_atual = None
usuario_logado = None             # login em lowercase
canvas_grafico = None
botao_fechar_grafico = None
janela_imagem_fundo = None
NUM_COLUNAS_ESPERADAS = 8         # Nome,RA,Email,LingEstC,Python,EngSoft,APS,Media Geral

# Credenciais iniciais
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

COLUNA_MAP = {
    "LingEstC": 3,
    "Python": 4,
    "EngSoft": 5,
    "APS": 6,
    "Media Geral": 7
}

# =================== UTILIDADES ===================

def carregar_credenciais_alunos():
    """Lê credenciais do arquivo de credenciais (se existir)."""
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

def salvar_credenciais_csv(login, senha):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
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

def salvar_dados_no_csv(caminho, dados_novos, modo='a'):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    cabecalho = ["Nome","RA","Email","LingEstC","Python","EngSoft","APS","Media Geral"]
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
    """Recalcula média geral a partir das 4 disciplinas (índices 3..6)."""
    notas = []
    for i in range(3, 7):
        try:
            v = str(aluno[i]).strip()
            if v != "":
                notas.append(float(v))
        except Exception:
            pass
    if notas:
        media = sum(notas) / len(notas)
        aluno[7] = f"{media:.2f}"
    else:
        aluno[7] = "0.00"

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

    janela_imagem_fundo = tk.Toplevel(janela, bg=FRAME_BG) 
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
    caminho_padrao_dados = os.path.join(CREDENTIALS_DIR, DEFAULT_CSV_FILE)

    if caminho is None:
        caminho = filedialog.askopenfilename(
            title="Selecione o arquivo CSV de alunos",
            initialdir=CREDENTIALS_DIR,
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

def lancar_nota():
    if nivel_acesso_atual not in ["Admin", "Professores"]:
        messagebox.showwarning("Acesso Negado", "Apenas Administradores e Professores podem lançar notas.")
        return
    if not dados_alunos:
        messagebox.showwarning("Aviso", "Nenhum aluno carregado. Por favor, carregue o CSV primeiro.")
        return

    coluna_indice = None
    disciplina_nome = None

    if nivel_acesso_atual == "Admin":
        disciplinas_disp = {
            "lingestc": 3, "lingest": 3, "ling": 3,
            "python": 4,
            "engsoft": 5, "eng": 5, "engenharia": 5,
            "aps": 6
        }
        escolha = simpledialog.askstring("Admin: Selecionar Disciplina",
                                         "Digite a disciplina (ex.: LingEstC, Python, EngSoft, APS):", parent=janela)
        if not escolha: return
        chave = escolha.strip().lower().replace(" ", "").replace(".", "")
        coluna_indice = disciplinas_disp.get(chave, None)
        if coluna_indice is None:
            messagebox.showerror("Erro", "Disciplina não reconhecida.")
            return
        disciplina_nome = escolha.capitalize()
    elif nivel_acesso_atual == "Professores":
        disciplina_nome_coluna = PROFESSOR_TO_COLNAME.get(usuario_logado, None)
        if disciplina_nome_coluna is None:
            messagebox.showerror("Erro", "Seu login de professor não está associado a uma disciplina.")
            return
        coluna_indice = COLUNA_MAP[disciplina_nome_coluna]
        disciplina_nome = disciplina_nome_coluna

    try:
        num = simpledialog.askinteger(
            "Lançar Nota",
            f"PROFESSOR {usuario_logado.upper()} ({disciplina_nome.upper()})\n\nDigite o número do aluno (1 a {len(dados_alunos)}) para lançar nota:",
            parent=janela,
            minvalue=1,
            maxvalue=len(dados_alunos)
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
            f"Digite a nova nota para {aluno_selecionado[0]} em {disciplina_nome} (Atual: {aluno_selecionado[coluna_indice]}):",
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
                    if len(linha) >= 1 and linha[0] == aluno_selecionado[0]:
                        linhas[idx] = aluno_selecionado
                        break

                with open(caminho_arquivo_atual, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerows(linhas)
            except Exception as e:
                messagebox.showwarning("Aviso", f"Nota lançada no sistema, mas houve erro ao salvar no CSV: {e}")

        mostrar_todos_alunos()
        messagebox.showinfo("Sucesso", f"Nota de {aluno_selecionado[0]} atualizada em {disciplina_nome} para {nova_nota:.2f}.")
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
            if aluno[0].split()[0].lower() == usuario_aluno:
                alunos_a_exibir.append(aluno)
                break

    todas_colunas = [
        "#", "Nome", "RA", "Email",
        "LingEstC", "Python", "EngSoft", "APS", "Media Geral"
    ]
    tree["columns"] = todas_colunas
    tree["show"] = "headings"

    larguras_base = {
        "#": 30, "Nome": 140, "RA": 90, "Email": 160,
        "LingEstC": 90, "Python": 90,
        "EngSoft": 90, "APS": 90, "Media Geral": 90
    }

    for col in todas_colunas:
        tree.heading(col, text=col)
        anchor_type = tk.CENTER if col == "#" or col in ["LingEstC","Python","EngSoft","APS","Media Geral"] else tk.W
        tree.column(col, width=larguras_base.get(col, 80), anchor=anchor_type)

    colunas_ocultas_indices = []
    if nivel_acesso_atual == "Professores":
        disciplina_colname = PROFESSOR_TO_COLNAME.get(usuario_logado, "")
        for col in todas_colunas[4:8]:
            if col != disciplina_colname:
                colunas_ocultas_indices.append(COLUNA_MAP.get(col, None))
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
            if aluno[0].split()[0].lower() == usuario_aluno:
                return i
        messagebox.showerror("Erro", f"Seu login ({usuario_aluno.capitalize()}) não foi encontrado na lista de alunos carregada.")
        return None
    try:
        num = simpledialog.askinteger(
            "Selecionar Aluno",
            f"Digite o número do aluno (1 a {len(dados_alunos)}):",
            parent=janela,
            minvalue=1,
            maxvalue=len(dados_alunos)
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
    janela_notas.geometry("500x250")
    texto = f"Aluno: {nome}\n\n"
    texto += f"LingEstC: {aluno[3]}\n"
    texto += f"Python: {aluno[4]}\n"
    texto += f"EngSoft: {aluno[5]}\n"
    texto += f"APS: {aluno[6]}\n"
    texto += f"\n============================\n"
    texto += f"MÉDIA GERAL: {aluno[7]}\n"
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
    medias = []
    for i in range(3,7):
        try:
            medias.append(float(aluno[i]))
        except Exception:
            medias.append(0.0)
    disciplinas = ["LingEstC","Python","EngSoft","APS"]
    fig, ax = plt.subplots(figsize=(6,4))
    x = range(len(disciplinas))
    cores = ['#2196F3', '#FF9800', '#4CAF50', '#9C27B0']
    ax.bar(x, medias, width=0.6, color=cores)
    ax.set_xlabel('Disciplinas')
    ax.set_ylabel('Média Final')
    ax.set_title(f'Médias Disciplinares de {nome}')
    ax.set_ylim(0, 10)
    ax.set_xticks(x)
    ax.set_xticklabels(disciplinas)
    for i, media in enumerate(medias):
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
    janela_professores.geometry("400x200")
    texto = "=== Professores por Disciplina ===\n\n"
    for chave, professor_login in PROFESSORES_POR_DISCIPLINA.items():
        texto += f"{chave}: {professor_login.capitalize()}\n"
    tk.Label(janela_professores, text=texto, font=("Arial", 12), justify=tk.LEFT, padx=20, pady=20).pack()

# =================== I.A: análise disciplinar e mensagem personalizada ===================

def analisar_por_ia():
    """Analisa as notas do aluno logado, identifica disciplina mais fraca/forte e mostra mensagem."""
    if nivel_acesso_atual != "Alunos":
        messagebox.showwarning("Acesso Negado", "Apenas alunos podem usar a I.A motivacional.")
        return

    if not dados_alunos:
        messagebox.showwarning("Aviso", "Nenhum aluno carregado. Carregue o CSV primeiro.")
        return

    # Localiza o aluno pelo login (primeiro nome em lowercase)
    aluno = None
    for a in dados_alunos:
        primeiro_login = a[0].split()[0].lower()
        if primeiro_login == usuario_logado:
            aluno = a
            break

    if aluno is None:
        messagebox.showerror("Erro", "Cadastro do aluno não encontrado nos dados carregados.")
        return

    disciplinas = ["LingEstC","Python","EngSoft","APS"]
    notas = []
    for i in range(3,7):
        try:
            notas.append(float(aluno[i]))
        except Exception:
            notas.append(0.0)

    # Cálculos
    media_geral = sum(notas) / len(notas) if notas else 0.0
    menor_nota = min(notas)
    maior_nota = max(notas)
    disc_mais_fraca = disciplinas[notas.index(menor_nota)]
    disc_mais_forte = disciplinas[notas.index(maior_nota)]

    # Mensagens
    motivacionais = [
        f"Não desista! Sua disciplina mais fraca é {disc_mais_fraca} ({menor_nota:.2f}). "
        "Pequenas ações diárias fazem grande diferença. Tente revisar 30 minutos por dia.",
        f"Foco em {disc_mais_fraca}! Identificamos {menor_nota:.2f} — organize sessões curtas de estudo e peça ajuda ao professor.",
        f"Você pode melhorar em {disc_mais_fraca}. Experimente exercícios práticos e revisar os tópicos fundamentais.",
    ]
    parabens = [
        f"Parabéns! Você se destacou em {disc_mais_forte} com {maior_nota:.2f}. Continue assim!",
        f"Excelente trabalho! Sua maior força é {disc_mais_forte} ({maior_nota:.2f}). Mantenha esse ritmo!",
        f"Incrível desempenho em {disc_mais_forte}. Isso mostra que seu esforço está dando resultado.",
    ]
    neutras = [
        f"Você está progredindo. Sua menor nota foi em {disc_mais_fraca} ({menor_nota:.2f}). Ajustes pontuais vão ajudar.",
        f"Bom trabalho! Continue praticando. {disc_mais_fraca} ({menor_nota:.2f}) merece atenção, mas a média geral é {media_geral:.2f}.",
        f"Está quase lá! Revise {disc_mais_fraca} e consolide seus conhecimentos — sua média atual é {media_geral:.2f}.",
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

    # Janela de exibição
    j = tk.Toplevel(janela)
    j.title("Sugestão Inteligente (I.A)")
    j.geometry("480x220")
    j.config(bg=FRAME_BG)

    tk.Label(j, text=titulo, bg=FRAME_BG, fg="#FFD700", font=("Arial", 13, "bold")).pack(pady=(12,6))
    tk.Message(j, text=texto, bg=FRAME_BG, fg="white", font=("Arial", 11), width=440).pack(padx=10, pady=6)

    # Sugestão extra: link rápido de ação (simples placeholder)
    def abrir_acao_rapida():
        messagebox.showinfo("Ação Rápida", f"Tente revisar 3 tópicos principais de {disc_mais_fraca} essa semana.")

    tk.Button(j, text="Ação Rápida", bg=BTN_ROXO_CLARO, fg="white", command=abrir_acao_rapida).pack(side=tk.LEFT, padx=20, pady=12)
    tk.Button(j, text="Fechar", bg=BTN_EXIT_BG, fg="white", command=j.destroy).pack(side=tk.RIGHT, padx=20, pady=12)

# =================== LOGIN E HABILITAÇÃO DE BOTOES ===================

def verificar_credenciais(usuario, senha):
    credenciais_dinamicas = carregar_credenciais_alunos()
    CREDENCIAIS["Alunos"].update({k.lower(): v for k, v in credenciais_dinamicas.items()})
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
    # Desabilita todos por padrão
    for btn in botoes_controle.values():
        btn.config(state=tk.DISABLED, bg=BTN_ROXO_BASE)
    # Habilita conforme nível
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
        janela_login.destroy()
        fechar_janela_imagem_fundo()
        janela.title(f"Sistema Acadêmico - {nivel} Logado: {usuario.capitalize()}")
        messagebox.showinfo("Sucesso", f"Login efetuado como {nivel} ({usuario.capitalize()}).\nUse 'Selecionar Arquivo CSV' para carregar dados.")
    else:
        messagebox.showerror("Erro de Login", "Usuário ou senha inválidos.")

def mostrar_janela_login():
    janela_login = tk.Toplevel(janela, bg=BG_DARK)
    janela_login.title("Login")
    janela_login.transient(janela)
    largura_login = 300
    altura_login = 190
    largura_tela = janela.winfo_screenwidth()
    altura_tela = janela.winfo_screenheight()
    pos_x = (largura_tela // 2) - (largura_login // 2)
    pos_y = (altura_tela // 2) - (altura_login // 2)
    janela_login.geometry(f'{largura_login}x{altura_login}+{pos_x}+{pos_y}')
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
    tk.Button(login_frame, text="Cadastre-se", bg=BTN_AMARELO_CADASTRO, fg="white",
              command=lambda: cadastrar_novo_aluno_interface(janela_login)).grid(row=3, column=0, columnspan=2, pady=5, sticky="ew")
    caminho_da_sua_imagem = os.path.join(BASE_PROJECT_DIR, "UNIP.jpg")
    # Mostra a imagem flutuante 10ms depois (permite a janela de login renderizar)
    janela.after(10, lambda: mostrar_janela_imagem_flutuante(janela_login, caminho_da_sua_imagem))
    janela_login.protocol("WM_DELETE_WINDOW", lambda: [fechar_janela_imagem_fundo(), janela.destroy()])
    user_entry.focus_set()

def cadastrar_novo_aluno_interface(janela_login=None):
    global caminho_arquivo_atual
    caminho_dados_alunos = os.path.join(OUTPUT_DIR, DEFAULT_CSV_FILE)
    if not os.path.exists(OUTPUT_DIR):
        messagebox.showwarning("Aviso", f"O diretório '{OUTPUT_DIR}' não existe. Crie-o manualmente antes de cadastrar.")
        return
    if janela_login:
        janela_login.withdraw()
    nome = simpledialog.askstring("Cadastro", "Nome Completo do Aluno:", parent=janela)
    if not nome:
        if janela_login: janela_login.deiconify()
        return
    base_login = nome.split()[0].lower()
    cred_dyn = carregar_credenciais_alunos()
    existentes = set(list(cred_dyn.keys()) + list(CREDENCIAIS.get("Alunos", {}).keys()))
    login = base_login
    suffix = 1
    while login in existentes:
        login = f"{base_login}{suffix}"
        suffix += 1
    senha = simpledialog.askstring("Cadastro", f"Crie uma Senha para o login '{login}':", show='*', parent=janela)
    if not senha or not senha.strip():
        if janela_login: janela_login.deiconify()
        return
    ra = simpledialog.askstring("Cadastro", "RA (Registro Acadêmico):", parent=janela)
    if not ra:
        if janela_login: janela_login.deiconify()
        return
    email_padrao = login + "@unip.com"
    email = simpledialog.askstring("Cadastro", f"Email (Padrão: {email_padrao}):", initialvalue=email_padrao, parent=janela)
    if not email:
        if janela_login: janela_login.deiconify()
        return
    media_ling = media_py = media_eng = media_aps = media_geral = "0.00"
    nova_linha_dados = [nome, ra, email, media_ling, media_py, media_eng, media_aps, media_geral]
    if salvar_dados_no_csv(caminho_dados_alunos, nova_linha_dados):
        if salvar_credenciais_csv(login, senha):
            messagebox.showinfo("Sucesso", f"Aluno '{nome}' cadastrado com sucesso! Use '{login}' para login.")
    if janela_login:
        janela_login.deiconify()

# =================== INTERFACE PRINCIPAL ===================

janela = tk.Tk()
janela.title("Sistema Acadêmico - Login Necessário")
janela.config(bg=BG_DARK)
largura_principal = 1050
altura_principal = 750
largura_tela = janela.winfo_screenwidth()
altura_tela = janela.winfo_screenheight()
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

# Botão I.A (será habilitado apenas para Alunos)
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

habilitar_botoes(None)
janela.after(100, mostrar_janela_login)
janela.mainloop()
