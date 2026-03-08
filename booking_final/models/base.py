"""
Module: base
Kelas dasar (abstract) untuk semua entitas dalam sistem.
"""

from abc import ABC, abstractmethod
from datetime import datetime


class BaseEntity(ABC):
    """
    Kelas dasar abstrak untuk semua entitas.
    Menerapkan konsep abstraction dan template pattern.
    """

    def __init__(self, id: int, created_at: datetime = None):
        """
        Inisialisasi entitas dasar.

        Args:
            id (int): ID unik entitas
            created_at (datetime): Waktu pembuatan, default sekarang
        """
        self.__id: int = id  # private attribute (hak akses)
        self.__created_at: datetime = created_at or datetime.now()

    @property
    def id(self) -> int:
        """Getter untuk ID (property)."""
        return self.__id

    @property
    def created_at(self) -> datetime:
        """Getter untuk waktu pembuatan (property)."""
        return self.__created_at

    @abstractmethod
    def to_dict(self) -> dict:
        """
        Konversi entitas ke dictionary.
        Wajib diimplementasikan oleh subclass (abstract method).
        """
        pass

    @abstractmethod
    def __str__(self) -> str:
        """Representasi string dari entitas."""
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.__id})"
