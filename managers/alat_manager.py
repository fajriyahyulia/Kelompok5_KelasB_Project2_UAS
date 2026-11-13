#dikerjakan oleh
#Nama : Sulthan Hafizh Putra Agung
#NIM : K3525013
#Kelas : B / Semester 3
#Angkatan : 2025

from datetime import date

from managers.dasar import ManagerDasar
from models.enums import KondisiAlat


class AlatManager(ManagerDasar):
    BIDANG_CARI = ("semua", "kode", "nama", "kategori")

    def __init__(self):
        super().__init__()
        self.data = {}
        self.pemeliharaan = {}  # kode alat -> tanggal masuk pemeliharaan

    def kosongkan(self):
        self.data.clear()
        self.pemeliharaan.clear()

    @property
    def kategori(self):
        """Dihitung dari data alat, jadi kategori baru langsung tersedia tanpa
        mengubah struktur program."""
        return {a.kategori for a in self.data.values()}

    def tambah(self, alat, simpan=True):
        if alat.kode in self.data:
            raise ValueError("Kode alat sudah terdaftar.")
        self.data[alat.kode] = alat
        if simpan:
            self._simpan("simpan_alat", lambda: self.data.pop(alat.kode, None))
            self._catat(f"Alat {alat.kode} ({alat.nama}) ditambahkan")
        return alat

    def edit(self, kode, nama=None, kategori=None):
        alat = self.get(kode)
        lama = (alat.nama, alat.kategori)
        alat.ubah(nama, kategori)

        def batalkan():
            alat.nama, alat.kategori = lama

        self._simpan("simpan_alat", batalkan)
        self._catat(f"Data alat {alat.kode} diperbarui")
        return alat

    def hapus(self, kode, transaksi_list, jaga_riwayat=True):
        alat = self.get(kode)
        if any(trx.is_aktif() and trx.punya_alat(alat.kode) for trx in transaksi_list):
            raise ValueError("Alat masih tercatat dalam transaksi aktif.")
        if jaga_riwayat and any(trx.pernah_memuat(alat.kode) for trx in transaksi_list):
            raise ValueError("Alat tercatat dalam riwayat transaksi dan tidak dapat dihapus "
                             "agar data antarfile tetap konsisten.")
        tgl_pemeliharaan = self.pemeliharaan.pop(alat.kode, None)
        del self.data[alat.kode]

        def batalkan():
            self.data[alat.kode] = alat
            if tgl_pemeliharaan is not None:
                self.pemeliharaan[alat.kode] = tgl_pemeliharaan

        self._simpan("simpan_alat", batalkan)
        self._catat(f"Alat {alat.kode} dihapus")
        return True

    def cari(self, keyword, bidang="semua"):
        keyword = keyword.strip().lower()
        if not keyword:
            raise ValueError("Kata kunci tidak boleh kosong.")
        if bidang not in self.BIDANG_CARI:
            raise ValueError("Bidang pencarian harus semua, kode, nama, atau kategori.")
        hasil = []
        for a in self.data.values():
            cocok = {
                "kode": keyword in a.kode.lower(),
                "nama": keyword in a.nama.lower(),
                "kategori": keyword in a.kategori.lower(),
            }
            if (bidang == "semua" and any(cocok.values())) or cocok.get(bidang):
                hasil.append(a)
        return hasil

    def get(self, kode):
        kode = kode.strip().upper()
        if kode not in self.data:
            raise ValueError("Alat tidak ditemukan.")
        return self.data[kode]

    def semua(self):
        return list(self.data.values())

    def daftar_tersedia(self):
        return [a for a in self.data.values() if a.is_tersedia()]

    def daftar_rusak(self):
        return [a for a in self.data.values() if a.kondisi != KondisiAlat.BAIK]

    # ------------------------------------------------------------------
    # Pemeliharaan (Tantangan C), disimpan di pemeliharaan.txt
    # ------------------------------------------------------------------
    def masuk_pemeliharaan(self, kode, tanggal=None):
        alat = self.get(kode)
        if alat.kondisi == KondisiAlat.BAIK:
            raise ValueError("Hanya alat yang rusak yang bisa masuk pemeliharaan.")
        if alat.kode in self.pemeliharaan:
            raise ValueError("Alat sudah ada dalam daftar pemeliharaan.")
        self.pemeliharaan[alat.kode] = tanggal or date.today()
        self._simpan("simpan_alat", lambda: self.pemeliharaan.pop(alat.kode, None))
        self._catat(f"Alat {alat.kode} masuk pemeliharaan")
        return alat

    def selesai_pemeliharaan(self, kode):
        alat = self.get(kode)
        if alat.kode not in self.pemeliharaan:
            raise ValueError("Alat tidak ada dalam daftar pemeliharaan.")
        kondisi_lama, tgl = alat.kondisi, self.pemeliharaan[alat.kode]
        alat.perbaiki()
        del self.pemeliharaan[alat.kode]

        def batalkan():
            alat.kondisi, alat.tersedia = kondisi_lama, False
            self.pemeliharaan[alat.kode] = tgl

        self._simpan("simpan_alat", batalkan)
        self._catat(f"Alat {alat.kode} selesai diperbaiki dan tersedia kembali")
        return alat

    def daftar_pemeliharaan(self):
        return [(self.data[k], tgl) for k, tgl in self.pemeliharaan.items() if k in self.data]


