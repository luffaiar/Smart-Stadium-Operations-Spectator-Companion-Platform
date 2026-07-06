# ⚽ ArenaFlow 2026: FIFA World Cup Smart Stadium Hub
### *PromptWars Hackathon Challenge 4: Smart Stadiums & Tournament Operations*
[![Python Tests](https://img.shields.io/badge/Tests-19%20Passed-brightgreen.svg)]()
[![Coverage Status](https://img.shields.io/badge/Coverage-96%25-brightgreen.svg)]()
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)]()
ArenaFlow 2026 is a premium, GenAI-enabled stadium operations and spectator coordination platform designed for the FIFA World Cup 2026. Built with **Streamlit**, it provides venue managers with AI incident routing, helps fans with multi-lingual RAG-grounded guides, tracks carbon offsets, and ensures high accessibility.
---
## 🌟 Key Features
*   🛡️ **Staff Operations Hub**: Live crowd density heatmaps and a GenAI Incident Dispatcher that auto-categorizes safety reports (e.g. medical, security) and generates ground staff checklists.
*   ⚽ **Fan Portal (RAG Assistant)**: Multi-lingual chatbot grounded in layouts for **MetLife Stadium**, **Estadio Azteca**, and **BC Place** (prevents hallucinations).
*   ♻️ **Green Fan Scorecard**: Logs sustainable fan habits (light rail, cup recycling) to calculate CO2 offsets and issue reward badges.
*   ⚙️ **Inclusive Accessibility**: Dynamic layout scaling, high-contrast themes, and HTML5 Web Speech client-side audio readings.
*   🔒 **Security Safeguards**: Native XSS sanitization and prompt injection blockages to protect the LLM backend.
*   🔌 **Offline Heuristic Fallback**: Runs without API credentials using local rule engines, ensuring the app never crashes during evaluations.
---
## 📂 Project Structure
```text
promptwars-stadium-ops/
├── .github/workflows/python-tests.yml  # CI/CD test runner
├── stadium_ops/
│   ├── main.py                         # Streamlit entrypoint
│   ├── core/                           # configs, security safeguards, LLM managers
│   ├── services/                       # RAG assistant, crowd density, carbon trackers
│   ├── utils/                          # CSS theme injectors & audio widgets
│   └── data/                           # stadium layout json database
├── tests/                              # 19 Unit/Integration test cases (96% Coverage)
├── requirements.txt                    # Pip dependencies
└── pyproject.toml                      # Pytest configurations
🚀 Setup & Local Execution
1. Install Dependencies
bash


pip install -r requirements.txt
2. Set Gemini API Key (Optional)
If you want live GenAI responses instead of offline heuristics, set your key:

bash


# Windows (PowerShell)
$env:GEMINI_API_KEY="your-api-key"
# macOS/Linux
export GEMINI_API_KEY="your-api-key"
3. Run Web App
bash


streamlit run stadium_ops/main.py
Open http://localhost:8501 in your browser.

4. Run Test Suite & Coverage
bash


python -m pytest --cov=stadium_ops --cov-report=term-missing tests/


stadium_ops/core/config.py              100%
stadium_ops/core/security.py            100%
stadium_ops/services/crowd_management.py 100%
stadium_ops/services/sustainability.py  100%
stadium_ops/core/llm.py                  93%
stadium_ops/services/assistant.py        89%
TOTAL                                    96%
