from src.repositories.course_repo import CourseRepository
from src.repositories.user_repo import UserRepository
from src.controllers.study_controller import StudyController
from src.controllers.auth_controller import AuthController
from src.controllers.social_controller import SocialController
from src.controllers.admin_controller import AdminController
from src.ui.app_window import AppWindow

def main():
    course_repo = CourseRepository(filepath="data/conteudos.json")
    user_repo = UserRepository(filepath="data/usuarios.json")

    study_controller = StudyController(course_repo)
    auth_controller = AuthController(user_repo)
    social_controller = SocialController(user_repo)
    admin_controller = AdminController(course_repo)

    app = AppWindow(auth_controller, study_controller, social_controller, admin_controller)
    app.mainloop()

if __name__ == "__main__":
    main()