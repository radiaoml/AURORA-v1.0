/**
 * AURORA Tactical System Frontend Integration
 * Integrates background tactical system with main AURORA HUD
 */

class AURORATacticalIntegration {
    constructor() {
        this.apiBase = 'http://localhost:8005';
        this.cache = new Map();
        this.cacheTimeout = 300000; // 5 minutes
        this.isConnected = false;
        this.lastUpdate = null;
        this.systemStatus = null;
        
        this.initializeIntegration();
    }

    async initializeIntegration() {
        try {
            // Check system health
            await this.checkSystemHealth();
            
            // Load system status
            await this.loadSystemStatus();
            
            // Initialize UI components
            this.createTacticalUI();
            
            // Start background monitoring
            this.startBackgroundMonitoring();
            
            this.isConnected = true;
            console.log('✅ AURORA Tactical System integrated successfully');
            
        } catch (error) {
            console.error('❌ Failed to integrate AURORA Tactical System:', error);
            this.showConnectionError(error);
        }
    }

    async checkSystemHealth() {
        try {
            const response = await fetch(`${this.apiBase}/system/health`);
            const health = await response.json();
            
            if (health.status !== 'healthy') {
                throw new Error(`System status: ${health.status}`);
            }
            
            return health;
        } catch (error) {
            throw new Error(`Health check failed: ${error.message}`);
        }
    }

    async loadSystemStatus() {
        try {
            const response = await fetch(`${this.apiBase}/status`);
            this.systemStatus = await response.json();
            this.lastUpdate = new Date();
            return this.systemStatus;
        } catch (error) {
            console.warn('Could not load system status:', error);
            return null;
        }
    }

    createTacticalUI() {
        // Create main tactical panel
        const tacticalPanel = document.createElement('div');
        tacticalPanel.id = 'aurora-tactical-panel';
        tacticalPanel.className = 'tactical-panel';
        tacticalPanel.innerHTML = `
            <div class="panel-header">
                <h3>🎯 AURORA Tactical System</h3>
                <div class="status-indicator" id="tactical-status">
                    <span class="status-dot"></span>
                    <span class="status-text">Connecting...</span>
                </div>
            </div>
            
            <div class="panel-content">
                <!-- System Overview -->
                <div class="section" id="system-overview">
                    <h4>📊 System Status</h4>
                    <div class="status-grid">
                        <div class="status-item">
                            <span class="label">Data Scraper</span>
                            <span class="value" id="scraper-status">Ready</span>
                        </div>
                        <div class="status-item">
                            <span class="label">Tactical Analysis</span>
                            <span class="value" id="analysis-status">Ready</span>
                        </div>
                        <div class="status-item">
                            <span class="label">Dataset</span>
                            <span class="value" id="dataset-status">400 samples</span>
                        </div>
                        <div class="status-item">
                            <span class="label">Intelligence</span>
                            <span class="value" id="intelligence-status">Active</span>
                        </div>
                    </div>
                </div>

                <!-- Tactical Analysis -->
                <div class="section" id="tactical-analysis">
                    <h4>⚡ Tactical Analysis</h4>
                    <div class="analysis-form">
                        <div class="form-row">
                            <label>Map:</label>
                            <select id="map-select">
                                <option value="BIND">BIND</option>
                                <option value="HAVEN">HAVEN</option>
                                <option value="SPLIT">SPLIT</option>
                                <option value="ASCENT">ASCENT</option>
                                <option value="ICEBOX">ICEBOX</option>
                                <option value="BREEZE">BREEZE</option>
                                <option value="FRACTURE">FRACTURE</option>
                                <option value="PEARL">PEARL</option>
                                <option value="LOTUS">LOTUS</option>
                                <option value="SUNSET">SUNSET</option>
                            </select>
                        </div>
                        <div class="form-row">
                            <label>Situation:</label>
                            <select id="situation-select">
                                <option value="entry">Entry</option>
                                <option value="retake">Retake</option>
                                <option value="post_plant">Post Plant</option>
                                <option value="eco">Eco</option>
                                <option value="buy_round">Buy Round</option>
                                <option value="force_buy">Force Buy</option>
                                <option value="mid_control">Mid Control</option>
                                <option value="flank">Flank</option>
                            </select>
                        </div>
                        <div class="form-row">
                            <label>Formation:</label>
                            <select id="formation-select">
                                <option value="tight">Tight</option>
                                <option value="balanced">Balanced</option>
                                <option value="spread">Spread</option>
                                <option value="scattered">Scattered</option>
                            </select>
                        </div>
                        <div class="form-row">
                            <label>Agents:</label>
                            <div class="agent-selector">
                                <label><input type="checkbox" value="JETT"> JETT</label>
                                <label><input type="checkbox" value="SOVA"> SOVA</label>
                                <label><input type="checkbox" value="VIPER"> VIPER</label>
                                <label><input type="checkbox" value="KILLJOY"> KILLJOY</label>
                                <label><input type="checkbox" value="REYNA"> REYNA</label>
                                <label><input type="checkbox" value="RAZE"> RAZE</label>
                            </div>
                        </div>
                        <button id="analyze-btn" class="analyze-button">
                            🎯 Analyze Tactical Situation
                        </button>
                    </div>
                </div>

                <!-- Analysis Results -->
                <div class="section hidden" id="analysis-results">
                    <h4>📈 Analysis Results</h4>
                    <div class="results-container" id="results-content">
                        <!-- Results will be populated here -->
                    </div>
                </div>

                <!-- Dataset Statistics -->
                <div class="section" id="dataset-stats">
                    <h4>📊 Dataset Statistics</h4>
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-value" id="total-samples">400</div>
                            <div class="stat-label">Total Samples</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value" id="avg-win-rate">64%</div>
                            <div class="stat-label">Avg Win Rate</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value" id="avg-entry-rating">3.6</div>
                            <div class="stat-label">Avg Entry Rating</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value" id="confidence-score">0.24</div>
                            <div class="stat-label">Confidence Score</div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Add styles
        this.addStyles();

        // Insert into main AURORA interface
        const mainContainer = document.querySelector('.main-content') || document.body;
        mainContainer.appendChild(tacticalPanel);

        // Setup event listeners
        this.setupEventListeners();
    }

    addStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .tactical-panel {
                background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                border: 2px solid #00ff88;
                border-radius: 15px;
                padding: 20px;
                margin: 20px 0;
                color: white;
                font-family: 'Orbitron', monospace;
                box-shadow: 0 8px 32px rgba(0, 255, 136, 0.3);
            }

            .panel-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
                padding-bottom: 15px;
                border-bottom: 2px solid rgba(0, 255, 136, 0.3);
            }

            .panel-header h3 {
                margin: 0;
                font-size: 1.5em;
                text-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
            }

            .status-indicator {
                display: flex;
                align-items: center;
                gap: 8px;
            }

            .status-dot {
                width: 12px;
                height: 12px;
                border-radius: 50%;
                background: #00ff88;
                animation: pulse 2s infinite;
            }

            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }

            .section {
                margin: 20px 0;
                padding: 15px;
                background: rgba(0, 0, 0, 0.3);
                border-radius: 10px;
                border: 1px solid rgba(0, 255, 136, 0.2);
            }

            .section h4 {
                margin: 0 0 15px 0;
                color: #00ff88;
                font-size: 1.2em;
            }

            .status-grid, .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
            }

            .status-item, .stat-card {
                background: rgba(0, 255, 136, 0.1);
                padding: 12px;
                border-radius: 8px;
                border: 1px solid rgba(0, 255, 136, 0.3);
            }

            .status-item .label {
                display: block;
                font-size: 0.9em;
                color: #aaa;
                margin-bottom: 5px;
            }

            .status-item .value {
                font-size: 1.1em;
                font-weight: bold;
                color: #00ff88;
            }

            .stat-card {
                text-align: center;
            }

            .stat-value {
                font-size: 1.8em;
                font-weight: bold;
                color: #00ff88;
                margin-bottom: 5px;
            }

            .stat-label {
                font-size: 0.9em;
                color: #aaa;
            }

            .analysis-form {
                display: grid;
                gap: 15px;
            }

            .form-row {
                display: grid;
                grid-template-columns: 120px 1fr;
                align-items: center;
                gap: 10px;
            }

            .form-row label {
                font-weight: bold;
                color: #00ff88;
            }

            .form-row select, .form-row input {
                padding: 8px 12px;
                border: 2px solid rgba(0, 255, 136, 0.3);
                border-radius: 5px;
                background: rgba(0, 0, 0, 0.5);
                color: white;
                font-family: inherit;
            }

            .agent-selector {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 8px;
            }

            .agent-selector label {
                display: flex;
                align-items: center;
                gap: 5px;
                font-size: 0.9em;
            }

            .analyze-button {
                background: linear-gradient(45deg, #00ff88, #00cc6a);
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                color: #000;
                font-weight: bold;
                font-size: 1em;
                cursor: pointer;
                transition: all 0.3s ease;
                margin-top: 10px;
            }

            .analyze-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0, 255, 136, 0.4);
            }

            .results-container {
                background: rgba(0, 0, 0, 0.2);
                padding: 15px;
                border-radius: 8px;
                border: 1px solid rgba(0, 255, 136, 0.2);
            }

            .hidden {
                display: none;
            }

            .recommendation-item {
                background: rgba(0, 255, 136, 0.1);
                padding: 10px;
                margin: 8px 0;
                border-radius: 5px;
                border-left: 3px solid #00ff88;
            }

            .performance-metric {
                display: flex;
                justify-content: space-between;
                padding: 8px 0;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }

            .performance-metric:last-child {
                border-bottom: none;
            }

            .metric-label {
                color: #aaa;
            }

            .metric-value {
                color: #00ff88;
                font-weight: bold;
            }
        `;
        document.head.appendChild(style);
    }

    setupEventListeners() {
        // Analyze button
        document.getElementById('analyze-btn').addEventListener('click', () => {
            this.performTacticalAnalysis();
        });

        // Auto-update stats
        setInterval(() => {
            this.updateSystemStatus();
            this.updateDatasetStats();
        }, 30000); // Update every 30 seconds
    }

    async performTacticalAnalysis() {
        const analyzeBtn = document.getElementById('analyze-btn');
        const resultsSection = document.getElementById('analysis-results');
        const resultsContent = document.getElementById('results-content');

        // Get form data
        const map = document.getElementById('map-select').value;
        const situation = document.getElementById('situation-select').value;
        const formation = document.getElementById('formation-select').value;
        
        // Get selected agents
        const agentCheckboxes = document.querySelectorAll('.agent-selector input:checked');
        const agents = Array.from(agentCheckboxes).map(cb => cb.value);

        if (agents.length === 0) {
            alert('Please select at least one agent');
            return;
        }

        // Show loading state
        analyzeBtn.textContent = '🔄 Analyzing...';
        analyzeBtn.disabled = true;

        try {
            const analysis = await this.analyzeTacticalSituation({
                map,
                tactical_situation: situation,
                formation,
                agents_detected: agents
            });

            // Display results
            this.displayAnalysisResults(analysis);
            resultsSection.classList.remove('hidden');

        } catch (error) {
            console.error('Analysis failed:', error);
            resultsContent.innerHTML = `
                <div class="error-message">
                    ❌ Analysis failed: ${error.message}
                </div>
            `;
            resultsSection.classList.remove('hidden');
        } finally {
            analyzeBtn.textContent = '🎯 Analyze Tactical Situation';
            analyzeBtn.disabled = false;
        }
    }

    async analyzeTacticalSituation(context) {
        const cacheKey = `tactical_${context.map}_${context.tactical_situation}_${context.formation}`;
        
        // Check cache
        if (this.cache.has(cacheKey)) {
            const cached = this.cache.get(cacheKey);
            if (Date.now() - cached.timestamp < this.cacheTimeout) {
                return cached.data;
            }
        }

        // Make API call
        const response = await fetch(`${this.apiBase}/aurora/tactical/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(context)
        });

        if (!response.ok) {
            throw new Error(`Analysis failed: ${response.statusText}`);
        }

        const analysis = await response.json();
        
        // Cache result
        this.cache.set(cacheKey, {
            data: analysis,
            timestamp: Date.now()
        });

        return analysis;
    }

    displayAnalysisResults(analysis) {
        const resultsContent = document.getElementById('results-content');
        
        const situation = analysis.situation_analysis || {};
        const benchmarks = analysis.performance_benchmarks || {};
        const recommendations = analysis.tactical_recommendations || {};

        resultsContent.innerHTML = `
            <div class="analysis-overview">
                <h5>📊 Situation Analysis</h5>
                <div class="performance-metric">
                    <span class="metric-label">Map:</span>
                    <span class="metric-value">${situation.map || 'Unknown'}</span>
                </div>
                <div class="performance-metric">
                    <span class="metric-label">Situation:</span>
                    <span class="metric-value">${situation.tactical_situation || 'Unknown'}</span>
                </div>
                <div class="performance-metric">
                    <span class="metric-label">Formation:</span>
                    <span class="metric-value">${situation.formation || 'Unknown'}</span>
                </div>
                <div class="performance-metric">
                    <span class="metric-label">Sample Count:</span>
                    <span class="metric-value">${situation.sample_count || 0}</span>
                </div>
                <div class="performance-metric">
                    <span class="metric-label">Confidence:</span>
                    <span class="metric-value">${((situation.confidence || 0) * 100).toFixed(1)}%</span>
                </div>
            </div>

            <div class="performance-benchmarks">
                <h5>📈 Performance Benchmarks</h5>
                <div class="performance-metric">
                    <span class="metric-label">Entry Rating:</span>
                    <span class="metric-value">${benchmarks.avg_entry_rating || 0}/5</span>
                </div>
                <div class="performance-metric">
                    <span class="metric-label">Timing Gap:</span>
                    <span class="metric-value">${benchmarks.avg_timing_gap || 0}s</span>
                </div>
                <div class="performance-metric">
                    <span class="metric-label">Formation Score:</span>
                    <span class="metric-value">${((benchmarks.avg_formation_score || 0) * 100).toFixed(1)}%</span>
                </div>
                <div class="performance-metric">
                    <span class="metric-label">Planting Score:</span>
                    <span class="metric-value">${((benchmarks.avg_planting_score || 0) * 100).toFixed(1)}%</span>
                </div>
                <div class="performance-metric">
                    <span class="metric-label">Win Rate:</span>
                    <span class="metric-value">${((benchmarks.avg_win_rate || 0) * 100).toFixed(1)}%</span>
                </div>
            </div>

            <div class="recommendations">
                <h5>🎯 Tactical Recommendations</h5>
                <div class="recommendation-item">
                    <strong>Positioning:</strong> ${recommendations.positioning_advice || 'Coordinate with team'}
                </div>
                <div class="recommendation-item">
                    <strong>Success Probability:</strong> ${((recommendations.success_probability || 0) * 100).toFixed(1)}%
                </div>
                ${recommendations.utility_usage ? recommendations.utility_usage.slice(0, 3).map(utility => 
                    `<div class="recommendation-item"><strong>Utility:</strong> ${utility}</div>`
                ).join('') : ''}
            </div>
        `;
    }

    async updateSystemStatus() {
        try {
            const status = await this.loadSystemStatus();
            if (status) {
                this.updateStatusIndicators(status);
            }
        } catch (error) {
            console.warn('Failed to update system status:', error);
        }
    }

    updateStatusIndicators(status) {
        const statusText = document.querySelector('.status-text');
        const statusDot = document.querySelector('.status-dot');
        
        if (statusText && statusDot) {
            statusText.textContent = 'Connected';
            statusDot.style.background = '#00ff88';
        }

        // Update component statuses
        const components = status.components || {};
        document.getElementById('scraper-status').textContent = components.data_scraper || 'Unknown';
        document.getElementById('analysis-status').textContent = components.tactical_analysis || 'Unknown';
        document.getElementById('intelligence-status').textContent = components.player_intelligence || 'Unknown';
    }

    async updateDatasetStats() {
        try {
            const response = await fetch(`${this.apiBase}/valorant/dataset/statistics`);
            const stats = await response.json();
            
            const overview = stats.dataset_overview || {};
            const averages = overview.performance_averages || {};
            
            document.getElementById('total-samples').textContent = overview.dataset_statistics?.total_analytics || 400;
            document.getElementById('avg-win-rate').textContent = `${((averages.win_rate || 0.64) * 100).toFixed(0)}%`;
            document.getElementById('avg-entry-rating').textContent = (averages.entry_rating || 3.6).toFixed(1);
            document.getElementById('confidence-score').textContent = (averages.confidence || 0.24).toFixed(2);
            
        } catch (error) {
            console.warn('Failed to update dataset stats:', error);
        }
    }

    startBackgroundMonitoring() {
        // Monitor connection status
        setInterval(async () => {
            try {
                await this.checkSystemHealth();
                if (!this.isConnected) {
                    this.isConnected = true;
                    this.updateStatusIndicators(this.systemStatus);
                }
            } catch (error) {
                if (this.isConnected) {
                    this.isConnected = false;
                    this.showConnectionError(error);
                }
            }
        }, 10000); // Check every 10 seconds
    }

    showConnectionError(error) {
        const statusText = document.querySelector('.status-text');
        const statusDot = document.querySelector('.status-dot');
        
        if (statusText && statusDot) {
            statusText.textContent = 'Disconnected';
            statusDot.style.background = '#ff4444';
        }
        
        console.error('AURORA Tactical System disconnected:', error);
    }
}

// Initialize integration when page loads
document.addEventListener('DOMContentLoaded', () => {
    // Wait a bit for main AURORA to load
    setTimeout(() => {
        window.auroraTactical = new AURORATacticalIntegration();
    }, 2000);
});

// Export for manual initialization
window.AURORATacticalIntegration = AURORATacticalIntegration;
