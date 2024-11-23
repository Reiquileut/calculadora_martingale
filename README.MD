# Bot Martingale para IQ Option

Este projeto é um bot automatizado para realizar operações na IQ Option utilizando a estratégia de **Martingale**. Ele conta com uma interface gráfica (GUI) que permite login, seleção de conta e gerenciamento visual do saldo.

## Funcionalidades

- **Login via GUI**: Insira seu e-mail e senha diretamente na interface.
- **Seleção de Conta**: Altere facilmente entre conta **Demo** e **Real**.
- **Estratégia Martingale**: Execute ciclos automáticos de negociação com cálculos otimizados.
- **Sincronização com Candles**: Garante que as operações sejam realizadas no início de cada candle.
- **Logs Detalhados**: Acompanhe o progresso e possíveis erros diretamente na interface.

## Requisitos

Certifique-se de instalar as dependências listadas no arquivo `requirements.txt`. Use o seguinte comando para instalar:

```bash
pip install -r requirements.txt

Estrutura do Projeto

.
├── bot-gui.py                # Interface principal do bot
├── calculadora_martingale.py # Cálculos relacionados à estratégia de Martingale
├── catalogador.py            # Análise de dados históricos de candles
├── get-ativos.py             # Listagem de ativos disponíveis na IQ Option
├── README.md                 # Documentação do projeto
├── requirements.txt          # Dependências do projeto

Como Usar

	1.	Inicie o Bot:
Execute o arquivo bot-gui.py:

python bot-gui.py


	2.	Faça Login:
	•	Insira seu e-mail e senha no campo correspondente.
	•	Clique em Login. O saldo será exibido na interface após a conexão.
	3.	Configure a Operação:
	•	Preencha os campos:
	•	Ativo: Nome do ativo (exemplo: EURUSD).
	•	Payout: Porcentagem de retorno (exemplo: 85).
	•	Valor Inicial: Valor da primeira operação.
	•	Selecione a direção inicial da operação (Compra ou Venda).
	4.	Selecione a Conta:
	•	Escolha entre Demo e Real na interface.
	5.	Inicie o Ciclo:
	•	Clique no botão Iniciar Ciclo para iniciar as operações automatizadas.
	•	Acompanhe os logs para monitorar o progresso.
	6.	Interrompa o Ciclo (se necessário):
	•	Clique em Encerrar Ciclo para parar manualmente as operações.

Funcionalidades da Interface

Campos de Login

	•	E-mail: Insira o e-mail usado para acessar a IQ Option.
	•	Senha: Insira sua senha (campo protegido).

Configuração de Operações

	•	Ativo: Nome do ativo para operar (ex.: EURUSD).
	•	Payout: Retorno esperado em porcentagem.
	•	Valor Inicial: Valor da primeira operação.
	•	Direção: Escolha entre Compra ou Venda.

Gerenciamento de Conta

	•	Tipo de Conta: Alterne entre conta Demo e Real.
	•	Saldo Atual: Mostra o saldo disponível na conta selecionada.

Logs

	•	Exibe mensagens detalhadas sobre o progresso das operações e erros encontrados.

Contribuições

Contribuições são bem-vindas! Para colaborar:
	1.	Faça um fork deste repositório.
	2.	Crie uma branch para sua funcionalidade: git checkout -b minha-funcionalidade.
	3.	Envie seu PR para revisão.

Licença

Este projeto é licenciado sob a MIT License.

Atenção: Use este bot de forma responsável. A negociação na IQ Option envolve risco, e você pode perder todo o capital investido.
