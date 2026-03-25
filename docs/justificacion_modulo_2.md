# Módulo 2: Motor de Alertas Tempranas - Justificación Técnica

Este documento detalla las decisiones de diseño y la lógica operativa implementada en el motor de alertas para la operación de Rappi en Monterrey.

---

## 1. Integración Climática: Selección de API
Para el monitoreo en tiempo real, se seleccionó el servicio de **Open-Meteo**.

### Razones de la elección:
* **Alineación de Unidades (mm/hr):** La API entrega la precipitación en milímetros por hora, unidad exacta utilizada en el Diagnóstico Operacional (Módulo 1). Esto permite una integración directa de los umbrales de riesgo sin necesidad de conversiones propensas a errores.
* **Granularidad Geográfica:** Permite consultas precisas por coordenadas (Lat/Lon), facilitando el mapeo exacto de los 14 centroides de las zonas operacionales de Monterrey definidos en el dataset.
* **Performance:** Ofrece una respuesta en JSON estructurado de baja latencia, ideal para un sistema que requiere monitoreo constante y alertas inmediatas.
* **Reproducibilidad:** Al no requerir llaves de API (API Keys), garantiza que el script sea ejecutable de forma inmediata por cualquier auditor técnico.

---

## 2. Motor de Decisión: Reglas Operativas

El corazón del sistema se basa en patrones encontrados durante el análisis histórico para garantizar una respuesta proactiva ante la saturación.

### 2.1 Umbrales de Precipitación Diferenciados
El umbral no es el mismo para todas las zonas debido a la disparidad en la sensibilidad operativa detectada:

* **Zonas Sensibles (Santiago y Carretera Nacional):** El umbral es de **1.2 mm/hr**. Estas zonas tienen una densidad de flota base muy baja (promedio de 7.37 repartidores) y una sensibilidad (Beta) de 0.27. Un ligero incremento en la lluvia satura la zona mucho más rápido que en el centro.
* **Zonas Estándar (Resto de la ciudad):** El umbral es de **2.0 mm/hr**. Los datos históricos muestran que a partir de este nivel se genera el "Efecto Tijera", donde la demanda se dispara un 154% mientras la oferta solo crece un 40%.

### 2.2 Ventana de Anticipación (2 horas)
Se seleccionó una ventana de actuación de 2 horas basada en el siguiente balance:
* **Contraste:** Un pronóstico de 1 hora ofrece alta precisión pero deja un margen de maniobra insuficiente para que los repartidores reaccionen o se desplacen. Un pronóstico de 3 horas aumenta el riesgo de falsas alarmas por la incertidumbre meteorológica.
* **Decisión:** Las 2 horas representan el punto intermedio óptimo para influir efectivamente en la oferta sin sacrificar la fiabilidad del pronóstico.

### 2.3 Incremento de Earnings Recomendado
El valor específico establecido es de **78 MXN**. 
En el análisis histórico se observó que los incentivos de nivel "Premium" (que llevan el pago total a un promedio de 78 MXN) fueron los únicos capaces de romper la inelasticidad del sistema bajo lluvia, logrando reducir un ratio de saturación crítico a un nivel saludable.

### 2.4 Estrategia de Deduplicación e Idempotencia
Para evitar el spam de alertas y el agotamiento de la flota por notificaciones redundantes, el motor implementa una **máquina de estados**:
1. Una vez disparada una alerta, la zona entra en un registro de exclusión.
2. El motor no permite emitir una nueva alerta para esa zona hasta que:
    * Hayan transcurrido **4 horas** (periodo de enfriamiento operativo).
    * **O** las condiciones climáticas regresen a niveles normales (debajo del umbral), reseteando el monitor para detectar un nuevo evento climático independiente.