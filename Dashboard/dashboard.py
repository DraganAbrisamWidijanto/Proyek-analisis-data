import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import folium
from folium.plugins import MarkerCluster
import matplotlib.dates as mdates  # Importing mdates

# Fungsi untuk memuat data
def load_data():
    rfm_df = pd.read_csv('Dashboard/rfm_df.csv')
    sorted_heatmap_data_clean = pd.read_csv('Dashboard/sorted_heatmap_data_clean.csv')
    Monthly_Order_Counts = pd.read_csv('Dashboard/monthly_order_counts.csv')
    payment_type_counts = pd.read_csv('Dashboard/payment_type_counts.csv')

    # Load state_counts and set it up properly
    state_counts_df = pd.read_csv('Dashboard/state_counts.csv')
    state_counts = state_counts_df.set_index('customer_state')['count']
    state_counts = state_counts.squeeze()  # Convert DataFrame to Series if it's 1D

    # Creating a DataFrame for monthly orders
    monthly_order_counts = Monthly_Order_Counts.copy()
    monthly_order_counts['year_month'] = pd.to_datetime(monthly_order_counts['year_month'], format='%Y-%m')  # Specify the format
    monthly_order_counts.set_index('year_month', inplace=True)

    return rfm_df, sorted_heatmap_data_clean, monthly_order_counts, payment_type_counts, state_counts


def plot_monthly_order_counts(monthly_order_counts):
    plt.figure(figsize=(12, 6))
    monthly_order_counts['count'].plot(kind='line', marker='o')  # Ensure this accesses the correct 'count' column
    
    # Title and labels
    plt.title('Monthly Order Counts', fontsize=16)
    plt.xlabel('Year-Month', fontsize=14)
    plt.ylabel('Number of Orders', fontsize=14)

    plt.grid(True)

    # Set up date formatting for the x-axis
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))  # Format x-axis as YYYY-MM
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())  # Set locator for monthly ticks

    # Set x-ticks to only show ticks at the positions of the data points
    plt.xticks(monthly_order_counts.index, rotation=45)  # Set ticks to the index values

    plt.tight_layout()
    
    st.pyplot(plt)  # Display the plot in Streamlit
    plt.clf()  # Clear figure for the next plots


# Function to plot payment type distribution
def plot_payment_type_distribution(payment_type_counts):
    plt.figure(figsize=(10, 10))  # Size of the figure

    # Ensure payment_type_counts is a Series with numeric values
    payment_counts = payment_type_counts['count']  # Extract the count column
    payment_types = payment_type_counts['payment_type']  # Extract the payment type column

    # Create the pie chart with percentages inside
    wedges, texts, autotexts = plt.pie(
        payment_counts,
        startangle=90,
        autopct='%1.1f%%',  # Percentage inside the pie
        colors=plt.cm.tab10.colors,  # Color map for better diversity
        labels=[""] * len(payment_types)  # Remove labels from the chart
    )

    # Prepare legend labels with percentages included
    legend_labels = [f"{payment_type}: {count/sum(payment_counts)*100:.1f}%" for payment_type, count in zip(payment_types, payment_counts)]

    # Create legend with payment types and their percentages
    plt.legend(legend_labels, title="Payment Types", loc="upper left", bbox_to_anchor=(1, 1))

    # Title for the pie chart
    plt.title('Distribution of Payment Types')

    # Equal aspect ratio ensures that the pie is drawn as a circle
    plt.axis('equal')

    plt.tight_layout()
    st.pyplot(plt)  # Display the plot in Streamlit
    plt.clf()  # Clear figure for future plots



def plot_top_states(state_counts):
    plt.figure(figsize=(10, 6))
    top_states = state_counts.nlargest(5)  # Get the top 5 states

    # Set color to blue for all bars
    sns.barplot(x=top_states.index, y=top_states.values, color='lightblue')  # Use a single color

    plt.title('Top 5 Kota Berdasarkan Banyaknya Customer', fontsize=16)
    plt.xlabel('State', fontsize=14)
    plt.ylabel('Number of Customers', fontsize=14)
    plt.xticks(rotation=45)  # Rotate x labels for better visibility
    plt.tight_layout()
    
    st.pyplot(plt)  # Display the plot in Streamlit
    plt.clf()  # Clear figure for next plots


# Fungsi untuk memplot distribusi RFM
def plot_rfm_distribution(rfm_df):
    category_counts = rfm_df['Customer_Category'].value_counts().reset_index()
    category_counts.columns = ['Customer_Category', 'Count']

    plt.figure(figsize=(10, 6))
    bar_plot = sns.barplot(data=category_counts, x='Customer_Category', y='Count', color='lightblue')  # Change 'palette' to 'color'

    plt.title('Distribusi Pelanggan Berdasarkan Kategori RFM', fontsize=16)
    plt.xlabel('Kategori Pelanggan', fontsize=14)
    plt.ylabel('Jumlah Pelanggan', fontsize=14)

    # Annotate bars with the counts
    for p in bar_plot.patches:
        bar_plot.annotate(f'{int(p.get_height())}',
                          (p.get_x() + p.get_width() / 2., p.get_height()),
                          ha='center', va='bottom',
                          fontsize=12, color='black', 
                          xytext=(0, 0), textcoords='offset points')

    plt.xticks(rotation=45)
    plt.tight_layout()
    
    st.pyplot(plt)  # Display the plot in Streamlit
    plt.clf()  # Clear figure for next plots


# Fungsi untuk memplot 10 kota dengan rata-rata nilai pembayaran tertinggi
def plot_top_cities(sorted_heatmap_data_clean):
    plt.figure(figsize=(16, 10))  # Memperbesar ukuran figura

    # Mengambil 10 kota teratas berdasarkan nilai pembayaran
    top_10_cities = sorted_heatmap_data_clean.sort_values(by='payment_value', ascending=False).head(10)

    # Buat kolom baru untuk nama kota dan negara bagian
    top_10_cities['city_state'] = top_10_cities['geolocation_city'] + ', ' + top_10_cities['geolocation_state']

    # Set warna biru untuk semua batang dan hapus legend
    bar_plot = sns.barplot(data=top_10_cities,
                           x='city_state',  # Menggunakan kolom baru
                           y='payment_value',
                           color='lightblue')  # Set warna tunggal untuk semua batang

    plt.title('10 Kota dengan Rata-rata Nilai Pembayaran Tertinggi di Brasil', fontsize=16)
    plt.xlabel('Kota, Negara Bagian', fontsize=14)
    plt.ylabel('Rata-rata Nilai Pembayaran', fontsize=14)

    # Annotate bars dengan nilainya
    for p in bar_plot.patches:
        bar_plot.annotate(f'{p.get_height():.2f}',
                          (p.get_x() + p.get_width() / 2., p.get_height()),
                          ha='center', va='bottom',
                          fontsize=10, color='black', 
                          xytext=(0, 5), textcoords='offset points')

    plt.xticks(rotation=45)
    plt.tight_layout()

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
    rfm_df, sorted_heatmap_data_clean, Monthly_Order_Counts, payment_type_counts, state_counts = load_data()

    # Analisis Pelanggan Berdasarkan Kategori RFM
    st.title('Analisis Pelanggan dan Pembayaran di Brasil')

    # Analysis of Monthly Order Counts
    with st.container():
        st.header('Jumlah Pesanan Bulanan')
        plot_monthly_order_counts(Monthly_Order_Counts)
        with st.expander("Insight"):
            st.markdown("Tren penjualan antara tahun 2016 hingga 2018 menunjukkan adanya pertumbuhan yang signifikan, terutama sejak Maret 2017. Meskipun volume pesanan mengalami fluktuasi, umumnya menunjukkan kecenderungan naik yang stabil. Penurunan di bulan Desember 2017, yang kemungkinan disebabkan oleh faktor musiman, tidak menghentikan pertumbuhan keseluruhan, melainkan memperlihatkan bahwa bisnis dapat mempertahankan pelanggan setelah periode puncak.")

    # Analysis of Payment Type Distribution
    with st.container():
        st.header('Distribusi Jenis Pembayaran')
        plot_payment_type_distribution(payment_type_counts)
        with st.expander("Insight"):
            st.markdown("Dari analisis, metode pembayaran menggunakan kartu kredit muncul sebagai yang paling efektif dan populer, dengan jumlah transaksi yang tinggi. Dalam merancang strategi promosi, bisnis harus mempertimbangkan pengoptimalan kampanye pemasaran yang memanfaatkan preferensi pelanggan terhadap kartu kredit, sekaligus memberikan kemudahan dan kenyamanan dalam proses pembayaran.")

    # Analysis of Top States by Customer Count
    with st.container():
        st.header('Top 5 Kota Berdasarkan Banyaknya Customer')
        plot_top_states(state_counts)
        with st.expander("Insight"):
            st.markdown("São Paulo, sebagai kota dengan jumlah pelanggan terbesar, menunjukkan potensi pasar yang signifikan didukung oleh populasi yang padat dan status ekonominya. Kota-kota lainnya seperti Rio de Janeiro dan Minas Gerais juga menunjukkan potensi pasar yang tinggi. Fokus pada pengembangan strategi pemasaran di kawasan-kawasan ini dapat meningkatkan penetrasi pasar dan mendatangkan lebih banyak pelanggan.")


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
