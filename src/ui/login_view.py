import tkinter as tk
from tkinter import messagebox
from src.controllers.auth_controller import AuthController

# Paleta de cores alinhada ao protótipo
BG_COLOR = "#2d2d2d"
FG_COLOR = "#ffffff"
INPUT_BG = "#1e1e1e"
BTN_BG = "#404040"
BTN_FG = "#ffffff"
FONT_TITLE = ("Arial", 20, "bold")
FONT_TEXT = ("Arial", 12)

class LoginView(tk.Frame):
    def __init__(self, parent, auth_controller: AuthController, on_success_callback):
        super().__init__(parent, bg=BG_COLOR)
        self.auth_controller = auth_controller
        self.on_success_callback = on_success_callback # Função chamada quando o login dá certo
        self.pack(fill=tk.BOTH, expand=True)
        
        self.render_login()

    def clear_view(self):
        for widget in self.winfo_children():
            widget.destroy()

    def render_login(self):
        self.clear_view()
        
        # Título
        tk.Label(self, text="KoiLingo", font=FONT_TITLE, bg=BG_COLOR, fg=FG_COLOR).pack(pady=(40, 10))
        tk.Label(self, text="Log in", font=("Arial", 16), bg=BG_COLOR, fg=FG_COLOR).pack(pady=(0, 30))

        # Campos
        tk.Label(self, text="E-mail", font=FONT_TEXT, bg=BG_COLOR, fg=FG_COLOR).pack(anchor="w", padx=50)
        entry_email = tk.Entry(self, font=FONT_TEXT, bg=INPUT_BG, fg=FG_COLOR, insertbackground=FG_COLOR, relief=tk.FLAT)
        entry_email.pack(fill=tk.X, padx=50, pady=(5, 15), ipady=5)

        tk.Label(self, text="Senha", font=FONT_TEXT, bg=BG_COLOR, fg=FG_COLOR).pack(anchor="w", padx=50)
        entry_password = tk.Entry(self, font=FONT_TEXT, bg=INPUT_BG, fg=FG_COLOR, insertbackground=FG_COLOR, show="*", relief=tk.FLAT)
        entry_password.pack(fill=tk.X, padx=50, pady=(5, 20), ipady=5)

        # Botões
        tk.Button(self, text="Não tenho uma conta", font=("Arial", 10), bg=BG_COLOR, fg="#aaaaaa", relief=tk.FLAT, activebackground=BG_COLOR, activeforeground=FG_COLOR, borderwidth=0, command=self.render_register).pack(pady=5)
        
        tk.Button(self, text="Log In", font=FONT_TEXT, bg=BTN_BG, fg=BTN_FG, relief=tk.FLAT, command=lambda: self.handle_login(entry_email.get(), entry_password.get())).pack(pady=10, ipadx=20, ipady=5)

    def render_register(self):
        self.clear_view()
        
        tk.Label(self, text="KoiLingo", font=FONT_TITLE, bg=BG_COLOR, fg=FG_COLOR).pack(pady=(20, 5))
        tk.Label(self, text="Criar conta", font=("Arial", 16), bg=BG_COLOR, fg=FG_COLOR).pack(pady=(0, 20))

        # Campos de Registo
        tk.Label(self, text="E-mail", font=FONT_TEXT, bg=BG_COLOR, fg=FG_COLOR).pack(anchor="w", padx=50)
        entry_email = tk.Entry(self, font=FONT_TEXT, bg=INPUT_BG, fg=FG_COLOR, insertbackground=FG_COLOR, relief=tk.FLAT)
        entry_email.pack(fill=tk.X, padx=50, pady=(2, 10), ipady=5)

        tk.Label(self, text="Senha", font=FONT_TEXT, bg=BG_COLOR, fg=FG_COLOR).pack(anchor="w", padx=50)
        entry_pass = tk.Entry(self, font=FONT_TEXT, bg=INPUT_BG, fg=FG_COLOR, insertbackground=FG_COLOR, show="*", relief=tk.FLAT)
        entry_pass.pack(fill=tk.X, padx=50, pady=(2, 10), ipady=5)

        tk.Label(self, text="Confirmar Senha", font=FONT_TEXT, bg=BG_COLOR, fg=FG_COLOR).pack(anchor="w", padx=50)
        entry_conf_pass = tk.Entry(self, font=FONT_TEXT, bg=INPUT_BG, fg=FG_COLOR, insertbackground=FG_COLOR, show="*", relief=tk.FLAT)
        entry_conf_pass.pack(fill=tk.X, padx=50, pady=(2, 10), ipady=5)

        tk.Label(self, text="Data de nascimento (AAAA-MM-DD)", font=FONT_TEXT, bg=BG_COLOR, fg=FG_COLOR).pack(anchor="w", padx=50)
        entry_birth = tk.Entry(self, font=FONT_TEXT, bg=INPUT_BG, fg=FG_COLOR, insertbackground=FG_COLOR, relief=tk.FLAT)
        entry_birth.pack(fill=tk.X, padx=50, pady=(2, 15), ipady=5)

        # Botões
        tk.Button(self, text="Tenho uma conta", font=("Arial", 10), bg=BG_COLOR, fg="#aaaaaa", relief=tk.FLAT, activebackground=BG_COLOR, activeforeground=FG_COLOR, borderwidth=0, command=self.render_login).pack(pady=5)
        
        tk.Button(self, text="Registrar", font=FONT_TEXT, bg=BTN_BG, fg=BTN_FG, relief=tk.FLAT, 
                  command=lambda: self.handle_register(entry_email.get(), entry_pass.get(), entry_conf_pass.get(), entry_birth.get())).pack(pady=5, ipadx=20, ipady=5)

    def render_username_setup(self):
        self.clear_view()
        
        tk.Label(self, text="KoiLingo", font=FONT_TITLE, bg=BG_COLOR, fg=FG_COLOR).pack(pady=(40, 10))
        tk.Label(self, text="Bem vindo(a)!", font=("Arial", 16), bg=BG_COLOR, fg=FG_COLOR).pack(pady=(0, 20))
        
        tk.Label(self, text="Escolha um nome de usuário:", font=FONT_TEXT, bg=BG_COLOR, fg=FG_COLOR).pack(pady=10)
        entry_user = tk.Entry(self, font=FONT_TEXT, bg=INPUT_BG, fg=FG_COLOR, insertbackground=FG_COLOR, relief=tk.FLAT)
        entry_user.pack(fill=tk.X, padx=50, pady=10, ipady=5)
        
        # Sugere o username gerado automaticamente no backend
        if self.auth_controller.current_user:
            entry_user.insert(0, self.auth_controller.current_user.username)

        tk.Button(self, text="Confirmar", font=FONT_TEXT, bg=BTN_BG, fg=BTN_FG, relief=tk.FLAT, 
                  command=lambda: self.handle_setup_username(entry_user.get())).pack(pady=20, ipadx=20, ipady=5)

    def handle_login(self, email, password):
        success, msg = self.auth_controller.login(email, password)
        if success:
            self.on_success_callback()
        else:
            messagebox.showerror("Erro de Login", msg)

    def handle_register(self, email, password, confirm_password, birthdate):
        if not all([email, password, confirm_password, birthdate]):
            messagebox.showwarning("Aviso", "Preencha todos os campos obrigatórios.")
            return
            
        success, msg = self.auth_controller.register_aluno(email, password, confirm_password, birthdate)
        if success:
            self.render_username_setup()
        else:
            messagebox.showerror("Erro de Registo", msg)

    def handle_setup_username(self, username):
        if not username:
            messagebox.showwarning("Aviso", "O nome de utilizador não pode ser vazio.")
            return
            
        success, msg = self.auth_controller.update_username(username)
        if success:
            messagebox.showinfo("Sucesso", msg)
            self.on_success_callback()
        else:
            messagebox.showerror("Erro", msg)