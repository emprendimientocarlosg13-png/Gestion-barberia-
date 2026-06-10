# 💈 Maranatha System - Gestión de Barbería

Sistema web interno de gestión para barbería Maranatha. Controla transacciones de caja, registro de clientes, métodos de pago y reportes financieros en tiempo real.

## ✨ Características

- 📊 **Dashboard interactivo** con resumen de ingresos, egresos y balance
- 💰 **Módulo de Caja** - Registra ventas y gastos con múltiples métodos de pago
- 👤 **Gestión de Clientes** - Registra clientes con sus preferencias y gustos
- 📈 **Reportes Avanzados** - Análisis diario, métodos de pago, historial de transacciones
- 💳 **Múltiples métodos de pago** - Efectivo, Pago Móvil, Divisas, Transferencias
- 📱 **Interfaz Responsiva** - Funciona en computadora, tablet y dispositivos móviles
- 🔄 **Actualización en tiempo real** - Dashboard se actualiza automáticamente

## 🚀 Inicio Rápido

### Requisitos
- Python 3.7+
- pip (gestor de paquetes de Python)

### Instalación

1. **Clona el repositorio**
```bash
git clone https://github.com/emprendimientocarlosg13-png/Gestion-barberia-.git
cd Gestion-barberia-
```

2. **Instala las dependencias del backend**
```bash
cd backend
pip install -r requirements.txt
```

3. **Ejecuta el servidor Flask**
```bash
python app.py
```

El servidor estará disponible en `http://localhost:5000`

4. **Abre la aplicación web**

En tu navegador, abre la carpeta `frontend`:
```bash
# Opción 1: Abre directamente el archivo
# Haz doble clic en frontend/index.html

# Opción 2: Usa un servidor web local (recomendado)
# En la carpeta frontend, ejecuta:
python -m http.server 8000
# Luego abre: http://localhost:8000
```

## 📁 Estructura del Proyecto

```
Gestion-barberia-/
├── backend/
│   ├── app.py                 # API Flask principal
│   └── requirements.txt       # Dependencias de Python
├── frontend/
│   ├── index.html             # Interfaz HTML
│   ├── style.css              # Estilos CSS
│   └── app.js                 # Lógica JavaScript
└── README.md                  # Este archivo
```

## 🎯 Uso de la Aplicación

### 📊 Dashboard
- Vista general del negocio
- Resumen de ingresos y egresos totales
- Balance neto
- Reporte del día actual
- Desglose por método de pago

### 💰 Módulo de Caja

**Registrar Transacción:**
1. Ve a la pestaña "Caja"
2. Completa el formulario:
   - **Descripción**: Tipo de servicio o gasto
   - **Monto**: Cantidad en dinero
   - **Tipo**: Selecciona "Ingreso" (venta) o "Egreso" (gasto)
   - **Método**: Efectivo, Pago Móvil, Divisas, etc.
3. Haz clic en "Guardar Transacción"

**Historial:** Visualiza todas las transacciones registradas con opción de eliminar

### 👤 Gestión de Clientes

**Registrar Cliente:**
1. Ve a la pestaña "Clientes"
2. Completa el formulario:
   - **Nombre**: Nombre completo del cliente
   - **Teléfono**: Número de contacto
   - **Gustos**: Sus preferencias de corte (ej: "Degradado alto", "Corte militar")
3. Haz clic en "Registrar Cliente"

**Visualizar:** Ve la lista de clientes con sus preferencias

### 📈 Reportes

Visualiza:
- Resumen general de ingresos y egresos
- Balance neto total
- Total de clientes
- Desglose detallado por método de pago
- Últimas 10 transacciones

## 🔌 API REST

### Endpoints de Transacciones
- `GET /api/transacciones` - Obtiene todas las transacciones
- `POST /api/transacciones` - Crea una transacción
- `DELETE /api/transacciones/<id>` - Elimina una transacción

### Endpoints de Clientes
- `GET /api/clientes` - Obtiene todos los clientes
- `POST /api/clientes` - Registra un cliente
- `PUT /api/clientes/<id>` - Actualiza un cliente
- `DELETE /api/clientes/<id>` - Elimina un cliente

### Endpoints de Reportes
- `GET /api/reportes/resumen` - Resumen general
- `GET /api/reportes/diario` - Reporte del día actual

## 💾 Base de Datos

La aplicación usa **SQLite** con las siguientes tablas:

### Tabla: transacciones
```sql
- id (INTEGER PRIMARY KEY)
- fecha (TEXT)
- descripcion (TEXT)
- tipo (TEXT) - "Ingreso" o "Egreso"
- monto (REAL)
- metodo_pago (TEXT)
```

### Tabla: clientes
```sql
- id (INTEGER PRIMARY KEY)
- nombre (TEXT)
- telefono (TEXT)
- gustos (TEXT)
- fecha_registro (TEXT)
```

## 🎨 Personalización

### Cambiar Colores
Edita `frontend/style.css` y busca:
```css
--primary-color: #667eea;
--secondary-color: #764ba2;
```

### Cambiar Nombre de Barbería
Edita `frontend/index.html` línea con:
```html
<h1>💈 Maranatha System</h1>
```

### Cambiar Puerto
En `backend/app.py`, última línea:
```python
app.run(debug=True, host='0.0.0.0', port=5000)  # Cambia 5000 al puerto que quieras
```

## 🔐 Seguridad

⚠️ **Nota importante para producción:**
- Esta versión está en desarrollo local
- Para usar en producción:
  - Agrega autenticación de usuario
  - Usa HTTPS
  - Configura base de datos remota
  - Implementa validaciones de seguridad adicionales

## 📱 Compatibilidad

✅ Chrome  
✅ Firefox  
✅ Safari  
✅ Edge  
✅ Navegadores móviles  

## 🛠️ Troubleshooting

**Error: "No se puede conectar a la API"**
- Asegúrate que el servidor Flask está corriendo (`python app.py`)
- Verifica que el puerto 5000 está disponible

**Error: "No se encuentra la base de datos"**
- La base de datos se crea automáticamente en la primera ejecución
- Verifica permisos de escritura en la carpeta `backend`

**La interfaz web no aparece**
- Asegúrate de tener instalado un servidor web local
- O abre directamente el archivo `frontend/index.html`

## 📞 Soporte

Para reportar problemas o sugerencias, abre un issue en el repositorio.

## 📄 Licencia

Todos los derechos reservados © 2024 Maranatha System

---

**Versión**: 1.0  
**Última actualización**: 2024  
**Autor**: Carlos G
