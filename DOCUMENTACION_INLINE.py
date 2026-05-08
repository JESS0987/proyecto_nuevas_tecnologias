# 📄 Documentación Inline — Sistema de Inventario MVC
# Archivo de referencia: comentarios técnicos listos para integrar en cada módulo

# =============================================================================
# ARCHIVO: models/producto_model.py
# =============================================================================

import sqlite3
from typing import Optional


# Ruta por defecto de la base de datos SQLite
DB_PATH = "database/inventario.db"


class ProductoModel:
    """Modelo de datos para la entidad Producto.

    Gestiona todas las operaciones de acceso a la base de datos SQLite
    para la tabla 'productos'. Actúa como la capa M del patrón MVC:
    no contiene lógica de presentación ni de negocio compleja.

    Attributes:
        db_path (str): Ruta al archivo de base de datos SQLite.
        connection (sqlite3.Connection): Conexión activa a la base de datos.
    """

    def __init__(self, db_path: str = DB_PATH) -> None:
        """Inicializa el modelo y establece la conexión con la base de datos.

        Crea la tabla 'productos' si no existe al iniciar la aplicación,
        garantizando que el esquema esté disponible desde el primer uso.

        Args:
            db_path (str): Ruta al archivo .db de SQLite.
                           Por defecto usa la constante DB_PATH.
        """
        self.db_path = db_path
        self.connection = sqlite3.connect(self.db_path)
        self._crear_tabla()

    def _crear_tabla(self) -> None:
        """Crea la tabla 'productos' en la base de datos si no existe.

        Este método es privado y se llama automáticamente desde __init__.
        Utiliza 'CREATE TABLE IF NOT EXISTS' para ser idempotente (seguro
        de ejecutar múltiples veces sin efectos secundarios).

        Esquema de la tabla:
            - id (INTEGER): Clave primaria autoincremental.
            - nombre (TEXT): Nombre del producto. No puede ser nulo.
            - cantidad (INTEGER): Unidades disponibles en stock.
            - precio (REAL): Precio unitario del producto.
            - categoria (TEXT): Categoría o tipo de producto.
        """
        cursor = self.connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre    TEXT    NOT NULL,
                cantidad  INTEGER DEFAULT 0,
                precio    REAL    DEFAULT 0.0,
                categoria TEXT
            )
        """)
        self.connection.commit()

    def agregar_producto(
        self,
        nombre: str,
        cantidad: int,
        precio: float,
        categoria: str
    ) -> int:
        """Inserta un nuevo producto en la base de datos.

        Args:
            nombre (str): Nombre descriptivo del producto.
            cantidad (int): Cantidad inicial disponible en inventario.
            precio (float): Precio unitario de venta.
            categoria (str): Categoría a la que pertenece el producto.

        Returns:
            int: ID autogenerado del producto recién insertado.

        Raises:
            sqlite3.IntegrityError: Si se viola una restricción de la tabla.

        Example:
            >>> model = ProductoModel()
            >>> nuevo_id = model.agregar_producto("Laptop", 10, 1500.0, "Electrónica")
            >>> print(nuevo_id)  # 1
        """
        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT INTO productos (nombre, cantidad, precio, categoria) VALUES (?, ?, ?, ?)",
            (nombre, cantidad, precio, categoria)
        )
        self.connection.commit()
        return cursor.lastrowid

    def obtener_todos_los_productos(self) -> list[tuple]:
        """Recupera todos los productos almacenados en el inventario.

        Returns:
            list[tuple]: Lista de tuplas con la estructura
                         (id, nombre, cantidad, precio, categoria).
                         Retorna lista vacía si no hay registros.
        """
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM productos ORDER BY nombre ASC")
        return cursor.fetchall()

    def obtener_producto_por_id(self, producto_id: int) -> Optional[tuple]:
        """Busca y retorna un producto específico por su identificador.

        Args:
            producto_id (int): ID único del producto a recuperar.

        Returns:
            Optional[tuple]: Tupla con los datos del producto si existe,
                             None si no se encuentra ningún registro con ese ID.
        """
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM productos WHERE id = ?", (producto_id,))
        return cursor.fetchone()

    def actualizar_producto(
        self,
        producto_id: int,
        nombre: str,
        cantidad: int,
        precio: float,
        categoria: str
    ) -> bool:
        """Actualiza todos los campos de un producto existente.

        Args:
            producto_id (int): Identificador del producto a modificar.
            nombre (str): Nuevo nombre del producto.
            cantidad (int): Nueva cantidad en stock.
            precio (float): Nuevo precio unitario.
            categoria (str): Nueva categoría.

        Returns:
            bool: True si se actualizó al menos un registro,
                  False si el ID no corresponde a ningún producto.
        """
        cursor = self.connection.cursor()
        cursor.execute(
            """UPDATE productos
               SET nombre = ?, cantidad = ?, precio = ?, categoria = ?
               WHERE id = ?""",
            (nombre, cantidad, precio, categoria, producto_id)
        )
        self.connection.commit()
        # rowcount indica cuántas filas fueron afectadas
        return cursor.rowcount > 0

    def eliminar_producto(self, producto_id: int) -> bool:
        """Elimina permanentemente un producto del inventario.

        Args:
            producto_id (int): Identificador del producto a eliminar.

        Returns:
            bool: True si el producto fue eliminado exitosamente,
                  False si no se encontró ningún producto con ese ID.

        Warning:
            Esta operación es irreversible. Se recomienda confirmar
            la acción con el usuario antes de llamar este método.
        """
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM productos WHERE id = ?", (producto_id,))
        self.connection.commit()
        return cursor.rowcount > 0

    def buscar_productos(self, termino: str) -> list[tuple]:
        """Busca productos cuyo nombre contenga el término indicado.

        Realiza una búsqueda parcial (LIKE) e insensible a mayúsculas
        para mejorar la experiencia del usuario.

        Args:
            termino (str): Texto parcial o completo a buscar en el nombre.

        Returns:
            list[tuple]: Lista de productos que coinciden con el criterio.
                         Lista vacía si no hay coincidencias.

        Example:
            >>> resultados = model.buscar_productos("lap")
            >>> # Retorna productos como "Laptop", "Laptop Gaming", etc.
        """
        cursor = self.connection.cursor()
        patron_busqueda = f"%{termino}%"
        cursor.execute(
            "SELECT * FROM productos WHERE nombre LIKE ? ORDER BY nombre ASC",
            (patron_busqueda,)
        )
        return cursor.fetchall()

    def cerrar_conexion(self) -> None:
        """Cierra la conexión activa con la base de datos SQLite.

        Debe llamarse al finalizar el uso del modelo para liberar
        el archivo de base de datos y evitar bloqueos de recursos.
        Se recomienda llamar este método en el evento de cierre de la aplicación.
        """
        if self.connection:
            self.connection.close()


# =============================================================================
# ARCHIVO: controllers/inventario_controller.py
# =============================================================================

class InventarioController:
    """Controlador central del sistema de inventario.

    Actúa como intermediario entre la Vista (View) y el Modelo (Model)
    dentro del patrón MVC. Su responsabilidad es:
      - Recibir eventos desde la vista.
      - Aplicar la lógica de negocio (validaciones, transformaciones).
      - Instruir al modelo para leer o escribir datos.
      - Devolver resultados a la vista para su renderización.

    Attributes:
        model (ProductoModel): Instancia del modelo de datos.
        view: Referencia a la vista (inyectada después de la inicialización
              para evitar dependencias circulares).
    """

    def __init__(self, model: "ProductoModel") -> None:
        """Inicializa el controlador con una instancia del modelo.

        La vista se asigna en un paso posterior mediante set_view(),
        siguiendo el principio de inyección de dependencias.

        Args:
            model (ProductoModel): Instancia del modelo de acceso a datos.
        """
        self.model = model
        self.view = None  # Se asigna después para evitar dependencia circular

    def set_view(self, view) -> None:
        """Asigna la referencia a la vista al controlador.

        Permite que el controlador notifique a la vista cuando
        se producen cambios en los datos (patrón Observer básico).

        Args:
            view: Instancia de la clase View del módulo views/.
        """
        self.view = view

    def guardar_producto(
        self,
        nombre: str,
        cantidad_str: str,
        precio_str: str,
        categoria: str
    ) -> tuple[bool, str]:
        """Valida los datos del formulario y persiste un nuevo producto.

        Aplica validaciones de negocio antes de delegar al modelo:
          - El nombre no puede estar vacío.
          - La cantidad debe ser un entero no negativo.
          - El precio debe ser un número positivo.

        Args:
            nombre (str): Nombre del producto ingresado en el formulario.
            cantidad_str (str): Cantidad como string (proviene del campo de texto).
            precio_str (str): Precio como string (proviene del campo de texto).
            categoria (str): Categoría seleccionada.

        Returns:
            tuple[bool, str]: Una tupla donde:
                - bool: True si el producto fue guardado exitosamente.
                - str: Mensaje de éxito o descripción del error de validación.

        Example:
            >>> exito, mensaje = controller.guardar_producto("Monitor", "5", "250.0", "TI")
            >>> if exito:
            ...     print(mensaje)  # "Producto guardado correctamente."
        """
        # Validación: nombre obligatorio
        nombre = nombre.strip()
        if not nombre:
            return False, "El nombre del producto no puede estar vacío."

        # Validación: cantidad debe ser entero no negativo
        try:
            cantidad = int(cantidad_str)
            if cantidad < 0:
                raise ValueError
        except ValueError:
            return False, "La cantidad debe ser un número entero mayor o igual a cero."

        # Validación: precio debe ser número positivo
        try:
            precio = float(precio_str)
            if precio < 0:
                raise ValueError
        except ValueError:
            return False, "El precio debe ser un número positivo."

        # Delegar persistencia al modelo
        self.model.agregar_producto(nombre, cantidad, precio, categoria)
        return True, "Producto guardado correctamente."

    def cargar_inventario(self) -> list[tuple]:
        """Recupera todos los productos para mostrarlos en la vista.

        Returns:
            list[tuple]: Lista completa de productos del inventario.
        """
        return self.model.obtener_todos_los_productos()

    def eliminar_producto(self, producto_id: int) -> tuple[bool, str]:
        """Solicita la eliminación de un producto tras validar el ID.

        Args:
            producto_id (int): Identificador del producto a eliminar.

        Returns:
            tuple[bool, str]: Resultado de la operación y mensaje descriptivo.
        """
        if not producto_id:
            return False, "Debe seleccionar un producto para eliminar."

        eliminado = self.model.eliminar_producto(producto_id)
        if eliminado:
            return True, "Producto eliminado correctamente."
        return False, "No se encontró el producto con el ID proporcionado."

    def buscar_producto(self, termino: str) -> list[tuple]:
        """Realiza una búsqueda de productos por nombre.

        Args:
            termino (str): Texto a buscar. Si está vacío,
                           retorna todos los productos.

        Returns:
            list[tuple]: Productos que coinciden con el término de búsqueda.
        """
        termino = termino.strip()
        if not termino:
            return self.model.obtener_todos_los_productos()
        return self.model.buscar_productos(termino)


# =============================================================================
# ARCHIVO: main.py
# =============================================================================

def main():
    """Punto de entrada principal de la aplicación de inventario.

    Inicializa las tres capas del patrón MVC en el orden correcto:
      1. Se instancia el Model (acceso a datos).
      2. Se instancia el Controller pasándole el Model.
      3. Se instancia la View pasándole el Controller.
      4. Se vincula la View al Controller (set_view).
      5. Se inicia el bucle principal de la interfaz gráfica (mainloop).

    Este orden garantiza que no existan dependencias circulares en la
    inicialización y que cada capa esté correctamente conectada.
    """
    # 1. Inicializar modelo (crea la BD y la tabla si no existen)
    model = ProductoModel()

    # 2. Inicializar controlador con referencia al modelo
    controller = InventarioController(model)

    # 3. Inicializar vista con referencia al controlador
    # view = InventarioView(controller)

    # 4. Inyectar la vista en el controlador (evita dependencia circular)
    # controller.set_view(view)

    # 5. Iniciar el bucle de eventos de Tkinter
    # view.iniciar()


if __name__ == "__main__":
    main()
