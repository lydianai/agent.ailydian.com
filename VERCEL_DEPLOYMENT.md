# 🚀 VERCEL DEPLOYMENT GUIDE
## agent.ailydian.com

### 📋 Ön Koşullar

1. **Vercel Account**
   - https://vercel.com adresinde hesap oluşturun
   - GitHub hesabınızı bağlayın

2. **Domain Erişimi**
   - `ailydian.com` domain'ine DNS erişiminiz olmalı

3. **Vercel CLI** (Opsiyonel)
   ```bash
   npm install -g vercel
   ```

### 🔧 Adım 1: Projeyi GitHub'a Push

```bash
cd /Users/sardag/Desktop/HealthCare-AI-Quantum-System

# Git repository başlat (eğer yoksa)
git init

# .gitignore oluştur
cat > .gitignore << EOF
__pycache__/
*.pyc
.env
*.log
*.pid
venv/
node_modules/
.DS_Store
*.bak
EOF

# İlk commit
git add .
git commit -m "Initial commit: Lydian Agent Healthcare AI System"

# GitHub repository oluşturun ve push edin
git remote add origin https://github.com/YOUR_USERNAME/lydian-agent.git
git branch -M main
git push -u origin main
```

### 🌐 Adım 2: Vercel'de Deployment

#### Yöntem 1: Vercel Dashboard (Önerilen)

1. **Vercel'e Giriş Yapın**
   - https://vercel.com/dashboard

2. **New Project**
   - "Add New..." → "Project" tıklayın
   - GitHub repository'nizi seçin: `lydian-agent`

3. **Configure Project**
   ```
   Project Name: lydian-agent
   Framework Preset: Other
   Root Directory: ./
   Build Command: (leave empty)
   Output Directory: (leave empty)
   Install Command: pip install -r requirements-vercel.txt
   ```

4. **Environment Variables**
   Şu değişkenleri ekleyin:
   ```
   APP_ENV=production
   APP_NAME=Lydian Agent
   DEBUG=false
   LOG_LEVEL=INFO
   API_HOST=0.0.0.0
   API_PORT=8000
   ```

5. **Deploy**
   - "Deploy" butonuna tıklayın
   - İlk deployment 2-3 dakika sürer

#### Yöntem 2: Vercel CLI

```bash
# Vercel'e login
vercel login

# Deployment (ilk kez)
vercel

# Sorulara cevaplar:
# - Set up and deploy? Y
# - Which scope? (Hesabınızı seçin)
# - Link to existing project? N
# - What's your project's name? lydian-agent
# - In which directory is your code located? ./

# Production deployment
vercel --prod
```

### 🔗 Adım 3: Custom Domain (agent.ailydian.com)

#### Vercel Dashboard'dan

1. **Domains Ayarları**
   - Projenize gidin
   - "Settings" → "Domains"

2. **Domain Ekle**
   - "Add Domain" tıklayın
   - `agent.ailydian.com` girin
   - "Add" tıklayın

3. **DNS Konfigürasyonu**

   Vercel size DNS kayıtları verecek. Domain registrar'ınızda:

   **CNAME Kaydı (Önerilen)**
   ```
   Type: CNAME
   Name: agent
   Value: cname.vercel-dns.com
   TTL: 3600
   ```

   **VEYA A Kaydı**
   ```
   Type: A
   Name: agent
   Value: 76.76.21.21
   TTL: 3600
   ```

4. **SSL Sertifikası**
   - Vercel otomatik olarak Let's Encrypt SSL sertifikası oluşturur
   - Yaklaşık 5-10 dakika sürer

### ✅ Adım 4: Deployment Doğrulama

```bash
# Health check
curl https://agent.ailydian.com/health

# API endpoint
curl https://agent.ailydian.com/api/v1/patient-monitoring/assess \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"patient_id":"TEST-001","vital_signs":{"heart_rate":75}}'

# Frontend
curl -I https://agent.ailydian.com/
```

### 🎨 Adım 5: Dil Geçişi Test

1. **Ana Sayfa**
   - https://agent.ailydian.com/ açın
   - Üst menüde TR/EN butonlarını test edin
   - Tüm menü, header, footer içeriklerinin değiştiğini doğrulayın

2. **Demo Sayfası**
   - https://agent.ailydian.com/demo.html
   - Türkiye/ABD hastane geçişlerini test edin
   - Dil değişimini test edin

3. **Console Check**
   - Browser DevTools → Console
   - Hata olmamalı ✅

### 🔧 Troubleshooting

#### Problem: 404 Not Found

**Çözüm:**
```bash
# vercel.json dosyasını kontrol edin
cat vercel.json

# Routes düzgün yapılandırılmış mı?
```

#### Problem: API Çalışmıyor

**Çözüm:**
```bash
# Vercel logs kontrol edin
vercel logs

# veya Dashboard'dan
# Project → Deployments → Latest → Function Logs
```

#### Problem: Static Files Yüklenmiyor

**Çözüm:**
```bash
# Frontend dosya yollarını kontrol edin
ls -la frontend/static/js/
ls -la frontend/static/css/

# HTML dosyalarında yolları kontrol edin
grep -r "static/" frontend/templates/
```

#### Problem: Language Switcher Çalışmıyor

**Çözüm:**
```bash
# JavaScript dosyasının yüklendiğini kontrol edin
curl https://agent.ailydian.com/static/js/enhanced-lang-switcher.js

# Browser console'da:
# localStorage.getItem('lydian-lang')
```

### 🔒 Güvenlik Ayarları (White-Hat)

Vercel Dashboard → Settings → Security:

1. **Deployment Protection**
   - ✅ Production Branch Protection
   - ✅ Vercel Authentication (optional)

2. **Environment Variables**
   - ✅ Hassas bilgileri `.env`'de tutun
   - ❌ Asla GitHub'a push etmeyin

3. **Headers**
   - ✅ CORS headers (vercel.json'da tanımlı)
   - ✅ Security headers

4. **Rate Limiting**
   - Vercel otomatik DDoS koruması sağlar
   - Pro plan'da custom rate limits

### 📊 Monitoring

**Vercel Analytics**
```
Dashboard → Analytics
- Page Views
- Unique Visitors
- Top Pages
- Performance Metrics
```

**Custom Monitoring**
```bash
# Health check monitoring (cron)
*/5 * * * * curl https://agent.ailydian.com/health
```

### 🚀 CI/CD Pipeline

Vercel otomatik deployment sağlar:

1. **GitHub'a Push**
   ```bash
   git add .
   git commit -m "Update features"
   git push origin main
   ```

2. **Automatic Deploy**
   - Vercel otomatik build yapar
   - Preview URL oluşturur
   - Test geçerse production'a deploy eder

3. **Preview Deployments**
   - Her pull request için otomatik preview
   - Test için kullanılabilir

### 📝 Deployment Checklist

- [ ] GitHub repository oluşturuldu
- [ ] Vercel'e import edildi
- [ ] Environment variables ayarlandı
- [ ] İlk deployment başarılı
- [ ] Custom domain eklendi (agent.ailydian.com)
- [ ] DNS kayıtları yapılandırıldı
- [ ] SSL sertifikası aktif
- [ ] Frontend erişilebilir
- [ ] API endpoints çalışıyor
- [ ] Language switcher test edildi
- [ ] Tüm sayfalar kontrol edildi
- [ ] Console'da 0 hata
- [ ] Mobile responsive test edildi
- [ ] Performance test edildi

### 🎯 Production URLs

```
Main Site:      https://agent.ailydian.com
Demo Page:      https://agent.ailydian.com/demo.html
API Health:     https://agent.ailydian.com/health
API Docs:       https://agent.ailydian.com/docs
API Endpoint:   https://agent.ailydian.com/api/v1/...
```

### 📞 Support

**Vercel Documentation:** https://vercel.com/docs
**Vercel Support:** https://vercel.com/support

---

## ✅ BEYAZ ŞAPKA KURALLAR (White-Hat Compliance)

1. **Güvenlik**
   - ✅ HTTPS/SSL zorunlu
   - ✅ CORS güvenli şekilde yapılandırıldı
   - ✅ API rate limiting
   - ✅ Hassas bilgiler gizli

2. **Privacy**
   - ✅ Kullanıcı dil tercihi localStorage'da
   - ✅ Tracking yok (default)
   - ✅ GDPR uyumlu

3. **Accessibility**
   - ✅ Semantic HTML
   - ✅ ARIA attributes
   - ✅ Keyboard navigation
   - ✅ Screen reader uyumlu

4. **Performance**
   - ✅ Minified assets
   - ✅ CDN (Vercel Edge Network)
   - ✅ Caching headers
   - ✅ Lazy loading

5. **Code Quality**
   - ✅ 0 console errors
   - ✅ Clean code
   - ✅ Documented
   - ✅ Version controlled

---

**🎊 Deployment Hazır!**
**🌐 Site: https://agent.ailydian.com**
