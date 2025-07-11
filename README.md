# WhisperPy

Aplicación gráfica básica para pruebas con Whisper.

## Requisitos

- Python 3.8 o superior
- Biblioteca `requests`
- (Opcional) crear un entorno virtual llamado `venv` en la carpeta del programa

## Ejecución

1. Instalar las dependencias (preferiblemente en un entorno virtual):
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   pip install requests
   ```

2. Ejecutar la aplicación:
   ```bash
   python main.py
   ```
   Si `main.py` detecta la carpeta `venv` y no se está dentro de un entorno
   virtual, reiniciará el programa utilizando ese entorno.

## Guía para desarrolladores

El proyecto se divide en varios módulos:

- **`main.py`**: punto de entrada de la aplicación. Comprueba si existe
  un directorio `venv` y vuelve a lanzar el script usando ese entorno si
  no se está ejecutando ya en él. Después crea la ventana principal y
  muestra la interfaz.
- **`gui.py`**: implementa la clase `WhisperGUI` basada en Tkinter. Permite
  seleccionar un archivo de audio, escoger modelo e idioma y opcionalmente
  usar el entorno `venv`. La transcripción se realiza en un hilo para no
  bloquear la interfaz.
- **`model_manager.py`**: contiene `WhisperModelManager`, encargado de
  obtener la lista de modelos disponibles desde HuggingFace y de detectar
  modelos locales en la carpeta `models`.
- **`transcriber.py`**: define la función `transcribe_audio` que invoca a
  Whisper mediante `subprocess` y devuelve el archivo de texto generado.
- **`env_manager.py`**: utilidades para crear un entorno virtual e instalar
  dependencias. Puede usarse para preparar el entorno `venv` antes de la
  ejecución.

Cada módulo está pensado para ser sencillo y fácilmente ampliable. Las
funciones y clases expuestas son el punto de extensión principal del
programa.
