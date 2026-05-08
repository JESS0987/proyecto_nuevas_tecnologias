# 📦 Sistema de Inventario MVC

> Aplicación de escritorio para la gestión y control de inventario, desarrollada en Python bajo el patrón arquitectónico **Model-View-Controller (MVC)**. Diseñada como proyecto académico para la asignatura de Nuevas Tecnologías.

---

## 📋 Tabla de Contenidos

- [Descripción](#-descripción)
- [Stack Tecnológico](#-stack-tecnológico)
- [Características](#-características)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Requisitos Previos](#-requisitos-previos)
- [Instalación](#-instalación)
- [Uso](#-uso)
- [Arquitectura MVC](#-arquitectura-mvc)
- [Contribución](#-contribución)
- [Licencia](#-licencia)

---

## 📝 Descripción

Este sistema permite registrar, consultar, actualizar y eliminar productos de un inventario mediante una interfaz gráfica desarrollada en Python. El proyecto aplica el patrón **MVC** para separar las responsabilidades de datos, lógica de negocio y presentación, facilitando el mantenimiento y la escalabilidad del código.

---

## 🛠 Stack Tecnológico

| Tecnología | Versión | Propósito |
|---|---|---|
| Python | 3.10+ | Lenguaje principal |
| Tkinter | Built-in | Interfaz gráfica (View) |
| SQLite3 | Built-in | Persistencia de datos (Model) |
| unittest | Built-in | Pruebas unitarias |

> **Nota:** Todas las dependencias son parte de la biblioteca estándar de Python. No se requieren instalaciones externas.

---

## ✨ Características

| # | Característica | Estado |
|---|---|---|
| 1 | Registro de nuevos productos | ✅ Implementado |
| 2 | Consulta y búsqueda de inventario | ✅ Implementado |
| 3 | Actualización de stock y datos | ✅ Implementado |
| 4 | Eliminación de registros | ✅ Implementado |
| 5 | Persistencia con base de datos SQLite | ✅ Implementado |
| 6 | Separación de capas MVC | ✅ Implementado |
| 7 | Interfaz gráfica con Tkinter | ✅ Implementado |
| 8 | Validación de datos de entrada | 🚧 En desarrollo |
| 9 | Exportación de reportes | 🔜 Planeado |
| 10 | Autenticación de usuarios | 🔜 Planeado |

---

## 📁 Estructura del Proyecto

```
proyecto_nuevas_tecnologias/
│
└── inventario-mvc/
    ├── models/
    │   └── producto_model.py       # Lógica de acceso a datos y ORM
    ├── views/
    │   └── inventario_view.py      # Interfaz gráfica (Tkinter)
    ├── controllers/
    │   └── inventario_controller.py # Lógica de negocio y mediación
    ├── database/
    │   └── inventario.db           # Base de datos SQLite (autogenerada)
    ├── tests/
    │   └── test_producto.py        # Pruebas unitarias
    └── main.py                     # Punto de entrada de la aplicación
```

---

## ✅ Requisitos Previos

- Python **3.10 o superior**
- Sistema operativo: Windows, macOS o Linux
- Git (para clonar el repositorio)

Verificar versión de Python instalada:

```bash
python --version
```

---

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/JESS0987/proyecto_nuevas_tecnologias.git
cd proyecto_nuevas_tecnologias
```

### 2. (Opcional) Crear un entorno virtual

```bash
# Crear entorno virtual
python -m venv venv

# Activar en Windows
venv\Scripts\activate

# Activar en macOS/Linux
source venv/bin/activate
```

### 3. Instalar dependencias

Este proyecto no requiere dependencias externas. Todos los módulos utilizados son parte de la biblioteca estándar de Python.

### 4. Ejecutar la aplicación

```bash
cd inventario-mvc
python main.py
```

La base de datos SQLite se creará automáticamente en la primera ejecución.

---

## 💡 Uso

1. Al iniciar la aplicación, se mostrará la ventana principal del inventario.
2. Desde la interfaz puedes:
   - **Agregar** un nuevo producto completando el formulario y haciendo clic en "Guardar".
   - **Buscar** productos por nombre o código en el campo de búsqueda.
   - **Editar** seleccionando un producto de la tabla y modificando sus campos.
   - **Eliminar** seleccionando un producto y confirmando la acción.

---

## 🏗 Arquitectura MVC

El proyecto implementa estrictamente el patrón **Model-View-Controller**:

```
Usuario
   │
   ▼
[View] ──────► [Controller] ──────► [Model]
  ▲                │                   │
  └────────────────┴───────────────────┘
       (respuesta / actualización UI)
```

- **Model (`models/`):** Gestiona la conexión con SQLite y las operaciones CRUD. No conoce la vista.
- **View (`views/`):** Renderiza la interfaz con Tkinter. No contiene lógica de negocio.
- **Controller (`controllers/`):** Recibe eventos de la vista, los procesa y llama al modelo. Es el mediador.

---

## 🤝 Contribución

¿Deseas colaborar? Lee el archivo [CONTRIBUTING.md](./Contributing.md) para conocer las normas y flujo de trabajo del proyecto.

---

## 📄 Licencia

Este proyecto es de uso académico. Desarrollado para la asignatura de Nuevas Tecnologías.

---

<p align="center">
  Desarrollado con 🐍 Python · Patrón MVC · SQLite
</p>
