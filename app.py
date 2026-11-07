import json
import math
import urllib.request
import urllib.error
from datetime import datetime
from typing import Any

import streamlit as st
import streamlit.components.v1 as components

# ============================================================
# SME FinancePilot — Local Agentic AI MVP
# AI planner: Ollama (local Qwen3)
# Deterministic tools: Python financial calculations
# ============================================================

st.set_page_config(
    page_title="SME FinancePilot | Agentic Finance HQ",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

OLLAMA_URL = "http://localhost:11434/api/chat"
DEFAULT_MODEL = "qwen3:4b"
MAX_TOOLS_PER_RUN = 4

# ---------------------------- Styling ----------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    .stApp { background: radial-gradient(circle at 10% 0%, #15253b 0, #08111f 42%, #060b14 100%); color: #eef4ff; }
    [data-testid="stSidebar"] { background: #0b1728; border-right: 1px solid #243650; }
    h1,h2,h3 { font-family: 'Space Grotesk', sans-serif !important; color: #f3f7ff !important; }
    .hero { padding: 22px 26px; border: 1px solid #29415e; border-radius: 18px; background: linear-gradient(115deg, rgba(24,51,79,.95), rgba(12,26,44,.94)); margin-bottom: 18px; }
    .eyebrow { color: #73d9c4; font-size: 12px; font-weight: 700; letter-spacing: 2px; }
    .muted { color: #9eb1c9; font-size: 13px; }
    .agent-card { background: rgba(17,33,53,.92); border: 1px solid #2a405a; padding: 14px 16px; border-radius: 14px; min-height: 105px; }
    .agent-name { color: #dceaff; font-weight: 700; font-size: 14px; }
    .agent-desc { color: #9eb1c9; font-size: 12px; margin-top: 5px; }
    .pill { display:inline-block; border:1px solid #35516e; color:#8fe4d2; border-radius:20px; padding:3px 9px; font-size:11px; margin:3px 4px 3px 0; }
    .result { background: rgba(15,31,49,.92); border:1px solid #2b4561; border-radius:14px; padding:16px 18px; margin:8px 0; }
    .warning { color:#ffd28b; }
    div[data-testid="stMetric"] { background:#102239; border:1px solid #2b4561; border-radius:12px; padding:12px; }
    .stButton>button { border-radius: 10px; font-weight: 700; }
    .small-note { color:#8da2bc; font-size:11px; }
</style>
""", unsafe_allow_html=True)

# ---------------------------- Finance tools ----------------------------
def finance_calculator(data: dict) -> dict:
    revenue = max(0.0, float(data["monthly_revenue"]))
    cogs = max(0.0, float(data["monthly_cogs"]))
    opex = max(0.0, float(data["monthly_opex"]))
    gross_profit = revenue - cogs
    operating_surplus = gross_profit - opex
    gross_margin = (gross_profit / revenue * 100) if revenue else 0
    operating_margin = (operating_surplus / revenue * 100) if revenue else 0
    return {
        "monthly_revenue_rm": round(revenue, 2),
        "cost_of_goods_sold_rm": round(cogs, 2),
        "operating_expenses_rm": round(opex, 2),
        "gross_profit_rm": round(gross_profit, 2),
        "operating_surplus_before_financing_tax_rm": round(operating_surplus, 2),
        "gross_margin_percent": round(gross_margin, 2),
        "operating_margin_percent": round(operating_margin, 2),
        "interpretation": (
            "Operating surplus is positive before financing costs and tax."
            if operating_surplus >= 0 else
            "The business is operating at a monthly deficit before financing costs and tax."
        ),
        "caution": "This is a simplified management estimate, not audited net profit."
    }


def cash_flow_calculator(data: dict) -> dict:
    opening = max(0.0, float(data["opening_cash"]))
    received = max(0.0, float(data["cash_received"]))
    paid = max(0.0, float(data["cash_paid"]))
    net = received - paid
    closing = opening + net
    daily_burn = max(0.0, paid - received) / 30
    runway = (closing / daily_burn) if daily_burn > 0 else None
    # Simple 3-month stress forecast: same net movement each month.
    forecast = []
    balance = opening
    for month in range(1, 4):
        balance += net
        forecast.append({"month": month, "projected_cash_rm": round(balance, 2)})
    return {
        "opening_cash_rm": round(opening, 2),
        "cash_received_rm": round(received, 2),
        "cash_paid_rm": round(paid, 2),
        "net_cash_movement_rm": round(net, 2),
        "estimated_closing_cash_rm": round(closing, 2),
        "estimated_runway_days": round(runway * 30, 1) if runway is not None else "No cash burn under current inputs",
        "three_month_projection": forecast,
        "warning": "Projection assumes the same monthly cash movement repeats; it is not a guarantee."
    }


def risk_detector(data: dict) -> dict:
    finance = finance_calculator(data)
    cash = cash_flow_calculator(data)
    risks = []
    score = 0
    if finance["operating_surplus_before_financing_tax_rm"] < 0:
        risks.append({"risk": "Operating deficit", "severity": "High", "reason": "Monthly operating costs exceed gross profit."})
        score += 35
    if cash["estimated_closing_cash_rm"] < 0:
        risks.append({"risk": "Negative estimated closing cash", "severity": "Critical", "reason": "Expected cash outflow exceeds available cash."})
        score += 40
    elif cash["estimated_closing_cash_rm"] < data["monthly_opex"]:
        risks.append({"risk": "Low cash buffer", "severity": "High", "reason": "Estimated closing cash is below one month of operating expenses."})
        score += 25
    if data["monthly_revenue"] > 0 and data["monthly_cogs"] / data["monthly_revenue"] > 0.55:
        risks.append({"risk": "High direct-cost ratio", "severity": "Medium", "reason": "COGS is above 55% of monthly revenue."})
        score += 15
    if data["monthly_revenue"] > 0 and data["monthly_opex"] / data["monthly_revenue"] > 0.40:
        risks.append({"risk": "High operating-expense ratio", "severity": "Medium", "reason": "Operating expenses are above 40% of monthly revenue."})
        score += 15
    if not risks:
        risks.append({"risk": "No major rule-based warning detected", "severity": "Low", "reason": "Current sample inputs do not trigger the prototype's risk thresholds."})
    return {
        "risk_score_out_of_100": min(score, 100),
        "risk_level": "Critical" if score >= 70 else "High" if score >= 40 else "Moderate" if score >= 20 else "Low",
        "identified_risks": risks,
        "method_note": "Transparent prototype thresholds; not a credit score or professional risk rating."
    }


def strategy_simulator(data: dict) -> dict:
    revenue = float(data["monthly_revenue"])
    cogs = float(data["monthly_cogs"])
    opex = float(data["monthly_opex"])
    # Three illustrative, editable-by-code scenarios.
    scenarios = [
        {"name": "Cost-control", "revenue_change_pct": 0, "cogs_change_pct": -5, "opex_change_pct": -8,
         "explanation": "Reduce ingredient wastage and review recurring operating expenses."},
        {"name": "Sales-growth", "revenue_change_pct": 8, "cogs_change_pct": 3, "opex_change_pct": 2,
         "explanation": "Test a small promotion or higher-margin menu bundle; costs also rise slightly."},
        {"name": "Balanced", "revenue_change_pct": 4, "cogs_change_pct": -2, "opex_change_pct": -3,
         "explanation": "Combine a modest sales push with purchasing and expense controls."},
    ]
    output = []
    for s in scenarios:
        r = revenue * (1 + s["revenue_change_pct"] / 100)
        c = cogs * (1 + s["cogs_change_pct"] / 100)
        o = opex * (1 + s["opex_change_pct"] / 100)
        surplus = r - c - o
        output.append({
            "scenario": s["name"],
            "revenue_rm": round(r, 2),
            "cogs_rm": round(c, 2),
            "opex_rm": round(o, 2),
            "estimated_operating_surplus_rm": round(surplus, 2),
            "change_vs_current_rm": round(surplus - (revenue - cogs - opex), 2),
            "assumption": s["explanation"]
        })
    best = max(output, key=lambda x: x["estimated_operating_surplus_rm"])
    return {
        "scenarios": output,
        "best_by_estimated_operating_surplus": best["scenario"],
        "important_note": "Illustrative what-if scenarios only. Results are not forecasts or guaranteed outcomes."
    }


TOOL_REGISTRY = {
    "finance_calculator": {
        "agent": "Finance Agent",
        "description": "Calculate gross profit, operating surplus and margins from monthly revenue, COGS and OPEX.",
        "function": finance_calculator,
    },
    "cash_flow_calculator": {
        "agent": "Cash Flow Agent",
        "description": "Calculate net cash movement, estimated closing cash, runway and a simple 3-month projection.",
        "function": cash_flow_calculator,
    },
    "risk_detector": {
        "agent": "Risk Agent",
        "description": "Detect operating deficit, low cash buffer and cost-ratio risks using transparent thresholds.",
        "function": risk_detector,
    },
    "strategy_simulator": {
        "agent": "Strategy Agent",
        "description": "Compare cost-control, sales-growth and balanced business scenarios.",
        "function": strategy_simulator,
    },
}

# ---------------------------- Ollama functions ----------------------------
def ollama_chat(messages: list[dict], model: str, json_mode: bool = False) -> str:
    payload: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {"temperature": 0.2, "num_ctx": 8192},
    }
    if json_mode:
        payload["format"] = "json"
    request = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result.get("message", {}).get("content", "")
    except urllib.error.URLError as exc:
        raise RuntimeError(
            "无法连接本机 Ollama。请确认 Ollama 已安装并在后台运行，"
            "再在 PowerShell 执行 `ollama list` 检查模型。"
        ) from exc


def extract_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = text.replace("```json", "").replace("```", "").strip()
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("模型没有返回有效 JSON")
    return json.loads(text[start:end + 1])


def make_plan(goal: str, data: dict, model: str) -> dict:
    tool_lines = "\n".join(
        f'- {name}: {spec["description"]}'
        for name, spec in TOOL_REGISTRY.items()
    )
    system = f"""
You are Finance Core, an agentic planner for a Malaysian small cafe/restaurant SME.
Your job is to understand the user's goal, create a short plan, and select only the tools needed.
Available tools:
{tool_lines}

Rules:
- Select 1 to 4 tools from the exact tool names above.
- Use finance_calculator for profit/margin questions.
- Use cash_flow_calculator for liquidity/cash runway questions.
- Use risk_detector for risk/survival questions.
- Use strategy_simulator for "what should I do", scenario or improvement questions.
- For broad business-health questions, choose all relevant tools.
- Never invent financial figures. Tools will calculate the figures.
- This is a sample decision-support prototype, not professional financial advice.
Return ONLY valid JSON with this exact structure:
{{
  "goal_interpretation": "one sentence",
  "plan": ["step 1", "step 2"],
  "selected_tools": ["tool_name"],
  "reason_for_selection": "short reason"
}}
"""
    user = f"Business data (RM): {json.dumps(data, ensure_ascii=False)}\nUser goal: {goal}"
    raw = ollama_chat(
        [{"role": "system", "content": system}, {"role": "user", "content": user}],
        model,
        json_mode=True,
    )
    plan = extract_json(raw)
    selected = plan.get("selected_tools", [])
    selected = [x for x in selected if x in TOOL_REGISTRY][:MAX_TOOLS_PER_RUN]
    if not selected:
        raise ValueError("AI 没有选择有效工具。请重试或更换模型。")
    plan["selected_tools"] = selected
    return plan


def run_agentic_workflow(goal: str, data: dict, model: str) -> dict:
    # 1) AI interprets the goal and dynamically selects tools.
    plan = make_plan(goal, data, model)

    # 2) Orchestrator validates the plan and executes selected Python tools.
    tool_results = {}
    activity = []
    for tool_name in plan["selected_tools"]:
        spec = TOOL_REGISTRY[tool_name]
        activity.append(f'{spec["agent"]}：执行 `{tool_name}`')
        tool_results[tool_name] = spec["function"](data)

    # 3) AI observes tool outputs and synthesizes a recommendation.
    synthesis_system = """
You are Decision Agent in SME FinancePilot.
Use ONLY the supplied tool outputs and business data. Do not invent numbers.
Explain the most important findings, recommend practical next steps, and mention assumptions.
Distinguish operating surplus from cash flow. Operating surplus is not net profit.
Never claim that a real payment, bank transaction or external action has been made.
Return concise, clear language suitable for a Malaysian small business owner.
"""
    synthesis_user = (
        f"User goal: {goal}\n"
        f"Business data: {json.dumps(data, ensure_ascii=False)}\n"
        f"AI plan: {json.dumps(plan, ensure_ascii=False)}\n"
        f"Tool outputs: {json.dumps(tool_results, ensure_ascii=False)}\n"
        "Write: (1) key findings, (2) recommended action, (3) what owner should verify."
    )
    final_text = ollama_chat(
        [{"role": "system", "content": synthesis_system},
         {"role": "user", "content": synthesis_user}],
        model,
        json_mode=False,
    )
    return {
        "plan": plan,
        "activity": activity,
        "tool_results": tool_results,
        "decision": final_text,
        "timestamp": datetime.now().strftime("%d %b %Y, %I:%M:%S %p"),
    }


# ---------------------------- Sidebar ----------------------------
st.sidebar.markdown("## 🏦 FinancePilot")
st.sidebar.caption("Local Agentic AI • SAMPLE DEMO")
model = st.sidebar.text_input("Ollama model", value=DEFAULT_MODEL, help="必须与 `ollama list` 显示的名称一致。")
st.sidebar.markdown("---")
st.sidebar.markdown("### Sample SME financial data (RM)")
monthly_revenue = st.sidebar.number_input("Monthly revenue", min_value=0.0, value=30000.0, step=500.0)
monthly_cogs = st.sidebar.number_input("Monthly COGS / ingredients", min_value=0.0, value=12000.0, step=500.0)
monthly_opex = st.sidebar.number_input("Monthly operating expenses", min_value=0.0, value=14000.0, step=500.0)
opening_cash = st.sidebar.number_input("Opening cash balance", min_value=0.0, value=10000.0, step=500.0)
cash_received = st.sidebar.number_input("Cash received this month", min_value=0.0, value=28000.0, step=500.0)
cash_paid = st.sidebar.number_input("Cash paid this month", min_value=0.0, value=26000.0, step=500.0)

business_data = {
    "monthly_revenue": monthly_revenue,
    "monthly_cogs": monthly_cogs,
    "monthly_opex": monthly_opex,
    "opening_cash": opening_cash,
    "cash_received": cash_received,
    "cash_paid": cash_paid,
}

st.sidebar.markdown("---")
st.sidebar.markdown("**Privacy mode:** All model inference runs on this computer through Ollama.")
st.sidebar.caption("Do not enter real customer identities, bank credentials or confidential account numbers.")

# ---------------------------- Main UI ----------------------------
st.markdown("""
<div class="hero">
  <div class="eyebrow">AUTONOMOUS SME FINANCIAL INTELLIGENCE</div>
  <h1 style="margin:6px 0 2px 0;">SME FinancePilot</h1>
  <div style="color:#b8c9dc;font-size:15px;">Your local AI finance team — plan, analyse, simulate and recommend.</div>
  <div style="margin-top:10px;">
    <span class="pill">LOCAL AI</span><span class="pill">5 AGENTS</span><span class="pill">HUMAN APPROVAL</span><span class="pill">SAMPLE DATA</span>
  </div>
</div>
""", unsafe_allow_html=True)

# Connection status
col_status1, col_status2, col_status3 = st.columns([1, 1, 2])
with col_status1:
    st.metric("AI model", model)
with col_status2:
    st.metric("Agent team", "5")
with col_status3:
    st.caption("Ollama endpoint: http://localhost:11434 • Local-only inference")

st.markdown("### 🏙️ Agentic Finance HQ")
scene_path = "components/hq_scene.html"
try:
    with open(scene_path, "r", encoding="utf-8") as f:
        scene_html = f.read()
    components.html(scene_html, height=470, scrolling=False)
except FileNotFoundError:
    st.error("Missing components/hq_scene.html. Keep the components folder beside app.py.")

st.markdown("### 👥 Your five-agent team")
agent_cols = st.columns(5)
agents = [
    ("🏦", "Finance Agent", "Profit, cost & margin"),
    ("🌊", "Cash Flow Agent", "Liquidity & runway"),
    ("🔭", "Risk Agent", "Early warning signals"),
    ("🧪", "Strategy Agent", "What-if simulations"),
    ("🎯", "Decision Agent", "Recommendation & approval"),
]
for col, (emoji, name, desc) in zip(agent_cols, agents):
    with col:
        st.markdown(
            f'<div class="agent-card"><div style="font-size:24px">{emoji}</div>'
            f'<div class="agent-name">{name}</div><div class="agent-desc">{desc}</div></div>',
            unsafe_allow_html=True
        )

st.markdown("---")
st.markdown("### 🤖 Ask Finance Core")
st.write("告诉 Finance Core 你想解决什么问题。AI 会先规划，再选择需要的财务工具，而不是每次固定执行全部计算。")
goal = st.text_area(
    "Business goal / question",
    value="Please assess whether my cafe is financially healthy, identify the biggest risks, and recommend the best action to improve monthly operating surplus and cash resilience.",
    height=105,
)
run_col, info_col = st.columns([1, 2])
with run_col:
    run_clicked = st.button("🚀 Run Finance Core", type="primary", use_container_width=True)
with info_col:
    st.caption("The AI planner chooses tools dynamically. Python performs the calculations. Decision Agent explains the results.")

if run_clicked:
    if not goal.strip():
        st.warning("Please enter a business goal first.")
    else:
        with st.spinner("Finance Core is planning and coordinating the agents... This may take a minute on a CPU."):
            try:
                result = run_agentic_workflow(goal.strip(), business_data, model.strip())
                st.session_state["last_result"] = result
                st.session_state["approval_status"] = "Pending owner review"
            except Exception as e:
                st.error(f"Agent workflow could not complete: {e}")
                st.info("Check that Ollama is running and the selected model has been downloaded.")
                st.code("ollama list\nollama run qwen3:4b")

if "last_result" in st.session_state:
    result = st.session_state["last_result"]
    st.markdown("---")
    st.markdown("## 🧠 Finance Core execution report")
    st.caption(f"Completed: {result['timestamp']}")
    st.markdown("### 1. Goal interpretation")
    st.info(result["plan"].get("goal_interpretation", ""))
    st.markdown("### 2. AI-generated execution plan")
    for i, step in enumerate(result["plan"].get("plan", []), 1):
        st.write(f"**{i}.** {step}")
    st.markdown("**Tools dynamically selected by AI:**")
    selected_cols = st.columns(len(result["plan"]["selected_tools"]))
    for col, tool_name in zip(selected_cols, result["plan"]["selected_tools"]):
        with col:
            st.markdown(f'<div class="agent-card"><div class="agent-name">{TOOL_REGISTRY[tool_name]["agent"]}</div><div class="agent-desc">{tool_name}</div></div>', unsafe_allow_html=True)
    st.markdown("### 3. Agent execution log")
    for item in result["activity"]:
        st.success(item)
    st.markdown("### 4. Financial tool outputs")
    for tool_name, output in result["tool_results"].items():
        with st.expander(f'{TOOL_REGISTRY[tool_name]["agent"]} — {tool_name}', expanded=True):
            st.json(output)
    st.markdown("### 5. Decision Agent recommendation")
    st.markdown(f'<div class="result">{result["decision"].replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)

    st.markdown("### 6. Human-in-the-loop approval")
    st.warning("No real payment, bank transfer or business change will be executed. This approval is a simulated demo action only.")
    if st.session_state.get("approval_status") == "Pending owner review":
        approve_col, reject_col = st.columns(2)
        with approve_col:
            if st.button("✅ Approve recommendation (simulation)", use_container_width=True):
                st.session_state["approval_status"] = "Approved in demo"
                st.session_state["approval_log"] = f"Owner approved the recommendation in the SAMPLE demo at {datetime.now().strftime('%d %b %Y %I:%M %p')}."
                st.rerun()
        with reject_col:
            if st.button("↩️ Request revision", use_container_width=True):
                st.session_state["approval_status"] = "Revision requested"
                st.session_state["approval_log"] = "Owner did not approve; no action was executed."
                st.rerun()
    st.info(f"Status: {st.session_state.get('approval_status', 'Pending owner review')}")
    if st.session_state.get("approval_log"):
        st.caption(st.session_state["approval_log"])

st.markdown("---")
st.markdown("### 📌 Prototype limitations")
st.markdown("""
- This is a **competition MVP / SAMPLE DEMO**, not a regulated financial-advice service.
- Ollama runs locally on the computer hosting this app. A Streamlit Cloud deployment cannot automatically access Ollama on your personal laptop.
- Calculations use the sample values entered in the sidebar. Strategy scenarios are illustrative assumptions, not forecasts.
- No bank connection, payment, loan application or external transaction is performed.
- Operating surplus is not the same as accounting net profit; tax, interest, depreciation and other adjustments are not fully modelled.
""")
st.caption("SME FinancePilot • Agentic AI Challenge 2026 • Built as a local prototype")
