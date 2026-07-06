# ⚽ ArenaFlow 2026: FIFA World Cup Smart Stadium Hub

### *PromptWars Hackathon Challenge 4: Smart Stadiums & Tournament Operations*

ArenaFlow 2026 is a premium, GenAI-enabled stadium operations and spectator coordination platform designed for the FIFA World Cup 2026. Built using Streamlit, this platform helps venue managers handle incident workflows, provides fans with multi-lingual RAG-grounded support, tracks environmental impact, and ensures a highly accessible interface.

---

## 🌟 Key Features

### 1. 🛡️ Staff Operations Hub
*   **Live Crowd Density Heatmap**: Visualizes spectator traffic across gates, seats, and dining zones to monitor for capacity bottlenecks.
*   **GenAI Incident Dispatcher**: Dynamically parses raw text incident reports (e.g. slips, medical concerns, rowdiness), auto-categorizes severity, tags the correct operations unit (Facilities, Medical, Security), and generates actionable dispatch checklists.
*   **Crowd Rerouting Engine**: Provides rules-based operational recommendations when sector densities exceed critical limits.

### 2. ⚽ Fan Portal & RAG Assistant
*   **Multilingual Stadium Companion**: Answers spectator questions about access ramps, dining concessions, diaper-changing facilities, or light rail links.
*   **Retrieval-Augmented Generation (RAG)**: Answers are grounded in the official stadium guidelines (`stadium_guides.json`) for **MetLife Stadium**, **Estadio Azteca**, and **BC Place**, preventing hallucinations.
*   **Supported Languages**: English, Español, Français, Português, Deutsch, and Arabic.
*   **Green Fan Scorecard**: Tracks eco-friendly actions (taking public transport, using refill stations, ordering plant-based meals), calculates carbon offsets (kg CO2 saved), and suggests AI eco-tips.

### 3. ⚙️ Inclusive Design & Accessibility Features
*   **Dynamic Layout Resizing**: Dynamic CSS font adjustment (Standard, Large, Extra Large) for visually impaired spectators.
*   **Text-to-Speech (TTS)**: HTML5-based client-side voice feedback that reads announcements and chatbot answers aloud with zero latency.
*   **High-Contrast Slate Theme**: Provides optimal legibility under bright stadium sunlight or outdoor screens.

---

## 🔒 Security Safeguards
*   **XSS Tag Sanitizer**: Strips out HTML script injection tags from text inputs before processing.
*   **Prompt Injection Interceptor**: Detects typical LLM jailbreak attempts (e.g., *"ignore previous instructions"* or *"act as"*) and intercepts them before making API calls.
*   **Mock Fallback Engine**: If no Gemini API key is supplied or network connections fail, the application seamlessly switches to local rule-based heuristics so the system never crashes during evaluation.

---

## 📂 Project Structure
```text
promptwars-stadium-ops/
├── .github/
│   └── workflows/
│       └── python-tests.yml        # CI/CD test automation
├── app/
│   ├── __init__.py
│   ├── main.py                     # Streamlit dashboard entrypoint
│   ├── core/
│   │   ├── config.py               # Credentials and config settings
│   │   ├── security.py             # Input sanitizers & prompt-injection guards
│   │   └── llm.py                  # Gemini API and offline fallback logic
│   ├── services/
│   │   ├── assistant.py            # RAG-based search engine
│   │   ├── crowd_management.py     # Simulation metrics & incident classifier
│   │   └── sustainability.py       # CO2 calculators and eco-tips
│   ├── utils/
│   │   └── accessibility.py        # CSS styling injections & browser audio TTS
│   └── data/
│       └── stadium_guides.json     # Grounding data for WC 2026 stadiums
├── tests/
│   ├── test_security.py            # Sanitizer and security guards unit tests
│   ├── test_services.py            # Core analytics & calculations unit tests
│   └── test_assistant.py           # RAG retrieval unit tests
├── requirements.txt                # Package dependencies
├── pyproject.toml                  # Test runner & coverage configs
└── README.md                       # Documentation
```

---

## 🚀 Setup & Execution

### 1. Clone & Set Workspace
Set `promptwars-stadium-ops` as your active workspace directory:
```bash
cd promptwars-stadium-ops
```

### 2. Install Dependencies
Make sure you have Python 3.10+ installed:
```bash
pip install -r requirements.txt
```

### 3. Set Google Gemini API Key (Optional)
Set the API key in your terminal environment, or input it directly in the app's sidebar settings:
```bash
# Windows (PowerShell)
$env:GEMINI_API_KEY="your-api-key-here"

# Linux/macOS
export GEMINI_API_KEY="your-api-key-here"
```

### 4. Run Streamlit
Launch the local development web server:
```bash
streamlit run app/main.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🧪 Testing & Code Coverage
We emphasize clean, maintainable code with high test coverage:
To run the full suite and view terminal coverage:
```bash
python -m pytest --cov=app --cov-report=term-missing tests/
```
Targeting 90%+ code coverage.
