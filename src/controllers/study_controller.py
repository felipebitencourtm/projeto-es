from typing import Dict, Any, Optional
from src.repositories.course_repo import CourseRepository

class StudyController:
    def __init__(self, course_repo: CourseRepository):
        self.course_repo = course_repo
        self.current_lesson: Optional[Dict[str, Any]] = None
        self.current_exercise_index: int = 0
        self.correct_answers_count: int = 0
        self.session_results = [] 
        self._attempts = {}

    def start_lesson(self, lang_id: str, unit_number: int, lesson_id: str) -> bool:
        data = self.course_repo.read_data()
        idioma = data.get("idiomas", {}).get(lang_id)
        if not idioma: return False
        unidade = next((u for u in idioma.get("unidades", []) if u["number"] == unit_number), None)
        if not unidade: return False
        licao = next((l for l in unidade.get("licoes", []) if l["lessonId"] == lesson_id), None)
        if not licao: return False

        self.current_lesson = licao
        self.current_exercise_index = 0
        self.correct_answers_count = 0
        self.session_results = []
        self._attempts = {}
        return True

    def get_categorized_reviews(self, lang_id: str, due_ex_ids: list) -> tuple:
        """Divide a fila SRS em Vocabulário e Gramática (Alternativas clonadas)"""
        data = self.course_repo.read_data()
        idioma = data.get("idiomas", {}).get(lang_id, {})
        vocab_due, grammar_due = [], []
        
        for u in idioma.get("unidades", []):
            for l in u.get("licoes", []):
                for ex in l.get("exercicios", []):
                    ex_id = ex["exerciseId"]
                    ex_type = ex.get("type", "")
                    
                    if ex_id in due_ex_ids and ex_type == "RevisaoVocabulario":
                        vocab_due.append(ex)
                        
                    # Procura pelo ID gerado automaticamente
                    alt_id = f"alt_{ex_id}"
                    if alt_id in due_ex_ids and ex_type == "ExercicioAlternativas":
                        # Instancia como RevisaoAlternativas dinamicamente
                        rev_ex = ex.copy()
                        rev_ex["exerciseId"] = alt_id
                        rev_ex["type"] = "RevisaoAlternativas"
                        grammar_due.append(rev_ex)
                        
        return grammar_due, vocab_due

    def start_review(self, title: str, exercises: list) -> bool:
        if not exercises: return False
        self.current_lesson = {"title": title, "exercicios": exercises}
        self.current_exercise_index = 0
        self.correct_answers_count = 0
        self.session_results = []
        self._attempts = {}
        return True

    def get_current_exercise(self) -> Optional[Dict[str, Any]]:
        if not self.current_lesson: return None
        exercicios = self.current_lesson.get("exercicios", [])
        if self.current_exercise_index < len(exercicios):
            return exercicios[self.current_exercise_index]
        return None

    def verify_answer(self, user_answer: Any, quality: int = None) -> bool:
        ex = self.get_current_exercise()
        if not ex: return False
        
        ex_id = ex["exerciseId"]
        ex_type = ex.get("type", "")
        is_correct = False

        if ex_type == "RevisaoVocabulario":
            if ex_id not in self._attempts:
                self.session_results.append((ex_id, quality))
                self._attempts[ex_id] = True
            if quality > 0: self.correct_answers_count += 1
            return True

        if ex_type == "ExercicioAlternativas" or ex_type == "RevisaoAlternativas":
            for alt in ex.get("alternativas", []):
                if alt.get("id") == user_answer and alt.get("correct") is True:
                    is_correct = True
                    break
            
            # Se for revisão, submete a nota automaticamente (1 ou 0)
            if ex_type == "RevisaoAlternativas":
                if ex_id not in self._attempts:
                    self.session_results.append((ex_id, 1 if is_correct else 0))
                    self._attempts[ex_id] = True
                if is_correct: self.correct_answers_count += 1
                return is_correct

        elif ex_type == "ExercicioTraducao":
            respostas_validas = [t.lower() for t in ex.get("correctTexts", [])]
            is_correct = isinstance(user_answer, str) and user_answer.strip().lower() in respostas_validas
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
            
        return is_correct

    def next_exercise(self) -> bool:
        self.current_exercise_index += 1
        return self.get_current_exercise() is not None

    def get_final_score(self) -> int:
        if not self.current_lesson: return 0
        total = len(self.current_lesson.get("exercicios", []))
        if total == 0: return 0
        return int((self.correct_answers_count / total) * 100)