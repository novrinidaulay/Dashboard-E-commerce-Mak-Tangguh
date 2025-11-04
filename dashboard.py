import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, date

# Menambahkan Judul Dashboard
st.title('Dashboard Analisis Data E-commerce Mak Tangguh')

# --- Fungsi Helper untuk Memuat Data (dengan Caching) ---
@st.cache_data 
def load_prepared_data(product_sales_path, customers_state_path, rfm_summary_path, combined_data_path):
    """
    Loads the prepared dataframes from CSV files.
    """
    product_sales_viz_df = pd.read_csv(product_sales_path)
    customers_per_state_viz = pd.read_csv(customers_state_path)
    rfm_segment_analysis_sorted_size = pd.read_csv(rfm_summary_path)
    all_data_combined_df = pd.read_csv(combined_data_path)

    # Konversi kolom date columns ke datetime 
    all_data_combined_df['order_purchase_timestamp'] = pd.to_datetime(all_data_combined_df['order_purchase_timestamp'])
    return {
        'product_sales_viz_df': product_sales_viz_df,
        'customers_per_state_viz': customers_per_state_viz,
        'rfm_segment_analysis_sorted_size': rfm_segment_analysis_sorted_size,
        'all_data_combined_df': all_data_combined_df
    }

# --- Fungsi Helper untuk Mendapatkan N Produk Teratas/Terbawah ---
def get_top_least_sold_products(product_sales_df, n=10):
    """
    Gets the top N and least N sold products based on order count.
    """
    if 'order_count' not in product_sales_df.columns:
        st.error("Error: 'order_count' column not found in the DataFrame for top/least products.")
        return None, None

    top_n_products_df = product_sales_df.sort_values(by='order_count', ascending=False).head(n).reset_index(drop=True)
    least_n_products_df = product_sales_df.sort_values(by='order_count', ascending=True).head(n).reset_index(drop=True)

    return top_n_products_df, least_n_products_df

# --- Fungsi Helper untuk Mendapatkan Distribusi Pelanggan per Negara Bagian ---
def get_customers_per_state_distribution(customers_state_df):
    """
    Gets the customer distribution data per state.
    """
    if 'customer_state' not in customers_state_df.columns or 'unique_customer_count' not in customers_state_df.columns:
        st.error("Error: Required columns ('customer_state', 'unique_customer_count') not found in the customer state DataFrame.")
        return None

    # DataFrame tersebut sudah dalam format yang diinginkan
    return customers_state_df

# --- Fungsi Helper untuk Mendapatkan Ringkasan Segmen RFM ---
def get_rfm_segment_summary(rfm_summary_df):
    """
    Gets the RFM segment summary data.
    """
    required_cols = ['RFM_Segment', 'AvgRecency', 'AvgFrequency', 'AvgMonetary', 'SegmentSize']
    if not all(col in rfm_summary_df.columns for col in required_cols):
         st.error(f"Error: Required columns ({required_cols}) not found in the RFM summary DataFrame.")
         return None

    # DataFrame tersebut sudah dalam format yang diinginkan
    return rfm_summary_df


# --- Muat Data ---
# Ganti dengan path file CSV 
data_paths = {
    'product_sales': 'product_sales_viz_data.csv',
    'customers_state': 'customers_per_state_data.csv',
    'rfm_summary': 'rfm_segment_summary_data.csv',
    'combined_data': 'all_data_combined.csv' # Diperlukan jika menggunakan filter tanggal pada data utama
}
try:
    prepared_data = load_prepared_data(
        data_paths['product_sales'],
        data_paths['customers_state'],
        data_paths['rfm_summary'],
        data_paths['combined_data']
    )
    # Akses DataFrame yang dimuat
    product_sales_viz_df = prepared_data['product_sales_viz_df']
    customers_per_state_viz = prepared_data['customers_per_state_viz']
    rfm_segment_analysis_sorted_size = prepared_data['rfm_segment_analysis_sorted_size']
    all_data_combined_df = prepared_data['all_data_combined_df'].copy() # Gunakan copy() untuk filtering agar data asli tidak berubah

    st.success("Data berhasil dimuat!") # Opsional: pesan sukses

except FileNotFoundError:
    st.error("Pastikan file CSV berada di lokasi yang benar.")
    st.stop() # Hentikan eksekusi jika file tidak ditemukan


# --- Komponen Filter di Sidebar ---
with st.sidebar: # Tambahkan logo di dalam blok sidebar
    # Menambahkan logo perusahaan menggunakan path local
    st.image("https://github.com/novrinidaulay/Dashboard-E-commerce-Mak-Tangguh/blob/15202477e9b526d4a05e495626210bbe75436e0c/emak%20tangguh.png?raw=true")

    st.header('Filter Data')

    # Filter 1: Rentang Waktu Pesanan
    try:
        # Ensure the date column exists before attempting conversion
        if 'order_purchase_timestamp' in all_data_combined_df.columns:
            all_data_combined_df['order_purchase_timestamp'] = pd.to_datetime(all_data_combined_df['order_purchase_timestamp'])
            min_date = all_data_combined_df['order_purchase_timestamp'].min().date()
            max_date = all_data_combined_df['order_purchase_timestamp'].max().date()

            start_date, end_date = st.date_input( # Gunakan st.date_input karena sudah di dalam with st.sidebar
                label='Pilih Tanggal',
                min_value=min_date,
                max_value=max_date,
                value=[min_date, max_date]
            )

            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.max.time())

            # Apply date filter
            filtered_combined_df = all_data_combined_df[
               (all_data_combined_df['order_purchase_timestamp'] >= start_datetime) &
               (all_data_combined_df['order_purchase_timestamp'] <= end_datetime)
            ].copy()
        else:
            st.warning("Kolom 'order_purchase_timestamp' tidak ditemukan di data gabungan untuk filter tanggal.")
            filtered_combined_df = all_data_combined_df.copy() 
    except Exception as e:
        st.error(f"Error applying date filter: {e}")
        st.stop() # Stop if date filter fails

    # Filter 2: Negara Bagian Pelanggan
    if 'customer_state' in filtered_combined_df.columns:
        all_states = sorted(filtered_combined_df['customer_state'].unique().tolist())
        selected_states = st.multiselect('Pilih Negara Bagian', all_states, default=all_states) # Gunakan st.multiselect

        if selected_states:
            filtered_combined_df = filtered_combined_df[filtered_combined_df['customer_state'].isin(selected_states)].copy()
        else:
            st.warning("Pilih setidaknya satu Negara Bagian.")
            # Optionally stop or show empty state if no state is selected
            # st.stop()
            filtered_combined_df = pd.DataFrame(columns=filtered_combined_df.columns) # Show empty dataframe


    # Filter 3: Kategori Produk
    if 'product_category_name_english' in filtered_combined_df.columns:
        all_categories = sorted(filtered_combined_df['product_category_name_english'].unique().tolist())
        selected_categories = st.multiselect('Pilih Kategori Produk', all_categories, default=all_categories) # Gunakan st.multiselect

        if selected_categories:
            filtered_combined_df = filtered_combined_df[filtered_combined_df['product_category_name_english'].isin(selected_categories)].copy()
        else:
            st.warning("Pilih setidaknya satu Kategori Produk.")
            # Optionally stop or show empty state
            # st.stop()
            filtered_combined_df = pd.DataFrame(columns=filtered_combined_df.columns) # Show empty dataframe


# --- Tampilkan Data Pesanan yang Difilter (Opsional) ---
# st.subheader('Data Pesanan yang Difilter (Preview)')
# st.write(f"Menampilkan data dari {start_date.date()} hingga {end_date.date()}")
# st.dataframe(filtered_combined_df.head()) # Tampilkan head dari dataframe yang difilter
# st.write(f"Jumlah baris data setelah filter: {len(filtered_combined_df)}")


# --- Bagian 1: Produk Paling Laris/Kurang Laris ---
# NOTE: Visualisasi produk terlaris/kurang laris di sini saat ini TIDAK difilter oleh filter sidebar
# karena menggunakan product_sales_viz_df yang sudah dihitung sebelumnya dari data UTUH.

st.subheader("Analisis Produk Terlaris dan Kurang Laris (Data Keseluruhan)")

# Ambil data produk teratas dan terbawah menggunakan fungsi helper
top_n = st.slider("Jumlah Produk Teratas/Terbawah", 5, 20, 10) # Slider untuk memilih N
top_products, least_products = get_top_least_sold_products(product_sales_viz_df, n=top_n) # Menggunakan data UTUH

if top_products is not None and least_products is not None:
    col1, col2 = st.columns(2) # Gunakan kolom untuk tata letak berdampingan

    with col1:
        st.write(f"**Top {top_n} Produk Paling Laris (Berdasarkan Jumlah Pesanan - Data Keseluruhan)**")
        st.dataframe(top_products) # Tampilkan dalam tabel

        # Visualisasikan dengan bar plot (contoh menggunakan matplotlib/seaborn)
        fig1, ax1 = plt.subplots(figsize=(10, 6))
        sns.barplot(x='order_count', y='product_category_name_english', data=top_products, ax=ax1, palette='viridis')
        ax1.set_title(f'Top {top_n} Most Sold Product Categories')
        ax1.set_xlabel('Number of Orders')
        ax1.set_ylabel('Product Category')
        plt.tight_layout()
        st.pyplot(fig1)

    with col2:
        st.write(f"**Top {top_n} Produk Paling Sedikit Terjual (Berdasarkan Jumlah Pesanan - Data Keseluruhan)**")
        st.dataframe(least_products) # Tampilkan dalam tabel

        # Visualisasikan dengan bar plot
        fig2, ax2 = plt.subplots(figsize=(10, 6))
        sns.barplot(x='order_count', y='product_category_name_english', data=least_products, ax=ax2, palette='viridis')
        ax2.set_title(f'Top {top_n} Least Sold Product Categories')
        ax2.set_xlabel('Number of Orders')
        ax2.set_ylabel('Product Category')
        plt.tight_layout()
        st.pyplot(fig2)


# --- Bagian 2: Penjualan per Negara Bagian ---
st.subheader("Penjualan (Revenue) per Negara Bagian (Difilter)")

# Hitung total payment value per state dari filtered_combined_df (jika filter tanggal relevan)
# Atau dari all_data_combined_df jika filter tanggal tidak relevan untuk visualisasi ini
# Di sini kita gunakan data yang sudah difilter tanggal, negara bagian, dan kategori (filtered_combined_df)
# Pastikan kolom payment_value ada dan numerik
if 'payment_value' in filtered_combined_df.columns:
    # Handle potential non-numeric payment_value if necessary (should be numeric after loading/cleaning)
    # filtered_combined_df['payment_value'] = pd.to_numeric(filtered_combined_df['payment_value'], errors='coerce')
    # filtered_combined_df.dropna(subset=['payment_value'], inplace=True) # Drop rows if conversion failed

    # Check if filtered_combined_df is not empty before grouping
    if not filtered_combined_df.empty:
        sales_per_state = filtered_combined_df.groupby('customer_state')['payment_value'].sum().reset_index()
        sales_per_state_sorted = sales_per_state.sort_values(by='payment_value', ascending=False)

        st.write("**Total Revenue per State (Filtered by Date, State, Category)**")
        # Tampilkan tabel top 10 negara bagian berdasarkan revenue
        st.dataframe(sales_per_state_sorted.head(10))

        fig3, ax3 = plt.subplots(figsize=(12, 7))
        # Tampilkan top 10 negara bagian berdasarkan revenue
        sns.barplot(x='payment_value', y='customer_state', data=sales_per_state_sorted.head(10), ax=ax3, palette='viridis')
        ax3.set_title('Top 10 States by Total Sales Revenue')
        ax3.set_xlabel('Total Sales Revenue')
        ax3.set_ylabel('State')
        plt.tight_layout()
        st.pyplot(fig3)
    else:
        st.warning("Tidak ada data yang cocok dengan filter yang dipilih.")

else:
    st.warning("Kolom 'payment_value' tidak ditemukan di DataFrame gabungan yang difilter.")


# --- Bagian 3: Hasil Analisis RFM ---
# NOTE: Visualisasi RFM summary di sini saat ini TIDAK difilter oleh filter sidebar
# karena menggunakan rfm_segment_analysis_sorted_size yang sudah dihitung sebelumnya dari data UTUH pelanggan.

st.subheader("Ringkasan Segmen Pelanggan RFM (Data Keseluruhan)")

# Ambil data ringkasan RFM menggunakan fungsi helper
rfm_summary_data = get_rfm_segment_summary(rfm_segment_analysis_sorted_size) # Menggunakan data UTUH

if rfm_summary_data is not None:
    st.write("**Karakteristik Segmen RFM**")
    st.dataframe(rfm_summary_data) # Tampilkan tabel ringkasan

    # Contoh visualisasi ukuran segmen
    fig4, ax4 = plt.subplots(figsize=(10, 6))
    sns.barplot(x='SegmentSize', y='RFM_Segment', data=rfm_summary_data.sort_values(by='SegmentSize', ascending=False), ax=ax4, palette='coolwarm')
    ax4.set_title('RFM Segment Size Distribution')
    ax4.set_xlabel('Number of Customers')
    ax4.set_ylabel('RFM Segment')
    plt.tight_layout()
    st.pyplot(fig4)

else:
     st.warning("Data ringkasan RFM tidak tersedia.")

# --- Bagian Tambahan: Visualisasi Distribusi Tipe Pembayaran ---
# NOTE: Visualisasi ini DIFILTER oleh filter sidebar karena menggunakan filtered_combined_df
st.subheader("Distribusi Tipe Pembayaran (Difilter)")

# Ambil data tipe pembayaran dari filtered_combined_df
if 'payment_type' in filtered_combined_df.columns:
    # Check if filtered_combined_df is not empty before plotting
    if not filtered_combined_df.empty and not filtered_combined_df['payment_type'].isnull().all():
        # Count the occurrences of each payment type
        payment_type_counts = filtered_combined_df['payment_type'].value_counts()

        fig6, ax6 = plt.subplots(figsize=(10, 6))
        sns.barplot(x=payment_type_counts.index, y=payment_type_counts.values, ax=ax6, palette='viridis')
        ax6.set_title('Distribution of Payment Types')
        ax6.set_xlabel('Payment Type')
        ax6.set_ylabel('Number of Transactions')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig6)
    else:
        st.warning("Tidak ada data tipe pembayaran yang cocok dengan filter yang dipilih.")
else:
    st.warning("Kolom 'payment_type' tidak ditemukan di DataFrame gabungan yang difilter.")
