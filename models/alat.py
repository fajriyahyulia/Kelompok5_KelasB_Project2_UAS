#dikerjakan oleh
#Nama : Sulthan Hafizh Putra Agung
#NIM : K3525013
#Kelas : B / Semester 3
#Angkatan : 2025


from models.enums import KondisiAlat
from models.validasi import kode_wajib, teks_wajib


class Alat:
    def __init__(self, kode: str, nama: str, kategori: str,
                 kondisi=KondisiAlat.BAIK, tersedia=True):
        self.kode = kode_wajib(kode, "Kode alat")
        self.nama = teks_wajib(nama, "Nama alat")
        self.kategori = teks_wajib(kategori, "Kategori")
        self.kondisi = kondisi if isinstance(kondisi, KondisiAlat) else KondisiAlat.dari_teks(kondisi)
        self.tersedia = bool(tersedia) and self.kondisi == KondisiAlat.BAIK

    def ubah(self, nama=None, kategori=None):
        nama_baru = teks_wajib(nama, "Nama alat") if nama and nama.strip() else self.nama
        kategori_baru = teks_wajib(kategori, "Kategori") if kategori and kategori.strip() else self.kategori
        self.nama, self.kategori = nama_baru, kategori_baru

    def is_tersedia(self):
        return self.tersedia and self.kondisi == KondisiAlat.BAIK

    def set_tersedia(self, status: bool):
        self.tersedia = bool(status) and self.kondisi == KondisiAlat.BAIK

    def update_kondisi(self, kondisi):
        self.kondisi = kondisi if isinstance(kondisi, KondisiAlat) else KondisiAlat.dari_teks(kondisi)
        if self.kondisi != KondisiAlat.BAIK:
            self.tersedia = False

    def perbaiki(self):
        if self.kondisi == KondisiAlat.BAIK:
            raise ValueError("Alat sudah dalam kondisi baik.")
        self.kondisi = KondisiAlat.BAIK
        self.tersedia = True

    def status_teks(self):
        if self.kondisi != KondisiAlat.BAIK:
            return "tidak tersedia"
        return "tersedia" if self.tersedia else "dipinjam"

    def __str__(self):
        return f"{self.kode} - {self.nama} | {self.kategori} | {self.kondisi.teks} | {self.status_teks()}"
