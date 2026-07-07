# ⚽ ArenaFlow 2026: FIFA World Cup Smart Stadium Hub

### *PromptWars Hackathon Challenge 4: Smart Stadiums & Tournament Operations*

[![Python Tests](https://github.com/your-username/promptwars-stadium-ops/actions/workflows/python-tests.yml/badge.svg)](https://github.com/your-username/promptwars-stadium-ops/actions)
[![Coverage Status](https://img.shields.io/badge/Coverage-96%25-brightgreen.svg)](https://github.com/your-username/promptwars-stadium-ops)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://github.com/your-username/promptwars-stadium-ops)

ArenaFlow 2026 is a premium, GenAI-enabled stadium operations and spectator coordination platform designed for the FIFA World Cup 2026. Built using Streamlit, this platform helps venue managers handle incident workflows, provides fans with multi-lingual RAG-grounded support, tracks environmental impact, and ensures a highly accessible interface.

---

## 🌟 Key Features

### 1. 🛡️ Staff Operations Hub
*   **Live Crowd Density Heatmap**: Visualizes spectator traffic across gates, seats, and dining zones to monitor for capacity bottlenecks.
*   **GenAI Incident Dispatcher**: Dynamically parses raw text incident reports (e.g. slips, medical concerns, rowdiness), auto-categorizes severity, tags the correct operations unit (Facilities, Medical, Security), and generates actionable dispatch checklists.
*   **Crowd Rerouting Engine**: Provides rules-based operational recommendations when sector densities exceed critical limits.
*   **Active Volunteer Dispatch Board**: Simulates on-duty volunteers. When an incident is logged, the dispatcher automatically schedules the closest available volunteer with matching skills (e.g., Medical Assistant, Security Assistant) in real-time.
*   **Match-Day Transportation Board**: Renders real-time shuttle, rail, and bus route congestion levels and schedule delays.

### 2. ⚽ Fan Portal & RAG Assistant
*   **Multilingual Stadium Companion**: Answers spectator questions about access gates, accessible elevators, dining concessions, or diaper-changing facilities.
*   **Retrieval-Augmented Generation (RAG)**: Answers are grounded in the official stadium guidelines (`stadium_guides.json`) for **MetLife Stadium**, **Estadio Azteca**, and **BC Place**, preventing hallucinations.
*   **Supported Languages**: English, Español, Français, Português, Deutsch, and Arabic.
*   **Green Fan Scorecard**: Tracks eco-friendly actions (taking public transport, using refill stations, ordering plant-based meals), calculates carbon offsets (kg CO2 saved), and suggests AI eco-tips.

### 3. ⚙️ Inclusive Design & Accessibility Features
*   **Dynamic Layout Resizing**: Dynamic CSS font adjustment (Standard, Large, Extra Large) for visually impaired spectators.
*   **Color-Blindness Filters**: SVG color spectral shifting filters for Protanopia (red-blindness) and Deuteranopia (green-blindness).
*   **Vestibular Reduced Motion**: Disables transitions, animation durations, and scroll delays.
*   **Text-to-Speech (TTS)**: HTML5-based client-side voice feedback that reads announcements and chatbot answers aloud with zero latency.
*   **High-Contrast Slate Theme**: Provides optimal legibility under bright stadium sunlight or outdoor screens.

---

## 🔒 Security Safeguards
*   **XSS HTMLParser Sanitizer**: Strips out HTML scripting tags using the Python standard library `html.parser.HTMLParser` to prevent script injections without regex flaws.
*   **Log Injection Defense (CWE-117)**: Sanitizes all logged text inside security violation logs by stripping line breaks (`\n`, `\r`) and capping sizes to prevent log forging.
*   **Path Traversal Prevention (CWE-22)**: Verifies that custom specifications paths resolve strictly within the package directory boundary.
*   **Prompt Injection Interceptor**: Detects typical LLM jailbreak attempts (e.g., *"ignore previous instructions"*) and intercepts them.
*   **Session-based Rate Limiter**: Streamlit session state rolling-window filter that prevents request spamming.
*   **Length Guards**: Limits user input fields to 300 characters to prevent remote prompt overflows.
*   **Security Audit Logger**: Writes safety violations with timestamp parameters directly to `security_audit.log` (viewable in the Pitch tab).
*   **Mock Fallback Engine**: If no Gemini API key is supplied or network connections fail, the application seamlessly switches to local rule-based heuristics so the system never crashes during evaluation.

---

## 📂 Project Structure
```text
promptwars-stadium-ops/
├── .github/
│   └── workflows/
│       └── python-tests.yml        # CI/CD test automation
├── stadium_ops/
│   ├── __init__.py
│   ├── main.py                     # Streamlit dashboard entrypoint
│   ├── core/
│   │   ├── config.py               # Credentials and config settings
│   │   ├── exceptions.py           # Custom exception definitions
│   │   ├── security.py             # Input sanitizers & prompt-injection guards
│   │   ├── llm_interface.py        # Abstract Base Class for LLM Service
│   │   └── llm.py                  # Gemini API and offline fallback logic
│   ├── services/
│   │   ├── assistant.py            # RAG-based search engine
│   │   ├── crowd_management.py     # Simulation metrics & incident classifier
│   │   ├── sustainability.py       # CO2 calculators and eco-tips
│   │   ├── stadium_repository.py   # Repository for guides data loading
│   │   └── transport_service.py    # Transportation tracking service
│   ├── utils/
│   │   └── accessibility.py        # CSS styling injections & browser audio TTS
│   └── data/
│       └── stadium_guides.json     # Grounding data for WC 2026 stadiums
├── tests/
│   ├── test_security.py            # Sanitizer and security guards unit tests
│   ├── test_services.py            # Core analytics & calculations unit tests
│   ├── test_assistant.py           # RAG retrieval unit tests
│   ├── test_llm.py                 # Direct configurations & LLM mock unit tests
│   └── test_transport.py           # Transit monitoring unit tests
├── requirements.txt                # Package dependencies
├── pyproject.toml                  # Test runner & coverage configs
└── README.md                       # Documentation
```

---

## 🚀 Setup & Execution

### 1. Clone & Set Workspace
Set `promptwars-stadium-ops` as your active directory:
```bash
git clone https://github.com/your-username/promptwars-stadium-ops.git
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
streamlit run stadium_ops/main.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🧪 Testing & Code Coverage
We emphasize clean, maintainable code with high test coverage:
To run the full suite (39 test cases) and view terminal coverage:
```bash
python -m pytest --cov=stadium_ops --cov-report=term-missing tests/
```

### Coverage Report
```text
Name                                         Stmts   Miss  Cover   Missing
--------------------------------------------------------------------------
stadium_ops\__init__.py                          0      0   100%
stadium_ops\core\__init__.py                     0      0   100%
stadium_ops\core\config.py                      18      2    89%   35-36
stadium_ops\core\exceptions.py                   8      0   100%
stadium_ops\core\llm.py                         97     11    89%   56, 75-76, 90-101
stadium_ops\core\llm_interface.py                6      1    83%   32
stadium_ops\core\security.py                    65      0   100%
stadium_ops\data\__init__.py                     0      0   100%
stadium_ops\services\__init__.py                 0      0   100%
stadium_ops\services\assistant.py               26      0   100%
stadium_ops\services\crowd_management.py        84      0   100%
stadium_ops\services\stadium_repository.py      29      0   100%
stadium_ops\services\sustainability.py          40      0   100%
stadium_ops\services\transport_service.py       22      0   100%
stadium_ops\utils\__init__.py                    0      0   100%
--------------------------------------------------------------------------
TOTAL                                          395     16    96%
```
**96% Code Coverage Achieved (100% on all core services and security modules).**
