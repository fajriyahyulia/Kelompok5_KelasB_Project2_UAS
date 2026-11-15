#dikerjakan oleh
#Nama : Muzni Mubarok Salim
#NIM : K3525036
#Kelas : B / Semester 3
#Angkatan : 2025

from models.validasi import kode_wajib, teks_wajib, no_hp_valid


class Mahasiswa:
    MAKS_TRANSAKSI_AKTIF = 2

    def __init__(self, nim: str, nama: str, no_hp: str):
        self.nim = kode_wajib(nim, "NIM")
        self.nama = teks_wajib(nama, "Nama")
        self.no_hp = no_hp_valid(no_hp)

    def ubah(self, nama=None, no_hp=None):
        nama_baru = teks_wajib(nama, "Nama") if nama and nama.strip() else self.nama
        hp_baru = no_hp_valid(no_hp) if no_hp and no_hp.strip() else self.no_hp
        self.nama, self.no_hp = nama_baru, hp_baru

    def jumlah_transaksi_aktif(self, transaksi_list):
        return sum(
            1 for trx in transaksi_list
            if trx.mahasiswa.nim == self.nim and trx.is_aktif()
        )

    def status_aktif(self, transaksi_list):
        return "aktif" if self.jumlah_transaksi_aktif(transaksi_list) > 0 else "tidak aktif"

    def boleh_pinjam(self, transaksi_list):
        return self.jumlah_transaksi_aktif(transaksi_list) < self.MAKS_TRANSAKSI_AKTIF

    def boleh_dihapus(self, transaksi_list):
        return self.jumlah_transaksi_aktif(transaksi_list) == 0

    def punya_riwayat(self, transaksi_list):
        return any(trx.mahasiswa.nim == self.nim for trx in transaksi_list)

    def __str__(self):
        return f"{self.nim} - {self.nama} (HP: {self.no_hp})"
