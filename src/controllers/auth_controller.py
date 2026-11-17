import uuid
import re
import hashlib
from datetime import date
from typing import Optional, Union, Tuple
from src.repositories.user_repo import UserRepository
from src.models.profile import Aluno, Admin, ProgressoIdioma, EstadoRevisao, hash_password_with_salt

class AuthController:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
        self.current_user: Optional[Union[Aluno, Admin]] = None

    def login(self, email: str, password: str) -> Tuple[bool, str]:
        user = self.user_repo.get_user_by_email(email)
        if user and user.authenticate(password):
            self.current_user = user
            return True, "Login realizado com sucesso."
        return False, "E-mail ou senha incorretos."

    def logout(self) -> None:
        self.current_user = None

    def register_aluno(self, email: str, password: str, confirm_password: str, birthdate: str) -> Tuple[bool, str]:
        email = email.strip().lower()
        if not email or len(email) > 255: return False, "E-mail inválido."
        if not password or len(password) < 6: return False, "A senha deve ter pelo menos 6 caracteres."
        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email): return False, "Formato de e-mail inválido."
        if password != confirm_password: return False, "As senhas não coincidem."

        if self.user_repo.get_user_by_email(email) is not None:
            return False, "Este e-mail já está cadastrado."

        new_id = str(uuid.uuid4())
        base_username = email.split('@')[0][:20]
        temp_username = base_username
        contador = 1
        while any(a.username.lower() == temp_username.lower() for a in self.user_repo.get_all_alunos().values()):
            temp_username = f"{base_username[:15]}{contador}"
            contador += 1
        
        pw_hash, pw_salt = hash_password_with_salt(password)

        novo_aluno = Aluno(
            userId=new_id,
            email=email,
            username=temp_username,
            passwordHash=pw_hash,
            passwordSalt=pw_salt,
            birthdate=birthdate,
            registrationDate=date.today().isoformat()
        )

        if not novo_aluno.isMinimumAgeValid(12):
            return False, "Você deve ter pelo menos 12 anos para se cadastrar (RN01)."
        
        if self.user_repo.save_aluno(novo_aluno):
            self.current_user = novo_aluno
            return True, "Conta criada com sucesso!"
        return False, "Erro ao criar conta."

    def update_username(self, new_username: str) -> Tuple[bool, str]:
        if not self.current_user or isinstance(self.current_user, Admin): return False, "Sessão inválida."
        new_username = new_username.strip()
        if len(new_username) < 3 or len(new_username) > 20: return False, "Tamanho inválido (3-20)."
        if any(a.username.lower() == new_username.lower() and a.userId != self.current_user.userId for a in self.user_repo.get_all_alunos().values()):
            return False, "Nome em uso."
        self.current_user.changeUsername(new_username)
        if self.user_repo.save_aluno(self.current_user): return True, "Nome atualizado!"
        return False, "Erro ao salvar."

    def register_study_activity(self) -> None:
        if not self.current_user or isinstance(self.current_user, Admin):
            return
        hoje = date.today()
        hoje_iso = hoje.isoformat()

        # Só incrementa se ainda não registrou atividade hoje
        if self.current_user.lastActivityDate != hoje_iso:
            if self.current_user.lastActivityDate:
                diferenca = (hoje - date.fromisoformat(self.current_user.lastActivityDate)).days
                if diferenca == 1:
                    self.current_user.incrementStreak()
                elif diferenca > 1:
                    self.current_user.resetStreak()
                    self.current_user.incrementStreak()
            else:
                self.current_user.incrementStreak()

            self.current_user.lastActivityDate = hoje_iso

            # Atualiza ofensiva compartilhada se o amigo também já estudou hoje (RN05)
            alunos = self.user_repo.get_all_alunos()
            for friend_id, amizade in self.current_user.amizadesDetalhes.items():
                amigo = alunos.get(friend_id)
                if amigo and amigo.lastActivityDate == hoje_iso:
                    amizade.incrementFriendStreak()
                    if self.current_user.userId in amigo.amizadesDetalhes:
                        amigo.amizadesDetalhes[self.current_user.userId].incrementFriendStreak()
                        self.user_repo.save_aluno(amigo)

            self.user_repo.save_aluno(self.current_user)

    def mark_lesson_completed(self, lang_id: str, lesson_id: str) -> None:
        if not self.current_user or isinstance(self.current_user, Admin): return
        
        # Garante que o idioma existe no progresso do aluno
        if lang_id not in self.current_user.progress:
            self.current_user.progress[lang_id] = ProgressoIdioma(languageId=lang_id)
            
        # Altera o progresso utilizando o método UML
        self.current_user.progress[lang_id].changeProgress(lesson_id)
        self.user_repo.save_aluno(self.current_user)

    def get_due_reviews(self, lang_id: str) -> list:
        if not self.current_user or isinstance(self.current_user, Admin): return []
        if lang_id not in self.current_user.progress: return []
        
        sessao = self.current_user.progress[lang_id].sessaoSrs
        return [c.reviewId for c in sessao.cards.values() if c.isDueToday()]

    def update_srs(self, lang_id: str, ex_id: str, quality: int) -> None:
        if not self.current_user or isinstance(self.current_user, Admin): return
        
        if lang_id not in self.current_user.progress:
            self.current_user.progress[lang_id] = ProgressoIdioma(languageId=lang_id)
            
        sessao = self.current_user.progress[lang_id].sessaoSrs
        
        if ex_id not in sessao.cards:
            sessao.cards[ex_id] = EstadoRevisao(reviewId=ex_id, lastRecalledDate="")
            
        # Aplica a pontuação do flashcard e agenda a nova data
        sessao.cards[ex_id].assignAnswer(quality)
        self.user_repo.save_aluno(self.current_user)

    def is_logged_in(self) -> bool:
        return self.current_user is not None

    def update_email(self, new_email: str) -> Tuple[bool, str]:
        if not self.current_user or isinstance(self.current_user, Admin): return False, "Sessão inválida."
        new_email = new_email.strip().lower()
        if not new_email or not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", new_email): return False, "E-mail inválido."
        if any(u.email == new_email and u.userId != self.current_user.userId for u in self.user_repo.get_all_alunos().values()):
            return False, "E-mail em uso."
        self.current_user.changeEmail(new_email)
        if self.user_repo.save_aluno(self.current_user): return True, "E-mail atualizado!"
        return False, "Erro ao salvar."

    def update_password(self, new_password: str) -> Tuple[bool, str]:
        if not self.current_user or isinstance(self.current_user, Admin): return False, "Sessão inválida."
        if len(new_password) < 6: return False, "Senha muito curta."
        self.current_user.changePassword(new_password)
        if self.user_repo.save_aluno(self.current_user): return True, "Senha atualizada!"
        return False, "Erro ao salvar."
    
    def reset_progress(self) -> Tuple[bool, str]:
        if not self.current_user or isinstance(self.current_user, Admin): return False, "Ação inválida."
        # Usa o método de reset unificado do modelo UML
        self.current_user.resetAccountProgress()
        if self.user_repo.save_aluno(self.current_user): return True, "Progresso zerado com sucesso!"
        return False, "Erro ao zerar."

    def delete_account(self) -> Tuple[bool, str]:
        if not self.current_user or isinstance(self.current_user, Admin): return False, "Ação inválida."
        data = self.user_repo.read_data()
        user_id = self.current_user.userId
        if user_id in data.get("alunos", {}):
            del data["alunos"][user_id]
            for u_data in data.get("alunos", {}).values():
                if user_id in u_data.get("friends", []):
                    u_data["friends"].remove(user_id)
                    u_data.get("amizadesDetalhes", {}).pop(user_id, None)
            if self.user_repo.write_data(data):
                self.logout()
                return True, "Conta apagada."
        return False, "Erro ao apagar."

    def register_admin(self, email: str, password: str, confirm_password: str) -> Tuple[bool, str]:
        if not self.current_user or not isinstance(self.current_user, Admin): return False, "Sem permissão."
        email = email.strip().lower()
        if not email or not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email): return False, "E-mail inválido."
        if len(password) < 6 or password != confirm_password: return False, "Erro nas senhas."
        if self.user_repo.get_user_by_email(email) is not None: return False, "E-mail já existe."

        new_id = f"admin_{uuid.uuid4().hex[:8]}"
        pw_hash, pw_salt = hash_password_with_salt(password)
        novo_admin = Admin(
            userId=new_id,
            email=email,
            username="Admin",
            passwordHash=pw_hash,
            passwordSalt=pw_salt,
            birthdate="1900-01-01",
            registrationDate=date.today().isoformat()
        )
        
        if self.user_repo.save_admin(novo_admin): return True, "Administrador registrado!"
        return False, "Erro ao salvar."

    def enroll_in_srs(self, lang_id: str, ex_id: str) -> None:
        """Regista um exercício na fila SRS pela primeira vez."""
        if not self.current_user or isinstance(self.current_user, Admin): return
        
        if lang_id not in self.current_user.progress:
            self.current_user.progress[lang_id] = ProgressoIdioma(languageId=lang_id)
            
        sessao = self.current_user.progress[lang_id].sessaoSrs
        
        if ex_id not in sessao.cards:
            # Sem chamar assignAnswer, entra virgem. lastRecalledDate="" faz com que isDueToday() seja True.
            sessao.cards[ex_id] = EstadoRevisao(reviewId=ex_id, lastRecalledDate="")
            self.user_repo.save_aluno(self.current_user)