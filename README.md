# AURORA // Multimodal Tactical Intelligence HUD

AURORA is a state-of-the-art **Decision Intelligence** platform for Valorant, bridging high-fidelity data visualization with live multimodal reasoning. It transforms raw gameplay video into specialized tactical critiques using **Gemini 1.5 Pro**.

## 🚀 Core Architecture: The "Zero-Simulation" Bridge
AURORA has transitioned from a static data visualizer to a live neural ecosystem:
- **[FRONTEND] Cyber-HUD**: A professional eSports analytics interface (HTML5/CSS3/JS) with real-time asynchronous "Neural Handshakes."
- **[BACKEND] FastAPI Neural Engine**: A Python-based orchestrator that manages video frame extraction and LLM communications.
- **[VISION] Gemini 1.5 Pro**: A multimodal large language model that performs visual reasoning on gameplay VODs to extract high-level strategic insights.

## 💎 Key Features
- **Multimodal VOD Review**: Upload local files or paste YouTube links to receive a deep-match critique.
- **High-Fidelity Neural Graphics**: On-the-fly generation of smooth **KDE Heatmaps** and **Dense Pathing Webs** for professional match visualization.
- **Predictive Tactical Intelligence**: Real-time extraction of **Rotation Latency** and **Win Rate Prediction** based on detected gameplay patterns.
- **Neural Spatial Synchronization**: AI-driven map detection that automatically swaps tactical assets for Ascent, Bind, and Haven.
- **Unified HUD Sync**: Global performance benchmarks (Latency, Stability) hard-wired to the live VOD analysis stream.
- **Universal Ingestion**: Support for drag-and-drop file uploads, local system paths, and cloud video streams.

## 🛠️ Technical Setup
### Prerequisites
- Python 3.10+
- Google Generative AI API Key (`GEMINI_API_KEY`)
- Riot Games Developer Credentials (`RIOT_CLIENT_ID`, `RIOT_CLIENT_SECRET`)

### Installation
```bash
pip install fastapi uvicorn google-generativeai opencv-python pydantic matplotlib pandas seaborn httpx
```

### Deployment
1. **Initialize the Backend**:
   ```bash
   python aurora_backend.py
   ```
2. **Launch the HUD**:
   Open `index.html` in any modern browser.

## 🛰️ How to Use
1. **Neural Authorization**: Sign in with your Riot ID to establish the identity handshake.
2. **Tactical Ingestion**: Upload a VOD or paste a URL into the **Tactical Vision Terminal**.
3. **Neural Sync**: Watch the terminal status for `[BRAIN] Handing off context...`.
4. **Analysis View**: Review the dynamic findings and watch the **COORDINATE_GRID_MAPPING** sync with the AI's detected map context.

## 📂 Project Structure
- `aurora_backend.py`: FastAPI server orchestrating the intelligence pipeline.
- `gemini_vision_client.py`: Real SDK integration for multimodal reasoning.
- `video_analyzer.py`: Precision frame extraction and source meta processing.
- `index.html`: The central analytical Cyber-HUD.
- `tactical_knowledge_base.json`: The repository of learned pro tactics.

---
*AURORA // PROJECT_HANDOFF_v2.0 // NO_SIMULATION_DETECTED*
