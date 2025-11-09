# 🚀 Deployment Guide - URL Shortener Pro

Bu rehber, URL Shortener Pro'yu internette yayınlamak için adım adım talimatlar içerir.

## 📋 İçindekiler
1. [Render.com (Önerilen)](#1-rendercom-önerilen)
2. [Railway.app](#2-railwayapp)
3. [Fly.io](#3-flyio)
4. [Heroku](#4-heroku)
5. [VPS (Digital Ocean / Linode)](#5-vps-deployment)

---

## 1️⃣ Render.com (Önerilen)

**✅ Avantajlar:**
- Ücretsiz plan (750 saat/ay)
- Otomatik HTTPS
- Kolay setup
- Git ile otomatik deploy

**📝 Adımlar:**

### A. GitHub'a Yükle

1. **GitHub'da yeni repository oluştur:**
   - https://github.com/new adresine git
   - Repository adı: `url-shortener-pro`
   - Public veya Private seç
   - "Create repository" tıkla

2. **Local repository'i GitHub'a push et:**
```bash
cd "/Users/emre/Desktop/Github Projects/url shortener"
git remote add origin https://github.com/KULLANICI_ADIN/url-shortener-pro.git
git branch -M main
git push -u origin main
```

### B. Render'da Deploy Et

1. **Render hesabı oluştur:**
   - https://render.com adresine git
   - GitHub ile giriş yap

2. **New Web Service oluştur:**
   - Dashboard'da "New +" → "Web Service"
   - GitHub repository'ini seç (`url-shortener-pro`)

3. **Ayarları yapılandır:**
   ```
   Name: url-shortener-pro
   Region: Frankfurt (veya Oregon)
   Branch: main
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: ./start.sh
   Instance Type: Free
   ```

4. **Environment Variables ekle (opsiyonel):**
   - `PYTHON_VERSION`: `3.11.0`
   - `PORT`: `10000` (Render otomatik ayarlar)

5. **"Create Web Service" tıkla**

6. **Deploy tamamlanınca:**
   - URL: `https://url-shortener-pro-xxxx.onrender.com`
   - Deployment 2-3 dakika sürer

**⚠️ Not:** Ücretsiz planda 15 dakika inaktiflik sonrası uygulama uyur. İlk istek 30-60 saniye sürebilir.

---

## 2️⃣ Railway.app

**✅ Avantajlar:**
- $5 ücretsiz kredi/ay
- Daha hızlı cold start
- Kolay kullanım

**📝 Adımlar:**

1. **Railway hesabı oluştur:**
   - https://railway.app adresine git
   - GitHub ile giriş yap

2. **New Project:**
   - "Deploy from GitHub repo"
   - Repository seç

3. **Settings:**
   - `Start Command`: `uvicorn url-shortener:app --host 0.0.0.0 --port $PORT`
   - Otomatik environment detect eder

4. **Domain:**
   - Settings → Networking → Generate Domain

**URL:** `https://url-shortener-pro.up.railway.app`

---

## 3️⃣ Fly.io

**✅ Avantajlar:**
- Ücretsiz tier (3 GB RAM)
- Global edge network
- Daha profesyonel

**📝 Adımlar:**

1. **flyctl CLI kur:**
```bash
# macOS
brew install flyctl

# veya
curl -L https://fly.io/install.sh | sh
```

2. **Login:**
```bash
flyctl auth login
```

3. **fly.toml oluştur:**
```bash
cd "/Users/emre/Desktop/Github Projects/url shortener"
cat > fly.toml << 'EOF'
app = "url-shortener-pro"
primary_region = "ams"

[build]
  builder = "paketobuildpacks/builder:base"

[env]
  PORT = "8080"

[[services]]
  http_checks = []
  internal_port = 8080
  processes = ["app"]
  protocol = "tcp"

  [[services.ports]]
    force_https = true
    handlers = ["http"]
    port = 80

  [[services.ports]]
    handlers = ["tls", "http"]
    port = 443
EOF
```

4. **Deploy:**
```bash
flyctl launch --no-deploy
flyctl deploy
```

**URL:** `https://url-shortener-pro.fly.dev`

---

## 4️⃣ Heroku

**⚠️ Not:** Heroku artık ücretsiz plan sunmuyor ($5-7/ay başlangıç)

**📝 Adımlar:**

1. **Procfile oluştur:**
```bash
echo "web: uvicorn url-shortener:app --host 0.0.0.0 --port \$PORT" > Procfile
```

2. **Heroku CLI kur:**
```bash
brew tap heroku/brew && brew install heroku
```

3. **Deploy:**
```bash
heroku login
heroku create url-shortener-pro
git push heroku main
```

---

## 5️⃣ VPS Deployment (Digital Ocean / Linode)

**✅ Tam kontrol, daha ucuz (uzun vadede)**

### A. VPS Satın Al

1. **Digital Ocean:**
   - https://digitalocean.com
   - $4-6/ay Droplet
   - Ubuntu 22.04 seç

2. **SSH ile bağlan:**
```bash
ssh root@YOUR_IP
```

### B. Sunucu Setup

```bash
# 1. Sistem güncellemeleri
apt update && apt upgrade -y

# 2. Python kur
apt install python3 python3-pip python3-venv nginx -y

# 3. Uygulama dizini oluştur
mkdir -p /var/www/url-shortener
cd /var/www/url-shortener

# 4. Git ile klonla (veya SFTP ile yükle)
git clone https://github.com/KULLANICI_ADIN/url-shortener-pro.git .

# 5. Virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 6. Systemd service oluştur
cat > /etc/systemd/system/url-shortener.service << 'EOF'
[Unit]
Description=URL Shortener Pro
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/url-shortener
Environment="PATH=/var/www/url-shortener/venv/bin"
ExecStart=/var/www/url-shortener/venv/bin/uvicorn url-shortener:app --host 0.0.0.0 --port 8000

[Install]
WantedBy=multi-user.target
EOF

# 7. Service'i başlat
systemctl daemon-reload
systemctl enable url-shortener
systemctl start url-shortener

# 8. Nginx yapılandır
cat > /etc/nginx/sites-available/url-shortener << 'EOF'
server {
    listen 80;
    server_name YOUR_DOMAIN.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

ln -s /etc/nginx/sites-available/url-shortener /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx

# 9. SSL (Let's Encrypt)
apt install certbot python3-certbot-nginx -y
certbot --nginx -d YOUR_DOMAIN.com
```

### C. Domain Ayarları

1. **DNS kayıtlarını güncelle:**
   - A Record: `@` → `YOUR_SERVER_IP`
   - A Record: `www` → `YOUR_SERVER_IP`

2. **Propagasyon bekle (5-30 dakika)**

---

## 📊 Karşılaştırma Tablosu

| Platform | Ücretsiz | Setup | Hız | Önerilen |
|----------|----------|-------|-----|----------|
| **Render** | ✅ 750h/ay | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ✅ Başlangıç |
| **Railway** | $5 kredi | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ Orta |
| **Fly.io** | ✅ 3GB RAM | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ Profesyonel |
| **Heroku** | ❌ $5-7/ay | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⚠️ Ücretli |
| **VPS** | ❌ $4-6/ay | ⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ Uzun vadede |

---

## 🔒 Güvenlik Önerileri

### 1. HTTPS Zorla
Tüm platformlar otomatik HTTPS sağlar.

### 2. Rate Limiting Ekle
```python
# url-shortener.py içine ekle
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/shorten")
@limiter.limit("10/minute")
async def shorten(...):
    ...
```

### 3. CORS Ayarları
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_methods=["GET", "POST", "DELETE"],
)
```

### 4. Environment Variables
Hassas bilgileri environment variable'da tut:
```python
import os
SECRET_KEY = os.getenv("SECRET_KEY", "default-key")
```

---

## 🎯 Production Checklist

- [ ] Git repository oluşturuldu
- [ ] requirements.txt hazır
- [ ] .gitignore ekli
- [ ] README.md güncel
- [ ] Database backup planı
- [ ] SSL/HTTPS aktif
- [ ] Domain bağlandı (opsiyonel)
- [ ] Analytics eklendi (opsiyonel)
- [ ] Rate limiting aktif
- [ ] Error monitoring (Sentry vb.)

---

## 📈 Deploy Sonrası

### Test Et
```bash
# Health check
curl https://your-app.render.com/

# URL kısalt
curl -X POST https://your-app.render.com/shorten \
  -H "Content-Type: application/json" \
  -d '{"url":"https://google.com"}'
```

### Monitor Et
- **Render:** Dashboard → Logs
- **Railway:** Project → Observability
- **Fly.io:** `flyctl logs`

### Update Et
```bash
git add .
git commit -m "Update: new feature"
git push origin main
# Otomatik deploy başlar
```

---

## 🆘 Troubleshooting

### Deploy Başarısız
```bash
# Logları kontrol et
render logs # veya railway logs
```

### Database Kayboldu
- Ücretsiz planlarda database geçici olabilir
- Persistent storage için upgrade gerekli
- Alternatif: External database (PostgreSQL)

### Slow Response
- Ücretsiz planlarda cold start normal
- Ping servisi kullan (uptimerobot.com)
- Veya ücretli plan al

---

## 💡 İpuçları

1. **Custom Domain:**
   - Namecheap/GoDaddy'den domain al ($10-15/yıl)
   - DNS ayarlarını güncelle

2. **Analytics:**
   - Google Analytics ekle
   - Plausible.io (privacy-friendly)

3. **Backup:**
   - Database'i düzenli yedekle
   - Git'te version control

4. **Monitoring:**
   - UptimeRobot.com (ücretsiz uptime monitoring)
   - Sentry.io (error tracking)

---

## 🎉 Başarılı Deploy!

Artık URL Shortener Pro'nuz internette yayında! 

**Sırada ne var?**
- [ ] Custom domain ekle
- [ ] Analytics ekle
- [ ] SEO optimizasyonu
- [ ] Sosyal medyada paylaş

**Örnek URL'ler:**
- Render: `https://url-shortener-pro.onrender.com`
- Railway: `https://url-shortener-pro.up.railway.app`
- Fly.io: `https://url-shortener-pro.fly.dev`

---

**Sorular?** GitHub Issues'da veya [email] ile iletişime geçin.

*Son güncelleme: Kasım 9, 2025*
