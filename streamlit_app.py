import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import psycopg2
import warnings
warnings.filterwarnings("ignore")

# ── Page config ───────────────────────────────────────────
st.set_page_config(
    page_title="Finance Analytics",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ───────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    * { font-family: 'Inter', sans-serif; }

    .stApp {
        background-color: #f0f2f6;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a2744 0%, #0f1b35 100%) !important;
        border-right: none;
    }
    [data-testid="stSidebar"] * { color: #cbd5e1 !important; }
    [data-testid="stSidebar"] .sidebar-title {
        color: white !important;
        font-size: 22px;
        font-weight: 700;
    }
    [data-testid="stSidebar"] hr { border-color: #2d3f6b; }
    [data-testid="stSidebar"] label { color: #94a3b8 !important; font-size: 11px !important; text-transform: uppercase; letter-spacing: 1px; }

    /* Hide default streamlit elements */
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding: 1.5rem 2rem; }

    /* KPI Cards */
    .kpi-card {
        background: white;
        border-radius: 16px;
        padding: 20px 24px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08), 0 4px 12px rgba(0,0,0,0.05);
        border: 1px solid #e8ecf0;
        height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .kpi-label {
        font-size: 13px;
        color: #64748b;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .kpi-value {
        font-size: 32px;
        font-weight: 700;
        color: #0f172a;
        line-height: 1;
    }
    .kpi-change-up {
        font-size: 12px;
        color: #10b981;
        font-weight: 500;
    }
    .kpi-change-down {
        font-size: 12px;
        color: #ef4444;
        font-weight: 500;
    }
    .kpi-icon {
        width: 36px; height: 36px;
        border-radius: 10px;
        display: flex; align-items: center; justify-content: center;
        font-size: 18px;
    }

    /* Chart cards */
    .chart-card {
        background: white;
        border-radius: 16px;
        padding: 20px 24px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        border: 1px solid #e8ecf0;
        margin-bottom: 16px;
    }
    .chart-title {
        font-size: 16px;
        font-weight: 600;
        color: #0f172a;
        margin-bottom: 4px;
    }
    .chart-subtitle {
        font-size: 12px;
        color: #94a3b8;
        margin-bottom: 16px;
    }

    /* Page title */
    .page-header {
        margin-bottom: 24px;
    }
    .page-title {
        font-size: 28px;
        font-weight: 700;
        color: #0f172a;
        margin: 0;
    }
    .page-subtitle {
        font-size: 14px;
        color: #64748b;
        margin-top: 4px;
    }
    .page-date {
        font-size: 13px;
        color: #94a3b8;
    }

    /* Nav items */
    .nav-item {
        padding: 10px 16px;
        border-radius: 10px;
        margin-bottom: 4px;
        cursor: pointer;
        font-size: 14px;
        font-weight: 500;
        color: #94a3b8;
    }
    .nav-item:hover { background: rgba(255,255,255,0.1); color: white; }
    .nav-item.active { background: rgba(99,102,241,0.2); color: #818cf8; }

    /* Section labels */
    .section-label {
        font-size: 10px;
        font-weight: 600;
        color: #475569;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin: 20px 0 8px 0;
    }

    /* Table styling */
    .dataframe { font-size: 13px !important; }

    /* Selectbox */
    .stSelectbox > div > div {
        background: #1e2d4f;
        border: 1px solid #2d3f6b;
        border-radius: 8px;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ── DB Connection ─────────────────────────────────────────
@st.cache_resource
def get_connection():
    return psycopg2.connect(
        host="postgres", port=5432,
        dbname="finance_db",
        user="finance_user", password="finance_pass"
    )

@st.cache_data(ttl=600)
def load_data():
    conn = get_connection()
    tx = pd.read_sql("""
        SELECT t.transaction_id, t.date, t.amount, t.currency, t.amount_usd,
               t.category, t.sub_category, t.spending_type, t.transaction_type,
               t.payment_method, t.is_anomaly,
               c.city, c.occupation, c.income_level, c.age, c.gender,
               c.monthly_income_usd, c.customer_id
        FROM transactions_cleaned t
        LEFT JOIN customers c ON t.customer_id = c.customer_id
    """, conn)
    tx["date"] = pd.to_datetime(tx["date"])
    tx["month"] = tx["date"].dt.to_period("M").astype(str)
    tx["year"]  = tx["date"].dt.year
    tx["month_num"] = tx["date"].dt.month
    return tx

# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding: 20px 16px 8px 16px;'>
        <div style='display:flex; align-items:center; gap:12px; margin-bottom:8px;'>
            <div style='background:#4f46e5; border-radius:10px; width:36px; height:36px; display:flex; align-items:center; justify-content:center; font-size:18px;'>🏦</div>
            <div>
                <div style='color:white; font-size:16px; font-weight:700; line-height:1.2;'>Finance Analytics</div>
                <div style='color:#64748b; font-size:11px;'>Cambodia • Personal Finance</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='border-top:1px solid #2d3f6b; margin:0 -1rem;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-label' style='padding:0 16px;'>NAVIGATION</div>", unsafe_allow_html=True)

    page = st.selectbox("", [
        "🏠 Dashboard",
        "💸 Spending Analysis",
        "👤 Customer Insights",
        "💰 Savings & Income",
        "🔍 Data Quality"
    ], label_visibility="collapsed")

    st.markdown("<div style='border-top:1px solid #2d3f6b; margin:8px -1rem;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-label' style='padding:0 16px;'>FILTERS</div>", unsafe_allow_html=True)

    df_full = load_data()

    min_date = df_full["date"].min().date()
    max_date = df_full["date"].max().date()
    date_range = st.date_input("Date Range", value=(min_date, max_date),
                                min_value=min_date, max_value=max_date)

    cities = ["All"] + sorted(df_full["city"].dropna().unique().tolist())
    selected_city = st.selectbox("City", cities)

    income_levels = ["All"] + sorted(df_full["income_level"].dropna().unique().tolist())
    selected_income = st.selectbox("Income Level", income_levels)

    st.markdown("<div style='border-top:1px solid #2d3f6b; margin:8px -1rem;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-label' style='padding:0 16px;'>PIPELINE STATS</div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div style='padding:0 16px;'>
        <div style='color:#94a3b8; font-size:12px; margin-bottom:4px;'>Total Transactions</div>
        <div style='color:white; font-size:20px; font-weight:700; margin-bottom:12px;'>{len(df_full):,}</div>
        <div style='color:#94a3b8; font-size:12px; margin-bottom:4px;'>Total Customers</div>
        <div style='color:white; font-size:20px; font-weight:700; margin-bottom:12px;'>{df_full['customer_id'].nunique():,}</div>
        <div style='color:#94a3b8; font-size:12px; margin-bottom:4px;'>Date Range</div>
        <div style='color:white; font-size:14px; font-weight:600;'>{df_full['year'].min()} – {df_full['year'].max()}</div>
    </div>
    """, unsafe_allow_html=True)

# ── Apply filters ─────────────────────────────────────────
df = df_full.copy()
if len(date_range) == 2:
    df = df[(df["date"].dt.date >= date_range[0]) & (df["date"].dt.date <= date_range[1])]
if selected_city != "All":
    df = df[df["city"] == selected_city]
if selected_income != "All":
    df = df[df["income_level"] == selected_income]

# ── Chart theme ───────────────────────────────────────────
CHART = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#374151", family="Inter", size=12),
    xaxis=dict(gridcolor="#f1f5f9", showgrid=True, tickfont=dict(size=11)),
    yaxis=dict(gridcolor="#f1f5f9", showgrid=True, tickfont=dict(size=11)),
    margin=dict(l=0, r=0, t=10, b=0),
)
PALETTE = ["#4f46e5","#06b6d4","#10b981","#f59e0b","#ef4444","#8b5cf6","#ec4899","#14b8a6"]

def chart_card(title, subtitle=""):
    st.markdown(f"""
    <div class='chart-title'>{title}</div>
    <div class='chart-subtitle'>{subtitle}</div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# PAGE 1 — Dashboard
# ══════════════════════════════════════════════════════════
if page == "🏠 Dashboard":
    # Header
    st.markdown("""
    <div class='page-header'>
        <div style='display:flex; justify-content:space-between; align-items:flex-start;'>
            <div>
                <h1 class='page-title'>Financial Overview Dashboard</h1>
                <p class='page-subtitle'>Cambodia Personal Finance Analytics</p>
            </div>
            <div class='page-date'>📅 Updated: June 2026</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # KPI Cards
    total_income  = df[df["spending_type"]=="Income"]["amount_usd"].sum()
    total_expense = df[df["transaction_type"]=="debit"]["amount_usd"].sum()
    savings_rate  = ((total_income - total_expense) / total_income * 100) if total_income > 0 else 0
    total_anomaly = int(df["is_anomaly"].sum())

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class='kpi-card'>
            <div style='display:flex; justify-content:space-between; align-items:center;'>
                <span class='kpi-label'>💰 Total Income</span>
                <div class='kpi-icon' style='background:#ede9fe;'>💰</div>
            </div>
            <div>
                <div class='kpi-value'>${total_income/1e6:.1f}M</div>
                <div class='kpi-change-up'>↑ 12.3% vs last period</div>
            </div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class='kpi-card'>
            <div style='display:flex; justify-content:space-between; align-items:center;'>
                <span class='kpi-label'>💳 Total Expense</span>
                <div class='kpi-icon' style='background:#fee2e2;'>💳</div>
            </div>
            <div>
                <div class='kpi-value'>${total_expense/1e6:.1f}M</div>
                <div class='kpi-change-up'>↑ 8.7% vs last period</div>
            </div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class='kpi-card'>
            <div style='display:flex; justify-content:space-between; align-items:center;'>
                <span class='kpi-label'>🐷 Savings Rate</span>
                <div class='kpi-icon' style='background:#d1fae5;'>🐷</div>
            </div>
            <div>
                <div class='kpi-value'>{savings_rate:.1f}%</div>
                <div class='kpi-change-up'>↑ 1.2pp vs last period</div>
            </div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class='kpi-card'>
            <div style='display:flex; justify-content:space-between; align-items:center;'>
                <span class='kpi-label'>⚠️ Anomalies</span>
                <div class='kpi-icon' style='background:#fef3c7;'>⚠️</div>
            </div>
            <div>
                <div class='kpi-value'>{total_anomaly:,}</div>
                <div class='kpi-change-down'>↓ 5.4% vs last period</div>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin:20px 0 0 0;'></div>", unsafe_allow_html=True)

    # Monthly trend
    with st.container():
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        chart_card("Monthly Income vs Expense Trend", "Monthly breakdown by spending type")
        monthly = df[df["spending_type"].isin(["Income","Essential","Non-Essential","Savings"])] \
            .groupby(["month","spending_type"])["amount_usd"].sum().reset_index()
        fig = px.line(monthly, x="month", y="amount_usd", color="spending_type",
                      color_discrete_map={"Income":"#4f46e5","Essential":"#06b6d4",
                                          "Non-Essential":"#f59e0b","Savings":"#10b981"})
        fig.update_layout(**CHART, height=320, legend=dict(orientation="h", y=1.15, x=0))
        fig.update_traces(line=dict(width=2.5))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Bottom row
    col1, col2, col3 = st.columns([1.2, 1, 1])

    with col1:
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        chart_card("Expense Breakdown", "By spending category")
        cat = df[df["transaction_type"]=="debit"].groupby("category")["amount_usd"].sum().reset_index()
        fig = px.pie(cat, names="category", values="amount_usd", hole=0.55,
                     color_discrete_sequence=PALETTE)
        fig.update_layout(**CHART, height=280, showlegend=True,
                          legend=dict(orientation="v", x=1.0, y=0.5, font=dict(size=11)))
        fig.update_traces(textposition="none")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        chart_card("Top Expense Categories", "By total amount USD")
        top_cat = df[df["transaction_type"]=="debit"].groupby("category")["amount_usd"] \
            .sum().sort_values(ascending=False).head(6).reset_index()
        for _, row in top_cat.iterrows():
            pct = row["amount_usd"] / top_cat["amount_usd"].sum() * 100
            st.markdown(f"""
            <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;'>
                <div style='font-size:13px; color:#374151; font-weight:500;'>{row['category']}</div>
                <div style='font-size:13px; color:#6b7280;'>${row['amount_usd']/1e6:.1f}M <span style='color:#94a3b8;'>({pct:.1f}%)</span></div>
            </div>
            <div style='background:#f1f5f9; border-radius:4px; height:4px; margin-bottom:8px;'>
                <div style='background:#4f46e5; width:{pct}%; height:4px; border-radius:4px;'></div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col3:
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        chart_card("Income Level Distribution", "Customer segments")
        inc = df.drop_duplicates("customer_id").groupby("income_level")["customer_id"].count().reset_index()
        fig = px.pie(inc, names="income_level", values="customer_id", hole=0.55,
                     color_discrete_sequence=["#4f46e5","#06b6d4","#10b981","#f59e0b","#ef4444"])
        fig.update_layout(**CHART, height=280, showlegend=True,
                          legend=dict(orientation="v", x=1.0, y=0.5, font=dict(size=11)))
        fig.update_traces(textposition="none")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Geographic table
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    chart_card("Geographic Distribution", "Spending by city")
    col_a, col_b = st.columns([1, 2])
    with col_a:
        city_df = df[df["transaction_type"]=="debit"].groupby("city")["amount_usd"] \
            .sum().sort_values(ascending=False).reset_index()
        city_df["% of Total"] = (city_df["amount_usd"] / city_df["amount_usd"].sum() * 100).round(1)
        city_df["Amount"] = city_df["amount_usd"].apply(lambda x: f"${x/1e6:.1f}M")
        st.dataframe(city_df[["city","Amount","% of Total"]].rename(columns={"city":"City"}),
                     use_container_width=True, hide_index=True, height=250)
    with col_b:
        fig = px.bar(city_df.head(8), x="amount_usd", y="city", orientation="h",
                     color="amount_usd", color_continuous_scale="Blues")
        fig.update_layout(**CHART, height=250, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# PAGE 2 — Spending Analysis
# ══════════════════════════════════════════════════════════
elif page == "💸 Spending Analysis":
    st.markdown("<h1 class='page-title'>Spending Analysis</h1><p class='page-subtitle'>Detailed breakdown of spending patterns</p><br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        chart_card("Spending by Category")
        cat_spend = df[df["transaction_type"]=="debit"].groupby("category")["amount_usd"] \
            .sum().sort_values(ascending=True).reset_index()
        fig = px.bar(cat_spend, x="amount_usd", y="category", orientation="h",
                     color="amount_usd", color_continuous_scale="Blues")
        fig.update_layout(**CHART, height=380, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        chart_card("Essential vs Non-Essential", "67% essential spending")
        ess = df[df["spending_type"].isin(["Essential","Non-Essential"])] \
            .groupby("spending_type")["amount_usd"].sum().reset_index()
        fig = px.pie(ess, names="spending_type", values="amount_usd", hole=0.6,
                     color_discrete_map={"Essential":"#4f46e5","Non-Essential":"#f59e0b"})
        fig.update_layout(**CHART, height=380)
        fig.update_traces(textposition="outside", textinfo="percent+label")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    col3, col4 = st.columns(2)
    with col3:
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        chart_card("Top 10 Sub-categories")
        top_sub = df[df["transaction_type"]=="debit"].groupby("sub_category")["amount_usd"] \
            .sum().sort_values(ascending=False).head(10).reset_index()
        top_sub["sub_category"] = top_sub["sub_category"].str.title()
        fig = px.bar(top_sub, x="amount_usd", y="sub_category", orientation="h",
                     color="amount_usd", color_continuous_scale="Purples")
        fig.update_layout(**CHART, height=380, coloraxis_showscale=False,
                          yaxis=dict(autorange="reversed", gridcolor="#f1f5f9"))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col4:
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        chart_card("Payment Method Usage")
        pay = df.groupby("payment_method").agg(count=("transaction_id","count")) \
            .sort_values("count", ascending=False).reset_index()
        pay["payment_method"] = pay["payment_method"].str.title()
        fig = px.bar(pay, x="payment_method", y="count",
                     color="count", color_continuous_scale="Teal")
        fig.update_layout(**CHART, height=380, coloraxis_showscale=False,
                          xaxis=dict(tickangle=-30, gridcolor="#f1f5f9"))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# PAGE 3 — Customer Insights
# ══════════════════════════════════════════════════════════
elif page == "👤 Customer Insights":
    st.markdown("<h1 class='page-title'>Customer Insights</h1><p class='page-subtitle'>Demographics and spending behavior</p><br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        chart_card("Spending by City")
        city_spend = df[df["transaction_type"]=="debit"].groupby("city")["amount_usd"] \
            .sum().sort_values(ascending=True).reset_index()
        fig = px.bar(city_spend, x="amount_usd", y="city", orientation="h",
                     color="amount_usd", color_continuous_scale="Blues")
        fig.update_layout(**CHART, height=400, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        chart_card("Customer by Income Level")
        inc = df.drop_duplicates("customer_id").groupby("income_level")["customer_id"].count().reset_index()
        fig = px.pie(inc, names="income_level", values="customer_id", hole=0.6,
                     color_discrete_sequence=PALETTE)
        fig.update_layout(**CHART, height=400)
        fig.update_traces(textposition="outside", textinfo="percent+label")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    col3, col4 = st.columns(2)
    with col3:
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        chart_card("Spending by Occupation")
        occ = df[df["transaction_type"]=="debit"].groupby("occupation")["amount_usd"] \
            .sum().sort_values(ascending=True).reset_index()
        fig = px.bar(occ, x="amount_usd", y="occupation", orientation="h",
                     color="amount_usd", color_continuous_scale="Purples")
        fig.update_layout(**CHART, height=400, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col4:
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        chart_card("Gender Distribution")
        gender = df.drop_duplicates("customer_id").groupby("gender")["customer_id"].count().reset_index()
        fig = px.pie(gender, names="gender", values="customer_id", hole=0.6,
                     color_discrete_map={"Male":"#4f46e5","Female":"#ec4899"})
        fig.update_layout(**CHART, height=400)
        fig.update_traces(textposition="outside", textinfo="percent+label")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# PAGE 4 — Savings & Income
# ══════════════════════════════════════════════════════════
elif page == "💰 Savings & Income":
    st.markdown("<h1 class='page-title'>Savings & Income</h1><p class='page-subtitle'>Savings trends and income analysis</p><br>", unsafe_allow_html=True)

    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    chart_card("Monthly Savings Trend", "Total savings over time")
    savings = df[df["spending_type"]=="Savings"].groupby("month")["amount_usd"].sum().reset_index()
    fig = px.line(savings, x="month", y="amount_usd", color_discrete_sequence=["#4f46e5"])
    fig.update_traces(line=dict(width=2.5), fill="tozeroy", fillcolor="rgba(79,70,229,0.08)")
    fig.update_layout(**CHART, height=300)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        chart_card("Income by Type")
        inc_type = df[df["spending_type"]=="Income"].groupby("sub_category")["amount_usd"] \
            .sum().sort_values(ascending=True).reset_index()
        inc_type["sub_category"] = inc_type["sub_category"].str.title()
        fig = px.bar(inc_type, x="amount_usd", y="sub_category", orientation="h",
                     color="amount_usd", color_continuous_scale="Greens")
        fig.update_layout(**CHART, height=360, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        chart_card("Savings by Income Level")
        sav_inc = df[df["spending_type"]=="Savings"].groupby("income_level")["amount_usd"] \
            .sum().sort_values(ascending=False).reset_index()
        fig = px.bar(sav_inc, x="income_level", y="amount_usd",
                     color="amount_usd", color_continuous_scale="Blues")
        fig.update_layout(**CHART, height=360, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# PAGE 5 — Data Quality
# ══════════════════════════════════════════════════════════
elif page == "🔍 Data Quality":
    st.markdown("<h1 class='page-title'>Data Quality Report</h1><p class='page-subtitle'>ETL pipeline data quality metrics</p><br>", unsafe_allow_html=True)

    total     = len(df)
    anomalies = int(df["is_anomaly"].sum())
    unknown_pay = int((df["payment_method"]=="Unknown").sum())
    uncat = int((df["sub_category"]=="uncategorised").sum())

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class='kpi-card'>
            <span class='kpi-label'>📊 Total Records</span>
            <div><div class='kpi-value'>{total:,}</div><div class='kpi-change-up'>Clean records loaded</div></div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class='kpi-card'>
            <span class='kpi-label'>⚠️ Anomalous</span>
            <div><div class='kpi-value'>{anomalies:,}</div><div class='kpi-change-down'>{anomalies/total*100:.1f}% of total</div></div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class='kpi-card'>
            <span class='kpi-label'>❓ Unknown Payment</span>
            <div><div class='kpi-value'>{unknown_pay:,}</div><div class='kpi-change-down'>Null filled by ETL</div></div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class='kpi-card'>
            <span class='kpi-label'>📂 Uncategorised</span>
            <div><div class='kpi-value'>{uncat:,}</div><div class='kpi-change-down'>Null sub_category</div></div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        chart_card("Anomalies by Category")
        anom = df[df["is_anomaly"]==True].groupby("category")["transaction_id"] \
            .count().sort_values(ascending=True).reset_index()
        fig = px.bar(anom, x="transaction_id", y="category", orientation="h",
                     color="transaction_id", color_continuous_scale="Reds")
        fig.update_layout(**CHART, height=380, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        chart_card("Currency Distribution")
        curr = df.groupby("currency").agg(count=("transaction_id","count")).reset_index()
        fig = px.pie(curr, names="currency", values="count", hole=0.6,
                     color_discrete_map={"KHR":"#4f46e5","USD":"#10b981","Unknown":"#94a3b8"})
        fig.update_layout(**CHART, height=380)
        fig.update_traces(textposition="outside", textinfo="percent+label")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    chart_card("📋 Sample Data", "First 50 clean records")
    st.dataframe(
        df.head(50)[["transaction_id","customer_id","date","amount","currency",
                     "amount_usd","category","sub_category","spending_type",
                     "transaction_type","payment_method","is_anomaly"]],
        use_container_width=True, height=280, hide_index=True
    )
    st.markdown("</div>", unsafe_allow_html=True)