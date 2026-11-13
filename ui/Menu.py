#dikerjakan oleh
#Nama : Fajriyah Yulia Az Zahra
#NIM : K3525005
#Kelas : B / Semester 3
#Angkatan : 2025

import os

from models.mahasiswa import Mahasiswa
from models.alat import Alat
from models.enums import KondisiAlat
from storage.file_teks import PenyimpananError
from util import format as fmt

LEBAR = 72


class Menu:
    def __init__(self, sistem):
        self.sistem = sistem
        self.mhs_mgr = sistem.mhs_mgr
        self.alat_mgr = sistem.alat_mgr
        self.trx_mgr = sistem.trx_mgr

    # ------------------------------------------------------------------
    # Helper tampilan dan input
    # ------------------------------------------------------------------
    @staticmethod
    def _garis(karakter="-"):
        print(karakter * LEBAR)

    def _judul(self, teks):
        print()
        self._garis("=")
        print(teks.center(LEBAR))
        self._garis("=")

    def _tampil_menu(self, judul, pilihan):
        self._judul(judul)
        for nomor, label in pilihan:
            print(f"  [{nomor:>2}]  {label}")
        self._garis()

    @staticmethod
    def _sukses(pesan):
        print(f"\n[OK] {pesan}")

    @staticmethod
    def _gagal(pesan):
        print(f"\n[!] Error: {pesan}")

    @staticmethod
    def _peringatan(pesan):
        print(f"[PERINGATAN] {pesan}")

    @staticmethod
    def _input(prompt):
        return input(prompt).strip()

    def _tabel(self, header, baris):
        print(fmt.buat_tabel(header, baris))

    def _submenu(self, judul, pilihan_menu, aksi):
        """Loop submenu generik. Pilihan 0 selalu berarti kembali."""
        while True:
            self._tampil_menu(judul, pilihan_menu)
            p = self._input("Pilih: ")
            if p == "0":
                return
            try:
                if p in aksi:
                    aksi[p]()
                else:
                    self._gagal("Pilihan tidak valid.")
            except (ValueError, KeyError, PenyimpananError) as e:
                self._gagal(e)

    # ------------------------------------------------------------------
    # Menu utama
    # ------------------------------------------------------------------
    def jalankan(self):
        pilihan_menu = [
            ("1", "Kelola mahasiswa"),
            ("2", "Kelola alat"),
            ("3", "Buat transaksi peminjaman"),
            ("4", "Tampilkan transaksi"),
            ("5", "Proses pengembalian alat"),
            ("6", "Cari transaksi berdasarkan mahasiswa"),
            ("7", "Tampilkan alat tersedia"),
            ("8", "Tampilkan alat sedang dipinjam"),
            ("9", "Tampilkan alat rusak"),
            ("10", "Riwayat peminjaman mahasiswa"),
            ("11", "Statistik peminjaman"),
            ("12", "Pemeliharaan alat rusak"),
            ("13", "Log aktivitas"),
            ("14", "Backup dan pemulihan data"),
            ("15", "Ekspor laporan"),
            ("0", "Keluar (simpan semua data)"),
        ]
        aksi = {
            "1": self.menu_mahasiswa,
            "2": self.menu_alat,
            "3": self.buat_transaksi,
            "4": self.lihat_transaksi,
            "5": self.pengembalian,
            "6": self.cari_transaksi,
            "7": self.lihat_alat_tersedia,
            "8": self.lihat_alat_dipinjam,
            "9": self.lihat_alat_rusak,
            "10": self.lihat_riwayat,
            "11": self.tampilkan_statistik,
            "12": self.menu_pemeliharaan,
            "13": self.lihat_log,
            "14": self.menu_backup,
            "15": self.menu_laporan,
        }
        self._tampilkan_peringatan_muat()
        while True:
            self._tampil_menu("SISTEM PEMINJAMAN PERALATAN LABORATORIUM", pilihan_menu)
            try:
                pilihan = self._input("Pilih menu: ")
                if pilihan == "0":
                    break
                if pilihan in aksi:
                    aksi[pilihan]()
                else:
                    self._gagal("Pilihan tidak valid.")
            except (ValueError, KeyError, PenyimpananError) as e:
                self._gagal(e)
            except (KeyboardInterrupt, EOFError):
                print("\n\nProgram dihentikan.")
                break
        self._keluar()

    def _tampilkan_peringatan_muat(self):
        if self.sistem.peringatan:
            print("\nData dimuat dengan beberapa catatan:")
            for p in self.sistem.peringatan:
                self._peringatan(p)
            print("Baris yang dilewati akan hilang dari file pada penyimpanan berikutnya.")
            if self.sistem.cadangan_otomatis:
                folder = os.path.basename(self.sistem.backup.folder_backup)
                print(f"Salinan file asli sudah diamankan di {folder}/{self.sistem.cadangan_otomatis}.")

    def _keluar(self):
        try:
            self.sistem.simpan_semua()
            print("\nSemua data tersimpan. Program selesai. Terima kasih.")
        except PenyimpananError as e:
            self._gagal(f"Penyimpanan akhir gagal: {e}")

    # ------------------------------------------------------------------
    # Mahasiswa
    # ------------------------------------------------------------------
    def menu_mahasiswa(self):
        self._submenu(
            "KELOLA MAHASISWA",
            [("1", "Tambah"), ("2", "Edit"), ("3", "Hapus"), ("4", "Cari"),
             ("5", "Tampilkan semua"), ("0", "Kembali")],
            {
                "1": self._mhs_tambah,
                "2": self._mhs_edit,
                "3": self._mhs_hapus,
                "4": self._mhs_cari,
                "5": self._mhs_semua,
            },
        )

    def _mhs_tambah(self):
        m = Mahasiswa(input("NIM: "), input("Nama: "), input("No. HP: "))
        self.mhs_mgr.tambah(m)
        self._sukses("Mahasiswa berhasil ditambahkan dan disimpan.")

    def _mhs_edit(self):
        nim = self._input("NIM yang diedit: ")
        self.mhs_mgr.edit(
            nim,
            input("Nama baru (kosong = tetap): "),
            input("No. HP baru (kosong = tetap): "),
        )
        self._sukses("Data mahasiswa diperbarui.")

    def _mhs_hapus(self):
        self.trx_mgr.hapus_mahasiswa(self._input("NIM yang dihapus: "))
        self._sukses("Mahasiswa berhasil dihapus.")

    def _mhs_cari(self):
        kata = input("Kata kunci (NIM / nama): ")
        self._judul("HASIL PENCARIAN MAHASISWA")
        self._tampil_mahasiswa(self.mhs_mgr.cari(kata))

    def _mhs_semua(self):
        self._judul("DAFTAR MAHASISWA")
        self._tampil_mahasiswa(self.mhs_mgr.semua())

    def _tampil_mahasiswa(self, daftar):
        if not daftar:
            print("Data tidak ditemukan.")
            return
        self._tabel(fmt.HEADER_MAHASISWA, fmt.baris_mahasiswa(daftar, self.trx_mgr.data))

    # ------------------------------------------------------------------
    # Alat
    # ------------------------------------------------------------------
    def menu_alat(self):
        self._submenu(
            "KELOLA ALAT",
            [("1", "Tambah"), ("2", "Edit"), ("3", "Hapus"),
             ("4", "Cari fleksibel (kode / nama / kategori)"),
             ("5", "Tampilkan semua"), ("6", "Tampilkan kategori"), ("0", "Kembali")],
            {
                "1": self._alat_tambah,
                "2": self._alat_edit,
                "3": self._alat_hapus,
                "4": self._alat_cari,
                "5": self._alat_semua,
                "6": self._alat_kategori,
            },
        )

    def _alat_tambah(self):
        kode = input("Kode alat: ")
        nama = input("Nama alat: ")
        kategori = input("Kategori (boleh kategori baru): ")
        kondisi = self._input("Kondisi awal (baik / rusak ringan / rusak berat, kosong = baik): ")
        kondisi = KondisiAlat.dari_teks(kondisi) if kondisi else KondisiAlat.BAIK
        self.alat_mgr.tambah(Alat(kode, nama, kategori, kondisi))
        self._sukses("Alat berhasil ditambahkan dan disimpan.")

    def _alat_edit(self):
        kode = input("Kode alat yang diedit: ")
        self.alat_mgr.edit(
            kode,
            input("Nama baru (kosong = tetap): "),
            input("Kategori baru (kosong = tetap): "),
        )
        self._sukses("Data alat diperbarui.")

    def _alat_hapus(self):
        self.trx_mgr.hapus_alat(input("Kode alat yang dihapus: "))
        self._sukses("Alat berhasil dihapus.")

    def _alat_cari(self):
        print("Cari berdasarkan: [1] semua bidang  [2] kode  [3] nama  [4] kategori")
        bidang = {"1": "semua", "2": "kode", "3": "nama", "4": "kategori"}.get(
            self._input("Pilihan (default 1): ") or "1")
        if bidang is None:
            raise ValueError("Pilihan bidang tidak valid.")
        kata = input("Kata kunci: ")
        self._judul("HASIL PENCARIAN ALAT")
        self._tampil_alat(self.alat_mgr.cari(kata, bidang))

    def _alat_semua(self):
        self._judul("DAFTAR ALAT")
        self._tampil_alat(self.alat_mgr.semua())

    def _alat_kategori(self):
        self._judul("KATEGORI ALAT")
        daftar = sorted(self.alat_mgr.kategori)
        print("\n".join(f"  - {k}" for k in daftar) if daftar else "Belum ada kategori.")

    def _tampil_alat(self, daftar):
        if not daftar:
            print("Data tidak ditemukan.")
            return
        self._tabel(fmt.HEADER_ALAT, fmt.baris_alat(daftar))

    # ------------------------------------------------------------------
    # Pemeliharaan alat (Tantangan C)
    # ------------------------------------------------------------------
    def menu_pemeliharaan(self):
        self._submenu(
            "PEMELIHARAAN ALAT",
            [("1", "Lihat daftar pemeliharaan"), ("2", "Masukkan alat rusak ke pemeliharaan"),
             ("3", "Tandai alat selesai diperbaiki"), ("0", "Kembali")],
            {
                "1": self._pemeliharaan_lihat,
                "2": self._pemeliharaan_masuk,
                "3": self._pemeliharaan_selesai,
            },
        )

    def _pemeliharaan_lihat(self):
        self._judul("DAFTAR PEMELIHARAAN")
        baris = [(a.kode, a.nama, a.kondisi.teks, str(tgl))
                 for a, tgl in self.alat_mgr.daftar_pemeliharaan()]
        if baris:
            self._tabel(("Kode", "Nama", "Kondisi", "Masuk tanggal"), baris)
        else:
            print("Tidak ada alat dalam pemeliharaan.")

    def _pemeliharaan_masuk(self):
        alat = self.alat_mgr.masuk_pemeliharaan(input("Kode alat rusak: "))
        self._sukses(f"{alat.kode} masuk daftar pemeliharaan.")

    def _pemeliharaan_selesai(self):
        alat = self.alat_mgr.selesai_pemeliharaan(input("Kode alat yang selesai diperbaiki: "))
        self._sukses(f"{alat.kode} kembali berkondisi baik dan tersedia.")

    # ------------------------------------------------------------------
    # Transaksi
    # ------------------------------------------------------------------
    def buat_transaksi(self):
        self._judul("BUAT TRANSAKSI PEMINJAMAN")
        nim = self._input("NIM peminjam: ")
        kode = input("Kode alat (pisahkan dengan koma): ").split(",")
        trx = self.trx_mgr.buat_transaksi(nim, kode)
        self._sukses("Transaksi berhasil dibuat dan disimpan.")
        self._tampil_transaksi([trx])

    def pengembalian(self):
        self._judul("PENGEMBALIAN ALAT")
        trx_id = self._input("ID transaksi: ")
        kode = self._input("Kode alat yang dikembalikan: ")
        print("Kondisi alat: baik, rusak ringan, atau rusak berat")
        kondisi = KondisiAlat.dari_teks(self._input("Kondisi alat: "))
        item = self.trx_mgr.proses_pengembalian(trx_id, kode, kondisi)
        self._sukses(f"Pengembalian {item.alat.kode} berhasil dicatat dan disimpan.")
        self._tampil_transaksi([self.trx_mgr.get(trx_id)])

    def lihat_transaksi(self):
        self._judul("DAFTAR TRANSAKSI")
        self._tampil_transaksi(self.trx_mgr.semua())

    def cari_transaksi(self):
        nim = self._input("NIM: ")
        self._judul(f"TRANSAKSI MAHASISWA {nim.upper()}")
        self._tampil_transaksi(self.trx_mgr.cari_by_mahasiswa(nim))

    def lihat_riwayat(self):
        nim = self._input("NIM: ")
        self._judul(f"RIWAYAT PEMINJAMAN {nim.upper()}")
        self._tampil_transaksi(self.trx_mgr.riwayat_mahasiswa(nim))

    def lihat_alat_tersedia(self):
        self._judul("ALAT TERSEDIA")
        self._tampil_alat(self.alat_mgr.daftar_tersedia())

    def lihat_alat_dipinjam(self):
        self._judul("ALAT SEDANG DIPINJAM")
        rincian = self.trx_mgr.rincian_dipinjam()
        if not rincian:
            print("Data tidak ditemukan.")
            return
        self._tabel(fmt.HEADER_DIPINJAM, fmt.baris_dipinjam(rincian))

    def lihat_alat_rusak(self):
        self._judul("ALAT RUSAK")
        self._tampil_alat(self.alat_mgr.daftar_rusak())

    def _tampil_transaksi(self, daftar):
        if not daftar:
            print("Transaksi tidak ditemukan.")
            return
        for trx in daftar:
            print(fmt.teks_transaksi(trx))
            self._garis()
        print(f"Total: {len(daftar)} transaksi")

    # ------------------------------------------------------------------
    # Statistik (Tantangan B)
    # ------------------------------------------------------------------
    def tampilkan_statistik(self):
        s = self.trx_mgr.statistik_peminjaman()
        self._judul("STATISTIK PEMINJAMAN")

        print("\nAlat terpopuler")
        if s["alat_terpopuler"]:
            baris = [(no, kode, nama, f"{n}x")
                     for no, (kode, nama, n) in enumerate(s["alat_terpopuler"], start=1)]
            self._tabel(("#", "Kode", "Nama", "Dipinjam"), baris)
        else:
            print("-")

        print("\nMahasiswa teraktif")
        if s["mahasiswa_teraktif"]:
            baris = [(no, nim, nama, f"{n} transaksi")
                     for no, (nim, nama, n) in enumerate(s["mahasiswa_teraktif"], start=1)]
            self._tabel(("#", "NIM", "Nama", "Jumlah"), baris)
        else:
            print("-")

        print("\nRingkasan transaksi")
        self._tabel(("Keterangan", "Jumlah"),
                    [("Transaksi aktif", s["transaksi_aktif"]),
                     ("Transaksi selesai", s["transaksi_selesai"])])

    # ------------------------------------------------------------------
    # Log aktivitas (Tantangan D)
    # ------------------------------------------------------------------
    def lihat_log(self):
        self._judul("LOG AKTIVITAS")
        terakhir = self.sistem.log.terakhir(25)
        if not terakhir:
            print("Belum ada aktivitas tercatat.")
            return
        print("\n".join(terakhir))
        print(f"\nMenampilkan {len(terakhir)} dari {len(self.sistem.log.entri)} catatan. "
              f"Log lengkap ada di file log.txt.")

    # ------------------------------------------------------------------
    # Backup dan pemulihan (Tantangan E)
    # ------------------------------------------------------------------
    def menu_backup(self):
        self._submenu(
            "BACKUP DAN PEMULIHAN DATA",
            [("1", "Buat backup sekarang"), ("2", "Lihat daftar backup"),
             ("3", "Pulihkan data dari backup"), ("0", "Kembali")],
            {
                "1": self._backup_buat,
                "2": self._backup_daftar,
                "3": self._backup_pulihkan,
            },
        )

    def _backup_buat(self):
        nama = self.sistem.backup.buat()
        self.sistem.log.catat(f"Backup dibuat: {nama}")
        self._sukses(f"Backup tersimpan di folder {nama}.")

    def _backup_daftar(self):
        daftar = self.sistem.backup.daftar()
        self._judul("DAFTAR BACKUP")
        if not daftar:
            print("Belum ada backup.")
            return
        for no, nama in enumerate(daftar, start=1):
            print(f"  [{no:>2}]  {nama}")

    def _backup_pulihkan(self):
        daftar = self.sistem.backup.daftar()
        if not daftar:
            raise ValueError("Belum ada backup yang bisa dipulihkan.")
        self._backup_daftar()
        nomor = self._input("Nomor backup yang dipulihkan (kosong = batal): ")
        if not nomor:
            print("Dibatalkan.")
            return
        if not (nomor.isdigit() and 1 <= int(nomor) <= len(daftar)):
            raise ValueError("Nomor backup tidak valid.")
        nama = daftar[int(nomor) - 1]
        print(f"Data saat ini akan diganti dengan isi {nama}.")
        if self._input("Ketik YA untuk melanjutkan: ").upper() != "YA":
            print("Dibatalkan.")
            return
        pengaman = self.sistem.backup.pulihkan(nama)
        peringatan = self.sistem.muat()
        self.sistem.log.catat(f"Data dipulihkan dari {nama}")
        self._sukses(f"Data dipulihkan dari {nama}. Kondisi sebelumnya diamankan di {pengaman}.")
        for p in peringatan:
            self._peringatan(p)

    # ------------------------------------------------------------------
    # Ekspor laporan (Tantangan F)
    # ------------------------------------------------------------------
    def menu_laporan(self):
        self._submenu(
            "EKSPOR LAPORAN",
            [("1", "Laporan alat yang sedang dipinjam"), ("2", "Laporan alat rusak"),
             ("3", "Laporan riwayat peminjaman seorang mahasiswa"), ("0", "Kembali")],
            {
                "1": lambda: self._laporan_jadi(self.sistem.laporan.alat_dipinjam()),
                "2": lambda: self._laporan_jadi(self.sistem.laporan.alat_rusak()),
                "3": lambda: self._laporan_jadi(
                    self.sistem.laporan.riwayat_mahasiswa(self._input("NIM: "))),
            },
        )

    @staticmethod
    def _jalur_ringkas(jalur):
        try:
            return os.path.relpath(jalur)
        except ValueError:  # beda drive di Windows
            return jalur

    def _laporan_jadi(self, jalur):
        ringkas = self._jalur_ringkas(jalur)
        self.sistem.log.catat(f"Laporan dibuat: {ringkas}")
        self._sukses(f"Laporan tersimpan di {ringkas}")