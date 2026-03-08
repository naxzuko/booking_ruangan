/* ═══════════════════════════════════════════════════════════════
   BOOKR — Frontend App Logic
   ═══════════════════════════════════════════════════════════════ */

// ─── State ────────────────────────────────────────────────────
let currentUser   = null;
let allRuangan    = [];
let allBookings   = [];
let calYear       = new Date().getFullYear();
let calMonth      = new Date().getMonth() + 1;
let bookingFilter = 'all';

const MONTHS = ['Januari','Februari','Maret','April','Mei','Juni',
                'Juli','Agustus','September','Oktober','November','Desember'];
const DAYS   = ['Min','Sen','Sel','Rab','Kam','Jum','Sab'];

// ─── DOM helpers ──────────────────────────────────────────────
const $ = id => document.getElementById(id);
const fmt = n => 'Rp' + Number(n).toLocaleString('id-ID');
const today = () => new Date().toISOString().split('T')[0];

function showToast(msg, type = 'success') {
  const t = $('toast');
  t.textContent = msg;
  t.className = `toast ${type}`;
  t.classList.remove('hidden');
  clearTimeout(window._toastTimer);
  window._toastTimer = setTimeout(() => t.classList.add('hidden'), 3000);
}

// ─── Screen & Page navigation ─────────────────────────────────
function showScreen(id) {
  document.querySelectorAll('.screen').forEach(s => s.classList.toggle('active', s.id === id));
}

function showPage(name) {
  document.querySelectorAll('.page').forEach(p => p.classList.toggle('active', p.id === `page-${name}`));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.toggle('active', n.dataset.page === name));
  if (name === 'dashboard')  loadDashboard();
  if (name === 'ruangan')    loadRuangan();
  if (name === 'booking')    loadBookings();
  if (name === 'pengguna')   loadPengguna();
}

// ─── AUTH ──────────────────────────────────────────────────────
$('btn-login').addEventListener('click', async () => {
  const email = $('login-email').value.trim();
  const pass  = $('login-pass').value;
  if (!email || !pass) return showErr('login-error', 'Email dan password wajib diisi');
  const res = await window.api.login(email, pass);
  if (!res.ok) return showErr('login-error', res.msg);
  onLogin(res.user);
});
$('login-pass').addEventListener('keydown', e => e.key === 'Enter' && $('btn-login').click());

$('btn-register').addEventListener('click', async () => {
  const data = {
    nama: $('reg-nama').value.trim(), email: $('reg-email').value.trim(),
    password: $('reg-pass').value,    no_telepon: $('reg-telp').value.trim()
  };
  if (!data.nama || !data.email || !data.password) return showErr('reg-error', 'Semua field wajib diisi');
  const res = await window.api.register(data);
  if (!res.ok) return showErr('reg-error', res.msg);
  showToast('Akun berhasil dibuat! Silakan login.');
  toggleAuthForm(false);
});

$('btn-show-register').addEventListener('click', () => toggleAuthForm(true));
$('btn-show-login').addEventListener('click',    () => toggleAuthForm(false));
$('btn-logout').addEventListener('click', () => {
  currentUser = null;
  showScreen('login-screen');
  $('login-email').value = ''; $('login-pass').value = '';
});

function toggleAuthForm(showReg) {
  $('login-form').classList.toggle('hidden', showReg);
  $('register-form').classList.toggle('hidden', !showReg);
  hideErr('login-error'); hideErr('reg-error');
}

function showErr(id, msg) { const el=$(id); el.textContent=msg; el.classList.remove('hidden'); }
function hideErr(id) { $(id).classList.add('hidden'); }

function onLogin(user) {
  currentUser = user;
  const isAdmin = user.role === 'Admin' || user.role === 'Super Admin';

  $('sidebar-name').textContent   = user.nama;
  $('sidebar-role').textContent   = user.role;
  $('sidebar-avatar').textContent = user.nama[0].toUpperCase();

  // Admin-only elements
  document.querySelectorAll('.admin-only').forEach(el => el.classList.toggle('hidden', !isAdmin));

  showScreen('app-screen');
  showPage('dashboard');
}

// ─── NAVIGATION ───────────────────────────────────────────────
document.querySelectorAll('.nav-item').forEach(item => {
  item.addEventListener('click', () => showPage(item.dataset.page));
});

// ─── DASHBOARD ────────────────────────────────────────────────
async function loadDashboard() {
  // Date
  const now = new Date();
  $('dash-date').textContent = now.toLocaleDateString('id-ID', { weekday:'long', day:'numeric', month:'long', year:'numeric' });
  const hour = now.getHours();
  const greet = hour < 11 ? 'Selamat pagi' : hour < 15 ? 'Selamat siang' : hour < 18 ? 'Selamat sore' : 'Selamat malam';
  $('dash-greeting').textContent = `${greet}, ${currentUser.nama.split(' ')[0]} 👋`;

  // Stats
  const stats = await window.api.getStats();
  $('stat-total').textContent     = stats.totalBooking;
  $('stat-pendapatan').textContent = fmt(stats.pendapatan);
  $('stat-hari-ini').textContent  = stats.bookingHariIni;
  $('stat-ruangan').textContent   = `${stats.ruanganAktif}/${stats.totalRuangan}`;

  // Calendar
  renderCalendar();

  // Recent bookings
  const recent = await window.api.getRecent();
  renderRecentBookings(recent);
}

// ── Calendar ─────────────────────────────────────────────────
async function renderCalendar() {
  $('cal-month-label').textContent = `${MONTHS[calMonth-1]} ${calYear}`;
  const data = await window.api.getCalendar(calYear, calMonth);

  const firstDay = new Date(calYear, calMonth-1, 1).getDay();
  const daysInMonth = new Date(calYear, calMonth, 0).getDate();
  const todayStr = today();

  let html = `<div class="cal-days-header">${DAYS.map(d=>`<div class="cal-day-name">${d}</div>`).join('')}</div><div class="cal-cells">`;
  for (let i=0; i<firstDay; i++) html += `<div class="cal-cell empty"></div>`;
  for (let d=1; d<=daysInMonth; d++) {
    const dateStr = `${calYear}-${String(calMonth).padStart(2,'0')}-${String(d).padStart(2,'0')}`;
    const isToday = dateStr === todayStr;
    const info = data[dateStr];
    const hasBk = !!info;
    html += `<div class="cal-cell ${isToday?'today':''} ${hasBk?'has-booking':''}">
      <span>${d}</span>
      ${hasBk ? `<div class="cal-dot"></div><div class="cal-count">${info.count}</div>` : ''}
    </div>`;
  }
  html += '</div>';
  $('calendar-grid').innerHTML = html;
}

$('cal-prev').addEventListener('click', () => {
  calMonth--; if (calMonth<1) { calMonth=12; calYear--; } renderCalendar();
});
$('cal-next').addEventListener('click', () => {
  calMonth++; if (calMonth>12) { calMonth=1; calYear++; } renderCalendar();
});

// ── Recent Bookings ───────────────────────────────────────────
function renderRecentBookings(items) {
  const statusColor = { 'Dikonfirmasi': 'var(--green)', 'Selesai': 'var(--blue)', 'Dibatalkan': 'var(--text-3)', 'Pending': 'var(--orange)' };
  $('recent-list').innerHTML = items.length ? items.map(b => `
    <div class="recent-item">
      <div class="recent-dot" style="background:${statusColor[b.status]||'var(--text-3)'}"></div>
      <div class="recent-info">
        <div class="ri-room">${b.nama_ruangan}</div>
        <div class="ri-time">${b.tanggal} · ${String(b.jam_mulai).padStart(2,'0')}:00–${String(b.jam_selesai).padStart(2,'0')}:00</div>
      </div>
      <div class="recent-price">${fmt(b.total_harga)}</div>
    </div>
  `).join('') : '<div style="padding:20px;text-align:center;color:var(--text-3);font-size:13px;">Belum ada booking</div>';
}

// ─── RUANGAN ──────────────────────────────────────────────────
async function loadRuangan() {
  allRuangan = await window.api.getRuangan();
  renderRuangan('all');
}

function renderRuangan(filter) {
  const isAdmin = currentUser.role === 'Admin' || currentUser.role === 'Super Admin';
  let list = allRuangan;
  if (filter === 'rapat')    list = list.filter(r => r.jenis === 'Ruangan Rapat');
  if (filter === 'olahraga') list = list.filter(r => r.jenis === 'Lapangan Olahraga');

  $('ruangan-grid').innerHTML = list.map(r => `
    <div class="ruangan-card ${r.tersedia ? 'available' : 'unavailable'}">
      <div class="rc-jenis">${r.jenis}</div>
      <div class="rc-nama">${r.nama}</div>
      <div class="rc-harga">${fmt(r.harga_per_jam)} / jam</div>
      <div class="rc-info">
        <span class="rc-tag">👥 ${r.kapasitas} orang</span>
        ${r.jenis_olahraga ? `<span class="rc-tag">⚽ ${r.jenis_olahraga}</span>` : ''}
        ${r.outdoor ? `<span class="rc-tag">🌿 Outdoor</span>` : ''}
        ${r.ada_proyektor ? `<span class="rc-tag">📽 Proyektor</span>` : ''}
      </div>
      <div class="rc-status-row">
        <span class="rc-status ${r.tersedia?'on':'off'}">${r.tersedia ? '● Tersedia' : '● Tidak Tersedia'}</span>
        ${isAdmin ? `<button class="toggle-btn" onclick="toggleRuangan(${r.id})">${r.tersedia ? 'Nonaktifkan' : 'Aktifkan'}</button>` : ''}
      </div>
    </div>
  `).join('');
}

document.querySelectorAll('#filter-tabs .filter-tab').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('#filter-tabs .filter-tab').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    renderRuangan(btn.dataset.filter);
  });
});

async function toggleRuangan(id) {
  const res = await window.api.toggleRuangan(id);
  if (res.ok) { await loadRuangan(); showToast('Status ruangan diperbarui'); }
}

// ─── BOOKING ──────────────────────────────────────────────────
async function loadBookings() {
  const isAdmin = currentUser.role === 'Admin' || currentUser.role === 'Super Admin';
  allBookings = await window.api.getBookings(currentUser.id, isAdmin);
  renderBookings(bookingFilter);
}

function renderBookings(filter) {
  bookingFilter = filter;
  const isAdmin = currentUser.role === 'Admin' || currentUser.role === 'Super Admin';
  let list = allBookings;
  if (filter !== 'all') list = list.filter(b => b.status === filter);

  const badgeClass = { 'Dikonfirmasi':'badge-ok','Selesai':'badge-done','Dibatalkan':'badge-cancel','Pending':'badge-pend' };

  $('booking-tbody').innerHTML = list.length ? list.map(b => `
    <tr>
      <td>#${b.id}</td>
      <td class="td-room">${b.nama_ruangan}${isAdmin ? `<br><small style="color:var(--text-3)">${b.nama_pengguna||''}</small>` : ''}</td>
      <td>${b.tanggal}</td>
      <td>${String(b.jam_mulai).padStart(2,'0')}:00 – ${String(b.jam_selesai).padStart(2,'0')}:00</td>
      <td class="td-price">${fmt(b.total_harga)}</td>
      <td><span class="badge ${badgeClass[b.status]||'badge-pend'}">${b.status}</span></td>
      <td>
        ${b.status !== 'Dibatalkan' && b.status !== 'Selesai' ?
          `<button class="action-btn" onclick="doCancel(${b.id})">Batalkan</button>` : ''}
        ${isAdmin && b.status === 'Pending' ?
          `<button class="action-btn confirm" onclick="doConfirm(${b.id})" style="margin-left:4px">Konfirmasi</button>` : ''}
        ${isAdmin && b.status === 'Dikonfirmasi' ?
          `<button class="action-btn confirm" onclick="doFinish(${b.id})" style="margin-left:4px">Selesai</button>` : ''}
      </td>
    </tr>
  `).join('') : `<tr><td colspan="7" style="text-align:center;padding:28px;color:var(--text-3)">Tidak ada data booking</td></tr>`;
}

// Status filter tabs on booking page
document.querySelectorAll('#page-booking .filter-tab').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('#page-booking .filter-tab').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    renderBookings(btn.dataset.status);
  });
});

async function doCancel(id) {
  if (!confirm('Batalkan booking ini?')) return;
  const isAdmin = currentUser.role === 'Admin' || currentUser.role === 'Super Admin';
  const res = await window.api.cancelBooking(id, currentUser.id, isAdmin);
  if (res.ok) { showToast(res.msg); await loadBookings(); }
  else showToast(res.msg, 'error');
}
async function doConfirm(id) {
  await window.api.setStatus(id, 'Dikonfirmasi');
  showToast('Booking dikonfirmasi');
  await loadBookings();
}
async function doFinish(id) {
  await window.api.setStatus(id, 'Selesai');
  showToast('Booking ditandai selesai');
  await loadBookings();
}

// ─── NEW BOOKING MODAL ────────────────────────────────────────
$('btn-new-booking').addEventListener('click', async () => {
  const ruangan = await window.api.getRuangan();
  const tersedia = ruangan.filter(r => r.tersedia);
  $('bk-ruangan').innerHTML = tersedia.map(r => `<option value="${r.id}" data-harga="${r.harga_per_jam}" data-jenis="${r.jenis}" data-outdoor="${r.outdoor}">${r.nama} — ${fmt(r.harga_per_jam)}/jam</option>`).join('');
  $('bk-tanggal').value = today();
  populateJamSelect($('bk-jam-mulai'), 6, 21);
  populateJamSelect($('bk-jam-selesai'), 7, 22);
  $('bk-jam-mulai').value = 8; $('bk-jam-selesai').value = 10;
  hideErr('bk-error');
  updatePricePreview();
  openModal('modal-booking');
});

function populateJamSelect(sel, from, to) {
  sel.innerHTML = '';
  for (let h=from; h<=to; h++) sel.innerHTML += `<option value="${h}">${String(h).padStart(2,'0')}:00</option>`;
}

function updatePricePreview() {
  const opt = $('bk-ruangan').options[$('bk-ruangan').selectedIndex];
  if (!opt) return;
  const harga  = parseFloat(opt.dataset.harga);
  const jenis  = opt.dataset.jenis;
  const outdoor = opt.dataset.outdoor === '1';
  const durasi = parseInt($('bk-jam-selesai').value) - parseInt($('bk-jam-mulai').value);
  if (durasi <= 0) { $('bk-price-preview').classList.add('hidden'); return; }
  let total = harga * durasi;
  if (jenis === 'Ruangan Rapat') total *= 1.10;
  else if (outdoor) total *= 0.85;
  $('bk-price-val').textContent = fmt(total);
  $('bk-price-preview').classList.remove('hidden');
}

['bk-ruangan','bk-jam-mulai','bk-jam-selesai'].forEach(id => {
  $(id).addEventListener('change', updatePricePreview);
});

$('btn-submit-booking').addEventListener('click', async () => {
  const data = {
    pengguna_id: currentUser.id,
    ruangan_id:  parseInt($('bk-ruangan').value),
    tanggal:     $('bk-tanggal').value,
    jam_mulai:   parseInt($('bk-jam-mulai').value),
    jam_selesai: parseInt($('bk-jam-selesai').value),
    keterangan:  $('bk-ket').value.trim()
  };
  hideErr('bk-error');
  const res = await window.api.createBooking(data);
  if (!res.ok) return showErr('bk-error', res.msg);
  closeModal('modal-booking');
  showToast(res.msg);
  await loadBookings();
});

// ─── PENGGUNA ─────────────────────────────────────────────────
async function loadPengguna() {
  const list = await window.api.getPengguna();
  $('pengguna-tbody').innerHTML = list.map(p => `
    <tr>
      <td>#${p.id}</td>
      <td style="color:var(--text)">${p.nama}</td>
      <td>${p.email}</td>
      <td>${p.no_telepon || '—'}</td>
      <td><span class="badge ${p.role==='Member'?'badge-pend':'badge-ok'}">${p.role}</span></td>
      <td style="color:var(--blue);font-weight:600">${p.poin}</td>
      <td><span class="badge ${p.aktif?'badge-ok':'badge-cancel'}">${p.aktif?'Aktif':'Nonaktif'}</span></td>
    </tr>
  `).join('');
}

// ─── MODAL UTILS ──────────────────────────────────────────────
function openModal(id)  { $(id).classList.remove('hidden'); }
function closeModal(id) { $(id).classList.add('hidden'); }

document.querySelectorAll('[data-modal]').forEach(btn => {
  btn.addEventListener('click', () => closeModal(btn.dataset.modal));
});
document.querySelectorAll('.modal-overlay').forEach(overlay => {
  overlay.addEventListener('click', e => { if (e.target === overlay) closeModal(overlay.id); });
});
