#dikerjakan oleh
#Nama : Fajriyah Yulia Az Zahra
#NIM : K3525005
#Kelas : B / Semester 3
#Angkatan : 2025

import os

from core.sistem import Sistem
from storage.file_teks import PenyimpananError
from ui.Menu import Menu
z
FOLDER_PROYEK = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    try:
        sistem = Sistem(
            folder_data=os.path.join(FOLDER_PROYEK, "data"),
            folder_backup=os.path.join(FOLDER_PROYEK, "backup"),
            folder_laporan=os.path.join(FOLDER_PROYEK, "laporan"),
        )
    except PenyimpananError as e:
        print(f"[!] Data tidak dapat dibaca, program dihentikan: {e}")
    else:
        Menu(sistem).jalankan()