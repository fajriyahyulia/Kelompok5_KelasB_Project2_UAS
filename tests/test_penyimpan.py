#dikerjakan oleh
#Nama : Fajriyah Yulia Az Zahra
#NIM : K3525005
#Kelas : B / Semester 3
#Angkatan : 2025

import os
import shutil
import tempfile
import unittest
from datetime import date, datetime
from unittest import mock

from core.sistem import Sistem
from models.alat import Alat
from models.enums import KondisiAlat, StatusTransaksi
from models.mahasiswa import Mahasiswa
from storage.file_teks import FileTeks, PenyimpananError

FOLDER_PROYEK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def baca(folder, nama):
    with open(os.path.join(folder, nama), encoding="utf-8") as f:
        return f.read()


def baris_data(folder, nama):
    return [b for b in baca(folder, nama).splitlines() if b.strip() and not b.startswith("#")]


class DasarTes(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.folder = os.path.join(self.tmp, "data")
        self.s = Sistem(self.folder)
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def isi_awal(self):
        self.s.mhs_mgr.tambah(Mahasiswa("M001", "Andi Pratama", "081234567890"))
        self.s.mhs_mgr.tambah(Mahasiswa("M002", "Budi Santoso", "085612345678"))
        self.s.alat_mgr.tambah(Alat("A001", "Kamera Digital", "perangkat multimedia"))
        self.s.alat_mgr.tambah(Alat("A002", "Tripod", "perangkat multimedia"))
        self.s.alat_mgr.tambah(Alat("A003", "Kabel LAN", "perangkat jaringan"))

    def mulai_ulang(self):
        """Meniru menutup program lalu menjalankannya lagi."""
        return Sistem(self.folder)


class TestFileTeks(DasarTes):
    def test_file_belum_ada_dibuat_otomatis(self):
        f = FileTeks(os.path.join(self.tmp, "baru"))
        baris, peringatan = f.baca("x.txt", 2)
        self.assertEqual((baris, peringatan), ([], []))
        self.assertTrue(os.path.exists(f.jalur("x.txt")))

    def test_komentar_dan_baris_kosong_dilewati(self):
        f = FileTeks(self.tmp)
        f.tulis_teks("a.txt", "# judul\n\nA|1\n")
        baris, peringatan = f.baca("a.txt", 2)
        self.assertEqual([k for _, k in baris], [["A", "1"]])
        self.assertEqual(peringatan, [])

    def test_baris_salah_kolom_dilewati_dengan_peringatan(self):
        f = FileTeks(self.tmp)
        f.tulis_teks("a.txt", "A|1\nrusak\nB|2\n")
        baris, peringatan = f.baca("a.txt", 2)
        self.assertEqual(len(baris), 2)
        self.assertEqual(len(peringatan), 1)
        self.assertIn("baris 2", peringatan[0])

    def test_tulis_tidak_meninggalkan_file_sementara(self):
        folder = os.path.join(self.tmp, "bersih")
        f = FileTeks(folder)
        f.tulis("a.txt", "kolom1|kolom2", [["A", "1"]])
        self.assertEqual(sorted(os.listdir(folder)), ["a.txt"])

    def test_tulis_ke_lokasi_mustahil_melempar_penyimpananerror(self):
        berkas = os.path.join(self.tmp, "berkas")
        with open(berkas, "w") as f:
            f.write("x")
        with self.assertRaises(PenyimpananError):
            FileTeks(os.path.join(berkas, "dalam")).tulis("a.txt", None, [["A"]])

    def test_teks_dengan_pemisah_ditolak_model(self):
        with self.assertRaises(ValueError):
            Mahasiswa("M009", "Nama|Buruk", "08123456789")
        with self.assertRaises(ValueError):
            Alat("A009", "Alat", "kat|egori")


class TestSkenarioWajib(DasarTes):
    def test_skenario1_data_tercatat_di_file(self):
        self.isi_awal()
        self.assertEqual(len(baris_data(self.folder, "mahasiswa.txt")), 2)
        self.assertEqual(len(baris_data(self.folder, "alat.txt")), 3)
        self.assertIn("M001|Andi Pratama|081234567890|tidak aktif",
                      baris_data(self.folder, "mahasiswa.txt"))
        self.assertIn("A001|Kamera Digital|perangkat multimedia|baik|tersedia",
                      baris_data(self.folder, "alat.txt"))

    def test_skenario2_status_alat_di_program_dan_file(self):
        self.isi_awal()
        trx = self.s.trx_mgr.buat_transaksi("M001", ["A001", "A002"])
        self.assertFalse(self.s.alat_mgr.get("A001").is_tersedia())
        alat = baris_data(self.folder, "alat.txt")
        self.assertIn("A001|Kamera Digital|perangkat multimedia|baik|dipinjam", alat)
        self.assertIn("A002|Tripod|perangkat multimedia|baik|dipinjam", alat)
        self.assertIn("A003|Kabel LAN|perangkat jaringan|baik|tersedia", alat)
        self.assertEqual(len(baris_data(self.folder, "transaksi.txt")), 1)
        self.assertEqual(len(baris_data(self.folder, "detail_transaksi.txt")), 2)
        self.assertIn("M001|Andi Pratama|081234567890|aktif", baris_data(self.folder, "mahasiswa.txt"))
        self.assertEqual(trx.id_transaksi, "T001")

    def test_skenario3_penolakan_tidak_mengubah_file(self):
        self.isi_awal()
        self.s.trx_mgr.buat_transaksi("M001", ["A001"])
        sebelum = {n: baca(self.folder, n) for n in os.listdir(self.folder)}
        with self.assertRaises(ValueError):
            self.s.trx_mgr.buat_transaksi("M002", ["A001"])
        with self.assertRaises(ValueError):
            self.s.trx_mgr.buat_transaksi("M002", ["A999"])
        sesudah = {n: baca(self.folder, n) for n in os.listdir(self.folder)}
        # log.txt boleh bertambah, file data tidak
        for nama in ("mahasiswa.txt", "alat.txt", "transaksi.txt", "detail_transaksi.txt"):
            self.assertEqual(sebelum[nama], sesudah[nama], nama)

    def test_skenario4_pengembalian_sebagian(self):
        self.isi_awal()
        trx = self.s.trx_mgr.buat_transaksi("M001", ["A001", "A002"])
        self.s.trx_mgr.proses_pengembalian(trx.id_transaksi, "A001", KondisiAlat.BAIK,
                                           tanggal=date.today())
        self.assertEqual(trx.status, StatusTransaksi.SEBAGIAN_DIKEMBALIKAN)
        self.assertTrue(self.s.alat_mgr.get("A001").is_tersedia())
        self.assertFalse(self.s.alat_mgr.get("A002").is_tersedia())
        self.assertIn("sebagian dikembalikan", baris_data(self.folder, "transaksi.txt")[0])
        detail = baris_data(self.folder, "detail_transaksi.txt")
        self.assertTrue(any(b.startswith("T001|A001|dikembalikan|baik|") for b in detail))
        self.assertIn("T001|A002|dipinjam|-|-", detail)

    def test_skenario5_rusak_tidak_kembali_tersedia(self):
        self.isi_awal()
        trx = self.s.trx_mgr.buat_transaksi("M001", ["A001", "A002"])
        self.s.trx_mgr.proses_pengembalian(trx.id_transaksi, "A001", KondisiAlat.RUSAK_BERAT)
        self.s.trx_mgr.proses_pengembalian(trx.id_transaksi, "A002", KondisiAlat.RUSAK_RINGAN)
        alat = baris_data(self.folder, "alat.txt")
        self.assertIn("A001|Kamera Digital|perangkat multimedia|rusak berat|tidak tersedia", alat)
        self.assertIn("A002|Tripod|perangkat multimedia|rusak ringan|tidak tersedia", alat)
        self.assertEqual(self.s.alat_mgr.daftar_tersedia()[0].kode, "A003")

    def test_skenario6_hapus_mahasiswa_aktif_ditolak(self):
        self.isi_awal()
        self.s.trx_mgr.buat_transaksi("M001", ["A001"])
        sebelum = baca(self.folder, "mahasiswa.txt")
        with self.assertRaises(ValueError):
            self.s.trx_mgr.hapus_mahasiswa("M001")
        self.assertEqual(sebelum, baca(self.folder, "mahasiswa.txt"))

    def test_skenario7_data_bertahan_setelah_restart(self):
        self.isi_awal()
        t = self.s.trx_mgr.buat_transaksi("M001", ["A001", "A002"])
        self.s.trx_mgr.proses_pengembalian(t.id_transaksi, "A001", KondisiAlat.RUSAK_RINGAN,
                                           tanggal=date.today())
        baru = self.mulai_ulang()
        self.assertEqual(baru.peringatan, [])
        self.assertEqual(len(baru.mhs_mgr.data), 2)
        self.assertEqual(len(baru.alat_mgr.data), 3)
        trx = baru.trx_mgr.get("T001")
        self.assertEqual(trx.status, StatusTransaksi.SEBAGIAN_DIKEMBALIKAN)
        self.assertEqual(baru.alat_mgr.get("A001").kondisi, KondisiAlat.RUSAK_RINGAN)
        self.assertFalse(baru.alat_mgr.get("A001").is_tersedia())
        self.assertFalse(baru.alat_mgr.get("A002").is_tersedia())
        self.assertEqual([a.kode for a, _ in baru.trx_mgr.rincian_dipinjam()], ["A002"])
        self.assertEqual(baru.mhs_mgr.get("M001").status_aktif(baru.trx_mgr.data), "aktif")

    def test_skenario8_file_dihapus_program_tetap_jalan(self):
        self.isi_awal()
        os.remove(os.path.join(self.folder, "alat.txt"))
        open(os.path.join(self.folder, "mahasiswa.txt"), "w").close()  # dikosongkan
        baru = self.mulai_ulang()
        self.assertEqual(len(baru.alat_mgr.data), 0)
        self.assertEqual(len(baru.mhs_mgr.data), 0)
        self.assertTrue(os.path.exists(os.path.join(self.folder, "alat.txt")))
        baru.mhs_mgr.tambah(Mahasiswa("M010", "Baru", "081111111111"))
        self.assertEqual(len(baris_data(self.folder, "mahasiswa.txt")), 1)

    def test_skenario9_baris_salah_format_dilewati(self):
        self.isi_awal()
        with open(os.path.join(self.folder, "mahasiswa.txt"), "a", encoding="utf-8") as f:
            f.write("M099|Hanya Tiga Kolom|081234567890\n")
        baru = self.mulai_ulang()
        self.assertEqual(len(baru.peringatan), 1)
        self.assertIn("mahasiswa.txt baris", baru.peringatan[0])
        self.assertEqual(len(baru.mhs_mgr.data), 2)
        baru.mhs_mgr.tambah(Mahasiswa("M003", "Tetap Bisa Dipakai", "081222333444"))
        self.assertEqual(len(baru.mhs_mgr.data), 3)


class TestKonsistensiData(DasarTes):
    def test_id_transaksi_tetap_unik_setelah_restart(self):
        self.isi_awal()
        t1 = self.s.trx_mgr.buat_transaksi("M001", ["A001"])
        baru = self.mulai_ulang()
        t2 = baru.trx_mgr.buat_transaksi("M002", ["A002"])
        self.assertNotEqual(t1.id_transaksi, t2.id_transaksi)
        self.assertEqual(t2.id_transaksi, "T002")

    def test_tidak_ada_data_ganda_setelah_berkali_kali_dijalankan(self):
        self.isi_awal()
        self.s.trx_mgr.buat_transaksi("M001", ["A001"])
        for _ in range(3):
            baru = self.mulai_ulang()
            baru.simpan_semua()
        self.assertEqual(len(baris_data(self.folder, "mahasiswa.txt")), 2)
        self.assertEqual(len(baris_data(self.folder, "alat.txt")), 3)
        self.assertEqual(len(baris_data(self.folder, "transaksi.txt")), 1)
        self.assertEqual(len(baris_data(self.folder, "detail_transaksi.txt")), 1)

    def test_nim_dan_kode_ganda_di_file_dilewati(self):
        self.isi_awal()
        with open(os.path.join(self.folder, "mahasiswa.txt"), "a", encoding="utf-8") as f:
            f.write("M001|Kembaran|081234567890|aktif\n")
        with open(os.path.join(self.folder, "alat.txt"), "a", encoding="utf-8") as f:
            f.write("A001|Kembaran|x|baik|tersedia\n")
        baru = self.mulai_ulang()
        self.assertEqual(len(baru.peringatan), 2)
        self.assertEqual(baru.mhs_mgr.get("M001").nama, "Andi Pratama")

    def test_referensi_nim_tidak_ada_dilewati(self):
        self.isi_awal()
        self.s.trx_mgr.buat_transaksi("M001", ["A001"])
        with open(os.path.join(self.folder, "transaksi.txt"), "a", encoding="utf-8") as f:
            f.write("T009|M777|2026-11-01|2026-11-08|dipinjam\n")
        with open(os.path.join(self.folder, "detail_transaksi.txt"), "a", encoding="utf-8") as f:
            f.write("T009|A002|dipinjam|-|-\n")
        baru = self.mulai_ulang()
        self.assertEqual(len(baru.trx_mgr.data), 1)
        self.assertTrue(any("M777" in p for p in baru.peringatan))
        self.assertTrue(any("T009" in p for p in baru.peringatan))
        self.assertTrue(baru.alat_mgr.get("A002").is_tersedia())

    def test_kode_alat_tidak_ada_di_detail_dilewati(self):
        self.isi_awal()
        self.s.trx_mgr.buat_transaksi("M001", ["A001"])
        with open(os.path.join(self.folder, "detail_transaksi.txt"), "a", encoding="utf-8") as f:
            f.write("T001|A404|dipinjam|-|-\n")
        baru = self.mulai_ulang()
        self.assertTrue(any("A404" in p for p in baru.peringatan))
        self.assertEqual(len(baru.trx_mgr.get("T001").daftar_item), 1)

    def test_tanggal_tidak_valid_dilewati(self):
        self.isi_awal()
        with open(os.path.join(self.folder, "transaksi.txt"), "a", encoding="utf-8") as f:
            f.write("T005|M001|31-12-2026|2027-01-05|dipinjam\n")
        baru = self.mulai_ulang()
        self.assertEqual(len(baru.trx_mgr.data), 0)
        self.assertTrue(any("tanggal" in p for p in baru.peringatan))

    def test_status_alat_yang_salah_di_file_dikoreksi(self):
        self.isi_awal()
        self.s.trx_mgr.buat_transaksi("M001", ["A001"])
        jalur = os.path.join(self.folder, "alat.txt")
        isi = baca(self.folder, "alat.txt").replace("A001|Kamera Digital|perangkat multimedia|baik|dipinjam",
                                                    "A001|Kamera Digital|perangkat multimedia|baik|tersedia")
        with open(jalur, "w", encoding="utf-8") as f:
            f.write(isi)
        baru = self.mulai_ulang()
        self.assertFalse(baru.alat_mgr.get("A001").is_tersedia())
        self.assertTrue(any("dikoreksi" in p for p in baru.peringatan))

    def test_cadangan_otomatis_saat_ada_peringatan(self):
        self.isi_awal()
        with open(os.path.join(self.folder, "mahasiswa.txt"), "a", encoding="utf-8") as f:
            f.write("baris rusak\n")
        baru = self.mulai_ulang()
        self.assertIsNotNone(baru.cadangan_otomatis)
        salinan = os.path.join(baru.backup.folder_backup, baru.cadangan_otomatis)
        self.assertIn("baris rusak", baca(salinan, "mahasiswa.txt"))

    def test_tanpa_peringatan_tidak_ada_cadangan_otomatis(self):
        self.isi_awal()
        self.assertIsNone(self.mulai_ulang().cadangan_otomatis)

    def test_hapus_ditolak_bila_ada_riwayat_selesai(self):
        self.isi_awal()
        t = self.s.trx_mgr.buat_transaksi("M001", ["A001"])
        self.s.trx_mgr.proses_pengembalian(t.id_transaksi, "A001", KondisiAlat.BAIK)
        with self.assertRaises(ValueError):
            self.s.trx_mgr.hapus_mahasiswa("M001")
        with self.assertRaises(ValueError):
            self.s.trx_mgr.hapus_alat("A001")
        # mahasiswa dan alat tanpa riwayat tetap bisa dihapus
        self.assertTrue(self.s.trx_mgr.hapus_mahasiswa("M002"))
        self.assertTrue(self.s.trx_mgr.hapus_alat("A003"))
        self.assertEqual(len(baris_data(self.folder, "mahasiswa.txt")), 1)
        self.assertEqual(len(baris_data(self.folder, "alat.txt")), 2)
        self.assertEqual(self.mulai_ulang().peringatan, [])

    def test_edit_tersimpan(self):
        self.isi_awal()
        self.s.mhs_mgr.edit("M001", "Andi P. Nugroho", "")
        self.s.alat_mgr.edit("A001", "", "kategori baru")
        baru = self.mulai_ulang()
        self.assertEqual(baru.mhs_mgr.get("M001").nama, "Andi P. Nugroho")
        self.assertEqual(baru.alat_mgr.get("A001").kategori, "kategori baru")
        self.assertIn("kategori baru", baru.alat_mgr.kategori)

    def test_tanggal_kembali_dan_kondisi_tersimpan_utuh(self):
        self.isi_awal()
        t = self.s.trx_mgr.buat_transaksi("M001", ["A001"], tanggal_pinjam=date(2026, 11, 1))
        self.s.trx_mgr.proses_pengembalian(t.id_transaksi, "A001", KondisiAlat.RUSAK_BERAT,
                                           tanggal=date(2026, 11, 10))
        item = self.mulai_ulang().trx_mgr.get("T001").daftar_item[0]
        self.assertEqual(item.tanggal_kembali, date(2026, 11, 10))
        self.assertEqual(item.kondisi_kembali, KondisiAlat.RUSAK_BERAT)
        self.assertEqual(item.hari_terlambat(date(2026, 11, 8)), 2)


class TestGagalMenulis(DasarTes):
    """Bila file tidak bisa ditulis, memori harus kembali seperti semula (Aturan 7)."""

    def gagal(self):
        return mock.patch.object(self.s.repositori.file, "tulis_banyak",
                                 side_effect=PenyimpananError("disk penuh"))

    def test_tambah_mahasiswa_dibatalkan(self):
        with self.gagal(), self.assertRaises(PenyimpananError):
            self.s.mhs_mgr.tambah(Mahasiswa("M001", "Andi", "081234567890"))
        self.assertEqual(len(self.s.mhs_mgr.data), 0)

    def test_buat_transaksi_dibatalkan(self):
        self.isi_awal()
        with self.gagal(), self.assertRaises(PenyimpananError):
            self.s.trx_mgr.buat_transaksi("M001", ["A001"])
        self.assertEqual(self.s.trx_mgr.data, [])
        self.assertTrue(self.s.alat_mgr.get("A001").is_tersedia())

    def test_pengembalian_dibatalkan(self):
        self.isi_awal()
        trx = self.s.trx_mgr.buat_transaksi("M001", ["A001", "A002"])
        with self.gagal(), self.assertRaises(PenyimpananError):
            self.s.trx_mgr.proses_pengembalian(trx.id_transaksi, "A001", KondisiAlat.RUSAK_BERAT)
        self.assertEqual(trx.status, StatusTransaksi.DIPINJAM)
        self.assertEqual(self.s.alat_mgr.get("A001").kondisi, KondisiAlat.BAIK)
        self.assertFalse(trx.daftar_item[0].sudah_kembali)
        self.assertFalse(self.s.alat_mgr.get("A001").is_tersedia())

    def test_hapus_alat_dibatalkan(self):
        self.isi_awal()
        with self.gagal(), self.assertRaises(PenyimpananError):
            self.s.trx_mgr.hapus_alat("A003")
        self.assertIn("A003", self.s.alat_mgr.data)

    def test_edit_dibatalkan(self):
        self.isi_awal()
        with self.gagal(), self.assertRaises(PenyimpananError):
            self.s.mhs_mgr.edit("M001", "Nama Lain", "")
        self.assertEqual(self.s.mhs_mgr.get("M001").nama, "Andi Pratama")


class TestPemeliharaanLogBackupLaporan(DasarTes):
    def rusakkan_a001(self):
        self.isi_awal()
        t = self.s.trx_mgr.buat_transaksi("M001", ["A001"])
        self.s.trx_mgr.proses_pengembalian(t.id_transaksi, "A001", KondisiAlat.RUSAK_BERAT)

    def test_pemeliharaan_tersimpan_dan_kembali_ke_stok(self):
        self.rusakkan_a001()
        self.s.alat_mgr.masuk_pemeliharaan("A001", tanggal=date(2026, 11, 12))
        self.assertEqual(baris_data(self.folder, "pemeliharaan.txt"), ["A001|2026-11-12"])
        baru = self.mulai_ulang()
        self.assertEqual(baru.peringatan, [])
        self.assertEqual(len(baru.alat_mgr.daftar_pemeliharaan()), 1)
        baru.alat_mgr.selesai_pemeliharaan("A001")
        self.assertEqual(baris_data(self.folder, "pemeliharaan.txt"), [])
        self.assertTrue(self.mulai_ulang().alat_mgr.get("A001").is_tersedia())

    def test_pemeliharaan_alat_baik_ditolak(self):
        self.isi_awal()
        with self.assertRaises(ValueError):
            self.s.alat_mgr.masuk_pemeliharaan("A001")

    def test_log_ditambah_di_akhir_dan_tidak_terhapus(self):
        self.isi_awal()
        jumlah = len(self.s.log.entri)
        self.assertGreaterEqual(jumlah, 5)
        baru = self.mulai_ulang()
        baru.mhs_mgr.tambah(Mahasiswa("M003", "Citra", "087811223344"))
        baris = baris_data(self.folder, "log.txt")
        self.assertEqual(len(baris), jumlah + 1)
        self.assertIn("Mahasiswa M001 ditambahkan", baris[0])
        self.assertTrue(baris[-1].endswith("Mahasiswa M003 ditambahkan"))
        self.assertRegex(baris[0], r"^\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}\] ")

    def test_backup_dan_pemulihan(self):
        self.isi_awal()
        nama = self.s.backup.buat(waktu=datetime(2026, 11, 12, 10, 0))
        self.assertEqual(nama, "backup_2026-11-12")
        self.assertEqual(self.s.backup.buat(waktu=datetime(2026, 11, 12, 11, 0)), "backup_2026-11-12_2")
        self.s.trx_mgr.buat_transaksi("M001", ["A001"])
        self.s.mhs_mgr.tambah(Mahasiswa("M003", "Citra", "087811223344"))
        pengaman = self.s.backup.pulihkan(nama, waktu=datetime(2026, 11, 12, 12, 0))
        self.assertTrue(pengaman.startswith("sebelum_pulih_"))
        self.s.muat()
        self.assertEqual(len(self.s.mhs_mgr.data), 2)
        self.assertEqual(self.s.trx_mgr.data, [])
        self.assertTrue(self.s.alat_mgr.get("A001").is_tersedia())
        self.assertIn(pengaman, self.s.backup.daftar())

    def test_pulihkan_backup_tidak_ada_atau_tidak_lengkap(self):
        with self.assertRaises(ValueError):
            self.s.backup.pulihkan("backup_tidak_ada")
        os.makedirs(os.path.join(self.s.backup.folder_backup, "backup_kosong"))
        with self.assertRaises(ValueError):
            self.s.backup.pulihkan("backup_kosong")

    def test_laporan_dibuat_sebagai_text_file(self):
        self.rusakkan_a001()
        self.s.trx_mgr.buat_transaksi("M002", ["A002"])
        waktu = datetime(2026, 11, 12, 10, 30, 0)
        for jalur, isi in (
            (self.s.laporan.alat_dipinjam(waktu), "A002"),
            (self.s.laporan.alat_rusak(waktu), "rusak berat"),
            (self.s.laporan.riwayat_mahasiswa("M001", waktu), "T001"),
        ):
            self.assertTrue(os.path.exists(jalur))
            with open(jalur, encoding="utf-8") as f:
                self.assertIn(isi, f.read())

    def test_laporan_mahasiswa_tidak_ada_ditolak(self):
        with self.assertRaises(ValueError):
            self.s.laporan.riwayat_mahasiswa("M404")


class TestDataContoh(unittest.TestCase):
    """Folder data/ yang dikumpulkan harus lengkap, konsisten, dan memuat identitas kelompok."""

    def test_data_contoh_dimuat_tanpa_peringatan(self):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        folder = os.path.join(tmp, "data")
        shutil.copytree(os.path.join(FOLDER_PROYEK, "data"), folder)
        s = Sistem(folder)
        self.assertEqual(s.peringatan, [])
        self.assertGreaterEqual(len(s.mhs_mgr.data), 4)
        self.assertGreaterEqual(len(s.alat_mgr.data), 10)
        self.assertGreaterEqual(len(s.trx_mgr.data), 3)
        statuses = {t.status for t in s.trx_mgr.data}
        self.assertEqual(statuses, set(StatusTransaksi))


if __name__ == "__main__":
    unittest.main()