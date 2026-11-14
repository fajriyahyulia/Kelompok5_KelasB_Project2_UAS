#dikerjakan oleh
#Nama : Muzni Mubarok Salim
#NIM : K3525036
#Kelas : B / Semester 3
#Angkatan : 2025

from datetime import datetime

from models.mahasiswa import Mahasiswa
from models.alat import Alat
from models.item_pinjam import ItemPinjam
from models.transaksi import Transaksi
from models.enums import KondisiAlat, StatusTransaksi
from models.validasi import kode_wajib

FILE_MAHASISWA = "mahasiswa.txt"
FILE_ALAT = "alat.txt"
FILE_TRANSAKSI = "transaksi.txt"
FILE_DETAIL = "detail_transaksi.txt"
FILE_PEMELIHARAAN = "pemeliharaan.txt"

HEADER_MAHASISWA = "NIM|nama|no_hp|status_aktif"
HEADER_ALAT = "kode|nama|kategori|kondisi|status"
HEADER_TRANSAKSI = "id|nim|tgl_pinjam|batas_kembali|status"
HEADER_DETAIL = "id|kode|status|kondisi|tgl_kembali"
HEADER_PEMELIHARAAN = "kode|tgl_masuk"

STATUS_MAHASISWA = ("aktif", "tidak aktif")
STATUS_ALAT = ("tersedia", "dipinjam", "tidak tersedia")
KOSONG = "-"


def _tanggal(teks):
    try:
        return datetime.strptime(teks.strip(), "%Y-%m-%d").date()
    except ValueError:
        raise ValueError(f"tanggal '{teks}' tidak valid, gunakan format YYYY-MM-DD") from None


class Repositori:
    """Menerjemahkan antara file .txt dan objek di dalam manager.

    Manager tidak pernah menyentuh file. Mereka hanya memanggil simpan_*() di kelas ini,
    sedangkan format kolom setiap file hanya diketahui di sini.
    """

    def __init__(self, file_teks):
        self.file = file_teks
        self.mhs_mgr = None
        self.alat_mgr = None
        self.trx_mgr = None

    def hubungkan(self, mhs_mgr, alat_mgr, trx_mgr, log=None):
        self.mhs_mgr, self.alat_mgr, self.trx_mgr = mhs_mgr, alat_mgr, trx_mgr
        for mgr in (mhs_mgr, alat_mgr, trx_mgr):
            mgr.repositori = self
            mgr.log = log

    # ------------------------------------------------------------------
    # Menyimpan
    # ------------------------------------------------------------------
    def _berkas_mahasiswa(self):
        transaksi = self.trx_mgr.data
        baris = [[m.nim, m.nama, m.no_hp, m.status_aktif(transaksi)]
                 for m in self.mhs_mgr.data.values()]
        return (FILE_MAHASISWA, HEADER_MAHASISWA, baris)

    def _berkas_alat(self):
        baris = [[a.kode, a.nama, a.kategori, a.kondisi.teks, a.status_teks()]
                 for a in self.alat_mgr.data.values()]
        return (FILE_ALAT, HEADER_ALAT, baris)

    def _berkas_pemeliharaan(self):
        baris = [[kode, str(tgl)] for kode, tgl in self.alat_mgr.pemeliharaan.items()]
        return (FILE_PEMELIHARAAN, HEADER_PEMELIHARAAN, baris)

    def _berkas_transaksi(self):
        baris_trx, baris_detail = [], []
        for trx in self.trx_mgr.data:
            baris_trx.append([trx.id_transaksi, trx.mahasiswa.nim, str(trx.tanggal_pinjam),
                              str(trx.batas_kembali), trx.status.teks])
            for item in trx.daftar_item:
                if item.sudah_kembali:
                    baris_detail.append([trx.id_transaksi, item.alat.kode, "dikembalikan",
                                         item.kondisi_kembali.teks, str(item.tanggal_kembali)])
                else:
                    baris_detail.append([trx.id_transaksi, item.alat.kode, "dipinjam", KOSONG, KOSONG])
        return [(FILE_TRANSAKSI, HEADER_TRANSAKSI, baris_trx),
                (FILE_DETAIL, HEADER_DETAIL, baris_detail)]

    def simpan_mahasiswa(self):
        self.file.tulis_banyak([self._berkas_mahasiswa()])

    def simpan_alat(self):
        """Alat dan daftar pemeliharaan selalu ditulis bersama karena saling terkait."""
        self.file.tulis_banyak([self._berkas_alat(), self._berkas_pemeliharaan()])

    def simpan_semua(self):
        """Dipakai setelah transaksi, karena satu transaksi mengubah status mahasiswa,
        alat, dan transaksi sekaligus. Semua file diganti dalam satu langkah."""
        self.file.tulis_banyak([
            self._berkas_mahasiswa(), self._berkas_alat(), self._berkas_pemeliharaan(),
            *self._berkas_transaksi(),
        ])

    # ------------------------------------------------------------------
    # Memuat
    # ------------------------------------------------------------------
    def muat(self):
        """Baca semua file ke dalam manager. Mengembalikan daftar peringatan."""
        self.peringatan = []
        for mgr in (self.mhs_mgr, self.alat_mgr, self.trx_mgr):
            mgr.kosongkan()
        status_mhs = self._muat_mahasiswa()
        status_alat = self._muat_alat()
        self._muat_pemeliharaan()
        self._muat_transaksi()
        self._sinkronkan(status_mhs, status_alat)
        return self.peringatan

    def _baca(self, nama, kolom, header):
        baris, peringatan = self.file.baca(nama, kolom, header)
        self.peringatan.extend(peringatan)
        return baris

    def _tolak(self, nama, nomor, alasan):
        self.peringatan.append(f"{nama} baris {nomor}: {alasan}. Baris dilewati.")

    def _muat_mahasiswa(self):
        status_file = {}
        for nomor, k in self._baca(FILE_MAHASISWA, 4, HEADER_MAHASISWA):
            try:
                status = k[3].lower()
                if status not in STATUS_MAHASISWA:
                    raise ValueError(f"status_aktif '{k[3]}' tidak dikenal")
                m = Mahasiswa(k[0], k[1], k[2])
                self.mhs_mgr.tambah(m, simpan=False)
                status_file[m.nim] = status
            except ValueError as e:
                self._tolak(FILE_MAHASISWA, nomor, e)
        return status_file

    def _muat_alat(self):
        status_file = {}
        for nomor, k in self._baca(FILE_ALAT, 5, HEADER_ALAT):
            try:
                status = k[4].lower()
                if status not in STATUS_ALAT:
                    raise ValueError(f"status '{k[4]}' tidak dikenal")
                a = Alat(k[0], k[1], k[2], KondisiAlat.dari_teks(k[3]), tersedia=(status == "tersedia"))
                self.alat_mgr.tambah(a, simpan=False)
                status_file[a.kode] = status
            except ValueError as e:
                self._tolak(FILE_ALAT, nomor, e)
        return status_file

    def _muat_pemeliharaan(self):
        for nomor, k in self._baca(FILE_PEMELIHARAAN, 2, HEADER_PEMELIHARAAN):
            try:
                kode = kode_wajib(k[0], "Kode alat")
                alat = self.alat_mgr.data.get(kode)
                if alat is None:
                    raise ValueError(f"alat {kode} tidak ada di {FILE_ALAT}")
                if alat.kondisi == KondisiAlat.BAIK:
                    raise ValueError(f"alat {kode} berkondisi baik dan tidak perlu pemeliharaan")
                if kode in self.alat_mgr.pemeliharaan:
                    raise ValueError(f"alat {kode} tercatat ganda")
                self.alat_mgr.pemeliharaan[kode] = _tanggal(k[1])
            except ValueError as e:
                self._tolak(FILE_PEMELIHARAAN, nomor, e)

    def _muat_transaksi(self):
        header = {}
        for nomor, k in self._baca(FILE_TRANSAKSI, 5, HEADER_TRANSAKSI):
            try:
                id_trx = kode_wajib(k[0], "ID transaksi")
                if id_trx in header:
                    raise ValueError(f"ID transaksi {id_trx} ganda")
                mhs = self.mhs_mgr.data.get(k[1].strip().upper())
                if mhs is None:
                    raise ValueError(f"NIM {k[1]} tidak ada di {FILE_MAHASISWA}")
                StatusTransaksi.dari_teks(k[4])
                header[id_trx] = {"mhs": mhs, "tgl": _tanggal(k[2]), "batas": _tanggal(k[3]),
                                  "items": []}
            except ValueError as e:
                self._tolak(FILE_TRANSAKSI, nomor, e)

        dipakai, sedang_dipinjam = set(), set()
        for nomor, k in self._baca(FILE_DETAIL, 5, HEADER_DETAIL):
            try:
                id_trx = k[0].strip().upper()
                if id_trx not in header:
                    raise ValueError(f"ID transaksi {k[0]} tidak ada di {FILE_TRANSAKSI}")
                alat = self.alat_mgr.data.get(k[1].strip().upper())
                if alat is None:
                    raise ValueError(f"kode alat {k[1]} tidak ada di {FILE_ALAT}")
                if (id_trx, alat.kode) in dipakai:
                    raise ValueError(f"alat {alat.kode} tercatat ganda pada {id_trx}")
                status = k[2].lower()
                if status == "dipinjam":
                    if k[3] not in (KOSONG, "") or k[4] not in (KOSONG, ""):
                        raise ValueError("alat yang masih dipinjam seharusnya tanpa kondisi dan tanggal kembali")
                    if alat.kode in sedang_dipinjam:
                        raise ValueError(f"alat {alat.kode} tercatat dipinjam di dua transaksi sekaligus")
                    item = ItemPinjam(alat)
                    sedang_dipinjam.add(alat.kode)
                elif status == "dikembalikan":
                    kondisi = KondisiAlat.dari_teks(k[3])
                    tgl = _tanggal(k[4])
                    if tgl < header[id_trx]["tgl"]:
                        raise ValueError("tanggal kembali lebih awal dari tanggal pinjam")
                    item = ItemPinjam(alat, tgl, kondisi, True)
                else:
                    raise ValueError(f"status '{k[2]}' harus dipinjam atau dikembalikan")
                dipakai.add((id_trx, alat.kode))
                header[id_trx]["items"].append(item)
            except ValueError as e:
                self._tolak(FILE_DETAIL, nomor, e)

        for id_trx, h in header.items():
            try:
                trx = Transaksi(id_trx, h["mhs"], daftar_item=h["items"],
                                tanggal_pinjam=h["tgl"], batas_kembali=h["batas"])
                self.trx_mgr.tambah_dari_file(trx)
            except ValueError as e:
                self.peringatan.append(f"{FILE_TRANSAKSI}: transaksi {id_trx} dilewati ({e}).")

    def _sinkronkan(self, status_mhs, status_alat):
        """Status turunan (ketersediaan alat, status aktif mahasiswa) dihitung ulang dari
        data transaksi, lalu dibandingkan dengan isi file. Selisihnya dilaporkan."""
        sedang_dipinjam = {item.alat.kode for trx in self.trx_mgr.data
                           for item in trx.daftar_item if not item.sudah_kembali}
        for kode, alat in self.alat_mgr.data.items():
            alat.tersedia = alat.kondisi == KondisiAlat.BAIK and kode not in sedang_dipinjam
            if status_alat.get(kode) != alat.status_teks():
                self.peringatan.append(
                    f"{FILE_ALAT}: status {kode} di file '{status_alat.get(kode)}' tidak cocok dengan "
                    f"data transaksi, dikoreksi menjadi '{alat.status_teks()}'.")
        for nim, m in self.mhs_mgr.data.items():
            benar = m.status_aktif(self.trx_mgr.data)
            if status_mhs.get(nim) != benar:
                self.peringatan.append(
                    f"{FILE_MAHASISWA}: status_aktif {nim} di file '{status_mhs.get(nim)}' tidak cocok "
                    f"dengan transaksi, dikoreksi menjadi '{benar}'.")
