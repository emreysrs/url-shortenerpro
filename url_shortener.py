from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, HttpUrl
import sqlite3
from datetime import datetime
from pathlib import Path
import io
import base64

DB_PATH = Path(__file__).with_name("url_shortener.db")
ALPHABET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

app = FastAPI(title="URL Shortener Pro")

# ============ Yardımcı Fonksiyonlar ============
def base62(n: int) -> str:
    if n == 0:
        return ALPHABET[0]
    s = []
    b = len(ALPHABET)
    while n > 0:
        n, r = divmod(n, b)
        s.append(ALPHABET[r])
    return "".join(reversed(s))

def base62_decode(code: str) -> int:
    b = len(ALPHABET)
    n = 0
    for c in code:
        n = n * b + ALPHABET.index(c)
    return n

def get_conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_url TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL,
                clicks INTEGER DEFAULT 0
            )
        """)
        conn.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_original_url ON urls(original_url)
        """)

def generate_qr(data: str) -> str:
    """QR kod oluştur (base64 PNG döndürür)"""
    try:
        import qrcode
        qr = qrcode.QRCode(version=1, box_size=10, border=2)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return base64.b64encode(buf.read()).decode()
    except ImportError:
        return ""

@app.on_event("startup")
def startup():
    init_db()

# ============ Modeller ============
class ShortenIn(BaseModel):
    url: HttpUrl

class ShortenOut(BaseModel):
    code: str
    short_url: str
    long_url: str
    qr_code: str = ""

class URLDetail(BaseModel):
    id: int
    code: str
    original_url: str
    created_at: str
    clicks: int

# ============ Ana Sayfa (Web UI) ============
@app.get("/", response_class=HTMLResponse)
def home():
    return """
<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>✨ URL Kısaltıcı Pro</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');
    
    :root {
      --gradient-1: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      --gradient-2: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
      --gradient-3: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
      --gradient-hero: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
      --shadow-sm: 0 2px 8px rgba(0,0,0,.08);
      --shadow-md: 0 8px 30px rgba(0,0,0,.12);
      --shadow-lg: 0 20px 60px rgba(0,0,0,.3);
      --bg: #f8f9fe;
      --fg: #1a202c;
      --muted: #64748b;
      --card-bg: rgba(255,255,255,.85);
      --input-bg: #fff;
      --border: rgba(0,0,0,.08);
      --success: #10b981;
      --danger: #ef4444;
    }
    
    [data-theme="dark"] {
      --gradient-hero: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
      --bg: #0f172a;
      --fg: #f1f5f9;
      --muted: #94a3b8;
      --card-bg: rgba(30,41,59,.85);
      --input-bg: #1e293b;
      --border: rgba(255,255,255,.1);
    }
    
    * { box-sizing: border-box; margin: 0; padding: 0; }
    
    body {
      font-family: 'Inter', system-ui, -apple-system, sans-serif;
      background: var(--bg);
      color: var(--fg);
      min-height: 100vh;
      overflow-x: hidden;
      position: relative;
    }
    
    /* Animated gradient background */
    body::before {
      content: '';
      position: fixed;
      top: -50%;
      left: -50%;
      width: 200%;
      height: 200%;
      background: var(--gradient-hero);
      opacity: .15;
      animation: gradient-shift 15s ease infinite;
      z-index: -1;
    }
    
    @keyframes gradient-shift {
      0%, 100% { transform: translate(0, 0) rotate(0deg); }
      33% { transform: translate(5%, 5%) rotate(120deg); }
      66% { transform: translate(-5%, 5%) rotate(240deg); }
    }
    
    /* Floating particles */
    .particles { position: fixed; width: 100%; height: 100%; top: 0; left: 0; z-index: -1; pointer-events: none; }
    .particle {
      position: absolute;
      width: 3px;
      height: 3px;
      background: var(--gradient-3);
      border-radius: 50%;
      opacity: .4;
      animation: float 20s infinite ease-in-out;
    }
    
    @keyframes float {
      0%, 100% { transform: translate(0, 0) scale(1); }
      25% { transform: translate(100px, -100px) scale(1.2); }
      50% { transform: translate(-50px, -200px) scale(.8); }
      75% { transform: translate(150px, -150px) scale(1.1); }
    }
    
    .container {
      max-width: 1100px;
      margin: 0 auto;
      padding: 40px 24px;
      position: relative;
      z-index: 1;
    }
    
    /* Header with gradient text */
    .hero {
      text-align: center;
      margin-bottom: 48px;
      animation: fade-in-up .8s ease;
    }
    
    @keyframes fade-in-up {
      from { opacity: 0; transform: translateY(30px); }
      to { opacity: 1; transform: translateY(0); }
    }
    
    h1 {
      font-size: clamp(32px, 5vw, 56px);
      font-weight: 900;
      background: var(--gradient-hero);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      margin-bottom: 12px;
      letter-spacing: -0.02em;
    }
    
    .subtitle {
      color: var(--muted);
      font-size: 18px;
      font-weight: 500;
    }
    
    /* Glassmorphism cards */
    .card {
      background: var(--card-bg);
      backdrop-filter: blur(20px);
      border: 1px solid var(--border);
      border-radius: 24px;
      padding: 32px;
      margin: 24px 0;
      box-shadow: var(--shadow-md);
      transition: all .3s cubic-bezier(.4,0,.2,1);
      animation: fade-in-up .8s ease;
      animation-fill-mode: backwards;
    }
    
    .card:nth-child(2) { animation-delay: .1s; }
    .card:nth-child(3) { animation-delay: .2s; }
    
    .card:hover {
      transform: translateY(-4px);
      box-shadow: var(--shadow-lg);
    }
    
    /* Input styling */
    .input-group {
      display: flex;
      gap: 12px;
      margin-bottom: 24px;
    }
    
    input {
      flex: 1;
      font-family: inherit;
      font-size: 16px;
      padding: 16px 20px;
      border: 2px solid var(--border);
      border-radius: 16px;
      background: var(--input-bg);
      color: var(--fg);
      outline: none;
      transition: all .3s ease;
    }
    
    input:focus {
      border-color: #667eea;
      box-shadow: 0 0 0 4px rgba(102,126,234,.1);
    }
    
    input::placeholder { color: var(--muted); }
    
    /* Gradient buttons */
    button {
      font-family: inherit;
      font-size: 16px;
      font-weight: 600;
      padding: 16px 32px;
      border: 0;
      border-radius: 16px;
      background: var(--gradient-1);
      color: #fff;
      cursor: pointer;
      transition: all .3s ease;
      box-shadow: var(--shadow-sm);
      position: relative;
      overflow: hidden;
    }
    
    button::before {
      content: '';
      position: absolute;
      top: 0;
      left: -100%;
      width: 100%;
      height: 100%;
      background: linear-gradient(90deg, transparent, rgba(255,255,255,.3), transparent);
      transition: left .5s;
    }
    
    button:hover::before { left: 100%; }
    button:hover { transform: translateY(-2px); box-shadow: var(--shadow-md); }
    button:active { transform: scale(.98); }
    
    .btn-danger {
      background: var(--gradient-2);
      padding: 8px 16px;
      font-size: 14px;
    }
    
    .btn-secondary {
      background: var(--gradient-3);
      padding: 12px 24px;
    }
    
    /* Result card */
    .result {
      margin-top: 24px;
      padding: 20px;
      background: linear-gradient(135deg, rgba(102,126,234,.1), rgba(246,173,85,.1));
      border-radius: 16px;
      border: 2px dashed var(--border);
      animation: slide-in .4s ease;
    }
    
    @keyframes slide-in {
      from { opacity: 0; transform: translateY(-10px); }
      to { opacity: 1; transform: translateY(0); }
    }
    
    .result-url {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 16px;
      flex-wrap: wrap;
    }
    
    .result-url strong { color: var(--fg); font-size: 14px; }
    .result-url a {
      color: #667eea;
      text-decoration: none;
      font-weight: 600;
      word-break: break-all;
      position: relative;
    }
    
    .result-url a::after {
      content: '';
      position: absolute;
      bottom: -2px;
      left: 0;
      width: 0;
      height: 2px;
      background: #667eea;
      transition: width .3s ease;
    }
    
    .result-url a:hover::after { width: 100%; }
    
    .qr-container {
      display: inline-block;
      padding: 12px;
      background: #fff;
      border-radius: 12px;
      box-shadow: var(--shadow-sm);
    }
    
    .qr { max-width: 180px; display: block; border-radius: 8px; }
    
    /* URL list */
    .list-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
    }
    
    .list-header h2 {
      font-size: 24px;
      font-weight: 700;
    }
    
    .url-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 20px;
      margin-bottom: 12px;
      background: rgba(102,126,234,.05);
      border-radius: 16px;
      border: 1px solid var(--border);
      transition: all .3s ease;
      animation: fade-in .3s ease;
    }
    
    @keyframes fade-in {
      from { opacity: 0; }
      to { opacity: 1; }
    }
    
    .url-item:hover {
      background: rgba(102,126,234,.1);
      transform: translateX(4px);
    }
    
    .url-info { flex: 1; }
    .url-code {
      display: inline-block;
      padding: 4px 12px;
      background: var(--gradient-1);
      color: #fff;
      border-radius: 8px;
      font-weight: 600;
      font-size: 14px;
      margin-right: 12px;
    }
    
    .url-link {
      color: var(--fg);
      text-decoration: none;
      font-weight: 500;
    }
    
    .url-link:hover { color: #667eea; }
    
    .url-meta {
      color: var(--muted);
      font-size: 14px;
      margin-top: 8px;
      display: flex;
      gap: 16px;
    }
    
    .url-actions {
      display: flex;
      gap: 8px;
    }
    
    /* Theme toggle */
    .theme-toggle {
      position: fixed;
      top: 24px;
      right: 24px;
      width: 56px;
      height: 56px;
      border-radius: 50%;
      background: var(--card-bg);
      backdrop-filter: blur(10px);
      border: 1px solid var(--border);
      box-shadow: var(--shadow-md);
      cursor: pointer;
      z-index: 1000;
      font-size: 24px;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all .3s ease;
    }
    
    .theme-toggle:hover {
      transform: rotate(180deg) scale(1.1);
    }
    
    /* Language selector */
    .lang-selector {
      position: fixed;
      top: 24px;
      left: 24px;
      display: flex;
      gap: 8px;
      z-index: 1000;
    }
    
    .lang-btn {
      padding: 10px 16px;
      border-radius: 12px;
      background: var(--card-bg);
      backdrop-filter: blur(10px);
      border: 2px solid var(--border);
      color: var(--fg);
      font-size: 14px;
      font-weight: 600;
      cursor: pointer;
      transition: all .3s ease;
      box-shadow: var(--shadow-sm);
    }
    
    .lang-btn:hover {
      transform: translateY(-2px);
      box-shadow: var(--shadow-md);
      border-color: #667eea;
    }
    
    .lang-btn.active {
      background: var(--gradient-1);
      color: #fff;
      border-color: transparent;
    }
    
    /* Loading spinner */
    .spinner {
      display: inline-block;
      width: 20px;
      height: 20px;
      border: 3px solid rgba(102,126,234,.3);
      border-top-color: #667eea;
      border-radius: 50%;
      animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
      to { transform: rotate(360deg); }
    }
    
    /* Copy button */
    .copy-btn {
      padding: 8px 16px;
      font-size: 14px;
      background: var(--gradient-3);
    }
    
    /* Stats badge */
    .stats-badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 10px;
      background: rgba(16,185,129,.15);
      color: var(--success);
      border-radius: 8px;
      font-size: 13px;
      font-weight: 600;
    }
    
    /* Empty state */
    .empty-state {
      text-align: center;
      padding: 60px 20px;
      color: var(--muted);
    }
    
    .empty-state svg {
      width: 120px;
      height: 120px;
      margin-bottom: 20px;
      opacity: .5;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
      .container { padding: 20px 16px; }
      .hero h1 { font-size: 32px; }
      .input-group { flex-direction: column; }
      button { width: 100%; }
      .url-item { flex-direction: column; align-items: flex-start; gap: 12px; }
      .url-actions { width: 100%; justify-content: stretch; }
      .url-actions button { flex: 1; }
      
      .lang-selector {
        top: auto;
        bottom: 24px;
        left: 50%;
        transform: translateX(-50%);
        background: var(--card-bg);
        backdrop-filter: blur(10px);
        padding: 8px;
        border-radius: 16px;
        box-shadow: var(--shadow-lg);
      }
      
      .theme-toggle {
        top: auto;
        bottom: 24px;
        right: 24px;
      }
      
      .card { padding: 20px; }
      .list-header { flex-direction: column; align-items: flex-start; gap: 12px; }
      .list-header button { width: 100%; }
    }
  </style>
</head>
<body>
  <div class="particles" id="particles"></div>
  
  <button class="theme-toggle" onclick="toggleTheme()" title="Toggle Theme">
    <span id="theme-icon">🌙</span>
  </button>
  
  <div class="lang-selector">
    <button class="lang-btn" onclick="changeLang('en')" data-lang="en">🇬🇧 EN</button>
    <button class="lang-btn" onclick="changeLang('tr')" data-lang="tr">🇹🇷 TR</button>
    <button class="lang-btn" onclick="changeLang('de')" data-lang="de">🇩🇪 DE</button>
  </div>
  
  <div class="container">
    <div class="hero">
      <h1 data-i18n="title">✨ URL Shortener Pro</h1>
      <p class="subtitle" data-i18n="subtitle">Shorten long links instantly • Generate QR codes • Track statistics</p>
    </div>
    
    <div class="card">
      <div class="input-group">
        <input 
          id="url" 
          type="url"
          data-i18n-placeholder="inputPlaceholder"
          placeholder="https://example.com/very-long-url-here..." 
          onkeypress="if(event.key==='Enter')shorten()"
        />
        <button onclick="shorten()"><span data-i18n="shortenBtn">🚀 Shorten</span></button>
      </div>
      <div id="result"></div>
    </div>

    <div class="card">
      <div class="list-header">
        <h2><span data-i18n="allUrls">📊 All URLs</span></h2>
        <button class="btn-secondary" onclick="loadAll()"><span data-i18n="refreshBtn">🔄 Refresh</span></button>
      </div>
      <div id="list"></div>
    </div>
  </div>

  <script>
    // Translations
    const translations = {
      en: {
        title: '✨ URL Shortener Pro',
        subtitle: 'Shorten long links instantly • Generate QR codes • Track statistics',
        inputPlaceholder: 'https://example.com/very-long-url-here...',
        shortenBtn: '🚀 Shorten',
        allUrls: '📊 All URLs',
        refreshBtn: '🔄 Refresh',
        processing: 'Processing...',
        pleaseEnterUrl: '❌ Please enter a URL',
        error: 'Error',
        shortUrl: 'Short URL:',
        copy: '📋 Copy',
        copied: '✅ Copied!',
        delete: '🗑️',
        clicks: 'clicks',
        noUrls: 'No shortened URLs yet.',
        startMessage: 'Add a URL from above to get started! 🚀',
        deleteConfirm: 'Are you sure you want to delete this URL?',
        deleteError: '❌ Could not delete',
        copyError: '❌ Could not copy'
      },
      tr: {
        title: '✨ URL Kısaltıcı Pro',
        subtitle: 'Uzun linkleri anında kısalt • QR kod üret • İstatistik tut',
        inputPlaceholder: 'https://ornek.com/cok-uzun-bir-url-buraya...',
        shortenBtn: '🚀 Kısalt',
        allUrls: '📊 Tüm URLler',
        refreshBtn: '🔄 Yenile',
        processing: 'İşleniyor...',
        pleaseEnterUrl: '❌ Lütfen bir URL girin',
        error: 'Hata',
        shortUrl: 'Kısa URL:',
        copy: '📋 Kopyala',
        copied: '✅ Kopyalandı!',
        delete: '🗑️',
        clicks: 'tıklama',
        noUrls: 'Henüz kısaltılmış URL yok.',
        startMessage: 'Yukarıdan bir URL ekleyerek başlayın! 🚀',
        deleteConfirm: 'Bu URLi silmek istediğinizden emin misiniz?',
        deleteError: '❌ Silinemedi',
        copyError: '❌ Kopyalanamadı'
      },
      de: {
        title: '✨ URL-Kürzer Pro',
        subtitle: 'Lange Links sofort kürzen • QR-Codes generieren • Statistiken verfolgen',
        inputPlaceholder: 'https://beispiel.com/sehr-lange-url-hier...',
        shortenBtn: '🚀 Kürzen',
        allUrls: '📊 Alle URLs',
        refreshBtn: '🔄 Aktualisieren',
        processing: 'Wird verarbeitet...',
        pleaseEnterUrl: '❌ Bitte geben Sie eine URL ein',
        error: 'Fehler',
        shortUrl: 'Kurz-URL:',
        copy: '📋 Kopieren',
        copied: '✅ Kopiert!',
        delete: '🗑️',
        clicks: 'Klicks',
        noUrls: 'Noch keine gekürzten URLs.',
        startMessage: 'Fügen Sie oben eine URL hinzu, um zu beginnen! 🚀',
        deleteConfirm: 'Sind Sie sicher, dass Sie diese URL löschen möchten?',
        deleteError: '❌ Konnte nicht gelöscht werden',
        copyError: '❌ Konnte nicht kopiert werden'
      }
    };
    
    // Language management
    let currentLang = localStorage.getItem('lang') || 'en';
    
    function changeLang(lang) {
      currentLang = lang;
      localStorage.setItem('lang', lang);
      updateLanguage();
      playSound('click');
    }
    
    function updateLanguage() {
      const t = translations[currentLang];
      
      // Update all elements with data-i18n attribute
      document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (t[key]) el.textContent = t[key];
      });
      
      // Update placeholder
      const input = document.getElementById('url');
      if (input) input.placeholder = t.inputPlaceholder;
      
      // Update active language button
      document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.classList.toggle('active', btn.getAttribute('data-lang') === currentLang);
      });
      
      // Reload list to update translations
      if (document.getElementById('list').children.length > 0) {
        loadAll();
      }
    }
    
    // Theme management
    let theme = localStorage.getItem('theme') || 'light';
    document.documentElement.dataset.theme = theme;
    updateThemeIcon();
    
    function toggleTheme() {
      theme = theme === 'dark' ? 'light' : 'dark';
      document.documentElement.dataset.theme = theme;
      localStorage.setItem('theme', theme);
      updateThemeIcon();
      playSound('click');
    }
    
    function updateThemeIcon() {
      document.getElementById('theme-icon').textContent = theme === 'dark' ? '☀️' : '🌙';
    }
    
    // Initialize language on load
    updateLanguage();
    
    // Generate floating particles
    function createParticles() {
      const container = document.getElementById('particles');
      for (let i = 0; i < 15; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.left = Math.random() * 100 + '%';
        particle.style.top = Math.random() * 100 + '%';
        particle.style.animationDelay = Math.random() * 20 + 's';
        particle.style.animationDuration = (15 + Math.random() * 10) + 's';
        container.appendChild(particle);
      }
    }
    createParticles();
    
    // Sound Effects System
    let audioContext;
    try {
      audioContext = new (window.AudioContext || window.webkitAudioContext)();
    } catch(e) {
      console.warn('Audio not supported:', e);
    }
    
    function playSound(type) {
      if (!audioContext) return;
      
      try {
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
      
      oscillator.connect(gainNode);
      gainNode.connect(audioContext.destination);
      
      switch(type) {
        case 'success':
          // Başarı sesi - yükselen notalar
          oscillator.frequency.setValueAtTime(523.25, audioContext.currentTime); // C5
          oscillator.frequency.setValueAtTime(659.25, audioContext.currentTime + 0.1); // E5
          oscillator.frequency.setValueAtTime(783.99, audioContext.currentTime + 0.2); // G5
          gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
          gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.4);
          oscillator.start(audioContext.currentTime);
          oscillator.stop(audioContext.currentTime + 0.4);
          break;
          
        case 'copy':
          // Kopyalama sesi - kısa bip
          oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
          oscillator.type = 'sine';
          gainNode.gain.setValueAtTime(0.2, audioContext.currentTime);
          gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.15);
          oscillator.start(audioContext.currentTime);
          oscillator.stop(audioContext.currentTime + 0.15);
          break;
          
        case 'delete':
          // Silme sesi - düşen notalar
          oscillator.frequency.setValueAtTime(600, audioContext.currentTime);
          oscillator.frequency.exponentialRampToValueAtTime(200, audioContext.currentTime + 0.3);
          oscillator.type = 'sawtooth';
          gainNode.gain.setValueAtTime(0.15, audioContext.currentTime);
          gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3);
          oscillator.start(audioContext.currentTime);
          oscillator.stop(audioContext.currentTime + 0.3);
          break;
          
        case 'error':
          // Hata sesi - düşük titreşim
          oscillator.frequency.setValueAtTime(150, audioContext.currentTime);
          oscillator.type = 'sawtooth';
          gainNode.gain.setValueAtTime(0.2, audioContext.currentTime);
          gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.4);
          oscillator.start(audioContext.currentTime);
          oscillator.stop(audioContext.currentTime + 0.4);
          break;
          
        case 'click':
          // Tıklama sesi - kısa patlama
          oscillator.frequency.setValueAtTime(400, audioContext.currentTime);
          oscillator.type = 'square';
          gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
          gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.05);
          oscillator.start(audioContext.currentTime);
          oscillator.stop(audioContext.currentTime + 0.05);
          break;
      }
      } catch(e) {
        console.warn('Sound error:', e);
      }
    }
    
    // Confetti effect for success
    function createConfetti() {
      const colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe'];
      const confettiCount = 50;
      
      for (let i = 0; i < confettiCount; i++) {
        const confetti = document.createElement('div');
        confetti.style.position = 'fixed';
        confetti.style.width = '10px';
        confetti.style.height = '10px';
        confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
        confetti.style.left = Math.random() * 100 + '%';
        confetti.style.top = '-10px';
        confetti.style.borderRadius = Math.random() > 0.5 ? '50%' : '0';
        confetti.style.opacity = '1';
        confetti.style.zIndex = '9999';
        confetti.style.pointerEvents = 'none';
        document.body.appendChild(confetti);
        
        const duration = 2000 + Math.random() * 1000;
        const startTime = Date.now();
        const xMovement = (Math.random() - 0.5) * 200;
        
        function animateConfetti() {
          const elapsed = Date.now() - startTime;
          const progress = elapsed / duration;
          
          if (progress < 1) {
            confetti.style.top = (progress * window.innerHeight) + 'px';
            confetti.style.transform = `translateX(${xMovement * progress}px) rotate(${progress * 720}deg)`;
            confetti.style.opacity = (1 - progress).toString();
            requestAnimationFrame(animateConfetti);
          } else {
            confetti.remove();
          }
        }
        
        animateConfetti();
      }
    }
    
    // Shorten URL
    async function shorten() {
      const t = translations[currentLang];
      const input = document.getElementById('url');
      const url = input.value.trim();
      const resultDiv = document.getElementById('result');
      
      if (!url) {
        playSound('error');
        resultDiv.innerHTML = `<div class="result" style="border-color:var(--danger);background:rgba(239,68,68,.1);">${t.pleaseEnterUrl}</div>`;
        return;
      }
      
      playSound('click');
      resultDiv.innerHTML = `<div class="result"><div class="spinner"></div> ${t.processing}</div>`;
      
      try {
        const res = await fetch('/shorten', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({url})
        });
        
        if (!res.ok) throw new Error(await res.text());
        
        const data = await res.json();
        
        // Success sound and confetti!
        playSound('success');
        createConfetti();
        
        let html = '<div class="result">';
        html += '<div class="result-url">';
        html += `<strong>${t.shortUrl}</strong>`;
        html += `<a href="${data.short_url}" target="_blank">${data.short_url}</a>`;
        html += `<button class="copy-btn" onclick="copyToClipboard('${data.short_url}')">${t.copy}</button>`;
        html += '</div>';
        
        if (data.qr_code) {
          html += '<div class="qr-container">';
          html += `<img class="qr" src="data:image/png;base64,${data.qr_code}" alt="QR Code"/>`;
          html += '</div>';
        }
        
        html += '</div>';
        resultDiv.innerHTML = html;
        
        input.value = '';
        loadAll();
      } catch (e) {
        playSound('error');
        resultDiv.innerHTML = `<div class="result" style="border-color:var(--danger);background:rgba(239,68,68,.1);">❌ ${t.error}: ${e.message}</div>`;
      }
    }
    
    // Copy to clipboard
    async function copyToClipboard(text) {
      const t = translations[currentLang];
      try {
        await navigator.clipboard.writeText(text);
        playSound('copy');
        
        // Visual feedback
        const btn = event.target;
        const originalText = btn.innerHTML;
        btn.innerHTML = t.copied;
        btn.style.background = 'linear-gradient(135deg, #10b981, #059669)';
        
        setTimeout(() => {
          btn.innerHTML = originalText;
          btn.style.background = '';
        }, 2000);
      } catch (e) {
        playSound('error');
        alert(t.copyError);
      }
    }
    
    // Load all URLs
    async function loadAll() {
      const t = translations[currentLang];
      const listDiv = document.getElementById('list');
      listDiv.innerHTML = '<div style="text-align:center;padding:20px;"><div class="spinner"></div></div>';
      
      try {
        const res = await fetch('/urls');
        const data = await res.json();
        
        if (!data.length) {
          listDiv.innerHTML = `
            <div class="empty-state">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="8" x2="12" y2="12"/>
                <line x1="12" y1="16" x2="12.01" y2="16"/>
              </svg>
              <p>${t.noUrls}<br/>${t.startMessage}</p>
            </div>
          `;
          return;
        }
        
        const locale = currentLang === 'de' ? 'de-DE' : currentLang === 'tr' ? 'tr-TR' : 'en-US';
        
        listDiv.innerHTML = data.map(u => `
          <div class="url-item">
            <div class="url-info">
              <div>
                <span class="url-code">${u.code}</span>
                <a class="url-link" href="${u.original_url}" target="_blank">${u.original_url}</a>
              </div>
              <div class="url-meta">
                <span class="stats-badge">👆 ${u.clicks} ${t.clicks}</span>
                <span>📅 ${new Date(u.created_at).toLocaleDateString(locale)}</span>
              </div>
            </div>
            <div class="url-actions">
              <button class="copy-btn" onclick="copyToClipboard('${window.location.origin}/${u.code}')">📋</button>
              <button class="btn-danger" onclick="deleteURL(${u.id})">${t.delete}</button>
            </div>
          </div>
        `).join('');
      } catch (e) {
        listDiv.innerHTML = `<div class="empty-state">❌ ${t.error}</div>`;
      }
    }
    
    // Delete URL
    async function deleteURL(id) {
      const t = translations[currentLang];
      if (!confirm(t.deleteConfirm)) return;
      
      playSound('click');
      
      try {
        await fetch(`/urls/${id}`, {method: 'DELETE'});
        playSound('delete');
        loadAll();
      } catch (e) {
        playSound('error');
        alert(t.deleteError + ': ' + e.message);
      }
    }
    
    // Initial load
    loadAll();
  </script>
</body>
</html>
"""

# ============ API Endpoint'leri ============
@app.post("/shorten", response_model=ShortenOut)
def shorten(payload: ShortenIn, request: Request):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM urls WHERE original_url = ?", (str(payload.url),))
        row = cur.fetchone()
        if row:
            url_id = row[0]
        else:
            cur.execute(
                "INSERT INTO urls (original_url, created_at, clicks) VALUES (?, ?, 0)",
                (str(payload.url), datetime.utcnow())
            )
            url_id = cur.lastrowid
            conn.commit()
        
        code = base62(url_id)
        short_url = f"{request.base_url}{code}"
        qr = generate_qr(short_url)
        return ShortenOut(code=code, short_url=short_url, long_url=str(payload.url), qr_code=qr)

@app.get("/{code}")
def redirect_url(code: str):
    try:
        url_id = base62_decode(code)
    except (ValueError, IndexError):
        raise HTTPException(status_code=404, detail="Geçersiz kod")
    
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT original_url FROM urls WHERE id = ?", (url_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="URL bulunamadı")
        
        # Tıklama sayısını artır
        cur.execute("UPDATE urls SET clicks = clicks + 1 WHERE id = ?", (url_id,))
        conn.commit()
        
        return RedirectResponse(row[0], status_code=307)

@app.get("/urls", response_model=list[URLDetail])
def list_urls():
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, original_url, created_at, clicks FROM urls ORDER BY created_at DESC")
        rows = cur.fetchall()
        return [
            URLDetail(
                id=r[0],
                code=base62(r[0]),
                original_url=r[1],
                created_at=r[2],
                clicks=r[3]
            ) for r in rows
        ]

@app.delete("/urls/{url_id}")
def delete_url(url_id: int):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM urls WHERE id = ?", (url_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="URL bulunamadı")
        conn.commit()
    return {"message": "Silindi"}


