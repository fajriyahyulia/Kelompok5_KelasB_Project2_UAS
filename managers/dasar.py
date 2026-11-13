#dikerjakan oleh
#Nama : Sulthan Hafizh Putra Agung
#NIM : K3525013
#Kelas : B / Semester 3
#Angkatan : 2025

from storage.file_teks import PenyimpananError


class ManagerDasar:
    """Kemampuan bersama semua manager: menyimpan ke file dan mencatat log.

    Bila penyimpanan gagal, perubahan di memori dibatalkan lewat fungsi `batalkan`
    supaya data di program dan data di file tetap sama (Aturan 7).
    """

    def __init__(self):
        self.repositori = None
        self.log = None

    def _simpan(self, nama_metode, batalkan=None):
        if self.repositori is None:
            return
        try:
            getattr(self.repositori, nama_metode)()
        except PenyimpananError:
            if batalkan is not None:
                batalkan()
            raise

    def _catat(self, pesan):
        if self.log is not None:
            self.log.catat(pesan)