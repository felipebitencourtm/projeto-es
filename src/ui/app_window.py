import tkinter as tk
from src.controllers.auth_controller import AuthController
from src.controllers.study_controller import StudyController
from src.controllers.social_controller import SocialController
from src.ui.login_view import LoginView
from src.ui.exercise_view import ExerciseView
from src.ui.dashboard_view import DashboardView
from src.ui.social_view import SocialView
from src.models.profile import Admin
from src.controllers.admin_controller import AdminController
from src.ui.admin_view import AdminView
from src.ui.options_view import OptionsView

class AppWindow(tk.Tk):
    def __init__(self, auth_controller: AuthController, study_controller: StudyController, social_controller: SocialController, admin_controller: AdminController):
        super().__init__()
        self.title("KoiLingo")
        self.geometry("800x600")
        self.configure(bg="#2d2d2d")

        self.auth_controller = auth_controller
        self.study_controller = study_controller
        self.social_controller = social_controller
        self.admin_controller = admin_controller

        self.current_view = None
        self.show_login()

    def show_options(self):
        self.switch_view(OptionsView, app_window=self)

    def switch_view(self, view_class, **kwargs):
        if self.current_view is not None:
            self.current_view.destroy()
        
        self.current_view = view_class(self, **kwargs)
        self.current_view.pack(fill=tk.BOTH, expand=True)

    def show_login(self):
        self.switch_view(LoginView, auth_controller=self.auth_controller, on_success_callback=self.show_dashboard)

    def show_dashboard(self):
        if isinstance(self.auth_controller.current_user, Admin):
            self.switch_view(AdminView, app_window=self, admin_controller=self.admin_controller)
        else:
            self.switch_view(DashboardView, app_window=self)
        
    def show_social(self):
        self.switch_view(SocialView, app_window=self, social_controller=self.social_controller)

    def start_lesson_flow(self, lang_id: str, unit_number: int, lesson_id: str):
        sucesso = self.study_controller.start_lesson(lang_id, unit_number, lesson_id)
        if sucesso:
            self.switch_view(ExerciseView, controller=self.study_controller)
            
            def custom_completion():
                self.auth_controller.register_study_activity()
                self.auth_controller.mark_lesson_completed(lang_id, lesson_id)
                
                # 1. Atualiza Flashcards de Vocabulário feitos DURANTE esta lição (caso o admin tenha colocado na lição)
                for ex_id, quality in self.study_controller.session_results:
                    self.auth_controller.update_srs(lang_id, ex_id, quality)
                    
                # 2. Clona e insere todos os ExercicioAlternativas da lição na fila SRS (Gramática)
                for ex in self.study_controller.current_lesson.get("exercicios", []):
                    if ex.get("type") == "ExercicioAlternativas":
                        self.auth_controller.enroll_in_srs(lang_id, f"alt_{ex['exerciseId']}")
                
                self.current_view.clear_view()
                tk.Label(self.current_view, text="Lição Concluída!", font=("Arial", 24, "bold"), bg="#2d2d2d", fg="#4caf50").pack(pady=50)
                tk.Button(self.current_view, text="Voltar ao Menu", font=("Arial", 14), bg="#404040", fg="white", command=self.show_dashboard, relief=tk.FLAT).pack(pady=30)
                
            self.current_view.show_completion_screen = custom_completion
        else:
            import tkinter.messagebox as mb
            mb.showerror("Erro", "Não foi possível carregar a lição.")

    def start_review_flow(self, lang_id: str, title: str, exercises: list):
        sucesso = self.study_controller.start_review(title, exercises)
        if sucesso:
            self.switch_view(ExerciseView, controller=self.study_controller)
            
            def custom_completion():
                self.auth_controller.register_study_activity()
                
                # Processa apenas os cartões respondidos até o momento (Permite fechar no meio da sessão)
                for ex_id, quality in self.study_controller.session_results:
                    self.auth_controller.update_srs(lang_id, ex_id, quality)
                
                self.current_view.clear_view()
                tk.Label(self.current_view, text="Sessão Encerrada!", font=("Arial", 24, "bold"), bg="#2d2d2d", fg="#ff9800").pack(pady=50)
                tk.Button(self.current_view, text="Voltar ao Menu", font=("Arial", 14), bg="#404040", fg="white", command=self.show_dashboard, relief=tk.FLAT).pack(pady=30)
                
            self.current_view.show_completion_screen = custom_completion
            
    def handle_logout(self):
        self.auth_controller.logout()
        self.show_login()