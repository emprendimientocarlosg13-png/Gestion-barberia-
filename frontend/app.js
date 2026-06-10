// Configuración
const API_URL = 'http://localhost:5000/api';

// ========== UTILIDADES ==========
function showAlert(message, type = 'success') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert ${type}`;
    alertDiv.textContent = message;
    alertDiv.style.position = 'fixed';
    alertDiv.style.top = '20px';
    alertDiv.style.right = '20px';
    alertDiv.style.zIndex = '1000';
    alertDiv.style.maxWidth = '400px';
    
    document.body.appendChild(alertDiv);
    
    setTimeout(() => alertDiv.remove(), 3000);
}

function formatCurrency(value) {
    return new Intl.NumberFormat('es-VE', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2
    }).format(value);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-VE') + ' ' + date.toLocaleTimeString('es-VE', { hour: '2-digit', minute: '2-digit' });
}

// ========== TAB NAVIGATION ==========
function setupTabNavigation() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active class from all tabs and contents
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            
            // Add active class to clicked tab
            btn.classList.add('active');
            const tabName = btn.dataset.tab;
            document.getElementById(tabName).classList.add('active');
            
            // Cargar datos cuando se abre la pestaña
            if (tabName === 'caja') {
                loadTransacciones();
            } else if (tabName === 'clientes') {
                loadClientes();
            } else if (tabName === 'reportes') {
                loadReportes();
            }
        });
    });
}

// ========== DASHBOARD ==========
async function loadDashboard() {
    try {
        const response = await fetch(`${API_URL}/reportes/resumen`);
        const data = await response.json();
        
        // Actualizar cards
        document.getElementById('total-ingresos').textContent = formatCurrency(data.ingresos);
        document.getElementById('total-egresos').textContent = formatCurrency(data.egresos);
        document.getElementById('balance-neto').textContent = formatCurrency(data.balance);
        document.getElementById('total-clientes-count').textContent = data.total_clientes;
        
        // Reporte del día
        const dayResponse = await fetch(`${API_URL}/reportes/diario`);
        const dayData = await dayResponse.json();
        document.getElementById('ingresos-hoy').textContent = formatCurrency(dayData.ingresos);
        document.getElementById('egresos-hoy').textContent = formatCurrency(dayData.egresos);
        document.getElementById('balance-hoy').textContent = formatCurrency(dayData.balance);
        
        // Métodos de pago
        const metodosGrid = document.getElementById('metodos-pago-grid');
        metodosGrid.innerHTML = '';
        
        if (Object.keys(data.metodos_pago).length === 0) {
            metodosGrid.innerHTML = '<p class="text-center">Sin transacciones aún</p>';
        } else {
            Object.entries(data.metodos_pago).forEach(([metodo, total]) => {
                const div = document.createElement('div');
                div.className = 'metodo-item';
                div.innerHTML = `
                    <span>${metodo}</span>
                    <strong>${formatCurrency(total)}</strong>
                `;
                metodosGrid.appendChild(div);
            });
        }
    } catch (error) {
        console.error('Error cargando dashboard:', error);
        showAlert('Error cargando dashboard', 'error');
    }
}

// ========== TRANSACCIONES (CAJA) ==========
async function loadTransacciones() {
    try {
        const response = await fetch(`${API_URL}/transacciones`);
        const transacciones = await response.json();
        
        const tbody = document.getElementById('transacciones-body');
        tbody.innerHTML = '';
        
        if (transacciones.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center">Sin transacciones registradas</td></tr>';
            return;
        }
        
        transacciones.forEach(t => {
            const row = document.createElement('tr');
            const tipoClass = t.tipo === 'Ingreso' ? 'ingresos' : 'egresos';
            const signo = t.tipo === 'Ingreso' ? '+' : '-';
            
            row.innerHTML = `
                <td>${formatDate(t.fecha)}</td>
                <td>${t.descripcion}</td>
                <td><span class="${tipoClass}">${t.tipo}</span></td>
                <td><strong>${signo}${formatCurrency(t.monto)}</strong></td>
                <td>${t.metodo_pago}</td>
                <td><button class="btn btn-danger" onclick="deleteTransaccion(${t.id})">🗑️ Eliminar</button></td>
            `;
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Error cargando transacciones:', error);
        showAlert('Error cargando transacciones', 'error');
    }
}

async function deleteTransaccion(id) {
    if (!confirm('¿Estás seguro de que quieres eliminar esta transacción?')) return;
    
    try {
        const response = await fetch(`${API_URL}/transacciones/${id}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showAlert('Transacción eliminada');
            loadTransacciones();
            loadDashboard();
        }
    } catch (error) {
        console.error('Error eliminando transacción:', error);
        showAlert('Error eliminando transacción', 'error');
    }
}

// ========== FORM TRANSACCIONES ==========
function setupFormTransaccion() {
    const form = document.getElementById('form-transaccion');
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const descripcion = document.getElementById('desc').value;
        const monto = parseFloat(document.getElementById('monto').value);
        const tipo = document.getElementById('tipo').value;
        const metodo_pago = document.getElementById('metodo').value;
        
        try {
            const response = await fetch(`${API_URL}/transacciones`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    descripcion,
                    monto,
                    tipo,
                    metodo_pago
                })
            });
            
            if (response.ok) {
                showAlert('✅ Transacción guardada correctamente');
                form.reset();
                loadTransacciones();
                loadDashboard();
            }
        } catch (error) {
            console.error('Error:', error);
            showAlert('Error al guardar transacción', 'error');
        }
    });
}

// ========== CLIENTES ==========
async function loadClientes() {
    try {
        const response = await fetch(`${API_URL}/clientes`);
        const clientes = await response.json();
        
        const grid = document.getElementById('clientes-grid');
        grid.innerHTML = '';
        
        if (clientes.length === 0) {
            grid.innerHTML = '<div class="text-center" style="grid-column: 1/-1; padding: 40px;">Sin clientes registrados</div>';
            return;
        }
        
        clientes.forEach(c => {
            const card = document.createElement('div');
            card.className = 'cliente-card';
            card.innerHTML = `
                <h3>👤 ${c.nombre}</h3>
                <p><strong>Teléfono:</strong> ${c.telefono}</p>
                <p><strong>Gustos:</strong></p>
                <span class="gustos">${c.gustos}</span>
                <div class="cliente-actions">
                    <button class="btn btn-secondary" onclick="deleteCliente(${c.id})">🗑️ Eliminar</button>
                </div>
            `;
            grid.appendChild(card);
        });
    } catch (error) {
        console.error('Error cargando clientes:', error);
        showAlert('Error cargando clientes', 'error');
    }
}

async function deleteCliente(id) {
    if (!confirm('¿Estás seguro de que quieres eliminar este cliente?')) return;
    
    try {
        const response = await fetch(`${API_URL}/clientes/${id}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showAlert('Cliente eliminado');
            loadClientes();
            loadDashboard();
        }
    } catch (error) {
        console.error('Error eliminando cliente:', error);
        showAlert('Error eliminando cliente', 'error');
    }
}

// ========== FORM CLIENTES ==========
function setupFormCliente() {
    const form = document.getElementById('form-cliente');
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const nombre = document.getElementById('nombre').value;
        const telefono = document.getElementById('telefono').value;
        const gustos = document.getElementById('gustos').value;
        
        try {
            const response = await fetch(`${API_URL}/clientes`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    nombre,
                    telefono,
                    gustos
                })
            });
            
            if (response.ok) {
                showAlert('✅ Cliente registrado correctamente');
                form.reset();
                loadClientes();
                loadDashboard();
            }
        } catch (error) {
            console.error('Error:', error);
            showAlert('Error al registrar cliente', 'error');
        }
    });
}

// ========== REPORTES ==========
async function loadReportes() {
    try {
        const response = await fetch(`${API_URL}/reportes/resumen`);
        const data = await response.json();
        
        // Resumen general
        document.getElementById('rep-ingresos').textContent = formatCurrency(data.ingresos);
        document.getElementById('rep-egresos').textContent = formatCurrency(data.egresos);
        document.getElementById('rep-balance').textContent = formatCurrency(data.balance);
        document.getElementById('rep-clientes').textContent = data.total_clientes;
        
        // Métodos de pago en reportes
        const metodosReporte = document.getElementById('metodos-reporte');
        metodosReporte.innerHTML = '';
        
        if (Object.keys(data.metodos_pago).length === 0) {
            metodosReporte.innerHTML = '<p>Sin datos</p>';
        } else {
            const ul = document.createElement('ul');
            Object.entries(data.metodos_pago).forEach(([metodo, total]) => {
                const li = document.createElement('li');
                li.innerHTML = `<strong>${metodo}:</strong> ${formatCurrency(total)}`;
                ul.appendChild(li);
            });
            metodosReporte.appendChild(ul);
        }
        
        // Últimas transacciones
        const transResponse = await fetch(`${API_URL}/transacciones`);
        const transacciones = await transResponse.json();
        
        const tbody = document.getElementById('ultimas-transacciones');
        tbody.innerHTML = '';
        
        transacciones.slice(0, 10).forEach(t => {
            const row = document.createElement('tr');
            const signo = t.tipo === 'Ingreso' ? '+' : '-';
            
            row.innerHTML = `
                <td>${formatDate(t.fecha)}</td>
                <td>${t.descripcion}</td>
                <td>${t.tipo}</td>
                <td><strong>${signo}${formatCurrency(t.monto)}</strong></td>
            `;
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Error cargando reportes:', error);
        showAlert('Error cargando reportes', 'error');
    }
}

// ========== INICIALIZACIÓN ==========
function init() {
    setupTabNavigation();
    setupFormTransaccion();
    setupFormCliente();
    loadDashboard();
}

// Ejecutar cuando el DOM está listo
document.addEventListener('DOMContentLoaded', init);

// Refrescar dashboard cada 30 segundos
setInterval(loadDashboard, 30000);
