# **Calculadora de Martingale, Bot GUI e Catalogador**

Este repositório contém um conjunto de scripts Python para realizar operações financeiras utilizando a estratégia de Martingale, com suporte para análise de dados históricos, simulação, e execução automatizada de ordens.

## **Componentes**

1. **Bot GUI**: Uma interface gráfica para executar operações automatizadas com controle manual de ciclos.
2. **Calculadora de Martingale**: Interface gráfica para calcular a sequência de apostas baseada no payout e estratégia de Martingale.
3. **Catalogador**: Analisa dados históricos de candles para avaliar a eficácia da estratégia.
4. **Get Ativos**: Lista ativos disponíveis para operação na IQ Option.
5. **Bot IQ**: Script básico para conectar à IQ Option e realizar operações.

---

## **Sumário**

- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Uso](#uso)
  - [Bot GUI](#bot-gui)
  - [Calculadora de Martingale](#calculadora-de-martingale)
  - [Catalogador](#catalogador)
  - [Get Ativos](#get-ativos)
- [Observações Importantes](#observações-importantes)
- [Licença](#licença)

---

## **Pré-requisitos**

Certifique-se de ter:

- **Python 3.7 ou superior**
- **MetaTrader 5** (para o uso do Catalogador)
- **Conta na IQ Option** para execução de operações.
- **Bibliotecas Python listadas no `requirements.txt`**

---

## **Instalação**

1. **Clone o repositório (opcional):**

    ```bash
    git clone https://github.com/seu-usuario/seu-repositorio.git
    cd seu-repositorio
    ```

2. **Crie um ambiente virtual (recomendado):**

    ```bash
    python -m venv venv
    source venv/bin/activate  # macOS/Linux
    venv\Scripts\activate     # Windows
    ```

3. **Instale as dependências:**

    ```bash
    pip install -r requirements.txt
    ```

---

## **Uso**

### **Bot GUI**

1. Execute o bot GUI:

    ```bash
    python bot-gui.py
    ```

2. **Configurações na GUI:**

   - **Ativo:** Insira o ativo desejado (ex.: "EURUSD").
   - **Payout (%):** Payout da corretora (ex.: "80").
   - **Valor Inicial:** Valor da primeira aposta.
   - **Tipo de Conta:** Selecione entre Demo e Real.
   - **Direção:** Escolha "Compra" ou "Venda".

3. **Ciclo de Operações:**
   - Clique em **Iniciar Ciclo** para começar a sequência.
   - O ciclo será interrompido manualmente ao clicar em **Encerrar Ciclo** ou automaticamente ao atingir saldo insuficiente.

4. **Fluxo Manual:**
   - Quando um gain é atingido, o ciclo é parado manualmente.
   - Para reiniciar, ajuste os parâmetros e clique novamente em **Iniciar Ciclo**.

---

### **Calculadora de Martingale**

- Calcule valores e direções das apostas para maximizar o lucro com a interface gráfica:

    ```bash
    python calculadora_martingale.py
    ```

---

### **Catalogador**

- Analise dados históricos para verificar a eficácia da estratégia:

    ```bash
    python catalogador.py
    ```

---

### **Get Ativos**

- Liste os ativos disponíveis para operação:

    ```bash
    python get-ativos.py
    ```

---

## **Observações Importantes**

- **Uso Responsável**: O Martingale pode levar a perdas significativas.
- **MetaTrader 5**: O catalogador requer o MetaTrader 5 configurado corretamente.
- **Controle Manual**: O bot GUI permite parar e reiniciar o ciclo conforme necessário, proporcionando maior controle.

---

## **Licença**

Este projeto é licenciado sob os termos da licença MIT. Consulte o arquivo LICENSE para mais detalhes.
