import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Konfigurasi Halaman (Harus paling atas)
st.set_page_config(page_title="E-Library SMAS PLUS MULTAZAM", layout="wide")

# 2. Hubungkan ke Google Sheets
URL_SHEET = "https://docs.google.com/spreadsheets/d/1flqGUqJV06xicuYw0RmHOMIcU8qvG31DHGwB3s5dgMA/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Fungsi Ambil Data dengan Cache agar Cepat
def load_data():
    try:
        return conn.read(spreadsheet=URL_SHEET, ttl="0")
    except:
        return pd.DataFrame(columns=["Judul", "Kategori", "Link"])

df_buku = load_data()

# 4. Navigasi Sidebar
st.sidebar.title("📚 SMAS PLUS MULTAZAM")
# Gunakan Session State untuk Menu agar tidak terpental
if 'menu' not in st.session_state:
    st.session_state.menu = "Beranda Siswa"

def set_menu():
    st.session_state.menu = st.session_state.pilihan_menu

st.sidebar.radio(
    "Navigasi", 
    ["Beranda Siswa", "Panel Admin"], 
    key="pilihan_menu", 
    on_change=set_menu
)

# --- HALAMAN BERANDA SISWA ---
if st.session_state.menu == "Beranda Siswa":
    st.title("📖 Perpustakaan Digital")
    st.info("Selamat datang! Silakan cari buku yang ingin Anda baca.")
    
    if not df_buku.empty:
        # Filter Pencarian
        search = st.text_input("🔍 Cari Judul Buku...")
        
        # Logika Filter
        display_df = df_buku.copy()
        if search:
            display_df = display_df[display_df["Judul"].str.contains(search, case=False, na=False)]
        
        st.divider()
        
        # Tampilan Koleksi
        for _, row in display_df.iterrows():
            with st.expander(f"📘 {row['Judul']} ({row['Kategori']})"):
                st.write(f"Kategori: **{row['Kategori']}**")
                st.link_button("Klik untuk Membaca PDF", row["Link"])
    else:
        st.warning("Koleksi buku belum tersedia di database.")

# --- HALAMAN ADMIN ---
elif st.session_state.menu == "Panel Admin":
    st.title("🔐 Panel Administrasi")
    
    # Input Password
    password = st.text_input("Masukkan Password Admin", type="password")
    
    if password == "multazam2026":
        st.success("Akses Diterima! Silakan kelola data buku.")
        
        # Form Tambah Buku
        with st.form("form_tambah"):
            st.subheader("Tambah Buku Baru")
            judul = st.text_input("Judul Buku")
            kat = st.selectbox("Kategori", ["Agama", "Matematika", "Bahasa", "IPA", "IPS", "Umum"])
            link = st.text_input("Link Google Drive PDF")
            submit = st.form_submit_button("Simpan ke Google Sheets")
            
            if submit:
                if judul and link:
                    new_row = pd.DataFrame([{"Judul": judul, "Kategori": kat, "Link": link}])
                    updated_df = pd.concat([df_buku, new_data if 'new_data' in locals() else new_row], ignore_index=True)
                    
                    try:
                        conn.update(spreadsheet=URL_SHEET, data=updated_df)
                        st.balloons()
                        st.success("Buku berhasil disimpan! Silakan refresh halaman.")
                        st.cache_data.clear() # Membersihkan cache agar data baru muncul
                    except Exception as e:
                        st.error(f"Gagal menyimpan: Pastikan Secrets sudah benar. Error: {e}")
                else:
                    st.warning("Mohon isi Judul dan Link.")
        
        st.divider()
        st.subheader("Daftar Buku di Database")
        st.dataframe(df_buku, use_container_width=True)
        
    elif password != "" and password != "multazam2026":
        st.error("Password Salah!")