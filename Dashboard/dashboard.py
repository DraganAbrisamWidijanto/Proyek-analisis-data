import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import folium
from folium.plugins import MarkerCluster

# Fungsi untuk memuat data
def load_data():
    rfm_df = pd.read_csv('Dashboard/rfm_df.csv')
    sorted_heatmap_data_clean = pd.read_csv('Dashboard/sorted_heatmap_data_clean.csv')
    return rfm_df, sorted_heatmap_data_clean

# Fungsi untuk memplot distribusi RFM
def plot_rfm_distribution(rfm_df):
    category_counts = rfm_df['Customer_Category'].value_counts().reset_index()
    category_counts.columns = ['Customer_Category', 'Count']

    plt.figure(figsize=(10, 6))
    bar_plot = sns.barplot(data=category_counts, x='Customer_Category', y='Count', palette='muted')
    plt.title('Distribusi Pelanggan Berdasarkan Kategori RFM', fontsize=16)
    plt.xlabel('Kategori Pelanggan', fontsize=14)
    plt.ylabel('Jumlah Pelanggan', fontsize=14)

    for p in bar_plot.patches:
        bar_plot.annotate(f'{int(p.get_height())}',
                          (p.get_x() + p.get_width() / 2., p.get_height()),
                          ha='center', va='bottom',
                          fontsize=12, color='black', 
                          xytext=(0, 0), textcoords='offset points')

    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(plt)
    plt.clf()  # Membersihkan figure untuk plot berikutnya

# Fungsi untuk memplot 10 kota dengan rata-rata nilai pembayaran tertinggi
def plot_top_cities(sorted_heatmap_data_clean):
    plt.figure(figsize=(16, 10))  # Memperbesar ukuran figura

    top_10_cities = sorted_heatmap_data_clean.sort_values(by='payment_value', ascending=False).head(10)

    bar_plot = sns.barplot(data=top_10_cities,
                           x='geolocation_city',
                           y='payment_value',
                           hue='geolocation_state',
                           palette='muted')

    plt.title('10 Kota dengan Rata-rata Nilai Pembayaran Tertinggi di Brasil', fontsize=16)
    plt.xlabel('Kota', fontsize=14)
    plt.ylabel('Rata-rata Nilai Pembayaran', fontsize=14)

    for p in bar_plot.patches:
        bar_plot.annotate(f'{p.get_height():.2f}',
                          (p.get_x() + p.get_width() / 2., p.get_height()),
                          ha='center', va='bottom',
                          fontsize=10, color='black', 
                          xytext=(0, 5), textcoords='offset points')

    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.legend(title='Negara Bagian', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
    st.pyplot(plt)
    plt.clf()  # Membersihkan figure untuk plot berikutnya

# Fungsi untuk membuat peta penyebaran pembayaran
def create_map(sorted_heatmap_data_clean):
    map_center = [-15.7801, -47.9292]
    my_map = folium.Map(location=map_center, zoom_start=4)
    marker_cluster = MarkerCluster().add_to(my_map)
    
    for _, row in sorted_heatmap_data_clean.iterrows():
        folium.CircleMarker(location=[row['geolocation_lat'], row['geolocation_lng']],
                            radius=row['payment_value'] / 100,
                            color='blue', fill=True, fill_color='blue',
                            fill_opacity=0.6,
                            popup=f"{row['geolocation_city']}: {row['payment_value']:.2f}"
                           ).add_to(marker_cluster)

    return my_map

# Main application
def main():
    # Sidebar content
    st.sidebar.image("https://media.licdn.com/dms/image/v2/D5612AQGDDZFCAumQsg/article-cover_image-shrink_720_1280/article-cover_image-shrink_720_1280/0/1680677375849?e=2147483647&v=beta&t=5YkPYXmRLOqryF-CP9c7U20tHqyuYjmRMFqFdSwLwTQ", use_column_width=True)
    st.sidebar.header('Proyek Analisis Data')
    st.sidebar.markdown("**E-Commerce Public Dataset** (Brazilian E-Commerce Public Dataset by Olist)")
    st.sidebar.markdown("Dibuat oleh:")
    st.sidebar.markdown("- **Nama:** Dragan Abrisam Widijanto")

    # Load data
    rfm_df, sorted_heatmap_data_clean = load_data()

    # Analisis Pelanggan Berdasarkan Kategori RFM
    st.title('Analisis Pelanggan dan Pembayaran di Brasil')

    with st.container():
        st.header('Distribusi Pelanggan Berdasarkan Kategori RFM')
        plot_rfm_distribution(rfm_df)
        with st.expander("Insight"):
            st.markdown("Dari analisis RFM, kami menemukan bahwa Low Value Customers adalah kategori pelanggan yang paling banyak, dengan total 45.916 pelanggan. Hal ini menunjukkan adanya peluang untuk meningkatkan engagement dengan mereka. Angka ini kami peroleh melalui pengelompokan manual berdasarkan nilai Monetary dan Recency.")

    # 10 Kota dengan Rata-rata Nilai Pembayaran Tertinggi di Brasil
    with st.container():
        st.header('10 Kota dengan Rata-rata Nilai Pembayaran Tertinggi di Brasil')
        plot_top_cities(sorted_heatmap_data_clean)
        with st.expander("Insight"):
            st.markdown("Dari analisis visualisasi, terlihat bahwa Araguari, MG menonjol sebagai kota dengan kontribusi nilai pembayaran tertinggi, mencapai 2416. Ini menunjukkan bahwa pelanggan di Araguari bersedia menghabiskan lebih banyak untuk produk atau layanan yang ditawarkan, menciptakan peluang signifikan bagi perusahaan untuk meningkatkan strategi pemasaran di wilayah ini. Perhatian juga harus diberikan kepada kota-kota lain yang berkontribusi tinggi, seperti Rio de Janeiro, RJ dan Sao Paulo, SP dengan rata-rata nilai pembayaran masing-masing 2.337 dan 2.328")
    
    # Peta Penyebaran Pembayaran di Brasil
    with st.container():
        st.header('Peta Penyebaran Pembayaran di Brasil')
        my_map = create_map(sorted_heatmap_data_clean)   
        # Menyusun peta
        st.components.v1.html(my_map._repr_html_(), height=500)   
        # Insight dalam expander
        with st.expander("Insight"):
            st.markdown("""
            ### Insight Peta
            Peta interaktif ini menggambarkan lokasi-lokasi pelanggan di Brasil berdasarkan kontribusi mereka terhadap nilai pembayaran. Kota-kota dengan kontribusi pembayaran tertinggi, seperti Piancó, PB dan São Sebastião, AL, dapat digunakan untuk mengidentifikasi pasar potensial yang kuat.
            """)


if __name__ == "__main__":
    main()
