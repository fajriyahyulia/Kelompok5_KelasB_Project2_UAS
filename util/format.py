#dikerjakan oleh
#Nama : Fajriyah Yulia Az Zahra
#NIM : K3525005
#Kelas : B / Semester 3
#Angkatan : 2025

HEADER_MAHASISWA = ("NIM", "Nama", "No. HP", "Status peminjaman")
HEADER_ALAT = ("Kode", "Nama", "Kategori", "Kondisi", "Status")
HEADER_DIPINJAM = ("Kode", "Nama", "Kategori", "Peminjam", "Transaksi", "Batas kembali")


def buat_tabel(header, baris):
    lebar = [len(str(h)) for h in header]
    for b in baris:
        for i, sel in enumerate(b):
            lebar[i] = max(lebar[i], len(str(sel)))
    pemisah = "+" + "+".join("-" * (w + 2) for w in lebar) + "+"

    def rapikan(b):
        return "| " + " | ".join(str(s).ljust(w) for s, w in zip(b, lebar)) + " |"

    keluar = [pemisah, rapikan(header), pemisah]
    keluar.extend(rapikan(b) for b in baris)
    keluar.extend([pemisah, f"Total: {len(baris)} data"])
    return "\n".join(keluar)


def baris_mahasiswa(daftar, transaksi_list):
    return [(m.nim, m.nama, m.no_hp, m.status_aktif(transaksi_list)) for m in daftar]


def baris_alat(daftar):
    return [(a.kode, a.nama, a.kategori, a.kondisi.teks, a.status_teks().capitalize())
            for a in daftar]


def baris_dipinjam(rincian):
    return [(a.kode, a.nama, a.kategori, f"{t.mahasiswa.nim} - {t.mahasiswa.nama}",
             t.id_transaksi, str(t.batas_kembali)) for a, t in rincian]


def teks_transaksi(trx, acuan=None):
    baris = [
        f"ID Transaksi   : {trx.id_transaksi}",
        f"Peminjam       : {trx.mahasiswa.nim} - {trx.mahasiswa.nama}",
        f"Tanggal pinjam : {trx.tanggal_pinjam}",
        f"Batas kembali  : {trx.batas_kembali}",
        f"Status         : {trx.status.value}",
        "Alat           :",
    ]
    for i, item in enumerate(trx.daftar_item, start=1):
        if item.sudah_kembali:
            ket = f"Kembali {item.tanggal_kembali}, kondisi {item.kondisi_kembali.teks}"
        else:
            ket = "Masih dipinjam"
        telat = item.hari_terlambat(trx.batas_kembali, acuan)
        if telat:
            ket += f", terlambat {telat} hari"
        baris.append(f"  {i}. {item.alat.kode} - {item.alat.nama}  [{ket}]")
    return "\n".join(baris)