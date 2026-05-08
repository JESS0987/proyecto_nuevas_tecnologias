# Guía de Contribución — Glamour Bisutería

¡Gracias por querer mejorar el proyecto! Esta guía explica cómo colaborar correctamente en el repositorio.

---

## 📋 Código de Conducta

- Respeta a todos los integrantes del equipo.
- Escribe en español dentro del código y la documentación.
- Si encuentras un bug, repórtalo antes de arreglarlo directamente.
- Las decisiones de arquitectura se discuten en Issues antes de implementarse.

---

## 🌿 Flujo de Trabajo con Git

### Ramas principales

| Rama | Propósito |
|------|-----------|
| `main` | Código en producción (Railway) — **nunca hacer push directo** |
| `develop` | Rama de integración — aquí se mezclan los features |
| `feature/<nombre>` | Nueva funcionalidad |
| `fix/<nombre>` | Corrección de bug |
| `docs/<nombre>` | Solo documentación |

### Paso a paso para contribuir

```bash
# 1. Haz fork del repositorio (si eres colaborador externo)
# 2. Clona tu fork
git clone https://github.com/TU_USUARIO/proyecto_nuevas_tecnologias.git

# 3. Crea tu rama desde develop
git checkout develop
git pull origin develop
git checkout -b feature/mi-nueva-funcionalidad

# 4. Haz tus cambios y commits
git add .
git commit -m "feat(api): agregar endpoint DELETE /api/productos/<id>"

# 5. Sube tu rama
git push origin feature/mi-nueva-funcionalidad

# 6. Abre un Pull Request hacia develop en GitHub
```

---

## 📝 Convenciones de Código Python (PEP 8)

| Elemento | Convención | Ejemplo correcto |
|----------|-----------|-----------------|
| Variables y funciones | `snake_case` | `precio_venta`, `obtener_todos()` |
| Clases | `PascalCase` | `ProductoModel`, `PedidoController` |
| Constantes | `UPPER_SNAKE_CASE` | `BASE_DIR`, `DB_PATH` |
| Módulos | `snake_case` | `producto_model.py`, `api_client.py` |
| Parámetros booleanos | Nombres descriptivos | `solo_activos=True` (no `flag=True`) |
| Longitud de línea | Máximo 100 caracteres | — |
| Comillas | Dobles `"` en docstrings, simples `'` en código | — |

### Docstrings (estilo Google/PEP 257)

Todos los métodos públicos deben tener docstring:

```python
@staticmethod
def crear_pedido(cliente_id, items, descuento=0, notas="", estado="pendiente"):
    """
    Crea un nuevo pedido y lo registra en SQLite y MongoDB.

    Args:
        cliente_id (int): ID del cliente en la tabla clientes.
        items (list[dict]): Lista de ítems con keys:
            - producto_id (int)
            - cantidad (int)
            - precio_unitario (float)
            - costo_unitario (float)
        descuento (float): Monto fijo de descuento. Por defecto 0.
        notas (str): Observaciones del pedido. Por defecto "".
        estado (str): Estado inicial. Por defecto "pendiente".

    Returns:
        str: Número de factura generado (ej. "FAC-2025-0026").

    Raises:
        ValueError: Si items está vacío.
        sqlite3.Error: Si falla la transacción en base de datos.
    """
```

---

## 💬 Convenciones de Commits (Conventional Commits)

Formato: `tipo(scope): descripción corta en minúsculas`

| Tipo | Cuándo usarlo | Ejemplo |
|------|--------------|---------|
| `feat` | Nueva funcionalidad | `feat(api): agregar endpoint PATCH /pedidos/<id>/estado` |
| `fix` | Corrección de bug | `fix(modelo): corregir cálculo de subtotal con descuento` |
| `docs` | Solo documentación | `docs: actualizar README con guía de instalación` |
| `refactor` | Refactorización sin cambio de comportamiento | `refactor(controller): delegar lógica de stock a modelo` |
| `style` | Formato, espacios, renombrado de variables | `style(vista): aplicar convenciones PEP 8` |
| `test` | Agregar o corregir tests | `test(modelo): agregar test de creación de pedido vacío` |
| `chore` | Cambios en herramientas, dependencias | `chore: actualizar Flask a 3.0.3` |

---

## 🐛 Reportar un Bug

Abre un **Issue** en GitHub con la siguiente información:

```
**Descripción del problema:**
[Qué está fallando]

**Pasos para reproducirlo:**
1. Ir a...
2. Hacer clic en...
3. Ver el error...

**Comportamiento esperado:**
[Qué debería pasar]

**Comportamiento actual:**
[Qué está pasando]

**Entorno:**
- SO: Windows / macOS / Linux
- Python: 3.x
- Rama: main / develop
```

---

## ✅ Criterios para que un Pull Request sea aprobado

Un PR será revisado y aprobado si cumple todos estos puntos:

- [ ] Apunta a `develop`, no a `main`
- [ ] Tiene al menos un commit con mensaje en formato Conventional Commits
- [ ] No rompe los endpoints existentes de la API
- [ ] El código nuevo tiene docstrings en métodos públicos
- [ ] No hay variables con nombres de una sola letra (excepto bucles simples como `i`, `k`)
- [ ] El archivo `requirements.txt` fue actualizado si se añadió alguna dependencia
- [ ] Se probó manualmente tanto la API como la app de escritorio si el cambio afecta a ambas

---

## 🗂️ Archivos que NO se deben subir

Asegúrate de que tu `.gitignore` excluya:

```
__pycache__/
*.pyc
*.pyo
venv/
.env
inventario.db        ← base de datos local con datos reales
*.db.hash
.DS_Store
```

---

## 📬 Contacto

Cualquier duda sobre el proyecto, escríbele al equipo a través de los Issues de GitHub o en el canal del grupo de estudio.

> Proyecto académico — Nuevas Tecnologías · Grupo 3 · UTS 2025
