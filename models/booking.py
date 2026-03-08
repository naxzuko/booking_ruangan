"""
Module: booking
Model untuk transaksi booking ruangan.
"""

from .base import BaseEntity
from datetime import datetime
from enum import Enum


class StatusBooking(Enum):
    """Enum status booking - menerapkan tipe data yang sesuai."""
    PENDING = "Pending"
    DIKONFIRMASI = "Dikonfirmasi"
    DIBATALKAN = "Dibatalkan"
    SELESAI = "Selesai"


class Booking(BaseEntity):
    """
    Model transaksi booking ruangan/lapangan.
    """

    def __init__(self, id: int, pengguna_id: int, ruangan_id: str,
                 tanggal: str, jam_mulai: int, jam_selesai: int,
                 total_harga: float, keterangan: str = ""):
        """
        Inisialisasi booking.

        Args:
            id (int): ID booking
            pengguna_id (int): ID pengguna yang booking
            ruangan_id (str): ID ruangan yang dibooking
            tanggal (str): Tanggal booking (YYYY-MM-DD)
            jam_mulai (int): Jam mulai (0-23)
            jam_selesai (int): Jam selesai (0-23)
            total_harga (float): Total biaya
            keterangan (str): Keterangan tambahan
        """
        super().__init__(id)
        self.__pengguna_id: int = pengguna_id
        self.__ruangan_id: str = ruangan_id
        self.__tanggal: str = tanggal
        self.__jam_mulai: int = jam_mulai
        self.__jam_selesai: int = jam_selesai
        self.__total_harga: float = total_harga
        self.__keterangan: str = keterangan
        self.__status: StatusBooking = StatusBooking.PENDING

    # --- Properties ---
    @property
    def pengguna_id(self) -> int:
        return self.__pengguna_id

    @property
    def ruangan_id(self) -> str:
        return self.__ruangan_id

    @property
    def tanggal(self) -> str:
        return self.__tanggal

    @property
    def jam_mulai(self) -> int:
        return self.__jam_mulai

    @property
    def jam_selesai(self) -> int:
        return self.__jam_selesai

    @property
    def durasi_jam(self) -> int:
        return self.__jam_selesai - self.__jam_mulai

    @property
    def total_harga(self) -> float:
        return self.__total_harga

    @property
    def status(self) -> StatusBooking:
        return self.__status

    @status.setter
    def status(self, value: StatusBooking):
        """Setter dengan validasi transisi status."""
        if not isinstance(value, StatusBooking):
            raise ValueError("Status tidak valid")
        self.__status = value

    @property
    def keterangan(self) -> str:
        return self.__keterangan

    # --- Methods ---
    def konfirmasi(self):
        """Konfirmasi booking."""
        if self.__status == StatusBooking.PENDING:
            self.__status = StatusBooking.DIKONFIRMASI

    def batalkan(self):
        """Batalkan booking."""
        if self.__status in [StatusBooking.PENDING, StatusBooking.DIKONFIRMASI]:
            self.__status = StatusBooking.DIBATALKAN

    def selesaikan(self):
        """Tandai booking sebagai selesai."""
        if self.__status == StatusBooking.DIKONFIRMASI:
            self.__status = StatusBooking.SELESAI

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "pengguna_id": self.__pengguna_id,
            "ruangan_id": self.__ruangan_id,
            "tanggal": self.__tanggal,
            "jam_mulai": self.__jam_mulai,
            "jam_selesai": self.__jam_selesai,
            "durasi_jam": self.durasi_jam,
            "total_harga": self.__total_harga,
            "status": self.__status.value,
            "keterangan": self.__keterangan,
            "created_at": self.created_at.isoformat()
        }

    def __str__(self) -> str:
        return (f"Booking #{self.id} | Ruangan ID: {self.__ruangan_id} | "
                f"{self.__tanggal} | {self.__jam_mulai:02d}:00-{self.__jam_selesai:02d}:00 | "
                f"Rp{self.__total_harga:,.0f} | {self.__status.value}")
