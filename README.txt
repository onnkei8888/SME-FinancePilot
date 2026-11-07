# SME FinancePilot — Local Agentic AI MVP

## What this is
A competition demo prototype for Malaysian micro/small café and restaurant operators.
It uses:
- Streamlit for the dashboard
- Ollama + a local Qwen3 model for goal interpretation, planning, dynamic tool selection and decision synthesis
- Python functions for deterministic financial calculations
- A Three.js 3D HQ with five specialist agent buildings

## Important deployment note
**Ollama runs on the computer that hosts it.** If you run this app on your laptop, it calls `http://localhost:11434`.
A Streamlit Community Cloud app runs on a remote server and cannot automatically access Ollama installed on your laptop. For the competition demo, run the app locally on the same Windows computer as Ollama. Keep the GitHub deployment as a visual backup only unless you separately host a secured model endpoint.

## Windows setup (beginner)
1. Install Ollama from https://ollama.com/download/windows
2. Open PowerShell and run:
   ```powershell
   ollama pull qwen3:4b
   ```
   The model download is about 2.5 GB. If your computer has limited RAM, use `qwen3:1.7b` and enter that exact model name in the app sidebar.
3. Test the model:
   ```powershell
   ollama run qwen3:4b
   ```
   Ask `你好，请介绍你自己。` then type `/bye` to exit.
4. Extract this ZIP to a normal folder, e.g. Desktop\SME-FinancePilot-Agentic-Local
5. Open PowerShell in that folder and run:
   ```powershell
   py -m venv .venv
   .venv\Scripts\activate
   py -m pip install --upgrade pip
   pip install -r requirements.txt
   streamlit run app.py
   ```
6. Open the local URL Streamlit shows, normally http://localhost:8501
7. Keep Ollama running in the background while using FinancePilot.

## How the agentic workflow works
1. Finance Core sends the business goal, sample figures and allowed tool descriptions to the local model.
2. The model returns a JSON plan and selects from a restricted tool registry.
3. The orchestrator validates the selected tool names and runs only those Python tools.
4. Specialist tools return calculated evidence.
5. Decision Agent receives the tool outputs and generates a recommendation.
6. The owner approves or rejects a simulated recommendation. No real external action is executed.

## Five agents
- Finance Agent -> finance_calculator
- Cash Flow Agent -> cash_flow_calculator
- Risk Agent -> risk_detector
- Strategy Agent -> strategy_simulator
- Decision Agent -> synthesizes findings and asks for owner approval

## Demo prompt
"Please assess whether my cafe is financially healthy, identify the biggest risks, and recommend the best action to improve monthly operating surplus and cash resilience."

Try a second prompt:
"Only check my cash position and estimate how many days of runway I may have."

The AI should choose different tools for the two goals. This is a good way to demonstrate dynamic planning.

## Limitations to state honestly in your pitch
- SAMPLE data only; no bank integrations or real transactions.
- Risk thresholds and strategy scenarios are transparent prototype assumptions, not validated financial models.
- Operating surplus is not net profit.
- The model is a local open-weight model; quality and speed depend on computer hardware.
- The 3D scene loads Three.js from a CDN, so internet access is required to load the 3D view.

## Competition video idea (under 5 minutes)
1. 0:00–0:30 — SME problem and product introduction.
2. 0:30–1:00 — Show the 3D HQ and five agents.
3. 1:00–2:30 — Ask the broad financial-health question; show AI plan, selected tools, tool outputs and decision.
4. 2:30–3:15 — Ask a cash-flow-only question; show that AI selects a different tool set.
5. 3:15–4:00 — Show human approval / rejection; emphasize no real payment is executed.
6. 4:00–4:40 — Explain local privacy, sample-data limitations and impact for small businesses.

Remember to show the required DEMO or SAMPLE watermark in the final screen recording if the competition rules require it.
