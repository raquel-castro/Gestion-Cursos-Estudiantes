# Sistema de Gestión de Cursos y Estudiantes - Frontend

Interfaz web del Sistema de Gestión de Cursos y Estudiantes.

El frontend permite interactuar con el sistema académico mediante una interfaz desarrollada con React y Vite.

La aplicación se comunica con el backend mediante una API REST utilizando Axios.

## Tecnologías

- React
- Vite
- JavaScript
- Bootstrap
- Bootstrap Icons
- React Router DOM
- SweetAlert2
- Axios

## Funcionalidades

El frontend proporciona una interfaz para administrar los diferentes módulos del sistema.

### Personas

Permite:

- Registrar personas
- Listar personas
- Buscar personas
- Buscar por ID
- Buscar por DNI
- Buscar por correo
- Editar personas
- Eliminar personas
- Validar información
- Limpiar formularios

Los datos administrados incluyen:

- DNI
- Nombres
- Apellidos
- Teléfono
- Correo
- Dirección

### Distritos

Permite:

- Registrar distritos
- Listar distritos
- Buscar distritos
- Buscar por ID
- Editar distritos
- Eliminar distritos

### Alumnos

Permite:

- Registrar alumnos
- Listar alumnos
- Buscar alumnos
- Buscar por ID
- Buscar por código
- Buscar por DNI
- Buscar por nombre
- Buscar por distrito
- Editar alumnos
- Eliminar alumnos

### Docentes

Permite:

- Registrar docentes
- Listar docentes
- Buscar docentes
- Buscar por ID
- Buscar por especialidad
- Buscar por nombre
- Editar docentes
- Eliminar docentes

### Cursos

Permite:

- Registrar cursos
- Listar cursos
- Buscar cursos
- Buscar por ID
- Buscar por nombre
- Editar cursos
- Eliminar cursos
- Gestionar créditos
- Gestionar ciclo
- Gestionar horas semanales
- Asignar docentes

### Matrículas

Permite:

- Registrar matrículas
- Listar matrículas
- Buscar matrículas
- Buscar por ID
- Buscar por alumno
- Buscar por curso
- Editar matrículas
- Eliminar matrículas
- Gestionar estados de matrícula

Los estados disponibles son:

```text
ACTIVO
RETIRADO
FINALIZADO
```

### Historial

El sistema incluye un módulo para consultar las actividades realizadas.

Permite:

- Visualizar eventos
- Buscar registros
- Filtrar información
- Actualizar el historial
- Limpiar el historial

### Autenticación

El frontend incluye un sistema de acceso para el administrador.

También cuenta con:

- Inicio de sesión
- Cierre de sesión
- Confirmación antes de cerrar sesión
- Protección de las rutas correspondientes

## Estructura del proyecto

```text
GestionEstudiante/
│
├── public/
│
├── src/
│   │
│   ├── api/
│   │   └── axios.js
│   │
│   ├── assets/
│   │
│   ├── components/
│   │   ├── busqueda/
│   │   │   ├── Busqueda.jsx
│   │   │   └── busqueda.css
│   │   │
│   │   ├── header/
│   │   │   ├── Header.jsx
│   │   │   └── header.css
│   │   │
│   │   └── menu/
│   │       ├── Menu.jsx
│   │       └── menu.css
│   │
│   ├── config/
│   │   └── auth.js
│   │
│   ├── pages/
│   │   ├── alumnos/
│   │   ├── cursos/
│   │   ├── dashboard/
│   │   ├── distritos/
│   │   ├── docentes/
│   │   ├── login/
│   │   ├── matriculas/
│   │   ├── personas/
│   │   └── registros/
│   │
│   ├── utils/
│   │   └── alertas.js
│   │
│   ├── App.jsx
│   ├── App.css
│   ├── index.css
│   └── main.jsx
│
├── index.html
├── package.json
├── package-lock.json
└── vite.config.js
```

## Organización del frontend

### Components

Contiene componentes reutilizables de la interfaz.

Entre ellos:

- Menú de navegación
- Header
- Componentes de búsqueda

### Pages

Contiene las diferentes páginas o módulos del sistema.

```text
alumnos
cursos
dashboard
distritos
docentes
login
matriculas
personas
registros
```

### API

Contiene la configuración utilizada para realizar las solicitudes al backend.

```text
src/api/axios.js
```

### Config

Contiene configuraciones relacionadas con la autenticación.

```text
src/config/auth.js
```

### Utils

Contiene funciones auxiliares utilizadas por el sistema.

```text
src/utils/alertas.js
```

## Requisitos

Antes de ejecutar el proyecto se necesita tener instalado:

- Node.js
- npm

## Instalación

Ingresar a la carpeta del proyecto:

```bash
cd GestionEstudiante
```

Instalar las dependencias:

```bash
npm install
```

También se pueden instalar las principales librerías manualmente:

```bash
npm install bootstrap bootstrap-icons react-router-dom sweetalert2
```

```bash
npm install axios
```

## Librerías utilizadas

### React

Framework utilizado para construir la interfaz de usuario mediante componentes.

### Vite

Herramienta utilizada para ejecutar y construir el proyecto React.

### Bootstrap

Se utiliza para facilitar el diseño y la organización de la interfaz.

### Bootstrap Icons

Proporciona los iconos utilizados en diferentes elementos de la aplicación.

### React Router DOM

Permite administrar la navegación entre las diferentes páginas del sistema.

### SweetAlert2

Permite mostrar alertas, confirmaciones, mensajes de éxito y mensajes de error.

### Axios

Se utiliza para realizar las solicitudes HTTP al backend.

## Ejecución

Desde la carpeta:

```text
GestionEstudiante
```

ejecutar:

```bash
npm run dev
```

Vite iniciará el servidor de desarrollo.

Normalmente el frontend estará disponible en:

```text
http://localhost:5173
```

## Comunicación con el Backend

El frontend se comunica con el backend mediante solicitudes HTTP.

El flujo es:

```text
Usuario
   |
   v
React
   |
   | Axios
   v
FastAPI
   |
   | SQL
   v
PostgreSQL
```

Axios permite que los componentes del frontend envíen solicitudes a los diferentes endpoints de la API.

## Backend requerido

Para que el frontend pueda funcionar completamente, el backend debe estar ejecutándose.

El backend normalmente estará disponible en:

```text
http://127.0.0.1:8000
```

La documentación de la API puede consultarse en:

```text
http://127.0.0.1:8000/docs
```

## Build de producción

Para generar la versión de producción:

```bash
npm run build
```

Los archivos generados estarán dentro de:

```text
dist/
```

## Vista previa del build

Después de generar el build se puede ejecutar:

```bash
npm run preview
```

Esto permite comprobar la versión generada para producción.

## Navegación

El sistema utiliza React Router DOM para manejar las diferentes rutas de la aplicación.

Los principales módulos son:

```text
Inicio
Personas
Distritos
Alumnos
Docentes
Cursos
Matrículas
Historial
```

## Interfaz

La interfaz incluye:

- Menú lateral
- Encabezado
- Formularios
- Tablas
- Botones de acciones
- Buscadores
- Iconos
- Alertas
- Confirmaciones
- Navegación entre módulos

## Validaciones

El frontend realiza validaciones antes de enviar información al backend.

También muestra mensajes al usuario cuando:

- Se registra correctamente un elemento
- Ocurre un error
- Falta información requerida
- Se intenta eliminar un registro
- Se intenta cerrar sesión

Las validaciones principales también son procesadas por el backend.

## Estado del proyecto

Frontend funcional del Sistema de Gestión de Cursos y Estudiantes.

Incluye los módulos necesarios para interactuar con:

- Personas
- Distritos
- Alumnos
- Docentes
- Cursos
- Matrículas
- Historial
- Autenticación

## Autor

Fabian Tello
Raquel Castro

Proyecto académico:

**Sistema de Gestión de Cursos y Estudiantes**
