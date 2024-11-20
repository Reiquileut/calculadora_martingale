from iqoptionapi.stable_api import IQ_Option
import time
import tkinter as tk
from tkinter import messagebox
from calculadora_martingale import calcular_martingale  # Importa cálculo do Martingale

# Configurações
EMAIL = "thiagosoteroprado@gmail.com"
SENHA = "thiago.thi"
CICLO_ATIVO = False

# Conexão com IQ Option
def conectar():
    iq = IQ_Option(EMAIL, SENHA)
    status, reason = iq.connect()
    if status:
        iq.change_balance("PRACTICE")  # Usa conta prática
        return iq
    else:
        messagebox.showerror("Erro", f"Falha na conexão: {reason}")
        exit()

iq = conectar()  # Conecta ao iniciar o script

def sincronizar_com_candle():
    """Espera até o início do próximo candle de 1 minuto."""
    tempo_atual = time.time()
    proximo_candle = tempo_atual + (60 - (tempo_atual % 60))
    tempo_restante = proximo_candle - tempo_atual
    time.sleep(tempo_restante)

def executar_ciclo(ativo, payout, direcao, valor_inicial):
    """Executa o ciclo de operações com base na calculadora."""
    global CICLO_ATIVO
    CICLO_ATIVO = True

    try:
        sequencia = calcular_martingale(valor_inicial, payout)
    except ValueError as e:
        log_mensagem(f"Erro no cálculo do Martingale: {e}")
        return

    for index, valor in enumerate(sequencia):
        if not CICLO_ATIVO:
            log_mensagem("Ciclo interrompido manualmente.")
            break
        
        sincronizar_com_candle()  # Sincroniza com o início do próximo candle
        
        status, lucro_esperado = iq.buy(valor, ativo, direcao, 1)  # Ordem de 1 minuto
        if status:
            log_mensagem(f"Ordem {index + 1} executada: {direcao} | Valor: {valor} | Lucro esperado: {lucro_esperado}")
            time.sleep(70)  # Tempo para encerrar a ordem
            resultado, lucro = iq.check_win_digital()
            if lucro > 0:
                log_mensagem(f"Ordem {index + 1} foi lucrativa. Encerrando ciclo.")
                break
            else:
                log_mensagem(f"Ordem {index + 1} teve prejuízo. Continuando o ciclo.")
        else:
            log_mensagem(f"Falha ao executar a ordem {index + 1}. Encerrando ciclo.")
            break

def iniciar_ciclo():
    """Inicia o ciclo com base nos dados da interface."""
    ativo = entry_ativo.get()
    payout = float(entry_payout.get())
    direcao = var_direcao.get()
    valor_inicial = float(entry_valor_inicial.get())

    if not ativo or not payout or not direcao:
        messagebox.showerror("Erro", "Preencha todos os campos antes de iniciar o ciclo.")
        return

    log_mensagem(f"Iniciando ciclo para o ativo {ativo} com payout {payout} e direção {direcao}.")
    executar_ciclo(ativo, payout, direcao, valor_inicial)

def encerrar_ciclo():
    """Encerra o ciclo manualmente."""
    global CICLO_ATIVO
    CICLO_ATIVO = False
    log_mensagem("Solicitação para encerrar o ciclo enviada.")

def log_mensagem(msg):
    """Adiciona mensagens ao log na interface."""
    text_log.insert(tk.END, f"{msg}\n")
    text_log.see(tk.END)

# Interface Gráfica (GUI)
root = tk.Tk()
root.title("Bot de Martingale")

# Campos da GUI
frame_top = tk.Frame(root)
frame_top.pack(pady=10)

tk.Label(frame_top, text="Ativo:").grid(row=0, column=0, padx=5)
entry_ativo = tk.Entry(frame_top)
entry_ativo.grid(row=0, column=1, padx=5)

tk.Label(frame_top, text="Payout:").grid(row=1, column=0, padx=5)
entry_payout = tk.Entry(frame_top)
entry_payout.grid(row=1, column=1, padx=5)

tk.Label(frame_top, text="Valor Inicial:").grid(row=2, column=0, padx=5)
entry_valor_inicial = tk.Entry(frame_top)
entry_valor_inicial.grid(row=2, column=1, padx=5)

tk.Label(frame_top, text="Direção:").grid(row=3, column=0, padx=5)
var_direcao = tk.StringVar(value="call")
tk.Radiobutton(frame_top, text="Compra (call)", variable=var_direcao, value="call").grid(row=3, column=1, sticky="w")
tk.Radiobutton(frame_top, text="Venda (put)", variable=var_direcao, value="put").grid(row=4, column=1, sticky="w")

# Botões
frame_bottom = tk.Frame(root)
frame_bottom.pack(pady=10)

btn_iniciar = tk.Button(frame_bottom, text="Iniciar Ciclo", command=iniciar_ciclo)
btn_iniciar.grid(row=0, column=0, padx=10)

btn_encerrar = tk.Button(frame_bottom, text="Encerrar Ciclo", command=encerrar_ciclo)
btn_encerrar.grid(row=0, column=1, padx=10)

# Log de operações
text_log = tk.Text(root, height=15, width=50, state="normal")
text_log.pack(pady=10)

root.mainloop()
