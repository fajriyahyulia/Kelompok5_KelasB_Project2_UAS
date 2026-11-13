#dikerjakan oleh
#Nama : Sulthan Hafizh Putra Agung
#NIM : K3525013
#Kelas : B / Semester 3
#Angkatan : 2025

import os
from datetime import datetime

from storage.file_teks import FileTeks, PenyimpananError

BERKAS_DATA = ("mahasiswa.txt", "alat.txt", "transaksi.txt", "detail_transaksi.txt",
               "pemeliharaan.txt", "log.txt")
BERKAS_INTI = BERKAS_DATA[:4]


class PengelolaBackup:
    """Backup dan pemulihan (Tantangan E). Satu backup adalah satu folder bernama
    backup_YYYY-MM-DD berisi salinan semua file data."""

    def __init__(self, file_data, folder_backup):
        self.file_data = file_data
        self.folder_backup = folder_backup

    def _nama_unik(self, awalan, waktu):
        dasar = f"{awalan}_{waktu.strftime('%Y-%m-%d')}"
        nama, urutan = dasar, 2
        while os.path.exists(os.path.join(self.folder_backup, nama)):
            nama = f"{dasar}_{urutan}"
            urutan += 1
        return nama

    def buat(self, awalan="backup", waktu=None):
        waktu = waktu or datetime.now()
        nama = self._nama_unik(awalan, waktu)
        tujuan = os.path.join(self.folder_backup, nama)
        for berkas in BERKAS_DATA:
            self.file_data.salin(berkas, tujuan)
        return nama

    def daftar(self):
        try:
            isi = os.listdir(self.folder_backup)
        except FileNotFoundError:
            return []
        except OSError as e:
            raise PenyimpananError(f"Gagal membaca folder backup: {e}") from e
        return sorted(n for n in isi if os.path.isdir(os.path.join(self.folder_backup, n)))

    def pulihkan(self, nama, waktu=None):
        """Kembalikan data dari backup. Kondisi saat ini diamankan dulu ke folder
        sebelum_pulih_..., lalu backup yang dipilih disalin ke folder data."""
        if nama not in self.daftar():
            raise ValueError("Backup tidak ditemukan.")
        sumber = FileTeks(os.path.join(self.folder_backup, nama))
        kurang = [b for b in BERKAS_INTI if not os.path.exists(sumber.jalur(b))]
        if kurang:
            raise ValueError(f"Backup tidak lengkap, file hilang: {', '.join(kurang)}.")
        pengaman = self.buat("sebelum_pulih", waktu)
        for berkas in BERKAS_DATA:
            sumber.salin(berkas, self.file_data.folder)
        return pengaman
