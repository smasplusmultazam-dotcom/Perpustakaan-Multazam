import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Konfigurasi Halaman
st.set_page_config(page_title="E-Library SMAS PLUS MULTAZAM", layout="wide")

# Link Spreadsheet Anda (Sudah menggunakan ID yang Anda berikan)
URL_SHEET = "https://docs.google.com/spreadsheets/d/1flqGUqJV06xicuYw0RmHOMIcU8qvG31DHGwB3s5dgMA/edit#gid=0"

# Koneksi ke Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        # Membaca data dari sheet pertama
        return conn.read(spreadsheet=URL_SHEET, usecols=[0, 1, 2], ttl="0")
    except:
        # Jika sheet masih kosong, buat dataframe kosong dengan kolom yang sesuai
        return pd.DataFrame(columns=["Judul", "Kategori", "Link"])

# Ambil data terbaru
df_buku = load_data()

# --- TAMPILAN SIDEBAR ---
st.sidebar.title("📚 E-Library")
st.sidebar.subheader("SMAS PLUS MULTAZAM")
menu = st.sidebar.radio("Navigasi", ["Beranda Siswa", "Panel Admin"])

# --- HALAMAN BERANDA SISWA ---
if menu == "Beranda Siswa":
    st.title("📖 Koleksi Buku Digital")
    st.write("Selamat datang di perpustakaan digital SMAS PLUS MULTAZAM.")
    
    # Fitur Pencarian & Filter
    col1, col2 = st.columns([2, 1])
    search = col1.text_input("Cari Judul Buku...")
    
    # Pastikan kategori unik tersedia
    available_cats = ["Semua"] + sorted(list(df_buku["Kategori"].unique())) if not df_buku.empty else ["Semua"]
    selected_kat = col2.selectbox("Kategori", available_cats)
    
    # Logika Filter
    display_df = df_buku.copy()
    if search:
        display_df = display_df[display_df["Judul"].str.contains(search, case=False, na=False)]
    if selected_kat != "Semua":
        display_df = display_df[display_df["Kategori"] == selected_kat]
    
    st.divider()
    
    if not display_df.empty:
        for _, row in display_df.iterrows():
            with st.container():
                st.subheader(f"📘 {row['Judul']}")
                st.caption(f"Kategori: {row['Kategori']}")
                st.link_button(f"Baca Sekarang", row["Link"])
                st.write("---")
    else:
        st.info("Buku tidak ditemukan atau koleksi masih kosong.")

# --- HALAMAN ADMIN ---
elif menu == "Panel Admin":
    st.title("🔐 Kelola Database Buku")
    
    # Password Admin
    pwd = st.sidebar.text_input("Password", type="password")
    if pwd == "multazam2026":
        st.success("Mode Admin Aktif")
        
        with st.form("tambah_buku"):
            st.subheader("Tambah Buku Baru")
            judul = st.text_input("Judul Buku")
            kat = st.selectbox("Kategori", ["Agama", "Matematika", "Bahasa Indonesia", "IPA", "IPS", "Sastra", "Umum"])
            link = st.text_input("Link Google Drive (Pastikan akses: Anyone with the link)")
            submit = st.form_submit_button("Simpan ke Database")
            
            if submit and judul and link:
                # Menambahkan baris baru
                new_data = pd.DataFrame([{"Judul": judul, "Kategori": kat, "Link": link}])
                updated_df = pd.concat([df_buku, new_data], ignore_index=True)
                
                # Update ke Google Sheets
                conn.update(spreadsheet=URL_SHEET, data=updated_df)
                st.success(f"Buku '{judul}' Berhasil disimpan!")
                st.rerun()
                
        st.divider()
        st.subheader("Daftar Buku (Database)")
        st.dataframe(df_buku, use_container_width=True)
    else:
        st.warning("Silakan masukkan password admin untuk menambah buku.")