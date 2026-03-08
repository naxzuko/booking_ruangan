const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('api', {
  minimize: () => ipcRenderer.send('window-minimize'),
  maximize: () => ipcRenderer.send('window-maximize'),
  close:    () => ipcRenderer.send('window-close'),

  login:    (e,p)     => ipcRenderer.invoke('auth:login', e, p),
  register: (d)       => ipcRenderer.invoke('auth:register', d),

  getStats:    ()     => ipcRenderer.invoke('dashboard:stats'),
  getRecent:   ()     => ipcRenderer.invoke('dashboard:recent'),
  getCalendar: (y,m)  => ipcRenderer.invoke('dashboard:calendar', y, m),

  getRuangan:    ()   => ipcRenderer.invoke('ruangan:list'),
  toggleRuangan: (id) => ipcRenderer.invoke('ruangan:toggle', id),

  getBookings:   (pid,admin) => ipcRenderer.invoke('booking:list', pid, admin),
  createBooking: (d)         => ipcRenderer.invoke('booking:create', d),
  cancelBooking: (id,pid,a)  => ipcRenderer.invoke('booking:cancel', id, pid, a),
  setStatus:     (id,s)      => ipcRenderer.invoke('booking:status', id, s),
  getSlots:      (rid,tgl)   => ipcRenderer.invoke('booking:slots', rid, tgl),

  getPengguna: () => ipcRenderer.invoke('pengguna:list'),
});
