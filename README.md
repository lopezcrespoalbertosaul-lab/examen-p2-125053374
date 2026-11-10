# Examen Parcial 2 — Pipeline de Datos Contenerizado con Hadoop MapReduce y API REST

* **Estudiante:** Alberto Saúl López Crespo
* **Matrícula:** 125053374
* **Fecha:** Noviembre 2026
* **Dataset Procesado:** 5,000,000 de registros (`ventas_125053374.csv`)

---

## 1. Arquitectura del Sistema

El pipeline implementa una arquitectura multicapa distribuida y contenerizada mediante Docker Compose, compuesta por tres servicios interconectados a través de una red virtual tipo puente (`pipeline-net`):

```text
+---------------------------------------------------------------------------------+
|                                 pipeline-net                                    |
|                                                                                 |
|  +--------------------+      +--------------------+      +-------------------+  |
|  |  pipeline_hadoop   |      |    pipeline_api    |      |    pipeline_db    |  |
|  |  (Hadoop 3.3.6)    | ---> |   (Flask / REST)   | ---> |    (MySQL 8.0)    |  |
|  |                    |      |                    |      |                   |  |
|  | MapReduce Streaming|      | POST /cargar       |      | Tabla:            |  |
|  | python3 mapper     |      | GET  /resultados   |      |   resultados      |  |
|  | python3 reducer    |      |                    |      |                   |  |
|  +--------------------+      +--------------------+      +-------------------+  |
|            |                           |                           |            |
+------------|---------------------------|---------------------------|------------+
             |                           |                           |             
      Host Volume:                Host Port:                  Host Port:          
       ./evidencias                 5000:5000                   3306:3306




       examen-p2-125053374/
├── api/
│   ├── app.py                  # API REST Flask con endpoints /cargar y /resultados
│   ├── Dockerfile              # Construcción de la imagen API Python 3.11
│   └── requirements.txt        # Dependencias (Flask, PyMySQL, SQLAlchemy)
├── evidencias/
│   ├── 01_hadoop_ssh.png       # Verificación Hadoop 3.3.6 y SSH sin contraseña
│   ├── 02_mapreduce_job.png    # Salida y métricas del job MapReduce (5M registros)
│   ├── 03_salida_hadoop.png    # Inspección de part-00000 con los 28 grupos
│   └── 04_api_resultados.png   # Consulta GET /resultados validando persistencia
├── hadoop/
│   └── Dockerfile              # Entorno Hadoop 3.3.6, JDK 11 y SSH
├── mapreduce/
│   ├── mapper.py               # Extracción y emisión de tuplas (Método_Día, Monto)
│   ├── reducer.py              # Agrupación y suma de ventas por categoría
│   └── secuencial.py           # Script monolítico de benchmark en Python
├── scripts/
│   └── cargar_resultados.py    # Envío de part-00000 hacia el endpoint POST de la API
├── .env.example                # Plantilla de variables de entorno seguras
├── .gitignore                  # Exclusión de datasets pesados, .env y temporales
├── docker-compose.yml          # Orquestación de servicios, redes y volúmenes
├── generar_dataset.py          # Generador de los 5,000,000 registros sintéticos
└── README.md                   # Documentación técnica completa del proyecto