"""
AURORA Frontend Intelligence Integration
Enhanced frontend with player intelligence capabilities
"""

// Intelligence API endpoints
const INTELLIGENCE_API = {
    player: '/intelligence/player',
    enhance: '/intelligence/enhance-analysis',
    meta: '/intelligence/meta-trends',
    patterns: '/intelligence/patterns',
    status: '/intelligence/status'
};

// Intelligence state management
class IntelligenceManager {
    constructor() {
        this.cache = new Map();
        this.cacheTimeout = 3600000; // 1 hour
        this.isEnabled = true;
    }

    async function getPlayerIntelligence(riotId, username = null) {
        const cacheKey = `player_${riotId}_${username || ''}`;
        
        // Check cache first
        if (this.cache.has(cacheKey)) {
            const cached = this.cache.get(cacheKey);
            if (Date.now() - cached.timestamp < this.cacheTimeout) {
                return cached.data;
            }
        }

        try {
            const response = await fetch(INTELLIGENCE_API.player, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    riot_id: riotId,
                    username: username,
                    include_patterns: true,
                    include_meta: true
                })
            });

            const intelligence = await response.json();
            
            // Cache the result
            this.cache.set(cacheKey, {
                data: intelligence,
                timestamp: Date.now()
            });

            return intelligence;
        } catch (error) {
            console.error('Error fetching player intelligence:', error);
            return { error: 'Failed to fetch player intelligence' };
        }
    }

    async function enhanceAnalysis(analysisData, riotId, username) {
        if (!riotId && !username) return analysisData;

        try {
            const response = await fetch(INTELLIGENCE_API.enhance, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    source: analysisData.source,
                    type: analysisData.type,
                    player_riot_id: riotId,
                    player_username: username
                })
            });

            return await response.json();
        } catch (error) {
            console.error('Error enhancing analysis:', error);
            return analysisData;
        }
    }

    async function getMetaTrends() {
        try {
            const response = await fetch(INTELLIGENCE_API.meta);
            return await response.json();
        } catch (error) {
            console.error('Error fetching meta trends:', error);
            return { meta_trends: [] };
        }
    }

    function clearCache() {
        this.cache.clear();
    }
}

// Global intelligence manager
const intelligenceManager = new IntelligenceManager();

// Enhanced UI components
class IntelligenceUI {
    static createPlayerContextCard(playerData) {
        return `
            <div class="intelligence-card player-context">
                <div class="card-header">
                    <h3>🎯 Player Intelligence</h3>
                    <div class="rank-badge ${playerData.rank.toLowerCase()}">${playerData.rank}</div>
                </div>
                <div class="player-stats">
                    <div class="stat-item">
                        <span class="stat-label">Rank</span>
                        <span class="stat-value">${playerData.rank} ${playerData.tier}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Win Rate</span>
                        <span class="stat-value">${playerData.win_rate?.toFixed(1) || 0}%</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">K/D Ratio</span>
                        <span class="stat-value">${playerData.kd_ratio?.toFixed(2) || 0}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Main Agents</span>
                        <span class="stat-value">${(playerData.main_agents || []).join(', ')}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Playstyle</span>
                        <span class="stat-value">${playerData.playstyle || 'Unknown'}</span>
                    </div>
                </div>
            </div>
        `;
    }

    static createEnhancedMetricsCard(enhancedMetrics) {
        return `
            <div class="intelligence-card enhanced-metrics">
                <div class="card-header">
                    <h3>📊 Enhanced Metrics</h3>
                </div>
                <div class="metrics-grid">
                    <div class="metric-item">
                        <span class="metric-label">Rank-Adjusted OVR</span>
                        <span class="metric-value">${enhancedMetrics.rank_adjusted_ovr?.toFixed(1) || 0}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Skill Level Score</span>
                        <span class="metric-value">${enhancedMetrics.skill_level_score || 0}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Playstyle Efficiency</span>
                        <span class="metric-value">${enhancedMetrics.playstyle_efficiency?.toFixed(1) || 0}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Agent Mastery Bonus</span>
                        <span class="metric-value">+${enhancedMetrics.agent_mastery_bonus || 0}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Consistency</span>
                        <span class="metric-value">${enhancedMetrics.consistency_score || 'Unknown'}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Adaptability</span>
                        <span class="metric-value">${enhancedMetrics.adaptability_score || 'Unknown'}</span>
                    </div>
                </div>
            </div>
        `;
    }

    static createPersonalizedRecommendationsCard(recommendations) {
        if (!recommendations || recommendations.length === 0) {
            return '';
        }

        const recommendationsHtml = recommendations.map(rec => `
            <div class="recommendation-item ${rec.priority}-priority">
                <div class="rec-header">
                    <span class="rec-type">${rec.type}</span>
                    <span class="rec-priority ${rec.priority}">${rec.priority.toUpperCase()}</span>
                </div>
                <div class="rec-content">
                    <h4>${rec.title}</h4>
                    <p>${rec.description}</p>
                    <div class="rec-actions">
                        ${rec.actions.map(action => `<span class="action-tag">${action}</span>`).join('')}
                    </div>
                </div>
            </div>
        `).join('');

        return `
            <div class="intelligence-card recommendations">
                <div class="card-header">
                    <h3>🎯 Personalized Recommendations</h3>
                </div>
                <div class="recommendations-list">
                    ${recommendationsHtml}
                </div>
            </div>
        `;
    }

    static createPerformanceBenchmarksCard(benchmarks) {
        return `
            <div class="intelligence-card performance-benchmarks">
                <div class="card-header">
                    <h3>📈 Performance Benchmarks</h3>
                </div>
                <div class="benchmarks-content">
                    <div class="benchmark-comparison">
                        <h4>Rank Benchmarks</h4>
                        <div class="benchmark-grid">
                            <div class="benchmark-item">
                                <span class="benchmark-label">Kills</span>
                                <span class="benchmark-value">${benchmarks.rank_benchmarks?.kills || 0}</span>
                            </div>
                            <div class="benchmark-item">
                                <span class="benchmark-label">Deaths</span>
                                <span class="benchmark-value">${benchmarks.rank_benchmarks?.deaths || 0}</span>
                            </div>
                            <div class="benchmark-item">
                                <span class="benchmark-label">Assists</span>
                                <span class="benchmark-value">${benchmarks.rank_benchmarks?.assists || 0}</span>
                            </div>
                            <div class="benchmark-item">
                                <span class="benchmark-label">Win Rate</span>
                                <span class="benchmark-value">${benchmarks.rank_benchmarks?.win_rate || 0}%</span>
                            </div>
                        </div>
                    </div>
                    ${benchmarks.areas_for_improvement && benchmarks.areas_for_improvement.length > 0 ? `
                        <div class="improvement-areas">
                            <h4>Areas for Improvement</h4>
                            <div class="improvement-list">
                                ${benchmarks.areas_for_improvement.map(area => `
                                    <div class="improvement-item">
                                        <span class="improvement-icon">⚠️</span>
                                        <span class="improvement-text">${area}</span>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }

    static createMetaAnalysisCard(metaAnalysis) {
        return `
            <div class="intelligence-card meta-analysis">
                <div class="card-header">
                    <h3>🔮 Meta Analysis</h3>
                </div>
                <div class="meta-content">
                    <div class="meta-relevance">
                        <div class="relevance-score">
                            <span class="score-label">Meta Relevance</span>
                            <div class="score-bar">
                                <div class="score-fill" style="width: ${metaAnalysis.meta_relevance_score || 0}%"></div>
                            </div>
                            <span class="score-value">${metaAnalysis.meta_relevance_score?.toFixed(1) || 0}%</span>
                        </div>
                        <p class="meta-analysis-text">${metaAnalysis.analysis || 'No meta analysis available'}</p>
                    </div>
                    ${metaAnalysis.recommended_meta_agents && metaAnalysis.recommended_meta_agents.length > 0 ? `
                        <div class="recommended-agents">
                            <h4>Recommended Meta Agents</h4>
                            <div class="agents-list">
                                ${metaAnalysis.recommended_meta_agents.map(agent => `
                                    <div class="agent-item">
                                        <span class="agent-name">${agent}</span>
                                        <span class="agent-tag">META</span>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }
}

// Integration with existing AURORA functions
async function analyzeVodWithIntelligence(source, type, riotId, username) {
    try {
        // Show loading state
        showLoading('Analyzing with intelligence enhancement...');
        
        // Get base analysis
        const baseAnalysis = await analyzeVod(source, type);
        
        // Enhance with intelligence if player data provided
        if (riotId || username) {
            const enhancedAnalysis = await intelligenceManager.enhanceAnalysis(baseAnalysis, riotId, username);
            displayEnhancedAnalysis(enhancedAnalysis);
        } else {
            displayAnalysis(baseAnalysis);
        }
        
    } catch (error) {
        console.error('Error in enhanced analysis:', error);
        showError('Enhanced analysis failed. Please try again.');
    }
}

function displayEnhancedAnalysis(enhancedData) {
    // Clear existing content
    clearAnalysisDisplay();
    
    // Display enhanced sections
    const container = document.getElementById('analysis-results');
    
    // Player context
    if (enhancedData.player_context) {
        container.innerHTML += IntelligenceUI.createPlayerContextCard(enhancedData.player_context);
    }
    
    // Enhanced metrics
    if (enhancedData.enhanced_metrics) {
        container.innerHTML += IntelligenceUI.createEnhancedMetricsCard(enhancedData.enhanced_metrics);
    }
    
    // Personalized recommendations
    if (enhancedData.personalized_recommendations) {
        container.innerHTML += IntelligenceUI.createPersonalizedRecommendationsCard(enhancedData.personalized_recommendations);
    }
    
    // Performance benchmarks
    if (enhancedData.performance_benchmarks) {
        container.innerHTML += IntelligenceUI.createPerformanceBenchmarksCard(enhancedData.performance_benchmarks);
    }
    
    // Meta analysis
    if (enhancedData.meta_analysis) {
        container.innerHTML += IntelligenceUI.createMetaAnalysisCard(enhancedData.meta_analysis);
    }
    
    // Animate entrance
    animateIntelligenceCards();
}

function animateIntelligenceCards() {
    const cards = document.querySelectorAll('.intelligence-card');
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

// Enhanced CSS styles
const intelligenceStyles = `
.intelligence-card {
    background: linear-gradient(135deg, rgba(0, 245, 212, 0.05), rgba(59, 130, 246, 0.05));
    border: 1px solid rgba(0, 245, 212, 0.2);
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 15px;
    position: relative;
    overflow: hidden;
}

.intelligence-card::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--tactical-cyan), var(--neural-blue));
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
}

.card-header h3 {
    font-family: var(--font-mono);
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: #cbd5e1;
    margin: 0;
}

.rank-badge {
    font-size: 0.5rem;
    padding: 2px 6px;
    border-radius: 3px;
    font-weight: 900;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

.rank-badge.iron { background: #8b4513; color: #fff; }
.rank-badge.bronze { background: #cd7f32; color: #fff; }
.rank-badge.silver { background: #c0c0c0; color: #000; }
.rank-badge.gold { background: #ffd700; color: #000; }
.rank-badge.platinum { background: #e5e4e2; color: #000; }
.rank-badge.diamond { background: #b9f2ff; color: #fff; }
.rank-badge.immortal { background: #ff4655; color: #fff; }
.rank-badge.radiant { background: #ff9a00; color: #000; }

.player-stats, .metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 10px;
}

.stat-item, .metric-item {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 4px;
    padding: 10px;
    text-align: center;
}

.stat-label, .metric-label {
    display: block;
    font-size: 0.5rem;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 5px;
}

.stat-value, .metric-value {
    font-size: 0.8rem;
    font-weight: 700;
    color: var(--tactical-cyan);
    font-family: var(--font-mono);
}

.recommendation-item {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 4px;
    padding: 15px;
    margin-bottom: 10px;
    border-left: 3px solid transparent;
}

.recommendation-item.high-priority {
    border-left-color: var(--riot-red);
}

.recommendation-item.medium-priority {
    border-left-color: #f59e0b;
}

.recommendation-item.low-priority {
    border-left-color: #10b981;
}

.rec-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}

.rec-type {
    font-size: 0.6rem;
    font-family: var(--font-mono);
    color: #94a3b8;
    text-transform: uppercase;
}

.rec-priority {
    font-size: 0.5rem;
    font-weight: 700;
    padding: 2px 6px;
    border-radius: 3px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.rec-priority.high { background: var(--riot-red); color: #fff; }
.rec-priority.medium { background: #f59e0b; color: #000; }
.rec-priority.low { background: #10b981; color: #fff; }

.rec-content h4 {
    font-size: 0.7rem;
    font-weight: 700;
    color: #cbd5e1;
    margin: 0 0 8px 0;
}

.rec-content p {
    font-size: 0.6rem;
    color: #94a3b8;
    margin: 0 0 10px 0;
}

.action-tag {
    font-size: 0.5rem;
    background: rgba(0, 245, 212, 0.1);
    color: var(--tactical-cyan);
    padding: 2px 6px;
    border-radius: 3px;
    margin-right: 5px;
    margin-bottom: 5px;
    display: inline-block;
}

.benchmark-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
    margin-top: 10px;
}

.benchmark-item {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 4px;
    padding: 8px;
    text-align: center;
}

.benchmark-label {
    display: block;
    font-size: 0.5rem;
    color: #94a3b8;
    text-transform: uppercase;
    margin-bottom: 3px;
}

.benchmark-value {
    font-size: 0.7rem;
    font-weight: 700;
    color: var(--neural-blue);
    font-family: var(--font-mono);
}

.improvement-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px;
    background: rgba(255, 70, 85, 0.1);
    border-radius: 4px;
    margin-bottom: 5px;
}

.improvement-icon {
    font-size: 0.8rem;
}

.improvement-text {
    font-size: 0.6rem;
    color: #cbd5e1;
}

.meta-relevance {
    margin-bottom: 15px;
}

.relevance-score {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 10px;
}

.score-bar {
    flex: 1;
    height: 6px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 3px;
    overflow: hidden;
}

.score-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--tactical-cyan), var(--neural-blue));
    transition: width 0.6s ease;
}

.score-value {
    font-size: 0.7rem;
    font-weight: 700;
    color: var(--tactical-cyan);
    font-family: var(--font-mono);
}

.meta-analysis-text {
    font-size: 0.6rem;
    color: #94a3b8;
    margin: 0;
}

.agents-list {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-top: 10px;
}

.agent-item {
    display: flex;
    align-items: center;
    gap: 5px;
    background: rgba(59, 130, 246, 0.1);
    border: 1px solid rgba(59, 130, 246, 0.2);
    border-radius: 4px;
    padding: 5px 8px;
}

.agent-name {
    font-size: 0.6rem;
    color: #cbd5e1;
    font-family: var(--font-mono);
}

.agent-tag {
    font-size: 0.4rem;
    background: var(--neural-blue);
    color: #fff;
    padding: 1px 4px;
    border-radius: 2px;
    font-weight: 700;
}
`;

// Inject intelligence styles
function injectIntelligenceStyles() {
    const styleSheet = document.createElement('style');
    styleSheet.textContent = intelligenceStyles;
    document.head.appendChild(styleSheet);
}

// Initialize intelligence system
document.addEventListener('DOMContentLoaded', () => {
    injectIntelligenceStyles();
    
    // Add intelligence toggle to UI
    const analysisForm = document.getElementById('analysis-form');
    if (analysisForm) {
        const intelligenceSection = document.createElement('div');
        intelligenceSection.className = 'intelligence-section';
        intelligenceSection.innerHTML = `
            <div class="intelligence-toggle">
                <label>
                    <input type="checkbox" id="enable-intelligence" checked>
                    <span>🧠 Enable Player Intelligence</span>
                </label>
                <div id="player-input-section" style="display: block;">
                    <input type="text" id="riot-id" placeholder="Riot ID (optional)">
                    <input type="text" id="username" placeholder="Username (optional)">
                </div>
            </div>
        `;
        
        analysisForm.appendChild(intelligenceSection);
        
        // Handle intelligence toggle
        document.getElementById('enable-intelligence').addEventListener('change', (e) => {
            const playerSection = document.getElementById('player-input-section');
            playerSection.style.display = e.target.checked ? 'block' : 'none';
            intelligenceManager.isEnabled = e.target.checked;
        });
    }
});

// Export for global use
window.intelligenceManager = intelligenceManager;
window.IntelligenceUI = IntelligenceUI;
window.analyzeVodWithIntelligence = analyzeVodWithIntelligence;
