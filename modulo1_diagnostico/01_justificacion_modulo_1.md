# Módulo 1: Diagnóstico Operacional - Justificación Técnica

## 1. Enfoque Metodológico
El diagnóstico se desarrolló sobre un enfoque cuantitativo buscando entender las variables críticas que detonan la saturación en la operación (ratio > 1.8). Se priorizó pasar de métricas de vanidad a la identificación de causas raíz accionables.

## 2. Hallazgos Fundamentales

### 2.1. El "Efecto Tijera" Pluvial
Se demostró que la lluvia no afecta la operación de manera simétrica. Al cruzar el umbral de **2.0 mm/hr**, ocurre una desconexión crítica:
* **Demanda:** Se dispara un **154.2%**.
* **Oferta:** Solamente crece un **40.4%**.
Este "Efecto Tijera" es la principal causa exógena del colapso de ratios en días de lluvia.

### 2.2. Saturación Estructural (Clima Seco)
El 46.3% de los episodios críticos ocurrieron sin lluvia, concentrándose rígidamente en ventanas bimodales:
* **Almuerzo:** 12:00 - 14:00
* **Cena:** 19:00 - 21:00
Esto indica que el sistema adolece de una saturación de capacidad recurrente, no solo de choques externos climáticos.

### 2.3. Vulnerabilidad Geográfica y Betas Clínicos
No todas las zonas resisten igual el estrés. A través de un modelo de **Regresión Lineal Simple**, se estimó la sensibilidad (Coeficiente β) de cada zona ante la lluvia:
* **Santiago (β = 0.27) y Carretera Nacional (β = 0.21)** son extremadamente frágiles. 
* Santiago puede colapsar a un ratio de 2.8 incluso sin lluvia, debido a su bajísima densidad de flota base (promedio de 4.58 repartidores). Cualquier pico de órdenes destruye el ratio local.

## 3. Eficiencia de la Inversión (Earnings)
El análisis cruzó el umbral de pago vs. el ratio operacional para determinar el ROI del gasto en incentivos.

* **Inelasticidad en Clima Seco:** Se observó un patrón *reactivo*, donde los earnings de nivel Premium sólo se activaban cuando el ratio ya estaba rebasando el **2.5** (colapso inminente).
* **Alta Efectividad Bajo Lluvia:** Se encontró una correlación negativa de **-0.25**. Bajo estrés climático severo, la única forma de mitigar el Efecto Tijera e incentivar a la flota fue elevando los earnings a niveles de compensación premium (~$78 - $85 MXN).
* **Fuga de Capital:** Se evidenció ineficiencia los fines de semana (ej. 18 y 24 de mayo), donde se pagó tarifa alta en zonas de sobreoferta (Ratio < 0.8), sugiriendo que el presupuesto es fijo o está mal automatizado.

## 4. Conclusión Estratégica
La operación de Monterrey no requiere más presupuesto general, requiere un despliegue **dinámico, asimétrico y basado en alertas**. La zona de Santiago requiere un aumento estructural de flota base (retos de conexión), y los incentivos de lluvia deben activarse preventivamente usando Open-Meteo antes de que el Ratio llegue a 2.5, escalonando los pagos según la vulnerabilidad regional detectada.
