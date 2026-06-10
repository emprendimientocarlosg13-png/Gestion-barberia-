from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# Configuración
DATABASE = "sistema_interno.db"

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
    
    conn.commit()
    conn.close()

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
    return jsonify({'status': 'ok', 'message': 'Maranatha System API running'}), 200

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
