-- ============================================================
-- Sistema de Control de Inventario y Rentabilidad
-- Datos reales: Tienda de Bisutería | Mar-Abr 2025
-- Grupo 3: Jesus Gonzalez, Marlon Gelvez, Sebastian Velandia
-- ============================================================

CREATE TABLE IF NOT EXISTS categorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE,
    descripcion TEXT,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT NOT NULL UNIQUE,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    categoria_id INTEGER,
    costo REAL NOT NULL DEFAULT 0,
    precio_venta REAL NOT NULL DEFAULT 0,
    stock INTEGER NOT NULL DEFAULT 0,
    stock_minimo INTEGER NOT NULL DEFAULT 5,
    activo INTEGER NOT NULL DEFAULT 1,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (categoria_id) REFERENCES categorias(id)
);
CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    documento TEXT UNIQUE,
    telefono TEXT,
    email TEXT,
    direccion TEXT,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS pedidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_factura TEXT NOT NULL UNIQUE,
    cliente_id INTEGER,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    subtotal REAL NOT NULL DEFAULT 0,
    descuento REAL NOT NULL DEFAULT 0,
    total REAL NOT NULL DEFAULT 0,
    estado TEXT NOT NULL DEFAULT 'despachado',
    notas TEXT,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
);
CREATE TABLE IF NOT EXISTS items_pedido (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pedido_id INTEGER NOT NULL,
    producto_id INTEGER NOT NULL,
    cantidad INTEGER NOT NULL,
    precio_unitario REAL NOT NULL,
    costo_unitario REAL NOT NULL,
    subtotal REAL NOT NULL,
    FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
    FOREIGN KEY (producto_id) REFERENCES productos(id)
);
CREATE TABLE IF NOT EXISTS entradas_inventario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    producto_id INTEGER NOT NULL,
    cantidad INTEGER NOT NULL,
    costo_unitario REAL NOT NULL,
    proveedor TEXT,
    notas TEXT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (producto_id) REFERENCES productos(id)
);

-- Categorías
INSERT OR IGNORE INTO categorias (nombre, descripcion) VALUES
    ('General', 'Categoría general'),
    ('Bisutería', 'Accesorios y joyería de moda'),
    ('Electrónica', 'Dispositivos electrónicos'),
    ('Ropa', 'Prendas de vestir'),
    ('Hogar', 'Artículos para el hogar');

-- Clientes
INSERT OR IGNORE INTO clientes (nombre, documento, telefono, email, direccion) VALUES ('Cliente General', '000000000', '0000000000', NULL, NULL);
INSERT OR IGNORE INTO clientes (nombre, documento, telefono, email, direccion) VALUES ('María García', '12345678', '3001234567', 'maria@email.com', 'Calle 10 #5-20, Bucaramanga');
INSERT OR IGNORE INTO clientes (nombre, documento, telefono, email, direccion) VALUES ('Carlos López', '87654321', '3109876543', 'carlos@email.com', 'Carrera 15 #8-30, Bucaramanga');
INSERT OR IGNORE INTO clientes (nombre, documento, telefono, email, direccion) VALUES ('Ana Martínez', '11223344', '3152345678', 'ana.m@email.com', 'Av. Quebrada #3-15, Girón');
INSERT OR IGNORE INTO clientes (nombre, documento, telefono, email, direccion) VALUES ('Luisa Fernández', '44332211', '3203456789', 'luisa@email.com', 'Calle 45 #22-10, Floridablanca');
INSERT OR IGNORE INTO clientes (nombre, documento, telefono, email, direccion) VALUES ('Valentina Torres', '55667788', '3174567890', 'vale.t@email.com', 'Carrera 27 #50-5, Bucaramanga');
INSERT OR IGNORE INTO clientes (nombre, documento, telefono, email, direccion) VALUES ('Sandra Ríos', '99887766', '3185678901', 'sandra@email.com', 'Calle 56 #30-20, Bucaramanga');
INSERT OR IGNORE INTO clientes (nombre, documento, telefono, email, direccion) VALUES ('Patricia Núñez', '33221100', '3016789012', 'patri@email.com', 'Cra 33 #12-40, Piedecuesta');

-- Productos
INSERT OR IGNORE INTO productos (codigo, nombre, categoria_id, costo, precio_venta, stock, stock_minimo) VALUES ('P001', 'Collar Dorado Largo', 2, 5000, 12000, 20, 5);
INSERT OR IGNORE INTO productos (codigo, nombre, categoria_id, costo, precio_venta, stock, stock_minimo) VALUES ('P002', 'Aretes Plateados Argolla', 2, 3000, 8000, 15, 5);
INSERT OR IGNORE INTO productos (codigo, nombre, categoria_id, costo, precio_venta, stock, stock_minimo) VALUES ('P003', 'Pulsera Cristal Multicolor', 2, 4000, 10000, 10, 3);
INSERT OR IGNORE INTO productos (codigo, nombre, categoria_id, costo, precio_venta, stock, stock_minimo) VALUES ('P004', 'Anillo Ajustable Dorado', 2, 2000, 6000, 25, 5);
INSERT OR IGNORE INTO productos (codigo, nombre, categoria_id, costo, precio_venta, stock, stock_minimo) VALUES ('P005', 'Cadena Fina Plateada', 2, 6000, 15000, 8, 3);
INSERT OR IGNORE INTO productos (codigo, nombre, categoria_id, costo, precio_venta, stock, stock_minimo) VALUES ('P006', 'Dije Corazón Esmaltado', 2, 3500, 9000, 18, 4);
INSERT OR IGNORE INTO productos (codigo, nombre, categoria_id, costo, precio_venta, stock, stock_minimo) VALUES ('P007', 'Pulsera Macramé Perlas', 2, 4500, 11000, 12, 4);
INSERT OR IGNORE INTO productos (codigo, nombre, categoria_id, costo, precio_venta, stock, stock_minimo) VALUES ('P008', 'Aretes Gota Resina', 2, 2500, 7000, 20, 5);
INSERT OR IGNORE INTO productos (codigo, nombre, categoria_id, costo, precio_venta, stock, stock_minimo) VALUES ('P009', 'Collar Perlas Artificiales', 2, 7000, 18000, 6, 3);
INSERT OR IGNORE INTO productos (codigo, nombre, categoria_id, costo, precio_venta, stock, stock_minimo) VALUES ('P010', 'Set Collar+Aretes Dorado', 2, 10000, 25000, 8, 3);
INSERT OR IGNORE INTO productos (codigo, nombre, categoria_id, costo, precio_venta, stock, stock_minimo) VALUES ('P011', 'Tobillera Dorada Flor', 2, 2000, 5500, 15, 4);
INSERT OR IGNORE INTO productos (codigo, nombre, categoria_id, costo, precio_venta, stock, stock_minimo) VALUES ('P012', 'Pulsera Rígida Plateada', 2, 5000, 13000, 10, 3);
INSERT OR IGNORE INTO productos (codigo, nombre, categoria_id, costo, precio_venta, stock, stock_minimo) VALUES ('P013', 'Aretes Chandelier Dorados', 2, 4000, 10500, 14, 4);
INSERT OR IGNORE INTO productos (codigo, nombre, categoria_id, costo, precio_venta, stock, stock_minimo) VALUES ('P014', 'Dije Mariposa Cristal', 2, 3000, 8500, 16, 4);
INSERT OR IGNORE INTO productos (codigo, nombre, categoria_id, costo, precio_venta, stock, stock_minimo) VALUES ('P015', 'Collar Choker Terciopelo', 2, 3500, 9500, 12, 3);

-- Entradas de inventario
INSERT INTO entradas_inventario (producto_id, cantidad, costo_unitario, proveedor, notas, fecha) VALUES (1, 15, 5000, 'Importadora Glamour Ltda', 'Reabastecimiento Marzo 2025', '2025-03-02 08:30:00');
INSERT INTO entradas_inventario (producto_id, cantidad, costo_unitario, proveedor, notas, fecha) VALUES (2, 27, 3000, 'Importadora Glamour Ltda', 'Reabastecimiento Marzo 2025', '2025-03-02 08:30:00');
INSERT INTO entradas_inventario (producto_id, cantidad, costo_unitario, proveedor, notas, fecha) VALUES (3, 17, 4000, 'Importadora Glamour Ltda', 'Reabastecimiento Marzo 2025', '2025-03-02 08:30:00');
INSERT INTO entradas_inventario (producto_id, cantidad, costo_unitario, proveedor, notas, fecha) VALUES (4, 15, 2000, 'Importadora Glamour Ltda', 'Reabastecimiento Marzo 2025', '2025-03-02 08:30:00');
INSERT INTO entradas_inventario (producto_id, cantidad, costo_unitario, proveedor, notas, fecha) VALUES (5, 24, 6000, 'Importadora Glamour Ltda', 'Reabastecimiento Marzo 2025', '2025-03-02 08:30:00');
INSERT INTO entradas_inventario (producto_id, cantidad, costo_unitario, proveedor, notas, fecha) VALUES (6, 22, 3500, 'Importadora Glamour Ltda', 'Reabastecimiento Marzo 2025', '2025-03-02 08:30:00');
INSERT INTO entradas_inventario (producto_id, cantidad, costo_unitario, proveedor, notas, fecha) VALUES (7, 18, 4500, 'Importadora Glamour Ltda', 'Reabastecimiento Marzo 2025', '2025-03-02 08:30:00');
INSERT INTO entradas_inventario (producto_id, cantidad, costo_unitario, proveedor, notas, fecha) VALUES (8, 30, 2500, 'Importadora Glamour Ltda', 'Reabastecimiento Marzo 2025', '2025-03-02 08:30:00');
INSERT INTO entradas_inventario (producto_id, cantidad, costo_unitario, proveedor, notas, fecha) VALUES (9, 27, 7000, 'Importadora Glamour Ltda', 'Reabastecimiento Marzo 2025', '2025-03-02 08:30:00');
INSERT INTO entradas_inventario (producto_id, cantidad, costo_unitario, proveedor, notas, fecha) VALUES (10, 17, 10000, 'Importadora Glamour Ltda', 'Reabastecimiento Marzo 2025', '2025-03-02 08:30:00');
INSERT INTO entradas_inventario (producto_id, cantidad, costo_unitario, proveedor, notas, fecha) VALUES (11, 20, 2000, 'Importadora Glamour Ltda', 'Reabastecimiento Marzo 2025', '2025-03-02 08:30:00');
INSERT INTO entradas_inventario (producto_id, cantidad, costo_unitario, proveedor, notas, fecha) VALUES (12, 11, 5000, 'Importadora Glamour Ltda', 'Reabastecimiento Marzo 2025', '2025-03-02 08:30:00');
INSERT INTO entradas_inventario (producto_id, cantidad, costo_unitario, proveedor, notas, fecha) VALUES (13, 17, 4000, 'Importadora Glamour Ltda', 'Reabastecimiento Marzo 2025', '2025-03-02 08:30:00');
INSERT INTO entradas_inventario (producto_id, cantidad, costo_unitario, proveedor, notas, fecha) VALUES (14, 11, 3000, 'Importadora Glamour Ltda', 'Reabastecimiento Marzo 2025', '2025-03-02 08:30:00');
INSERT INTO entradas_inventario (producto_id, cantidad, costo_unitario, proveedor, notas, fecha) VALUES (15, 20, 3500, 'Importadora Glamour Ltda', 'Reabastecimiento Marzo 2025', '2025-03-02 08:30:00');
INSERT INTO entradas_inventario (producto_id, cantidad, costo_unitario, proveedor, notas, fecha) VALUES (1, 18, 5000, 'Bisutería Mayorista Cali', 'Reabastecimiento Abril 2025', '2025-04-02 08:30:00');
INSERT INTO entradas_inventario (producto_id, cantidad, costo_unitario, proveedor, notas, fecha) VALUES (2, 12, 3000, 'Bisutería Mayorista Cali', 'Reabastecimiento Abril 2025', '2025-04-02 08:30:00');
INSERT INTO entradas_inventario (producto_id, cantidad, costo_unitario, proveedor, notas, fecha) VALUES (3, 16, 4000, 'Bisutería Mayorista Cali', 'Reabastecimiento Abril 2025', '2025-04-02 08:30:00');
INSERT INTO entradas_inventario (producto_id, cantidad, costo_unitario, proveedor, notas, fecha) VALUES (4, 28, 2000, 'Bisutería Mayorista Cali', 'Reabastecimiento Abril 2025', '2025-04-02 08:30:00');
INSERT INTO entradas_inventario (producto_id, cantidad, costo_unitario, proveedor, notas, fecha) VALUES (5, 20, 6000, 'Bisutería Mayorista Cali', 'Reabastecimiento Abril 2025', '2025-04-02 08:30:00');
INSERT INTO entradas_inventario (producto_id, cantidad, costo_unitario, proveedor, notas, fecha) VALUES (6, 16, 3500, 'Bisutería Mayorista Cali', 'Reabastecimiento Abril 2025', '2025-04-02 08:30:00');
INSERT INTO entradas_inventario (producto_id, cantidad, costo_unitario, proveedor, notas, fecha) VALUES (7, 30, 4500, 'Bisutería Mayorista Cali', 'Reabastecimiento Abril 2025', '2025-04-02 08:30:00');
INSERT INTO entradas_inventario (producto_id, cantidad, costo_unitario, proveedor, notas, fecha) VALUES (8, 25, 2500, 'Bisutería Mayorista Cali', 'Reabastecimiento Abril 2025', '2025-04-02 08:30:00');
INSERT INTO entradas_inventario (producto_id, cantidad, costo_unitario, proveedor, notas, fecha) VALUES (9, 22, 7000, 'Bisutería Mayorista Cali', 'Reabastecimiento Abril 2025', '2025-04-02 08:30:00');
INSERT INTO entradas_inventario (producto_id, cantidad, costo_unitario, proveedor, notas, fecha) VALUES (10, 30, 10000, 'Bisutería Mayorista Cali', 'Reabastecimiento Abril 2025', '2025-04-02 08:30:00');
INSERT INTO entradas_inventario (producto_id, cantidad, costo_unitario, proveedor, notas, fecha) VALUES (11, 24, 2000, 'Bisutería Mayorista Cali', 'Reabastecimiento Abril 2025', '2025-04-02 08:30:00');
INSERT INTO entradas_inventario (producto_id, cantidad, costo_unitario, proveedor, notas, fecha) VALUES (12, 14, 5000, 'Bisutería Mayorista Cali', 'Reabastecimiento Abril 2025', '2025-04-02 08:30:00');
INSERT INTO entradas_inventario (producto_id, cantidad, costo_unitario, proveedor, notas, fecha) VALUES (13, 18, 4000, 'Bisutería Mayorista Cali', 'Reabastecimiento Abril 2025', '2025-04-02 08:30:00');
INSERT INTO entradas_inventario (producto_id, cantidad, costo_unitario, proveedor, notas, fecha) VALUES (14, 14, 3000, 'Bisutería Mayorista Cali', 'Reabastecimiento Abril 2025', '2025-04-02 08:30:00');
INSERT INTO entradas_inventario (producto_id, cantidad, costo_unitario, proveedor, notas, fecha) VALUES (15, 17, 3500, 'Bisutería Mayorista Cali', 'Reabastecimiento Abril 2025', '2025-04-02 08:30:00');

-- Pedidos y sus ítems
INSERT INTO pedidos (id, numero_factura, cliente_id, fecha, subtotal, descuento, total, estado, notas) VALUES (1, 'FAC-2025-0001', 5, '2025-03-01 12:08:00', 85500.0, 4275, 81225.0, 'despachado', NULL);
INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, costo_unitario, subtotal) VALUES (1, 15, 1, 9500, 3500, 9500);
INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, costo_unitario, subtotal) VALUES (1, 10, 1, 25000, 10000, 25000);
INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, costo_unitario, subtotal) VALUES (1, 7, 3, 11000, 4500, 33000);
INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, costo_unitario, subtotal) VALUES (1, 6, 2, 9000, 3500, 18000);

INSERT INTO pedidos (id, numero_factura, cliente_id, fecha, subtotal, descuento, total, estado, notas) VALUES (2, 'FAC-2025-0002', 3, '2025-03-02 10:43:00', 145000.0, 0.0, 145000.0, 'despachado', NULL);
INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, costo_unitario, subtotal) VALUES (2, 10, 3, 25000, 10000, 75000);
INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, costo_unitario, subtotal) VALUES (2, 2, 2, 8000, 3000, 16000);
INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, costo_unitario, subtotal) VALUES (2, 7, 3, 11000, 4500, 33000);
INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, costo_unitario, subtotal) VALUES (2, 13, 2, 10500, 4000, 21000);

INSERT INTO pedidos (id, numero_factura, cliente_id, fecha, subtotal, descuento, total, estado, notas) VALUES (3, 'FAC-2025-0003', 2, '2025-03-03 17:05:00', 39500.0, 1975, 37525.0, 'pendiente', 'Regalo de cumpleaños');
INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, costo_unitario, subtotal) VALUES (3, 13, 1, 10500, 4000, 10500);
INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, costo_unitario, subtotal) VALUES (3, 11, 2, 5500, 2000, 11000);
INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, costo_unitario, subtotal) VALUES (3, 6, 2, 9000, 3500, 18000);

INSERT INTO pedidos (id, numero_factura, cliente_id, fecha, subtotal, descuento, total, estado, notas) VALUES (4, 'FAC-2025-0004', 5, '2025-03-07 18:27:00', 70000.0, 0.0, 70000.0, 'despachado', 'Transferencia bancaria');
INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, costo_unitario, subtotal) VALUES (4, 9, 3, 18000, 7000, 54000);
INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, costo_unitario, subtotal) VALUES (4, 2, 2, 8000, 3000, 16000);

INSERT INTO pedidos (id, numero_factura, cliente_id, fecha, subtotal, descuento, total, estado, notas) VALUES (5, 'FAC-2025-0005', 3, '2025-03-08 12:14:00', 95500.0, 0.0, 95500.0, 'despachado', NULL);
INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, costo_unitario, subtotal) VALUES (5, 13, 3, 10500, 4000, 31500);
INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, costo_unitario, subtotal) VALUES (5, 3, 1, 10000, 4000, 10000);
INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, costo_unitario, subtotal) VALUES (5, 9, 3, 18000, 7000, 54000);

INSERT INTO pedidos (id, numero_factura, cliente_id, fecha, subtotal, descuento, total, estado, notas) VALUES (6, 'FAC-2025-0006', 6, '2025-03-14 17:38:00', 39500.0, 0.0, 39500.0, 'cancelado', NULL);
INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, costo_unitario, subtotal) VALUES (6, 4, 3, 6000, 2000, 18000);
INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, costo_unitario, subtotal) VALUES (6, 1, 1, 12000, 5000, 12000);
INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, costo_unitario, subtotal) VALUES (6, 15, 1, 9500, 3500, 9500);

INSERT INTO pedidos (id, numero_factura, cliente_id, fecha, subtotal, descuento, total, estado, notas) VALUES (7, 'FAC-2025-0007', 3, '2025-03-16 17:26:00', 23500.0, 0.0, 23500.0, 'despachado', 'Transferencia bancaria');
INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, costo_unitario, subtotal) VALUES (7, 11, 3, 5500, 2000, 16500);
INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, costo_unitario, subtotal) VALUES (7, 8, 1, 7000, 2500, 7000);

INSERT INTO pedidos (id, numero_factura, cliente_id, fecha, subtotal, descuento, total, estado, notas) VALUES (8, 'FAC-2025-0008', 4, '2025-03-19 12:28:00', 71000.0, 0.0, 71000.0, 'pendiente', 'Pago en efectivo');
INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, costo_unitario, subtotal) VALUES (8, 12, 2, 13000, 5000, 26000);
INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, costo_unitario, subtotal) VALUES (8, 5, 3, 15000, 6000, 45000);

INSERT INTO pedidos (id, numero_factura, cliente_id, fecha, subtotal, descuento, total, estado, notas) VALUES (9, 'FAC-2025-0009', 8, '2025-03-22 14:17:00', 6000.0, 300, 5700.0, 'despachado', 'Transferencia bancaria');
INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, costo_unitario, subtotal) VALUES (9, 4, 1, 6000, 2000, 6000);

INSERT INTO pedidos (id, numero_factura, cliente_id, fecha, subtotal, descuento, total, estado, notas) VALUES (10, 'FAC-2025-0010', 4, '2025-03-23 11:13:00', 24000.0, 0.0, 24000.0, 'despachado', 'Entrega a domicilio');
INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, costo_unitario, subtotal) VALUES (10, 2, 3, 8000, 3000, 24000);

INSERT INTO pedidos (id, numero_factura, cliente_id, fecha, subtotal, descuento, total, estado, notas) VALUES (11, 'FAC-2025-0011', 1, '2025-03-24 14:06:00', 82000.0, 0.0, 82000.0, 'despachado', 'Entrega a domicilio');
INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, costo_unitario, subtotal) VALUES (11, 2, 2, 8000, 3000, 16000);
INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, costo_unitario, subtotal) VALUES (11, 9, 3, 18000, 7000, 54000);
INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, costo_unitario, subtotal) VALUES (11, 4, 2, 6000, 2000, 12000);

INSERT INTO pedidos (id, numero_factura, cliente_id, fecha, subtotal, descuento, total, estado, notas) VALUES (12, 'FAC-2025-0012', 8, '2025-03-25 10:24:00', 28000.0, 2800, 25200.0, 'despachado', 'Cliente frecuente');
INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, costo_unitario, subtotal) VALUES (12, 13, 2, 10500, 4000, 21000);
INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, costo_unitario, subtotal) VALUES (12, 8, 1, 7000, 2500, 7000);

INSERT INTO pedidos (id, numero_factura, cliente_id, fecha, subtotal, descuento, total, estado, notas) VALUES (13, 'FAC-2025-0013', 8, '2025-03-31 18:16:00', 16500.0, 0.0, 16500.0, 'despachado', NULL);
INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, costo_unitario, subtotal) VALUES (13, 11, 3, 5500, 2000, 16500);

INSERT INTO pedidos (id, numero_factura, cliente_id, fecha, subtotal, descuento, total, estado, notas) VALUES (14, 'FAC-2025-0014', 6, '2025-04-04 09:46:00', 6000.0, 600, 5400.0, 'despachado', 'Entrega a domicilio');
INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, costo_unitario, subtotal) VALUES (14, 4, 1, 6000, 2000, 6000);

INSERT INTO pedidos (id, numero_factura, cliente_id, fecha, subtotal, descuento, total, estado, notas) VALUES (15, 'FAC-2025-0015', 5, '2025-04-05 10:35:00', 55500.0, 0.0, 55500.0, 'cancelado', NULL);
INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, costo_unitario, subtotal) VALUES (15, 4, 3, 6000, 2000, 18000);
INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, costo_unitario, subtotal) VALUES (15, 14, 1, 8500, 3000, 8500);
INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, costo_unitario, subtotal) VALUES (15, 2, 1, 8000, 3000, 8000);
INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, costo_unitario, subtotal) VALUES (15, 8, 3, 7000, 2500, 21000);

INSERT INTO pedidos (id, numero_factura, cliente_id, fecha, subtotal, descuento, total, estado, notas) VALUES (16, 'FAC-2025-0016', 4, '2025-04-08 13:53:00', 29000.0, 0.0, 29000.0, 'despachado', NULL);
INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, costo_unitario, subtotal) VALUES (16, 7, 2, 11000, 4500, 22000);
INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, costo_unitario, subtotal) VALUES (16, 8, 1, 7000, 2500, 7000);

INSERT INTO pedidos (id, numero_factura, cliente_id, fecha, subtotal, descuento, total, estado, notas) VALUES (17, 'FAC-2025-0017', 1, '2025-04-09 18:56:00', 97500.0, 0.0, 97500.0, 'despachado', 'Transferencia bancaria');
INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, costo_unitario, subtotal) VALUES (17, 5, 2, 15000, 6000, 30000);
INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, costo_unitario, subtotal) VALUES (17, 13, 2, 10500, 4000, 21000);
INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, costo_unitario, subtotal) VALUES (17, 14, 3, 8500, 3000, 25500);
INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, costo_unitario, subtotal) VALUES (17, 8, 3, 7000, 2500, 21000);

INSERT INTO pedidos (id, numero_factura, cliente_id, fecha, subtotal, descuento, total, estado, notas) VALUES (18, 'FAC-2025-0018', 8, '2025-04-12 09:42:00', 21000.0, 0.0, 21000.0, 'despachado', 'Transferencia bancaria');
INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, costo_unitario, subtotal) VALUES (18, 4, 1, 6000, 2000, 6000);
INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, costo_unitario, subtotal) VALUES (18, 5, 1, 15000, 6000, 15000);

INSERT INTO pedidos (id, numero_factura, cliente_id, fecha, subtotal, descuento, total, estado, notas) VALUES (19, 'FAC-2025-0019', 6, '2025-04-13 12:49:00', 36000.0, 0.0, 36000.0, 'despachado', 'Transferencia bancaria');
INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, costo_unitario, subtotal) VALUES (19, 1, 3, 12000, 5000, 36000);

INSERT INTO pedidos (id, numero_factura, cliente_id, fecha, subtotal, descuento, total, estado, notas) VALUES (20, 'FAC-2025-0020', 2, '2025-04-16 13:05:00', 83000.0, 0.0, 83000.0, 'despachado', 'Pago en efectivo');
INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, costo_unitario, subtotal) VALUES (20, 2, 1, 8000, 3000, 8000);
INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, costo_unitario, subtotal) VALUES (20, 10, 3, 25000, 10000, 75000);

INSERT INTO pedidos (id, numero_factura, cliente_id, fecha, subtotal, descuento, total, estado, notas) VALUES (21, 'FAC-2025-0021', 4, '2025-04-19 15:17:00', 25000.0, 0.0, 25000.0, 'despachado', 'Transferencia bancaria');
INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, costo_unitario, subtotal) VALUES (21, 10, 1, 25000, 10000, 25000);

INSERT INTO pedidos (id, numero_factura, cliente_id, fecha, subtotal, descuento, total, estado, notas) VALUES (22, 'FAC-2025-0022', 6, '2025-04-25 16:40:00', 43500.0, 0.0, 43500.0, 'despachado', 'Regalo de cumpleaños');
INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, costo_unitario, subtotal) VALUES (22, 4, 2, 6000, 2000, 12000);
INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, costo_unitario, subtotal) VALUES (22, 11, 1, 5500, 2000, 5500);
INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, costo_unitario, subtotal) VALUES (22, 12, 2, 13000, 5000, 26000);

INSERT INTO pedidos (id, numero_factura, cliente_id, fecha, subtotal, descuento, total, estado, notas) VALUES (23, 'FAC-2025-0023', 8, '2025-04-27 12:42:00', 54500.0, 0.0, 54500.0, 'despachado', NULL);
INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, costo_unitario, subtotal) VALUES (23, 15, 1, 9500, 3500, 9500);
INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, costo_unitario, subtotal) VALUES (23, 13, 2, 10500, 4000, 21000);
INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, costo_unitario, subtotal) VALUES (23, 2, 3, 8000, 3000, 24000);

INSERT INTO pedidos (id, numero_factura, cliente_id, fecha, subtotal, descuento, total, estado, notas) VALUES (24, 'FAC-2025-0024', 4, '2025-04-28 13:44:00', 44000.0, 4400, 39600.0, 'cancelado', 'Transferencia bancaria');
INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, costo_unitario, subtotal) VALUES (24, 3, 1, 10000, 4000, 10000);
INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, costo_unitario, subtotal) VALUES (24, 6, 2, 9000, 3500, 18000);
INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, costo_unitario, subtotal) VALUES (24, 2, 2, 8000, 3000, 16000);

INSERT INTO pedidos (id, numero_factura, cliente_id, fecha, subtotal, descuento, total, estado, notas) VALUES (25, 'FAC-2025-0025', 1, '2025-04-30 10:38:00', 28500.0, 0.0, 28500.0, 'despachado', 'Regalo de cumpleaños');
INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, costo_unitario, subtotal) VALUES (25, 15, 1, 9500, 3500, 9500);
INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, costo_unitario, subtotal) VALUES (25, 11, 2, 5500, 2000, 11000);
INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, costo_unitario, subtotal) VALUES (25, 2, 1, 8000, 3000, 8000);