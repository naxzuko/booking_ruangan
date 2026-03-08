"""
Module: database
Layanan koneksi dan operasi database SQLite.
Menggunakan library eksternal: sqlite3.
"""

import sqlite3
import json
import os
from typing import List, Optional, Dict, Any


class DatabaseService:
    """
    Layanan database menggunakan SQLite (external library).
    Mengelola koneksi dan CRUD operations.
    """

    DB_FILE: str = "booking_system.db"

    def __init__(self, db_path: str = None):
        """
        Inisialisasi koneksi database.

        Args:
            db_path (str): Path file database, default DB_FILE
        """
        self.__db_path: str = db_path or self.DB_FILE
        self.__connection: Optional[sqlite3.Connection] = None
        self.__inisialisasi_database()

    def __inisialisasi_database(self):
        """Buat tabel-tabel yang diperlukan jika belum ada."""
        conn = self.__get_connection()
        cursor = conn.cursor()

        # Tabel pengguna
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pengguna (
                id INTEGER PRIMARY KEY,
                nama TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                no_telepon TEXT,
                role TEXT DEFAULT 'Member',
                aktif INTEGER DEFAULT 1,
                poin INTEGER DEFAULT 0,
                level_admin INTEGER DEFAULT 0,
                riwayat_booking TEXT DEFAULT '[]',
                created_at TEXT
            )
        """)

        # Tabel ruangan
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ruangan (
                id INTEGER PRIMARY KEY,
                nama TEXT NOT NULL,
                jenis TEXT NOT NULL,
                kapasitas INTEGER,
                harga_per_jam REAL,
                fasilitas TEXT DEFAULT '[]',
                tersedia INTEGER DEFAULT 1,
                jenis_olahraga TEXT,
                outdoor INTEGER DEFAULT 0,
                ada_proyektor INTEGER DEFAULT 0,
                created_at TEXT
            )
        """)

        # Tabel booking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS booking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pengguna_id INTEGER,
                ruangan_id INTEGER,
                tanggal TEXT,
                jam_mulai INTEGER,
                jam_selesai INTEGER,
                total_harga REAL,
                status TEXT DEFAULT 'Pending',
                keterangan TEXT DEFAULT '',
                created_at TEXT,
                FOREIGN KEY (pengguna_id) REFERENCES pengguna(id),
                FOREIGN KEY (ruangan_id) REFERENCES ruangan(id)
            )
        """)

        conn.commit()
        self.__seed_data_awal(cursor, conn)

    def __seed_data_awal(self, cursor, conn):
        """Isi data awal jika database kosong."""
        # Cek apakah sudah ada data
        cursor.execute("SELECT COUNT(*) FROM pengguna")
        if cursor.fetchone()[0] > 0:
            return

        import hashlib
        from datetime import datetime
        now = datetime.now().isoformat()

        def hash_pw(pw):
            return hashlib.sha256(pw.encode()).hexdigest()

        # Seed admin
        cursor.execute("""
            INSERT INTO pengguna (id, nama, email, password_hash, no_telepon,
                role, aktif, level_admin, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (1, "Administrator", "admin@booking.com", hash_pw("admin123"),
              "081234567890", "Super Admin", 1, 2, now))

        # Seed member
        cursor.execute("""
            INSERT INTO pengguna (id, nama, email, password_hash, no_telepon,
                role, aktif, poin, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (2, "Budi Santoso", "budi@email.com", hash_pw("budi123"),
              "082345678901", "Member", 1, 50, now))

        # Seed ruangan rapat
        fasilitas_rapat = json.dumps(["Listrik", "Ventilasi", "Pencahayaan",
                                       "Proyektor", "Whiteboard", "Sound System", "AC"])
        cursor.execute("""
            INSERT INTO ruangan (id, nama, jenis, kapasitas, harga_per_jam,
                fasilitas, tersedia, ada_proyektor, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (1, "Ruang Rapat A", "Ruangan Rapat", 20, 150000,
              fasilitas_rapat, 1, 1, now))

        cursor.execute("""
            INSERT INTO ruangan (id, nama, jenis, kapasitas, harga_per_jam,
                fasilitas, tersedia, ada_proyektor, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (2, "Ruang Rapat B", "Ruangan Rapat", 10, 100000,
              fasilitas_rapat, 1, 0, now))

        # Seed lapangan olahraga
        fasilitas_sport = json.dumps(["Listrik", "Ventilasi", "Pencahayaan",
                                       "Ruang Ganti", "Toilet", "AC"])
        cursor.execute("""
            INSERT INTO ruangan (id, nama, jenis, kapasitas, harga_per_jam,
                fasilitas, tersedia, jenis_olahraga, outdoor, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (3, "Lapangan Badminton 1", "Lapangan Badminton", 4, 75000,
              fasilitas_sport, 1, "Badminton", 0, now))

        cursor.execute("""
            INSERT INTO ruangan (id, nama, jenis, kapasitas, harga_per_jam,
                fasilitas, tersedia, jenis_olahraga, outdoor, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (4, "Lapangan Futsal", "Lapangan Futsal", 14, 200000,
              json.dumps(["Listrik", "Ventilasi", "Pencahayaan", "Ruang Ganti", "Toilet"]),
              1, "Futsal", 0, now))

        cursor.execute("""
            INSERT INTO ruangan (id, nama, jenis, kapasitas, harga_per_jam,
                fasilitas, tersedia, jenis_olahraga, outdoor, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (5, "Lapangan Basket Outdoor", "Lapangan Basketball", 10, 80000,
              json.dumps(["Pencahayaan", "Ruang Ganti", "Toilet"]),
              1, "Basketball", 1, now))

        conn.commit()

    def __get_connection(self) -> sqlite3.Connection:
        """Dapatkan koneksi database (lazy connection)."""
        if not self.__connection:
            self.__connection = sqlite3.connect(self.__db_path)
            self.__connection.row_factory = sqlite3.Row
        return self.__connection

    def close(self):
        """Tutup koneksi database."""
        if self.__connection:
            self.__connection.close()
            self.__connection = None

    # --- CRUD Pengguna ---
    def simpan_pengguna(self, data: dict) -> bool:
        """Simpan data pengguna baru ke database."""
        try:
            conn = self.__get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO pengguna
                (id, nama, email, password_hash, no_telepon, role,
                 aktif, poin, level_admin, riwayat_booking, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data.get("id"), data["nama"], data["email"],
                data["password_hash"], data.get("no_telepon"),
                data.get("role", "Member"), int(data.get("aktif", True)),
                data.get("poin", 0), data.get("level_admin", 0),
                json.dumps(data.get("riwayat_booking", [])),
                data.get("created_at")
            ))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error simpan pengguna: {e}")
            return False

    def cari_pengguna_by_email(self, email: str) -> Optional[Dict]:
        """Cari pengguna berdasarkan email."""
        conn = self.__get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pengguna WHERE email = ?", (email,))
        row = cursor.fetchone()
        if row:
            data = dict(row)
            data["riwayat_booking"] = json.loads(data.get("riwayat_booking", "[]"))
            return data
        return None

    def get_semua_pengguna(self) -> List[Dict]:
        """Ambil semua data pengguna."""
        conn = self.__get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pengguna ORDER BY id")
        rows = cursor.fetchall()
        result = []
        for row in rows:
            data = dict(row)
            data["riwayat_booking"] = json.loads(data.get("riwayat_booking", "[]"))
            result.append(data)
        return result

    def update_poin_member(self, pengguna_id: int, poin_baru: int) -> bool:
        """Update poin member."""
        try:
            conn = self.__get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE pengguna SET poin = ? WHERE id = ?",
                           (poin_baru, pengguna_id))
            conn.commit()
            return True
        except Exception:
            return False

    # --- CRUD Ruangan ---
    def get_semua_ruangan(self) -> List[Dict]:
        """Ambil semua data ruangan."""
        conn = self.__get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ruangan ORDER BY id")
        rows = cursor.fetchall()
        result = []
        for row in rows:
            data = dict(row)
            data["fasilitas"] = json.loads(data.get("fasilitas", "[]"))
            result.append(data)
        return result

    def get_ruangan_by_id(self, ruangan_id: int) -> Optional[Dict]:
        """Ambil data ruangan berdasarkan ID."""
        conn = self.__get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ruangan WHERE id = ?", (ruangan_id,))
        row = cursor.fetchone()
        if row:
            data = dict(row)
            data["fasilitas"] = json.loads(data.get("fasilitas", "[]"))
            return data
        return None

    def update_ketersediaan_ruangan(self, ruangan_id: int, tersedia: bool) -> bool:
        """Update status ketersediaan ruangan."""
        try:
            conn = self.__get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE ruangan SET tersedia = ? WHERE id = ?",
                           (int(tersedia), ruangan_id))
            conn.commit()
            return True
        except Exception:
            return False

    # --- CRUD Booking ---
    def simpan_booking(self, data: dict) -> int:
        """
        Simpan booking baru. Returns ID booking yang dibuat.
        """
        try:
            from datetime import datetime
            conn = self.__get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO booking
                (pengguna_id, ruangan_id, tanggal, jam_mulai, jam_selesai,
                 total_harga, status, keterangan, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data["pengguna_id"], data["ruangan_id"], data["tanggal"],
                data["jam_mulai"], data["jam_selesai"], data["total_harga"],
                data.get("status", "Pending"), data.get("keterangan", ""),
                datetime.now().isoformat()
            ))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error simpan booking: {e}")
            return -1

    def get_booking_by_pengguna(self, pengguna_id: int) -> List[Dict]:
        """Ambil semua booking milik pengguna tertentu."""
        conn = self.__get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT b.*, r.nama as nama_ruangan
            FROM booking b
            JOIN ruangan r ON b.ruangan_id = r.id
            WHERE b.pengguna_id = ?
            ORDER BY b.tanggal DESC, b.jam_mulai
        """, (pengguna_id,))
        return [dict(row) for row in cursor.fetchall()]

    def get_semua_booking(self) -> List[Dict]:
        """Ambil semua booking (untuk admin)."""
        conn = self.__get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT b.*, r.nama as nama_ruangan, p.nama as nama_pengguna
            FROM booking b
            JOIN ruangan r ON b.ruangan_id = r.id
            JOIN pengguna p ON b.pengguna_id = p.id
            ORDER BY b.tanggal DESC, b.jam_mulai
        """)
        return [dict(row) for row in cursor.fetchall()]

    def update_status_booking(self, booking_id: int, status: str) -> bool:
        """Update status booking."""
        try:
            conn = self.__get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE booking SET status = ? WHERE id = ?",
                           (status, booking_id))
            conn.commit()
            return True
        except Exception:
            return False

    def cek_konflik_booking(self, ruangan_id: int, tanggal: str,
                             jam_mulai: int, jam_selesai: int,
                             exclude_id: int = None) -> bool:
        """
        Cek apakah ada konflik jadwal booking.

        Returns:
            bool: True jika ada konflik
        """
        conn = self.__get_connection()
        cursor = conn.cursor()
        query = """
            SELECT COUNT(*) FROM booking
            WHERE ruangan_id = ? AND tanggal = ?
            AND status NOT IN ('Dibatalkan')
            AND NOT (jam_selesai <= ? OR jam_mulai >= ?)
        """
        params = [ruangan_id, tanggal, jam_mulai, jam_selesai]
        if exclude_id:
            query += " AND id != ?"
            params.append(exclude_id)
        cursor.execute(query, params)
        return cursor.fetchone()[0] > 0

    def get_next_pengguna_id(self) -> int:
        """Dapatkan ID pengguna berikutnya."""
        conn = self.__get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(id) FROM pengguna")
        result = cursor.fetchone()[0]
        return (result or 0) + 1
