/* =====================================================
   AEE Platform — Global JavaScript
   Shared API helpers, auth, toast, utils
   ===================================================== */

const API = 'http://localhost:8000';

/* ── Auth helpers ── */
const Auth = {
  save(data) {
    localStorage.setItem('aee_token',    data.access_token);
    localStorage.setItem('aee_role',     data.role);
    localStorage.setItem('aee_user_id',  data.user_id);
    localStorage.setItem('aee_anon_id',  data.anonymous_id);
    localStorage.setItem('aee_name',     data.name || '');
    localStorage.setItem('aee_email',    data.email || '');
  },
  token()   { return localStorage.getItem('aee_token'); },
  role()    { return localStorage.getItem('aee_role'); },
  userId()  { return localStorage.getItem('aee_user_id'); },
  anonId()  { return localStorage.getItem('aee_anon_id'); },
  name()    { return localStorage.getItem('aee_name'); },
  email()   { return localStorage.getItem('aee_email'); },
  clear()   { ['aee_token','aee_role','aee_user_id','aee_anon_id','aee_name','aee_email'].forEach(k => localStorage.removeItem(k)); },
  isLoggedIn() { return !!this.token(); },
  headers() {
    const h = { 'Content-Type': 'application/json' };
    if (this.token()) h['Authorization'] = 'Bearer ' + this.token();
    return h;
  },
  redirectToDashboard() {
    const map = { student:'student', counselor:'counselor', advisor:'counselor',
                  admin:'admin', management:'management' };
    const role = this.role();
    window.location.href = `/ui/dashboard/${map[role] || 'student'}`;
  }
};

/* ── API request wrapper ── */
async function api(method, path, body = null) {
  const opts = { method, headers: Auth.headers() };
  if (body) opts.body = JSON.stringify(body);
  try {
    const res = await fetch(API + path, opts);
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`);
    return data;
  } catch (e) {
    throw e;
  }
}

/* ── Toast notifications ── */
function toast(msg, type = 'success', duration = 3000) {
  let el = document.getElementById('__toast__');
  if (!el) {
    el = document.createElement('div');
    el.id = '__toast__';
    el.className = 'toast';
    document.body.appendChild(el);
  }
  el.textContent = msg;
  el.className = `toast show ${type}`;
  clearTimeout(el._t);
  el._t = setTimeout(() => { el.className = 'toast'; }, duration);
}

/* ── Date helper ── */
function fmtDate(iso) {
  if (!iso) return '—';
  return new Date(iso).toLocaleString('en-BD', { month:'short', day:'numeric', hour:'2-digit', minute:'2-digit' });
}

function todayLabel() {
  return new Date().toLocaleDateString('en-BD', { weekday:'short', month:'short', day:'numeric' });
}

/* ── Role badge ── */
function roleBadge(role) {
  return `<span class="role-badge rb-${role}">${role}</span>`;
}

/* ── Risk badge ── */
function riskBadge(level) {
  const map = { HIGH:'red', MODERATE:'yellow', LOW:'green', UNKNOWN:'blue' };
  const col = map[level] || 'blue';
  return `<span style="font-size:.7rem;padding:2px 8px;border-radius:99px;font-weight:500;
          background:var(--${col}-d);color:var(--${col})">${level}</span>`;
}

/* ── Sidebar builder ── */
function buildSidebar({ items, active, role }) {
  const initials = (Auth.name() || Auth.email() || 'U').slice(0,2).toUpperCase();
  const roleLabel = { student:'Student', counselor:'Counselor', advisor:'Advisor',
                      admin:'System Admin', management:'University Mgmt' };

  const navHtml = items.map(it => {
    if (it.type === 'label') return `<div class="nav-lbl">${it.text}</div>`;
    const badge = it.badge ? `<span class="nav-badge" id="${it.badgeId || ''}">${it.badge}</span>` : '';
    const cls = it.id === active ? 'nav-item active' : 'nav-item';
    return `<button class="${cls}" onclick="${it.onclick}">${it.icon} ${it.label}${badge}</button>`;
  }).join('');

  return `
  <div class="sb-brand">
    <div class="brand-row">
      <div class="brand-icon">🧠</div>
      <div>
        <div class="brand-name">AEE Platform</div>
        <div class="brand-sub">CSE307 · IUB · Group 05</div>
      </div>
    </div>
    <div class="user-chip">
      <div class="user-av">${initials}</div>
      <div>
        <div class="user-nm">${Auth.name() || Auth.email()}</div>
        <div class="user-rl">${roleLabel[role] || role}</div>
      </div>
    </div>
  </div>
  <nav class="sb-nav">${navHtml}</nav>
  <div class="sb-foot">
    <button class="logout-btn" onclick="doLogout()">🚪 Sign out</button>
    <div class="sb-copy">CSE307 · Section 01 · Group 05<br>Independent University, Bangladesh</div>
  </div>`;
}

/* ── Topbar builder ── */
function buildTopbar({ title, tag, tagClass = 'tag-blue', showNotif = false }) {
  return `
  <div class="tb-left">
    <div class="pg-title">${title}</div>
    <span class="pg-tag ${tagClass}">${tag}</span>
  </div>
  <div class="tb-right">
    <span class="tb-date">${todayLabel()}</span>
    ${showNotif ? `<button class="tb-btn" onclick="openNotifPanel()">🔔 Alerts <span class="notif-dot" id="notif-dot"></span></button>` : ''}
    <button class="tb-btn" onclick="doLogout()">← Logout</button>
  </div>`;
}

/* ── Logout ── */
function doLogout() {
  Auth.clear();
  window.location.href = '/ui/login';
}

/* ── Guard: redirect to login if not logged in ── */
function requireAuth() {
  if (!Auth.isLoggedIn()) { window.location.href = '/ui/login'; return false; }
  return true;
}

/* ── Chart.js color helpers ── */
const CH = {
  gridColor: 'rgba(255,255,255,0.05)',
  tickColor: '#5a6380',
  defaultOptions(yMax = 10) {
    return {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        y: { min:0, max:yMax, ticks:{ color:CH.tickColor, font:{size:10} }, grid:{ color:CH.gridColor } },
        x: { ticks:{ color:CH.tickColor, font:{size:10} }, grid:{ display:false } }
      }
    };
  },
  bar(ctx, labels, data, colors) {
    return new Chart(ctx, {
      type: 'bar',
      data: { labels, datasets:[{ data, backgroundColor: colors, borderRadius:4, borderSkipped:false }] },
      options: CH.defaultOptions()
    });
  },
  line(ctx, labels, data, color) {
    return new Chart(ctx, {
      type: 'line',
      data: { labels, datasets:[{ data, borderColor:color, backgroundColor: color+'22',
               tension:0.4, fill:true, pointRadius:3, pointBackgroundColor:color }] },
      options: CH.defaultOptions()
    });
  },
  donut(ctx, labels, data, colors) {
    return new Chart(ctx, {
      type: 'doughnut',
      data: { labels, datasets:[{ data, backgroundColor:colors, borderWidth:0, hoverOffset:4 }] },
      options: { responsive:true, maintainAspectRatio:false, cutout:'65%',
                 plugins:{ legend:{ display:true, position:'bottom',
                 labels:{ color:'#8896b3', font:{size:11}, boxWidth:10 } } } }
    });
  }
};


