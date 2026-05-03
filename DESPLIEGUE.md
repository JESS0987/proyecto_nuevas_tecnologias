# 🛍️ Glamour Bisutería — Tienda Web

Sistema completo: **Flask API + Frontend HTML** conectado a la base de datos SQLite existente.

## 📁 Estructura
```
inventario-mvc/
├── api.py              ← Servidor Flask REST (NUEVO)
├── index.html          ← Frontend mercadillo (NUEVO)
├── requirements.txt    ← Dependencias Python (NUEVO)
├── Procfile            ← Para Railway (NUEVO)
├── railway.json        ← Config Railway (NUEVO)
├── app/
│   ├── Models/         ← Modelos existentes (sin cambios)
│   └── Controllers/    ← Controladores existentes (sin cambios)
├── config/settings.py  ← Config existente (sin cambios)
├── database.sql        ← Esquema BD (sin cambios)
└── inventario.db       ← Base de datos SQLite
```

## 🚀 Despliegue en Railway

### Paso 1 — Subir a GitHub
```bash
git add .
git commit -m "Añadir API Flask y tienda web"
git push origin main
```

### Paso 2 — Crear proyecto en Railway
1. Ve a [railway.app](https://railway.app) → **New Project**
2. Elige **Deploy from GitHub repo**
3. Selecciona tu repositorio `JESS0987/proyecto_nuevas_tecnologias`
4. Railway detecta el `Procfile` y despliega automáticamente

### Paso 3 — Obtener dominio
1. En tu proyecto Railway → **Settings → Networking**
2. Click en **Generate Domain**
3. Tu URL será algo como: `https://proyecto-nuevas-tecnologias.up.railway.app`

### Paso 4 — Actualizar el frontend
En `index.html`, la línea:
```javascript
const API = window.location.hostname === "localhost" ...
```
Ya está configurada para detectar Railway automáticamente. ✅

## 🖥️ Prueba local
```bash
cd inventario-mvc
pip install flask flask-cors gunicorn
python api.py
# Abre: http://localhost:5000
```

## 🔗 Endpoints API
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/` | Frontend tienda |
| GET | `/api/productos` | Listar productos activos |
| GET | `/api/productos?q=collar` | Buscar productos |
| GET | `/api/productos/:id` | Detalle producto |
| GET | `/api/clientes` | Listar clientes |
| POST | `/api/clientes` | Crear cliente |
| POST | `/api/pedidos` | Crear pedido + factura |
| GET | `/api/pedidos/:factura` | Consultar factura |

## ✨ Funcionalidades de la tienda
- 🔍 Búsqueda en tiempo real por nombre/código
- 🏷️ Filtro por categoría
- 🛒 Carrito lateral con control de cantidad
- 👤 Registro de cliente nuevo o selección de existente
- 📄 Generación de factura automática (número FAC-YYYY-XXXX)
- 🖨️ Impresión / guardado en PDF de la factura
- 📉 El stock se descuenta en la BD automáticamente
- ⚠️ Alerta de stock bajo visible en la tarjeta del producto
