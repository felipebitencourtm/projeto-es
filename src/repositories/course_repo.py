from typing import List, Dict
from src.repositories.base_repository import BaseRepository
from src.models.practice import (
    Exercicio, ExercicioTraducao, ExercicioAlternativas, 
    ExercicioCombinar, ExercicioGramatica, RevisaoAlternativas, 
    RevisaoVocabulario, Alternativa, ParDeAlternativas, PontoGramatical
)

class CourseRepository(BaseRepository):
    def __init__(self, filepath: str = "data/conteudos.json"): # Atualizado aqui
        super().__init__(filepath)

    def get_exercises_for_lesson(self, language_id: str, unit_number: int, lesson_id: str) -> List[Exercicio]:
        """Navega pelo JSON de conteúdos e instancia os exercícios de uma lição específica."""
        data = self.read_data()
        
        idioma_data = data.get("idiomas", {}).get(language_id)
        if not idioma_data:
            return []

        for unidade in idioma_data.get("unidades", []):
            if unidade["number"] == unit_number:
                for licao in unidade.get("licoes", []):
                    if licao["lessonId"] == lesson_id:
                        return self._instantiate_exercises(licao.get("exercicios", []))
        return []

    def _instantiate_exercises(self, exercicios_data: List[Dict]) -> List[Exercicio]:
        """Fábrica (Factory) que converte dicionários JSON nas subclasses corretas de Exercicio."""
        exercicios_instanciados = []
        
        for ex_data in exercicios_data:
            ex_type = ex_data.get("type")
            
            base_args = {
                "exerciseId": ex_data["exerciseId"],
                "exerciseTitle": ex_data["exerciseTitle"],
                "frontText": ex_data["frontText"],
                "position": ex_data["position"]
            }
            if ex_type == "ExercicioTraducao":
                # Aceita tanto uma string única quanto uma lista de traduções do JSON
                correct_data = ex_data.get("correctTexts", [])
                if not correct_data and "correctTexts" in ex_data:
                    correct_data = [ex_data["correctTexts"]]
                    
                exercicios_instanciados.append(
                    ExercicioTraducao(**base_args, correctTexts=correct_data)
                )
                
            elif ex_type == "ExercicioAlternativas":
                # Mapeamento manual para corrigir a diferença entre 'correct' (JSON) e 'is_correct' (Model)
                alternativas = [
                    Alternativa(id=alt["id"], text=alt["text"], is_correct=alt.get("correct", False)) 
                    for alt in ex_data.get("alternativas", [])
                ]
                exercicios_instanciados.append(
                    ExercicioAlternativas(**base_args, alternativas=alternativas)
                )
                
            elif ex_type == "ExercicioCombinar":
                pares = []
                for par_data in ex_data.get("pares", []):
                    # Como no JSON de combinar não tem o campo correct, usamos o padrão (False)
                    first = Alternativa(id=par_data["first"]["id"], text=par_data["first"]["text"])
                    second = Alternativa(id=par_data["second"]["id"], text=par_data["second"]["text"])
                    pares.append(
                        ParDeAlternativas(
                            pairId=par_data["pairId"],
                            positionFirst=par_data["positionFirst"],
                            positionSecond=par_data["positionSecond"],
                            first=first,
                            second=second
                        )
                    )
                exercicios_instanciados.append(
                    ExercicioCombinar(**base_args, pares=pares)
                )
                
            elif ex_type == "ExercicioGramatica":
                pontos = [PontoGramatical(**pt) for pt in ex_data.get("pontosGramaticais", [])]
                exercicios_instanciados.append(
                    ExercicioGramatica(**base_args, pontosGramaticais=pontos)
                )
                
            elif ex_type == "RevisaoAlternativas":
                alternativas = [
                    Alternativa(id=alt["id"], text=alt["text"], is_correct=alt.get("correct", False)) 
                    for alt in ex_data.get("alternativas", [])
                ]
                exercicios_instanciados.append(
                    RevisaoAlternativas(
                        **base_args, 
                        reviewId=ex_data["reviewId"], 
                        alternativas=alternativas
                    )
                )
                
            elif ex_type == "RevisaoVocabulario":
                exercicios_instanciados.append(
                    RevisaoVocabulario(
                        **base_args, 
                        reviewId=ex_data["reviewId"], 
                        backText=ex_data["backText"]
                    )
                )

        return exercicios_instanciados
