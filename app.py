import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Konfigurasi Halaman
st.set_page_config(page_title="E-Library SMAS PLUS MULTAZAM", layout="wide")

# 2. Inisialisasi Koneksi
URL_SHEET = "https://docs.google.com/spreadsheets/d/1flqGUqJV06xicuYw0RmHOMIcU8qvG31DHGwB3s5dgMA/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Fungsi Ambil Data
def load_data():
    try:
        # Mengambil data tanpa cache agar selalu terbaru
        return conn.read(spreadsheet=URL_SHEET, ttl=0)
    except:
        return pd.DataFrame(columns=["Judul", "Kategori", "Link"])

# --- SIDEBAR NAVIGASI ---
st.sidebar.title("📚 SMAS PLUS MULTAZAM")
menu = st.sidebar.radio("Navigasi", ["Beranda Siswa", "Panel Admin"])

# --- HALAMAN BERANDA SISWA ---
if menu == "Beranda Siswa":
    st.title("📖 Perpustakaan Digital")
    df_buku = load_data()
    
    if not df_buku.empty:
        search = st.text_input("🔍 Cari Judul Buku...")
        display_df = df_buku.copy()
        if search:
            display_df = display_df[display_df["Judul"].str.contains(search, case=False, na=False)]
        
        st.divider()
        for _, row in display_df.iterrows():
            with st.expander(f"📘 {row['Judul']}"):
                st.write(f"Kategori: **{row['Kategori']}**")
                st.link_button("Buka PDF", row["Link"])
    else:
        st.info("Koleksi buku belum tersedia.")

# --- HALAMAN ADMIN ---
else:
    st.title("🔐 Panel Administrasi")
    
    # Gunakan form agar input password tidak terpental saat mengetik
    with st.sidebar.form("login_form"):
        pwd_input = st.text_input("Password Admin", type="password")
        login_submit = st.form_submit_button("Masuk")

    # Cek Password (Ganti 'multazam2026' jika ingin merubahnya)
    if pwd_input == "multazam2026":
        st.success("✅ Akses Diterima")
        df_buku = load_data()
        
        with st.form("tambah_data", clear_on_submit=True):
            st.subheader("Tambah Koleksi Baru")
            judul = st.text_input("Judul Buku")
            kat = st.selectbox("Kategori", ["Agama", "Matematika", "Bahasa", "IPA", "IPS", "Sastra", "Umum"])
            link = st.text_input("Link Google Drive (Pastikan akses: Anyone with Link)")
            submit_btn = st.form_submit_button("Simpan ke Google Sheets")
            
            if submit_btn:
                if judul and link:
                    # Proses Tambah Data
                    new_row = pd.DataFrame([{"Judul": judul, "Kategori": kat, "Link": link}])
                    updated_df = pd.concat([df_buku, new_row], ignore_index=True)
                    
                    try:
                        conn.update(spreadsheet=URL_SHEET, data=updated_df)
                        st.balloons()
                        st.success(f"Berhasil menyimpan: {judul}")
                        st.info("Data sedang diperbarui, silakan tunggu sebentar...")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal simpan! Pastikan 'Secrets' di Streamlit sudah diisi URL Spreadsheet. Error: {e}")
                else:
                    st.warning("Judul dan Link tidak boleh kosong!")
        
        st.divider()
        st.subheader("Data Saat Ini")
        st.dataframe(df_buku, use_container_width=True)
        
    elif pwd_input != "":
        st.error("❌ Password Salah!")