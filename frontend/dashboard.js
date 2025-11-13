const API_URL = 'http://localhost:5000/api';
let currentFilter = 'all';

// Check authentication
function checkAuth() {
    const token = localStorage.getItem('access_token');
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    
    if (!token) {
        window.location.href = 'index.html';
        return null;
    }
    
    // Display user info
    document.getElementById('username').textContent = user.username || 'User';
    const roleBadge = document.getElementById('userRole');
    roleBadge.textContent = user.role || 'user';
    roleBadge.className = `badge ${user.role === 'admin' ? 'critical' : 'medium'}`;
    
    return token;
}

// API call with authentication
async function apiCall(endpoint, options = {}) {
    const token = localStorage.getItem('access_token');
    
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        }
    };
    
    const response = await fetch(`${API_URL}${endpoint}`, {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...options.headers
        }
    });
    
    if (response.status === 401) {
        // Token expired, redirect to login
        localStorage.clear();
        window.location.href = 'index.html';
        return null;
    }
    
    return response;
}

// Load statistics
async function loadStatistics() {
    try {
        const [assetsRes, alertsRes] = await Promise.all([
            apiCall('/assets'),
            apiCall('/alerts/statistics')
        ]);
        
        const assets = await assetsRes.json();
        const stats = await alertsRes.json();
        
        document.getElementById('totalAssets').textContent = assets.length;
        document.getElementById('totalAlerts').textContent = stats.total_alerts;
        document.getElementById('criticalAlerts').textContent = stats.critical_alerts;
        document.getElementById('openAlerts').textContent = stats.open_alerts;
    } catch (error) {
        console.error('Error loading statistics:', error);
    }
}

// Load assets
async function loadAssets() {
    try {
        const response = await apiCall('/assets');
        const assets = await response.json();
        
        const tbody = document.getElementById('assetsBody');
        tbody.innerHTML = '';
        
        assets.slice(0, 10).forEach(asset => {
            const row = tbody.insertRow();
            row.innerHTML = `
                <td>${asset.name}</td>
                <td>${asset.asset_type || 'N/A'}</td>
                <td>${asset.ip_address || 'N/A'}</td>
                <td>${asset.os || 'N/A'}</td>
                <td><span class="badge ${asset.criticality}">${asset.criticality}</span></td>
            `;
        });
        
        document.getElementById('assetsLoading').style.display = 'none';
        document.getElementById('assetsTable').style.display = 'table';
    } catch (error) {
        console.error('Error loading assets:', error);
    }
}

// Load alerts
async function loadAlerts(status = null) {
    try {
        let endpoint = '/alerts';
        if (status && status !== 'all') {
            endpoint += `?status=${status}`;
        }
        
        const response = await apiCall(endpoint);
        const alerts = await response.json();
        
        const tbody = document.getElementById('alertsBody');
        tbody.innerHTML = '';
        
        alerts.slice(0, 20).forEach(alert => {
            const row = tbody.insertRow();
            row.innerHTML = `
                <td>${alert.cve_id || 'N/A'}</td>
                <td>${alert.asset_name || 'N/A'}</td>
                <td>${alert.title}</td>
                <td><span class="badge ${alert.severity}">${alert.severity}</span></td>
                <td>${alert.cvss_score || 'N/A'}</td>
                <td>${alert.priority_score || 'N/A'}</td>
                <td>${alert.status}</td>
                <td>
                    ${alert.status === 'open' ? `<button class="btn btn-primary" onclick="resolveAlert(${alert.id})">Resolve</button>` : '-'}
                </td>
            `;
        });
        
        document.getElementById('alertsLoading').style.display = 'none';
        document.getElementById('alertsTable').style.display = 'table';
    } catch (error) {
        console.error('Error loading alerts:', error);
    }
}

// Filter alerts
function filterAlerts(status) {
    currentFilter = status;
    
    // Update tab styles
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });
    event.target.classList.add('active');
    
    loadAlerts(status);
}

// Resolve alert
async function resolveAlert(alertId) {
    try {
        const response = await apiCall(`/alerts/${alertId}/resolve`, {
            method: 'POST'
        });
        
        if (response.ok) {
            loadAlerts(currentFilter);
            loadStatistics();
        }
    } catch (error) {
        console.error('Error resolving alert:', error);
    }
}

// Logout
function logout() {
    localStorage.clear();
    window.location.href = 'index.html';
}

// Initialize dashboard
window.onload = function() {
    if (checkAuth()) {
        loadStatistics();
        loadAssets();
        loadAlerts();
    }
};
