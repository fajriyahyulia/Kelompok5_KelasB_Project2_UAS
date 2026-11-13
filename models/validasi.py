#dikerjakan oleh
#Nama : Fajriyah Yulia Az Zahra
#NIM : K3525005
#Kelas : B / Semester 3
#Angkatan : 2025

def teks_wajib(nilai, label):
    """Teks tidak boleh kosong dan tidak boleh memuat pemisah file (|) atau baris baru,
    karena itu akan merusak format text file."""
    teks = str(nilai).strip()
    if not teks:
        raise ValueError(f"{label} tidak boleh kosong.")
    if "|" in teks or "\n" in teks or "\r" in teks:
        raise ValueError(f"{label} tidak boleh mengandung karakter '|' atau baris baru.")
    return teks


def kode_wajib(nilai, label):
    teks = teks_wajib(nilai, label).upper()
    if not (teks.isascii() and teks.isalnum()):
        raise ValueError(f"{label} hanya boleh berisi huruf dan angka tanpa spasi.")
    return teks


def no_hp_valid(nilai):
    teks = teks_wajib(nilai, "No. HP")
    angka = teks[1:] if teks.startswith("+") else teks
    if not (angka.isascii() and angka.isdigit() and 8 <= len(angka) <= 15):
        raise ValueError("No. HP harus 8 sampai 15 digit angka (boleh diawali +).")
    return teks