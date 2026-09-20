import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Global Superstore - Investor & Revival Dashboard v3",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS STYLING ---
st.markdown("""
<style>
    .main-title {
        font-size: 2.3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #1E3A8A, #2563EB);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #4B5563;
        margin-bottom: 20px;
    }
    .investor-card {
        background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 100%);
        color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.2);
        margin-bottom: 15px;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        padding: 16px;
        border-radius: 10px;
        border-left: 5px solid #2563EB;
    }
    .kpi-title {
        font-size: 0.9rem;
        color: #64748B;
        font-weight: 600;
        text-transform: uppercase;
    }
    .kpi-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0F172A;
    }
    .live-banner {
        background-color: #EFF6FF;
        border: 2px solid #3B82F6;
        padding: 15px;
        border-radius: 10px;
        color: #1E3A8A;
        font-weight: 600;
        font-size: 1.1rem;
        text-align: center;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# --- TITLE HEADER ---
st.markdown('<p class="main-title">Global Superstore: Revival & Investor Forecast Dashboard (v3)</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Interactive Analytics with Dynamic Live-Updating Scenario Simulator & Profit Forecast</p>', unsafe_allow_html=True)

# --- DATA LOADER / GENERATOR ---
@st.cache_data
def load_and_preprocess(file_source=None):
    if file_source is not None:
        try:
            if file_source.name.endswith('.csv'):
                df = pd.read_csv(file_source, encoding='latin1')
            else:
                df = pd.read_excel(file_source)
            df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True, errors='coerce')
            df['Ship Date'] = pd.to_datetime(df['Ship Date'], dayfirst=True, errors='coerce')
        except Exception as e:
            st.error(f"Error membaca file: {e}")
            return None
    else:
        try:
            df = pd.read_csv('Global_Superstore2.csv', encoding='latin1')
            df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True, errors='coerce')
            df['Ship Date'] = pd.to_datetime(df['Ship Date'], dayfirst=True, errors='coerce')
        except:
            dates = pd.date_range(start='2011-01-01', end='2014-12-31', freq='D')
            np.random.seed(42)
            markets = ['APAC', 'US', 'EU', 'LATAM', 'EMEA', 'Africa', 'Canada']
            categories = ['Technology', 'Furniture', 'Office Supplies']
            subcats = ['Phones', 'Chairs', 'Tables', 'Binders', 'Accessories', 'Copiers', 'Appliances']
            
            data = []
            for d in dates:
                if np.random.rand() > 0.3:
                    num_orders = np.random.randint(15, 45)
                    for _ in range(num_orders):
                        m = np.random.choice(markets, p=[0.3, 0.25, 0.2, 0.12, 0.08, 0.05])
                        cat = np.random.choice(categories, p=[0.3, 0.3, 0.4])
                        subcat = np.random.choice(subcats)
                        sales = round(np.random.exponential(scale=200) + 20, 2)
                        disc = np.random.choice([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.7], p=[0.5, 0.2, 0.1, 0.08, 0.06, 0.04, 0.02])
                        base_margin = 0.25 if cat == 'Technology' else (0.15 if cat == 'Office Supplies' else -0.05)
                        profit = sales * (base_margin - disc * 0.8) + np.random.normal(0, 10)
                        ship_cost = sales * np.random.uniform(0.05, 0.25)
                        
                        data.append({
                            'Order Date': d,
                            'Ship Date': d + pd.Timedelta(days=np.random.randint(1, 5)),
                            'Market': m,
                            'Category': cat,
                            'Sub-Category': subcat,
                            'Country': 'United States' if m == 'US' else ('Australia' if m == 'APAC' else 'Germany'),
                            'Segment': np.random.choice(['Consumer', 'Corporate', 'Home Office']),
                            'Sales': max(sales, 5.0),
                            'Quantity': np.random.randint(1, 10),
                            'Discount': disc,
                            'Profit': profit,
                            'Shipping Cost': ship_cost,
                            'Order ID': f"ORD-{d.year}-{np.random.randint(10000, 99999)}"
                        })
            df = pd.DataFrame(data)

    df['Profit Margin'] = df['Profit'] / df['Sales']
    df['Year'] = df['Order Date'].dt.year
    df['Quarter'] = df['Order Date'].dt.to_period('Q').astype(str)
    df['Year-Month'] = df['Order Date'].dt.to_period('M')
    df['Shipping_Ratio'] = df['Shipping Cost'] / df['Sales']
    
    bins = [-0.01, 0, 0.1, 0.2, 0.3, 0.4, 0.5, 1.0]
    labels = ['0%', '1-10%', '11-20%', '21-30%', '31-40%', '41-50%', '>50%']
    df['Discount_Range'] = pd.cut(df['Discount'], bins=bins, labels=labels)
    
    return df

# --- SIDEBAR CONTROLS ---
st.sidebar.header("📁 Data & Filter Control")
uploaded_file = st.sidebar.file_uploader("Unggah File Data (.csv / .xlsx)", type=['csv', 'xlsx'], key="uploader_main")

df_raw = load_and_preprocess(uploaded_file)

all_markets = ["All Markets"] + sorted(list(df_raw['Market'].dropna().unique()))
selected_market = st.sidebar.selectbox("Filter Market", all_markets, key="sb_market")

all_years = ["All Years"] + sorted(list(df_raw['Year'].dropna().unique().astype(int)))
selected_year = st.sidebar.selectbox("Filter Tahun (Historical View)", all_years, key="sb_year")

all_segments = ["All Segments"] + sorted(list(df_raw['Segment'].dropna().unique()))
selected_segment = st.sidebar.selectbox("Filter Customer Segment", all_segments, key="sb_segment")

# Apply Filters for Historical Views
df = df_raw.copy()
if selected_market != "All Markets":
    df = df[df['Market'] == selected_market]
if selected_segment != "All Segments":
    df = df[df['Segment'] == selected_segment]

df_hist_view = df.copy()
if selected_year != "All Years":
    df_hist_view = df_hist_view[df_hist_view['Year'] == int(selected_year)]

# --- TOP KPI METRICS ---
tot_sales = df_hist_view['Sales'].sum()
tot_profit = df_hist_view['Profit'].sum()
margin_pct = (tot_profit / tot_sales * 100) if tot_sales > 0 else 0
tot_orders = df_hist_view['Order ID'].nunique()

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="metric-card"><div class="kpi-title">Total Sales</div><div class="kpi-value">${tot_sales:,.0f}</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-card"><div class="kpi-title">Total Profit</div><div class="kpi-value">${tot_profit:,.0f}</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="metric-card"><div class="kpi-title">Profit Margin</div><div class="kpi-value">{margin_pct:.2f}%</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="metric-card"><div class="kpi-title">Total Transactions</div><div class="kpi-value">{tot_orders:,}</div></div>', unsafe_allow_html=True)

st.divider()

# --- MAIN TABS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Historical Trends (Task 1)",
    "🎯 Problem Areas (Task 2)",
    "🔍 Root Causes (Task 3)",
    "💡 Investor Simulator & Forecast (LIVE)",
    "🚀 Revival Strategy (Task 4 & 5)"
])

# ==========================================
# TAB 1: HISTORICAL TRENDS
# ==========================================
with tab1:
    st.subheader("Performa Penjualan & Profitabilitas Historis (2011–2014)")
    
    monthly_agg = df_hist_view.groupby('Year-Month').agg({'Sales': 'sum', 'Profit': 'sum'}).reset_index()
    monthly_agg['Year-Month-Str'] = monthly_agg['Year-Month'].astype(str)
    
    fig_hist = go.Figure()
    fig_hist.add_trace(go.Scatter(
        x=monthly_agg['Year-Month-Str'], y=monthly_agg['Sales'],
        name='Sales ($)', mode='lines+markers', line=dict(color='#2563EB', width=3),
        fill='tozeroy', fillcolor='rgba(37, 99, 235, 0.1)'
    ))
    fig_hist.add_trace(go.Scatter(
        x=monthly_agg['Year-Month-Str'], y=monthly_agg['Profit'],
        name='Profit ($)', mode='lines+markers', line=dict(color='#10B981', width=3),
        fill='tozeroy', fillcolor='rgba(16, 185, 129, 0.15)'
    ))
    fig_hist.update_layout(
        title="Tren Bulanan Sales & Profit",
        xaxis_title="Tahun-Bulan", yaxis_title="Nilai ($)",
        hovermode="x unified", height=450, legend=dict(orientation="h", y=1.1)
    )
    st.plotly_chart(fig_hist, use_container_width=True, key="chart_hist_trends")
    
    yearly_df = df.groupby('Year').agg({'Sales': 'sum', 'Profit': 'sum'}).reset_index()
    yearly_df['Profit Margin (%)'] = (yearly_df['Profit'] / yearly_df['Sales']) * 100
    yearly_df['Sales YoY Growth (%)'] = yearly_df['Sales'].pct_change() * 100
    yearly_df['Profit YoY Growth (%)'] = yearly_df['Profit'].pct_change() * 100
    
    st.write("#### Ringkasan Tahunan & YoY Growth")
    st.dataframe(yearly_df.style.format({
        'Sales': '${:,.2f}', 'Profit': '${:,.2f}',
        'Profit Margin (%)': '{:.2f}%', 'Sales YoY Growth (%)': '{:.2f}%',
        'Profit YoY Growth (%)': '{:.2f}%'
    }), use_container_width=True)

# ==========================================
# TAB 2: PROBLEM AREAS
# ==========================================
with tab2:
    st.subheader("Identifikasi Wilayah & Produk Pembuat Rugi")
    col_l, col_r = st.columns(2)
    with col_l:
        country_agg = df_hist_view.groupby(['Market', 'Country']).agg({'Sales': 'sum', 'Profit': 'sum'}).reset_index()
        top_loss = country_agg.sort_values(by='Profit', ascending=True).head(10)
        
        fig_country = px.bar(
            top_loss, x='Profit', y='Country', color='Market', orientation='h',
            title="10 Negara dengan Kerugian Terbesar ($)",
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig_country.update_layout(height=400, yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig_country, use_container_width=True, key="chart_problem_countries")
        
    with col_r:
        subcat_agg = df_hist_view.groupby('Sub-Category').agg({'Sales': 'sum', 'Profit': 'sum'}).reset_index()
        subcat_agg['Status'] = np.where(subcat_agg['Profit'] >= 0, 'Untung', 'Rugi')
        subcat_agg = subcat_agg.sort_values(by='Profit', ascending=True)
        
        fig_subcat = px.bar(
            subcat_agg, x='Profit', y='Sub-Category', color='Status', orientation='h',
            title="Profit / Rugi per Sub-Kategori Produk",
            color_discrete_map={'Untung': '#10B981', 'Rugi': '#EF4444'}
        )
        fig_subcat.update_layout(height=400)
        st.plotly_chart(fig_subcat, use_container_width=True, key="chart_problem_subcats")

# ==========================================
# TAB 3: ROOT CAUSES
# ==========================================
with tab3:
    st.subheader("Analisis Akar Masalah: Diskon & Biaya Pengiriman")
    c_disc, c_ship = st.columns(2)
    with c_disc:
        disc_agg = df_hist_view.groupby('Discount_Range', observed=False).agg({'Sales': 'sum', 'Profit': 'sum'}).reset_index()
        disc_agg['Status'] = np.where(disc_agg['Profit'] >= 0, 'Positive Profit', 'Unprofitable')
        
        fig_disc = px.bar(
            disc_agg, x='Discount_Range', y='Profit', color='Status',
            title="Pengaruh Diskon terhadap Profitability Threshold",
            color_discrete_map={'Positive Profit': '#2563EB', 'Unprofitable': '#DC2626'}
        )
        fig_disc.add_hline(y=0, line_dash="dash", line_color="black")
        fig_disc.update_layout(height=400, xaxis_title="Rentang Diskon", yaxis_title="Profit ($)")
        st.plotly_chart(fig_disc, use_container_width=True, key="chart_root_disc")
        
    with c_ship:
        fig_scatter = px.scatter(
            df_hist_view.sample(min(1000, len(df_hist_view))), x='Shipping Cost', y='Profit', color='Market',
            title="Korelasi Shipping Cost vs Profit (Sample Transactions)",
            hover_data=['Country', 'Sub-Category', 'Discount'], opacity=0.7
        )
        fig_scatter.update_layout(height=400)
        st.plotly_chart(fig_scatter, use_container_width=True, key="chart_root_ship")

# ==========================================
# TAB 4: INVESTOR FORECAST & SIMULATOR (LIVE)
# ==========================================
with tab4:
    st.subheader("💡 Dynamic Investor Forecast & Revival Simulator (2015–2016)")
    
    st.markdown("""
    <div class="investor-card">
        <h3>🚀 Interactive What-If Scenario Simulator</h3>
        <p>Geser slider di bawah ini untuk mensimulasikan dampak <b>Batas Diskon</b> dan <b>Efisiensi Logistik</b>. Grafik proyeksi dan statistik di bawah akan berubah secara <b>real-time</b>.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("#### ⚙️ Simulation Controls")
    sc1, sc2 = st.columns(2)
    with sc1:
        discount_cap = st.slider(
            "Batas Maksimal Diskon (%)", min_value=10, max_value=50, value=20, step=5, key="slider_disc_cap",
            help="Diskon transaksi yang melebihi batas ini akan dipangkas ke batas maksimum."
        )
    with sc2:
        shipping_savings = st.slider(
            "Efisiensi Biaya Logistik (%)", min_value=0, max_value=30, value=15, step=5, key="slider_ship_sav",
            help="Persentase penghematan biaya pengiriman melalui optimasi rute & negosiasi vendor."
        )
        
    # Recalculate Simulation on FULL Time Series (2011-2014) for accurate forecasting
    df_sim = df.copy()
    df_sim['Discount_Sim'] = np.minimum(df_sim['Discount'], discount_cap / 100.0)
    discount_reduction = df_sim['Discount'] - df_sim['Discount_Sim']
    
    # Recovered Margin Formula
    df_sim['Profit_Sim'] = df_sim['Profit'] + (df_sim['Sales'] * discount_reduction * 0.90) + (df_sim['Shipping Cost'] * (shipping_savings / 100.0))
    
    # Monthly Aggregation across 2011-2014
    m_hist = df.groupby('Year-Month').agg({'Profit': 'sum'}).reset_index()
    m_hist_sim = df_sim.groupby('Year-Month').agg({'Profit_Sim': 'sum'}).reset_index()
    
    y_vals = m_hist['Profit'].values
    y_sim_vals = m_hist_sim['Profit_Sim'].values
    x_idx = np.arange(len(y_vals))
    
    # Fit Linear Models
    poly_bau = np.polyfit(x_idx, y_vals, deg=1)
    poly_opt = np.polyfit(x_idx, y_sim_vals, deg=1)
    
    future_x = np.arange(len(y_vals), len(y_vals) + 24)
    future_dates = pd.date_range(start='2015-01-01', periods=24, freq='MS').strftime('%Y-%m').tolist()
    
    # Seasonality Factor
    monthly_season = m_hist.groupby(m_hist['Year-Month'].dt.month)['Profit'].mean()
    season_factor = (monthly_season / monthly_season.mean()).values
    if len(season_factor) == 12:
        season_pattern = np.tile(season_factor, 2)
    else:
        season_pattern = np.ones(24)
    
    # Forecast Arrays
    forecast_bau = (poly_bau[0] * future_x + poly_bau[1]) * season_pattern
    forecast_opt = (poly_opt[0] * future_x + poly_opt[1]) * season_pattern
    
    # Calculate Live Differences
    proj_2015_bau = np.sum(forecast_bau[:12])
    proj_2015_opt = np.sum(forecast_opt[:12])
    annual_profit_gain = proj_2015_opt - proj_2015_bau
    pct_recovery = (annual_profit_gain / abs(proj_2015_bau) * 100) if proj_2015_bau != 0 else 0
    
    # Dynamic Live Banner
    st.markdown(f"""
    <div class="live-banner">
        ⚡ <b>SIMULATION IMPACT:</b> Cap Diskon {discount_cap}% & Hemat Logistik {shipping_savings}% menghasilkan tambahan profit sebesar 
        <span style="color:#10B981; font-size:1.3rem;">+${annual_profit_gain:,.0f} (+{pct_recovery:.1f}%)</span> di tahun 2015!
    </div>
    """, unsafe_allow_html=True)
    
    # Plotly Forecast Chart
    hist_dates = m_hist['Year-Month'].astype(str).tolist()
    
    fig_fc = go.Figure()
    
    # Historical Actual Baseline
    fig_fc.add_trace(go.Scatter(
        x=hist_dates, y=y_vals, name='Historical Actual (2011-2014)',
        mode='lines+markers', line=dict(color='#64748B', width=2)
    ))
    
    # Forecast BAU (Red Line)
    fig_fc.add_trace(go.Scatter(
        x=future_dates, y=forecast_bau, name='Forecast BAU (Tanpa Perubahan)',
        mode='lines+markers', line=dict(color='#EF4444', width=2.5, dash='dash')
    ))
    
    # Forecast Revival (Green Line)
    fig_fc.add_trace(go.Scatter(
        x=future_dates, y=forecast_opt, name=f'Forecast Revival Strategy (Cap {discount_cap}%, Logistik {shipping_savings}%)',
        mode='lines+markers', line=dict(color='#10B981', width=3.5),
        fill='tonexty', fillcolor='rgba(16, 185, 129, 0.15)' # Shaded gain area
    ))
    
    # Fixed Y-axis auto-margin for visible dynamic shift
    y_min = min(min(y_vals), min(forecast_bau)) * 0.9
    y_max = max(max(y_vals), max(forecast_opt)) * 1.15
    
    fig_fc.update_layout(
        title=f"Proyeksi Profit 2015–2016: BAU vs Revival Strategy (Cap Diskon {discount_cap}%, Logistik {shipping_savings}%)",
        xaxis_title="Tahun-Bulan", yaxis_title="Projected Monthly Profit ($)",
        yaxis=dict(range=[y_min, y_max]),
        hovermode="x unified", height=500,
        legend=dict(orientation="h", y=1.12)
    )
    
    st.plotly_chart(fig_fc, use_container_width=True, key=f"chart_fc_{discount_cap}_{shipping_savings}")
    
    # Dynamic Financial Metrics
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        st.metric("Proyeksi Profit 2015 (BAU)", f"${proj_2015_bau:,.0f}")
    with fc2:
        st.metric(f"Proyeksi Profit 2015 (Revival)", f"${proj_2015_opt:,.0f}", delta=f"+${annual_profit_gain:,.0f}")
    with fc3:
        st.metric("Persentase Kenaikan Profit", f"+{pct_recovery:.2f}%", delta="Net Profit Growth")

# ==========================================
# TAB 5: REVIVAL STRATEGY ROADMAP
# ==========================================
with tab5:
    st.subheader("🚀 Pelaksanaan Rencana Aksi untuk Board of Directors")
    
    st.markdown("""
    | No | Inisiatif Strategis | Root Cause Terkait | Penanggung Jawab (Owner) | Timeline | KPI Utama | Target Dampak Financial |
    |---|---|---|---|---|---|---|
    | **1** | **Discount Governance & Cap** | Diskon >20% menghasilkan kerugian pada transaksi | Head of Commercial & Sales | 1 - 3 Bulan | % Transaksi Diskon >20% < 2% | Rebound Margin +3.5% |
    | **2** | **Supply Chain & Freight Optimization** | Rasio shipping cost tinggi di pengiriman kilat | VP Supply Chain & Logistics | 3 - 6 Bulan | Shipping-to-Sales Ratio < 10% | Hemat $150K - $300K/tahun |
    | **3** | **Regional Market Restructuring** | Kerugian terfokus di 10 negara kunci | Chief Strategy Officer | 6 - 12 Bulan | Operating Profit 10 Negara < 0 -> Positive | Eliminasi rugi $250K/tahun |
    """)
    
    st.success("🎯 **Key Takeaway untuk Direksi & Investor**: Global Superstore memiliki fondasi pendapatan yang sangat kuat ($4.3M+ di 2014). Dengan disiplin diskon dan optimasi logistik, perusahaan akan mengalami *margin recovery* signifikan di tahun 2015–2016.")

st.divider()
st.caption("Global Superstore Analytics & Forecasting Dashboard v3 | Dynamic Live-Updating Scenario Simulator")
