import threading
import tkinter as tk
from tkinter import messagebox
from iqoptionapi.stable_api import IQ_Option
from calculadora_martingale import calcular_martingale
import time

# Configurações
EMAIL = "thiagosoteroprado@gmail.com"
SENHA = "thiago.thi"
CICLO_ATIVO = False

def conectar():
    """Conecta à IQ Option."""
    iq = IQ_Option(EMAIL, SENHA)
    status, reason = iq.connect()
    if status:
        iq.change_balance("PRACTICE")  # Conta prática
        return iq
    else:
        messagebox.showerror("Erro", f"Falha na conexão: {reason}")
        exit()

iq = conectar()

def verificar_ativo(ativo):
    """Verifica se o ativo está disponível para operações."""
    open_time = iq.get_all_open_time()
    if ativo in open_time["digital"] and open_time["digital"][ativo]["open"]:
        return True
    else:
        return False

def sincronizar_com_candle():
    """Sincroniza com o início do próximo candle."""
    tempo_atual = time.time()
    proximo_candle = tempo_atual + (60 - (tempo_atual % 60))
    time.sleep(proximo_candle - tempo_atual)

def executar_ciclo(ativo, payout, direcao, valor_inicial):
    """Executa as operações conforme a sequência calculada."""
    global CICLO_ATIVO
    CICLO_ATIVO = True

    try:
        sequencia, _ = calcular_martingale(valor_inicial, payout, direcao)
    except ValueError as e:
        log_mensagem(f"Erro: {e}")
        return

    log_mensagem(f"Iniciando ciclo para o ativo {ativo} | Direção: {direcao} | Payout: {payout}%")

    for index, valor in enumerate(sequencia):
        if not CICLO_ATIVO:
            log_mensagem("Ciclo interrompido manualmente.")
            break

        sincronizar_com_candle()  # Espera o início do próximo candle
        status, buy_order_id = iq.buy_digital_spot(ativo, valor, direcao, 1)

        if status:
            log_mensagem(f"Ordem {index + 1} executada: {direcao} | Valor: R$ {valor}")
        else:
            log_mensagem(f"Erro ao executar ordem de valor R$ {valor}. Encerrando ciclo.")
            break

        # Não verifica resultado, continua até interrupção manual
        if not CICLO_ATIVO:
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

    log_mensagem(f"Iniciando ciclo para o ativo {ativo} com payout {payout} e direção {direcao}.")
    
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

# Campos da GUI
tk.Label(root, text="Ativo:").grid(row=0, column=0)
entry_ativo = tk.Entry(root)
entry_ativo.grid(row=0, column=1)

tk.Label(root, text="Payout (%):").grid(row=1, column=0)
entry_payout = tk.Entry(root)
entry_payout.grid(row=1, column=1)

tk.Label(root, text="Valor Inicial:").grid(row=2, column=0)
entry_valor_inicial = tk.Entry(root)
entry_valor_inicial.grid(row=2, column=1)

var_direcao = tk.StringVar(value="call")
tk.Radiobutton(root, text="Compra", variable=var_direcao, value="call").grid(row=3, column=0)
tk.Radiobutton(root, text="Venda", variable=var_direcao, value="put").grid(row=3, column=1)

tk.Button(root, text="Iniciar Ciclo", command=iniciar_ciclo).grid(row=4, column=0)
tk.Button(root, text="Encerrar Ciclo", command=encerrar_ciclo).grid(row=4, column=1)

text_log = tk.Text(root, height=10, width=50)
text_log.grid(row=5, column=0, columnspan=2)

root.mainloop()
