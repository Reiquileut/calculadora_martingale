from iqoptionapi.stable_api import IQ_Option
import time

# Autenticação
iq = IQ_Option("thiagosoteroprado@gmail.com", "thiago.thi")
status, reason = iq.connect()
if status:
    print("Conectado com sucesso!")
else:
    print(f"Falha na conexão: {reason}")
    exit()

# Selecionar a conta demo
iq.change_balance("PRACTICE")

# Verificar saldo
balance = iq.get_balance()
print(f"Saldo atual: {balance}")

if balance < 10:
    print("Saldo insuficiente para realizar a operação.")
    exit()

# Verificar se o ativo está disponível
ativo = "EURUSD"
if iq.check_win(ativo):
    print(f"Ativo {ativo} está disponível.")
else:
    print(f"Ativo {ativo} não está disponível. Tente outro ativo.")
    exit()

# Realizar operação binária
valor = 10
direcao = "call"  # ou "put"
expiracao = 1

status, ordem_id = iq.buy(valor, ativo, direcao, expiracao)
if status:
    print(f"Operação realizada com sucesso! ID da ordem: {ordem_id}")
else:
    print("Falha ao realizar a operação.")
