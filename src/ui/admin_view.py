import tkinter as tk
from tkinter import ttk, messagebox
from src.controllers.admin_controller import AdminController

BG_COLOR = "#2d2d2d"
FG_COLOR = "#ffffff"
BTN_BG = "#3a3a3a"
INPUT_BG = "#1e1e1e"

class AdminView(tk.Frame):
    def __init__(self, parent, app_window, admin_controller: AdminController):
        super().__init__(parent, bg=BG_COLOR)
        self.app_window = app_window
        self.admin_controller = admin_controller
        self.auth_controller = app_window.auth_controller
        
        self.dynamic_widgets = {} # Guarda os inputs da tela de exercícios dinâmicos
        
        self.pack(fill=tk.BOTH, expand=True)
        self.content_frame = tk.Frame(self, bg=BG_COLOR)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        self.render_main_menu()

    def _create_password_entry(self, parent, label_text):
        f = tk.Frame(parent, bg=BG_COLOR)
        f.pack(fill=tk.X, pady=10, padx=80)
        tk.Label(f, text=label_text, font=("Arial", 12), bg=BG_COLOR, fg="#aaaaaa").pack(anchor="w")
        e = tk.Entry(f, font=("Arial", 16), bg=BG_COLOR, fg=FG_COLOR, relief=tk.FLAT, insertbackground=FG_COLOR, show="*")
        e.pack(fill=tk.X, pady=5)
        tk.Frame(f, bg="#555555", height=1).pack(fill=tk.X)
        return e

    def render_change_email(self):
        self.clear_content()
        tk.Label(self.content_frame, text="Painel de Admin\nAlterar E-mail", font=("Arial", 16, "bold"), bg=BG_COLOR, fg=FG_COLOR, justify=tk.LEFT).pack(anchor="w", padx=40, pady=(30, 10))
        
        atual = self.auth_controller.current_user.email if self.auth_controller.current_user else ""
        tk.Label(self.content_frame, text=f"E-mail atual: {atual}", font=("Arial", 12), bg=BG_COLOR, fg="#aaaaaa").pack(anchor="w", padx=80, pady=(0, 10))
        
        e_email = self._create_entry(self.content_frame, "Novo E-mail")

        f_btns = tk.Frame(self.content_frame, bg=BG_COLOR)
        f_btns.pack(fill=tk.X, pady=30, padx=80)
        tk.Button(f_btns, text="Cancelar", font=("Arial", 12, "bold"), bg=BTN_BG, fg=FG_COLOR, relief=tk.FLAT, command=self.render_main_menu).pack(side=tk.LEFT, ipadx=20, ipady=5)

        def on_save():
            novo = e_email.get().strip()
            if novo == "Novo E-mail":
                novo = ""
            suc, msg = self.auth_controller.update_email(novo)
            if suc:
                messagebox.showinfo("Sucesso", msg)
                self.render_main_menu()
            else:
                messagebox.showerror("Erro", msg)

        tk.Button(f_btns, text="Salvar", font=("Arial", 12, "bold"), bg="#4caf50", fg="white", relief=tk.FLAT, command=on_save).pack(side=tk.RIGHT, ipadx=20, ipady=5)

    def render_change_password(self):
        self.clear_content()
        tk.Label(self.content_frame, text="Painel de Admin\nAlterar Senha", font=("Arial", 16, "bold"), bg=BG_COLOR, fg=FG_COLOR, justify=tk.LEFT).pack(anchor="w", padx=40, pady=(30, 10))

        e_atual = self._create_password_entry(self.content_frame, "Senha Atual")
        e_nova = self._create_password_entry(self.content_frame, "Nova Senha (mín. 6 caracteres)")
        e_conf = self._create_password_entry(self.content_frame, "Confirmar Nova Senha")

        f_btns = tk.Frame(self.content_frame, bg=BG_COLOR)
        f_btns.pack(fill=tk.X, pady=30, padx=80)
        tk.Button(f_btns, text="Cancelar", font=("Arial", 12, "bold"), bg=BTN_BG, fg=FG_COLOR, relief=tk.FLAT, command=self.render_main_menu).pack(side=tk.LEFT, ipadx=20, ipady=5)

        def on_save():
            user = self.auth_controller.current_user
            if not user or not user.authenticate(e_atual.get()):
                return messagebox.showerror("Erro", "Senha atual incorreta.")
            nova = e_nova.get()
            if nova != e_conf.get():
                return messagebox.showerror("Erro", "A nova senha e a confirmação não coincidem.")
            suc, msg = self.auth_controller.update_password(nova)
            if suc:
                messagebox.showinfo("Sucesso", msg)
                self.render_main_menu()
            else:
                messagebox.showerror("Erro", msg)

        tk.Button(f_btns, text="Salvar", font=("Arial", 12, "bold"), bg="#4caf50", fg="white", relief=tk.FLAT, command=on_save).pack(side=tk.RIGHT, ipadx=20, ipady=5)

    def render_register_admin(self):
        self.clear_content()
        tk.Label(self.content_frame, text="Painel de Admin\nRegistrar Novo Administrador", font=("Arial", 16, "bold"), bg=BG_COLOR, fg=FG_COLOR, justify=tk.LEFT).pack(anchor="w", padx=40, pady=(30, 10))

        e_email = self._create_entry(self.content_frame, "E-mail do Novo Admin")
        e_senha = self._create_password_entry(self.content_frame, "Senha (mín. 6 caracteres)")
        e_conf = self._create_password_entry(self.content_frame, "Confirmar Senha")

        f_btns = tk.Frame(self.content_frame, bg=BG_COLOR)
        f_btns.pack(fill=tk.X, pady=30, padx=80)
        tk.Button(f_btns, text="Cancelar", font=("Arial", 12, "bold"), bg=BTN_BG, fg=FG_COLOR, relief=tk.FLAT, command=self.render_main_menu).pack(side=tk.LEFT, ipadx=20, ipady=5)

        def on_register():
            email = e_email.get().strip()
            if email == "E-mail do Novo Admin":
                email = ""
            suc, msg = self.auth_controller.register_admin(email, e_senha.get(), e_conf.get())
            if suc:
                messagebox.showinfo("Sucesso", msg)
                self.render_main_menu()
            else:
                messagebox.showerror("Erro", msg)

        tk.Button(f_btns, text="Registrar", font=("Arial", 12, "bold"), bg="#4caf50", fg="white", relief=tk.FLAT, command=on_register).pack(side=tk.RIGHT, ipadx=20, ipady=5)

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def _create_entry(self, parent, placeholder):
        f = tk.Frame(parent, bg=BG_COLOR)
        f.pack(fill=tk.X, pady=15, padx=80)
        e = tk.Entry(f, font=("Arial", 16), bg=BG_COLOR, fg=FG_COLOR, relief=tk.FLAT, insertbackground=FG_COLOR)
        e.insert(0, placeholder)
        e.bind("<FocusIn>", lambda event: e.delete(0, tk.END) if e.get() == placeholder else None)
        e.bind("<FocusOut>", lambda event: e.insert(0, placeholder) if e.get() == "" else None)
        e.pack(fill=tk.X, pady=5)
        tk.Frame(f, bg="#555555", height=1).pack(fill=tk.X)
        return e

    def render_main_menu(self):
        self.clear_content()
        tk.Label(self.content_frame, text="Painel de Admin", font=("Arial", 20, "bold"), bg=BG_COLOR, fg=FG_COLOR).pack(pady=(40, 40))
        
        grid_frame = tk.Frame(self.content_frame, bg=BG_COLOR)
        grid_frame.pack(expand=True)
        
        col1 = tk.Frame(grid_frame, bg=BG_COLOR)
        col1.grid(row=0, column=0, padx=20)
        tk.Button(col1, text="Gerenciar Idiomas", font=("Arial", 14), bg=BTN_BG, fg=FG_COLOR, relief=tk.FLAT, width=25, command=self.render_manage_languages).pack(pady=15, ipady=5)
        tk.Button(col1, text="Gerenciar Unidades", font=("Arial", 14), bg=BTN_BG, fg=FG_COLOR, relief=tk.FLAT, width=25, command=self.render_manage_units).pack(pady=15, ipady=5)
        tk.Button(col1, text="Gerenciar Lições", font=("Arial", 14), bg=BTN_BG, fg=FG_COLOR, relief=tk.FLAT, width=25, command=self.render_manage_lessons).pack(pady=15, ipady=5)
        tk.Button(col1, text="Gerenciar Exercícios", font=("Arial", 14), bg=BTN_BG, fg=FG_COLOR, relief=tk.FLAT, width=25, command=self.render_manage_exercises).pack(pady=15, ipady=5)

        col2 = tk.Frame(grid_frame, bg=BG_COLOR)
        col2.grid(row=0, column=1, padx=20)
        tk.Button(col2, text="Alterar E-mail", font=("Arial", 14), bg=BTN_BG, fg=FG_COLOR, relief=tk.FLAT, width=25, command=self.render_change_email).pack(pady=15, ipady=5)
        tk.Button(col2, text="Alterar Senha", font=("Arial", 14), bg=BTN_BG, fg=FG_COLOR, relief=tk.FLAT, width=25, command=self.render_change_password).pack(pady=15, ipady=5)
        tk.Button(col2, text="Registrar Admin", font=("Arial", 14), bg=BTN_BG, fg=FG_COLOR, relief=tk.FLAT, width=25, command=self.render_register_admin).pack(pady=15, ipady=5)
        tk.Button(col2, text="Sair", font=("Arial", 14), bg=BTN_BG, fg=FG_COLOR, relief=tk.FLAT, width=25, command=self.app_window.handle_logout).pack(pady=15, ipady=5)
    def render_manage_languages(self):
        self.clear_content()
        tk.Label(self.content_frame, text="Painel de Admin\nID do Idioma", font=("Arial", 16, "bold"), bg=BG_COLOR, fg=FG_COLOR, justify=tk.LEFT).pack(anchor="w", padx=40, pady=20)
        tk.Button(self.content_frame, text="← Voltar", bg=BTN_BG, fg=FG_COLOR, relief=tk.FLAT, command=self.render_main_menu).pack(anchor="w", padx=40, pady=(0, 20))
        list_frame = tk.Frame(self.content_frame, bg=BG_COLOR)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=40)
        idiomas = self.admin_controller.get_all_languages()
        for lang_id, info in idiomas.items():
            row = tk.Frame(list_frame, bg=BG_COLOR)
            row.pack(fill=tk.X, pady=5)
            tk.Label(row, text=f"{lang_id[:8]}...", font=("Arial", 12), bg=BG_COLOR, fg="#aaaaaa", width=10, anchor="w").pack(side=tk.LEFT)
            tk.Label(row, text=info["name"], font=("Arial", 14), bg=BG_COLOR, fg=FG_COLOR).pack(side=tk.LEFT, padx=20)
            tk.Button(row, text="Remover", bg="#f44336", fg="white", relief=tk.FLAT, command=lambda lid=lang_id: self._del_lang(lid)).pack(side=tk.RIGHT)
            tk.Frame(list_frame, bg="#333333", height=1).pack(fill=tk.X, pady=5)
        tk.Button(self.content_frame, text="Criar Novo Idioma", font=("Arial", 14), bg=BTN_BG, fg=FG_COLOR, relief=tk.FLAT, command=self.render_create_language).pack(pady=20, ipady=5, fill=tk.X, padx=80)

    def _del_lang(self, lang_id):
        if messagebox.askyesno("Confirmar", "Tem certeza que deseja apagar?"):
            self.admin_controller.delete_language(lang_id)
            self.render_manage_languages()

    def render_create_language(self):
        self.clear_content()
        tk.Label(self.content_frame, text="Painel de Admin\nCriar Idioma", font=("Arial", 16, "bold"), bg=BG_COLOR, fg=FG_COLOR, justify=tk.LEFT).pack(anchor="w", padx=40, pady=30)
        e_nome = self._create_entry(self.content_frame, "Nome")
        f_btns = tk.Frame(self.content_frame, bg=BG_COLOR)
        f_btns.pack(fill=tk.X, pady=20, padx=80)
        tk.Button(f_btns, text="Cancelar", font=("Arial", 12, "bold"), bg=BTN_BG, fg=FG_COLOR, relief=tk.FLAT, command=self.render_manage_languages).pack(side=tk.LEFT, ipadx=20, ipady=5)
        def on_add():
            suc, msg = self.admin_controller.add_language(e_nome.get())
            if suc: self.render_manage_languages()
            else: messagebox.showerror("Erro", msg)
        tk.Button(f_btns, text="Adicionar", font=("Arial", 12, "bold"), bg="#4caf50", fg="white", relief=tk.FLAT, command=on_add).pack(side=tk.RIGHT, ipadx=20, ipady=5)

    def render_manage_units(self):
        self.clear_content()
        tk.Label(self.content_frame, text="Painel de Admin\nSelecione um Idioma", font=("Arial", 16, "bold"), bg=BG_COLOR, fg=FG_COLOR, justify=tk.LEFT).pack(anchor="w", padx=40, pady=20)
        tk.Button(self.content_frame, text="← Voltar", bg=BTN_BG, fg=FG_COLOR, relief=tk.FLAT, command=self.render_main_menu).pack(anchor="w", padx=40, pady=(0, 20))
        for lang_id, info in self.admin_controller.get_all_languages().items():
            tk.Button(self.content_frame, text=info["name"], font=("Arial", 14), bg=BTN_BG, fg=FG_COLOR, relief=tk.FLAT, command=lambda lid=lang_id, name=info["name"]: self.render_unit_list(lid, name)).pack(fill=tk.X, pady=10, ipady=5, padx=40)

    def render_unit_list(self, lang_id, lang_name):
        self.clear_content()
        tk.Label(self.content_frame, text=f"Painel de Admin\nGerenciador de Unidades de {lang_name}", font=("Arial", 16, "bold"), bg=BG_COLOR, fg=FG_COLOR, justify=tk.LEFT).pack(anchor="w", padx=40, pady=20)
        tk.Button(self.content_frame, text="← Voltar", bg=BTN_BG, fg=FG_COLOR, relief=tk.FLAT, command=self.render_manage_units).pack(anchor="w", padx=40, pady=(0, 20))

        list_frame = tk.Frame(self.content_frame, bg=BG_COLOR)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=40)
        unidades = self.admin_controller.get_all_languages().get(lang_id, {}).get("unidades", [])
        for u in unidades:
            row = tk.Frame(list_frame, bg=BG_COLOR)
            row.pack(fill=tk.X, pady=5)
            tk.Label(row, text=f"{u['number']:03d}", font=("Arial", 12), bg=BG_COLOR, fg="#aaaaaa", width=5).pack(side=tk.LEFT)
            tk.Label(row, text=u.get("title", "Unidade"), font=("Arial", 14), bg=BG_COLOR, fg=FG_COLOR).pack(side=tk.LEFT, padx=10)
            tk.Label(row, text=f"{len(u.get('licoes', []))} Lições", font=("Arial", 12), bg=BG_COLOR, fg="#aaaaaa").pack(side=tk.LEFT, padx=20)
            
            def del_cmd(u_num=u['number']):
                if messagebox.askyesno("Confirmar", "Tem certeza que deseja apagar a Unidade e todas as suas lições?"):
                    suc, msg = self.admin_controller.delete_unit(lang_id, u_num)
                    if suc: self.render_unit_list(lang_id, lang_name)
                    else: messagebox.showerror("Erro", msg)
                    
            tk.Button(row, text="Remover", bg="#f44336", fg="white", relief=tk.FLAT, command=del_cmd).pack(side=tk.RIGHT)
            tk.Frame(list_frame, bg="#333333", height=1).pack(fill=tk.X, pady=5)
        tk.Button(self.content_frame, text="Adicionar", font=("Arial", 14), bg=BTN_BG, fg=FG_COLOR, relief=tk.FLAT, command=lambda: self.render_create_unit(lang_id, lang_name)).pack(pady=20, ipady=5, fill=tk.X, padx=80)

    def render_create_unit(self, lang_id, lang_name):
        self.clear_content()
        tk.Label(self.content_frame, text=f"Painel de Admin\nGerenciador de Unidades de {lang_name}", font=("Arial", 16, "bold"), bg=BG_COLOR, fg=FG_COLOR, justify=tk.LEFT).pack(anchor="w", padx=40, pady=30)
        e_nome = self._create_entry(self.content_frame, "Nome")
        f_btns = tk.Frame(self.content_frame, bg=BG_COLOR)
        f_btns.pack(fill=tk.X, pady=40, padx=80)
        tk.Button(f_btns, text="Cancelar", font=("Arial", 12, "bold"), bg=BTN_BG, fg=FG_COLOR, relief=tk.FLAT, command=lambda: self.render_unit_list(lang_id, lang_name)).pack(side=tk.LEFT, ipadx=20, ipady=5)
        def on_add():
            unidades = self.admin_controller.get_all_languages().get(lang_id, {}).get("unidades", [])
            suc, msg = self.admin_controller.add_unit(lang_id, len(unidades)+1, e_nome.get())
            if suc: self.render_unit_list(lang_id, lang_name)
            else: messagebox.showerror("Erro", msg)
        tk.Button(f_btns, text="Adicionar", font=("Arial", 12, "bold"), bg="#4caf50", fg="white", relief=tk.FLAT, command=on_add).pack(side=tk.RIGHT, ipadx=20, ipady=5)

    def render_manage_lessons(self):
        self.clear_content()
        tk.Label(self.content_frame, text="Painel de Admin\nSelecione um Idioma", font=("Arial", 16, "bold"), bg=BG_COLOR, fg=FG_COLOR, justify=tk.LEFT).pack(anchor="w", padx=40, pady=20)
        tk.Button(self.content_frame, text="← Voltar", bg=BTN_BG, fg=FG_COLOR, relief=tk.FLAT, command=self.render_main_menu).pack(anchor="w", padx=40, pady=(0, 20))
        for lang_id, info in self.admin_controller.get_all_languages().items():
            tk.Button(self.content_frame, text=info["name"], font=("Arial", 14), bg=BTN_BG, fg=FG_COLOR, relief=tk.FLAT, command=lambda lid=lang_id, name=info["name"]: self.render_lesson_units_list(lid, name)).pack(fill=tk.X, pady=10, ipady=5, padx=40)

    def render_lesson_units_list(self, lang_id, lang_name):
        self.clear_content()
        tk.Label(self.content_frame, text=f"Painel de Admin\nGerenciador de Lições de {lang_name}", font=("Arial", 16, "bold"), bg=BG_COLOR, fg=FG_COLOR, justify=tk.LEFT).pack(anchor="w", padx=40, pady=20)
        tk.Button(self.content_frame, text="← Voltar", bg=BTN_BG, fg=FG_COLOR, relief=tk.FLAT, command=self.render_manage_lessons).pack(anchor="w", padx=40, pady=(0, 20))
        unidades = self.admin_controller.get_all_languages().get(lang_id, {}).get("unidades", [])
        for u in unidades:
            row = tk.Frame(self.content_frame, bg=BG_COLOR)
            row.pack(fill=tk.X, pady=5, padx=40)
            tk.Label(row, text=f"{u['number']:03d}", font=("Arial", 12), bg=BG_COLOR, fg="#aaaaaa", width=5).pack(side=tk.LEFT)
            tk.Label(row, text=u.get("title", f"Unidade {u['number']}"), font=("Arial", 14), bg=BG_COLOR, fg=FG_COLOR).pack(side=tk.LEFT, padx=10)
            tk.Button(row, text="Selecionar", bg="#2196f3", fg="white", relief=tk.FLAT, command=lambda u_num=u['number']: self.render_lesson_list(lang_id, lang_name, u_num)).pack(side=tk.RIGHT)
            tk.Frame(self.content_frame, bg="#333333", height=1).pack(fill=tk.X, pady=5, padx=40)

    def render_lesson_list(self, lang_id, lang_name, unit_num):
        self.clear_content()
        tk.Label(self.content_frame, text=f"Painel de Admin\nGerenciador de Lições de {lang_name}", font=("Arial", 16, "bold"), bg=BG_COLOR, fg=FG_COLOR, justify=tk.LEFT).pack(anchor="w", padx=40, pady=20)
        tk.Button(self.content_frame, text="← Voltar", bg=BTN_BG, fg=FG_COLOR, relief=tk.FLAT, command=lambda: self.render_lesson_units_list(lang_id, lang_name)).pack(anchor="w", padx=40, pady=(0, 20))

        list_frame = tk.Frame(self.content_frame, bg=BG_COLOR)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=40)
        unidade = next((u for u in self.admin_controller.get_all_languages().get(lang_id, {}).get("unidades", []) if u["number"] == unit_num), {})
        
        for l in unidade.get("licoes", []):
            row = tk.Frame(list_frame, bg=BG_COLOR)
            row.pack(fill=tk.X, pady=5)
            tk.Label(row, text=f"{l['number']:03d}", font=("Arial", 12), bg=BG_COLOR, fg="#aaaaaa", width=5).pack(side=tk.LEFT)
            tk.Label(row, text=l.get("title", f"Lição {l['number']}"), font=("Arial", 14), bg=BG_COLOR, fg=FG_COLOR).pack(side=tk.LEFT, padx=10)
            
            def del_cmd(l_id=l['lessonId']):
                if messagebox.askyesno("Confirmar", "Remover lição?"):
                    suc, msg = self.admin_controller.delete_lesson(lang_id, unit_num, l_id)
                    if suc: self.render_lesson_list(lang_id, lang_name, unit_num)
                    else: messagebox.showerror("Erro", msg)

            tk.Button(row, text="Remover", bg="#f44336", fg="white", relief=tk.FLAT, command=del_cmd).pack(side=tk.RIGHT)
            tk.Frame(list_frame, bg="#333333", height=1).pack(fill=tk.X, pady=5)
        tk.Button(self.content_frame, text="Adicionar", font=("Arial", 14), bg=BTN_BG, fg=FG_COLOR, relief=tk.FLAT, command=lambda: self.render_create_lesson(lang_id, lang_name, unit_num)).pack(pady=20, ipady=5, fill=tk.X, padx=80)

    def render_create_lesson(self, lang_id, lang_name, unit_num):
        self.clear_content()
        tk.Label(self.content_frame, text=f"Painel de Admin\nGerenciador de Lições de {lang_name}", font=("Arial", 16, "bold"), bg=BG_COLOR, fg=FG_COLOR, justify=tk.LEFT).pack(anchor="w", padx=40, pady=30)
        e_nome = self._create_entry(self.content_frame, "Nome da Lição")
        f_btns = tk.Frame(self.content_frame, bg=BG_COLOR)
        f_btns.pack(fill=tk.X, pady=40, padx=80)
        tk.Button(f_btns, text="Cancelar", font=("Arial", 12, "bold"), bg=BTN_BG, fg=FG_COLOR, relief=tk.FLAT, command=lambda: self.render_lesson_list(lang_id, lang_name, unit_num)).pack(side=tk.LEFT, ipadx=20, ipady=5)
        def on_add():
            suc, msg = self.admin_controller.add_lesson(lang_id, unit_num, e_nome.get())
            if suc: self.render_lesson_list(lang_id, lang_name, unit_num)
            else: messagebox.showerror("Erro", msg)
        tk.Button(f_btns, text="Adicionar", font=("Arial", 12, "bold"), bg="#4caf50", fg="white", relief=tk.FLAT, command=on_add).pack(side=tk.RIGHT, ipadx=20, ipady=5)

    def render_manage_exercises(self):
        self.clear_content()
        tk.Label(self.content_frame, text="Painel de Admin\nSelecione um Idioma para Exercícios", font=("Arial", 16, "bold"), bg=BG_COLOR, fg=FG_COLOR, justify=tk.LEFT).pack(anchor="w", padx=40, pady=20)
        tk.Button(self.content_frame, text="← Voltar", bg=BTN_BG, fg=FG_COLOR, relief=tk.FLAT, command=self.render_main_menu).pack(anchor="w", padx=40, pady=(0, 20))
        for lang_id, info in self.admin_controller.get_all_languages().items():
            tk.Button(self.content_frame, text=info["name"], font=("Arial", 14), bg=BTN_BG, fg=FG_COLOR, relief=tk.FLAT, command=lambda lid=lang_id, name=info["name"]: self.render_exercise_units_list(lid, name)).pack(fill=tk.X, pady=10, ipady=5, padx=40)

    def render_exercise_units_list(self, lang_id, lang_name):
        self.clear_content()
        tk.Label(self.content_frame, text=f"Painel de Admin\nSelecione a Unidade", font=("Arial", 16, "bold"), bg=BG_COLOR, fg=FG_COLOR, justify=tk.LEFT).pack(anchor="w", padx=40, pady=20)
        tk.Button(self.content_frame, text="← Voltar", bg=BTN_BG, fg=FG_COLOR, relief=tk.FLAT, command=self.render_manage_exercises).pack(anchor="w", padx=40, pady=(0, 20))
        unidades = self.admin_controller.get_all_languages().get(lang_id, {}).get("unidades", [])
        for u in unidades:
            tk.Button(self.content_frame, text=u.get("title", f"Unidade {u['number']}"), font=("Arial", 14), bg=BTN_BG, fg=FG_COLOR, relief=tk.FLAT, command=lambda u_num=u['number']: self.render_exercise_lessons_list(lang_id, lang_name, u_num)).pack(fill=tk.X, pady=10, ipady=5, padx=40)

    def render_exercise_lessons_list(self, lang_id, lang_name, unit_num):
        self.clear_content()
        tk.Label(self.content_frame, text=f"Painel de Admin\nSelecione a Lição", font=("Arial", 16, "bold"), bg=BG_COLOR, fg=FG_COLOR, justify=tk.LEFT).pack(anchor="w", padx=40, pady=20)
        tk.Button(self.content_frame, text="← Voltar", bg=BTN_BG, fg=FG_COLOR, relief=tk.FLAT, command=lambda: self.render_exercise_units_list(lang_id, lang_name)).pack(anchor="w", padx=40, pady=(0, 20))
        unidade = next((u for u in self.admin_controller.get_all_languages().get(lang_id, {}).get("unidades", []) if u["number"] == unit_num), {})
        for l in unidade.get("licoes", []):
            tk.Button(self.content_frame, text=l.get("title", f"Lição {l['number']}"), font=("Arial", 14), bg=BTN_BG, fg=FG_COLOR, relief=tk.FLAT, command=lambda l_id=l['lessonId']: self.render_exercise_list(lang_id, unit_num, l_id)).pack(fill=tk.X, pady=10, ipady=5, padx=40)

    def render_exercise_list(self, lang_id, unit_num, lesson_id):
        self.clear_content()
        tk.Label(self.content_frame, text="Painel de Admin\nExercícios da Lição", font=("Arial", 16, "bold"), bg=BG_COLOR, fg=FG_COLOR, justify=tk.LEFT).pack(anchor="w", padx=40, pady=20)
        tk.Button(self.content_frame, text="← Voltar", bg=BTN_BG, fg=FG_COLOR, relief=tk.FLAT, command=lambda: self.render_exercise_lessons_list(lang_id, "", unit_num)).pack(anchor="w", padx=40, pady=(0, 20))

        canvas = tk.Canvas(self.content_frame, bg=BG_COLOR, highlightthickness=0)
        scrollbar = tk.Scrollbar(self.content_frame, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=BG_COLOR)
        
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw", width=700)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=40)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        idioma = self.admin_controller.get_all_languages().get(lang_id, {})
        unidade = next((u for u in idioma.get("unidades", []) if u["number"] == unit_num), {})
        licao = next((l for l in unidade.get("licoes", []) if l["lessonId"] == lesson_id), {})
        
        for idx, ex in enumerate(licao.get("exercicios", [])):
            row = tk.Frame(scroll_frame, bg=BG_COLOR)
            row.pack(fill=tk.X, pady=5)
            tk.Label(row, text=f"{idx+1:03d}", font=("Arial", 12), bg=BG_COLOR, fg="#aaaaaa", width=5).pack(side=tk.LEFT)
            tk.Label(row, text=f"Ex {idx+1} ({ex.get('type', 'Novo')})", font=("Arial", 14), bg=BG_COLOR, fg=FG_COLOR).pack(side=tk.LEFT, padx=10)
            
            def del_cmd(e_id=ex['exerciseId']):
                if messagebox.askyesno("Confirmar", "Remover exercício?"):
                    suc, msg = self.admin_controller.delete_exercise(lang_id, unit_num, lesson_id, e_id)
                    if suc: self.render_exercise_list(lang_id, unit_num, lesson_id)
                    else: messagebox.showerror("Erro", msg)
                    
            tk.Button(row, text="Remover", bg="#f44336", fg="white", relief=tk.FLAT, command=del_cmd).pack(side=tk.RIGHT)
            tk.Button(row, text="Editar", bg="#2196f3", fg="white", relief=tk.FLAT, command=lambda ex_id=ex['exerciseId']: self.render_edit_exercise(lang_id, unit_num, lesson_id, ex_id)).pack(side=tk.RIGHT, padx=(0, 10))
            
            tk.Frame(scroll_frame, bg="#333333", height=1).pack(fill=tk.X, pady=5)

        tk.Button(self.content_frame, text="Adicionar Exercícios em Branco", font=("Arial", 14), bg=BTN_BG, fg=FG_COLOR, relief=tk.FLAT, command=lambda: self.render_prompt_exercise_count(lang_id, unit_num, lesson_id)).pack(pady=20, ipady=5, fill=tk.X, padx=80)

    def render_prompt_exercise_count(self, lang_id, unit_num, lesson_id):
        self.clear_content()
        tk.Label(self.content_frame, text="Painel de Admin\nAdicionar exercícios", font=("Arial", 16, "bold"), bg=BG_COLOR, fg=FG_COLOR, justify=tk.LEFT).pack(anchor="w", padx=40, pady=30)
        e_count = self._create_entry(self.content_frame, "Nº de Exercícios (>0)")
        
        f_btns = tk.Frame(self.content_frame, bg=BG_COLOR)
        f_btns.pack(fill=tk.X, pady=40, padx=80)
        tk.Button(f_btns, text="Cancelar", font=("Arial", 12, "bold"), bg=BTN_BG, fg=FG_COLOR, relief=tk.FLAT, command=lambda: self.render_exercise_list(lang_id, unit_num, lesson_id)).pack(side=tk.LEFT, ipadx=20, ipady=5)
        def on_add():
            try: count = int(e_count.get())
            except ValueError: return messagebox.showerror("Erro", "Insira um número inteiro.")
            suc, msg = self.admin_controller.add_blank_exercises(lang_id, unit_num, lesson_id, count)
            if suc: self.render_exercise_list(lang_id, unit_num, lesson_id)
            else: messagebox.showerror("Erro", msg)
        tk.Button(f_btns, text="Adicionar", font=("Arial", 12, "bold"), bg="#4caf50", fg="white", relief=tk.FLAT, command=on_add).pack(side=tk.RIGHT, ipadx=20, ipady=5)

    def render_edit_exercise(self, lang_id, unit_num, lesson_id, ex_id):
        self.clear_content()
        
        canvas = tk.Canvas(self.content_frame, bg=BG_COLOR, highlightthickness=0)
        scrollbar = tk.Scrollbar(self.content_frame, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=BG_COLOR)
        
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw", width=750)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=(40,0))
        scrollbar.pack(side="right", fill="y")

        tk.Label(scroll_frame, text="Painel de Admin\nEditar Exercício", font=("Arial", 16, "bold"), bg=BG_COLOR, fg=FG_COLOR, justify=tk.LEFT).pack(anchor="w", pady=20)
        
        idioma = self.admin_controller.get_all_languages().get(lang_id, {})
        unidade = next((u for u in idioma.get("unidades", []) if u["number"] == unit_num), {})
        licao = next((l for l in unidade.get("licoes", []) if l["lessonId"] == lesson_id), {})
        ex_data = next((e for e in licao.get("exercicios", []) if e["exerciseId"] == ex_id), {})

        f_ex = tk.Frame(scroll_frame, bg=BG_COLOR)
        f_ex.pack(fill=tk.BOTH, expand=True, pady=10)
        
        tk.Label(f_ex, text="Selecione o Tipo de Exercício (Dropdown):", font=("Arial", 12), bg=BG_COLOR, fg=FG_COLOR).pack(anchor="w")
        self.cb_type = ttk.Combobox(f_ex, state="readonly", font=("Arial", 14), values=["ExercicioTraducao", "ExercicioAlternativas", "ExercicioCombinar", "ExercicioGramatica", "RevisaoVocabulario"])     
        self.cb_type.pack(fill=tk.X, pady=5)
        self.cb_type.bind("<<ComboboxSelected>>", self._update_dynamic_form)

        tk.Label(f_ex, text="Título (ex: Tradução Direta):", font=("Arial", 12), bg=BG_COLOR, fg=FG_COLOR).pack(anchor="w", pady=(10,0))
        self.e_title = tk.Entry(f_ex, font=("Arial", 14), bg=INPUT_BG, fg=FG_COLOR, relief=tk.FLAT)
        self.e_title.insert(0, ex_data.get("exerciseTitle", ""))
        self.e_title.pack(fill=tk.X, pady=5, ipady=5)

        tk.Label(f_ex, text="Enunciado / Texto Principal:", font=("Arial", 12), bg=BG_COLOR, fg=FG_COLOR).pack(anchor="w", pady=(10,0))
        self.e_front = tk.Entry(f_ex, font=("Arial", 14), bg=INPUT_BG, fg=FG_COLOR, relief=tk.FLAT)
        self.e_front.insert(0, ex_data.get("frontText", ""))
        self.e_front.pack(fill=tk.X, pady=5, ipady=5)

        self.dynamic_frame = tk.Frame(f_ex, bg=BG_COLOR)
        self.dynamic_frame.pack(fill=tk.X, pady=15)
        
        # Inicia o formulário com o tipo selecionado
        self._update_dynamic_form(None, ex_data)

        f_bottom = tk.Frame(scroll_frame, bg=BG_COLOR)
        f_bottom.pack(fill=tk.X, pady=20)
        tk.Button(f_bottom, text="Cancelar", font=("Arial", 12, "bold"), bg=BTN_BG, fg=FG_COLOR, relief=tk.FLAT, command=lambda: self.render_exercise_list(lang_id, unit_num, lesson_id)).pack(side=tk.LEFT, ipadx=20, ipady=5)
        
        def on_save():
            ex_type = self.cb_type.get()
            specific_data = {}
            if ex_type == "ExercicioTraducao":
                specific_data["translations"] = [t.strip() for t in self.dynamic_widgets["translations"].get().split(",") if t.strip()]
            elif ex_type == "ExercicioAlternativas":
                specific_data["correct_idx"] = self.dynamic_widgets["correct_idx"].get()
                specific_data["alts"] = [e.get().strip() for e in self.dynamic_widgets["alts"]]
            elif ex_type == "ExercicioCombinar":
                specific_data["pairs"] = [(e1.get().strip(), e2.get().strip()) for e1, e2 in self.dynamic_widgets["pairs"]]
            elif ex_type == "ExercicioGramatica":
                specific_data["gram_point"] = self.dynamic_widgets["gram_point"].get().strip()
                specific_data["gram_desc"] = self.dynamic_widgets["gram_desc"].get().strip()
            elif ex_type == "ExercicioGramatica":
                specific_data["gram_point"] = self.dynamic_widgets["gram_point"].get().strip()
                specific_data["gram_desc"] = self.dynamic_widgets["gram_desc"].get().strip()
            elif ex_type == "RevisaoVocabulario":
                specific_data["back_text"] = self.dynamic_widgets["back_text"].get().strip()
                
            suc, msg = self.admin_controller.update_exercise(lang_id, unit_num, lesson_id, ex_id, ex_type, self.e_title.get(), self.e_front.get(), specific_data)
            if suc: self.render_exercise_list(lang_id, unit_num, lesson_id)
            else: messagebox.showerror("Erro", msg)

        tk.Button(f_bottom, text="Salvar Modificações", font=("Arial", 12, "bold"), bg="#4caf50", fg="white", relief=tk.FLAT, command=on_save).pack(side=tk.RIGHT, ipadx=20, ipady=5)

    def _update_dynamic_form(self, event=None, initial_data=None):
        for widget in self.dynamic_frame.winfo_children(): widget.destroy()
        self.dynamic_widgets.clear()
        ex_type = self.cb_type.get()
        if initial_data is None: initial_data = {}
        
        if ex_type == "ExercicioTraducao":
            tk.Label(self.dynamic_frame, text="Respostas corretas (separadas por vírgula):", font=("Arial", 12), bg=BG_COLOR, fg=FG_COLOR).pack(anchor="w")
            e = tk.Entry(self.dynamic_frame, font=("Arial", 14), bg=INPUT_BG, fg=FG_COLOR, relief=tk.FLAT)
            e.insert(0, ", ".join(initial_data.get("correctTexts", [])))
            e.pack(fill=tk.X, ipady=5)
            self.dynamic_widgets["translations"] = e
            
        elif ex_type == "ExercicioAlternativas":
            tk.Label(self.dynamic_frame, text="Alternativas (Selecione a correta no botão lateral):", font=("Arial", 12), bg=BG_COLOR, fg=FG_COLOR).pack(anchor="w")
            self.dynamic_widgets["correct_idx"] = tk.IntVar(value=0)
            self.dynamic_widgets["alts"] = []
            alts_data = initial_data.get("alternativas", [])
            for i in range(4):
                row = tk.Frame(self.dynamic_frame, bg=BG_COLOR)
                row.pack(fill=tk.X, pady=2)
                tk.Radiobutton(row, variable=self.dynamic_widgets["correct_idx"], value=i, bg=BG_COLOR, selectcolor=BTN_BG).pack(side=tk.LEFT)
                e = tk.Entry(row, font=("Arial", 14), bg=INPUT_BG, fg=FG_COLOR, relief=tk.FLAT)
                if i < len(alts_data): 
                    e.insert(0, alts_data[i].get("text", ""))
                    if alts_data[i].get("correct"): self.dynamic_widgets["correct_idx"].set(i)
                e.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
                self.dynamic_widgets["alts"].append(e)
                
        elif ex_type == "ExercicioCombinar":
            tk.Label(self.dynamic_frame, text="Pares (Coluna Esquerda - Coluna Direita):", font=("Arial", 12), bg=BG_COLOR, fg=FG_COLOR).pack(anchor="w")
            self.dynamic_widgets["pairs"] = []
            pares_data = initial_data.get("pares", [])
            for i in range(4):
                row = tk.Frame(self.dynamic_frame, bg=BG_COLOR)
                row.pack(fill=tk.X, pady=2)
                e1 = tk.Entry(row, font=("Arial", 14), bg=INPUT_BG, fg=FG_COLOR, relief=tk.FLAT)
                e2 = tk.Entry(row, font=("Arial", 14), bg=INPUT_BG, fg=FG_COLOR, relief=tk.FLAT)
                if i < len(pares_data):
                    e1.insert(0, pares_data[i]["first"]["text"])
                    e2.insert(0, pares_data[i]["second"]["text"])
                e1.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5), ipady=5)
                e2.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
                self.dynamic_widgets["pairs"].append((e1, e2))
                
        elif ex_type == "ExercicioGramatica":
            gram_data = initial_data.get("pontosGramaticais", [{}])[0]
            tk.Label(self.dynamic_frame, text="Tópico Gramatical:", font=("Arial", 12), bg=BG_COLOR, fg=FG_COLOR).pack(anchor="w")
            e1 = tk.Entry(self.dynamic_frame, font=("Arial", 14), bg=INPUT_BG, fg=FG_COLOR, relief=tk.FLAT)
            e1.insert(0, gram_data.get("point", ""))
            e1.pack(fill=tk.X, pady=2, ipady=5)
            
            tk.Label(self.dynamic_frame, text="Descrição da Regra:", font=("Arial", 12), bg=BG_COLOR, fg=FG_COLOR).pack(anchor="w")
            e2 = tk.Entry(self.dynamic_frame, font=("Arial", 14), bg=INPUT_BG, fg=FG_COLOR, relief=tk.FLAT)
            e2.insert(0, gram_data.get("description", ""))
            e2.pack(fill=tk.X, pady=2, ipady=5)
            self.dynamic_widgets["gram_point"] = e1
            self.dynamic_widgets["gram_desc"] = e2

        elif ex_type == "RevisaoVocabulario":
            tk.Label(self.dynamic_frame, text="Verso do Cartão (Resposta):", font=("Arial", 12), bg=BG_COLOR, fg=FG_COLOR).pack(anchor="w")
            e = tk.Entry(self.dynamic_frame, font=("Arial", 14), bg=INPUT_BG, fg=FG_COLOR, relief=tk.FLAT)
            e.insert(0, initial_data.get("backText", ""))
            e.pack(fill=tk.X, ipady=5)
            self.dynamic_widgets["back_text"] = e