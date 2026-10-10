# Sistema de Gestión de Cursos y Estudiantes - Backend

API REST para la gestión académica de una institución educativa.

El backend permite administrar personas, distritos, alumnos, docentes, cursos y matrículas mediante una API desarrollada con Python y FastAPI.

La información se almacena en una base de datos PostgreSQL.

## Tecnologías

- Python
- FastAPI
- Pydantic
- PostgreSQL
- psycopg2
- Uvicorn

## Funcionalidades

El backend permite realizar operaciones CRUD sobre las principales entidades del sistema.

### Personas

- Registrar personas
- Listar personas
- Buscar personas
- Buscar por ID
- Buscar por DNI
- Buscar por correo
- Actualizar personas
- Eliminar personas
- Validar DNI único
- Validar correo único

### Distritos

- Registrar distritos
- Listar distritos
- Buscar distritos
- Buscar por ID
- Actualizar distritos
- Eliminar distritos

### Alumnos

- Registrar alumnos
- Listar alumnos
- Buscar alumnos
- Buscar por ID
- Actualizar alumnos
- Eliminar alumnos
- Relacionar alumnos con personas
- Relacionar alumnos con distritos

### Docentes

- Registrar docentes
- Listar docentes
- Buscar docentes
- Buscar por ID
- Actualizar docentes
- Eliminar docentes
- Gestionar especialidad
- Relacionar docentes con personas

### Cursos

- Registrar cursos
- Listar cursos
- Buscar cursos
- Buscar por ID
- Actualizar cursos
- Eliminar cursos
- Gestionar créditos
- Gestionar ciclo
- Gestionar horas semanales
- Asignar docentes

### Matrículas

- Registrar matrículas
- Listar matrículas
- Buscar matrículas
- Buscar por ID
- Actualizar matrículas
- Eliminar matrículas
- Registrar fecha de matrícula
- Gestionar estado de matrícula
- Relacionar alumnos con cursos

Los estados disponibles son:

```text
ACTIVO
RETIRADO
FINALIZADO
```

### Historial

El backend también dispone de funcionalidades para registrar y consultar las actividades realizadas dentro del sistema.

## Arquitectura

El backend está organizado por capas para separar las responsabilidades de cada componente.

```text
Backend/
│
├── config/
│   └── base_datos.py
│
├── Dao/
│   ├── alumno_dao.py
│   ├── cursos_dao.py
│   ├── distrito_dao.py
│   ├── docente_dao.py
│   ├── matricula_dao.py
│   └── persona_dao.py
│
├── models/
│   ├── alumno.py
│   ├── curso.py
│   ├── distrito.py
│   ├── docente.py
│   ├── matricula.py
│   └── persona.py
│
├── routers/
│   ├── alumnos.py
│   ├── cursos.py
│   ├── distritos.py
│   ├── docentes.py
│   ├── logs.py
│   ├── matriculas.py
│   └── personas.py
│
├── schemas/
│   ├── alumno_schema.py
│   ├── curso_schema.py
│   ├── distrito_schema.py
│   ├── docente_schema.py
│   ├── matricula_schema.py
│   └── persona_schema.py
│
├── main.py
└── requirements.txt
```

## Descripción de las capas

### Config

Contiene la configuración necesaria para establecer la conexión con PostgreSQL.

### Models

Representan las entidades utilizadas por el sistema.

### Schemas

Definen y validan la estructura de los datos recibidos y enviados por la API mediante Pydantic.

### DAO

Contienen las operaciones relacionadas con el acceso y manipulación de los datos en PostgreSQL.

### Routers

Definen los endpoints de la API y conectan las solicitudes HTTP con las operaciones correspondientes.

### Main

Es el punto de entrada de la aplicación FastAPI.

## Base de datos

El proyecto utiliza PostgreSQL.

Las principales tablas son:

```text
distrito
persona
alumno
docente
curso
matricula
```

El script de creación de la base de datos se encuentra en:

```text
db_gestion_cursos_estudiantes.sql
```

## Requisitos

Antes de ejecutar el proyecto se necesita:

- Python
- PostgreSQL
- pip

## Instalación

Se recomienda utilizar un entorno virtual.

### Crear entorno virtual

```bash
python -m venv venv
```

### Activar entorno virtual en Windows

```bash
venv\Scripts\activate
```

### Instalar dependencias

Las principales librerías utilizadas son:

```bash
python -m pip install psycopg2-binary
python -m pip install pydantic
python -m pip install fastapi
python -m pip install uvicorn
```

También se pueden instalar todas las dependencias mediante:

```bash
pip install -r requirements.txt
```

## Configuración de PostgreSQL

Se debe configurar la conexión a PostgreSQL en:

```text
config/base_datos.py
```

Verificar que:

- PostgreSQL esté ejecutándose.
- El nombre de la base de datos sea correcto.
- El usuario sea correcto.
- La contraseña sea correcta.
- El puerto sea correcto.

Después se debe ejecutar el script:

```text
db_gestion_cursos_estudiantes.sql
```

## Ejecución

Desde la carpeta del backend:

```bash
uvicorn main:app --reload
```

El servidor estará disponible normalmente en:

```text
http://127.0.0.1:8000
```

## Documentación de la API

FastAPI genera automáticamente la documentación.

### Swagger UI

```text
http://127.0.0.1:8000/docs
```

### ReDoc

```text
http://127.0.0.1:8000/redoc
```

Desde Swagger se pueden consultar y probar los endpoints disponibles.

## Endpoints principales

Los endpoints están organizados por módulos:

```text
/distritos/
/personas/
/alumnos/
/docentes/
/cursos/
/matriculas/
/logs/
```

Las operaciones principales utilizan:

```text
GET
POST
PUT
DELETE
```

También existen endpoints específicos para búsquedas y consultas por ID.

## Comunicación con el Frontend

El backend funciona como API REST para el frontend desarrollado en React.

El flujo de comunicación es:

```text
Frontend React
      |
      | HTTP / Axios
      v
FastAPI
      |
      | SQL
      v
PostgreSQL
```

El frontend realiza solicitudes HTTP al backend y este procesa las operaciones correspondientes sobre la base de datos.

## Validaciones

El sistema utiliza validaciones en diferentes niveles.

Entre ellas:

- Campos obligatorios
- DNI único
- Correo único
- Código de alumno único
- Claves primarias
- Claves foráneas
- Estados válidos de matrícula
- Validaciones mediante Pydantic
- Restricciones mediante PostgreSQL
