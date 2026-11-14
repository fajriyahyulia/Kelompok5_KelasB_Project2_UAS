#dikerjakan oleh
#Nama : Zahra Faizza Kuncoroningrum
#NIM : K3525017
#Kelas : B / Semester 3
#Angkatan : 2025

from datetime import date, timedelta
from models.enums import StatusTransaksi
from models.item_pinjam import ItemPinjam


class Transaksi:
    MASA_PINJAM_HARI = 7

    def __init__(self, id_transaksi: str, mahasiswa, daftar_alat=(),
                 tanggal_pinjam=None, batas_kembali=None, daftar_item=None):
        self.id_transaksi = id_transaksi
        self.mahasiswa = mahasiswa
        self.tanggal_pinjam = tanggal_pinjam or date.today()
        maksimal = self.tanggal_pinjam + timedelta(days=self.MASA_PINJAM_HARI)
        self.batas_kembali = batas_kembali or maksimal
        if not (self.tanggal_pinjam <= self.batas_kembali <= maksimal):
            raise ValueError(f"Batas kembali harus dalam {self.MASA_PINJAM_HARI} hari sejak tanggal pinjam.")
        if daftar_item is not None:
            self.daftar_item = list(daftar_item)
        else:
            self.daftar_item = [ItemPinjam(alat) for alat in daftar_alat]
        if not self.daftar_item:
            raise ValueError("Transaksi harus memuat minimal satu alat.")
        self.status = StatusTransaksi.DIPINJAM
        self.update_status()

    def cari_item(self, kode):
        kode = kode.strip().upper()
        for item in self.daftar_item:
            if item.alat.kode == kode and not item.sudah_kembali:
                return item
        raise ValueError("Kode alat tidak ditemukan pada transaksi aktif ini.")

    def kembalikan_alat(self, kode, kondisi, tanggal=None):
        item = self.cari_item(kode)
        tanggal = tanggal or date.today()
        if tanggal < self.tanggal_pinjam:
            raise ValueError("Tanggal pengembalian tidak boleh sebelum tanggal peminjaman.")
        item.tandai_kembali(kondisi, tanggal)
        self.update_status()
        return item

    def update_status(self):
        if self.daftar_item and all(item.sudah_kembali for item in self.daftar_item):
            self.status = StatusTransaksi.SELESAI
        elif any(item.sudah_kembali for item in self.daftar_item):
            self.status = StatusTransaksi.SEBAGIAN_DIKEMBALIKAN
        else:
            self.status = StatusTransaksi.DIPINJAM

    def is_aktif(self):
        return self.status != StatusTransaksi.SELESAI

    def punya_alat(self, kode):
        """Benar bila alat masih dipinjam (belum dikembalikan) dalam transaksi ini."""
        kode = kode.strip().upper()
        return any(item.alat.kode == kode and not item.sudah_kembali for item in self.daftar_item)

    def pernah_memuat(self, kode):
        kode = kode.strip().upper()
        return any(item.alat.kode == kode for item in self.daftar_item)

    def __str__(self):
        item_text = ", ".join(
            f"{i.alat.kode}{' (kembali)' if i.sudah_kembali else ''}"
            for i in self.daftar_item
        )
        return (f"{self.id_transaksi} | {self.mahasiswa.nim} - {self.mahasiswa.nama} | "
                f"{self.tanggal_pinjam} s.d. {self.batas_kembali} | {self.status.value} | {item_text}")
