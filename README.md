# WhisperPy

Aplicación gráfica básica para pruebas con Whisper.

## Requisitos

- Python 3.8 o superior
- Bibliotecas `requests` y `openai-whisper`
- (Opcional) crear un entorno virtual llamado `WhispVenv` en la carpeta del programa

## Ejecución

1. Instalar las dependencias (preferiblemente en un entorno virtual):
   ```bash
   python -m venv WhispVenv
   source WhispVenv/bin/activate  # En Windows: WhispVenv\Scripts\activate
   pip install requests openai-whisper
   ```

2. Ejecutar la aplicación:
   ```bash
   python main.py
   ```
   Al ejecutarse, `main.py` creará si es necesario el entorno `WhispVenv`
   y reiniciará la aplicación dentro de él.

Al abrir la aplicación, el desplegable de modelos indica con "(local)" los
modelos que ya se encuentran descargados en la carpeta `models`.

## Guía para desarrolladores

### Estructura del código

El proyecto se divide en varios módulos principales:

- **`main.py`**: punto de entrada. Crea (si es necesario) el directorio
  `WhispVenv`, instala las dependencias y relanza el programa con ese
  intérprete antes de mostrar la interfaz gráfica.
- **`gui.py`**: define la clase `WhisperGUI`, que construye la interfaz
  basada en Tkinter. Gestiona la selección de archivos y opciones y lanza
  la transcripción en un hilo para evitar bloqueos.
- **`model_manager.py`**: incluye la clase `WhisperModelManager` que
  obtiene la lista de modelos remotos y detecta modelos locales en la
  carpeta `models`. La GUI marca como "(local)" aquellos modelos ya
  descargados.
- **`transcriber.py`**: contiene la función `transcribe_audio` encargada de
  invocar la CLI de Whisper y manejar los archivos de salida. Si no se
  indica un entorno virtual, utiliza el mismo intérprete de Python que
  ejecuta la aplicación para evitar problemas con rutas con espacios.
- **`env_manager.py`**: ofrece la clase `EnvironmentManager` para crear y
  preparar entornos virtuales.

### Clases y funciones destacadas

- **`prepare_env()`** (`main.py`): prepara el entorno `WhispVenv`,
  instalando dependencias y relanzando la aplicación dentro de él.
- **`WhisperGUI`** (`gui.py`): interfaz con métodos para seleccionar
  archivos (`seleccionar_archivo`), iniciar la tarea de transcripción
  (`iniciar_transcripcion`) y manejar el resultado.
- **`WhisperModelManager.get_available_models()`** (`model_manager.py`):
  devuelve un diccionario con los modelos disponibles combinando locales y
  remotos.
- **`transcribe_audio()`** (`transcriber.py`): ejecuta Whisper mediante
  `subprocess`, mueve el archivo de salida y devuelve la ruta final.
- **`EnvironmentManager`** (`env_manager.py`): ofrece `create_env` para
  crear un entorno virtual y `install_dependencies` para instalar paquetes
  en él.

Cada módulo está pensado para ser sencillo y fácilmente ampliable. Las
funciones y clases mencionadas son el punto de extensión principal del
programa.
