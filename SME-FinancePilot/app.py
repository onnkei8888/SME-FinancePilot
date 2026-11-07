import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="SME FinancePilot | 3D HQ", page_icon="🏙️", layout="wide")

st.markdown("""
<style>
.stApp { background:#081522; color:#edf3fa; }
[data-testid="stHeader"] { background:transparent; }
h1,h2,h3,h4,p,label,span { color:#edf3fa; }
[data-testid="stMetric"] { background:#1b3045; border:1px solid #405b73; padding:15px; border-radius:13px; }
[data-testid="stMetricLabel"],[data-testid="stMetricLabel"] p { color:#b9cde0 !important; }
[data-testid="stMetricValue"],[data-testid="stMetricValue"] div { color:#fff !important; font-weight:800; }
[data-testid="stCaptionContainer"] p { color:#9fb2c8 !important; }
.stButton button { background:#e9b64e; color:#102033; border:0; border-radius:9px; font-weight:800; min-height:42px; }
.stButton button:hover { background:#ffd477; color:#102033; }
[data-testid="stExpander"] { background:#14283b; border:1px solid #38536d; border-radius:12px; }
hr { border-color:#314960; }
</style>
""", unsafe_allow_html=True)

def money(v):
    return f"RM {v:,.2f}"

def finance_calculator(revenue, cogs, opex):
    gross_profit = revenue - cogs
    operating_surplus = gross_profit - opex
    return {
        "gross_profit": gross_profit,
        "gross_margin": gross_profit / revenue * 100 if revenue else 0,
        "operating_surplus": operating_surplus,
        "operating_margin": operating_surplus / revenue * 100 if revenue else 0,
        "cogs_ratio": cogs / revenue * 100 if revenue else 0,
        "opex_ratio": opex / revenue * 100 if revenue else 0,
    }

def cash_flow_calculator(opening_cash, cash_received, cash_paid):
    net = cash_received - cash_paid
    return {"net_cash_flow": net, "closing_cash": opening_cash + net}

def risk_detector(revenue, cogs, opex, closing_cash):
    risks = []
    if revenue <= 0:
        risks.append(("HIGH", "No revenue recorded. Check the reporting period and sales records."))
    if revenue > 0 and cogs / revenue > 0.45:
        risks.append(("MEDIUM", "COGS exceeds 45% of revenue. Review ingredient and supplier costs."))
    if revenue > 0 and opex / revenue > 0.50:
        risks.append(("MEDIUM", "Operating expenses exceed 50% of revenue. Review fixed and variable costs."))
    if closing_cash < 5000:
        risks.append(("HIGH", "Closing cash is below RM5,000. Review near-term payment commitments."))
    if not risks:
        risks.append(("INFO", "No warning was triggered by the illustrative thresholds used in this demo."))
    return risks

def strategy_simulator(revenue, cogs, opex):
    return {
        "Current baseline": revenue - cogs - opex,
        "A · Reduce OPEX by 5%": revenue - cogs - opex * 0.95,
        "B · Sales +8%, COGS scales, extra promo cost 3% of current revenue":
            revenue * 1.08 - cogs * 1.08 - (opex + revenue * 0.03)
    }

st.sidebar.markdown("## 🧠 FINANCE CORE")
st.sidebar.caption("Central SME financial intelligence")
page = st.sidebar.radio("NAVIGATION", [
    "🏙️ 3D Headquarters", "📊 Financial Intelligence", "💧 Cash Flow Analysis",
    "🔭 Risk Observatory", "⚙️ Strategy Lab", "🏛️ Decision Pavilion"
])
st.sidebar.divider()
st.sidebar.markdown("### ☕ SAMPLE SME DATA")
business_name = st.sidebar.text_input("Business name", "Kopi Kita Café (DEMO)")
revenue = st.sidebar.number_input("Monthly revenue (RM)", min_value=0.0, value=50000.0, step=1000.0)
cogs = st.sidebar.number_input("Cost of goods sold (RM)", min_value=0.0, value=18000.0, step=500.0)
opex = st.sidebar.number_input("Operating expenses (RM)", min_value=0.0, value=22000.0, step=500.0)
opening_cash = st.sidebar.number_input("Opening cash (RM)", min_value=0.0, value=15000.0, step=500.0)
cash_received = st.sidebar.number_input("Actual cash received (RM)", min_value=0.0, value=48000.0, step=1000.0)
cash_paid = st.sidebar.number_input("Actual cash paid (RM)", min_value=0.0, value=40000.0, step=1000.0)

def run_workflow():
    f = finance_calculator(revenue, cogs, opex)
    c = cash_flow_calculator(opening_cash, cash_received, cash_paid)
    r = risk_detector(revenue, cogs, opex, c["closing_cash"])
    s = strategy_simulator(revenue, cogs, opex)
    best = max(s, key=s.get)
    return {"finance": f, "cash": c, "risks": r, "strategies": s, "best": best}

if "result" not in st.session_state:
    st.session_state.result = None
if "approved" not in st.session_state:
    st.session_state.approved = None

st.markdown("# 🏙️ SME FinancePilot")
st.caption("AUTONOMOUS FINANCIAL INTELLIGENCE HQ · PROTOTYPE · DEMO / SAMPLE")
st.divider()

if page == "🏙️ 3D Headquarters":
    st.subheader("Financial Ecosystem — Interactive 3D HQ")
    st.caption("Drag to rotate · Scroll to zoom · Click a building to inspect its agent.")
    html_path = Path(__file__).parent / "components" / "hq_scene.html"
    if html_path.exists():
        components.html(html_path.read_text(encoding="utf-8"), height=720, scrolling=False)
    else:
        st.error("Missing components/hq_scene.html. Keep the components folder beside app.py.")
    a, b, c = st.columns(3)
    a.metric("Specialised agents", "5")
    b.metric("Business", business_name)
    c.metric("Mode", "DEMO")
    if st.button("🚀 Run all five agents", use_container_width=True):
        st.session_state.result = run_workflow()
        st.session_state.approved = None
        st.success("The five-agent analysis workflow has completed.")
    st.info("This prototype uses transparent Python calculation tools. The current 3D building click shows agent descriptions; the financial workflow runs with the button above.")

elif page == "📊 Financial Intelligence":
    st.subheader("01 · Finance Tower")
    st.write("Analyses sales, cost of goods sold, gross profit and operating surplus.")
    if st.button("Run Finance Agent"):
        st.session_state.result = run_workflow()
    if st.session_state.result:
        f = st.session_state.result["finance"]
        x, y, z = st.columns(3)
        x.metric("Gross profit", money(f["gross_profit"]))
        y.metric("Operating surplus", money(f["operating_surplus"]))
        z.metric("Operating margin", f'{f["operating_margin"]:.1f}%')
        st.write(f'COGS ratio: {f["cogs_ratio"]:.1f}% · OPEX ratio: {f["opex_ratio"]:.1f}%')
        st.caption("Operating surplus here is a simplified revenue − COGS − operating expenses measure. It is not accounting net profit.")

elif page == "💧 Cash Flow Analysis":
    st.subheader("02 · Cash Flow Harbour")
    st.write("Tracks actual cash received and paid, separately from accounting revenue and expenses.")
    if st.button("Run Cash Flow Agent"):
        st.session_state.result = run_workflow()
    if st.session_state.result:
        c = st.session_state.result["cash"]
        x, y = st.columns(2)
        x.metric("Net cash flow", money(c["net_cash_flow"]))
        y.metric("Closing cash", money(c["closing_cash"]))
        st.caption("Closing cash = opening cash + actual cash received − actual cash paid.")

elif page == "🔭 Risk Observatory":
    st.subheader("03 · Risk Observatory")
    if st.button("Scan business risks"):
        st.session_state.result = run_workflow()
    if st.session_state.result:
        for level, message in st.session_state.result["risks"]:
            (st.error if level == "HIGH" else st.warning if level == "MEDIUM" else st.info)(f"{level}: {message}")
    else:
        st.info("Run the risk scan to evaluate the current sample inputs.")

elif page == "⚙️ Strategy Lab":
    st.subheader("04 · Strategy Lab")
    st.write("Compares illustrative operating-surplus scenarios. Assumptions are explicit and editable in the source code.")
    if st.button("Simulate strategies"):
        st.session_state.result = run_workflow()
    if st.session_state.result:
        scenarios = st.session_state.result["strategies"]
        fig = go.Figure(go.Bar(x=list(scenarios.keys()), y=list(scenarios.values()), text=[f"RM {v:,.0f}" for v in scenarios.values()], textposition="auto"))
        fig.update_layout(template="plotly_dark", paper_bgcolor="#081522", plot_bgcolor="#081522", font_color="#edf3fa", yaxis_title="Illustrative operating surplus (RM)", height=420)
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Scenario B assumes sales rise 8%, COGS rises proportionally, and additional promotion expense equals 3% of current revenue. These are demo assumptions, not forecasts.")

elif page == "🏛️ Decision Pavilion":
    st.subheader("05 · Decision Pavilion")
    if st.button("Prepare decision report"):
        st.session_state.result = run_workflow()
        st.session_state.approved = None
    if st.session_state.result:
        result = st.session_state.result
        best = result["best"]
        st.info(f"Recommended scenario based only on the simplified operating-surplus calculation: {best}")
        st.metric("Scenario operating surplus", money(result["strategies"][best]))
        st.warning("Owner approval is required. Approval records a demo decision only; no real transaction or business change will occur.")
        if st.button("✅ Approve simulated strategy"):
            st.session_state.approved = best
        if st.session_state.approved:
            st.success(f"Demo approval recorded: {st.session_state.approved}")
    else:
        st.info("Prepare a decision report to review the recommended scenario.")

st.divider()
st.markdown("<div style='text-align:center;color:#91a9c0;padding:10px'>SME FinancePilot · Agentic AI Challenge 2026 · DEMO / SAMPLE</div>", unsafe_allow_html=True)
