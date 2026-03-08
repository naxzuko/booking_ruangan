"""
Module: ruangan
Model untuk ruangan/lapangan yang dapat dibooking.
Menerapkan inheritance dan polymorphism.
"""

from .base import BaseEntity
from datetime import datetime
from typing import List


class Ruangan(BaseEntity):
    """
    Kelas dasar untuk semua jenis ruangan.
    Menerapkan encapsulation dengan private/protected attributes.
    """

    # Class variable (array fasilitas standar)
    FASILITAS_STANDAR: List[str] = ["Listrik", "Ventilasi", "Pencahayaan"]

    def __init__(self, id: int, nama: str, kapasitas: int,
                 harga_per_jam: float, fasilitas: List[str] = None):
        """
        Inisialisasi ruangan.

        Args:
            id (int): ID unik ruangan
            nama (str): Nama ruangan
            kapasitas (int): Kapasitas maksimal pengguna
            harga_per_jam (float): Harga sewa per jam dalam rupiah
            fasilitas (List[str]): Daftar fasilitas tersedia
        """
        super().__init__(id)
        self._nama: str = nama                          # protected
        self.__kapasitas: int = kapasitas               # private
        self.__harga_per_jam: float = harga_per_jam     # private
        self._fasilitas: List[str] = fasilitas or self.FASILITAS_STANDAR.copy()
        self.__tersedia: bool = True                    # private

    # --- Properties ---
    @property
    def nama(self) -> str:
        """Getter nama ruangan."""
        return self._nama

    @nama.setter
    def nama(self, value: str):
        """Setter nama dengan validasi."""
        if not value or not isinstance(value, str):
            raise ValueError("Nama ruangan tidak boleh kosong")
        self._nama = value.strip()

    @property
    def kapasitas(self) -> int:
        return self.__kapasitas

    @property
    def harga_per_jam(self) -> float:
        return self.__harga_per_jam

    @harga_per_jam.setter
    def harga_per_jam(self, value: float):
        if value < 0:
            raise ValueError("Harga tidak boleh negatif")
        self.__harga_per_jam = value

    @property
    def tersedia(self) -> bool:
        return self.__tersedia

    @tersedia.setter
    def tersedia(self, value: bool):
        self.__tersedia = value

    @property
    def fasilitas(self) -> List[str]:
        return self._fasilitas.copy()

    # --- Methods ---
    def hitung_total_harga(self, durasi_jam: int) -> float:
        """
        Hitung total harga booking.

        Args:
            durasi_jam (int): Durasi booking dalam jam

        Returns:
            float: Total harga
        """
        return self.__harga_per_jam * durasi_jam

    def tambah_fasilitas(self, fasilitas: str):
        """Tambahkan fasilitas baru ke ruangan."""
        if fasilitas not in self._fasilitas:
            self._fasilitas.append(fasilitas)

    def get_jenis(self) -> str:
        """Polimorfisme - dikembalikan oleh subclass."""
        return "Ruangan Umum"

    def to_dict(self) -> dict:
        """Konversi ke dictionary untuk penyimpanan."""
        return {
            "id": self.id,
            "nama": self._nama,
            "jenis": self.get_jenis(),
            "kapasitas": self.__kapasitas,
            "harga_per_jam": self.__harga_per_jam,
            "fasilitas": self._fasilitas,
            "tersedia": self.__tersedia,
            "created_at": self.created_at.isoformat()
        }

    def __str__(self) -> str:
        status = "✓ Tersedia" if self.__tersedia else "✗ Tidak Tersedia"
        return (f"[{self.id}] {self._nama} | {self.get_jenis()} | "
                f"Kapasitas: {self.__kapasitas} | "
                f"Rp{self.__harga_per_jam:,.0f}/jam | {status}")


class RuanganRapat(Ruangan):
    """
    Ruangan untuk keperluan rapat/meeting.
    Mewarisi dari Ruangan (inheritance).
    """

    FASILITAS_RAPAT: List[str] = ["Proyektor", "Whiteboard", "Sound System", "AC"]

    def __init__(self, id: int, nama: str, kapasitas: int,
                 harga_per_jam: float, ada_proyektor: bool = True):
        """
        Inisialisasi ruangan rapat.

        Args:
            ada_proyektor (bool): Apakah tersedia proyektor
        """
        fasilitas = Ruangan.FASILITAS_STANDAR + self.FASILITAS_RAPAT
        super().__init__(id, nama, kapasitas, harga_per_jam, fasilitas)
        self.__ada_proyektor: bool = ada_proyektor

    @property
    def ada_proyektor(self) -> bool:
        return self.__ada_proyektor

    def get_jenis(self) -> str:
        """Override - polymorphism."""
        return "Ruangan Rapat"

    def hitung_total_harga(self, durasi_jam: int) -> float:
        """
        Override hitung harga - ruangan rapat ada tambahan biaya admin 10%.
        Overloading/override dari parent.
        """
        base = super().hitung_total_harga(durasi_jam)
        return base * 1.10  # +10% biaya admin

    def to_dict(self) -> dict:
        data = super().to_dict()
        data["ada_proyektor"] = self.__ada_proyektor
        return data

    def __str__(self) -> str:
        proyektor = "📽 Ada Proyektor" if self.__ada_proyektor else "Tanpa Proyektor"
        return super().__str__() + f" | {proyektor}"


class RuanganOlahraga(Ruangan):
    """
    Lapangan/ruangan untuk olahraga.
    Mewarisi dari Ruangan (inheritance).
    """

    JENIS_OLAHRAGA: List[str] = ["Badminton", "Futsal", "Basketball",
                                   "Tenis Meja", "Voli", "Lainnya"]

    def __init__(self, id: int, nama: str, kapasitas: int,
                 harga_per_jam: float, jenis_olahraga: str, outdoor: bool = False):
        """
        Inisialisasi ruangan/lapangan olahraga.

        Args:
            jenis_olahraga (str): Jenis olahraga (Badminton, Futsal, dll)
            outdoor (bool): Apakah lapangan outdoor
        """
        fasilitas = Ruangan.FASILITAS_STANDAR + ["Ruang Ganti", "Toilet"]
        if not outdoor:
            fasilitas.append("AC")
        super().__init__(id, nama, kapasitas, harga_per_jam, fasilitas)
        self.__jenis_olahraga: str = jenis_olahraga
        self.__outdoor: bool = outdoor

    @property
    def jenis_olahraga(self) -> str:
        return self.__jenis_olahraga

    @property
    def outdoor(self) -> bool:
        return self.__outdoor

    def get_jenis(self) -> str:
        """Override - polymorphism."""
        return f"Lapangan {self.__jenis_olahraga}"

    def hitung_total_harga(self, durasi_jam: int) -> float:
        """
        Override hitung harga - outdoor lebih murah 15%.
        Overloading/override dari parent.
        """
        base = super().hitung_total_harga(durasi_jam)
        if self.__outdoor:
            return base * 0.85  # diskon 15% untuk outdoor
        return base

    def to_dict(self) -> dict:
        data = super().to_dict()
        data["jenis_olahraga"] = self.__jenis_olahraga
        data["outdoor"] = self.__outdoor
        return data

    def __str__(self) -> str:
        tipe = "🌿 Outdoor" if self.__outdoor else "🏠 Indoor"
        return super().__str__() + f" | {tipe}"
