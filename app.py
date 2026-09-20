import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Global Superstore - Revival Strategy Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- STYLING ---
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0px;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #4B5563;
        margin-bottom: 25px;
    }
    .metric-card {
        background-color: #F3F4F6;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #1E3A8A;
    }
</style>
""", unsafe_allow_html=True)

# --- TITLE HEADER ---
st.markdown('<p class="main-title">Global Superstore: Revival Strategy Dashboard</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Executive Analytics Dashboard for the Board of Directors (Data 2011 - 2014)</p>', unsafe_allow_html=True)

# --- DATA LOADING & PREPROCESSING ---
@st.cache_data
def load_data(file_source=None):
    if file_source is not None:
        if file_source.name.endswith('.csv'):
            df = pd.read_csv(file_source, encoding='latin1')
        else:
            df = pd.read_excel(file_source)
    else:
        # Try local default filenames if available
        try:
            df = pd.read_csv('Global_Superstore2.csv', encoding='latin1')
        except FileNotFoundError:
            try:
                df = pd.read_excel('Global_Superstore2.xlsx')
            except FileNotFoundError:
                return None
    
    # Preprocessing
    df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True, errors='coerce')
    df['Ship Date'] = pd.to_datetime(df['Ship Date'], dayfirst=True, errors='coerce')
    
    df['Profit Margin'] = df['Profit'] / df['Sales']
    df['Year'] = df['Order Date'].dt.year
    df['Quarter'] = df['Order Date'].dt.to_period('Q').astype(str)
    df['Year-Month'] = df['Order Date'].dt.to_period('M').astype(str)
    df['Shipping_Ratio'] = df['Shipping Cost'] / df['Sales']
    
    # Discount Ranges
    bins = [-0.01, 0, 0.1, 0.2, 0.3, 0.4, 0.5, 1.0]
    labels = ['0%', '1-10%', '11-20%', '21-30%', '31-40%', '41-50%', '>50%']
    df['Discount_Range'] = pd.cut(df['Discount'], bins=bins, labels=labels)
    
    return df

# Sidebar Data Upload
st.sidebar.header("📁 Data Source")
uploaded_file = st.sidebar.file_uploader("Upload File (CSV / Excel)", type=['csv', 'xlsx'])

df_raw = load_data(uploaded_file)

if df_raw is None:
    st.info("👋 Silakan unggah file dataset `Global_Superstore2.csv` atau `Global_Superstore2.xlsx` pada sidebar di sebelah kiri untuk memulai dashboard.")
    st.stop()

# --- SIDEBAR FILTERS ---
st.sidebar.header("🔍 Filter Analytics")

# Market Filter
all_markets = ["All Markets"] + sorted(list(df_raw['Market'].dropna().unique()))
selected_market = st.sidebar.selectbox("Pilih Market", all_markets)

# Year Filter
all_years = ["All Years"] + sorted(list(df_raw['Year'].dropna().unique().astype(int)))
selected_year = st.sidebar.selectbox("Pilih Tahun", all_years)

# Segment Filter
all_segments = ["All Segments"] + sorted(list(df_raw['Segment'].dropna().unique()))
selected_segment = st.sidebar.selectbox("Pilih Customer Segment", all_segments)

# Apply Filters
df = df_raw.copy()
if selected_market != "All Markets":
    df = df[df['Market'] == selected_market]
if selected_year != "All Years":
    df = df[df['Year'] == int(selected_year)]
if selected_segment != "All Segments":
    df = df[df['Segment'] == selected_segment]

# --- KPI METRICS CARDS ---
total_sales = df['Sales'].sum()
total_profit = df['Profit'].sum()
overall_margin = (total_profit / total_sales * 100) if total_sales > 0 else 0
total_orders = df['Order ID'].nunique()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="💰 Total Sales", value=f"${total_sales:,.0f}")
with col2:
    st.metric(label="📈 Total Profit", value=f"${total_profit:,.0f}")
with col3:
    st.metric(label="📊 Profit Margin", value=f"{overall_margin:.2f}%")
with col4:
    st.metric(label="📦 Total Orders", value=f"{total_orders:,}")

st.divider()

# --- TABS ANALYSIS ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Task 1: Overall Performance", 
    "🎯 Task 2: Problem Areas (Drill-Down)", 
    "🔍 Task 3: Root Cause Analysis", 
    "🚀 Task 4: Revival Strategy"
])

# ==========================================
# TAB 1: OVERALL PERFORMANCE
# ==========================================
with tab1:
    st.subheader("Evaluasi Performa Keseluruhan (2011 - 2014)")
    st.write("Menganalisis tren penjualan, profitabilitas, serta pertumbuhan tahunan (YoY).")
    
    col_t1_left, col_t1_right = st.columns([1, 1])
    
    with col_t1_left:
        # Yearly Summary Table & Chart
        yearly_df = df.groupby('Year').agg({
            'Sales': 'sum',
            'Profit': 'sum',
            'Quantity': 'sum'
        }).reset_index()
        
        yearly_df['Profit Margin (%)'] = (yearly_df['Profit'] / yearly_df['Sales']) * 100
        yearly_df['Sales YoY Growth (%)'] = yearly_df['Sales'].pct_change() * 100
        yearly_df['Profit YoY Growth (%)'] = yearly_df['Profit'].pct_change() * 100
        
        fig_yearly = go.Figure()
        fig_yearly.add_trace(go.Bar(x=yearly_df['Year'], y=yearly_df['Sales'], name='Sales ($)', marker_color='#3B82F6'))
        fig_yearly.add_trace(go.Bar(x=yearly_df['Year'], y=yearly_df['Profit'], name='Profit ($)', marker_color='#10B981'))
        fig_yearly.update_layout(title="Total Sales & Profit per Tahun", barmode='group', height=400)
        st.plotly_chart(fig_yearly, use_container_width=True)
        
    with col_t1_right:
        # Profit Margin Trend
        fig_margin = px.line(yearly_df, x='Year', y='Profit Margin (%)', markers=True, 
                             title="Tren Profit Margin Tahunan (%)", color_discrete_sequence=['#8B5CF6'])
        fig_margin.update_layout(height=400)
        st.plotly_chart(fig_margin, use_container_width=True)
        
    # Monthly Trend
    monthly_df = df.groupby('Year-Month').agg({'Sales': 'sum', 'Profit': 'sum'}).reset_index()
    fig_monthly = px.line(monthly_df, x='Year-Month', y=['Sales', 'Profit'], 
                          title="Tren Bulanan Sales & Profit (2011 - 2014)",
                          color_discrete_map={'Sales': '#2563EB', 'Profit': '#059669'})
    fig_monthly.update_layout(height=400, xaxis_title="Tahun-Bulan", yaxis_title="Nilai ($)")
    st.plotly_chart(fig_monthly, use_container_width=True)
    
    with st.expander("📄 Lihat Tabel Summary YoY"):
        st.dataframe(yearly_df.style.format({
            'Sales': '${:,.2f}',
            'Profit': '${:,.2f}',
            'Quantity': '{:,.0f}',
            'Profit Margin (%)': '{:.2f}%',
            'Sales YoY Growth (%)': '{:.2f}%',
            'Profit YoY Growth (%)': '{:.2f}%'
        }))

# ==========================================
# TAB 2: PROBLEM AREAS
# ==========================================
with tab2:
    st.subheader("Identifikasi Titik Kerugian (Drill-Down)")
    
    col_t2_1, col_t2_2 = st.columns([1, 1])
    
    with col_t2_1:
        # Top 10 Loss Making Countries
        country_df = df.groupby(['Market', 'Country']).agg({'Sales': 'sum', 'Profit': 'sum'}).reset_index()
        top_loss_country = country_df.sort_values(by='Profit', ascending=True).head(10)
        
        fig_loss_country = px.bar(
            top_loss_country, x='Profit', y='Country', color='Market', orientation='h',
            title="Top 10 Negara Pembuat Rugi Terbesar ($)",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_loss_country.update_layout(height=420)
        st.plotly_chart(fig_loss_country, use_container_width=True)
        
    with col_t2_2:
        # Sub-Category Profitability
        subcat_df = df.groupby('Sub-Category').agg({'Sales': 'sum', 'Profit': 'sum'}).reset_index()
        subcat_df['Status'] = np.where(subcat_df['Profit'] >= 0, 'Untung', 'Rugi')
        subcat_df = subcat_df.sort_values(by='Profit', ascending=True)
        
        fig_subcat = px.bar(
            subcat_df, x='Profit', y='Sub-Category', color='Status', orientation='h',
            title="Profit / Kerugian per Sub-Kategori Produk",
            color_discrete_map={'Untung': '#10B981', 'Rugi': '#EF4444'}
        )
        fig_subcat.update_layout(height=420)
        st.plotly_chart(fig_subcat, use_container_width=True)

    # Matrix Market vs Sub-Category Profit Heatmap
    st.subheader("🔥 Matrix Profitabilitas: Market vs Sub-Category")
    pivot_matrix = df.pivot_table(index='Sub-Category', columns='Market', values='Profit', aggfunc='sum').fillna(0)
    fig_heatmap = px.imshow(
        pivot_matrix, 
        labels=dict(x="Market", y="Sub-Category", color="Profit ($)"),
        x=pivot_matrix.columns,
        y=pivot_matrix.index,
        color_continuous_scale="RdYlGn",
        aspect="auto"
    )
    fig_heatmap.update_layout(height=500)
    st.plotly_chart(fig_heatmap, use_container_width=True)

# ==========================================
# TAB 3: ROOT CAUSE ANALYSIS
# ==========================================
with tab3:
    st.subheader("Analisis Akar Penyebab Masalah (Root Causes)")
    
    col_t3_1, col_t3_2 = st.columns([1, 1])
    
    with col_t3_1:
        # Discount Level Impact
        discount_df = df.groupby('Discount_Range', observed=False).agg({
            'Order ID': 'count',
            'Sales': 'sum',
            'Profit': 'sum'
        }).reset_index()
        discount_df['Profit Margin (%)'] = (discount_df['Profit'] / discount_df['Sales']) * 100
        discount_df['Status'] = np.where(discount_df['Profit'] >= 0, 'Positive Profit', 'Unprofitable')
        
        fig_disc = px.bar(
            discount_df, x='Discount_Range', y='Profit', color='Status',
            title="Dampak Tingkat Diskon Terhadap Total Profit ($)",
            color_discrete_map={'Positive Profit': '#3B82F6', 'Unprofitable': '#DC2626'},
            text_auto='.2s'
        )
        fig_disc.add_hline(y=0, line_dash="dash", line_color="black")
        fig_disc.update_layout(height=420, xaxis_title="Rentang Diskon", yaxis_title="Total Profit ($)")
        st.plotly_chart(fig_disc, use_container_width=True)
        
    with col_t3_2:
        # Shipping Cost Ratio by Ship Mode & Order Priority
        ship_df = df.groupby(['Ship Mode', 'Order Priority']).agg({
            'Sales': 'sum',
            'Profit': 'sum',
            'Shipping Cost': 'sum',
            'Shipping_Ratio': 'mean'
        }).reset_index()
        ship_df['Shipping_Ratio (%)'] = ship_df['Shipping_Ratio'] * 100
        
        fig_ship = px.bar(
            ship_df, x='Ship Mode', y='Shipping_Ratio (%)', color='Order Priority', barmode='group',
            title="Rasio Biaya Pengiriman Terhadap Sales (%)",
            color_discrete_sequence=px.colors.qualitative.Dark24
        )
        fig_ship.update_layout(height=420, yaxis_title="Shipping Cost / Sales (%)")
        st.plotly_chart(fig_ship, use_container_width=True)

    st.warning("""
    📌 **Temuan Utama Akar Masalah:**
    1. **Erosi Profit Akibat Diskon**: Ketika diskon diberikan di atas **20%**, profitabilitas berbalik menjadi negatif secara signifikan.
    2. **Biaya Pengiriman Tinggi**: Pengiriman dengan *Order Priority* Critical/High dan *Ship Mode* Same Day/First Class memiliki rasio biaya pengiriman yang tinggi yang menggerus profit di wilayah tertentu.
    """)

# ==========================================
# TAB 4: REVIVAL STRATEGY
# ==========================================
with tab4:
    st.subheader("🚀 Strategi Pemulihan (Revival Strategy) untuk Direksi")
    
    st.markdown("""
    ### 🎯 Pesan Utama untuk Jajaran Direksi:
    > **"Global Superstore tidak mengalami penurunan secara keseluruhan, namun profitabilitas tergerus hebat oleh praktik diskon tak terkontrol di atas 20% serta biaya logistik yang tidak efisien di negara-negara tertentu."**
    """)
    
    st.divider()
    
    st.markdown("### 📋 3 Langkah Strategis Prioritas (6-12 Bulan Ke Depan)")
    
    col_s1, col_s2, col_s3 = st.columns(3)
    
    with col_s1:
        st.markdown("""
        <div class="metric-card">
            <h4>1. Kebijakan Diskon Ketat (Discount Cap)</h4>
            <p><b>Akar Masalah:</b> Diskon >20% menghasilkan kerugian bersih.</p>
            <p><b>Aksi:</b> Batasi diskon maksimal 15-20% & butuh persetujuan khusus untuk diskon tinggi.</p>
            <p><b>Owner:</b> Head of Sales & Commercial</p>
            <p><b>KPI:</b> Rebound Profit Margin ke >14%</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_s2:
        st.markdown("""
        <div class="metric-card">
            <h4>2. Optimalisasi Logistik & Pengiriman</h4>
            <p><b>Akar Masalah:</b> Rasio biaya pengiriman tinggi pada ekspedisi kilat.</p>
            <p><b>Aksi:</b> Negosiasi ulang tarif vendor ekspedisi & evaluasi opsi pengiriman wilayah rugi.</p>
            <p><b>Owner:</b> VP Supply Chain & Logistics</p>
            <p><b>KPI:</b> Penurunan Shipping Ratio sebesar 15%</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_s3:
        st.markdown("""
        <div class="metric-card">
            <h4>3. Restrukturisasi Wilayah Rugi</h4>
            <p><b>Akar Masalah:</b> Kerugian terkonsentrasi di 10 negara kunci.</p>
            <p><b>Aksi:</b> Evaluasi portofolio produk & rasionalisasi harga di pasar pembuat rugi.</p>
            <p><b>Owner:</b> Chief Strategy Officer & Regional Managers</p>
            <p><b>KPI:</b> Peningkatan profit di wilayah rugi sebesar 25%</p>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.divider()
st.caption("Global Superstore Analytics Dashboard | Developed with Streamlit & Plotly")
