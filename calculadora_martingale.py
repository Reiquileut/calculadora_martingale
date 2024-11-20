import tkinter as tk
from tkinter import messagebox

def calcular_martingale(valor_inicial, payout_porcentagem, acao='buy'):
    """
    Calcula a sequência de apostas do martingale com base no valor inicial, payout e tipo de ação (compra/venda).
    Retorna uma lista de valores calculados para as apostas.
    """
    if payout_porcentagem <= 0 or payout_porcentagem > 100:
        raise ValueError("Porcentagem de payout deve estar entre 0 e 100.")
    if valor_inicial < 1:
        raise ValueError("O valor inicial deve ser no mínimo R$ 1.")

    payout_rate = payout_porcentagem / 100
    if acao == 'buy':
        actions_sequence = ['C', 'C', 'V', 'C', 'V', 'V', 'C', 'C']
    else:
        actions_sequence = ['V', 'V', 'C', 'V', 'C', 'C', 'V', 'V']

    bets = []
    previous_losses = 0

    for i in range(8):
        if i == 0:
            bet_amount = valor_inicial
        else:
            desired_profit = bets[i-1]
            bet_amount = (previous_losses + desired_profit) / payout_rate
        bets.append(round(bet_amount, 2))
        previous_losses += bets[i]

    return bets, actions_sequence

def calculate_sequence(action):
    """
    Função da GUI que calcula a sequência e exibe os resultados na interface.
    """
    try:
        payout_percentage = float(payout_entry.get())
        initial_bet = float(initial_bet_entry.get())
        bets, actions = calcular_martingale(initial_bet, payout_percentage, action)
    except ValueError as e:
        messagebox.showerror("Erro", str(e))
        return

    # Limpa a área de resultado antes de mostrar os novos valores
    for widget in result_frame.winfo_children():
        widget.destroy()

    # Mostra a sequência de ações e valores
    for idx, (act, bet) in enumerate(zip(actions, bets)):
        frame = tk.Frame(result_frame, relief='raised', borderwidth=1)
        frame.grid(row=0, column=idx, padx=5, pady=5)
        label_action = tk.Label(frame, text=act, font=('Arial', 14))
        label_action.pack()
        label_bet = tk.Label(frame, text=f"R$ {bet}", font=('Arial', 12))
        label_bet.pack()

def reset_fields():
    """Reseta os campos da GUI."""
    payout_entry.delete(0, tk.END)
    initial_bet_entry.delete(0, tk.END)
    for widget in result_frame.winfo_children():
        widget.destroy()

# GUI isolada, executada apenas se o arquivo for o principal
if __name__ == "__main__":
    # Cria a janela principal
    root = tk.Tk()
    root.title("Calculadora de Martingale")

    # Campo para inserir a porcentagem de payout
    payout_label = tk.Label(root, text="Payout (%):")
    payout_label.grid(row=0, column=0, padx=5, pady=5)
    payout_entry = tk.Entry(root)
    payout_entry.grid(row=0, column=1, padx=5, pady=5)

    # Campo para inserir o valor do primeiro aporte
    initial_bet_label = tk.Label(root, text="Valor do Primeiro Aporte (R$):")
    initial_bet_label.grid(row=1, column=0, padx=5, pady=5)
    initial_bet_entry = tk.Entry(root)
    initial_bet_entry.grid(row=1, column=1, padx=5, pady=5)

    # Botões de compra e venda
    buy_button = tk.Button(root, text="Comprar", bg='green', fg='white', width=10, command=lambda: calculate_sequence('buy'))
    buy_button.grid(row=2, column=0, padx=5, pady=5)
    sell_button = tk.Button(root, text="Vender", bg='red', fg='white', width=10, command=lambda: calculate_sequence('sell'))
    sell_button.grid(row=2, column=1, padx=5, pady=5)

    # Botão de resetar
    reset_button = tk.Button(root, text="Resetar", width=10, command=reset_fields)
    reset_button.grid(row=2, column=2, padx=5, pady=5)

    # Frame para mostrar os resultados
    result_frame = tk.Frame(root)
    result_frame.grid(row=3, column=0, columnspan=3, padx=5, pady=10)

    root.mainloop()
