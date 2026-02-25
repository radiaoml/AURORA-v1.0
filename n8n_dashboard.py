"""
AURORA n8n Visualization Dashboard
Simple web interface to visualize n8n workflows and status
"""

from flask import Flask, render_template_string, jsonify, request
import requests
import json
from datetime import datetime
import os

app = Flask(__name__)

# n8n configuration
N8N_URL = "http://localhost:5678"
N8N_AUTH = ("aurora", "tactical_intel_2026")

# HTML template for the dashboard
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AURORA n8n Workflow Dashboard</title>
    <style>
        :root {
            --bg-deep: #020617;
            --riot-red: #ff4655;
            --tactical-cyan: #00f5d4;
            --neural-blue: #3b82f6;
            --glass: rgba(15, 23, 42, 0.7);
            --border: rgba(255, 255, 255, 0.08);
            --font-main: 'Outfit', sans-serif;
            --font-mono: 'JetBrains Mono', monospace;
        }

        body {
            background: var(--bg-deep);
            color: #cbd5e1;
            font-family: var(--font-main);
            margin: 0;
            padding: 20px;
            min-height: 100vh;
        }

        .dashboard-header {
            text-align: center;
            margin-bottom: 40px;
            padding: 20px;
            background: var(--glass);
            border: 1px solid var(--border);
            border-radius: 12px;
        }

        .dashboard-title {
            font-size: 2.5rem;
            font-weight: 900;
            background: linear-gradient(135deg, var(--tactical-cyan), var(--neural-blue));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }

        .dashboard-subtitle {
            font-size: 1rem;
            color: #94a3b8;
            font-family: var(--font-mono);
            letter-spacing: 2px;
            text-transform: uppercase;
        }

        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }

        .status-card {
            background: var(--glass);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
            position: relative;
            overflow: hidden;
        }

        .status-card::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--tactical-cyan), var(--neural-blue));
        }

        .status-title {
            font-size: 1.2rem;
            font-weight: 700;
            margin-bottom: 15px;
            color: #cbd5e1;
        }

        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }

        .status-online {
            background: #10b981;
            box-shadow: 0 0 10px #10b981;
        }

        .status-offline {
            background: #ef4444;
            box-shadow: 0 0 10px #ef4444;
        }

        .status-warning {
            background: #f59e0b;
            box-shadow: 0 0 10px #f59e0b;
        }

        .workflow-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
        }

        .workflow-card {
            background: var(--glass);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
            position: relative;
        }

        .workflow-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }

        .workflow-name {
            font-size: 1.1rem;
            font-weight: 700;
            color: #cbd5e1;
        }

        .workflow-status {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: uppercase;
        }

        .workflow-active {
            background: rgba(16, 185, 129, 0.2);
            color: #10b981;
            border: 1px solid #10b981;
        }

        .workflow-inactive {
            background: rgba(239, 68, 68, 0.2);
            color: #ef4444;
            border: 1px solid #ef4444;
        }

        .workflow-info {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin-top: 15px;
        }

        .info-item {
            font-size: 0.9rem;
            color: #94a3b8;
        }

        .info-label {
            font-family: var(--font-mono);
            text-transform: uppercase;
            font-size: 0.7rem;
            color: #64748b;
        }

        .control-panel {
            background: var(--glass);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
        }

        .btn {
            background: linear-gradient(135deg, var(--tactical-cyan), var(--neural-blue));
            color: #020617;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            font-weight: 700;
            cursor: pointer;
            margin-right: 10px;
            margin-bottom: 10px;
            transition: all 0.3s ease;
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 245, 212, 0.3);
        }

        .btn-secondary {
            background: var(--glass);
            color: var(--tactical-cyan);
            border: 1px solid var(--tactical-cyan);
        }

        .log-viewer {
            background: var(--glass);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
            margin-top: 20px;
            max-height: 400px;
            overflow-y: auto;
        }

        .log-entry {
            font-family: var(--font-mono);
            font-size: 0.8rem;
            margin-bottom: 5px;
            padding: 5px;
            border-left: 2px solid var(--tactical-cyan);
        }

        .refresh-indicator {
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--glass);
            border: 1px solid var(--tactical-cyan);
            border-radius: 50%;
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .refresh-indicator:hover {
            background: var(--tactical-cyan);
            color: var(--bg-deep);
        }

        .refresh-indicator.spinning {
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }

        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }

        .metric-item {
            text-align: center;
            padding: 15px;
            background: rgba(255, 255, 255, 0.02);
            border-radius: 8px;
        }

        .metric-value {
            font-size: 1.8rem;
            font-weight: 900;
            color: var(--tactical-cyan);
            font-family: var(--font-mono);
        }

        .metric-label {
            font-size: 0.8rem;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
    </style>
</head>
<body>
    <div class="dashboard-header">
        <h1 class="dashboard-title">AURORA n8n WORKFLOW DASHBOARD</h1>
        <p class="dashboard-subtitle">Multi-Agent Pipeline Orchestration</p>
    </div>

    <div class="control-panel">
        <h3>Control Center</h3>
        <button class="btn" onclick="refreshDashboard()">🔄 Refresh</button>
        <button class="btn btn-secondary" onclick="toggleAutoRefresh()">🔧 Auto Refresh: <span id="auto-status">OFF</span></button>
        <button class="btn btn-secondary" onclick="viewLogs()">📋 View Logs</button>
    </div>

    <div class="status-grid">
        <div class="status-card">
            <h3 class="status-title">n8n Service Status</h3>
            <div id="n8n-status">
                <span class="status-indicator status-offline"></span>
                <span>Checking...</span>
            </div>
            <div class="metrics-grid">
                <div class="metric-item">
                    <div class="metric-value" id="workflow-count">0</div>
                    <div class="metric-label">Workflows</div>
                </div>
                <div class="metric-item">
                    <div class="metric-value" id="execution-count">0</div>
                    <div class="metric-label">Executions</div>
                </div>
            </div>
        </div>

        <div class="status-card">
            <h3 class="status-title">AURORA Backend</h3>
            <div id="backend-status">
                <span class="status-indicator status-offline"></span>
                <span>Checking...</span>
            </div>
        </div>

        <div class="status-card">
            <h3 class="status-title">Intelligence System</h3>
            <div id="intelligence-status">
                <span class="status-indicator status-offline"></span>
                <span>Checking...</span>
            </div>
        </div>
    </div>

    <div class="workflow-grid" id="workflow-grid">
        <!-- Workflows will be populated here -->
    </div>

    <div class="log-viewer" id="log-viewer" style="display: none;">
        <h3>System Logs</h3>
        <div id="log-content">
            <!-- Logs will be populated here -->
        </div>
    </div>

    <div class="refresh-indicator" onclick="refreshDashboard()" id="refresh-btn">
        🔄
    </div>

    <script>
        let autoRefreshInterval = null;
        let autoRefreshEnabled = false;

        async function checkServiceStatus() {
            try {
                // Check n8n status
                const n8nResponse = await fetch('/api/n8n-status');
                const n8nData = await n8nResponse.json();
                updateStatusCard('n8n-status', n8nData.status, n8nData.message);

                // Check backend status
                const backendResponse = await fetch('/api/backend-status');
                const backendData = await backendResponse.json();
                updateStatusCard('backend-status', backendData.status, backendData.message);

                // Check intelligence status
                const intelResponse = await fetch('/api/intelligence-status');
                const intelData = await intelResponse.json();
                updateStatusCard('intelligence-status', intelData.status, intelData.message);

                // Update metrics
                document.getElementById('workflow-count').textContent = n8nData.workflows || 0;
                document.getElementById('execution-count').textContent = n8nData.executions || 0;

            } catch (error) {
                console.error('Error checking service status:', error);
            }
        }

        function updateStatusCard(elementId, status, message) {
            const element = document.getElementById(elementId);
            const indicator = element.querySelector('.status-indicator');
            const text = element.querySelector('span:last-child');
            
            indicator.className = 'status-indicator';
            
            if (status === 'online') {
                indicator.classList.add('status-online');
            } else if (status === 'warning') {
                indicator.classList.add('status-warning');
            } else {
                indicator.classList.add('status-offline');
            }
            
            text.textContent = message;
        }

        async function loadWorkflows() {
            try {
                const response = await fetch('/api/workflows');
                const workflows = await response.json();
                
                const grid = document.getElementById('workflow-grid');
                grid.innerHTML = '';
                
                workflows.forEach(workflow => {
                    const card = createWorkflowCard(workflow);
                    grid.appendChild(card);
                });
            } catch (error) {
                console.error('Error loading workflows:', error);
            }
        }

        function createWorkflowCard(workflow) {
            const card = document.createElement('div');
            card.className = 'workflow-card';
            
            const statusClass = workflow.active ? 'workflow-active' : 'workflow-inactive';
            const statusText = workflow.active ? 'ACTIVE' : 'INACTIVE';
            
            card.innerHTML = `
                <div class="workflow-header">
                    <div class="workflow-name">${workflow.name}</div>
                    <div class="workflow-status ${statusClass}">${statusText}</div>
                </div>
                <div class="workflow-info">
                    <div class="info-item">
                        <div class="info-label">ID</div>
                        <div>${workflow.id}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Nodes</div>
                        <div>${workflow.nodes?.length || 0}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Last Run</div>
                        <div>${workflow.lastRun || 'Never'}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Type</div>
                        <div>${workflow.tags?.join(', ') || 'General'}</div>
                    </div>
                </div>
            `;
            
            return card;
        }

        function refreshDashboard() {
            const btn = document.getElementById('refresh-btn');
            btn.classList.add('spinning');
            
            Promise.all([
                checkServiceStatus(),
                loadWorkflows()
            ]).finally(() => {
                setTimeout(() => {
                    btn.classList.remove('spinning');
                }, 1000);
            });
        }

        function toggleAutoRefresh() {
            autoRefreshEnabled = !autoRefreshEnabled;
            const statusSpan = document.getElementById('auto-status');
            
            if (autoRefreshEnabled) {
                statusSpan.textContent = 'ON';
                autoRefreshInterval = setInterval(refreshDashboard, 10000); // Refresh every 10 seconds
            } else {
                statusSpan.textContent = 'OFF';
                if (autoRefreshInterval) {
                    clearInterval(autoRefreshInterval);
                    autoRefreshInterval = null;
                }
            }
        }

        function viewLogs() {
            const logViewer = document.getElementById('log-viewer');
            const logContent = document.getElementById('log-content');
            
            if (logViewer.style.display === 'none') {
                logViewer.style.display = 'block';
                loadLogs();
            } else {
                logViewer.style.display = 'none';
            }
        }

        async function loadLogs() {
            try {
                const response = await fetch('/api/logs');
                const logs = await response.json();
                
                const logContent = document.getElementById('log-content');
                logContent.innerHTML = '';
                
                logs.forEach(log => {
                    const entry = document.createElement('div');
                    entry.className = 'log-entry';
                    entry.textContent = `[${log.timestamp}] ${log.level}: ${log.message}`;
                    logContent.appendChild(entry);
                });
                
                logContent.scrollTop = logContent.scrollHeight;
            } catch (error) {
                console.error('Error loading logs:', error);
            }
        }

        // Initial load
        document.addEventListener('DOMContentLoaded', () => {
            refreshDashboard();
        });
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    return render_template_string(DASHBOARD_TEMPLATE)

@app.route('/api/n8n-status')
def n8n_status():
    try:
        response = requests.get(f"{N8N_URL}/healthz", auth=N8N_AUTH, timeout=5)
        if response.status_code == 200:
            return {
                "status": "online",
                "message": "n8n service is running",
                "workflows": len(response.json().get('workflows', [])),
                "executions": response.json().get('executions', 0)
            }
        else:
            return {"status": "warning", "message": f"n8n responding with code {response.status_code}"}
    except requests.exceptions.ConnectionError:
        return {"status": "offline", "message": "Cannot connect to n8n service"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.route('/api/backend-status')
def backend_status():
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            return {"status": "online", "message": "AURORA backend is running"}
        else:
            return {"status": "warning", "message": f"Backend responding with code {response.status_code}"}
    except requests.exceptions.ConnectionError:
        return {"status": "offline", "message": "Cannot connect to AURORA backend"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.route('/api/intelligence-status')
def intelligence_status():
    try:
        response = requests.get("http://localhost:8000/intelligence/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {"status": "online", "message": "Intelligence system active", "features": data.get("supported_features", [])}
        else:
            return {"status": "warning", "message": f"Intelligence system responding with code {response.status_code}"}
    except requests.exceptions.ConnectionError:
        return {"status": "offline", "message": "Cannot connect to intelligence system"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.route('/api/workflows')
def get_workflows():
    try:
        response = requests.get(f"{N8N_URL}/api/v1/workflows", auth=N8N_AUTH, timeout=5)
        if response.status_code == 200:
            workflows = response.json().get('data', [])
            
            # Format workflows for display
            formatted_workflows = []
            for wf in workflows:
                formatted_workflows.append({
                    "id": wf.get("id"),
                    "name": wf.get("name"),
                    "active": wf.get("active", False),
                    "nodes": wf.get("nodes", []),
                    "tags": wf.get("tags", []),
                    "lastRun": wf.get("lastRun", "Never")
                })
            
            return {"workflows": formatted_workflows}
        else:
            return {"workflows": []}
    except Exception as e:
        return {"workflows": [], "error": str(e)}

@app.route('/api/logs')
def get_logs():
    # Mock logs for demonstration
    import random
    from datetime import datetime, timedelta
    
    logs = []
    levels = ["INFO", "WARNING", "ERROR", "DEBUG"]
    messages = [
        "n8n workflow execution started",
        "AURORA backend processing request",
        "Intelligence system cache updated",
        "VOD analysis completed successfully",
        "Multi-agent pipeline activated",
        "Performance benchmarks updated"
    ]
    
    for i in range(20):
        timestamp = datetime.now() - timedelta(minutes=random.randint(0, 60))
        logs.append({
            "timestamp": timestamp.strftime("%H:%M:%S"),
            "level": random.choice(levels),
            "message": random.choice(messages)
        })
    
    return {"logs": sorted(logs, key=lambda x: x["timestamp"], reverse=True)}

if __name__ == '__main__':
    print("🚀 AURORA n8n Dashboard starting...")
    print("📊 Dashboard will be available at: http://localhost:5000")
    print("🔧 Make sure n8n is running on http://localhost:5678")
    print("🧠 Make sure AURORA backend is running on http://localhost:8000")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
