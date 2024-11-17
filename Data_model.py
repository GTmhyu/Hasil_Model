import altair as alt
from pymongo import MongoClient
import pandas as pd
import streamlit as st

# Koneksi ke MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client["hasil_model"]
collection = db["console"]

# Fetch data
data = collection.find({"name": "person"})
df = pd.DataFrame(list(data))

# Debugging: Menampilkan DataFrame di Streamlit untuk memeriksa data
st.write("Data CSV:", df)

# Mengubah format timestamp dan mengurutkannya
df['timestamp'] = pd.to_datetime(df['timestamp'])  
df = df.sort_values(by='timestamp')

# Filter data untuk 1 minggu terakhir
last_week = df[df['timestamp'] >= (df['timestamp'].max() - pd.Timedelta(days=7))]

# Jumlah Person Per Hari dalam Seminggu
last_week['day_of_week'] = last_week['timestamp'].dt.day_name()
day_of_week_count = last_week.groupby('day_of_week').size().reset_index(name='counts')

# Mengubah chart menjadi pie chart
day_of_week_pie_chart = alt.Chart(day_of_week_count).mark_arc().encode(
    theta=alt.Theta(field='counts', type='quantitative'),
    color=alt.Color(field='day_of_week', type='nominal', sort=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']),
    tooltip=['day_of_week:N', 'counts:Q']
).properties(
    title='Jumlah Person dalam Seminggu (Data Terbaru)',
    width=350,  # Sesuaikan lebar agar muat di kolom
    height=400
)

# Agregasi data untuk menghitung jumlah 'person' per hari
df['date'] = df['timestamp'].dt.date  # Membuat kolom baru dengan hanya tanggal
daily_count = df.groupby('date').size().reset_index(name='counts')

# Tampilan person per hari
daily_chart = alt.Chart(daily_count).mark_bar().encode(
    x='date:T',  # T: temporal untuk data waktu/tanggal
    y='counts:Q',  # Q: quantitative, untuk jumlah 'person'
    tooltip=['date:T', 'counts:Q']  # Menampilkan tooltip
).properties(
    title='Jumlah Person Per Hari',
    width=350,  # Sesuaikan lebar agar muat di kolom
    height=400
).interactive()  

# Menampilkan chart bersampingan di Streamlit
col1, col2 = st.columns(2)

with col1:
    st.subheader("Jumlah Person dalam Seminggu (Data Terbaru)")
    st.altair_chart(day_of_week_pie_chart, use_container_width=True)

with col2:
    st.subheader("Jumlah Person Per Hari")
    st.altair_chart(daily_chart, use_container_width=True)