from iqoptionapi.stable_api import IQ_Option

# Configurações
EMAIL = "thiagosoteroprado@gmail.com"
SENHA = "thiago.thi"

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

def listar_ativos_regulares_disponiveis(iq):
    """Lista os ativos regulares disponíveis para operação digital."""
    ativos_disponiveis = []
    open_time = iq.get_all_open_time()
    for ativo, dados in open_time["digital"].items():
        if dados["open"]:
            ativos_disponiveis.append(ativo)
    return ativos_disponiveis

def main():
    iq = conectar()
    ativos_disponiveis = listar_ativos_regulares_disponiveis(iq)
    if ativos_disponiveis:
        print("Ativos regulares disponíveis:")
        for ativo in ativos_disponiveis:
            print(f"- {ativo}")
    else:
        print("Nenhum ativo regular está disponível no momento.")

if __name__ == "__main__":
    main()
