import tkinter as tk
from tkinter import messagebox
from src.controllers.social_controller import SocialController

BG_COLOR = "#2d2d2d"
FG_COLOR = "#ffffff"
BTN_BG = "#404040"
BTN_FG = "#ffffff"
FONT_TITLE = ("Arial", 20, "bold")
FONT_TEXT = ("Arial", 12)

class SocialView(tk.Frame):
    def __init__(self, parent, app_window, social_controller: SocialController):
        super().__init__(parent, bg=BG_COLOR)
        self.app_window = app_window
        self.social_controller = social_controller
        self.current_user = app_window.auth_controller.current_user
        
        self.pack(fill=tk.BOTH, expand=True)
        self.render_header()
        
        # Abas de Navegação (Agora com 3 opções)
        nav_frame = tk.Frame(self, bg=BG_COLOR)
        nav_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(nav_frame, text="Ranking Global", font=("Arial", 11, "bold"), bg=BTN_BG, fg=BTN_FG, relief=tk.FLAT, command=self.render_global_ranking).pack(side=tk.LEFT, padx=10, expand=True, fill=tk.X)
        tk.Button(nav_frame, text="Ranking de Amigos", font=("Arial", 11, "bold"), bg=BTN_BG, fg=BTN_FG, relief=tk.FLAT, command=self.render_friends_ranking).pack(side=tk.LEFT, padx=10, expand=True, fill=tk.X)
        tk.Button(nav_frame, text="Gerenciar Amigos", font=("Arial", 11, "bold"), bg=BTN_BG, fg=BTN_FG, relief=tk.FLAT, command=self.render_friends).pack(side=tk.LEFT, padx=10, expand=True, fill=tk.X)
        
        self.content_frame = tk.Frame(self, bg=BG_COLOR)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.render_global_ranking()

    def render_header(self):
        header = tk.Frame(self, bg="#1e1e1e", height=60)
        header.pack(fill=tk.X)
        tk.Button(header, text="← Voltar", bg=BTN_BG, fg=BTN_FG, font=("Arial", 12), relief=tk.FLAT, 
                  command=self.app_window.show_dashboard).pack(side=tk.LEFT, padx=20, pady=15)
        tk.Label(header, text="Comunidade & Ranking", font=("Arial", 16, "bold"), bg="#1e1e1e", fg=FG_COLOR).pack(side=tk.LEFT, padx=20, pady=15)

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def _build_ranking_list(self, title, ranking_data):
        self.clear_content()
        tk.Label(self.content_frame, text=title, font=FONT_TITLE, bg=BG_COLOR, fg="#ffc107").pack(pady=(0, 20))
        
        if not ranking_data:
            tk.Label(self.content_frame, text="Nenhum dado encontrado para o ranking.", font=FONT_TEXT, bg=BG_COLOR, fg=FG_COLOR).pack()
            return
            
        list_frame = tk.Frame(self.content_frame, bg=BG_COLOR)
        list_frame.pack(fill=tk.BOTH, expand=True)

        for pos, aluno_data in enumerate(ranking_data, start=1):
            cor_fundo = "#3a3a3a" if pos % 2 == 0 else "#2d2d2d"
            row = tk.Frame(list_frame, bg=cor_fundo)
            row.pack(fill=tk.X, pady=2)
            
            is_me = self.current_user and self.current_user.username == aluno_data["username"]
            cor_texto = "#4caf50" if is_me else FG_COLOR
            sufixo = " (Você)" if is_me else ""
            
            tk.Label(row, text=f"#{pos}", font=("Arial", 14, "bold"), bg=cor_fundo, fg="#aaaaaa", width=4).pack(side=tk.LEFT, pady=10)
            tk.Label(row, text=f"{aluno_data['username']}{sufixo}", font=("Arial", 14, "bold"), bg=cor_fundo, fg=cor_texto).pack(side=tk.LEFT, padx=10, pady=10)
            tk.Label(row, text=f"🔥 {aluno_data['streak']} dias", font=("Arial", 14, "bold"), bg=cor_fundo, fg="#ff9800").pack(side=tk.RIGHT, padx=20, pady=10)

    def render_global_ranking(self):
        ranking = self.social_controller.get_global_ranking()
        self._build_ranking_list("🌍 Ranking Global", ranking)

    def render_friends_ranking(self):
        ranking = self.social_controller.get_friends_ranking(self.current_user.userId)
        self._build_ranking_list("👥 Ranking de Amigos", ranking)

    def render_friends(self):
        self.clear_content()
        
        # Formulário para adicionar amigo
        add_frame = tk.Frame(self.content_frame, bg="#333333", padx=15, pady=15)
        add_frame.pack(fill=tk.X, pady=(0, 20))
        tk.Label(add_frame, text="Adicionar Amigo pelo Nome de Usuário", font=("Arial", 14, "bold"), bg="#333333", fg=FG_COLOR).pack(anchor="w", pady=(0, 10))
        
        input_frame = tk.Frame(add_frame, bg="#333333")
        input_frame.pack(fill=tk.X)
        entry_user = tk.Entry(input_frame, font=FONT_TEXT, bg="#1e1e1e", fg=FG_COLOR, insertbackground=FG_COLOR, relief=tk.FLAT)
        entry_user.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10), ipady=5)
        tk.Button(input_frame, text="Enviar Pedido", font=FONT_TEXT, bg="#2196f3", fg="white", relief=tk.FLAT,
                  command=lambda: self.handle_add_friend(entry_user.get())).pack(side=tk.RIGHT, ipadx=10)

        tk.Label(self.content_frame, text="Meus Amigos", font=("Arial", 14, "bold"), bg=BG_COLOR, fg="#4caf50").pack(anchor="w", pady=(10, 5))
        
        amigos_atuais = self.social_controller.get_current_friends(self.current_user.userId)
        if not amigos_atuais:
            tk.Label(self.content_frame, text="Você ainda não tem amigos adicionados.", font=FONT_TEXT, bg=BG_COLOR, fg="#aaaaaa").pack(anchor="w")
        else:
            for amigo in amigos_atuais:
                f_frame = tk.Frame(self.content_frame, bg="#3a3a3a")
                f_frame.pack(fill=tk.X, pady=2)
                tk.Label(f_frame, text=f"👤 {amigo['username']}", font=("Arial", 12, "bold"), bg="#3a3a3a", fg=FG_COLOR).pack(side=tk.LEFT, padx=15, pady=10)
                tk.Button(f_frame, text="Remover", bg="#f44336", fg="white", font=("Arial", 10, "bold"), relief=tk.FLAT, 
                          command=lambda fid=amigo['id']: self.handle_remove_friend(fid)).pack(side=tk.RIGHT, padx=10, pady=5)

        # Pedidos Pendentes
        tk.Label(self.content_frame, text="Pedidos Pendentes", font=("Arial", 14, "bold"), bg=BG_COLOR, fg="#ffeb3b").pack(anchor="w", pady=(10, 5))
        
        # Agora buscamos do banco de dados atualizado para evitar problemas de sincronia
        pedidos = self.social_controller.get_pending_requests_with_names(self.current_user.userId)
        
        if not pedidos:
            tk.Label(self.content_frame, text="Nenhum pedido pendente.", font=FONT_TEXT, bg=BG_COLOR, fg="#aaaaaa").pack(anchor="w")
        else:
            for pedido in pedidos:
                req_frame = tk.Frame(self.content_frame, bg="#3a3a3a")
                req_frame.pack(fill=tk.X, pady=2)
                
                # Exibe o Nome de Usuário em vez do ID!
                tk.Label(req_frame, text=f"Pedido de: {pedido['senderUsername']}", font=("Arial", 12, "bold"), bg="#3a3a3a", fg=FG_COLOR).pack(side=tk.LEFT, padx=15, pady=10)
                
                # Botões Aceitar e Recusar
                tk.Button(req_frame, text="Recusar", bg="#f44336", fg="white", font=("Arial", 10, "bold"), relief=tk.FLAT, 
                          command=lambda sid=pedido['senderId']: self.handle_reject_friend(sid)).pack(side=tk.RIGHT, padx=10, pady=5)
                tk.Button(req_frame, text="Aceitar", bg="#4caf50", fg="white", font=("Arial", 10, "bold"), relief=tk.FLAT, 
                          command=lambda sid=pedido['senderId']: self.handle_accept_friend(sid)).pack(side=tk.RIGHT, padx=5, pady=5)

    def handle_add_friend(self, username):
        if not username: return
        sucesso, msg = self.social_controller.send_friend_request(self.current_user.userId, username)
        if sucesso:
            messagebox.showinfo("Sucesso", msg)
            self.render_friends()
        else:
            messagebox.showwarning("Atenção", msg)

    def handle_remove_friend(self, friend_id):
        if messagebox.askyesno("Confirmar", "Tem certeza que deseja desfazer esta amizade?"):
            sucesso, msg = self.social_controller.remove_friend(self.current_user.userId, friend_id)
            if sucesso:
                messagebox.showinfo("Sucesso", msg)
                self.render_friends()
            else:
                messagebox.showerror("Erro", msg)

    def handle_accept_friend(self, sender_id):
        sucesso, msg = self.social_controller.accept_friend_request(self.current_user.userId, sender_id)
        if sucesso:
            messagebox.showinfo("Sucesso", msg)
            self.render_friends() # Ao atualizar a tela, o pedido já sumirá
        else:
            messagebox.showerror("Erro", msg)

    def handle_reject_friend(self, sender_id):
        sucesso, msg = self.social_controller.reject_friend_request(self.current_user.userId, sender_id)
        if sucesso:
            messagebox.showinfo("Sucesso", msg)
            self.render_friends() # Atualiza a tela e o pedido some
        else:
            messagebox.showerror("Erro", msg)