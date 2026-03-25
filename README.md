# Rappi Delivery Operations Case - Monterrey

Sistema de Alertas Operacionales con AI para la detección proactiva de saturación en la operación de delivery de Rappi en Monterrey.

## Arquitectura del Proyecto

```
rappi-case/
├── data/                          # Dataset operacional (RAW_DATA, ZONE_INFO, ZONE_POLYGONS)
├── modulo1_diagnostico/           # Notebook + justificación técnica
├── modulo2_motor_alertas/         # Motor de decisión con Open-Meteo
├── modulo3_agente_telegram/       # Agente AI (Gemini) + Telegram
├── requirements.txt               # Dependencias globales
└── README.md
```

* **modulo1_diagnostico/**: Diagnóstico analítico. Notebook con hallazgos del "Efecto Tijera", vulnerabilidad por zona (Betas), y eficiencia de earnings.
* **modulo2_motor_alertas/**: Motor de alertas preventivas. Script que consulta Open-Meteo y aplica umbrales diferenciados por zona calibrados con el Módulo 1.
* **modulo3_agente_telegram/**: Agente AI. Gemini 2.0 Flash (OpenRouter) genera mensajes accionables en <10 seg y los despacha a Telegram. Incluye resumen diario al cierre.

---

## Instalación

```bash
# 1. Clonar repositorio
git clone https://github.com/DiegoOLopez/rappi_delivery_case.git
cd rappi_delivery_case

# 2. Crear y activar entorno virtual
python3 -m venv venv
source venv/bin/activate    # Mac/Linux
# .\venv\Scripts\activate   # Windows

# 3. Instalar dependencias
pip install -r requirements.txt
```

---

## Configurar Bot de Telegram (Módulo 3)

Para que el agente envíe mensajes a Telegram, necesitas un bot y un canal/chat destino:

### Paso 1: Crear el bot con BotFather
1. En Telegram, busca a **@BotFather** y abre un chat con él.
2. Envía el comando `/newbot`.
3. Sigue las instrucciones: elige un nombre y un username (debe terminar en `bot`).
4. BotFather te dará un **token** con formato `123456789:ABCdefGHI...`. Guárdalo.

### Paso 2: Obtener el CHAT_ID del canal o usuario
**Opción A — Tu ID personal:** Busca a **@myidbot** en Telegram, inicia chat y envía `/getid`. Te dará tu ID numérico.

**Opción B — ID de un canal:** Reenvía un mensaje del canal a **@myidbot**. El bot te responderá con el ID del canal (empieza con `-100...`). Asegúrate de haber añadido tu bot como administrador del canal.

### Paso 3: Configurar las variables de entorno
Copia el archivo de ejemplo y completa tus datos:
```bash
cp modulo3_agente_telegram/.env.example modulo3_agente_telegram/.env
```
Edita el `.env`:
```env
TOKEN_TELEGRAM="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
CHAT_ID="-1001234567890"
OPENROUTER_KEY="sk-or-v1-tu-llave-aqui"
```
> La clave de OpenRouter se obtiene en [openrouter.ai/keys](https://openrouter.ai/keys) (registro gratuito).

---

## Quick Run: Los 3 Módulos

### Módulo 1 — Diagnóstico (Notebook)
```bash
jupyter notebook
# Abrir modulo1_diagnostico/01_operational_diagnosis.ipynb → Cell > Run All
```

### Módulo 2 — Motor de Alertas (Consola)
```bash
cd modulo2_motor_alertas
python3 02_alert_engine.py                  # Datos reales de Open-Meteo
# python3 -c "from alert_engine_02 import *; run_alert_engine(simulate_rain=True)"  # Simulación
```

### Módulo 3 — Agente Telegram (Demo en vivo)
```bash
cd modulo3_agente_telegram
python3 03_agent_telegram.py
# El agente enviará alertas reales a Telegram y se repetirá cada 10 min.
# Presiona Ctrl+C para generar el Resumen Diario de cierre.
```

---

## Decisiones Técnicas Relevantes

### ¿Por qué Open-Meteo?
Unidades compatibles (mm/hr), consulta por coordenadas exactas, sin API key, baja latencia. Documentado en `modulo2_motor_alertas/02_justificacion_modulo_2.md`.

### ¿Por qué centroides en lugar de point-in-polygon?
Open-Meteo acepta coordenadas puntuales y devuelve un valor por punto. Dado que consultamos directamente los 14 centroides de `ZONE_INFO.csv`, cada respuesta ya está mapeada 1:1 a su zona operacional sin ambigüedad. El check point-in-polygon (shapely + `ZONE_POLYGONS`) sería necesario si el API devolviera datos en una grid geográfica que necesita resolverse a qué zona pertenece cada punto.

### Costo estimado de API
* **Open-Meteo:** $0.00 USD (gratuito, sin API key).
* **Gemini 2.0 Flash (OpenRouter):** ~$0.000055 USD por alerta. Un mes completo con 50 alertas: ~$0.003 USD.
* **Telegram Bot API:** $0.00 USD (gratuito).

---

## Stack Tecnológico
Python 3.9 · Pandas · Matplotlib · Seaborn · Shapely · Requests · OpenAI SDK (OpenRouter) · Gemini 2.0 Flash · Telegram Bot API · Open-Meteo API
