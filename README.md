# Examen Parcial 2 — Pipeline de Datos Contenerizado con Hadoop MapReduce y API REST

* **Estudiante:** Alberto Saúl López Crespo
* **Matrícula:** 125053374
* **Último dígito:** 4
* **Pregunta de Negocio Asignada:** Unidades vendidas por método de pago y día de la semana.
* **Dataset Procesado:** 5,000,000 de registros (`ventas_125053374.csv`, ~352 MB)

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
|  | python3 reducer    |      | GET  /resultados/:k|      |                   |  |
|  +--------------------+      +--------------------+      +-------------------+  |
|            |                           |                           |            |
+------------|---------------------------|---------------------------|------------+
             |                           |                           |             
      Host Volume:                Host Port:                  Host Port:          
       ./evidencias                 5000:5000                   3306:3306

       examen-p2-125053374/
├── api/
│   ├── app.py                  # API REST Flask con endpoints /cargar, /resultados y /resultados/<clave>
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


---

## 6. Respuestas Teóricas (Parte E)

### 1. Diferencia entre modos standalone, pseudo-distribuido y totalmente distribuido de Hadoop. ¿En cuál de ellos se usa HDFS?
* **Standalone (Modo Local):** Todos los componentes de Hadoop se ejecutan en una sola JVM. Lee y escribe directamente del sistema de archivos local de la máquina y no usa demonios de red.
* **Pseudo-distribuido:** Todos los demonios (NameNode, DataNode, ResourceManager, NodeManager) se ejecutan de manera concurrente en una sola máquina o contenedor, simulando un clúster distribuido completo mediante procesos y sockets independientes.
* **Totalmente Distribuido:** Los demonios se dividen y ejecutan en un clúster físico o virtualizado compuesto por múltiples nodos (maestro y múltiples trabajadores o workers).
* **¿En cuál se usa HDFS?** HDFS se utiliza en el modo **pseudo-distribuido** y en el modo **totalmente distribuido**. En standalone no se utiliza.

### 2. ¿Por qué el dataset se monta como volumen y no se copia dentro de la imagen con COPY? Menciona al menos dos razones.
1. **Eficiencia en el tamaño de la imagen y tiempos de build:** Copiar un archivo de más de 350 MB inflaría innecesariamente el tamaño de la imagen Docker en una capa estática, haciendo que cada compilación (`docker build`) y descarga sea excesivamente pesada y lenta.
2. **Inmutabilidad y desacoplamiento de datos:** Los contenedores deben mantenerse como componentes inmutables (código y dependencias). Montar el dataset como volumen desacopla el ciclo de vida del dato del ciclo de vida del software, permitiendo modificar, renovar o limpiar el archivo CSV sin necesidad de recompilar la imagen de Hadoop.

### 3. ¿Qué ocurre con los datos de la base de datos al ejecutar `docker compose down`? ¿Y con `docker compose down -v`?
* Con **`docker compose down`**: Se detienen y eliminan los contenedores y la red creada, pero **los volúmenes nombrados (como `db_data`) se preservan intactos**. Al volver a levantar con `docker compose up`, la base de datos conserva todas sus tablas y registros.
* Con **`docker compose down -v`**: Además de remover los contenedores y redes, **se eliminan físicamente los volúmenes nombrados**, borrando por completo y de manera irreversible toda la información y bases de datos persistidas.

### 4. ¿Por qué MapReduce no siempre es más rápido que un script secuencial con un archivo de 400 MB? ¿A partir de qué condiciones conviene?
* MapReduce tiene una penalización por costo de arranque (*overhead*): tiempo de instanciación de la JVM, preparación de tareas, particionamiento en disco y la sincronización/ordenamiento en red (Shuffle & Sort). En archivos que caben cómodamente en memoria RAM (< 500 MB o 1 GB), un script secuencial en Python/Pandas puede ser más veloz al saltarse todo ese overhead de orquestación.
* MapReduce y el cómputo distribuido convienen cuando el tamaño del dataset excede la capacidad física de la memoria RAM del equipo (*Out of Memory*), requiriendo procesamiento fuera del búfer de memoria (*disk-spilling*), o cuando el volumen de datos alcanza decenas de gigabytes y terabytes repartidos en decenas o cientos de nodos paralelos.

### 5. Diferencia entre CMD y ENTRYPOINT, y entre COPY y ADD en Docker.
* **CMD vs ENTRYPOINT:** `ENTRYPOINT` establece el comando fijo ejecutable base del contenedor que no debería variar, mientras que `CMD` provee los parámetros o comandos predeterminados que pueden ser fácilmente sobreescritos desde la línea de comandos al ejecutar `docker run <imagen> [nuevo_comando]`.
* **COPY vs ADD:** `COPY` únicamente transfiere archivos o carpetas del host local hacia el sistema de archivos del contenedor. `ADD` incluye capacidades extras avanzadas: descomprime automáticamente archivos empaquetados locales (`.tar`, `.tar.gz`) en la carpeta destino y tiene la capacidad de descargar archivos desde URLs externas.