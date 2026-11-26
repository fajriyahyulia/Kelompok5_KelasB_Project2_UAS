#dikerjakan oleh
#Nama : Zahra Faizza Kuncoroningrum
#NIM : K3525017
#Kelas : B / Semester 3
#Angkatan : 2025

from datetime import datetime

from storage.file_teks import FileTeks
from util import format as fmt


class PembuatLaporan:
    """Ekspor laporan ke text file yang rapi (Tantangan F)."""

    def __init__(self, folder_laporan, mhs_mgr, alat_mgr, trx_mgr):
        self.file = FileTeks(folder_laporan)
        self.mhs_mgr = mhs_mgr
        self.alat_mgr = alat_mgr
        self.trx_mgr = trx_mgr

    def _tulis(self, nama_dasar, judul, isi, waktu):
        waktu = waktu or datetime.now()
        nama = f"{nama_dasar}_{waktu.strftime('%Y-%m-%d_%H%M%S')}.txt"
        garis = "=" * 72
        teks = f"{garis}\n{judul.center(72)}\n{garis}\nDibuat: {waktu.strftime('%Y-%m-%d %H:%M')}\n\n{isi}\n"
        self.file.tulis_teks(nama, teks)
        return self.file.jalur(nama)

    def alat_dipinjam(self, waktu=None):
        tabel = fmt.buat_tabel(fmt.HEADER_DIPINJAM, fmt.baris_dipinjam(self.trx_mgr.rincian_dipinjam()))
        return self._tulis("laporan_alat_dipinjam", "LAPORAN ALAT SEDANG DIPINJAM", tabel, waktu)

    def alat_rusak(self, waktu=None):
        tabel = fmt.buat_tabel(fmt.HEADER_ALAT, fmt.baris_alat(self.alat_mgr.daftar_rusak()))
        return self._tulis("laporan_alat_rusak", "LAPORAN ALAT RUSAK", tabel, waktu)

    def riwayat_mahasiswa(self, nim, waktu=None):
        mhs = self.mhs_mgr.get(nim)
        daftar = self.trx_mgr.riwayat_mahasiswa(mhs.nim)
        isi = f"Mahasiswa: {mhs.nim} - {mhs.nama}\n\n"
        if daftar:
            isi += ("\n" + "-" * 72 + "\n").join(fmt.teks_transaksi(t) for t in daftar)
            isi += f"\n\nTotal: {len(daftar)} transaksi"
        else:
            isi += "Belum ada transaksi."
        return self._tulis(f"laporan_riwayat_{mhs.nim}", f"RIWAYAT PEMINJAMAN {mhs.nim}", isi, waktu)
