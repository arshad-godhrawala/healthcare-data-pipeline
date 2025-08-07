// Healthcare Dashboard JavaScript

// API Configuration
const API_BASE_URL = 'http://localhost:8002';
let selectedPatientId = null;
let vitalSignsChart = null;
let forecastChart = null;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Healthcare Dashboard Initializing...');
    
    // Load initial data
    loadDashboardStats();
    loadPatients();
    
    // Set up real-time updates
    setInterval(loadDashboardStats, 30000); // Update every 30 seconds
    setInterval(loadAlerts, 10000); // Update alerts every 10 seconds
    
    // Initialize charts
    initializeCharts();
    
    console.log('✅ Dashboard initialized successfully');
});

// API Functions
async function apiCall(endpoint, options = {}) {
    try {
        const response = await axios({
            url: `${API_BASE_URL}${endpoint}`,
            method: options.method || 'GET',
            data: options.data,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        });
        return response.data;
    } catch (error) {
        console.error(`API Error (${endpoint}):`, error);
        updateConnectionStatus(false);
        throw error;
    }
}

// Dashboard Stats
async function loadDashboardStats() {
    try {
        const stats = await apiCall('/system/stats');
        updateDashboardStats(stats);
        updateConnectionStatus(true);
    } catch (error) {
        console.error('Error loading dashboard stats:', error);
        updateConnectionStatus(false);
    }
}

function updateDashboardStats(stats) {
    document.getElementById('total-patients').textContent = stats.total_patients || 0;
    document.getElementById('total-readings').textContent = stats.recent_vital_readings || 0;
    
    // Update active patients count
    const activePatients = document.getElementById('active-patients');
    if (stats.active_patients !== undefined) {
        activePatients.textContent = stats.active_patients;
    }
}

// Patient Management
async function loadPatients() {
    try {
        const patients = await apiCall('/patients');
        displayPatients(patients);
    } catch (error) {
        console.error('Error loading patients:', error);
        displayPatients([]);
    }
}

function displayPatients(patients) {
    const patientList = document.getElementById('patient-list');
    
    if (patients.length === 0) {
        patientList.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-user-friends"></i>
                <p>No patients found</p>
                <button class="btn btn-primary btn-sm" onclick="showAddPatientModal()">
                    <i class="fas fa-plus me-1"></i>Add Patient
                </button>
            </div>
        `;
        return;
    }
    
    patientList.innerHTML = `
        <div class="mb-2">
            <button class="btn btn-primary btn-sm" onclick="showAddPatientModal()">
                <i class="fas fa-plus me-1"></i>Add Patient
            </button>
        </div>
    `;
    
    patients.forEach(patient => {
        const patientElement = document.createElement('div');
        patientElement.className = 'patient-item';
        patientElement.onclick = () => selectPatient(patient.patient_id);
        patientElement.innerHTML = `
            <div class="patient-name">${patient.patient_name}</div>
            <div class="patient-info">
                ID: ${patient.patient_id} | ${patient.gender || 'N/A'}
            </div>
            <div class="mt-2">
                <button class="btn btn-outline-primary btn-action" onclick="event.stopPropagation(); showAddVitalSignModal(${patient.patient_id})">
                    <i class="fas fa-plus"></i> Vital
                </button>
                <button class="btn btn-outline-info btn-action" onclick="event.stopPropagation(); loadPatientSummary(${patient.patient_id})">
                    <i class="fas fa-chart-bar"></i> Summary
                </button>
            </div>
        `;
        patientList.appendChild(patientElement);
    });
}

function selectPatient(patientId) {
    selectedPatientId = patientId;
    
    // Update active state
    document.querySelectorAll('.patient-item').forEach(item => {
        item.classList.remove('active');
    });
    event.target.closest('.patient-item').classList.add('active');
    
    // Load patient data
    loadPatientVitals(patientId);
    loadPatientSummary(patientId);
    loadPatientAlerts(patientId);
    loadPatientForecast(patientId);
}

// Vital Signs
async function loadPatientVitals(patientId) {
    try {
        const vitals = await apiCall(`/patients/${patientId}/vitals?hours=24`);
        updateVitalSignsChart(vitals);
    } catch (error) {
        console.error('Error loading vitals:', error);
        updateVitalSignsChart([]);
    }
}

function updateVitalSignsChart(vitals) {
    if (!vitalSignsChart) return;
    
    const vitalType = document.getElementById('vital-sign-selector').value;
    const labels = vitals.map(v => new Date(v.timestamp).toLocaleTimeString());
    const data = vitals.map(v => v[vitalType]).filter(v => v !== null && v !== undefined);
    
    vitalSignsChart.data.labels = labels;
    vitalSignsChart.data.datasets[0].data = data;
    vitalSignsChart.data.datasets[0].label = vitalType.replace('_', ' ').toUpperCase();
    vitalSignsChart.update();
}

// Health Summary
async function loadPatientSummary(patientId) {
    try {
        const summary = await apiCall(`/patients/${patientId}/health-summary`);
        displayHealthSummary(summary);
    } catch (error) {
        console.error('Error loading health summary:', error);
        displayHealthSummary({});
    }
}

function displayHealthSummary(summary) {
    const container = document.getElementById('health-summary');
    
    if (!summary || Object.keys(summary).length === 0) {
        container.innerHTML = '<p class="text-muted">No health summary available</p>';
        return;
    }
    
    let html = '<h6>Health Summary</h6>';
    
    if (summary.trends) {
        Object.entries(summary.trends).forEach(([metric, data]) => {
            if (data && data.current_value !== null) {
                const trendClass = data.trend === 'increasing' ? 'up' : 
                                 data.trend === 'decreasing' ? 'down' : 'stable';
                html += `
                    <div class="health-metric">
                        <span class="metric-label">${metric.replace('_', ' ').toUpperCase()}</span>
                        <div>
                            <span class="metric-value">${data.current_value}</span>
                            <span class="metric-trend ${trendClass}">${data.trend}</span>
                        </div>
                    </div>
                `;
            }
        });
    }
    
    container.innerHTML = html;
}

// Alerts
async function loadAlerts() {
    if (!selectedPatientId) return;
    
    try {
        const alerts = await apiCall(`/patients/${selectedPatientId}/alerts`);
        displayAlerts(alerts);
    } catch (error) {
        console.error('Error loading alerts:', error);
    }
}

async function loadPatientAlerts(patientId) {
    try {
        const alerts = await apiCall(`/patients/${patientId}/alerts`);
        displayAlerts(alerts);
    } catch (error) {
        console.error('Error loading patient alerts:', error);
        displayAlerts([]);
    }
}

function displayAlerts(alerts) {
    const container = document.getElementById('alerts-container');
    const alertCount = document.getElementById('active-alerts');
    
    alertCount.textContent = alerts.length;
    
    if (alerts.length === 0) {
        container.innerHTML = '<p class="text-muted">No active alerts</p>';
        return;
    }
    
    let html = '';
    alerts.forEach(alert => {
        const severityClass = alert.severity === 'high' ? '' : 
                            alert.severity === 'medium' ? 'warning' : 'info';
        html += `
            <div class="alert-item ${severityClass}">
                <div class="alert-severity">${alert.severity.toUpperCase()}</div>
                <div class="alert-message">${alert.message}</div>
                <div class="alert-time">${new Date(alert.timestamp).toLocaleString()}</div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

// Forecasting
async function loadPatientForecast(patientId) {
    try {
        const forecast = await apiCall(`/patients/${patientId}/forecast?hours=24`);
        displayForecast(forecast);
    } catch (error) {
        console.error('Error loading forecast:', error);
        displayForecast({});
    }
}

function displayForecast(forecast) {
    const container = document.getElementById('forecast-details');
    
    if (!forecast || !forecast.forecasts || Object.keys(forecast.forecasts).length === 0) {
        container.innerHTML = '<p class="text-muted">No forecast data available</p>';
        return;
    }
    
    let html = '';
    Object.entries(forecast.forecasts).forEach(([vital, data]) => {
        if (data && data.forecast_values && data.forecast_values.length > 0) {
            const lastValue = data.forecast_values[data.forecast_values.length - 1];
            html += `
                <div class="forecast-metric">
                    <div class="metric-title">${vital.replace('_', ' ').toUpperCase()}</div>
                    <div class="metric-value">${lastValue.toFixed(1)}</div>
                </div>
            `;
        }
    });
    
    container.innerHTML = html;
    
    // Update forecast chart
    updateForecastChart(forecast);
}

function updateForecastChart(forecast) {
    if (!forecastChart || !forecast.forecasts) return;
    
    const vitalType = 'heart_rate'; // Default to heart rate
    const data = forecast.forecasts[vitalType];
    
    if (data && data.forecast_values) {
        forecastChart.data.labels = data.timestamps.map(t => new Date(t).toLocaleTimeString());
        forecastChart.data.datasets[0].data = data.forecast_values;
        forecastChart.data.datasets[1].data = data.lower_bound;
        forecastChart.data.datasets[2].data = data.upper_bound;
        forecastChart.update();
    }
}

// Charts
function initializeCharts() {
    // Vital Signs Chart
    const vitalCtx = document.getElementById('vitalSignsChart').getContext('2d');
    vitalSignsChart = new Chart(vitalCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Heart Rate',
                data: [],
                borderColor: '#007bff',
                backgroundColor: 'rgba(0, 123, 255, 0.1)',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: false
                }
            },
            plugins: {
                legend: {
                    display: true
                }
            }
        }
    });
    
    // Forecast Chart
    const forecastCtx = document.getElementById('forecastChart').getContext('2d');
    forecastChart = new Chart(forecastCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Forecast',
                data: [],
                borderColor: '#28a745',
                backgroundColor: 'rgba(40, 167, 69, 0.1)',
                tension: 0.4
            }, {
                label: 'Lower Bound',
                data: [],
                borderColor: '#ffc107',
                backgroundColor: 'rgba(255, 193, 7, 0.1)',
                tension: 0.4,
                borderDash: [5, 5]
            }, {
                label: 'Upper Bound',
                data: [],
                borderColor: '#dc3545',
                backgroundColor: 'rgba(220, 53, 69, 0.1)',
                tension: 0.4,
                borderDash: [5, 5]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: false
                }
            },
            plugins: {
                legend: {
                    display: true
                }
            }
        }
    });
}

// Modal Functions
function showAddPatientModal() {
    const modal = new bootstrap.Modal(document.getElementById('addPatientModal'));
    modal.show();
}

function showAddVitalSignModal(patientId) {
    selectedPatientId = patientId;
    const modal = new bootstrap.Modal(document.getElementById('addVitalSignModal'));
    modal.show();
}

async function addPatient() {
    const form = document.getElementById('addPatientForm');
    const formData = new FormData(form);
    
    const patientData = {
        patient_name: document.getElementById('patientName').value,
        date_of_birth: document.getElementById('patientDOB').value,
        gender: document.getElementById('patientGender').value,
        address: document.getElementById('patientAddress').value
    };
    
    try {
        await apiCall('/patients', {
            method: 'POST',
            data: patientData
        });
        
        // Close modal and refresh
        bootstrap.Modal.getInstance(document.getElementById('addPatientModal')).hide();
        form.reset();
        loadPatients();
        showMessage('Patient added successfully!', 'success');
    } catch (error) {
        console.error('Error adding patient:', error);
        showMessage('Error adding patient', 'error');
    }
}

async function addVitalSign() {
    const vitalData = {
        heart_rate: parseFloat(document.getElementById('vitalHeartRate').value) || null,
        systolic: parseFloat(document.getElementById('vitalSystolic').value) || null,
        diastolic: parseFloat(document.getElementById('vitalDiastolic').value) || null,
        temperature: parseFloat(document.getElementById('vitalTemperature').value) || null,
        respiration: parseInt(document.getElementById('vitalRespiration').value) || null,
        oxygen_saturation: parseFloat(document.getElementById('vitalOxygen').value) || null,
        timestamp: new Date().toISOString()
    };
    
    try {
        await apiCall(`/patients/${selectedPatientId}/vitals`, {
            method: 'POST',
            data: vitalData
        });
        
        // Close modal and refresh
        bootstrap.Modal.getInstance(document.getElementById('addVitalSignModal')).hide();
        document.getElementById('addVitalSignForm').reset();
        
        // Refresh patient data
        if (selectedPatientId) {
            loadPatientVitals(selectedPatientId);
            loadPatientSummary(selectedPatientId);
            loadPatientAlerts(selectedPatientId);
        }
        
        showMessage('Vital sign added successfully!', 'success');
    } catch (error) {
        console.error('Error adding vital sign:', error);
        showMessage('Error adding vital sign', 'error');
    }
}

// Utility Functions
function updateConnectionStatus(connected) {
    const statusElement = document.getElementById('connection-status');
    const indicator = document.querySelector('.connection-indicator');
    
    if (connected) {
        statusElement.textContent = 'Connected';
        indicator.className = 'connection-indicator connected';
    } else {
        statusElement.textContent = 'Disconnected';
        indicator.className = 'connection-indicator disconnected';
    }
}

function showMessage(message, type) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.textContent = message;
    
    document.body.insertBefore(messageDiv, document.body.firstChild);
    
    setTimeout(() => {
        messageDiv.remove();
    }, 5000);
}

// Event Listeners
document.getElementById('vital-sign-selector').addEventListener('change', function() {
    if (selectedPatientId) {
        loadPatientVitals(selectedPatientId);
    }
});

// Global functions for HTML onclick
window.showAddPatientModal = showAddPatientModal;
window.showAddVitalSignModal = showAddVitalSignModal;
window.addPatient = addPatient;
window.addVitalSign = addVitalSign;
window.loadPatients = loadPatients;
window.loadPatientSummary = loadPatientSummary;
window.updateVitalSignsChart = function() {
    if (selectedPatientId) {
        loadPatientVitals(selectedPatientId);
    }
}; 