import tkinter as tk
from tkinter import messagebox

def calcular_martingale(valor_inicial, payout, direcao_inicial):
    """
    Calcula a sequência de martingale para maximizar lucros considerando o payout.
    Retorna os valores de cada entrada e a sequência de ações (C/V).
    """
    valores = []
    acoes = []

    lucro_desejado = valor_inicial
    sequencia_padrao = ["C", "V", "C", "V", "V", "C", "C"] if direcao_inicial == "C" else ["V", "C", "V", "C", "C", "V", "V"]

    for acao in sequencia_padrao:
        entrada = round(lucro_desejado / (payout / 100), 2)
        valores.append(entrada)
        acoes.append(acao)
        lucro_desejado += entrada  # Atualiza o lucro desejado

    return valores, acoes

def mostrar_resultados(valores, acoes):
    """
    Exibe os resultados na interface gráfica.
    """
    for widget in result_frame.winfo_children():
        widget.destroy()  # Limpa resultados antigos

    for i, (acao, valor) in enumerate(zip(acoes, valores), start=1):
        frame = tk.Frame(result_frame, relief="solid", borderwidth=1)
        frame.pack(side="top", fill="x", pady=2)

        label_ordem = tk.Label(frame, text=f"Ordem {i}: {'Compra' if acao == 'C' else 'Venda'}")
        label_ordem.pack(side="left", padx=5)

        label_valor = tk.Label(frame, text=f"Valor: R$ {valor:.2f}")
        label_valor.pack(side="right", padx=5)

def calcular_sequencia():
    """
    Calcula a sequência de martingale com base nos dados inseridos na GUI.
    """
    try:
        valor_inicial = float(entry_valor_inicial.get())
        payout = float(entry_payout.get())
        direcao = var_direcao.get()

        valores, acoes = calcular_martingale(valor_inicial, payout, direcao)
        mostrar_resultados(valores, acoes)
    except ValueError:
        messagebox.showerror("Erro", "Por favor, insira valores válidos para o aporte inicial e payout.")

def resetar_campos():
    """
    Reseta os campos de entrada e limpa os resultados.
    """
    entry_valor_inicial.delete(0, tk.END)
    entry_payout.delete(0, tk.END)
    var_direcao.set("C")

    for widget in result_frame.winfo_children():
        widget.destroy()

if __name__ == "__main__":
    # Criação da janela principal
    root = tk.Tk()
    root.title("Calculadora de Martingale")

    # Frame de entrada
    frame_inputs = tk.Frame(root)
    frame_inputs.pack(pady=10)

    # Entrada do valor inicial
    tk.Label(frame_inputs, text="Valor Inicial (R$):").grid(row=0, column=0, padx=5, pady=5)
    entry_valor_inicial = tk.Entry(frame_inputs)
    entry_valor_inicial.grid(row=0, column=1, padx=5, pady=5)

    # Entrada do payout
    tk.Label(frame_inputs, text="Payout (%):").grid(row=1, column=0, padx=5, pady=5)
    entry_payout = tk.Entry(frame_inputs)
    entry_payout.grid(row=1, column=1, padx=5, pady=5)

    # Seleção de direção (compra ou venda)
    tk.Label(frame_inputs, text="Direção:").grid(row=2, column=0, padx=5, pady=5)
    var_direcao = tk.StringVar(value="C")
    tk.Radiobutton(frame_inputs, text="Compra", variable=var_direcao, value="C").grid(row=2, column=1, sticky="w")
    tk.Radiobutton(frame_inputs, text="Venda", variable=var_direcao, value="V").grid(row=3, column=1, sticky="w")

    # Botões de calcular e resetar
    frame_buttons = tk.Frame(root)
    frame_buttons.pack(pady=10)

    btn_calcular = tk.Button(frame_buttons, text="Calcular", command=calcular_sequencia)
    btn_calcular.pack(side="left", padx=10)

    btn_resetar = tk.Button(frame_buttons, text="Resetar", command=resetar_campos)
    btn_resetar.pack(side="right", padx=10)

    # Frame para mostrar resultados
    result_frame = tk.Frame(root)
    result_frame.pack(pady=10, fill="x")

    root.mainloop()
