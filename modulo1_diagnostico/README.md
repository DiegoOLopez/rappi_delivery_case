# Módulo 1: Diagnóstico Operacional

En esta carpeta encontrarás el núcleo analítico de la investigación sobre la saturación logística en Monterrey para Rappi. 

Este análisis se realizó utilizando un Jupyter Notebook y métodos cuantitativos para aislar las variables críticas (precipitación, flota conectada y demanda). Todo esto concluye en el documento de `01_justificacion_modulo_1.md`.

## Instrucciones de Reproducción

### Requisitos
El entorno virtual raíz ya cuenta con las dependencias necesarias instaladas en el `requirements.txt` (`pandas`, `matplotlib`, `seaborn`, `jupyter`).

### Configuración y Ejecución
1. Si no lo has hecho, clona el repositorio e instala las dependencias:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Abre Jupyter Notebook desde la raíz del proyecto (para que encuentre la carpeta `data/` correctamente):
```bash
jupyter notebook
```

3. Navega en la interfaz del navegador hacia la carpeta `modulo1_diagnostico/` y abre el archivo `01_operational_diagnosis.ipynb`.
4. En el menú superior, presiona `Cell > Run All` (o similar, dependiendo de la versión de Jupyter) para ejecutar todos los bloques de código secuencialmente.
5. El output de cada análisis, las gráficas de correlación de estrés pluvial y la matriz de dispersión de incentivos se dibujarán correctamente al final del documento de forma interactiva.
