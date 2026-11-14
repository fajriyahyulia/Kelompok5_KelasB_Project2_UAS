#dikerjakan oleh
#Nama : Muzni Mubarok Salim
#NIM : K3525036
#Kelas : B / Semester 3
#Angkatan : 2025

import os

class PenyimpananError(Exception):
    """Gagal membaca atau menulis file data."""
class FileTeks:
    """Satu-satunya tempat operasi baca/tulis text file.
    Kelas ini tidak tahu apa-apa tentang mahasiswa, alat, atau transaksi. Tugasnya
    hanya membuka file dengan open() + with, memecah dan merangkai baris dengan
    split() dan join(), serta menangani kesalahan file dengan try-except.
    """
    PEMISAH = "|"

    def __init__(self, folder):
        self.folder = folder

    def jalur(self, nama):
        return os.path.join(self.folder, nama)

    def pastikan_ada(self, nama, header=None):
        """Buat file kosong (dengan baris judul bila ada) kalau belum ada."""
        jalur = self.jalur(nama)
        if os.path.exists(jalur):
            return
        try:
            os.makedirs(self.folder, exist_ok=True)
            with open(jalur, "w", encoding="utf-8", newline="\n") as f:
                if header:
                    f.write(f"# {header}\n")
        except OSError as e:
            raise PenyimpananError(f"Gagal membuat {nama}: {e}") from e

    def baca(self, nama, jumlah_kolom, header=None):
        """Baca file berpemisah. Hasilnya (daftar (nomor_baris, kolom), daftar peringatan).

        Baris kosong dan baris berawalan # dilewati. Baris dengan jumlah kolom salah
        dilewati dengan peringatan, sehingga program tetap bisa berjalan.
        """
        self.pastikan_ada(nama, header)
        baris_valid, peringatan = [], []
        try:
            with open(self.jalur(nama), "r", encoding="utf-8") as f:
                for nomor, mentah in enumerate(f, start=1):
                    teks = mentah.strip()
                    if not teks or teks.startswith("#"):
                        continue
                    kolom = [k.strip() for k in teks.split(self.PEMISAH)]
                    if len(kolom) != jumlah_kolom:
                        peringatan.append(
                            f"{nama} baris {nomor}: ditemukan {len(kolom)} kolom, seharusnya "
                            f"{jumlah_kolom}. Baris dilewati.")
                        continue
                    baris_valid.append((nomor, kolom))
        except (OSError, UnicodeDecodeError) as e:
            raise PenyimpananError(f"Gagal membaca {nama}: {e}") from e
        return baris_valid, peringatan

    def baca_baris_mentah(self, nama):
        """Semua baris tak kosong apa adanya (dipakai untuk log)."""
        self.pastikan_ada(nama)
        try:
            with open(self.jalur(nama), "r", encoding="utf-8") as f:
                return [b.rstrip("\n") for b in f if b.strip()]
        except (OSError, UnicodeDecodeError) as e:
            raise PenyimpananError(f"Gagal membaca {nama}: {e}") from e

    def tulis_banyak(self, berkas):
        """Tulis beberapa file sekaligus. berkas = daftar (nama, header, baris_kolom).

        Semua dituliskan dulu ke file sementara. File asli baru diganti setelah semuanya
        berhasil ditulis, jadi kegagalan di tengah jalan tidak meninggalkan file setengah jadi.
        """
        sementara = []
        try:
            os.makedirs(self.folder, exist_ok=True)
            for nama, header, baris in berkas:
                jalur = self.jalur(nama)
                tmp = jalur + ".tmp"
                sementara.append((tmp, jalur))
                with open(tmp, "w", encoding="utf-8", newline="\n") as f:
                    if header:
                        f.write(f"# {header}\n")
                    for kolom in baris:
                        f.write(self.PEMISAH.join(str(k) for k in kolom) + "\n")
            for tmp, jalur in sementara:
                os.replace(tmp, jalur)
        except OSError as e:
            for tmp, _ in sementara:
                try:
                    os.remove(tmp)
                except OSError:
                    pass
            raise PenyimpananError(f"Gagal menulis file data: {e}") from e

    def tulis(self, nama, header, baris):
        self.tulis_banyak([(nama, header, baris)])

    def tulis_teks(self, nama, isi):
        """Tulis teks bebas (dipakai laporan)."""
        try:
            os.makedirs(self.folder, exist_ok=True)
            with open(self.jalur(nama), "w", encoding="utf-8", newline="\n") as f:
                f.write(isi if isi.endswith("\n") else isi + "\n")
        except OSError as e:
            raise PenyimpananError(f"Gagal menulis {nama}: {e}") from e

    def tambah(self, nama, baris):
        """Tambahkan satu baris di akhir file (mode append)."""
        try:
            os.makedirs(self.folder, exist_ok=True)
            with open(self.jalur(nama), "a", encoding="utf-8", newline="\n") as f:
                f.write(baris + "\n")
        except OSError as e:
            raise PenyimpananError(f"Gagal menambah baris ke {nama}: {e}") from e

    def salin(self, nama, folder_tujuan):
        """Salin satu file ke folder lain lewat open() + with. False bila sumber tidak ada."""
        sumber = self.jalur(nama)
        if not os.path.exists(sumber):
            return False
        try:
            os.makedirs(folder_tujuan, exist_ok=True)
            with open(sumber, "r", encoding="utf-8") as f:
                isi = f.read()
            with open(os.path.join(folder_tujuan, nama), "w", encoding="utf-8", newline="\n") as f:
                f.write(isi)
        except (OSError, UnicodeDecodeError) as e:
            raise PenyimpananError(f"Gagal menyalin {nama}: {e}") from e
        return True
