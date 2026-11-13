#dikerjakan oleh
#Nama : Sulthan Hafizh Putra Agung
#NIM : K3525013
#Kelas : B / Semester 3
#Angkatan : 2025

from enum import Enum

class _EnumTeks(str, Enum):
    """Dasar untuk enum yang nilainya bisa dibaca/ditulis sebagai teks biasa."""

    @property
    def teks(self):
        return self.value.lower().replace("_", " ")

    @classmethod
    def dari_teks(cls, teks):
        kunci = str(teks).strip().upper().replace(" ", "_")
        try:
            return cls(kunci)
        except ValueError:
            pilihan = ", ".join(m.teks for m in cls)
            raise ValueError(f"Nilai '{teks}' tidak dikenal. Pilihan: {pilihan}.") from None


class StatusTransaksi(_EnumTeks):
    DIPINJAM = "DIPINJAM"
    SEBAGIAN_DIKEMBALIKAN = "SEBAGIAN_DIKEMBALIKAN"
    SELESAI = "SELESAI"


class KondisiAlat(_EnumTeks):
    BAIK = "BAIK"
    RUSAK_RINGAN = "RUSAK_RINGAN"
    RUSAK_BERAT = "RUSAK_BERAT"



