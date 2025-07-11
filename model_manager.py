import os
from typing import Dict

try:
    import requests
except Exception:  # requests may be missing
    requests = None

class WhisperModelManager:
    """Gestiona los modelos de Whisper disponibles."""

    FALLBACK_MODELS: Dict[str, str] = {
        "tiny": "Muy rápido, baja precisión (~39 MB) - Ideal para pruebas rápidas",
        "base": "Rápido con precisión media (~74 MB) - Uso general",
        "small": "Equilibrio entre velocidad y precisión (~244 MB) - Proyectos medianos",
        "medium": "Alta precisión, más lento (~769 MB) - Transcripciones detalladas",
        "large": "Máxima precisión, muy lento (~1.5 GB) - Mejor para audios complejos",
    }

    @staticmethod
    def obtener_modelos_online() -> Dict[str, str]:
        """Obtiene la lista de modelos desde HuggingFace.

        Si la biblioteca ``requests`` no está disponible o sucede un error de
        red, se devuelven los modelos de :data:`FALLBACK_MODELS`.
        """
        if requests is None:
            return WhisperModelManager.FALLBACK_MODELS
        try:
            url = "https://huggingface.co/api/models?search=openai/whisper"
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            modelos = {
                m["id"].replace("openai/whisper-", ""): WhisperModelManager.FALLBACK_MODELS.get(
                    m["id"].split("-")[-1], "Modelo disponible"
                )
                for m in data
                if "openai/whisper-" in m.get("id", "")
            }
            return modelos or WhisperModelManager.FALLBACK_MODELS
        except Exception:
            # Ante cualquier problema de red se devuelven los modelos por defecto
            return WhisperModelManager.FALLBACK_MODELS

    @staticmethod
    def _modelos_locales() -> Dict[str, str]:
        """Busca modelos disponibles localmente."""
        modelos = {}

        dirs = [
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "models"),
        ]

        for directorio in dirs:
            if os.path.isdir(directorio):
                for archivo in os.listdir(directorio):
                    if archivo.endswith(".pt"):
                        nombre = os.path.splitext(archivo)[0]
                        modelos[nombre] = f"Modelo local disponible ({archivo})"

        return modelos

    @classmethod
    def get_available_models(cls) -> Dict[str, str]:
        """Combina modelos locales con los remotos.

        Si ocurre un error de red al consultar los remotos se devuelven los
        modelos de :data:`FALLBACK_MODELS`.
        """
        locales = cls._modelos_locales()
        try:
            remotos = cls.obtener_modelos_online()
        except Exception:
            remotos = cls.FALLBACK_MODELS
        modelos = {**remotos, **locales}
        return modelos or cls.FALLBACK_MODELS
    
    @classmethod
    def delete_local_model(cls, model_name: str) -> bool:
        """
        Intenta eliminar un modelo localmente.
        Retorna True si se eliminó, False si no se encontró o hubo error.
        """
        deleted = False
        # Rutas donde buscar el modelo
        dirs = [
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "models"),
            os.path.join(os.path.expanduser("~"), ".cache", "whisper"),
        ]

        for directorio in dirs:
            model_file_path = os.path.join(directorio, f"{model_name}.pt")
            if os.path.exists(model_file_path):
                try:
                    os.remove(model_file_path)
                    print(f"Modelo '{model_name}' eliminado de {directorio}")
                    deleted = True
                    # No retornar aquí, para buscar y borrar en ambas ubicaciones si existe duplicado
                except Exception as e:
                    print(f"Error al eliminar el modelo '{model_name}' de {directorio}: {e}")
        return deleted