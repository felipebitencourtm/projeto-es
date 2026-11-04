import hashlib
from datetime import date, timedelta
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum

class StatusPedido(Enum):
    PENDENTE = "PENDENTE"
    ACEITO = "ACEITO"
    RECUSADO = "RECUSADO"

@dataclass
class PedidoDeAmizade:
    senderId: str
    dateSent: str
    status: StatusPedido = StatusPedido.PENDENTE

    def accept(self) -> None:
        self.status = StatusPedido.ACEITO

    def reject(self) -> None:
        self.status = StatusPedido.RECUSADO

@dataclass
class Amizade:
    dateEstablished: str
    friendStreakStart: str
    friendStreak: int = 0

    def incrementFriendStreak(self) -> None:
        self.friendStreak += 1

    def resetFriendStreak(self) -> None:
        self.friendStreak = 0

# --- Classes de Progressão e SRS do Diagrama UML ---

@dataclass
class EstadoRevisao:
    reviewId: str
    lastRecalledDate: str
    easeFactor: float = 2.5
    repetitions: int = 0
    interval: int = 0

    def assignAnswer(self, quality: int) -> None:
        if quality > 0:
            self.repetitions += 1
            if self.repetitions == 1:
                self.interval = 1
            elif self.repetitions == 2:
                self.interval = 6
            else:
                bonus = 1.0 if quality == 1 else 1.2
                self.interval = int(self.interval * self.easeFactor * bonus)
            self.easeFactor = min(3.0, self.easeFactor + (0.1 if quality == 2 else 0.0))
        else:
            self.resetInterval()
            self.easeFactor = max(1.3, self.easeFactor - 0.2)
        
        self.lastRecalledDate = date.today().isoformat()

    def getNextDueDate(self) -> date:
        if not self.lastRecalledDate:
            return date.today()
        return date.fromisoformat(self.lastRecalledDate) + timedelta(days=self.interval)

    def isDueToday(self) -> bool:
        return self.getNextDueDate() <= date.today()

    def resetInterval(self) -> None:
        self.interval = 0
        self.repetitions = 0

    def incrementInterval(self) -> None:
        pass # Lógica embutida no assignAnswer

@dataclass
class SessaoSrs:
    sessionDate: str
    cards: Dict[str, EstadoRevisao] = field(default_factory=dict)

    def getNumberDue(self) -> int:
        return sum(1 for c in self.cards.values() if c.isDueToday())

    def getNextCardDue(self) -> Optional[EstadoRevisao]:
        # Como o isDueToday recalcula a data em tempo real, após dar uma nota o cartão sai da fila
        for c in self.cards.values():
            if c.isDueToday():
                return c
        return None

@dataclass
class ProgressoLicao:
    lessonId: str
    complete: bool = False
    completionDate: Optional[str] = None

    def markAsDone(self) -> None:
        self.complete = True
        self.completionDate = date.today().isoformat()

    def registerSolved(self, exerciseId: str) -> None:
        pass # Funcionalidade para controle granular futuro

@dataclass
class ProgressoIdioma:
    languageId: str
    lastCompletedLessonId: str = ""
    licoes: Dict[str, ProgressoLicao] = field(default_factory=dict)
    sessaoSrs: SessaoSrs = field(default_factory=lambda: SessaoSrs(sessionDate=date.today().isoformat()))

    def changeProgress(self, lessonId: str) -> None:
        self.lastCompletedLessonId = lessonId
        if lessonId not in self.licoes:
            self.licoes[lessonId] = ProgressoLicao(lessonId=lessonId)
        self.licoes[lessonId].markAsDone()

    def reset(self) -> None:
        self.lastCompletedLessonId = ""
        self.licoes = {}
        self.sessaoSrs = SessaoSrs(sessionDate=date.today().isoformat())

# ----------------------------------------------------

@dataclass
class Usuario:
    userId: str
    email: str
    username: str
    passwordHash: str
    birthdate: str
    registrationDate: str

    def changeUsername(self, newUsername: str) -> None:
        self.username = newUsername

    def changeEmail(self, newEmail: str) -> None:
        self.email = newEmail

    def authenticate(self, password: str) -> bool:
        hashed_input = hashlib.sha256(password.encode('utf-8')).hexdigest()
        return self.passwordHash == hashed_input

@dataclass
class Aluno(Usuario):
    streak: int = 0
    longestStreak: int = 0
    lastActivityDate: Optional[str] = None
    
    friends: List[str] = field(default_factory=list) 
    pedidosDeAmizade: List[PedidoDeAmizade] = field(default_factory=list)
    amizadesDetalhes: Dict[str, Amizade] = field(default_factory=dict)
    
    # Relação UML: 0..* ProgressoIdioma
    progress: Dict[str, ProgressoIdioma] = field(default_factory=dict)

    def incrementStreak(self) -> None:
        self.streak += 1
        if self.streak > self.longestStreak:
            self.longestStreak = self.streak
            
    def resetStreak(self) -> None:
        self.streak = 0
        
    def resetAccountProgress(self) -> None:
        self.resetStreak()
        self.longestStreak = 0
        self.lastActivityDate = None
        self.progress = {}

@dataclass
class Admin(Usuario):
    pass