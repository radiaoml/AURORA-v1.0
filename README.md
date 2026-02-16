# AURORA - Decision Intelligence for eSports

## Project Overview
AURORA is an advanced "Decision Intelligence" platform for Valorant, focusing on tactical analysis, predictive modeling, and data-driven performance optimization.

## Historical Log of Actions

### 1. Document Extraction & Analysis
- **Goal**: Convert "Analyse du marché AURORA.pdf" into professional LaTeX.
- **Action**: Installed `pypdf` and created an extraction script `extract_pdf.py`.
- **Command**: `pip install pypdf`
- **Result**: Extracted content to `extracted_text.txt` and generated an 8-page academic LaTeX document `aurora_analysis.tex`.

### 2. Environment Setup for Visualization
- **Goal**: Set up Python dependencies for data visualization and tactical mapping.
- **Action**: Installed core libraries for data processing and imaging.
- **Command**: `pip install matplotlib pandas seaborn opencv-python`
- **Date**: 2026-02-16

### 3. Implementation of Visualization System (In Progress)
- **Status**: Execution phase.
- **Components Pending**:
    - [ ] `generate_mock_data.py`: Multi-round gameplay data simulator.
    - [ ] `visualizer.py`: Heatmap and trajectory rendering engine.
    - [ ] `ascent_blueprint.png`: Tactical map base layer.

### 5. YouTube Intelligence Expansion (v3)
- **Goal**: Extract tactical benchmarks from professional instructional videos.
- **Action**: Developed a harvesting strategy for keywords like `"best tactic in valorant"`.
- **Result**: Integrated a "Tactical Intelligence" card into the dashboard, featuring transcript-extracted takeaways (e.g., Default strategies, Map Control benchmarks).

### 6. Data Acquisition Strategy (Hybrid Architecture)

AURORA uses a hybrid model combining official Riot APIs with a proprietary Computer Vision (CV) engine.

#### A. Official Riot APIs (Metadata & Identity)
The following endpoints from the Riot Developer Portal are required:
- **`ACCOUNT-V1`**: `GET /riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}`
    - *Purpose*: Map player names to PUUIDs for cross-match tracking.
- **`VAL-MATCH-V1` (PC) / `VAL-CONSOLE-MATCH-V1` (Console)**:
    - `GET /val/match/v1/matchlists/by-puuid/{puuid}`: Get a list of recent games.
    - `GET /val/match/v1/matches/{matchId}`: Retrieve the high-level scoreboard, map info, and round results.
- **`VAL-CONTENT-V1`**:
    - *Purpose*: Map internal IDs to human-readable Agent and Map names.

#### B. Computer Vision Engine (Tactical Depth)
Since Riot APIs **do not** provide real-time movement coordinates (X, Y, Z), AURORA extracts these from video sources:
- **Movement Trajectories**: Extracted from minimap or POV analysis.
- **Utility Usage**: Detected using pixel-pattern matching for smokes, flashes, and ultimates.
- **Combat Events**: Synchronized with Match API timestamps for 95% accuracy.

## How to Run
1. Ensure Python 3.10+ is installed.
2. Install dependencies: `pip install matplotlib pandas seaborn opencv-python pypdf`
3. Generate simulation data: `python generate_mock_data.py`
4. Run the tactical dashboard: `python dashboard.py`

## Output Files
- `match_metadata.json`: Simulated Riot API metadata.
- `tactical_kill_heatmap.png`: Tactical kill density analysis.
- `round_1_trajectories.png`: Movement patterns for the first round.
- `index.html`: **Interactive Tactical Dashboard** (Open this in your browser).
- `tactical_knowledge_base.json`: **Structured Mental Model** (Ready for LLM ingestion).
