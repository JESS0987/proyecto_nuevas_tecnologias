# 🤝 Guía de Contribución

¡Gracias por tu interés en contribuir a **Sistema de Inventario MVC**! Este documento describe las normas y el flujo de trabajo que deben seguir todos los colaboradores para mantener la calidad y consistencia del código.

---

## 📋 Tabla de Contenidos

- [Código de Conducta](#-código-de-conducta)
- [¿Cómo puedo contribuir?](#-cómo-puedo-contribuir)
- [Flujo de Trabajo con Git](#-flujo-de-trabajo-con-git)
- [Convenciones de Código](#-convenciones-de-código)
- [Convenciones de Commits](#-convenciones-de-commits)
- [Proceso de Pull Request](#-proceso-de-pull-request)
- [Reportar Bugs](#-reportar-bugs)

---

## 📜 Código de Conducta

Este proyecto se rige por principios de respeto y colaboración profesional. Se espera que todos los participantes:

- Usen lenguaje inclusivo y respetuoso.
- Acepten críticas constructivas con madurez.
- Se enfoquen en lo que es mejor para el proyecto.
- Eviten conductas inapropiadas o discriminatorias.

---

## 🙋 ¿Cómo puedo contribuir?

Existen varias formas de aportar al proyecto:

- 🐛 **Reportar bugs** mediante GitHub Issues.
- 💡 **Proponer nuevas funcionalidades** abriendo un Issue con la etiqueta `enhancement`.
- 🔧 **Corregir errores** o mejorar el código existente mediante Pull Requests.
- 📝 **Mejorar la documentación** del proyecto.
- ✅ **Escribir pruebas unitarias** para aumentar la cobertura de tests.

---

## 🌿 Flujo de Trabajo con Git

Este proyecto utiliza el modelo **Feature Branch Workflow**.

### 1. Hacer fork y clonar

```bash
# Hacer fork desde GitHub y luego clonar tu fork
git clone https://github.com/TU_USUARIO/proyecto_nuevas_tecnologias.git
cd proyecto_nuevas_tecnologias

# Agregar el repositorio original como remote upstream
git remote add upstream https://github.com/JESS0987/proyecto_nuevas_tecnologias.git
```

### 2. Mantener tu fork actualizado

```bash
git fetch upstream
git checkout main
git merge upstream/main
```

### 3. Crear una rama para tu contribución

```bash
# Nomenclatura: tipo/descripcion-corta
git checkout -b feature/agregar-exportacion-pdf
git checkout -b fix/corregir-validacion-stock
git checkout -b docs/actualizar-readme
```

### 4. Realizar los cambios y hacer commit

```bash
git add .
git commit -m "feat: agregar exportación de inventario a PDF"
```

### 5. Subir la rama y abrir un Pull Request

```bash
git push origin feature/agregar-exportacion-pdf
```

Luego abre un Pull Request desde GitHub hacia la rama `main` del repositorio original.

---

## 🧹 Convenciones de Código

Este proyecto sigue las guías de estilo de Python **PEP 8**. Puntos clave:

### Nomenclatura

| Elemento | Convención | Ejemplo |
|---|---|---|
| Variables | `snake_case` | `nombre_producto` |
| Funciones | `snake_case` | `obtener_producto_por_id()` |
| Clases | `PascalCase` | `ProductoModel` |
| Constantes | `UPPER_SNAKE_CASE` | `MAX_STOCK_PERMITIDO` |
| Archivos | `snake_case` | `producto_controller.py` |

### Reglas generales

- Máximo **79 caracteres** por línea.
- Usar **4 espacios** para indentación (no tabulaciones).
- Dejar **2 líneas en blanco** entre definiciones de clases y funciones de alto nivel.
- Dejar **1 línea en blanco** entre métodos dentro de una clase.
- Toda función pública debe tener su **docstring** explicando parámetros y retorno.
- Evitar nombres genéricos como `data`, `info`, `temp`, `x`, `obj`. Usar nombres descriptivos.

### Docstrings (estilo Google)

```python
def actualizar_stock(self, producto_id: int, cantidad: int) -> bool:
    """Actualiza la cantidad en stock de un producto existente.

    Args:
        producto_id (int): Identificador único del producto.
        cantidad (int): Nueva cantidad a establecer en el inventario.

    Returns:
        bool: True si la actualización fue exitosa, False en caso contrario.

    Raises:
        ValueError: Si la cantidad proporcionada es negativa.
    """
```

---

## 📝 Convenciones de Commits

Seguimos el estándar **Conventional Commits**. El formato es:

```
<tipo>(<alcance opcional>): <descripción corta en presente>
```

### Tipos permitidos

| Tipo | Cuándo usarlo |
|---|---|
| `feat` | Nueva funcionalidad |
| `fix` | Corrección de un bug |
| `docs` | Cambios en documentación |
| `style` | Formato, espacios, sin cambios lógicos |
| `refactor` | Refactorización sin cambiar comportamiento |
| `test` | Agregar o corregir pruebas |
| `chore` | Tareas de mantenimiento, dependencias |

### Ejemplos válidos

```
feat(controller): agregar método de búsqueda por categoría
fix(model): corregir consulta SQL que omitía productos con stock cero
docs: actualizar sección de instalación en README
test(model): agregar pruebas unitarias para ProductoModel
refactor(view): renombrar variables para seguir PEP 8
```

### Reglas para el mensaje de commit

- Usar el **imperativo en presente**: "agregar" no "agregado" ni "agrega".
- Primera letra en **minúscula**.
- Sin punto final.
- Máximo **72 caracteres** en la línea del título.

---

## 🔍 Proceso de Pull Request

1. Asegúrate de que tu rama esté actualizada con `main` antes de abrir el PR.
2. El PR debe incluir:
   - **Título** descriptivo siguiendo Conventional Commits.
   - **Descripción** explicando qué cambió y por qué.
   - **Screenshots** (si hay cambios en la interfaz).
   - **Referencia a un Issue** si aplica: `Closes #12`.
3. Todos los tests existentes deben pasar.
4. El código debe seguir las convenciones descritas en este documento.
5. Al menos **1 reviewer** debe aprobar el PR antes de hacer merge.
6. No hacer merge de tu propio PR salvo autorización del maintainer.

---

## 🐛 Reportar Bugs

Para reportar un bug, abre un **Issue** en GitHub con la siguiente información:

```markdown
## Descripción del bug
<!-- Descripción clara y concisa del problema -->

## Pasos para reproducirlo
1. Ir a '...'
2. Hacer clic en '...'
3. Ver el error

## Comportamiento esperado
<!-- Qué debería suceder en lugar del error -->

## Capturas de pantalla
<!-- Si aplica, agrega imágenes que ayuden a entender el problema -->

## Entorno
- OS: [e.g. Windows 11]
- Python: [e.g. 3.11.2]
- Versión del proyecto: [e.g. commit hash o tag]
```

---

## ❓ ¿Tienes dudas?

Si tienes preguntas que no están cubiertas aquí, abre un **Issue** con la etiqueta `question` y con gusto te ayudamos.

---

<p align="center">¡Gracias por contribuir! 🚀</p>
