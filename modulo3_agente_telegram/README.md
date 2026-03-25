# Módulo 3: Agente Telegram de Operaciones

Este módulo orquesta el flujo de alertas climáticas usando un Agente Empoderado con el modelo **Gemini 2.0 Flash (vía OpenRouter)**, despachando Alertas Operativas configurables e inmediatas para los Operations Managers en campo mediante **Telegram**.

## Costo Estimado de API por Uso

El Agente es altamente eficiente en su consumo usando un modelo tier "Flash".

### Desglose de Operación (Por Alerta):
* **Open-Meteo API**: $0.00 USD (Servicio gratuito).
* **Gemini 2.0 Flash (OpenRouter)**: 
  * Prompt promedio (Input): ~400 tokens
  * Respuesta generada (Output): ~100 tokens
  * **Tarifa (Input/Output)**: ~$0.10 input / $0.15 output por millón de tokens.
  * **Costo USD por Alerta:** `$0.00004` + `$0.000015` = **~$0.000055 USD**.

Al usar encadenamiento lógico optimizado en el formato del prompt y cálculo pre-renderizado (el LLM no "piensa" números, solo formatea y evalúa estado), generar un mes completo con 50 alertas operacionales costaría **menos de un centavo de dólar** (~$0.002 USD).

---

## Instrucciones de Reproducción

### 1. Variables de Entorno
Crea o edita el archivo `.env` en la misma carpeta (`modulo3_agente_telegram/.env`) con tus credenciales:

```env
TOKEN_TELEGRAM="tu-token-aqui"
CHAT_ID="tu-chat-id-aqui"
OPENROUTER_KEY="tu-openrouter-key-aqui"
```

### 2. Ejecutar el Agente Continuo
Enciende el entorno e inicia el script principal en la terminal. El agente entrará en un bucle (`polling`) de inspección continua a intervalos de 10 minutos.

```bash
cd modulo3_agente_telegram
python3 03_agent_telegram.py
```

### 3. Modo Simulación
Si tu entorno se encuentra seco pero quieres visualizar el comportamiento de una lluvia crítica (ej. Santiago a 6.5 mm/hr):
1. Por defecto, en el bloque `if __name__ == "__main__":`, la simulación viene activa y lista para la entrevista: `correr_agente(simulate=True)`. Solo ejecútalo.

### 4. Generar el "Corte de Caja" (Demo en Vivo)
El script incluye una captura especial (graceful shutdown). Cuando estés corriendo el modelo en loop y decidas parar la demostración en tu entrevista:

1. Presiona **`Ctrl + C`** en la consola donde corre el agente.
2. El sistema atrapará la interrupción manualmente y compilará la lista local de eventos (alertas emitidas durante esa sesión).
3. Generará y enviará al instante un **Mensaje Ejecutivo de Resumen Diario** al Telegram, cerrando con profesionalismo la demostración.
