from iqoptionapi.stable_api import IQ_Option
import time

# Configurações
EMAIL = "email"
SENHA = "senha"
ATIVO = "EURUSD-op"
VALOR = 1  # Valor da operação
DIRECAO = "call"  # ou "put"
EXPIRACAO = 1  # Tempo de expiração em minutos
MAX_TENTATIVAS = 3  # Máximo de tentativas para reconexão
TIPOS_OPERACAO = ["digital", "binary", "forex"]  # Tipos de operação a testar

def conectar():
    """Função para conectar na IQ Option."""
    iq = IQ_Option(EMAIL, SENHA)
    status, reason = iq.connect()
    if status:
        print("Conectado com sucesso!")
        return iq
    else:
        print(f"Falha na conexão: {reason}")
        exit()

def verificar_conexao(iq):
    """Função para verificar e reconectar caso necessário."""
    if not iq.check_connect():
        print("Conexão perdida. Tentando reconectar...")
        iq.connect()

def verificar_saldo(iq, valor):
    """Verifica se há saldo suficiente para operar."""
    saldo = iq.get_balance()
    print(f"Saldo atual: {saldo}")
    if saldo < valor:
        print("Saldo insuficiente para realizar a operação.")
        exit()

def verificar_ativo_disponivel(iq, ativo):
    """Verifica se o ativo está disponível."""
    open_time = iq.get_all_open_time()
    ativo_otc = f"{ativo}-OTC"
    if open_time["digital"].get(ativo, {}).get("open"):
        print(f"Ativo {ativo} está disponível no mercado digital.")
        return ativo, "digital"
    elif open_time["binary"].get(ativo, {}).get("open"):
        print(f"Ativo {ativo} está disponível no mercado binário.")
        return ativo, "binary"
    elif open_time["forex"].get(ativo, {}).get("open"):
        print(f"Ativo {ativo} está disponível no mercado forex.")
        return ativo, "forex"
    elif open_time["digital"].get(ativo_otc, {}).get("open"):
        print(f"Ativo regular indisponível. Operando no mercado OTC digital: {ativo_otc}.")
        return ativo_otc, "digital"
    elif open_time["binary"].get(ativo_otc, {}).get("open"):
        print(f"Ativo regular indisponível. Operando no mercado OTC binário: {ativo_otc}.")
        return ativo_otc, "binary"
    elif open_time["forex"].get(ativo_otc, {}).get("open"):
        print(f"Ativo regular indisponível. Operando no mercado OTC forex: {ativo_otc}.")
        return ativo_otc, "forex"
    else:
        print(f"Ativo {ativo} e {ativo_otc} estão indisponíveis ou não reconhecidos. Encerrando...")
        exit()

def realizar_operacao(iq, ativo, valor, direcao, expiracao, tipo_operacao):
    """Realiza a operação no tipo especificado."""
    tentativa = 0
    while tentativa < MAX_TENTATIVAS:
        verificar_conexao(iq)  # Garante que está conectado
        
        if tipo_operacao == "digital":
            status, lucro_esperado = iq.buy_digital_spot(ativo, valor, direcao, expiracao)
        elif tipo_operacao == "binary":
            status, lucro_esperado = iq.buy(valor, ativo, direcao, expiracao)
        elif tipo_operacao == "forex":
            # Forex utiliza outra função. Aqui deve ser adaptado conforme necessário.
            print("Operação Forex não implementada neste exemplo.")
            return
        
        if status:
            print(f"Operação {tipo_operacao} realizada com sucesso no ativo {ativo}! Lucro esperado: {lucro_esperado}")
            return
        else:
            tentativa += 1
            print(f"Tentativa {tentativa}/{MAX_TENTATIVAS} falhou para o tipo {tipo_operacao}. Tentando novamente...")
            time.sleep(2)  # Intervalo entre tentativas

    print(f"Todas as tentativas falharam para o ativo {ativo} no tipo {tipo_operacao}. Encerrando...")

def main():
    iq = conectar()  # Conecta à plataforma
    iq.change_balance("PRACTICE")  # Seleciona conta demo
    verificar_conexao(iq)
    verificar_saldo(iq, VALOR)
    ativo, tipo_inicial = verificar_ativo_disponivel(iq, ATIVO)

    for tipo in TIPOS_OPERACAO:
        if tipo == tipo_inicial:
            print(f"Tentando realizar operação no mercado {tipo}.")
            realizar_operacao(iq, ativo, VALOR, DIRECAO, EXPIRACAO, tipo)
            break
        else:
            print(f"Tentando próximo tipo de operação: {tipo}.")

if __name__ == "__main__":
    main()
