import threading
import tkinter as tk
from tkinter import messagebox
from iqoptionapi.stable_api import IQ_Option
from calculadora_martingale import calcular_martingale
import time

# Classe que representa a aplicação
class BotMartingaleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bot Martingale")

        # Variáveis de controle
        self.CICLO_ATIVO = False
        self.TIPO_CONTA = "PRACTICE"
        self.iq = None

        # Configuração da interface
        self.setup_gui()

    def setup_gui(self):
        """Configura os elementos da interface gráfica."""
        # Campos de Login
        tk.Label(self.root, text="E-mail:").grid(row=0, column=0, sticky="e")
        self.entry_email = tk.Entry(self.root)
        self.entry_email.grid(row=0, column=1, columnspan=2, sticky="we")

        tk.Label(self.root, text="Senha:").grid(row=1, column=0, sticky="e")
        self.entry_senha = tk.Entry(self.root, show="*")
        self.entry_senha.grid(row=1, column=1, columnspan=2, sticky="we")

        tk.Button(self.root, text="Login", command=self.fazer_login).grid(row=2, column=0, columnspan=3, pady=5)

        # Separador
        tk.Label(self.root, text="").grid(row=3, column=0)

        # Campos de Configuração
        tk.Label(self.root, text="Ativo:").grid(row=4, column=0, sticky="e")
        self.entry_ativo = tk.Entry(self.root)
        self.entry_ativo.grid(row=4, column=1, sticky="we")

        tk.Label(self.root, text="Payout (%):").grid(row=5, column=0, sticky="e")
        self.entry_payout = tk.Entry(self.root)
        self.entry_payout.grid(row=5, column=1, sticky="we")

        tk.Label(self.root, text="Valor Inicial:").grid(row=6, column=0, sticky="e")
        self.entry_valor_inicial = tk.Entry(self.root)
        self.entry_valor_inicial.grid(row=6, column=1, sticky="we")

        tk.Label(self.root, text="Direção:").grid(row=7, column=0, sticky="e")
        self.var_direcao = tk.StringVar(value="call")
        tk.Radiobutton(self.root, text="Compra", variable=self.var_direcao, value="call").grid(row=7, column=1, sticky="w")
        tk.Radiobutton(self.root, text="Venda", variable=self.var_direcao, value="put").grid(row=7, column=2, sticky="w")

        # Botões de Controle
        self.button_iniciar = tk.Button(self.root, text="Iniciar Ciclo", command=self.iniciar_ciclo)
        self.button_iniciar.grid(row=8, column=0, pady=5)
        self.button_encerrar = tk.Button(self.root, text="Encerrar Ciclo", command=self.encerrar_ciclo, state=tk.DISABLED)
        self.button_encerrar.grid(row=8, column=1, pady=5)

        # Seleção de Tipo de Conta
        tk.Label(self.root, text="Tipo de Conta:").grid(row=9, column=0, sticky="e")
        self.var_tipo_conta = tk.StringVar(value="PRACTICE")
        self.radio_demo = tk.Radiobutton(self.root, text="Demo", variable=self.var_tipo_conta, value="PRACTICE", command=self.alterar_tipo_conta, state=tk.DISABLED)
        self.radio_demo.grid(row=9, column=1, sticky="w")
        self.radio_real = tk.Radiobutton(self.root, text="Real", variable=self.var_tipo_conta, value="REAL", command=self.alterar_tipo_conta, state=tk.DISABLED)
        self.radio_real.grid(row=9, column=2, sticky="w")

        # Exibição de Saldo e Conta
        tk.Label(self.root, text="Saldo Atual:").grid(row=10, column=0, sticky="e")
        self.label_saldo = tk.Label(self.root, text="R$ 0.00")
        self.label_saldo.grid(row=10, column=1, sticky="w")

        tk.Label(self.root, text="Conta Atual:").grid(row=11, column=0, sticky="e")
        self.label_conta = tk.Label(self.root, text="Demo")
        self.label_conta.grid(row=11, column=1, sticky="w")

        # Área de Logs
        tk.Label(self.root, text="Logs:").grid(row=12, column=0, sticky="nw")
        self.text_log = tk.Text(self.root, height=10, width=50)
        self.text_log.grid(row=12, column=1, columnspan=2, sticky="we")

        # Status do Ciclo
        tk.Label(self.root, text="Status do Ciclo:").grid(row=13, column=0, sticky="e")
        self.label_status = tk.Label(self.root, text="Aguardando ação...", fg="black")
        self.label_status.grid(row=13, column=1, columnspan=2, sticky="w")

        # Ajuste de Layout
        for i in range(14):
            self.root.grid_rowconfigure(i, pad=5)
        for i in range(3):
            self.root.grid_columnconfigure(i, pad=5)

    def fazer_login(self):
        """Realiza o login na plataforma IQ Option."""
        email = self.entry_email.get().strip()
        senha = self.entry_senha.get().strip()

        if not email or not senha:
            messagebox.showerror("Erro de Login", "Por favor, preencha o e-mail e a senha.")
            return

        self.atualizar_status("Conectando...", "blue")
        threading.Thread(target=self.conectar, args=(email, senha)).start()

    def conectar(self, email, senha):
        """Conecta à IQ Option e atualiza a interface."""
        self.iq = IQ_Option(email, senha)
        status, reason = self.iq.connect()
        if status:
            self.iq.change_balance(self.TIPO_CONTA)
            self.log_mensagem("Conexão bem-sucedida!")
            saldo = self.obter_saldo_disponivel()
            self.atualizar_saldo(saldo)
            self.atualizar_conta("Demo" if self.TIPO_CONTA == "PRACTICE" else "Real")
            self.atualizar_status("Conectado com sucesso!", "green")
            # Habilitar botões após login
            self.root.after(0, lambda: self.radio_demo.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.radio_real.config(state=tk.NORMAL))
        else:
            self.iq = None
            self.atualizar_status("Erro ao conectar.", "red")
            self.log_mensagem(f"Falha na conexão: {reason}")
            messagebox.showerror("Erro de Login", f"Falha na conexão: {reason}")

    def alterar_tipo_conta(self):
        """Altera o tipo de conta (Demo ou Real)."""
        if self.iq is None:
            messagebox.showerror("Erro", "Faça login antes de alterar o tipo de conta.")
            return

        novo_tipo = self.var_tipo_conta.get()
        if novo_tipo == self.TIPO_CONTA:
            return  # Não há mudança

        if novo_tipo == "REAL":
            resposta = messagebox.askyesno("Confirmação", "Você tem certeza que deseja operar em conta REAL?")
            if not resposta:
                self.var_tipo_conta.set("PRACTICE")
                return

        self.TIPO_CONTA = novo_tipo
        self.iq.change_balance(self.TIPO_CONTA)
        saldo = self.obter_saldo_disponivel()
        self.atualizar_saldo(saldo)
        self.atualizar_conta("Demo" if self.TIPO_CONTA == "PRACTICE" else "Real")
        self.log_mensagem(f"Conta alterada para: {'Demo' if self.TIPO_CONTA == 'PRACTICE' else 'Real'} | Saldo: R$ {saldo:.2f}")

    def verificar_ativo(self, ativo):
        """Verifica se o ativo está disponível para operações digitais."""
        if self.iq is None:
            return False
        open_time = self.iq.get_all_open_time()
        return ativo in open_time["digital"] and open_time["digital"][ativo]["open"]

    def sincronizar_com_candle(self):
        """Sincroniza com o início do próximo candle."""
        tempo_atual = time.time()
        proximo_candle = tempo_atual + (60 - (tempo_atual % 60))

        while time.time() < proximo_candle:
            if not self.CICLO_ATIVO:
                return
            time.sleep(0.1)

    def obter_saldo_disponivel(self):
        """Obtém o saldo disponível da conta atual."""
        if self.iq is None:
            return 0.0
        saldo = self.iq.get_balance()
        self.log_mensagem(f"Saldo atualizado: R$ {saldo:.2f}")
        return saldo

    def log_mensagem(self, msg):
        """Exibe logs na GUI de forma segura."""
        def _log():
            self.text_log.insert(tk.END, f"{msg}\n")
            self.text_log.see(tk.END)
        self.root.after(0, _log)

    def atualizar_status(self, mensagem, cor="black"):
        """Atualiza o status exibido na interface."""
        def _atualizar():
            self.label_status.config(text=mensagem, fg=cor)
        self.root.after(0, _atualizar)

    def atualizar_saldo(self, saldo):
        """Atualiza o saldo exibido na interface."""
        def _atualizar():
            self.label_saldo.config(text=f"R$ {saldo:.2f}")
        self.root.after(0, _atualizar)

    def atualizar_conta(self, tipo):
        """Atualiza o tipo de conta exibido na interface."""
        def _atualizar():
            self.label_conta.config(text=tipo)
        self.root.after(0, _atualizar)

    def executar_ciclo(self, ativo, payout, direcao_inicial, valor_inicial):
        """Executa as operações conforme a sequência calculada."""
        self.CICLO_ATIVO = True
        self.root.after(0, lambda: self.button_encerrar.config(state=tk.NORMAL))

        try:
            sequencia, acoes = calcular_martingale(valor_inicial, payout, direcao_inicial)
        except ValueError as e:
            self.log_mensagem(f"Erro: {e}")
            self.atualizar_status("Erro ao calcular Martingale.", "red")
            self.CICLO_ATIVO = False
            self.root.after(0, lambda: self.button_iniciar.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.button_encerrar.config(state=tk.DISABLED))
            return

        self.log_mensagem(f"Iniciando ciclo para o ativo {ativo} | Direção inicial: {direcao_inicial} | Payout: {payout}%")
        self.atualizar_status("Executando ciclo...", "blue")

        try:
            self.sincronizar_com_candle()
            if not self.CICLO_ATIVO:
                self.log_mensagem("Ciclo interrompido antes da primeira ordem.")
                self.atualizar_status("Ciclo interrompido antes da execução.", "red")
                return

            saldo_disponivel = self.obter_saldo_disponivel()
            self.atualizar_saldo(saldo_disponivel)
            if saldo_disponivel < valor_inicial:
                self.log_mensagem(f"Saldo insuficiente. Saldo disponível: R$ {saldo_disponivel:.2f}")
                self.atualizar_status("Saldo insuficiente.", "red")
                return

            direcao_execucao = "call" if direcao_inicial == "call" else "put"
            status, _ = self.iq.buy_digital_spot(ativo, valor_inicial, direcao_execucao, 1)

            if status:
                self.log_mensagem(f"Primeira ordem executada: {direcao_execucao} | Valor: R$ {valor_inicial:.2f}")
            else:
                self.log_mensagem(f"Erro ao executar a primeira ordem de valor R$ {valor_inicial:.2f}. Encerrando ciclo.")
                self.atualizar_status("Erro na execução da primeira ordem.", "red")
                return

            for index, (acao, valor) in enumerate(zip(acoes, sequencia)):
                if not self.CICLO_ATIVO:
                    self.log_mensagem("Ciclo interrompido manualmente durante a execução.")
                    self.atualizar_status("Ciclo interrompido.", "red")
                    break

                self.sincronizar_com_candle()
                if not self.CICLO_ATIVO:
                    break

                saldo_disponivel = self.obter_saldo_disponivel()
                self.atualizar_saldo(saldo_disponivel)
                if saldo_disponivel < valor:
                    self.log_mensagem(f"Saldo insuficiente para a ordem {index + 2}. Saldo disponível: R$ {saldo_disponivel:.2f}")
                    self.atualizar_status("Saldo insuficiente para sequência.", "red")
                    break

                direcao_execucao = "call" if acao == "C" else "put"
                status, _ = self.iq.buy_digital_spot(ativo, valor, direcao_execucao, 1)

                if status:
                    self.log_mensagem(f"Ordem {index + 2} executada: {direcao_execucao} | Valor: R$ {valor:.2f}")
                else:
                    self.log_mensagem(f"Erro ao executar ordem de valor R$ {valor:.2f}. Encerrando ciclo.")
                    self.atualizar_status("Erro na execução de uma ordem.", "red")
                    break

            # Atualizar saldo após o ciclo
            saldo_final = self.obter_saldo_disponivel()
            self.atualizar_saldo(saldo_final)

        except Exception as e:
            self.log_mensagem(f"Erro inesperado durante o ciclo: {e}")
            self.atualizar_status("Erro inesperado durante o ciclo.", "red")
        finally:
            self.log_mensagem("Ciclo finalizado.")
            self.atualizar_status("Ciclo finalizado.", "green")
            self.CICLO_ATIVO = False
            self.root.after(0, lambda: self.button_iniciar.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.button_encerrar.config(state=tk.DISABLED))

    def iniciar_ciclo(self):
        """Inicia o ciclo de negociação."""
        if self.CICLO_ATIVO:
            messagebox.showwarning("Aviso", "Já existe um ciclo em execução.")
            return

        if self.iq is None:
            messagebox.showerror("Erro", "Você precisa estar conectado para iniciar um ciclo.")
            return

        ativo = self.entry_ativo.get().strip().upper()
        if not ativo:
            messagebox.showerror("Erro", "O campo 'Ativo' não pode estar vazio.")
            return

        try:
            payout = float(self.entry_payout.get())
            if payout <= 0 or payout > 100:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "Payout deve ser um número entre 0 e 100.")
            return

        try:
            valor_inicial = float(self.entry_valor_inicial.get())
            if valor_inicial <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "Valor inicial deve ser um número positivo.")
            return

        direcao = self.var_direcao.get()
        if direcao not in ["call", "put"]:
            messagebox.showerror("Erro", "Selecione uma direção válida (Compra ou Venda).")
            return

        if not self.verificar_ativo(ativo):
            messagebox.showerror("Erro", f"O ativo '{ativo}' não está disponível para operações no momento.")
            return

        self.log_mensagem(f"Iniciando ciclo para o ativo {ativo} com payout {payout}% e direção inicial {direcao}.")
        self.atualizar_status("Preparando para executar ciclo...", "blue")

        # Desativar botões durante a execução
        self.button_iniciar.config(state=tk.DISABLED)

        # Inicia o ciclo em uma nova thread
        threading.Thread(target=self.executar_ciclo, args=(ativo, payout, direcao, valor_inicial)).start()

    def encerrar_ciclo(self):
        """Encerra o ciclo de negociação."""
        if not self.CICLO_ATIVO:
            messagebox.showinfo("Informação", "Nenhum ciclo está em execução no momento.")
            return

        resposta = messagebox.askyesno("Confirmação", "Tem certeza que deseja encerrar o ciclo?")
        if resposta:
            self.CICLO_ATIVO = False
            self.log_mensagem("Ciclo interrompido manualmente.")
            self.atualizar_status("Ciclo interrompido.", "red")
            self.button_iniciar.config(state=tk.NORMAL)
            self.button_encerrar.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = BotMartingaleApp(root)
    root.mainloop()