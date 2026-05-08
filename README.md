# ✦ Glamour Bisutería — Sistema de Inventario y Tienda Web

> Sistema fullstack de gestión de inventario con tienda web integrada, desarrollado por el **Grupo 3** de Nuevas Tecnologías — UTS Bucaramanga.

**Jesús González · Marlón Gélvez · Sebastián Velandia**

---

## 📋 Descripción

**Glamour Bisutería** es un sistema de gestión dual que combina:

- Una **aplicación de escritorio** (Python + Tkinter) con arquitectura MVC para administrar el inventario de forma local.
- Una **API REST** (Flask) desplegada en la nube que expone los datos del inventario.
- Una **tienda web** (HTML/CSS/JS vanilla) que consume la API y permite a los clientes ver productos, armar su carrito y generar pedidos con factura.

Los datos se persisten en **SQLite** como fuente de verdad y se sincronizan automáticamente con **MongoDB** en cada operación de escritura.

---

## 🛠️ Stack Tecnológico

| Capa | Tecnología | Versión | Uso |
|------|-----------|---------|-----|
| App de escritorio | Python + Tkinter | 3.12 / 3.13 | Interfaz de administración local |
| API REST | Flask | 3.0.3 | Endpoints de productos, clientes y pedidos |
| CORS | Flask-CORS | 4.0.1 | Permitir peticiones del frontend |
| Servidor WSGI | Gunicorn | 22.0.0 | Despliegue en producción |
| Base de datos principal | SQLite | built-in | Fuente de verdad; archivo `inventario.db` |
| Base de datos nube | MongoDB (PyMongo) | 4.17.0 | Réplica automática de productos y pedidos |
| Frontend | HTML5 + CSS3 + JS vanilla | — | Tienda web responsiva |
| Tipografía | Google Fonts (Cormorant Garamond + DM Sans) | — | Diseño de lujo |
| Despliegue | Railway | — | Hosting del servidor Flask |

---

## 🗂️ Estructura del Repositorio

```
proyecto_nuevas_tecnologias/
├── api.py                      # API REST principal (Flask)
├── index.html                  # Tienda web (frontend completo)
├── database.sql                # Esquema + datos semilla
├── requirements.txt            # Dependencias Python
├── Procfile                    # Comando de arranque para Railway
├── railway.json                # Configuración de despliegue
├── DESPLIEGUE.md               # Guía de despliegue en Railway
│
└── inventario-mvc/             # Aplicación de escritorio (MVC)
    ├── main.py                 # Punto de entrada — lanza Tkinter
    ├── api_client.py           # Cliente HTTP que consume la API
    ├── config/
    │   └── settings.py         # Configuración global (DB path, etc.)
    ├── app/
    │   ├── Models/
    │   │   ├── database.py         # Conexión SQLite + helpers MongoDB
    │   │   ├── producto_model.py   # CRUD de productos + sync Mongo
    │   │   ├── pedido_model.py     # CRUD de pedidos + sync Mongo
    │   │   └── rentabilidad_model.py
    │   ├── Views/
    │   │   ├── main_window.py      # Ventana principal con tabs
    │   │   ├── productos_view.py   # Gestión de productos
    │   │   ├── ventas_view.py      # Registro de ventas
    │   │   ├── rentabilidad_view.py
    │   │   └── widgets.py          # Componentes reutilizables
    │   └── Controllers/
    │       ├── producto_controller.py  # Delega a api_client
    │       ├── pedido_controller.py
    │       └── rentabilidad_controller.py
    └── database.sql            # Esquema SQLite local
```

---

## ⚙️ Instalación y Configuración

### Requisitos previos

- Python 3.12 o superior
- pip
- Git

### 1. Clonar el repositorio

```bash
git clone https://github.com/JESS0987/proyecto_nuevas_tecnologias.git
cd proyecto_nuevas_tecnologias
```

### 2. Crear entorno virtual e instalar dependencias

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Inicializar la base de datos

```bash
# Desde la raíz del repo
sqlite3 inventario-mvc/inventario.db < database.sql
```

### 4. Ejecutar la API (desarrollo local)

```bash
python api.py
# La API queda disponible en http://localhost:5000
```

### 5. Abrir la tienda web

Abre `index.html` directamente en el navegador. El frontend apunta al mismo origen que el servidor Flask.

### 6. Ejecutar la app de escritorio (opcional)

```bash
cd inventario-mvc
python main.py
```

---

## 🌐 Endpoints de la API

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/` | Sirve la tienda web (`index.html`) |
| `GET` | `/health` | Estado del servidor |
| `GET` | `/api/productos` | Lista todos los productos activos |
| `GET` | `/api/productos?q=collar` | Búsqueda de productos por término |
| `GET` | `/api/productos/<id>` | Detalle de un producto |
| `GET` | `/api/clientes` | Lista de clientes registrados |
| `POST` | `/api/clientes` | Registrar nuevo cliente |
| `GET` | `/api/pedidos` | Lista los últimos 100 pedidos |
| `POST` | `/api/pedidos` | Crear un nuevo pedido |
| `GET` | `/api/pedidos/<num_factura>` | Detalle de pedido por número |
| `PATCH` | `/api/pedidos/<id>/estado` | Actualizar estado (`pendiente` / `despachado` / `cancelado`) |

---

## ✨ Tabla de Características

| Característica | Estado | Descripción |
|----------------|--------|-------------|
| Catálogo web de productos | ✅ Completo | Grid responsivo con filtros por categoría y búsqueda en tiempo real |
| Carrito de compras | ✅ Completo | Agregar, quitar, modificar cantidades con validación de stock |
| Checkout y facturación | ✅ Completo | Registro de cliente + pedido + factura imprimible/PDF |
| API REST | ✅ Completo | Endpoints de productos, clientes y pedidos con validaciones |
| App de escritorio MVC | ✅ Completo | Tkinter con arquitectura Model-View-Controller |
| Persistencia SQLite | ✅ Completo | Base de datos local con esquema relacional normalizado |
| Sincronización MongoDB | ✅ Completo | Upsert automático en cada escritura (productos y pedidos) |
| Detección automática de rutas | ✅ Completo | La API detecta su ubicación en el sistema de archivos |
| Despliegue en Railway | ✅ Completo | 8 despliegues realizados, Procfile configurado |
| Gestión de stock bajo | ✅ Completo | Alertas visuales cuando el stock está en mínimo |
| Descuentos en pedidos | ✅ Completo | Soporte de descuento por monto en cada pedido |
| Control de rentabilidad | 🚧 En progreso | Vista de márgenes por producto en la app de escritorio |
| Autenticación de administrador | 🔜 Pendiente | Login para proteger la app de escritorio |
| Panel de reportes web | 🔜 Pendiente | Dashboard con gráficas de ventas por periodo |

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────┐
│                    CLIENTE (Navegador)                   │
│               index.html  ─►  fetch() API               │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP/JSON
┌──────────────────────▼──────────────────────────────────┐
│                   API REST (Flask)                       │
│  api.py  ─►  ProductoModel / PedidoModel                │
└───────────┬─────────────────────────┬───────────────────┘
            │ SQLite (fuente verdad)  │ MongoDB (réplica)
     ┌──────▼──────┐          ┌───────▼──────┐
     │ inventario  │          │   MongoDB     │
     │    .db      │          │   Atlas/local │
     └─────────────┘          └──────────────┘
            ▲
            │ api_client.py (HTTP)
┌──────────────────────────────────────────────────────────┐
│              App de Escritorio (Tkinter MVC)             │
│  main.py ─► MainWindow ─► Controllers ─► api_client     │
└──────────────────────────────────────────────────────────┘
```

---

## 👥 Equipo — Grupo 3

| Nombre | GitHub | Rol |
|--------|--------|-----|
| Jesús González | [@JESS0987](https://github.com/JESS0987) | Líder · Backend · Despliegue |
| Marlón Gélvez | [@Marlon Gelvez]((https://github.com/MarlonGelvez)) | Frontend · Base de datos |
| Sebastián Velandia | — | App de escritorio · MVC |

---

## 📄 Licencia

Proyecto académico desarrollado para la asignatura **Nuevas Tecnologías** — Universidad de Tecnología de Santander (UTS), 2025.
