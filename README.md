# Sistem Booking Ruangan & Lapangan

## Cara Menjalankan

**Syarat:** Node.js LTS → https://nodejs.org

```
npm install
npx electron .
```

## Akun Default

| Role        | Email               | Password |
|-------------|---------------------|----------|
| Super Admin | admin@booking.com   | admin123 |
| Member      | budi@email.com      | budi123  |
| Member      | siti@email.com      | siti123  |

## Struktur Folder

```
booking_system/
├── main.js              ← Electron main process + database
├── preload.js           ← Bridge IPC
├── package.json
├── renderer/            ← Tampilan (HTML/CSS/JS)
│   ├── index.html
│   ├── style.css
│   └── app.js
├── models/              ← Package 1 (Python OOP)
│   ├── __init__.py
│   ├── base.py
│   ├── ruangan.py
│   ├── pengguna.py
│   └── booking.py
└── services/            ← Package 2 (Python Logic)
    ├── __init__.py
    ├── database.py
    └── booking_service.py
```
