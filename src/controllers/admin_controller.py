import uuid
from typing import Tuple, Dict, Any
from src.repositories.course_repo import CourseRepository

class AdminController:
    def __init__(self, course_repo: CourseRepository):
        self.course_repo = course_repo

    def get_all_languages(self) -> Dict[str, Any]:
        return self.course_repo.read_data().get("idiomas", {})

    def add_language(self, name: str) -> Tuple[bool, str]:
        name = name.strip()
        if not name or name == "Nome": return False, "Nome inválido."
        data = self.course_repo.read_data()
        if "idiomas" not in data: data["idiomas"] = {}
        lang_id = f"lang_{uuid.uuid4().hex[:8]}"
        data["idiomas"][lang_id] = {"languageId": lang_id, "name": name, "unidades": []}
        if self.course_repo.write_data(data): return True, "Idioma adicionado."
        return False, "Erro ao salvar idioma."

    def delete_language(self, lang_id: str) -> Tuple[bool, str]:
        data = self.course_repo.read_data()
        if lang_id in data.get("idiomas", {}):
            del data["idiomas"][lang_id]
            self.course_repo.write_data(data)
            return True, "Idioma removido."
        return False, "Erro ao remover."

    def add_unit(self, lang_id: str, unit_number: int, title: str) -> Tuple[bool, str]:
        title = title.strip()
        if not title or title == "Nome": return False, "Nome inválido."
        data = self.course_repo.read_data()
        idioma = data.get("idiomas", {}).get(lang_id)
        if not idioma: return False, "Idioma não encontrado."
        idioma["unidades"].append({"number": unit_number, "title": title, "licoes": []})
        idioma["unidades"].sort(key=lambda x: x["number"])
        if self.course_repo.write_data(data): return True, "Unidade adicionada."
        return False, "Erro ao salvar unidade."

    def add_lesson(self, lang_id: str, unit_number: int, title: str) -> Tuple[bool, str]:
        title = title.strip()
        if not title or title == "Nome da Lição": return False, "Nome inválido."
        data = self.course_repo.read_data()
        idioma = data.get("idiomas", {}).get(lang_id)
        unidade = next((u for u in idioma.get("unidades", []) if u["number"] == unit_number), None) if idioma else None
        if not unidade: return False, "Unidade não encontrada."
        
        next_num = len(unidade.get("licoes", [])) + 1
        lesson_id = f"les_{uuid.uuid4().hex[:6]}"
        
        unidade["licoes"].append({
            "lessonId": lesson_id, 
            "number": next_num, 
            "title": title, 
            "exercicios": []
        })
        if self.course_repo.write_data(data): return True, "Lição adicionada."
        return False, "Erro ao salvar lição."

    def delete_lesson(self, lang_id: str, unit_number: int, lesson_id: str) -> Tuple[bool, str]:
        data = self.course_repo.read_data()
        idioma = data.get("idiomas", {}).get(lang_id)
        unidade = next((u for u in idioma.get("unidades", []) if u["number"] == unit_number), None) if idioma else None
        if not unidade: return False, "Unidade não encontrada."
        unidade["licoes"] = [l for l in unidade["licoes"] if l["lessonId"] != lesson_id]
        if self.course_repo.write_data(data): return True, "Lição removida."
        return False, "Erro ao remover lição."

    def add_blank_exercises(self, lang_id: str, unit_num: int, lesson_id: str, count: int) -> Tuple[bool, str]:
        if count <= 0: return False, "Quantidade inválida."
        data = self.course_repo.read_data()
        idioma = data.get("idiomas", {}).get(lang_id)
        unidade = next((u for u in idioma.get("unidades", []) if u["number"] == unit_num), None) if idioma else None
        licao = next((l for l in unidade.get("licoes", []) if l["lessonId"] == lesson_id), None) if unidade else None
        if not licao: return False, "Lição não encontrada."

        for _ in range(count):
            ex_id = f"ex_{uuid.uuid4().hex[:6]}"
            licao["exercicios"].append({
                "type": "ExercicioTraducao",
                "exerciseId": ex_id,
                "exerciseTitle": "Novo Exercício",
                "frontText": "",
                "position": len(licao["exercicios"]) + 1,
                "correctTexts": []
            })
        if self.course_repo.write_data(data): return True, f"{count} exercícios criados em branco."
        return False, "Erro ao criar exercícios."

    def update_exercise(self, lang_id: str, unit_num: int, lesson_id: str, ex_id: str, tipo: str, titulo: str, enunciado: str, specific_data: dict) -> Tuple[bool, str]:
        data = self.course_repo.read_data()
        idioma = data.get("idiomas", {}).get(lang_id)
        unidade = next((u for u in idioma.get("unidades", []) if u["number"] == unit_num), None) if idioma else None
        licao = next((l for l in unidade.get("licoes", []) if l["lessonId"] == lesson_id), None) if unidade else None
        if not licao: return False, "Lição não encontrada."
        
        ex = next((e for e in licao["exercicios"] if e["exerciseId"] == ex_id), None)
        if not ex: return False, "Exercício não encontrado."

        # Atualiza campos base
        ex["type"] = tipo
        ex["exerciseTitle"] = titulo.strip()
        ex["frontText"] = enunciado.strip()
        
        # Limpa chaves antigas de outros tipos para evitar lixo no JSON
        for k in ["correctTexts", "alternativas", "pares", "pontosGramaticais", "backText"]:
            ex.pop(k, None)

        # Preenche de forma estruturada conforme o tipo
        if tipo == "ExercicioTraducao":
            ex["correctTexts"] = specific_data.get("translations", [])
            
        elif tipo == "ExercicioAlternativas":
            alts_list = []
            correct_idx = specific_data.get("correct_idx", 0)
            for idx, text in enumerate(specific_data.get("alts", [])):
                alts_list.append({"id": f"alt_{idx}", "text": text, "correct": (idx == correct_idx)})
            ex["alternativas"] = alts_list
            
        elif tipo == "ExercicioCombinar":
            pares = []
            for idx, (esq, drt) in enumerate(specific_data.get("pairs", [])):
                if esq and drt:
                    pares.append({
                        "pairId": f"par_{idx}", "positionFirst": idx+1, "positionSecond": idx+5,
                        "first": {"id": f"c_{idx}_1", "text": esq},
                        "second": {"id": f"c_{idx}_2", "text": drt}
                    })
            ex["pares"] = pares
            
        elif tipo == "ExercicioGramatica":
            ex["pontosGramaticais"] = [{
                "point": specific_data.get("gram_point", ""), 
                "description": specific_data.get("gram_desc", "")
            }]
        elif tipo == "RevisaoVocabulario":
            ex["backText"] = specific_data.get("back_text", "")

        if self.course_repo.write_data(data): return True, "Exercício salvo com sucesso!"

        

        if self.course_repo.write_data(data): return True, "Exercício salvo com sucesso!"
        return False, "Erro ao atualizar exercício."

    def delete_unit(self, lang_id: str, unit_number: int) -> Tuple[bool, str]:
        data = self.course_repo.read_data()
        idioma = data.get("idiomas", {}).get(lang_id)
        if not idioma: return False, "Idioma não encontrado."
        
        idioma["unidades"] = [u for u in idioma.get("unidades", []) if u["number"] != unit_number]
        if self.course_repo.write_data(data): return True, "Unidade removida."
        return False, "Erro ao remover unidade."

    def delete_exercise(self, lang_id: str, unit_num: int, lesson_id: str, ex_id: str) -> Tuple[bool, str]:
        data = self.course_repo.read_data()
        idioma = data.get("idiomas", {}).get(lang_id)
        unidade = next((u for u in idioma.get("unidades", []) if u["number"] == unit_num), None) if idioma else None
        licao = next((l for l in unidade.get("licoes", []) if l["lessonId"] == lesson_id), None) if unidade else None
        if not licao: return False, "Lição não encontrada."
        
        licao["exercicios"] = [e for e in licao["exercicios"] if e["exerciseId"] != ex_id]
        
        # Reajusta as posições após a remoção
        for i, ex in enumerate(licao["exercicios"]):
            ex["position"] = i + 1
            
        if self.course_repo.write_data(data): return True, "Exercício removido."
        return False, "Erro ao remover exercício."