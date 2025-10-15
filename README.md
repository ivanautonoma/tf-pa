# 📦 Sistema de Inventario Multitienda

Sistema de gestión de inventario para múltiples tiendas con control de roles y permisos.

## 🚀 Características

-   ✅ **Gestión multitienda** - Controla el inventario de varias sucursales
-   ✅ **Sistema de roles** - 3 niveles de acceso (Admin, Encargado, Vendedor)
-   ✅ **Control de stock** - Seguimiento en tiempo real por tienda
-   ✅ **Registro de movimientos** - Ingresos y salidas con trazabilidad
-   ✅ **Reportes y filtros** - Visualización por tienda y estado de stock
-   ✅ **Interfaz gráfica** - UI moderna con Tkinter
-   ✅ **Base de datos SQLite** - Sin dependencias externas

## 📋 Requisitos

-   Python 3.8 o superior
-   Tkinter (incluido en Python estándar)
-   SQLite3 (incluido en Python estándar)

## 🛠️ Instalación

1. **Clonar el repositorio:**

```bash
git clone <url-del-repositorio>
cd inventarios_multitienda
```

2. **Ejecutar la aplicación:**

```bash
python main.py
```

**¡Eso es todo!** La primera vez que ejecutes la aplicación:

-   Se creará automáticamente la base de datos `inventario.db`
-   Se inicializará con datos de prueba
-   Se crearán usuarios, tiendas, productos y movimientos de ejemplo

## 🔑 Credenciales por Defecto

| Usuario | Contraseña | Rol       | Descripción        |
| ------- | ---------- | --------- | ------------------ |
| admin   | admin      | ADMIN     | Administrador      |
| carlos  | 123        | ENCARGADO | Encargado (Centro) |
| maria   | 123        | ENCARGADO | Encargada (Norte)  |
| juan    | 123        | VENDEDOR  | Vendedor (Sur)     |
| ana     | 123        | VENDEDOR  | Vendedora (Centro) |

## 👥 Roles y Permisos

### ADMIN (Administrador)

-   ✅ Gestionar tiendas, empleados y productos
-   ✅ Registrar ingresos y salidas
-   ✅ Acceso total a todos los reportes

### ENCARGADO (Jefe de Tienda)

-   ✅ Registrar INGRESOS de mercancía
-   ✅ Registrar salidas/ventas
-   ✅ Consultar productos y reportes
-   ❌ No puede crear/editar productos ni empleados

### VENDEDOR (Cajero)

-   ✅ Registrar SALIDAS (ventas)
-   ✅ Consultar productos y reportes
-   ❌ No puede registrar ingresos
-   ❌ No puede crear/editar productos

## 📂 Estructura del Proyecto

```
inventarios_multitienda/
├── inventory_app/
│   ├── domain/          # Modelos de dominio e interfaces
│   ├── infra/           # Repositorios y base de datos
│   ├── services/        # Lógica de negocio
│   └── mvc/             # Arquitectura MVC
│       ├── models/      # Modelos de datos
│       ├── views/       # Vistas de la UI
│       └── controllers/ # Controladores
├── main.py              # Punto de entrada
├── DATOS_DE_PRUEBA.md   # Documentación de datos de prueba
└── README.md            # Este archivo
```

## 🎯 Uso Básico

### Como Encargado:

1. Inicia sesión con usuario de encargado
2. Ve a **Movimientos**
3. Haz clic en **"Registrar Ingreso"** (botón verde)
4. Selecciona tienda, producto y cantidad
5. Agrega una nota (opcional)
6. Confirma el ingreso

### Como Vendedor:

1. Inicia sesión con usuario de vendedor
2. Ve a **Movimientos**
3. Haz clic en **"Registrar Salida"** (botón rojo)
4. Selecciona el producto a vender
5. Ingresa cantidad y nota
6. Confirma la salida

### Como Admin:

1. Acceso completo a todas las funcionalidades
2. Puede gestionar todo el sistema
3. Crear nuevas tiendas, productos y empleados

## 📊 Reportes

La sección de **Reportes** permite:

-   Filtrar por tienda usando el dropdown superior
-   Filtrar por estado de stock (Todos, OK, Bajo mínimo, Sin stock)
-   Combinar ambos filtros para análisis específicos
-   Ver stock en tiempo real por tienda

## 🔄 Arquitectura

El sistema usa:

-   **Arquitectura MVC** - Separación clara de responsabilidades
-   **Repository Pattern** - Abstracción de acceso a datos
-   **Service Layer** - Lógica de negocio centralizada
-   **SQLite** - Base de datos liviana y portable

## 📝 Notas para Desarrollo

-   La base de datos se crea automáticamente al iniciar
-   Los datos de prueba solo se cargan si la BD está vacía
-   Para resetear el sistema, elimina `inventario.db` y vuelve a ejecutar
-   El sistema usa SQLite Row Factory para acceso tipo diccionario

## 🤝 Contribuir

Este es un proyecto académico. Si deseas mejorarlo:

1. Haz fork del repositorio
2. Crea una rama para tu feature
3. Haz commit de tus cambios
4. Envía un pull request

## 📄 Licencia

Proyecto académico - Libre uso para fines educativos

## 👨‍💻 Autor

Desarrollado como trabajo final para la Universidad Autónoma

---

**¿Preguntas?** Consulta `DATOS_DE_PRUEBA.md` para más detalles sobre los datos de prueba y casos de uso.
