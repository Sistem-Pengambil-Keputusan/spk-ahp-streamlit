import streamlit as st
import pandas as pd
import numpy as np
import requests
from io import StringIO

# Set the page configuration
st.set_page_config(page_title='Data Tanaman Padi Sumatera', page_icon='🌾', layout='wide')

# Custom CSS for cursor
cursor_url = "https://icons.iconarchive.com/icons/google/noto-emoji-animals-nature/32/22215-blossom-icon.png"
st.markdown(f"""
    <style>
    body {{
        cursor: url({cursor_url}), auto;
    }}
    </style>
    """, unsafe_allow_html=True)

# Function to fetch the CSV file from Google Drive
def fetch_csv_from_gdrive(gdrive_url):
    response = requests.get(gdrive_url)
    response.raise_for_status()  # Raise an exception for HTTP errors
    return response.content.decode('utf-8')

# Google Drive file URL
file_url = 'https://drive.google.com/uc?id=1gEP8S3GvxmsgTs0KlytOBVjwCDr4fHFB'

# Fetch and load the dataset
csv_data = fetch_csv_from_gdrive(file_url)
data = pd.read_csv(StringIO(csv_data))

# Sidebar Navigation
st.sidebar.title("Navigasi")
page = st.sidebar.radio("Pilih Halaman", ["Informasi Umum", "Eksplorasi Data", "Kesimpulan"])

# AHP criteria and alternatives
criteria = ['Tahun', 'Produksi', 'Luas Panen', 'Curah hujan', 'Kelembapan', 'Suhu rata-rata']
alternatives = ['Lampung', 'Sumatera Selatan', 'Jambi', 'Sumatera Utara', 'Sumatera Barat', 'Riau']

# AHP Functions
def ahp_criteria_matrix(criteria):
    n = len(criteria)
    matrix = np.ones((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            matrix[i, j] = st.slider(f"Perbandingan {criteria[i]} vs {criteria[j]}", 0, 5, 0)
            matrix[j, i] = 1 / matrix[i, j]
    return matrix

def normalize(matrix):
    column_sums = np.sum(matrix, axis=0)
    normalized_matrix = matrix / column_sums
    return normalized_matrix

def calculate_priority_vector(normalized_matrix):
    return np.mean(normalized_matrix, axis=1)

def consistency_ratio(matrix, priority_vector):
    n = len(matrix)
    weighted_sum_vector = np.dot(matrix, priority_vector)
    consistency_vector = weighted_sum_vector / priority_vector
    lambda_max = np.mean(consistency_vector)
    ci = (lambda_max - n) / (n - 1)
    ri_values = {1: 0.0, 2: 0.0, 3: 0.58, 4: 0.9, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45}
    ri = ri_values.get(n, 1.45)
    cr = ci / ri
    return cr

def calculate_alternative_scores(data, criteria, alternatives, criteria_weights):
    scores = {}
    for alternative in alternatives:
        alternative_data = data[data['Provinsi'] == alternative]
        score = 0
        for criterion, weight in zip(criteria, criteria_weights):
            if criterion in alternative_data.columns:
                criterion_mean = alternative_data[criterion].mean()
                score += criterion_mean * weight
        scores[alternative] = score
    return scores

if page == "Informasi Umum":
    st.title('Dashboard Data Tanaman Padi di Sumatera')
    st.markdown("""
        <style>
        .main { background-color: #f5f5f5; }
        .header { color: #008080; }
        .dataframe { border: 1px solid #ddd; }
        </style>
    """, unsafe_allow_html=True)

    st.header('Informasi Umum')
    st.markdown('''
    Aplikasi ini menyajikan informasi mengenai data tanaman padi di Sumatera. 
    Anda dapat menjelajahi data ini dan melihat berbagai statistik yang relevan.
    ''')
    st.subheader('Dataset Tanaman Padi')
    st.dataframe(data)

elif page == "Eksplorasi Data":
    st.header('Eksplorasi Data')
    st.markdown('''
    Di bagian ini, Anda dapat melihat statistik deskriptif dan visualisasi data.
    ''')
    
    st.subheader('Statistik Deskriptif')
    st.write(data.describe())

    st.subheader('Visualisasi Data')
    column = st.selectbox('Pilih Kolom untuk Visualisasi', data.columns)
    
    st.markdown(f"### Grafik Garis untuk Kolom {column}")
    st.line_chart(data[column])
    
    st.markdown(f"### Grafik Batang untuk Kolom {column}")
    st.bar_chart(data[column])
    
    st.markdown(f"### Grafik Area untuk Kolom {column}")
    st.area_chart(data[column])
    
    st.subheader('Metode AHP')

    ahp_matrix = ahp_criteria_matrix(criteria)
    
    st.subheader('Matriks Perbandingan Kriteria')
    st.write(pd.DataFrame(ahp_matrix, index=criteria, columns=criteria))
    
    normalized_matrix = normalize(ahp_matrix)
    priority_vector = calculate_priority_vector(normalized_matrix)
    cr = consistency_ratio(ahp_matrix, priority_vector)

    st.subheader('Prioritas Kriteria')
    for crit, pv in zip(criteria, priority_vector):
        st.write(f"{crit}: {pv:.4f}")
    
    st.write(f"Consistency Ratio (CR): {cr:.4f}")
    if cr > 0.1:
        st.warning("Consistency Ratio lebih dari 0.1, matriks perbandingan kriteria mungkin tidak konsisten.")

    # Save priority_vector to session state
    st.session_state['priority_vector'] = priority_vector

    alternative_scores = calculate_alternative_scores(data, criteria, alternatives, priority_vector)
    
    st.subheader('Skor Alternatif')
    for alternative, score in alternative_scores.items():
        st.write(f"{alternative}: {score:.4f}")
    
    st.subheader('Penjelasan AHP')
    st.markdown('''
    Analytic Hierarchy Process (AHP) adalah metode pengambilan keputusan yang membantu menentukan prioritas 
    dan membuat keputusan yang lebih baik dengan membandingkan berbagai kriteria secara berpasangan. 
    Metode ini mengubah penilaian kualitatif menjadi nilai kuantitatif dan memberikan bobot pada setiap kriteria 
    yang dapat dibandingkan secara objektif.

    **Mengapa Kriteria dan Alternatif Ini yang Dipilih?**

    - **Kriteria**: Kriteria yang dipilih mencakup berbagai faktor penting yang mempengaruhi produksi padi, seperti:
        - **Tahun**: Untuk melihat tren produksi dari waktu ke waktu.
        - **Produksi**: Mengukur jumlah padi yang dihasilkan.
        - **Luas Panen**: Mengindikasikan area yang digunakan untuk menanam padi.
        - **Curah Hujan**: Faktor cuaca yang mempengaruhi pertumbuhan padi.
        - **Kelembapan**: Tingkat kelembapan udara yang dapat mempengaruhi kesehatan tanaman.
        - **Suhu Rata-rata**: Suhu lingkungan yang mempengaruhi siklus pertumbuhan padi.
    - **Alternatif**: Provinsi-provinsi di Sumatera dipilih sebagai alternatif untuk menentukan wilayah dengan potensi produksi padi terbaik. Provinsi yang dipilih adalah:
        - Lampung
        - Sumatera Selatan
        - Jambi
        - Sumatera Utara
        - Sumatera Barat
        - Riau
    ''')

elif page == "Kesimpulan":
    st.header('Kesimpulan')
    st.markdown('''
    Berdasarkan data yang telah dieksplorasi dan perhitungan AHP, kita dapat menyimpulkan beberapa hal penting terkait produksi padi di Sumatera.
    ''')

    if 'priority_vector' in st.session_state:
        priority_vector = st.session_state['priority_vector']
        alternative_scores = calculate_alternative_scores(data, criteria, alternatives, priority_vector)
        best_alternative = max(alternative_scores, key=alternative_scores.get)
        best_score = alternative_scores[best_alternative]
        worst_alternative = min(alternative_scores, key=alternative_scores.get)
        worst_score = alternative_scores[worst_alternative]

        st.markdown(f'''
        Wilayah dengan prioritas tertinggi berdasarkan kriteria yang dipilih adalah **{best_alternative}** dengan skor AHP sebesar **{best_score:.4f}**.
        Wilayah dengan prioritas terendah berdasarkan kriteria yang dipilih adalah **{worst_alternative}** dengan skor AHP sebesar **{worst_score:.4f}**.
        ''')

        st.subheader('Rekomendasi')
        st.markdown(f'''
        - **{best_alternative}** memiliki potensi tertinggi untuk produksi padi di Sumatera. Disarankan untuk memberikan perhatian lebih pada daerah ini.
        - **{worst_alternative}** memiliki potensi terendah, dan mungkin perlu peninjauan lebih lanjut untuk memahami faktor-faktor yang mempengaruhinya.
        ''')
    else:
        st.error("Prioritas kriteria belum dihitung. Silakan kunjungi halaman Eksplorasi Data terlebih dahulu.")

    st.markdown('''
    ### Insights dan Rekomendasi
    - Wilayah dengan skor AHP tertinggi menunjukkan potensi terbesar berdasarkan kriteria yang telah dipilih.
    - Pengelolaan lahan yang baik dan dukungan teknologi pertanian sangat berpengaruh terhadap peningkatan produksi.
    - Rekomendasi untuk pengambil kebijakan adalah fokus pada peningkatan teknologi pertanian dan pelatihan petani di wilayah-wilayah dengan potensi produksi tinggi.
    ''')

# Footer
st.markdown('''
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #333;
        color: white;
        text-align: center;
        padding: 10px;
    }
    </style>
    <div class="footer">
        Kelompok 1 Sistem Pengambil Keputusan Pilihan B
    </div>
''', unsafe_allow_html=True)