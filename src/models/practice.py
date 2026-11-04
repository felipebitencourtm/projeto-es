import json
from dataclasses import dataclass, field
from typing import List, Optional

# --- Classes Base e Componentes ---

@dataclass
class Alternativa:
    id: str
    text: str
    is_correct: bool = False

@dataclass
class ParDeAlternativas:
    pairId: str
    positionFirst: int
    positionSecond: int
    first: Alternativa
    second: Alternativa

@dataclass
class PontoGramatical:
    point: str
    description: str

# --- Classe Pai: Exercicio ---

@dataclass
class Exercicio:
    exerciseId: str
    exerciseTitle: str
    frontText: str
    position: int
    
    def confirmAnswer(self, answer: str) -> bool:
        """Método base a ser sobrescrito pelas classes filhas."""
        raise NotImplementedError("Subclasses devem implementar confirmAnswer")

# --- Subclasses de Exercicio ---

@dataclass
class ExercicioTraducao(Exercicio):
    correctTexts: List[str] # Agora é uma lista de traduções aceitas
    
    def confirmAnswer(self, answer: str) -> bool:
        ans_norm = answer.strip().lower()
        # Verifica se a resposta está contida nas traduções corretas
        return any(ans_norm == ct.strip().lower() for ct in self.correctTexts)

@dataclass
class ExercicioAlternativas(Exercicio):
    alternativas: List[Alternativa] = field(default_factory=list)
    
    def confirmAnswer(self, answer: str) -> bool:
        # Verifica se o ID passado como resposta corresponde à alternativa correta
        for alt in self.alternativas:
            if alt.id == answer and alt.is_correct:
                return True
        return False

@dataclass
class ExercicioCombinar(Exercicio):
    pares: List[ParDeAlternativas] = field(default_factory=list)
    
    def confirmAnswer(self, answer: str) -> bool:
        """
        Espera uma string JSON no formato: {"id_first_1": "id_second_1", ...}
        """
        try:
            respostas_usuario = json.loads(answer)
            if len(respostas_usuario) != len(self.pares):
                return False
                
            for par in self.pares:
                id_first = par.first.id
                id_second = par.second.id
                
                # Verifica se o mapeamento do usuário está correto em qualquer direção
                if respostas_usuario.get(id_first) != id_second and respostas_usuario.get(id_second) != id_first:
                    return False
            return True
        except (json.JSONDecodeError, AttributeError):
            return False
        
    def getCorrectPairing(self, choice: Alternativa) -> Optional[ParDeAlternativas]:
        for par in self.pares:
            if par.first.id == choice.id or par.second.id == choice.id:
                return par
        return None

@dataclass
class ExercicioGramatica(Exercicio):
    pontosGramaticais: List[PontoGramatical] = field(default_factory=list)
    
    def confirmAnswer(self, answer: str) -> bool:
        return True # Gramática é apenas leitura, confirmar é avançar

# --- Classe Pai: Revisao ---

@dataclass
class Revisao(Exercicio):
    reviewId: str

# --- Subclasses de Revisao ---

@dataclass
class RevisaoAlternativas(Revisao):
    alternativas: List[Alternativa] = field(default_factory=list)
    
    def confirmAnswer(self, answer: str) -> bool:
        # Mesma lógica do ExercicioAlternativas
        for alt in self.alternativas:
            if alt.id == answer and alt.is_correct:
                return True
        return False

@dataclass
class RevisaoVocabulario(Revisao):
    backText: str
    
    def confirmAnswer(self, answer: str) -> bool:
        # O flashcard recebe o JSON com a qualidade (Erro, Bom, Fácil).
        # A submissão sempre "passa" na validação de resposta para avançar.
        return True