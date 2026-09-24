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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Header Container */
    .header-container {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
        padding: 30px;
        border-radius: 12px;
        color: white;
        margin-bottom: 30px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .header-title {
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .header-subtitle {
        font-size: 1.1rem;
        font-weight: 400;
        opacity: 0.9;
        margin-top: 5px;
    }

    /* KPI Cards */
    .kpi-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: transform 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .kpi-label {
        font-size: 0.9rem;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }
    .kpi-value {
        font-size: 2rem;
        color: #0f172a;
        font-weight: 700;
        margin: 0;
    }

    /* Strategy Cards */
    .strategy-card {
        background-color: #f8fafc;
        padding: 20px;
        border-radius: 12px;
        border-left: 6px solid #2563eb;
        border-top: 1px solid #e2e8f0;
        border-right: 1px solid #e2e8f0;
        border-bottom: 1px solid #e2e8f0;
        height: 100%;
    }
    .strategy-card h4 {
        color: #0f172a;
        font-weight: 700;
        margin-top: 0;
    }
    .strategy-card p {
        color: #334155;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    .badge {
        background-color: #dbeafe;
        color: #1e40af;
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# --- TITLE HEADER ---
st.markdown("""
<div class="header-container">
    <p class="header-title">Global Superstore Analytics</p>
    <p class="header-subtitle">Revival Strategy & Executive Performance Dashboard (2011 - 2014)</p>
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
    
    bins = [-0.01, 0, 0.1, 0.2, 0.3, 0.4, 0.5, 1.0]
    labels = ['0%', '1-10%', '11-20%', '21-30%', '31-40%', '41-50%', '>50%']
    df['Discount_Range'] = pd.cut(df['Discount'], bins=bins, labels=labels)
    
    return df

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3075/3075977.png", width=60)
    st.markdown("### Data Source")
    uploaded_file = st.file_uploader("Upload CSV / Excel", type=['csv', 'xlsx'])
    
    df_raw = load_data(uploaded_file)
    if df_raw is None:
        st.warning("Silakan unggah dataset Global_Superstore2.")
        st.stop()

    st.markdown("### Filter Analytics")
    all_markets = ["All Markets"] + sorted(list(df_raw['Market'].dropna().unique()))
    selected_market = st.selectbox("Market", all_markets)

    all_years = ["All Years"] + sorted(list(df_raw['Year'].dropna().unique().astype(int)))
    selected_year = st.selectbox("Tahun", all_years)

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
    <div class="kpi-label">💰 Total Sales</div>
    <div class="kpi-value">${total_sales:,.0f}</div>
</div>
""", unsafe_allow_html=True)

col2.markdown(f"""
<div class="kpi-card">
    <div class="kpi-label">📈 Total Profit</div>
    <div class="kpi-value">${total_profit:,.0f}</div>
</div>
""", unsafe_allow_html=True)

col3.markdown(f"""
<div class="kpi-card">
    <div class="kpi-label">📊 Profit Margin</div>
    <div class="kpi-value" style="color: {'#10b981' if overall_margin > 0 else '#ef4444'};">{overall_margin:.2f}%</div>
</div>
""", unsafe_allow_html=True)

col4.markdown(f"""
<div class="kpi-card">
    <div class="kpi-label">📦 Total Orders</div>
    <div class="kpi-value">{total_orders:,}</div>
</div>
""", unsafe_allow_html=True)

st.write("") # Spacer

# --- GLOBAL PLOTLY CONFIG ---
layout_config = dict(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    margin=dict(l=20, r=20, t=50, b=20),
    title_font=dict(family="Inter", size=18, color="#0f172a"),
    font=dict(family="Inter", color="#475569")
)

# --- TABS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Overall Performance", 
    "🎯 Problem Areas", 
    "🔍 Root Cause Analysis", 
    "🚀 Revival Strategy",
    "🔮 Forecasting"
])

# ==========================================
# TAB 1: OVERALL PERFORMANCE
# ==========================================
with tab1:
    st.markdown("#### Tren Pertumbuhan Bisnis")
    
    col_t1_left, col_t1_right = st.columns(2, gap="large")
    
    with col_t1_left:
        yearly_df = df.groupby('Year').agg({'Sales': 'sum', 'Profit': 'sum'}).reset_index()
        yearly_df['Profit Margin (%)'] = (yearly_df['Profit'] / yearly_df['Sales']) * 100
        
        fig_yearly = go.Figure()
        fig_yearly.add_trace(go.Bar(x=yearly_df['Year'], y=yearly_df['Sales'], name='Sales', marker_color='#3b82f6', marker_line_width=0))
        fig_yearly.add_trace(go.Bar(x=yearly_df['Year'], y=yearly_df['Profit'], name='Profit', marker_color='#10b981', marker_line_width=0))
        fig_yearly.update_layout(**layout_config, title="Sales & Profit per Tahun", barmode='group', height=380)
        fig_yearly.update_yaxes(gridcolor='#f1f5f9')
        st.plotly_chart(fig_yearly, use_container_width=True)
        
    with col_t1_right:
        fig_margin = px.line(yearly_df, x='Year', y='Profit Margin (%)', markers=True, 
                             title="Tren Profit Margin (%)", color_discrete_sequence=['#8b5cf6'])
        fig_margin.update_layout(**layout_config, height=380)
        fig_margin.update_yaxes(gridcolor='#f1f5f9')
        fig_margin.update_traces(line=dict(width=3), marker=dict(size=8))
        st.plotly_chart(fig_margin, use_container_width=True)
        
    monthly_df = df.groupby('Year-Month').agg({'Sales': 'sum', 'Profit': 'sum'}).reset_index()
    fig_monthly = px.area(monthly_df, x='Year-Month', y=['Sales', 'Profit'], 
                          title="Tren Bulanan (2011 - 2014)",
                          color_discrete_map={'Sales': '#eff6ff', 'Profit': '#d1fae5'})
    
    # Overlay lines for sharp edges over area
    fig_monthly.add_trace(go.Scatter(x=monthly_df['Year-Month'], y=monthly_df['Sales'], mode='lines', line=dict(color='#2563eb', width=2), showlegend=False))
    fig_monthly.add_trace(go.Scatter(x=monthly_df['Year-Month'], y=monthly_df['Profit'], mode='lines', line=dict(color='#059669', width=2), showlegend=False))
    
    fig_monthly.update_layout(**layout_config, height=400, xaxis_title="", yaxis_title="USD ($)")
    fig_monthly.update_yaxes(gridcolor='#f1f5f9')
    st.plotly_chart(fig_monthly, use_container_width=True)

# ==========================================
# TAB 2: PROBLEM AREAS
# ==========================================
with tab2:
    st.markdown("#### Identifikasi Area Kerugian")
    
    col_t2_1, col_t2_2 = st.columns(2, gap="large")
    
    with col_t2_1:
        country_df = df.groupby(['Market', 'Country']).agg({'Profit': 'sum'}).reset_index()
        top_loss_country = country_df.sort_values(by='Profit', ascending=True).head(10)
        
        fig_loss_country = px.bar(
            top_loss_country, x='Profit', y='Country', color='Market', orientation='h',
            title="10 Negara Penyumbang Rugi Terbesar",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_loss_country.update_layout(**layout_config, height=400)
        fig_loss_country.update_xaxes(gridcolor='#f1f5f9')
        st.plotly_chart(fig_loss_country, use_container_width=True)
        
    with col_t2_2:
        subcat_df = df.groupby('Sub-Category').agg({'Profit': 'sum'}).reset_index()
        subcat_df['Status'] = np.where(subcat_df['Profit'] >= 0, 'Untung', 'Rugi')
        subcat_df = subcat_df.sort_values(by='Profit', ascending=True)
        
        fig_subcat = px.bar(
            subcat_df, x='Profit', y='Sub-Category', color='Status', orientation='h',
            title="Profitabilitas Sub-Kategori Produk",
            color_discrete_map={'Untung': '#10b981', 'Rugi': '#ef4444'}
        )
        fig_subcat.update_layout(**layout_config, height=400)
        fig_subcat.update_xaxes(gridcolor='#f1f5f9')
        st.plotly_chart(fig_subcat, use_container_width=True)

    st.markdown("#### Heatmap Profitabilitas: Market vs Sub-Category")
    pivot_matrix = df.pivot_table(index='Sub-Category', columns='Market', values='Profit', aggfunc='sum').fillna(0)
    fig_heatmap = px.imshow(
        pivot_matrix, 
        labels=dict(x="Market", y="Sub-Category", color="Profit ($)"),
        x=pivot_matrix.columns,
        y=pivot_matrix.index,
        color_continuous_scale="RdYlGn",
        aspect="auto"
    )
    fig_heatmap.update_layout(**layout_config, height=500)
    fig_heatmap.update_layout(margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig_heatmap, use_container_width=True)

# ==========================================
# TAB 3: ROOT CAUSE ANALYSIS
# ==========================================
with tab3:
    st.markdown("#### Analisis Akar Masalah")
    
    col_t3_1, col_t3_2 = st.columns(2, gap="large")
    
    with col_t3_1:

        # A. Analisis Ambang Batas Diskon (Discount Threshold)
        discount_impact = df.groupby('Discount_Range', observed=False).agg({
            'Order ID': 'count',
            'Sales': 'sum',
            'Profit': 'sum',
            'Profit Margin': 'mean'
        }).rename(columns={'Order ID': 'Total Orders'}).reset_index()

        discount_impact['Profit Margin (%)'] = discount_impact['Profit Margin'] * 100

        
        # Visualisasi Dampak Diskon
        fig_disc = px.bar(
            discount_impact,
            x='Discount_Range',
            y='Profit',
            title='Total Profit by Discount Range (Identifying Loss Threshold)',
            color='Profit',
            color_continuous_scale='RdYlGn',
            custom_data=['Total Orders', 'Sales', 'Profit Margin (%)']
        )
        fig_disc.add_hline(y=0, line_dash='dash', line_color='black')
        fig_disc.update_traces(
            hovertemplate=(
                '<b>%{x}</b><br>'
                'Total Profit: $%{y:,.0f}<br>'
                'Total Sales: $%{customdata[1]:,.0f}<br>'
                'Total Orders: %{customdata[0]:,.0f}<br>'
                'Avg Profit Margin: %{customdata[2]:.2f}%<extra></extra>'
            )
        )
        fig_disc.update_layout(height=420, xaxis_title='Discount Range', yaxis_title='Total Profit ($)')
        st.plotly_chart(fig_disc, use_container_width=True)

        print("=== TASK 3A: DISCOUNT LEVEL VS PROFITABILITY ===")
        st.dataframe(discount_impact, use_container_width=True)

        
                
    with col_t3_2:
        ship_df = df.groupby(['Ship Mode', 'Order Priority']).agg({'Shipping_Ratio': 'mean'}).reset_index()
        ship_df['Shipping_Ratio (%)'] = ship_df['Shipping_Ratio'] * 100
        
        fig_ship = px.bar(
            ship_df, x='Ship Mode', y='Shipping_Ratio (%)', color='Order Priority', barmode='group',
            title="Rasio Biaya Pengiriman terhadap Penjualan",
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        fig_ship.update_layout(**layout_config, height=400, yaxis_title="Biaya Pengiriman / Sales (%)")
        fig_ship.update_yaxes(gridcolor='#f1f5f9')
        st.plotly_chart(fig_ship, use_container_width=True)

        # B. Analisis Rasio Biaya Kirim berdasarkan Mode Pengiriman & Prioritas
        shipping_analysis = df.groupby(['Ship Mode', 'Order Priority']).agg({
            'Sales': 'sum',
            'Profit': 'sum',
            'Shipping Cost': 'sum',
            'Shipping_Ratio': 'mean'
        }).reset_index()
        shipping_analysis['Avg Shipping Ratio (%)'] = shipping_analysis['Shipping_Ratio'] * 100

        print("=== TASK 3B: SHIPPING COST RATIO BY SHIP MODE ===")
        st.dataframe(shipping_analysis.sort_values(by='Avg Shipping Ratio (%)', ascending=False), use_container_width=True)
    st.info("Pemberian diskon di atas 20% adalah penyebab utama kerugian margin. Selain itu, mode pengiriman Same Day untuk prioritas Critical memakan biaya logistik yang tidak proporsional dengan nilai penjualan.")

# ==========================================
# TAB 4: REVIVAL STRATEGY
# ==========================================
with tab4:
    st.markdown("#### Ringkasan Eksekutif")
    st.write("Skala pendapatan global stabil, namun kebocoran profit terjadi secara masif pada transaksi dengan diskon tak terkontrol dan inefisiensi logistik pengiriman kilat. Tiga inisiatif strategis wajib dieksekusi:")
    st.write("")

    col_s1, col_s2, col_s3 = st.columns(3, gap="medium")
    
    with col_s1:
        st.markdown("""
        <div class="strategy-card">
            <span class="badge">Prioritas 1</span>
            <h4 style="margin-top: 15px;">Kebijakan Batas Diskon</h4>
            <p><b>Akar Masalah:</b> Diskon >20% menggerus profit hingga minus.</p>
            <p><b>Tindakan:</b> Kunci sistem agar batas maksimal diskon 15%. Diskon lebih dari itu wajib melewati <i>approval</i> level manajer.</p>
            <p><b>Target:</b> Recovery margin profit di atas 14%.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_s2:
        st.markdown("""
        <div class="strategy-card">
            <span class="badge">Prioritas 2</span>
            <h4 style="margin-top: 15px;">Rasionalisasi Logistik</h4>
            <p><b>Akar Masalah:</b> Margin hilang akibat biaya <i>Same Day / First Class</i> pada order <i>Critical</i>.</p>
            <p><b>Tindakan:</b> Negosiasi ulang kontrak vendor atau bebankan sebagian biaya premium langsung ke pelanggan.</p>
            <p><b>Target:</b> Menurunkan rasio beban ongkos kirim sebesar 15%.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_s3:
        st.markdown("""
        <div class="strategy-card">
            <span class="badge">Prioritas 3</span>
            <h4 style="margin-top: 15px;">Restrukturisasi Wilayah</h4>
            <p><b>Akar Masalah:</b> Beban kerugian terkonsentrasi di 10 negara spesifik.</p>
            <p><b>Tindakan:</b> Hentikan penjualan sub-kategori yang terbukti rugi di negara tersebut, dan sesuaikan harga dasar (<i>base price</i>).</p>
            <p><b>Target:</b> Meningkatkan profit region terdampak sebesar 25%.</p>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# TAB 5: FORECASTING
# ==========================================
with tab5:
    st.markdown("#### Proyeksi Penjualan (12 Bulan Kedepan)")
    
    # Agregasi data bulanan
    monthly_sales = df.groupby('Year-Month')['Sales'].sum().reset_index()
    monthly_sales['Date'] = pd.to_datetime(monthly_sales['Year-Month'])
    monthly_sales = monthly_sales.sort_values('Date')
    
    # Kalkulasi regresi linear (Trend) menggunakan numpy
    x_hist = np.arange(len(monthly_sales))
    y_hist = monthly_sales['Sales'].values
    
    z = np.polyfit(x_hist, y_hist, 1) # Degree 1 untuk garis lurus
    p = np.poly1d(z)
    
    # Buat titik waktu masa depan (12 bulan)
    last_date = monthly_sales['Date'].iloc[-1]
    future_dates = [last_date + pd.DateOffset(months=i) for i in range(1, 13)]
    x_future = np.arange(len(monthly_sales), len(monthly_sales) + 12)
    y_future = p(x_future)
    
    fig_forecast = go.Figure()
    
    # Plot Data Historis
    fig_forecast.add_trace(go.Scatter(
        x=monthly_sales['Date'], 
        y=monthly_sales['Sales'],
        mode='lines', 
        name='Data Aktual',
        line=dict(color='#2563eb', width=2)
    ))
    
    # Plot Garis Forecast Historis (agar menyambung)
    fig_forecast.add_trace(go.Scatter(
        x=monthly_sales['Date'], 
        y=p(x_hist),
        mode='lines', 
        name='Garis Tren Historis',
        line=dict(color='#94a3b8', width=1, dash='dot')
    ))
    
    # Plot Proyeksi 12 Bulan Kedepan
    fig_forecast.add_trace(go.Scatter(
        x=future_dates, 
        y=y_future,
        mode='lines+markers', 
        name='Proyeksi 12 Bulan',
        line=dict(color='#ef4444', width=3, dash='dash')
    ))
    
    fig_forecast.update_layout(
        **layout_config, 
        height=500, 
        yaxis_title="Total Sales ($)",
        hovermode="x unified"
    )
    fig_forecast.update_yaxes(gridcolor='#f1f5f9')
    st.plotly_chart(fig_forecast, use_container_width=True)

    # Analisis Angka Forecast
    sales_growth = ((y_future[-1] - y_future[0]) / y_future[0]) * 100
    
    col_f1, col_f2 = st.columns(2, gap="large")
    with col_f1:
        st.info(f"Berdasarkan lintasan historis, tren penjualan diproyeksikan tumbuh **{sales_growth:.2f}%** selama 12 bulan ke depan (hanya menghitung momentum basis).")
    with col_f2:
        st.warning("Model regresi linear ini tidak menangkap efek musiman (seasonality) seperti lonjakan akhir tahun. Fokuskan strategi pada peningkatan margin, bukan sekadar mengejar volume proyeksi ini.")