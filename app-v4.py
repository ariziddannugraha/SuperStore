import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Global Superstore - Revival Strategy",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS STYLING ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Header Container */
    .header-container {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
        padding: 28px 32px;
        border-radius: 12px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .header-title {
        font-size: 2.1rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .header-subtitle {
        font-size: 1.05rem;
        font-weight: 400;
        opacity: 0.9;
        margin-top: 6px;
    }

    /* KPI Cards */
    .kpi-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 18px 20px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
        transition: transform 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.08);
    }
    .kpi-label {
        font-size: 0.85rem;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 6px;
    }
    .kpi-value {
        font-size: 1.85rem;
        color: #0f172a;
        font-weight: 700;
        margin: 0;
    }

    /* Narrative Box */
    .narrative-box {
        background-color: #f8fafc;
        border-left: 4px solid #2563eb;
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 20px;
        color: #334155;
        font-size: 0.95rem;
        line-height: 1.55;
    }
    .narrative-box strong {
        color: #0f172a;
    }

    /* Key Finding Highlight */
    .finding-box {
        background-color: #fef2f2;
        border-left: 4px solid #ef4444;
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 20px;
        color: #7f1d1d;
        font-size: 0.95rem;
        line-height: 1.55;
    }

    /* Strategy Table */
    .action-plan {
        width: 100%;
        border-collapse: collapse;
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        overflow: hidden;
    }
    .action-plan th,
    .action-plan td {
        padding: 16px;
        border-bottom: 1px solid #e2e8f0;
        text-align: left;
        vertical-align: top;
        color: #334155;
        line-height: 1.5;
    }
    .action-plan th {
        background-color: #eff6ff;
        color: #1e3a8a;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.4px;
    }
    .action-plan tr:last-child td {
        border-bottom: 0;
    }
</style>
""", unsafe_allow_html=True)

# --- TITLE HEADER ---
st.markdown("""
<div class="header-container">
    <p class="header-title">Global Superstore Analytics</p>
    <p class="header-subtitle">Diagnostic Audit Report & Profitability Recovery Strategy (2011 - 2014)</p>
</div>
""", unsafe_allow_html=True)

# --- DATA LOADING & PREPROCESSING ---
@st.cache_data
def load_data(file_source=None):
    if file_source is not None:
        if file_source.name.endswith('.csv'):
            df = pd.read_csv(file_source, encoding='latin1')
        else:
            df = pd.read_excel(file_source)
    else:
        gdrive_url = 'https://drive.google.com/file/d/1sdtcwBx4Skbh3C4hO7g29hY5v8uihpPo/view?usp=drive_link'
        download_url = 'https://drive.google.com/uc?id=' + gdrive_url.split('/')[-2]

        try:
            df = pd.read_csv(download_url, encoding='latin1')
        except Exception:
            return None
    
    df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True, errors='coerce')
    df['Ship Date'] = pd.to_datetime(df['Ship Date'], dayfirst=True, errors='coerce')
    
    df['Profit Margin'] = df['Profit'] / df['Sales']
    df['Year'] = df['Order Date'].dt.year
    df['Quarter'] = df['Order Date'].dt.to_period('Q').astype(str)
    df['Year-Month'] = df['Order Date'].dt.to_period('M').astype(str)
    df['Shipping_Ratio'] = df['Shipping Cost'] / df['Sales']
    
    # Custom Discount Clusters based on Audit Report
    bins = [-0.001, 0.10, 0.20, 0.30, 0.50, 0.80, 1.0]
    labels = ['0%-10%', '10%-20%', '20%-30%', '30%-50%', '50%-80%', '>80%']
    df['Discount_Range'] = pd.cut(df['Discount'], bins=bins, labels=labels)
    
    return df

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3075/3075977.png", width=55)
    st.markdown("### Data Source")
    uploaded_file = st.file_uploader("Upload CSV / Excel Dataset", type=['csv', 'xlsx'])
    
    df_raw = load_data(uploaded_file)
    if df_raw is None:
        st.warning("Please upload the Global Superstore dataset to initialize analysis.")
        st.stop()

    st.markdown("### Executive Filters")
    all_markets = ["All Markets"] + sorted(list(df_raw['Market'].dropna().unique()))
    selected_market = st.selectbox("Market Region", all_markets)

    all_years = ["All Years"] + sorted(list(df_raw['Year'].dropna().unique().astype(int)))
    selected_year = st.selectbox("Fiscal Year", all_years)

    all_segments = ["All Segments"] + sorted(list(df_raw['Segment'].dropna().unique()))
    selected_segment = st.selectbox("Customer Segment", all_segments)

# Apply Filters
df = df_raw.copy()
if selected_market != "All Markets":
    df = df[df['Market'] == selected_market]
if selected_year != "All Years":
    df = df[df['Year'] == int(selected_year)]
if selected_segment != "All Segments":
    df = df[df['Segment'] == selected_segment]

# --- KPI METRICS ---
total_sales = df['Sales'].sum()
total_profit = df['Profit'].sum()
overall_margin = (total_profit / total_sales * 100) if total_sales > 0 else 0
total_orders = df['Order ID'].nunique()

col1, col2, col3, col4 = st.columns(4)

col1.markdown(f"""
<div class="kpi-card">
    <div class="kpi-label">💰 Total Revenue</div>
    <div class="kpi-value">${total_sales:,.0f}</div>
</div>
""", unsafe_allow_html=True)

col2.markdown(f"""
<div class="kpi-card">
    <div class="kpi-label">📈 Net Profit</div>
    <div class="kpi-value">${total_profit:,.0f}</div>
</div>
""", unsafe_allow_html=True)

col3.markdown(f"""
<div class="kpi-card">
    <div class="kpi-label">📊 Overall Margin</div>
    <div class="kpi-value" style="color: {'#10b981' if overall_margin > 0 else '#ef4444'};">{overall_margin:.2f}%</div>
</div>
""", unsafe_allow_html=True)

col4.markdown(f"""
<div class="kpi-card">
    <div class="kpi-label">📦 Unique Orders</div>
    <div class="kpi-value">{total_orders:,}</div>
</div>
""", unsafe_allow_html=True)

st.write("") # Spacer

# --- GLOBAL PLOTLY CONFIG ---
layout_config = dict(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    margin=dict(l=20, r=20, t=50, b=20),
    title_font=dict(family="Inter", size=17, color="#0f172a"),
    font=dict(family="Inter", color="#475569")
)

# --- TABS ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Overall Performance", 
    "🎯 Problem Areas", 
    "🔍 Root Cause Analysis", 
    "🚀 Revival Strategy",
])

# ==========================================
# TAB 1: OVERALL PERFORMANCE
# ==========================================
with tab1:
    st.markdown("""
    <div class="narrative-box">
        <strong>Executive Summary: The Volume-Margin Trap</strong><br>
        Global Superstore has consistently generated strong top-line sales growth, expanding revenue from <strong>$2.26M in 2011 to $4.30M in 2014</strong>. However, net profit margins stagnated and dropped to a low of <strong>9.0% in 2013</strong> before slightly recovering. This disparity between top-line expansion and bottom-line erosion confirms that the business is suffering from a systemic <em>margin inefficiency</em> rather than a demand problem.
    </div>
    """, unsafe_allow_html=True)

    col_t1_left, col_t1_right = st.columns(2, gap="large")
    
    with col_t1_left:
        yearly_df = df.groupby('Year').agg({'Sales': 'sum', 'Profit': 'sum'}).reset_index()
        yearly_df['Profit Margin (%)'] = (yearly_df['Profit'] / yearly_df['Sales']) * 100
        
        fig_yearly = go.Figure()
        fig_yearly.add_trace(go.Bar(x=yearly_df['Year'], y=yearly_df['Sales'], name='Sales ($)', marker_color='#3b82f6'))
        fig_yearly.add_trace(go.Bar(x=yearly_df['Year'], y=yearly_df['Profit'], name='Profit ($)', marker_color='#10b981'))
        fig_yearly.update_layout(**layout_config, title="Annual Revenue vs Net Profit Growth", barmode='group', height=380)
        fig_yearly.update_yaxes(gridcolor='#f1f5f9')
        st.plotly_chart(fig_yearly, use_container_width=True)
        st.caption("📌 **Takeaway:** Revenue grew steadily every year, but profit growth failed to keep pace due to expanding operational costs and discounts.")
        
    with col_t1_right:
        fig_margin = px.line(yearly_df, x='Year', y='Profit Margin (%)', markers=True, 
                             title="Net Profit Margin Trend (%)", color_discrete_sequence=['#8b5cf6'])
        fig_margin.update_layout(**layout_config, height=380)
        fig_margin.update_yaxes(gridcolor='#f1f5f9')
        fig_margin.update_traces(line=dict(width=3), marker=dict(size=8))
        st.plotly_chart(fig_margin, use_container_width=True)
        st.caption("📌 **Takeaway:** Notice the dip in margin in 2012-2013. Unchecked promotional discounts directly pulled down profitability.")

    st.markdown("#### Monthly Revenue & Profit Trajectory")
    monthly_df = df.groupby('Year-Month').agg({'Sales': 'sum', 'Profit': 'sum'}).reset_index()
    fig_monthly = px.area(monthly_df, x='Year-Month', y=['Sales', 'Profit'], 
                          title="Monthly Performance Dynamics (2011 - 2014)",
                          color_discrete_map={'Sales': '#eff6ff', 'Profit': '#d1fae5'})
    
    fig_monthly.add_trace(go.Scatter(x=monthly_df['Year-Month'], y=monthly_df['Sales'], mode='lines', line=dict(color='#2563eb', width=2), showlegend=False))
    fig_monthly.add_trace(go.Scatter(x=monthly_df['Year-Month'], y=monthly_df['Profit'], mode='lines', line=dict(color='#059669', width=2), showlegend=False))
    
    fig_monthly.update_layout(**layout_config, height=380, xaxis_title="", yaxis_title="USD ($)")
    fig_monthly.update_yaxes(gridcolor='#f1f5f9')
    st.plotly_chart(fig_monthly, use_container_width=True)
    st.caption("📌 **Takeaway:** Strong Q4 seasonality boosts total sales every December, but profit spikes are proportionally narrower due to end-of-year discounting.")

# ==========================================
# TAB 2: PROBLEM AREAS
# ==========================================
with tab2:
    st.markdown("""
    <div class="narrative-box">
        <strong>Diagnostic Overview: Where is Profit Bleeding?</strong><br>
        Financial losses are <em>not company-wide</em>; they are concentrated in specific product sub-categories and high-cost export regions. 
        <strong>Tables</strong> and <strong>Bookcases</strong> generate severe net operational losses (Tables alone lost over -$64,000 globally), driven by high shipping freight for heavy goods in regions like LATAM, EMEA, and US markets with heavy discount rates.
    </div>
    """, unsafe_allow_html=True)
    
    col_t2_1, col_t2_2 = st.columns(2, gap="large")
    
    with col_t2_1:
        country_df = df.groupby(['Market', 'Country']).agg({'Profit': 'sum'}).reset_index()
        top_loss_country = country_df.sort_values(by='Profit', ascending=True).head(10)
        
        fig_loss_country = px.bar(
            top_loss_country, x='Profit', y='Country', color='Market', orientation='h',
            title="Top 10 Loss-Generating Countries",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_loss_country.update_layout(**layout_config, height=380)
        fig_loss_country.update_xaxes(gridcolor='#f1f5f9')
        st.plotly_chart(fig_loss_country, use_container_width=True)
        st.caption("📌 **Takeaway:** Targeted markets (e.g., Turkey, Netherlands, Nigeria, Honduras) suffer severe profit drain due to unfavorable pricing tariffs and shipping expenses.")
        
    with col_t2_2:
        subcat_df = df.groupby('Sub-Category').agg({'Profit': 'sum'}).reset_index()
        subcat_df['Status'] = np.where(subcat_df['Profit'] >= 0, 'Profitable', 'Loss-Making')
        subcat_df = subcat_df.sort_values(by='Profit', ascending=True)
        
        fig_subcat = px.bar(
            subcat_df, x='Profit', y='Sub-Category', color='Status', orientation='h',
            title="Sub-Category Net Profit / Loss Profile",
            color_discrete_map={'Profitable': '#10b981', 'Loss-Making': '#ef4444'}
        )
        fig_subcat.update_layout(**layout_config, height=380)
        fig_subcat.update_xaxes(gridcolor='#f1f5f9')
        st.plotly_chart(fig_subcat, use_container_width=True)
        st.caption("📌 **Takeaway:** High-performing tech items (Copiers, Phones, Accessories) subsidize heavy furniture losses (Tables, Bookcases, Supplies).")

    st.markdown("#### Geographic & Product Category Heatmap")
    pivot_matrix = df.pivot_table(index='Sub-Category', columns='Market', values='Profit', aggfunc='sum').fillna(0)
    fig_heatmap = px.imshow(
        pivot_matrix, 
        labels=dict(x="Market Region", y="Product Sub-Category", color="Net Profit ($)"),
        x=pivot_matrix.columns,
        y=pivot_matrix.index,
        color_continuous_scale="RdYlGn",
        aspect="auto"
    )
    fig_heatmap.update_layout(**layout_config, height=480)
    fig_heatmap.update_layout(margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig_heatmap, use_container_width=True)
    st.caption("📌 **Takeaway:** Dark red cells identify severe localized loss centers (e.g., Furniture Tables across US, EMEA, and LATAM).")

# ==========================================
# TAB 3: ROOT CAUSE ANALYSIS
# ==========================================
with tab3:
    st.markdown("""
    <div class="finding-box">
        <strong>Root Cause Findings: Aggressive Discounting & Customer Segment Profiling</strong><br>
        1. <strong>The 20% Tipping Point:</strong> Giving discounts above 20% completely destroys gross margin. Transactions with 0%-20% discount yield +$24 to +$38 average profit per order, whereas discounts from 30%-80% trigger catastrophic net losses (-$48 to -$115 per order).<br>
        2. <strong>B2B Corporate Value:</strong> The <strong>Corporate segment</strong> generates the highest Average Order Value ($342.50) and healthiest profit margin (12.4%), significantly outperforming the Consumer and Home Office segments.
    </div>
    """, unsafe_allow_html=True)
    
    col_t3_1, col_t3_2 = st.columns(2, gap="large")
    
    with col_t3_1:
        # Discount Range Analysis
        discount_impact = df.groupby('Discount_Range', observed=False).agg({
            'Order ID': 'count',
            'Sales': 'sum',
            'Profit': 'sum',
            'Profit Margin': 'mean'
        }).rename(columns={'Order ID': 'Total Orders'}).reset_index()

        discount_impact['Profit Margin (%)'] = discount_impact['Profit Margin'] * 100
        
        fig_disc = px.bar(
            discount_impact,
            x='Discount_Range',
            y='Profit',
            title='Net Profit by Discount Tier (Breakeven Analysis)',
            color='Profit',
            color_continuous_scale='RdYlGn',
            custom_data=['Total Orders', 'Sales', 'Profit Margin (%)']
        )
        fig_disc.add_hline(y=0, line_dash='dash', line_color='black')
        fig_disc.update_traces(
            hovertemplate=(
                '<b>%{x} Discount Tier</b><br>'
                'Net Profit: $%{y:,.0f}<br>'
                'Total Revenue: $%{customdata[1]:,.0f}<br>'
                'Orders Count: %{customdata[0]:,.0f}<br>'
                'Avg Margin: %{customdata[2]:.2f}%<extra></extra>'
            )
        )
        fig_disc.update_layout(**layout_config, height=400, xaxis_title='Discount Range Cluster', yaxis_title='Total Net Profit ($)')
        st.plotly_chart(fig_disc, use_container_width=True)
        st.caption("📌 **Takeaway:** Hard-capping discounts at a maximum of 20% will immediately halt financial bleeding without hurting volume sales.")

    with col_t3_2:
        # Market Segment Profile: AOV vs Profit Margin
        segment_profile = df.groupby('Segment').agg({
            'Sales': 'sum',
            'Profit': 'sum',
            'Order ID': 'nunique'
        }).reset_index()
        segment_profile['AOV'] = segment_profile['Sales'] / segment_profile['Order ID']
        segment_profile['Margin (%)'] = (segment_profile['Profit'] / segment_profile['Sales']) * 100

        fig_seg = go.Figure()
        fig_seg.add_trace(go.Bar(x=segment_profile['Segment'], y=segment_profile['AOV'], name='Average Order Value ($)', marker_color='#1e3a8a'))
        fig_seg.add_trace(go.Bar(x=segment_profile['Segment'], y=segment_profile['Margin (%)'], name='Profit Margin (%)', marker_color='#38bdf8'))
        fig_seg.update_layout(**layout_config, title="Customer Segment Profile: AOV ($) vs Margin (%)", barmode='group', height=400)
        st.plotly_chart(fig_seg, use_container_width=True)
        st.caption("📌 **Takeaway:** B2B Corporate buyers make larger bulk purchases with higher margins and lower discount sensitivity.")

    st.markdown("#### Summary Analysis of Discount Clusters")
    
    # Table breakdown for clearer reading
    disc_summary = df.groupby('Discount_Range', observed=False).agg(
        Total_Orders=('Order ID', 'count'),
        Total_Sales=('Sales', 'sum'),
        Total_Profit=('Profit', 'sum'),
        Avg_Profit_Per_Order=('Profit', 'mean')
    ).reset_index()
    
    disc_summary['Profit Margin %'] = (disc_summary['Total_Profit'] / disc_summary['Total_Sales']) * 100
    disc_summary['Status'] = disc_summary['Total_Profit'].apply(lambda x: '🟢 Profitable' if x > 0 else '🔴 Severe Loss')
    
    st.dataframe(
        disc_summary.style.format({
            'Total_Sales': '${:,.2f}',
            'Total_Profit': '${:,.2f}',
            'Avg_Profit_Per_Order': '${:,.2f}',
            'Profit Margin %': '{:.2f}%',
            'Total_Orders': '{:,}'
        }),
        use_container_width=True
    )

# ==========================================
# TAB 4: REVIVAL STRATEGY
# ==========================================
with tab4:
    st.markdown("""
    <div class="narrative-box">
        <strong>Strategic Roadmap: Profitability Recovery Plan (0 - 12 Months)</strong><br>
        To restore net profit by <strong>+$1.2M to +$1.8M</strong> over the next 12 months, management will execute four cross-functional intervention pillars. This plan requires no downsizing, relying instead on operational control, strategic bundling, and disciplined pricing rules.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### 1. Cross-Category Product Bundling Strategy")
    st.markdown("""
    * **Program Name:** Executive Office Bundle
    * **Bundling Mechanism:** Pair 1 low-margin/loss unit (e.g., Table or Bookcase) with 2-3 high-margin Technology/Office Supply items (e.g., Copiers, Phones, Accessories).
    * **Pricing Rule:** Maximum allowable bundle discount set at **10%-12% off total retail price**. Standalone discounted sales of Tables prohibited.
    * **Financial Target:** Secure a minimum combined transaction profit margin of **18% - 20%**.
    """)

    st.write("")
    st.markdown("#### 2. Strategy Execution Matrix & Measurable KPIs")

    st.markdown("""
    <table class="action-plan">
        <thead>
            <tr>
                <th>Strategic Initiative</th>
                <th>Owner & Timeline</th>
                <th>Measurable KPI & Threshold</th>
                <th>Expected Financial Impact</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><b>1. Automated Discount Capping</b><br>Systematic ERP hard-lock preventing discounts above 20%. Any exception requires C-Level authorization.</td>
                <td>CCO & Regional Sales Director<br><i>(Months 0-3)</i></td>
                <td>• Hard Cap: Max 20% discount<br>• Zero unauthorized discounts >20%</td>
                <td>Instantly stops profit bleeding; increases average order profit by +$35.</td>
            </tr>
            <tr>
                <td><b>2. Executive Office Bundling Program</b><br>Mandate cross-category bundling for Tables & Bookcases with high-margin Tech accessories.</td>
                <td>VP Merchandising & Product Mgmt<br><i>(Months 3-6)</i></td>
                <td>• Bundled sales ≥ 40% Furniture inventory<br>• Combined order margin ≥ 18%</td>
                <td>Transforms Tables sub-category from -$64K loss to breakeven / profit.</td>
            </tr>
            <tr>
                <td><b>3. B2B Corporate Prioritization</b><br>Re-allocate 65% of marketing budget toward B2B corporate client acquisition and annual contracts.</td>
                <td>Head of Global Marketing & Enterprise Sales<br><i>(Months 3-9)</i></td>
                <td>• Corporate revenue contribution > 45%<br>• B2B Client Retention Rate ≥ 80%</td>
                <td>Lifts Average Order Value (AOV) from $284 to $350+.</td>
            </tr>
            <tr>
                <td><b>4. Heavy Goods Logistics Optimization</b><br>Base shipping fee adjustments and carrier renegotiation on EMEA & LATAM export routes.</td>
                <td>VP Supply Chain & Logistics<br><i>(Months 6-12)</i></td>
                <td>• Shipping Fee / Sales ratio ≤ 8%<br>• Freight route consolidation -15%</td>
                <td>Recovers 8%-12% gross margin on heavy goods in export markets.</td>
            </tr>
        </tbody>
    </table>
    """, unsafe_allow_html=True)