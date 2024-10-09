import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz
import matplotlib.pyplot as plt

# Inicializa o MetaTrader 5
if not mt5.initialize():
    print("Falha ao inicializar")
    mt5.shutdown()

# Define o ativo e o timeframe
symbol = "EURUSD"
timeframe = mt5.TIMEFRAME_M1

# Define o fuso horário (UTC)
timezone = pytz.timezone("Etc/UTC")

# Data atual em UTC
now = datetime.now(timezone)

# Início do dia (meia-noite UTC)
start_of_day = datetime(now.year, now.month, now.day, tzinfo=timezone)

# Obtém os dados desde o início do dia até agora
rates = mt5.copy_rates_range(symbol, timeframe, start_of_day, now)

# Verifica se os dados foram obtidos
if rates is None or len(rates) == 0:
    print("Falha ao obter dados")
    mt5.shutdown()

# Converte para DataFrame
data = pd.DataFrame(rates)
data['time'] = pd.to_datetime(data['time'], unit='s')

# Fecha a conexão com o MetaTrader 5
mt5.shutdown()

# Sequências de operações
sequence_buy = ['C', 'C', 'V', 'C', 'V', 'V', 'C', 'C']
sequence_sell = ['V', 'V', 'C', 'V', 'C', 'C', 'V', 'V']

# Escolha a sequência que deseja testar
sequence = sequence_buy  # ou sequence_sell

# Parâmetros
payout_percentage = 80  # Porcentagem de payout
payout_rate = payout_percentage / 100
initial_bet = 2  # Valor inicial da aposta
max_martingale = 8  # Número máximo de martingales

# Função para determinar se a operação foi gain ou loss
def is_gain(operation, open_price, close_price):
    if operation == 'C':
        return close_price > open_price
    elif operation == 'V':
        return close_price < open_price
    else:
        return False

# Variáveis de controle
results = []
bet_amount = initial_bet
martingale_level = 0
total_gains = 0
total_losses = 0
sequence_index = 0

for index, row in data.iterrows():
    if martingale_level >= max_martingale:
        # Reseta após atingir o máximo de martingales
        martingale_level = 0
        bet_amount = initial_bet
        sequence_index = 0

    operation = sequence[sequence_index % len(sequence)]
    open_price = row['open']
    close_price = row['close']

    gain = is_gain(operation, open_price, close_price)

    if gain:
        profit = bet_amount * payout_rate
        total_gains += 1
        martingale_level = 0
        bet_amount = initial_bet
        sequence_index = 0  # Reinicia a sequência após gain
    else:
        profit = -bet_amount
        total_losses += 1
        martingale_level += 1
        bet_amount *= 2  # Aplica o martingale
        sequence_index += 1  # Avança na sequência

    results.append({
        'time': row['time'],
        'operation': operation,
        'open': open_price,
        'close': close_price,
        'bet_amount': bet_amount,
        'profit': profit,
        'total_gains': total_gains,
        'total_losses': total_losses
    })

# Converte os resultados para DataFrame
results_df = pd.DataFrame(results)

# Exibir resultados
print(f"Total de Gains: {total_gains}")
print(f"Total de Losses: {total_losses}")
print(f"Lucro Total: R$ {results_df['profit'].sum():.2f}")

# Visualizar lucro acumulado
results_df['cumulative_profit'] = results_df['profit'].cumsum()

plt.figure(figsize=(12,6))
plt.plot(results_df['time'], results_df['cumulative_profit'], marker='o')
plt.title('Lucro Acumulado ao Longo do Dia')
plt.xlabel('Tempo')
plt.ylabel('Lucro Acumulado (R$)')
plt.grid(True)
plt.show()
