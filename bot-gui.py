import threading
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from iqoptionapi.stable_api import IQ_Option
from calculadora_martingale import calcular_martingale
import time
import logging
import os
from datetime import datetime
import traceback

# Configuração inicial do logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

class IQOptionAPI:
    """Classe para gerenciar a conexão e operações com a IQ Option."""

    def __init__(self, email, senha):
        self.email = email
        self.senha = senha
        self.iq = IQ_Option(email, senha)

    def conectar(self):
        """Conecta à IQ Option."""
        status, reason = self.iq.connect()
        return status, reason

    def alterar_tipo_conta(self, tipo_conta):
        """Altera o tipo de conta."""
        self.iq.change_balance(tipo_conta)

    def obter_saldo(self):
        """Obtém o saldo disponível."""
        return self.iq.get_balance()

    def verificar_ativo(self, ativo):
        """Verifica se o ativo está disponível para operações digitais."""
        open_time = self.iq.get_all_open_time()
        return ativo in open_time["digital"] and open_time["digital"][ativo]["open"]

    def executar_ordem(self, ativo, valor, direcao):
        """Executa uma ordem digital."""
        status, order_id = self.iq.buy_digital_spot(ativo, valor, direcao, 1)
        return status, order_id

class BotMartingaleApp:
    """Classe principal do aplicativo Bot Martingale."""

    def __init__(self, root):
        self.root = root
        self.root.title("Bot Martingale")

        # Definir tamanho mínimo da janela
        self.root.minsize(600, 500)

        # Variáveis de controle
        self.CICLO_ATIVO = False
        self.TIPO_CONTA = "PRACTICE"
        self.api = None

        # Configuração da interface
        self.setup_gui()

    def setup_gui(self):
        """Configura os elementos da interface gráfica."""
        # Estilos personalizados
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TButton', font=('Helvetica', 10))
        self.style.configure('TLabel', font=('Helvetica', 10))
        self.style.configure('TEntry', font=('Helvetica', 10))
        self.style.configure('TRadiobutton', font=('Helvetica', 10))
        self.style.configure('TFrame', background='#f0f0f0')

        # Frame principal
        self.main_frame = ttk.Frame(self.root, padding=(10, 10, 10, 10))
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Configurar grid no frame principal
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.columnconfigure(2, weight=1)
        self.main_frame.rowconfigure(5, weight=1)  # Área de logs expande

        # Campos de Login
        login_frame = ttk.LabelFrame(self.main_frame, text="Login", padding=(10, 10))
        login_frame.grid(row=0, column=0, columnspan=3, sticky="we", pady=(0, 10))
        login_frame.columnconfigure(1, weight=1)

        ttk.Label(login_frame, text="E-mail:").grid(row=0, column=0, sticky="e")
        self.entry_email = ttk.Entry(login_frame)
        self.entry_email.grid(row=0, column=1, sticky="we")

        ttk.Label(login_frame, text="Senha:").grid(row=1, column=0, sticky="e")
        self.entry_senha = ttk.Entry(login_frame, show="*")
        self.entry_senha.grid(row=1, column=1, sticky="we")

        self.button_login = ttk.Button(login_frame, text="Login", command=self.fazer_login)
        self.button_login.grid(row=0, column=2, rowspan=2, padx=(10, 0))

        # Separador
        ttk.Separator(self.main_frame, orient='horizontal').grid(row=1, column=0, columnspan=3, sticky="we", pady=10)

        # Campos de Configuração
        config_frame = ttk.LabelFrame(self.main_frame, text="Configurações da Operação", padding=(10, 10))
        config_frame.grid(row=2, column=0, columnspan=3, sticky="we", pady=(0, 10))
        config_frame.columnconfigure(1, weight=1)
        config_frame.columnconfigure(2, weight=1)

        ttk.Label(config_frame, text="Ativo:").grid(row=0, column=0, sticky="e")
        self.entry_ativo = ttk.Entry(config_frame)
        self.entry_ativo.grid(row=0, column=1, sticky="we")

        ttk.Label(config_frame, text="Payout (%):").grid(row=1, column=0, sticky="e")
        self.entry_payout = ttk.Entry(config_frame)
        self.entry_payout.grid(row=1, column=1, sticky="we")

        ttk.Label(config_frame, text="Valor Inicial:").grid(row=2, column=0, sticky="e")
        self.entry_valor_inicial = ttk.Entry(config_frame)
        self.entry_valor_inicial.grid(row=2, column=1, sticky="we")

        ttk.Label(config_frame, text="Direção:").grid(row=3, column=0, sticky="e")
        self.var_direcao = tk.StringVar(value="call")
        direcao_frame = ttk.Frame(config_frame)
        direcao_frame.grid(row=3, column=1, sticky="w")
        ttk.Radiobutton(direcao_frame, text="Compra", variable=self.var_direcao, value="call").pack(side=tk.LEFT)
        ttk.Radiobutton(direcao_frame, text="Venda", variable=self.var_direcao, value="put").pack(side=tk.LEFT)

        # Botões de Controle
        controle_frame = ttk.Frame(self.main_frame)
        controle_frame.grid(row=3, column=0, columnspan=3, pady=(0, 10))
        self.button_iniciar = ttk.Button(controle_frame, text="Iniciar Ciclo", command=self.iniciar_ciclo)
        self.button_iniciar.pack(side=tk.LEFT, padx=5)
        self.button_encerrar = ttk.Button(controle_frame, text="Encerrar Ciclo", command=self.encerrar_ciclo, state=tk.DISABLED)
        self.button_encerrar.pack(side=tk.LEFT, padx=5)

        # Seleção de Tipo de Conta
        conta_frame = ttk.LabelFrame(self.main_frame, text="Conta", padding=(10, 10))
        conta_frame.grid(row=4, column=0, columnspan=3, sticky="we", pady=(0, 10))
        conta_frame.columnconfigure(1, weight=1)

        self.var_tipo_conta = tk.StringVar(value="PRACTICE")
        ttk.Label(conta_frame, text="Tipo de Conta:").grid(row=0, column=0, sticky="e")
        tipo_conta_frame = ttk.Frame(conta_frame)
        tipo_conta_frame.grid(row=0, column=1, sticky="w")
        self.radio_demo = ttk.Radiobutton(tipo_conta_frame, text="Demo", variable=self.var_tipo_conta, value="PRACTICE", command=self.alterar_tipo_conta, state=tk.DISABLED)
        self.radio_demo.pack(side=tk.LEFT)
        self.radio_real = ttk.Radiobutton(tipo_conta_frame, text="Real", variable=self.var_tipo_conta, value="REAL", command=self.alterar_tipo_conta, state=tk.DISABLED)
        self.radio_real.pack(side=tk.LEFT)

        ttk.Label(conta_frame, text="Saldo Atual:").grid(row=1, column=0, sticky="e")
        self.label_saldo = ttk.Label(conta_frame, text="R$ 0.00")
        self.label_saldo.grid(row=1, column=1, sticky="w")

        ttk.Label(conta_frame, text="Conta Atual:").grid(row=2, column=0, sticky="e")
        self.label_conta = ttk.Label(conta_frame, text="Demo")
        self.label_conta.grid(row=2, column=1, sticky="w")

        # Área de Logs com Scrollbar
        logs_frame = ttk.LabelFrame(self.main_frame, text="Logs", padding=(10, 10))
        logs_frame.grid(row=5, column=0, columnspan=3, sticky="nsew")
        logs_frame.columnconfigure(0, weight=1)
        logs_frame.rowconfigure(0, weight=1)

        self.text_log = tk.Text(logs_frame, wrap=tk.WORD)
        self.text_log.grid(row=0, column=0, sticky="nsew")
        self.scrollbar_log = ttk.Scrollbar(logs_frame, command=self.text_log.yview)
        self.scrollbar_log.grid(row=0, column=1, sticky='ns')
        self.text_log['yscrollcommand'] = self.scrollbar_log.set

        # Status do Ciclo
        status_frame = ttk.Frame(self.main_frame)
        status_frame.grid(row=6, column=0, columnspan=3, sticky="we", pady=(10, 0))
        ttk.Label(status_frame, text="Status do Ciclo:").grid(row=0, column=0, sticky="e")
        self.label_status = ttk.Label(status_frame, text="Aguardando ação...", foreground="black")
        self.label_status.grid(row=0, column=1, sticky="w")

        # Ajuste de Layout
        for child in self.main_frame.winfo_children():
            child.grid_configure(padx=5, pady=5)

    def fazer_login(self):
        """Realiza o login na plataforma IQ Option."""
        email = self.entry_email.get().strip()
        senha = self.entry_senha.get().strip()

        if not email or not senha:
            messagebox.showerror("Erro de Login", "Por favor, preencha o e-mail e a senha.")
            return

        self.atualizar_status("Conectando...", "blue")
        # Desabilitar campos de login e botão
        self.entry_email.config(state=tk.DISABLED)
        self.entry_senha.config(state=tk.DISABLED)
        self.button_login.config(state=tk.DISABLED)
        threading.Thread(target=self.conectar, args=(email, senha)).start()

    def conectar(self, email, senha):
        """Conecta à IQ Option e atualiza a interface."""
        try:
            self.api = IQOptionAPI(email, senha)
            status, reason = self.api.conectar()
            if status:
                # Configura o logging para a nova sessão
                self.setup_logging_session()
                self.api.alterar_tipo_conta(self.TIPO_CONTA)
                self.log_mensagem("Conexão bem-sucedida!")
                saldo = self.obter_saldo_disponivel()
                self.atualizar_saldo(saldo)
                self.atualizar_conta("Demo" if self.TIPO_CONTA == "PRACTICE" else "Real")
                self.atualizar_status("Conectado com sucesso!", "green")
                # Habilitar botões após login
                self.root.after(0, lambda: self.radio_demo.config(state=tk.NORMAL))
                self.root.after(0, lambda: self.radio_real.config(state=tk.NORMAL))
                logger.info("Usuário conectado com sucesso.")
            else:
                self.api = None
                self.atualizar_status("Erro ao conectar.", "red")
                self.log_mensagem(f"Falha na conexão: {reason}")
                self.root.after(0, lambda: messagebox.showerror("Erro de Login", f"Falha na conexão: {reason}"))
                logger.error(f"Falha na conexão: {reason}")
        except Exception as e:
            self.api = None
            self.atualizar_status("Erro ao conectar.", "red")
            self.log_mensagem(f"Exceção durante conexão: {e}")
            self.root.after(0, lambda: messagebox.showerror("Erro de Login", f"Exceção durante conexão: {e}"))
            logger.error(f"Exceção durante conexão: {traceback.format_exc()}")
        finally:
            # Reabilitar campos de login e botão
            self.root.after(0, lambda: self.entry_email.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.entry_senha.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.button_login.config(state=tk.NORMAL))

    def setup_logging_session(self):
        """Configura o logging para uma nova sessão."""
        # Criar diretório 'logs' se não existir
        if not os.path.exists('logs'):
            os.makedirs('logs')

        # Gerar um novo nome de arquivo de log com timestamp
        log_filename = datetime.now().strftime("bot_martingale_%Y%m%d_%H%M%S.log")
        log_filepath = os.path.join('logs', log_filename)

        # Remover handlers existentes
        logger = logging.getLogger()
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
            handler.close()

        # Criar um novo handler para o novo arquivo de log
        handler = logging.FileHandler(log_filepath)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # Manter apenas os últimos 15 arquivos de log
        self.cleanup_log_files()

    def cleanup_log_files(self):
        """Mantém apenas os últimos 15 arquivos de log."""
        log_files = [f for f in os.listdir('logs') if f.startswith('bot_martingale_') and f.endswith('.log')]
        if len(log_files) > 15:
            # Ordenar arquivos por nome (que contém a data e hora)
            log_files.sort()
            files_to_delete = log_files[:-15]  # Manter os últimos 15 arquivos
            for file_name in files_to_delete:
                file_path = os.path.join('logs', file_name)
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Erro ao excluir arquivo de log {file_name}: {e}")

    def alterar_tipo_conta(self):
        """Altera o tipo de conta (Demo ou Real)."""
        if self.api is None:
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
        self.api.alterar_tipo_conta(self.TIPO_CONTA)
        saldo = self.obter_saldo_disponivel()
        self.atualizar_saldo(saldo)
        self.atualizar_conta("Demo" if self.TIPO_CONTA == "PRACTICE" else "Real")
        self.log_mensagem(f"Conta alterada para: {'Demo' if self.TIPO_CONTA == 'PRACTICE' else 'Real'} | Saldo: R$ {saldo:.2f}")
        logger.info(f"Tipo de conta alterado para {self.TIPO_CONTA}.")

    def verificar_ativo(self, ativo):
        """Verifica se o ativo está disponível para operações digitais."""
        if self.api is None:
            return False
        return self.api.verificar_ativo(ativo)

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
        if self.api is None:
            return 0.0
        saldo = self.api.obter_saldo()
        self.log_mensagem(f"Saldo atualizado: R$ {saldo:.2f}")
        logger.info(f"Saldo atualizado: R$ {saldo:.2f}")
        return saldo

    def log_mensagem(self, msg):
        """Exibe logs na GUI de forma segura."""
        def _log():
            self.text_log.insert(tk.END, f"{msg}\n")
            self.text_log.see(tk.END)
        self.root.after(0, _log)
        logger.info(msg)

    def atualizar_status(self, mensagem, cor="black"):
        """Atualiza o status exibido na interface."""
        def _atualizar():
            self.label_status.config(text=mensagem, foreground=cor)
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
        self.root.after(0, lambda: self.button_iniciar.config(state=tk.DISABLED))
        self.root.after(0, lambda: self.radio_demo.config(state=tk.DISABLED))
        self.root.after(0, lambda: self.radio_real.config(state=tk.DISABLED))

        try:
            sequencia, acoes = calcular_martingale(valor_inicial, payout, direcao_inicial)
        except ValueError as e:
            self.log_mensagem(f"Erro: {e}")
            self.atualizar_status("Erro ao calcular Martingale.", "red")
            self.CICLO_ATIVO = False
            self.root.after(0, lambda: self.button_iniciar.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.button_encerrar.config(state=tk.DISABLED))
            logger.error(f"Erro ao calcular Martingale: {e}")
            return

        self.log_mensagem(f"Iniciando ciclo para o ativo {ativo} | Direção inicial: {direcao_inicial} | Payout: {payout}%")
        self.atualizar_status("Executando ciclo...", "blue")
        logger.info(f"Iniciando ciclo para o ativo {ativo}.")

        # Mostrar mensagem de confirmação na thread principal
        self.root.after(0, lambda: messagebox.showinfo("Ciclo Iniciado", f"O ciclo para o ativo {ativo} foi iniciado."))

        try:
            self.sincronizar_com_candle()
            if not self.CICLO_ATIVO:
                self.log_mensagem("Ciclo interrompido antes da primeira ordem.")
                self.atualizar_status("Ciclo interrompido antes da execução.", "red")
                logger.warning("Ciclo interrompido antes da primeira ordem.")
                return

            saldo_disponivel = self.obter_saldo_disponivel()
            self.atualizar_saldo(saldo_disponivel)
            if saldo_disponivel < valor_inicial:
                self.log_mensagem(f"Saldo insuficiente. Saldo disponível: R$ {saldo_disponivel:.2f}")
                self.atualizar_status("Saldo insuficiente.", "red")
                logger.error("Saldo insuficiente para iniciar o ciclo.")
                return

            direcao_execucao = "call" if direcao_inicial == "call" else "put"
            status, _ = self.api.executar_ordem(ativo, valor_inicial, direcao_execucao)

            if status:
                self.log_mensagem(f"Primeira ordem executada: {direcao_execucao} | Valor: R$ {valor_inicial:.2f}")
                logger.info(f"Primeira ordem executada: {direcao_execucao} | Valor: R$ {valor_inicial:.2f}")
            else:
                self.log_mensagem(f"Erro ao executar a primeira ordem de valor R$ {valor_inicial:.2f}. Encerrando ciclo.")
                self.atualizar_status("Erro na execução da primeira ordem.", "red")
                logger.error("Erro na execução da primeira ordem.")
                return

            for index, (acao, valor) in enumerate(zip(acoes, sequencia)):
                if not self.CICLO_ATIVO:
                    self.log_mensagem("Ciclo interrompido manualmente durante a execução.")
                    self.atualizar_status("Ciclo interrompido.", "red")
                    logger.warning("Ciclo interrompido manualmente durante a execução.")
                    break

                self.sincronizar_com_candle()
                if not self.CICLO_ATIVO:
                    break

                saldo_disponivel = self.obter_saldo_disponivel()
                self.atualizar_saldo(saldo_disponivel)
                if saldo_disponivel < valor:
                    self.log_mensagem(f"Saldo insuficiente para a ordem {index + 2}. Saldo disponível: R$ {saldo_disponivel:.2f}")
                    self.atualizar_status("Saldo insuficiente para sequência.", "red")
                    logger.error("Saldo insuficiente durante a sequência.")
                    break

                direcao_execucao = "call" if acao == "C" else "put"
                status, _ = self.api.executar_ordem(ativo, valor, direcao_execucao)

                if status:
                    self.log_mensagem(f"Ordem {index + 2} executada: {direcao_execucao} | Valor: R$ {valor:.2f}")
                    logger.info(f"Ordem {index + 2} executada: {direcao_execucao} | Valor: R$ {valor:.2f}")
                else:
                    self.log_mensagem(f"Erro ao executar ordem de valor R$ {valor:.2f}. Encerrando ciclo.")
                    self.atualizar_status("Erro na execução de uma ordem.", "red")
                    logger.error(f"Erro ao executar ordem de valor R$ {valor:.2f}.")
                    break

            # Atualizar saldo após o ciclo
            saldo_final = self.obter_saldo_disponivel()
            self.atualizar_saldo(saldo_final)

        except Exception as e:
            self.log_mensagem(f"Erro inesperado durante o ciclo: {e}")
            self.atualizar_status("Erro inesperado durante o ciclo.", "red")
            logger.error(f"Erro inesperado durante o ciclo: {traceback.format_exc()}")
        finally:
            self.log_mensagem("Ciclo finalizado.")
            self.atualizar_status("Ciclo finalizado.", "green")
            self.CICLO_ATIVO = False
            self.root.after(0, lambda: self.button_iniciar.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.button_encerrar.config(state=tk.DISABLED))
            self.root.after(0, lambda: self.radio_demo.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.radio_real.config(state=tk.NORMAL))
            logger.info("Ciclo finalizado.")
            # Mostrar mensagem ao finalizar ciclo na thread principal
            self.root.after(0, lambda: messagebox.showinfo("Ciclo Finalizado", "O ciclo de negociação foi finalizado."))

    def iniciar_ciclo(self):
        """Inicia o ciclo de negociação."""
        if self.CICLO_ATIVO:
            messagebox.showwarning("Aviso", "Já existe um ciclo em execução.")
            return

        if self.api is None:
            messagebox.showerror("Erro", "Você precisa estar conectado para iniciar um ciclo.")
            return

        ativo = self.entry_ativo.get().strip()
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

        # Desabilitar botões antes de iniciar o ciclo
        self.button_iniciar.config(state=tk.DISABLED)
        self.button_encerrar.config(state=tk.DISABLED)  # Será habilitado no início do ciclo
        self.radio_demo.config(state=tk.DISABLED)
        self.radio_real.config(state=tk.DISABLED)

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
            self.radio_demo.config(state=tk.NORMAL)
            self.radio_real.config(state=tk.NORMAL)
            logger.warning("Ciclo interrompido manualmente.")

if __name__ == "__main__":
    root = tk.Tk()
    app = BotMartingaleApp(root)
    root.mainloop()