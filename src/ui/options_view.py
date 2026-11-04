import tkinter as tk
from tkinter import messagebox

BG_COLOR = "#2d2d2d"
FG_COLOR = "#ffffff"
BTN_BG = "#3a3a3a"
INPUT_BG = "#1e1e1e"

class OptionsView(tk.Frame):
    def __init__(self, parent, app_window):
        super().__init__(parent, bg=BG_COLOR)
        self.app_window = app_window
        self.auth_controller = app_window.auth_controller
        self.pack(fill=tk.BOTH, expand=True)
        
        self.render_header()
        
        self.content_frame = tk.Frame(self, bg=BG_COLOR)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)
        
        # Elemento inferior fixo para botões de formulário
        self.bottom_frame = tk.Frame(self, bg=BG_COLOR)
        self.bottom_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=20, padx=40)
        
        self.render_main_options()

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        for widget in self.bottom_frame.winfo_children():
            widget.destroy()

    def render_header(self):
        header = tk.Frame(self, bg="#1e1e1e", height=60)
        header.pack(fill=tk.X)
        tk.Button(header, text="← Voltar", bg=BTN_BG, fg=FG_COLOR, font=("Arial", 12), relief=tk.FLAT, 
                  command=self.app_window.show_dashboard).pack(side=tk.LEFT, padx=20, pady=15)
        tk.Label(header, text="Opções", font=("Arial", 16, "bold"), bg="#1e1e1e", fg=FG_COLOR).pack(side=tk.LEFT, padx=20, pady=15)

    # --- SLIDE 24: Menu Principal de Opções ---
    def render_main_options(self):
        self.clear_content()
        opcoes = [
            ("Zerar Progresso", self.render_confirm_reset),
            ("Editar Perfil", self.render_edit_profile),
            ("Sair", self.app_window.handle_logout),
            ("Apagar Conta", self.render_confirm_delete)
        ]
        
        for texto, comando in opcoes:
            tk.Button(self.content_frame, text=texto, font=("Arial", 14), bg=BTN_BG, fg=FG_COLOR, relief=tk.FLAT, 
                      command=comando).pack(fill=tk.X, pady=10, ipady=10)

    # --- SLIDES 25 e 26: Confirmações ---
    def _render_confirmation(self, question):
        self.clear_content()
        tk.Label(self.content_frame, text=question, font=("Arial", 16), bg=BG_COLOR, fg=FG_COLOR, justify=tk.CENTER).pack(pady=(40, 20))
        tk.Label(self.content_frame, text="Essa ação é irreversível", font=("Arial", 14, "bold"), bg=BG_COLOR, fg="#aaaaaa").pack(pady=(0, 40))
        
        btn_frame = tk.Frame(self.content_frame, bg=BG_COLOR)
        btn_frame.pack()
        btn_nao = tk.Button(btn_frame, text="Não", font=("Arial", 14), bg=BTN_BG, fg=FG_COLOR, relief=tk.FLAT, width=10, command=self.render_main_options)
        btn_nao.pack(side=tk.LEFT, padx=20)
        return btn_frame # Retorna o frame para adicionarmos o botão "Sim" customizado
        
    def render_confirm_reset(self):
        f = self._render_confirmation("Você tem certeza que quer zerar seu\nprogresso?")
        tk.Button(f, text="Sim", font=("Arial", 14), bg="#f44336", fg=FG_COLOR, relief=tk.FLAT, width=10, command=self.handle_reset).pack(side=tk.LEFT, padx=20)

    def render_confirm_delete(self):
        f = self._render_confirmation("Você tem certeza que quer apagar sua\nconta?")
        tk.Button(f, text="Sim", font=("Arial", 14), bg="#f44336", fg=FG_COLOR, relief=tk.FLAT, width=10, command=self.handle_delete).pack(side=tk.LEFT, padx=20)

    # --- SLIDE 27: Editar Perfil ---
    def render_edit_profile(self):
        self.clear_content()
        user = self.auth_controller.current_user
        username = user.username if user else "Usuário"
        
        tk.Label(self.content_frame, text=username, font=("Arial", 18, "bold"), bg=BG_COLOR, fg=FG_COLOR).pack(anchor="w", pady=(0, 20))
        
        tk.Button(self.content_frame, text="Alterar E-mail", font=("Arial", 14), bg=BTN_BG, fg=FG_COLOR, relief=tk.FLAT, command=lambda: self.render_input_edit("E-mail", "email@exemplo.com", self.handle_update_email)).pack(fill=tk.X, pady=10, ipady=10)
        tk.Button(self.content_frame, text="Alterar Senha", font=("Arial", 14), bg=BTN_BG, fg=FG_COLOR, relief=tk.FLAT, command=lambda: self.render_input_edit("Senha", "********", self.handle_update_password, is_pw=True)).pack(fill=tk.X, pady=10, ipady=10)
        tk.Button(self.content_frame, text="Alterar Nome", font=("Arial", 14), bg=BTN_BG, fg=FG_COLOR, relief=tk.FLAT, command=lambda: self.render_input_edit("Nome de usuário", "Ex: user123", self.handle_update_username)).pack(fill=tk.X, pady=10, ipady=10)
        
        tk.Button(self.content_frame, text="Voltar", font=("Arial", 12), bg=BG_COLOR, fg="#aaaaaa", relief=tk.FLAT, command=self.render_main_options).pack(pady=20)

    # --- SLIDES 28, 29 e 30: Formulários de Edição ---
    def render_input_edit(self, field_name, placeholder, action_cmd, is_pw=False):
        self.clear_content()
        user = self.auth_controller.current_user
        username = user.username if user else "Usuário"
        
        tk.Label(self.content_frame, text=username, font=("Arial", 18, "bold"), bg=BG_COLOR, fg=FG_COLOR).pack(anchor="w", pady=(0, 30))
        tk.Label(self.content_frame, text=field_name, font=("Arial", 14), bg=BG_COLOR, fg=FG_COLOR).pack(anchor="w")
        
        entry = tk.Entry(self.content_frame, font=("Arial", 16), bg=INPUT_BG, fg=FG_COLOR, insertbackground=FG_COLOR, relief=tk.FLAT)
        if is_pw: entry.config(show="*")
        entry.insert(0, placeholder)
        
        # Limpa o placeholder ao clicar
        entry.bind("<FocusIn>", lambda e: entry.delete(0, tk.END) if entry.get() == placeholder else None)
        entry.pack(fill=tk.X, pady=10, ipady=5)
        
        tk.Frame(self.content_frame, bg="#555555", height=1).pack(fill=tk.X)
        
        tk.Button(self.bottom_frame, text="Cancelar", font=("Arial", 12, "bold"), bg=BTN_BG, fg=FG_COLOR, relief=tk.FLAT, command=self.render_edit_profile).pack(side=tk.LEFT, ipadx=20, ipady=5)
        tk.Button(self.bottom_frame, text="Confirmar", font=("Arial", 12, "bold"), bg="#4caf50", fg="white", relief=tk.FLAT, command=lambda: action_cmd(entry.get())).pack(side=tk.RIGHT, ipadx=20, ipady=5)

    # --- HANDLERS LÓGICOS ---
    def handle_reset(self):
        suc, msg = self.auth_controller.reset_progress()
        if suc:
            messagebox.showinfo("Sucesso", msg)
            self.app_window.show_dashboard()
        else: messagebox.showerror("Erro", msg)

    def handle_delete(self):
        suc, msg = self.auth_controller.delete_account()
        if suc:
            messagebox.showinfo("Aviso", msg)
            self.app_window.show_login()
        else: messagebox.showerror("Erro", msg)

    def handle_update_email(self, val):
        suc, msg = self.auth_controller.update_email(val)
        if suc:
            messagebox.showinfo("Sucesso", msg)
            self.render_edit_profile()
        else: messagebox.showerror("Erro", msg)

    def handle_update_password(self, val):
        suc, msg = self.auth_controller.update_password(val)
        if suc:
            messagebox.showinfo("Sucesso", msg)
            self.render_edit_profile()
        else: messagebox.showerror("Erro", msg)

    def handle_update_username(self, val):
        suc, msg = self.auth_controller.update_username(val)
        if suc:
            messagebox.showinfo("Sucesso", msg)
            self.render_edit_profile()
        else: messagebox.showerror("Erro", msg)