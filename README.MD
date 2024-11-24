# Bot Martingale para IQ Option

[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Este projeto é um bot automatizado para realizar operações na **IQ Option** utilizando a estratégia de **Martingale**. Ele possui uma interface gráfica (GUI) que permite login, seleção de conta e gerenciamento visual do saldo.

## Sumário

- [Funcionalidades](#funcionalidades)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Como Usar](#como-usar)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Funcionalidades da Interface](#funcionalidades-da-interface)
- [Contribuições](#contribuições)
- [Licença](#licença)
- [Suporte](#suporte)
- [Aviso Legal](#aviso-legal)
- [Créditos](#créditos)

## Funcionalidades

- **Login via GUI**: Insira seu e-mail e senha diretamente na interface.
- **Seleção de Conta**: Altere facilmente entre conta **Demo** e **Real**.
- **Estratégia Martingale**: Execute ciclos automáticos de negociação com cálculos otimizados.
- **Sincronização com Candles**: Garante que as operações sejam realizadas no início de cada candle.
- **Logs Detalhados**: Acompanhe o progresso e possíveis erros diretamente na interface.

## Pré-requisitos

- **Python 3.x**
- **Bibliotecas Python**: listadas em `requirements.txt`

## Instalação

Clone o repositório e instale as dependências:

```bash
git clone https://github.com/seu-usuario/seu-repositorio.git
cd seu-repositorio
pip install -r requirements.txt

Como Usar

	1.	Inicie o Bot:
Execute o arquivo bot-gui.py:

python bot-gui.py


	2.	Faça Login:
	•	Insira seu e-mail e senha nos campos correspondentes.
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

Estrutura do Projeto

.
├── bot-gui.py                # Interface principal do bot
├── calculadora_martingale.py # Cálculos relacionados à estratégia de Martingale
├── catalogador.py            # Análise de dados históricos de candles
├── get-ativos.py             # Listagem de ativos disponíveis na IQ Option
├── README.md                 # Documentação do projeto
├── requirements.txt          # Dependências do projeto
└── LICENSE                   # Licença do projeto

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
	2.	Crie uma branch para sua funcionalidade:

git checkout -b minha-funcionalidade


	3.	Envie seu Pull Request para revisão.

Licença

Este projeto é licenciado sob a MIT License.

Suporte

Se você tiver alguma dúvida ou encontrar problemas, por favor, abra uma issue no GitHub ou entre em contato pelo e-mail: thiagosoteroprado@gmail.com .

Aviso Legal

Atenção: Use este bot de forma responsável. A negociação na IQ Option envolve riscos significativos, e você pode perder todo o capital investido. Certifique-se de compreender os riscos e pratique sempre em uma conta demo antes de utilizar fundos reais.

Créditos

	•	Desenvolvido por Thiago Prado.
	•	Agradecimentos especiais às bibliotecas de código aberto utilizadas neste projeto.

