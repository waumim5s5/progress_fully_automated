import streamlit as st
import os
import json
import pandas as pd
from datetime import datetime
import openpyxl

st.set_page_config(page_title="Sistem Laporan Proyek RS", page_icon="🏗️", layout="wide")

# ==========================================
# 1. PERSIAPAN FOLDER & FILE DATABASE
# ==========================================
DIR_SAAT_INI = os.path.dirname(os.path.abspath(__file__))
FILE_DATABASE = os.path.join(DIR_SAAT_INI, "database_proyek.json")
FILE_AGENDA = os.path.join(DIR_SAAT_INI, "database_agenda.json")

# ---------- PROGRES (dari progres.py) ----------
def simpan_database():
    with open(FILE_DATABASE, 'w') as f:
        json.dump({
            "tasks": st.session_state.database_tasks,
            "workers": st.session_state.database_workers
        }, f, indent=4)

def muat_database():
    if os.path.exists(FILE_DATABASE):
        try:
            with open(FILE_DATABASE, 'r') as f:
                data = json.load(f)
                if "tasks" not in data:
                    return {"tasks": data, "workers": {}}
                return data
        except Exception:
            return {"tasks": {}, "workers": {}}
    return {"tasks": {}, "workers": {}}

# ---------- AGENDA (dari nama.py) ----------
def simpan_agenda():
    with open(FILE_AGENDA, 'w') as f:
        json.dump(st.session_state.db_agenda, f, indent=4, ensure_ascii=False)

def muat_agenda():
    if os.path.exists(FILE_AGENDA):
        try:
            with open(FILE_AGENDA, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

if 'db_loaded' not in st.session_state:
    db = muat_database()
    st.session_state.database_tasks = db["tasks"]
    st.session_state.database_workers = db["workers"]
    st.session_state.db_agenda = muat_agenda()
    st.session_state.db_loaded = True
    simpan_database()


# ==========================================
# 2. SIDEBAR - MANAJEMEN DATA
# ==========================================
with st.sidebar:
    st.header("➕ Manajemen Data")

    # ----- PROGRES: Area / Pekerjaan / Printilan -----
    with st.expander("1. Tambah Area Baru (Progres)"):
        with st.form("form_area"):
            area_baru = st.text_input("Nama Area")
            if st.form_submit_button("Tambah Area") and area_baru:
                if area_baru not in st.session_state.database_tasks:
                    st.session_state.database_tasks[area_baru] = {}
                    simpan_database()
                    st.success("Berhasil! Refresh halaman.")

    with st.expander("2. Tambah Pekerjaan Utama"):
        if st.session_state.database_tasks:
            pilih_area_1 = st.selectbox("Pilih Area", list(st.session_state.database_tasks.keys()), key="sb_area_pek")
            with st.form("form_pekerjaan"):
                pekerjaan_baru = st.text_input("Nama Pekerjaan")
                if st.form_submit_button("Tambah Pekerjaan") and pekerjaan_baru:
                    if pekerjaan_baru not in st.session_state.database_tasks[pilih_area_1]:
                        st.session_state.database_tasks[pilih_area_1][pekerjaan_baru] = {}
                        simpan_database()
                        st.success("Berhasil! Refresh halaman.")
        else:
            st.write("Buat area dulu.")

    with st.expander("3. Tambah Printilan"):
        if st.session_state.database_tasks:
            pilih_area_2 = st.selectbox("Pilih Area", list(st.session_state.database_tasks.keys()), key="sb_area_prin")
            if st.session_state.database_tasks[pilih_area_2]:
                pilih_pekerjaan = st.selectbox("Pilih Pekerjaan", list(st.session_state.database_tasks[pilih_area_2].keys()), key="sb_pek_prin")
                with st.form("form_printilan"):
                    printilan_baru = st.text_input("Nama Printilan")
                    if st.form_submit_button("Tambah Printilan") and printilan_baru:
                        if printilan_baru not in st.session_state.database_tasks[pilih_area_2][pilih_pekerjaan]:
                            st.session_state.database_tasks[pilih_area_2][pilih_pekerjaan][printilan_baru] = 0
                            simpan_database()
                            st.success("Berhasil! Refresh halaman.")
            else:
                st.write("Buat pekerjaan dulu.")
        else:
            st.write("Buat area dulu.")

    st.divider()

    # ----- AGENDA: Area baru -----
    with st.expander("4. Tambah Area Agenda"):
        with st.form("form_area_agenda"):
            area_agenda_baru = st.text_input("Nama Area Agenda (contoh: Lantai 1)")
            if st.form_submit_button("Tambah Area Agenda") and area_agenda_baru:
                if area_agenda_baru not in st.session_state.db_agenda:
                    st.session_state.db_agenda[area_agenda_baru] = []
                    simpan_agenda()
                    st.success("Area agenda ditambahkan!")
                    st.rerun()

    st.divider()

    st.header("🗑️ Hapus Data")
    with st.expander("Panel Hapus Data (Hati-hati!)"):
        jenis_hapus = st.radio("Pilih Jenis Hapus", [
            "Area Progres", "Pekerjaan Progres", "Printilan",
            "Area Agenda", "Pekerjaan Agenda"], key="jenis_hapus")

        if jenis_hapus == "Area Progres" and st.session_state.database_tasks:
            area_hapus = st.selectbox("Pilih Area", list(st.session_state.database_tasks.keys()), key="del_area")
            if st.button("🚨 HAPUS AREA INI"):
                del st.session_state.database_tasks[area_hapus]
                simpan_database()
                st.success(f"Area {area_hapus} terhapus!")
                st.rerun()

        elif jenis_hapus == "Pekerjaan Progres" and st.session_state.database_tasks:
            area_pilih = st.selectbox("Dari Area Mana?", list(st.session_state.database_tasks.keys()), key="del_area_pek")
            if st.session_state.database_tasks[area_pilih]:
                pek_hapus = st.selectbox("Pilih Pekerjaan", list(st.session_state.database_tasks[area_pilih].keys()), key="del_pek")
                if st.button("🚨 HAPUS PEKERJAAN INI"):
                    del st.session_state.database_tasks[area_pilih][pek_hapus]
                    st.session_state.database_workers.pop(f"{area_pilih}_{pek_hapus}_tukang", None)
                    st.session_state.database_workers.pop(f"{area_pilih}_{pek_hapus}_peladen", None)
                    simpan_database()
                    st.success(f"Pekerjaan {pek_hapus} terhapus!")
                    st.rerun()
            else:
                st.write("Tidak ada pekerjaan di area ini.")

        elif jenis_hapus == "Printilan" and st.session_state.database_tasks:
            area_pilih2 = st.selectbox("Pilih Area", list(st.session_state.database_tasks.keys()), key="del_area_prin")
            if st.session_state.database_tasks[area_pilih2]:
                pek_pilih = st.selectbox("Pilih Pekerjaan", list(st.session_state.database_tasks[area_pilih2].keys()), key="del_pek_prin")
                if st.session_state.database_tasks[area_pilih2][pek_pilih]:
                    prin_hapus = st.selectbox("Pilih Printilan", list(st.session_state.database_tasks[area_pilih2][pek_pilih].keys()), key="del_prin")
                    if st.button("🚨 HAPUS PRINTILAN INI"):
                        del st.session_state.database_tasks[area_pilih2][pek_pilih][prin_hapus]
                        simpan_database()
                        st.success(f"Printilan {prin_hapus} terhapus!")
                        st.rerun()
                else:
                    st.write("Tidak ada printilan.")
            else:
                st.write("Tidak ada pekerjaan.")

        elif jenis_hapus == "Area Agenda" and st.session_state.db_agenda:
            agenda_area_hapus = st.selectbox("Pilih Area Agenda", list(st.session_state.db_agenda.keys()), key="del_ag_area")
            if st.button("🚨 HAPUS AREA AGENDA INI"):
                del st.session_state.db_agenda[agenda_area_hapus]
                simpan_agenda()
                st.success(f"Area agenda {agenda_area_hapus} terhapus!")
                st.rerun()

        elif jenis_hapus == "Pekerjaan Agenda" and st.session_state.db_agenda:
            agenda_area_pilih = st.selectbox("Pilih Area Agenda", list(st.session_state.db_agenda.keys()), key="del_ag_area_pek")
            if st.session_state.db_agenda[agenda_area_pilih]:
                daftar_ag = list(st.session_state.db_agenda[agenda_area_pilih])
                nama_ag = [f"{i+1}. {a.get('pekerjaan') or '(kosong)'}" for i, a in enumerate(daftar_ag)]
                pilihan_ag = st.selectbox("Pilih Pekerjaan", range(len(daftar_ag)), format_func=lambda x: nama_ag[x], key="del_ag_pek")
                if st.button("🚨 HAPUS PEKERJAAN INI"):
                    del st.session_state.db_agenda[agenda_area_pilih][pilihan_ag]
                    simpan_agenda()
                    st.success("Pekerjaan agenda terhapus!")
                    st.rerun()
            else:
                st.write("Tidak ada pekerjaan agenda.")

    st.divider()

    # ----- EKSPOR & RESTORE -----
    st.header("📂 Restore Data (Upload Excel)")
    file_excel_upload = st.file_uploader("Upload Excel Backup (*.xlsx)", type=["xlsx"])
    if file_excel_upload:
        if st.button("🔄 Pulihkan Data"):
            try:
                df_upload = pd.read_excel(file_excel_upload)
                database_baru = {}
                workers_baru = {}

                for index, row in df_upload.iterrows():
                    area = str(row['Area']).strip()
                    pekerjaan = str(row['Pekerjaan Utama']).strip()
                    tukang = str(row.get('Nama Tukang', '')).strip()
                    peladen = str(row.get('Nama Peladen', '')).strip()
                    printilan = str(row['Item Printilan']).strip()
                    progres_val = float(row.get('Progres (%)', 0))

                    if area not in database_baru:
                        database_baru[area] = {}
                    if pekerjaan not in database_baru[area]:
                        database_baru[area][pekerjaan] = {}

                    if tukang and tukang.lower() != "nan" and tukang != "-":
                        workers_baru[f"{area}_{pekerjaan}_tukang"] = tukang
                    if peladen and peladen.lower() != "nan" and peladen != "-":
                        workers_baru[f"{area}_{pekerjaan}_peladen"] = peladen

                    if printilan != "-" and printilan.lower() != "nan":
                        database_baru[area][pekerjaan][printilan] = int(progres_val * 100)

                st.session_state.database_tasks = database_baru
                st.session_state.database_workers = workers_baru
                simpan_database()
                st.success("✅ Berhasil dipulihkan!")
                st.rerun()
            except Exception as e:
                st.error(f"Gagal memulihkan: {e}")

    st.divider()

    st.header("📊 Export Laporan")
    if st.button("Siapkan File Excel"):
        data_untuk_excel = []
        for area, dict_pekerjaan in st.session_state.database_tasks.items():
            for pekerjaan, dict_printilan in dict_pekerjaan.items():
                jumlah_printilan = len(dict_printilan)
                if jumlah_printilan > 0:
                    total_progres = 0
                    for val in dict_printilan.values():
                        if isinstance(val, bool):
                            val = 100 if val else 0
                        total_progres += val
                    progres_rata = (total_progres / (jumlah_printilan * 100))
                else:
                    progres_rata = 0

                nama_tukang = st.session_state.database_workers.get(f"{area}_{pekerjaan}_tukang", "-")
                nama_peladen = st.session_state.database_workers.get(f"{area}_{pekerjaan}_peladen", "-")

                data_untuk_excel.append({"Area": area, "Pekerjaan Utama": pekerjaan, "Nama Tukang": nama_tukang, "Nama Peladen": nama_peladen, "Item Printilan": "-", "Status": "PROGRES KESELURUHAN", "Progres (%)": progres_rata})

                for printilan, val in dict_printilan.items():
                    if isinstance(val, bool):
                        val = 100 if val else 0
                    status_text = "Selesai" if val == 100 else f"Proses {val}%"
                    data_untuk_excel.append({"Area": area, "Pekerjaan Utama": pekerjaan, "Nama Tukang": nama_tukang, "Nama Peladen": nama_peladen, "Item Printilan": printilan, "Status": status_text, "Progres (%)": (val / 100)})

        if data_untuk_excel:
            df = pd.DataFrame(data_untuk_excel)
            file_excel_final = os.path.join(DIR_SAAT_INI, "Laporan_Progres_Final.xlsx")
            df.to_excel(file_excel_final, index=False)

            try:
                with open(file_excel_final, "rb") as f:
                    st.download_button(label="📥 Unduh Excel", data=f, file_name=f"Laporan_Lengkap_{datetime.now().strftime('%Y%m%d')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            except Exception as e:
                st.error(f"Gagal menyiapkan unduhan: {e}")

    st.divider()
    if st.button("🔄 Muat Ulang Halaman (Refresh)"):
        st.rerun()


# ==========================================
# 3. TAB HALAMAN
# ==========================================
tab_agenda, tab_tracker, tab_wa = st.tabs([
    "📋 Agenda Pekerja Harian",
    "🏗️ Tracker Progres",
    "📱 Laporan WhatsApp"
])

# -----------------------------------------------------------
# TAB 1: AGENDA PEKERJA HARIAN
# -----------------------------------------------------------
with tab_agenda:
    st.title("📋 Agenda Pekerja Harian")
    st.caption("Isi nama pekerjaan, tukang, laden, pengawas, dan note secara terpisah per baris.")

    if not st.session_state.db_agenda:
        st.info("👈 Belum ada area agenda. Tambahkan di menu kiri → '4. Tambah Area Agenda'.")
    else:
        for area, entries in st.session_state.db_agenda.items():
            with st.expander(f"📍 {area}", expanded=True):
                if not entries:
                    st.caption("*Belum ada pekerjaan.*")

                for i, e in enumerate(entries):
                    st.markdown(f"**Baris {i+1}**")

                    def make_cb(area, i, field, key):
                        def cb():
                            st.session_state.db_agenda[area][i][field] = st.session_state[key]
                            simpan_agenda()
                        return cb

                    col_p, col_t, col_l, col_pg, col_n, col_d = st.columns([3, 2, 2, 2, 2, 1])

                    with col_p:
                        st.text_input("Pekerjaan", key=f"ag_p_{area}_{i}", value=str(e.get("pekerjaan", "")), on_change=make_cb(area, i, "pekerjaan", f"ag_p_{area}_{i}"))
                    with col_t:
                        st.text_input("Tukang", key=f"ag_t_{area}_{i}", value=str(e.get("tukang", "")), on_change=make_cb(area, i, "tukang", f"ag_t_{area}_{i}"))
                    with col_l:
                        st.text_input("Laden", key=f"ag_l_{area}_{i}", value=str(e.get("laden", "")), on_change=make_cb(area, i, "laden", f"ag_l_{area}_{i}"))
                    with col_pg:
                        st.text_input("Pengawas", key=f"ag_pg_{area}_{i}", value=str(e.get("pengawas", "")), on_change=make_cb(area, i, "pengawas", f"ag_pg_{area}_{i}"))
                    with col_n:
                        st.text_input("Note", key=f"ag_n_{area}_{i}", value=str(e.get("note", "")), on_change=make_cb(area, i, "note", f"ag_n_{area}_{i}"))
                    with col_d:
                        st.write("")
                        st.write("")
                        if st.button("🗑️", key=f"ag_del_{area}_{i}"):
                            del st.session_state.db_agenda[area][i]
                            simpan_agenda()
                            st.rerun()
                    st.write("---")

                if st.button("➕ Tambah Pekerjaan", key=f"ag_add_{area}"):
                    st.session_state.db_agenda[area].append({"pekerjaan": "", "tukang": "", "laden": "", "pengawas": "", "note": ""})
                    simpan_agenda()
                    st.rerun()

# -----------------------------------------------------------
# TAB 2: TRACKER PROGRES
# -----------------------------------------------------------
with tab_tracker:
    st.title("🏗️ Aplikasi Tracker Progres Proyek")

    if not st.session_state.database_tasks:
        st.info("👈 Data kosong. Tambah data di panel kiri.")
    else:
        daftar_area_t = list(st.session_state.database_tasks.keys())
        if "ingat_area" not in st.session_state or st.session_state.ingat_area not in daftar_area_t:
            st.session_state.ingat_area = daftar_area_t[0]

        area_terpilih = st.selectbox("📍 Pilih Area Pekerjaan:", daftar_area_t, key="ingat_area")
        st.divider()

        pekerjaan_utama_dict = st.session_state.database_tasks[area_terpilih]

        if not pekerjaan_utama_dict:
            st.warning(f"Belum ada pekerjaan di area {area_terpilih}.")
        else:
            for main_task, sub_tasks in pekerjaan_utama_dict.items():
                with st.expander(f"🛠️ {main_task}", expanded=True):
                    if not sub_tasks:
                        st.write("Belum ada checklist.")
                    else:
                        total_printilan = len(sub_tasks)
                        total_skor = 0
                        for p_val in sub_tasks.values():
                            if isinstance(p_val, bool):
                                p_val = 100 if p_val else 0
                            total_skor += p_val
                        persentase = int(total_skor / total_printilan) if total_printilan > 0 else 0

                        st.progress(persentase / 100)
                        st.markdown(f"**Progres Pekerjaan: {persentase}%**")
                        st.write("---")

                        for printilan, val in sub_tasks.items():
                            if isinstance(val, bool):
                                val = 100 if val else 0
                                st.session_state.database_tasks[area_terpilih][main_task][printilan] = val

                            unik_key = f"sld_{area_terpilih}_{main_task}_{printilan}"

                            def update_status(a=area_terpilih, p=main_task, pr=printilan, key=unik_key):
                                st.session_state.database_tasks[a][p][pr] = st.session_state[key]
                                simpan_database()

                            c1, c2 = st.columns([1, 10])
                            with c1:
                                if val == 100:
                                    st.markdown("<h4 style='color:green; margin-top:20px;'>✅</h4>", unsafe_allow_html=True)
                                else:
                                    st.markdown("<h4 style='color:gray; margin-top:20px;'>⚙️</h4>", unsafe_allow_html=True)
                            with c2:
                                st.slider(printilan, min_value=0, max_value=100, value=val, step=5, key=unik_key, on_change=update_status)

# -----------------------------------------------------------
# TAB 3: GENERATOR LAPORAN WHATSAPP
# -----------------------------------------------------------
with tab_wa:
    st.title("📱 Buat Laporan WhatsApp")
    st.caption("Laporan digabung otomatis dari agenda pekerja harian + item pekerjaan & progres.")

    col_w1, col_w2, col_w3 = st.columns(3)
    with col_w1:
        input_nama = st.text_input("Nama Pelapor", value="samsul")
    with col_w2:
        input_tgl = st.text_input("Tanggal (DD MM YYYY)", value=datetime.now().strftime("%d %m %Y"))
    with col_w3:
        input_jam = st.text_input("Jam Laporan", value="14.00")

    input_notes = st.text_area("NOTE (opsional - kosongkan jika tidak ada catatan):", placeholder="1. tukang nya pak no tidak ada yg lembur\n2. pembersihan kaca = pending")

    def bagian_agenda_wa(jam):
        lines = []
        for area, entries in st.session_state.db_agenda.items():
            lines.append(f"Agenda tim {area.lower()} ({jam})")
            aktif = False
            for e in entries:
                pek = str(e.get("pekerjaan", "")).strip()
                tukang = str(e.get("tukang", "")).strip()
                laden = str(e.get("laden", "")).strip()
                pengawas = str(e.get("pengawas", "")).strip()
                note = str(e.get("note", "")).strip()

                if not any([pek, tukang, laden, pengawas, note]):
                    continue
                aktif = True
                if pek:
                    lines.append(f"👷🏻‍♂️{pek.lower()}") 
                if tukang:
                    lines.append(f"==> tukang = {tukang}")
                if laden:
                    lines.append(f"==> laden = {laden}")
                if pengawas:
                    lines.append(f"==> pengawas = {pengawas}")
                if note:
                    lines.append(f"==> note = {note}")
            if not aktif:
                lines.append("👷🏻‍♂️sementara tidak ada pekerjaan")
            lines.append("")
        return lines

    def bagian_progres_wa():
        lines = ["*ITEM PEKERJAAN DAN PROGRES*", ""]
        area_idx = 1
        for area, dict_pekerjaan in st.session_state.database_tasks.items():
            lines.append(f"{area_idx}. *{area}*")

            for pekerjaan, dict_printilan in dict_pekerjaan.items():
                jumlah_printilan = len(dict_printilan)

                if jumlah_printilan > 0:
                    total_skor = 0
                    for v in dict_printilan.values():
                        if isinstance(v, bool):
                            v = 100 if v else 0
                        total_skor += v
                    persen = int(total_skor / jumlah_printilan)
                else:
                    persen = 0

                if jumlah_printilan == 0:
                    lines.append(f"👷🏻‍♂️ Pekerjaan {pekerjaan} ({persen}%)")
                else:
                    lines.append(f"• *{pekerjaan}* ({persen}%)")

                prin_idx = 1
                for printilan, val in dict_printilan.items():
                    if isinstance(val, bool):
                        val = 100 if val else 0
                    status_simbol = "✅" if val == 100 else ""
                    lines.append(f"   {prin_idx}. {printilan} ({val}%){status_simbol}")
                    prin_idx += 1

            lines.append("")
            area_idx += 1
        return lines

    def generate_wa(nama, tgl, jam, notes):
        out = []
        out.append(f"Assalamualikum pak {nama} izin melaporkan perkembngan proyek di RS Bina Sehat Tanggal {tgl}")
        out.append("")

        out.extend(bagian_agenda_wa(jam))
        out.extend(bagian_progres_wa())

        out.append("NOTE :")
        baris_note = [l.strip() for l in notes.split("\n") if l.strip()] if notes.strip() else []
        if not baris_note:
            out.append("1. tidak ada catatan hari ini")
        else:
            for b in baris_note:
                out.append(b)

        return "\n".join(out)

    if st.button("Generate Teks Laporan", type="primary"):
        teks_laporan_wa = generate_wa(input_nama, input_tgl, input_jam, input_notes)
        st.text_area("Silakan Copy Teks Berikut:", value=teks_laporan_wa, height=600)
