#dikerjakan oleh
#Nama : Zahra Faizza Kuncoroningrum
#NIM : K3525017
#Kelas : B / Semester 3
#Angkatan : 2025

from datetime import datetime

from storage.file_teks import PenyimpananError

NAMA_FILE = "log.txt"


class LogAktivitas:
    """Riwayat aktivitas. Disimpan di list selama program berjalan dan ditambahkan
    ke akhir log.txt (mode append) sehingga log lama tidak pernah terhapus."""

    def __init__(self, file_teks):
        self.file = file_teks
        self.entri = []
        self.galat_terakhir = None

    def muat(self):
        self.entri = self.file.baca_baris_mentah(NAMA_FILE)

    def catat(self, pesan, waktu=None):
        waktu = waktu or datetime.now()
        pesan = " ".join(str(pesan).split())
        baris = f"[{waktu.strftime('%Y-%m-%d %H:%M')}] {pesan}"
        self.entri.append(baris)
        try:
            self.file.tambah(NAMA_FILE, baris)
        except PenyimpananError as e:
            # Kegagalan menulis log tidak boleh membatalkan operasi utama.
            self.galat_terakhir = e

    def terakhir(self, jumlah=25):
        return self.entri[-jumlah:]
