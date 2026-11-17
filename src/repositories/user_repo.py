import json
from datetime import date
from typing import Dict, Optional, Union
from src.repositories.base_repository import BaseRepository
from src.models.profile import Aluno, Admin, Amizade, PedidoDeAmizade, StatusPedido
from src.models.profile import ProgressoIdioma, ProgressoLicao, SessaoSrs, EstadoRevisao

class UserRepository(BaseRepository):
    def __init__(self, filepath: str = "data/usuarios.json"):
        super().__init__(filepath)

    def get_all_alunos(self) -> Dict[str, Aluno]:
        data = self.read_data()
        alunos_data = data.get("alunos", {})
        alunos_instanciados = {}

        for user_id, a_data in alunos_data.items():
            pedidos = []
            for p_data in a_data.get("pedidosDeAmizade", []):
                pedidos.append(PedidoDeAmizade(
                    senderId=p_data["senderId"],
                    dateSent=p_data["dateSent"],
                    status=StatusPedido(p_data.get("status", "PENDENTE"))
                ))

            amizades = {}
            for amigo_id, amz_data in a_data.get("amizadesDetalhes", {}).items():
                amizades[amigo_id] = Amizade(
                    dateEstablished=amz_data["dateEstablished"],
                    friendStreakStart=amz_data["friendStreakStart"],
                    friendStreak=amz_data.get("friendStreak", 0)
                )

            # Reconstrução do Progresso e Sessão SRS
            progress_dict = {}
            for lang_id, p_data in a_data.get("progress", {}).items():
                licoes_dict = {}
                for l_id, l_data in p_data.get("licoes", {}).items():
                    licoes_dict[l_id] = ProgressoLicao(
                        lessonId=l_data["lessonId"],
                        complete=l_data.get("complete", False),
                        completionDate=l_data.get("completionDate")
                    )
                
                srs_data = p_data.get("sessaoSrs", {})
                cards_dict = {}
                for rev_id, rev_data in srs_data.get("cards", {}).items():
                    cards_dict[rev_id] = EstadoRevisao(
                        reviewId=rev_data["reviewId"],
                        lastRecalledDate=rev_data["lastRecalledDate"],
                        easeFactor=rev_data.get("easeFactor", 2.5),
                        repetitions=rev_data.get("repetitions", 0),
                        interval=rev_data.get("interval", 0)
                    )
                sessao = SessaoSrs(
                    sessionDate=srs_data.get("sessionDate", date.today().isoformat()),
                    cards=cards_dict
                )
                
                progress_dict[lang_id] = ProgressoIdioma(
                    languageId=p_data["languageId"],
                    lastCompletedLessonId=p_data.get("lastCompletedLessonId", ""),
                    licoes=licoes_dict,
                    sessaoSrs=sessao
                )

            aluno_obj = Aluno(
                userId=a_data["userId"],
                email=a_data["email"],
                username=a_data["username"],
                passwordHash=a_data["passwordHash"],
                passwordSalt=a_data.get("passwordSalt", ""),
                birthdate=a_data["birthdate"],
                registrationDate=a_data["registrationDate"],
                streak=a_data.get("streak", 0),
                longestStreak=a_data.get("longestStreak", 0),
                lastActivityDate=a_data.get("lastActivityDate"),
                friends=a_data.get("friends", []),
                pedidosDeAmizade=pedidos,
                amizadesDetalhes=amizades,
                progress=progress_dict
            )


            if aluno_obj.lastActivityDate and aluno_obj.streak > 0:
                dias_sem_estudar = (date.today() - date.fromisoformat(aluno_obj.lastActivityDate)).days
                if dias_sem_estudar > 1:
                    aluno_obj.resetStreak()
                    for amz in aluno_obj.amizadesDetalhes.values():
                        amz.resetFriendStreak()
                    self.save_aluno(aluno_obj)

            alunos_instanciados[user_id] = aluno_obj

        for aluno in alunos_instanciados.values():
            atualizou = False
            for amigo_id, amz in aluno.amizadesDetalhes.items():
                amigo = alunos_instanciados.get(amigo_id)
                if amz.friendStreak > 0 and (not amigo or amigo.streak == 0):
                    amz.resetFriendStreak()
                    atualizou = True
            if atualizou:
                self.save_aluno(aluno)
            
        return alunos_instanciados

    def get_all_admins(self) -> Dict[str, Admin]:
        data = self.read_data()
        admins_data = data.get("admins", {})
        admins_instanciados = {}

        for user_id, ad_data in admins_data.items():
            admins_instanciados[user_id] = Admin(
                userId=ad_data["userId"],
                email=ad_data["email"],
                username=ad_data["username"],
                passwordHash=ad_data["passwordHash"],
                passwordSalt=ad_data.get("passwordSalt", ""),
                birthdate=ad_data["birthdate"],
                registrationDate=ad_data["registrationDate"]
            )
            
        return admins_instanciados

    def get_user_by_email(self, email: str) -> Optional[Union[Aluno, Admin]]:
        for aluno in self.get_all_alunos().values():
            if aluno.email.lower() == email.lower():
                return aluno
                
        for admin in self.get_all_admins().values():
            if admin.email.lower() == email.lower():
                return admin
                
        return None

    def save_aluno(self, aluno: Aluno) -> bool:
        data = self.read_data()
        if "alunos" not in data:
            data["alunos"] = {}

        pedidos_serializados = [
            {"senderId": p.senderId, "dateSent": p.dateSent, "status": p.status.value} 
            for p in aluno.pedidosDeAmizade
        ]
        
        amizades_serializadas = {
            amigo_id: {
                "dateEstablished": amz.dateEstablished,
                "friendStreakStart": amz.friendStreakStart,
                "friendStreak": amz.friendStreak
            } for amigo_id, amz in aluno.amizadesDetalhes.items()
        }

        # Serialização do Progresso e Sessão SRS
        progress_serializado = {}
        for lang_id, prog in aluno.progress.items():
            licoes_ser = {
                l_id: {
                    "lessonId": lic.lessonId,
                    "complete": lic.complete,
                    "completionDate": lic.completionDate
                } for l_id, lic in prog.licoes.items()
            }
            
            cards_ser = {
                rev_id: {
                    "reviewId": card.reviewId,
                    "lastRecalledDate": card.lastRecalledDate,
                    "easeFactor": card.easeFactor,
                    "repetitions": card.repetitions,
                    "interval": card.interval
                } for rev_id, card in prog.sessaoSrs.cards.items()
            }
            
            sessao_ser = {
                "sessionDate": prog.sessaoSrs.sessionDate,
                "cards": cards_ser
            }
            
            progress_serializado[lang_id] = {
                "languageId": prog.languageId,
                "lastCompletedLessonId": prog.lastCompletedLessonId,
                "licoes": licoes_ser,
                "sessaoSrs": sessao_ser
            }

        data["alunos"][aluno.userId] = {
            "userId": aluno.userId,
            "email": aluno.email,
            "username": aluno.username,
            "passwordHash": aluno.passwordHash,
            "passwordSalt": aluno.passwordSalt,
            "birthdate": aluno.birthdate,
            "registrationDate": aluno.registrationDate,
            "streak": aluno.streak,
            "longestStreak": aluno.longestStreak,
            "lastActivityDate": aluno.lastActivityDate,
            "friends": aluno.friends,
            "pedidosDeAmizade": pedidos_serializados,
            "amizadesDetalhes": amizades_serializadas,
            "progress": progress_serializado
        }
        
        return self.write_data(data)

    def save_admin(self, admin: Admin) -> bool:
        data = self.read_data()
        if "admins" not in data:
            data["admins"] = {}

        data["admins"][admin.userId] = {
            "userId": admin.userId,
            "email": admin.email,
            "username": admin.username,
            "passwordHash": admin.passwordHash,
            "passwordSalt": admin.passwordSalt,
            "birthdate": admin.birthdate,
            "registrationDate": admin.registrationDate
        }
        
        return self.write_data(data)