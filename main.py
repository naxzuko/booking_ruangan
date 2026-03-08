"""
Module: main
Entry point aplikasi Sistem Booking Ruangan/Lapangan.
Menyediakan antarmuka CLI (Command Line Interface) untuk pengguna.

Author: Sistem Booking Team
Version: 1.0.0
"""

import os
import sys
from datetime import datetime
from typing import Optional

# Import dari package models dan services (2 namespace/package)
from models import Pengguna, Admin, Member, Booking, StatusBooking
from models import Ruangan, RuanganRapat, RuanganOlahraga
from services import DatabaseService, BookingService


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def clear_screen():
    """Bersihkan layar terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(judul: str, lebar: int = 60):
    """
    Cetak header dengan format kotak.

    Args:
        judul (str): Judul yang ditampilkan
        lebar (int): Lebar kotak
    """
    print("=" * lebar)
    print(f"{'SISTEM BOOKING RUANGAN & LAPANGAN':^{lebar}}")
    print(f"{judul:^{lebar}}")
    print("=" * lebar)


def input_int(prompt: str, min_val: int = None, max_val: int = None) -> int:
    """
    Input integer dengan validasi range.

    Args:
        prompt (str): Teks prompt
        min_val (int): Nilai minimum
        max_val (int): Nilai maksimum

    Returns:
        int: Nilai yang diinput
    """
    while True:
        try:
            nilai = int(input(prompt))
            if min_val is not None and nilai < min_val:
                print(f"  ⚠ Nilai minimal {min_val}")
                continue
            if max_val is not None and nilai > max_val:
                print(f"  ⚠ Nilai maksimal {max_val}")
                continue
            return nilai
        except ValueError:
            print("  ⚠ Masukkan angka yang valid")


def format_rupiah(nilai: float) -> str:
    """Format angka menjadi format rupiah."""
    return f"Rp{nilai:,.0f}"


def cetak_tabel_ruangan(ruangan_list: list):
    """Cetak daftar ruangan dalam format tabel."""
    print(f"\n{'ID':<5} {'Nama':<25} {'Jenis':<20} {'Kapasitas':<12} {'Harga/Jam':<15} {'Status'}")
    print("-" * 85)
    for r in ruangan_list:
        status = "✓ Tersedia" if r["tersedia"] else "✗ Penuh"
        print(f"{r['id']:<5} {r['nama']:<25} {r['jenis']:<20} "
              f"{r['kapasitas']:<12} {format_rupiah(r['harga_per_jam']):<15} {status}")
    print()


def cetak_tabel_booking(booking_list: list, tampilkan_pengguna: bool = False):
    """Cetak daftar booking dalam format tabel."""
    print()
    for b in booking_list:
        info_pengguna = f" | {b.get('nama_pengguna','')}" if tampilkan_pengguna else ""
        print(f"  #{b['id']} | {b.get('nama_ruangan','Ruangan '+str(b['ruangan_id']))} | "
              f"{b['tanggal']} | {b['jam_mulai']:02d}:00-{b['jam_selesai']:02d}:00 | "
              f"{format_rupiah(b['total_harga'])} | [{b['status']}]{info_pengguna}")
    print()


# ============================================================
# MENU FUNCTIONS
# ============================================================

class Aplikasi:
    """
    Kelas utama aplikasi yang mengelola alur program.
    Menggunakan pola Session untuk menyimpan state login.
    """

    def __init__(self):
        """Inisialisasi aplikasi dan koneksi database."""
        self.db = DatabaseService()
        self.booking_svc = BookingService(self.db)
        self.pengguna_login: Optional[dict] = None  # session data

    def jalankan(self):
        """Entry point utama - jalankan aplikasi."""
        while True:
            if not self.pengguna_login:
                self.__menu_utama()
            else:
                role = self.pengguna_login.get("role", "Member")
                if role in ["Admin", "Super Admin"]:
                    self.__menu_admin()
                else:
                    self.__menu_member()

    # ---- Menu Utama (Belum Login) ----

    def __menu_utama(self):
        """Menu sebelum login."""
        clear_screen()
        print_header("SELAMAT DATANG")
        print("\n  1. Login")
        print("  2. Daftar Akun Baru")
        print("  3. Lihat Daftar Ruangan (Tanpa Login)")
        print("  0. Keluar\n")

        pilihan = input("  Pilih menu: ").strip()

        if pilihan == "1":
            self.__proses_login()
        elif pilihan == "2":
            self.__proses_daftar()
        elif pilihan == "3":
            self.__tampilkan_ruangan_publik()
        elif pilihan == "0":
            print("\n  Terima kasih! Sampai jumpa.\n")
            self.db.close()
            sys.exit(0)
        else:
            print("  ⚠ Pilihan tidak valid")
            input("  Tekan Enter untuk melanjutkan...")

    def __proses_login(self):
        """Proses autentikasi pengguna."""
        clear_screen()
        print_header("LOGIN")
        print()
        email = input("  Email    : ").strip()
        password = input("  Password : ").strip()

        data = self.db.cari_pengguna_by_email(email)
        if not data:
            print("\n  ✗ Email tidak terdaftar")
            input("  Tekan Enter...")
            return

        # Verifikasi password (menggunakan method dari model)
        import hashlib
        pw_hash = hashlib.sha256(password.encode()).hexdigest()
        if data["password_hash"] != pw_hash:
            print("\n  ✗ Password salah")
            input("  Tekan Enter...")
            return

        if not data["aktif"]:
            print("\n  ✗ Akun tidak aktif")
            input("  Tekan Enter...")
            return

        self.pengguna_login = data
        print(f"\n  ✓ Login berhasil! Selamat datang, {data['nama']}")
        input("  Tekan Enter...")

    def __proses_daftar(self):
        """Proses pendaftaran member baru."""
        clear_screen()
        print_header("DAFTAR AKUN BARU")
        print()
        nama = input("  Nama Lengkap : ").strip()
        email = input("  Email        : ").strip()
        password = input("  Password     : ").strip()
        no_telp = input("  No. Telepon  : ").strip()

        if not all([nama, email, password, no_telp]):
            print("\n  ✗ Semua field harus diisi")
            input("  Tekan Enter...")
            return

        if self.db.cari_pengguna_by_email(email):
            print("\n  ✗ Email sudah terdaftar")
            input("  Tekan Enter...")
            return

        import hashlib
        from datetime import datetime
        new_id = self.db.get_next_pengguna_id()
        data = {
            "id": new_id,
            "nama": nama,
            "email": email,
            "password_hash": hashlib.sha256(password.encode()).hexdigest(),
            "no_telepon": no_telp,
            "role": "Member",
            "aktif": True,
            "poin": 0,
            "level_admin": 0,
            "riwayat_booking": [],
            "created_at": datetime.now().isoformat()
        }

        if self.db.simpan_pengguna(data):
            print(f"\n  ✓ Akun berhasil dibuat! Silakan login.")
        else:
            print("\n  ✗ Gagal membuat akun")
        input("  Tekan Enter...")

    def __tampilkan_ruangan_publik(self):
        """Tampilkan daftar ruangan tanpa login."""
        clear_screen()
        print_header("DAFTAR RUANGAN & LAPANGAN")
        ruangan_list = self.db.get_semua_ruangan()
        cetak_tabel_ruangan(ruangan_list)
        input("  Tekan Enter untuk kembali...")

    # ---- Menu Member ----

    def __menu_member(self):
        """Menu utama untuk member."""
        clear_screen()
        nama = self.pengguna_login["nama"]
        poin = self.pengguna_login.get("poin", 0)
        print_header(f"MEMBER: {nama} | Poin: {poin}")
        print("\n  1. Lihat Daftar Ruangan")
        print("  2. Booking Ruangan")
        print("  3. Riwayat Booking Saya")
        print("  4. Batalkan Booking")
        print("  5. Cek Jadwal Ruangan")
        print("  6. Profil Saya")
        print("  0. Logout\n")

        pilihan = input("  Pilih menu: ").strip()

        if pilihan == "1":
            self.__lihat_ruangan()
        elif pilihan == "2":
            self.__booking_ruangan()
        elif pilihan == "3":
            self.__riwayat_booking()
        elif pilihan == "4":
            self.__batalkan_booking_member()
        elif pilihan == "5":
            self.__cek_jadwal()
        elif pilihan == "6":
            self.__profil()
        elif pilihan == "0":
            self.pengguna_login = None
            print("\n  ✓ Logout berhasil")
        else:
            print("  ⚠ Pilihan tidak valid")
            input("  Tekan Enter...")

    def __lihat_ruangan(self):
        """Tampilkan daftar ruangan."""
        clear_screen()
        print_header("DAFTAR RUANGAN & LAPANGAN")
        ruangan_list = self.db.get_semua_ruangan()

        # Filter berdasarkan jenis (menggunakan array dan loop)
        jenis_list = list(set(r["jenis"].split()[0] for r in ruangan_list))
        print("  Filter: 1=Semua  2=Rapat  3=Olahraga")
        filter_pilih = input("  Pilih filter (Enter=Semua): ").strip()

        if filter_pilih == "2":
            ruangan_list = [r for r in ruangan_list if "Rapat" in r["jenis"]]
        elif filter_pilih == "3":
            ruangan_list = [r for r in ruangan_list if "Lapangan" in r["jenis"]]

        cetak_tabel_ruangan(ruangan_list)

        # Detail fasilitas
        lihat_detail = input("  Lihat detail fasilitas? (y/n): ").strip().lower()
        if lihat_detail == "y":
            ruangan_id = input_int("  Masukkan ID Ruangan: ", 1)
            ruangan = self.db.get_ruangan_by_id(ruangan_id)
            if ruangan:
                print(f"\n  Fasilitas {ruangan['nama']}:")
                for f in ruangan["fasilitas"]:
                    print(f"    • {f}")
            else:
                print("  ⚠ Ruangan tidak ditemukan")

        input("\n  Tekan Enter untuk kembali...")

    def __booking_ruangan(self):
        """Proses booking ruangan oleh member."""
        clear_screen()
        print_header("BOOKING RUANGAN")

        # Tampilkan ruangan tersedia
        ruangan_list = [r for r in self.db.get_semua_ruangan() if r["tersedia"]]
        if not ruangan_list:
            print("\n  ✗ Tidak ada ruangan tersedia saat ini")
            input("  Tekan Enter...")
            return

        cetak_tabel_ruangan(ruangan_list)

        ruangan_id = input_int("  Pilih ID Ruangan: ", 1)
        ruangan = self.db.get_ruangan_by_id(ruangan_id)
        if not ruangan or not ruangan["tersedia"]:
            print("  ✗ Ruangan tidak valid atau tidak tersedia")
            input("  Tekan Enter...")
            return

        # Input tanggal
        print(f"\n  Booking: {ruangan['nama']}")
        tanggal = input("  Tanggal (YYYY-MM-DD): ").strip()

        # Tampilkan slot tersedia
        slots = self.booking_svc.get_slot_tersedia(ruangan_id, tanggal)
        if slots:
            print(f"\n  Slot tersedia di {tanggal}:")
            for i, s in enumerate(slots, 1):
                print(f"    {i}. {s}")
        else:
            print(f"\n  ✗ Tidak ada slot tersedia di {tanggal}")
            input("  Tekan Enter...")
            return

        print(f"\n  Jam operasional: 06:00 - 22:00")
        jam_mulai = input_int("  Jam Mulai (6-21): ", 6, 21)
        jam_selesai = input_int("  Jam Selesai (7-22): ", 7, 22)

        # Preview harga
        from services.booking_service import BookingService
        durasi = jam_selesai - jam_mulai
        if durasi <= 0:
            print("  ✗ Jam tidak valid")
            input("  Tekan Enter...")
            return

        # Estimasi harga
        harga_base = ruangan["harga_per_jam"] * durasi
        if "Rapat" in ruangan["jenis"]:
            total = harga_base * 1.10
            print(f"\n  Estimasi harga: {format_rupiah(harga_base)} + 10% admin = {format_rupiah(total)}")
        elif ruangan.get("outdoor"):
            total = harga_base * 0.85
            print(f"\n  Estimasi harga: {format_rupiah(harga_base)} - 15% diskon = {format_rupiah(total)}")
        else:
            total = harga_base
            print(f"\n  Estimasi harga: {format_rupiah(total)}")

        keterangan = input("  Keterangan (opsional): ").strip()
        konfirmasi = input("\n  Konfirmasi booking? (y/n): ").strip().lower()

        if konfirmasi != "y":
            print("  Booking dibatalkan")
            input("  Tekan Enter...")
            return

        sukses, pesan = self.booking_svc.buat_booking(
            self.pengguna_login["id"], ruangan_id,
            tanggal, jam_mulai, jam_selesai, keterangan
        )

        if sukses:
            print(f"\n  ✓ {pesan}")
            # Update poin di session
            self.pengguna_login["poin"] = self.pengguna_login.get("poin", 0) + BookingService.POIN_PER_BOOKING
        else:
            print(f"\n  ✗ {pesan}")
        input("  Tekan Enter...")

    def __riwayat_booking(self):
        """Tampilkan riwayat booking pengguna."""
        clear_screen()
        print_header("RIWAYAT BOOKING SAYA")
        bookings = self.db.get_booking_by_pengguna(self.pengguna_login["id"])
        if not bookings:
            print("\n  Belum ada riwayat booking")
        else:
            cetak_tabel_booking(bookings)
        input("  Tekan Enter untuk kembali...")

    def __batalkan_booking_member(self):
        """Batalkan booking oleh member."""
        clear_screen()
        print_header("BATALKAN BOOKING")
        bookings = self.db.get_booking_by_pengguna(self.pengguna_login["id"])
        aktif = [b for b in bookings if b["status"] in ["Pending", "Dikonfirmasi"]]

        if not aktif:
            print("\n  Tidak ada booking aktif yang bisa dibatalkan")
            input("  Tekan Enter...")
            return

        cetak_tabel_booking(aktif)
        booking_id = input_int("  Masukkan ID Booking yang dibatalkan: ", 1)
        sukses, pesan = self.booking_svc.batalkan_booking(
            booking_id, self.pengguna_login["id"]
        )
        print(f"\n  {'✓' if sukses else '✗'} {pesan}")
        input("  Tekan Enter...")

    def __cek_jadwal(self):
        """Cek jadwal ruangan di tanggal tertentu."""
        clear_screen()
        print_header("CEK JADWAL RUANGAN")
        cetak_tabel_ruangan(self.db.get_semua_ruangan())
        ruangan_id = input_int("  Pilih ID Ruangan: ", 1)
        tanggal = input("  Tanggal (YYYY-MM-DD): ").strip()

        ruangan = self.db.get_ruangan_by_id(ruangan_id)
        if not ruangan:
            print("  ✗ Ruangan tidak ditemukan")
            input("  Tekan Enter...")
            return

        jadwal = self.booking_svc.get_jadwal_ruangan(ruangan_id, tanggal)
        slots = self.booking_svc.get_slot_tersedia(ruangan_id, tanggal)

        print(f"\n  Jadwal {ruangan['nama']} - {tanggal}:")
        print(f"\n  Sudah Dipesan ({len(jadwal)}):")
        if jadwal:
            for j in jadwal:
                print(f"    🔴 {j['jam_mulai']:02d}:00 - {j['jam_selesai']:02d}:00 [{j['status']}]")
        else:
            print("    (Belum ada booking)")

        print(f"\n  Slot Tersedia ({len(slots)}):")
        if slots:
            for s in slots:
                print(f"    🟢 {s}")
        else:
            print("    (Tidak ada slot tersedia)")

        input("\n  Tekan Enter untuk kembali...")

    def __profil(self):
        """Tampilkan profil pengguna."""
        clear_screen()
        print_header("PROFIL SAYA")
        p = self.pengguna_login
        print(f"\n  Nama      : {p['nama']}")
        print(f"  Email     : {p['email']}")
        print(f"  Telepon   : {p.get('no_telepon', '-')}")
        print(f"  Role      : {p.get('role', 'Member')}")
        print(f"  Poin      : {p.get('poin', 0)}")
        total_booking = len(self.db.get_booking_by_pengguna(p["id"]))
        print(f"  Total Booking : {total_booking}")
        input("\n  Tekan Enter untuk kembali...")

    # ---- Menu Admin ----

    def __menu_admin(self):
        """Menu untuk administrator."""
        clear_screen()
        nama = self.pengguna_login["nama"]
        role = self.pengguna_login.get("role")
        print_header(f"{role}: {nama}")
        print("\n  1. Lihat Semua Booking")
        print("  2. Kelola Ruangan (Ubah Ketersediaan)")
        print("  3. Lihat Semua Pengguna")
        print("  4. Laporan Pendapatan")
        print("  5. Konfirmasi / Batalkan Booking")
        print("  0. Logout\n")

        pilihan = input("  Pilih menu: ").strip()

        if pilihan == "1":
            self.__admin_lihat_booking()
        elif pilihan == "2":
            self.__admin_kelola_ruangan()
        elif pilihan == "3":
            self.__admin_lihat_pengguna()
        elif pilihan == "4":
            self.__admin_laporan()
        elif pilihan == "5":
            self.__admin_update_booking()
        elif pilihan == "0":
            self.pengguna_login = None

    def __admin_lihat_booking(self):
        """Admin: lihat semua booking."""
        clear_screen()
        print_header("SEMUA BOOKING")
        bookings = self.db.get_semua_booking()
        if not bookings:
            print("\n  Belum ada booking")
        else:
            cetak_tabel_booking(bookings, tampilkan_pengguna=True)
        input("  Tekan Enter untuk kembali...")

    def __admin_kelola_ruangan(self):
        """Admin: ubah ketersediaan ruangan."""
        clear_screen()
        print_header("KELOLA RUANGAN")
        ruangan_list = self.db.get_semua_ruangan()
        cetak_tabel_ruangan(ruangan_list)

        ruangan_id = input_int("  Pilih ID Ruangan: ", 1)
        ruangan = self.db.get_ruangan_by_id(ruangan_id)
        if not ruangan:
            print("  ✗ Ruangan tidak ditemukan")
            input("  Tekan Enter...")
            return

        status_skrg = "Tersedia" if ruangan["tersedia"] else "Tidak Tersedia"
        print(f"\n  Status sekarang: {status_skrg}")
        toggle = input("  Ubah status? (y/n): ").strip().lower()
        if toggle == "y":
            baru = not ruangan["tersedia"]
            self.db.update_ketersediaan_ruangan(ruangan_id, baru)
            print(f"  ✓ Status diubah menjadi {'Tersedia' if baru else 'Tidak Tersedia'}")
        input("  Tekan Enter...")

    def __admin_lihat_pengguna(self):
        """Admin: lihat daftar pengguna."""
        clear_screen()
        print_header("DAFTAR PENGGUNA")
        pengguna_list = self.db.get_semua_pengguna()
        print(f"\n{'ID':<5} {'Nama':<25} {'Email':<30} {'Role':<15} {'Status'}")
        print("-" * 85)
        for p in pengguna_list:
            status = "Aktif" if p["aktif"] else "Nonaktif"
            print(f"{p['id']:<5} {p['nama']:<25} {p['email']:<30} {p['role']:<15} {status}")
        print(f"\nTotal: {len(pengguna_list)} pengguna")
        input("\n  Tekan Enter untuk kembali...")

    def __admin_laporan(self):
        """Admin: laporan pendapatan."""
        clear_screen()
        print_header("LAPORAN PENDAPATAN")
        bookings = self.db.get_semua_booking()

        # Hitung total menggunakan loop dan array
        total_semua: float = 0
        total_per_ruangan: dict = {}
        jumlah_per_status: dict = {}

        for b in bookings:
            status = b["status"]
            jumlah_per_status[status] = jumlah_per_status.get(status, 0) + 1

            if status not in ["Dibatalkan"]:
                total_semua += b["total_harga"]
                nama_r = b.get("nama_ruangan", "Unknown")
                if nama_r not in total_per_ruangan:
                    total_per_ruangan[nama_r] = 0
                total_per_ruangan[nama_r] += b["total_harga"]

        print(f"\n  Total Booking   : {len(bookings)}")
        for status, jumlah in jumlah_per_status.items():
            print(f"    - {status:<15}: {jumlah}")

        print(f"\n  Total Pendapatan: {format_rupiah(total_semua)}")
        print(f"\n  Per Ruangan:")
        for nama, total in total_per_ruangan.items():
            print(f"    {nama:<30} : {format_rupiah(total)}")

        input("\n  Tekan Enter untuk kembali...")

    def __admin_update_booking(self):
        """Admin: update status booking."""
        clear_screen()
        print_header("UPDATE STATUS BOOKING")
        bookings = self.db.get_semua_booking()
        aktif = [b for b in bookings if b["status"] not in ["Selesai", "Dibatalkan"]]
        cetak_tabel_booking(aktif, tampilkan_pengguna=True)

        if not aktif:
            print("  Tidak ada booking aktif")
            input("  Tekan Enter...")
            return

        booking_id = input_int("  ID Booking: ", 1)
        print("  Status: 1=Dikonfirmasi  2=Selesai  3=Dibatalkan")
        pilihan = input_int("  Pilih status: ", 1, 3)
        status_map = {1: "Dikonfirmasi", 2: "Selesai", 3: "Dibatalkan"}
        status_baru = status_map[pilihan]

        ok = self.db.update_status_booking(booking_id, status_baru)
        print(f"  {'✓ Status diperbarui' if ok else '✗ Gagal update'}")
        input("  Tekan Enter...")


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    """
    Program utama - Sistem Booking Ruangan & Lapangan
    Jalankan: python main.py
    """
    print("\n  Memuat sistem...")
    app = Aplikasi()
    try:
        app.jalankan()
    except KeyboardInterrupt:
        print("\n\n  Program dihentikan.")
        app.db.close()
        sys.exit(0)
