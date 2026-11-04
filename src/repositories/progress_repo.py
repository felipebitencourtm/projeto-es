import json
from typing import Dict, List, Any
from src.repositories.base_repository import BaseRepository
from src.models.progress import ProgressoIdioma, ProgressoLicao, SessaoSrs, EstadoRevisao

class ProgressRepository(BaseRepository):
    def __init__(self, filepath: str = "data/progresso.json"):
        super().__init__(filepath)

    def get_student_progress(self, student_id: str) -> Dict[str, ProgressoIdioma]:
        """Lê o ficheiro e devolve o progresso de todos os idiomas para um aluno específico."""
        data = self.read_data()
        alunos_data = data.get("progresso_alunos", {})
        aluno_progresso = alunos_data.get(student_id, {}).get("progressosIdioma", {})
        
        progressos_instanciados = {}
        for lang_id, lang_data in aluno_progresso.items():
            # 1. Instanciar Progressos de Lição
            licoes = {}
            for lesson_id, licao_data in lang_data.get("progressosLicao", {}).items():
                licoes[lesson_id] = ProgressoLicao(
                    complete=licao_data.get("complete", False),
                    completionDate=licao_data.get("completionDate")
                )
            
            # 2. Instanciar Sessões SRS
            sessoes = []
            for sessao_data in lang_data.get("sessoesSrs", []):
                estados = {}
                for ex_id, estado_data in sessao_data.get("estadosRevisao", {}).items():
                    estados[ex_id] = EstadoRevisao(
                        lastRecalledDate=estado_data["lastRecalledDate"],
                        easeFactor=estado_data.get("easeFactor", 2.5),
                        repetitions=estado_data.get("repetitions", 0),
                        interval=estado_data.get("interval", 0)
                    )
                sessoes.append(SessaoSrs(
                    sessionDate=sessao_data.get("date", ""),
                    estadosRevisao=estados
                ))
            
            # 3. Construir o Progresso do Idioma
            progressos_instanciados[lang_id] = ProgressoIdioma(
                lastCompletedLessonId=lang_data.get("lastCompletedLessonId"),
                completionDate=lang_data.get("completionDate"),
                progressosLicao=licoes,
                sessoesSrs=sessoes
            )
            
        return progressos_instanciados

    def save_student_progress(self, student_id: str, progressos: Dict[str, ProgressoIdioma]) -> bool:
        """Serializa os objetos de progresso e guarda no ficheiro JSON."""
        data = self.read_data()
        
        if "progresso_alunos" not in data:
            data["progresso_alunos"] = {}
            
        if student_id not in data["progresso_alunos"]:
            data["progresso_alunos"][student_id] = {"progressosIdioma": {}}
            
        serialized_progressos = {}
        for lang_id, prog_idioma in progressos.items():
            # Serializa Progresso de Lições
            serialized_licoes = {}
            for lesson_id, licao in prog_idioma.progressosLicao.items():
                serialized_licoes[lesson_id] = {
                    "complete": licao.complete,
                    "completionDate": licao.completionDate
                }
                
            # Serializa Sessões SRS
            serialized_sessoes = []
            for sessao in prog_idioma.sessoesSrs:
                serialized_estados = {}
                for ex_id, estado in sessao.estadosRevisao.items():
                    serialized_estados[ex_id] = {
                        "lastRecalledDate": estado.lastRecalledDate,
                        "easeFactor": estado.easeFactor,
                        "repetitions": estado.repetitions,
                        "interval": estado.interval
                    }
                serialized_sessoes.append({
                    "date": sessao.sessionDate,
                    "estadosRevisao": serialized_estados
                })
                
            serialized_progressos[lang_id] = {
                "lastCompletedLessonId": prog_idioma.lastCompletedLessonId,
                "completionDate": prog_idioma.completionDate,
                "progressosLicao": serialized_licoes,
                "sessoesSrs": serialized_sessoes
            }
            
        data["progresso_alunos"][student_id]["progressosIdioma"] = serialized_progressos
        
        return self.write_data(data)