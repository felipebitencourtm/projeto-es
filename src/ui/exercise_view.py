import tkinter as tk
from tkinter import ttk, messagebox
import random
from src.controllers.study_controller import StudyController

BG_COLOR = "#2d2d2d"
FG_COLOR = "#ffffff"
BTN_BG = "#3a3a3a"
BTN_ACTIVE = "#4a4a4a"
INPUT_BG = "#1e1e1e"

class ExerciseView(tk.Frame):
    def __init__(self, parent, controller: StudyController):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller
        self.show_completion_screen = None # Inicializa a variável para evitar o AttributeError
        self.pack(fill=tk.BOTH, expand=True)
        
        self.answer_str = tk.StringVar()
        self.comboboxes = [] 
        
        self.render_exercise()

    def clear_view(self):
        for widget in self.winfo_children(): widget.destroy()
        self.answer_str.set("")
        self.comboboxes.clear()

    def render_exercise(self):
        self.clear_view()
        ex = self.controller.get_current_exercise()
        
        if not ex:
            if self.show_completion_screen:
                self.show_completion_screen()
            return

        # BARRA SUPERIOR
        top_bar = tk.Frame(self, bg=BG_COLOR)
        top_bar.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        tk.Label(top_bar, text=ex.get("exerciseTitle", "Exercício"), font=("Arial", 12), bg=BG_COLOR, fg="#aaaaaa").pack(side=tk.LEFT)
        
        if self.controller.current_lesson.get("title", "").startswith("Revisão"):
            # O lambda adia a execução e avaliação até o botão ser clicado
            tk.Button(top_bar, text="Sair (Salva Progresso)", font=("Arial", 10, "bold"), bg="#f44336", fg="white", relief=tk.FLAT, command=lambda: self.show_completion_screen() if self.show_completion_screen else None).pack(side=tk.RIGHT)

        tk.Label(self, text=ex.get("frontText", ""), font=("Arial", 22, "bold"), bg=BG_COLOR, fg=FG_COLOR, wraplength=600).pack(pady=(20, 40))

        f_content = tk.Frame(self, bg=BG_COLOR)
        f_content.pack(fill=tk.BOTH, expand=True, padx=40)
        
        self.f_bottom = tk.Frame(self, bg=BG_COLOR)
        self.f_bottom.pack(fill=tk.X, side=tk.BOTTOM, pady=20, padx=20)

        ex_type = ex.get("type")

        # 1. FLASHCARDS
        if ex_type == "RevisaoVocabulario":
            self.back_text = ex.get("backText", "")
            self.ans_label = tk.Label(f_content, text="???", font=("Arial", 18, "bold"), bg=BG_COLOR, fg="#555555")
            self.ans_label.pack(pady=40)
            
            self.btn_reveal = tk.Button(self.f_bottom, text="Mostrar Resposta", font=("Arial", 14, "bold"), bg="#2196f3", fg="white", relief=tk.FLAT, command=self._reveal_flashcard)
            self.btn_reveal.pack(fill=tk.X, ipady=10, padx=40)
            return

        # 2. TRADUÇÃO
        elif ex_type == "ExercicioTraducao":
            entry = tk.Entry(f_content, textvariable=self.answer_str, font=("Arial", 16), bg=BG_COLOR, fg=FG_COLOR, insertbackground=FG_COLOR, relief=tk.FLAT, justify=tk.CENTER)
            entry.pack(fill=tk.X, pady=20)
            tk.Frame(f_content, bg="#555555", height=1).pack(fill=tk.X, padx=50)
            entry.focus()

        # 3. ALTERNATIVAS
        elif ex_type in ["ExercicioAlternativas", "RevisaoAlternativas"]:
            alts = ex.get("alternativas", [])
            random.shuffle(alts)
            grid_frame = tk.Frame(f_content, bg=BG_COLOR)
            grid_frame.pack()
            for idx, alt in enumerate(alts):
                tk.Radiobutton(grid_frame, text=alt.get("text"), variable=self.answer_str, value=alt.get("id"),
                               font=("Arial", 12), bg=BTN_BG, fg=FG_COLOR, selectcolor="#4caf50", 
                               indicatoron=False, width=20, height=3, relief=tk.FLAT, activebackground=BTN_ACTIVE, activeforeground=FG_COLOR).grid(row=idx//2, column=idx%2, padx=10, pady=10)

        # 4. COMBINAR
        elif ex_type == "ExercicioCombinar":
            pares = ex.get("pares", [])
            opcoes_direita = [p["second"]["text"] for p in pares]
            random.shuffle(opcoes_direita)
            for p in pares:
                row = tk.Frame(f_content, bg=BG_COLOR)
                row.pack(pady=8)
                tk.Label(row, text=p["first"]["text"], font=("Arial", 12), bg=BTN_BG, fg=FG_COLOR, width=25, height=2, relief=tk.FLAT).pack(side=tk.LEFT, padx=(0, 10))
                cb = ttk.Combobox(row, values=opcoes_direita, state="readonly", font=("Arial", 12), width=23)
                cb.pack(side=tk.LEFT, fill=tk.Y)
                self.comboboxes.append((p["first"]["text"], cb))

        # 5. GRAMÁTICA
        elif ex_type == "ExercicioGramatica":
            tk.Label(f_content, text=ex.get("pontosGramaticais", [{}])[0].get("description", ""), font=("Arial", 16), bg=BG_COLOR, fg="#aaaaaa", wraplength=500).pack(pady=20)

        btn_text = "Próximo" if ex_type == "ExercicioGramatica" else "Confirmar"
        tk.Button(self.f_bottom, text=btn_text, font=("Arial", 12, "bold"), bg="#4caf50", fg="white", relief=tk.FLAT, command=self.handle_verify).pack(ipadx=40, ipady=10)

    def _reveal_flashcard(self):
        self.ans_label.config(text=self.back_text, fg=FG_COLOR)
        self.btn_reveal.destroy()
        
        tk.Button(self.f_bottom, text="Errei (0)", bg="#f44336", fg="white", font=("Arial", 12, "bold"), command=lambda: self._handle_flashcard_grade(0)).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5, ipady=10)
        tk.Button(self.f_bottom, text="Bom (1)", bg="#ff9800", fg="white", font=("Arial", 12, "bold"), command=lambda: self._handle_flashcard_grade(1)).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5, ipady=10)
        tk.Button(self.f_bottom, text="Fácil (2)", bg="#4caf50", fg="white", font=("Arial", 12, "bold"), command=lambda: self._handle_flashcard_grade(2)).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5, ipady=10)

    def _handle_flashcard_grade(self, quality: int):
        self.controller.verify_answer(None, quality=quality)
        self.controller.next_exercise()
        self.render_exercise()

    def handle_verify(self):
        ex_type = self.controller.get_current_exercise().get("type")
        
        if ex_type == "ExercicioCombinar":
            user_ans = {esq: cb.get() for esq, cb in self.comboboxes}
            if any(not val for val in user_ans.values()):
                messagebox.showwarning("Aviso", "Combine todas as opções.")
                return
        elif ex_type == "ExercicioGramatica":
            user_ans = True
        else:
            user_ans = self.answer_str.get()
            if not user_ans: return

        is_correct = self.controller.verify_answer(user_ans)
        
        if ex_type != "ExercicioGramatica":
            if not is_correct:
                messagebox.showerror("Incorreto", "A resposta não está correta.")
                return 

        self.controller.next_exercise()
        self.render_exercise()