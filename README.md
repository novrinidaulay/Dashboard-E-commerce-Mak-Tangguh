# Dashboard Analisis Data E-commerce ✨

Dashboard interaktif ini dibangun menggunakan Streamlit untuk memvisualisasikan analisis utama dari dataset E-commerce Brasil. Visualisasi mencakup analisis produk terlaris, distribusi pelanggan per negara bagian, dan ringkasan segmentasi pelanggan (RFM).

# Prasyarat

Python 3.x
Anaconda / Miniconda terinstal.

# Struktur Proyek
Pastikan direktori proyek Anda memiliki struktur sebagai berikut:

.
├── dashboard.py          
├── requirements.txt      
├── customers_per_state_data.csv
├── product_sales_viz_data.csv
└── rfm_segment_summary_data.csv

# Cara Menjalankan Secara Lokal

1. Kloning Repositori
Bash

git clone https://github.com/novrinidaulay/Dashboard-E-commerce-Mak-Tangguh.git
cd Dashboard-E-commerce-Mak-Tangguh

2. Penyiapan Environment

conda activate main-ds 
pip install -r requirements.txt

4. Menjalankan Dashboard
Jalankan script Streamlit dari terminal:

streamlit run dashboard.py
Setelah perintah dijalankan, dashboard akan terbuka otomatis di browser default Anda pada alamat http://localhost:8501.


