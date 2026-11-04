from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import date, timedelta

@dataclass
class EstadoRevisao:
    # A data é guardada como string ISO (YYYY-MM-DD) para facilitar o JSON
    lastRecalledDate: str 
    easeFactor: float = 2.5
    repetitions: int = 0
    interval: int = 0

    def assignAnswer(self, quality: int) -> None:
        """
        Calcula o próximo intervalo baseado na qualidade da resposta (algoritmo SM-2).
        Qualidades esperadas: 0 (Erro), 3 (Bom), 5 (Fácil)
        """
        if quality < 3:
            self.repetitions = 0
            self.interval = 1
        else:
            if self.repetitions == 0:
                self.interval = 1
            elif self.repetitions == 1:
                self.interval = 6
            else:
                self.interval = int(self.interval * self.easeFactor)
            self.repetitions += 1

        # Atualiza o fator de facilidade (easeFactor)
        self.easeFactor = self.easeFactor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        if self.easeFactor < 1.3:
            self.easeFactor = 1.3

        self.lastRecalledDate = date.today().isoformat()

    def getNextDueDate(self) -> date:
        last_date = date.fromisoformat(self.lastRecalledDate)
        return last_date + timedelta(days=self.interval)

    def isDueToday(self) -> bool:
        return self.getNextDueDate() <= date.today()

@dataclass
class SessaoSrs:
    sessionDate: str
    # Dicionário mapeando exerciseId para o seu EstadoRevisao
    estadosRevisao: Dict[str, EstadoRevisao] = field(default_factory=dict)

    def getNumberDue(self) -> int:
        return sum(1 for estado in self.estadosRevisao.values() if estado.isDueToday())

@dataclass
class ProgressoLicao:
    complete: bool = False
    completionDate: Optional[str] = None

    def markAsDone(self) -> None:
        self.complete = True
        self.completionDate = date.today().isoformat()

@dataclass
class ProgressoIdioma:
    lastCompletedLessonId: Optional[str] = None
    completionDate: Optional[str] = None
    # Mapeamento de lessonId para ProgressoLicao
    progressosLicao: Dict[str, ProgressoLicao] = field(default_factory=dict)
    sessoesSrs: List[SessaoSrs] = field(default_factory=list)

    def changeProgress(self, lessonId: str) -> None:
        self.lastCompletedLessonId = lessonId
        self.completionDate = date.today().isoformat()
        
        if lessonId not in self.progressosLicao:
            self.progressosLicao[lessonId] = ProgressoLicao()
        self.progressosLicao[lessonId].markAsDone()