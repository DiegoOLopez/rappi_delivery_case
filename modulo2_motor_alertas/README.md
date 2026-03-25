# Módulo 2: Motor de Alertas (Alert Engine)

Este módulo evalúa las condiciones climáticas futuras (próximas 2 horas) de las 14 zonas operativas utilizando la API de Open-Meteo, y diagnostica el riesgo de saturación basándose en el análisis efectuado en el diagnóstico del Módulo 1.

## Instrucciones de Reproducción

### Requisitos
1. Python 3.9+
2. Las dependencias deben estar instaladas en el entorno virtual (`pip install -r ../requirements.txt`).

### Ejecución Básica
Desde la terminal, ubicado en la carpeta del script:

```bash
cd modulo2_motor_alertas
python3 02_alert_engine.py
```

### Ejecutar en Modo Simulación
Dado que la probabilidad de lluvia activa en tiempo real de la evaluación no está garantizada, puedes ejecutar la lógica forzando datos simulados de lluvia intensa.

1. Abre `02_alert_engine.py`.
2. Hacia el final del archivo, en el bloque `if __name__ == '__main__':`, comenta la ejecución real y descomenta la simulada:
   ```python
   run_alert_engine(simulate_rain=True)
   # run_alert_engine()
   ```
3. Ejecuta el script de nuevo. Evaluará internamente un evento de lluvia intensa en la zona de `Santiago` y disparará la lógica de la alerta por la consola.

---
**Nota:** Este script emite sus alertas e insights a través de la consola local (`stdout`). Para el despliegue con agentes generativos (Gemini) e integración con plataformas sociales (Telegram), consulta el **Módulo 3**.
