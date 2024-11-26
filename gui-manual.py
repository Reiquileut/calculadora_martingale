import threading
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from iqoptionapi.stable_api import IQ_Option
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

    def enviar_ordem(self, ativo, valor, direcao, expiracao, tipo_operacao):
        """
        Envia uma ordem diretamente, sem verificar disponibilidade.

        Args:
            ativo (str): O ativo a ser operado.
            valor (float): Valor da operação.
            direcao (str): 'call' ou 'put'.
            expiracao (int): Tempo de expiração em minutos.
            tipo_operacao (str): 'digital' ou 'binary'.

        Returns:
            bool: True se a ordem foi executada com sucesso, False caso contrário.
        """
        try:
            if tipo_operacao.lower() == "digital":
                status, order_id = self.iq.buy_digital_spot(ativo, valor, direcao, expiracao)
            elif tipo_operacao.lower() == "binary":
                status, order_id = self.iq.buy(valor, ativo, direcao, expiracao)
            else:
                logger.error(f"Tipo de operação '{tipo_operacao}' inválido.")
                return False

            if status:
                logger.info(f"Ordem {tipo_operacao} executada com sucesso no ativo {ativo}! Order ID: {order_id}")
                return True
            else:
                logger.error(f"Falha ao executar ordem {tipo_operacao} no ativo {ativo}.")
                return False
        except Exception as e:
            logger.error(f"Erro ao executar ordem {tipo_operacao} no ativo {ativo}: {e}")
            return False

class BotMartingaleApp:
    """Classe principal do aplicativo Bot Martingale."""

    def __init__(self, root):
        self.root = root
        self.root.title("Bot Martingale Simplificado")

        # Definir tamanho mínimo da janela
        self.root.minsize(600, 500)

        # Variáveis de controle
        self.api = None

        # Configuração da interface
        self.setup_gui()

    def setup_gui(self):
        """Configura os elementos da interface gráfica."""
        # Estilos personalizados
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Você pode testar outros temas: 'default', 'alt', 'clam', 'vista', 'xpnative'
        self.style.configure('TButton', font=('Helvetica', 10))
        self.style.configure('TLabel', font=('Helvetica', 10))
        self.style.configure('TEntry', font=('Helvetica', 10))
        self.style.configure('TRadiobutton', font=('Helvetica', 10))
        self.style.configure('TFrame', background='#f0f0f0')

        # Frame principal
        self.main_frame = ttk.Frame(self.root, padding=(10, 10, 10, 10))
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Configurar grid no frame principal
        for i in range(10):
            self.main_frame.rowconfigure(i, weight=0)
        self.main_frame.rowconfigure(8, weight=1)  # Área de logs expande
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.columnconfigure(2, weight=1)

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

        ttk.Button(login_frame, text="Login", command=self.fazer_login).grid(row=0, column=2, rowspan=2, padx=(10, 0))

        # Separador
        ttk.Separator(self.main_frame, orient='horizontal').grid(row=1, column=0, columnspan=3, sticky="we", pady=10)

        # Campos de Configuração da Operação
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
        self.button_enviar = ttk.Button(controle_frame, text="Enviar Ordem", command=self.enviar_ordem, state=tk.DISABLED)
        self.button_enviar.pack(side=tk.LEFT, padx=5)

        # Área de Logs com Scrollbar
        logs_frame = ttk.LabelFrame(self.main_frame, text="Logs", padding=(10, 10))
        logs_frame.grid(row=4, column=0, columnspan=3, sticky="nsew")
        logs_frame.columnconfigure(0, weight=1)
        logs_frame.rowconfigure(0, weight=1)

        self.text_log = tk.Text(logs_frame, wrap=tk.WORD)
        self.text_log.grid(row=0, column=0, sticky="nsew")
        self.scrollbar_log = ttk.Scrollbar(logs_frame, command=self.text_log.yview)
        self.scrollbar_log.grid(row=0, column=1, sticky='ns')
        self.text_log['yscrollcommand'] = self.scrollbar_log.set

        # Status da Aplicação
        status_frame = ttk.Frame(self.main_frame)
        status_frame.grid(row=5, column=0, columnspan=3, sticky="we", pady=(10, 0))
        ttk.Label(status_frame, text="Status:").grid(row=0, column=0, sticky="e")
        self.label_status = ttk.Label(status_frame, text="Aguardando login...", foreground="black")
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
        self.log_mensagem("Tentando conectar à IQ Option...")
        threading.Thread(target=self.conectar, args=(email, senha), daemon=True).start()

    def conectar(self, email, senha):
        """Conecta à IQ Option e atualiza a interface."""
        try:
            self.api = IQOptionAPI(email, senha)
            status, reason = self.api.conectar()
            if status:
                # Configura o logging para a nova sessão
                self.setup_logging_session()
                self.api.alterar_tipo_conta("PRACTICE")
                self.log_mensagem("Conexão bem-sucedida!")
                saldo = self.obter_saldo_disponivel()
                self.atualizar_status("Conectado com sucesso!", "green")
                self.button_enviar.config(state=tk.NORMAL)
                logger.info("Usuário conectado com sucesso.")
            else:
                self.api = None
                self.atualizar_status("Erro ao conectar.", "red")
                self.log_mensagem(f"Falha na conexão: {reason}")
                messagebox.showerror("Erro de Login", f"Falha na conexão: {reason}")
                logger.error(f"Falha na conexão: {reason}")
        except Exception as e:
            self.api = None
            self.atualizar_status("Erro ao conectar.", "red")
            self.log_mensagem(f"Exceção durante conexão: {e}")
            messagebox.showerror("Erro de Login", f"Exceção durante conexão: {e}")
            logger.error(f"Exceção durante conexão: {traceback.format_exc()}")

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
        if novo_tipo == "PRACTICE":
            tipo_conta = "PRACTICE"
            tipo_texto = "Demo"
        else:
            tipo_conta = "REAL"
            tipo_texto = "Real"

        try:
            self.api.alterar_tipo_conta(tipo_conta)
            saldo = self.obter_saldo_disponivel()
            self.atualizar_saldo(saldo)
            self.atualizar_conta(tipo_texto)
            self.log_mensagem(f"Conta alterada para: {tipo_texto} | Saldo: R$ {saldo:.2f}")
            logger.info(f"Tipo de conta alterado para {tipo_conta}.")
        except Exception as e:
            self.log_mensagem(f"Erro ao alterar tipo de conta: {e}")
            messagebox.showerror("Erro", f"Erro ao alterar tipo de conta: {e}")
            logger.error(f"Erro ao alterar tipo de conta: {traceback.format_exc()}")

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

    def enviar_ordem(self):
        """Envia a ordem diretamente."""
        if self.api is None:
            messagebox.showerror("Erro", "Você precisa estar conectado para enviar ordens.")
            return

        ativo = self.entry_ativo.get().strip()
        payout = self.entry_payout.get().strip()
        valor = self.entry_valor_inicial.get().strip()
        direcao = self.var_direcao.get().strip()
        tipo_operacao = "digital"  # Você pode tornar isso uma opção se desejar

        # Validações básicas
        if not ativo:
            messagebox.showerror("Erro", "O campo 'Ativo' não pode estar vazio.")
            return
        try:
            payout = float(payout)
            if payout <= 0 or payout > 100:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "Payout deve ser um número entre 0 e 100.")
            return
        try:
            valor = float(valor)
            if valor <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "Valor inicial deve ser um número positivo.")
            return
        if direcao not in ["call", "put"]:
            messagebox.showerror("Erro", "Selecione uma direção válida (Compra ou Venda).")
            return

        self.atualizar_status("Enviando ordem...", "blue")
        self.log_mensagem(f"Enviando ordem: {direcao.upper()} | Ativo: {ativo} | Valor: R$ {valor:.2f} | Payout: {payout}%")
        threading.Thread(target=self.enviar_ordem_thread, args=(ativo, valor, direcao, 1, tipo_operacao), daemon=True).start()

    def enviar_ordem_thread(self, ativo, valor, direcao, expiracao, tipo_operacao):
        """Thread para enviar a ordem."""
        sucesso = self.api.enviar_ordem(ativo, valor, direcao, expiracao, tipo_operacao)
        if sucesso:
            self.log_mensagem(f"Ordem {tipo_operacao} enviada com sucesso para {ativo}.")
            self.atualizar_status("Ordem enviada com sucesso!", "green")
        else:
            self.log_mensagem(f"Falha ao enviar ordem para {ativo}.")
            self.atualizar_status("Falha ao enviar ordem.", "red")
            resposta = messagebox.askyesno("Erro", f"Falha ao enviar ordem para {ativo}. Deseja tentar novamente?")
            if resposta:
                self.enviar_ordem()

def main():
    root = tk.Tk()
    app = BotMartingaleApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
