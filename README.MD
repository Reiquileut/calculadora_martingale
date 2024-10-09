# Calculadora de Martingale e Catalogador

Este repositório contém dois programas em Python:

1. **Calculadora de Martingale**: Uma interface gráfica que ajuda a calcular a sequência de apostas e valores a serem apostados com base no payout da corretora e na estratégia de Martingale.

2. **Catalogador**: Um script que analisa os dados históricos de candles de 1 minuto do par EUR/USD e aplica a estratégia de Martingale, fornecendo estatísticas sobre ganhos e perdas ao longo do dia.

---

## **Sumário**

- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Uso](#uso)
  - [Calculadora de Martingale](#calculadora-de-martingale)
  - [Catalogador](#catalogador)
- [Observações Importantes](#observações-importantes)
- [Licença](#licença)
- [Contato](#contato)

---

## **Pré-requisitos**

Antes de utilizar os programas, certifique-se de ter o seguinte instalado em seu sistema:

- **Python 3.7 ou superior**
- **MetaTrader 5** (para o uso do Catalogador)
  - O MetaTrader 5 deve estar instalado e em execução.
  - Você deve estar logado em uma conta que possua acesso ao par EUR/USD.
- **Git** (opcional, para clonar o repositório)

---

## **Instalação**

1. **Clone o repositório (opcional):**

    ```bash
    git clone https://github.com/seu-usuario/seu-repositorio.git
    cd seu-repositorio
    ```

2. **Crie um ambiente virtual (recomendado):**

    ```bash
    # No Windows
    python -m venv venv
    venv\Scripts\activate

    # No macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3. **Atualize o `pip`:**

    ```bash
    pip install --upgrade pip
    ```

4. **Instale as dependências:**

    ```bash
    pip install -r requirements.txt
    ```

    **Nota:** Devido a incompatibilidades, é importante que a versão do NumPy seja inferior a 2.0. O arquivo `requirements.txt` já especifica a versão correta.

---

## **Uso**

### **Calculadora de Martingale**

1. **Navegue até o diretório da calculadora:**

    ```bash
    cd calculadora_martingale
    ```

2. **Execute o script:**

    ```bash
    python calculadora_martingale.py
    ```

3. **Utilize a interface gráfica:**

    - **Payout (%):** Insira a porcentagem de payout da corretora (por exemplo, `80` para 80%).
    - **Valor do Primeiro Aporte (R$):** Insira o valor da primeira aposta (mínimo de R$ 2).
    - **Botões de Compra e Venda:**
      - **Comprar (verde):** Clique para iniciar a sequência começando com compra.
      - **Vender (vermelho):** Clique para iniciar a sequência começando com venda.
    - **Resetar:** Limpa os campos e os resultados para uma nova simulação.

4. **Resultados:**

    - Após clicar em **Comprar** ou **Vender**, a calculadora exibirá visualmente a sequência de apostas e os valores a serem apostados em cada etapa, considerando o payout e a estratégia de Martingale.

### **Catalogador**

1. **Navegue até o diretório do catalogador:**

    ```bash
    cd catalogador
    ```

2. **Execute o script:**

    ```bash
    python catalogador.py
    ```

3. **Descrição do Script:**

    - O script conecta-se ao MetaTrader 5 e obtém os dados de candles de 1 minuto do par EUR/USD desde o início do dia.
    - Aplica a estratégia de Martingale alternando entre operações de compra e venda após cada gain.
    - Exibe o total de gains e losses, além dos horários em que ocorreram prejuízos após atingir o nível máximo de Martingale.

4. **Parâmetros Personalizáveis:**

    - **payout_percentage:** Porcentagem de payout (padrão: `80`).
    - **initial_bet:** Valor inicial da aposta (padrão: `2`).
    - **max_martingale:** Número máximo de níveis de Martingale (padrão: `8`).

    Você pode ajustar esses parâmetros diretamente no código, se necessário.

---

## **Observações Importantes**

- **MetaTrader 5:**
  - O MetaTrader 5 deve estar aberto e conectado a uma conta válida para que o catalogador funcione corretamente.
  - Certifique-se de que o par EUR/USD está disponível e possui dados históricos suficientes.

- **Estratégia de Martingale:**
  - O uso do Martingale pode levar a perdas significativas. Esteja ciente dos riscos envolvidos.
  - Este programa é fornecido para fins educacionais e não constitui aconselhamento financeiro.

- **Compatibilidade do NumPy:**
  - Devido a incompatibilidades entre o MetaTrader 5 e versões mais recentes do NumPy, é necessário usar uma versão do NumPy inferior a `2.0`.
  - O arquivo `requirements.txt` especifica a versão adequada.

---

## **Licença**

Este projeto é licenciado sob os termos da licença MIT. Consulte o arquivo [LICENSE](LICENSE) para obter mais informações.

---


