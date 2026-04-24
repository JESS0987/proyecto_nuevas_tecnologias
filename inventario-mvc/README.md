# Sistema de Inventario y Rentabilidad — Corte 2

**Grupo 3 · Nuevas Tecnologías · UTS**  
Jesus Gonzalez · Marlon Gelvez · Sebastian Velandia

---

## Descripción
Aplicación de escritorio en Python (Tkinter + SQLite) para el control de inventario, ventas y rentabilidad de pequeñas empresas. Arquitectura **MVC** estricta.

---

## Estructura del Proyecto
```
inventario-mvc/
├── main.py                      ← Punto de entrada
├── database.sql                 ← Script de creación de tablas
├── README.md
├── .gitignore
├── config/
│   └── settings.py              ← Configuración global
├── app/
│   ├── Models/
│   │   ├── database.py          ← Conexión SQLite
│   │   ├── producto_model.py    ← CRUD productos, stock, entradas
│   │   ├── pedido_model.py      ← CRUD ventas, clientes, facturas
│   │   └── rentabilidad_model.py← Cálculos de ganancias
│   ├── Controllers/
│   │   ├── producto_controller.py
│   │   ├── pedido_controller.py
│   │   └── rentabilidad_controller.py
│   └── Views/
│       ├── main_window.py       ← Ventana principal + navegación
│       ├── widgets.py           ← Componentes reutilizables
│       ├── productos_view.py    ← Módulo Inventario
│       ├── ventas_view.py       ← Módulo Ventas
│       └── rentabilidad_view.py ← Módulo Reportes
└── reports/                     ← CSVs exportados (autogenerado)
```

---

## Requisitos
- **Python 3.8+**
- **tkinter** (incluido en Python estándar — en Linux instalar `python3-tk`)
- No requiere librerías externas adicionales

---

## Cómo Ejecutar

### Windows
```bash
# En la carpeta inventario-mvc
python main.py
```

### macOS / Linux
```bash
# Instalar tkinter si es necesario (Linux/Ubuntu)
sudo apt install python3-tk

# Ejecutar
python3 main.py
```

---

## Funcionalidades

### 📦 Módulo de Inventario
- Registrar, editar y eliminar productos (eliminación lógica)
- Control de stock con alertas visuales de stock bajo
- Registro de entradas de inventario (compras con proveedor)
- Búsqueda en tiempo real por nombre, código o categoría
- Filtrar por productos activos/inactivos

### 🛒 Módulo de Ventas
- Crear pedidos con múltiples productos
- Descuento configurable por pedido
- Facturación automática con número consecutivo (`FAC-YYYYMMDD-####`)
- Descuento automático del stock al confirmar venta
- Historial de ventas con vista de factura
- Gestión de clientes

### 📊 Módulo de Rentabilidad
- Resumen general del inventario (valor costo, valor venta, ganancia potencial)
- Ganancia del período seleccionado (ingresos, costos, margen)
- Desglose mensual de ventas y ganancias
- Rentabilidad por producto con margen porcentual
- **Exportación CSV** de 4 tipos de reportes:
  - Ventas por mes
  - Ventas por día
  - Rentabilidad por producto
  - Inventario actual

---

## Base de Datos (SQLite)
El archivo `inventario.db` se crea automáticamente al iniciar la app.

Tablas principales:
| Tabla | Descripción |
|---|---|
| `productos` | Catálogo con stock y precios |
| `categorias` | Categorías de productos |
| `clientes` | Directorio de clientes |
| `pedidos` | Cabecera de cada venta |
| `items_pedido` | Líneas detalle de cada venta |
| `entradas_inventario` | Registro de compras/reposiciones |

---

## Tecnologías
| Componente | Tecnología |
|---|---|
| Lenguaje | Python 3 |
| Interfaz gráfica | Tkinter (stdlib) |
| Base de datos | SQLite3 (stdlib) |
| Exportación | CSV (stdlib) |
| Control de versiones | Git / GitHub |

---

## Próxima Fase
- Integración de asistente con IA (API Claude / GPT) para consultas en lenguaje natural sobre el inventario.
