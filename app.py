import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------------------------------------------
# 1. PAGE CONFIGURATION & CUSTOM CSS
# -------------------------------------------------------------------
st.set_page_config(page_title="Pizza Sales Dashboard", page_icon="🍕", layout="wide")

st.markdown("""
<style>
    /* Header Styling */
    .header-section {
        background: linear-gradient(90deg, #0f172a 0%, #1e293b 100%);
        padding: 30px;
        border-radius: 12px;
        color: white;
        margin-bottom: 30px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .header-title { font-size: 2.5rem; font-weight: 800; margin-bottom: 10px; }
    .header-subtitle { font-size: 1.1rem; color: #cbd5e1; font-weight: 400; }
    
    /* KPI Card Styling */
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border-left: 5px solid #0284c7;
        padding: 25px 15px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.08);
        transition: transform 0.3s ease;
        text-align: center;
        margin-bottom: 20px;
    }
    .metric-card:hover { transform: translateY(-6px); border-left: 5px solid #0369a1; }
    .metric-icon { font-size: 2.8rem; margin-bottom: 12px; }
    .metric-title { color: #64748b; font-size: 0.95rem; font-weight: 700; text-transform: uppercase; }
    .metric-value { color: #0f172a; font-size: 2.2rem; font-weight: 800; margin: 0; }
    
    /* Standard Chart Container */
    .chart-container {
        background: #ffffff; border-radius: 12px;
        box-shadow: 0 6px 15px rgba(0,0,0,0.08);
        padding: 20px; margin-top: 15px; border-top: 5px solid #0284c7;
    }
    
    /* Special Pizza Box styling for the Pie Chart */
    .pizza-box {
        background: radial-gradient(circle, #fffbeb 0%, #fde68a 100%);
        border: 3px dashed #d97706; border-radius: 15px;
        padding: 25px; margin-top: 15px; text-align: center; position: relative;
    }
    .pizza-box-title { color: #b45309; font-size: 1.8rem; font-weight: 800; font-family: 'Comic Sans MS', cursive, sans-serif; }
    .pizza-box-badge { position: absolute; top: -15px; right: -15px; background: #ef4444; color: white; padding: 10px; border-radius: 50%; font-weight: bold; transform: rotate(15deg); }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# 2. DATA LOADING & CACHING (FIXED ENCODING)
# -------------------------------------------------------------------
@st.cache_data
def load_data():
    # Using 'windows-1252' safely handles the 0x91 smart quotes and special characters
    orders = pd.read_csv('orders.csv', encoding='windows-1252')
    order_details = pd.read_csv('order_details.csv', encoding='windows-1252')
    pizzas = pd.read_csv('pizzas.csv', encoding='windows-1252')
    pizza_types = pd.read_csv('pizza_types.csv', encoding='windows-1252')
    return orders, order_details, pizzas, pizza_types

orders, order_details, pizzas, pizza_types = load_data()

# -------------------------------------------------------------------
# 3. DATA PROCESSING
# -------------------------------------------------------------------
# Process KPIs
df_sales = pd.merge(order_details, pizzas, on='pizza_id', how='left')
df_sales['total_price'] = df_sales['quantity'] * df_sales['price']

total_revenue = df_sales['total_price'].sum()
total_orders = orders['order_id'].nunique()
total_pizzas_sold = df_sales['quantity'].sum()
avg_order_value = total_revenue / total_orders if total_orders > 0 else 0

# Process Time Trends & Distributions
df_sales = pd.merge(df_sales, pizza_types, on='pizza_type_id', how='left')
orders['date'] = pd.to_datetime(orders['date'])
orders['hour'] = pd.to_datetime(orders['time'], format='%H:%M:%S').dt.hour
df_timeline = pd.merge(df_sales, orders, on='order_id', how='left')

monthly_sales = df_timeline.groupby(df_timeline['date'].dt.to_period('M'))['total_price'].sum().reset_index()
monthly_sales['date'] = monthly_sales['date'].dt.to_timestamp()
monthly_sales.columns = ['Month', 'Total Revenue']

hourly_orders = orders.groupby('hour')['order_id'].nunique().reset_index()
hourly_orders.columns = ['Hour of Day', 'Total Orders']

category_sales = df_sales.groupby('category')['quantity'].sum().reset_index()

# -------------------------------------------------------------------
# 4. SECTION 1 UI: KEY METRICS (KPIs)
# -------------------------------------------------------------------
st.markdown('<div class="header-section"><div class="header-title">🍕 Maven Pizza Performance Dashboard</div><div class="header-subtitle">Section 1: Key Metrics (KPIs) - Executive Summary</div></div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

def create_kpi_card(icon, title, value):
    return f'<div class="metric-card"><div class="metric-icon">{icon}</div><div class="metric-title">{title}</div><div class="metric-value">{value}</div></div>'

with col1: st.markdown(create_kpi_card("💵", "Total Revenue", f"${total_revenue:,.2f}"), unsafe_allow_html=True)
with col2: st.markdown(create_kpi_card("📦", "Total Orders", f"{total_orders:,}"), unsafe_allow_html=True)
with col3: st.markdown(create_kpi_card("🍕", "Total Pizzas Sold", f"{total_pizzas_sold:,}"), unsafe_allow_html=True)
with col4: st.markdown(create_kpi_card("📈", "Average Order Value", f"${avg_order_value:,.2f}"), unsafe_allow_html=True)

# -------------------------------------------------------------------
# 5. SECTION 2 UI: TRENDS & DISTRIBUTIONS
# -------------------------------------------------------------------
st.markdown('<div class="header-section" style="margin-top: 40px; background: linear-gradient(90deg, #1e293b 0%, #334155 100%);"><div class="header-title">📈 Section 2: Trends & Distributions</div><div class="header-subtitle">Analyzing sales patterns over time and product share</div></div>', unsafe_allow_html=True)

col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.markdown('<div class="chart-container"><h4 style="color: #334155; text-align: center;">📅 Monthly Sales Trend</h4>', unsafe_allow_html=True)
    fig_monthly = px.area(monthly_sales, x='Month', y='Total Revenue', color_discrete_sequence=['#0284c7'], markers=True, labels={'Month': 'Order Date (Month)', 'Total Revenue': 'Revenue (USD)'})
    fig_monthly.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=20, r=20, t=20, b=20), hovermode="x unified")
    fig_monthly.update_yaxes(tickprefix="$", gridcolor='#e2e8f0', title_text="Total Monthly Sales ($)")
    fig_monthly.update_xaxes(gridcolor='rgba(0,0,0,0)', title_text="Timeline")
    st.plotly_chart(fig_monthly, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_chart2:
    st.markdown('<div class="chart-container"><h4 style="color: #334155; text-align: center;">⏰ Peak Order Hours</h4>', unsafe_allow_html=True)
    fig_hourly = px.line(hourly_orders, x='Hour of Day', y='Total Orders', color_discrete_sequence=['#f59e0b'], markers=True, labels={'Hour of Day': 'Time of Day (24H)', 'Total Orders': 'Volume of Orders'})
    fig_hourly.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=20, r=20, t=20, b=20), hovermode="x unified")
    fig_hourly.update_xaxes(tickmode='linear', gridcolor='rgba(0,0,0,0)', title_text="Hour of the Day")
    fig_hourly.update_yaxes(gridcolor='#e2e8f0', title_text="Number of Orders")
    st.plotly_chart(fig_hourly, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- THE PIE CHART PIZZA BOX ---
fig_pie = px.pie(category_sales, values='quantity', names='category', labels={'category': 'Pizza Category', 'quantity': 'Pizzas Sold'}, color='category', color_discrete_map={'Classic': '#f5cb5c', 'Veggie': '#2a9d8f', 'Chicken': '#f4a261', 'Supreme': '#e63946'})
fig_pie.update_traces(textposition='inside', textinfo='percent+label', pull=[0.05, 0.05, 0.05, 0.05], marker=dict(line=dict(color='#8B4513', width=6)), hoverinfo='label+percent+value')
fig_pie.update_layout(showlegend=True, legend_title_text='Pizza Types:', legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5), paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=10, b=10, l=10, r=10))

st.markdown('<div class="pizza-box"><div class="pizza-box-badge">100%<br>Fresh</div><div class="pizza-box-title">🍕 Pizza Category Share</div><p style="color: #78350f; margin-bottom: 0;">Breakdown of pizzas sold by category</p></div>', unsafe_allow_html=True)
st.plotly_chart(fig_pie, use_container_width=True)

# -------------------------------------------------------------------
# 6. DATA PROCESSING FOR SECTIONS 3 & 4
# -------------------------------------------------------------------
# Data for Section 3: Comparisons (Top 10 Pizzas by Revenue)
# Group by pizza name and sum the total revenue, then grab the top 10
top_pizzas = df_sales.groupby('name')['total_price'].sum().reset_index()
top_pizzas = top_pizzas.sort_values(by='total_price', ascending=False).head(10)

# Data for Section 4: Distribution of Data (Order Values)
# Group by order_id to find out the total dollar amount spent per individual order
order_values = df_sales.groupby('order_id')['total_price'].sum().reset_index()

# -------------------------------------------------------------------
# 7. SECTIONS 3 & 4 UI: COMPARISONS & DISTRIBUTIONS
# -------------------------------------------------------------------
st.markdown("""
<div class="header-section" style="margin-top: 40px; background: linear-gradient(90deg, #0f172a 0%, #1e293b 100%);">
    <div class="header-title"> Sections 3 & 4: Comparisons and Distributions</div>
    <div class="header-subtitle">Comparing top products and analyzing customer spending behavior</div>
</div>
""", unsafe_allow_html=True)

# Create a 2-column layout for these charts
col_chart3, col_chart4 = st.columns(2)

with col_chart3:
    st.markdown('<div class="chart-container"><h4 style="color: #334155; text-align: center;">🏆 Top 10 Pizzas by Revenue (Comparisons)</h4>', unsafe_allow_html=True)
    
    # Horizontal Bar Chart (Satisfies Section 3)
    fig_bar = px.bar(top_pizzas, 
                     x='total_price', 
                     y='name', 
                     orientation='h', # Horizontal for easier reading of long pizza names
                     color='total_price', # Adds a heat map color scale
                     color_continuous_scale='Blues',
                     labels={'total_price': 'Total Revenue ($)', 'name': 'Pizza Name'})
    
    # Sort the chart so the highest seller is at the top
    fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}, 
                          plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', 
                          margin=dict(l=10, r=20, t=20, b=20),
                          coloraxis_showscale=False) # Hide the color legend to save space
    fig_bar.update_xaxes(tickprefix="$", gridcolor='#e2e8f0')
    
    st.plotly_chart(fig_bar, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_chart4:
    st.markdown('<div class="chart-container"><h4 style="color: #334155; text-align: center;">📈 Customer Spend Distribution</h4>', unsafe_allow_html=True)
    
    # Histogram Chart (Satisfies Section 4)
    fig_hist = px.histogram(order_values, 
                            x='total_price', 
                            nbins=40, # Number of buckets
                            color_discrete_sequence=['#10b981'], # Professional green
                            labels={'total_price': 'Order Value ($)'})
    
    # Customizing layout to show distributions clearly
    fig_hist.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', 
                           margin=dict(l=10, r=20, t=20, b=20),
                           bargap=0.1, # Adds a small gap between histogram bars for better readability
                           hovermode="x unified")
    fig_hist.update_xaxes(tickprefix="$", title_text="Total Amount Spent per Order ($)")
    fig_hist.update_yaxes(gridcolor='#e2e8f0', title_text="Number of Orders")
    
    st.plotly_chart(fig_hist, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------------------------------------------
# 8. DATA PROCESSING FOR SECTIONS 5 & 6 (FIXED)
# -------------------------------------------------------------------

# ----------------------------
# LOW PERFORMANCE PIZZA
# ----------------------------
bottom_pizzas = (
    df_timeline.groupby('name')['total_price']
    .sum()
    .reset_index()
    .sort_values(by='total_price', ascending=True)
)

# FIX: correct row selection
worst_row = bottom_pizzas.iloc[0]

worst_pizza_name = worst_row['name']
worst_pizza_rev = worst_row['total_price']


# ----------------------------
# TOP ORDER OUTLIER
# ----------------------------
order_quantities = (
    df_timeline.groupby('order_id')['quantity']
    .sum()
    .reset_index()
)

max_order_row = order_quantities.sort_values(by='quantity', ascending=False).iloc[0]

max_order_id = max_order_row['order_id']
max_order_qty = max_order_row['quantity']


# -------------------------------------------------------------------
# 9. SECTIONS 5 & 6 UI: ALERTS & INTERACTIVITY
# -------------------------------------------------------------------
st.markdown("""
<div class="header-section" style="margin-top: 40px; background: linear-gradient(90deg, #b91c1c 0%, #ef4444 100%);">
    <div class="header-title">🚨 Section 5: Alerts & Highlights</div>
    <div class="header-subtitle">Identifying outliers, thresholds, and areas needing attention</div>
</div>
""", unsafe_allow_html=True)

col_alert1, col_alert2 = st.columns(2)

with col_alert1:
    st.error(
        f"⚠️ **Low Performance Warning:**\n\n"
        f"The **{worst_pizza_name}** is the worst-selling pizza, generating "
        f"**${worst_pizza_rev:,.2f}** in total revenue. "
        f"Recommendation: consider reviewing pricing or removing it from the menu."
    )

with col_alert2:
    st.info(
        f"💡 **Outlier Highlight:**\n\n"
        f"Order **#{int(max_order_id)}** is a major outlier. "
        f"A single order contained **{int(max_order_qty)} pizzas**. "
        f"Ensure operational readiness for bulk/catering orders."
    )



# -------------------------------------------------------------------
# 7. SECTION 7: FUN INTERACTIVE PIZZA EXPLORER 🍕
# -------------------------------------------------------------------
st.markdown("""
<div class="header-section" style="margin-top: 40px; background: linear-gradient(90deg, #f59e0b 0%, #ef4444 100%);">
    <div class="header-title">🍕 Section 6: Pizza Explorer Playground</div>
    <div class="header-subtitle">Have fun exploring pizzas — compare, filter, and discover insights visually</div>
</div>
""", unsafe_allow_html=True)

# ----------------------------
# PREP DATA (SAFE AGGREGATION)
# ----------------------------
pizza_stats = (
    df_sales.groupby(['name', 'category'])
    .agg(
        total_revenue=('total_price', 'sum'),
        total_quantity=('quantity', 'sum')
    )
    .reset_index()
)

# ----------------------------
# FILTERS (INTERACTIVE)
# ----------------------------
col_a, col_b = st.columns(2)

with col_a:
    category_pick = st.selectbox(
        "🍕 Choose Pizza Category:",
        options=["All"] + sorted(pizza_stats['category'].dropna().unique().tolist())
    )

with col_b:
    sort_metric = st.selectbox(
        "📊 Sort pizzas by:",
        options=["Revenue", "Quantity"]
    )

# ----------------------------
# APPLY FILTERS
# ----------------------------
filtered_pizzas = pizza_stats.copy()

if category_pick != "All":
    filtered_pizzas = filtered_pizzas[filtered_pizzas["category"] == category_pick]

sort_col = "total_revenue" if sort_metric == "Revenue" else "total_quantity"
filtered_pizzas = filtered_pizzas.sort_values(by=sort_col, ascending=False)

top_n = st.slider("🔢 How many pizzas to show?", 5, 20, 10)

filtered_pizzas = filtered_pizzas.head(top_n)

# ----------------------------
# VISUAL 1: BAR CHART (REVENUE / QUANTITY)
# ----------------------------
fig_fun_bar = px.bar(
    filtered_pizzas,
    x="name",
    y=sort_col,
    color="category",
    text=sort_col,
    title="🍕 Pizza Performance Explorer",
    labels={
        "name": "Pizza Name",
        sort_col: "Value"
    }
)

fig_fun_bar.update_traces(textposition="outside")

fig_fun_bar.update_layout(
    xaxis_tickangle=-45,
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=20, r=20, t=60, b=120),
    showlegend=True
)

st.plotly_chart(fig_fun_bar, use_container_width=True)


# -------------------------------------------------------------------
# 10. AUTOMATED CALCULATIONS FOR INSIGHTS (FIXED)
# -------------------------------------------------------------------

# Peak hour (highest number of orders)
peak_row = hourly_orders.sort_values(by='Total Orders', ascending=False).iloc[0]
peak_hour = int(peak_row['Hour of Day'])

# Best-selling pizza (by revenue)
top_pizza_row = top_pizzas.sort_values(by='total_price', ascending=False).iloc[0]
top_pizza_name = top_pizza_row['name']

# -------------------------------------------------------------------
# 10. AUTOMATED CALCULATIONS FOR INSIGHTS (FIXED)
# -------------------------------------------------------------------

# Peak hour (hour with highest number of orders)
peak_row = hourly_orders.sort_values(by='Total Orders', ascending=False).iloc[0]
peak_hour = int(peak_row['Hour of Day'])

# Best-selling pizza (by revenue)
top_pizza_row = top_pizzas.sort_values(by='total_price', ascending=False).iloc[0]
top_pizza_name = top_pizza_row['name']


# ==========================================
# SECTIONS 7, 8, & 9 UI: INSIGHTS, ETHICS, METADATA
# ==========================================
st.markdown("---")

# ==========================================
# 8. SUMMARY & BUSINESS INSIGHTS SECTION
# ==========================================
st.header("💡 Section 7: Summary & Business Insights")

# ---------------------------
# SAFE DATA SOURCE (FIXED)
# ---------------------------
filtered_df = df_timeline.copy()

# ---------------------------
# 1. CATEGORY PERFORMANCE
# ---------------------------
category_revenue = df_sales.groupby('category')['total_price'].sum().reset_index()

if not category_revenue.empty:
    top_cat_row = category_revenue.sort_values(by='total_price', ascending=False).iloc[0]
    top_category = top_cat_row['category']
    top_cat_revenue = top_cat_row['total_price']
    total_rev = category_revenue['total_price'].sum()
    top_cat_pct = (top_cat_revenue / total_rev) * 100
else:
    top_category, top_cat_revenue, top_cat_pct = "N/A", 0, 0


# ---------------------------
# 2. TOP PRODUCT
# ---------------------------
item_sales = df_sales.groupby('name')['quantity'].sum().reset_index(name='qty')

if not item_sales.empty:
    top_item_row = item_sales.sort_values(by='qty', ascending=False).iloc[0]
    top_item = top_item_row['name']
    top_item_qty = top_item_row['qty']
else:
    top_item, top_item_qty = "N/A", 0


# ---------------------------
# 3. PEAK HOUR ANALYSIS (FIXED)
# ---------------------------
busiest_hour_df = hourly_orders.copy()

if not busiest_hour_df.empty:
    peak_row = busiest_hour_df.sort_values(by='Total Orders', ascending=False).iloc[0]
    peak_hour_num = int(peak_row['Hour of Day'])
    peak_hour_str = f"{peak_hour_num % 12 or 12}:00 {'AM' if peak_hour_num < 12 else 'PM'}"
    peak_hour_orders = peak_row['Total Orders']
else:
    peak_hour_str, peak_hour_orders = "N/A", 0


# ==========================================
# 8.1 KEY FINDINGS
# ==========================================
st.subheader("7.1 Key Findings")

col_kf1, col_kf2 = st.columns(2)

with col_kf1:
    st.info(f"🏆 Revenue Leader: **{top_category}** generated **${top_cat_revenue:,.2f}** ({top_cat_pct:.1f}%)")
    st.info(f"🍕 Top Product: **{top_item}** sold **{top_item_qty} units**")

with col_kf2:
    st.info(f"⏰ Peak Hour: **{peak_hour_str}** with **{peak_hour_orders} orders**")


# ==========================================
# 8.2 BUSINESS RECOMMENDATIONS (DATA DRIVEN)
# ==========================================
st.subheader("8.2 Data-Driven Recommendations")

st.success(f"""
1. **Inventory Strategy:** Focus on **{top_item}**, the highest-demand product with {top_item_qty} units sold.
2. **Revenue Optimization:** Prioritize **{top_category}** category which contributes {top_cat_pct:.1f}% of total revenue.
3. **Operational Efficiency:** Scale staffing during **{peak_hour_str}** to handle peak demand smoothly.
""")


# ==========================================
# 7. ETHICS SECTION
# ==========================================
st.header("🛡️ Section 8: Ethics, Privacy & Data Integrity")

with st.expander("View Ethics Analysis", expanded=True):
    st.markdown("""
    **Privacy & PII Handling:**  
    The dataset contains no personally identifiable information. All records are anonymized transactional logs.

    **Bias Consideration:**  
    The dataset reflects only consumer behavior at a single business and cannot be generalized to broader populations.

    **Data Integrity:**  
    Transactional joins are preserved using relational keys (`order_id`, `pizza_id`) ensuring accurate revenue attribution.
    """)


# ==========================================
# 9. METADATA SECTION
# ==========================================
st.header("📄 Section 9: Dataset Metadata")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    * Dataset: Maven Pizza Sales
    * Type: Relational CSV Dataset
    * Source: Maven Analytics
    """)

with col2:
    st.markdown("""
    * Year: 2015 Snapshot
    * Purpose: Educational Analytics
    * Link: https://www.mavenanalytics.io/data-playground
    """)
