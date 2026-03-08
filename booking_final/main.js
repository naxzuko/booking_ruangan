const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const fs   = require('fs');
const crypto = require('crypto');

let mainWindow;

// ── Database (JSON file, pure JS) ──────────────────────────────
const DB_FILE = path.join(app.getPath('userData'), 'data.json');

function hashPw(pw) { return crypto.createHash('sha256').update(pw).digest('hex'); }
function nowStr()   { return new Date().toLocaleString('id-ID'); }

function addDays(d, n) { const x = new Date(d); x.setDate(x.getDate()+n); return x; }
function fmt(d) { return d.toISOString().split('T')[0]; }

function loadDB() {
  try {
    if (fs.existsSync(DB_FILE)) return JSON.parse(fs.readFileSync(DB_FILE, 'utf8'));
  } catch(e) {}
  return null;
}

function saveDB(data) { fs.writeFileSync(DB_FILE, JSON.stringify(data, null, 2)); }

function initDB() {
  let data = loadDB();
  if (data) return data;
  const today = new Date();
  data = {
    pengguna: [
      { id:1, nama:'Administrator',  email:'admin@booking.com', password_hash:hashPw('admin123'), no_telepon:'081234567890', role:'Super Admin', aktif:1, poin:0,   level_admin:2, created_at:nowStr() },
      { id:2, nama:'Budi Santoso',   email:'budi@email.com',    password_hash:hashPw('budi123'),  no_telepon:'082345678901', role:'Member',     aktif:1, poin:120, level_admin:0, created_at:nowStr() },
      { id:3, nama:'Siti Rahma',     email:'siti@email.com',    password_hash:hashPw('siti123'),  no_telepon:'083456789012', role:'Member',     aktif:1, poin:45,  level_admin:0, created_at:nowStr() },
    ],
    ruangan: [
      { id:1, nama:'Ruang Rapat A',           jenis:'Ruangan Rapat',    kapasitas:20, harga_per_jam:150000, fasilitas:['Proyektor','Whiteboard','AC','Sound System'], tersedia:1, jenis_olahraga:null,       outdoor:0, ada_proyektor:1 },
      { id:2, nama:'Ruang Rapat B',           jenis:'Ruangan Rapat',    kapasitas:10, harga_per_jam:100000, fasilitas:['Whiteboard','AC'],                           tersedia:1, jenis_olahraga:null,       outdoor:0, ada_proyektor:0 },
      { id:3, nama:'Lapangan Badminton 1',    jenis:'Lapangan Olahraga',kapasitas:4,  harga_per_jam:75000,  fasilitas:['AC','Ruang Ganti','Toilet'],                 tersedia:1, jenis_olahraga:'Badminton', outdoor:0, ada_proyektor:0 },
      { id:4, nama:'Lapangan Futsal',         jenis:'Lapangan Olahraga',kapasitas:14, harga_per_jam:200000, fasilitas:['Ruang Ganti','Toilet','Tribun'],             tersedia:1, jenis_olahraga:'Futsal',    outdoor:0, ada_proyektor:0 },
      { id:5, nama:'Lapangan Basket Outdoor', jenis:'Lapangan Olahraga',kapasitas:10, harga_per_jam:80000,  fasilitas:['Pencahayaan','Toilet'],                      tersedia:1, jenis_olahraga:'Basketball',outdoor:1, ada_proyektor:0 },
    ],
    booking: [
      { id:1, pengguna_id:2, ruangan_id:1, tanggal:fmt(today),             jam_mulai:9,  jam_selesai:11, total_harga:330000, status:'Dikonfirmasi', keterangan:'Rapat bulanan',   created_at:nowStr() },
      { id:2, pengguna_id:3, ruangan_id:3, tanggal:fmt(today),             jam_mulai:13, jam_selesai:15, total_harga:150000, status:'Dikonfirmasi', keterangan:'Latihan rutin',   created_at:nowStr() },
      { id:3, pengguna_id:2, ruangan_id:4, tanggal:fmt(addDays(today,1)),  jam_mulai:15, jam_selesai:17, total_harga:400000, status:'Dikonfirmasi', keterangan:'Turnamen futsal', created_at:nowStr() },
      { id:4, pengguna_id:3, ruangan_id:1, tanggal:fmt(addDays(today,2)),  jam_mulai:10, jam_selesai:12, total_harga:330000, status:'Pending',      keterangan:'Workshop tim',    created_at:nowStr() },
      { id:5, pengguna_id:2, ruangan_id:3, tanggal:fmt(addDays(today,-1)), jam_mulai:8,  jam_selesai:10, total_harga:150000, status:'Selesai',      keterangan:'Latihan pagi',    created_at:nowStr() },
      { id:6, pengguna_id:3, ruangan_id:2, tanggal:fmt(addDays(today,-2)), jam_mulai:14, jam_selesai:16, total_harga:220000, status:'Selesai',      keterangan:'Briefing',        created_at:nowStr() },
      { id:7, pengguna_id:2, ruangan_id:5, tanggal:fmt(addDays(today,3)),  jam_mulai:7,  jam_selesai:9,  total_harga:136000, status:'Dikonfirmasi', keterangan:'Basket pagi',     created_at:nowStr() },
    ],
    _nextId: 8
  };
  saveDB(data);
  return data;
}

// ── Window ─────────────────────────────────────────────────────
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280, height: 800,
    minWidth: 1024, minHeight: 680,
    frame: false,
    backgroundColor: '#0d0d0f',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    }
  });
  mainWindow.loadFile(path.join(__dirname, 'renderer', 'index.html'));
}

app.whenReady().then(() => {
  initDB();
  setupIPC();
  createWindow();
});
app.on('window-all-closed', () => { if (process.platform !== 'darwin') app.quit(); });

// ── IPC ────────────────────────────────────────────────────────
function setupIPC() {
  ipcMain.on('window-minimize', () => mainWindow.minimize());
  ipcMain.on('window-maximize', () => mainWindow.isMaximized() ? mainWindow.unmaximize() : mainWindow.maximize());
  ipcMain.on('window-close',    () => mainWindow.close());

  ipcMain.handle('auth:login',    (_, email, pass) => {
    const db   = loadDB();
    const user = db.pengguna.find(p => p.email === email);
    if (!user)                                   return { ok:false, msg:'Email tidak terdaftar' };
    if (user.password_hash !== hashPw(pass))     return { ok:false, msg:'Password salah' };
    if (!user.aktif)                             return { ok:false, msg:'Akun tidak aktif' };
    const { password_hash, ...safe } = user;
    return { ok:true, user: safe };
  });

  ipcMain.handle('auth:register', (_, d) => {
    const db = loadDB();
    if (db.pengguna.find(p => p.email === d.email)) return { ok:false, msg:'Email sudah terdaftar' };
    const id = Math.max(...db.pengguna.map(p => p.id)) + 1;
    db.pengguna.push({ id, nama:d.nama, email:d.email, password_hash:hashPw(d.password),
      no_telepon:d.no_telepon, role:'Member', aktif:1, poin:0, level_admin:0, created_at:nowStr() });
    saveDB(db);
    return { ok:true };
  });

  ipcMain.handle('dashboard:stats', () => {
    const db = loadDB();
    const todayStr = new Date().toISOString().split('T')[0];
    return {
      totalBooking:   db.booking.filter(b => b.status !== 'Dibatalkan').length,
      pendapatan:     db.booking.filter(b => ['Dikonfirmasi','Selesai'].includes(b.status)).reduce((s,b)=>s+b.total_harga,0),
      bookingHariIni: db.booking.filter(b => b.tanggal === todayStr && b.status !== 'Dibatalkan').length,
      totalRuangan:   db.ruangan.length,
      ruanganAktif:   db.ruangan.filter(r => r.tersedia).length,
    };
  });

  ipcMain.handle('dashboard:recent', () => {
    const db = loadDB();
    return [...db.booking].sort((a,b)=>b.id-a.id).slice(0,8).map(b=>({
      ...b,
      nama_ruangan:  db.ruangan.find(r=>r.id===b.ruangan_id)?.nama||'-',
      nama_pengguna: db.pengguna.find(p=>p.id===b.pengguna_id)?.nama||'-',
    }));
  });

  ipcMain.handle('dashboard:calendar', (_, year, month) => {
    const db     = loadDB();
    const prefix = `${year}-${String(month).padStart(2,'0')}`;
    const map    = {};
    db.booking.filter(b=>b.tanggal.startsWith(prefix)&&b.status!=='Dibatalkan')
      .forEach(b=>{ if(!map[b.tanggal]) map[b.tanggal]={count:0,total:0}; map[b.tanggal].count++; map[b.tanggal].total+=b.total_harga; });
    return map;
  });

  ipcMain.handle('ruangan:list',   () => loadDB().ruangan);
  ipcMain.handle('ruangan:toggle', (_, id) => {
    const db = loadDB();
    const r  = db.ruangan.find(r=>r.id===id);
    if (!r) return { ok:false };
    r.tersedia = r.tersedia ? 0 : 1;
    saveDB(db);
    return { ok:true, tersedia:!!r.tersedia };
  });

  ipcMain.handle('booking:list', (_, pid, isAdmin) => {
    const db   = loadDB();
    const list = isAdmin ? db.booking : db.booking.filter(b=>b.pengguna_id===pid);
    return [...list].sort((a,b)=>b.id-a.id).map(b=>({
      ...b,
      nama_ruangan:  db.ruangan.find(r=>r.id===b.ruangan_id)?.nama||'-',
      nama_pengguna: db.pengguna.find(p=>p.id===b.pengguna_id)?.nama||'-',
    }));
  });

  ipcMain.handle('booking:create', (_, d) => {
    if (d.jam_mulai >= d.jam_selesai)           return { ok:false, msg:'Jam tidak valid' };
    if (d.jam_mulai < 6 || d.jam_selesai > 22) return { ok:false, msg:'Jam operasional 06:00–22:00' };
    const db = loadDB();
    const konflik = db.booking.some(b =>
      b.ruangan_id===d.ruangan_id && b.tanggal===d.tanggal && b.status!=='Dibatalkan' &&
      !(b.jam_selesai<=d.jam_mulai || b.jam_mulai>=d.jam_selesai));
    if (konflik) return { ok:false, msg:'Jadwal bentrok dengan booking lain' };
    const ruangan = db.ruangan.find(r=>r.id===d.ruangan_id);
    if (!ruangan) return { ok:false, msg:'Ruangan tidak ditemukan' };
    const durasi = d.jam_selesai - d.jam_mulai;
    let total = ruangan.harga_per_jam * durasi;
    if (ruangan.jenis==='Ruangan Rapat') total *= 1.10;
    else if (ruangan.outdoor)            total *= 0.85;
    total = Math.round(total);
    const newBk = { id:db._nextId++, pengguna_id:d.pengguna_id, ruangan_id:d.ruangan_id,
      tanggal:d.tanggal, jam_mulai:d.jam_mulai, jam_selesai:d.jam_selesai,
      total_harga:total, status:'Dikonfirmasi', keterangan:d.keterangan||'', created_at:nowStr() };
    db.booking.push(newBk);
    const user = db.pengguna.find(p=>p.id===d.pengguna_id);
    if (user && user.role==='Member') user.poin += 10;
    saveDB(db);
    return { ok:true, msg:`Booking berhasil! Total: Rp${total.toLocaleString('id-ID')}`, id:newBk.id, total };
  });

  ipcMain.handle('booking:cancel', (_, id, pid, isAdmin) => {
    const db = loadDB();
    const b  = db.booking.find(b=>b.id===id);
    if (!b)                                    return { ok:false, msg:'Booking tidak ditemukan' };
    if (!isAdmin && b.pengguna_id!==pid)       return { ok:false, msg:'Tidak berhak membatalkan' };
    if (['Dibatalkan','Selesai'].includes(b.status)) return { ok:false, msg:`Booking sudah ${b.status}` };
    b.status = 'Dibatalkan'; saveDB(db);
    return { ok:true, msg:'Booking dibatalkan' };
  });

  ipcMain.handle('booking:status', (_, id, status) => {
    const db = loadDB();
    const b  = db.booking.find(b=>b.id===id);
    if (b) { b.status = status; saveDB(db); }
    return { ok:true };
  });

  ipcMain.handle('booking:slots', (_, rid, tanggal) => {
    const db   = loadDB();
    const taken = new Set();
    db.booking.filter(b=>b.ruangan_id===rid&&b.tanggal===tanggal&&b.status!=='Dibatalkan')
      .forEach(b=>{ for(let h=b.jam_mulai;h<b.jam_selesai;h++) taken.add(h); });
    const slots = [];
    for(let h=6;h<22;h++) if(!taken.has(h)) slots.push({ jam:h, label:`${String(h).padStart(2,'0')}:00 – ${String(h+1).padStart(2,'0')}:00` });
    return slots;
  });

  ipcMain.handle('pengguna:list', () => loadDB().pengguna.map(({password_hash,...p})=>p));
}
