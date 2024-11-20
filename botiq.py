from iqoptionapi.stable_api import IQ_Option
import schedule
import time

# Autenticação
iq = IQ_Option("thiagosoteroprado@gmail.com", "thiago.thi")
status, reason = iq.connect()
if status:
    print("Conectado com sucesso!")
else:
    print(f"Falha na conexão: {reason}")
    exit()

# Definir função de execução da operação
def executar_operacao():
    ativo = "EURUSD"
    valor = 10
    direcao = "call"  # ou "put"
    expiracao = 1  # em minutos
    status, ordem_id = iq.buy(valor, ativo, direcao, expiracao)
    if status:
        print(f"Operação realizada com sucesso! ID da ordem: {ordem_id}")
    else:
        print("Falha ao realizar a operação.")

# Agendar a operação
schedule.every().day.at("10:00").do(executar_operacao)

# Loop de execução
while True:
    schedule.run_pending()
    time.sleep(1)
