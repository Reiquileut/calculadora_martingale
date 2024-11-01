import tkinter as tk
from tkinter import messagebox

def calculate_sequence(action):
    try:
        payout_percentage = float(payout_entry.get())
        initial_bet = float(initial_bet_entry.get())
        if payout_percentage <= 0 or payout_percentage > 100:
            messagebox.showerror("Erro", "Insira uma porcentagem de payout entre 0 e 100.")
            return
        if initial_bet < 2:
            messagebox.showerror("Erro", "O valor mínimo da primeira aposta é R$ 2.")
            return
    except ValueError:
        messagebox.showerror("Erro", "Insira valores numéricos válidos.")
        return

    payout_rate = payout_percentage / 100
    actions = []

    if action == 'buy':
        actions_sequence = ['C', 'C', 'V', 'C', 'V', 'V', 'C', 'C']
    else:
        actions_sequence = ['V', 'V', 'C', 'V', 'C', 'C', 'V', 'V']

    bets = []
    previous_losses = 0

    for i in range(8):
        if i == 0:
            bet_amount = initial_bet
        else:
            desired_profit = bets[i-1]
            bet_amount = (previous_losses + desired_profit) / payout_rate
        bets.append(round(bet_amount, 2))
        previous_losses += bets[i]

    # Limpa a área de resultado antes de mostrar os novos valores
    for widget in result_frame.winfo_children():
        widget.destroy()

    # Mostra a sequência de ações e valores
    for idx, (act, bet) in enumerate(zip(actions_sequence, bets)):
        frame = tk.Frame(result_frame, relief='raised', borderwidth=1)
        frame.grid(row=0, column=idx, padx=5, pady=5)
        label_action = tk.Label(frame, text=act, font=('Arial', 14))
        label_action.pack()
        label_bet = tk.Label(frame, text=f"R$ {bet}", font=('Arial', 12))
        label_bet.pack()

def reset_fields():
    payout_entry.delete(0, tk.END)
    initial_bet_entry.delete(0, tk.END)
    for widget in result_frame.winfo_children():
        widget.destroy()

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
