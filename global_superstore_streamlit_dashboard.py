import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="Global Superstore, Revival Strategy",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    .finding-box {
        background-color: #fffbeb;
        border-left: 4px solid #f59e0b;
        padding: 15px;
        border-radius: 4px;
        margin-top: 15px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header-container">
    <p class="header-title">Global Superstore Analytics</p>
    <p class="header-subtitle">Executive Performance Dashboard & Revival Strategy (2011 to 2014)</p>
</div>
""", unsafe_allow_html=True)

@st.cache_data
def load_data(file_source=None):
    try:
        if file_source is not None:
            if file_source.name.endswith('.csv'):
                df = pd.read_csv(file_source, encoding='latin1')
            else:
                df = pd.read_excel(file_source)
        else:
            # Gunakan data simulasi jika file tidak diunggah agar presentasi tetap berjalan aman
            gdrive_url = 'https://drive.google.com/file/d/1sdtcwBx4Skbh3C4hO7g29hY5v8uihpPo/view?usp=drive_link'
            download_url = 'https://drive.google.com/uc?id=' + gdrive_url.split('/')[-2]
            
            try:
                df = pd.read_csv(download_url, encoding='latin1')
            except Exception:
                return None

        # Standarisasi Kolom
        df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')
        df['Profit Margin'] = (df['Profit'] / df['Sales']) * 100
        df['Shipping_Ratio'] = (df['Shipping Cost'] / df['Sales']) * 100
        df['Year'] = df['Order Date'].dt.year
        df['Month'] = df['Order Date'].dt.month
        df['Year-Month'] = df['Order Date'].dt.to_period('M').astype(str)
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3075/3075977.png", width=60)
    st.markdown("### Data Source")
    uploaded_file = st.file_uploader("Upload Dataset CSV / Excel", type=['csv', 'xlsx'])
    
    df_raw = load_data(uploaded_file)
    if df_raw is None:
        st.warning("Gagal memuat data.")
        st.stop()

    if uploaded_file is None:
        st.info("Menggunakan Data Simulasi. Silakan unggah file asli untuk melihat data nyata Anda.")

    st.markdown("### Filter Analytics")
    all_markets = ["All Markets"] + sorted(list(df_raw['Market'].dropna().unique()))
    selected_market = st.selectbox("Market Region", all_markets)

    all_years = ["All Years"] + sorted(list(df_raw['Year'].dropna().unique().astype(int)))
    selected_year = st.selectbox("Tahun Transaksi", all_years)

df = df_raw.copy()
if selected_market != "All Markets":
    df = df[df['Market'] == selected_market]
if selected_year != "All Years":
    df = df[df['Year'] == int(selected_year)]

total_sales = df['Sales'].sum()
total_profit = df['Profit'].sum()
overall_margin = (total_profit / total_sales * 100) if total_sales > 0 else 0
total_orders = df['Order ID'].nunique() if 'Order ID' in df.columns else len(df)

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
    <div class="kpi-label">📊 Avg Profit Margin</div>
    <div class="kpi-value" style="color: {'#10b981' if overall_margin > 0 else '#ef4444'};">{overall_margin:.2f}%</div>
</div>
""", unsafe_allow_html=True)

col4.markdown(f"""
<div class="kpi-card">
    <div class="kpi-label">📦 Total Orders</div>
    <div class="kpi-value">{total_orders:,}</div>
</div>
""", unsafe_allow_html=True)

st.write("") 

layout_config = dict(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    margin=dict(l=20, r=20, t=50, b=20),
    title_font=dict(family="Inter", size=18, color="#0f172a"),
    font=dict(family="Inter", color="#475569")
)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 1. Executive Summary", 
    "🎯 2. Problem Areas", 
    "🔍 3. Root Cause Analysis", 
    "🚀 4. Revival Strategy",
    "🔮 5. Forecasting 2015"
])

with tab1:
    st.markdown("#### Analisis Performa Keseluruhan (The Growth Trap)")
    
    st.markdown("""
    <div class="finding-box">
        <strong>Pesan Kunci:</strong> Global Superstore sedang mengalami ilusi pertumbuhan. Secara kasat mata volume pendapatan (Sales) terus memecahkan rekor setiap tahunnya, namun rasio profitabilitas (Margin) justru menukik tajam. Kita membeli pendapatan dengan ongkos kerugian internal.
    </div>
    """, unsafe_allow_html=True)
    
    yearly_df = df_raw.groupby('Year').agg({'Sales': 'sum', 'Profit': 'sum'}).reset_index()
    yearly_df['Profit Margin (%)'] = (yearly_df['Profit'] / yearly_df['Sales']) * 100
    
    fig_yoy = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig_yoy.add_trace(
        go.Bar(x=yearly_df['Year'], y=yearly_df['Sales'], name="Total Sales ($)", marker_color='#3b82f6'),
        secondary_y=False,
    )
    fig_yoy.add_trace(
        go.Scatter(x=yearly_df['Year'], y=yearly_df['Profit Margin (%)'], name="Profit Margin (%)", 
                   mode='lines+markers', line=dict(color='#ef4444', width=4), marker=dict(size=10)),
        secondary_y=True,
    )
    
    fig_yoy.update_layout(**layout_config, title="Year-over-Year, Volume Penjualan vs Profit Margin", height=450)
    fig_yoy.update_yaxes(title_text="Total Sales ($)", secondary_y=False, gridcolor='#f1f5f9')
    fig_yoy.update_yaxes(title_text="Profit Margin (%)", secondary_y=True, showgrid=False)
    
    st.plotly_chart(fig_yoy, use_container_width=True)

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

with tab2:
    st.markdown("#### Pemetaan Kerugian Berdasarkan Pasar dan Kategori Produk")
    
    st.markdown("""
    <div class="finding-box">
        <strong>Temuan Area Bermasalah:</strong> Kerugian paling masif tidak tersebar secara merata, melainkan sangat terpusat pada kategori <strong>Furniture</strong>, khususnya di wilayah operasi <strong>EMEA</strong> dan <strong>APAC</strong>.
    </div>
    """, unsafe_allow_html=True)
    
    col_t2_1, col_t2_2 = st.columns(2, gap="large")
    
    geo_prod = df_raw.groupby(['Market', 'Category']).agg({'Profit': 'sum', 'Sales': 'sum'}).reset_index()
    
    with col_t2_1:
        fig_bar = px.bar(
            geo_prod, x='Market', y='Profit', color='Category', barmode='group',
            title="Total Profit Berdasarkan Pasar & Kategori",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_bar.add_hline(y=0, line_dash="dash", line_color="black")
        fig_bar.update_layout(**layout_config, height=450)
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with col_t2_2:
        pivot_matrix = df_raw.pivot_table(index='Category', columns='Market', values='Profit', aggfunc='sum').fillna(0)
        fig_heatmap = px.imshow(
            pivot_matrix, 
            labels=dict(x="Pasar Regional", y="Kategori Produk", color="Profit ($)"),
            x=pivot_matrix.columns, y=pivot_matrix.index,
            color_continuous_scale="RdYlGn", aspect="auto",
            title="Heatmap Profitabilitas Area"
        )
        fig_heatmap.update_layout(**layout_config, height=450)
        st.plotly_chart(fig_heatmap, use_container_width=True)

with tab3:
    st.markdown("#### Analisis Akar Permasalahan (Root Cause)")
    
    col_t3_1, col_t3_2 = st.columns(2, gap="large")
    
    with col_t3_1:
        st.markdown("##### 1. Masalah Inefisiensi Logistik")
        st.write("Produk furnitur di pasar internasional hancur marginnya akibat biaya pengiriman (Shipping Cost) yang memakan porsi terlalu besar dari nilai transaksi.")
        
        ship_df = df_raw.groupby(['Market', 'Category']).agg({'Profit': 'sum', 'Shipping_Ratio': 'mean'}).reset_index()
        fig_scatter = px.scatter(
            ship_df, x='Shipping_Ratio', y='Profit', color='Category', hover_data=['Market'],
            title="Korelasi Rasio Ongkos Kirim vs Laba",
            labels={'Shipping_Ratio': 'Rata-rata Ongkos Kirim (% dari Penjualan)'}
        )
        fig_scatter.add_hline(y=0, line_dash="dash", line_color="black")
        fig_scatter.update_layout(**layout_config, height=380)
        st.plotly_chart(fig_scatter, use_container_width=True)

    with col_t3_2:
        st.markdown("##### 2. Ilusi Diskon Musiman (Kepanikan Q1)")
        st.write("Penjualan natural selalu turun di awal tahun (Jan-Feb). Manajemen merespons dengan obral diskon ekstrem yang gagal menaikkan volume, namun berhasil merusak margin kotor.")
        
        monthly_trend = df_raw.groupby('Month').agg({'Sales': 'mean', 'Discount': 'mean'}).reset_index()
        monthly_trend['Discount (%)'] = monthly_trend['Discount'] * 100
        
        fig_season = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig_season.add_trace(
            go.Bar(x=monthly_trend['Month'], y=monthly_trend['Sales'], name='Rata-rata Penjualan', 
                   marker_color=['#ef4444' if i in [1, 2] else '#94a3b8' for i in monthly_trend['Month']]),
            secondary_y=False,
        )
        fig_season.add_trace(
            go.Scatter(x=monthly_trend['Month'], y=monthly_trend['Discount (%)'], name='Rata-rata Diskon (%)',
                       mode='lines+markers', line=dict(color='#f59e0b', width=3)),
            secondary_y=True,
        )
        fig_season.update_layout(**layout_config, title="Pola Musiman, Sales vs Tingkat Diskon", height=380)
        fig_season.update_yaxes(title_text="Sales ($)", secondary_y=False)
        fig_season.update_yaxes(title_text="Diskon (%)", secondary_y=True, showgrid=False)
        st.plotly_chart(fig_season, use_container_width=True)

with tab4:
    st.markdown("#### Strategi Pemulihan (Action Plan)")
    st.write("Berdasarkan temuan data, berikut adalah tiga langkah prioritas yang wajib dieksekusi untuk mengembalikan kesehatan profitabilitas perusahaan dalam 6 hingga 12 bulan ke depan.")
    st.write("")

    col_s1, col_s2, col_s3 = st.columns(3, gap="medium")
    
    with col_s1:
        st.markdown("""
        <div class="strategy-card">
            <span class="badge">Prioritas 1</span>
            <h4 style="margin-top: 15px;">Rasionalisasi Logistik Regional</h4>
            <p><b>Masalah:</b> Pengiriman furnitur jarak jauh di EMEA dan APAC merugikan perusahaan.</p>
            <p><b>Tindakan:</b> Hentikan pengiriman lintas batas untuk barang bervolume besar. Terapkan model kemitraan manufaktur lokal atau sistem <i>drop-shipping</i> di wilayah tersebut.</p>
            <p><b>PIC & Target:</b> VP Supply Chain, Turunkan rasio biaya pengiriman di bawah 10%.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_s2:
        st.markdown("""
        <div class="strategy-card">
            <span class="badge">Prioritas 2</span>
            <h4 style="margin-top: 15px;">Kebijakan Batas Diskon (Hard-Cap)</h4>
            <p><b>Masalah:</b> Tim penjualan memberikan diskon berlebihan yang menghancurkan margin kotor.</p>
            <p><b>Tindakan:</b> Implementasikan algoritma pembatas diskon otomatis pada sistem POS. Ubah metrik insentif tenaga penjual menjadi berbasis margin laba kotor, bukan volume.</p>
            <p><b>PIC & Target:</b> Chief Sales Officer, Eliminasi 100% transaksi rugi akibat diskon.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_s3:
        st.markdown("""
        <div class="strategy-card">
            <span class="badge">Prioritas 3</span>
            <h4 style="margin-top: 15px;">Pivot Pemasaran Q1 ke B2B</h4>
            <p><b>Masalah:</b> Kepanikan promosi B2C di bulan Januari dan Februari terbukti membakar anggaran tanpa hasil.</p>
            <p><b>Tindakan:</b> Hentikan promosi masal awal tahun. Alihkan dana pemasaran untuk mengakuisisi klien korporat (B2B) yang baru saja mencairkan anggaran tahunan mereka.</p>
            <p><b>PIC & Target:</b> Chief Marketing Officer, Pertumbuhan 15% pada segmen korporat di Q1.</p>
        </div>
        """, unsafe_allow_html=True)

with tab5:
    st.markdown("#### Proyeksi Valuasi Penjualan (2015)")
    
    # Agregasi data bulanan untuk time series
    monthly_sales = df_raw.groupby('Year-Month')['Sales'].sum().reset_index()
    monthly_sales['Date'] = pd.to_datetime(monthly_sales['Year-Month'])
    monthly_sales = monthly_sales.sort_values('Date')
    
    # Ekstraksi komponen untuk proyeksi (Tren Linear + Faktor Musiman)
    monthly_sales['MonthNum'] = monthly_sales['Date'].dt.month
    
    # 1. Menghitung Faktor Musiman Rata-rata
    seasonal_means = monthly_sales.groupby('MonthNum')['Sales'].mean()
    overall_mean = monthly_sales['Sales'].mean()
    seasonal_indices = seasonal_means / overall_mean
    
    # 2. Menghitung Tren Linear dasar menggunakan Numpy
    x_hist = np.arange(len(monthly_sales))
    y_hist = monthly_sales['Sales'].values
    z = np.polyfit(x_hist, y_hist, 1)
    p = np.poly1d(z)
    
    # 3. Menerapkan proyeksi 12 bulan ke depan
    last_date = monthly_sales['Date'].iloc[-1]
    future_dates = [last_date + pd.DateOffset(months=i) for i in range(1, 13)]
    future_months = [d.month for d in future_dates]
    
    x_future = np.arange(len(monthly_sales), len(monthly_sales) + 12)
    y_trend_future = p(x_future)
    
    # Kalikan tren dengan indeks musiman agar grafik naik turun secara realistis
    y_future_seasonal = [y_trend_future[i] * seasonal_indices[future_months[i]] for i in range(12)]
    
    fig_forecast = go.Figure()
    
    fig_forecast.add_trace(go.Scatter(
        x=monthly_sales['Date'], y=monthly_sales['Sales'],
        mode='lines+markers', name='Data Historis Aktual',
        line=dict(color='#2563eb', width=2)
    ))
    
    fig_forecast.add_trace(go.Scatter(
        x=future_dates, y=y_future_seasonal,
        mode='lines+markers', name='Proyeksi 2015 (Dengan Musiman)',
        line=dict(color='#10b981', width=3, dash='dash')
    ))
    
    fig_forecast.update_layout(
        **layout_config, height=500, yaxis_title="Total Sales ($)", hovermode="x unified",
        title="Pemodelan Time Series, Historis dan Target Pasca-Intervensi"
    )
    fig_forecast.update_yaxes(gridcolor='#f1f5f9')
    st.plotly_chart(fig_forecast, use_container_width=True)

    col_f1, col_f2 = st.columns(2, gap="large")
    with col_f1:
        st.info("Model peramalan ini telah disempurnakan. Kami tidak hanya menggunakan regresi garis lurus, melainkan telah memasukkan algoritma **Indeks Multiplikatif Musiman** agar proyeksi mencerminkan pola naik-turun perilaku konsumen yang nyata.")
    with col_f2:
        st.warning("Garis proyeksi hijau adalah target valusasi volume kita. Jika ketiga rekomendasi strategi dieksekusi dengan baik, kita dapat menikmati volume penjualan yang tinggi ini **tanpa** harus mengorbankan margin profitabilitas lagi.")