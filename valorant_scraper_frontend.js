/**
 * AURORA Valorant Scraper Frontend Integration
 * Frontend components for Valorant data scraping visualization
 */

// Valorant Scraper API endpoints
const VALORANT_API = {
    scrape: '/valorant/scrape',
    player: '/valorant/player-analysis',
    meta: '/valorant/meta',
    matches: '/valorant/matches',
    stats: '/valorant/stats',
    status: '/valorant/status'
};

// Valorant Scraper Frontend Manager
class ValorantScraperManager {
    constructor() {
        this.cache = new Map();
        this.cacheTimeout = 1800000; // 30 minutes
        this.isScraping = false;
        this.scrapeProgress = 0;
    }

    async scrapeValorantData(scrapeType = 'full', playerName = null, playerTag = null) {
        if (this.isScraping) {
            throw new Error('Scraping already in progress');
        }

        this.isScraping = true;
        this.scrapeProgress = 0;

        try {
            const requestBody = {
                scrape_type: scrapeType
            };

            if (scrapeType === 'player' && playerName && playerTag) {
                requestBody.player_name = playerName;
                requestBody.player_tag = playerTag;
            }

            showLoading(`Scraping Valorant data (${scrapeType})...`);
            
            const response = await fetch(VALORANT_API.scrape, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestBody)
            });

            const result = await response.json();
            
            if (response.ok) {
                this.displayScrapeResults(result, scrapeType);
                return result;
            } else {
                throw new Error(result.detail || 'Scraping failed');
            }

        } catch (error) {
            console.error('Valorant scraping error:', error);
            showError(`Scraping failed: ${error.message}`);
            throw error;
        } finally {
            this.isScraping = false;
            this.scrapeProgress = 0;
            hideLoading();
        }
    }

    async analyzePlayer(playerName, playerTag) {
        try {
            showLoading(`Analyzing player ${playerName}#${playerTag}...`);
            
            const response = await fetch(VALORANT_API.player, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    player_name: playerName,
                    player_tag: playerTag,
                    include_trends: true
                })
            });

            const result = await response.json();
            
            if (response.ok) {
                this.displayPlayerAnalysis(result);
                return result;
            } else {
                throw new Error(result.detail || 'Player analysis failed');
            }

        } catch (error) {
            console.error('Player analysis error:', error);
            showError(`Player analysis failed: ${error.message}`);
            throw error;
        } finally {
            hideLoading();
        }
    }

    displayScrapeResults(results, scrapeType) {
        const container = document.getElementById('valorant-results');
        if (!container) return;

        let html = '';

        switch (scrapeType) {
            case 'full':
                html = this.createFullScrapeDisplay(results);
                break;
            case 'player':
                html = this.createPlayerScrapeDisplay(results);
                break;
            case 'meta':
                html = this.createMetaScrapeDisplay(results);
                break;
            case 'matches':
                html = this.createMatchScrapeDisplay(results);
                break;
        }

        container.innerHTML = html;
        this.animateResults();
    }

    createFullScrapeDisplay(results) {
        const report = results.scrape_report || {};
        const meta = results.meta_data || {};
        const matches = results.match_data || {};

        return `
            <div class="valorant-scrape-report">
                <div class="scrape-header">
                    <h3>🔍 Full Valorant Scrape Report</h3>
                    <span class="timestamp">${new Date(results.full_scrape_timestamp).toLocaleString()}</span>
                </div>
                
                <div class="scrape-stats">
                    <div class="stat-card">
                        <div class="stat-value">${report.total_matches_analyzed || 0}</div>
                        <div class="stat-label">Matches Analyzed</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${report.agents_tracked || 0}</div>
                        <div class="stat-label">Agents Tracked</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${meta.agent_meta?.length || 0}</div>
                        <div class="stat-label">Meta Entries</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${matches.match_data?.length || 0}</div>
                        <div class="stat-label">Recent Matches</div>
                    </div>
                </div>
            </div>
        `;
    }

    createPlayerScrapeDisplay(results) {
        const playerData = results.player_data || {};
        const trends = results.trends || {};
        const metaComparison = results.meta_comparison || {};

        return `
            <div class="valorant-player-analysis">
                <div class="player-header">
                    <h3>👤 Player Analysis: ${playerData.player_name}#${playerData.player_tag}</h3>
                    <div class="rank-badge ${playerData.rank?.toLowerCase() || 'unknown'}">${playerData.rank || 'Unknown'}</div>
                </div>
                
                <div class="player-stats">
                    <div class="stat-item">
                        <span class="stat-label">Win Rate</span>
                        <span class="stat-value">${(playerData.win_rate || 0).toFixed(1)}%</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">K/D Ratio</span>
                        <span class="stat-value">${(playerData.kd_ratio || 0).toFixed(2)}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Headshot %</span>
                        <span class="stat-value">${(playerData.headshot_pct || 0).toFixed(1)}%</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Main Agents</span>
                        <span class="stat-value">${playerData.agents_played || 'None'}</span>
                    </div>
                </div>
            </div>
        `;
    }

    createMetaScrapeDisplay(results) {
        const agentMeta = results.agent_meta || [];

        return `
            <div class="valorant-meta-analysis">
                <div class="meta-header">
                    <h3>📊 Current Meta Analysis</h3>
                    <span class="timestamp">${new Date(results.scrape_timestamp).toLocaleString()}</span>
                </div>
                
                <div class="meta-grid">
                    ${agentMeta.slice(0, 10).map(agent => `
                        <div class="agent-card">
                            <div class="agent-name">${agent.agent_name}</div>
                            <div class="agent-stats">
                                <div class="agent-stat">
                                    <span class="stat-label">Pick Rate</span>
                                    <span class="stat-value">${(agent.pick_rate || 0).toFixed(1)}%</span>
                                </div>
                                <div class="agent-stat">
                                    <span class="stat-label">Win Rate</span>
                                    <span class="stat-value">${(agent.win_rate || 0).toFixed(1)}%</span>
                                </div>
                                <div class="agent-stat">
                                    <span class="stat-label">K/D Avg</span>
                                    <span class="stat-value">${(agent.kd_average || 0).toFixed(2)}</span>
                                </div>
                            </div>
                            <div class="agent-role">${agent.role || 'Unknown'}</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    createMatchScrapeDisplay(results) {
        const matchData = results.match_data || [];
        const analysis = results.match_analysis || {};

        return `
            <div class="valorant-match-analysis">
                <div class="match-header">
                    <h3>⚔️ Recent Match Analysis</h3>
                    <span class="timestamp">${new Date(results.scrape_timestamp).toLocaleString()}</span>
                </div>
                
                <div class="match-summary">
                    <div class="summary-stat">
                        <span class="summary-value">${analysis.total_matches || 0}</span>
                        <span class="summary-label">Total Matches</span>
                    </div>
                </div>
            </div>
        `;
    }

    displayPlayerAnalysis(results) {
        this.displayScrapeResults(results, 'player');
    }

    animateResults() {
        const cards = document.querySelectorAll('.valorant-scrape-report, .valorant-player-analysis, .valorant-meta-analysis');
        cards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                card.style.transition = 'all 0.5s ease-out';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, index * 100);
        });
    }

    clearCache() {
        this.cache.clear();
    }
}

// Global Valorant scraper manager
const valorantScraperManager = new ValorantScraperManager();

// Valorant Scraper UI Components
class ValorantScraperUI {
    static createScrapeControlPanel() {
        return `
            <div class="valorant-scraper-controls">
                <div class="controls-header">
                    <h3>🔍 Valorant Data Scraper</h3>
                    <div class="scraper-status" id="scraper-status">
                        <span class="status-indicator online"></span>
                        <span>Ready</span>
                    </div>
                </div>
                
                <div class="scrape-options">
                    <div class="option-group">
                        <label>Scrape Type:</label>
                        <select id="scrape-type">
                            <option value="full">Full Scrape</option>
                            <option value="player">Player Analysis</option>
                            <option value="meta">Meta Analysis</option>
                            <option value="matches">Match Data</option>
                        </select>
                    </div>
                    
                    <div class="option-group player-inputs" id="player-inputs" style="display: none;">
                        <label>Player Name:</label>
                        <input type="text" id="player-name" placeholder="e.g., TenZ">
                        
                        <label>Player Tag:</label>
                        <input type="text" id="player-tag" placeholder="e.g., 1234">
                    </div>
                    
                    <div class="action-buttons">
                        <button class="btn btn-primary" onclick="startValorantScrape()">
                            🚀 Start Scraping
                        </button>
                        <button class="btn btn-secondary" onclick="getValorantStats()">
                            📊 Get Stats
                        </button>
                        <button class="btn btn-secondary" onclick="clearValorantCache()">
                            🗑️ Clear Cache
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    static createResultsContainer() {
        return `
            <div class="valorant-results-container">
                <div class="results-header">
                    <h3>📊 Scraping Results</h3>
                    <button class="btn btn-secondary" onclick="exportValorantData()">
                        📥 Export Data
                    </button>
                </div>
                <div id="valorant-results" class="results-content">
                    <p class="placeholder">Run a scrape to see results here...</p>
                </div>
            </div>
        `;
    }
}

// Global functions for UI interaction
async function startValorantScrape() {
    const scrapeType = document.getElementById('scrape-type').value;
    const playerName = document.getElementById('player-name').value;
    const playerTag = document.getElementById('player-tag').value;
    
    try {
        await valorantScraperManager.scrapeValorantData(scrapeType, playerName, playerTag);
    } catch (error) {
        console.error('Scraping failed:', error);
    }
}

async function getValorantStats() {
    try {
        const response = await fetch('/valorant/stats');
        const result = await response.json();
        
        if (response.ok) {
            valorantScraperManager.displayDatabaseStats(result);
        } else {
            showError('Failed to get stats');
        }
    } catch (error) {
        console.error('Failed to get stats:', error);
    }
}

function clearValorantCache() {
    valorantScraperManager.clearCache();
    showSuccess('Cache cleared successfully');
}

function exportValorantData() {
    showInfo('Export feature coming soon!');
}

// Handle scrape type change
document.addEventListener('change', (e) => {
    if (e.target.id === 'scrape-type') {
        const playerInputs = document.getElementById('player-inputs');
        playerInputs.style.display = e.target.value === 'player' ? 'block' : 'none';
    }
});

// Initialize Valorant scraper when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Add Valorant scraper controls to existing UI
    const existingPanel = document.querySelector('.analysis-panel');
    if (existingPanel) {
        const controlsHTML = ValorantScraperUI.createScrapeControlPanel();
        const resultsHTML = ValorantScraperUI.createResultsContainer();
        
        existingPanel.insertAdjacentHTML('beforeend', controlsHTML);
        existingPanel.insertAdjacentHTML('beforeend', resultsHTML);
    }
});

// Export for global use
window.valorantScraperManager = valorantScraperManager;
window.ValorantScraperUI = ValorantScraperUI;
window.startValorantScrape = startValorantScrape;
window.getValorantStats = getValorantStats;
window.clearValorantCache = clearValorantCache;
window.exportValorantData = exportValorantData;
