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
