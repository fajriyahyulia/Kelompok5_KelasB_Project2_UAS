#dikerjakan oleh
#Nama : Zahra Faizza Kuncoroningrum
#NIM : K3525017
#Kelas : B / Semester 3
#Angkatan : 2025

from datetime import date
from models.enums import KondisiAlat


class ItemPinjam:
    def __init__(self, alat, tanggal_kembali=None,
                 kondisi_kembali=None, sudah_kembali=False):
        self.alat = alat
        self.tanggal_kembali = tanggal_kembali
        self.kondisi_kembali = kondisi_kembali
        self.sudah_kembali = sudah_kembali

    def tandai_kembali(self, kondisi, tanggal=None):
        if self.sudah_kembali:
            raise ValueError("Alat ini sudah dikembalikan.")
        kondisi = kondisi if isinstance(kondisi, KondisiAlat) else KondisiAlat.dari_teks(kondisi)
        self.kondisi_kembali = kondisi
        self.tanggal_kembali = tanggal or date.today()
        self.sudah_kembali = True
        self.alat.update_kondisi(kondisi)
        self.alat.set_tersedia(kondisi == KondisiAlat.BAIK)

    def hari_terlambat(self, batas_kembali, acuan=None):
        """Jumlah hari lewat batas. Alat yang belum kembali dihitung sampai hari acuan."""
        akhir = self.tanggal_kembali if self.sudah_kembali else (acuan or date.today())
        return max(0, (akhir - batas_kembali).days)
