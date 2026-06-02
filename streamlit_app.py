import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import psycopg2
from psycopg2 import sql
import warnings
warnings.filterwarnings("ignore")

# ── Page config ───────────────────────────────────────────
st.set_page_config(
    page_title="🇰🇭 Cambodia Personal Finance Analytics",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #0f1117; }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1f2e 0%, #16213e 100%);
        border-right: 1px solid #2d3561;
    }
    
    /* Metric cards */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #1a1f2e 0%, #16213e 100%);
        border: 1px solid #2d3561;
        border-radius: 12px;
        padding: 16px;
    }
    [data-testid="metric-container"] label {
        color: #8892b0 !important;
        font-size: 13px !important;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #64ffda !important;
        font-size: 28px !important;
        font-weight: 700 !important;
    }
    
    /* Headers */
    h1, h2, h3 { color: #ccd6f6 !important; }
    
    /* Divider */
    hr { border-color: #2d3561; }

    /* Select boxes */
    .stSelectbox label, .stMultiSelect label { color: #8892b0 !important; }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #1a1f2e;
        border-radius: 8px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #8892b0;
        border-radius: 6px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2d3561 !important;
        color: #64ffda !important;
    }
</style>
""", unsafe_allow_html=True)

# ── DB Connection ─────────────────────────────────────────
@st.cache_resource
def get_connection():
    return psycopg2.connect(
        host="postgres",
        port=5432,
        dbname="finance_db",
        user="finance_user",
        password="finance_pass"
    )

@st.cache_data(ttl=300)
def run_query(query):
    conn = get_connection()
    return pd.read_sql(query, conn)

# ── Load base data ────────────────────────────────────────
@st.cache_data(ttl=300)
def load_data():
    tx = run_query("""
        SELECT t.*, c.city, c.occupation, c.income_level, c.age, c.gender, c.monthly_income_usd
        FROM transactions_cleaned t
        LEFT JOIN customers c ON t.customer_id = c.customer_id
    """)
    tx["date"] = pd.to_datetime(
    tx["date"],
    errors="coerce"
)
    tx["month"] = tx["date"].dt.to_period("M").astype(str)
    tx["year"] = tx["date"].dt.year.fillna(0).astype(int)
    return tx

# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏦 Finance Analytics")
    st.markdown("**Cambodia Personal Finance**")
    st.markdown("---")

    page = st.selectbox(
        "📊 Navigate",
        ["🏠 Financial Overview",
         "💸 Spending Analysis",
         "👤 Customer Insights",
         "💰 Savings & Income",
         "🔍 Data Quality"]
    )

    st.markdown("---")
    st.markdown("### 🔧 Filters")

    df_full = load_data()

    # Date range filter
    # Date range filter (safe version)

df_full["date"] = pd.to_datetime(df_full["date"], errors="coerce")

valid_dates = df_full["date"].dropna()

if len(valid_dates) > 0:

    min_date = valid_dates.min().date()
    max_date = valid_dates.max().date()

    date_range = st.date_input(
        "📅 Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

else:
    st.warning("No valid dates found in database.")
    date_range = None

    # City filter
    cities = ["All"] + sorted(df_full["city"].dropna().unique().tolist())
    selected_city = st.selectbox("🏙️ City", cities)

    # Income level filter
    income_levels = ["All"] + sorted(df_full["income_level"].dropna().unique().tolist())
    selected_income = st.selectbox("💵 Income Level", income_levels)

    st.markdown("---")
    st.markdown("### 📈 Pipeline Stats")
    st.metric("Total Transactions", f"{len(df_full):,}")
    st.metric("Total Customers", f"{df_full['customer_id'].nunique():,}")
    st.metric("Date Range", f"{df_full['year'].min()}–{df_full['year'].max()}")

# ── Apply filters ─────────────────────────────────────────
df = df_full.copy()
if date_range and len(date_range) == 2:
    df = df[
        (df["date"].dt.date >= date_range[0]) &
        (df["date"].dt.date <= date_range[1])
    ]
if selected_city != "All":
    df = df[df["city"] == selected_city]
if selected_income != "All":
    df = df[df["income_level"] == selected_income]

# ── Color palette ─────────────────────────────────────────
COLORS = {
    "Income":       "#64ffda",
    "Essential":    "#7ec8e3",
    "Non-Essential":"#f4a261",
    "Savings":      "#a8dadc",
    "teal":         "#64ffda",
    "purple":       "#c77dff",
    "orange":       "#f4a261",
    "blue":         "#7ec8e3",
}
CHART_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(26,31,46,0.8)",
    font=dict(color="#ccd6f6", family="Inter"),
    xaxis=dict(gridcolor="#2d3561", showgrid=True),
    yaxis=dict(gridcolor="#2d3561", showgrid=True),
)

# ══════════════════════════════════════════════════════════
# PAGE 1 — Financial Overview
# ══════════════════════════════════════════════════════════
if page == "🏠 Financial Overview":
    st.title("🏠 Financial Overview")
    st.markdown("*Cambodia Personal Finance Analytics — 1M+ Transactions*")
    st.markdown("---")

    # KPI Row
    col1, col2, col3, col4 = st.columns(4)
    total_income  = df[df["spending_type"] == "Income"]["amount_usd"].sum()
    total_expense = df[df["transaction_type"] == "debit"]["amount_usd"].sum()
    total_anomaly = df[df["is_anomaly"] == True].shape[0]
    savings_rate  = ((total_income - total_expense) / total_income * 100) if total_income > 0 else 0

    col1.metric("💰 Total Income",   f"${total_income/1e6:.1f}M")
    col2.metric("💸 Total Expense",  f"${total_expense/1e6:.1f}M")
    col3.metric("⚠️ Anomalies",      f"{total_anomaly:,}")
    col4.metric("📈 Savings Rate",   f"{savings_rate:.1f}%")

    st.markdown("---")

    # Monthly trend
    st.subheader("📈 Monthly Income vs Expense Trend")
    monthly = df[df["spending_type"].isin(["Income","Essential","Non-Essential","Savings"])] \
        .groupby(["month","spending_type"])["amount_usd"].sum().reset_index()

    fig = px.line(
        monthly, x="month", y="amount_usd", color="spending_type",
        color_discrete_map=COLORS,
        labels={"amount_usd": "Total USD", "month": "Month", "spending_type": "Type"},
    )
    fig.update_layout(**CHART_THEME, height=400, legend=dict(orientation="h", y=1.1))
    fig.update_traces(line=dict(width=2.5))
    st.plotly_chart(fig, use_container_width=True)

    # Income vs Expense bar by year
    st.subheader("📊 Yearly Income vs Expense")
    yearly_income  = df[df["spending_type"]=="Income"].groupby("year")["amount_usd"].sum()
    yearly_expense = df[df["transaction_type"]=="debit"].groupby("year")["amount_usd"].sum()
    years = sorted(set(yearly_income.index) | set(yearly_expense.index))

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(name="Income",  x=years, y=[yearly_income.get(y,0) for y in years],  marker_color=COLORS["Income"]))
    fig2.add_trace(go.Bar(name="Expense", x=years, y=[yearly_expense.get(y,0) for y in years], marker_color=COLORS["Non-Essential"]))
    fig2.update_layout(**CHART_THEME, height=350, barmode="group",
                       legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig2, use_container_width=True)

# ══════════════════════════════════════════════════════════
# PAGE 2 — Spending Analysis
# ══════════════════════════════════════════════════════════
elif page == "💸 Spending Analysis":
    st.title("💸 Spending Analysis")
    st.markdown("---")

    col1, col2 = st.columns(2)

    # Spending by category
    with col1:
        st.subheader("🗂️ Spending by Category")
        cat_spend = df[df["transaction_type"]=="debit"] \
            .groupby("category")["amount_usd"].sum() \
            .sort_values(ascending=True).reset_index()
        fig = px.bar(cat_spend, x="amount_usd", y="category", orientation="h",
                     color="amount_usd", color_continuous_scale="Teal")
        fig.update_layout(**CHART_THEME, height=400, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    # Essential vs Non-Essential
    with col2:
        st.subheader("⚖️ Essential vs Non-Essential")
        ess = df[df["spending_type"].isin(["Essential","Non-Essential"])] \
            .groupby("spending_type")["amount_usd"].sum().reset_index()
        fig = px.pie(ess, names="spending_type", values="amount_usd",
                     hole=0.5,
                     color="spending_type",
                     color_discrete_map={"Essential": COLORS["teal"], "Non-Essential": COLORS["orange"]})
        fig.update_layout(**CHART_THEME, height=400)
        fig.update_traces(textposition="outside", textinfo="percent+label")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    col3, col4 = st.columns(2)

    # Top 10 sub-categories
    with col3:
        st.subheader("🏆 Top 10 Sub-categories")
        top_sub = df[df["transaction_type"]=="debit"] \
            .groupby("sub_category")["amount_usd"].sum() \
            .sort_values(ascending=False).head(10).reset_index()
        top_sub["sub_category"] = top_sub["sub_category"].str.title()
        fig = px.bar(top_sub, x="amount_usd", y="sub_category", orientation="h",
                     color="amount_usd", color_continuous_scale="Mint")
        fig.update_layout(**CHART_THEME, height=400, coloraxis_showscale=False,
                          yaxis=dict(autorange="reversed", gridcolor="#2d3561"))
        st.plotly_chart(fig, use_container_width=True)

    # Payment method
    with col4:
        st.subheader("💳 Payment Method Usage")
        pay = df.groupby("payment_method").agg(
            count=("transaction_id","count"),
            total=("amount_usd","sum")
        ).sort_values("count", ascending=False).reset_index()
        pay["payment_method"] = pay["payment_method"].str.title()
        fig = px.bar(pay, x="payment_method", y="count",
                     color="count", color_continuous_scale="Purples")
        fig.update_layout(**CHART_THEME, height=400, coloraxis_showscale=False,
                          xaxis=dict(tickangle=-30, gridcolor="#2d3561"))
        st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════
# PAGE 3 — Customer Insights
# ══════════════════════════════════════════════════════════
elif page == "👤 Customer Insights":
    st.title("👤 Customer Insights")
    st.markdown("---")

    col1, col2 = st.columns(2)

    # Spending by city
    with col1:
        st.subheader("🏙️ Spending by City")
        city_spend = df[df["transaction_type"]=="debit"] \
            .groupby("city")["amount_usd"].sum() \
            .sort_values(ascending=True).reset_index()
        fig = px.bar(city_spend, x="amount_usd", y="city", orientation="h",
                     color="amount_usd", color_continuous_scale="Blues")
        fig.update_layout(**CHART_THEME, height=420, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    # Income level distribution
    with col2:
        st.subheader("💵 Customer by Income Level")
        inc = df.drop_duplicates("customer_id") \
            .groupby("income_level")["customer_id"].count().reset_index()
        fig = px.pie(inc, names="income_level", values="customer_id", hole=0.5,
                     color_discrete_sequence=px.colors.sequential.Teal)
        fig.update_layout(**CHART_THEME, height=420)
        fig.update_traces(textposition="outside", textinfo="percent+label")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    col3, col4 = st.columns(2)

    # Spending by occupation
    with col3:
        st.subheader("👔 Spending by Occupation")
        occ = df[df["transaction_type"]=="debit"] \
            .groupby("occupation")["amount_usd"].sum() \
            .sort_values(ascending=True).reset_index()
        fig = px.bar(occ, x="amount_usd", y="occupation", orientation="h",
                     color="amount_usd", color_continuous_scale="Purples")
        fig.update_layout(**CHART_THEME, height=420, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    # Gender distribution
    with col4:
        st.subheader("👥 Gender Distribution")
        gender = df.drop_duplicates("customer_id") \
            .groupby("gender")["customer_id"].count().reset_index()
        fig = px.pie(gender, names="gender", values="customer_id", hole=0.5,
                     color_discrete_map={"Male": COLORS["blue"], "Female": COLORS["purple"]})
        fig.update_layout(**CHART_THEME, height=420)
        fig.update_traces(textposition="outside", textinfo="percent+label")
        st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════
# PAGE 4 — Savings & Income
# ══════════════════════════════════════════════════════════
elif page == "💰 Savings & Income":
    st.title("💰 Savings & Income")
    st.markdown("---")

    # Monthly savings trend
    st.subheader("📈 Monthly Savings Trend")
    savings = df[df["spending_type"]=="Savings"] \
        .groupby("month")["amount_usd"].sum().reset_index()
    fig = px.line(savings, x="month", y="amount_usd",
                  color_discrete_sequence=[COLORS["teal"]])
    fig.update_traces(line=dict(width=2.5), fill="tozeroy",
                      fillcolor="rgba(100,255,218,0.1)")
    fig.update_layout(**CHART_THEME, height=350)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    col1, col2 = st.columns(2)

    # Income by type
    with col1:
        st.subheader("💼 Income by Type")
        inc_type = df[df["spending_type"]=="Income"] \
            .groupby("sub_category")["amount_usd"].sum() \
            .sort_values(ascending=True).reset_index()
        inc_type["sub_category"] = inc_type["sub_category"].str.title()
        fig = px.bar(inc_type, x="amount_usd", y="sub_category", orientation="h",
                     color="amount_usd", color_continuous_scale="Teal")
        fig.update_layout(**CHART_THEME, height=380, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    # Savings by income level
    with col2:
        st.subheader("🏦 Savings by Income Level")
        sav_inc = df[df["spending_type"]=="Savings"] \
            .groupby("income_level")["amount_usd"].sum() \
            .sort_values(ascending=False).reset_index()
        fig = px.bar(sav_inc, x="income_level", y="amount_usd",
                     color="amount_usd", color_continuous_scale="Mint")
        fig.update_layout(**CHART_THEME, height=380, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════
# PAGE 5 — Data Quality
# ══════════════════════════════════════════════════════════
elif page == "🔍 Data Quality":
    st.title("🔍 Data Quality Report")
    st.markdown("*ETL pipeline data quality metrics*")
    st.markdown("---")

    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    total        = len(df)
    anomalies    = df["is_anomaly"].sum()
    nulls_pay    = df["payment_method"].isna().sum()
    nulls_sub    = df["sub_category"].isna().sum()

    col1.metric("Total Records",    f"{total:,}")
    col2.metric("Anomalous Amounts",f"{anomalies:,}", f"{anomalies/total*100:.1f}%")
    col3.metric("Unknown Payment",  f"{(df['payment_method']=='Unknown').sum():,}")
    col4.metric("Uncategorised",    f"{(df['sub_category']=='uncategorised').sum():,}")

    st.markdown("---")

    col5, col6 = st.columns(2)

    # Anomalies by category
    with col5:
        st.subheader("⚠️ Anomalies by Category")
        anom = df[df["is_anomaly"]==True] \
            .groupby("category")["transaction_id"].count() \
            .sort_values(ascending=True).reset_index()
        fig = px.bar(anom, x="transaction_id", y="category", orientation="h",
                     color="transaction_id", color_continuous_scale="Reds")
        fig.update_layout(**CHART_THEME, height=400, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    # Transaction type distribution
    with col6:
        st.subheader("🔄 Transaction Type Split")
        tx_type = df.groupby("transaction_type")["transaction_id"].count().reset_index()
        fig = px.pie(tx_type, names="transaction_type", values="transaction_id", hole=0.5,
                     color_discrete_sequence=[COLORS["teal"], COLORS["orange"]])
        fig.update_layout(**CHART_THEME, height=400)
        fig.update_traces(textposition="outside", textinfo="percent+label")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Currency distribution
    st.subheader("💱 Currency Distribution")
    curr = df.groupby("currency").agg(
        count=("transaction_id","count"),
        total_usd=("amount_usd","sum")
    ).reset_index()
    fig = px.bar(curr, x="currency", y="count",
                 color="currency",
                 color_discrete_map={"KHR": COLORS["teal"], "USD": COLORS["orange"], "Unknown": "#666"})
    fig.update_layout(**CHART_THEME, height=300)
    st.plotly_chart(fig, use_container_width=True)

    # Raw data sample
    st.markdown("---")
    st.subheader("📋 Sample Data (50 rows)")
    st.dataframe(
        df.head(50)[[
            "transaction_id","customer_id","date","amount","currency",
            "amount_usd","category","sub_category","spending_type",
            "transaction_type","payment_method","is_anomaly"
        ]],
        use_container_width=True,
        height=300
    )