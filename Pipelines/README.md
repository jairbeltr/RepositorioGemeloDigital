# Pipelines

Conjunto de *pipelines* desarrollados en **Jupyter Notebook** para el procesamiento y análisis de datos del **Gemelo Digital para Servicios de Urgencias**.  
Estos notebooks fueron ejecutados localmente y exportados como archivos **HTML** para visualización directa en GitHub, sin requerir entorno Jupyter.

---

## 📊 Propósito general

Los *pipelines* conforman la fase analítica del proyecto y representan el flujo completo de datos desde su origen hasta la evaluación del modelo predictivo de clasificación responsable de identificar si los tiempos de atención cumplen con los parámetros establecidos para pacientes de **Triage III (≤ 2 h)**.

---

## 📁 Estructura

| Archivo | Descripción |
|---|---|
| **prepro.html** | Etapa de **preprocesamiento**. Limpieza inicial, anonimización y estandarización de las tablas hospitalarias (Atención, Triage, Evolución, Interconsultas). |
| **join.html** | **Integración de datos**. Unificación de las tablas en un único dataset `mh.csv` mediante llaves de paciente y fecha. |
| **check.html** | **Validación de consistencia**. Revisión de valores nulos, tiempos negativos y coherencia temporal. Genera el dataset validado `mh_features_checked.csv`. |
| **exploration.html** | **Modelado y evaluación**. Entrenamiento de algoritmos de clasificación (Logistic Regression, LightGBM, XGBoost) y comparación de métricas. |

---

## ⚙️ Requisitos originales

Estos notebooks fueron desarrollados en **Jupyter Notebook (Visual Studio Code)** con:
- Python 3.9+
- Librerías principales:
  ```bash
  pip install pandas numpy scikit-learn matplotlib seaborn lightgbm xgboost
