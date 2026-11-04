import json
import os
from typing import Dict, Any

class BaseRepository:
    def __init__(self, filepath: str):
        self.filepath = filepath

    def read_data(self) -> Dict[str, Any]:
        """Lê o arquivo JSON e retorna um dicionário."""
        if not os.path.exists(self.filepath):
            return {}
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            print(f"Erro ao ler {self.filepath}: {e}")
            return {}

    def write_data(self, data: Dict[str, Any]) -> bool:
        """Escreve um dicionário no arquivo JSON."""
        # Garante que o diretório existe
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except OSError as e:
            print(f"Erro ao escrever em {self.filepath}: {e}")
            return False
