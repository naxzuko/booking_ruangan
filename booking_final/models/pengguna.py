"""
Module: pengguna
Model pengguna sistem booking.
Menerapkan inheritance, encapsulation, dan interface (ABC).
"""

from .base import BaseEntity
from abc import abstractmethod
from typing import List
import hashlib


class IAuthentication:
    """
    Interface untuk autentikasi pengguna.
    Python menerapkan interface melalui ABC/mixin.
    """

    def verify_password(self, password: str) -> bool:
        raise NotImplementedError("Subclass harus mengimplementasikan verify_password")

    def hash_password(self, password: str) -> str:
        """Hash password menggunakan SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()


class Pengguna(BaseEntity, IAuthentication):
    """
    Kelas dasar untuk semua jenis pengguna.
    Menerapkan multiple inheritance (BaseEntity + IAuthentication).
    """

    def __init__(self, id: int, nama: str, email: str,
                 password: str, no_telepon: str):
        """
        Inisialisasi pengguna.

        Args:
            id (int): ID unik pengguna
            nama (str): Nama lengkap
            email (str): Email pengguna
            password (str): Password (akan di-hash)
            no_telepon (str): Nomor telepon
        """
        BaseEntity.__init__(self, id)
        self._nama: str = nama
        self.__email: str = email
        self.__password_hash: str = self.hash_password(password)
        self.__no_telepon: str = no_telepon
        self._aktif: bool = True
        self._riwayat_booking: List[int] = []  # array ID booking

    # --- Properties ---
    @property
    def nama(self) -> str:
        return self._nama

    @property
    def email(self) -> str:
        return self.__email

    @property
    def no_telepon(self) -> str:
        return self.__no_telepon

    @property
    def aktif(self) -> bool:
        return self._aktif

    @property
    def riwayat_booking(self) -> List[int]:
        return self._riwayat_booking.copy()

    # --- Methods ---
    def verify_password(self, password: str) -> bool:
        """Verifikasi password. Implementasi dari IAuthentication."""
        return self.__password_hash == self.hash_password(password)

    def tambah_riwayat(self, booking_id: int):
        """Tambah ID booking ke riwayat."""
        self._riwayat_booking.append(booking_id)

    def get_role(self) -> str:
        """Polimorfisme - dioverride oleh subclass."""
        return "Pengguna"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nama": self._nama,
            "email": self.__email,
            "password_hash": self.__password_hash,
            "no_telepon": self.__no_telepon,
            "role": self.get_role(),
            "aktif": self._aktif,
            "riwayat_booking": self._riwayat_booking,
            "created_at": self.created_at.isoformat()
        }

    def __str__(self) -> str:
        status = "Aktif" if self._aktif else "Nonaktif"
        return f"[{self.id}] {self._nama} | {self.__email} | {self.get_role()} | {status}"


class Member(Pengguna):
    """
    Pengguna biasa/member. Mewarisi dari Pengguna.
    """

    def __init__(self, id: int, nama: str, email: str,
                 password: str, no_telepon: str, poin: int = 0):
        """
        Inisialisasi member.

        Args:
            poin (int): Poin reward member
        """
        super().__init__(id, nama, email, password, no_telepon)
        self.__poin: int = poin

    @property
    def poin(self) -> int:
        return self.__poin

    def tambah_poin(self, jumlah: int):
        """Tambah poin setelah booking berhasil."""
        self.__poin += jumlah

    def get_role(self) -> str:
        """Override - polymorphism."""
        return "Member"

    def to_dict(self) -> dict:
        data = super().to_dict()
        data["poin"] = self.__poin
        return data

    def __str__(self) -> str:
        return super().__str__() + f" | Poin: {self.__poin}"


class Admin(Pengguna):
    """
    Administrator sistem. Mewarisi dari Pengguna.
    Memiliki hak akses lebih tinggi.
    """

    def __init__(self, id: int, nama: str, email: str,
                 password: str, no_telepon: str, level_admin: int = 1):
        """
        Inisialisasi admin.

        Args:
            level_admin (int): Level admin (1=operator, 2=superadmin)
        """
        super().__init__(id, nama, email, password, no_telepon)
        self.__level_admin: int = level_admin

    @property
    def level_admin(self) -> int:
        return self.__level_admin

    def is_superadmin(self) -> bool:
        return self.__level_admin >= 2

    def get_role(self) -> str:
        """Override - polymorphism."""
        return "Admin" if self.__level_admin == 1 else "Super Admin"

    def to_dict(self) -> dict:
        data = super().to_dict()
        data["level_admin"] = self.__level_admin
        return data
