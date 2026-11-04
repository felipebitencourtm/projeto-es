from datetime import date
from typing import Any, List, Dict, Tuple
from src.repositories.user_repo import UserRepository
from src.models.profile import Aluno, PedidoDeAmizade, Amizade, StatusPedido

class SocialController:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def send_friend_request(self, sender_id: str, receiver_username: str) -> Tuple[bool, str]:
        """Envia um pedido de amizade procurando o destinatário pelo nome de usuário."""
        alunos = self.user_repo.get_all_alunos()
        
        receiver = next((a for a in alunos.values() if a.username.lower() == receiver_username.lower()), None)
        
        if not receiver:
            return False, "Usuário não encontrado."
            
        if receiver.userId == sender_id:
            return False, "Você não pode enviar um pedido para você mesmo."
            
        if sender_id in receiver.friends:
            return False, "Vocês já são amigos."

        if any(p.senderId == sender_id and p.status == StatusPedido.PENDENTE for p in receiver.pedidosDeAmizade):
            return False, "Pedido de amizade já enviado e aguardando resposta."

        novo_pedido = PedidoDeAmizade(
            senderId=sender_id,
            dateSent=date.today().isoformat()
        )
        receiver.pedidosDeAmizade.append(novo_pedido)
        
        if self.user_repo.save_aluno(receiver):
            return True, "Pedido de amizade enviado com sucesso!"
        return False, "Erro ao enviar pedido."

    def accept_friend_request(self, receiver_id: str, sender_id: str) -> Tuple[bool, str]:
        """Aceita um pedido de amizade e cria o vínculo para ambos os usuários."""
        alunos = self.user_repo.get_all_alunos()
        receiver = alunos.get(receiver_id)
        sender = alunos.get(sender_id)
        
        if not receiver or not sender:
            return False, "Erro de dados: Usuário não encontrado."

        pedido = next((p for p in receiver.pedidosDeAmizade if p.senderId == sender_id and p.status == StatusPedido.PENDENTE), None)
        if not pedido:
            return False, "Pedido não encontrado ou já processado."
            
        pedido.accept()
        hoje = date.today().isoformat()
        
        receiver.friends.append(sender_id)
        receiver.amizadesDetalhes[sender_id] = Amizade(dateEstablished=hoje, friendStreakStart=hoje)
        
        sender.friends.append(receiver_id)
        sender.amizadesDetalhes[receiver_id] = Amizade(dateEstablished=hoje, friendStreakStart=hoje)
        
        s1 = self.user_repo.save_aluno(receiver)
        s2 = self.user_repo.save_aluno(sender)
        
        if s1 and s2:
            return True, f"Agora você é amigo de {sender.username}!"
        return False, "Erro ao salvar a amizade."

    def reject_friend_request(self, receiver_id: str, sender_id: str) -> Tuple[bool, str]:
        """Recusa um pedido de amizade pendente."""
        alunos = self.user_repo.get_all_alunos()
        receiver = alunos.get(receiver_id)
        
        if not receiver:
            return False, "Erro de dados: Usuário não encontrado."

        pedido = next((p for p in receiver.pedidosDeAmizade if p.senderId == sender_id and p.status == StatusPedido.PENDENTE), None)
        if not pedido:
            return False, "Pedido não encontrado ou já processado."
            
        pedido.reject()
        
        if self.user_repo.save_aluno(receiver):
            return True, "Pedido de amizade recusado."
        return False, "Erro ao recusar pedido."

    def get_pending_requests_with_names(self, user_id: str) -> List[Dict]:
        """Busca os pedidos pendentes já mapeando o ID do remetente para o Nome de Usuário."""
        alunos = self.user_repo.get_all_alunos()
        user = alunos.get(user_id)
        if not user:
            return []
            
        requests = []
        for p in user.pedidosDeAmizade:
            if p.status == StatusPedido.PENDENTE:
                sender = alunos.get(p.senderId)
                sender_name = sender.username if sender else "Usuário Desconhecido"
                requests.append({"senderId": p.senderId, "senderUsername": sender_name})
        return requests

    def get_global_ranking(self) -> List[Dict]:
        alunos = self.user_repo.get_all_alunos().values()
        ranking = [{"username": a.username, "streak": a.streak} for a in alunos]
        ranking.sort(key=lambda x: x["streak"], reverse=True)
        return ranking

    def get_friends_ranking(self, user_id: str) -> List[Dict]:
        """Gera um ranking contendo apenas o usuário atual e seus amigos."""
        alunos = self.user_repo.get_all_alunos()
        current_user = alunos.get(user_id)
        
        if not current_user:
            return []
            
        ranking = [{"username": current_user.username, "streak": current_user.streak}]
        
        for friend_id in current_user.friends:
            friend = alunos.get(friend_id)
            if friend:
                ranking.append({"username": friend.username, "streak": friend.streak})
                
        ranking.sort(key=lambda x: x["streak"], reverse=True)
        return ranking
    
    def remove_friend(self, user_id: str, friend_id: str) -> Tuple[bool, str]:
        """Remove o vínculo de amizade entre dois usuários."""
        alunos = self.user_repo.get_all_alunos()
        user = alunos.get(user_id)
        friend = alunos.get(friend_id)
        
        if not user or not friend:
            return False, "Usuário não encontrado."

        if friend_id in user.friends:
            user.friends.remove(friend_id)
            user.amizadesDetalhes.pop(friend_id, None)

        if user_id in friend.friends:
            friend.friends.remove(user_id)
            friend.amizadesDetalhes.pop(user_id, None)

        s1 = self.user_repo.save_aluno(user)
        s2 = self.user_repo.save_aluno(friend)
        
        if s1 and s2:
            return True, "Amizade desfeita."
        return False, "Erro ao atualizar dados."

    def get_current_friends(self, user_id: str) -> List[Dict]:
        """Retorna a lista de amigos atuais para a interface."""
        alunos = self.user_repo.get_all_alunos()
        user = alunos.get(user_id)
        if not user: return []
        
        friends_list = []
        for f_id in user.friends:
            friend = alunos.get(f_id)
            if friend:
                friends_list.append({"id": friend.userId, "username": friend.username})
        return friends_list

    def verify_answer(self, user_answer: Any, quality: int = None) -> bool:
        ex = self.get_current_exercise()
        if not ex: return False
        
        ex_type = ex.get("type")
        is_correct = False

        # Se for Flashcard, a interface já passa a nota (0, 1 ou 2)
        if ex_type == "RevisaoVocabulario":
            self.session_results.append((ex["exerciseId"], quality))
            if quality > 0: self.correct_answers_count += 1
            return True # Flashcards sempre avançam para a próxima tela

        if ex_type == "ExercicioTraducao":
            respostas_validas = [t.lower() for t in ex.get("correctTexts", [])]
            is_correct = isinstance(user_answer, str) and user_answer.strip().lower() in respostas_validas
        elif ex_type == "ExercicioAlternativas":
            for alt in ex.get("alternativas", []):
                if alt.get("id") == user_answer and alt.get("correct") is True:
                    is_correct = True
                    break
        elif ex_type == "ExercicioCombinar":
            gabarito = {p["first"]["text"]: p["second"]["text"] for p in ex.get("pares", [])}
            is_correct = True
            for esq, dir_sel in user_answer.items():
                if gabarito.get(esq) != dir_sel:
                    is_correct = False
                    break
        elif ex_type == "ExercicioGramatica":
            is_correct = True

        if is_correct:
            self.correct_answers_count += 1
            
        if ex_type != "ExercicioGramatica":
            # Para exercícios normais, mapeia o booleano para a escala do SRS (0 = erro, 1 = acerto padrão)
            final_quality = 1 if is_correct else 0
            self.session_results.append((ex["exerciseId"], final_quality))
            
        return is_correct