"""
Module: booking_service
Logika bisnis untuk proses booking ruangan.
"""

from .database import DatabaseService
from typing import List, Optional, Dict, Tuple
from datetime import datetime


class BookingService:
    """
    Service layer untuk operasi booking.
    Memisahkan logika bisnis dari UI.
    """

    POIN_PER_BOOKING: int = 10  # poin yang didapat per booking

    def __init__(self, db: DatabaseService):
        """
        Inisialisasi service dengan dependency injection.

        Args:
            db (DatabaseService): Instance database service
        """
        self.__db: DatabaseService = db

    def buat_booking(self, pengguna_id: int, ruangan_id: int,
                     tanggal: str, jam_mulai: int, jam_selesai: int,
                     keterangan: str = "") -> Tuple[bool, str]:
        """
        Proses pembuatan booking baru.

        Args:
            pengguna_id: ID pengguna
            ruangan_id: ID ruangan
            tanggal: Tanggal booking (YYYY-MM-DD)
            jam_mulai: Jam mulai (0-23)
            jam_selesai: Jam selesai (0-23)
            keterangan: Catatan tambahan

        Returns:
            Tuple[bool, str]: (sukses, pesan)
        """
        # Validasi waktu
        if jam_mulai >= jam_selesai:
            return False, "Jam selesai harus lebih besar dari jam mulai"
        if jam_mulai < 6 or jam_selesai > 22:
            return False, "Jam operasional: 06:00 - 22:00"

        # Validasi tanggal
        try:
            tgl = datetime.strptime(tanggal, "%Y-%m-%d")
            if tgl.date() < datetime.now().date():
                return False, "Tidak bisa booking tanggal yang sudah lewat"
        except ValueError:
            return False, "Format tanggal tidak valid (gunakan YYYY-MM-DD)"

        # Cek ketersediaan ruangan
        ruangan = self.__db.get_ruangan_by_id(ruangan_id)
        if not ruangan:
            return False, "Ruangan tidak ditemukan"
        if not ruangan["tersedia"]:
            return False, "Ruangan sedang tidak tersedia"

        # Cek konflik jadwal
        if self.__db.cek_konflik_booking(ruangan_id, tanggal, jam_mulai, jam_selesai):
            return False, "Jadwal bentrok dengan booking lain"

        # Hitung total harga
        durasi = jam_selesai - jam_mulai
        harga_per_jam = ruangan["harga_per_jam"]

        # Terapkan diskon/surcharge berdasarkan jenis ruangan
        total_harga = self.__hitung_harga(ruangan, durasi)

        # Simpan booking
        data = {
            "pengguna_id": pengguna_id,
            "ruangan_id": ruangan_id,
            "tanggal": tanggal,
            "jam_mulai": jam_mulai,
            "jam_selesai": jam_selesai,
            "total_harga": total_harga,
            "keterangan": keterangan,
            "status": "Dikonfirmasi"
        }
        booking_id = self.__db.simpan_booking(data)

        if booking_id > 0:
            # Tambah poin ke member
            pengguna_data = self.__get_pengguna_by_id(pengguna_id)
            if pengguna_data and pengguna_data.get("role") == "Member":
                poin_baru = pengguna_data.get("poin", 0) + self.POIN_PER_BOOKING
                self.__db.update_poin_member(pengguna_id, poin_baru)

            return True, (f"Booking berhasil! ID: #{booking_id} | "
                         f"Total: Rp{total_harga:,.0f}")
        return False, "Gagal menyimpan booking"

    def __hitung_harga(self, ruangan: dict, durasi_jam: int) -> float:
        """
        Hitung harga berdasarkan jenis ruangan.

        Args:
            ruangan: Data ruangan dari database
            durasi_jam: Durasi dalam jam

        Returns:
            float: Total harga
        """
        base = ruangan["harga_per_jam"] * durasi_jam
        jenis = ruangan.get("jenis", "")

        if "Rapat" in jenis:
            return base * 1.10  # surcharge 10%
        elif ruangan.get("outdoor"):
            return base * 0.85  # diskon 15% outdoor
        return base

    def __get_pengguna_by_id(self, pengguna_id: int) -> Optional[dict]:
        """Cari pengguna berdasarkan ID."""
        semua = self.__db.get_semua_pengguna()
        for p in semua:
            if p["id"] == pengguna_id:
                return p
        return None

    def batalkan_booking(self, booking_id: int, pengguna_id: int,
                         is_admin: bool = False) -> Tuple[bool, str]:
        """
        Batalkan booking.

        Args:
            booking_id: ID booking yang dibatalkan
            pengguna_id: ID pengguna yang membatalkan
            is_admin: True jika yang membatalkan adalah admin

        Returns:
            Tuple[bool, str]: (sukses, pesan)
        """
        semua = self.__db.get_semua_booking()
        booking = next((b for b in semua if b["id"] == booking_id), None)

        if not booking:
            return False, "Booking tidak ditemukan"
        if not is_admin and booking["pengguna_id"] != pengguna_id:
            return False, "Tidak berhak membatalkan booking ini"
        if booking["status"] == "Dibatalkan":
            return False, "Booking sudah dibatalkan"
        if booking["status"] == "Selesai":
            return False, "Booking sudah selesai, tidak bisa dibatalkan"

        ok = self.__db.update_status_booking(booking_id, "Dibatalkan")
        return (True, "Booking berhasil dibatalkan") if ok else (False, "Gagal membatalkan")

    def get_jadwal_ruangan(self, ruangan_id: int, tanggal: str) -> List[Dict]:
        """
        Dapatkan jadwal booking suatu ruangan di tanggal tertentu.

        Returns:
            List jadwal yang sudah dipesan
        """
        semua = self.__db.get_semua_booking()
        return [b for b in semua
                if b["ruangan_id"] == ruangan_id
                and b["tanggal"] == tanggal
                and b["status"] != "Dibatalkan"]

    def get_slot_tersedia(self, ruangan_id: int, tanggal: str) -> List[str]:
        """
        Dapatkan slot waktu yang masih tersedia.

        Returns:
            List string slot waktu tersedia
        """
        jadwal = self.get_jadwal_ruangan(ruangan_id, tanggal)
        jam_terpakai = set()

        for b in jadwal:
            for jam in range(b["jam_mulai"], b["jam_selesai"]):
                jam_terpakai.add(jam)

        slots: List[str] = []
        for jam in range(6, 22):
            if jam not in jam_terpakai:
                slots.append(f"{jam:02d}:00 - {jam+1:02d}:00")

        return slots
