import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Mengatur konfigurasi halaman Streamlit
st.set_page_config(
    page_title="E-commerce Data Analysis Dashboard (Interaktif)",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Fungsi untuk Memuat Data (Menggunakan cache untuk performa) ---
@st.cache_data
def load_data():
    """Memuat dan memproses data dari file CSV yang sudah diolah."""
    # Q1: Analisis Produk
    product_sales_df = pd.read_csv("product_sales_viz_data.csv")
    
    # Agregasi total pesanan per kategori produk (menggunakan nama Inggris)
    category_sales = product_sales_df.groupby('product_category_name_english').agg(
        order_count=('order_count', 'sum')
    ).sort_values(by="order_count", ascending=False).reset_index()

    # Q2: Analisis Pelanggan per Negara Bagian
    customers_per_state_df = pd.read_csv("customers_per_state_data.csv")
    customers_per_state_df = customers_per_state_df.sort_values(by='unique_customer_count', ascending=False).reset_index(drop=True)
    
    # RFM: Ringkasan Segmentasi
    rfm_df = pd.read_csv("rfm_segment_summary_data.csv")
    rfm_df.set_index('RFM_Segment', inplace=True)
    rfm_df = rfm_df.sort_values(by='SegmentSize', ascending=False)

    return category_sales, customers_per_state_df, rfm_df

category_sales_df, customers_per_state_df, rfm_df = load_data()


# ====================================================================
# --- SIDEBAR INTERAKTIF ---
# ====================================================================
# Link gambar dari GitHub
IMAGE_URL = "https://github.com/novrinidaulay/Dashboard-E-commerce-Mak-Tangguh/blob/15202477e9b526d4a05e495626210bbe75436e0c/emak%20tangguh.png?raw=true"
GITHUB_LINK = "https://github.com/novrinidaulay/Dashboard-E-commerce-Mak-Tangguh"

# Tampilkan gambar di sidebar
st.sidebar.image(IMAGE_URL, use_container_width=True)

# Tambahkan tautan GitHub di bawah gambar menggunakan Markdown
st.sidebar.markdown(f"**[Lihat di GitHub](<{GITHUB_LINK}>)**", unsafe_allow_html=True)

st.sidebar.title("Pengaturan Dashboard")
st.sidebar.markdown("Atur jumlah data yang ditampilkan untuk visualisasi Top/Bottom N.")

# Input interaktif untuk Q1: Produk
st.sidebar.subheader("Produk Terjual")
top_n_products = st.sidebar.slider(
    "Pilih Jumlah Top/Bottom Kategori Produk:", 
    min_value=5, 
    max_value=20, 
    value=10, 
    step=1
)

# Input interaktif untuk Q2: Pelanggan
st.sidebar.subheader("Pelanggan per Negara Bagian")
top_n_states = st.sidebar.slider(
    "Pilih Jumlah Top Negara Bagian:", 
    min_value=5, 
    max_value=27, # Total negara bagian
    value=10, 
    step=1
)

# Input interaktif untuk Q3: RFM (Opsional, untuk detail segmen)
st.sidebar.subheader("Segmentasi RFM")
rfm_segments = rfm_df.index.tolist()
selected_rfm_segment = st.sidebar.selectbox(
    "Pilih Segmen RFM untuk Detail Ringkas:",
    options=['Semua Segmen'] + rfm_segments
)


# ====================================================================
# --- KONTEN UTAMA DASHBOARD ---
# ====================================================================

# --- Judul Dashboard ---
st.title("Dashboard Analisis Data E-commerce 🛍️")
st.markdown("Dashboard interaktif ini menyajikan analisis utama E-commerce Brasil.")
st.markdown("---")

# --- 1. Analisis Kategori Produk (Q1) ---
st.header(f"1. Top {top_n_products} Kategori Produk Terlaris & Paling Sedikit Terjual")

col1, col2 = st.columns(2)

with col1:
    st.subheader(f"Top {top_n_products} Kategori Terlaris")
    top_categories = category_sales_df.head(top_n_products)
    
    # Visualisasi Top N
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.barplot(
        x="order_count", 
        y="product_category_name_english", 
        data=top_categories, 
        palette=sns.color_palette("viridis", n_colors=top_n_products),
        ax=ax
    )
    ax.set_title(f"Top {top_n_products} Kategori Produk Paling Banyak Terjual", fontsize=14)
    ax.set_xlabel("Jumlah Pesanan", fontsize=12)
    ax.set_ylabel("Kategori Produk (English)", fontsize=12)
    plt.tight_layout()
    st.pyplot(fig)

with col2:
    st.subheader(f"Bottom {top_n_products} Kategori Terjual")
    bottom_categories = category_sales_df.tail(top_n_products).sort_values(by='order_count', ascending=True)
    
    # Visualisasi Bottom N
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.barplot(
        x="order_count", 
        y="product_category_name_english", 
        data=bottom_categories, 
        palette=sns.color_palette("rocket_r", n_colors=top_n_products),
        ax=ax
    )
    ax.set_title(f"Bottom {top_n_products} Kategori Produk Paling Sedikit Terjual", fontsize=14)
    ax.set_xlabel("Jumlah Pesanan", fontsize=12)
    ax.set_ylabel("Kategori Produk (English)", fontsize=12)
    plt.tight_layout()
    st.pyplot(fig)


st.markdown("---")

# --- 2. Analisis Jumlah Pelanggan per Negara Bagian (Q2) ---
st.header(f"2. Top {top_n_states} Negara Bagian dengan Jumlah Pelanggan Terbanyak")

# Filter data berdasarkan slider
top_states = customers_per_state_df.head(top_n_states)

# Visualisasi Top N Negara Bagian
fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(
    x='unique_customer_count', 
    y='customer_state', 
    data=top_states, 
    palette=sns.color_palette("mako", n_colors=top_n_states),
    ax=ax
)
ax.set_title(f"Top {top_n_states} Negara Bagian dengan Pelanggan Terbanyak", fontsize=15)
ax.set_xlabel("Jumlah Pelanggan Unik", fontsize=12)
ax.set_ylabel("Negara Bagian (State)", fontsize=12)
plt.tight_layout()
st.pyplot(fig)

st.markdown("---")

# --- 3. Ringkasan Analisis RFM ---
st.header("3. Ringkasan Segmentasi Pelanggan (RFM)")

# Tampilkan ringkasan segmen RFM
st.subheader("Tabel Ringkasan Segmen")
st.dataframe(
    rfm_df.style.format({
        'AvgRecency': "{:.0f} hari",
        'AvgFrequency': "{:.2f}",
        'AvgMonetary': "R$ {:.2f}",
        'SegmentSize': "{:,}"
    }), 
    use_container_width=True
)

st.caption("Tabel diurutkan dari segmen dengan jumlah pelanggan terbanyak.")

# Visualisasi Ukuran Segmen
st.subheader("Distribusi Ukuran Segmen RFM")
fig, ax = plt.subplots(figsize=(10, 6))
rfm_size_df = rfm_df.reset_index()

# Membuat palet warna yang konsisten
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
sns.barplot(
    x='SegmentSize', 
    y='RFM_Segment', 
    data=rfm_size_df, 
    palette=colors[:len(rfm_size_df)],
    ax=ax
)
ax.set_title("Jumlah Pelanggan per Segmen RFM", fontsize=15)
ax.set_xlabel("Jumlah Pelanggan", fontsize=12)
ax.set_ylabel("Segmen RFM", fontsize=12)
plt.tight_layout()
st.pyplot(fig)


# Detail Segmen yang Dipilih dari Sidebar
if selected_rfm_segment != 'Semua Segmen':
    st.markdown("---")
    st.subheader(f"Detail Segmen: {selected_rfm_segment}")
    segment_data = rfm_df.loc[selected_rfm_segment]
    
    st.markdown(f"""
    <div style='border: 1px solid #ddd; padding: 15px; border-radius: 5px;'>
        <p><strong>Jumlah Pelanggan:</strong> {segment_data['SegmentSize']:,} orang</p>
        <p><strong>Rata-rata Recency (Hari Sejak Pembelian Terakhir):</strong> {segment_data['AvgRecency']:.0f} hari</p>
        <p><strong>Rata-rata Frequency (Jumlah Pesanan):</strong> {segment_data['AvgFrequency']:.2f}</p>
        <p><strong>Rata-rata Monetary (Pengeluaran):</strong> R$ {segment_data['AvgMonetary']:.2f}</p>
    </div>
    """, unsafe_allow_html=True)
