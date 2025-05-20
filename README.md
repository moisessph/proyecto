# Sistema de Llamadas Paciente-Enfermero

Este sistema permite registrar llamadas y presencias desde habitaciones hacia un servidor central. Las llamadas:
- Se registran en una base de datos SQLite.
- Envían una notificación a la app Pushover del asistente.
- Encienden o apagan pilotos LED con relés WiFi.

## Pasos para usar

1. Crear entorno virtual:
   python -m venv venv

2. Activarlo:
   .\venv\Scripts\activate

3. Instalar dependencias:
   pip install -r requirements.txt

4. Ejecutar el servidor Flask:
   cd api
   python main.py

5. Probar en navegador:
   http://localhost:5000/llamada/101/a
