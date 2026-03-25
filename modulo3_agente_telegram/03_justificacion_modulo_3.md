# Módulo 3: Agente AI de Operaciones - Justificación Técnica

## 1. Objetivo y Alcance
El **Agente AI de Operaciones** es una solución proactiva que cierra la brecha entre el diagnóstico analítico y la ejecución en campo. El sistema monitorea en tiempo real las 14 zonas de Monterrey mediante la API de **Open-Meteo** y procesa la toma de decisiones utilizando el modelo **Gemini 2.0 Flash** (vía OpenRouter) para emitir alertas accionables en menos de 10 segundos.

## 2. Inyección de Inteligencia (Contexto Módulo 1)
A diferencia de un bot genérico, este agente integra los hallazgos del diagnóstico operativo en su motor de reglas y en el diccionario de **`ZONE_INTELLIGENCE`**:
* **Sensibilidad Calibrada:** Utiliza los coeficientes **Beta** (lluvia → ratio) calculados en el Módulo 1 para proyectar el impacto exacto en la saturación.
* **Efecto Tijera:** El agente comunica el desbalance específico entre el *Demand Surge* y el *Supply Surge* de cada zona (ej. Santiago con +110% de demanda vs +8.7% de oferta bajo lluvia).
* **Umbrales Diferenciados:** Se implementó un disparador de **1.2 mm/hr** para zonas críticas y **2.0 mm/hr** para zonas estándar, optimizando el despliegue de capital.

## 3. Diseño del Mensaje (Regla de los 10 Segundos)
El formato de salida en **HTML para Telegram** prioriza la jerarquía visual para un Operations Manager en movimiento:
* **Jerarquía de Riesgo:** Clasificación inmediata (CRÍTICO/ALTO/MEDIO) con emojis tácticos.
* **Acción Imperativa:** Se eliminó el lenguaje ambiguo. El agente ordena subir los earnings de **$55 a un monto específico ($70, $78 o $85 MXN)** validado en el modelo de elasticidad del Módulo 2.
* **Ventana de Actuación:** El sistema calcula la proximidad a los picos de saturación de Monterrey (almuerzo/cena) para determinar la urgencia de la maniobra.

## 4. Arquitectura y Escalabilidad (Q&A)

* **¿Cómo maneja los falsos positivos?** El sistema opera en un bucle de **polling de 10 minutos**. Si el pronóstico de lluvia desaparece o baja del umbral en la siguiente actualización de la API, el agente limpia el estado de la zona y no dispara la alerta, protegiendo el P&L de la compañía.
* **¿Cómo evita el 'Alert Fatigue'?** Se implementó una **estrategia de idempotencia con cooldown de 4 horas**. Una vez emitida una alerta, el sistema silencia la zona para evitar spam, asegurando que cada notificación sea crítica y de alta prioridad.
* **¿Cómo escalaría a otras ciudades?** La arquitectura es **Data-Driven y agnóstica a la ubicación**. Para expandir a CDMX o Lima, solo se requiere actualizar el archivo `ZONE_INFO.csv` y alimentar los coeficientes de sensibilidad local en el diccionario de inteligencia. El motor de clima y el LLM tienen cobertura global.

## 5. Implementación de Bonus
* **Memoria del Agente:** Registro persistente de alertas enviadas para evitar duplicidad.
* **Nivel de Alerta Diferenciado:** Lógica de negocio ajustada por la vulnerabilidad detectada en el diagnóstico inicial.
* **Resumen Diario:** Generación automática de un reporte ejecutivo (vía IA) al cierre de la jornada que resume las zonas afectadas y las acciones económicas tomadas para estabilizar la operación.

---
**Costo Operativo Estimado:** ~$0.00015 USD por alerta generada.
**Stack:** Python 3.9, Pandas, Open-Meteo API, Gemini 2.0 Flash, Telegram Bot API.