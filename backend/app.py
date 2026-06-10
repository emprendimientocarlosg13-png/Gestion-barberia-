from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from twilio.rest import Client

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuración
DATABASE = "sistema_interno.db"

# Twilio Configuration
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', '')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', '')
TWILIO_WHATSAPP_FROM = os.getenv('TWILIO_WHATSAPP_FROM', '')
BARBERIA_NOMBRE = os.getenv('BARBERIA_NOMBRE', 'Maranatha System')

# Inicializar cliente de Twilio si hay credenciales
twilio_client = None
if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# --- FUNCIONES DE BASE DE DATOS ---
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Inicializa las tablas si no existen"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transacciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            descripcion TEXT,
            tipo TEXT,
            monto REAL,
            metodo_pago TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            telefono TEXT,
            gustos TEXT,
            fecha_registro TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS citas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            cliente_nombre TEXT,
            cliente_telefono TEXT,
            fecha_cita TEXT,
            hora_cita TEXT,
            servicio TEXT,
            estado TEXT,
            notas TEXT,
            fecha_registro TEXT,
            recordatorio_enviado INTEGER DEFAULT 0,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        )
    ''')
    
    conn.commit()
    conn.close()

# --- FUNCIONES DE WHATSAPP ---
def send_whatsapp_message(phone_number, message):
    """Envía mensaje por WhatsApp usando Twilio"""
    try:
        if not twilio_client:
            return {'success': False, 'error': 'Twilio no configurado'}
        
        # Formatear número de teléfono
        if not phone_number.startswith('whatsapp:'):
            phone_number = f'whatsapp:{phone_number}'
        
        message_obj = twilio_client.messages.create(
            from_=TWILIO_WHATSAPP_FROM,
            body=message,
            to=phone_number
        )
        
        return {'success': True, 'message_id': message_obj.sid}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def send_reminder_whatsapp(cita_id):
    """Envía recordatorio de cita por WhatsApp"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM citas WHERE id = ?', (cita_id,))
        cita = cursor.fetchone()
        conn.close()
        
        if not cita:
            return {'success': False, 'error': 'Cita no encontrada'}
        
        mensaje = f"""
👋 Hola {cita['cliente_nombre']},

📅 Recordatorio de tu cita en {BARBERIA_NOMBRE}:

📆 Fecha: {cita['fecha_cita']}
⏰ Hora: {cita['hora_cita']}
💈 Servicio: {cita['servicio']}

¿Confirmas tu asistencia? Responde SÍ o NO

¡Gracias!
        """.strip()
        
        result = send_whatsapp_message(cita['cliente_telefono'], mensaje)
        
        # Marcar recordatorio como enviado
        if result['success']:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('UPDATE citas SET recordatorio_enviado = 1 WHERE id = ?', (cita_id,))
            conn.commit()
            conn.close()
        
        return result
    except Exception as e:
        return {'success': False, 'error': str(e)}

# --- ENDPOINTS: TRANSACCIONES (CAJA) ---

@app.route('/api/transacciones', methods=['GET'])
def get_transacciones():
    """Obtiene todas las transacciones"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM transacciones ORDER BY fecha DESC')
    transacciones = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(transacciones)

@app.route('/api/transacciones', methods=['POST'])
def crear_transaccion():
    """Crea una nueva transacción"""
    data = request.json
    
    try:
        descripcion = data.get('descripcion', '').strip().capitalize()
        monto = float(data.get('monto', 0))
        tipo = data.get('tipo', 'Ingreso')
        metodo_pago = data.get('metodo_pago', 'EFECTIVO').upper()
        
        fecha_hoy = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO transacciones (fecha, descripcion, tipo, monto, metodo_pago)
            VALUES (?, ?, ?, ?, ?)
        ''', (fecha_hoy, descripcion, tipo, monto, metodo_pago))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Transacción guardada'}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/transacciones/<int:id>', methods=['DELETE'])
def eliminar_transaccion(id):
    """Elimina una transacción"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM transacciones WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Transacción eliminada'}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# --- ENDPOINTS: CLIENTES ---

@app.route('/api/clientes', methods=['GET'])
def get_clientes():
    """Obtiene todos los clientes"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clientes ORDER BY nombre ASC')
    clientes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(clientes)

@app.route('/api/clientes', methods=['POST'])
def crear_cliente():
    """Crea un nuevo cliente"""
    data = request.json
    
    try:
        nombre = data.get('nombre', '').strip().title()
        telefono = data.get('telefono', '').strip()
        gustos = data.get('gustos', '').strip().capitalize()
        fecha_registro = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO clientes (nombre, telefono, gustos, fecha_registro)
            VALUES (?, ?, ?, ?)
        ''', (nombre, telefono, gustos, fecha_registro))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Cliente registrado'}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/clientes/<int:id>', methods=['DELETE'])
def eliminar_cliente(id):
    """Elimina un cliente"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM clientes WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Cliente eliminado'}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/clientes/<int:id>', methods=['PUT'])
def actualizar_cliente(id):
    """Actualiza datos de un cliente"""
    data = request.json
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE clientes 
            SET nombre = ?, telefono = ?, gustos = ?
            WHERE id = ?
        ''', (data.get('nombre'), data.get('telefono'), data.get('gustos'), id))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Cliente actualizado'}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# --- ENDPOINTS: CITAS ---

@app.route('/api/citas', methods=['GET'])
def get_citas():
    """Obtiene todas las citas"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM citas ORDER BY fecha_cita DESC, hora_cita DESC')
    citas = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(citas)

@app.route('/api/citas/disponibles', methods=['GET'])
def get_horas_disponibles():
    """Obtiene horas disponibles para una fecha"""
    fecha = request.args.get('fecha', '')
    
    if not fecha:
        return jsonify({'success': False, 'error': 'Fecha requerida'}), 400
    
    # Horas disponibles (de 8:00 a 20:00 cada 30 minutos)
    horas_totales = []
    for hora in range(8, 20):
        for minuto in ['00', '30']:
            horas_totales.append(f'{hora:02d}:{minuto}')
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT hora_cita FROM citas WHERE fecha_cita = ? AND estado != ?',
            (fecha, 'cancelada')
        )
        horas_ocupadas = [row['hora_cita'] for row in cursor.fetchall()]
        conn.close()
        
        horas_disponibles = [h for h in horas_totales if h not in horas_ocupadas]
        
        return jsonify({
            'success': True,
            'horas_disponibles': horas_disponibles,
            'total': len(horas_disponibles)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/citas', methods=['POST'])
def crear_cita():
    """Crea una nueva cita"""
    data = request.json
    
    try:
        cliente_id = data.get('cliente_id')
        cliente_nombre = data.get('cliente_nombre', '').strip().title()
        cliente_telefono = data.get('cliente_telefono', '').strip()
        fecha_cita = data.get('fecha_cita', '')
        hora_cita = data.get('hora_cita', '')
        servicio = data.get('servicio', 'Corte').strip()
        notas = data.get('notas', '').strip()
        
        if not all([fecha_cita, hora_cita, cliente_nombre, cliente_telefono]):
            return jsonify({'success': False, 'error': 'Datos incompletos'}), 400
        
        # Validar que la fecha sea futura
        fecha_obj = datetime.strptime(fecha_cita, '%Y-%m-%d')
        if fecha_obj.date() < datetime.now().date():
            return jsonify({'success': False, 'error': 'La fecha debe ser futura'}), 400
        
        fecha_registro = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO citas (cliente_id, cliente_nombre, cliente_telefono, fecha_cita, hora_cita, servicio, estado, notas, fecha_registro)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (cliente_id, cliente_nombre, cliente_telefono, fecha_cita, hora_cita, servicio, 'confirmada', notas, fecha_registro))
        
        conn.commit()
        cita_id = cursor.lastrowid
        conn.close()
        
        # Enviar confirmación por WhatsApp
        mensaje_confirmacion = f"""
✅ Cita confirmada en {BARBERIA_NOMBRE}

📅 Fecha: {fecha_cita}
⏰ Hora: {hora_cita}
💈 Servicio: {servicio}

¡Te esperamos! 💈
        """.strip()
        
        send_whatsapp_message(cliente_telefono, mensaje_confirmacion)
        
        return jsonify({
            'success': True, 
            'message': 'Cita registrada',
            'cita_id': cita_id
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/citas/<int:id>', methods=['PUT'])
def actualizar_cita(id):
    """Actualiza una cita"""
    data = request.json
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE citas 
            SET cliente_nombre = ?, fecha_cita = ?, hora_cita = ?, servicio = ?, estado = ?, notas = ?
            WHERE id = ?
        ''', (
            data.get('cliente_nombre'),
            data.get('fecha_cita'),
            data.get('hora_cita'),
            data.get('servicio'),
            data.get('estado'),
            data.get('notas'),
            id
        ))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Cita actualizada'}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/citas/<int:id>', methods=['DELETE'])
def eliminar_cita(id):
    """Elimina/cancela una cita"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM citas WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Cita cancelada'}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/citas/<int:id>/recordatorio', methods=['POST'])
def enviar_recordatorio(id):
    """Envía recordatorio de cita por WhatsApp"""
    try:
        result = send_reminder_whatsapp(id)
        return jsonify(result), (200 if result['success'] else 400)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/citas/proximas/<int:dias>', methods=['GET'])
def get_proximas_citas(dias):
    """Obtiene citas de los próximos N días"""
    try:
        fecha_inicio = datetime.now().date()
        fecha_fin = fecha_inicio + timedelta(days=dias)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM citas 
            WHERE fecha_cita BETWEEN ? AND ? AND estado = 'confirmada'
            ORDER BY fecha_cita, hora_cita
        ''', (str(fecha_inicio), str(fecha_fin)))
        
        citas = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({'success': True, 'citas': citas})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# --- ENDPOINTS: REPORTES ---

@app.route('/api/reportes/resumen', methods=['GET'])
def get_resumen():
    """Obtiene el resumen financiero"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Ingresos y egresos
    cursor.execute("SELECT SUM(monto) FROM transacciones WHERE tipo = 'Ingreso'")
    ingresos = cursor.fetchone()[0] or 0.0
    
    cursor.execute("SELECT SUM(monto) FROM transacciones WHERE tipo = 'Egreso'")
    egresos = cursor.fetchone()[0] or 0.0
    
    # Total clientes
    cursor.execute("SELECT COUNT(*) FROM clientes")
    total_clientes = cursor.fetchone()[0] or 0
    
    # Citas próximas
    cursor.execute("SELECT COUNT(*) FROM citas WHERE estado = 'confirmada' AND fecha_cita >= ?", 
                   (datetime.now().strftime('%Y-%m-%d'),))
    proximas_citas = cursor.fetchone()[0] or 0
    
    # Métodos de pago
    cursor.execute("""
        SELECT metodo_pago, SUM(monto) as total 
        FROM transacciones 
        WHERE tipo = 'Ingreso'
        GROUP BY metodo_pago
    """)
    metodos = {row['metodo_pago']: row['total'] for row in cursor.fetchall()}
    
    conn.close()
    
    return jsonify({
        'ingresos': ingresos,
        'egresos': egresos,
        'balance': ingresos - egresos,
        'total_clientes': total_clientes,
        'proximas_citas': proximas_citas,
        'metodos_pago': metodos
    })

@app.route('/api/reportes/diario', methods=['GET'])
def get_reporte_diario():
    """Obtiene reporte del día actual"""
    fecha_hoy = datetime.now().strftime('%Y-%m-%d')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT tipo, SUM(monto) as total
        FROM transacciones
        WHERE fecha LIKE ?
        GROUP BY tipo
    ''', (f'{fecha_hoy}%',))
    
    resultados = cursor.fetchall()
    conn.close()
    
    reporte = {'ingresos': 0, 'egresos': 0}
    for row in resultados:
        if row['tipo'] == 'Ingreso':
            reporte['ingresos'] = row['total']
        else:
            reporte['egresos'] = row['total']
    
    reporte['balance'] = reporte['ingresos'] - reporte['egresos']
    return jsonify(reporte)

# --- HEALTH CHECK ---

@app.route('/api/health', methods=['GET'])
def health():
    whatsapp_status = 'conectado' if twilio_client else 'no configurado'
    return jsonify({
        'status': 'ok',
        'message': 'Maranatha System API running',
        'whatsapp': whatsapp_status
    }), 200

# --- ERROR HANDLERS ---

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'No encontrado'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Error interno del servidor'}), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
