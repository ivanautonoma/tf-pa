# 📦 Datos de Prueba del Sistema de Inventario

## 🔑 Credenciales de Acceso

| Usuario    | Contraseña | Rol       | Descripción                |
| ---------- | ---------- | --------- | -------------------------- |
| **admin**  | admin      | ADMIN     | Administrador del sistema  |
| **carlos** | 123        | ENCARGADO | Encargado de Tienda Centro |
| **maria**  | 123        | ENCARGADO | Encargada de Tienda Norte  |
| **juan**   | 123        | VENDEDOR  | Vendedor de Tienda Sur     |
| **ana**    | 123        | VENDEDOR  | Vendedora de Tienda Centro |

## 🔐 Permisos por Rol

### ADMIN (Gerente General)

-   ✅ Gestionar tiendas (crear/eliminar)
-   ✅ Gestionar empleados (crear/editar/eliminar)
-   ✅ Gestionar productos (crear/editar/eliminar)
-   ✅ Registrar ingresos de mercancía
-   ✅ Registrar salidas/ventas
-   ✅ Ver reportes de todas las tiendas
-   ✅ Acceso total al sistema

### ENCARGADO (Jefe de Tienda)

-   ❌ No puede gestionar tiendas
-   ❌ No puede gestionar empleados
-   ❌ No puede crear/editar/eliminar productos
-   ✅ Puede ver productos
-   ✅ **Puede registrar INGRESOS** (recepción de mercancía)
-   ✅ Puede registrar salidas/ventas
-   ✅ Ver reportes y movimientos
-   📝 Solo ve datos de todas las tiendas (puede filtrar)

### VENDEDOR (Cajero)

-   ❌ No puede gestionar tiendas
-   ❌ No puede gestionar empleados
-   ❌ No puede crear/editar/eliminar productos
-   ✅ Puede ver productos
-   ❌ **NO puede registrar ingresos**
-   ✅ **Puede registrar SALIDAS** (ventas a clientes)
-   ✅ Ver reportes y movimientos
-   📝 Solo ve datos de todas las tiendas (puede filtrar)

---

## 🏪 Tiendas

1. **Tienda Centro** - Av. Principal 123, Lima
2. **Tienda Norte** - Av. Túpac Amaru 456, Lima
3. **Tienda Sur** - Av. Aviación 789, Lima

---

## 👥 Empleados

| Nombre           | DNI      | Tienda        | Jornada  | Usuario | Rol       |
| ---------------- | -------- | ------------- | -------- | ------- | --------- |
| Carlos Rodríguez | 12345678 | Tienda Centro | Completa | carlos  | ENCARGADO |
| María González   | 87654321 | Tienda Norte  | Completa | maria   | ENCARGADO |
| Juan Pérez       | 11223344 | Tienda Sur    | Completa | juan    | VENDEDOR  |
| Ana Torres       | 55667788 | Tienda Centro | Media    | ana     | VENDEDOR  |

---

## 📦 Productos por Tienda

### Tienda Centro

| SKU    | Producto          | Categoría   | Precio  | Stock Mínimo | Stock Actual |
| ------ | ----------------- | ----------- | ------- | ------------ | ------------ |
| ARR001 | Arroz Costeño 1kg | Granos      | S/ 4.50 | 10           | 40           |
| AZU001 | Azúcar Rubia 1kg  | Endulzantes | S/ 3.80 | 8            | 30           |
| ACE001 | Aceite Primor 1L  | Aceites     | S/ 9.50 | 5            | 25           |

### Tienda Norte

| SKU    | Producto                | Categoría | Precio  | Stock Mínimo | Stock Actual |
| ------ | ----------------------- | --------- | ------- | ------------ | ------------ |
| LEC001 | Leche Gloria Lata       | Lácteos   | S/ 4.20 | 12           | 12           |
| ATU001 | Atún Florida 170g       | Conservas | S/ 3.50 | 15           | 5 ⚠️         |
| FID001 | Fideos Don Vittorio 1kg | Pastas    | S/ 3.20 | 10           | 20           |

### Tienda Sur

| SKU    | Producto            | Categoría | Precio  | Stock Mínimo | Stock Actual |
| ------ | ------------------- | --------- | ------- | ------------ | ------------ |
| GAL001 | Galletas Soda 6pack | Galletas  | S/ 5.80 | 8            | 7            |
| JAB001 | Jabón Bolívar 3pack | Limpieza  | S/ 4.50 | 6            | 0 🔴         |

---

## 📊 Estado del Inventario

-   **OK**: 7 productos con stock adecuado
-   **BAJO MÍNIMO**: 1 producto (Atún en Tienda Norte)
-   **SIN STOCK**: 1 producto (Jabón en Tienda Sur)

---

## 📝 Movimientos Registrados

El sistema tiene **18 movimientos** totales:

-   **11 ingresos** (Stock inicial)
-   **3 salidas** (Ventas a clientes)
-   Distribuidos entre las 3 tiendas
-   Registrados por diferentes usuarios

---

## 🎯 Casos de Uso para Probar

### Como ADMIN (admin/admin):

1. ✅ Crear/editar/eliminar productos
2. ✅ Gestionar empleados y tiendas
3. ✅ Registrar ingresos de mercancía
4. ✅ Registrar ventas
5. ✅ Ver todos los reportes

### Como ENCARGADO (carlos/123 o maria/123):

1. ❌ NO ve botones de crear/editar productos
2. ✅ **Ve botón "Registrar Ingreso"** en Movimientos
3. ✅ Puede registrar recepciones de mercancía
4. ✅ Puede registrar ventas
5. ✅ Consultar stock y reportes

### Como VENDEDOR (juan/123 o ana/123):

1. ❌ NO ve botones de crear/editar productos
2. ❌ **NO ve botón "Registrar Ingreso"**
3. ✅ **Solo ve botón "Registrar Salida"** en Movimientos
4. ✅ Puede registrar ventas a clientes
5. ✅ Consultar productos y reportes

### Filtros:

1. **Filtrar por tienda**: Usa el dropdown superior para ver solo una tienda
2. **Filtrar por estado**: En Reportes, usa los radio buttons (Todos, OK, Bajo mínimo, Sin stock)
3. **Combinar filtros**: Selecciona tienda + estado para ver la intersección

---

## 💡 Notas Importantes

-   ✅ **Sistema simplificado**: Ya no hay almacenes, todo es directo por tienda
-   ✅ **Lógica clara**: Una empresa → Varias tiendas → Productos con stock
-   ✅ **Sistema de roles mejorado**: 3 roles con separación clara de responsabilidades
-   ✅ **Separación de funciones**: ENCARGADO registra ingresos, VENDEDOR registra salidas
-   ✅ **Botones contextuales**: Solo ves los botones que puedes usar según tu rol
-   ✅ **Filtros funcionan en todas las secciones**: Empleados, Productos, Movimientos, Reportes
-   ✅ **Datos realistas**: Nombres de productos peruanos comunes

## 🔄 Flujo de Trabajo Típico

1. **ENCARGADO recibe mercancía** → Registra ingreso en el sistema
2. **VENDEDOR realiza venta** → Registra salida en el sistema
3. **ADMIN supervisa** → Revisa reportes, gestiona catálogo, administra personal

## ⚠️ Seguridad

-   ✅ Separación de responsabilidades (control interno)
-   ✅ Trazabilidad completa (quién hizo qué)
-   ✅ Prevención de fraudes (una persona no puede ingresar y sacar libremente)
-   ✅ Validaciones a nivel de controlador (no solo UI)
