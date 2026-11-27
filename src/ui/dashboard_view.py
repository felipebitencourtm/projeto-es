import tkinter as tk
from src.controllers.auth_controller import AuthController

BG_COLOR = "#2d2d2d"
FG_COLOR = "#ffffff"
BTN_BG = "#404040"
BTN_FG = "#ffffff"
FONT_TITLE = ("Arial", 20, "bold")
FONT_TEXT = ("Arial", 14)

class DashboardView(tk.Frame):
    def __init__(self, parent, app_window, initial_lang_id: str = None):
        super().__init__(parent, bg=BG_COLOR)
        self.app_window = app_window
        self.auth_controller = app_window.auth_controller
        self.course_repo = app_window.study_controller.course_repo
        
        self.pack(fill=tk.BOTH, expand=True)
        self.render_header()
        
        self.content_frame = tk.Frame(self, bg=BG_COLOR)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        idiomas = self.course_repo.read_data().get("idiomas", {})
        if initial_lang_id and initial_lang_id in idiomas:
            self.render_lessons(initial_lang_id, idiomas[initial_lang_id])
        else:
            self.render_languages()

    def render_header(self):
        header = tk.Frame(self, bg="#1e1e1e", height=60)
        header.pack(fill=tk.X)
        
        user = self.auth_controller.current_user
        username = user.username if user else "Visitante"
        streak = user.streak if user and hasattr(user, 'streak') else 0

        tk.Label(header, text=f"👤 {username}", font=("Arial", 14, "bold"), bg="#1e1e1e", fg=FG_COLOR).pack(side=tk.LEFT, padx=20, pady=15)
        tk.Button(header, text="🏆 Ranking & Amigos", font=("Arial", 10, "bold"), bg="#2196f3", fg="white", relief=tk.FLAT, command=self.app_window.show_social).pack(side=tk.LEFT, padx=10, pady=15)
        tk.Button(header, text="⚙️ Opções", font=("Arial", 10, "bold"), bg=BTN_BG, fg="white", relief=tk.FLAT, command=self.app_window.show_options).pack(side=tk.RIGHT, padx=20, pady=15)
        tk.Label(header, text=f"🔥 {streak} Dias", font=("Arial", 14, "bold"), bg="#1e1e1e", fg="#ff9800").pack(side=tk.RIGHT, padx=20, pady=15)

    def render_languages(self):
        self.clear_content()
        tk.Label(self.content_frame, text="Idiomas", font=FONT_TITLE, bg=BG_COLOR, fg=FG_COLOR).pack(anchor="w", pady=(0, 20))
        
        idiomas = self.course_repo.read_data().get("idiomas", {})
        if not idiomas:
            tk.Label(self.content_frame, text="Nenhum idioma disponível no sistema.", font=FONT_TEXT, bg=BG_COLOR, fg=FG_COLOR).pack()
            return

        for lang_id, lang_info in idiomas.items():
            frame_btn = tk.Frame(self.content_frame, bg=BTN_BG)
            frame_btn.pack(fill=tk.X, pady=5)
            tk.Button(frame_btn, text=f"{lang_info['name']}", font=FONT_TEXT, bg=BTN_BG, fg=BTN_FG, relief=tk.FLAT, anchor="w", command=lambda l_id=lang_id, l_info=lang_info: self.render_lessons(l_id, l_info)).pack(fill=tk.X, ipady=15, padx=20)

    def render_lessons(self, lang_id, lang_info):
        self.clear_content()
        
        top_frame = tk.Frame(self.content_frame, bg=BG_COLOR)
        top_frame.pack(fill=tk.X, pady=(0, 20))
        tk.Button(top_frame, text="← Voltar", bg=BTN_BG, fg=BTN_FG, font=("Arial", 12), relief=tk.FLAT, command=self.render_languages).pack(side=tk.LEFT)
        tk.Label(top_frame, text=lang_info["name"], font=FONT_TITLE, bg=BG_COLOR, fg=FG_COLOR).pack(side=tk.LEFT, padx=20)

        # Botões Separados para as Revisões
        due_ids = self.auth_controller.get_due_reviews(lang_id)
        grammar_due, vocab_due = self.app_window.study_controller.get_categorized_reviews(lang_id, due_ids)        
        if grammar_due:
            tk.Button(top_frame, text=f"🔄 Gramática ({len(grammar_due)})", bg="#2196f3", fg="white", font=("Arial", 12, "bold"), relief=tk.FLAT, command=lambda: self.app_window.start_review_flow(lang_id, "Revisão de Gramática", grammar_due)).pack(side=tk.RIGHT, padx=5)
            
        if vocab_due:
            tk.Button(top_frame, text=f"🎴 Vocabulário ({len(vocab_due)})", bg="#ff9800", fg="white", font=("Arial", 12, "bold"), relief=tk.FLAT, command=lambda: self.app_window.start_review_flow(lang_id, "Revisão de Vocabulário", vocab_due)).pack(side=tk.RIGHT, padx=5)

        # (O resto do código permanece idêntico, iterando sobre as unidades)
        unidades = lang_info.get("unidades", [])
        
        # Mapear ordem global para dependências
        ordered_lessons = []
        for u in unidades:
            for l in u.get("licoes", []): ordered_lessons.append(l["lessonId"])

        # Referência ao Progresso Oficial do UML
        user_progress = getattr(self.auth_controller.current_user, 'progress', {}).get(lang_id)

        canvas = tk.Canvas(self.content_frame, bg=BG_COLOR, highlightthickness=0)
        scrollbar = tk.Scrollbar(self.content_frame, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=BG_COLOR)
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw", width=750)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        for unidade in unidades:
            tk.Label(scroll_frame, text=f"Unidade {unidade['number']}: {unidade.get('title', '')}", font=("Arial", 16, "bold"), bg=BG_COLOR, fg="#4caf50").pack(anchor="w", pady=(15, 5))
            
            for licao in unidade.get("licoes", []):
                l_id = licao["lessonId"]
                licao_frame = tk.Frame(scroll_frame, bg=BTN_BG)
                licao_frame.pack(fill=tk.X, pady=2)
                
                # Validação de Bloqueio Linear no modelo oficial
                is_completed = False
                if user_progress and l_id in user_progress.licoes:
                    is_completed = user_progress.licoes[l_id].complete
                
                global_idx = ordered_lessons.index(l_id)
                if global_idx == 0:
                    is_unlocked = True
                else:
                    prev_l_id = ordered_lessons[global_idx - 1]
                    is_unlocked = (user_progress is not None and prev_l_id in user_progress.licoes and user_progress.licoes[prev_l_id].complete)

                if is_completed: status, color = "✅ Concluída", "#4caf50"
                elif is_unlocked: status, color = "🔓 Desbloqueada", "#2196f3"
                else: status, color = "🔒 Bloqueada", "#555555"

                tk.Label(licao_frame, text=f"Lição {licao['number']} - {status}", font=FONT_TEXT, bg=BTN_BG, fg=BTN_FG).pack(side=tk.LEFT, padx=20, pady=10)
                
                if is_unlocked or is_completed:
                    tk.Button(licao_frame, text="Iniciar", font=("Arial", 12, "bold"), bg=color, fg="white", relief=tk.FLAT, command=lambda u_num=unidade['number'], lid=l_id: self.app_window.start_lesson_flow(lang_id, u_num, lid)).pack(side=tk.RIGHT, padx=20, pady=10)
                else:
                    tk.Label(licao_frame, text="Indisponível", font=("Arial", 12, "bold"), bg=BTN_BG, fg="#888888").pack(side=tk.RIGHT, padx=20, pady=10)

    def clear_content(self):
        for widget in self.content_frame.winfo_children(): widget.destroy()