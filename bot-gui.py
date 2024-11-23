import threading
import tkinter as tk
from tkinter import messagebox
from iqoptionapi.stable_api import IQ_Option
from calculadora_martingale import calcular_martingale
import time

# Configurações Globais
CICLO_ATIVO = False
TIPO_CONTA = "PRACTICE"  # Conta padrão é demo PRACTICE ou REAL
iq = None  # Variável global para o objeto IQ_Option


def conectar(email, senha):
    """Conecta à IQ Option com as credenciais fornecidas pelo usuário."""
    global iq
    iq = IQ_Option(email, senha)
    status, reason = iq.connect()
    if status:
        iq.change_balance(TIPO_CONTA)  # Define o tipo de conta
        log_mensagem("Conexão bem-sucedida!")
        saldo = obter_saldo_disponivel()
        label_saldo.config(text=f"R$ {saldo:.2f}")
        label_conta.config(text="Demo" if TIPO_CONTA == "PRACTICE" else "Real")
    else:
        messagebox.showerror("Erro de Login", f"Falha na conexão: {reason}")
        iq = None


def alterar_tipo_conta(tipo):
    """Altera o tipo de conta (demo ou real)."""
    global TIPO_CONTA
    if iq is None:
        messagebox.showerror("Erro", "Faça login antes de alterar o tipo de conta.")
        return

    TIPO_CONTA = tipo
    iq.change_balance(TIPO_CONTA)  # Altera o tipo de conta
    saldo = obter_saldo_disponivel()

    # Atualiza os rótulos da interface gráfica
    label_saldo.config(text=f"R$ {saldo:.2f}")
    label_conta.config(text="Demo" if tipo == "PRACTICE" else "Real")

    log_mensagem(f"Conta alterada para: {'Demo' if tipo == 'PRACTICE' else 'Real'} | Saldo: R$ {saldo:.2f}")


def verificar_ativo(ativo):
    """Verifica se o ativo está disponível para operações."""
    if iq is None:
        return False
    open_time = iq.get_all_open_time()
    if ativo in open_time["digital"] and open_time["digital"][ativo]["open"]:
        return True
    else:
        return False


def sincronizar_com_candle():
    """Sincroniza com o início do próximo candle."""
    tempo_atual = time.time()
    proximo_candle = tempo_atual + (60 - (tempo_atual % 60))

    while time.time() < proximo_candle:
        if not CICLO_ATIVO:
            return  # Interrompe imediatamente se o ciclo foi encerrado
        time.sleep(0.1)  # Evita sobrecarregar a CPU


def obter_saldo_disponivel():
    """Obtém o saldo disponível da conta atual."""
    if iq is None:
        return 0.0
    saldo = iq.get_balance()
    log_mensagem(f"Saldo atualizado: R$ {saldo:.2f}")
    return saldo


def executar_ciclo(ativo, payout, direcao_inicial, valor_inicial):
    """Executa as operações conforme a sequência calculada."""
    global CICLO_ATIVO
    CICLO_ATIVO = True

    try:
        sequencia, acoes = calcular_martingale(valor_inicial, payout, direcao_inicial)
    except ValueError as e:
        log_mensagem(f"Erro: {e}")
        return

    log_mensagem(f"Iniciando ciclo para o ativo {ativo} | Direção inicial: {direcao_inicial} | Payout: {payout}%")

    sincronizar_com_candle()
    if not CICLO_ATIVO:
        log_mensagem("Ciclo interrompido antes da primeira ordem.")
        return

    saldo_disponivel = obter_saldo_disponivel()
    if saldo_disponivel < valor_inicial:
        log_mensagem(f"Saldo insuficiente. Saldo disponível: R$ {saldo_disponivel:.2f}")
        return

    direcao_execucao = "call" if direcao_inicial == "call" else "put"
    status, _ = iq.buy_digital_spot(ativo, valor_inicial, direcao_execucao, 1)

    if status:
        log_mensagem(f"Primeira ordem executada: {direcao_execucao} | Valor: R$ {valor_inicial:.2f}")
    else:
        log_mensagem(f"Erro ao executar a primeira ordem de valor R$ {valor_inicial:.2f}. Encerrando ciclo.")
        return

    for index, (acao, valor) in enumerate(zip(acoes, sequencia)):
        if not CICLO_ATIVO:
            log_mensagem("Ciclo interrompido manualmente durante a execução.")
            break

        sincronizar_com_candle()
        if not CICLO_ATIVO:
            break

        saldo_disponivel = obter_saldo_disponivel()
        if saldo_disponivel < valor:
            log_mensagem(f"Saldo insuficiente para a ordem {index + 2}. Saldo disponível: R$ {saldo_disponivel:.2f}")
            break

        direcao_execucao = "call" if acao == "C" else "put"
        status, _ = iq.buy_digital_spot(ativo, valor, direcao_execucao, 1)

        if status:
            log_mensagem(f"Ordem {index + 2} executada: {direcao_execucao} | Valor: R$ {valor:.2f}")
        else:
            log_mensagem(f"Erro ao executar ordem de valor R$ {valor:.2f}. Encerrando ciclo.")
            break

    log_mensagem("Ciclo finalizado.")


def iniciar_ciclo():
    """Inicia o ciclo a partir da GUI."""
    global CICLO_ATIVO
    if CICLO_ATIVO:
        messagebox.showwarning("Aviso", "Já existe um ciclo em execução.")
        return

    ativo = entry_ativo.get()
    try:
        payout = float(entry_payout.get())
        valor_inicial = float(entry_valor_inicial.get())
    except ValueError:
        messagebox.showerror("Erro", "Insira valores válidos para payout e valor inicial.")
        return

    direcao = var_direcao.get()

    if not ativo or not payout or not direcao or valor_inicial <= 0:
        messagebox.showerror("Erro", "Preencha todos os campos corretamente.")
        return

    if not verificar_ativo(ativo):
        log_mensagem(f"Erro: O ativo '{ativo}' não está disponível para operações.")
        return

    log_mensagem(f"Iniciando ciclo para o ativo {ativo} com payout {payout} e direção inicial {direcao}.")

    thread = threading.Thread(target=executar_ciclo, args=(ativo, payout, direcao, valor_inicial))
    thread.daemon = True
    thread.start()


def encerrar_ciclo():
    """Encerra o ciclo manualmente."""
    global CICLO_ATIVO
    CICLO_ATIVO = False
    log_mensagem("Ciclo interrompido manualmente.")


def log_mensagem(msg):
    """Exibe logs na GUI."""
    text_log.insert(tk.END, f"{msg}\n")
    text_log.see(tk.END)


# Interface Gráfica
root = tk.Tk()
root.title("Bot Martingale")

# Campos de Login
tk.Label(root, text="E-mail:").grid(row=0, column=0)
entry_email = tk.Entry(root)
entry_email.grid(row=0, column=1, columnspan=2)

tk.Label(root, text="Senha:").grid(row=1, column=0)
entry_senha = tk.Entry(root, show="*")  # Oculta o texto da senha
entry_senha.grid(row=1, column=1, columnspan=2)

tk.Button(root, text="Login", command=lambda: conectar(entry_email.get(), entry_senha.get())).grid(row=2, column=0, columnspan=3)

# Campos da GUI
tk.Label(root, text="Ativo:").grid(row=3, column=0)
entry_ativo = tk.Entry(root)
entry_ativo.grid(row=3, column=1)

tk.Label(root, text="Payout (%):").grid(row=4, column=0)
entry_payout = tk.Entry(root)
entry_payout.grid(row=4, column=1)

tk.Label(root, text="Valor Inicial:").grid(row=5, column=0)
entry_valor_inicial = tk.Entry(root)
entry_valor_inicial.grid(row=5, column=1)

var_direcao = tk.StringVar(value="call")
tk.Radiobutton(root, text="Compra", variable=var_direcao, value="call").grid(row=6, column=0)
tk.Radiobutton(root, text="Venda", variable=var_direcao, value="put").grid(row=6, column=1)

tk.Button(root, text="Iniciar Ciclo", command=iniciar_ciclo).grid(row=7, column=0)
tk.Button(root, text="Encerrar Ciclo", command=encerrar_ciclo).grid(row=7, column=1)

# Seleção de tipo de conta
tk.Label(root, text="Tipo de Conta:").grid(row=8, column=0)
var_tipo_conta = tk.StringVar(value="PRACTICE")
tk.Radiobutton(root, text="Demo", variable=var_tipo_conta, value="PRACTICE", command=lambda: alterar_tipo_conta("PRACTICE")).grid(row=8, column=1)
tk.Radiobutton(root, text="Real", variable=var_tipo_conta, value="REAL", command=lambda: alterar_tipo_conta("REAL")).grid(row=8, column=2)

# Exibição de saldo e tipo de conta
tk.Label(root, text="Saldo Atual:").grid(row=9, column=0)
label_saldo = tk.Label(root, text="R$ 0.00")
label_saldo.grid(row=9, column=1)

tk.Label(root, text="Conta Atual:").grid(row=10, column=0)
label_conta = tk.Label(root, text="Demo")
label_conta.grid(row=10, column=1)

# Logs na parte inferior
text_log = tk.Text(root, height=10, width=50)
text_log.grid(row=11, column=0, columnspan=3)

root.mainloop()