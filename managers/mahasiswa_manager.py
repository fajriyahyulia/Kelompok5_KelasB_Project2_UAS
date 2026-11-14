#dikerjakan oleh
#Nama : Muzni Mubarok Salim
#NIM : K3525036
#Kelas : B / Semester 3
#Angkatan : 2025

from managers.dasar import ManagerDasar


class MahasiswaManager(ManagerDasar):
    def __init__(self):
        super().__init__()
        self.data = {}

    def kosongkan(self):
        self.data.clear()

    def tambah(self, mahasiswa, simpan=True):
        if mahasiswa.nim in self.data:
            raise ValueError("NIM sudah terdaftar.")
        self.data[mahasiswa.nim] = mahasiswa
        if simpan:
            self._simpan("simpan_mahasiswa", lambda: self.data.pop(mahasiswa.nim, None))
            self._catat(f"Mahasiswa {mahasiswa.nim} ditambahkan")
        return mahasiswa

    def edit(self, nim, nama=None, no_hp=None):
        mhs = self.get(nim)
        lama = (mhs.nama, mhs.no_hp)
        mhs.ubah(nama, no_hp)

        def batalkan():
            mhs.nama, mhs.no_hp = lama

        self._simpan("simpan_mahasiswa", batalkan)
        self._catat(f"Data mahasiswa {mhs.nim} diperbarui")
        return mhs

    def hapus(self, nim, transaksi_list, jaga_riwayat=True):
        """Aturan 6: tidak boleh dihapus selama ada transaksi aktif.

        Dengan jaga_riwayat=True, mahasiswa yang pernah bertransaksi juga tidak boleh
        dihapus, supaya NIM di transaksi.txt selalu menunjuk data yang ada (Aturan 8).
        """
        mhs = self.get(nim)
        if not mhs.boleh_dihapus(transaksi_list):
            raise ValueError("Mahasiswa masih memiliki transaksi aktif.")
        if jaga_riwayat and mhs.punya_riwayat(transaksi_list):
            raise ValueError("Mahasiswa tercatat dalam riwayat transaksi dan tidak dapat dihapus "
                             "agar data antarfile tetap konsisten.")
        del self.data[mhs.nim]
        self._simpan("simpan_mahasiswa", lambda: self.data.__setitem__(mhs.nim, mhs))
        self._catat(f"Mahasiswa {mhs.nim} dihapus")
        return True

    def cari(self, keyword):
        keyword = keyword.strip().lower()
        if not keyword:
            raise ValueError("Kata kunci tidak boleh kosong.")
        return [m for m in self.data.values()
                if keyword in m.nim.lower() or keyword in m.nama.lower()]

    def get(self, nim):
        kunci = nim.strip().upper()
        if kunci not in self.data:
            raise ValueError("Mahasiswa tidak ditemukan.")
        return self.data[kunci]

    def semua(self):
        return list(self.data.values())
