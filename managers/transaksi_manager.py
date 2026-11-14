#dikerjakan oleh
#Nama : Zahra Faizza Kuncoroningrum
#NIM : K3525017
#Kelas : B / Semester 3
#Angkatan : 2025

from managers.dasar import ManagerDasar
from models.transaksi import Transaksi


class TransaksiManager(ManagerDasar):
    PREFIX_ID = "T"

    def __init__(self, mahasiswa_manager, alat_manager):
        super().__init__()
        self.data = []
        self.mahasiswa_manager = mahasiswa_manager
        self.alat_manager = alat_manager

    def kosongkan(self):
        self.data.clear()

    def tambah_dari_file(self, trx):
        """Dipakai Repositori saat memuat. Tidak menyimpan dan tidak mencatat log."""
        self.data.append(trx)

    def _id_berikutnya(self):
        """ID dihitung dari data yang ada, jadi tetap unik setelah program dijalankan ulang."""
        angka = []
        for trx in self.data:
            digit = "".join(ch for ch in trx.id_transaksi if ch.isdigit())
            if digit:
                angka.append(int(digit))
        nomor = max(angka, default=0) + 1
        terpakai = {trx.id_transaksi for trx in self.data}
        while f"{self.PREFIX_ID}{nomor:03d}" in terpakai:
            nomor += 1
        return f"{self.PREFIX_ID}{nomor:03d}"

    def buat_transaksi(self, nim, daftar_kode, tanggal_pinjam=None):
        # Semua pemeriksaan dilakukan sebelum ada data yang berubah, sehingga
        # transaksi yang ditolak tidak menyentuh memori maupun file (Aturan 7).
        mahasiswa = self.mahasiswa_manager.get(nim)
        if not mahasiswa.boleh_pinjam(self.data):
            raise ValueError(
                f"Mahasiswa sudah memiliki {mahasiswa.MAKS_TRANSAKSI_AKTIF} transaksi aktif.")
        kode_unik = [k.strip().upper() for k in daftar_kode if k.strip()]
        if not kode_unik:
            raise ValueError("Pilih minimal satu alat.")
        if len(kode_unik) != len(set(kode_unik)):
            raise ValueError("Kode alat tidak boleh dipilih dua kali dalam satu transaksi.")
        alat_list = [self.alat_manager.get(k) for k in kode_unik]
        tidak_tersedia = [a.kode for a in alat_list if not a.is_tersedia()]
        if tidak_tersedia:
            raise ValueError(f"Alat {', '.join(tidak_tersedia)} tidak tersedia.")

        trx = Transaksi(self._id_berikutnya(), mahasiswa, alat_list, tanggal_pinjam=tanggal_pinjam)
        for alat in alat_list:
            alat.set_tersedia(False)
        self.data.append(trx)

        def batalkan():
            self.data.remove(trx)
            for alat in alat_list:
                alat.set_tersedia(True)

        self._simpan("simpan_semua", batalkan)
        self._catat(f"Transaksi {trx.id_transaksi} dibuat untuk {mahasiswa.nim}, alat: "
                    f"{', '.join(kode_unik)}")
        return trx

    def proses_pengembalian(self, id_transaksi, kode, kondisi, tanggal=None):
        trx = self.get(id_transaksi)
        alat = trx.cari_item(kode).alat
        keadaan_lama = (alat.kondisi, alat.tersedia, trx.status)
        item = trx.kembalikan_alat(kode, kondisi, tanggal)

        def batalkan():
            item.sudah_kembali = False
            item.tanggal_kembali = None
            item.kondisi_kembali = None
            alat.kondisi, alat.tersedia, trx.status = keadaan_lama

        self._simpan("simpan_semua", batalkan)
        self._catat(f"Alat {alat.kode} dikembalikan pada {trx.id_transaksi}, kondisi "
                    f"{item.kondisi_kembali.teks}")
        if not trx.is_aktif():
            self._catat(f"Transaksi {trx.id_transaksi} selesai")
        return item

    def get(self, id_transaksi):
        for trx in self.data:
            if trx.id_transaksi.upper() == id_transaksi.strip().upper():
                return trx
        raise ValueError("Transaksi tidak ditemukan.")

    def cari_by_mahasiswa(self, nim):
        nim = nim.strip().upper()
        return [trx for trx in self.data if trx.mahasiswa.nim == nim]

    def riwayat_mahasiswa(self, nim):
        return self.cari_by_mahasiswa(nim)

    def semua(self):
        return list(self.data)

    def hapus_mahasiswa(self, nim):
        return self.mahasiswa_manager.hapus(nim, self.data)

    def hapus_alat(self, kode):
        return self.alat_manager.hapus(kode, self.data)

    def alat_dipinjam(self):
        return [item for trx in self.data for item in trx.daftar_item if not item.sudah_kembali]

    def rincian_dipinjam(self):
        """Pasangan (alat, transaksi) untuk setiap alat yang masih dipinjam, urut kode alat."""
        hasil = [(item.alat, trx) for trx in self.data
                 for item in trx.daftar_item if not item.sudah_kembali]
        return sorted(hasil, key=lambda pasangan: pasangan[0].kode)

    def alat_ada_di_trx_aktif(self, kode):
        return any(trx.is_aktif() and trx.punya_alat(kode) for trx in self.data)

    def statistik_peminjaman(self):
        frek_alat, nama_alat = {}, {}
        frek_mhs, nama_mhs = {}, {}
        for trx in self.data:
            nim = trx.mahasiswa.nim
            frek_mhs[nim] = frek_mhs.get(nim, 0) + 1
            nama_mhs[nim] = trx.mahasiswa.nama
            for item in trx.daftar_item:
                kode = item.alat.kode
                frek_alat[kode] = frek_alat.get(kode, 0) + 1
                nama_alat[kode] = item.alat.nama
        urut = lambda x: (-x[2], x[0])
        return {
            "alat_terpopuler": sorted(((k, nama_alat[k], n) for k, n in frek_alat.items()), key=urut),
            "mahasiswa_teraktif": sorted(((k, nama_mhs[k], n) for k, n in frek_mhs.items()), key=urut),
            "transaksi_selesai": sum(1 for t in self.data if not t.is_aktif()),
            "transaksi_aktif": sum(1 for t in self.data if t.is_aktif()),
        }
