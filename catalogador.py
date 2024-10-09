import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz

# Inicializa o MetaTrader 5
if not mt5.initialize():
    print("Falha ao inicializar o MetaTrader 5")
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
total_gains = 0
total_losses = 0
martingale_level = 0
bet_amount = initial_bet
previous_losses = 0
desired_profit = initial_bet
current_operation = 'C'  # Começa com 'C' (compra)
results = []
loss_times = []  # Lista para armazenar os horários dos prejuízos

i = 0
while i < len(data):
    row = data.iloc[i]
    open_price = row['open']
    close_price = row['close']

    gain = is_gain(current_operation, open_price, close_price)

    if gain:
        # Calcula o lucro
        profit = bet_amount * payout_rate - previous_losses - bet_amount
        total_gains += 1

        # Armazena o resultado
        results.append({
            'time': row['time'],
            'operation': current_operation,
            'open': open_price,
            'close': close_price,
            'bet_amount': bet_amount,
            'profit': profit,
            'martingale_level': martingale_level,
            'total_gains': total_gains,
            'total_losses': total_losses,
            'final_result': 'Gain'
        })

        # Reseta as variáveis para a próxima operação
        martingale_level = 0
        bet_amount = initial_bet
        previous_losses = 0
        desired_profit = initial_bet

        # Alterna o tipo de operação após um gain
        if current_operation == 'C':
            current_operation = 'V'
        else:
            current_operation = 'C'

        i += 1  # Move para o próximo candle

    else:
        # Ocorreu um loss
        previous_losses += bet_amount
        martingale_level += 1

        if martingale_level >= max_martingale:
            # Considera como 1 loss
            profit = -previous_losses
            total_losses += 1

            # Armazena o resultado
            results.append({
                'time': row['time'],
                'operation': current_operation,
                'open': open_price,
                'close': close_price,
                'bet_amount': bet_amount,
                'profit': profit,
                'martingale_level': martingale_level,
                'total_gains': total_gains,
                'total_losses': total_losses,
                'final_result': 'Loss'
            })

            # Registra o horário em que o prejuízo ocorreu
            loss_times.append(row['time'])

            # Reseta as variáveis para a próxima operação
            martingale_level = 0
            bet_amount = initial_bet
            previous_losses = 0
            desired_profit = initial_bet

            # Após um loss, mantém o mesmo tipo de operação
            # Não alterna current_operation

            i += 1  # Move para o próximo candle

        else:
            # Calcula o próximo valor da aposta usando o martingale
            desired_profit = initial_bet
            bet_amount = (previous_losses + desired_profit) / payout_rate

            # Armazena o resultado parcial (opcional)
            results.append({
                'time': row['time'],
                'operation': current_operation,
                'open': open_price,
                'close': close_price,
                'bet_amount': bet_amount,
                'profit': -bet_amount,
                'martingale_level': martingale_level,
                'total_gains': total_gains,
                'total_losses': total_losses,
                'final_result': 'In Martingale'
            })

            i += 1  # Continua para o próximo candle no martingale

# Converte os resultados para DataFrame
results_df = pd.DataFrame(results)

# Exibe os resultados
print(f"Total de Gains: {total_gains}")
print(f"Total de Losses: {total_losses}")

# Exibe os horários dos prejuízos
if loss_times:
    print("\nHorários em que ocorreram prejuízos após o último martingale:")
    for loss_time in loss_times:
        print(loss_time)
else:
    print("\nNão ocorreram prejuízos após o último martingale.")

# Opcionalmente, exibe as operações realizadas
# print(results_df[['time', 'operation', 'bet_amount', 'profit', 'martingale_level', 'final_result']])
